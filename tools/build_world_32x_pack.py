#!/usr/bin/env python3
"""
Build & install a complete 32x32 Medium-Realism World Resource Pack for Indraprastha (Java 1.21+ / 26.3 & Bedrock)
paired with all 32x32 custom model textures so world blocks match 32x32 vehicles, furniture, and props seamlessly.
Installs into local %APPDATA%/.minecraft/resourcepacks/ (safely preserving repo main packs).
"""
import json
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import numpy as np
from PIL import Image, ImageColor, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import studio_3d_engine as s3d
import validate_creative_r4 as v4

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
WORLD_32_SRC = CREATIVE / "source" / "textures" / "world_32x"
PACKS_OUT = CREATIVE / "packs"
PREVIEWS = CREATIVE / "previews"


def make_32x_block(name: str, style: str, c1: str, c2: str, c3: str = None, seed: int = 1) -> np.ndarray:
    """Synthesize a crisp seamless 32x32 tiling Minecraft world block texture."""
    rng = np.random.default_rng(5000 + seed * 41)
    rgb1 = np.array(ImageColor.getrgb(c1), dtype=np.float32)
    rgb2 = np.array(ImageColor.getrgb(c2), dtype=np.float32)
    rgb3 = np.array(ImageColor.getrgb(c3 or c1), dtype=np.float32)

    tile = np.zeros((32, 32, 4), dtype=np.float32)
    tile[:, :, :3] = rgb1
    tile[:, :, 3] = 255.0

    yy, xx = np.mgrid[0:32, 0:32]
    n = rng.uniform(-1.0, 1.0, (32, 32))
    # Wrapping tileable harmonic noise
    wave = (np.sin(2 * np.pi * xx / 32.0) * np.cos(2 * np.pi * yy / 32.0) +
            0.5 * np.sin(4 * np.pi * xx / 32.0 + 2 * np.pi * yy / 32.0))

    if style == "stone":
        mix = np.clip(0.5 + wave * 0.25 + n * 0.18, 0.0, 1.0)[:, :, None]
        tile[:, :, :3] = rgb1 * (1 - mix) + rgb2 * mix
        tile[n > 0.72, :3] *= 0.88
        tile[n < -0.72, :3] *= 1.12
    elif style == "cobble":
        # Interlocking rounded 8x8/16x8 cobblestones with mortar
        seam = ((yy % 8 == 0) | (((xx + (yy // 8) * 6) % 10) == 0))
        tile[:, :, :3] = rgb1 * 0.85 + rgb2 * 0.15 + n[:, :, None] * 10.0
        tile[seam, :3] = rgb3 * 0.65
        tile[np.roll(seam, 1, axis=0) & ~seam, :3] *= 1.14
    elif style == "bricks":
        row = yy // 8
        off = (row % 2) * 8
        mortar = (yy % 8 == 0) | (((xx + off) % 16) == 0)
        brick_var = ((row * 3 + (xx + off) // 16) % 4) - 1.5
        tile[:, :, :3] = rgb1 + brick_var[:, :, None] * 8.0 + n[:, :, None] * 6.0
        tile[mortar, :3] = rgb2
        tile[np.roll(yy % 8 == 1, 0, axis=0), :3] *= 1.08
    elif style == "polished":
        # Subtle bevel border + honed stone veins
        tile[:, :, :3] = rgb1 + wave[:, :, None] * 6.0 + n[:, :, None] * 4.0
        tile[0:2, :, :3] = rgb2
        tile[:, 0:2, :3] = rgb2
        tile[30:32, :, :3] = rgb3
        tile[:, 30:32, :3] = rgb3
    elif style == "planks":
        plank_idx = yy // 8
        seam = (yy % 8 == 0) | ((xx == ((plank_idx * 11) % 32)) & (yy % 8 != 0))
        grain = np.sin(xx * 0.4 + plank_idx * 1.9 + np.sin(yy * 0.6) * 0.8) * 10.0
        tile[:, :, :3] = rgb1 + grain[:, :, None] + (((plank_idx % 2) * 6.0 - 3.0))[:, :, None]
        tile[seam, :3] = rgb2
        tile[np.roll(yy % 8 == 1, 0, axis=0), :3] *= 1.10
    elif style == "log_side":
        bark = np.sin(xx * 1.3 + np.sin(yy * 0.35) * 1.4) * 0.5 + 0.5
        tile[:, :, :3] = rgb1 * (1 - bark[:, :, None]) + rgb2 * bark[:, :, None] + n[:, :, None] * 5.0
    elif style == "log_top":
        dist = np.sqrt((xx - 15.5) ** 2 + (yy - 15.5) ** 2)
        rings = (np.sin(dist * 1.45) > 0.15)
        tile[:, :, :3] = np.where(rings[:, :, None], rgb1, rgb2)
        border = (dist > 13.5)
        tile[border, :3] = rgb3
    elif style == "asphalt":
        # Realistic fine-grain tarmac / concrete with aggregate flecks
        speck = rng.choice([0, 1, 2], size=(32, 32), p=[0.75, 0.15, 0.10])
        tile[:, :, :3] = rgb1 + n[:, :, None] * 6.0
        tile[speck == 1, :3] = rgb2
        tile[speck == 2, :3] = rgb3
    elif style == "concrete_line":
        tile = make_32x_block(name, "asphalt", c1, c2, c3, seed).astype(np.float32)
        if "yellow" in name:
            tile[:, 13:19, :3] = ImageColor.getrgb("#F5B800")
        elif "white" in name:
            tile[:, 12:20, :3] = ImageColor.getrgb("#E8ECEF")
    elif style == "glass":
        tile[:, :, :3] = rgb1
        tile[:, :, 3] = 90.0 if "tinted" not in name else 160.0
        # Beveled crisp frame + diagonal sky reflection streak
        tile[0:2, :, :4] = [*rgb2, 235]
        tile[30:32, :, :4] = [*rgb2, 235]
        tile[:, 0:2, :4] = [*rgb2, 235]
        tile[:, 30:32, :4] = [*rgb2, 235]
        streak = ((xx - yy) >= 4) & ((xx - yy) <= 7) & (xx > 5) & (xx < 26)
        tile[streak, :4] = [255, 255, 255, 195]
    elif style == "leaves":
        leaf_pat = ((np.sin(xx * 0.7) * np.cos(yy * 0.7) + n * 0.45) > 0.05)
        tile[:, :, :3] = np.where(leaf_pat[:, :, None], rgb1, rgb2)
        holes = (n < -0.55) & ((xx + yy) % 2 == 0)
        tile[holes, 3] = 0.0
    elif style == "grass_side":
        tile = make_32x_block(name, "stone", c2, c3, seed=seed).astype(np.float32)
        overhang = 7 + (np.sin(xx[0, :] * 0.7) * 2.5 + n[0, :] * 1.5).astype(int)
        for col_x in range(32):
            h_g = max(3, int(overhang[col_x]))
            tile[:h_g, col_x, :3] = rgb1 + n[:h_g, col_x, None] * 10.0
    elif style == "lamp":
        tile[:, :, :3] = rgb1
        frame = (xx < 3) | (xx > 28) | (yy < 3) | (yy > 28) | (xx == 15) | (yy == 15)
        tile[frame, :3] = rgb2
        dist = np.sqrt((xx - 15.5) ** 2 + (yy - 15.5) ** 2)
        tile[~frame, :3] += np.clip((1.0 - dist[~frame] / 18.0) * 55.0, 0, 65)[:, None]
    elif style == "metal":
        plate = (xx % 16 == 0) | (yy % 16 == 0)
        diag = np.sin((xx + yy) * 0.25) * 14.0
        tile[:, :, :3] = rgb1 + diag[:, :, None]
        tile[plate, :3] = rgb2
        tile[2:4, 2:4, :3] = rgb3
        tile[2:4, 28:30, :3] = rgb3
        tile[28:30, 2:4, :3] = rgb3
        tile[28:30, 28:30, :3] = rgb3
    elif style == "water":
        ripple = np.sin(2 * np.pi * xx / 16.0 + np.sin(2 * np.pi * yy / 16.0)) * 22.0
        tile[:, :, :3] = rgb1 + ripple[:, :, None]
        tile[:, :, 3] = 205.0
    else:
        tile[:, :, :3] = rgb1 + wave[:, :, None] * 10.0 + n[:, :, None] * 8.0

    return np.clip(tile, 0, 255).astype(np.uint8)


def build_world_blocks():
    """Generate 88 essential cohesive 32x32 Indraprastha city & world block textures."""
    specs = [
        # Asphalt, Roads, Sidewalks & Concretes
        ("gray_concrete", "asphalt", "#3A4047", "#4D545E", "#282C32"),
        ("black_concrete", "asphalt", "#191D22", "#262B32", "#101317"),
        ("light_gray_concrete", "polished", "#A6ACB4", "#BFC5CC", "#838A92"),
        ("white_concrete", "polished", "#E8ECEF", "#FFFFFF", "#C6CCD4"),
        ("yellow_concrete", "polished", "#EAB308", "#FDE047", "#B45309"),
        ("cyan_concrete", "asphalt", "#255D66", "#357B85", "#18424A"),
        ("blue_concrete", "polished", "#1D4E89", "#3B82F6", "#1E3A8A"),
        ("red_concrete", "polished", "#B8292F", "#EF4444", "#7F1D1D"),
        ("green_concrete", "polished", "#236653", "#34D399", "#14532D"),
        ("orange_concrete", "polished", "#AD5637", "#FB923C", "#7C2D12"),
        ("lime_concrete", "polished", "#4D9E3A", "#84CC16", "#365314"),
        ("purple_concrete", "polished", "#6B21A8", "#A855F7", "#4C1D95"),
        ("magenta_concrete", "polished", "#9D174D", "#EC4899", "#701A75"),
        ("pink_concrete", "polished", "#EC4899", "#F9A8D4", "#BE185D"),
        ("light_blue_concrete", "polished", "#0284C7", "#38BDF8", "#075985"),
        ("brown_concrete", "asphalt", "#5C3D2E", "#755240", "#3D251A"),
        # Stones & Masonry
        ("stone", "stone", "#7F848A", "#686D73", "#969BA2"),
        ("smooth_stone", "polished", "#9CA1A8", "#B6BCC4", "#787E85"),
        ("smooth_stone_slab_side", "polished", "#9CA1A8", "#B6BCC4", "#666B72"),
        ("cobblestone", "cobble", "#6F747A", "#8A9096", "#42464B"),
        ("mossy_cobblestone", "cobble", "#5D7357", "#7E8589", "#3A4E36"),
        ("stone_bricks", "bricks", "#7A7F86", "#54585E", "#969CA4"),
        ("cracked_stone_bricks", "bricks", "#6C7178", "#42464B", "#888E96"),
        ("mossy_stone_bricks", "bricks", "#647662", "#475746", "#839381"),
        ("andesite", "stone", "#86898B", "#6F7275", "#A0A4A6"),
        ("polished_andesite", "polished", "#898E92", "#A4A9AE", "#696E72"),
        ("diorite", "stone", "#D0CFD2", "#A7A7AA", "#EFEFF2"),
        ("polished_diorite", "polished", "#D4D4D8", "#EDEDEF", "#A1A1AA"),
        ("granite", "stone", "#996A59", "#7C5242", "#B88471"),
        ("polished_granite", "polished", "#9E6E5C", "#BC8875", "#764E3E"),
        ("deepslate", "stone", "#3C3E44", "#282A2F", "#52555D"),
        ("polished_deepslate", "polished", "#40434A", "#565963", "#2A2C32"),
        ("deepslate_bricks", "bricks", "#3A3D43", "#24262A", "#4F535C"),
        ("deepslate_tiles", "bricks", "#34373D", "#1E2024", "#474B52"),
        ("bricks", "bricks", "#9E472D", "#C8C1B8", "#B95D42"),
        ("mud_bricks", "bricks", "#89674E", "#634835", "#A68065"),
        # Indian Terracotta & Sandstone & Quartz Heritage Facades
        ("terracotta", "stone", "#985B43", "#7E4833", "#B06F55"),
        ("white_terracotta", "stone", "#D1B1A1", "#B79686", "#E5C8BA"),
        ("orange_terracotta", "stone", "#A15325", "#864119", "#BC6938"),
        ("yellow_terracotta", "stone", "#BA8523", "#9A6C19", "#D49E38"),
        ("red_terracotta", "stone", "#8F3D2E", "#732E22", "#A95040"),
        ("sandstone", "bricks", "#DFCE9B", "#C5B079", "#EFE2B6"),
        ("sandstone_top", "stone", "#E3D4A5", "#D0BE8A", "#EFE3BA"),
        ("sandstone_bottom", "stone", "#D2BF8B", "#B8A46F", "#E3D1A0"),
        ("smooth_sandstone", "polished", "#E4D5A7", "#F2E6BE", "#C9B783"),
        ("quartz_block_side", "polished", "#ECE8E0", "#FFFFFF", "#CFC9BE"),
        ("quartz_block_top", "polished", "#F0ECE4", "#FFFFFF", "#D8D2C8"),
        ("quartz_bricks", "bricks", "#EAE5DC", "#C8C2B8", "#FFFFFF"),
        ("quartz_pillar", "planks", "#EDE9E1", "#D4CEC4", "#FFFFFF"),
        # Woods (Teak, Oak, Spruce, Dark Oak, Birch)
        ("oak_planks", "planks", "#A9804D", "#78572E", "#C49A63"),
        ("spruce_planks", "planks", "#715230", "#4E371E", "#8A6842"),
        ("dark_oak_planks", "planks", "#432B16", "#2B1B0D", "#593A20"),
        ("birch_planks", "planks", "#C8B77C", "#9E8D57", "#DECFA0"),
        ("jungle_planks", "planks", "#A37451", "#785134", "#BD8E6A"),
        ("acacia_planks", "planks", "#AD5D32", "#7C3F1E", "#C87446"),
        ("oak_log", "log_side", "#685134", "#4A3821", "#856B49"),
        ("oak_log_top", "log_top", "#B38A56", "#8E693C", "#5E482C"),
        ("spruce_log", "log_side", "#3A2512", "#25170B", "#52371D"),
        ("spruce_log_top", "log_top", "#7E5D38", "#5E4325", "#3A2512"),
        ("dark_oak_log", "log_side", "#38281A", "#23190F", "#4D3927"),
        ("birch_log", "log_side", "#DEDAD2", "#3A3A3A", "#C4BEB3"),
        # Glass & Metals & Lighting
        ("glass", "glass", "#94D4E4", "#E2F6FA", "#5BA6B8"),
        ("light_blue_stained_glass", "glass", "#5BB4E5", "#BAE6FD", "#2563EB"),
        ("gray_stained_glass", "glass", "#525A65", "#94A3B8", "#334155"),
        ("black_stained_glass", "glass", "#1E222A", "#475569", "#0F172A"),
        ("tinted_glass", "glass", "#2B2832", "#6B7280", "#18151D"),
        ("iron_block", "metal", "#DCE0E4", "#A4ACB5", "#FFFFFF"),
        ("gold_block", "metal", "#F2C641", "#B58517", "#FFF2A6"),
        ("copper_block", "metal", "#C26B4A", "#8B452C", "#E29070"),
        ("obsidian", "stone", "#161021", "#2B1B42", "#0B0812"),
        ("glowstone", "lamp", "#F5B841", "#8C5214", "#FFF5B8"),
        ("sea_lantern", "lamp", "#8AE2D0", "#327A78", "#E6FFFA"),
        ("redstone_lamp", "lamp", "#5E3820", "#2A180D", "#8A5636"),
        ("redstone_lamp_on", "lamp", "#E8B058", "#6B421A", "#FFF1BA"),
        # Natural Coastal Terrain
        ("grass_block_top", "stone", "#5E9D3B", "#4B822D", "#74B84E"),
        ("grass_block_side", "grass_side", "#5E9D3B", "#866043", "#6B4A31"),
        ("dirt", "stone", "#866043", "#6B4A31", "#9C7354"),
        ("coarse_dirt", "asphalt", "#755239", "#5B4A3B", "#946A4D"),
        ("sand", "stone", "#E4D7A5", "#D2C38E", "#F2E8BE"),
        ("red_sand", "stone", "#BE6422", "#9A4E16", "#D97E3B"),
        ("gravel", "asphalt", "#827E7E", "#656161", "#9E9A9A"),
        ("clay", "stone", "#9EA4B0", "#89909C", "#B4BAC6"),
        ("oak_leaves", "leaves", "#4C872D", "#33611C", "#66A344"),
        ("spruce_leaves", "leaves", "#3E663D", "#284727", "#538052"),
        ("birch_leaves", "leaves", "#628E42", "#47692D", "#78A656"),
        ("water_still", "water", "#2684B8", "#3EA4DB", "#19618C")
    ]

    blk_dir = WORLD_32_SRC / "assets" / "minecraft" / "textures" / "block"
    bed_blk_dir = WORLD_32_SRC / "bedrock" / "textures" / "blocks"
    blk_dir.mkdir(parents=True, exist_ok=True)
    bed_blk_dir.mkdir(parents=True, exist_ok=True)

    imgs, titles = [], []
    for i, (bname, bstyle, c1, c2, c3) in enumerate(specs):
        arr = make_32x_block(bname, bstyle, c1, c2, c3, seed=i + 1)
        im = Image.fromarray(arr, mode="RGBA")
        im.save(blk_dir / f"{bname}.png", format="PNG", optimize=True)
        # Bedrock equivalent filename mapping where needed
        bed_name = bname
        if bname == "grass_block_top":
            bed_name = "grass_top"
        elif bname == "grass_block_side":
            bed_name = "grass_side_carried"
        elif bname.endswith("_concrete"):
            bed_name = "concrete_" + bname.replace("_concrete", "")
        im.save(bed_blk_dir / f"{bed_name}.png", format="PNG", optimize=True)
        imgs.append(im)
        titles.append(bname)

    return imgs, titles


def package_and_install_world_32x(imgs, titles):
    PACKS_OUT.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)

    # Preview contact sheet of the 32x32 World Pack
    v4.create_grid(imgs, titles, cols=11, cell_w=92, cell_h=108).save(PREVIEWS / "world_32x_blocks_contact_sheet.png", optimize=True)

    pack_icon = CREATIVE / "source" / "icons" / "server-icon.png"

    # 1. Build GTM_Indraprastha_World_32x_Java.zip (Java 1.21+ / Paper 26.3, pack_format 46-84+ overlay compatible)
    java_zip_path = PACKS_OUT / "GTM_Indraprastha_World_32x_Java.zip"
    mcmeta = {
        "pack": {
            "pack_format": 48,
            "supported_formats": {"min_inclusive": 15, "max_inclusive": 999},
            "min_format": 15,
            "max_format": 999,
            "description": "\u00a76GTM Indraprastha World \u00a78| \u00a7e32x32 Cohesive City & World Textures"
        }
    }
    blk_dir = WORLD_32_SRC / "assets" / "minecraft" / "textures" / "block"
    with ZipFile(java_zip_path, "w", ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps(mcmeta, indent=2) + "\n")
        if pack_icon.exists():
            z.write(pack_icon, "pack.png")
        for p in sorted(blk_dir.glob("*.png")):
            z.write(p, f"assets/minecraft/textures/block/{p.name}")
        # Also include 32x32 custom model textures inside the combined Java world+model texture pack!
        for p in sorted(s3d.TEX_32_DIR.glob("*.png")):
            z.write(p, f"assets/gtm/textures/item/{p.name}")
            z.write(p, f"assets/sdcraft/textures/item/{p.name}")
        if s3d.ATLAS_PATH.exists():
            z.write(s3d.ATLAS_PATH, "assets/gtm/textures/item/gtm_master_atlas_32x.png")

    # 2. Build GTM_Indraprastha_World_32x_Bedrock.mcpack (Geyser crossplay compatible!)
    bed_pack_path = PACKS_OUT / "GTM_Indraprastha_World_32x_Bedrock.mcpack"
    manifest_bed = {
        "format_version": 2,
        "header": {
            "name": "GTM Indraprastha World 32x32",
            "description": "32x32 Cohesive Indraprastha City World & Model Textures for Geyser Crossplay",
            "uuid": "9e8d7c6b-5a4f-4132-89ab-cdef01234567",
            "version": [1, 0, 0],
            "min_engine_version": [1, 21, 0]
        },
        "modules": [{
            "type": "resources",
            "uuid": "1a2b3c4d-5e6f-4789-abcd-ef0123456789",
            "version": [1, 0, 0]
        }]
    }
    bed_blk_dir = WORLD_32_SRC / "bedrock" / "textures" / "blocks"
    with ZipFile(bed_pack_path, "w", ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest_bed, indent=2) + "\n")
        if pack_icon.exists():
            z.write(pack_icon, "pack_icon.png")
        for p in sorted(bed_blk_dir.glob("*.png")):
            z.write(p, f"textures/blocks/{p.name}")
        for p in sorted(s3d.TEX_32_DIR.glob("*.png")):
            z.write(p, f"textures/items/gtm_{p.name}")

    # 3. Install GTM_Indraprastha_World_32x_Java.zip locally into %APPDATA%/.minecraft/resourcepacks/
    mc_rp_dir = Path.home() / "AppData" / "Roaming" / ".minecraft" / "resourcepacks"
    installed_msg = "Skipped (no local .minecraft dir)"
    if mc_rp_dir.parent.exists():
        mc_rp_dir.mkdir(parents=True, exist_ok=True)
        dest_rp = mc_rp_dir / "GTM_Indraprastha_World_32x_Java.zip"
        shutil.copy2(java_zip_path, dest_rp)
        installed_msg = str(dest_rp)

        # Also enable gently in .minecraft/options.txt right above vanilla if present
        opt_file = Path.home() / "AppData" / "Roaming" / ".minecraft" / "options.txt"
        if opt_file.exists():
            lines = opt_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            updated = []
            pack_entry = "file/GTM_Indraprastha_World_32x_Java.zip"
            for ln in lines:
                if ln.startswith("resourcePacks:"):
                    try:
                        rp_list = json.loads(ln.split(":", 1)[1])
                        if pack_entry not in rp_list:
                            rp_list.append(pack_entry)
                        ln = "resourcePacks:" + json.dumps(rp_list)
                    except Exception:
                        pass
                updated.append(ln)
            opt_file.write_text("\n".join(updated) + "\n", encoding="utf-8")

    # 4. Also copy clean 32x world pack ZIP into d:\Games\SDCRAFT\sdcraft_isolated\resourcepacks\ for staging convenience
    iso_rp = Path(r"d:\Games\SDCRAFT\sdcraft_isolated\resourcepacks")
    if iso_rp.exists():
        shutil.copy2(java_zip_path, iso_rp / "GTM_Indraprastha_World_32x_Java.zip")

    print(f"SUCCESS: Built 86 World 32x32 blocks + {len(list(s3d.TEX_32_DIR.glob('*.png')))} model 32x32 textures!")
    print(f"  - Java Pack: {java_zip_path}")
    print(f"  - Bedrock Pack: {bed_pack_path}")
    print(f"  - Installed locally at: {installed_msg}")


if __name__ == "__main__":
    s3d.build_shared_atlas()
    imgs, titles = build_world_blocks()
    package_and_install_world_32x(imgs, titles)
