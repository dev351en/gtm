#!/usr/bin/env python3
"""Assemble a NEW private laptop server; never operate a live server or Daytona.

Two explicit inputs are supported: a stopped private server directory, or the
exact sanitized public city ZIP. No source data is overwritten. Java 25 javac
is needed only by the builder; the finished launchers require no Python.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

from bootstrap_laptop_dependencies import DEFAULT_LOCK, REPO, digest, verify

TEMPLATES = REPO / "packaging/laptop"
RELEASE_DOCUMENTATION_ROOT = REPO / "docs"
RUNTIME_VALIDATION_REPORT = REPO / "build/runtime-packs/runtime-pack-validation.json"
RELEASE_DOCUMENTS = (
    "PLAYABLE_R4_ACCEPTANCE.md",
    "PLAYABLE_R4_HANDOFF.md",
    "STATE_RECOVERY_R4.md",
    "AUTHENTICATION.md",
    "LAPTOP_BUNDLE.md",
    "LAPTOP_BUNDLE_VALIDATION.json",
    "BUILD_RUNTIME_R4_REPORT.md",
    "BUILD_RUNTIME_R4_EVIDENCE.json",
    "PUBLIC_WORLD_SITES.json",
    "reports/PUBLIC_WORLD_2026-11-23_SITE_SURVEY.json",
    "creative/DESIGN_LANGUAGE_128.md",
    "creative/GENERATION_128_REPORT.md",
)
CORE_CLASSES = (
    "com/sdcraft/core/SDCraftCorePlugin.class",
    "com/sdcraft/core/GtmAuthentication.class",
    "com/sdcraft/core/gtm/AuthenticationStore.class",
    "com/sdcraft/core/GtmCityModels.class",
)
CONFLICTING_AUTH = {"simplelogin", "authme", "loginsecurity"}
WINDOWS_RESERVED = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}


def save_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def require_regular(path: Path) -> None:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Expected a regular input file: {path.name}")
    with path.open("rb") as stream:
        if stream.read(80).startswith(b"version https://git-lfs.github.com/spec/v1"):
            raise ValueError(f"Unresolved Git LFS pointer: {path.name}")


def copy_release_documentation(stage: Path) -> None:
    """Attach only the reviewed release documents, never a source or private-data tree."""
    destination = stage / "documentation"
    destination.mkdir()
    sources = [(RELEASE_DOCUMENTATION_ROOT / name, Path(name)) for name in RELEASE_DOCUMENTS]
    if RUNTIME_VALIDATION_REPORT.is_file():
        sources.append((RUNTIME_VALIDATION_REPORT, Path("runtime-pack-validation.json")))
    sources.append((stage / "launcher/build-report.json", Path("laptop-build-report.json")))
    for source, relative in sources:
        require_regular(source)
        before = digest(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if digest(target) != before or digest(source) != before:
            raise ValueError("A release document changed during assembly; wait for the final reviewed documents")
    (destination / "README.txt").write_text(
        "GTM LOCAL LAPTOP CANDIDATE — RELEASE EVIDENCE\n\n"
        "Start with PLAYABLE_R4_ACCEPTANCE.md for the requirements matrix and concrete missing gameplay.\n"
        "PLAYABLE_R4_HANDOFF.md explains the candidate scope and remaining work.\n"
        "LAPTOP_BUNDLE.md covers startup, source profiles and the first-start EULA gate.\n"
        "AUTHENTICATION.md covers account registration and protected identity recovery.\n"
        "STATE_RECOVERY_R4.md records the transaction and recovery guarantees and limits.\n"
        "BUILD_RUNTIME_R4_REPORT.md and BUILD_RUNTIME_R4_EVIDENCE.json record the tested core and packs.\n"
        "laptop-build-report.json records this folder's exact input hashes and configuration changes.\n"
        "reports/ contains the actual public-world site survey; it is not a full route-accessibility audit.\n"
        "creative/ contains the native 128 design language and generation report.\n\n"
        "These records do not certify a full game or a live Java/Bedrock client session.\n"
        "SHA256SUMS records the exact files in this documentation snapshot.\n",
        encoding="utf-8",
    )
    documents = sorted(p for p in destination.rglob("*") if p.is_file())
    (destination / "SHA256SUMS").write_text(
        "".join(f"{digest(p)}  {p.relative_to(destination).as_posix()}\n" for p in documents),
        encoding="utf-8",
    )


def safe_zip_name(name: str) -> PurePosixPath:
    if not name or "\\" in name or ":" in name or "\x00" in name:
        raise ValueError("Unsafe archive path")
    p = PurePosixPath(name)
    if p.is_absolute() or any(part in ("", ".", "..") for part in name.rstrip("/").split("/")):
        raise ValueError("Archive path traversal is not allowed")
    for part in p.parts:
        if part.rstrip(" .") != part or part.split(".")[0].lower() in WINDOWS_RESERVED:
            raise ValueError("Archive contains a path that is unsafe on Windows")
    return p


def inspect_zip(path: Path, limit: int = 8 * 1024**3) -> list:
    require_regular(path)
    with ZipFile(path) as z:
        entries = z.infolist()
        seen = set()
        size = 0
        for info in entries:
            name = str(safe_zip_name(info.filename)).casefold()
            if name in seen:
                raise ValueError("Archive has duplicate/case-colliding paths")
            seen.add(name)
            if stat.S_ISLNK(info.external_attr >> 16) or info.flag_bits & 1:
                raise ValueError("Symlink or encrypted archive entries are not supported")
            size += info.file_size
            if size > limit:
                raise ValueError("Archive exceeds the extraction budget")
        if z.testzip() is not None:
            raise ValueError("Archive CRC validation failed")
        return entries


def extract_zip(path: Path, dest: Path, strip_prefix: str = "", limit: int = 8 * 1024**3) -> None:
    entries = inspect_zip(path, limit)
    with ZipFile(path) as z:
        for info in entries:
            name = info.filename
            if strip_prefix:
                if not name.startswith(strip_prefix):
                    raise ValueError("Archive has unexpected files outside its root")
                name = name[len(strip_prefix):]
            if not name:
                continue
            target = dest.joinpath(*safe_zip_name(name).parts)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output, 1024 * 1024)


def descriptor_field(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*([^\r\n#]+)", text)
    return match.group(1).strip().strip("\"'") if match else None


def plugin_info(path: Path, core: bool = False) -> dict:
    require_regular(path)
    with ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError(f"Plugin CRC failed: {path.name}")
        name = next((n for n in ("plugin.yml", "paper-plugin.yml") if n in z.namelist()), None)
        if name is None:
            raise ValueError(f"Not a Bukkit/Paper plugin: {path.name}")
        text = z.read(name).decode("utf-8-sig")
        identity = descriptor_field(text, "name")
        version = descriptor_field(text, "version")
        if not identity or not version:
            raise ValueError(f"Missing plugin identity/version: {path.name}")
        depends = []
        match = re.search(r"(?m)^depend:[ \t]*([^\r\n]*)", text)
        if match:
            value = match.group(1).strip()
            if value.startswith("[") and value.endswith("]"):
                depends = [v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()]
            elif not value:
                tail = text[match.end():]
                for line in tail.splitlines():
                    if line and not line[0].isspace(): break
                    item = re.match(r"\s*-\s*[\"']?([^\"'\s#]+)", line)
                    if item: depends.append(item.group(1))
            else:
                raise ValueError(f"Unsupported dependency declaration: {path.name}")
        if core:
            if identity != "SDCraftCore" or descriptor_field(text, "api-version") != "26.3":
                raise ValueError("Candidate must be SDCraftCore for API 26.3")
            missing = [n for n in CORE_CLASSES if n not in z.namelist()]
            if missing:
                raise ValueError("Candidate is missing current gameplay/authentication classes: " + ", ".join(missing))
            for command in ("login", "register", "logout", "changepassword", "gtmauth", "gtmassets"):
                if not re.search(rf"(?m)^  {command}:\s*$", text):
                    raise ValueError(f"Candidate is missing command {command}")
        return {"filename": path.name, "name": identity, "version": version, "depends": depends,
                "sha256": digest(path), "bytes": path.stat().st_size}


def read_properties(path: Path) -> dict:
    props = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*([^#!\s=:]+)\s*[=:]\s*(.*)$", line)
        if match: props[match.group(1)] = match.group(2).replace("\\:", ":").replace("\\=", "=")
    return props


def update_properties(path: Path, updates: dict) -> dict:
    before = read_properties(path) if path.exists() else {}
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    output = []
    written = set()
    for line in lines:
        match = re.match(r"\s*([^#!\s=:]+)\s*[=:]", line)
        key = match.group(1) if match else None
        if key in updates:
            if key not in written: output.append(f"{key}={updates[key]}"); written.add(key)
        else: output.append(line)
    for key, value in updates.items():
        if "\n" in str(value) or "\r" in str(value): raise ValueError("Property values cannot contain literal newlines")
        if key not in written: output.append(f"{key}={value}")
    path.write_text("\n".join(output) + "\n", encoding="utf-8")
    return {k: {"before": before.get(k), "after": str(v)} for k, v in updates.items() if before.get(k) != str(v)}


def disable_command_logging(root: Path) -> None:
    path = root / "spigot.yml"
    text = path.read_text(encoding="utf-8") if path.exists() else "settings:\n"
    if re.search(r"(?m)^\s+log-commands:", text):
        text = re.sub(r"(?m)^(\s+)log-commands:.*$", r"\1log-commands: false", text)
    elif re.search(r"(?m)^settings:\s*$", text):
        text = re.sub(r"(?m)^(settings:\s*)$", r"\1\n  log-commands: false", text, count=1)
    else:
        # Inline/anchored settings require a real YAML migration; fail closed.
        if re.search(r"(?m)^settings:", text): raise ValueError("Cannot safely update inline spigot settings; set settings.log-commands=false in a separate source copy")
        text += "\nsettings:\n  log-commands: false\n"
    path.write_text(text, encoding="utf-8")


def yaml_scalar(path: Path, section: str, key: str) -> str | None:
    """Read a simple root section's scalar; reject ambiguous YAML rather than migrate it."""
    active = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"): continue
        if not line[0].isspace():
            active = line.strip() == section + ":"
            continue
        if active:
            match = re.match(rf"^  {re.escape(key)}:[ \t]*([^#]*?)[ \t]*$", line)
            if match: return match.group(1).strip().strip("\"'")
    return None


def tree_manifest(root: Path) -> dict:
    result = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(base) / name
            if getattr(path, "is_junction", lambda: False)():
                raise ValueError("Server copy contains a Windows junction; handle it explicitly before export")
            mode = path.lstat().st_mode
            if stat.S_ISDIR(mode): continue
            if not stat.S_ISREG(mode): raise ValueError("Server copy contains a symlink or special file; handle it explicitly before export")
            result[path.relative_to(root).as_posix()] = {"sha256": digest(path), "bytes": path.stat().st_size}
    return result


@contextmanager
def stopped_world_locks(source: Path):
    handles = []
    try:
        for world in source.iterdir():
            lock = world / "session.lock"
            if not world.is_dir() or not lock.is_file(): continue
            handle = lock.open("r+b")  # Lock only; no source bytes are changed.
            handles.append(handle)
            try:
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, max(1, lock.stat().st_size))
                else:
                    import fcntl
                    fcntl.lockf(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise ValueError("Source world is locked by a running server; stop Minecraft before exporting") from exc
        yield
    finally:
        for handle in handles: handle.close()


def validate_world(root: Path, level_name: str) -> Path:
    path = root / level_name
    if Path(level_name).is_absolute() or ".." in Path(level_name).parts or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("World path must stay within the private bundle")
    require_regular(path / "level.dat")
    region_dirs = (path / "region", path / "dimensions/minecraft/overworld/region")
    if not any(p.stat().st_size >= 8192 for folder in region_dirs for p in folder.glob("*.mca")):
        raise ValueError("City world contains no valid-size region files")
    return path


def compile_launcher(javac: Path, target: Path) -> None:
    version = subprocess.run([str(javac), "-version"], capture_output=True, text=True, check=True)
    if not re.search(r"javac 25(?:\.|\s|$)", version.stdout + version.stderr):
        raise ValueError("Java 25 javac is required to build the self-contained launcher")
    with tempfile.TemporaryDirectory(prefix="gtm-launcher-classes-") as td:
        classes = Path(td)
        subprocess.run([str(javac), "--release", "25", "-encoding", "UTF-8", "-d", str(classes), str(TEMPLATES / "GtmLauncher.java")], check=True)
        with ZipFile(target, "x", ZIP_DEFLATED, compresslevel=9) as z:
            z.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\nMain-Class: com.sdcraft.launcher.GtmLauncher\n\n")
            for p in sorted(classes.rglob("*.class")): z.write(p, p.relative_to(classes).as_posix())


def build(args) -> dict:
    output = args.output.resolve()
    if output.exists() or output.is_relative_to(REPO.resolve()):
        raise ValueError("Output must be a NEW private directory outside the Git repository")
    if args.archive and (args.archive.exists() or args.archive.resolve().is_relative_to(REPO.resolve())):
        raise ValueError("Archive must be a NEW private file outside the Git repository")
    if args.archive and args.archive.resolve().is_relative_to(output):
        raise ValueError("Archive must be outside the assembled server directory")
    if not 1 <= args.port <= 65535 or not 1 <= args.pack_port <= 65535 or args.port == args.pack_port:
        raise ValueError("Minecraft and HTTP pack ports must be distinct valid ports")
    if not re.fullmatch(r"[1-9][0-9]*[MG]", args.heap): raise ValueError("Heap must use an M or G suffix")
    lock = json.loads(args.lock.read_text(encoding="utf-8"))["items"]
    verify(args.paper, lock["paper"])
    candidate = plugin_info(args.candidate, core=True)
    inspect_zip(args.resource_pack, 2 * 1024**3)
    with ZipFile(args.resource_pack) as z:
        metadata = json.loads(z.read("pack.mcmeta"))
        if "pack" not in metadata: raise ValueError("Invalid Java resource-pack metadata")
    pack_sha1 = digest(args.resource_pack, "sha1")
    pack_sha256 = digest(args.resource_pack)
    input_bytes = args.paper.stat().st_size + args.candidate.stat().st_size + args.resource_pack.stat().st_size
    input_bytes += sum(p.stat().st_size for p in args.plugin)
    input_bytes += sum(p.stat().st_size for p in (args.bedrock_pack, args.geyser_mappings) if p is not None)
    source_manifest = None
    if args.stopped_server:
        source = args.stopped_server.resolve(strict=True)
        if output == source or output.is_relative_to(source) or source.is_relative_to(output):
            raise ValueError("Private copy must be separate from the source server")
        if args.online_mode is not None: raise ValueError("Import mode preserves authentication policy; do not pass --online-mode")
        if not (source / "server.properties").is_file(): raise ValueError("Stopped server is missing server.properties")
        # Existing launcher files would create ambiguous integrity/profile handling.
        if (source / "launcher").exists(): raise ValueError("Input already contains a launcher; use the original stopped server export")
        source_manifest = tree_manifest(source)
        input_bytes += sum(r["bytes"] for r in source_manifest.values())
        profile = "private_stopped_server_copy"
    else:
        if args.online_mode is None: raise ValueError("Fresh public-world profile requires explicit --online-mode true or false")
        verify(args.public_world, lock["public-world"])
        entries = inspect_zip(args.public_world)
        if "world/level.dat" not in [i.filename for i in entries]: raise ValueError("Pinned public world has an unexpected layout")
        input_bytes += sum(i.file_size for i in entries)
        profile = "public_world_2026_11_23_fresh_accounts"
    if args.windows_runtime:
        verify(args.windows_runtime, lock["windows-java25"])
        input_bytes += sum(i.file_size for i in inspect_zip(args.windows_runtime, 1024**3))
    if args.minecraft_bundler:
        verify(args.minecraft_bundler, lock["minecraft-bundler"])
        input_bytes += args.minecraft_bundler.stat().st_size
    output.parent.mkdir(parents=True, exist_ok=True)
    reserve = input_bytes * (2 if args.archive else 1) + 2 * 1024**3
    if shutil.disk_usage(output.parent).free < reserve:
        raise ValueError("Insufficient free disk for staging, archive and save headroom")
    source_preserved = True
    with tempfile.TemporaryDirectory(prefix=".gtm-private-build-", dir=output.parent) as td:
        stage = Path(td) / output.name
        if args.stopped_server:
            with stopped_world_locks(source):
                shutil.copytree(source, stage)
                if tree_manifest(stage) != source_manifest or tree_manifest(source) != source_manifest:
                    raise ValueError("Source changed while snapshotting; export only a stopped server")
        else:
            stage.mkdir(mode=0o700)
            extract_zip(args.public_world, stage)
            (stage / "plugins/SDCraftCore").mkdir(parents=True)
            with ZipFile(args.candidate) as z:
                (stage / "plugins/SDCraftCore/config.yml").write_bytes(z.read("config.yml"))
            for name in ("runtime.yml", "anchors.yml"):
                original = REPO / "config/SDCraftCore" / name
                if original.is_file(): shutil.copy2(original, stage / "plugins/SDCraftCore" / name)
            update_properties(stage / "server.properties", {
                "level-name": "world", "motd": "GTM | Indraprastha | Local staging", "max-players": "4",
                "view-distance": "6", "simulation-distance": "4", "online-mode": args.online_mode,
                "white-list": "false", "enforce-whitelist": "false", "pvp": "true", "allow-flight": "true",
                "difficulty": "normal", "gamemode": "survival", "spawn-protection": "0", "enable-command-block": "false"
            })
            (stage / "eula.txt").write_text("# Read https://www.minecraft.net/en-us/eula and accept explicitly at first start.\neula=false\n", encoding="utf-8")
        plugins = stage / "plugins"
        plugins.mkdir(exist_ok=True)
        for extra in args.plugin:
            entry = plugin_info(extra)
            if entry["name"] == "SDCraftCore": raise ValueError("Use --candidate for the core plugin")
            dest = plugins / extra.name
            if dest.exists() and digest(dest) != digest(extra): raise ValueError("Cannot silently replace an imported plugin; prepare a separate reviewed source copy")
            if not dest.exists(): shutil.copy2(extra, dest)
        existing = [plugin_info(p) for p in sorted(plugins.glob("*.jar"))]
        for entry in existing:
            if entry["name"].lower() in CONFLICTING_AUTH:
                raise ValueError("Existing authentication provider requires explicit migration; its database was not changed")
        old_core = [r for r in existing if r["name"] == "SDCraftCore"]
        if len(old_core) > 1: raise ValueError("Multiple core plugins found")
        core_name = old_core[0]["filename"] if old_core else args.candidate.name
        shutil.copy2(args.candidate, plugins / core_name)
        if digest(plugins / core_name) != candidate["sha256"] or digest(args.candidate) != candidate["sha256"]:
            raise ValueError("Core candidate changed during assembly; wait for the final build")
        infos = [plugin_info(p) for p in sorted(plugins.glob("*.jar"))]
        names = [r["name"].casefold() for r in infos]
        if len(names) != len(set(names)): raise ValueError("Duplicate plugin identities")
        if "vault" not in names: raise ValueError("The verified Vault economy dependency is required")
        for entry in infos:
            missing = [n for n in entry["depends"] if n.casefold() not in names]
            if missing: raise ValueError(f"Missing hard dependencies for {entry['name']}: {', '.join(missing)}")
        geyser = "geyser-spigot" in names
        if geyser and "floodgate" not in names:
            raise ValueError("This crossplay profile requires verified Geyser and Floodgate together")
        if args.bedrock_pack or args.geyser_mappings:
            if not geyser: raise ValueError("Bedrock pack/mappings require the Geyser and Floodgate plugin inputs")
        if geyser:
            geyser_dir = plugins / "Geyser-Spigot"
            geyser_dir.mkdir(exist_ok=True)
            geyser_config = geyser_dir / "config.yml"
            if not args.stopped_server:
                shutil.copy2(TEMPLATES / "geyser-local.yml", geyser_config)
            if not geyser_config.is_file() or yaml_scalar(geyser_config, "bedrock", "address") != "127.0.0.1":
                raise ValueError("Imported Geyser config needs a reviewed loopback-only copy; identity settings and keys were not changed")
            if yaml_scalar(geyser_config, "bedrock", "port") != "19132":
                raise ValueError("Local Geyser profile expects its separately checked TCP/UDP port 19132")
            if args.port == 19132 or args.pack_port == 19132:
                raise ValueError("Bedrock port cannot equal the Java or pack port")
            if args.bedrock_pack:
                inspect_zip(args.bedrock_pack, 2 * 1024**3)
                with ZipFile(args.bedrock_pack) as z:
                    bedrock_meta = json.loads(z.read("manifest.json"))
                    if "header" not in bedrock_meta or "modules" not in bedrock_meta: raise ValueError("Invalid Bedrock pack manifest")
                packs = geyser_dir / "packs";packs.mkdir(exist_ok=True)
                destination = packs / "GTM_Local_Bedrock.mcpack"
                if destination.exists(): raise ValueError("Managed Bedrock pack already exists; do not overwrite an import implicitly")
                shutil.copy2(args.bedrock_pack, destination)
            if args.geyser_mappings:
                mapping = json.loads(args.geyser_mappings.read_text(encoding="utf-8"))
                if not isinstance(mapping, dict): raise ValueError("Invalid Geyser mapping object")
                maps = geyser_dir / "custom_mappings";maps.mkdir(exist_ok=True)
                destination = maps / "gtm_native128.json"
                if destination.exists(): raise ValueError("Managed Geyser mapping already exists; do not overwrite an import implicitly")
                shutil.copy2(args.geyser_mappings, destination)
        shutil.copy2(args.paper, stage / lock["paper"]["filename"])
        verify(stage / lock["paper"]["filename"], lock["paper"])
        if args.minecraft_bundler:
            cache = stage / "cache";cache.mkdir(exist_ok=True)
            cached = cache / lock["minecraft-bundler"]["filename"]
            if cached.exists(): verify(cached, lock["minecraft-bundler"])
            else: shutil.copy2(args.minecraft_bundler, cached)
        pack_dir = stage / "resourcepacks"
        pack_dir.mkdir(exist_ok=True)
        final_pack = pack_dir / "GTM_Local_Java.zip"
        if final_pack.exists(): raise ValueError("Imported source already has the managed pack filename; choose a fresh source copy")
        shutil.copy2(args.resource_pack, final_pack)
        if digest(final_pack) != pack_sha256 or digest(final_pack, "sha1") != pack_sha1:
            raise ValueError("Resource pack changed during assembly; wait for the final pack build")
        before = read_properties(stage / "server.properties")
        online = before.get("online-mode", "true").lower()
        if online not in ("true", "false"): raise ValueError("Unrecognized authentication mode")
        world = validate_world(stage, before.get("level-name", "world"))
        changes = update_properties(stage / "server.properties", {
            "server-ip": "127.0.0.1", "server-port": str(args.port), "enable-rcon": "false", "enable-query": "false",
            "broadcast-console-to-ops": "false", "broadcast-rcon-to-ops": "false", "log-ips": "false",
            "resource-pack": f"http://127.0.0.1:{args.pack_port}/gtm-pack.zip", "resource-pack-sha1": pack_sha1,
            "require-resource-pack": "true", "resource-pack-prompt": '{"text":"Verified local GTM resource pack"}'
        })
        disable_command_logging(stage)
        launcher = stage / "launcher"
        launcher.mkdir()
        compile_launcher(args.javac, launcher / "gtm-launcher.jar")
        for name in ("Start-GTM.bat", "Start-GTM.sh", "README_LAPTOP.txt"):
            shutil.copy2(TEMPLATES / name, stage / name)
        (stage / "Start-GTM.sh").chmod(0o755)
        if args.windows_runtime:
            with ZipFile(args.windows_runtime) as z:
                roots = {safe_zip_name(i.filename).parts[0] for i in z.infolist()}
            if len(roots) != 1: raise ValueError("Unexpected Windows runtime archive layout")
            extract_zip(args.windows_runtime, stage / "runtime/java", next(iter(roots)) + "/", 1024**3)
            require_regular(stage / "runtime/java/bin/java.exe")
            if not (stage / "runtime/java/legal").is_dir(): raise ValueError("Java runtime license files must be retained")
        settings = {
            "profile.name": profile, "paper.jar": lock["paper"]["filename"], "resource.pack": "resourcepacks/GTM_Local_Java.zip",
            "expected.online.mode": online, "pack.bind": "127.0.0.1", "pack.client.host": "127.0.0.1",
            "pack.port": str(args.pack_port), "pack.sha1": pack_sha1, "allow.network": "false", "max.heap": args.heap,
            "minimum.free.bytes": str(2 * 1024**3)
        }
        if geyser:
            settings.update({"bedrock.enabled": "true", "bedrock.config": "plugins/Geyser-Spigot/config.yml", "bedrock.port": "19132"})
        update_properties(launcher / "launcher.properties", settings)
        immutable = [stage / settings["paper.jar"], final_pack, launcher / "gtm-launcher.jar", *sorted(plugins.glob("*.jar"))]
        if args.minecraft_bundler: immutable.append(stage / "cache" / lock["minecraft-bundler"]["filename"])
        if geyser and args.bedrock_pack: immutable.append(plugins / "Geyser-Spigot/packs/GTM_Local_Bedrock.mcpack")
        if geyser and args.geyser_mappings: immutable.append(plugins / "Geyser-Spigot/custom_mappings/gtm_native128.json")
        if args.windows_runtime: immutable.extend(p for p in sorted((stage / "runtime/java").rglob("*")) if p.is_file())
        (launcher / "integrity.sha256").write_text("".join(f"{digest(p)}  {p.relative_to(stage).as_posix()}\n" for p in immutable), encoding="utf-8")
        report = {
            "schema_version": 1, "profile": profile, "status": "assembled_not_client_verified", "minecraft": "26.3", "paper_build": 255,
            "world": {"folder": world.relative_to(stage).as_posix(), "source": "private_stopped_copy" if args.stopped_server else "public_sanitized_snapshot_2026_11_23",
                      "latest_daytona_claim": False, "source_zip_sha256": None if args.stopped_server else digest(args.public_world)},
            "authentication": {"online_mode_preserved": online, "uuid_migration_performed": False, "provider": "SDCraftCore built-in authentication"},
            "core_candidate": candidate, "plugins": infos, "resource_pack": {"sha256": digest(final_pack), "sha1": pack_sha1, "metadata": metadata},
            "server_properties_changes": changes, "command_logging": "disabled_in_local_copy", "source_unchanged": True,
            "windows_java_bundled": bool(args.windows_runtime), "source_file_count": len(source_manifest or {}),
            "official_minecraft_bootstrap_cached": bool(args.minecraft_bundler),
            "crossplay": {"geyser_included": geyser, "bedrock_pack_included": bool(args.bedrock_pack), "mappings_included": bool(args.geyser_mappings), "client_verification": "not_run"},
            "eula_acceptance": "preserved_from_private_source" if args.stopped_server and (stage / "eula.txt").is_file() and read_properties(stage / "eula.txt").get("eula") == "true" else "owner_first_start_required",
            "limits": ["No Daytona access or mutation", "No Minecraft client bundled", "No full-game or live-client verification", "First Paper boot may fetch official libraries"],
        }
        save_json(launcher / "build-report.json", report)
        if source_manifest is not None: save_json(launcher / "private-source-manifest.json", source_manifest)
        save_json(launcher / "dependency-lock.json", json.loads(args.lock.read_text(encoding="utf-8")))
        copy_release_documentation(stage)
        if args.stopped_server and tree_manifest(source) != source_manifest:
            raise ValueError("Source changed before finalization")
        stage.rename(output)
    if args.archive:
        args.archive.parent.mkdir(parents=True, exist_ok=True)
        try:
            with ZipFile(args.archive, "x", ZIP_DEFLATED, compresslevel=6) as z:
                for p in sorted(output.rglob("*")):
                    if p.is_file(): z.write(p, output.name + "/" + p.relative_to(output).as_posix())
            with ZipFile(args.archive) as z:
                if z.testzip() is not None: raise ValueError("Final archive CRC check failed")
        except BaseException:
            args.archive.unlink(missing_ok=True)
            raise
        report["archive"] = {"path": str(args.archive.resolve()), "bytes": args.archive.stat().st_size, "sha256": digest(args.archive)}
    report["output"] = str(output)
    return report


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--stopped-server", type=Path, help="A stopped private server directory; never a live server")
    mode.add_argument("--public-world", type=Path, help="Exact verified sanitized public world ZIP; starts fresh accounts")
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--paper", type=Path, required=True)
    p.add_argument("--resource-pack", type=Path, required=True)
    p.add_argument("--bedrock-pack", type=Path)
    p.add_argument("--geyser-mappings", type=Path)
    p.add_argument("--plugin", type=Path, action="append", default=[])
    p.add_argument("--windows-runtime", type=Path)
    p.add_argument("--minecraft-bundler", type=Path, help="Optional exact official Paperclip dependency, for private cache only")
    p.add_argument("--javac", type=Path, required=True)
    p.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    p.add_argument("--online-mode", choices=("true", "false"), help="Explicit fresh-profile choice; forbidden for private import")
    p.add_argument("--heap", default="3G")
    p.add_argument("--port", type=int, default=25565)
    p.add_argument("--pack-port", type=int, default=25566)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--archive", type=Path)
    return p


def main(argv=None) -> int:
    try:
        result = build(parser().parse_args(argv))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"Laptop bundle stopped: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
