#!/usr/bin/env python3
"""GTM 128 equipment, street-kitchen and cosmetic art build.

Extends the versioned creative-r4 recipes. This module does not register runtime
items, alter player entitlements, or depend on the original artist's workstation.
All variant IDs and their legacy mappings come from the existing manifests.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import city_item_art
import food_art
import studio_3d_engine as s3d
from regenerate_equipment_finishes_festivals import recipe_to_partbuilder

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "creative" / "manifests"
DEFAULT_OUTPUT = ROOT / "creative" / "generated_128"

SWATCH_MAP = {
    "steel": "steel_light", "rim": "stainless", "clay": "terracotta", "terra": "terracotta",
    "cream": "linen_white", "milk": "paint_white", "crust": "wood_oak", "bread": "bamboo",
    "toast": "wood_sheesham", "gold": "brass", "gravy": "paint_red", "chilli": "fire_red",
    "leaf": "paint_emerald", "mint": "leaf_green", "pink": "holi_pink", "rice": "fabric_beige",
    "bean": "leather_tan", "saffron": "marigold", "violet": "lotus_dark", "ice": "glass_clear",
}
FOOD_KINDS = {
    "steel": "metal", "rim": "chrome", "clay": "food_ceramic", "terra": "food_ceramic",
    "cream": "food_rice", "milk": "food_rice", "crust": "food_bread", "bread": "food_bread",
    "toast": "food_bread", "gold": "food_grain", "gravy": "food_sauce", "chilli": "food_sauce",
    "leaf": "food_leaf", "mint": "food_leaf", "pink": "food_sauce", "rice": "food_rice",
    "bean": "food_grain", "saffron": "food_grain", "violet": "food_sauce", "ice": "glass",
}
FINISH_COLORS = {
    "gold_leaf": ("#D6AD59", "#6E4E12", "#FFF1A8"),
    "monsoon_camo": ("#236653", "#182830", "#4AA885"),
    "graphite_stealth": ("#2B333D", "#151B20", "#64748B"),
    "royal_emerald": ("#1F4E3F", "#0D2B22", "#E8C87E"),
    "terracotta_dune": ("#AD5637", "#73311A", "#D2B997"),
    "deccan_chrome": ("#C0D5E0", "#6B8291", "#FFFFFF"),
    "maratha_rust": ("#8C4727", "#4D2210", "#C97D52"),
    "lotus_pearl": ("#5A1846", "#1C0818", "#EC4899"),
    "bazaar_mosaic": ("#2668A8", "#16385E", "#FBBF24"),
    "cyber_neon": ("#13293D", "#081421", "#22D3EE"),
}
PALETTE = {"graphite": "#151B20", "gold": "#D6AD59", "emerald": "#236653", "sandstone": "#D2B997", "terracotta": "#AD5637"}
HERO_MATERIALS = {
    "fabric": "fabric_emerald", "trim": "leather_black", "webbing": "police_khaki", "zipper": "chrome",
    "patch": "linen_white", "cross": "medical_red", "hardware": "steel_light",
    "leather": "leather_black", "edge": "graphite", "stitch": "sandstone", "gold": "brass",
    "gold_dark": "copper", "gold_bright": "gold_filigree", "silver": "chrome", "window": "glass_tint",
    "hinge": "steel_dark", "id_card": "linen_white", "body": "graphite", "magazine": "steel_light",
    "grip": "weapon_grip_stipple", "metal": "chrome", "wood_ash": "wood_oak", "grip_tape": "weapon_grip_stipple",
    "brand_stamp": "brass", "barrel": "chrome", "receiver": "steel_dark", "stock": "wood_sheesham",
    "pump": "wood_teak", "card_front": "card_ark_vip", "card_back": "graphite", "chip": "brass",
    "chip_trace": "copper", "can_red": "jerrycan_rib_red", "handle": "paint_red", "spout": "chrome",
    "details": "hazard_yellow", "slide": "weapon_slide_dark", "frame": "steel_dark", "fob_case": "graphite",
    "buttons": "steel_light", "chrome": "chrome", "keyring": "chrome", "bills_side": "linen_white",
    "bills_top": "bills_ark_top", "band": "paint_gold", "handguard": "weapon_vent_guard",
}


def read_manifest(name):
    return json.loads((SOURCE / f"{name}.json").read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def font(size=12):
    for name in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"):
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.int16)


def ramp(h):
    c = rgb(h)
    return [np.clip(c * factor + offset, 0, 255).astype(np.uint8) for factor, offset in ((0.54, 0), (0.74, 0), (0.91, 0), (1.0, 0), (1.04, 12), (1.06, 28))]


def material_from_legacy_uv(face):
    """Read the versioned 16 by 16 material-cell atlas without inferring IDs."""
    uv = face.get("uv", [0, 0, 1, 1])
    idx = int(math.floor(min(uv[0], uv[2] if len(uv) > 2 else uv[0]) + 0.001)) + 16 * int(math.floor(min(uv[1], uv[3] if len(uv) > 3 else uv[1]) + 0.001))
    if idx < 0 or idx >= len(s3d.MATERIALS):
        raise ValueError(f"Unknown legacy atlas slot {idx}")
    return s3d.MATERIALS[idx][0]


def from_tracked_java(path):
    """Reconstitute preserved meshes, including rotations and per-face materials."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    pb = s3d.PartBuilder()
    for index, element in enumerate(data["elements"]):
        origin = element["from"]
        size = [element["to"][i] - origin[i] for i in range(3)]
        uses_atlas = any("gtm_master_atlas" in value for value in data.get("textures", {}).values())
        if uses_atlas:
            face_mats = {face: material_from_legacy_uv(info) for face, info in element["faces"].items()}
        else:
            # User hero props use named material slots, not the common atlas.
            # Treating their0..16 UVs as atlas cells makes every prop dark steel.
            face_mats = {}
            for face, info in element["faces"].items():
                name = info["texture"].removeprefix("#")
                if name not in HERO_MATERIALS:
                    raise ValueError(f"Unmapped hero material: {Path(path).name} #{name}")
                face_mats[face] = HERO_MATERIALS[name]
        mat = next(iter(face_mats.values()))
        rot = None
        pivot = None
        if element.get("rotation"):
            record = element["rotation"]
            rot = ([record["angle"] if axis == record["axis"] else 0 for axis in "xyz"]
                   if "angle" in record else [record.get(axis, 0) for axis in "xyz"])
            pivot = [record["origin"][0] - 8, record["origin"][1], record["origin"][2] - 8]
        pb.box(origin[0] - 8, origin[1], origin[2] - 8, *size, mat=mat, face_mats=face_mats,
               rot=rot, pivot=pivot, name=element.get("name", f"part_{index}"))
    return pb


def iter_equipment():
    original = {entry["id"]: entry for entry in read_manifest("equipment_manifest")["equipment"]}
    for slug, (category, title, parts) in city_item_art.objects().items():
        asset_id = f"gtm:{slug}"
        if asset_id not in original:
            raise ValueError(f"Recipe ID is not in the preserved equipment manifest: {asset_id}")
        pb = recipe_to_partbuilder(parts, SWATCH_MAP, slug)
        yield {**original[asset_id], "id": asset_id, "title": title, "category": "equipment", "equipment_category": category, "catalogue_group": "primary"}, pb


def iter_food():
    original = {entry["meal_slug"]: entry for entry in read_manifest("food_manifest")["items"]}
    for slug, parts in food_art.recipes().items():
        pb = food_recipe_128(slug)
        yield {**original[slug], "category": "food", "catalogue_group": "primary"}, pb


def food_recipe_128(slug):
    """Human-readable cuisine silhouettes on the preserved street-kitchen IDs.

    Stepped rims, tapered vessels and domed breads remain Minecraft cuboids;
    ingredient colour is supplied by the shared native128 material library.
    """
    pb = s3d.PartBuilder()
    counter = 0
    def box(x, y, z, w, h, d, color, label="ingredient"):
        nonlocal counter
        pb.box(x, y, z, w, h, d, mat="food_" + color, name=f"{label}_{counter}")
        counter += 1
    def disk(cx, y, cz, rx, rz, h, color, bands=8):
        for i in range(bands):
            z0 = -rz + 2 * rz * i / bands
            zmid = z0 + rz / bands
            hw = rx * math.sqrt(max(0.04, 1 - (zmid / rz) ** 2))
            box(cx - hw, y, cz + z0, 2 * hw, h, 2 * rz / bands, color, "round_profile")
    def ring(cx, y, cz, radius, width, h, color, bands=10):
        inner = radius - width
        for i in range(bands):
            z0 = -radius + 2 * radius * i / bands
            zmid = z0 + radius / bands
            outer = radius * math.sqrt(max(0.01, 1 - (zmid / radius) ** 2))
            hole = math.sqrt(max(0, inner * inner - zmid * zmid)) if abs(zmid) < inner else 0
            if hole > 0.03:
                box(cx - outer, y, cz + z0, outer - hole, h, 2 * radius / bands, color, "vessel_rim")
                box(cx + hole, y, cz + z0, outer - hole, h, 2 * radius / bands, color, "vessel_rim")
            else:
                box(cx - outer, y, cz + z0, 2 * outer, h, 2 * radius / bands, color, "vessel_rim")
    def dome(cx, y, cz, radius, height, color):
        for level, factor in enumerate((1, .91, .73, .46)):
            disk(cx, y + height * level / 4, cz, radius * factor, radius * factor, height / 4, color)
    def plate():
        disk(0, .9, 0, 6.4, 5.4, .42, "steel")
        disk(0, 1.32, 0, 6.0, 5.0, .22, "rim")
        disk(0, 1.54, 0, 5.35, 4.35, .12, "steel")
    def bowl(base, filling):
        disk(0, 1, 0, 3.5, 3.5, .7, base)
        disk(0, 1.7, 0, 4.2, 4.2, .8, base)
        disk(0, 2.5, 0, 4.8, 4.8, 1.15, base)
        ring(0, 3.65, 0, 4.8, .55, .5, "rim" if base == "steel" else base)
        disk(0, 3.65, 0, 4.1, 4.1, .25, filling)
    def cup(base, filling, height=7, handle=False):
        disk(0, 1, 0, 2.35, 2.35, .45, base)
        for k, radius in enumerate((2.5, 2.75, 3)):
            disk(0, 1.45 + k * height / 3, 0, radius, radius, height / 3, base)
        ring(0, 1.45 + height, 0, 3.05, .45, .4, base)
        disk(0, 1.48 + height, 0, 2.56, 2.56, .15, filling)
        if handle:
            box(2.6, 3.1, -.7, 2.4, .7, 1.4, base, "handle_lower")
            box(4.3, 3.1, -.7, .75, 3.8, 1.4, base, "handle_outer")
            box(2.6, 6.2, -.7, 2.4, .7, 1.4, base, "handle_upper")
    def sprinkles(points, y=4.0, color="mint", size=.55):
        for x, z in points:
            box(x, y, z, size, .2, size * .6, color, "garnish")
    def bun(cx, cz, fill="gold", radius=2.8, base_y=1.8):
        disk(cx, base_y, cz, radius, radius, .6, "bread")
        disk(cx, base_y + .6, cz, radius + .1, radius + .1, 1.0, fill)
        disk(cx, base_y + 1.6, cz, radius, radius, .25, "crust")
        dome(cx, base_y + 1.85, cz, radius, 1.6, "bread")
        sprinkles([(cx - .5, cz - 1), (cx + .5, cz + .3), (cx - .4, cz + .5)], base_y + 3.5, "cream", .42)
    def roll(cx, y, cz, length, radius, color):
        for i in range(8):
            z = -radius + 2 * radius * i / 8
            mid = z + radius / 8
            hh = radius * math.sqrt(max(.03, 1 - (mid / radius) ** 2))
            box(cx - length / 2, y + radius - hh, cz + z, length, 2 * hh, radius / 4, color, "rolled_profile")

    if slug in {"chai", "lassi", "falooda", "nimbu_pani", "filter_coffee"}:
        settings = {"chai": ("clay", "toast", 6, True), "lassi": ("steel", "milk", 8, False), "falooda": ("pink", "milk", 8, False), "nimbu_pani": ("ice", "cream", 7.5, False), "filter_coffee": ("steel", "toast", 4.6, False)}
        base, filling, height, handle = settings[slug]
        if slug == "filter_coffee":
            disk(0, .6, 0, 4.8, 4.8, .35, "rim")
        cup(base, filling, height, handle)
        if slug == "lassi":
            dome(.2, height + 1.65, .1, 1.6, .55, "milk")
            sprinkles([(-.6, 0), (.3, -.4)], height + 2.2, "saffron", .45)
        if slug == "falooda":
            dome(0, height + 1.6, 0, 1.7, 1.4, "pink")
            dome(0, height + 3, 0, .55, .6, "chilli")
            box(1.9, 7.0, .8, .5, 6.5, .5, "cream", "straw")
        if slug == "nimbu_pani":
            box(2.0, 7.5, -2.5, .55, 3.3, 3.0, "gold", "lemon_rind")
            box(2.05, 8, -2.1, .62, 2.4, 2.2, "cream", "lemon_flesh")
            sprinkles([(-1, .5), (-.4, 1.2)], height + 1.7, "mint", .8)
    elif slug in {"vada_pav", "dabeli"}:
        plate(); bun(0, 0, "gold" if slug == "vada_pav" else "gravy", 3.3)
        box(-3.6, 3.1, -.8, 6.8, .3, 1.5, "leaf", "chutney_leaf")
        if slug == "dabeli":
            sprinkles([(-2.5, -2.4), (-1.5, -2.9), (.5, -2.9), (1.9, -2.4)], 3.8, "pink", .5)
        else:
            box(-4.5, 1.9, 2.4, 3.3, .4, .6, "leaf", "green_chilli")
    elif slug == "pav_bhaji":
        plate(); bun(-2.6, -.3, "bread", 2.1)
        disk(2.7, 1.8, .3, 2.3, 2.7, 1.3, "clay")
        disk(2.7, 3.1, .3, 2.0, 2.4, .35, "gravy")
        box(2.1, 3.5, -.3, 1.2, .4, 1.2, "cream", "butter")
        sprinkles([(1.2, .8), (3.4, -.9)], 3.6, "mint")
    elif slug == "samosa":
        plate()
        for i in range(9):
            t = i / 9
            width, depth = 7.8 * (1 - t), 5.8 * (1 - t)
            box(-width / 2, 1.8 + i * .64, -depth / 2 + t * 1.4, width, .64, depth, "crust" if i == 0 else "bread", "folded_pastry")
        disk(-3.7, 1.85, 2.6, 1, .8, .3, "leaf")
    elif slug in {"dosa", "kathi_roll"}:
        plate(); roll(0, 1.8, .6, 10, 1.6, "bread")
        if slug == "dosa":
            box(-4.8, 3.6, .4, 9.6, .22, .8, "gold", "toasted_crease")
            disk(-2.7, 1.8, -3.0, 1.3, .9, .3, "leaf")
            disk(1.3, 1.8, -3.0, 1.4, .9, .3, "gravy")
        else:
            box(-1.5, 1.75, -.9, 3.2, 3.3, 3.15, "cream", "paper_wrap")
            sprinkles([(-5.15, 0), (4.85, .3)], 3.2, "leaf", .8)
            sprinkles([(-5.1, -.5), (4.8, -.5)], 2.8, "chilli", .65)
    elif slug == "idli":
        plate(); dome(-2.3, 1.8, -1.0, 2.15, 1.5, "milk"); dome(2.1, 1.8, 1.0, 2.15, 1.5, "milk")
        disk(-2.9, 1.8, 2.8, 1.4, 1, .35, "gravy")
    elif slug == "thali":
        plate(); dome(-2.9, 1.8, -1.8, 2, 1.8, "rice")
        disk(-2.5, 1.8, 2.0, 2.6, 1.7, .28, "bread")
        for x, z, color in ((2.5, -2, "gravy"), (2.5, 2, "gold"), (0, 0, "leaf")):
            disk(x, 1.8, z, 1.6, 1.5, .6, "rim"); disk(x, 2.4, z, 1.35, 1.25, .25, color)
    elif slug in {"biryani", "poha", "misal", "upma", "ragda", "sheera"}:
        fill = {"biryani": "rice", "poha": "gold", "misal": "gravy", "upma": "cream", "ragda": "cream", "sheera": "gold"}[slug]
        base = {"biryani": "clay", "poha": "leaf", "misal": "steel", "upma": "rim", "ragda": "terra", "sheera": "clay"}[slug]
        bowl(base, fill)
        if slug == "biryani":
            sprinkles([(-2, -2), (0, 0), (2, 1), (-1, 2)], 4, "saffron", .9)
            sprinkles([(-1, -2), (1, -.8), (-2, 1), (.5, 2)], 4.1, "rice", .65)
        elif slug == "poha":
            for x, z in ((-2, -1), (1, 1), (2, -2)):
                dome(x, 4, z, .55, .4, "bean")
            box(1, 4.1, 1.7, 1.7, .4, .9, "cream", "lemon_wedge")
        elif slug == "misal":
            for x, z in ((-2, -1), (0, 1), (2, -1)):
                box(x, 4, z, 1.8, .3, .35, "gold", "farsan")
            sprinkles([(-1, -.5), (1.5, 1.5)], 4.25, "pink", .7)
        elif slug == "upma":
            sprinkles([(-2, -1.5), (.8, 1.2)], 4.05, "terra", .8)
        elif slug == "ragda":
            dome(-1.8, 4, -.8, 1.4, .7, "crust"); dome(1.5, 4, 1, 1.35, .7, "crust")
        else:
            for x, z in ((-1.5, -.7), (1, .8)):
                box(x, 4.1, z, 1.2, .3, .4, "cream", "cashew")
            dome(1.4, 4.1, -1.4, .5, .35, "bean")
        sprinkles([(-1.1, 1.1), (1.7, -1.1), (.3, .1)], 4.35, "mint", .6)
    elif slug == "dhokla":
        plate()
        for x, z in ((-3.5, -2.7), (.5, .3)):
            box(x, 1.8, z, 3, 2.8, 3, "gold", "steamed_cake")
            sprinkles([(x + .5, z + .5), (x + 1.7, z + 1.8)], 4.65, "leaf", .65)
            sprinkles([(x + .7, z + 1.7)], 4.65, "bean", .3)
    elif slug == "khandvi":
        plate()
        for z in (-2.6, 0, 2.6):
            roll(0, 1.9, z, 6.5, .9, "gold")
            sprinkles([(-1.7, z), (1.2, z)], 3.72, "leaf", .6)
    elif slug in {"puran_poli", "bhakri", "thepla"}:
        plate()
        base = "cream" if slug == "bhakri" else "bread"
        for layer in range(2 if slug == "thepla" else 1):
            disk(layer * .35, 1.8 + layer * .4, -layer * .35, 4.5, 4.0, .35, base)
        if slug == "puran_poli":
            box(-.7, 2.2, -.7, 1.4, .4, 1.4, "cream", "ghee")
        for i, (x, z) in enumerate(((-2, -1), (2, 1.5), (.4, -2.6), (-2.1, 2))):
            disk(x, 2.2 + (.4 if slug == "thepla" else 0), z, .45 + .1 * (i % 2), .35, .07, "toast" if slug != "thepla" else "leaf", bands=4)
        if slug == "bhakri":
            box(-4.5, 2.3, 2, 3.2, .3, .6, "leaf", "chilli")
    elif slug == "modak":
        plate()
        for i in range(9):
            radius = 2.4 * (1 - i / 10)
            disk(0, 1.8 + i * .5, 0, radius, radius, .5, "milk", bands=8)
        for x, z in ((-1.9, 0), (1.4, 0), (0, -1.9), (0, 1.4)):
            box(x, 2, z, .5, 2.5, .5, "cream", "pleat")
    elif slug == "jalebi":
        plate()
        # Interlocking sweet coils. The ring gaps remain visible from inventory.
        for x, z, radius in ((-2, -1, 2), (1.5, -.6, 2), (0, 2, 1.9)):
            ring(x, 1.9, z, radius, .65, .6, "saffron")
        sprinkles([(-2.2, -2), (1.1, -.7), (-.8, 2)], 2.55, "gold", .9)
    elif slug == "kulfi":
        box(-.45, .8, -.45, .9, 4.6, .9, "toast", "wooden_stick")
        for i in range(6):
            r = 2.3 - i * .16
            disk(0, 4 + i * 1.0, 0, r, r, 1.0, "cream" if i < 5 else "gold")
        sprinkles([(-1.4, -1.5), (.6, .6)], 10.1, "mint", .5)
    elif slug == "pani_puri":
        plate()
        for x, z in ((-2.5, -1.8), (2.3, -1.6), (0, 2.1)):
            dome(x, 1.8, z, 1.85, 2.5, "bread")
            disk(x, 4.25, z, .65, .65, .12, "gravy", bands=6)
            sprinkles([(x - .1, z - .1)], 4.4, "leaf", .55)
    elif slug == "sev_puri":
        plate()
        for x, z in ((-2.4, -1.5), (2.3, -1.4), (0, 2.0)):
            disk(x, 1.8, z, 1.75, 1.75, .35, "bread")
            dome(x, 2.15, z, 1.25, .6, "gravy")
            for offset in (-.6, .1, .7):
                box(x - .9, 2.8, z + offset, 1.8, .2, .15, "gold", "sev")
    elif slug == "sandesh":
        plate()
        for x, z in ((-2.3, -1.4), (2.1, 1.2)):
            dome(x, 1.8, z, 2, 1.7, "milk")
            sprinkles([(x - .3, z - .2)], 3.55, "mint", .65)
            sprinkles([(x + .4, z + .4)], 3.55, "saffron", .5)
    else:
        raise ValueError(f"Missing preserved food recipe: {slug}")
    return pb


def iter_weapons():
    seen = set()
    for mapping in read_manifest("finishes_migration")["mappings"]:
        asset_id = mapping["target_weapon_id"]
        if asset_id in seen:
            continue
        seen.add(asset_id)
        path = ROOT / mapping["weapon_java_model_path"]
        yield {"id": asset_id, "title": mapping["target_weapon_name"], "category": "weapons",
               "weapon_class": mapping["target_weapon_class"], "catalogue_group": "additional_weapon_sources",
               "preserved_source_path": mapping["weapon_java_model_path"]}, from_tracked_java(path)


def iter_hero_props():
    for entry in read_manifest("equipment_manifest")["hero_props"]:
        yield {**entry, "category": "hero_props", "catalogue_group": "additional_hero_sources", "preserved_source_path": entry["java_model_path"]}, from_tracked_java(ROOT / entry["java_model_path"])


def finish_pattern(finish_id, weapon_index, weapon_id):
    """Native 128-pixel pattern, with materially different collection structures."""
    if finish_id not in FINISH_COLORS:
        raise ValueError(f"Unsupported preserved finish ID {finish_id}")
    a, b, c = [ramp(x) for x in FINISH_COLORS[finish_id]]
    y, x = np.mgrid[:128, :128]
    phase = weapon_index % 13
    px, py = x + phase * 3, y + (weapon_index // 3) * 5
    arr = np.zeros((128, 128, 4), np.uint8)
    arr[:, :, :3] = a[3]
    arr[:, :, 3] = 255
    if finish_id == "gold_leaf":
        # Engraved architectural jali: stepped diamonds, filigree and rivet keys.
        dx, dy = abs((px % 32) - 15.5), abs((py % 32) - 15.5)
        arr[:, :, :3] = a[2]
        arr[((dx + dy).astype(int) % 16) < 2, :3] = b[1]
        arr[((dx + dy).astype(int) % 16) == 2, :3] = c[4]
        arr[(dx < 2) | (dy < 2), :3] = a[4]
        arr[(dx < 2) & (dy < 2), :3] = c[5]
        arr[(x % 4 == 0) & (y % 4 == 0), :3] = a[3]
    elif finish_id == "monsoon_camo":
        # Broad rain-shadow patches with irregular stepped boundaries.
        cells = (((px // 11) * 19 + (py // 9) * 31 + (px // 23) * (py // 19) + weapon_index) % 11)
        arr[cells < 4, :3] = b[1]
        arr[cells > 7, :3] = c[2]
        arr[(cells == 6) & ((px + py) % 7 < 2), :3] = a[5]
        arr[(px % 17 == 4) & (py % 11 < 7), :3] = c[3]
    elif finish_id == "graphite_stealth":
        # Eight-pixel carbon twill with a directional two-pixel sheen.
        weave = ((px // 8 + py // 8) % 2 == 0)
        arr[:, :, :3] = b[2]
        arr[weave, :3] = a[3]
        arr[weave & (px % 8 < 2), :3] = a[5]
        arr[~weave & (py % 8 < 2), :3] = a[4]
        arr[(px + py) % 32 == 0, :3] = c[3]
    elif finish_id == "royal_emerald":
        dx, dy = abs(px % 32 - 15.5), abs(py % 32 - 15.5)
        arr[:, :, :3] = b[2]
        arr[(dx + dy) < 19, :3] = a[3]
        arr[((dx + dy) >= 14) & ((dx + dy) < 16), :3] = c[4]
        arr[((dx < 2) & (dy < 7)) | ((dy < 2) & (dx < 7)), :3] = c[5]
        arr[(dx > 12) & (dy > 12), :3] = a[5]
    elif finish_id == "terracotta_dune":
        # Sandstone sediment bands, interlocking stepped topographic contours.
        contour = (py + (px // 13) * 3 + ((px // 31) % 3) * 4) % 36
        arr[contour < 12, :3] = a[2]
        arr[(contour >= 12) & (contour < 25), :3] = c[3]
        arr[contour >= 25, :3] = b[3]
        arr[(contour == 11) | (contour == 24), :3] = a[5]
        arr[(px % 11 == 2) & (py % 13 == 6), :3] = b[2]
    elif finish_id == "deccan_chrome":
        reflection = (px + 2 * py + weapon_index * 7) % 64
        arr[:, :, :3] = b[3]
        arr[(reflection >= 16) & (reflection < 42), :3] = a[3]
        arr[(reflection >= 27) & (reflection < 35), :3] = c[5]
        arr[(reflection == 15) | (reflection == 42), :3] = a[5]
        arr[(py % 8 == 0) & (reflection < 24), :3] = b[4]
    elif finish_id == "maratha_rust":
        # Chipped panels and oxidised seams; large clusters rather than noise.
        seam = (px % 43 < 3) | (py % 37 < 3)
        chips = (((px // 7) * 17 + (py // 5) * 23 + weapon_index) % 19 < 4)
        arr[:, :, :3] = b[3]
        arr[chips, :3] = a[3]
        arr[seam, :3] = c[3]
        arr[seam & (px % 3 == 0), :3] = c[5]
        arr[chips & ((px + py) % 7 == 1), :3] = a[5]
    elif finish_id == "lotus_pearl":
        dx, dy = abs(px % 32 - 15.5), abs(py % 32 - 15.5)
        petals = (dx * 2 + dy < 22) | (dx + dy * 2 < 22)
        arr[:, :, :3] = b[2]
        arr[petals, :3] = a[3]
        arr[(dx + dy < 13) & petals, :3] = c[2]
        arr[(dx + dy < 5), :3] = c[5]
        arr[(dx > 13) & (dy > 13), :3] = a[5]
    elif finish_id == "bazaar_mosaic":
        dx, dy = abs(px % 32 - 15.5), abs(py % 32 - 15.5)
        arr[:, :, :3] = a[3]
        arr[(dx + dy) < 12, :3] = c[3]
        arr[(dx < 3) | (dy < 3), :3] = b[2]
        arr[((dx + dy) > 20) & ((dx + dy) < 23), :3] = c[4]
        arr[(px % 32 == 0) | (py % 32 == 0), :3] = b[0]
        arr[(px % 32 == 1) | (py % 32 == 1), :3] = a[5]
    else:
        # Offset circuit routes with pads and right-angle branching.
        arr[:, :, :3] = b[2]
        horizontal = ((py % 24 == 7) | (py % 24 == 8)) & (px % 48 < 36)
        vertical = ((px % 24 == 13) | (px % 24 == 14)) & (py % 48 < 36)
        arr[horizontal | vertical, :3] = c[3]
        arr[(px % 24 >= 11) & (px % 24 <= 16) & (py % 24 >= 5) & (py % 24 <= 10), :3] = c[5]
        arr[(px % 12 == 1) & (py % 12 == 1), :3] = a[4]
    image = Image.fromarray(arr)
    # Small engraved maker cartouche identifies the matching weapon, not a
    # random distinguishing pixel. The collection design occupies the surface.
    draw = ImageDraw.Draw(image)
    mark = weapon_id.removeprefix("gtm:").replace("_", " ").upper()
    draw.rectangle((3, 113, 91, 124), fill=tuple(int(v) for v in b[1]) + (255,))
    draw.text((5, 114), mark[:17], font=font(7), fill=tuple(int(v) for v in c[4]) + (255,))
    return image


def secondary_cells():
    """Native procedural material cells within each 128-pixel finish UV map."""
    cells = {}
    y, x = np.mgrid[:32, :32]
    for name, color in (("grip", "#242A2D"), ("metal", "#9EADB5"), ("wood", "#824D27"), ("lens", "#236653")):
        r = ramp(color)
        a = np.zeros((32, 32, 4), np.uint8)
        a[:, :, :3] = r[3]
        a[:, :, 3] = 255
        if name == "grip":
            a[(x // 3 + y // 3) % 2 == 0, :3] = r[1]
            a[(x % 3 == 0) & (y % 3 == 0), :3] = r[4]
        elif name == "metal":
            a[(x + y) % 32 < 9, :3] = r[1]
            a[((x + y) % 32 >= 15) & ((x + y) % 32 < 19), :3] = r[5]
        elif name == "wood":
            a[(y + (x // 7) % 3) % 8 < 2, :3] = r[1]
            a[(y + (x // 7) % 3) % 8 == 2, :3] = r[4]
        else:
            a[(x + y) % 32 < 6, :3] = r[5]
            a[(x + y) % 32 > 25, :3] = r[1]
        a[0, :, :3] = r[4]
        a[-1, :, :3] = r[1]
        a[:, 0, :3] = r[4]
        a[:, -1, :3] = r[1]
        cells[name] = Image.fromarray(a)
    return cells


def finish_atlas(pattern):
    image = pattern.copy()
    for index, cell in enumerate(secondary_cells().values()):
        image.paste(cell, (96, 32 * index))
    return image


def classify_material(name):
    if any(token in name for token in ("grip", "leather", "rubber", "carbon", "fabric")):
        return "grip"
    if any(token in name for token in ("wood", "bamboo")):
        return "wood"
    if any(token in name for token in ("glass", "neon", "beacon", "headlight")):
        return "lens"
    if name in {"chrome", "stainless", "aluminum", "gun_muzzle_bore"}:
        return "metal"
    return "body"


def finish_region(material):
    kind = classify_material(material)
    if kind == "body":
        return [0.5, 0.5, 95, 127]
    index = {"grip": 0, "metal": 1, "wood": 2, "lens": 3}[kind]
    return [96.5, 32 * index + .5, 31, 31]


def export_finish_variant(pb, original_java, record, output):
    """Export the same geometry with a compact, explicitly bound 128 UV map."""
    slug = record["target_full_id"].removeprefix("gtm:")
    old = json.loads(Path(original_java).read_text(encoding="utf-8"))
    java = deepcopy(old)
    java["credit"] = "SD Craft / GTM 128 — preserved geometry, compact cosmetic UV atlas"
    java["textures"] = {"finish": f"gtm:item/finishes/{slug}", "particle": "#finish"}
    for element in java["elements"]:
        if element.get("rotation"):
            old_rotation = element["rotation"]
            angles = ([old_rotation["angle"] if axis == old_rotation["axis"] else 0 for axis in "xyz"]
                      if "angle" in old_rotation else [old_rotation.get(axis, 0) for axis in "xyz"])
            element["rotation"] = {"origin": old_rotation["origin"], **dict(zip("xyz", angles))}
        for face in element["faces"].values():
            region = finish_region(material_from_legacy_uv(face))
            face["uv"] = [round(region[0] / 8, 5), round(region[1] / 8, 5), round((region[0] + region[2]) / 8, 5), round((region[1] + region[3]) / 8, 5)]
            face["texture"] = "#finish"
    geo_bones = []
    for name, bone in pb.bones.items():
        cubes = []
        for part in bone["parts"]:
            uv = {}
            for face in ("north", "south", "east", "west", "up", "down"):
                u, v, w, h = finish_region(part["face_mats"].get(face, part["mat"]))
                uv[face] = {"uv": [u, v], "uv_size": [w, h]}
            cube = {"origin": part["origin"], "size": part["size"], "uv": uv}
            if part["rot"]:
                cube["rotation"] = part["rot"]
                cube["pivot"] = part["pivot"] or [part["origin"][i] + part["size"][i] / 2 for i in range(3)]
            cubes.append(cube)
        item = {"name": name, "pivot": bone["pivot"], "cubes": cubes}
        if bone["parent"]:
            item["parent"] = bone["parent"]
        geo_bones.append(item)
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{"description": {"identifier": f"geometry.gtm.{slug}", "texture_width": 128, "texture_height": 128, "visible_bounds_width": 4, "visible_bounds_height": 4, "visible_bounds_offset": [0, 1, 0]}, "bones": geo_bones}]}
    java_path = output / "source/models/finishes/java" / f"{slug}.json"
    geo_path = output / "source/models/finishes" / f"{slug}.geo.json"
    for path, data in ((java_path, java), (geo_path, geo)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"java_model_path": java_path.relative_to(output).as_posix(), "geometry_path": geo_path.relative_to(output).as_posix(), "sha256_java_model": sha(java_path), "sha256_bedrock_geometry": sha(geo_path), "java_rotation_approximations": 0, "java_rotation_format": "multi_axis_1.21.11_plus"}


def render_finish_icon(pb, atlas_image, dest):
    """Render the actual compact UV material regions onto the preserved mesh.

    Each UV region is resampled as a material for the shared renderer; the
    silhouette, lighting, depth buffer and final output are evaluated at128.
    No rendered image is enlarged from a lower-resolution sprite.
    """
    original = (s3d.MATERIALS, s3d.MAT_INDEX, s3d.ATLAS_ARR, s3d.TILE_SIZE)
    try:
        names = ("body", "grip", "metal", "wood", "lens")
        s3d.MATERIALS = [(name, "#151B20", "metal") for name in names]
        s3d.MAT_INDEX = {name: i for i, name in enumerate(names)}
        s3d.TILE_SIZE = 128
        regions = [atlas_image.crop((0, 0, 96, 128))] + [atlas_image.crop((96, i * 32, 128, (i + 1) * 32)) for i in range(4)]
        s3d.ATLAS_ARR = np.concatenate([np.asarray(region.resize((128, 128), Image.Resampling.NEAREST)) for region in regions], axis=1)
        shaded = s3d.PartBuilder()
        shaded.bones = deepcopy(pb.bones)
        for bone in shaded.bones.values():
            for part in bone["parts"]:
                part["mat"] = classify_material(part["mat"])
                part["face_mats"] = {face: classify_material(material) for face, material in part["face_mats"].items()}
        shaded.render_icon(dest, size=128, grid=128, yaw_deg=-38, pitch_deg=24)
    finally:
        s3d.MATERIALS, s3d.MAT_INDEX, s3d.ATLAS_ARR, s3d.TILE_SIZE = original


def contact_sheet(entries, output, filename, title, columns=6, thumb_key="icon_path"):
    tile_w, tile_h = 166, 164
    rows = math.ceil(len(entries) / columns)
    image = Image.new("RGB", (columns * tile_w + 32, rows * tile_h + 78), "#10171B")
    draw = ImageDraw.Draw(image)
    draw.text((20, 16), title, font=font(21), fill="#E4C58A")
    draw.text((20, 44), "GTM / INDRAPRASTHA  •  native 128 × 128  •  SD CRAFT", font=font(12), fill="#A6B9B0")
    for i, record in enumerate(entries):
        pos = (16 + (i % columns) * tile_w, 72 + (i // columns) * tile_h)
        draw.rounded_rectangle((pos[0], pos[1], pos[0] + tile_w - 8, pos[1] + tile_h - 8), radius=6, fill="#1B262B", outline="#2C3E41")
        path = output / record[thumb_key]
        icon = Image.open(path).convert("RGBA")
        if icon.size != (128, 128):
            raise ValueError(f"Non-native128 thumbnail: {path} {icon.size}")
        image.paste(icon, (pos[0] + 15, pos[1] + 3), icon)
        label = record.get("title", record.get("id", "")).replace("gtm:", "")
        if len(label) > 22:
            label = label[:21] + "…"
        draw.text((pos[0] + 7, pos[1] + 134), label, font=font(10), fill="#E1E4DC")
    path = output / "previews" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)
    return path.relative_to(output).as_posix()


def build_finishes(output, weapon_builders, export_geometry=True):
    original = read_manifest("finishes_migration")
    mappings = original["mappings"]
    weapons = list(dict.fromkeys(x["target_weapon_id"] for x in mappings))
    weapon_indexes = {wid: i for i, wid in enumerate(weapons)}
    out = []
    tex_dir = output / "source/textures/finishes"
    tex_dir.mkdir(parents=True, exist_ok=True)
    for mapping in mappings:
        record = deepcopy(mapping)
        slug = record["target_full_id"].removeprefix("gtm:")
        pattern = finish_pattern(record["target_finish_id"], weapon_indexes[record["target_weapon_id"]], record["target_weapon_id"])
        atlas = finish_atlas(pattern)
        path = tex_dir / f"{slug}.png"
        atlas.save(path, optimize=True)
        data = {"id": record["target_full_id"], "title": record["target_weapon_name"] + " / " + record["target_finish_name"], "texture": path.relative_to(output).as_posix(), "size_px": [128, 128], "sha256": sha(path), "geometry_id": record["target_weapon_id"], "collection_id": record["target_finish_id"], "legacy_mapping": record, "status": "art_generated", "engine_binding": "migration_review_required", "client_verification": "not_performed", "uv_layout": {"body": [0, 0, 96, 128], "grip": [96, 0, 32, 32], "metal": [96, 32, 32, 32], "wood": [96, 64, 32, 32], "lens": [96, 96, 32, 32]}}
        if export_geometry:
            data.update(export_finish_variant(weapon_builders[record["target_weapon_id"]], ROOT / record["weapon_java_model_path"], record, output))
            icon_path = output / "source/icons/finishes" / f"{slug}.png"
            render_finish_icon(weapon_builders[record["target_weapon_id"]], atlas, icon_path)
            data["icon_path"] = icon_path.relative_to(output).as_posix()
            data["sha256_icon"] = sha(icon_path)
        out.append(data)
    if len(out) != 300 or len({x["id"] for x in out}) != 300:
        raise ValueError("Expected 300 preserved unique finish IDs")
    if len({x["sha256"] for x in out}) != 300:
        raise ValueError("Finish textures are unexpectedly duplicated")
    original["generation_profile"] = "INDRAPRASTHA_128_V1"
    original["mappings_128"] = out
    original["note"] = "Original mappings retained unchanged. Finished art does not activate the proposed entitlement migration. Thirty preserved weapon-source meshes include melee and special props; they are not thirty newly verified firearms."
    dest = output / "manifests/finishes_128.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(original, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    contact_sheet(out, output, "equipment_finishes_all.png", "300 cosmetic textures · 30 preserved sources × 10 collections", columns=10, thumb_key="texture")
    representatives = [{**item, "title": item["legacy_mapping"]["target_finish_name"]} for name in FINISH_COLORS for item in [next(x for x in out if x["collection_id"] == name)]]
    contact_sheet(representatives, output, "equipment_finish_collections.png", "Ten cosmetic collections · native128 UV artwork", columns=5, thumb_key="texture")
    if export_geometry:
        contact_sheet(representatives, output, "equipment_finish_models.png", "Applied finishes · native128 texture and geometry preview", columns=5)
        contact_sheet(out, output, "equipment_finish_models_all.png", "300 cosmetic variants · native128 geometry previews", columns=10)
    return out


def validate_generated(output, model_groups, finishes):
    """Check geometry parity, actual raster dimensions, UV bounds and stable IDs."""
    base = [entry for records in model_groups.values() for entry in records]
    errors = []
    stats = {"base_models": len(base), "finish_variants": len(finishes), "checked_pngs": 0,
             "checked_model_pairs": 0, "native128_icons": 0, "native128_finish_atlases": 0}
    for record in base + finishes:
        java = json.loads((output / record["java_model_path"]).read_text())
        geo = json.loads((output / record["geometry_path"]).read_text())["minecraft:geometry"][0]
        cubes = [cube for bone in geo["bones"] for cube in bone.get("cubes", [])]
        if len(cubes) != len(java["elements"]):
            errors.append(record["id"] + ": platform element counts differ")
        width, height = geo["description"]["texture_width"], geo["description"]["texture_height"]
        for cube in cubes:
            if min(cube["size"]) <= 0:
                errors.append(record["id"] + ": nonpositive cube dimensions")
            for face in cube["uv"].values():
                u, v = face["uv"]
                w, h = face["uv_size"]
                if u < 0 or v < 0 or u + w > width or v + h > height:
                    errors.append(record["id"] + ": Bedrock UV out of bounds")
        for element in java["elements"]:
            for face in element["faces"].values():
                if min(face["uv"]) < 0 or max(face["uv"]) > 16:
                    errors.append(record["id"] + ": Java UV out of bounds")
            rotation = element.get("rotation", {})
            if rotation and ("axis" in rotation or "angle" in rotation):
                errors.append(record["id"] + ": stale rotation representation")
        stats["checked_model_pairs"] += 1
        image = Image.open(output / record["icon_path"])
        if image.size != (128, 128) or image.mode != "RGBA" or image.getbbox() is None:
            errors.append(record["id"] + ": invalid native128 icon")
        if image.getchannel("A").getextrema() != (0, 255):
            errors.append(record["id"] + ": icon transparency missing")
        stats["checked_pngs"] += 1
        stats["native128_icons"] += 1
    for record in finishes:
        image = Image.open(output / record["texture"])
        if image.size != (128, 128) or image.mode != "RGBA" or image.getchannel("A").getextrema() != (255, 255):
            errors.append(record["id"] + ": invalid finish UV atlas")
        stats["checked_pngs"] += 1
        stats["native128_finish_atlases"] += 1
    stats["unique_finish_pixels"] = len({hashlib.sha256(Image.open(output / record["texture"]).tobytes()).hexdigest() for record in finishes})
    if stats["unique_finish_pixels"] != 300:
        errors.append("Finish textures unexpectedly share pixel hashes")
    for group, source_name, key in (("equipment", "equipment_manifest", "equipment"), ("food", "food_manifest", "items")):
        original_ids = {record["id"] for record in read_manifest(source_name)[key]}
        if original_ids != {record["id"] for record in model_groups[group]}:
            errors.append(group + ": stable IDs differ from source")
    report = {"profile": "INDRAPRASTHA_128_V1", "checks": stats, "errors": errors, "passed": not errors,
              "preview_files": ["food_128.png", "equipment_equipment_128.png", "equipment_weapons_128.png", "equipment_hero_props_128.png", "equipment_finish_collections.png", "equipment_finish_models.png"],
              "client_verification": "not_run", "runtime_entitlement_migration": "not_applied"}
    path = output / "reports/equipment_food_checks.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if errors:
        raise ValueError("Equipment art validation failed: " + "; ".join(errors[:10]))
    return report


def build(output=DEFAULT_OUTPUT, textures_only=False):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    weapon_records = list(iter_weapons())
    weapon_builders = {record["id"]: pb for record, pb in weapon_records}
    if textures_only:
        return {"finishes": build_finishes(output, weapon_builders)}
    import gtm128_core as core
    core.configure(output)
    for name, color in food_art.PALETTE.items():
        core.register_material("food_" + name, color, FOOD_KINDS[name])
    groups = {"equipment": list(iter_equipment()), "food": list(iter_food()), "weapons": weapon_records, "hero_props": list(iter_hero_props())}
    all_records = {}
    for group, recipes in groups.items():
        records = []
        for original, pb in recipes:
            metadata = {"catalogue_group": original["catalogue_group"], "preserved_id": original["id"], "source_recipe": original.get("preserved_source_path", "tools/city_item_art.py" if group == "equipment" else "tools/gtm128_equipment_food.py"), "native_grid": [128, 128], "preview_yaw_deg": 142 if group in ("equipment", "hero_props") else -38, "preview_pitch_deg": 24}
            record = core.export_model(pb, original["id"], original["title"], original["category"], output, metadata=metadata)
            record["legacy_source_record"] = original
            record["catalogue_group"] = original["catalogue_group"]
            records.append(record)
        all_records[group] = records
        # Core's canonical icon field is intentionally required, not guessed.
        contact_sheet(records, output, f"equipment_{group}_128.png" if group != "food" else "food_128.png", f"{group.replace('_', ' ').title()} · {len(records)} preserved designs", columns=6)
        print(f"Generated {len(records)} {group} model pairs and native128 icons", flush=True)
    finishes = build_finishes(output, weapon_builders)
    manifest = {"schema_version": 1, "profile": "INDRAPRASTHA_128_V1", "palette": PALETTE, "source_revision": "dddd9da4e469882988d513836dc81052a8283f32", "status": "art_generated", "client_verification": "not_performed", "counts": {**{k: len(v) for k, v in all_records.items()}, "finish_textures": len(finishes), "primary_models": len(all_records["equipment"]) + len(all_records["food"])}, "equipment_category_counts": dict(Counter(x["legacy_source_record"]["equipment_category"] for x in all_records["equipment"])), "note": "Preserved existing catalogue. Additional thirty weapon-source designs and eleven hero props are reported separately, not added to the509 primary total. Finish variants share these existing meshes.", **all_records, "finishes_manifest": "manifests/finishes_128.json"}
    dest = output / "manifests/equipment_food_128.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    validate_generated(output, all_records, finishes)
    print(json.dumps(manifest["counts"], sort_keys=True), flush=True)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--textures-only", action="store_true", help="Build the300 cosmetic textures and paired UV geometry independently")
    args = parser.parse_args()
    build(args.output, args.textures_only)
