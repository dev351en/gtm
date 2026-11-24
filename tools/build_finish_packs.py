"""Paint the four existing SD Craft item meshes and export both client formats."""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageEnhance
from build_food_packs import ROOT, archive, encoded, png

FAMILIES = {"pistol":"iron_hoe","shotgun":"golden_hoe","smg":"diamond_hoe","rifle":"netherite_hoe"}
PALETTES = [
    ("#182a50","#486aab","#c9d9e6","#e1ad62"), ("#5e3225","#c16835","#ffce6d","#f4e7bf"),
    ("#163f41","#298079","#c0d592","#f0c563"), ("#512d40","#bb627d","#f5c1ac","#e3ac65"),
    ("#202131","#555474","#d3d4e7","#87e0d7")
]


def pattern(number,x,y):
    a,b = x%16,y%16
    if number==0: return ((x+y+(y//4)%2)//3)%3
    if number==1: return 3 if (x+y)%12<2 or (x-y)%12<2 else (x//12)%2
    if number==2: return 2 if (x+2*y)%17<2 else int((x-y)%9<3)
    if number==3: return (abs(a-8)+abs(b-8))//3%4
    if number==4: return 3 if y%11==0 else int((y+(x//4)%3)%8<4)
    if number==5: return 2 if abs(a-8)+abs(b-8)<6 else (3 if (a+b)%16==0 else 0)
    if number==6: return (a//4+b//4+(x//16)%2)%3
    if number==7: return 2 if 3<y%12<7 and x%8<5 else int(y%12<3)
    if number==8: return int((x//3+y//3)%5<2)*2+int(b==15)
    if number==9: return 3 if (a-8)**2+(b-8)**2<8 else int(abs(a-8)*abs(b-8)<12)*2
    if number==10: return 2 if x%9<2 else int((y+2*x)%13<3)
    if number==11: return 3 if min(a,b)==0 else int((x//16+y//16)%2)
    if number==12: return int(math.hypot(a-8,b-8)//2)%3
    if number==13: return 3 if (x+2*y)%13==0 else (x//5+y//7)%3
    return 2 if (b==4 and a<12) or (a==12 and b>=4) else (3 if (a-3)**2+(b-4)**2<5 else 0)


def paint(family,index):
    color = [ImageColor.getrgb(v) for v in PALETTES[index%5]]
    variant = list(FAMILIES).index(family)
    image = Image.new("RGB",(32,32))
    for y in range(32):
        for x in range(32):
            # Rotate the fabric direction by chassis and edge-bind the artwork.
            u,v = ((x,y),(31-y,x),(31-x,31-y),(y,31-x))[variant]
            c = color[pattern(index//5,u+variant*2,v)]
            if y in (1,30): c = color[3]
            if x==0 or y==0 or x==31 or y==31: c = color[0]
            if 3<=x<=4+variant*2 and 26<=y<=27: c=color[3]
            image.putpixel((x,y),c)
    return image


def geometry(model,family):
    cubes = []
    for elem in model["elements"]:
        x,y,z = elem["from"]
        X,Y,Z = elem["to"]
        cube = {"origin":[8-X,y-8,z-8],"size":[X-x,Y-y,Z-z],"uv":{
            face:{"uv":[0,0],"uv_size":[32,32]} for face in elem["faces"]}}
        if rot := elem.get("rotation"):
            ox,oy,oz = rot["origin"]
            cube["pivot"] = [8-ox,oy-8,oz-8]
            angle = [0,0,0]
            angle["xyz".index(rot["axis"])] = rot["angle"] * (1 if rot["axis"]=="x" else -1)
            cube["rotation"] = angle
        cubes.append(cube)
    return {"description":{"identifier":"geometry.gtm.finish_"+family,"texture_width":32,"texture_height":32,
                           "visible_bounds_width":2,"visible_bounds_height":2,"visible_bounds_offset":[0,0,0]},
            "bones":[{"name":"item","binding":"q.item_slot_to_bone_name(c.item_slot)","pivot":[0,0,0],"cubes":cubes}]}


def icon(model, texture):
    # Side-profile orthographic projection of each stock mesh, including rotated parts.
    out = Image.new("RGBA",(64,64))
    for elem in sorted(model["elements"],key=lambda e:e["to"][2]):
        x,y,_ = elem["from"]
        X,Y,Z = elem["to"]
        points = [(x,y),(X,y),(X,Y),(x,Y)]
        if rot := elem.get("rotation"):
            ox,oy,_ = rot["origin"]
            a = math.radians(rot["angle"])
            points = [(ox+(px-ox)*math.cos(a)-(py-oy)*math.sin(a),
                       oy+(px-ox)*math.sin(a)+(py-oy)*math.cos(a)) for px,py in points]
        points = [(round(3+px*3.6),round(62-py*3.6)) for px,py in points]
        mask=Image.new("L",out.size)
        ImageDraw.Draw(mask).polygon(points,fill=255)
        surface=ImageEnhance.Brightness(texture.resize(out.size,Image.Resampling.NEAREST)).enhance(.78+(Z%3)/10)
        out.paste(surface,(0,0),mask)
        ImageDraw.Draw(out).line(points[2:]+[points[0]],fill=(55,49,54,255),width=1)
    return png(out)


def build(dest):
    dest.mkdir(parents=True,exist_ok=True)
    java = {"pack.mcmeta":encoded({"pack":{"description":"GTM Finish Studio • SD Craft",
                                          "pack_format":84,"min_format":84,"max_format":999}})}
    bed = {"manifest.json":encoded({"format_version":2,"header":{"name":"GTM Finish Studio",
        "description":"Indraprastha finishes by SD Craft","uuid":"6fb4df75-f200-4cb0-84ae-24c2e05ef592",
        "version":[1,0,0],"min_engine_version":[1,21,80]},"modules":[{"type":"resources",
        "uuid":"ac07cbb9-b73a-48c0-b503-fb4e0b3d5075","version":[1,0,0]}]})}
    mappings,icons,meshes,hashes = {},{},{},set()
    with ZipFile(ROOT/"resource-pack/EXPECT_SDCRAFT_ResourcePack_26.3.zip") as source:
        for family,material in FAMILIES.items():
            model=json.loads(source.read(f"assets/sdcraft/models/item/gun_{family}_3d.json"))
            for elem in model["elements"]:
                for face in elem["faces"].values():
                    face.update(texture="#finish",uv=[0,0,16,16])
            model["textures"]={"particle":"#finish"}
            java[f"assets/gtm/models/item/base_{family}.json"]=encoded(model)
            meshes[family]=geometry(model,family)
            definitions=[]
            for index in range(75):
                name=f"{family}_{index+1:02d}"
                item="gtm:"+name
                image=paint(family,index)
                hashes.add(hashlib.sha256(image.tobytes()).digest())
                surface=png(image)
                java[f"assets/gtm/items/{name}.json"]=encoded({"model":{"type":"minecraft:model","model":"gtm:item/"+name}})
                java[f"assets/gtm/models/item/{name}.json"]=encoded({"parent":"gtm:item/base_"+family,
                                                                     "textures":{"finish":"gtm:finish/"+name}})
                java[f"assets/gtm/textures/finish/{name}.png"]=surface
                bed[f"textures/gtm/{name}.png"]=surface
                bed[f"textures/items/{name}.png"]=icon(model,image)
                bed[f"attachables/{name}.json"]=encoded({"format_version":"1.10.0","minecraft:attachable":{
                    "description":{"identifier":item,"materials":{"default":"entity_alphatest"},
                    "textures":{"default":"textures/gtm/"+name},"geometry":{"default":"geometry.gtm.finish_"+family},
                    "render_controllers":["controller.render.default"]}}})
                icons["gtm_"+name]={"textures":"textures/items/"+name}
                definitions.append({"type":"definition","model":item,"bedrock_identifier":item,
                                    "bedrock_options":{"icon":"gtm_"+name}})
            mappings["minecraft:"+material]=definitions
    if len(hashes)!=300:
        raise ValueError("Duplicate finish textures")
    bed["models/entity/finish.geo.json"]=encoded({"format_version":"1.16.0","minecraft:geometry":list(meshes.values())})
    bed["textures/item_texture.json"]=encoded({"resource_pack_name":"gtm_finishes","texture_name":"atlas.items","texture_data":icons})
    archive(dest/"GTM_Finish_Studio_Java.zip",java)
    archive(dest/"GTM_Finish_Studio_Bedrock.mcpack",bed)
    (dest/"gtm_finish_mappings.json").write_bytes(encoded({"format_version":2,"items":mappings}))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    build(parser.parse_args().output)
