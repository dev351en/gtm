#!/usr/bin/env python3
"""Build a reproducible, narrowly patched runtime from the preserved 1.0.3 input.

The recovered binary is an explicit build input, not falsely claimed as rebuilt
from the older source/ tree. Unknown inputs, missing replacement classes and
duplicate ZIP entries stop the build. No server or world is contacted.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "runtime/functional-r4/plugins/SDCraftCore-1.0.3-r4-functional-candidate.jar"
BASE_HASH = "b7c76cd3a664e1bb7e1e56fd2098f7ef0a71e921d47170ed10c4e658974715af"
PATCH_HASH = "0677ac5af1e338e47bcf0c9db7395bd00ff4d3a61d6836587d881186638986f8"
NPC_PATCH_HASH = "bafc49db8c280b33dc93342dc7253725b0e44b21876dd4bb87e55517febccb71"
VERSION = "1.0.5-r4-spec-candidate"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def members(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or z.testzip():
            raise ValueError("Invalid or duplicate archive members: " + path.name)
        if any(n.startswith("/") or ".." in Path(n).parts or "\\" in n for n in names):
            raise ValueError("Unsafe archive path")
        return {n: z.read(n) for n in names if not n.endswith("/")}


def archive(path: Path, data: dict[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, content in sorted(data.items()):
            info = zipfile.ZipInfo(name, (2026, 11, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, content)


def build_core(overlay: Path, patched_vehicle: Path, dest: Path, patched_npc: Path | None = None) -> dict:
    if sha(BASE.read_bytes()) != BASE_HASH:
        raise ValueError("Preserved input changed; refusing an unreviewed repair")
    if sha(patched_vehicle.read_bytes()) != PATCH_HASH:
        raise ValueError("Vehicle patch does not match the reviewed transform and boarding patch")
    patched_npc = patched_npc or ROOT / "hotfix/build/npc-combat-patch/com/sdcraft/core/GtmEquipment.class"
    if sha(patched_npc.read_bytes()) != NPC_PATCH_HASH:
        raise ValueError("NPC combat patch does not match the reviewed two target gates")
    base, patch = members(BASE), members(overlay)
    required = ["SDCraftCorePlugin", "GunEngine", "GtmPhoneApps", "GtmPhoneHud", "GtmWebConsole", "GtmWeaponUpgrade",
                "GtmClientHud", "AiService", "GtmDialogue", "NpcService", "NpcCombatAccess", "NpcConversationBackend"]
    for name in required:
        if f"com/sdcraft/core/{name}.class" not in patch:
            raise ValueError("Missing compiled repair class: " + name)
    patch.pop("META-INF/MANIFEST.MF", None)
    roots = {name.removesuffix(".class").split("$")[0] for name in patch if name.endswith(".class")}
    removed = {name for name in base if name.endswith(".class") and name.removesuffix(".class").split("$")[0] in roots}
    output = {name: content for name, content in base.items() if name not in removed}
    output.update(patch)
    output["com/sdcraft/core/GtmVehicles.class"] = patched_vehicle.read_bytes()
    output["com/sdcraft/core/GtmEquipment.class"] = patched_npc.read_bytes()
    plugin = base["plugin.yml"].decode("utf-8")
    plugin, count = re.subn(r"(?m)^version:.*$", "version: " + VERSION, plugin)
    if count != 1 or "commands:\n" not in plugin: raise ValueError("Unsupported plugin metadata")
    plugin, permission_count = re.subn(r"(?m)(^  gtm\.dialogue:\n    description: [^\n]*\n    default: )false$", r"\g<1>true", plugin)
    if permission_count != 1: raise ValueError("Dialogue permission metadata is not the reviewed baseline")
    plugin = plugin.replace("Use experimental local dialogue after authentication", "Converse with nearby NPCs after authentication")
    plugin = plugin.replace("commands:\n", "commands:\n  gtmweb:\n    description: Open the private GTM Control Centre\n    usage: /gtmweb\n    permission: sdcraft.admin\n", 1)
    output["plugin.yml"] = plugin.encode()
    # Defaults only. The updater never overwrites an existing server config.
    output["config.yml"] = base["config.yml"] + b"\n# Private local control centre; use SSH forwarding for remote access.\nweb-console:\n  enabled: true\n  port: 8765\n# Authenticated nearby NPC dialogue; external inference stays opt-in.\ndialogue:\n  enabled: true\n  proximity-greetings: true\n"
    changed = sorted(name for name in output if base.get(name) != output[name])
    unchanged = {name: content for name, content in base.items() if name in output and name not in changed}
    archive(dest, output)
    readback = members(dest)
    assert readback == output
    assert all(readback[name] == content for name, content in unchanged.items())
    return {"base_sha256": BASE_HASH, "sha256": sha(dest.read_bytes()), "bytes": dest.stat().st_size,
            "unchanged_entries": len(unchanged), "replaced_top_level_classes": sorted(roots),
            "removed_original_class_entries": len(removed), "changed_or_added_entries": changed,
            "vehicle_class_sha256": PATCH_HASH, "npc_combat_class_sha256": NPC_PATCH_HASH,
            "source_status": "Maintained source overlay and verified vehicle/target-gate patches over preserved 1.0.3; not a full original-source rebuild"}


def build(overlay: Path, vehicle: Path, packs: Path, output: Path, pack_url: str) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    core_path = "plugins/SDCraftCore-" + VERSION + ".jar"
    report = build_core(overlay, vehicle, output / core_path)
    pack_report = json.loads((packs / "pack-repair-report.json").read_text())
    expected_profile = pack_report.get("traditional_rickshaw_canopy", {}).get("profile_resource_sha256")
    compiled_profile = members(output / core_path).get("vehicle/road-profiles.tsv", b"")
    if not expected_profile or sha(compiled_profile) != expected_profile:
        raise ValueError("Compiled vehicle collision profile does not match the repaired pack geometry; rebuild the overlay")
    report["vehicle_profile_sha256"] = expected_profile
    expected_animation = pack_report.get("traditional_rickshaw_canopy", {}).get("animation_resource_sha256")
    if not expected_animation or sha(members(output / core_path).get("vehicle/animated-parts.tsv", b"")) != expected_animation:
        raise ValueError("Compiled wheel animation pivots do not match the repaired pack geometry")
    report["vehicle_animation_sha256"] = expected_animation
    copies = {
        "resourcepacks/GTM_Repair_128_Java.zip": packs / "GTM_Repair_128_Java.zip",
        "plugins/Geyser-Spigot/packs/GTM_Repair_128_Bedrock.mcpack": packs / "GTM_Repair_128_Bedrock.mcpack",
        "plugins/Geyser-Spigot/custom_mappings/gtm_native128.json": packs / "gtm_native128.json",
        "Open-Control-Centre.bat": ROOT / "packaging/repair/Open-Control-Centre.bat",
        "tools/open_control_centre.py": ROOT / "tools/open_control_centre.py",
    }
    for destination, source in copies.items():
        target = output / destination; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target)
    files = []
    for name in [core_path, *copies]:
        path = output / name
        files.append({"path": name, "bytes": path.stat().st_size, "sha256": sha(path.read_bytes()),
                      "optional_bedrock": name.startswith("plugins/Geyser-Spigot/")})
    java_pack = output / "resourcepacks/GTM_Repair_128_Java.zip"
    manifest = {"schema": "GTM_RUNTIME_REPAIR_V1", "version": VERSION,
                "base_core_sha256": BASE_HASH,
                "base_bedrock_sha256": "d02cc8f41f6f97799dedab824b6fd23049c01556475e0031a50824543b507aab",
                "files": files,
                "java_pack": {"path": "resourcepacks/GTM_Repair_128_Java.zip",
                              "sha1": hashlib.sha1(java_pack.read_bytes()).hexdigest(),
                              "id": pack_report["java_pack_id"], "url": pack_url},
                "scope": "Update for the reviewed 1.0.3 and 1.0.4 runtimes; existing worlds, accounts, ownership, routes and configuration are retained. The optional Java HUD is installed separately on the client."}
    (output / "repair-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "build-report.json").write_text(json.dumps(report, indent=2) + "\n")
    shutil.copyfile(packs / "pack-repair-report.json", output / "pack-repair-report.json")
    for source, name in [(ROOT / "tools/install_runtime_repair.py", "install_runtime_repair.py"),
                         (ROOT / "packaging/repair/Update-GTM.bat", "Update-GTM.bat"),
                         (ROOT / "packaging/repair/Update-GTM.sh", "Update-GTM.sh"),
                         (ROOT / "packaging/repair/Open-Control-Centre.bat", "Open-Control-Centre.bat")]:
        if source.is_file(): shutil.copyfile(source, output / name)
    guide = ROOT / "packaging/repair/README.md"
    if guide.is_file(): shutil.copyfile(guide, output / "README.md")
    notes = ROOT / "packaging/repair/RELEASE_NOTES.md"
    if notes.is_file(): shutil.copyfile(notes, output / "RELEASE_NOTES.md")
    client = ROOT / "client-hud"
    client_report = json.loads((client / "build/build-report.json").read_text())
    client_jar = client / "build/libs/GTM-Client-HUD-1.0.0.jar"
    if sha(client_jar.read_bytes()) != client_report.get("sha256"):
        raise ValueError("Optional HUD JAR differs from its verified build report")
    if client_report.get("minecraft") != "26.3" or client_report.get("minecraft_binaries_redistributed") is not False:
        raise ValueError("Optional HUD has an unreviewed target or redistribution scope")
    for source, name in [(client_jar, client_jar.name), (client / "README.md", "README.md"),
                         (client / "dependencies.lock.json", "dependencies.lock.json"),
                         (client / "build/build-report.json", "build-report.json")]:
        target = output / "client" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if name == "README.md":
            client_guide = source.read_text(encoding="utf-8")
            client_guide = client_guide.replace("(../docs/repair-evidence/", "(../evidence/")
            client_guide = client_guide.replace("(../docs/SPEC_REPAIR_2026-11-25.md)", "(../SPEC_REPAIR_2026-11-25.md)")
            target.write_text(client_guide, encoding="utf-8")
        else:
            shutil.copyfile(source, target)
    record = ROOT / "docs/SPEC_REPAIR_2026-11-25.md"
    if record.is_file():
        # The standalone ZIP keeps its guide at the root; source-code links go
        # to the maintained repository instead of pointing outside extraction.
        guide_text = record.read_text(encoding="utf-8")
        guide_text = guide_text.replace("(../packaging/repair/README.md)", "(README.md)")
        guide_text = guide_text.replace("(../packaging/repair/RELEASE_NOTES.md)", "(RELEASE_NOTES.md)")
        guide_text = guide_text.replace("(repair-evidence/", "(evidence/")
        guide_text = guide_text.replace("(RUNTIME_REPAIR_2026-11-25.md)", "(https://github.com/dev351en/gtm/blob/fix/spec-hud-npc-passengers-20261125/docs/RUNTIME_REPAIR_2026-11-25.md)")
        guide_text = guide_text.replace("(../client-hud/README.md)", "(client/README.md)")
        guide_text = guide_text.replace("(../", "(https://github.com/dev351en/gtm/blob/fix/spec-hud-npc-passengers-20261125/")
        (output / "SPEC_REPAIR_2026-11-25.md").write_text(guide_text, encoding="utf-8")
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--overlay", type=Path, required=True)
    p.add_argument("--vehicle-class", type=Path, required=True)
    p.add_argument("--packs", type=Path, default=ROOT / "build/repaired-packs")
    p.add_argument("--output", type=Path, default=ROOT / "build/repaired-release")
    p.add_argument("--pack-url", default="https://github.com/dev351en/gtm/releases/download/gtm-spec-repair-1.0.5-20261125/GTM_Repair_128_Java.zip")
    args = p.parse_args()
    print(json.dumps(build(args.overlay, args.vehicle_class, args.packs, args.output, args.pack_url), indent=2))
