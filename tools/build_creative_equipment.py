#!/usr/bin/env python3
"""Build equipment 3D models, food models, 48x48 food icons, and finishes migration mapping."""
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageColor, ImageDraw, ImageEnhance

import food_art

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
MODELS_DIR = CREATIVE / "source" / "models"
EQUIPMENT_MODELS = MODELS_DIR / "equipment"
FOOD_MODELS = MODELS_DIR / "food"
FOOD_ICONS = CREATIVE / "source" / "icons" / "food"
MANIFESTS_DIR = CREATIVE / "manifests"

def generate_box(name, from_pt, to_pt, uv_origin=(0, 0), uv_size=(16, 16)):
    x, y, z = from_pt
    X, Y, Z = to_pt
    return {
        "origin": [round(8 - X, 3), round(y - 8, 3), round(z - 8, 3)],
        "size": [round(X - x, 3), round(Y - y, 3), round(Z - z, 3)],
        "uv": {
            "north": {"uv": list(uv_origin), "uv_size": list(uv_size)},
            "south": {"uv": list(uv_origin), "uv_size": list(uv_size)},
            "east": {"uv": list(uv_origin), "uv_size": list(uv_size)},
            "west": {"uv": list(uv_origin), "uv_size": list(uv_size)},
            "up": {"uv": list(uv_origin), "uv_size": list(uv_size)},
            "down": {"uv": list(uv_origin), "uv_size": list(uv_size)}
        }
    }

def make_geo(ident, cubes, tex_w=32, tex_h=32):
    return {
        "format_version": "1.12.0",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": f"geometry.gtm.{ident.replace('gtm:', '')}",
                    "texture_width": tex_w,
                    "texture_height": tex_h,
                    "visible_bounds_width": 2.0,
                    "visible_bounds_height": 2.0,
                    "visible_bounds_offset": [0.0, 0.5, 0.0]
                },
                "bones": [
                    {
                        "name": "root",
                        "pivot": [0.0, 0.0, 0.0],
                        "cubes": cubes
                    }
                ]
            }
        ]
    }

def build():
    EQUIPMENT_MODELS.mkdir(parents=True, exist_ok=True)
    FOOD_MODELS.mkdir(parents=True, exist_ok=True)
    FOOD_ICONS.mkdir(parents=True, exist_ok=True)
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

    cat_file = ROOT / "docs" / "creative" / "CREATIVE_CATALOGUE.json"
    catalogue = json.loads(cat_file.read_text(encoding="utf-8"))

    # 1. Build Equipment models (55 protection, 20 civic, 2 property, 5 effect, 10 entertainment = 92 items)
    equipment_cats = {"protection", "civic", "property", "effect", "entertainment"}
    equipment_items = [m for m in catalogue["models"] if m.get("category") in equipment_cats]
    assert len(equipment_items) == 92, f"Expected 92 equipment items, got {len(equipment_items)}"

    eq_manifest_items = []
    for item in equipment_items:
        ident = item["id"]
        slug = ident.replace("gtm:", "")
        category = item["category"]
        cat_dir = EQUIPMENT_MODELS / category
        cat_dir.mkdir(parents=True, exist_ok=True)

        # Procedural distinct geometry based on item type and category
        cubes = []
        if category == "protection":
            # Shields, vests, bracers, helmets, tags, visors
            if "shield" in slug:
                cubes.append(generate_box("plate", [3, 2, 7], [13, 14, 9]))
                cubes.append(generate_box("boss", [6, 6, 9], [10, 10, 10]))
                cubes.append(generate_box("handle", [7, 6, 5], [9, 10, 7]))
            elif "vest" in slug:
                cubes.append(generate_box("torso", [4, 2, 6], [12, 14, 10]))
                cubes.append(generate_box("collar", [5, 14, 6], [11, 15, 10]))
                cubes.append(generate_box("pocket_l", [4.5, 5, 5.5], [7.5, 9, 6]))
                cubes.append(generate_box("pocket_r", [8.5, 5, 5.5], [11.5, 9, 6]))
            elif "helmet" in slug:
                cubes.append(generate_box("cap", [4, 6, 4], [12, 14, 12]))
                cubes.append(generate_box("visor", [4.5, 7, 3.5], [11.5, 10, 4]))
                cubes.append(generate_box("crest", [7.5, 14, 5], [8.5, 16, 11]))
            elif "bracer" in slug:
                cubes.append(generate_box("cuff", [5, 4, 5], [11, 12, 11]))
                cubes.append(generate_box("plate", [4.5, 6, 4.5], [11.5, 10, 5]))
            elif "visor" in slug:
                cubes.append(generate_box("band", [4, 9, 4], [12, 11, 12]))
                cubes.append(generate_box("lens", [4.5, 8.5, 3.5], [11.5, 10.5, 4.5]))
            else: # light tag
                cubes.append(generate_box("emitter", [6, 4, 7], [10, 12, 9]))
                cubes.append(generate_box("crystal", [6.5, 6, 6.5], [9.5, 10, 9.5]))
                cubes.append(generate_box("clip", [7, 2, 7.5], [9, 4, 8.5]))

        elif category == "civic":
            if "flag" in slug or "marker" in slug or "sign" in slug:
                cubes.append(generate_box("pole", [7.5, 0, 7.5], [8.5, 16, 8.5]))
                cubes.append(generate_box("board", [2, 10, 7.8], [14, 15, 8.2]))
            elif "post" in slug or "meter" in slug:
                cubes.append(generate_box("base", [6, 0, 6], [10, 2, 10]))
                cubes.append(generate_box("column", [7, 2, 7], [9, 14, 9]))
                cubes.append(generate_box("head", [5.5, 10, 5.5], [10.5, 14, 10.5]))
            elif "cabinet" in slug or "kiosk" in slug or "box" in slug:
                cubes.append(generate_box("body", [3, 0, 3], [13, 16, 13]))
                cubes.append(generate_box("screen", [4, 6, 2.5], [12, 13, 3]))
            elif "barrier" in slug or "bollard" in slug or "cone" in slug:
                cubes.append(generate_box("base", [4, 0, 4], [12, 2, 12]))
                cubes.append(generate_box("body", [5, 2, 5], [11, 14, 11]))
            else:
                cubes.append(generate_box("pedestal", [4, 0, 4], [12, 4, 12]))
                cubes.append(generate_box("unit", [5, 4, 5], [11, 15, 11]))

        elif category == "property":
            if "key" in slug:
                cubes.append(generate_box("bow", [6, 10, 7.5], [10, 14, 8.5]))
                cubes.append(generate_box("blade", [7.5, 2, 7.5], [8.5, 10, 8.5]))
                cubes.append(generate_box("bitting1", [8.5, 3, 7.5], [10, 4.5, 8.5]))
                cubes.append(generate_box("bitting2", [8.5, 6, 7.5], [9.5, 7.5, 8.5]))
            else: # deed
                cubes.append(generate_box("scroll", [4, 1, 4], [12, 3, 12]))
                cubes.append(generate_box("ribbon", [7.5, 0.5, 3.5], [8.5, 3.5, 12.5]))
                cubes.append(generate_box("seal", [7, 3, 7], [9, 3.5, 9]))

        elif category == "effect":
            cubes.append(generate_box("core", [6, 6, 6], [10, 10, 10]))
            cubes.append(generate_box("ring1", [5, 7.5, 5], [11, 8.5, 11]))
            cubes.append(generate_box("halo", [7.5, 5, 5], [8.5, 11, 11]))

        elif category == "entertainment":
            if "projector" in slug or "deck" in slug or "receiver" in slug:
                cubes.append(generate_box("chassis", [2, 2, 4], [14, 8, 12]))
                cubes.append(generate_box("lens_dial", [6, 4, 2], [10, 8, 4]))
                cubes.append(generate_box("spool", [4, 8, 6], [12, 14, 10]))
            elif "dhol" in slug or "tabla" in slug:
                cubes.append(generate_box("drum_body", [3, 2, 3], [13, 14, 13]))
                cubes.append(generate_box("membrane_top", [4, 14, 4], [12, 15, 12]))
                cubes.append(generate_box("strap", [2.5, 6, 2.5], [13.5, 10, 13.5]))
            elif "mic" in slug or "spotlight" in slug:
                cubes.append(generate_box("stand", [7.5, 0, 7.5], [8.5, 11, 8.5]))
                cubes.append(generate_box("head", [5.5, 11, 5.5], [10.5, 16, 10.5]))
            else:
                cubes.append(generate_box("unit", [3, 0, 3], [13, 14, 13]))
                cubes.append(generate_box("grille", [4, 2, 2.5], [12, 12, 3]))

        geo_data = make_geo(ident, cubes)
        geo_file = cat_dir / f"{slug}.geo.json"
        geo_file.write_text(json.dumps(geo_data, indent=2) + "\n", encoding="utf-8")

        eq_manifest_items.append({
            "id": ident,
            "category": category,
            "title": item["title"],
            "base_item": item["base_item"],
            "model_path": f"creative/source/models/equipment/{category}/{slug}.geo.json",
            "cube_count": len(cubes),
            "sha256": hashlib.sha256(geo_file.read_bytes()).hexdigest()
        })

    eq_manifest = MANIFESTS_DIR / "equipment_manifest.json"
    eq_manifest.write_text(json.dumps({
        "schema_version": "1.0.0",
        "total_equipment": len(eq_manifest_items),
        "categories": {
            "protection": 55,
            "civic": 20,
            "property": 2,
            "effect": 5,
            "entertainment": 10
        },
        "equipment": eq_manifest_items
    }, indent=2) + "\n", encoding="utf-8")
    print(f"SUCCESS: Generated 92 equipment Blockbench 3D models and {eq_manifest.name}")

    # 2. Build Finishes Migration Mapping (300 finishes)
    # 4 legacy families x 75 finishes -> 30 fictional weapons x 10 finishes
    legacy_families = ["pistol", "shotgun", "smg", "rifle"]
    target_weapons = [
        # 6 Pistols / Sidearms
        ("kavach_9", "Kavach 9mm Compact", "sidearm"),
        ("rajput_45", "Rajput .45 Heavy", "sidearm"),
        ("maratha_auto", "Maratha Auto-Pistol", "sidearm"),
        ("deccan_compact", "Deccan Concealed 9", "sidearm"),
        ("konkan_magnum", "Konkan .357 Revolver", "sidearm"),
        ("astra_holdout", "Astra Micro Derringer", "sidearm"),
        # 6 Shotguns
        ("sher_pump", "Sher 12G Tactical Pump", "shotgun"),
        ("ghadial_12g", "Ghadial Heavy Auto-Shotgun", "shotgun"),
        ("sahyadri_enforcer", "Sahyadri Enforcer Riot 12G", "shotgun"),
        ("garuda_breacher", "Garuda Compact Breacher", "shotgun"),
        ("cyclone_tactical", "Cyclone Double-Barrel", "shotgun"),
        ("tulwar_short", "Tulwar Sawed-Off Special", "shotgun"),
        # 6 Submachine Guns
        ("chetak_9", "Chetak 9mm Machine Pistol", "smg"),
        ("viper_sub", "Viper Tactical SMG", "smg"),
        ("shikari_pdw", "Shikari Personal Defense Weapon", "smg"),
        ("storm_9", "Storm Sub-Carbine", "smg"),
        ("lotus_burst", "Lotus Rapid SMG", "smg"),
        ("varun_rapid", "Varun Commando SMG", "smg"),
        # 6 Assault Rifles / Carbines
        ("indrayani_carbine", "Indrayani Service Carbine", "rifle"),
        ("trishul_ar", "Trishul 5.56 Assault Rifle", "rifle"),
        ("vijay_service", "Vijay Bullpup Rifle", "rifle"),
        ("ashoka_tactical", "Ashoka Battle Rifle 7.62", "rifle"),
        ("brahmos_precision", "Brahmos Marksman Rifle", "rifle"),
        ("arya_recon", "Arya Tactical Patrol Rifle", "rifle"),
        # 6 Specialist & Melee Props
        ("ghatkopar_bat", "Ghatkopar Heavy Bat", "melee"),
        ("talwar_cleaver", "Talwar Ceremonial Cleaver", "melee"),
        ("lathi_tactical", "Lathi Polycarbonate Baton", "melee"),
        ("khanda_blade", "Khanda Broadsword", "melee"),
        ("kurukshetra_dmr", "Kurukshetra DMR Precision", "special"),
        ("vajra_heavy", "Vajra Ordnance Launcher", "special")
    ]
    assert len(target_weapons) == 30, f"Expected 30 fictional weapons, got {len(target_weapons)}"

    finishes_catalog = [
        ("gold_leaf", "ARK Gold Leaf", "legendary", "#D6AD59"),
        ("monsoon_camo", "Monsoon Storm Camo", "rare", "#236653"),
        ("graphite_stealth", "Graphite Urban Stealth", "uncommon", "#151B20"),
        ("royal_emerald", "Chhatrapati Royal Emerald", "epic", "#1F4E3F"),
        ("terracotta_dune", "Sandstone Terracotta", "common", "#AD5637"),
        ("deccan_chrome", "Deccan Mirrored Chrome", "rare", "#C0D5E0"),
        ("maratha_rust", "Sahyadri Weathered Rust", "uncommon", "#8C4727"),
        ("lotus_pearl", "Black Lotus Iridescent", "legendary", "#452D40"),
        ("bazaar_mosaic", "Bazaar Glazed Ceramic", "rare", "#FFBD3E"),
        ("cyber_neon", "Indraprastha Cyber Glow", "epic", "#87E0D7")
    ]
    assert len(finishes_catalog) == 10, f"Expected 10 finishes per weapon, got {len(finishes_catalog)}"

    # Generate deterministic 1-to-1 migration mapping
    migration_table = []
    legacy_index = 0
    for fam in legacy_families:
        for idx in range(75):
            leg_id = f"gtm:{fam}_{idx:02d}"

            target_w_idx = legacy_index // 10
            target_f_idx = legacy_index % 10

            w_id, w_name, w_class = target_weapons[target_w_idx]
            f_id, f_name, f_rarity, f_palette = finishes_catalog[target_f_idx]

            new_id = f"gtm:{w_id}_{f_id}"

            migration_table.append({
                "legacy_id": leg_id,
                "legacy_family": fam,
                "legacy_variant_index": idx,
                "target_weapon_id": f"gtm:{w_id}",
                "target_weapon_name": w_name,
                "target_weapon_class": w_class,
                "target_finish_id": f_id,
                "target_finish_name": f_name,
                "target_full_id": new_id,
                "rarity": f_rarity,
                "palette_primary": f_palette
            })
            legacy_index += 1

    assert len(migration_table) == 300, f"Expected 300 migrated finishes, got {len(migration_table)}"

    migration_file = MANIFESTS_DIR / "finishes_migration.json"
    migration_file.write_text(json.dumps({
        "schema_version": "1.0.0",
        "description": "Entitlement-preserving 1-to-1 mapping from 4 legacy families (75 each = 300) to 30 fictional weapons x 10 finishes (300 total).",
        "total_mappings": len(migration_table),
        "target_weapons_count": len(target_weapons),
        "finishes_per_weapon": len(finishes_catalog),
        "mappings": migration_table
    }, indent=2) + "\n", encoding="utf-8")
    print(f"SUCCESS: Generated 300-finish entitlement-preserving migration manifest at {migration_file.name}")

    # 3. Build 30 Food items: 3D Blockbench models + 48x48 PNG icons
    food_recipes = food_art.recipes()
    food_manifest_items = []

    # Map swatches to RGB hex for icons and textures
    swatches = food_art.PALETTE

    for meal in food_recipes:
        parts = food_recipes[meal]

        # Convert parts to Blockbench cubes
        cubes = []
        for swatch, x, y, z, w, h, d in parts:
            cubes.append(generate_box(f"part_{swatch}", [x, y, z], [x + w, y + h, z + d]))

        geo_data = make_geo(f"food_{meal}", cubes, 32, 32)
        geo_file = FOOD_MODELS / f"{meal}.geo.json"
        geo_file.write_text(json.dumps(geo_data, indent=2) + "\n", encoding="utf-8")

        # Render 48x48 orthographic icon
        icon_img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon_img)

        # Draw subtle plate / shadow base
        draw.ellipse([4, 28, 44, 44], fill=(20, 24, 28, 90))

        # Render isometric projection of voxels
        # Project (x, y, z) into 2D: px = 24 + (x - z) * 1.5, py = 26 - y * 1.8 + (x + z) * 0.75
        sorted_parts = sorted(parts, key=lambda p: (p[1] + p[3], p[2]))
        for swatch, x, y, z, w, h, d in sorted_parts:
            color_hex = swatches.get(swatch, "#c0c0c0")
            rgb = ImageColor.getrgb(color_hex)

            # Draw bounding footprint/box on 2D projection
            p1 = (24 + (x - z) * 1.6, 26 - y * 1.6 + (x + z) * 0.8)
            p2 = (24 + (x + w - z) * 1.6, 26 - y * 1.6 + (x + w + z) * 0.8)
            p3 = (24 + (x + w - (z + d)) * 1.6, 26 - y * 1.6 + (x + w + z + d) * 0.8)
            p4 = (24 + (x - (z + d)) * 1.6, 26 - y * 1.6 + (x + z + d) * 0.8)

            # Top face
            draw.polygon([p1, p2, p3, p4], fill=(*rgb, 255), outline=(*ImageColor.getrgb("#151b20"), 180))

            # Vertical front faces
            h_offset = h * 1.6
            pf1 = (p1[0], p1[1] - h_offset)
            pf2 = (p2[0], p2[1] - h_offset)
            pf3 = (p3[0], p3[1] - h_offset)
            pf4 = (p4[0], p4[1] - h_offset)

            # Front-right face
            draw.polygon([p2, p3, pf3, pf2], fill=tuple(max(0, c - 30) for c in rgb) + (255,))
            # Front-left face
            draw.polygon([p1, p2, pf2, pf1], fill=tuple(max(0, c - 15) for c in rgb) + (255,))
            # Top raised
            draw.polygon([pf1, pf2, pf3, pf4], fill=(*rgb, 255), outline=(*ImageColor.getrgb("#151b20"), 180))

        icon_file = FOOD_ICONS / f"{meal}.png"
        icon_img.save(icon_file, optimize=True)

        food_manifest_items.append({
            "id": f"gtm:food_{meal}",
            "meal_slug": meal,
            "title": meal.replace("_", " ").title(),
            "model_path": f"creative/source/models/food/{meal}.geo.json",
            "icon_path": f"creative/source/icons/food/{meal}.png",
            "icon_dimensions": [48, 48],
            "cube_count": len(cubes),
            "sha256_model": hashlib.sha256(geo_file.read_bytes()).hexdigest(),
            "sha256_icon": hashlib.sha256(icon_file.read_bytes()).hexdigest()
        })

    assert len(food_manifest_items) == 30, f"Expected 30 food items, got {len(food_manifest_items)}"

    food_manifest = MANIFESTS_DIR / "food_manifest.json"
    food_manifest.write_text(json.dumps({
        "schema_version": "1.0.0",
        "total_food_items": len(food_manifest_items),
        "items": food_manifest_items
    }, indent=2) + "\n", encoding="utf-8")
    print(f"SUCCESS: Generated 30 food Blockbench 3D models and 48x48 icons at {food_manifest.name}")

if __name__ == "__main__":
    build()
