#!/usr/bin/env python3
"""Merge native128 art with the existing runtime packs without reassigning legacy IDs.

This builds local artifacts only. It never installs a pack, changes a world, edits
an entitlement, enables a feature flag, or changes a server URL.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
import uuid
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROFILE = "INDRAPRASTHA_128_V1"
CATALOG_HEADER = "# gtm-asset-catalog\t1\t" + PROFILE
RESOURCE = ROOT / "source/src/main/resources/gtm-assets.tsv"
ID = re.compile(r"gtm:[a-z0-9_]+")
FINISH_BASES = {"pistol": "iron_hoe", "shotgun": "golden_hoe", "smg": "diamond_hoe", "rifle": "netherite_hoe"}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_archive(path):
    files = {}
    with ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError(f"Corrupt pack: {path}")
        for member in archive.infolist():
            if member.is_dir():
                continue
            name = member.filename
            if name.startswith("/") or ".." in PurePosixPath(name).parts or "\\" in name or "\0" in name:
                raise ValueError(f"Unsafe pack entry: {name}")
            content = archive.read(member)
            if name in files and files[name] != content:
                raise ValueError(f"Conflicting duplicate pack entry: {name}")
            # The preserved server pack contains one byte-identical repeated
            # metro-ticket model. Deduplicate exact copies; refuse ambiguity.
            files[name] = content
    return files


def archive(path, files):
    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, "w", ZIP_DEFLATED) as output:
        for name, data in sorted(files.items()):
            info = ZipInfo(name, (2026, 11, 25, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            output.writestr(info, data)
    with ZipFile(path) as check:
        if check.testzip() is not None:
            raise ValueError(f"Failed output CRC: {path}")
    return {"file": path.name, "sha256": digest(path.read_bytes()),
            "sha1": hashlib.sha1(path.read_bytes()).hexdigest(),
            "size_bytes": path.stat().st_size, "entries": len(files)}


def records(art):
    result = {}
    def add(row, category, kind):
        key = row["id"]
        if key in result:
            raise ValueError("Duplicate authored asset ID: " + key)
        result[key] = {**row, "runtime_category": category, "runtime_kind": kind}
    for name in ("furniture", "transport", "festivals", "festival_additions"):
        for row in json.loads((art / "manifests" / (name + "_128.json")).read_text())["assets"]:
            category = name
            if name == "transport":
                category = row.get("subcategory", "road")
                category = category if category in ("rail", "marine", "helicopter") else "rail" if category == "ropeway" else "road"
            if name in ("festivals", "festival_additions"):
                category = "festival"
            add(row, category, "city")
    equipment = json.loads((art / "manifests/equipment_food_128.json").read_text())
    for group in ("equipment", "food", "weapons", "hero_props"):
        for row in equipment[group]:
            category = row.get("legacy_source_record", {}).get("category", group)
            if group == "equipment":
                category = row.get("legacy_source_record", {}).get("subcategory", "equipment")
            add(row, category, "food" if group == "food" else "city" if group == "equipment" else "prop")
    for row in json.loads((art / "manifests/finishes_128.json").read_text())["mappings_128"]:
        add(row, "finish_art", "prop")
    states = json.loads((art / "manifests/vehicle_states_128.json").read_text())
    choices = [v for v in states.values() if isinstance(v, list) and v and isinstance(v[0], dict) and "java_model_path" in v[0]]
    if len(choices) != 1:
        raise ValueError("Ambiguous vehicle state catalogue")
    for row in choices[0]:
        add(row, "vehicle_state", "prop")
    if len(result) != 1073:
        raise ValueError(f"Unexpected native128 model count: {len(result)}")
    return result


def merge_mappings(target, incoming):
    if incoming.get("format_version") != 2:
        raise ValueError("Only Geyser v2 mappings are supported")
    for base, rows in incoming["items"].items():
        for row in rows:
            if row.get("type") not in ("definition", "legacy"):
                raise ValueError("Unsupported Geyser mapping type")
            key = (base, row["type"], row.get("model", row.get("custom_model_data")))
            target[key] = deepcopy(row)


def merge_bedrock(target, incoming):
    # A legacy file contains many geometries; remove only geometry identifiers
    # explicitly replaced by the new pack, preserving every other old design.
    incoming_ids = set()
    for name, data in incoming.items():
        if name.endswith(".geo.json"):
            incoming_ids.update(g["description"]["identifier"] for g in json.loads(data)["minecraft:geometry"])
    for name in list(target):
        if name.endswith(".geo.json"):
            document = json.loads(target[name])
            kept = [g for g in document["minecraft:geometry"] if g["description"]["identifier"] not in incoming_ids]
            if kept:
                document["minecraft:geometry"] = kept
                target[name] = encoded(document)
            else:
                del target[name]
    for name, data in incoming.items():
        if name in ("manifest.json", "pack_icon.png"):
            continue
        if name == "textures/item_texture.json":
            old = json.loads(target.get(name, b'{"texture_data":{}}'))
            old["texture_data"].update(json.loads(data)["texture_data"])
            old.update(resource_pack_name="gtm_runtime128", texture_name="atlas.items")
            target[name] = encoded(old)
        elif name.startswith("render_controllers/") and name in target:
            old = json.loads(target[name])
            old.setdefault("render_controllers", {}).update(json.loads(data)["render_controllers"])
            target[name] = encoded(old)
        else:
            target[name] = data


def java_model(files, identifier, visiting=None):
    """Resolve inheritance, including legacy finish parent meshes and texture slots."""
    # Minecraft resource locations without a namespace use minecraft, including
    # the valid "item/generated" parent used by preserved third-party models.
    identifier = identifier if ":" in identifier else "minecraft:" + identifier
    visiting = set() if visiting is None else visiting
    if identifier in visiting:
        raise ValueError("Java model parent cycle: " + identifier)
    visiting = visiting | {identifier}
    namespace, key = identifier.split(":", 1)
    path = f"assets/{namespace}/models/{key}.json"
    if path not in files:
        if namespace == "minecraft":
            return {"textures": {}}
        raise ValueError("Missing Java model: " + path)
    child = json.loads(files[path])
    parent = java_model(files, child["parent"], visiting) if "parent" in child else {}
    return {**parent, **child, "textures": {**parent.get("textures", {}), **child.get("textures", {})}}


def texture_reference(textures, reference):
    seen = set()
    while reference.startswith("#"):
        if reference in seen or reference[1:] not in textures:
            raise ValueError("Unresolved or cyclic Java texture slot: " + reference)
        seen.add(reference)
        reference = textures[reference[1:]]
    return reference


def mapping_document(mapping):
    items = {}
    for (base, _, _), row in sorted(mapping.items(), key=lambda pair: str(pair[0])):
        items.setdefault(base, []).append(row)
    return {"format_version": 2, "items": items}


def catalogue(mapping, native, old_city):
    result = {}
    for (base, kind, identifier), definition in mapping.items():
        if kind != "definition" or not ID.fullmatch(identifier):
            continue
        key = identifier.removeprefix("gtm:")
        canonical = identifier
        if identifier in native:
            row = native[identifier]
            category, title, asset_kind = row["runtime_category"], row.get("title", key), row["runtime_kind"]
            source = "NATIVE_128"
        elif "gtm:food_" + key in native and base == "minecraft:bread":
            canonical = "gtm:food_" + key
            category, title, asset_kind = "food", native[canonical]["title"], "food"
            source = "ALIAS_128"
        elif key in old_city:
            category, title = old_city[key]
            asset_kind, source = "city", "LEGACY_COMPATIBILITY"
        elif any(key.startswith(family + "_") for family in FINISH_BASES):
            category, title, asset_kind = "finish", definition.get("display_name", key.replace("_", " ").title()), "finish"
            source = "LEGACY_COMPATIBILITY"
        else:
            raise ValueError("Unaccounted runtime model: " + identifier)
        # The stable old catalogue retains its semantic name and category even
        # where an authored128 model safely replaces the exact same identifier.
        if key in old_city:
            category, title = old_city[key]
        fields = [identifier, category, title, base, source, canonical, asset_kind]
        if any("\t" in str(value) or "\n" in str(value) or "\r" in str(value) for value in fields):
            raise ValueError("Unsafe catalogue field: " + identifier)
        if identifier in result:
            raise ValueError("Ambiguous catalogue base item: " + identifier)
        result[identifier] = fields
    return result


def validate(java, bed, mapping, native, old_city, base_java, allowed_overrides, legacy_models=None):
    protected = [name for name in base_java if name not in allowed_overrides]
    changed = [name for name in protected if java.get(name) != base_java[name]]
    if changed:
        raise ValueError("Existing active Java assets changed: " + ", ".join(changed[:5]))
    geometries, attachments = {}, {}
    for name, data in bed.items():
        if name.endswith(".geo.json"):
            for geometry in json.loads(data)["minecraft:geometry"]:
                gid = geometry["description"]["identifier"]
                if gid in geometries:
                    raise ValueError("Duplicate Bedrock geometry: " + gid)
                geometries[gid] = geometry
        elif name.startswith("attachables/") and name.endswith(".json"):
            description = json.loads(data)["minecraft:attachable"]["description"]
            identifier = description["identifier"]
            if identifier in attachments:
                raise ValueError("Duplicate Bedrock attachable: " + identifier)
            attachments[identifier] = description
    icons = json.loads(bed["textures/item_texture.json"])["texture_data"]
    seen, definition_ids = set(), set()
    native_icons, compatibility_icons, face_count, legacy_resolved = 0, 0, 0, 0
    legacy_models = legacy_models or {}
    for (base, kind, selector), definition in mapping.items():
        identifier = definition["bedrock_identifier"]
        if identifier in seen:
            raise ValueError("Duplicate global Bedrock identifier: " + identifier)
        seen.add(identifier)
        if kind == "legacy":
            detail = legacy_models[identifier]
            if detail["base_item"] != base or detail["custom_model_data"] != selector:
                raise ValueError("Incorrect legacy CustomModelData selector: " + identifier)
            model = java_model(java, detail["java_model"])
            expected_cubes = detail["cube_count"]
            key = identifier.split(":", 1)[1]
            legacy_resolved += 1
        else:
            if selector != identifier:
                raise ValueError("Unexpected runtime model alias: " + selector)
            definition_ids.add(selector)
            namespace, key = selector.split(":", 1)
            definition_path = f"assets/{namespace}/items/{key}.json"
            item = json.loads(java[definition_path])["model"]
            if item.get("type") != "minecraft:model":
                raise ValueError("Unsupported GTM item definition: " + selector)
            model = java_model(java, item["model"])
            expected_cubes = len(model.get("elements", []))
        for element in model.get("elements", []):
            for face in element["faces"].values():
                texture = texture_reference(model["textures"], face["texture"])
                ns, path = texture.split(":", 1)
                if f"assets/{ns}/textures/{path}.png" not in java:
                    raise ValueError("Missing Java texture: " + texture)
                face_count += 1
        attachable = attachments[identifier]
        geometry = geometries[attachable["geometry"]["default"]]
        cubes = sum(len(b.get("cubes", [])) for b in geometry["bones"])
        if cubes != expected_cubes:
            raise ValueError("Java/Bedrock geometry mismatch: " + identifier)
        surface = bed[attachable["textures"]["default"] + ".png"]
        with Image.open(io.BytesIO(surface)) as image:
            if image.size != (geometry["description"]["texture_width"], geometry["description"]["texture_height"]):
                raise ValueError("Bedrock UV atlas size mismatch: " + identifier)
            for bone in geometry["bones"]:
                for cube in bone.get("cubes", []):
                    for face in cube.get("uv", {}).values():
                        start, size = face["uv"], face["uv_size"]
                        if any(not math.isfinite(value) for value in [*start, *size]):
                            raise ValueError("Non-finite Bedrock UV: " + identifier)
                        if any(min(start[axis], start[axis]+size[axis]) < -1e-5 or
                               max(start[axis], start[axis]+size[axis]) > image.size[axis]+1e-5 for axis in (0, 1)):
                            raise ValueError("Bedrock UV outside its atlas: " + identifier)
        icon_path = icons[definition["bedrock_options"]["icon"]]["textures"]
        with Image.open(io.BytesIO(bed[icon_path + ".png"])) as image:
            if not image.convert("RGBA").getchannel("A").getbbox():
                raise ValueError("Empty Bedrock icon: " + identifier)
            is_native = kind == "definition" and (identifier in native or "gtm:food_" + key in native)
            if is_native:
                if image.size != (128, 128):
                    raise ValueError("Native128 icon dimensions changed: " + identifier)
                native_icons += 1
            else:
                compatibility_icons += 1
    expected_old = {"gtm:" + key for key in old_city}
    expected_food = {"gtm:" + key.removeprefix("gtm:food_") for key in native if native[key]["runtime_kind"] == "food"}
    expected_finishes = {f"gtm:{family}_{index:02d}" for family in FINISH_BASES for index in range(1, 76)}
    for label, expected in [("city", expected_old), ("food", expected_food), ("finish", expected_finishes)]:
        missing = expected - definition_ids
        if missing:
            raise ValueError("Missing legacy " + label + " IDs: " + ", ".join(sorted(missing)))
    if not set(native).issubset(definition_ids):
        raise ValueError("Missing native128 item definitions")
    return {"legacy_city_ids_resolved": len(expected_old), "legacy_food_ids_resolved": len(expected_food),
            "legacy_one_based_finish_ids_resolved": len(expected_finishes), "native128_models_resolved": len(native),
            "item_definitions_resolved": len(definition_ids), "global_bedrock_identifiers": len(seen),
            "existing_custom_model_data_items_resolved": legacy_resolved,
            "native128_icons": native_icons, "legacy_compatibility_icons": compatibility_icons,
            "protected_active_java_files_unchanged": len(protected), "java_texture_face_references": face_count,
            "bedrock_uv_rectangles": "finite_and_within_bound_atlas",
            "multi_bone_and_inherited_mesh_counts": "matched", "live_java_bedrock_clients": "not_run"}


def build(output, art=None, java_base=None, bedrock_bases=(), write_resource=False, check_resource=False):
    from build_food_packs import build as build_food
    from build_city_packs import build as build_city
    from build_finish_packs import build as build_finishes
    from check_client_packs import verify as check_legacy

    output = Path(output)
    art = Path(art or ROOT / "creative/generated_128")
    java_base = Path(java_base or ROOT / "resource-pack/EXPECT_SDCRAFT_ResourcePack_26.3.zip")
    output.mkdir(parents=True, exist_ok=True)
    compatibility = output / "legacy_compatibility"
    build_food(compatibility)
    build_city(compatibility)
    build_finishes(compatibility)
    for title, mappings, count in [("Street_Kitchen", "gtm_kitchen_mappings.json", 30),
                                   ("City_Collection", "gtm_city_mappings.json", 479),
                                   ("Finish_Studio", "gtm_finish_mappings.json", 300)]:
        check_legacy(compatibility, title, mappings, count)
    base_java = read_archive(java_base)
    java = dict(base_java)
    bed, mapping = {}, {}
    for base in bedrock_bases:
        merge_bedrock(bed, read_archive(Path(base)))
    for name, mappings in [("Street_Kitchen", "gtm_kitchen_mappings.json"), ("City_Collection", "gtm_city_mappings.json"), ("Finish_Studio", "gtm_finish_mappings.json")]:
        for path, content in read_archive(compatibility / f"GTM_{name}_Java.zip").items():
            if path != "pack.mcmeta":
                java[path] = content
        merge_bedrock(bed, read_archive(compatibility / f"GTM_{name}_Bedrock.mcpack"))
        merge_mappings(mapping, json.loads((compatibility / mappings).read_text()))
    native = records(art)
    native_java = read_archive(art / "packs/GTM_Indraprastha_128_Java.zip")
    native_bed = read_archive(art / "packs/GTM_Indraprastha_128_Bedrock.mcpack")
    world = json.loads((art / "manifests/world_128.json").read_text())["textures"]
    world_paths = {row["java_texture"] for row in world}
    allowed_overrides = world_paths | {"pack.mcmeta", "pack.png"}
    for name, content in native_java.items():
        if name == "pack.mcmeta":
            continue
        if name in base_java and base_java[name] != content and name not in allowed_overrides:
            raise ValueError("Native128 pack would overwrite an active non-world asset: " + name)
        java[name] = content
    merge_bedrock(bed, native_bed)
    merge_mappings(mapping, json.loads((art / "packs/Geyser_v2_128_ART_PROPOSAL.json").read_text()))
    from gtm_legacy_pack_adapter import repair_phone_models, bridge
    repaired_phone_models = repair_phone_models(java, art)
    compatible_bed, compatible_mapping, legacy_models = bridge(java, java_model, texture_reference)
    merge_bedrock(bed, compatible_bed)
    merge_mappings(mapping, compatible_mapping)
    # Existing animation overlays and license files survive the merge. Only the
    # pack's declared target range and description change.
    metadata = json.loads(base_java["pack.mcmeta"])
    metadata["pack"] = {"description": "GTM Indraprastha128 | SD Craft | native128 city + preserved active pack",
                        "min_format": [97, 1], "max_format": [97, 1]}
    java["pack.mcmeta"] = encoded(metadata)
    java["pack.png"] = native_java["pack.png"]
    bed["pack_icon.png"] = native_bed["pack_icon.png"]
    # Keep geometry not referenced by an attachable: imported Bedrock resource
    # packs may use it from client entities or other independent controllers.
    uid = lambda value: str(uuid.uuid5(uuid.NAMESPACE_URL, "https://github.com/dev351en/gtm/runtime128/" + value))
    content_hash = digest(b"".join(name.encode() + hashlib.sha256(value).digest() for name, value in sorted(bed.items())))
    version = [1, 0, int(content_hash[:6], 16)]
    bed["manifest.json"] = encoded({"format_version": 2, "header": {
        "name": "GTM Indraprastha128 Runtime", "description": "SD Craft native128 city and stable legacy compatibility models",
        "uuid": uid("header"), "version": version, "min_engine_version": [1, 21, 80]},
        "modules": [{"type": "resources", "uuid": uid("resources"), "version": version}]})
    old_city = {parts[0]: parts[1:] for parts in (line.split("\t") for line in
                (ROOT / "source/src/main/resources/gtm-city-models.tsv").read_text().splitlines())}
    if len(old_city) != 479:
        raise ValueError("Legacy catalogue changed unexpectedly")
    rows = catalogue(mapping, native, old_city)
    tsv = CATALOG_HEADER + "\n" + "".join("\t".join(fields) + "\n" for _, fields in sorted(rows.items()))
    if check_resource and (not RESOURCE.is_file() or RESOURCE.read_text() != tsv):
        raise ValueError("Committed gtm-assets.tsv is stale; regenerate with --write-resource")
    checks = validate(java, bed, mapping, native, old_city, base_java, allowed_overrides, legacy_models)
    (output / "gtm-assets.tsv").write_text(tsv, encoding="utf-8")
    if write_resource:
        RESOURCE.write_text(tsv, encoding="utf-8")
    document = mapping_document(mapping)
    (output / "gtm_runtime_mappings.json").write_bytes(encoded(document))
    java_result = archive(output / "GTM_Runtime_128_Java.zip", java)
    bed_result = archive(output / "GTM_Runtime_128_Bedrock.mcpack", bed)
    report = {"profile": PROFILE, "target_java": "26.3", "java_resource_format": [97, 1],
        "passed": True, "checks": checks, "packs": [java_result, bed_result],
        "catalogue_entries": len(rows), "catalogue_sha256": digest(tsv.encode()),
        "catalogue_provenance": dict(Counter(row[4] for row in rows.values())),
        "mapping_sha256": digest(encoded(document)), "base_java_sha256": digest(java_base.read_bytes()),
        "bedrock_base_count": len(bedrock_bases), "world_textures_overlaid": len(world_paths),
        "repaired_missing_phone_models": repaired_phone_models,
        "existing_custom_model_data_adapters": list(legacy_models.values()),
        "geysers_custom_item_contract": "https://geysermc.org/wiki/geyser/custom-items/",
        "legacy_compatibility_policy": "Retain exact IDs and geometry when no semantically identical native128 ID exists. No ordinal migration.",
        "finish_entitlements": "Actual runtime IDs *_01 through *_75 remain unchanged. Creative zero-based migration proposals are not applied.",
        "installation": "not_installed", "feature_flags": "unchanged", "world_placement": "not_applied",
        "client_verification": "not_run", "unique_design_counts": {"primary": 509, "additional_base_models": 69,
            "road_damage_variants": 195, "new_cosmetic_variants": 300, "legacy_assets": "compatibility reuse, not new designs"}}
    (output / "runtime-pack-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/runtime-packs")
    parser.add_argument("--art", type=Path, default=ROOT / "creative/generated_128")
    parser.add_argument("--java-base", type=Path, default=ROOT / "resource-pack/EXPECT_SDCRAFT_ResourcePack_26.3.zip")
    parser.add_argument("--bedrock-base", type=Path, action="append", default=[])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write-resource", action="store_true")
    group.add_argument("--check-resource", action="store_true")
    args = parser.parse_args()
    report = build(args.output, args.art, args.java_base, args.bedrock_base, args.write_resource, args.check_resource)
    print(json.dumps({"passed": report["passed"], "catalogue_entries": report["catalogue_entries"], "checks": report["checks"], "packs": report["packs"]}, indent=2))


if __name__ == "__main__":
    main()
