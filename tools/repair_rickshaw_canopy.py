#!/usr/bin/env python3
"""Measured traditional-auto canopy and four-seat repair, using existing art.

The native 26.3 client exposed the original 1.7875-block roof intersecting the
seated avatar's head. Retain that .45-block lift; widen the existing rear bench,
body and canopy by .84 block, with posts/rear wheels moved .42 each side, for
three passengers plus the driver. Keep textures, UVs, IDs, depth and handling.
Wreck height remains collapsed. Exact hashes reject drift/repeated application.
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
ANIMATION_RESOURCE = ROOT / "hotfix/src/main/resources/vehicle/animated-parts.tsv"
PROFILE_PATH = "vehicle/road-profiles.tsv"
ANIMATION_PATH = "vehicle/animated-parts.tsv"
MODEL_ID = "gtm:rickshaw_traditional"
EXISTING_FRONT_PASSENGERS = {
    "gtm:emerg_police_suv": "driver:driver:-0.47,0.68,0.24",
    "gtm:emerg_patrol_sedan": "driver:driver:-0.42,0.54,0.2",
}
RAISE_BLOCKS = 0.45
WIDEN_PER_SIDE_BLOCKS = 0.42
PASSENGER_X = (-0.6, 0.6, 0.0)  # Retain existing left/right indices; append centre.
COLLISION_HALF_WIDTH = 1.07
COLLISION_MAX_Y = 2.238  # Round up the model's 2.237512 rendered maximum.
STATES = {"normal": ("", 1.179), "damaged": ("_damaged", 1.179), "critical": ("_critical", 1.196), "wreck": ("_wreck", 1.196)}
POST_NAMES = frozenset("part_" + str(n) for n in range(6, 10))
PART_NAMES = POST_NAMES | {"part_0", "part_3", "part_3_retained_shell", "part_3_crumpled_front", "part_5", "part_10"}
BASE_PROFILE_SHA256 = "afa52bcf660a03ee1fb0506b21a186f797a8cad6ed881c1cb0529b092bc0ce31"
BASE_ANIMATION_SHA256 = "3e979771f19c5fc148f48ef1c52ee4af862ddf8e2d8e61284a71d3c0d0567c87"
SOURCE_SHA256 = json.loads((ROOT / "hotfix/vehicle-geometry-source-hashes.json").read_text())
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
    row[5] = f"-{COLLISION_HALF_WIDTH},0,-1.3,{COLLISION_HALF_WIDTH},{COLLISION_MAX_Y},1.3"
    row[6] = ("driver:driver:0,0.60625,0.208;rear_left:passenger:-0.6,0.65,-0.624;"
              "rear_right:passenger:0.6,0.65,-0.624;rear_center:passenger:0,0.65,-0.624")
    row[12] = (geometry_sha256 + "|authored driver cushion and widened existing rear bench; "
               "repair105 driver +3 passengers, rear body/canopy +0.84 block wide and canopy +0.45 high; "
               "SHA-256 of packed normal Bedrock geometry")
    lines[index] = "\t".join(row) + ("\r\n" if lines[index].endswith("\r\n") else "\n")
    for model, driver in EXISTING_FRONT_PASSENGERS.items():
        found = [i for i, line in enumerate(lines) if line.startswith(model + "\t")]
        if len(found) != 1:
            raise ValueError("Existing two-cushion emergency car is not unique")
        at = found[0]
        current = lines[at].rstrip("\r\n").split("\t")
        if len(current) != 13 or current[6] != driver:
            raise ValueError("Emergency car driver's authored anchor changed")
        point = driver.rsplit(":", 1)[1].split(",")
        point[0] = point[0].removeprefix("-")
        current[6] += ";front_passenger:passenger:" + ",".join(point)
        current[12] += "; repair105 enables existing opposite front leather cushion; original geometry retained"
        lines[at] = "\t".join(current) + ("\r\n" if lines[at].endswith("\r\n") else "\n")
    return "".join(lines).encode("utf-8")


def repaired_animations(original: bytes) -> bytes:
    if sha(original) != BASE_ANIMATION_SHA256:
        raise ValueError("Unexpected source vehicle articulation")
    lines, changed = original.decode().splitlines(keepends=True), 0
    for index, line in enumerate(lines):
        row = line.rstrip("\r\n").split("\t")
        if len(row) != 8 or row[0] != MODEL_ID or row[2] not in {"wheel_rl", "wheel_rr"}:
            continue
        pivot = [float(n) for n in row[5].split(",")]
        expected = -.546 if row[2] == "wheel_rl" else .546
        if pivot != [expected, .2, -.78] or row[1] not in STATES or row[4] != "X":
            raise ValueError("Unexpected traditional-auto wheel pivot")
        pivot[0] += math.copysign(WIDEN_PER_SIDE_BLOCKS, expected)
        row[5] = ",".join(format(n, ".6g") for n in pivot)
        lines[index] = "\t".join(row) + ("\r\n" if line.endswith("\r\n") else "\n")
        changed += 1
    if changed != 8:
        raise ValueError("Expected two rear wheel pivots in each of four art states")
    return "".join(lines).encode()


def _java_model(original: dict, scale: float, state: str) -> dict:
    result = deepcopy(original)
    widen = WIDEN_PER_SIDE_BLOCKS * 16 / scale
    rise = RAISE_BLOCKS * 16 / scale if state != "wreck" else 0
    changed = 0
    for part in result["elements"]:
        name = part.get("name", "")
        low, high = part["from"], part["to"]
        if name in {"part_0", "part_3", "part_3_retained_shell", "part_3_crumpled_front", "part_5", "part_10"}:
            if part.get("rotation"):
                raise ValueError("Rear cabin axes changed")
            low[0], high[0] = round(low[0] - widen, 6), round(high[0] + widen, 6)
        elif name in POST_NAMES:
            shift = -widen if name in {"part_6", "part_7"} else widen
            low[0], high[0] = round(low[0] + shift, 6), round(high[0] + shift, 6)
        elif name in {"tire_v", "tire_h", "tire_d", "rim"} and (low[2] + high[2]) / 2 < 8:
            # Preserve the tyre/rim shape; shift only the rear mesh and pivot.
            shift = -widen if (low[0] + high[0]) / 2 < 8 else widen
            low[0], high[0] = round(low[0] + shift, 6), round(high[0] + shift, 6)
            if part.get("rotation"):
                part["rotation"]["origin"][0] = round(part["rotation"]["origin"][0] + shift, 6)
        else:
            continue
        if name in POST_NAMES:
            high[1] = round(high[1] + rise, 6)
        elif name == "part_10":
            low[1], high[1] = round(low[1] + rise, 6), round(high[1] + rise, 6)
        changed += 1
    if not changed:
        raise ValueError("No reviewed traditional-auto component was found")
    return result


def _raw_geometry(original: dict, before: dict, after: dict, scale: float, state: str) -> dict:
    result = deepcopy(original)
    geometries = result["minecraft:geometry"]
    if len(geometries) != 1:
        raise ValueError("Unexpected traditional auto geometry count")
    geometry = geometries[0]
    cubes = [cube for bone in geometry["bones"] for cube in bone.get("cubes", [])]
    if len(cubes) != len(before["elements"]):
        raise ValueError("Raw geometry disagrees with source Java component count")
    translation = [0, scale * 8, -.017 * 16 if state in {"normal", "damaged"} else 0]
    for cube, old, new in zip(cubes, before["elements"], after["elements"]):
        if old == new:
            continue
        for axis in range(3):
            if abs(cube["origin"][axis] - ((old["from"][axis] - 8) * scale + translation[axis])) > .003:
                raise ValueError("Raw geometry coordinate transform changed")
            cube["origin"][axis] = round(cube["origin"][axis] + (new["from"][axis] - old["from"][axis]) * scale, 6)
            cube["size"][axis] = round(cube["size"][axis]
                + (new["to"][axis] - new["from"][axis] - old["to"][axis] + old["from"][axis]) * scale, 6)
        if cube.get("pivot") and old.get("rotation"):
            for axis in range(3):
                cube["pivot"][axis] = round(cube["pivot"][axis]
                    + (new["rotation"]["origin"][axis] - old["rotation"]["origin"][axis]) * scale, 6)
    for bone in geometry["bones"]:
        if bone["name"] in {"wheel_rl", "wheel_rr"}:
            expected = -8.736 if bone["name"] == "wheel_rl" else 8.736
            if bone["pivot"] != [expected, 3.2, -12.48]:
                raise ValueError("Rear wheel bone pivot changed")
            bone["pivot"][0] = round(expected + math.copysign(WIDEN_PER_SIDE_BLOCKS * 16, expected), 6)
    if state != "wreck":
        description = geometry["description"]
        description["visible_bounds_height"] = round(description["visible_bounds_height"] + RAISE_BLOCKS, 6)
        description["visible_bounds_offset"][1] = round(description["visible_bounds_offset"][1] + RAISE_BLOCKS / 2, 6)
    return result


def _display_geometry(original: dict, before: dict, after: dict) -> dict:
    result = deepcopy(original)
    bones = result["minecraft:geometry"][0]["bones"]
    if len(bones) != 1 or bones[0]["name"] != "item":
        raise ValueError("Unexpected display-bridge geometry")
    cubes = bones[0]["cubes"]
    if len(cubes) != len(before["elements"]):
        raise ValueError("Display-bridge geometry disagrees with Java element count")
    for cube, old, new in zip(cubes, before["elements"], after["elements"]):
        for axis in range(3):
            # Geyser's display export mirrors Java X: lowX = 8 - Java highX.
            # Y/Z retain the item-origin subtraction. Using Java lowX here
            # would put an outward-moving left wheel on the wrong side.
            expected = 8 - old["to"][axis] if axis == 0 else old["from"][axis] - 8
            if (abs(cube["origin"][axis] - expected) > 1e-6
                    or abs(cube["size"][axis] - (old["to"][axis] - old["from"][axis])) > 1e-6):
                raise ValueError("Display-bridge source coordinates changed")
            shift = old["to"][axis] - new["to"][axis] if axis == 0 else new["from"][axis] - old["from"][axis]
            growth = new["to"][axis] - new["from"][axis] - old["to"][axis] + old["from"][axis]
            if abs(shift) > 1e-9:
                cube["origin"][axis] = round(cube["origin"][axis] + shift, 6)
            if abs(growth) > 1e-9:
                cube["size"][axis] = round(cube["size"][axis] + growth, 6)
        if cube.get("pivot") and old.get("rotation"):
            for axis in range(3):
                shift = new["rotation"]["origin"][axis] - old["rotation"]["origin"][axis]
                if abs(shift) > 1e-9:
                    cube["pivot"][axis] = round(cube["pivot"][axis] + (-shift if axis == 0 else shift), 6)
    return result


def build_plan(java: dict[str, bytes], bedrock: dict[str, bytes]) -> tuple[dict, dict, bytes, dict]:
    """Calculate the repair without mutating packs or writing the profile."""
    for name, expected in SOURCE_SHA256.items():
        source = java if name in JAVA_PATHS else bedrock
        if name not in source or sha(source[name]) != expected:
            raise ValueError("Unexpected or already-repaired canopy input: " + name)
    java_changes, bedrock_changes = {}, {}
    for state, (suffix, scale) in STATES.items():
        names = ["rickshaw_traditional" + suffix]
        names += ["vt_rickshaw_traditional_" + state + "_" + part for part in ("body", "wheel_rl", "wheel_rr")]
        for name in names:
            java_path = "assets/gtm/models/item/" + name + ".json"
            original = json.loads(java[java_path])
            corrected = _java_model(original, scale, state)
            java_changes[java_path] = encoded(corrected)
            raw_path = "models/entity/" + ("rt/" if name.startswith("vt_") else "") + name + ".geo.json"
            bedrock_changes[raw_path] = encoded(_raw_geometry(json.loads(bedrock[raw_path]), original, corrected, scale, state))
            display_path = "models/entity/rd/" + name + ".geo.json"
            bedrock_changes[display_path] = encoded(_display_geometry(json.loads(bedrock[display_path]), original, corrected))
    if set(java_changes) != JAVA_PATHS or set(bedrock_changes) != BEDROCK_PATHS:
        raise ValueError("Canopy repair exceeded its explicit path boundary")
    geometry_sha = sha(bedrock_changes["models/entity/rickshaw_traditional.geo.json"])
    with ZipFile(CORE) as jar:
        profile = repaired_profile(jar.read(PROFILE_PATH), geometry_sha)
        animation = repaired_animations(jar.read(ANIMATION_PATH))
    # Actual 26.3 client constants: root lift 1.501, player scale 0.9375,
    # helmet cube y=-9..1,z=-5..5. Include the higher rear seat (.65-.6).
    head_max = 0.05 + 0.9375 * (1.501 + math.hypot(9, 5) / 16)
    report = {"model": MODEL_ID, "raise_blocks": RAISE_BLOCKS, "states": list(STATES),
              "widen_per_side_blocks": WIDEN_PER_SIDE_BLOCKS,
              "rear_bench_width_blocks": 15.808 / 16 + 2 * WIDEN_PER_SIDE_BLOCKS,
              "seats": {"driver": 1, "passengers": 3, "total": 4, "rear_x": list(PASSENGER_X)},
              "existing_front_passenger_profiles_enabled": sorted(EXISTING_FRONT_PASSENGERS),
              "canopy_raised_states": [s for s in STATES if s != "wreck"],
              "java_models": sorted(JAVA_PATHS), "bedrock_geometries": sorted(BEDROCK_PATHS),
              "collision_half_width": COLLISION_HALF_WIDTH,
              "collision_max_y": COLLISION_MAX_Y, "roof_underside_y": 26.2 / 16 + RAISE_BLOCKS,
              "seated_head_with_helmet_max_y": round(head_max, 6),
              "minimum_head_clearance_blocks": round(26.2 / 16 + RAISE_BLOCKS - head_max, 6),
              "normal_geometry_sha256": geometry_sha, "profile_resource_sha256": sha(profile),
              "animation_resource_sha256": sha(animation),
              "preserved": ["driver and front wheel", "driving parameters", "wheel shape/radius/axis and vertical/depth pivots",
                            "all model IDs", "all texture bytes and UVs", "collapsed wreck height", "other 84 profiles"]}
    return java_changes, bedrock_changes, profile, report


def repair_packs(java: dict[str, bytes], bedrock: dict[str, bytes]) -> dict:
    java_changes, bedrock_changes, profile, report = build_plan(java, bedrock)
    with ZipFile(CORE) as jar:
        animation = repaired_animations(jar.read(ANIMATION_PATH))
    if not PROFILE_RESOURCE.is_file() or PROFILE_RESOURCE.read_bytes() != profile:
        raise ValueError("Maintained runtime profile does not match the four-seat auto geometry")
    if not ANIMATION_RESOURCE.is_file() or ANIMATION_RESOURCE.read_bytes() != animation:
        raise ValueError("Maintained rear-wheel pivots do not match the widened auto geometry")
    java.update(java_changes)
    bedrock.update(bedrock_changes)
    return report
