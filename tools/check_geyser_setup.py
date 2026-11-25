#!/usr/bin/env python3
"""Read-only asset preflight for an existing Paper/Geyser GTM server.

Do not mistake successful asset paths for proof that Bedrock rendered a
moving ItemDisplay entity. A compatible Geyser renderer must be checked
on an actual Bedrock client separately.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile

BEDROCK_PACK = "plugins/Geyser-Spigot/packs/GTM_Repair_128_Bedrock.mcpack"
BEDROCK_MAP = "plugins/Geyser-Spigot/custom_mappings/gtm_native128.json"
JAVA_PACK = "resourcepacks/GTM_Repair_128_Java.zip"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect(server: Path) -> dict:
    server = server.resolve(strict=True)
    config = server / "plugins/Geyser-Spigot/config.yml"
    props = server / "server.properties"
    warnings = []
    blockers = []
    if not (server / "plugins/Geyser-Spigot").is_dir():
        blockers.append("Geyser-Spigot is not installed on this server")
    enabled = None
    if config.is_file():
        cfg = config.read_text(encoding="utf-8-sig", errors="replace")
        found = re.findall(r"(?mi)^\s*enable-custom-content:\s*(true|false)\b", cfg)
        if len(found) == 1:
            enabled = found[0].lower() == "true"
        if enabled is not True:
            blockers.append("Set enable-custom-content: true in Geyser config.yml and restart")
    else:
        blockers.append("Missing Geyser config.yml")

    files = {}
    for name in (JAVA_PACK, BEDROCK_PACK, BEDROCK_MAP):
        f = server / name
        files[name] = {
            "exists": f.is_file(),
            "size": f.stat().st_size if f.is_file() else 0,
            "sha256": sha256(f) if f.is_file() else None,
        }
        if not f.is_file():
            blockers.append("Missing GTM pack/mapping: " + name)
    if props.is_file():
        rows = {}
        for raw in props.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            if "=" in raw and not raw.strip().startswith("#"):
                k, v = raw.split("=", 1)
                rows[k.strip()] = v.strip()
        if not rows.get("resource-pack") or not rows.get("resource-pack-sha1"):
            blockers.append("Java server resource-pack URL and SHA-1 are not configured")
    else:
        blockers.append("Missing server.properties")

    renderer = server / "plugins/Geyser-Spigot/extensions"
    extensions = sorted(p.name for p in renderer.glob("*.jar")) if renderer.is_dir() else []
    display_renderers = [n for n in extensions if "displayentity" in n.lower()]
    if not display_renderers:
        warnings.append(
            "Bedrock cannot natively render Java ItemDisplay vehicles/furniture. "
            "A compatible server-side Geyser display renderer must be installed and live-tested."
        )
    else:
        warnings.append(
            "Found a display extension, but binary compatibility and geometry/animation "
            "are not verified until an actual Bedrock join and drive test."
        )

    return {
        "schema": "GTM_CROSSPLAY_SETUP_PREFLIGHT_V1",
        "server": str(server),
        "item_models_configured": enabled is True and
            files[BEDROCK_PACK]["exists"] and files[BEDROCK_MAP]["exists"],
        "display_extensions_found": display_renderers,
        "files": files,
        "status": "CONFIG_READY_NOT_CLIENT_CERTIFIED" if not blockers else "NEEDS_SETUP",
        "blockers": blockers,
        "warnings": warnings,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("server", type=Path, help="Path to the server containing server.properties")
    args = p.parse_args()
    try:
        report = inspect(args.server)
        print(json.dumps(report, indent=2))
        sys.exit(0 if not report["blockers"] else 2)
    except (OSError, ValueError) as exc:
        print("GTM asset preflight failed: " + str(exc), file=sys.stderr)
        sys.exit(2)
