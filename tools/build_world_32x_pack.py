#!/usr/bin/env python3
"""
Build & install a complete Faithful-32x-Inspired World Resource Pack for Indraprastha (Java 1.21+ / 26.3 & Bedrock)
paired with all Faithful 32x custom model textures & sprites so every world block matches vehicles, furniture,
weapons, foods, and props cleanly.
Installs into local %APPDATA%/.minecraft/resourcepacks/ (safely preserving repo main packs).
"""
import json
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import numpy as np
from PIL import Image, ImageColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
import faithful_32x_palette as f32
import studio_3d_engine as s3d
import validate_creative_r4 as v4

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
WORLD_32_SRC = CREATIVE / "source" / "textures" / "world_32x"
PACKS_OUT = CREATIVE / "packs"
PREVIEWS = CREATIVE / "previews"


def make_32x_block(name: str, style: str, c1: str, c2: str, c3: str = None, seed: int = 1) -> np.ndarray:
    """Synthesize a crisp seamless 32x32 Faithful-32x-inspired Minecraft block texture."""
    c3 = c3 or c1
    if style == "stone":
        return f32.tex_stone_rough(c1, contrast=0.88, seed=seed)
    if style == "cobble":
        mossy = c2 if "mossy" in name else None
        return f32.tex_cobble(c1, mossy_hex=mossy, seed=seed)
    if style == "bricks":
        return f32.tex_bricks(
            c1, c2,
            bw=16, bh=8,
            cracked=("cracked" in name),
            mossy_hex=("#4D7A44" if "mossy" in name else None),
            seed=seed,
        )
    if style == "tiles":
        return f32.tex_bricks(c1, c2, bw=8, bh=8, seed=seed)
    if style == "polished":
        return f32.tex_polished(c1, frame=2, flecks=("smooth" not in name and "quartz" not in name), seed=seed)
    if style == "planks":
        return f32.tex_planks(c1, vertical=("pillar" in name), seed=seed)
    if style == "log_side":
        return f32.tex_log_side(c1, birch=("birch" in name), seed=seed)
    if style == "log_top":
        return f32.tex_log_top(c3, c1, seed=seed)
    if style in ("asphalt", "dirt", "sand", "gravel"):
        sub = "sand" if style == "sand" else ("gravel" if style == "gravel" else "dirt")
        return f32.tex_dirt_sand_gravel(c1, style=sub, seed=seed)
    if style == "glass":
        return f32.tex_glass(c1, c2, alpha=165 if "tinted" in name else (140 if "stained" in name else 108))
    if style == "leaves":
        return f32.tex_leaves(c1, seed=seed)
    if style == "grass_top":
        return f32.tex_grass_top(c1, seed=seed)
    if style == "grass_side":
        return f32.tex_grass_side(c1, c2, seed=seed)
    if style == "glowstone":
        return f32.tex_glowstone()
    if style == "sea_lantern":
        return f32.tex_sea_lantern()
    if style == "lamp_on":
        return f32.tex_redstone_lamp(lit=True)
    if style == "lamp_off":
        return f32.tex_redstone_lamp(lit=False)
    if style == "metal":
        return f32.tex_metal_block(c1, rivets=("iron" in name or "copper" in name), specular=True, seed=seed)
    if style == "gem":
        out = f32.tex_metal_block(c1, rivets=False, specular=True, seed=seed)
        ramp = f32.make_ramp(c1, contrast=1.15)
        for y in range(6, 26):
            for x in range(6, 26):
                d = abs(x - 15.5) + abs(y - 15.5)
                if d < 5.0:
                    out[y, x, :3] = ramp[5]
                elif d < 9.5:
                    out[y, x, :3] = ramp[4]
        return out
    if style == "wool":
        return f32.tex_fabric(c1, stitch=False, seed=seed)
    if style == "bookshelf":
        return f32.tex_bookshelf()
    if style == "water":
        return f32.tex_glass(c1, c1, is_water=True)
    if style == "obsidian":
        out = f32.tex_cobble(c1, seed=seed)
        violet = f32.make_ramp("#4C2A75", contrast=1.1)
        out[(out[:, :, 0] > 42), :3] = violet[4]
        return out
    if style == "rails":
        out = np.zeros((32, 32, 4), dtype=np.uint8)
        wood = f32.make_ramp("#6D4826", contrast=0.95)
        iron = f32.make_ramp("#9DA8B4", contrast=1.05)
        for sy in (2, 10, 18, 26):
            out[sy:sy + 4, 2:30, :3] = wood[2]
            out[sy, 2:30, :3] = wood[4]
            out[sy + 3, 2:30, :3] = wood[0]
            out[sy:sy + 4, 2:30, 3] = 255
        for rx in (6, 23):
            out[:, rx:rx + 3, :3] = iron[3]
            out[:, rx, :3] = iron[5]
            out[:, rx + 2, :3] = iron[1]
            out[:, rx:rx + 3, 3] = 255
        return out
    if style == "bars":
        out = np.zeros((32, 32, 4), dtype=np.uint8)
        iron = f32.make_ramp("#747D88", contrast=1.05)
        for bx in (4, 15, 25):
            out[:, bx:bx + 3, :3] = iron[3]
            out[:, bx, :3] = iron[5]
            out[:, bx + 2, :3] = iron[0]
            out[:, bx:bx + 3, 3] = 255
        for by in (7, 23):
            out[by:by + 3, :, :3] = iron[2]
            out[by, :, :3] = iron[4]
            out[by:by + 3, :, 3] = 255
        return out
    return f32.tex_stone_rough(c1, seed=seed)


def build_world_blocks():
    """Generate 104 cohesive Faithful-32x-inspired Indraprastha city & world block textures."""
    specs = [
        # Asphalt, Roads, Sidewalks & Concretes (16)
        ("gray_concrete", "asphalt", "#3D434B", "#525862", "#2B3038"),
        ("black_concrete", "asphalt", "#1B1F26", "#2A3038", "#111419"),
        ("light_gray_concrete", "polished", "#A6ACB4", "#BFC5CC", "#838A92"),
        ("white_concrete", "polished", "#E8ECEF", "#FFFFFF", "#C6CCD4"),
        ("yellow_concrete", "polished", "#EAB308", "#FDE047", "#B45309"),
        ("cyan_concrete", "asphalt", "#255D66", "#357B85", "#18424A"),
        ("blue_concrete", "polished", "#1E5290", "#3B82F6", "#1E3A8A"),
        ("red_concrete", "polished", "#B8292F", "#EF4444", "#7F1D1D"),
        ("green_concrete", "polished", "#236653", "#34D399", "#14532D"),
        ("orange_concrete", "polished", "#C45B2C", "#FB923C", "#7C2D12"),
        ("lime_concrete", "polished", "#4D9E3A", "#84CC16", "#365314"),
        ("purple_concrete", "polished", "#6B21A8", "#A855F7", "#4C1D95"),
        ("magenta_concrete", "polished", "#9D174D", "#EC4899", "#701A75"),
        ("pink_concrete", "polished", "#EC4899", "#F9A8D4", "#BE185D"),
        ("light_blue_concrete", "polished", "#0284C7", "#38BDF8", "#075985"),
        ("brown_concrete", "asphalt", "#5E3F30", "#755240", "#3D251A"),
        # Stones & Masonry (22)
        ("stone", "stone", "#7F848A", "#686D73", "#969BA2"),
        ("smooth_stone", "polished", "#9CA1A8", "#B6BCC4", "#787E85"),
        ("smooth_stone_slab_side", "polished", "#9CA1A8", "#B6BCC4", "#666B72"),
        ("cobblestone", "cobble", "#767B82", "#8A9096", "#42464B"),
        ("mossy_cobblestone", "cobble", "#6F767B", "#4B7A43", "#3A4E36"),
        ("stone_bricks", "bricks", "#7E838A", "#52565E", "#969CA4"),
        ("cracked_stone_bricks", "bricks", "#747980", "#42464B", "#888E96"),
        ("mossy_stone_bricks", "bricks", "#6C786C", "#4E574D", "#839381"),
        ("andesite", "stone", "#86898B", "#6F7275", "#A0A4A6"),
        ("polished_andesite", "polished", "#898E92", "#A4A9AE", "#696E72"),
        ("diorite", "stone", "#CECDD2", "#A7A7AA", "#EFEFF2"),
        ("polished_diorite", "polished", "#D4D4D8", "#EDEDEF", "#A1A1AA"),
        ("granite", "stone", "#996A59", "#7C5242", "#B88471"),
        ("polished_granite", "polished", "#9E6E5C", "#BC8875", "#764E3E"),
        ("deepslate", "stone", "#44474F", "#282A2F", "#52555D"),
        ("polished_deepslate", "polished", "#474A52", "#565963", "#2A2C32"),
        ("deepslate_bricks", "bricks", "#40434B", "#26282E", "#545862"),
        ("deepslate_tiles", "tiles", "#383B42", "#1E2024", "#4A4E56"),
        ("blackstone", "stone", "#2B262D", "#1E1920", "#3D3640"),
        ("polished_blackstone_bricks", "bricks", "#312C34", "#1A161C", "#453E49"),
        ("bricks", "bricks", "#A2492F", "#C8C1B8", "#B95D42"),
        ("mud_bricks", "bricks", "#8C6A50", "#634835", "#A68065"),
        # Indian Terracotta, Sandstone, Quartz & Cloth (17)
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
        ("white_wool", "wool", "#E9ECEF", "#FFFFFF", "#CBD5E1"),
        ("red_wool", "wool", "#A62B2B", "#DC2626", "#7F1D1D"),
        ("blue_wool", "wool", "#2F4E8C", "#60A5FA", "#1E3A8A"),
        ("yellow_wool", "wool", "#E5B422", "#FEF08A", "#B45309"),
        # Woods & Libraries (13)
        ("oak_planks", "planks", "#A9804D", "#78572E", "#C49A63"),
        ("spruce_planks", "planks", "#715230", "#4E371E", "#8A6842"),
        ("dark_oak_planks", "planks", "#482F19", "#2B1B0D", "#593A20"),
        ("birch_planks", "planks", "#C8B77C", "#9E8D57", "#DECFA0"),
        ("jungle_planks", "planks", "#A37451", "#785134", "#BD8E6A"),
        ("acacia_planks", "planks", "#AD5D32", "#7C3F1E", "#C87446"),
        ("oak_log", "log_side", "#685134", "#4A3821", "#856B49"),
        ("oak_log_top", "log_top", "#B38A56", "#8E693C", "#5E482C"),
        ("spruce_log", "log_side", "#3E2814", "#25170B", "#52371D"),
        ("spruce_log_top", "log_top", "#7E5D38", "#5E4325", "#3A2512"),
        ("dark_oak_log", "log_side", "#3C2B1C", "#23190F", "#4D3927"),
        ("birch_log", "log_side", "#DDD8CE", "#3A3A3A", "#C4BEB3"),
        ("bookshelf", "bookshelf", "#8D6034", "#543214", "#D6AD59"),
        # Glass, Metals, Gems, Rails & Lighting (18)
        ("glass", "glass", "#94D4E4", "#C8DEE8", "#5BA6B8"),
        ("light_blue_stained_glass", "glass", "#5BB4E5", "#2563EB", "#BAE6FD"),
        ("gray_stained_glass", "glass", "#525A65", "#334155", "#94A3B8"),
        ("black_stained_glass", "glass", "#1E222A", "#0F172A", "#475569"),
        ("tinted_glass", "glass", "#2B2832", "#18151D", "#6B7280"),
        ("iron_block", "metal", "#DCE0E4", "#A4ACB5", "#FFFFFF"),
        ("gold_block", "metal", "#F2C641", "#B58517", "#FFF2A6"),
        ("copper_block", "metal", "#C26B4A", "#8B452C", "#E29070"),
        ("diamond_block", "gem", "#4CD9CF", "#259A9E", "#D6FFFA"),
        ("emerald_block", "gem", "#34C768", "#187B42", "#C4FFE0"),
        ("lapis_block", "gem", "#2853A6", "#1A336D", "#8DB4F7"),
        ("obsidian", "obsidian", "#231936", "#4C2A75", "#0E0918"),
        ("glowstone", "glowstone", "#F5B841", "#8C5214", "#FFF5B8"),
        ("sea_lantern", "sea_lantern", "#8AE2D0", "#327A78", "#E6FFFA"),
        ("redstone_lamp", "lamp_off", "#5E3820", "#2A180D", "#8A5636"),
        ("redstone_lamp_on", "lamp_on", "#E8B058", "#6B421A", "#FFF1BA"),
        ("rail", "rails", "#8E99A4", "#6D4826", "#3E2814"),
        ("iron_bars", "bars", "#747D88", "#2B3036", "#CBD5E1"),
        # Natural Coastal Terrain (12)
        ("grass_block_top", "grass_top", "#5E9D3B", "#4B822D", "#74B84E"),
        ("grass_block_side", "grass_side", "#5E9D3B", "#866043", "#6B4A31"),
        ("dirt", "dirt", "#866043", "#6B4A31", "#9C7354"),
        ("coarse_dirt", "dirt", "#755239", "#5B4A3B", "#946A4D"),
        ("sand", "sand", "#E4D7A5", "#D2C38E", "#F2E8BE"),
        ("red_sand", "sand", "#BE6422", "#9A4E16", "#D97E3B"),
        ("gravel", "gravel", "#827E7E", "#656161", "#9E9A9A"),
        ("clay", "stone", "#9EA4B0", "#89909C", "#B4BAC6"),
        ("oak_leaves", "leaves", "#4C872D", "#33611C", "#66A344"),
        ("spruce_leaves", "leaves", "#3E663D", "#284727", "#538052"),
        ("birch_leaves", "leaves", "#628E42", "#47692D", "#78A656"),
        ("water_still", "water", "#2684B8", "#3EA4DB", "#19618C")
    ]

    blk_dir = WORLD_32_SRC / "assets" / "minecraft" / "textures" / "block"
    bed_blk_dir = WORLD_32_SRC / "bedrock" / "textures" / "blocks"
    if blk_dir.exists():
        shutil.rmtree(blk_dir)
    if bed_blk_dir.exists():
        shutil.rmtree(bed_blk_dir)
    blk_dir.mkdir(parents=True, exist_ok=True)
    bed_blk_dir.mkdir(parents=True, exist_ok=True)

    imgs, titles = [], []
    for i, (bname, bstyle, c1, c2, c3) in enumerate(specs):
        arr = make_32x_block(bname, bstyle, c1, c2, c3, seed=i + 1)
        im = Image.fromarray(arr, mode="RGBA")
        im.save(blk_dir / f"{bname}.png", format="PNG", optimize=True)
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


def package_and_install_world_32x(imgs=None, titles=None):
    if imgs is None or titles is None:
        imgs, titles = build_world_blocks()
    PACKS_OUT.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)

    # Preview contact sheet of the Faithful 32x World Pack (NEAREST integer scaling -> razor sharp!)
    v4.create_grid(imgs, titles, cols=11, cell_w=96, cell_h=112).save(PREVIEWS / "world_32x_blocks_contact_sheet.png", optimize=True)

    pack_icon = CREATIVE / "source" / "icons" / "server-icon.png"

    # 1. Build GTM_Indraprastha_World_32x_Java.zip (Java 1.21+ / Paper 26.3 compatible)
    java_zip_path = PACKS_OUT / "GTM_Indraprastha_World_32x_Java.zip"
    mcmeta = {
        "pack": {
            "pack_format": 48,
            "supported_formats": {"min_inclusive": 15, "max_inclusive": 999},
            "min_format": 15,
            "max_format": 999,
            "description": "\u00a76GTM Indraprastha Faithful 32x \u00a78| \u00a7eBlocks, Models & Pixel Icons"
        }
    }
    blk_dir = WORLD_32_SRC / "assets" / "minecraft" / "textures" / "block"
    icons_root = CREATIVE / "source" / "icons"
    with ZipFile(java_zip_path, "w", ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps(mcmeta, indent=2) + "\n")
        if pack_icon.exists():
            z.write(pack_icon, "pack.png")
        for p in sorted(blk_dir.glob("*.png")):
            z.write(p, f"assets/minecraft/textures/block/{p.name}")
        for p in sorted(s3d.TEX_32_DIR.glob("*.png")):
            z.write(p, f"assets/gtm/textures/item/{p.name}")
            z.write(p, f"assets/sdcraft/textures/item/{p.name}")
        if s3d.ATLAS_PATH.exists():
            z.write(s3d.ATLAS_PATH, "assets/gtm/textures/item/gtm_master_atlas_32x.png")
        # Bundle food/weapon/equipment sprite icons into GTM namespace too
        for sub in ("food", "weapons", "equipment", "transport", "furniture", "festivals"):
            sdir = icons_root / sub
            if sdir.exists():
                for p in sorted(sdir.rglob("*.png")):
                    rel = p.relative_to(icons_root).as_posix()
                    z.write(p, f"assets/gtm/textures/item/icons/{rel}")

    # 2. Build GTM_Indraprastha_World_32x_Bedrock.mcpack (Geyser crossplay)
    bed_pack_path = PACKS_OUT / "GTM_Indraprastha_World_32x_Bedrock.mcpack"
    manifest_bed = {
        "format_version": 2,
        "header": {
            "name": "GTM Indraprastha Faithful 32x",
            "description": "Faithful 32x Inspired Indraprastha World, Model Textures & Pixel Icons",
            "uuid": "9e8d7c6b-5a4f-4132-89ab-cdef01234567",
            "version": [2, 0, 0],
            "min_engine_version": [1, 21, 0]
        },
        "modules": [{
            "type": "resources",
            "uuid": "1a2b3c4d-5e6f-4789-abcd-ef0123456789",
            "version": [2, 0, 0]
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
        if s3d.ATLAS_PATH.exists():
            z.write(s3d.ATLAS_PATH, "textures/gtm/gtm_master_atlas_32x.png")

    # 3. Install locally into %APPDATA%/.minecraft/resourcepacks/
    mc_rp_dir = Path.home() / "AppData" / "Roaming" / ".minecraft" / "resourcepacks"
    installed_msg = "Skipped (no local .minecraft dir)"
    if mc_rp_dir.parent.exists():
        mc_rp_dir.mkdir(parents=True, exist_ok=True)
        dest_rp = mc_rp_dir / "GTM_Indraprastha_World_32x_Java.zip"
        shutil.copy2(java_zip_path, dest_rp)
        installed_msg = str(dest_rp)

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

    iso_rp = Path(r"d:\Games\SDCRAFT\sdcraft_isolated\resourcepacks")
    if iso_rp.exists():
        shutil.copy2(java_zip_path, iso_rp / "GTM_Indraprastha_World_32x_Java.zip")

    print(f"SUCCESS: Built {len(imgs)} Faithful 32x World blocks + {len(list(s3d.TEX_32_DIR.glob('*.png')))} model 32x32 textures!")
    print(f"  - Java Pack: {java_zip_path}")
    print(f"  - Bedrock Pack: {bed_pack_path}")
    print(f"  - Installed locally at: {installed_msg}")


if __name__ == "__main__":
    s3d.build_shared_atlas()
    imgs, titles = build_world_blocks()
    package_and_install_world_32x(imgs, titles)
