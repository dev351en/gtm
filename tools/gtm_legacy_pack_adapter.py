"""Explicit Bedrock adapters for the core's existing Java CustomModelData items.

The original Java models/textures are retained. Bedrock geometry samples those
same textures; 3D inventory icons are rendered directly on a128 pixel grid.
This is compatibility reuse, not an additional authored asset catalogue.
"""
from __future__ import annotations

from copy import deepcopy
import io
import json
import math
from pathlib import Path
import tempfile

import numpy as np
from PIL import Image

import studio_3d_engine as engine


PHONE_MODELS = {
    "app_gps": "app_maps", "app_jobs": "app_careers", "app_garage": "app_garage",
    "app_bank": "app_bank", "app_safety": "app_police", "app_medical": "app_medical",
    "app_settings": "app_settings",
}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def png(image):
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def repair_phone_models(java, art):
    """Fill eight absent files referenced by the existing phone CMD dispatch."""
    repaired = []
    for legacy, native in {**PHONE_MODELS, "app_gear": "legacy_app_gear"}.items():
        path = f"assets/sdcraft/models/item/{legacy}.json"
        if path in java:
            continue
        texture = "gtm:ui/phone/" + native
        if legacy == "app_gear":
            java["assets/gtm/textures/ui/phone/legacy_app_gear.png"] = (Path(art) / "source/icons/hero_props/hero_pistol.png").read_bytes()
        if "assets/" + texture.replace(":", "/textures/") + ".png" not in java:
            raise ValueError("Missing semantic phone icon: " + legacy)
        java[path] = encoded({"parent": "minecraft:item/generated", "textures": {"layer0": texture}})
        repaired.append(path)
    return repaired


def legacy_bindings(java):
    result = []
    for name, data in sorted(java.items()):
        if not name.startswith("assets/minecraft/items/") or not name.endswith(".json"):
            continue
        tree = json.loads(data).get("model", {})
        if tree.get("type", "").removeprefix("minecraft:") != "range_dispatch":
            continue
        if tree.get("property", "").removeprefix("minecraft:") != "custom_model_data":
            continue
        base = "minecraft:" + Path(name).stem
        for row in tree["entries"]:
            model = row["model"]
            if model.get("type", "").removeprefix("minecraft:") != "model":
                raise ValueError("Unsupported nested legacy item dispatch: " + name)
            threshold = row["threshold"]
            if not isinstance(threshold, (float, int)) or not math.isfinite(threshold):
                raise ValueError("Invalid custom model data selector: " + name)
            if not model["model"].startswith("sdcraft:"):
                # User-imported packs may contain other independent namespaces;
                # these retain their existing assets and need their own mapping.
                continue
            key = model["model"].split(":", 1)[1].removeprefix("item/").replace("/", "_")
            result.append({"base_item": base, "custom_model_data": threshold, "java_model": model["model"],
                           "bedrock_identifier": "sdcraft:legacy_" + key + "_" + str(threshold).replace(".", "_")})
    return result


def default_uv(element, face):
    x, y, z = element["from"]
    X, Y, Z = element["to"]
    return {"down": [x, 16-Z, X, 16-z], "up": [x, z, X, Z],
            "north": [16-X, 16-Y, 16-x, 16-y], "south": [x, 16-Y, X, 16-y],
            "west": [z, 16-Y, Z, 16-y], "east": [16-Z, 16-Y, 16-z, 16-y]}[face]


def rotated(element):
    record = element.get("rotation", {})
    if record.get("rescale"):
        raise ValueError("Legacy rescaled rotations need an explicit adapter")
    angles = [record.get(axis, 0) for axis in "xyz"]
    if "axis" in record:
        angles["xyz".index(record["axis"])] = record["angle"]
    return angles, record.get("origin")


def mesh_atlas(model, java, resolver):
    references = set()
    for element in model["elements"]:
        for face in element["faces"].values():
            if face.get("rotation", 0):
                raise ValueError("Legacy rotated face UVs need an explicit adapter")
            references.add(resolver(model["textures"], face["texture"]))
    textures = {}
    for reference in sorted(references):
        namespace, path = reference.split(":", 1)
        textures[reference] = Image.open(io.BytesIO(java[f"assets/{namespace}/textures/{path}.png"])).convert("RGBA")
    edge = max(max(image.size) for image in textures.values())
    tile = 1 << (edge - 1).bit_length()
    columns = 1 << (min(4, len(textures)) - 1).bit_length()
    rows = 1 << ((len(textures) + columns - 1) // columns - 1).bit_length()
    atlas = Image.new("RGBA", (tile * columns, tile * rows))
    regions = {}
    for index, (name, image) in enumerate(textures.items()):
        x, y = index % columns * tile, index // columns * tile
        atlas.paste(image, (x, y))
        regions[name] = (x, y, *image.size)
    return atlas, regions, textures


def bedrock_geometry(model, identifier, atlas, regions, resolver):
    cubes = []
    for element in model["elements"]:
        x, y, z = element["from"]
        X, Y, Z = element["to"]
        if min(X-x, Y-y, Z-z) <= 0:
            raise ValueError("Zero-size legacy model element")
        cube = {"origin": [8-X, y-8, z-8], "size": [X-x, Y-y, Z-z], "uv": {}}
        for face, detail in element["faces"].items():
            texture = resolver(model["textures"], detail["texture"])
            tx, ty, width, height = regions[texture]
            u0, v0, u1, v1 = detail.get("uv", default_uv(element, face))
            cube["uv"][face] = {"uv": [tx + u0 * width / 16, ty + v0 * height / 16],
                                 "uv_size": [(u1-u0) * width / 16, (v1-v0) * height / 16]}
        angles, pivot = rotated(element)
        if any(angles):
            if pivot is None:
                pivot = [(x+X)/2, (y+Y)/2, (z+Z)/2]
            cube["rotation"] = [angles[0], -angles[1], -angles[2]]
            cube["pivot"] = [8-pivot[0], pivot[1]-8, pivot[2]-8]
        cubes.append(cube)
    return {"format_version": "1.16.0", "minecraft:geometry": [{
        "description": {"identifier": identifier, "texture_width": atlas.width, "texture_height": atlas.height,
                        "visible_bounds_width": 3, "visible_bounds_height": 3, "visible_bounds_offset": [0, 0, 0]},
        "bones": [{"name": "item", "binding": "q.item_slot_to_bone_name(c.item_slot)", "pivot": [0, 0, 0], "cubes": cubes}]}]}


def render_icon(model, textures, resolver, path, yaw):
    materials, tiles = {}, []
    builder = engine.PartBuilder()
    for index, element in enumerate(model["elements"]):
        faces = {}
        for face, detail in element["faces"].items():
            reference = resolver(model["textures"], detail["texture"])
            uv = detail.get("uv", default_uv(element, face))
            signature = (reference, *uv)
            if signature not in materials:
                material = "legacy_" + str(len(tiles))
                texture = textures[reference]
                extent = tuple(value / 16 * (texture.width if i % 2 == 0 else texture.height) for i, value in enumerate(uv))
                crop = texture.transform((128, 128), Image.Transform.EXTENT, extent, resample=Image.Resampling.NEAREST)
                materials[signature] = material
                tiles.append(crop)
            faces[face] = materials[signature]
        x, y, z = element["from"]
        X, Y, Z = element["to"]
        angles, pivot = rotated(element)
        builder.box(x-8, y, z-8, X-x, Y-y, Z-z, mat=next(iter(faces.values())), face_mats=faces,
                    rot=angles if any(angles) else None,
                    pivot=[pivot[0]-8, pivot[1], pivot[2]-8] if pivot else None, name="legacy_part_" + str(index))
    old = engine.MATERIALS, engine.MAT_INDEX, engine.ATLAS_ARR, engine.TILE_SIZE
    try:
        names = list(materials.values())
        engine.MATERIALS = [(name, "#666666", "compatibility") for name in names]
        engine.MAT_INDEX = {name: index for index, name in enumerate(names)}
        engine.TILE_SIZE = 128
        atlas = Image.new("RGBA", (16*128, math.ceil(len(tiles)/16)*128))
        for index, tile in enumerate(tiles):
            atlas.paste(tile, (index % 16 * 128, index // 16 * 128))
        engine.ATLAS_ARR = np.asarray(atlas)
        builder.render_icon(path, size=128, grid=128, yaw_deg=yaw, pitch_deg=24)
        return path.read_bytes()
    finally:
        engine.MATERIALS, engine.MAT_INDEX, engine.ATLAS_ARR, engine.TILE_SIZE = old


def bridge(java, model_loader, texture_resolver):
    bed, items, details, icons = {}, {}, {}, {}
    with tempfile.TemporaryDirectory(prefix="gtm-legacy-icons-") as temporary:
        for binding in legacy_bindings(java):
            identifier = binding["bedrock_identifier"]
            key = identifier.split(":", 1)[1]
            geometry_id = "geometry.sdcraft." + key
            model = deepcopy(model_loader(java, binding["java_model"]))
            flat = not bool(model.get("elements"))
            if flat:
                reference = texture_resolver(model["textures"], "#layer0")
                namespace, path = reference.split(":", 1)
                original_icon = java[f"assets/{namespace}/textures/{path}.png"]
                model["elements"] = [{"from": [0, 0, 7.99], "to": [16, 16, 8.01], "faces": {
                    face: {"texture": "#layer0", "uv": [0, 0, 16, 16]} for face in ("north", "south")}}]
            atlas, regions, textures = mesh_atlas(model, java, texture_resolver)
            geometry = bedrock_geometry(model, geometry_id, atlas, regions, texture_resolver)
            surface = "textures/sdcraft_compat/" + key
            bed[surface + ".png"] = png(atlas)
            bed[f"models/entity/{key}.geo.json"] = encoded(geometry)
            bed[f"attachables/{key}.json"] = encoded({"format_version": "1.10.0", "minecraft:attachable": {"description": {
                "identifier": identifier, "materials": {"default": "entity_alphatest"}, "textures": {"default": surface},
                "geometry": {"default": geometry_id}, "render_controllers": ["controller.render.gtm128"]}}})
            icon_path = "textures/items/sdcraft_" + key
            icon = original_icon if flat else render_icon(model, textures, texture_resolver, Path(temporary) / (key + ".png"),
                    -38 if "gun_" in key or "baseball_bat" in key else 142)
            bed[icon_path + ".png"] = icon
            icon_id = "sdcraft_" + key
            icons[icon_id] = {"textures": icon_path}
            items.setdefault(binding["base_item"], []).append({"type": "legacy", "custom_model_data": binding["custom_model_data"],
                "bedrock_identifier": identifier, "bedrock_options": {"icon": icon_id}})
            details[identifier] = {**binding, "geometry_id": geometry_id, "cube_count": len(model["elements"]),
                "source_render_kind": "flat_generated_item" if flat else "preserved_3d_mesh", "compatibility_reuse": True}
    bed["textures/item_texture.json"] = encoded({"resource_pack_name": "gtm_runtime128", "texture_name": "atlas.items", "texture_data": icons})
    return bed, {"format_version": 2, "items": items}, details
