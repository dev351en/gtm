#!/usr/bin/env python3
"""Reconstruct and package the preserved functional payload, entirely offline.

This produces a runtime update payload, not a complete server or private-world
installer. Only explicitly manifested bytes are read. Existing outputs are
never replaced. Repository-relative .parts inputs are verified individually
and again as their complete reconstructed file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tempfile
from zipfile import BadZipFile, ZipFile, ZipInfo, ZIP_STORED

DEFAULT_MANIFEST = "runtime/functional-r4/manifest.json"
RUNTIME_ROOT = "runtime/functional-r4"
UPDATE_NAME = "GTM_Functional_Runtime_1.0.3.zip"
JAVA_NAME = "GTM_Runtime_128_Java.zip"
BEDROCK_NAME = "GTM_Runtime_128_Bedrock.mcpack"
ART_NAME = "GTM_Indraprastha_128_Assets.zip"
CONNECTOR_NAME = "GTM_Daytona_Laptop_Connector.zip"
CONNECTOR_FILES = ("Start-Daytona.bat", "connect_daytona_server.bat", "tools/daytona_tunnel.py", "docs/DAYTONA_LAPTOP_CONNECTION.md")
JAVA_PATH = "resourcepacks/GTM_Local_Java.zip"
BEDROCK_PATH = "plugins/Geyser-Spigot/packs/GTM_Local_Bedrock.mcpack"
PAYLOAD_FOLDER = "GTM_Functional_Runtime_1.0.3"
MAX_FILE = 1024 ** 3
MAX_TOTAL = 4 * 1024 ** 3
BLOCK = 1024 ** 2
RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
NOTICE = """GTM FUNCTIONAL RUNTIME 1.0.3 - VERIFIED UPDATE PAYLOAD

This archive contains the preserved functional core, resource packs, optional
Bedrock bridge, corresponding bridge source/license, launcher files, and evidence.
It is NOT a complete Paper server, a private-world export, or an automatic updater.
The local launcher files need the complete separately saved laptop package.

Do not extract this payload over a running server or replace accounts, UUIDs,
authentication stores, permissions, active configuration, or world data with it.
Use a coherent stopped backup and a reviewed staging update before deployment.
The latest core/launcher source was not recovered; older repository source does
not rebuild this binary. See runtime-manifest.json and the included documentation.

Opening the repository's Start-Daytona.bat connects to the existing running
Daytona server. It does not deploy this update. No Daytona operation is performed
by this archive or its offline assembler. Native Windows and live client checks
remain unverified. Model functions may need properties, supplies or setup.
"""


class AssemblyError(ValueError):
    pass


def safe_relative(value: str) -> str:
    if not isinstance(value, str) or not value or any(c in value for c in '\\:<>"|?*') or any(ord(c) < 32 for c in value):
        raise AssemblyError("Invalid manifest path")
    path = PurePosixPath(value)
    if path.is_absolute() or value != path.as_posix() or any(p in ("", ".", "..") for p in path.parts):
        raise AssemblyError("Absolute, ambiguous or escaping manifest path")
    for part in path.parts:
        if part.endswith((".", " ")) or part.split(".", 1)[0].upper() in RESERVED:
            raise AssemblyError("Manifest path is unsafe on Windows")
    return value


def input_file(repo: Path, relative: str) -> Path:
    relative = safe_relative(relative)
    target = repo
    for part in PurePosixPath(relative).parts:
        target = target / part
        if target.is_symlink():
            raise AssemblyError("Symlink input refused: " + relative)
    if not target.is_file():
        raise AssemblyError("Missing regular input: " + relative)
    if not target.resolve().is_relative_to(repo):
        raise AssemblyError("Input escaped repository")
    return target


def validate_record(record: dict):
    if not isinstance(record, dict):
        raise AssemblyError("Invalid file record")
    safe_relative(record.get("path"))
    if type(record.get("bytes")) is not int or not 0 <= record["bytes"] <= MAX_FILE:
        raise AssemblyError("Invalid file byte count")
    if not isinstance(record.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]):
        raise AssemblyError("Invalid SHA-256")
    if "git_sha" in record and not re.fullmatch(r"[0-9a-f]{40}", record["git_sha"]):
        raise AssemblyError("Invalid Git blob SHA")


def copy_verified(repo: Path, record: dict, destination: Path, default_source: str):
    validate_record(record)
    parts = record.get("parts")
    if parts is not None:
        if not isinstance(parts, list) or not 1 <= len(parts) <= 4096:
            raise AssemblyError("Invalid chunk list")
        for part in parts:
            validate_record(part)
        if sum(p["bytes"] for p in parts) != record["bytes"]:
            raise AssemblyError("Chunk sizes do not sum to the full file size")
        if len({p["path"].casefold() for p in parts}) != len(parts):
            raise AssemblyError("Repeated chunk path")
        inputs = [(part, part["path"]) for part in parts]
    else:
        source = record.get("source_repo_path", default_source)
        inputs = [(record, safe_relative(source))]
    full_hash = hashlib.sha256()
    git_hash = hashlib.sha1(f"blob {record['bytes']}\0".encode())
    total = 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as output:
        for part, relative in inputs:
            source = input_file(repo, relative)
            chunk_hash = hashlib.sha256()
            count = 0
            with source.open("rb") as stream:
                if stream.read(80).startswith(b"version https://git-lfs.github.com/spec/v1"):
                    raise AssemblyError("Unresolved Git LFS pointer: " + relative)
                stream.seek(0)
                while data := stream.read(BLOCK):
                    count += len(data)
                    total += len(data)
                    if count > part["bytes"] or total > record["bytes"]:
                        raise AssemblyError("Input exceeds declared size: " + relative)
                    chunk_hash.update(data)
                    full_hash.update(data)
                    git_hash.update(data)
                    output.write(data)
            if count != part["bytes"] or chunk_hash.hexdigest() != part["sha256"]:
                raise AssemblyError("Input size or SHA-256 mismatch: " + relative)
        output.flush()
        os.fsync(output.fileno())
    if total != record["bytes"] or full_hash.hexdigest() != record["sha256"]:
        raise AssemblyError("Reconstructed file size or SHA-256 mismatch: " + record["path"])
    if record.get("git_sha") and git_hash.hexdigest() != record["git_sha"]:
        raise AssemblyError("Reconstructed Git blob SHA mismatch: " + record["path"])
    if destination.suffix.lower() in (".zip", ".jar", ".mcpack"):
        try:
            with ZipFile(destination) as archive:
                if archive.testzip() is not None:
                    raise AssemblyError("Archive CRC failure: " + record["path"])
        except BadZipFile:
            raise AssemblyError("Invalid ZIP/JAR payload: " + record["path"]) from None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while data := stream.read(BLOCK):
            digest.update(data)
    return digest.hexdigest()


def write_deterministic_zip(destination: Path, payload: Path, folder=PAYLOAD_FOLDER):
    # Stored ZIP entries avoid compression-library-dependent output bytes.
    with ZipFile(destination, "x", compression=ZIP_STORED) as archive:
        for source in sorted(p for p in payload.rglob("*") if p.is_file()):
            name = folder + "/" + source.relative_to(payload).as_posix()
            entry = ZipInfo(name, (2026, 11, 25, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            entry.compress_type = ZIP_STORED
            with archive.open(entry, "w") as target, source.open("rb") as incoming:
                shutil.copyfileobj(incoming, target, BLOCK)
    with ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise AssemblyError("Generated payload ZIP CRC failure")


def assemble(repo: Path, output: Path, manifest_relative=DEFAULT_MANIFEST) -> dict:
    repo = repo.resolve(strict=True)
    manifest_path = input_file(repo, manifest_relative)
    if manifest_path.stat().st_size > 16 * BLOCK:
        raise AssemblyError("Manifest is too large")
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(files, list) or not 1 <= len(files) <= 20000:
        raise AssemblyError("Manifest needs a nonempty files list")
    names = set()
    for record in files:
        validate_record(record)
        name = record["path"].casefold()
        if name in names or name in ("readme_runtime_update.txt", "runtime-manifest.json"):
            raise AssemblyError("Duplicate or reserved payload output path")
        names.add(name)
    if sum(r["bytes"] for r in files) > MAX_TOTAL:
        raise AssemblyError("Payload exceeds assembly size limit")
    if JAVA_PATH.casefold() not in names or BEDROCK_PATH.casefold() not in names:
        raise AssemblyError("The exact Java and Bedrock pack records are required")
    artwork = manifest.get("artwork")
    if not isinstance(artwork, dict):
        raise AssemblyError("The artwork record is required for this complete release")
    validate_record(artwork)
    output = output.absolute()
    if output.exists() or output.is_symlink():
        raise AssemblyError("Output already exists; choose a new directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".gtm-functional-", dir=output.parent) as temporary:
        work = Path(temporary)
        payload = work / "payload"
        payload.mkdir()
        release = work / "release"
        release.mkdir()
        for record in files:
            copy_verified(repo, record, payload / record["path"], RUNTIME_ROOT + "/" + record["path"])
        copy_verified(repo, artwork, release / ART_NAME, artwork.get("source_repo_path", artwork["path"]))
        connector = work / "connector"
        connector.mkdir()
        for name in CONNECTOR_FILES:
            source = input_file(repo, name)
            if source.stat().st_size > BLOCK:
                raise AssemblyError("Unexpectedly large connector source: " + name)
            target = connector / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
        write_deterministic_zip(release / CONNECTOR_NAME, connector, "GTM_Daytona_Laptop_Connector")
        (payload / "README_RUNTIME_UPDATE.txt").write_text(NOTICE, encoding="utf-8", newline="\n")
        (payload / "runtime-manifest.json").write_bytes(manifest_bytes)
        write_deterministic_zip(release / UPDATE_NAME, payload)
        shutil.copyfile(payload / JAVA_PATH, release / JAVA_NAME)
        shutil.copyfile(payload / BEDROCK_PATH, release / BEDROCK_NAME)
        assets = [{"name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
                  for path in sorted(release.iterdir())]
        report = {"schema": "GTM_FUNCTIONAL_ASSEMBLY_V1", "status": "PASS",
                  "scope": "Verified runtime update payload; not a complete server or deployment",
                  "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                  "runtime_files": len(files), "artwork_bytes": artwork["bytes"],
                  "connector_files": list(CONNECTOR_FILES),
                  "network_requests": 0, "server_started": False,
                  "core_or_launcher_rebuilt": False, "assets": assets}
        (release / "assembly-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        sums = "".join(sha256(path) + "  " + path.name + "\n" for path in sorted(release.iterdir()))
        (release / "SHA256SUMS").write_text(sums, encoding="ascii")
        # Claim a new output directory atomically. Hard links are exclusive and
        # keep final files complete; the temporary directory shares this volume.
        output.mkdir()
        for source in sorted(release.iterdir()):
            os.link(source, output / source.name)
        return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = assemble(args.repo_root, args.output, args.manifest)
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print("Functional assembly stopped: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
