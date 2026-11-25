#!/usr/bin/env python3
"""Read-only per-model capacity audit from preserved art and maintained profiles.

Up to date output requires rerunning this tool after a profile repair. It never
infers a passenger count from a real-world name or marketing description.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZipFile

import build_repaired_packs as packs
import repair_rickshaw_canopy as repair

ROOT = Path(__file__).resolve().parents[1]
ART_SHA = "877b8b095f5d479681ed1bf7b8475e9984b7b0adca4777fac8bcdb4b2b703d8a"
CAR_CATEGORIES = {"hatchback", "sedan", "suv", "luxury"}


def rows(data):
    return {r[0]: r for line in data.decode().splitlines() if line and not line.startswith("#")
            for r in [line.split("\t")]}


def seating(text):
    result = []
    for value in text.split(";") if text else []:
        name, role, point = value.split(":")
        result.append({"name": name, "role": role, "hip_blocks": [float(x) for x in point.split(",")]})
    return result


def audit():
    art_bytes = b"".join(p.read_bytes() for p in sorted((ROOT / "creative/delivery/GTM_Indraprastha_128_Assets.zip.parts").glob("part.*")))
    if hashlib.sha256(art_bytes).hexdigest() != ART_SHA:
        raise ValueError("Unknown editable art archive")
    art = ZipFile(BytesIO(art_bytes))
    bedrock = packs.read_bytes(packs.preserved_bytes("plugins/Geyser-Spigot/packs/GTM_Local_Bedrock.mcpack"))
    maintained = rows(repair.PROFILE_RESOURCE.read_bytes())
    with ZipFile(repair.CORE) as core:
        original = rows(core.read(repair.PROFILE_PATH))
    if set(maintained) != set(original) or len(maintained) != 87:
        raise ValueError("Vehicle identities changed")
    result = []
    for model, row in maintained.items():
        name = model.split(":", 1)[1]
        editable_path = "GTM_Indraprastha_128/source/models/transport/editable/" + name + ".parts.json"
        source = art.read(editable_path)
        editable = json.loads(source)
        raw_path = "models/entity/" + name + ".geo.json"
        geometry = json.loads(bedrock[raw_path])["minecraft:geometry"][0]
        parts = [(bn, part) for bn, bone in editable["bones"].items() for part in bone["parts"]]
        cubes = {bone["name"]: bone.get("cubes", []) for bone in geometry["bones"]}
        upholstery = []
        for bone, part in parts:
            if bone == "steering_wheel" or not part["mat"].startswith("leather_"):
                continue
            # Verify each identified editable cushion also exists in the
            # delivered runtime mesh; manifest labels alone are insufficient.
            if not any(c["origin"] == part["origin"] and c["size"] == part["size"] for c in cubes.get(bone, [])):
                raise ValueError("Editable/runtime cushion mismatch: " + model + "/" + part["name"])
            upholstery.append({"bone": bone, "part": part["name"], "material": part["mat"],
                               "origin_blocks": [n/16 for n in part["origin"]],
                               "size_blocks": [n/16 for n in part["size"]]})
        seats = seating(row[6])
        old_seats = seating(original[model][6])
        category = row[2]
        if model == repair.MODEL_ID:
            work = "Driver plus three passenger mounts implemented; existing bench/cabin widened .84 block and roof raised .45. Network occupancy evidence and native visual acceptance are separate checks."
            physical_places = 4
        elif category in CAR_CATEGORIES:
            if len(upholstery) != 2:
                raise ValueError("Civilian car seat-mesh assumption changed: " + model)
            work = "Two authored front seat cuboids only. Rear seating requires actual bench/cushion, hollow cabin, adult-avatar headroom and client validation; no rear capacity guessed."
            physical_places = 2
        elif category == "bus":
            if upholstery:
                raise ValueError("Bus interior assumption changed: " + model)
            work = "Exterior body/window shells; no passenger cushions or internal aisle. Requires an authored interior, measured seats/boarding doors and avatar headroom before passenger capacity can be claimed."
            physical_places = 0
        elif model in repair.EXISTING_FRONT_PASSENGERS:
            if len(upholstery) != 2:
                raise ValueError("Emergency front-seat assumption changed: " + model)
            work = "Existing opposite front cushion enabled as passenger; original driver, art and handling preserved. Rear cabin/headroom need separate client review."
            physical_places = 2
        elif category in {"motorcycle", "scooter"}:
            work = "One driver mount retained. Upholstery pieces form the authored saddle (Bullet pieces overlap); no distinct pillion place verified."
            physical_places = 1
        elif model == "gtm:rickshaw_electric":
            work = "Existing driver plus two rear passenger anchors retained; narrow bench and roof clearance require separate geometry/client review."
            physical_places = 3
        elif model == "gtm:rickshaw_cargo":
            work = "Driver-only cargo configuration retained; decorative rear upholstery is covered by cargo and is not an approved passenger place."
            physical_places = 1
        elif category == "agricultural":
            work = "Authored driver saddle retained; no separate passenger cushion verified."
            physical_places = 1
        elif category in {"commercial", "emergency"}:
            work = "Driver-only profile retained; no extra usable seat or hollow passenger interior established from the delivered geometry."
            physical_places = 0
        else:
            work = "Existing authored runtime anchors retained. No passenger-count increase; independent interior/boarding/clearance verification remains required."
            physical_places = None
        result.append({"id": model, "title": row[1], "category": category,
                       "runtime_total_seats": len(seats), "runtime_driver_seats": sum(s["role"] == "driver" for s in seats),
                       "runtime_passenger_seats": sum(s["role"] == "passenger" for s in seats),
                       "previous_runtime_total_seats": len(old_seats), "runtime_seat_anchors": seats,
                       "identified_upholstery_mesh_piece_count": len(upholstery),
                       "independently_identified_seating_places": physical_places,
                       "upholstery_meshes_in_preserved_art": upholstery,
                       "profile_bounds_blocks": [float(x) for x in row[5].split(",")],
                       "profile_geometry_provenance": row[12],
                       "preserved_geometry_path": raw_path, "preserved_geometry_sha256": hashlib.sha256(bedrock[raw_path]).hexdigest(),
                       "editable_source_path": editable_path, "editable_source_sha256": hashlib.sha256(source).hexdigest(),
                       "interior_work_and_limits": work})
    return {"schema": "GTM_VEHICLE_CAPACITY_AUDIT_V1", "model_count": len(result),
            "basis": "Preserved actual native128 meshes and editable component/material records, compared with maintained loaded profile TSV. No marketing/name capacity inference.",
            "mesh_count_caution": "Mesh-piece count is not passenger capacity: one bench can hold several players, overlapping saddle pieces form one seat, and some modes lack independently reviewed seating geometry.",
            "editable_archive_sha256": ART_SHA,
            "profile_resource_sha256": repair.sha(repair.PROFILE_RESOURCE.read_bytes()),
            "animation_resource_sha256": repair.sha(repair.ANIMATION_RESOURCE.read_bytes()),
            "driving_engine": {"implementation": "Custom server-authoritative SDCraftCore GtmVehicles/RoadPhysics on Paper26.3; not a separate GTA or rigid-body engine.",
                               "road_step_seconds": .05, "controls": "W/S throttle/brake-through-zero/reverse, A/D steering, Jump brake, Sneak safe exit.",
                               "movement": "Analytic longitudinal integration, bounded bicycle-arc steering, swept accepted movement/collision, fuel/health/odometer; one ArmorStand carrier per loaded seat.",
                               "passenger_follow": "Paper26.3 CraftEntity.teleport0 uses TeleportTransition.PassengerTeleportationMode.POSITION_RIDER; GtmVehicles transforms every carrier with the same accepted body pose.",
                               "limits": "Custom kinematic road model, not suspension/tyre/rigid-body simulation. Native driving checked previously on flat workshop terrain; no broad slope/terrain/Bedrock certification."},
            "models": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/repair-evidence/vehicle-capacity-audit.json")
    parser.add_argument("--csv", type=Path, default=ROOT / "docs/repair-evidence/vehicle-capacity-audit.csv")
    args = parser.parse_args()
    report = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    columns = ["id", "title", "category", "previous_runtime_total_seats", "runtime_total_seats", "runtime_driver_seats",
               "runtime_passenger_seats", "identified_upholstery_mesh_piece_count", "independently_identified_seating_places", "interior_work_and_limits"]
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, columns, extrasaction="ignore")
        writer.writeheader(); writer.writerows(report["models"])
    print("Capacity audit: 87 actual profiles; corrected auto4 seats and two existing emergency front passengers; car rear cabins/bus interiors remain incomplete.")


if __name__ == "__main__":
    main()
