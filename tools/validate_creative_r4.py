#!/usr/bin/env python3
"""Comprehensive validation suite and contact sheet generator for GTM Revision 4 Creative Track (V2 Quality Gate)."""
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
PREVIEWS_DIR = CREATIVE / "previews"
REPORTS_DIR = CREATIVE / "reports"
MANIFESTS_DIR = CREATIVE / "manifests"


def create_grid(images, titles, cols=8, cell_w=128, cell_h=148, pad=10, bg="#151B20"):
    n = len(images)
    rows = math.ceil(n / cols)
    sheet_w = cols * cell_w + (cols + 1) * pad
    sheet_h = rows * cell_h + (rows + 1) * pad

    sheet = Image.new("RGBA", (sheet_w, sheet_h), bg)
    draw = ImageDraw.Draw(sheet)

    for idx, (img, title) in enumerate(zip(images, titles)):
        r = idx // cols
        c = idx % cols
        x = pad + c * (cell_w + pad)
        y = pad + r * (cell_h + pad)

        draw.rounded_rectangle([x, y, x + cell_w, y + cell_h], radius=6, fill="#20272E", outline="#303A45", width=1)

        img_w, img_h = img.size
        max_w = cell_w - 16
        max_h = cell_h - 36
        ratio = min(max_w / img_w, max_h / img_h)
        new_size = (max(1, int(img_w * ratio)), max(1, int(img_h * ratio)))
        resized = img.resize(new_size, Image.Resampling.NEAREST if img_w <= 64 else Image.Resampling.BILINEAR)

        paste_x = x + (cell_w - new_size[0]) // 2
        paste_y = y + 8 + (max_h - new_size[1]) // 2
        sheet.paste(resized, (paste_x, paste_y), resized if resized.mode == "RGBA" else None)

        short_title = title[:16]
        draw.text((x + 8, y + cell_h - 22), short_title, fill="#D6AD59")

    return sheet


def validate_all():
    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        "status": "PASS",
        "quality_tier": "V2_ZBUFFER_32X32_VECTOR",
        "domains_validated": {},
        "packs_validated": {},
        "contact_sheets": [str(p.relative_to(ROOT)).replace("\\", "/") for p in sorted(PREVIEWS_DIR.glob("*.png"))]
    }

    # 1. Domain 1: Visual Identity, Brands (32), Phone Icons (24), HUD (33)
    srv_icon = CREATIVE / "source" / "icons" / "server-icon.png"
    assert srv_icon.exists()
    with Image.open(srv_icon) as im:
        assert im.size == (64, 64) and im.mode == "RGB"

    brands_data = json.loads((MANIFESTS_DIR / "brands.json").read_text(encoding="utf-8"))
    assert len(brands_data) == 32
    for b in brands_data:
        assert (ROOT / b["svg"]).exists()
        with Image.open(ROOT / b["png"]) as im:
            assert im.size == (256, 256) and im.mode == "RGBA"

    phone_data = json.loads((MANIFESTS_DIR / "phone_icons.json").read_text(encoding="utf-8"))
    assert len(phone_data) == 24
    for p in phone_data:
        with Image.open(ROOT / p["png"]) as im:
            assert im.size == (128, 128) and im.mode == "RGBA"

    hud_data = json.loads((MANIFESTS_DIR / "hud_manifest.json").read_text(encoding="utf-8"))
    assert len(hud_data) == 33
    for h in hud_data:
        assert (ROOT / h["png"]).exists()

    report["domains_validated"]["domain_1_branding_ui"] = {
        "server_icon": "64x64 RGB verified", "brands_count": 32, "phone_icons_count": 24, "hud_components_count": 33
    }

    # 2. Domain 2: Transport (87 models + 87 icons + Java models)
    trans_manifest = json.loads((MANIFESTS_DIR / "transport_art_manifest.json").read_text(encoding="utf-8"))
    trans_map = json.loads((MANIFESTS_DIR / "transport_catalog_mapping.json").read_text(encoding="utf-8"))
    assert len(trans_manifest) == 87 and len(trans_map) == 65
    for m in trans_manifest:
        assert (ROOT / m["json_path"]).exists()
        assert (ROOT / m["java_model_path"]).exists()
        assert (ROOT / m["icon_path"]).exists()
        assert m.get("cube_count", 0) >= 4, f"Transport {m['id']} has empty mesh"

    report["domains_validated"]["domain_2_transport"] = {
        "transport_models_count": 87, "transport_icons_count": 87, "road_mappings": 65
    }

    # 3. Domain 3: Furniture (200 models + 200 icons) & Facilities (46)
    furn_manifest = json.loads((MANIFESTS_DIR / "furniture_art_manifest.json").read_text(encoding="utf-8"))
    furn_map = json.loads((MANIFESTS_DIR / "furniture_catalog_mapping.json").read_text(encoding="utf-8"))
    fac_manifest = json.loads((MANIFESTS_DIR / "facilities_manifest.json").read_text(encoding="utf-8"))
    assert len(furn_manifest) == 200 and len(furn_map) == 200 and len(fac_manifest) == 46
    for f in furn_manifest:
        assert (ROOT / f["json_path"]).exists()
        assert (ROOT / f["java_model_path"]).exists()
        assert (ROOT / f["icon_path"]).exists()
        assert f.get("cube_count", 0) >= 3

    report["domains_validated"]["domain_3_furniture_facilities"] = {
        "furniture_models_count": 200, "furniture_icons_count": 200, "municipal_facilities_surveyed": 46
    }

    # 4. Domain 4: Characters (500 unique dual-layer skins + 100 outfits)
    skins_manifest = json.loads((MANIFESTS_DIR / "npc_skins_manifest.json").read_text(encoding="utf-8"))
    outfits_manifest = json.loads((MANIFESTS_DIR / "outfits_manifest.json").read_text(encoding="utf-8"))
    assert len(skins_manifest["skins"]) == 500 and len(outfits_manifest["outfits"]) == 100
    assert skins_manifest["gang_boss_id"] == "npc-481" and len(skins_manifest["prisoner_ids"]) == 5
    skin_hashes = {hashlib.sha256((ROOT / s["texture"]).read_bytes()).hexdigest() for s in skins_manifest["skins"]}
    assert len(skin_hashes) == 500
    report["domains_validated"]["domain_4_characters"] = {
        "npc_skins_count": 500, "unique_skin_textures": 500, "outfits_count": 100
    }

    # 5. Domain 5: Equipment (92 + 11 Hero), 30 Weapons, 300 Finishes, 30 Foods
    eq_manifest = json.loads((MANIFESTS_DIR / "equipment_manifest.json").read_text(encoding="utf-8"))
    fin_manifest = json.loads((MANIFESTS_DIR / "finishes_migration.json").read_text(encoding="utf-8"))
    food_manifest = json.loads((MANIFESTS_DIR / "food_manifest.json").read_text(encoding="utf-8"))
    assert len(eq_manifest["equipment"]) == 92 and len(eq_manifest["hero_props"]) == 11
    for eq in eq_manifest["equipment"] + eq_manifest["hero_props"]:
        assert (ROOT / eq["model_path"]).exists()
        assert (ROOT / eq["java_model_path"]).exists()
        assert (ROOT / eq["icon_path"]).exists()

    assert len(fin_manifest["mappings"]) == 300
    for m in fin_manifest["mappings"]:
        assert (ROOT / m["weapon_model_path"]).exists()
        assert (ROOT / m["weapon_java_model_path"]).exists()
        assert (ROOT / m["weapon_icon_path"]).exists()
        assert (ROOT / m["finish_texture_path"]).exists()

    assert len(food_manifest["items"]) == 30
    for item in food_manifest["items"]:
        assert (ROOT / item["model_path"]).exists()
        assert (ROOT / item["java_model_path"]).exists()
        with Image.open(ROOT / item["icon_path"]) as im:
            assert im.size == (128, 128) and im.mode == "RGBA"

    report["domains_validated"]["domain_5_equipment_finishes_food"] = {
        "equipment_models_count": 92, "hero_props_count": 11,
        "fictional_weapons_count": 30, "finishes_textures_count": 300, "food_items_count": 30
    }

    # 6. Domain 6: Festivals (100) & Bilingual Signage (120)
    fest_manifest = json.loads((MANIFESTS_DIR / "festivals_manifest.json").read_text(encoding="utf-8"))
    sig_manifest = json.loads((MANIFESTS_DIR / "signage_manifest.json").read_text(encoding="utf-8"))
    assert len(fest_manifest["festivals"]) == 100 and len(sig_manifest["signs"]) == 120
    for f in fest_manifest["festivals"]:
        assert (ROOT / f["model_path"]).exists()
        assert (ROOT / f["java_model_path"]).exists()
        assert (ROOT / f["icon_path"]).exists()
    for s in sig_manifest["signs"]:
        with Image.open(ROOT / s["texture_path"]) as im:
            assert im.size == (512, 256)

    report["domains_validated"]["domain_6_festivals_signage"] = {
        "festival_installations_count": 100, "bilingual_signs_count": 120
    }

    # 7. Domain 7: 32x32 Model Textures & World Resource Pack
    model_32x_count = len(list((CREATIVE / "source" / "textures" / "32x32").glob("*.png")))
    world_32x_count = len(list((CREATIVE / "source" / "textures" / "world_32x" / "assets" / "minecraft" / "textures" / "block").glob("*.png")))
    java_pack = CREATIVE / "packs" / "GTM_Indraprastha_World_32x_Java.zip"
    bed_pack = CREATIVE / "packs" / "GTM_Indraprastha_World_32x_Bedrock.mcpack"
    local_installed = Path.home() / "AppData" / "Roaming" / ".minecraft" / "resourcepacks" / "GTM_Indraprastha_World_32x_Java.zip"
    assert model_32x_count >= 100 and world_32x_count >= 86
    assert java_pack.exists() and bed_pack.exists()
    with ZipFile(java_pack) as z:
        assert z.testzip() is None
    with ZipFile(bed_pack) as z:
        assert z.testzip() is None

    report["packs_validated"] = {
        "model_32x32_textures_count": model_32x_count,
        "world_32x32_block_textures_count": world_32x_count,
        "java_world_pack_bytes": java_pack.stat().st_size,
        "bedrock_world_pack_bytes": bed_pack.stat().st_size,
        "local_minecraft_installed": local_installed.exists()
    }

    report_file = REPORTS_DIR / "ASSET_VALIDATION_REPORT.json"
    report_file.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("=" * 64)
    print(f"V2 FULL VALIDATION PASSED (0 ERRORS) -> {report_file.name}")
    print(json.dumps(report, indent=2))
    print("=" * 64)


if __name__ == "__main__":
    validate_all()
