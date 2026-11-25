#!/usr/bin/env python3
"""Package the verified runtime updater, never a private world or server data."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
UPDATE_NAME = "GTM_Runtime_Repair_1.0.4.zip"
JAVA_NAME = "GTM_Repair_128_Java.zip"
BEDROCK_NAME = "GTM_Repair_128_Bedrock.mcpack"
ASSETS = {UPDATE_NAME, JAVA_NAME, BEDROCK_NAME, "release-report.json", "SHA256SUMS"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package(payload: Path, output: Path) -> dict:
    from install_runtime_repair import verify_payload
    # Uses the same boundary validation as the updater before exposing bytes.
    verify_payload(payload)
    manifest = json.loads((payload / "repair-manifest.json").read_text())
    required = {row["path"] for row in manifest["files"]} | {
        "repair-manifest.json", "build-report.json", "pack-repair-report.json",
        "install_runtime_repair.py", "Update-GTM.bat", "Update-GTM.sh", "README.md", "RELEASE_NOTES.md",
        "RUNTIME_REPAIR_2026-11-25.md"}
    for name in required:
        file = payload / name
        if not file.is_file() or file.is_symlink(): raise ValueError("Missing release input: " + name)
    # Test reports are explicit allow-listed inputs; server logs and token files
    # are never collected by directory globbing.
    evidence = ROOT / "docs/repair-evidence"
    extras = {"evidence/" + p.name: p for p in evidence.glob("*.json") if p.is_file() and not p.is_symlink()}
    for name in ["phone-native-java.png", "jeeva-native-java.png", "kavach-held-native-java.png", "equipment-native-java.png",
                 "vehicle-native-java.png", "vehicle-driving-native-java.png",
                 "weapon-reloaded-native-java.png", "control-centre-login.jpg",
                 "phone-final-native-java.png", "vehicle-canopy-final.png"]:
        file = evidence / name
        if file.is_file() and not file.is_symlink(): extras["evidence/" + name] = file
    output.mkdir(parents=True, exist_ok=True)
    update = output / UPDATE_NAME
    with zipfile.ZipFile(update, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, file in sorted({**{n: payload / n for n in required}, **extras}.items()):
            info = zipfile.ZipInfo("GTM_Repair_1.0.4/" + name, (2026, 11, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, file.read_bytes())
    shutil.copyfile(payload / "resourcepacks" / JAVA_NAME, output / JAVA_NAME)
    shutil.copyfile(payload / "plugins/Geyser-Spigot/packs" / BEDROCK_NAME, output / BEDROCK_NAME)
    report = {"schema": "GTM_REPAIR_RELEASE_V1", "version": manifest["version"],
              "status": "PASS", "scope": "Verified installable update; no production deployment.",
              "pack_url": manifest["java_pack"]["url"],
              "files": {name: {"sha256": digest(output / name), "bytes": (output / name).stat().st_size}
                        for name in [UPDATE_NAME, JAVA_NAME, BEDROCK_NAME]}}
    (output / "release-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (output / "SHA256SUMS").write_text("".join(digest(output / name) + "  " + name + "\n"
                                              for name in sorted(ASSETS - {"SHA256SUMS"})), encoding="ascii")
    with zipfile.ZipFile(update) as z:
        if z.testzip(): raise ValueError("Update archive verification failed")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", type=Path, default=ROOT / "build/repaired-release")
    parser.add_argument("--output", type=Path, default=ROOT / "dist/repair")
    args = parser.parse_args()
    print(json.dumps(package(args.payload, args.output), indent=2))
