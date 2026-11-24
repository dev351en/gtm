#!/usr/bin/env python3
"""
Faithful 32x Studio 3D Engine & Pixel-Art Sprite Pipeline for GTM Revision 4.

Capabilities:
1. Generates 115+ individual 32x32 Faithful-32x-inspired RGBA PNG textures in creative/source/textures/32x32/
   AND packs them into a 512x512 (16x16 x 32px = 256 slots) master atlas (creative/source/textures/gtm_master_atlas_32x.png).
2. Multi-bone PartBuilder with PER-FACE UV overrides (`face_mats`) across Bedrock .geo.json and Java .json models.
3. True Per-Pixel Z-Buffered & UV-Textured Pixel-Locked Isometric Renderer:
   - Outward-facing CCW cube topology (zero inverted/culled front faces).
   - Native 64x64 pixel-art Z-buffer render with quantized Faithful lighting, crisp 1px dark hue-shifted outline,
     zero Gaussian smudge, and integer NEAREST upscaling to 128x128 RGBA.
4. `PixelCanvas` helper for hand-crafted 32x32 / 64x64 Faithful-inspired 2D pixel-art icons
   (outlines, hue-shifted specular/shadow ramps, anti-pillow lighting, NEAREST integer upscaling).
"""
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageColor, ImageDraw

import faithful_32x_palette as f32

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
TEX_32_DIR = CREATIVE / "source" / "textures" / "32x32"
ATLAS_PATH = CREATIVE / "source" / "textures" / "gtm_master_atlas_32x.png"
# Legacy defaults; the isolated 128 profile configures these without changing IDs.
TILE_SIZE = 32
ATLAS_SIZE = 512
ATLAS_RESOURCE = "gtm:item/gtm_master_atlas_32x"

# Core 64 Materials + 46 Dedicated Per-Face Detail Tiles = 110 slots inside 16x16 (512x512) Atlas
MATERIALS = [
    # Row 0 (0..15): Core Metals, Chassis & Fleet Paints
    ("steel_dark", "#2B323C", "metal"), ("steel_light", "#748292", "metal"), ("chrome", "#D8E4F0", "chrome"), ("aluminum", "#B2BECA", "metal"),
    ("graphite", "#171C22", "stone"), ("rubber_tire", "#1D2026", "tread"), ("alloy_rim", "#B8C4D0", "chrome"), ("carbon", "#21262D", "carbon"),
    ("paint_red", "#BA2B31", "metal_paint"), ("paint_white", "#ECEEF2", "metal_paint"), ("paint_black", "#1E2228", "metal_paint"), ("paint_silver", "#B8C2CC", "metal_paint"),
    ("paint_blue", "#1E5290", "metal_paint"), ("paint_emerald", "#246A56", "metal_paint"), ("paint_saffron", "#E27D24", "metal_paint"), ("paint_gold", "#D6AD59", "chrome"),
    # Row 1 (16..31): Transit, Emergency, Glass & Lights
    ("taxi_yellow", "#F5B800", "metal_paint"), ("auto_green", "#1A6B44", "metal_paint"), ("maroon_rail", "#7E222B", "metal_paint"), ("terracotta", "#AD5637", "bricks"),
    ("police_khaki", "#C2A673", "fabric"), ("police_navy", "#172742", "metal_paint"), ("fire_red", "#CC2C2C", "metal_paint"), ("ambulance_white", "#F4F7FA", "metal_paint"),
    ("glass_tint", "#2D4F66", "glass"), ("glass_clear", "#82CFE4", "glass"), ("headlight", "#FFF3C4", "headlight"), ("taillight", "#DC2626", "taillight"),
    ("beacon_blue", "#2563EB", "lamp_blue"), ("beacon_amber", "#F59E0B", "lamp_amber"), ("grille_mesh", "#22262C", "mesh"), ("license_plate", "#E8EAED", "plate"),
    # Row 2 (32..47): Woods, Stones & Fabrics
    ("wood_teak", "#824D27", "wood"), ("wood_sheesham", "#593018", "wood"), ("wood_oak", "#B68652", "wood"), ("bamboo", "#C4A35A", "wood"),
    ("sandstone", "#D4BB94", "bricks"), ("marble", "#EAE5DC", "polished"), ("granite", "#525860", "cobble"), ("brick_clay", "#9E472D", "bricks"),
    ("fabric_beige", "#D6C5A9", "fabric"), ("fabric_emerald", "#1E5646", "fabric"), ("fabric_navy", "#243447", "fabric"), ("fabric_maroon", "#692332", "fabric"),
    ("leather_tan", "#8B4E24", "fabric"), ("leather_black", "#242429", "fabric"), ("linen_white", "#EFEBE0", "fabric"), ("mattress_blue", "#789BB2", "fabric"),
    # Row 3 (48..63): Ornament, Festival, Hazard & Props
    ("brass", "#D69E2E", "chrome"), ("copper", "#C06C44", "chrome"), ("marigold", "#F59E0B", "leaves"), ("crimson_silk", "#9F1239", "fabric"),
    ("neon_cyan", "#22D3EE", "lamp_blue"), ("neon_magenta", "#E879F9", "lamp_amber"), ("holi_pink", "#EC4899", "leaves"), ("leaf_green", "#368C48", "leaves"),
    ("hazard_yellow", "#EAB308", "hazard"), ("medical_red", "#DC2626", "metal_paint"), ("medical_teal", "#0D9488", "metal_paint"), ("stainless", "#CBD5E1", "chrome"),
    ("earth_soil", "#6D4F35", "dirt"), ("water_teal", "#2282A4", "water"), ("gold_filigree", "#E8C87E", "chrome"), ("lotus_dark", "#3B1C32", "metal_paint"),
    # Row 4 (64..79): Per-Face Automotive & Transit Detail Tiles
    ("headlight_face", "#FFF3C4", "detail_headlight"), ("taillight_face", "#DC2626", "detail_taillight"),
    ("grille_chrome", "#CBD5E1", "detail_grille_chrome"), ("grille_black", "#1E222A", "detail_grille_black"),
    ("windshield_front", "#2A4C66", "detail_windshield"), ("license_plate_mh01", "#E8EAED", "plate"),
    ("car_door_red", "#BA2B31", "door_std"), ("car_door_white", "#ECEEF2", "door_std"),
    ("car_door_black", "#1E2228", "door_std"), ("car_door_silver", "#B8C2CC", "door_std"),
    ("car_door_blue", "#1E5290", "door_std"), ("car_door_emerald", "#246A56", "door_std"),
    ("car_door_saffron", "#E27D24", "door_std"), ("car_door_taxi", "#1E2228", "door_taxi"),
    ("car_door_police", "#172742", "door_police"), ("car_door_ambulance", "#F4F7FA", "door_amb"),
    # Row 5 (80..95): Wheels, Bus, Rail, Furniture & Equipment Per-Face Detail Tiles
    ("car_door_bus", "#CC2C2C", "door_std"), ("car_door_train", "#A8B4C2", "door_train"),
    ("wheel_side_alloy", "#B8C4D0", "wheel_side"), ("wheel_side_steel", "#687482", "wheel_side"),
    ("wheel_side_gold", "#D6AD59", "wheel_side"), ("bookshelf_front", "#8D6034", "detail_bookshelf"),
    ("screen_ecg", "#16202A", "detail_ecg"), ("screen_atm", "#16202A", "detail_atm"),
    ("screen_pc", "#16202A", "detail_pc"), ("stove_front", "#CBD5E1", "detail_stove"),
    ("drawer_teak", "#8D562E", "detail_drawer"), ("mandir_jali", "#7A4624", "detail_mandir"),
    ("speaker_grille", "#1E242C", "detail_speaker"), ("cobble_wall", "#767B82", "cobble"),
    ("glowstone_lamp", "#F5B841", "glowstone"), ("sea_prism", "#8AE2D0", "sea_lantern"),
    # Row 6 (96..111): Hero / Weapon / Festival Detail Tiles
    ("weapon_slide_dark", "#252B34", "weapon_slide"), ("weapon_slide_chrome", "#C8D4E0", "weapon_slide"),
    ("weapon_grip_stipple", "#211E1D", "carbon"), ("weapon_vent_guard", "#2B323A", "detail_grille_black"),
    ("gun_muzzle_bore", "#14181E", "detail_muzzle"), ("medkit_cross_tile", "#DC2626", "hero_cross"),
    ("jerrycan_rib_red", "#C92A2A", "hero_jerry"), ("bills_ark_top", "#22754B", "hero_bills"),
    ("card_ark_vip", "#151B20", "hero_card"), ("festival_toran", "#F59E0B", "detail_toran"),
    ("festival_rangoli", "#E11D48", "detail_rangoli"), ("brick_sandstone", "#D8C690", "bricks"),
    ("wood_oak_v", "#B68652", "wood_v"), ("wood_teak_v", "#824D27", "wood_v"),
    ("oak_bark", "#685134", "bark"), ("birch_planks", "#C8B77C", "wood"),
]
MAT_INDEX = {m[0]: i for i, m in enumerate(MATERIALS)}


def generate_32x32_tile(name: str, hex_col: str, kind: str, idx: int = 0) -> np.ndarray:
    """Synthesize a crisp Faithful-32x-inspired 32x32 RGBA pixel-art tile."""
    if kind == "wood":
        return f32.tex_planks(hex_col, vertical=False, seed=idx + 1)
    if kind == "wood_v":
        return f32.tex_planks(hex_col, vertical=True, seed=idx + 1)
    if kind == "bark":
        return f32.tex_log_side(hex_col, birch=False, seed=idx + 1)
    if kind == "cobble":
        return f32.tex_cobble(hex_col, seed=idx + 1)
    if kind == "bricks":
        mortar = "#CFC7B8" if "brick" in name else "#565B64"
        return f32.tex_bricks(hex_col, mortar, seed=idx + 1)
    if kind == "polished":
        return f32.tex_polished(hex_col, frame=2, flecks=True, seed=idx + 1)
    if kind == "stone":
        return f32.tex_stone_rough(hex_col, seed=idx + 1)
    if kind == "dirt":
        return f32.tex_dirt_sand_gravel(hex_col, style="dirt", seed=idx + 1)
    if kind == "metal":
        return f32.tex_metal_block(hex_col, rivets=True, specular=True, seed=idx + 1)
    if kind == "metal_paint":
        return f32.tex_polished(hex_col, frame=1, flecks=False, seed=idx + 1)
    if kind == "chrome":
        return f32.tex_metal_block(hex_col, rivets=False, specular=True, seed=idx + 1)
    if kind == "tread":
        return f32.tex_tire_tread(hex_col)
    if kind == "carbon":
        return f32.tex_carbon_mesh(hex_col, mesh=False)
    if kind == "mesh":
        return f32.tex_carbon_mesh(hex_col, mesh=True)
    if kind == "glass":
        return f32.tex_glass(hex_col, "#1D2430", alpha=165 if "tint" in name else 120)
    if kind == "water":
        return f32.tex_glass(hex_col, hex_col, is_water=True)
    if kind == "fabric":
        return f32.tex_fabric(hex_col, stitch=True, seed=idx + 1)
    if kind == "leaves":
        leaf_overlay = f32.tex_leaves(hex_col, seed=idx + 1)
        backing = f32.tex_stone_rough(hex_col, contrast=0.72, seed=idx + 9)
        mask = leaf_overlay[:, :, 3] > 0
        backing[mask, :3] = leaf_overlay[mask, :3]
        backing[:, :, 3] = 255
        return backing
    if kind == "hazard":
        return f32.tex_hazard(hex_col, "#181B22")
    if kind == "plate":
        return f32.tex_license_plate()
    if kind == "glowstone":
        return f32.tex_glowstone()
    if kind == "sea_lantern":
        return f32.tex_sea_lantern()
    if kind == "headlight" or kind == "detail_headlight":
        return f32.tex_headlight()
    if kind == "taillight" or kind == "detail_taillight":
        return f32.tex_taillight()
    if kind == "lamp_blue" or kind == "lamp_amber":
        ramp = f32.make_ramp(hex_col, contrast=1.1)
        out = f32.tex_metal_block(hex_col, rivets=False, specular=False)
        out[4:28, 4:28, :3] = ramp[4]
        out[9:23, 9:23, :3] = ramp[5]
        return out
    if kind == "detail_grille_chrome":
        return f32.tex_grille(chrome_slats=True)
    if kind == "detail_grille_black":
        return f32.tex_grille(chrome_slats=False)
    if kind == "detail_windshield":
        return f32.tex_windshield()
    if kind == "door_std":
        return f32.tex_car_door(hex_col, trim="standard")
    if kind == "door_taxi":
        return f32.tex_car_door(hex_col, trim="taxi")
    if kind == "door_police":
        return f32.tex_car_door(hex_col, trim="police")
    if kind == "door_amb":
        return f32.tex_car_door(hex_col, trim="ambulance")
    if kind == "door_train":
        return f32.tex_car_door(hex_col, trim="train")
    if kind == "wheel_side":
        return f32.tex_car_wheel_hub(hex_col)
    if kind == "detail_bookshelf":
        return f32.tex_bookshelf()
    if kind == "detail_ecg":
        return f32.tex_screen_ui("ecg")
    if kind == "detail_atm":
        return f32.tex_screen_ui("atm")
    if kind == "detail_pc":
        return f32.tex_screen_ui("pc")
    if kind == "detail_stove":
        return f32.tex_appliance_front("stove")
    if kind == "detail_drawer":
        return f32.tex_appliance_front("drawer")
    if kind == "detail_mandir":
        return f32.tex_appliance_front("mandir")
    if kind == "detail_speaker":
        return f32.tex_appliance_front("speaker")
    if kind == "weapon_slide":
        out = f32.tex_metal_block(hex_col, rivets=False, specular=True)
        ramp = f32.make_ramp(hex_col, contrast=1.0)
        for rx in range(21, 29, 2):
            out[4:28, rx, :3] = ramp[0]
            out[4:28, rx + 1, :3] = ramp[4]
        return out
    if kind == "detail_muzzle":
        out = f32.tex_metal_block("#303844", rivets=False, specular=False)
        for y in range(32):
            for x in range(32):
                d = (x - 15.5) ** 2 + (y - 15.5) ** 2
                if d < 36.0:
                    out[y, x, :3] = [10, 12, 16]
                elif d < 64.0:
                    out[y, x, :3] = [165, 178, 192] if (x + y < 32) else [68, 76, 88]
        return out
    if kind == "hero_cross":
        out = f32.tex_polished("#DC2626", frame=2, flecks=False)
        out[5:27, 12:20, :3] = [248, 250, 252]
        out[12:20, 5:27, :3] = [248, 250, 252]
        out[5, 12:20, :3] = [255, 255, 255]
        out[26, 12:20, :3] = [195, 206, 220]
        return out
    if kind == "hero_jerry":
        out = f32.tex_polished("#C92A2A", frame=2, flecks=False)
        dark = f32.make_ramp("#C92A2A", contrast=1.05)
        for i in range(5, 27):
            for d in (-1, 0, 1):
                out[i, min(31, max(0, i + d)), :3] = dark[1 if d >= 0 else 4]
                out[i, min(31, max(0, 31 - i + d)), :3] = dark[1 if d >= 0 else 4]
        return out
    if kind == "hero_bills":
        out = f32.tex_fabric("#22754B", stitch=True)
        gold = f32.make_ramp("#D6AD59", contrast=1.0)
        out[4:28, 12:20, :3] = gold[3]
        out[4:28, 12, :3] = gold[5]
        out[4:28, 19, :3] = gold[1]
        out[11:21, 13:19, :3] = gold[5]
        return out
    if kind == "hero_card":
        out = f32.tex_polished("#151B20", frame=1, flecks=False)
        gold = f32.make_ramp("#D6AD59", contrast=1.0)
        out[11:19, 5:13, :3] = gold[4]
        out[13:17, 7:11, :3] = gold[1]
        out[5:8, 5:26, :3] = gold[4]
        out[23:25, 5:21, :3] = [180, 194, 210]
        return out
    if kind == "detail_toran":
        out = f32.tex_leaves("#F59E0B", seed=7)
        for y in range(22, 32):
            for x in range(32):
                if (x + y) % 4 == 0:
                    out[y, x, :3] = [34, 139, 64]
        return out
    if kind == "detail_rangoli":
        out = f32.tex_polished("#5E1B42", frame=2, flecks=False)
        cols = [(245, 184, 0), (236, 72, 153), (34, 211, 238), (248, 250, 252)]
        for y in range(32):
            for x in range(32):
                d = int(abs(x - 15.5) + abs(y - 15.5))
                if d < 14 and d % 3 == 0:
                    out[y, x, :3] = cols[(d // 3) % len(cols)]
        return out
    return f32.tex_polished(hex_col, frame=1, flecks=False, seed=idx + 1)


def build_shared_atlas() -> np.ndarray:
    """Build 148+ individual Faithful 32x32 PNGs + pack all 112 atlas slots into 512x512 gtm_master_atlas_32x.png."""
    TEX_32_DIR.mkdir(parents=True, exist_ok=True)
    ATLAS_PATH.parent.mkdir(parents=True, exist_ok=True)
    arr = np.zeros((ATLAS_SIZE, ATLAS_SIZE, 4), dtype=np.uint8)

    for idx, (name, hex_col, kind) in enumerate(MATERIALS):
        tile = generate_32x32_tile(name, hex_col, kind, idx)
        Image.fromarray(tile, mode="RGBA").save(TEX_32_DIR / f"{name}.png", optimize=True)
        r0, c0 = idx // 16, idx % 16
        arr[r0 * TILE_SIZE:(r0 + 1) * TILE_SIZE, c0 * TILE_SIZE:(c0 + 1) * TILE_SIZE] = tile

    Image.fromarray(arr, mode="RGBA").save(ATLAS_PATH, format="PNG", optimize=True)

    # Also build all 36 dedicated named 32x32 PNG textures referenced by the user's Hero 3D JSON models
    hero_tex_specs = [
        ("medkit_olive_nylon", "#2D4D3B", "fabric"), ("medkit_dark_trim", "#1A2026", "stone"),
        ("medkit_webbing", "#383E46", "fabric"), ("medkit_zipper", "#94A3B8", "chrome"),
        ("medkit_patch", "#F1F5F9", "polished"), ("medkit_red_cross", "#DC2626", "hero_cross"),
        ("medkit_hardware", "#CBD5E1", "chrome"),
        ("gun_pistol_slide", "#323A45", "weapon_slide"), ("gun_pistol_frame", "#1A1E24", "polished"),
        ("gun_pistol_grip", "#242120", "carbon"), ("gun_steel", "#7E8B9B", "chrome"),
        ("gun_rifle_receiver", "#22272E", "metal"), ("gun_rifle_handguard", "#2D333B", "carbon"),
        ("gun_rifle_mag", "#3E4650", "weapon_slide"), ("gun_rifle_stock", "#1B1E23", "polished"),
        ("shotgun_wood", "#6E3A1C", "wood"), ("shotgun_receiver", "#282E36", "metal"),
        ("fob_case", "#1A1E26", "polished"), ("fob_buttons", "#38BDF8", "detail_atm"),
        ("can_red", "#C92A2A", "hero_jerry"), ("can_spout", "#F59E0B", "polished"),
        ("wood_ash", "#C99A63", "wood_v"), ("grip_tape", "#1E2024", "carbon"), ("brand_stamp", "#D6AD59", "chrome"),
        ("bills_side", "#E2DFC7", "fabric"), ("bills_top", "#22754B", "hero_bills"), ("bills_band", "#D6AD59", "chrome"),
        ("card_front", "#151B20", "hero_card"), ("card_back", "#1E262E", "polished"), ("chip", "#D6AD59", "chrome"),
        ("leather", "#7C421C", "fabric"), ("gold", "#D6AD59", "chrome"), ("silver", "#D8E2EC", "chrome"),
        ("smartphone_chassis", "#1E242B", "metal"), ("smartphone_screen", "#162A4C", "detail_pc"),
        ("smartphone_camera", "#0F172A", "detail_muzzle")
    ]
    for idx_h, (hname, hcol, hkind) in enumerate(hero_tex_specs):
        htile = generate_32x32_tile(hname, hcol, hkind, 120 + idx_h)
        Image.fromarray(htile, mode="RGBA").save(TEX_32_DIR / f"{hname}.png", optimize=True)

    return arr


ATLAS_ARR = None


def get_atlas() -> np.ndarray:
    global ATLAS_ARR
    if ATLAS_ARR is None:
        ATLAS_ARR = build_shared_atlas()
    return ATLAS_ARR


class PartBuilder:
    """Ergonomic multi-part voxel geometry builder with PER-FACE Faithful 32x UV mapping."""

    def __init__(self):
        self.bones = {"root": {"pivot": [0, 0, 0], "parent": None, "parts": []}}

    def add_bone(self, name: str, pivot=(0, 0, 0), parent="root"):
        if name not in self.bones:
            self.bones[name] = {"pivot": [round(float(v), 3) for v in pivot], "parent": parent, "parts": []}

    def box(self, x, y, z, w, h, d, mat="steel_dark", bone="root", rot=None, pivot=None, name=None, face_mats=None):
        if w <= 0 or h <= 0 or d <= 0:
            return
        if bone not in self.bones:
            self.add_bone(bone, pivot or [x + w / 2, y + h / 2, z + d / 2])
        self.bones[bone]["parts"].append({
            "origin": [round(float(x), 3), round(float(y), 3), round(float(z), 3)],
            "size": [round(float(w), 3), round(float(h), 3), round(float(d), 3)],
            "mat": mat,
            "face_mats": dict(face_mats) if face_mats else {},
            "rot": list(rot) if rot else None,
            "pivot": list(pivot) if pivot else None,
            "name": name or f"part_{len(self.bones[bone]['parts'])}"
        })

    def cbox(self, cx, y, cz, w, h, d, mat="steel_dark", bone="root", rot=None, pivot=None, name=None, face_mats=None):
        self.box(cx - w / 2.0, y, cz - d / 2.0, w, h, d, mat=mat, bone=bone, rot=rot, pivot=pivot, name=name, face_mats=face_mats)

    def wheel(self, cx, y_center, cz, radius=4.5, width=2.8, tire_mat="rubber_tire", rim_mat="alloy_rim", bone="root"):
        """Crisp octagon-stepped tire + Faithful alloy spoke side UVs on east/west faces."""
        r = radius
        t = r * 0.48
        side_hub = "wheel_side_gold" if rim_mat in ("brass", "paint_gold") else ("wheel_side_steel" if rim_mat == "steel_light" else "wheel_side_alloy")
        f_tire = {"east": side_hub, "west": side_hub}
        self.cbox(cx, y_center - r, cz, width, r * 2, r * 1.18, mat=tire_mat, bone=bone, name="tire_v", face_mats=f_tire)
        self.cbox(cx, y_center - r * 0.59, cz, width, r * 1.18, r * 2, mat=tire_mat, bone=bone, name="tire_h", face_mats=f_tire)
        self.cbox(cx, y_center - r * 0.86, cz, width * 0.96, r * 1.72, r * 1.68, mat=tire_mat, bone=bone, name="tire_d", face_mats=f_tire)
        self.cbox(cx, y_center - t, cz, width + 0.35, t * 2, t * 2, mat=rim_mat, bone=bone, name="rim", face_mats=f_tire)

    def export_bedrock_geo(self, geo_id: str, dest: Path) -> int:
        dest.parent.mkdir(parents=True, exist_ok=True)
        out_bones = []
        total_cubes = 0
        min_pt = [1e9, 1e9, 1e9]
        max_pt = [-1e9, -1e9, -1e9]

        for bname, bdata in self.bones.items():
            cubes = []
            for p in bdata["parts"]:
                ox, oy, oz = p["origin"]
                sw, sh, sd = p["size"]
                min_pt = [min(min_pt[0], ox), min(min_pt[1], oy), min(min_pt[2], oz)]
                max_pt = [max(max_pt[0], ox + sw), max(max_pt[1], oy + sh), max(max_pt[2], oz + sd)]

                uv_dict = {}
                for f in ("north", "south", "east", "west", "up", "down"):
                    fmat = p["face_mats"].get(f, p["mat"])
                    mi = MAT_INDEX.get(fmat, 0)
                    u0, v0 = (mi % 16) * TILE_SIZE, (mi // 16) * TILE_SIZE
                    uv_dict[f] = {"uv": [u0 + 0.5, v0 + 0.5], "uv_size": [TILE_SIZE - 1, TILE_SIZE - 1]}

                c = {"origin": [ox, oy, oz], "size": [sw, sh, sd], "uv": uv_dict}
                if p["rot"]:
                    c["rotation"] = p["rot"]
                    c["pivot"] = p["pivot"] or [ox + sw / 2, oy + sh / 2, oz + sd / 2]
                cubes.append(c)
                total_cubes += 1

            bone_obj = {"name": bname, "pivot": bdata["pivot"]}
            if bdata["parent"]:
                bone_obj["parent"] = bdata["parent"]
            if cubes:
                bone_obj["cubes"] = cubes
            out_bones.append(bone_obj)

        span_x = max(1.0, (max_pt[0] - min_pt[0]) / 16.0)
        span_y = max(1.0, (max_pt[1] - min_pt[1]) / 16.0)
        span_z = max(1.0, (max_pt[2] - min_pt[2]) / 16.0)
        geo = {
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {
                    "identifier": geo_id,
                    "texture_width": ATLAS_SIZE,
                    "texture_height": ATLAS_SIZE,
                    "visible_bounds_width": round(max(span_x, span_z) + 1.0, 2),
                    "visible_bounds_height": round(span_y + 1.0, 2),
                    "visible_bounds_offset": [0.0, round(span_y * 0.5, 2), 0.0]
                },
                "bones": out_bones
            }]
        }
        dest.write_text(json.dumps(geo, indent=2) + "\n", encoding="utf-8")
        return total_cubes

    def export_java_item(self, dest: Path, display_preset: str = "standard"):
        dest.parent.mkdir(parents=True, exist_ok=True)
        all_parts = [p for b in self.bones.values() for p in b["parts"]]
        if not all_parts:
            return
        xs = [p["origin"][0] for p in all_parts] + [p["origin"][0] + p["size"][0] for p in all_parts]
        ys = [p["origin"][1] for p in all_parts] + [p["origin"][1] + p["size"][1] for p in all_parts]
        zs = [p["origin"][2] for p in all_parts] + [p["origin"][2] + p["size"][2] for p in all_parts]
        cx, cy, cz = (min(xs) + max(xs)) * 0.5, min(ys), (min(zs) + max(zs)) * 0.5
        max_dim = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 1.0)
        scale = min(1.0, 32.0 / max_dim)

        elements = []
        for p in all_parts:
            ox, oy, oz = p["origin"]
            sw, sh, sd = p["size"]
            fx, fy, fz = round(8.0 + (ox - cx) * scale, 3), round((oy - cy) * scale, 3), round(8.0 + (oz - cz) * scale, 3)
            tx, ty, tz = round(8.0 + (ox + sw - cx) * scale, 3), round((oy + sh - cy) * scale, 3), round(8.0 + (oz + sd - cz) * scale, 3)
            faces = {}
            for f in ("north", "south", "east", "west", "up", "down"):
                fmat = p["face_mats"].get(f, p["mat"])
                mi = MAT_INDEX.get(fmat, 0)
                u0, v0 = (mi % 16) * 1.0, (mi // 16) * 1.0
                faces[f] = {"uv": [u0 + 0.02, v0 + 0.02, u0 + 0.98, v0 + 0.98], "texture": "#atlas"}
            el = {"name": p["name"], "from": [fx, fy, fz], "to": [tx, ty, tz], "faces": faces}
            if p["rot"]:
                rx, ry, rz = p["rot"]
                mabs = max(abs(rx), abs(ry), abs(rz))
                if mabs > 0.1:
                    axis = "x" if abs(rx) == mabs else ("y" if abs(ry) == mabs else "z")
                    ang = max(-45.0, min(45.0, rx if axis == "x" else (ry if axis == "y" else rz)))
                    px, py, pz = p["pivot"] or [ox + sw / 2, oy + sh / 2, oz + sd / 2]
                    el["rotation"] = {
                        "angle": round(ang, 1), "axis": axis,
                        "origin": [round(8.0 + (px - cx) * scale, 2), round((py - cy) * scale, 2), round(8.0 + (pz - cz) * scale, 2)]
                    }
            elements.append(el)

        model = {
            "credit": "GTM Indraprastha - Faithful 32x Studio 3D Asset",
            "parent": "minecraft:block/block",
            "textures": {"atlas": ATLAS_RESOURCE, "particle": "#atlas"},
            "elements": elements,
            "display": {
                "gui": {"rotation": [28, 225, 0], "translation": [0, 0.5, 0], "scale": [0.78, 0.78, 0.78]},
                "ground": {"translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
                "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.45, 0.45, 0.45]},
                "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.38, 0.38, 0.38]}
            }
        }
        dest.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")

    def render_icon(self, dest: Path, size: int = 128, yaw_deg: float = -38.0, pitch_deg: float = 24.0, grid: int = 64):
        """
        Faithful-32x Pixel-Locked Z-Buffered Isometric Sprite Renderer:
        - Renders onto an integer `grid x grid` pixel canvas (64x64 default = 2x Faithful pixel density).
        - Outward-facing CCW cube face culling + per-pixel Z-depth + per-face Faithful 32x UV texture sampling!
        - Quantized stepped top-left lighting with subtle warm/cool Faithful hue shift (no CGI haze!).
        - Crisp 1px dark hue-shifted outline around the foreground silhouette, ZERO blurry Gaussian shadow!
        - Upscaled cleanly using NEAREST neighbor so every pixel stays razor-sharp!
        """
        dest.parent.mkdir(parents=True, exist_ok=True)
        atlas = get_atlas()
        all_parts = [p for b in self.bones.values() for p in b["parts"]]
        if not all_parts:
            return

        yaw = math.radians(yaw_deg)
        pitch = math.radians(pitch_deg)
        cy, sy = math.cos(yaw), math.sin(yaw)
        cp, sp = math.cos(pitch), math.sin(pitch)

        def rotate_pt(pt):
            x, y, z = pt
            x1 = x * cy - z * sy
            z1 = x * sy + z * cy
            y2 = y * cp - z1 * sp
            z2 = y * sp + z1 * cp
            return np.array([x1, y2, z2], dtype=np.float32)

        world_corners = []
        for p in all_parts:
            ox, oy, oz = p["origin"]
            sw, sh, sd = p["size"]
            corners = [
                (ox, oy, oz), (ox + sw, oy, oz), (ox + sw, oy + sh, oz), (ox, oy + sh, oz),
                (ox, oy, oz + sd), (ox + sw, oy, oz + sd), (ox + sw, oy + sh, oz + sd), (ox, oy + sh, oz + sd)
            ]
            if p["rot"]:
                rx, ry, rz = [math.radians(a) for a in p["rot"]]
                px, py, pz = p["pivot"] or [ox + sw / 2, oy + sh / 2, oz + sd / 2]
                cxr, sxr = math.cos(rx), math.sin(rx)
                cyr, syr = math.cos(ry), math.sin(ry)
                czr, szr = math.cos(rz), math.sin(rz)
                rc = []
                for x, y, z in corners:
                    dx, dy, dz = x - px, y - py, z - pz
                    dy, dz = dy * cxr - dz * sxr, dy * sxr + dz * cxr
                    dx, dz = dx * cyr + dz * syr, -dx * syr + dz * cyr
                    dx, dy = dx * czr - dy * szr, dx * szr + dy * czr
                    rc.append((px + dx, py + dy, pz + dz))
                corners = rc
            world_corners.append((p["mat"], p["face_mats"], [rotate_pt(c) for c in corners]))

        all_pts = np.array([c for _, _, cs in world_corners for c in cs])
        minx, miny = all_pts[:, 0].min(), all_pts[:, 1].min()
        maxx, maxy = all_pts[:, 0].max(), all_pts[:, 1].max()

        W = grid
        span = max(maxx - minx, maxy - miny, 1.0)
        scale = (W * 0.80) / span
        mid_x, mid_y = (minx + maxx) * 0.5, (miny + maxy) * 0.5

        L = np.array([-0.46, 0.78, 0.42], dtype=np.float32)
        L /= np.linalg.norm(L)

        FACE_META = [
            ("north", (0, 3, 2, 1)),
            ("south", (4, 5, 6, 7)),
            ("west", (4, 7, 3, 0)),
            ("east", (1, 2, 6, 5)),
            ("up", (3, 7, 6, 2)),
            ("down", (0, 1, 5, 4)),
        ]

        zbuf = np.full((W, W), -1e9, dtype=np.float32)
        cbuf = np.zeros((W, W, 4), dtype=np.uint8)

        for mat_name, f_mats, cs in world_corners:
            for fname, idxs in FACE_META:
                v0, v1, v2, v3 = cs[idxs[0]], cs[idxs[1]], cs[idxs[2]], cs[idxs[3]]
                normal = np.cross(v1 - v0, v3 - v0)
                nlen = np.linalg.norm(normal)
                if nlen < 1e-6:
                    continue
                normal /= nlen
                if normal[2] <= 0.01:
                    continue

                fmat = f_mats.get(fname, mat_name)
                mi = MAT_INDEX.get(fmat, 0)
                _, _, mkind = MATERIALS[mi]
                tx0, ty0 = (mi % 16) * TILE_SIZE, (mi // 16) * TILE_SIZE
                tex_patch = atlas[ty0:ty0 + TILE_SIZE, tx0:tx0 + TILE_SIZE].astype(np.float32)

                pts3 = np.stack([v0, v1, v2, v3])
                sx = W * 0.5 + (pts3[:, 0] - mid_x) * scale
                sy = W * 0.50 - (pts3[:, 1] - mid_y) * scale
                sz = pts3[:, 2]

                bx0, bx1 = max(1, int(math.floor(sx.min()))), min(W - 1, int(math.ceil(sx.max())) + 1)
                by0, by1 = max(1, int(math.floor(sy.min()))), min(W - 1, int(math.ceil(sy.max())) + 1)
                if bx1 <= bx0 or by1 <= by0:
                    continue

                ux, uy = sx[1] - sx[0], sy[1] - sy[0]
                vx, vy = sx[3] - sx[0], sy[3] - sy[0]
                det = ux * vy - uy * vx
                if abs(det) < 1e-5:
                    continue
                inv_det = 1.0 / det

                yy, xx = np.mgrid[by0:by1, bx0:bx1]
                dx = xx.astype(np.float32) + 0.5 - sx[0]
                dy = yy.astype(np.float32) + 0.5 - sy[0]
                u = (dx * vy - dy * vx) * inv_det
                v = (ux * dy - uy * dx) * inv_det

                mask = (u >= -0.015) & (u <= 1.015) & (v >= -0.015) & (v <= 1.015)
                if not mask.any():
                    continue

                z_val = sz[0] + u * (sz[1] - sz[0]) + v * (sz[3] - sz[0])
                hit = mask & (z_val > zbuf[by0:by1, bx0:bx1])
                if not hit.any():
                    continue

                tu = np.clip((u[hit] * (TILE_SIZE - 0.01)).astype(np.int32), 0, TILE_SIZE - 1)
                tv = np.clip((v[hit] * (TILE_SIZE - 0.01)).astype(np.int32), 0, TILE_SIZE - 1)
                sampled_rgba = tex_patch[tv, tu]

                # Quantized Faithful directional lighting (warm top face, crisp neutral front, cool side)
                ndotl = max(0.0, float(np.dot(normal, L)))
                if ndotl > 0.72:
                    shade = 1.12
                    tint = np.array([10.0, 8.0, 0.0], dtype=np.float32)
                elif ndotl > 0.42:
                    shade = 0.96
                    tint = np.array([0.0, 0.0, 0.0], dtype=np.float32)
                else:
                    shade = 0.76
                    tint = np.array([-6.0, -4.0, 10.0], dtype=np.float32)

                if mkind in ("detail_headlight", "headlight", "lamp_blue", "lamp_amber", "glowstone", "sea_lantern", "detail_ecg", "detail_atm", "detail_pc"):
                    lit_rgb = np.maximum(sampled_rgba[:, :3] * 1.04, sampled_rgba[:, :3] * shade)
                else:
                    lit_rgb = sampled_rgba[:, :3] * shade + tint

                lit_rgb = np.clip(lit_rgb, 0, 255).astype(np.uint8)
                lit_a = np.where(sampled_rgba[:, 3] >= 120, 255, 0).astype(np.uint8)

                sub_z = zbuf[by0:by1, bx0:bx1]
                sub_c = cbuf[by0:by1, bx0:bx1]
                opaque_hit = hit.copy()
                sub_z[opaque_hit] = z_val[opaque_hit]
                sub_c[opaque_hit, :3] = lit_rgb
                sub_c[opaque_hit, 3] = lit_a

        # Crisp 1-pixel dark Faithful outline (top/bottom/left/right neighbor check, ZERO blur!)
        alpha = cbuf[:, :, 3] > 0
        padded = np.pad(alpha, 1, mode="constant", constant_values=False)
        dilated4 = padded[:-2, 1:-1] | padded[2:, 1:-1] | padded[1:-1, :-2] | padded[1:-1, 2:]
        outline_mask = dilated4 & (~alpha)

        final_grid = cbuf.copy()
        final_grid[outline_mask] = [14, 16, 26, 255]  # Crisp cool midnight Faithful outline

        out_im = Image.fromarray(final_grid, mode="RGBA")
        if out_im.size != (size, size):
            out_im = out_im.resize((size, size), Image.Resampling.NEAREST)
        out_im.save(dest, format="PNG", optimize=True)


class PixelSprite:
    """
    Hand-crafted Faithful-32x Pixel-Art Canvas (32x32 or 64x64 native integer grid).
    Supports stepped hue-shifted ramps, top-left directional speculars, 1px outline pass,
    and razor-sharp NEAREST integer upscaling!
    """

    def __init__(self, w: int = 32, h: int = 32):
        self.w = w
        self.h = h
        self.buf = np.zeros((h, w, 4), dtype=np.uint8)

    def px(self, x: int, y: int, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            if isinstance(col, str):
                col = (*ImageColor.getrgb(col), 255)
            elif len(col) == 3:
                col = (col[0], col[1], col[2], 255)
            self.buf[y, x] = col

    def rect(self, x: int, y: int, rw: int, rh: int, col):
        for py in range(y, y + rh):
            for px_i in range(x, x + rw):
                self.px(px_i, py, col)

    def disc(self, cx: float, cy: float, r: float, col):
        for py in range(int(cy - r) - 1, int(cy + r) + 2):
            for px_i in range(int(cx - r) - 1, int(cx + r) + 2):
                if (px_i - cx) ** 2 + (py - cy) ** 2 <= r * r:
                    self.px(px_i, py, col)

    def line(self, x0: int, y0: int, x1: int, y1: int, col, thick: int = 1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            t = i / steps
            px_i = int(round(x0 + (x1 - x0) * t))
            py_i = int(round(y0 + (y1 - y0) * t))
            if thick <= 1:
                self.px(px_i, py_i, col)
            else:
                self.rect(px_i - thick // 2, py_i - thick // 2, thick, thick, col)

    def shade_bevel(self, ramp_hex: str, x0: int, y0: int, rw: int, rh: int, corner_cut: int = 1):
        """Draw a shaded faceted Faithful pixel block with warm top-left hi & cool bottom-right shadow."""
        ramp = f32.make_ramp(ramp_hex, contrast=1.0)
        for py in range(y0, y0 + rh):
            for px_i in range(x0, x0 + rw):
                lx, ly = px_i - x0, py - y0
                if corner_cut > 0 and ((lx < corner_cut and ly < corner_cut) or (lx >= rw - corner_cut and ly < corner_cut)
                                       or (lx < corner_cut and ly >= rh - corner_cut) or (lx >= rw - corner_cut and ly >= rh - corner_cut)):
                    continue
                if ly == 0 or lx == 0:
                    c = ramp[5] if (lx <= 2 and ly <= 2) else ramp[4]
                elif ly == rh - 1 or lx == rw - 1:
                    c = ramp[1]
                else:
                    c = ramp[3]
                self.px(px_i, py, tuple(int(v) for v in c))

    def add_outline(self, col=(14, 16, 28, 255), diagonal: bool = False):
        """Add classic 1px dark hue-shifted Faithful outline around all painted pixels."""
        if isinstance(col, str):
            col = (*ImageColor.getrgb(col), 255)
        alpha = self.buf[:, :, 3] > 0
        padded = np.pad(alpha, 1, mode="constant", constant_values=False)
        nbr = padded[:-2, 1:-1] | padded[2:, 1:-1] | padded[1:-1, :-2] | padded[1:-1, 2:]
        if diagonal:
            nbr |= padded[:-2, :-2] | padded[:-2, 2:] | padded[2:, :-2] | padded[2:, 2:]
        mask = nbr & (~alpha)
        self.buf[mask] = col

    def to_image(self, target_size: int = None) -> Image.Image:
        im = Image.fromarray(self.buf, mode="RGBA")
        if target_size and target_size != self.w:
            im = im.resize((target_size, target_size), Image.Resampling.NEAREST)
        return im

    def save(self, dest: Path, target_size: int = None):
        dest.parent.mkdir(parents=True, exist_ok=True)
        self.to_image(target_size=target_size).save(dest, format="PNG", optimize=True)

