"""Build reproducible Java and Bedrock food packs and the Geyser v2 item mappings."""
import argparse
import io
import json
from pathlib import Path
import re
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from PIL import Image, ImageColor, ImageDraw
from food_art import PALETTE, recipes

ROOT = Path(__file__).resolve().parents[1]
FACES = ("north", "south", "east", "west", "up", "down")
COLORS = list(PALETTE)


def encoded(data):
    return (json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def png(image):
    data = io.BytesIO()
    image.save(data, format="PNG")
    return data.getvalue()


def archive(path, files):
    with ZipFile(path, "w") as out:
        for name, data in sorted(files.items()):
            info = ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            out.writestr(info, data)
    with ZipFile(path) as check:
        if check.testzip() is not None:
            raise ValueError(f"Archive verification failed: {path}")


def atlas():
    image = Image.new("RGB", (32, 32))
    draw = ImageDraw.Draw(image)
    for i, color in enumerate(COLORS):
        x, y = i % 8 * 4, i // 8 * 4
        rgb = ImageColor.getrgb(PALETTE[color])
        draw.rectangle((x, y, x+3, y+3), fill=rgb)
        draw.point((x+1, y+2), fill=tuple(max(0, n-12) for n in rgb))
        draw.point((x+3, y), fill=tuple(min(255, n+10) for n in rgb))
    return png(image)


def inventory_icon(parts):
    image = Image.new("RGBA", (96, 96))
    draw = ImageDraw.Draw(image)

    def project(x,y,z):
        return (48 + (x-z)*3.2, 65 + (x+z-16)*1.6 - y*3.6)

    # Draw the three visible faces from farthest to nearest in the orthographic view.
    faces = []
    for color,x,y,z,w,h,d in parts:
        rgb = ImageColor.getrgb(PALETTE[color])
        X,Y,Z = x+w,y+h,z+d
        for points,shade in [
            ([(X,y,z),(X,y,Z),(X,Y,Z),(X,Y,z)],.72),
            ([(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],.86),
            ([(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)],1.07)
        ]:
            depth = sum(a+b+c for a,b,c in points)/4
            faces.append((depth, [project(*point) for point in points],
                          tuple(min(255, int(v*shade)) for v in rgb)))
    for _, points, color in sorted(faces, key=lambda f: f[0]):
        draw.polygon(points, fill=color)
    return png(image.resize((48,48), Image.Resampling.LANCZOS))


def build(dest):
    dest.mkdir(parents=True, exist_ok=True)
    art = recipes()
    source = (ROOT/"source/src/main/java/com/sdcraft/core/gtm/FoodCatalogue.java").read_text()
    catalogue = dict(re.findall(r'new Meal\("([a-z_]+)",\s*"([^"]+)"', source))
    if set(catalogue) != set(art) or len(art) != 30:
        raise ValueError("Java catalogue and art IDs disagree")
    write_models(dest, art, catalogue, "Street_Kitchen", "minecraft:bread",
                 "a4877730-d813-41fa-a83e-f8a61a79021c", "4cb62365-8eea-4137-b475-e1ff5656ab4f",
                 "gtm_kitchen_mappings.json")


def write_models(dest, art, catalogue, title, base_item, header_id, module_id, mappings_name):
    dest.mkdir(parents=True, exist_ok=True)
    texture = atlas()
    atlas_name = title.lower()
    description = "GTM " + title.replace("_", " ") + " • SD Craft"
    java = {"pack.mcmeta": encoded({"pack":{"description":description,
                                              "min_format":84,"max_format":999,"pack_format":84}}),
            f"assets/gtm/textures/item/{atlas_name}.png":texture}
    bed = {"manifest.json":encoded({"format_version":2,"header":{"name":description,
               "description":description,"uuid":header_id,
               "version":[1,0,0],"min_engine_version":[1,21,80]},"modules":[{"type":"resources",
               "uuid":module_id,"version":[1,0,0]}]}),
           f"textures/gtm/{atlas_name}.png":texture}
    mappings, icons, geometry = [], {}, []
    for meal, parts in art.items():
        identifier = "gtm:"+meal
        elements, cubes = [], []
        for color,x,y,z,w,h,d in parts:
            if min(w,h,d) <= 0 or min(x,y,z)<0 or max(x+w,y+h,z+d)>16:
                raise ValueError(f"Invalid dimensions in {meal}")
            idx = COLORS.index(color)
            u,v = (idx%8)*4,(idx//8)*4
            elements.append({"from":[x,y,z],"to":[x+w,y+h,z+d],"faces":{
                face:{"uv":[u/2,v/2,(u+4)/2,(v+4)/2],"texture":"#kitchen"} for face in FACES}})
            cubes.append({"origin":[8-x-w,y-4,z-8],"size":[w,h,d],"uv":{
                face:{"uv":[u,v],"uv_size":[4,4]} for face in FACES}})
        java[f"assets/gtm/items/{meal}.json"] = encoded({"model":{"type":"minecraft:model","model":"gtm:item/"+meal}})
        java[f"assets/gtm/models/item/{meal}.json"] = encoded({"parent":"minecraft:block/block",
            "textures":{"kitchen":f"gtm:item/{atlas_name}","particle":f"gtm:item/{atlas_name}"},"elements":elements,
            "display":{"gui":{"rotation":[28,225,0],"translation":[0,1,0],"scale":[.88,.88,.88]},
                       "firstperson_righthand":{"rotation":[0,40,0],"translation":[1,2,0],"scale":[.55,.55,.55]}}})
        icon = "gtm_"+meal
        icons[icon] = {"textures":"textures/items/"+icon}
        bed[f"textures/items/{icon}.png"] = inventory_icon(parts)
        gid = "geometry.gtm."+meal
        geometry.append({"description":{"identifier":gid,"texture_width":32,"texture_height":32,
                                        "visible_bounds_width":2,"visible_bounds_height":2,"visible_bounds_offset":[0,.5,0]},
                         "bones":[{"name":"item","binding":"q.item_slot_to_bone_name(c.item_slot)",
                                   "pivot":[0,0,0],"cubes":cubes}]})
        bed[f"attachables/{meal}.json"] = encoded({"format_version":"1.10.0","minecraft:attachable":{
            "description":{"identifier":identifier,"materials":{"default":"entity_alphatest"},
                           "textures":{"default":f"textures/gtm/{atlas_name}"},"geometry":{"default":gid},
                           "render_controllers":["controller.render.default"]}}})
        mappings.append({"type":"definition","model":identifier,"bedrock_identifier":identifier,
                         "display_name":catalogue[meal],"bedrock_options":{"icon":icon}})
    bed[f"models/entity/{atlas_name}.geo.json"] = encoded({"format_version":"1.16.0","minecraft:geometry":geometry})
    bed["textures/item_texture.json"] = encoded({"resource_pack_name":"gtm_"+atlas_name,"texture_name":"atlas.items","texture_data":icons})
    archive(dest/f"GTM_{title}_Java.zip",java)
    archive(dest/f"GTM_{title}_Bedrock.mcpack",bed)
    (dest/mappings_name).write_bytes(encoded({"format_version":2,"items":{base_item:mappings}}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    build(parser.parse_args().output)
