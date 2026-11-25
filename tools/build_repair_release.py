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
PATCH_HASH = "c5ce0eb4254e4ba3a496a899eda466053e08dabb043761e1e17ee3cc0e07e7db"
VERSION = "1.0.4-r4-repair"


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


def build_core(overlay: Path, patched_vehicle: Path, dest: Path) -> dict:
    if sha(BASE.read_bytes()) != BASE_HASH:
        raise ValueError("Preserved input changed; refusing an unreviewed repair")
    if sha(patched_vehicle.read_bytes()) != PATCH_HASH:
        raise ValueError("Vehicle patch does not match the reviewed two-call-site patch")
    base, patch = members(BASE), members(overlay)
    required = ["SDCraftCorePlugin", "GunEngine", "GtmPhoneApps", "GtmPhoneHud", "GtmWebConsole", "GtmWeaponUpgrade"]
    for name in required:
        if f"com/sdcraft/core/{name}.class" not in patch:
            raise ValueError("Missing compiled repair class: " + name)
    patch.pop("META-INF/MANIFEST.MF", None)
    roots = {name.removesuffix(".class").split("$")[0] for name in patch if name.endswith(".class")}
    removed = {name for name in base if name.endswith(".class") and name.removesuffix(".class").split("$")[0] in roots}
    output = {name: content for name, content in base.items() if name not in removed}
    output.update(patch)
    output["com/sdcraft/core/GtmVehicles.class"] = patched_vehicle.read_bytes()
    plugin = base["plugin.yml"].decode("utf-8")
    plugin, count = re.subn(r"(?m)^version:.*$", "version: " + VERSION, plugin)
    if count != 1 or "commands:\n" not in plugin: raise ValueError("Unsupported plugin metadata")
    plugin = plugin.replace("commands:\n", "commands:\n  gtmweb:\n    description: Open the private GTM Control Centre\n    usage: /gtmweb\n    permission: sdcraft.admin\n", 1)
    output["plugin.yml"] = plugin.encode()
    # Defaults only. The updater never overwrites an existing server config.
    output["config.yml"] = base["config.yml"] + b"\n# Private local control centre; use SSH forwarding for remote access.\nweb-console:\n  enabled: true\n  port: 8765\n"
    changed = sorted(name for name in output if base.get(name) != output[name])
    unchanged = {name: content for name, content in base.items() if name in output and name not in changed}
    archive(dest, output)
    readback = members(dest)
    assert readback == output
    assert all(readback[name] == content for name, content in unchanged.items())
    return {"base_sha256": BASE_HASH, "sha256": sha(dest.read_bytes()), "bytes": dest.stat().st_size,
            "unchanged_entries": len(unchanged), "replaced_top_level_classes": sorted(roots),
            "removed_original_class_entries": len(removed), "changed_or_added_entries": changed,
            "vehicle_class_sha256": PATCH_HASH, "source_status": "Maintained source overlay and verified two-call-site patch over preserved 1.0.3; not a full original-source rebuild"}


def build(overlay: Path, vehicle: Path, packs: Path, output: Path, pack_url: str) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    core_path = "plugins/SDCraftCore-" + VERSION + ".jar"
    report = build_core(overlay, vehicle, output / core_path)
    pack_report = json.loads((packs / "pack-repair-report.json").read_text())
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
                "scope": "Update for the preserved functional 1.0.3 runtime; existing worlds, accounts, ownership, routes and configuration are retained."}
    (output / "repair-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "build-report.json").write_text(json.dumps(report, indent=2) + "\n")
    shutil.copyfile(packs / "pack-repair-report.json", output / "pack-repair-report.json")
    for source, name in [(ROOT / "tools/install_runtime_repair.py", "install_runtime_repair.py"),
                         (ROOT / "packaging/repair/Update-GTM.bat", "Update-GTM.bat"),
                         (ROOT / "packaging/repair/Update-GTM.sh", "Update-GTM.sh"),
                         (ROOT / "packaging/repair/Open-Control-Centre.bat", "Open-Control-Centre.bat")]:
        if source.is_file(): shutil.copyfile(source, output / name)
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--overlay", type=Path, required=True)
    p.add_argument("--vehicle-class", type=Path, required=True)
    p.add_argument("--packs", type=Path, default=ROOT / "build/repaired-packs")
    p.add_argument("--output", type=Path, default=ROOT / "build/repaired-release")
    p.add_argument("--pack-url", default="https://raw.githubusercontent.com/dev351en/gtm/fix/playable-ui-vehicles-20261125/resource-pack/EXPECT_SDCRAFT_ResourcePack_26.3.zip")
    args = p.parse_args()
    print(json.dumps(build(args.overlay, args.vehicle_class, args.packs, args.output, args.pack_url), indent=2))
