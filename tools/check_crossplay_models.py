#!/usr/bin/env python3
"""Fail closed if the published Java model, Bedrock mapping or render asset is missing.

This checks generated resources, not screenshots or theoretical model names.
It does not certify a running Geyser instance or Bedrock ItemDisplay rendering.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from zipfile import ZipFile

REQUIRED_PHONE = (
    "app_quoggle app_amazzo app_flippit app_arkpay app_zomatoo app_swiffy "
    "app_fashion app_property app_car_app app_maps app_garage app_bank "
    "app_loans app_taxi app_transport app_news app_police app_medical "
    "app_events app_missions app_careers app_contacts app_keys app_settings "
    "hud_phone_shortcut hud_hotbar_frame hud_notification_frame"
).split()


def check(java_path: Path, bedrock_path: Path, mapping_path: Path) -> dict:
    errors = []
    mappings = json.loads(mapping_path.read_text(encoding="utf-8"))
    if mappings.get("format_version") != 2:
        errors.append("Bedrock item mappings are not Geyser v2")
    definitions = {}
    for base, entries in mappings.get("items", {}).items():
        for item in entries:
            if item.get("type") != "definition":
                continue
            key = (base, item.get("model"))
            if key in definitions:
                errors.append("Duplicate Java base/model pair: " + str(key))
            definitions[key] = item

    with ZipFile(java_path) as java, ZipFile(bedrock_path) as bedrock:
        java_files = set(java.namelist())
        bedrock_files = set(bedrock.namelist())
        texture_index = json.loads(bedrock.read("textures/item_texture.json"))["texture_data"]
        attachables = {}
        geometry = set()
        for name in bedrock_files:
            if name.startswith("models/") and name.endswith(".json"):
                for record in json.loads(bedrock.read(name)).get("minecraft:geometry", []):
                    geometry.add(record["description"]["identifier"])
            if name.startswith("attachables/") and name.endswith(".json"):
                record = json.loads(bedrock.read(name))["minecraft:attachable"]["description"]
                ident = record["identifier"]
                if ident in attachables:
                    errors.append("Duplicate Bedrock attachable: " + ident)
                attachables[ident] = record
                for tex in record.get("textures", {}).values():
                    if tex + ".png" not in bedrock_files:
                        errors.append("Missing attachable PNG: " + ident + " -> " + tex)

        for ident, record in attachables.items():
            for geo in record.get("geometry", {}).values():
                if geo not in geometry:
                    errors.append("Missing Bedrock geometry: " + ident + " -> " + geo)

        for (base, model), item in definitions.items():
            if not isinstance(model, str) or model.count(":") != 1:
                errors.append("Invalid Java item_model key: " + str(model))
                continue
            namespace, path = model.split(":", 1)
            definition = f"assets/{namespace}/items/{path}.json"
            if definition not in java_files:
                errors.append("Missing Java item definition: " + definition)
                continue
            item_json = json.loads(java.read(definition))
            ref = item_json.get("model", {}).get("model")
            if not isinstance(ref, str) or ref.count(":") != 1:
                errors.append("Missing Java model reference: " + definition)
                continue
            ref_namespace, ref_path = ref.split(":", 1)
            model_json = f"assets/{ref_namespace}/models/{ref_path}.json"
            if model_json not in java_files:
                errors.append("Missing Java model file: " + model_json)

            bed_id = item.get("bedrock_identifier")
            if bed_id not in attachables:
                errors.append("Missing Bedrock attachable: " + str(bed_id))
            icon = item.get("bedrock_options", {}).get("icon")
            value = texture_index.get(icon)
            if not isinstance(value, dict):
                errors.append("Missing Bedrock item icon: " + str(icon))
                continue
            paths = value.get("textures")
            paths = [paths] if isinstance(paths, str) else paths
            if not isinstance(paths, list) or not paths or any(
                not isinstance(t, str) or t + ".png" not in bedrock_files for t in paths
            ):
                errors.append("Missing Bedrock item icon PNG: " + str(icon))

        for name in REQUIRED_PHONE:
            key = ("minecraft:paper", "gtm:" + name)
            if key not in definitions:
                errors.append("Phone model is not mapped from PAPER: " + name)

        if len(definitions) < 3000:
            errors.append(f"Too few mapped models: {len(definitions)}")

    report = {
        "schema": "GTM_CROSSPLAY_MODEL_AUDIT_V1",
        "status": "PASS" if not errors else "FAIL",
        "mapped_models": len(definitions),
        "bedrock_attachables": len(attachables),
        "bedrock_geometry_identifiers": len(geometry),
        "required_phone_model_ids": len(REQUIRED_PHONE),
        "errors": errors[:100],
        "note": "Static asset references only; Bedrock display entity runtime requires separate acceptance.",
    }
    if errors:
        raise ValueError(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--java", type=Path, default=Path("build/crossplay-release/resourcepacks/GTM_Repair_128_Java.zip"))
    parser.add_argument("--bedrock", type=Path, default=Path("build/crossplay-release/plugins/Geyser-Spigot/packs/GTM_Repair_128_Bedrock.mcpack"))
    parser.add_argument("--mappings", type=Path, default=Path("build/crossplay-release/plugins/Geyser-Spigot/custom_mappings/gtm_native128.json"))
    args = parser.parse_args()
    print(json.dumps(check(args.java, args.bedrock, args.mappings), indent=2))
