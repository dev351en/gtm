#!/usr/bin/env python3
"""Correct the measured traditional-auto canopy clearance, not its seat or chassis.

The native 26.3 client exposed the original 1.7875-block roof intersecting the
seated avatar's head. Only the intact canopy and four posts in this one model's
normal/damaged/critical art states change. Wreck art remains intentionally
collapsed. Input hashes, runtime-profile readback and explicit path sets keep
this repair bounded and reject an accidental second application.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "runtime/functional-r4/plugins/SDCraftCore-1.0.3-r4-functional-candidate.jar"
PROFILE_RESOURCE = ROOT / "hotfix/src/main/resources/vehicle/road-profiles.tsv"
PROFILE_PATH = "vehicle/road-profiles.tsv"
MODEL_ID = "gtm:rickshaw_traditional"
RAISE_BLOCKS = 0.45
COLLISION_MAX_Y = 2.238  # Round up the model's 2.237512 rendered maximum.
STATES = {"normal": ("", 1.179), "damaged": ("_damaged", 1.179), "critical": ("_critical", 1.196)}
POST_NAMES = frozenset("part_" + str(n) for n in range(6, 10))
PART_NAMES = POST_NAMES | {"part_10"}
BASE_PROFILE_SHA256 = "afa52bcf660a03ee1fb0506b21a186f797a8cad6ed881c1cb0529b092bc0ce31"
SOURCE_SHA256 = {
    "assets/gtm/models/item/rickshaw_traditional.json": "2128acf1cbd5b6e58011d8e596c3effd6be4d8d74d475101a3736a593aaee8fe",
    "assets/gtm/models/item/rickshaw_traditional_critical.json": "62157e17454b49fabd4f8341baced023e77b85250c3f8015305de86def840cff",
    "assets/gtm/models/item/rickshaw_traditional_damaged.json": "0709193a49882ceafae9569e2bebb92192a59a876b79a273caa3bf444bde37cf",
    "assets/gtm/models/item/vt_rickshaw_traditional_critical_body.json": "65fbacaebbd3bbfab5689be8b00d36350519ab13bf78fca3e16e6aac4dc0dadd",
    "assets/gtm/models/item/vt_rickshaw_traditional_damaged_body.json": "3d7fe928669f01ef72ad857951d78dce7f568eedcd5d4a124f213506e370166e",
    "assets/gtm/models/item/vt_rickshaw_traditional_normal_body.json": "0dc9833996baf2bbbee0a27d9b26f5cb11d67d1e58d8ca1ac8848d219e42b1d5",
    "models/entity/rd/rickshaw_traditional.geo.json": "4be63a9baede971397960090d045938b840e10a62bb8c9c8b5757504190f7cea",
    "models/entity/rd/rickshaw_traditional_critical.geo.json": "cf3e6f82ee8d47a9e9683862ba92c8e8f3fb9f5e4454a292e50d265766dfd247",
    "models/entity/rd/rickshaw_traditional_damaged.geo.json": "1ccc238deb35f8e1709185377121a1702f81e319de3a975f3dbb4ad8928a0f80",
    "models/entity/rd/vt_rickshaw_traditional_critical_body.geo.json": "748d30e18e100fdf46cc2fa4fed949fe50c2e8bde7bdc72a2a715bd50092b4f5",
    "models/entity/rd/vt_rickshaw_traditional_damaged_body.geo.json": "688f099d797417494b88b4c38d2d296959ccb1ea3fc4d5f017c42343c6e03f07",
    "models/entity/rd/vt_rickshaw_traditional_normal_body.geo.json": "38fed5b299965bfcc0443effee26e10b86a0e4b36ac9dc1cbb32111a9b4bfee1",
    "models/entity/rickshaw_traditional.geo.json": "2f3079ee1509ba2193bb94ca0b4a01b92b7c1a8a327c65299ced553df79eb53d",
    "models/entity/rickshaw_traditional_critical.geo.json": "84f8cde1f59dabf0461a9b9f3bc4a977fb8b4241802e5e11b48e13ec12dfd62c",
    "models/entity/rickshaw_traditional_damaged.geo.json": "fe48a11114ba414a8ebdeeeaf82aa8ff5c2d8feac1f3ca517decb726c798c0af",
    "models/entity/rt/vt_rickshaw_traditional_critical_body.geo.json": "2b5ebd6440338d588e46369a9eb0f60f7729ff102e329bb5953d2a72a643611b",
    "models/entity/rt/vt_rickshaw_traditional_damaged_body.geo.json": "06544b144f84d5352e76b0279804360e451700aaf29da8a981c89b8fe8a49d7b",
    "models/entity/rt/vt_rickshaw_traditional_normal_body.geo.json": "aa358800c723b3d1f8b0f6bd2c256dd059adfc8d67fd59400cca17e7e48452bb",
}
JAVA_PATHS = frozenset(path for path in SOURCE_SHA256 if path.startswith("assets/"))
BEDROCK_PATHS = frozenset(SOURCE_SHA256) - JAVA_PATHS


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def encoded(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def repaired_profile(original: bytes, geometry_sha256: str) -> bytes:
    if sha(original) != BASE_PROFILE_SHA256:
        raise ValueError("Unexpected source vehicle profiles; canopy correction was not applied")
    lines = original.decode("utf-8").splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.startswith(MODEL_ID + "\t")]
    if len(matches) != 1:
        raise ValueError("Traditional auto profile is not unique")
    index = matches[0]
    row = lines[index].rstrip("\r\n").split("\t")
    if len(row) != 13 or row[5] != "-0.65,0,-1.3,0.65,1.7875,1.3":
        raise ValueError("Traditional auto collision schema changed")
    row[5] = "-0.65,0,-1.3,0.65," + str(COLLISION_MAX_Y) + ",1.3"
    row[12] = (geometry_sha256 + "|" + row[12].split("|", 1)[1]
               + "; repair104 canopy +0.45 block; SHA-256 of packed normal Bedrock geometry")
    lines[index] = "\t".join(row) + ("\r\n" if lines[index].endswith("\r\n") else "\n")
    return "".join(lines).encode("utf-8")


def _java_model(original: dict, rise: float) -> dict:
    result = deepcopy(original)
    found = []
    for part in result["elements"]:
        name = part.get("name")
        if name not in PART_NAMES:
            continue
        if part.get("rotation"):
            raise ValueError("Canopy/post axes changed")
        found.append(name)
        part["to"][1] = round(part["to"][1] + rise, 6)
        if name == "part_10":
            part["from"][1] = round(part["from"][1] + rise, 6)
    if sorted(found) != sorted(PART_NAMES):
        raise ValueError("Expected one canopy and four posts")
    return result


def _raw_geometry(original: dict) -> dict:
    result = deepcopy(original)
    geometries = result["minecraft:geometry"]
    if len(geometries) != 1:
        raise ValueError("Unexpected traditional auto geometry count")
    geometry = geometries[0]
    chassis = [bone for bone in geometry["bones"] if bone["name"] == "chassis"]
    if len(chassis) != 1:
        raise ValueError("Missing traditional auto chassis")
    posts = roof = 0
    for cube in chassis[0]["cubes"]:
        origin, size = cube["origin"], cube["size"]
        if (origin[0], origin[2]) in {(-9.286, -18.022), (-9.286, 7.77), (8.186, -18.022), (8.186, 7.77)}:
            if size[0] != 1.1 or size[2] != 1.1 or cube.get("rotation"):
                raise ValueError("Unexpected traditional auto support post")
            size[1] = round(size[1] + RAISE_BLOCKS * 16, 6)
            posts += 1
        elif origin == [-9.984, 26.2, -18.304] and size == [19.968, 2.4, 29.952]:
            origin[1] = round(origin[1] + RAISE_BLOCKS * 16, 6)
            roof += 1
    if posts != 4 or roof != 1:
        raise ValueError("Expected four source posts and one intact canopy")
    description = geometry["description"]
    description["visible_bounds_height"] = round(description["visible_bounds_height"] + RAISE_BLOCKS, 6)
    description["visible_bounds_offset"][1] = round(description["visible_bounds_offset"][1] + RAISE_BLOCKS / 2, 6)
    return result


def _display_geometry(original: dict, java: dict, rise: float) -> dict:
    result = deepcopy(original)
    bones = result["minecraft:geometry"][0]["bones"]
    if len(bones) != 1 or bones[0]["name"] != "item":
        raise ValueError("Unexpected display-bridge geometry")
    cubes = bones[0]["cubes"]
    if len(cubes) != len(java["elements"]):
        raise ValueError("Display-bridge geometry disagrees with Java element count")
    for cube, part in zip(cubes, java["elements"]):
        if part.get("name") not in PART_NAMES:
            continue
        if (abs(cube["origin"][1] - (part["from"][1] - 8)) > 1e-6
                or abs(cube["size"][1] - (part["to"][1] - part["from"][1])) > 1e-6):
            raise ValueError("Display-bridge canopy coordinates changed")
        if part["name"] == "part_10":
            cube["origin"][1] = round(cube["origin"][1] + rise, 6)
        else:
            cube["size"][1] = round(cube["size"][1] + rise, 6)
    return result


def build_plan(java: dict[str, bytes], bedrock: dict[str, bytes]) -> tuple[dict, dict, bytes, dict]:
    """Calculate the repair without mutating packs or writing the profile."""
    for name, expected in SOURCE_SHA256.items():
        source = java if name in JAVA_PATHS else bedrock
        if name not in source or sha(source[name]) != expected:
            raise ValueError("Unexpected or already-repaired canopy input: " + name)
    java_changes, bedrock_changes = {}, {}
    for state, (suffix, scale) in STATES.items():
        for name in ("rickshaw_traditional" + suffix, "vt_rickshaw_traditional_" + state + "_body"):
            java_path = "assets/gtm/models/item/" + name + ".json"
            original = json.loads(java[java_path])
            rise = RAISE_BLOCKS * 16 / scale
            java_changes[java_path] = encoded(_java_model(original, rise))
            raw_path = "models/entity/" + ("rt/" if name.startswith("vt_") else "") + name + ".geo.json"
            bedrock_changes[raw_path] = encoded(_raw_geometry(json.loads(bedrock[raw_path])))
            display_path = "models/entity/rd/" + name + ".geo.json"
            bedrock_changes[display_path] = encoded(_display_geometry(json.loads(bedrock[display_path]), original, rise))
    if set(java_changes) != JAVA_PATHS or set(bedrock_changes) != BEDROCK_PATHS:
        raise ValueError("Canopy repair exceeded its explicit path boundary")
    geometry_sha = sha(bedrock_changes["models/entity/rickshaw_traditional.geo.json"])
    with ZipFile(CORE) as jar:
        profile = repaired_profile(jar.read(PROFILE_PATH), geometry_sha)
    # Actual 26.3 client constants: root lift 1.501, player scale 0.9375,
    # helmet cube y=-9..1,z=-5..5. Include the higher rear seat (.65-.6).
    head_max = 0.05 + 0.9375 * (1.501 + math.hypot(9, 5) / 16)
    report = {"model": MODEL_ID, "raise_blocks": RAISE_BLOCKS, "states": list(STATES),
              "java_models": sorted(JAVA_PATHS), "bedrock_geometries": sorted(BEDROCK_PATHS),
              "collision_max_y": COLLISION_MAX_Y, "roof_underside_y": 26.2 / 16 + RAISE_BLOCKS,
              "seated_head_with_helmet_max_y": round(head_max, 6),
              "minimum_head_clearance_blocks": round(26.2 / 16 + RAISE_BLOCKS - head_max, 6),
              "normal_geometry_sha256": geometry_sha, "profile_resource_sha256": sha(profile),
              "preserved": ["all seat coordinates", "driving parameters", "all wheel geometry and pivots",
                            "all model IDs", "all texture bytes and UVs", "wreck art", "other 86 profiles"]}
    return java_changes, bedrock_changes, profile, report


def repair_packs(java: dict[str, bytes], bedrock: dict[str, bytes]) -> dict:
    java_changes, bedrock_changes, profile, report = build_plan(java, bedrock)
    if not PROFILE_RESOURCE.is_file() or PROFILE_RESOURCE.read_bytes() != profile:
        raise ValueError("Maintained runtime profile does not match the repaired canopy geometry")
    java.update(java_changes)
    bedrock.update(bedrock_changes)
    return report
