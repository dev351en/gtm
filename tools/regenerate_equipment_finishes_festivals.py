#!/usr/bin/env python3
"""
Faithful 32x Overhaul for:
1. All 11 User Hero 3D Props (preserved JSON + enriched Bedrock .geo.json + crisp 32x32 Faithful pixel sprites).
2. All 92 Equipment Props (per-face Faithful 32x UVs + pixel-locked Faithful isometric icons).
3. All 30 Fictional Weapons (distinct real-world sculpted 3D silhouettes + hand-crafted 48x48 Faithful pixel icons)
   + 300 crisp pixel-art 64x64 Weapon Finish textures + updated finishes_migration.json.
4. All 100 Festival Installations (8 themes with rangoli, toran & lamp UV tiles + Faithful isometric icons).
"""
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
import faithful_32x_palette as f32
import studio_3d_engine as s3d
import city_item_art
import city_festival_art
import validate_creative_r4 as v4

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
MODELS_DIR = CREATIVE / "source" / "models"
ICONS_DIR = CREATIVE / "source" / "icons"
TEX_DIR = CREATIVE / "source" / "textures"
MANIFESTS = CREATIVE / "manifests"
PREVIEWS = CREATIVE / "previews"
UPLOAD_DIR = Path(r"C:\Users\brode\.gemini\antigravity\brain\ceee3c26-6ae4-4f1c-b357-09eb59f51997\.user_uploaded")

UPLOADED_HERO_PROPS = [
    ("hero_medkit", "media_1795517373640_fbfd6222.json", "Trauma Medkit Pouch"),
    ("hero_atm_card", "media_1795517373641_766eeed9.json", "ARK VIP Debit Card"),
    ("hero_police_badge", "media_1795517373641_8f52ae25.json", "SDPD Detective Badge & Wallet"),
    ("hero_cash_bundle", "media_1795517373641_b6e27b11.json", "Cash Currency Stack"),
    ("hero_shotgun", "media_1795531381382_46b54742.json", "Shotgun Prop Mesh"),
    ("hero_jerrycan", "media_1795531381382_746050e8.json", "Fuel Jerrycan"),
    ("hero_rifle", "media_1795531381382_77a12ec4.json", "Assault Rifle Prop Mesh"),
    ("hero_key_fob", "media_1795531381382_8d66a534.json", "Vehicle Smart Key Fob"),
    ("hero_pistol", "media_1795531381382_e3925f91.json", "Sidearm Pistol Prop Mesh"),
    ("hero_baseball_bat", "media_1795531381456_864a9c54.json", "Wooden Baseball Bat"),
    ("hero_smg", "media_1795531409892_63d65d67.json", "Compact SMG Prop Mesh")
]


def _ramp(hex_c: str, contrast: float = 1.0):
    r = f32.make_ramp(hex_c, contrast=contrast)
    return [tuple(int(v) for v in c) + (255,) for c in r]


def draw_hero_faithful_sprite(hid: str) -> s3d.PixelSprite:
    """Crisp 32x32 Faithful pixel-art held item icon matching Minecraft Faithful 32x inventory style."""
    sp = s3d.PixelSprite(32, 32)
    steel = _ramp("#8B98A8", 1.1)
    dark = _ramp("#2A313B", 1.05)
    wood = _ramp("#8E5229", 1.0)
    gold = _ramp("#D6AD59", 1.05)

    if hid == "hero_medkit":
        sp.rect(12, 5, 8, 3, steel[3]); sp.rect(13, 6, 6, 2, (0, 0, 0, 0))
        sp.shade_bevel("#2E6B52", 5, 8, 22, 18, corner_cut=2)
        sp.rect(8, 12, 16, 11, "#F8FAFC")
        sp.rect(14, 14, 4, 7, "#DC2626"); sp.rect(12, 16, 8, 3, "#DC2626")
    elif hid == "hero_atm_card":
        sp.shade_bevel("#19222C", 4, 9, 24, 15, corner_cut=2)
        sp.rect(4, 12, 24, 2, gold[4])
        sp.shade_bevel("#D6AD59", 7, 15, 5, 4, corner_cut=0)
        sp.rect(14, 16, 10, 2, "#E2E8F0"); sp.rect(14, 19, 7, 2, "#94A3B8")
    elif hid == "hero_police_badge":
        sp.shade_bevel("#7C421C", 4, 7, 12, 18, corner_cut=1)
        sp.shade_bevel("#8B4E24", 16, 7, 12, 18, corner_cut=1)
        sp.disc(22, 16, 5, gold[4]); sp.disc(22, 16, 2, gold[5])
        sp.rect(6, 10, 8, 12, "#F1F5F9"); sp.rect(7, 12, 6, 4, "#3B82F6")
    elif hid == "hero_cash_bundle":
        sp.shade_bevel("#22754B", 5, 10, 22, 13, corner_cut=1)
        sp.rect(6, 21, 20, 3, "#E5E2C9")
        sp.rect(13, 10, 6, 14, gold[4]); sp.rect(14, 13, 4, 6, gold[5])
    elif hid == "hero_jerrycan":
        sp.shade_bevel("#C92A2A", 7, 8, 18, 19, corner_cut=2)
        sp.rect(11, 5, 8, 3, "#991B1B"); sp.rect(20, 6, 4, 4, gold[4])
        sp.line(10, 12, 22, 24, "#991B1B", 2); sp.line(22, 12, 10, 24, "#991B1B", 2)
    elif hid == "hero_key_fob":
        sp.disc(11, 21, 4, steel[4]); sp.disc(11, 21, 2, (0, 0, 0, 0))
        sp.shade_bevel("#2A313B", 12, 7, 11, 13, corner_cut=2)
        sp.rect(15, 10, 5, 3, "#38BDF8"); sp.rect(15, 15, 5, 3, "#F59E0B")
        sp.line(19, 12, 27, 5, steel[5], 2)
    elif hid == "hero_baseball_bat":
        sp.line(6, 26, 25, 7, wood[3], 3)
        sp.line(20, 12, 25, 7, wood[5], 4)
        sp.line(6, 26, 11, 21, dark[1], 3)
    elif hid == "hero_pistol":
        return draw_weapon_sprite("kavach_9", "sidearm", 0)
    elif hid == "hero_shotgun":
        return draw_weapon_sprite("sher_pump", "shotgun", 0)
    elif hid == "hero_smg":
        return draw_weapon_sprite("viper_sub", "smg", 1)
    else:  # rifle
        return draw_weapon_sprite("indrayani_carbine", "rifle", 0)

    sp.add_outline(col=(14, 16, 26, 255))
    return sp


def draw_weapon_sprite(wid: str, wclass: str, var: int) -> s3d.PixelSprite:
    """Hand-crafted 48x48 Faithful 32x pixel-art weapon sprite with sharp 1px specular & silhouette variety."""
    sp = s3d.PixelSprite(48, 48)
    pal_accents = ["#D6AD59", "#CBD5E1", "#22C55E", "#F59E0B", "#E879F9", "#22D3EE"]
    acc = _ramp(pal_accents[var % 6], 1.15)
    body = _ramp("#4A5568" if var % 2 == 0 else "#64748B", 1.15)
    stl = _ramp("#B8C6D6", 1.15)
    wal = _ramp("#8B4E24", 1.05)
    grip = wal if (var % 3 == 0 or "rajput" in wid or "sher" in wid or "tulwar" in wid or "konkan" in wid) else _ramp("#2A3038", 1.05)

    if wclass == "melee":
        if "bat" in wid:
            sp.line(8, 40, 39, 9, wal[3], 4)
            sp.line(28, 20, 39, 9, wal[4], 6)
            sp.line(29, 19, 38, 10, acc[5], 2)
            sp.line(8, 40, 15, 33, _ramp("#1F242C")[2], 4)
        elif "lathi" in wid:
            sp.line(8, 39, 39, 8, _ramp("#1E3A8A")[3], 4)
            sp.line(9, 38, 38, 9, _ramp("#60A5FA")[5], 1)
            sp.line(18, 29, 12, 23, _ramp("#1E242B")[2], 3)  # tonfa side handle
            sp.rect(36, 7, 4, 4, stl[5])
        elif "talwar" in wid:
            # Swept curved Indian cavalry blade + disc pommel hilt
            for t in range(28):
                x = 13 + t
                y = int(34 - t * 0.85 - (t * t) * 0.012)
                w = 4 if t > 18 else 3
                sp.rect(x, y, w, 3, stl[4] if t % 2 else stl[3])
                sp.px(x, y, stl[5])
            sp.line(9, 36, 15, 32, acc[4], 3)
            sp.line(12, 29, 17, 36, acc[5], 2)
            sp.disc(8, 38, 3, acc[5])
        else:  # khanda broadsword
            sp.line(11, 37, 38, 10, stl[3], 5)
            sp.line(12, 36, 39, 9, stl[5], 2)
            sp.rect(37, 8, 5, 5, stl[4])
            sp.line(10, 30, 18, 38, acc[5], 3)
            sp.line(8, 40, 13, 35, acc[4], 3)
            sp.line(6, 42, 9, 39, acc[5], 2)  # khanda spike pommel
    elif wclass == "sidearm":
        if "konkan" in wid:  # 6-shot revolver
            sp.line(11, 24, 15, 36, wal[3], 5)
            sp.rect(14, 17, 13, 8, stl[3]); sp.rect(14, 17, 13, 2, stl[5])  # cylinder + frame
            sp.rect(17, 18, 7, 6, acc[3])  # cylinder flutes
            sp.rect(26, 17, 14, 3, stl[4]); sp.rect(26, 16, 14, 1, stl[5])  # long barrel rib
            sp.rect(18, 25, 5, 4, body[2])
        elif "astra" in wid:  # twin over-under pocket derringer
            sp.line(15, 25, 19, 34, acc[4], 5)
            sp.rect(17, 18, 15, 7, stl[4]); sp.rect(17, 18, 15, 2, stl[5])
            sp.rect(17, 22, 15, 2, stl[2])
        else:
            sp.line(12, 23, 15, 37, grip[3], 5)
            sp.rect(12, 19, 20, 4, body[3])
            sp.rect(12, 14, 21, 5, acc[4] if var % 2 == 0 else stl[4])
            sp.rect(12, 14, 21, 1, acc[5] if var % 2 == 0 else stl[5])
            sp.rect(19, 23, 5, 4, body[2])
            if var in (2, 5) or "maratha" in wid:
                sp.rect(33, 15, 9, 4, body[1]); sp.rect(33, 15, 9, 1, body[4])  # silencer
    elif wclass == "shotgun":
        if "cyclone" in wid:  # coach double-barrel
            sp.line(5, 31, 14, 25, wal[3], 5)
            sp.rect(13, 19, 10, 5, stl[3])
            sp.rect(23, 17, 19, 4, stl[4]); sp.rect(23, 17, 19, 1, stl[5])
            sp.rect(24, 21, 12, 3, wal[4])
        elif "tulwar" in wid:  # sawed-off
            sp.line(9, 29, 15, 24, wal[3], 5)
            sp.rect(14, 19, 8, 5, body[3])
            sp.rect(22, 18, 12, 4, stl[4]); sp.rect(22, 18, 12, 1, stl[5])
        else:
            sp.rect(4, 21, 11, 5, grip[3]); sp.rect(4, 21, 11, 1, grip[4])  # stock
            sp.rect(15, 19, 12, 5, body[3]); sp.rect(15, 19, 12, 1, body[5])
            sp.rect(27, 18, 16, 2, stl[4]); sp.rect(27, 18, 16, 1, stl[5])  # top barrel
            sp.rect(27, 21, 13, 2, stl[2])  # tube mag
            if "ghadial" in wid:
                sp.rect(20, 24, 5, 9, acc[3])  # drum/box mag
            else:
                sp.rect(28, 20, 8, 4, acc[4])  # pump grip
    elif wclass == "smg":
        if "shikari" in wid:  # P90 compact PDW
            sp.rect(7, 19, 18, 8, body[3])
            sp.rect(14, 16, 18, 3, acc[4])  # top translucent mag
            sp.rect(25, 19, 10, 6, body[4]); sp.rect(29, 14, 4, 3, "#38BDF8")
            sp.rect(35, 21, 7, 3, stl[4])
        else:
            sp.rect(5, 20, 9, 3, body[2])  # stock
            sp.rect(14, 18, 15, 6, body[3]); sp.rect(14, 18, 15, 1, body[5])
            sp.line(15, 24, 13, 33, grip[3], 4)
            sp.rect(21, 24, 4, 10, acc[4] if "chetak" in wid else stl[3])  # extended mag
            sp.rect(29, 20, 10, 3, stl[4])
            if var >= 3 or "lotus" in wid:
                sp.rect(19, 15, 5, 3, "#22D3EE")
    elif wclass in ("rifle", "special"):
        if "vijay" in wid:  # TRUE Bullpup (mag behind grip!)
            sp.rect(6, 18, 22, 7, body[3]); sp.rect(6, 18, 22, 1, body[5])
            sp.rect(8, 25, 4, 9, acc[4])  # rear bullpup magazine
            sp.line(21, 25, 19, 33, grip[3], 4)  # forward trigger grip
            sp.rect(14, 14, 12, 4, body[2])  # optic rail
            sp.rect(28, 19, 13, 3, stl[4])
        elif "vajra" in wid:  # heavy ordnance tube
            sp.rect(5, 17, 34, 7, body[3]); sp.rect(5, 17, 34, 2, acc[4])
            sp.rect(37, 16, 5, 9, acc[5])
            sp.rect(14, 24, 4, 8, grip[3]); sp.rect(26, 24, 4, 7, grip[3])
            sp.rect(16, 13, 6, 4, "#38BDF8")
        else:
            sp.rect(3, 21, 11, 5, grip[3]); sp.rect(3, 21, 11, 1, grip[4])
            sp.rect(14, 19, 13, 5, body[3]); sp.rect(14, 19, 13, 1, body[5])
            sp.line(15, 24, 13, 32, grip[2], 3)
            sp.rect(20, 24, 4, 9, acc[3] if "trishul" in wid else stl[3])
            sp.rect(27, 19, 9, 4, body[4] if "trishul" not in wid else wal[3])
            sp.rect(36, 20, 9, 2, stl[5])
            sp.rect(17, 15, 8, 3, stl[4]); sp.rect(19, 16, 4, 1, "#38BDF8")  # ACOG / scope

    sp.add_outline(col=(14, 16, 26, 255))
    return sp


def import_and_render_hero_props():
    """Preserve all 11 user-uploaded JSONs, export enriched Bedrock geo, and render crisp Faithful 32x sprites."""
    hero_dir = MODELS_DIR / "equipment" / "user_props"
    hero_icon_dir = ICONS_DIR / "equipment" / "user_props"
    hero_dir.mkdir(parents=True, exist_ok=True)
    hero_icon_dir.mkdir(parents=True, exist_ok=True)

    tex_to_mat = {
        "slide": "weapon_slide_dark", "frame": "graphite", "grip": "weapon_grip_stipple", "barrel": "chrome",
        "receiver": "weapon_slide_dark", "handguard": "weapon_vent_guard", "magazine": "steel_light", "stock": "graphite",
        "pump": "weapon_grip_stipple", "body": "graphite", "metal": "chrome",
        "wood_ash": "wood_oak", "grip_tape": "weapon_grip_stipple", "brand_stamp": "brass",
        "fob_case": "graphite", "buttons": "screen_atm", "chrome": "chrome", "keyring": "stainless",
        "can_red": "jerrycan_rib_red", "handle": "paint_red", "spout": "hazard_yellow", "details": "steel_dark",
        "fabric": "paint_emerald", "trim": "graphite", "webbing": "steel_dark", "zipper": "chrome", "patch": "linen_white", "cross": "medkit_cross_tile", "hardware": "chrome",
        "leather": "leather_tan", "edge": "wood_sheesham", "stitch": "sandstone", "gold": "brass", "gold_dark": "brass", "gold_bright": "gold_filigree", "silver": "stainless", "window": "glass_clear", "hinge": "chrome", "id_card": "linen_white",
        "card_front": "card_ark_vip", "card_back": "paint_black", "chip": "brass", "chip_trace": "gold_filigree",
        "bills_side": "paint_emerald", "bills_top": "bills_ark_top", "band": "paint_gold"
    }

    hero_entries = []
    for hid, src_name, title in UPLOADED_HERO_PROPS:
        src_file = UPLOAD_DIR / src_name
        if not src_file.exists():
            continue
        raw = json.loads(src_file.read_text(encoding="utf-8"))
        dest_java = hero_dir / f"{hid}.json"
        shutil.copy2(src_file, dest_java)

        pb = s3d.PartBuilder()
        for el in raw.get("elements", []):
            fx, fy, fz = el["from"]
            tx, ty, tz = el["to"]
            faces = el.get("faces", {})
            tex_ref = next(iter(faces.values())).get("texture", "#metal").lstrip("#") if faces else "metal"
            mat = tex_to_mat.get(tex_ref, "steel_dark")
            rot_info = el.get("rotation")
            rot, piv = None, None
            if rot_info:
                ax, ang = rot_info["axis"], rot_info["angle"]
                rot = [ang if ax == "x" else 0, ang if ax == "y" else 0, ang if ax == "z" else 0]
                piv = [rot_info["origin"][0] - 8.0, rot_info["origin"][1], rot_info["origin"][2] - 8.0]
            pb.box(fx - 8.0, fy, fz - 8.0, tx - fx, ty - fy, tz - fz, mat=mat, rot=rot, pivot=piv)

        dest_geo = hero_dir / f"{hid}.geo.json"
        dest_icon = hero_icon_dir / f"{hid}.png"
        cubes = pb.export_bedrock_geo(f"geometry.gtm.{hid}", dest_geo)
        # Render bespoke Faithful 32x/48x crisp pixel-art icon!
        draw_hero_faithful_sprite(hid).save(dest_icon, target_size=128)

        hero_entries.append({
            "id": f"gtm:{hid}", "title": title,
            "java_model_path": f"creative/source/models/equipment/user_props/{hid}.json",
            "model_path": f"creative/source/models/equipment/user_props/{hid}.geo.json",
            "icon_path": f"creative/source/icons/equipment/user_props/{hid}.png",
            "cube_count": cubes
        })
    print(f"SUCCESS: Imported & pixel-crafted {len(hero_entries)} User Hero 3D Props!")
    return hero_entries


def recipe_to_partbuilder(parts, swatch_map, slug: str = "") -> s3d.PartBuilder:
    pb = s3d.PartBuilder()
    for idx_p, (col, x, y, z, w, h, d) in enumerate(parts):
        mat = swatch_map.get(col, "steel_dark")
        f_mats = None
        if "first_aid" in slug and idx_p == 0:
            f_mats = {"north": "medkit_cross_tile", "south": "medkit_cross_tile"}
        elif "speaker" in slug and col == "steel":
            mat = "speaker_grille"
        elif "dj_deck" in slug and idx_p == 0:
            f_mats = {"up": "speaker_grille"}
        elif ("news_display" in slug or "ticket_validator" in slug or "parking_meter" in slug) and col == "ice":
            mat = "screen_pc"
        elif "mandap" in slug or "arch" in slug or "gateway" in slug:
            if col == "gold" or col == "saffron":
                mat = "festival_toran"
        pb.box(x - 8.0, y, z - 8.0, w, h, d, mat=mat, face_mats=f_mats)
    return pb


def rebuild_equipment_92():
    SWATCH_MAP = {
        "steel": "steel_light", "rim": "stainless", "clay": "terracotta", "terra": "terracotta",
        "cream": "linen_white", "milk": "paint_white", "crust": "wood_oak", "bread": "bamboo",
        "toast": "wood_sheesham", "gold": "brass", "gravy": "paint_red", "chilli": "fire_red",
        "leaf": "paint_emerald", "mint": "leaf_green", "pink": "holi_pink", "rice": "fabric_beige",
        "bean": "leather_tan", "saffron": "marigold", "violet": "lotus_dark", "ice": "glass_clear"
    }
    raw_items = city_item_art.objects()
    eq_icons_dir = ICONS_DIR / "equipment"
    eq_icons_dir.mkdir(parents=True, exist_ok=True)
    cat_counts = {}
    entries = []

    for slug, (category, title, parts) in raw_items.items():
        cat_counts[category] = cat_counts.get(category, 0) + 1
        cat_dir = MODELS_DIR / "equipment" / category
        java_cat_dir = cat_dir / "java"
        cat_dir.mkdir(parents=True, exist_ok=True)
        java_cat_dir.mkdir(parents=True, exist_ok=True)

        pb = recipe_to_partbuilder(parts, SWATCH_MAP, slug=slug)
        geo_path = cat_dir / f"{slug}.geo.json"
        java_path = java_cat_dir / f"{slug}.json"
        icon_path = eq_icons_dir / f"{slug}.png"

        cubes = pb.export_bedrock_geo(f"geometry.gtm.{slug}", geo_path)
        pb.export_java_item(java_path)
        pb.render_icon(icon_path, size=128, yaw_deg=-38, pitch_deg=24, grid=64)

        entries.append({
            "id": f"gtm:{slug}", "category": category, "title": title,
            "model_path": f"creative/source/models/equipment/{category}/{slug}.geo.json",
            "java_model_path": f"creative/source/models/equipment/{category}/java/{slug}.json",
            "icon_path": f"creative/source/icons/equipment/{slug}.png",
            "cube_count": cubes, "sha256": hashlib.sha256(geo_path.read_bytes()).hexdigest()
        })

    assert len(entries) == 92
    return entries, cat_counts


def build_30_weapons_and_300_finishes():
    """Rebuild all 30 Fictional Weapons (sculpted variants + Faithful 48x48 pixel icons) + 300 pixel-art finishes."""
    weap_dir = MODELS_DIR / "weapons"
    weap_java_dir = weap_dir / "java"
    weap_icons_dir = ICONS_DIR / "weapons"
    fin_tex_dir = TEX_DIR / "finishes"
    for d in (weap_dir, weap_java_dir, weap_icons_dir, fin_tex_dir):
        d.mkdir(parents=True, exist_ok=True)

    target_weapons = [
        ("kavach_9", "Kavach 9mm Compact", "sidearm"), ("rajput_45", "Rajput .45 Heavy", "sidearm"),
        ("maratha_auto", "Maratha Auto-Pistol", "sidearm"), ("deccan_compact", "Deccan Concealed 9", "sidearm"),
        ("konkan_magnum", "Konkan .357 Revolver", "sidearm"), ("astra_holdout", "Astra Micro Derringer", "sidearm"),
        ("sher_pump", "Sher 12G Tactical Pump", "shotgun"), ("ghadial_12g", "Ghadial Heavy Auto-Shotgun", "shotgun"),
        ("sahyadri_enforcer", "Sahyadri Enforcer Riot 12G", "shotgun"), ("garuda_breacher", "Garuda Compact Breacher", "shotgun"),
        ("cyclone_tactical", "Cyclone Double-Barrel", "shotgun"), ("tulwar_short", "Tulwar Sawed-Off Special", "shotgun"),
        ("chetak_9", "Chetak 9mm Machine Pistol", "smg"), ("viper_sub", "Viper Tactical SMG", "smg"),
        ("shikari_pdw", "Shikari PDW", "smg"), ("storm_9", "Storm Sub-Carbine", "smg"),
        ("lotus_burst", "Lotus Rapid SMG", "smg"), ("varun_rapid", "Varun Commando SMG", "smg"),
        ("indrayani_carbine", "Indrayani Service Carbine", "rifle"), ("trishul_ar", "Trishul 5.56 Rifle", "rifle"),
        ("vijay_service", "Vijay Bullpup Rifle", "rifle"), ("ashoka_tactical", "Ashoka Battle Rifle 7.62", "rifle"),
        ("brahmos_precision", "Brahmos Marksman Rifle", "rifle"), ("arya_recon", "Arya Tactical Patrol Rifle", "rifle"),
        ("ghatkopar_bat", "Ghatkopar Heavy Bat", "melee"), ("talwar_cleaver", "Talwar Ceremonial Blade", "melee"),
        ("lathi_tactical", "Lathi Polycarbonate Baton", "melee"), ("khanda_blade", "Khanda Ceremonial Broadsword", "melee"),
        ("kurukshetra_dmr", "Kurukshetra Precision DMR", "special"), ("vajra_heavy", "Vajra Ordnance Prop", "special")
    ]
    finishes_catalog = [
        ("gold_leaf", "ARK Gold Leaf", "legendary", "#D6AD59", "#6E4E12", "#FFF1A8"),
        ("monsoon_camo", "Monsoon Storm Camo", "rare", "#236653", "#182830", "#4AA885"),
        ("graphite_stealth", "Graphite Urban Stealth", "uncommon", "#2B333D", "#151B20", "#64748B"),
        ("royal_emerald", "Chhatrapati Royal Emerald", "epic", "#1F4E3F", "#0D2B22", "#E8C87E"),
        ("terracotta_dune", "Sandstone Terracotta", "common", "#AD5637", "#73311A", "#D2B997"),
        ("deccan_chrome", "Deccan Mirrored Chrome", "rare", "#C0D5E0", "#6B8291", "#FFFFFF"),
        ("maratha_rust", "Sahyadri Weathered Rust", "uncommon", "#8C4727", "#4D2210", "#C97D52"),
        ("lotus_pearl", "Black Lotus Iridescent", "legendary", "#5A1846", "#1C0818", "#EC4899"),
        ("bazaar_mosaic", "Bazaar Glazed Ceramic", "rare", "#2668A8", "#16385E", "#FBBF24"),
        ("cyber_neon", "Indraprastha Cyber Glow", "epic", "#13293D", "#081421", "#22D3EE")
    ]

    weapon_icons, weapon_titles = [], []
    hero_templates = {
        "sidearm": json.loads((UPLOAD_DIR / "media_1795531381382_e3925f91.json").read_text(encoding="utf-8")),
        "shotgun": json.loads((UPLOAD_DIR / "media_1795531381382_46b54742.json").read_text(encoding="utf-8")),
        "smg": json.loads((UPLOAD_DIR / "media_1795531409892_63d65d67.json").read_text(encoding="utf-8")),
        "rifle": json.loads((UPLOAD_DIR / "media_1795531381382_77a12ec4.json").read_text(encoding="utf-8")),
        "special": json.loads((UPLOAD_DIR / "media_1795531381382_77a12ec4.json").read_text(encoding="utf-8")),
        "bat": json.loads((UPLOAD_DIR / "media_1795531381456_864a9c54.json").read_text(encoding="utf-8")),
    }
    variant_styles = [
        ("brass", "weapon_slide_dark", "leather_tan", "wood_sheesham"),
        ("weapon_slide_chrome", "steel_dark", "weapon_grip_stipple", "wood_teak"),
        ("paint_emerald", "weapon_slide_dark", "carbon", "graphite"),
        ("paint_saffron", "steel_light", "weapon_grip_stipple", "carbon"),
        ("lotus_dark", "weapon_slide_chrome", "fabric_maroon", "graphite"),
        ("neon_cyan", "graphite", "carbon", "steel_dark"),
    ]

    for wi, (wid, wname, wclass) in enumerate(target_weapons):
        pb = s3d.PartBuilder()
        var = wi % 6
        accent_m, body_m, grip_m, stock_m = variant_styles[var]

        if wid == "konkan_magnum":  # Unique 3D Revolver geometry
            pb.cbox(-5.0, 5.2, 0.0, 2.5, 4.2, 1.4, mat="wood_sheesham", rot=[0, 0, -18])
            pb.cbox(-2.0, 8.2, 0.0, 4.5, 2.2, 1.8, mat="chrome")
            pb.cbox(0.5, 8.6, 0.0, 2.6, 2.4, 2.6, mat="brass")  # 6-shot cylinder
            pb.cbox(5.0, 9.2, 0.0, 7.5, 1.4, 1.2, mat="chrome", face_mats={"east": "gun_muzzle_bore"})
        elif wid == "astra_holdout":  # Compact twin over-under derringer
            pb.cbox(-3.2, 6.0, 0.0, 2.4, 3.0, 1.2, mat="wood_oak", rot=[0, 0, -15])
            pb.cbox(0.5, 8.2, 0.0, 5.2, 2.0, 1.2, mat="chrome")
            pb.cbox(0.5, 7.2, 0.0, 5.2, 1.0, 1.2, mat="brass")
        elif wid == "cyclone_tactical":  # Double-barrel side-by-side shotgun
            pb.cbox(-6.0, 7.2, 0.0, 6.5, 2.2, 1.6, mat="wood_sheesham")
            pb.cbox(0.0, 8.0, 0.0, 4.5, 2.2, 1.8, mat="brass")
            pb.cbox(5.5, 8.2, -0.55, 8.5, 1.0, 1.0, mat="chrome", face_mats={"east": "gun_muzzle_bore"})
            pb.cbox(5.5, 8.2, 0.55, 8.5, 1.0, 1.0, mat="chrome", face_mats={"east": "gun_muzzle_bore"})
        elif wid == "vijay_service":  # True Bullpup Rifle (rear magazine)
            pb.cbox(-3.5, 5.0, 0.0, 2.4, 4.2, 1.2, mat="paint_emerald", rot=[0, 0, -8])  # rear bullpup mag
            pb.cbox(-1.0, 8.0, 0.0, 11.5, 2.8, 1.8, mat="graphite")
            pb.cbox(2.5, 5.5, 0.0, 2.0, 3.0, 1.2, mat="weapon_grip_stipple")  # forward grip
            pb.cbox(1.5, 10.8, 0.0, 5.5, 1.4, 1.2, mat="steel_dark")  # carry rail optic
            pb.cbox(6.5, 8.8, 0.0, 5.0, 1.0, 1.0, mat="chrome", face_mats={"east": "gun_muzzle_bore"})
        elif wid == "vajra_heavy":  # Heavy ordnance tube launcher
            pb.cbox(0.0, 8.0, 0.0, 18.0, 3.2, 3.2, mat="paint_emerald")
            pb.cbox(-7.5, 7.8, 0.0, 2.0, 3.6, 3.6, mat="hazard_yellow")
            pb.cbox(7.5, 7.8, 0.0, 2.0, 3.6, 3.6, mat="brass", face_mats={"east": "gun_muzzle_bore"})
            pb.cbox(2.0, 5.2, 0.0, 2.0, 3.0, 1.2, mat="weapon_grip_stipple")
            pb.cbox(-2.0, 11.2, 0.0, 3.5, 2.0, 1.4, mat="neon_cyan")
        elif wclass in hero_templates and "bat" not in wid and wclass != "melee":
            tmpl = hero_templates[wclass]
            tmap = {
                "slide": accent_m if var % 2 == 0 else body_m,
                "frame": body_m, "receiver": body_m, "body": body_m,
                "grip": grip_m, "barrel": "chrome" if var % 3 == 0 else "steel_light",
                "handguard": accent_m if var >= 3 else "weapon_vent_guard",
                "magazine": "brass" if var == 0 else "steel_light",
                "stock": stock_m, "pump": stock_m, "metal": "chrome"
            }
            for el in tmpl.get("elements", []):
                fx, fy, fz = el["from"]
                tx, ty, tz = el["to"]
                faces = el.get("faces", {})
                tex_ref = next(iter(faces.values())).get("texture", "#body").lstrip("#") if faces else "body"
                mat = tmap.get(tex_ref, body_m)
                rot_info = el.get("rotation")
                rot, piv = None, None
                if rot_info:
                    ax, ang = rot_info["axis"], rot_info["angle"]
                    rot = [ang if ax == "x" else 0, ang if ax == "y" else 0, ang if ax == "z" else 0]
                    piv = [rot_info["origin"][0] - 8.0, rot_info["origin"][1], rot_info["origin"][2] - 8.0]
                pb.box(fx - 8.0, fy, fz - 8.0, tx - fx, ty - fy, tz - fz, mat=mat, rot=rot, pivot=piv)

            xs_e = [e["to"][0] - 8.0 for e in tmpl.get("elements", [])]
            ys_e = [e["to"][1] for e in tmpl.get("elements", [])]
            max_x = max(xs_e) if xs_e else 6.0
            mid_y = (sum(ys_e) / len(ys_e)) if ys_e else 9.0
            if wclass in ("rifle", "special"):
                if var in (0, 2, 4):
                    pb.cbox(0.0, mid_y + 0.6, 0.0, 4.2, 1.3, 1.0, mat="steel_dark")
                    pb.cbox(0.0, mid_y + 0.7, 0.0, 4.4, 1.0, 0.8, mat="glass_clear")
                if var in (1, 3, 5) or wclass == "special":
                    pb.box(max_x - 0.4, mid_y - 0.7, -0.5, 3.2, 1.0, 1.0, mat=accent_m)
            elif wclass == "sidearm" and var in (2, 5):
                pb.box(max_x - 0.3, mid_y - 0.5, -0.4, 3.0, 0.9, 0.8, mat="carbon")
            elif wclass == "smg" and var >= 3:
                pb.cbox(0.0, mid_y + 0.5, 0.0, 2.2, 1.1, 0.9, mat="neon_cyan")
        elif "bat" in wid:
            tmpl = hero_templates["bat"]
            for el in tmpl.get("elements", []):
                fx, fy, fz = el["from"]
                tx, ty, tz = el["to"]
                faces = el.get("faces", {})
                tex_ref = next(iter(faces.values())).get("texture", "#wood_ash").lstrip("#") if faces else "wood_ash"
                mat = {"wood_ash": "wood_oak", "grip_tape": "weapon_grip_stipple", "brand_stamp": accent_m}.get(tex_ref, "wood_oak")
                pb.box(fx - 8.0, fy, fz - 8.0, tx - fx, ty - fy, tz - fz, mat=mat)
        elif "lathi" in wid:
            pb.cbox(-7.5, 7.5, 0, 5.5, 1.6, 1.6, mat="weapon_grip_stipple")
            pb.cbox(-4.2, 7.5, 0, 1.2, 2.2, 2.2, mat="brass")
            pb.cbox(3.5, 7.5, 0, 14.5, 1.8, 1.8, mat="police_navy")
            pb.cbox(11.0, 7.5, 0, 1.5, 1.9, 1.9, mat="chrome")
        else:  # Talwar / Khanda
            pb.cbox(-8.5, 7.4, 0, 5.0, 1.4, 1.4, mat="leather_tan")
            pb.cbox(-6.0, 6.0, 0, 1.4, 4.2, 2.8, mat="brass")
            pb.cbox(1.5, 7.2, 0, 11.0, 2.0, 0.7, mat="chrome")
            pb.cbox(8.5, 7.8, 0, 5.5, 1.8, 0.65, mat=accent_m, rot=[0, 0, 16])

        geo_path = weap_dir / f"{wid}.geo.json"
        java_path = weap_java_dir / f"{wid}.json"
        icon_path = weap_icons_dir / f"{wid}.png"
        pb.export_bedrock_geo(f"geometry.gtm.{wid}", geo_path)
        pb.export_java_item(java_path)
        # Render Faithful 48x48 pixel-art weapon sprite -> crisp NEAREST 128x128!
        draw_weapon_sprite(wid, wclass, var).save(icon_path, target_size=128)
        weapon_icons.append(Image.open(icon_path))
        weapon_titles.append(wname)

        # 10 Faithful Pixel-Art Weapon Finishes (64x64 RGBA, zero sine blur!)
        for fi, (f_id, f_name, f_rarity, c1, c2, c3) in enumerate(finishes_catalog):
            tile_a = f32.make_ramp(c1, 1.05)
            tile_b = f32.make_ramp(c2, 1.05)
            tile_c = f32.make_ramp(c3, 1.05)
            arr = np.zeros((64, 64, 4), dtype=np.uint8)
            arr[:, :, 3] = 255
            for y in range(64):
                for x in range(64):
                    px, py = x // 2, y // 2
                    if fi == 0:  # ARK Gold Filigree
                        pat = ((px % 8 in (0, 7)) or (py % 8 in (0, 7)) or (abs((px % 8) - 3.5) + abs((py % 8) - 3.5) <= 2.0))
                        arr[y, x, :3] = tile_c[5] if pat else tile_a[3 if (px + py) % 2 == 0 else 2]
                    elif fi == 1:  # Monsoon Pixel Camo
                        c_id = ((px // 4) * 13 + (py // 3) * 29 + wi) % 7
                        arr[y, x, :3] = tile_b[1] if c_id in (0, 1) else (tile_c[4] if c_id in (2, 3) else tile_a[3])
                    elif fi == 2:  # Graphite Carbon Weave
                        arr[y, x, :3] = tile_a[4 if ((x // 2 + y // 2) % 2 == 0) else 1]
                        if (x + y) % 16 == 0:
                            arr[y, x, :3] = tile_c[5]
                    elif fi == 3 or fi == 8:  # Royal Emerald / Bazaar Glazed Mosaic
                        d = (px % 8) + (py % 8)
                        arr[y, x, :3] = tile_c[4] if d in (0, 7, 14) else (tile_b[2] if d < 6 else tile_a[3])
                    elif fi == 5:  # Deccan Mirrored Chrome (Stepped diag specular!)
                        d = (px + py + wi * 2) % 16
                        arr[y, x, :3] = tile_c[5] if d in (0, 1) else (tile_a[4] if d in (2, 3, 15) else tile_b[2 if d < 9 else 3])
                    elif fi == 7:  # Black Lotus Stepped Diamond
                        d = (abs((px % 16) - 8) + abs((py % 16) - 8))
                        arr[y, x, :3] = tile_c[5] if d <= 3 else (tile_c[3] if d <= 6 else tile_b[2])
                    elif fi == 9:  # Cyber Neon Traces
                        tr = (px % 8 == 2 or py % 10 == 4) and ((px + py) % 12 < 8)
                        node = (px % 8 == 2 and py % 10 == 4)
                        arr[y, x, :3] = tile_c[5] if node else (tile_c[3] if tr else tile_b[1])
                    else:  # Stepped diagonal tactical stripe
                        s = ((px + py + wi * 3) // 5) % 3
                        arr[y, x, :3] = tile_a[3] if s == 0 else (tile_b[2] if s == 1 else tile_c[4])
            fin_png = fin_tex_dir / f"{wid}_{f_id}.png"
            Image.fromarray(arr, "RGBA").save(fin_png, optimize=True)

    mig_file = MANIFESTS / "finishes_migration.json"
    mig_data = json.loads(mig_file.read_text(encoding="utf-8"))
    for m in mig_data["mappings"]:
        wid_slug = m["target_weapon_id"].replace("gtm:", "")
        m["weapon_model_path"] = f"creative/source/models/weapons/{wid_slug}.geo.json"
        m["weapon_java_model_path"] = f"creative/source/models/weapons/java/{wid_slug}.json"
        m["weapon_icon_path"] = f"creative/source/icons/weapons/{wid_slug}.png"
        m["finish_texture_path"] = f"creative/source/textures/finishes/{wid_slug}_{m['target_finish_id']}.png"
    mig_file.write_text(json.dumps(mig_data, indent=2) + "\n", encoding="utf-8")

    v4.create_grid(weapon_icons, weapon_titles, cols=6, cell_w=120, cell_h=136).save(PREVIEWS / "weapons_contact_sheet.png", optimize=True)
    print("SUCCESS: Rebuilt 30 Distinct Sculpted Weapons + 30 Faithful Weapon Sprites + 300 Pixel-Art Finishes!")


def rebuild_festivals_100():
    SWATCH_MAP = {
        "steel": "steel_light", "rim": "stainless", "clay": "terracotta", "terra": "terracotta",
        "cream": "linen_white", "milk": "paint_white", "crust": "wood_oak", "bread": "bamboo",
        "toast": "wood_sheesham", "gold": "festival_toran", "gravy": "paint_red", "chilli": "fire_red",
        "leaf": "leaf_green", "mint": "paint_emerald", "pink": "festival_rangoli", "rice": "fabric_beige",
        "bean": "leather_tan", "saffron": "glowstone_lamp", "violet": "neon_magenta", "ice": "sea_prism"
    }
    raw_festivals = city_festival_art.festival()
    fest_dir = MODELS_DIR / "festivals"
    fest_icons_dir = ICONS_DIR / "festivals"
    fest_icons_dir.mkdir(parents=True, exist_ok=True)

    fest_manifest = json.loads((MANIFESTS / "festivals_manifest.json").read_text(encoding="utf-8"))
    by_id = {f["id"]: f for f in fest_manifest["festivals"]}
    sample_imgs, sample_titles = [], []

    for idx, (key, (category, label, parts)) in enumerate(raw_festivals.items()):
        theme = key.split("_")[0]
        tdir = fest_dir / theme
        jdir = tdir / "java"
        tdir.mkdir(parents=True, exist_ok=True)
        jdir.mkdir(parents=True, exist_ok=True)

        pb = recipe_to_partbuilder(parts, SWATCH_MAP, slug=key)
        geo_path = tdir / f"{key}.geo.json"
        java_path = jdir / f"{key}.json"
        icon_path = fest_icons_dir / f"{key}.png"

        cubes = pb.export_bedrock_geo(f"geometry.gtm.{key}", geo_path)
        pb.export_java_item(java_path)
        pb.render_icon(icon_path, size=128, yaw_deg=-32, pitch_deg=18, grid=64)

        entry = by_id.get(f"gtm:{key}")
        if entry:
            entry["java_model_path"] = f"creative/source/models/festivals/{theme}/java/{key}.json"
            entry["icon_path"] = f"creative/source/icons/festivals/{key}.png"
            entry["cube_count"] = cubes
            entry["sha256"] = hashlib.sha256(geo_path.read_bytes()).hexdigest()

        if idx % 3 == 0 and len(sample_imgs) < 32:
            sample_imgs.append(Image.open(icon_path))
            sample_titles.append(label)

    (MANIFESTS / "festivals_manifest.json").write_text(json.dumps(fest_manifest, indent=2) + "\n", encoding="utf-8")
    v4.create_grid(sample_imgs, sample_titles, cols=8, cell_w=112, cell_h=128).save(PREVIEWS / "festivals_sample_contact_sheet.png", optimize=True)
    print("SUCCESS: Upgraded all 100 Festival installations (Faithful 32x textures + crisp pixel icons)!")


def build_all():
    s3d.build_shared_atlas()
    hero_entries = import_and_render_hero_props()
    eq_entries, eq_counts = rebuild_equipment_92()

    eq_imgs = [Image.open(ROOT / h["icon_path"]) for h in hero_entries]
    eq_titles = [h["title"] for h in hero_entries]
    for e in eq_entries[::3][:25]:
        eq_imgs.append(Image.open(ROOT / e["icon_path"]))
        eq_titles.append(e["title"])
    v4.create_grid(eq_imgs, eq_titles, cols=6, cell_w=116, cell_h=132).save(PREVIEWS / "equipment_sample_contact_sheet.png", optimize=True)

    (MANIFESTS / "equipment_manifest.json").write_text(json.dumps({
        "schema_version": "3.0.0",
        "total_equipment": len(eq_entries),
        "hero_props_count": len(hero_entries),
        "categories": eq_counts,
        "hero_props": hero_entries,
        "equipment": eq_entries
    }, indent=2) + "\n", encoding="utf-8")

    build_30_weapons_and_300_finishes()
    rebuild_festivals_100()


if __name__ == "__main__":
    build_all()
