#!/usr/bin/env python3
"""
True Per-Pixel Z-Buffered 3D Studio Engine & 32x32 Texture Library for GTM Revision 4.

Fixes & Upgrades:
1. Outward-winding CCW cube face topology (zero culled front faces / inside-out meshes).
2. True Per-Pixel Depth Buffer (Z-Buffer) with Barycentric/Affine UV Texture Sampling
   at 256x256 supersampled resolution -> 128x128 RGBA icons.
3. True 32x32 RGBA pixel-art material textures saved both individually in
   creative/source/textures/32x32/<name>.png AND packed into a 256x256 (8x8 x 32px)
   master atlas for dual Bedrock (.geo.json) + Java (.json) models.
4. Generates all dedicated 32x32 named textures referenced by the user's 11 hero JSON models
   (medkit, pistol, rifle, shotgun, smg, police badge, atm card, cash bundle, key fob, jerrycan, bat).
"""
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
TEX_32_DIR = CREATIVE / "source" / "textures" / "32x32"
ATLAS_PATH = CREATIVE / "source" / "textures" / "gtm_master_atlas_32x.png"

# 64 Rich 32x32 Materials (8x8 grid inside 256x256 atlas)
MATERIALS = [
    # Row 0: Metals, Chassis & Industrial
    ("steel_dark", "#252B33", "metal"), ("steel_light", "#6E7A8A", "metal"), ("chrome", "#DCE6F2", "chrome"), ("aluminum", "#AAB7C6", "metal"),
    ("graphite", "#151B20", "matte"), ("rubber_tire", "#181A1F", "tread"), ("alloy_rim", "#A8B5C4", "chrome"), ("carbon", "#1D2228", "carbon"),
    # Row 1: Automotive & Fleet Paints
    ("paint_red", "#B8292F", "gloss"), ("paint_white", "#EDEFF2", "gloss"), ("paint_black", "#1B1F24", "gloss"), ("paint_silver", "#B2BCC7", "gloss"),
    ("paint_blue", "#1D4E89", "gloss"), ("paint_emerald", "#236653", "gloss"), ("paint_saffron", "#E07A22", "gloss"), ("paint_gold", "#D6AD59", "gloss"),
    # Row 2: Mumbai Taxi / Auto / Emergency / Transit
    ("taxi_yellow", "#F5B800", "gloss"), ("auto_green", "#196942", "gloss"), ("maroon_rail", "#7A2029", "gloss"), ("terracotta", "#AD5637", "stone"),
    ("police_khaki", "#C2A673", "fabric"), ("police_navy", "#14243D", "gloss"), ("fire_red", "#C92A2A", "gloss"), ("ambulance_white", "#F5F7FA", "gloss"),
    # Row 3: Glass, Lights, Grilles & UI Plates
    ("glass_tint", "#2A4A5E", "glass"), ("glass_clear", "#7ACAE0", "glass"), ("headlight", "#FFF3C4", "emissive"), ("taillight", "#E02424", "emissive"),
    ("beacon_blue", "#2563EB", "emissive"), ("beacon_amber", "#F59E0B", "emissive"), ("grille_mesh", "#22262C", "mesh"), ("license_plate", "#E8EAED", "plate"),
    # Row 4: Woods, Stone & Traditional Indian
    ("wood_teak", "#7A4624", "wood"), ("wood_sheesham", "#542C16", "wood"), ("wood_oak", "#B68652", "wood"), ("bamboo", "#C4A35A", "wood"),
    ("sandstone", "#D2B997", "stone"), ("marble", "#EAE5DC", "marble"), ("granite", "#4B5056", "stone"), ("brick_clay", "#9E472D", "brick"),
    # Row 5: Interior Fabrics & Cushion
    ("fabric_beige", "#D6C5A9", "fabric"), ("fabric_emerald", "#1E5646", "fabric"), ("fabric_navy", "#243447", "fabric"), ("fabric_maroon", "#692332", "fabric"),
    ("leather_tan", "#8B4E24", "leather"), ("leather_black", "#212126", "leather"), ("linen_white", "#F0ECE1", "fabric"), ("mattress_blue", "#789BB2", "fabric"),
    # Row 6: Ornament, Festival & Brass
    ("brass", "#D69E2E", "chrome"), ("copper", "#B86B43", "chrome"), ("marigold", "#F59E0B", "organic"), ("crimson_silk", "#9F1239", "fabric"),
    ("neon_cyan", "#22D3EE", "emissive"), ("neon_magenta", "#E879F9", "emissive"), ("holi_pink", "#EC4899", "organic"), ("leaf_green", "#2F855A", "organic"),
    # Row 7: Hazard, Medical, Kitchen & Prop Finishes
    ("hazard_yellow", "#EAB308", "hazard"), ("medical_red", "#DC2626", "gloss"), ("medical_teal", "#0D9488", "gloss"), ("stainless", "#CBD5E1", "chrome"),
    ("earth_soil", "#6B4E35", "stone"), ("water_teal", "#1D7898", "glass"), ("gold_filigree", "#E8C87E", "chrome"), ("lotus_dark", "#3B1C32", "gloss")
]
MAT_INDEX = {m[0]: i for i, m in enumerate(MATERIALS)}


def generate_32x32_tile(name: str, hex_col: str, kind: str, idx: int = 0) -> np.ndarray:
    """Synthesize a genuine high-detail 32x32 RGBA pixel-art texture."""
    base = np.array(ImageColor.getrgb(hex_col), dtype=np.float32)
    tile = np.zeros((32, 32, 4), dtype=np.float32)
    tile[:, :, :3] = base
    tile[:, :, 3] = 255.0

    yy, xx = np.mgrid[0:32, 0:32]
    rng = np.random.default_rng(1000 + idx * 37)
    noise = rng.uniform(-5.0, 5.0, (32, 32))

    if kind == "metal":
        streak = np.sin(yy * 0.9 + noise * 0.15) * 6.0 + noise * 0.7
        tile[:, :, :3] += streak[:, :, None]
        # Rivet studs near corners
        for rx, ry in ((2, 2), (29, 2), (2, 29), (29, 29)):
            tile[ry:ry + 2, rx:rx + 2, :3] *= 1.3
    elif kind == "chrome":
        diag = np.sin((xx + yy) * 0.25) * 28.0 + noise * 0.4
        tile[:, :, :3] += diag[:, :, None]
    elif kind == "tread":
        # Chevron tire tread blocks
        chev = ((np.abs(xx - 15.5) + yy * 1.4).astype(int) % 6) < 2
        tile[chev, :3] *= 0.58
        tile[~chev, :3] += noise[~chev, None] * 0.6
    elif kind == "carbon":
        twill = (((xx // 2) + (yy // 2)) % 2 == 0)
        tile[twill, :3] *= 1.28
        tile[~twill, :3] *= 0.78
    elif kind == "glass":
        sheen = ((30 - xx + yy) >= 8) & ((30 - xx + yy) <= 13)
        sheen2 = ((30 - xx + yy) >= 16) & ((30 - xx + yy) <= 18)
        tile[sheen, :3] += 65.0
        tile[sheen2, :3] += 38.0
        tile[:, :, 3] = 225.0
    elif kind == "emissive":
        dist = np.sqrt((xx - 15.5) ** 2 + (yy - 15.5) ** 2)
        tile[:, :, :3] += np.clip((1.0 - dist / 18.0) * 65.0, 0, 80)[:, :, None]
    elif kind == "mesh":
        mesh = ((xx % 3 == 0) | (yy % 3 == 0))
        tile[mesh, :3] *= 0.42
    elif kind == "wood":
        plank_seam = (yy % 8 == 0)
        grain = np.sin(xx * 0.35 + np.sin(yy * 0.5 + (yy // 8) * 1.7) * 2.5) * 14.0
        tile[:, :, :3] += grain[:, :, None] + noise[:, :, None] * 0.5
        tile[plank_seam, :3] *= 0.62
        tile[(yy % 8 == 1), :3] *= 1.12
    elif kind == "brick":
        row = yy // 8
        offset = (row % 2) * 8
        mortar = (yy % 8 == 0) | (((xx + offset) % 16) == 0)
        tile[:, :, :3] += noise[:, :, None] * 1.4
        tile[mortar, :3] = np.array([185, 178, 168], dtype=np.float32)
    elif kind == "stone" or kind == "marble":
        blotch = np.sin(xx * 0.35 + yy * 0.25) * 8.0 + noise * 1.3
        tile[:, :, :3] += blotch[:, :, None]
        if kind == "marble":
            vein = np.abs(xx - yy * 0.8 + np.sin(xx * 0.35) * 3.5) < 1.3
            tile[vein, :3] *= 0.78
    elif kind == "hazard":
        stripe = (((xx + yy) // 6) % 2 == 0)
        tile[stripe, :3] = np.array([24, 26, 30], dtype=np.float32)
    elif kind == "fabric" or kind == "leather":
        weave = np.sin(xx * 1.4) * np.sin(yy * 1.4) * 7.0 + noise * 0.7
        tile[:, :, :3] += weave[:, :, None]
        # Stitched seam border
        tile[2, 2:30:3, :3] *= 1.25
        tile[29, 2:30:3, :3] *= 1.25
    elif kind == "plate":
        tile[5:27, 2:30, :3] = np.array([248, 248, 250])
        tile[10:22, 6:26, :3] = np.array([28, 36, 48])
    elif kind == "organic":
        petal = np.sin(xx * 0.6) * np.cos(yy * 0.6) * 18.0 + noise * 1.2
        tile[:, :, :3] += petal[:, :, None]
    else:
        tile[:, :, :3] += noise[:, :, None] * 0.7

    # Crisp 1px top/left highlight + bottom/right bevel so every 32x32 surface pops in 3D
    tile[0, :, :3] += 12.0
    tile[:, 0, :3] += 9.0
    tile[31, :, :3] -= 15.0
    tile[:, 31, :3] -= 12.0
    return np.clip(tile, 0, 255).astype(np.uint8)


def build_shared_atlas() -> np.ndarray:
    """Build 64 individual 32x32 PNG textures + pack into 256x256 master atlas + create User Hero 32x32 textures."""
    TEX_32_DIR.mkdir(parents=True, exist_ok=True)
    ATLAS_PATH.parent.mkdir(parents=True, exist_ok=True)
    arr = np.zeros((256, 256, 4), dtype=np.uint8)

    for idx, (name, hex_col, kind) in enumerate(MATERIALS):
        tile = generate_32x32_tile(name, hex_col, kind, idx)
        Image.fromarray(tile, mode="RGBA").save(TEX_32_DIR / f"{name}.png", optimize=True)
        r0, c0 = idx // 8, idx % 8
        arr[r0 * 32:(r0 + 1) * 32, c0 * 32:(c0 + 1) * 32] = tile

    Image.fromarray(arr, mode="RGBA").save(ATLAS_PATH, format="PNG", optimize=True)

    # Also build all dedicated named 32x32 PNG textures referenced by the user's uploaded JSONs!
    hero_tex_specs = [
        ("medkit_olive_nylon", "#2B4A38", "fabric"), ("medkit_dark_trim", "#1A2026", "matte"),
        ("medkit_webbing", "#383E46", "fabric"), ("medkit_zipper", "#94A3B8", "chrome"),
        ("medkit_patch", "#F1F5F9", "fabric"), ("medkit_red_cross", "#DC2626", "gloss"),
        ("medkit_hardware", "#CBD5E1", "chrome"),
        ("gun_pistol_slide", "#323A45", "metal"), ("gun_pistol_frame", "#1A1E24", "matte"),
        ("gun_pistol_grip", "#242120", "leather"), ("gun_steel", "#7E8B9B", "chrome"),
        ("gun_rifle_receiver", "#22272E", "metal"), ("gun_rifle_handguard", "#2D333B", "carbon"),
        ("gun_rifle_mag", "#3E4650", "metal"), ("gun_rifle_stock", "#1B1E23", "matte"),
        ("shotgun_wood", "#6E3A1C", "wood"), ("shotgun_receiver", "#282E36", "metal"),
        ("fob_case", "#1A1E26", "matte"), ("fob_buttons", "#38BDF8", "emissive"),
        ("can_red", "#C92A2A", "gloss"), ("can_spout", "#F59E0B", "matte"),
        ("wood_ash", "#C99A63", "wood"), ("grip_tape", "#1E2024", "fabric"), ("brand_stamp", "#D6AD59", "chrome"),
        ("bills_side", "#E2DFC7", "plate"), ("bills_top", "#22754B", "fabric"), ("bills_band", "#D6AD59", "matte"),
        ("card_front", "#151B20", "chrome"), ("card_back", "#1E262E", "matte"), ("chip", "#D6AD59", "chrome"),
        ("leather", "#7C421C", "leather"), ("gold", "#D6AD59", "chrome"), ("silver", "#D8E2EC", "chrome"),
        ("smartphone_chassis", "#1E242B", "metal"), ("smartphone_screen", "#1D4ED8", "emissive"), ("smartphone_camera", "#0F172A", "glass")
    ]
    for idx_h, (hname, hcol, hkind) in enumerate(hero_tex_specs):
        htile = generate_32x32_tile(hname, hcol, hkind, 100 + idx_h)
        # Custom insignia details on hero textures
        if hname == "medkit_red_cross":
            htile[4:28, 12:20, :3] = [255, 255, 255]
            htile[12:20, 4:28, :3] = [255, 255, 255]
        elif hname == "bills_top":
            htile[6:26, 6:26, :3] = [30, 105, 62]
            htile[11:21, 11:21, :3] = [214, 173, 89]
        elif hname == "smartphone_screen":
            # Wallpaper + app grid dots at 32x32
            for ay in range(6, 26, 6):
                for ax in range(6, 26, 6):
                    htile[ay:ay + 4, ax:ax + 4, :3] = [(ax * 9) % 255, 210, (ay * 11) % 255]
        Image.fromarray(htile, mode="RGBA").save(TEX_32_DIR / f"{hname}.png", optimize=True)

    return arr


ATLAS_ARR = None


def get_atlas() -> np.ndarray:
    global ATLAS_ARR
    if ATLAS_ARR is None:
        if ATLAS_PATH.exists():
            ATLAS_ARR = np.array(Image.open(ATLAS_PATH).convert("RGBA"))
        else:
            ATLAS_ARR = build_shared_atlas()
    return ATLAS_ARR


class PartBuilder:
    """Ergonomic multi-part voxel geometry builder with 32x32 textured UV mapping."""

    def __init__(self):
        self.bones = {"root": {"pivot": [0, 0, 0], "parent": None, "parts": []}}

    def add_bone(self, name: str, pivot=(0, 0, 0), parent="root"):
        if name not in self.bones:
            self.bones[name] = {"pivot": [round(float(v), 3) for v in pivot], "parent": parent, "parts": []}

    def box(self, x, y, z, w, h, d, mat="steel_dark", bone="root", rot=None, pivot=None, name=None):
        if w <= 0 or h <= 0 or d <= 0:
            return
        if bone not in self.bones:
            self.add_bone(bone, pivot or [x + w / 2, y + h / 2, z + d / 2])
        self.bones[bone]["parts"].append({
            "origin": [round(float(x), 3), round(float(y), 3), round(float(z), 3)],
            "size": [round(float(w), 3), round(float(h), 3), round(float(d), 3)],
            "mat": mat,
            "rot": list(rot) if rot else None,
            "pivot": list(pivot) if pivot else None,
            "name": name or f"part_{len(self.bones[bone]['parts'])}"
        })

    def cbox(self, cx, y, cz, w, h, d, mat="steel_dark", bone="root", rot=None, pivot=None, name=None):
        self.box(cx - w / 2.0, y, cz - d / 2.0, w, h, d, mat=mat, bone=bone, rot=rot, pivot=pivot, name=name)

    def wheel(self, cx, y_center, cz, radius=4.5, width=2.8, tire_mat="rubber_tire", rim_mat="alloy_rim", bone="root"):
        r = radius
        t = r * 0.42
        self.cbox(cx, y_center - r, cz, width, r * 2, r * 1.15, mat=tire_mat, bone=bone, name="tire_v")
        self.cbox(cx, y_center - r * 0.58, cz, width, r * 1.16, r * 2, mat=tire_mat, bone=bone, name="tire_h")
        self.cbox(cx, y_center - r * 0.85, cz, width * 0.96, r * 1.7, r * 1.65, mat=tire_mat, bone=bone, name="tire_d")
        self.cbox(cx, y_center - t, cz, width + 0.35, t * 2, t * 2, mat=rim_mat, bone=bone, name="rim")
        self.cbox(cx, y_center - t * 0.4, cz, width + 0.6, t * 0.8, t * 0.8, mat="chrome", bone=bone, name="hub")

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

                mi = MAT_INDEX.get(p["mat"], 0)
                u0, v0 = (mi % 8) * 32, (mi // 8) * 32
                c = {
                    "origin": [ox, oy, oz],
                    "size": [sw, sh, sd],
                    "uv": {
                        f: {"uv": [u0 + 1, v0 + 1], "uv_size": [30, 30]}
                        for f in ("north", "south", "east", "west", "up", "down")
                    }
                }
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
                    "texture_width": 256,
                    "texture_height": 256,
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
            mi = MAT_INDEX.get(p["mat"], 0)
            u0, v0 = (mi % 8) * 2.0, (mi // 8) * 2.0
            el = {
                "name": p["name"], "from": [fx, fy, fz], "to": [tx, ty, tz],
                "faces": {f: {"uv": [u0 + 0.08, v0 + 0.08, u0 + 1.92, v0 + 1.92], "texture": "#atlas"}
                          for f in ("north", "south", "east", "west", "up", "down")}
            }
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
            "credit": "GTM Indraprastha - Studio 3D Asset (32x32 Atlas)",
            "parent": "minecraft:block/block",
            "textures": {"atlas": "gtm:item/gtm_master_atlas_32x", "particle": "#atlas"},
            "elements": elements,
            "display": {
                "gui": {"rotation": [28, 225, 0], "translation": [0, 0.5, 0], "scale": [0.78, 0.78, 0.78]},
                "ground": {"translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
                "firstperson_righthand": {"rotation": [0, 45, 0], "scale": [0.45, 0.45, 0.45]},
                "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.38, 0.38, 0.38]}
            }
        }
        dest.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")

    def render_icon(self, dest: Path, size: int = 128, yaw_deg: float = -38.0, pitch_deg: float = 24.0):
        """
        TRUE Per-Pixel Z-Buffered & UV-Textured Studio 3D Renderer (256x256 -> 128x128 RGBA):
        - Outward-facing quad winding (front faces NEVER culled!).
        - Exact per-pixel Z-depth comparison across every quad bounding box!
        - Per-pixel bilinear-free crisp UV sampling from the 32x32 material textures!
        - 3-point studio lighting + specular reflections + soft contact shadow + glossy outline!
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
            world_corners.append((p["mat"], [rotate_pt(c) for c in corners]))

        all_pts = np.array([c for _, cs in world_corners for c in cs])
        minx, miny = all_pts[:, 0].min(), all_pts[:, 1].min()
        maxx, maxy = all_pts[:, 0].max(), all_pts[:, 1].max()

        W = 224  # supersampled internal resolution (~1.75x of 128px -> super fast & sharp)
        span = max(maxx - minx, maxy - miny, 1.0)
        scale = (W * 0.78) / span
        mid_x, mid_y = (minx + maxx) * 0.5, (miny + maxy) * 0.5

        L = np.array([-0.42, 0.78, 0.46], dtype=np.float32)
        L /= np.linalg.norm(L)
        V = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        H_vec = (L + V)
        H_vec /= np.linalg.norm(H_vec)

        # VERIFIED OUTWARD-FACING COUNTER-CLOCKWISE NORMALS:
        # e1 = v1 - v0, e2 = v3 - v0 -> cross(e1, e2) points strictly OUTWARD from the cube!
        FACE_VERTS = [
            (0, 3, 2, 1),  # north (-Z): e1=(0,1,0), e2=(1,0,0) -> (0,0,-1) OUTWARD!
            (4, 5, 6, 7),  # south (+Z): e1=(1,0,0), e2=(0,1,0) -> (0,0,+1) OUTWARD!
            (4, 7, 3, 0),  # west  (-X): e1=(0,1,0), e2=(0,0,-1)-> (-1,0,0) OUTWARD!
            (1, 2, 6, 5),  # east  (+X): e1=(0,1,0), e2=(0,0,1) -> (+1,0,0) OUTWARD!
            (3, 7, 6, 2),  # up    (+Y): e1=(0,0,1), e2=(1,0,0) -> (0,+1,0) OUTWARD!
            (0, 1, 5, 4),  # down  (-Y): e1=(1,0,0), e2=(0,0,1) -> (0,-1,0) OUTWARD!
        ]

        zbuf = np.full((W, W), -1e9, dtype=np.float32)
        cbuf = np.zeros((W, W, 4), dtype=np.uint8)

        # Pre-allocate coordinate grid for vectorized barycentric parallelogram test
        for mat_name, cs in world_corners:
            mi = MAT_INDEX.get(mat_name, 0)
            _, _, mkind = MATERIALS[mi]
            tx0, ty0 = (mi % 8) * 32, (mi // 8) * 32
            tex_patch = atlas[ty0:ty0 + 32, tx0:tx0 + 32].astype(np.float32)

            for idxs in FACE_VERTS:
                v0, v1, v2, v3 = cs[idxs[0]], cs[idxs[1]], cs[idxs[2]], cs[idxs[3]]
                e1 = v1 - v0
                e2 = v3 - v0
                normal = np.cross(e1, e2)
                nlen = np.linalg.norm(normal)
                if nlen < 1e-6:
                    continue
                normal /= nlen
                # Keep ONLY front-facing faces whose outward normal faces +Z camera!
                if normal[2] <= 0.01:
                    continue

                # Project parallelogram corners to screen pixels (sx, sy) and depth (sz)
                pts3 = np.stack([v0, v1, v2, v3])
                sx = W * 0.5 + (pts3[:, 0] - mid_x) * scale
                sy = W * 0.51 - (pts3[:, 1] - mid_y) * scale
                sz = pts3[:, 2]

                bx0 = max(0, int(math.floor(sx.min())))
                bx1 = min(W, int(math.ceil(sx.max())) + 1)
                by0 = max(0, int(math.floor(sy.min())))
                by1 = min(W, int(math.ceil(sy.max())) + 1)
                if bx1 <= bx0 or by1 <= by0:
                    continue

                # Screen-space affine parallelogram vectors (v0 -> v1 is u axis, v0 -> v3 is v axis)
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

                mask = (u >= -0.02) & (u <= 1.02) & (v >= -0.02) & (v <= 1.02)
                if not mask.any():
                    continue

                # Interpolated per-pixel Z!
                z_val = sz[0] + u * (sz[1] - sz[0]) + v * (sz[3] - sz[0])
                hit = mask & (z_val > zbuf[by0:by1, bx0:bx1])
                if not hit.any():
                    continue

                # Sample real 32x32 texture coordinates!
                tu = np.clip((u[hit] * 31.99).astype(np.int32), 0, 31)
                tv = np.clip((v[hit] * 31.99).astype(np.int32), 0, 31)
                sampled_rgba = tex_patch[tv, tu]  # shape (N, 4)

                # Lighting computation
                ndotl = max(0.0, float(np.dot(normal, L)))
                ambient = 0.44
                diffuse = 0.60 * ndotl
                rim = 0.22 * (1.0 - max(0.0, float(normal[2]))) ** 1.5
                spec = 0.0
                if mkind in ("gloss", "chrome", "glass", "metal"):
                    ndoth = max(0.0, float(np.dot(normal, H_vec)))
                    spec = (44.0 if mkind in ("chrome", "glass") else 22.0) * (ndoth ** 18.0)

                lit_rgb = sampled_rgba[:, :3] * (ambient + diffuse) + np.array([210.0, 225.0, 255.0]) * (rim * 0.25) + spec
                if mkind == "emissive":
                    lit_rgb = np.maximum(lit_rgb, sampled_rgba[:, :3] * 1.15)
                lit_rgb = np.clip(lit_rgb, 0, 255).astype(np.uint8)
                lit_a = np.clip(sampled_rgba[:, 3], 0, 255).astype(np.uint8)

                sub_z = zbuf[by0:by1, bx0:bx1]
                sub_c = cbuf[by0:by1, bx0:bx1]
                sub_z[hit] = z_val[hit]
                sub_c[hit, :3] = lit_rgb
                sub_c[hit, 3] = lit_a

        # Compose with studio contact shadow + crisp dark silhouette outline!
        obj_im = Image.fromarray(cbuf, mode="RGBA")
        shadow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow, "RGBA")
        sd.ellipse([int(W * 0.16), int(W * 0.77), int(W * 0.84), int(W * 0.91)], fill=(6, 9, 14, 120))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=5))

        alpha_ch = obj_im.split()[3]
        expanded = alpha_ch.filter(ImageFilter.MaxFilter(5))
        outline = Image.new("RGBA", (W, W), (10, 14, 20, 215))

        composed = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        composed.paste(shadow, (0, 0), shadow)
        composed.paste(outline, (0, 0), expanded)
        composed.paste(obj_im, (0, 0), obj_im)

        final_im = composed.resize((size, size), Image.Resampling.LANCZOS)
        final_im.save(dest, format="PNG", optimize=True)
