#!/usr/bin/env python3
"""Install or roll back the verified GTM repair in an explicitly selected stopped server.

Standard library only. No network deployment, world replacement, account reset,
configuration-template merge, feature-flag changes, or server process launch.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack, contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import socket
import stat
import sys
import tempfile
import uuid
from urllib.parse import urlsplit
from zipfile import BadZipFile, ZipFile

BASE_CORE = "b7c76cd3a664e1bb7e1e56fd2098f7ef0a71e921d47170ed10c4e658974715af"
# These exact released inputs have the same retained data/schema contract.
# A manifest cannot authorize an unknown installed plugin binary.
REVIEWED_CORE_HASHES = frozenset({
    BASE_CORE,
    "cd7db28cf7959e5c0801507c647479ebffca67616a8c543333ce24c8051ad5ac",  # released 1.0.4
})
BASE_BEDROCK = "d02cc8f41f6f97799dedab824b6fd23049c01556475e0031a50824543b507aab"
JAVA_PACK = "resourcepacks/GTM_Repair_128_Java.zip"
BEDROCK_PACK = "plugins/Geyser-Spigot/packs/GTM_Repair_128_Bedrock.mcpack"
MAPPINGS = "plugins/Geyser-Spigot/custom_mappings/gtm_native128.json"
EXTRAS = {"Open-Control-Centre.bat", "tools/open_control_centre.py"}
MAX_BYTES = 256 * 1024 * 1024
BACKUPS = "repair-backups"
RECEIPT = "repair-receipt.json"
RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


class RepairError(ValueError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while data := stream.read(1024 * 1024):
            digest.update(data)
    return digest.hexdigest()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(value: str) -> str:
    if not isinstance(value, str) or not value or any(c in value for c in '\\:<>"|?*') or any(ord(c) < 32 for c in value):
        raise RepairError("Unsafe relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or value != path.as_posix() or any(p in ("", ".", "..") for p in path.parts):
        raise RepairError("Absolute, ambiguous or escaping path: " + value)
    if any(p.endswith((".", " ")) or p.split(".", 1)[0].upper() in RESERVED for p in path.parts):
        raise RepairError("Path is unsafe on Windows: " + value)
    return value


def linked(path: Path) -> bool:
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def root_path(path: Path) -> Path:
    path = path.absolute()
    for ancestor in [*reversed(path.parents), path]:
        if linked(ancestor):
            raise RepairError("Symlink or junction root refused: " + str(path))
    if not path.is_dir():
        raise RepairError("Expected an existing directory: " + str(path))
    return path.resolve()


def local(root: Path, name: str, existing: bool = False) -> Path:
    name = relative(name)
    path = root
    for part in PurePosixPath(name).parts:
        path = path / part
        if linked(path):
            raise RepairError("Symlink or junction path refused: " + name)
    if not path.resolve(strict=False).is_relative_to(root):
        raise RepairError("Path escapes the selected directory: " + name)
    if existing and not path.is_file():
        raise RepairError("Missing regular file: " + name)
    if path.exists() and not path.is_file():
        raise RepairError("Expected a file, found a directory: " + name)
    return path


def _unescape(text: str) -> str:
    out, index = [], 0
    while index < len(text):
        c = text[index]
        index += 1
        if c != "\\" or index == len(text):
            out.append(c)
            continue
        c = text[index]
        index += 1
        if c == "u":
            digits = text[index:index + 4]
            if not re.fullmatch("[0-9a-fA-F]{4}", digits):
                raise RepairError("Invalid Unicode escape in properties")
            out.append(chr(int(digits, 16)))
            index += 4
        else:
            out.append({"t": "\t", "r": "\r", "n": "\n", "f": "\f"}.get(c, c))
    return "".join(out)


def property_records(data: bytes):
    # Latin-1 is used only as a byte-preserving transport. All changed keys and
    # values are ASCII; unrelated UTF-8 MOTDs and comments retain their bytes.
    lines = data.decode("latin-1").splitlines(keepends=True)
    index = 0
    while index < len(lines):
        start = index
        text = lines[index].rstrip("\r\n")
        index += 1
        while (len(text) - len(text.rstrip("\\"))) % 2 and index < len(lines):
            text = text[:-1] + lines[index].lstrip().rstrip("\r\n")
            index += 1
        stripped = text.lstrip()
        if not stripped or stripped.startswith(("#", "!")):
            yield start, index, None, None
            continue
        escaped, split = False, len(stripped)
        for pos, character in enumerate(stripped):
            if not escaped and (character in "=:" or character.isspace()):
                split = pos
                break
            if character == "\\" and not escaped:
                escaped = True
            else:
                escaped = False
        value = stripped[split:].lstrip()
        if value.startswith(("=", ":")):
            value = value[1:].lstrip()
        yield start, index, _unescape(stripped[:split]), _unescape(value)


def properties(data: bytes) -> dict[str, str]:
    return {key: value for _, _, key, value in property_records(data) if key is not None}


def update_properties(data: bytes, changes: dict[str, str]) -> bytes:
    lines = data.decode("latin-1").splitlines(keepends=True)
    newline = "\r\n" if b"\r\n" in data else "\n"
    output, written = [], set()
    for start, end, key, _ in property_records(data):
        if key not in changes:
            output.extend(lines[start:end])
            continue
        if key not in written:
            value = str(changes[key]).replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
            output.append(key + "=" + value + newline)
            written.add(key)
    if output and not output[-1].endswith(("\r", "\n")):
        output[-1] += newline
    for key, value in changes.items():
        if key not in written:
            value = str(value).replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
            output.append(key + "=" + value + newline)
    return "".join(output).encode("latin-1")


def plugin_name(path: Path) -> str | None:
    try:
        with ZipFile(path) as archive:
            for name in ("plugin.yml", "paper-plugin.yml"):
                if name not in archive.namelist():
                    continue
                info = archive.getinfo(name)
                if info.file_size > 65536:
                    raise RepairError("Oversized plugin metadata: " + path.name)
                text = archive.read(name).decode("utf-8-sig")
                match = re.search(r"(?m)^name\s*:\s*(['\"]?)([^'\"\r\n#]+)\1\s*(?:#.*)?$", text)
                return match.group(2).strip() if match else None
    except (BadZipFile, UnicodeDecodeError):
        if "sdcraftcore" in path.name.lower():
            raise RepairError("Unreadable core JAR: " + path.name)
    return None


def verify_payload(payload: Path) -> tuple[dict, dict[str, bytes]]:
    file = local(payload, "repair-manifest.json", True)
    if file.stat().st_size > 1024 * 1024:
        raise RepairError("Repair manifest is too large")
    manifest = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("schema") != "GTM_RUNTIME_REPAIR_V1":
        raise RepairError("Unsupported repair manifest schema")
    if manifest.get("base_core_sha256") != BASE_CORE:
        raise RepairError("This payload does not derive from the preserved 1.0.3 base core")
    if not isinstance(manifest.get("version"), str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", manifest["version"]):
        raise RepairError("Invalid repair version")
    rows = manifest.get("files")
    if not isinstance(rows, list) or not 2 <= len(rows) <= 16:
        raise RepairError("Invalid repair file list")
    files, folded, cores = {}, set(), []
    for row in rows:
        if not isinstance(row, dict):
            raise RepairError("Invalid repair file entry")
        name = relative(row.get("path"))
        core = bool(re.fullmatch(r"plugins/SDCraftCore-[A-Za-z0-9._-]+\.jar", name))
        if not core and name not in {JAVA_PACK, BEDROCK_PACK, MAPPINGS, *EXTRAS}:
            raise RepairError("Payload cannot replace this server path: " + name)
        if name.casefold() in folded:
            raise RepairError("Duplicate repair path: " + name)
        folded.add(name.casefold())
        if type(row.get("bytes")) is not int or not 0 <= row["bytes"] <= MAX_BYTES or not re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256", ""))):
            raise RepairError("Invalid size or SHA-256: " + name)
        optional = row.get("optional_bedrock", False)
        if type(optional) is not bool or optional != (name in {BEDROCK_PACK, MAPPINGS}):
            raise RepairError("Invalid optional Bedrock designation: " + name)
        path = local(payload, name, True)
        if path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]:
            raise RepairError("Payload size or SHA-256 mismatch: " + name)
        files[name] = path.read_bytes()
        if core:
            if (plugin_name(path) or "").casefold() != "sdcraftcore":
                raise RepairError("Repair core JAR has the wrong plugin identity")
            cores.append(name)
    if len(cores) != 1 or JAVA_PACK not in files:
        raise RepairError("Repair must contain exactly one core and the matching Java pack")
    if bool(BEDROCK_PACK in files) != bool(MAPPINGS in files):
        raise RepairError("The Bedrock pack and mappings must be supplied together")
    pack = manifest.get("java_pack", {})
    if not isinstance(pack, dict) or pack.get("path") != JAVA_PACK or not re.fullmatch(r"[0-9a-f]{40}", str(pack.get("sha1", ""))):
        raise RepairError("Invalid Java pack descriptor")
    if hashlib.sha1(files[JAVA_PACK]).hexdigest() != pack["sha1"]:
        raise RepairError("Java pack SHA-1 mismatch")
    if str(uuid.UUID(str(pack.get("id")))) != pack["id"]:
        raise RepairError("Invalid Java pack ID")
    url = urlsplit(pack.get("url", ""))
    if url.scheme != "https" or not url.netloc or url.username or url.password or "\n" in pack["url"] or "\r" in pack["url"]:
        raise RepairError("Manifest pack URL must be a credential-free HTTPS download")
    manifest["core_path"] = cores[0]
    return manifest, files


def core_files(server: Path) -> list[tuple[str, str]]:
    folder = server / "plugins"
    if linked(folder) or not folder.is_dir():
        raise RepairError("Selected directory has no regular plugins folder")
    result = []
    for path in sorted(folder.glob("*.jar")):
        local(server, path.relative_to(server).as_posix(), True)
        if (plugin_name(path) or "").casefold() == "sdcraftcore":
            result.append((path.relative_to(server).as_posix(), sha256(path)))
    if not result:
        raise RepairError("No SDCraftCore installation found in the selected server")
    return result


@contextmanager
def file_lock(path: Path, *, create: bool = False):
    if linked(path):
        raise RepairError("Symlink lock refused")
    created = False
    if create:
        try:
            stream = path.open("x+b")
            created = True
        except FileExistsError:
            stream = path.open("r+b")
    else:
        stream = path.open("r+b")
    acquired = False
    try:
        stream.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.lockf(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        acquired = True
        yield
    except OSError as failure:
        if not acquired:
            raise RepairError("Server or another updater is running; lock held: " + str(path)) from failure
        raise
    finally:
        if acquired:
            stream.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.lockf(stream.fileno(), fcntl.LOCK_UN)
        stream.close()
        if created and acquired and path.name == "session.lock":
            path.unlink(missing_ok=True)


def tcp_port(value: str) -> int:
    if not value.isdigit() or not 1 <= int(value) <= 65535:
        raise RepairError("Invalid configured server port")
    return int(value)


@contextmanager
def stopped_server(server: Path):
    with ExitStack() as stack:
        stack.enter_context(file_lock(server / ".gtm-repair.lock", create=True))
        values = properties(local(server, "server.properties", True).read_bytes())
        ports = {tcp_port(values.get("server-port", "25565"))}
        launcher = local(server, "launcher/launcher.properties")
        if launcher.is_file():
            cfg = properties(launcher.read_bytes())
            ports.add(tcp_port(cfg.get("pack.port", "25566")))
        for port in ports:
            for family, host in ((socket.AF_INET, "127.0.0.1"), (socket.AF_INET6, "::1")):
                try:
                    with socket.socket(family, socket.SOCK_STREAM) as probe:
                        probe.settimeout(0.25)
                        if probe.connect_ex((host, port)) == 0:
                            raise RepairError(f"Server or launcher is running on loopback port {port}; stop it first")
                except (OSError, OverflowError):
                    pass
            # Reserve the gameplay/pack ports during replacement, closing the
            # check-then-start race for the usual local/wildcard bind profile.
            reservation = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                reservation.bind(("127.0.0.1", port))
            except OSError as failure:
                reservation.close()
                raise RepairError(f"Port {port} is in use; stop the server and launcher first") from failure
            stack.callback(reservation.close)
        main = server / relative(values.get("level-name", "world"))
        local(server, (main / "level.dat").relative_to(server).as_posix(), True)
        worlds = {main}
        for directory in server.iterdir():
            if directory.is_dir() and (directory / "level.dat").is_file():
                if linked(directory):
                    raise RepairError("Symlink world directory refused")
                worlds.add(directory)
        for world in sorted(worlds):
            lock = local(server, (world / "session.lock").relative_to(server).as_posix())
            stack.enter_context(file_lock(lock, create=True))
        yield


def integrity_bytes(original: bytes, changes: dict[str, bytes | None]) -> bytes:
    lines, result, seen = original.decode("utf-8").splitlines(keepends=True), [], set()
    for line in lines:
        if not line.strip() or line.startswith("#"):
            result.append(line)
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+?)(?:\r?\n)?", line)
        if not match:
            raise RepairError("Malformed portable launcher integrity manifest")
        name = relative(match.group(2))
        if name in seen:
            raise RepairError("Duplicate portable integrity path: " + name)
        seen.add(name)
        if name in changes:
            if changes[name] is not None:
                result.append(digest(changes[name]) + "  " + name + "\n")
        else:
            result.append(line if line.endswith("\n") else line + "\n")
    # New immutable payload files must be recorded. Mutable server/launcher
    # settings retain their existing inclusion/exclusion policy.
    for name, data in changes.items():
        if data is not None and name not in seen and name not in {"server.properties", "launcher/launcher.properties"}:
            result.append(digest(data) + "  " + name + "\n")
    return "".join(result).encode("utf-8")


def plan(server: Path, manifest: dict, files: dict[str, bytes], bedrock: bool) -> dict[str, bytes | None]:
    new_core_hash = digest(files[manifest["core_path"]])
    cores = core_files(server)
    if any(value not in REVIEWED_CORE_HASHES | {new_core_hash} for _, value in cores):
        raise RepairError("Unsupported or unrecognized SDCraftCore binary; no files changed")
    if bedrock and not (server / "plugins/Geyser-Spigot").is_dir():
        raise RepairError("--bedrock requires an existing Geyser-Spigot configuration")
    if bedrock and not {BEDROCK_PACK, MAPPINGS}.issubset(files):
        raise RepairError("This repair payload does not include the complete Bedrock update")
    changes = {row["path"]: files[row["path"]] for row in manifest["files"]
               if bedrock or not row.get("optional_bedrock", False)}
    for name, _ in cores:
        if name != manifest["core_path"]:
            changes[name] = None
    if bedrock:
        expected = manifest.get("base_bedrock_sha256", BASE_BEDROCK)
        if expected != BASE_BEDROCK:
            raise RepairError("Unrecognized base Bedrock pack fingerprint")
        folder = server / "plugins/Geyser-Spigot/packs"
        if linked(folder):
            raise RepairError("Symlink Bedrock pack directory refused")
        for candidate in folder.glob("*.mcpack"):
            name = candidate.relative_to(server).as_posix()
            local(server, name, True)
            if name != BEDROCK_PACK and sha256(candidate) == expected:
                changes[name] = None
    server_file = local(server, "server.properties", True)
    server_data = server_file.read_bytes()
    current = properties(server_data)
    pack = manifest["java_pack"]
    url = pack["url"]
    launcher = local(server, "launcher/launcher.properties")
    if launcher.is_file():
        launch_data = launcher.read_bytes()
        cfg = properties(launch_data)
        # The preserved real launcher uses resource.pack; retain optional aliases
        # used by newer launchers without rewriting any unrelated setting.
        settings = {"resource.pack": JAVA_PACK, "pack.sha1": pack["sha1"]}
        if "pack.file" in cfg:
            settings["pack.file"] = JAVA_PACK
        derived = f"http://{cfg.get('pack.client.host', '127.0.0.1')}:{tcp_port(cfg.get('pack.port', '25566'))}/gtm-pack.zip"
        url = cfg.get("pack.url") or current.get("resource-pack") or derived
        if "pack.url" not in cfg and url != derived:
            raise RepairError("Existing portable pack URL differs from its launcher host/port; resolve it before updating")
        changes["launcher/launcher.properties"] = update_properties(launch_data, settings)
        integrity = local(server, "launcher/integrity.sha256", True)
        changes["server.properties"] = update_properties(server_data, {
            "resource-pack": url, "resource-pack-sha1": pack["sha1"], "resource-pack-id": pack["id"]})
        changes["launcher/integrity.sha256"] = integrity_bytes(integrity.read_bytes(), changes)
    else:
        changes["server.properties"] = update_properties(server_data, {
            "resource-pack": url, "resource-pack-sha1": pack["sha1"], "resource-pack-id": pack["id"]})
    # Validate every target before making a backup or replacing anything.
    for name in changes:
        local(server, name)
    return {name: data for name, data in changes.items()
            if (data is None and local(server, name).exists()) or
            (data is not None and (not local(server, name).exists() or sha256(local(server, name)) != digest(data)))}


def atomic_json(path: Path, value: dict):
    data = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".receipt-", delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def commit_change(server: Path, backup: Path, row: dict):
    target = local(server, row["path"])
    if row["after_sha256"] is None:
        target.unlink()
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(local(backup, "staged/" + row["path"], True), target)


def restore(server: Path, backup: Path, receipt: dict, *, partial: bool):
    if receipt.get("schema") != "GTM_REPAIR_RECEIPT_V1" or receipt.get("server_root") != str(server):
        raise RepairError("Backup receipt belongs to another server or schema")
    rows = receipt.get("files")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 64:
        raise RepairError("Invalid backup receipt")
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise RepairError("Invalid backup receipt entry")
        name = relative(row.get("path"))
        allowed = (name in {JAVA_PACK, BEDROCK_PACK, MAPPINGS, *EXTRAS,
                           "server.properties", "launcher/launcher.properties", "launcher/integrity.sha256"}
                   or bool(re.fullmatch(r"plugins/[^/]+\.jar", name))
                   or bool(re.fullmatch(r"plugins/Geyser-Spigot/packs/[^/]+\.mcpack", name)))
        if not allowed:
            raise RepairError("Backup receipt cannot restore this server path: " + name)
        for key in ("before_sha256", "after_sha256"):
            if key not in row or (row[key] is not None and not re.fullmatch(r"[0-9a-f]{64}", str(row[key]))):
                raise RepairError("Invalid backup receipt fingerprint")
        if name.casefold() in seen:
            raise RepairError("Duplicate backup receipt path")
        seen.add(name.casefold())
        target = local(server, name)
        actual = sha256(target) if target.exists() else None
        permitted = {row["after_sha256"], row["before_sha256"]} if partial else {row["after_sha256"]}
        if actual not in permitted:
            raise RepairError("File changed since repair; rollback will not overwrite it: " + name)
        if row["before_sha256"] is not None:
            original = local(backup, "files/" + name, True)
            if sha256(original) != row["before_sha256"]:
                raise RepairError("Backup checksum mismatch: " + name)
    for row in reversed(rows):
        target = local(server, row["path"])
        if row["before_sha256"] is None:
            target.unlink(missing_ok=True)
            continue
        original = local(backup, "files/" + row["path"], True)
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".restore-", delete=False) as stream:
            temporary = Path(stream.name)
        try:
            shutil.copy2(original, temporary)
            with temporary.open("rb") as stream:
                os.fsync(stream.fileno())
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
    receipt["status"] = "rolled_back"
    receipt["rolled_back_at"] = datetime.now(timezone.utc).isoformat()
    atomic_json(backup / RECEIPT, receipt)


def apply(payload: Path, server: Path, bedrock: bool = False) -> dict:
    payload, server = root_path(payload), root_path(server)
    manifest, files = verify_payload(payload)
    with stopped_server(server):
        parent = server / BACKUPS
        if linked(parent) or (parent.exists() and not parent.is_dir()):
            raise RepairError("Unsafe repair backup directory")
        if parent.exists():
            # A killed process can leave a durable prepared receipt. Do not layer
            # another update over it and make the original rollback ambiguous.
            for path in sorted(parent.glob("*/" + RECEIPT)):
                local(server, path.relative_to(server).as_posix(), True)
                if path.stat().st_size > 1024 * 1024:
                    raise RepairError("Oversized backup receipt")
                previous = json.loads(path.read_text(encoding="utf-8"))
                if (isinstance(previous, dict) and previous.get("schema") == "GTM_REPAIR_RECEIPT_V1"
                        and previous.get("status") == "prepared"):
                    raise RepairError("Unfinished repair " + path.parent.name + "; run rollback with this backup ID before applying again")
        changes = plan(server, manifest, files, bedrock)
        if not changes:
            return {"status": "already_installed", "version": manifest["version"], "files_changed": 0}
        required = sum(len(data) for data in changes.values() if data is not None)
        required += sum(local(server, name).stat().st_size for name in changes if local(server, name).exists())
        if shutil.disk_usage(server).free < required + 16 * 1024 * 1024:
            raise RepairError("Insufficient disk space for staging and a complete repair backup")
        parent.mkdir(exist_ok=True)
        identifier = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:10]
        backup = parent / identifier
        backup.mkdir(mode=0o700)
        receipt = {"schema": "GTM_REPAIR_RECEIPT_V1", "status": "prepared", "version": manifest["version"],
                   "server_root": str(server), "created_at": datetime.now(timezone.utc).isoformat(),
                   "manifest_sha256": sha256(payload / "repair-manifest.json"), "files": []}
        for name, data in changes.items():
            target = local(server, name)
            row = {"path": name, "before_sha256": sha256(target) if target.exists() else None,
                   "after_sha256": digest(data) if data is not None else None}
            if target.exists():
                original = backup / "files" / name
                original.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, original)
                if sha256(original) != row["before_sha256"]:
                    raise RepairError("Backup verification failed before replacement: " + name)
            if data is not None:
                staged = backup / "staged" / name
                staged.parent.mkdir(parents=True, exist_ok=True)
                with staged.open("xb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
                if target.exists():
                    staged.chmod(stat.S_IMODE(target.stat().st_mode))
                if sha256(staged) != row["after_sha256"]:
                    raise RepairError("Staged file verification failed: " + name)
            receipt["files"].append(row)
        atomic_json(backup / RECEIPT, receipt)
        try:
            for row in receipt["files"]:
                commit_change(server, backup, row)
            for row in receipt["files"]:
                target = local(server, row["path"])
                if (sha256(target) if target.exists() else None) != row["after_sha256"]:
                    raise RepairError("Installed file verification failed: " + row["path"])
            receipt["status"] = "committed"
            atomic_json(backup / RECEIPT, receipt)
        except (OSError, RepairError, KeyboardInterrupt) as failure:
            try:
                restore(server, backup, receipt, partial=True)
            except (OSError, RepairError) as rollback_failure:
                raise RepairError(f"Repair interrupted; automatic rollback needs review. Backup {identifier}: {rollback_failure}") from failure
            raise RepairError(f"Repair failed and original files were restored. Backup: {identifier}") from failure
        return {"status": "installed", "version": manifest["version"], "files_changed": len(changes),
                "backup": identifier, "worlds_accounts_and_feature_flags": "preserved",
                "next_step": "Start your existing server normally and accept its updated resource pack."}


def rollback(server: Path, identifier: str) -> dict:
    server = root_path(server)
    if not re.fullmatch(r"[0-9]{8}T[0-9]{6}Z-[0-9a-f]{10}", identifier):
        raise RepairError("Use the exact backup ID printed by the updater")
    backup = root_path(server / BACKUPS / identifier)
    receipt_file = local(backup, RECEIPT, True)
    if receipt_file.stat().st_size > 1024 * 1024:
        raise RepairError("Oversized backup receipt")
    receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    if not isinstance(receipt, dict) or receipt.get("schema") != "GTM_REPAIR_RECEIPT_V1" or receipt.get("server_root") != str(server):
        raise RepairError("Backup receipt belongs to another server or schema")
    if receipt.get("status") == "rolled_back":
        return {"status": "already_rolled_back", "backup": identifier}
    if receipt.get("status") not in {"prepared", "committed"}:
        raise RepairError("Unrecognized backup state")
    with stopped_server(server):
        restore(server, backup, receipt, partial=receipt["status"] == "prepared")
    return {"status": "rolled_back", "backup": identifier, "worlds_and_accounts": "unchanged"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    install = actions.add_parser("apply", help="Update an explicitly selected stopped server")
    install.add_argument("--payload", required=True, type=Path)
    install.add_argument("--server", required=True, type=Path)
    install.add_argument("--bedrock", action="store_true", help="Also update an existing Geyser pack and mappings")
    undo = actions.add_parser("rollback", help="Restore only files replaced by this repair")
    undo.add_argument("--server", required=True, type=Path)
    undo.add_argument("--backup", required=True)
    args = parser.parse_args()
    try:
        result = apply(args.payload, args.server, args.bedrock) if args.action == "apply" else rollback(args.server, args.backup)
        print(json.dumps(result, indent=2))
        return 0
    except (RepairError, OSError, ValueError, KeyError, BadZipFile) as failure:
        print("GTM repair stopped: " + str(failure), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
