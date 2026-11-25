#!/usr/bin/env python3
"""Package only the verified server plugin, server packs, and rollback updater.

Never include a Fabric/Forge/NeoForge client JAR, world, database or secrets.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "GTM_Server_Only_Crossplay_1.0.7.zip"
PREFIX = "GTM_Server_Only_Crossplay_1.0.7/"
VERSION = "1.0.7-r4-crossplay-models"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def package(payload: Path, output: Path) -> dict:
    from install_runtime_repair import verify_payload
    payload = payload.resolve(strict=True)
    manifest, _ = verify_payload(payload)
    if manifest["version"] != VERSION:
        raise ValueError("Not a reviewed crossplay payload")
    required = {row["path"] for row in manifest["files"]}
    required.update({
        "repair-manifest.json", "build-report.json",
        "pack-repair-report.json", "install_runtime_repair.py",
        "Update-GTM.bat", "Update-GTM.sh", "README.md",
        "RELEASE_NOTES.md", "SERVER_ONLY_CROSSPLAY.md", "crossplay-model-audit.json",
    })
    forbidden = ("client/", ".minecraft/", "world/", "playerdata/", "secrets")
    entries: dict[str, Path] = {}
    for name in sorted(required):
        if any(term in name.lower() for term in forbidden):
            raise ValueError("Client or private data in server-only payload: " + name)
        path = payload / name
        if not path.is_file() or path.is_symlink() or path.resolve().parent != (payload / name).parent.resolve():
            raise ValueError("Missing/unsafe server-only release input: " + name)
        entries[name] = path
    output.mkdir(parents=True, exist_ok=True)
    target = output / NAME
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, path in sorted(entries.items()):
            zi = zipfile.ZipInfo(PREFIX + name, (2026, 11, 26, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o100644 << 16
            z.writestr(zi, path.read_bytes())
    with zipfile.ZipFile(target) as z:
        if z.testzip():
            raise ValueError("Corrupt crossplay ZIP")
        contents = z.namelist()
        if any("/client/" in x or "fabric" in x.lower() or "forge" in x.lower()
               for x in contents):
            raise ValueError("Client components accidentally bundled")
    report = {
        "schema": "GTM_SERVER_ONLY_CROSSPLAY_CANDIDATE_V1",
        "version": VERSION,
        "status": "BUILT_NOT_CROSSPLAY_ACCEPTED",
        "requires_client_mod": False,
        "java_bedrock_smoke_test": "PENDING_REAL_CLIENTS",
        "daytona_deployed": False,
        "zip": NAME,
        "sha256": sha256(target),
        "bytes": target.stat().st_size,
        "included": sorted(required),
    }
    (output / "crossplay-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    (output / "SHA256SUMS").write_text(
        sha256(target) + "  " + NAME + "\n", encoding="ascii"
    )
    return report


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--payload", type=Path, default=ROOT / "build/crossplay-release")
    p.add_argument("--output", type=Path, default=ROOT / "dist/crossplay")
    args = p.parse_args()
    print(json.dumps(package(args.payload, args.output), indent=2))
