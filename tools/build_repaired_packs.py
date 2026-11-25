#!/usr/bin/env python3
"""Build the 1.0.4 repair packs from the hash-verified, preserved 1.0.3 payload.

The historical payload is immutable. Outputs go to a separate directory; this
tool does not deploy a server or edit its configuration. Its verification reads
the actual core's UI registry, not an independently maintained icon count.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import uuid
from zipfile import ZipFile

from PIL import Image, ImageDraw

from assemble_functional_runtime import copy_verified
from build_runtime_packs import archive, encoded, java_model, read_archive, texture_reference
from repair_rickshaw_canopy import repair_packs as repair_rickshaw_canopy

ROOT = Path(__file__).resolve().parents[1]
PRESERVED = ROOT / "runtime/functional-r4"
CORE = PRESERVED / "plugins/SDCraftCore-1.0.3-r4-functional-candidate.jar"
ALIASES = {
    "core_pistol": ("kavach_9", "minecraft:iron_hoe"),
    "core_shotgun": ("sher_pump", "minecraft:golden_hoe"),
    "core_smg": ("viper_sub", "minecraft:diamond_hoe"),
    "core_rifle": ("indrayani_carbine", "minecraft:netherite_hoe"),
}
SCREENS = {"home": (6, "\uf100"), "menu3": (3, "\uf101"),
           "menu4": (4, "\uf102"), "menu6": (6, "\uf103")}
ATLAS_BLOCKS = "assets/minecraft/atlases/blocks.json"
ATLAS_ITEMS = "assets/minecraft/atlases/items.json"
ITEM_DIRECTORIES = ("items", "custom", "ui", "finish", "outfits")
LEGACY_AMMO_MODEL = "assets/minecraft/models/item/phantom_membrane_org.json"


def preserved_bytes(path: str) -> bytes:
    manifest = json.loads((PRESERVED / "manifest.json").read_text())
    record = next(row for row in manifest["files"] if row["path"] == path)
    with tempfile.TemporaryDirectory(prefix="gtm-pack-input-") as folder:
        destination = Path(folder) / Path(path).name
        copy_verified(ROOT.resolve(), record, destination, "runtime/functional-r4/" + path)
        return destination.read_bytes()


def read_bytes(data: bytes) -> dict[str, bytes]:
    with tempfile.TemporaryDirectory(prefix="gtm-pack-read-") as folder:
        file = Path(folder) / "input.zip"
        file.write_bytes(data)
        return read_archive(file)


def core_ui(core: Path = CORE) -> list[dict[str, str]]:
    with ZipFile(core) as jar:
        rows = jar.read("ui/catalog.tsv").decode("utf-8").splitlines()
    result = []
    for line in rows:
        if not line or line.startswith("#"):
            continue
        identifier, model, family, title, texture, glyph = line.split("\t")
        result.append(dict(id=identifier, model=model, family=family, title=title,
                           texture=texture, glyph=glyph))
    return result


def png(image: Image.Image) -> bytes:
    output = io.BytesIO()
    image.save(output, format="PNG", optimize=False)
    return output.getvalue()


def screen(rows: int, home: bool = False) -> Image.Image:
    """Code-native inventory skin at the client's exact 176px GUI dimensions.

    Existing 128px app master art is not resized or modified in the pack. The
    container skin is a rectangular compatibility surface, not a new icon.
    """
    if rows not in (3, 4, 6):
        raise ValueError("Unsupported container row count")
    height = 114 + rows * 18
    image = Image.new("RGBA", (176, height), "#151b20")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 175, height - 1), fill="#151b20", outline="#d6ad59")
    draw.rectangle((2, 2, 173, height - 3), outline="#354249")
    draw.rectangle((3, 3, 172, 15), fill="#202a30")
    draw.line((7, 15, 168, 15), fill="#866c3f")
    if home:
        draw.rectangle((7, 19, 146, 105), fill="#10171b")
        draw.line((149, 19, 149, 105), fill="#41514c")
        for row in range(1, 5):
            for column in range(1, 7):
                x, y = 7 + column * 18, 17 + row * 18
                draw.rectangle((x, y, x + 17, y + 17), fill="#202a30")
            # Four usable shortcuts, one per row: assistant, gear, car, settings.
            x, y = 151, 17 + row * 18
            draw.rectangle((x, y, x + 17, y + 17), fill="#183a32", outline="#47735c")
        draw.line((8, 106, 167, 106), fill="#354249")
    else:
        for row in range(rows):
            for column in range(9):
                x, y = 7 + column * 18, 17 + row * 18
                draw.rectangle((x, y, x + 17, y + 17), fill="#192329", outline="#2d3c43")
    # The native inventory label is rendered by the client after its title.
    # Keep a light, high-contrast label strip beneath it, rather than masking
    # or pretending the player's actual inventory can be removed by a pack.
    boundary = 18 * rows + 18
    draw.rectangle((5, boundary, 170, boundary + 11), fill="#d2b997")
    for row in range(3):
        for column in range(9):
            x, y = 7 + 18 * column, 18 * rows + 30 + 18 * row
            draw.rectangle((x, y, x + 17, y + 17), fill="#202b31", outline="#526066")
    for column in range(9):
        x, y = 7 + 18 * column, 18 * rows + 88
        draw.rectangle((x, y, x + 17, y + 17), fill="#24362f", outline="#64806c")
    return image


def add_screens(java: dict[str, bytes]):
    providers = [{"type": "space", "advances": {"\uf010": -8, "\uf011": -169}}]
    for name, (rows, character) in SCREENS.items():
        image = screen(rows, name == "home")
        path = f"assets/gtm/textures/gui/phone_{name}.png"
        java[path] = png(image)
        providers.append({"type": "bitmap", "file": f"gtm:gui/phone_{name}.png",
                          "height": image.height, "ascent": 13, "chars": [character]})
    java["assets/gtm/font/phone_screen.json"] = encoded({"providers": providers})


def add_aliases(java: dict[str, bytes], bedrock: dict[str, bytes], mappings: dict):
    for alias, (native, base) in ALIASES.items():
        java[f"assets/gtm/items/{alias}.json"] = java[f"assets/gtm/items/{native}.json"]
        attachable = json.loads(bedrock[f"attachables/{native}.json"])
        attachable["minecraft:attachable"]["description"]["identifier"] = "gtm:" + alias
        bedrock[f"attachables/{alias}.json"] = encoded(attachable)
        sources = [row for row in mappings["items"]["minecraft:paper"]
                   if row.get("model") == "gtm:" + native]
        if len(sources) != 1:
            raise ValueError("Ambiguous native weapon mapping: " + native)
        row = deepcopy(sources[0])
        row["model"] = row["bedrock_identifier"] = "gtm:" + alias
        if any(r.get("model") == row["model"] for values in mappings["items"].values() for r in values):
            raise ValueError("Duplicate alias: " + alias)
        mappings["items"].setdefault(base, []).append(row)


def repair_atlases(java: dict[str, bytes]):
    # 26.3 stitches item/ and block/ into separate vanilla atlases. A PNG's
    # existence does not make arbitrary ui/, finish/ or outfits/ paths visible.
    # The inherited blocks override also copied item sprites into both atlases.
    # Atlas source lists merge with vanilla: leave its block list alone and add
    # only the extra item directories, without copying vanilla item/ again.
    java[ATLAS_BLOCKS] = encoded({"sources": []})
    java[ATLAS_ITEMS] = encoded({"sources": [
        {"type": "minecraft:directory", "source": path, "prefix": path + "/"}
        for path in ITEM_DIRECTORIES
    ]})


def repair_legacy_json(java: dict[str, bytes]):
    # The inherited backup model is not selected by an item, but Minecraft
    # parses it during reload. Its original ten override records lack commas.
    # Keep every predicate/model unchanged and repair only the serialization.
    original = java[LEGACY_AMMO_MODEL].decode("utf-8")
    fixed = original.replace('}\n       {', '},\n       {')
    data = json.loads(fixed)
    if [row["predicate"].get("custom_model_data") for row in data.get("overrides", [])] != list(range(1, 11)):
        raise ValueError("Unexpected legacy ammo backup model; refusing an unrelated repair")
    java[LEGACY_AMMO_MODEL] = encoded(data)


def atlas_sprites(java: dict[str, bytes], atlas: str) -> set[str]:
    """Evaluate the relevant 26.3 directory/single atlas providers.

    Vanilla item/ and block/ sources are supplied by the client. Custom PNGs
    outside those paths require an explicit provider in the effective atlas.
    """
    base = "item" if atlas == "items" else "block"
    sources = [{"type": "directory", "source": base, "prefix": base + "/"}]
    data = java.get(f"assets/minecraft/atlases/{atlas}.json")
    if data:
        sources += json.loads(data)["sources"]
    sprites = set()
    for source in sources:
        kind = source["type"].removeprefix("minecraft:")
        if kind == "directory":
            prefix = "/textures/" + source["source"].rstrip("/") + "/"
            for name in java:
                if name.startswith("assets/") and prefix in name and name.endswith(".png"):
                    namespace = name.split("/", 2)[1]
                    tail = name.split(prefix, 1)[1].removesuffix(".png")
                    sprites.add(namespace + ":" + source.get("prefix", "") + tail)
        elif kind == "single":
            resource = source["resource"]
            if java_path(resource, "textures", ".png") in java:
                sprite = source.get("sprite", resource)
                sprites.add(sprite if ":" in sprite else "minecraft:" + sprite)
        else:
            raise ValueError("Unsupported custom item/block atlas provider: " + kind)
    return sprites


def repair_weapon_poses(java: dict[str, bytes], core: Path = CORE) -> list[str]:
    # The original models put their meshes near y=0..8, yet inherited the block
    # hand pose with no vertical translation. The real client showed only a tiny
    # piece below the screen. Preserve geometry, texture and GUI views; change
    # only first-person placement for functional guns and their own finishes.
    with ZipFile(core) as jar:
        rows = [row.split("\t") for row in jar.read("equipment/catalog.tsv").decode().splitlines()
                if row and not row.startswith("#")]
        native = {row[0] for row in rows if row[2] in {"RANGED", "SCATTER", "PRECISION", "PULSE"}}
        finished = {row.split("\t")[0] for row in jar.read("equipment/finishes.tsv").decode().splitlines()
                    if row and not row.startswith("#") and row.split("\t")[1] in native}
    changed = []
    for identifier in sorted(native | finished):
        definition = json.loads(java[java_path(identifier, "items", ".json")])
        for reference in model_nodes(definition):
            path = java_path(reference, "models", ".json")
            data = json.loads(java[path])
            display = data.setdefault("display", {})
            for hand, yaw in (("righthand", 45), ("lefthand", -45)):
                display["firstperson_" + hand] = {"rotation": [0, yaw, 0],
                                                "translation": [0, 6, 0], "scale": [.65, .65, .65]}
            java[path] = encoded(data)
            changed.append(path)
    return sorted(set(changed))


def model_nodes(node):
    if isinstance(node, dict):
        if node.get("type", "").removeprefix("minecraft:") == "model" and isinstance(node.get("model"), str):
            yield node["model"]
        for value in node.values():
            yield from model_nodes(value)
    elif isinstance(node, list):
        for value in node:
            yield from model_nodes(value)


def java_path(reference: str, kind: str, suffix: str) -> str:
    namespace, key = reference.split(":", 1) if ":" in reference else ("minecraft", reference)
    if not namespace or not key or ".." in key.split("/") or key.startswith("/"):
        raise ValueError("Unsafe resource reference: " + reference)
    return f"assets/{namespace}/{kind}/{key}{suffix}"


def validate_java(java: dict[str, bytes], core: Path = CORE, require_skin: bool = True) -> dict:
    required = core_ui(core)
    for row in required:
        path = java_path(row["model"], "items", ".json")
        if path not in java:
            raise ValueError("Missing runtime UI item definition: " + row["model"])
    if require_skin:
        for alias in ALIASES:
            if f"assets/gtm/items/{alias}.json" not in java:
                raise ValueError("Missing usable core weapon alias: " + alias)
        if "assets/gtm/font/phone_screen.json" not in java:
            raise ValueError("Missing phone screen font")
    item_sprites, block_sprites = atlas_sprites(java, "items"), atlas_sprites(java, "blocks")
    duplicates = item_sprites & block_sprites
    if duplicates:
        raise ValueError("Sprites copied into both item and block atlases: " + sorted(duplicates)[0])
    refs, textures, font_files, custom_items, parsed_models = set(), set(), set(), 0, 0
    for path, content in java.items():
        if "/models/" in path and path.endswith(".json"):
            try:
                parsed = json.loads(content)
            except (ValueError, UnicodeError) as failure:
                raise ValueError("Malformed model JSON: " + path) from failure
            if not isinstance(parsed, dict):
                raise ValueError("Model must be a JSON object: " + path)
            parsed_models += 1
        if path.startswith("assets/") and "/items/" in path and path.endswith(".json"):
            refs.update(model_nodes(json.loads(content)))
            custom_items += int(not path.startswith("assets/minecraft/"))
        if path.startswith("assets/gtm/font/") and path.endswith(".json"):
            for provider in json.loads(content)["providers"]:
                if provider["type"] == "bitmap":
                    file = java_path(provider["file"], "textures", "")
                    if file not in java:
                        raise ValueError("Missing font bitmap: " + file)
                    with Image.open(io.BytesIO(java[file])) as bitmap:
                        if not bitmap.convert("RGBA").getchannel("A").getbbox():
                            raise ValueError("Empty font bitmap: " + file)
                    font_files.add(file)
    for reference in sorted(refs):
        reference = reference if ":" in reference else "minecraft:" + reference
        model = java_model(java, reference)
        # Generated item parents have no element faces. Checking faces alone
        # missed the original phone bug, so validate every inherited layer too.
        raw_refs = set(model.get("textures", {}).values())
        for element in model.get("elements", []):
            raw_refs.update(face["texture"] for face in element.get("faces", {}).values())
        for raw in raw_refs:
            resolved = texture_reference(model.get("textures", {}), raw)
            file = java_path(resolved, "textures", ".png")
            if file not in java and not file.startswith("assets/minecraft/"):
                raise ValueError("Missing model texture: " + resolved)
            canonical = resolved if ":" in resolved else "minecraft:" + resolved
            if not canonical.startswith("minecraft:") and canonical not in item_sprites | block_sprites:
                raise ValueError("Model texture exists but is absent from render atlases: " + canonical)
            textures.add(resolved)
    for name, (rows, _) in SCREENS.items():
        path = f"assets/gtm/textures/gui/phone_{name}.png"
        if require_skin:
            with Image.open(io.BytesIO(java[path])) as image:
                if image.size != (176, 114 + rows * 18):
                    raise ValueError("Phone container skin does not match slot geometry")
    return {"runtime_ui_items": len(required), "phone_apps": sum(r["family"] == "phone" for r in required),
            "custom_item_definitions": custom_items, "resolved_item_model_roots": len(refs),
            "parsed_model_json_files": parsed_models,
            "model_texture_references": len(textures), "font_bitmaps": len(font_files),
            "custom_atlas_sprites": sum(not value.startswith("minecraft:") for value in item_sprites | block_sprites),
            "duplicate_item_block_sprites": len(duplicates),
            "phone_skins": len(SCREENS) if require_skin else 0,
            "native_client_render_test": "not_run_by_static_builder; see separate native-java acceptance record"}


def validate_bedrock(bedrock: dict[str, bytes], mappings: dict) -> dict:
    identifiers = set()
    geometries = set()
    for name, content in bedrock.items():
        if name.endswith(".geo.json"):
            geometries.update(row["description"]["identifier"] for row in json.loads(content)["minecraft:geometry"])
    icons = json.loads(bedrock["textures/item_texture.json"])["texture_data"]
    aliases = 0
    for base, entries in mappings["items"].items():
        for entry in entries:
            identifier = entry["bedrock_identifier"]
            if identifier in identifiers:
                raise ValueError("Duplicate Bedrock identifier: " + identifier)
            identifiers.add(identifier)
            if identifier.removeprefix("gtm:") not in ALIASES:
                continue
            alias = identifier.removeprefix("gtm:")
            if base != ALIASES[alias][1]:
                raise ValueError("Weapon alias attached to wrong base material: " + alias)
            description = json.loads(bedrock[f"attachables/{alias}.json"])["minecraft:attachable"]["description"]
            if description["identifier"] != identifier or description["geometry"]["default"] not in geometries:
                raise ValueError("Broken Bedrock weapon alias: " + identifier)
            if description["textures"]["default"] + ".png" not in bedrock:
                raise ValueError("Missing Bedrock weapon texture")
            if icons[entry["bedrock_options"]["icon"]]["textures"] + ".png" not in bedrock:
                raise ValueError("Missing Bedrock weapon icon")
            aliases += 1
    if aliases != len(ALIASES):
        raise ValueError("Missing cross-platform weapon aliases")
    return {"unique_identifiers": len(identifiers), "weapon_aliases": aliases,
            "bedrock_native_gui": "native inventory fallback; Java font skin is not sent as a Bedrock GUI"}


def build(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    java_input = preserved_bytes("resourcepacks/GTM_Local_Java.zip")
    bed_input = preserved_bytes("plugins/Geyser-Spigot/packs/GTM_Local_Bedrock.mcpack")
    java, bedrock = read_bytes(java_input), read_bytes(bed_input)
    mapping_data = preserved_bytes("plugins/Geyser-Spigot/custom_mappings/gtm_native128.json")
    mappings = json.loads(mapping_data)
    add_screens(java)
    add_aliases(java, bedrock, mappings)
    repair_atlases(java)
    repair_legacy_json(java)
    pose_models = repair_weapon_poses(java)
    canopy_report = repair_rickshaw_canopy(java, bedrock)
    metadata = json.loads(java["pack.mcmeta"])
    metadata["pack"]["description"] = "GTM Indraprastha · 1.0.4 · Phone UI, native128 models and compatibility"
    java["pack.mcmeta"] = encoded(metadata)
    manifest = json.loads(bedrock["manifest.json"])
    # A new content-versioned identity prevents the old hash-derived version
    # number from making clients treat this repaired pack as a downgrade.
    manifest["header"]["version"] = [1, 0, 4]
    manifest["header"]["uuid"] = str(uuid.uuid5(uuid.NAMESPACE_URL, "https://github.com/dev351en/gtm/repair104/bedrock"))
    manifest["header"]["name"] = "GTM Indraprastha 128 · Repair 1.0.4"
    for module in manifest["modules"]:
        module["version"] = [1, 0, 4]
        module["uuid"] = str(uuid.uuid5(uuid.NAMESPACE_URL, "https://github.com/dev351en/gtm/repair104/bedrock/" + module["type"]))
    bedrock["manifest.json"] = encoded(manifest)
    report = {"version": "1.0.4-r4-repair", "input_java_sha256": hashlib.sha256(java_input).hexdigest(),
              "input_bedrock_sha256": hashlib.sha256(bed_input).hexdigest(),
              "checks": validate_java(java), "bedrock_checks": validate_bedrock(bedrock, mappings),
              "first_person_pose_models": len(pose_models),
              "traditional_rickshaw_canopy": canopy_report,
              "preserved_original_payload": True, "deployment": "not_performed"}
    report["packs"] = [archive(output / "GTM_Repair_128_Java.zip", java),
                       archive(output / "GTM_Repair_128_Bedrock.mcpack", bedrock)]
    (output / "gtm_native128.json").write_bytes(encoded(mappings))
    report["mapping_sha256"] = hashlib.sha256((output / "gtm_native128.json").read_bytes()).hexdigest()
    report["java_pack_id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, report["packs"][0]["sha256"]))
    report["source_attribution"] = (
        "Preserved native128 source textures and stable identities; code-authored inventory compatibility skin, "
        "atlas registration, first-person gun poses, and a bounded traditional-auto canopy/post geometry repair. "
        "No new unique texture artwork.")
    (output / "pack-repair-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/repaired-packs")
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))
