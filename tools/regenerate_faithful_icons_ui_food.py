#!/usr/bin/env python3
"""
Regenerate ALL Domain 1 (Server Icon, 32 Brands, 24 Phone Apps, 33 HUD Assets)
and Domain 5 (30 Food Sprite Icons + Upgraded 30 Food 3D Models & Faithful 64x64 Food Atlas)
in a unified Faithful-32x-inspired hand-pixelled aesthetic (zero blurry vectors/gradients).
"""
import hashlib
import json
import math
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageColor, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import faithful_32x_palette as f32
import studio_3d_engine as s3d
import food_art
import validate_creative_r4 as v4

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
SOURCE = CREATIVE / "source"
MANIFESTS = CREATIVE / "manifests"
PREVIEWS = CREATIVE / "previews"


def hex_ramp(h: str, contrast: float = 1.0):
    r = f32.make_ramp(h, contrast=contrast)
    return [tuple(int(v) for v in c) + (255,) for c in r]


# Crisp 3x5 bitmap pixel font for HUD text, numbers & badges (exact 1px crisp pixels!)
FONT_3X5 = {
    'A': ["010", "101", "111", "101", "101"], 'B': ["110", "101", "110", "101", "110"],
    'C': ["011", "100", "100", "100", "011"], 'D': ["110", "101", "101", "101", "110"],
    'E': ["111", "100", "110", "100", "111"], 'F': ["111", "100", "110", "100", "100"],
    'G': ["011", "100", "101", "101", "011"], 'H': ["101", "101", "111", "101", "101"],
    'I': ["111", "010", "010", "010", "111"], 'J': ["001", "001", "001", "101", "010"],
    'K': ["101", "101", "110", "101", "101"], 'L': ["100", "100", "100", "100", "111"],
    'M': ["10001", "11011", "10101", "10001", "10001"], 'N': ["110", "101", "101", "101", "101"],
    'O': ["010", "101", "101", "101", "010"], 'P': ["110", "101", "110", "100", "100"],
    'Q': ["010", "101", "101", "111", "011"], 'R': ["110", "101", "110", "101", "101"],
    'S': ["011", "100", "010", "001", "110"], 'T': ["111", "010", "010", "010", "010"],
    'U': ["101", "101", "101", "101", "111"], 'V': ["101", "101", "101", "101", "010"],
    'W': ["10001", "10001", "10101", "11011", "10001"], 'X': ["101", "101", "010", "101", "101"],
    'Y': ["101", "101", "010", "010", "010"], 'Z': ["111", "001", "010", "100", "111"],
    '0': ["111", "101", "101", "101", "111"], '1': ["010", "110", "010", "010", "111"],
    '2': ["111", "001", "111", "100", "111"], '3': ["111", "001", "111", "001", "111"],
    '4': ["101", "101", "111", "001", "001"], '5': ["111", "100", "111", "001", "111"],
    '6': ["111", "100", "111", "101", "111"], '7': ["111", "001", "001", "010", "010"],
    '8': ["111", "101", "111", "101", "111"], '9': ["111", "101", "111", "001", "111"],
    '+': ["000", "010", "111", "010", "000"], '-': ["000", "000", "111", "000", "000"],
    ':': ["000", "010", "000", "010", "000"], '/': ["001", "001", "010", "100", "100"],
    ' ': ["000", "000", "000", "000", "000"], '₹': ["111", "010", "111", "010", "001"],
}


def draw_pixel_text(sp: s3d.PixelSprite, text: str, x: int, y: int, col, scale: int = 1, shadow_col=None):
    cx = x
    for ch in text.upper():
        pat = FONT_3X5.get(ch, FONT_3X5[' '])
        cw = len(pat[0])
        for ry, row in enumerate(pat):
            for rx, bit in enumerate(row):
                if bit == '1':
                    if shadow_col is not None:
                        sp.rect(cx + rx * scale + scale, y + ry * scale + scale, scale, scale, shadow_col)
                    sp.rect(cx + rx * scale, y + ry * scale, scale, scale, col)
        cx += (cw + 1) * scale


def build_server_icon() -> Path:
    """64x64 Opaque RGB Faithful-32x Pixel-Art Server Icon (GTM Golden Shield + Sea-Link Bridge)."""
    out_path = SOURCE / "icons" / "server-icon.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sp = s3d.PixelSprite(64, 64)

    # Quantized dusk harbor sky bands + subtle pixel stars
    sky_bands = [(0, 12, "#0B1524"), (12, 24, "#132944"), (24, 34, "#1D4663"), (34, 42, "#B4532A"), (42, 47, "#E2953B")]
    for y0, y1, hcol in sky_bands:
        sp.rect(0, y0, 64, y1 - y0, hcol)
    for sx, sy in [(8, 6), (22, 9), (44, 5), (55, 11), (14, 16), (49, 17)]:
        sp.px(sx, sy, "#FFF8D6")

    # Stepped pixel skyline behind bridge
    for bx, bw, bh in [(6, 6, 16), (12, 5, 22), (17, 7, 13), (40, 6, 15), (46, 7, 21), (53, 5, 12)]:
        sp.rect(bx, 47 - bh, bw, bh, "#16202C")
        for wy in range(47 - bh + 2, 46, 3):
            for wx in range(bx + 1, bx + bw - 1, 2):
                sp.px(wx, wy, "#E8B954" if (wx + wy) % 3 == 0 else "#28394D")

    # Ocean waves (47..63)
    sea = hex_ramp("#175C6E")
    sp.rect(0, 47, 64, 17, sea[1])
    for y in range(48, 63, 3):
        for x in range((y % 6), 64, 7):
            sp.rect(x, y, 4, 1, sea[4] if y < 53 else sea[3])

    # Chamfered Outer Golden Shield Frame
    gold = hex_ramp("#D6AD59", contrast=1.05)
    for p in range(64):
        for q in range(64):
            dist_edge = min(p, 63 - p, q, 63 - q)
            if p + q >= 112 or (63 - p) + q >= 112:
                sp.px(p, q, "#0D1118")
            elif dist_edge == 0 or (p + q == 111) or ((63 - p) + q == 111):
                sp.px(p, q, "#0D1118")
            elif dist_edge == 1:
                sp.px(p, q, gold[5] if (p < 32 or q < 32) else gold[1])
            elif dist_edge == 2:
                sp.px(p, q, gold[3] if (p < 32 or q < 32) else gold[2])

    # Twin Sea-Link Cable-Stayed Pylons + Suspension Cables
    sp.rect(20, 20, 3, 27, gold[4])
    sp.rect(22, 20, 1, 27, gold[1])
    sp.rect(41, 20, 3, 27, gold[4])
    sp.rect(43, 20, 1, 27, gold[1])
    for i in range(12):
        sp.line(21, 21 + i, max(5, 21 - i * 2), 45, gold[4])
        sp.line(21, 21 + i, min(32, 21 + i), 45, gold[3])
        sp.line(42, 21 + i, max(32, 42 - i), 45, gold[4])
        sp.line(42, 21 + i, min(58, 42 + i * 2), 45, gold[3])
    # Road deck
    sp.rect(4, 45, 56, 3, "#1D242E")
    sp.rect(4, 44, 56, 1, gold[5])
    # Bold pixel "GTM" plaque in center sky
    sp.rect(16, 9, 32, 9, "#111722")
    sp.rect(16, 8, 32, 1, gold[4])
    sp.rect(16, 18, 32, 1, gold[1])
    draw_pixel_text(sp, "GTM", 19, 11, gold[5], scale=2, shadow_col="#0A0E14")

    sp.to_image().convert("RGB").save(out_path, format="PNG", optimize=True)
    return out_path


def _brand_pixel_art(bid: str, primary: str, accent: str) -> s3d.PixelSprite:
    """Craft a unique 64x64 Faithful pixel-art corporate/gang emblem on transparent background."""
    sp = s3d.PixelSprite(64, 64)
    pr = hex_ramp(primary, contrast=1.05)
    ac = hex_ramp(accent, contrast=1.05)
    gd = hex_ramp("#D6AD59", contrast=1.05)
    sv = hex_ramp("#CBD5E1", contrast=1.05)
    wh = (248, 250, 252, 255)
    dk = (16, 20, 30, 255)

    def crest_shield(c_fill, c_trim):
        for y in range(8, 56):
            half = 22 if y < 34 else max(3, int(22 * (1.0 - ((y - 34) / 23.0) ** 1.2)))
            for x in range(32 - half, 32 + half):
                if abs(x - 32) >= half - 2 or y <= 10:
                    sp.px(x, y, c_trim[5] if x < 32 or y <= 11 else c_trim[2])
                else:
                    sp.px(x, y, c_fill[3] if x < 34 else c_fill[2])

    if bid == "wahindra":
        # Sculpted bull head crest
        crest_shield(hex_ramp("#232A34"), hex_ramp("#D6AD59"))
        sp.line(13, 18, 21, 27, sv[5], 3)
        sp.line(51, 18, 43, 27, sv[3], 3)
        sp.shade_bevel("#AD5637", 21, 24, 22, 20, corner_cut=3)
        sp.rect(25, 31, 4, 3, "#FEF08A")
        sp.rect(35, 31, 4, 3, "#FEF08A")
        sp.rect(28, 39, 8, 5, gd[4])
    elif bid == "tavara":
        crest_shield(hex_ramp("#1D4E89"), sv)
        # Bold electric lightning bolt
        for y in range(15, 49):
            cx = 34 - int((y - 15) * 0.45) if y < 32 else 38 - int((y - 32) * 0.7)
            w = 7 if y < 32 else 6
            sp.rect(cx - w // 2, y, w, 1, "#38BDF8" if y < 32 else "#FACC15")
    elif bid == "maruva":
        sp.line(8, 27, 22, 27, sv[4], 3)
        sp.line(10, 32, 22, 32, sv[2], 2)
        sp.line(42, 27, 56, 27, sv[4], 3)
        sp.line(42, 32, 54, 32, sv[2], 2)
        sp.disc(32, 32, 16, "#1E5240")
        sp.disc(32, 32, 13, "#236653")
        sp.disc(32, 32, 9, "#151B20")
        sp.line(32, 20, 32, 44, gd[5], 2)
        sp.line(23, 32, 41, 32, gd[4], 2)
    elif bid == "toyora":
        for cx, cy, r in ((22, 32, 12), (42, 32, 12), (32, 32, 14)):
            for y in range(cy - r - 1, cy + r + 2):
                for x in range(cx - r - 1, cx + r + 2):
                    d = math.hypot(x - cx, y - cy)
                    if r - 2.6 <= d <= r:
                        sp.px(x, y, gd[5 if x + y < 60 else 2] if cx == 32 else sv[4 if x + y < 64 else 1])
    elif bid == "royal_iron":
        sp.line(12, 24, 52, 24, gd[4], 4)
        sp.line(16, 30, 48, 30, gd[2], 3)
        sp.disc(32, 33, 13, "#151B20")
        sp.disc(32, 33, 10, gd[4])
        sp.rect(24, 24, 16, 4, gd[5])
        sp.rect(24, 21, 3, 3, gd[5])
        sp.rect(31, 20, 3, 4, gd[5])
        sp.rect(38, 21, 3, 3, gd[5])
        draw_pixel_text(sp, "RI", 28, 30, dk, scale=2)
    elif bid == "veero":
        crest_shield(hex_ramp("#9E1B24"), sv)
        sp.line(18, 16, 32, 46, "#EF4444", 5)
        sp.line(46, 16, 32, 46, "#DC2626", 5)
        sp.line(34, 18, 28, 33, "#FDE047", 3)
        sp.line(28, 33, 36, 33, "#FDE047", 2)
    elif bid == "hondo":
        for i in range(5):
            y0 = 16 + i * 6
            sp.line(12 + i * 2, y0 + 8, 52 - i * 2, 16 + i * 3, sv[5 - min(3, i // 2)], 3)
            sp.line(14 + i * 2, y0 + 10, 48 - i * 2, 18 + i * 3, pr[3], 2)
    elif bid == "quoggle":
        sp.disc(28, 28, 17, "#1E293B")
        for y in range(12, 45):
            for x in range(12, 45):
                d = math.hypot(x - 28, y - 28)
                if 10 <= d <= 16:
                    if x < 28 and y < 28:
                        sp.px(x, y, "#EF4444")
                    elif x >= 28 and y < 28:
                        sp.px(x, y, "#3B82F6")
                    elif x < 28 and y >= 28:
                        sp.px(x, y, "#FACC15")
                    else:
                        sp.px(x, y, "#22C55E")
                elif d < 10:
                    sp.px(x, y, "#7DD3FC" if x + y < 52 else "#38BDF8")
        sp.line(39, 39, 54, 54, sv[3], 6)
    elif bid == "amazzo":
        sp.shade_bevel("#D98A36", 14, 14, 36, 30, corner_cut=2)
        sp.rect(28, 14, 8, 12, "#F5F5DC")
        sp.line(15, 48, 32, 54, gd[5], 3)
        sp.line(32, 54, 49, 46, gd[4], 3)
        sp.rect(46, 44, 5, 5, gd[5])
    elif bid == "flippit":
        sp.shade_bevel("#2563EB", 14, 14, 36, 36, corner_cut=4)
        sp.rect(10, 22, 10, 3, "#FACC15")
        sp.rect(8, 29, 12, 3, "#FACC15")
        sp.rect(12, 36, 10, 3, "#FACC15")
        draw_pixel_text(sp, "F", 28, 22, "#FACC15", scale=3, shadow_col="#1E3A8A")
    elif bid == "arkpay":
        sp.shade_bevel("#D6AD59", 18, 14, 34, 24, corner_cut=2)
        sp.shade_bevel("#236653", 12, 24, 36, 26, corner_cut=2)
        sp.rect(17, 30, 8, 6, gd[4])
        draw_pixel_text(sp, "₹", 32, 29, gd[5], scale=2)
    elif bid == "zomatoo":
        for y in range(16, 40):
            r = int(math.sqrt(max(0, 20 * 20 - (38 - y) ** 2)))
            sp.rect(32 - r, y, 2 * r, 1, "#DC2626" if y < 28 else "#B91C1C")
        sp.rect(30, 12, 4, 4, sv[5])
        sp.rect(10, 40, 44, 5, sv[4])
        sp.line(25, 22, 39, 36, wh, 2)
        sp.line(39, 22, 25, 36, wh, 2)
    elif bid == "swiffy":
        sp.disc(32, 26, 17, "#E27D24")
        sp.disc(32, 26, 13, "#AD5637")
        sp.line(20, 37, 32, 54, "#E27D24", 4)
        sp.line(44, 37, 32, 54, "#AD5637", 4)
        sp.line(35, 16, 26, 28, "#FFF3C4", 3)
        sp.line(26, 28, 36, 28, "#FFF3C4", 2)
        sp.line(36, 28, 29, 39, "#FACC15", 3)
    elif bid == "indra_fuel":
        for dy in range(-22, 23):
            w = 22 - abs(dy)
            sp.rect(32 - w, 32 + dy, w * 2, 1, "#202A34" if abs(dy) < 19 else gd[4])
        sp.disc(32, 36, 7, "#2DD4BF")
        sp.line(32, 18, 26, 33, "#99F6E4", 4)
        sp.line(32, 18, 38, 33, "#2DD4BF", 4)
    elif bid == "indra_bank":
        sp.rect(12, 44, 40, 6, gd[4])
        sp.rect(15, 24, 5, 20, sv[4])
        sp.rect(29, 24, 6, 20, sv[4])
        sp.rect(44, 24, 5, 20, sv[4])
        for dy in range(11):
            sp.rect(10 + dy * 2, 22 - dy, 44 - dy * 4, 2, gd[4 if dy > 3 else 5])
        sp.disc(32, 38, 10, gd[3])
        draw_pixel_text(sp, "₹", 29, 33, dk, scale=2)
    elif bid == "vayu_bharat":
        sp.line(10, 44, 54, 14, "#38BDF8", 6)
        sp.line(54, 14, 36, 52, "#0284C7", 5)
        sp.line(10, 44, 36, 52, "#0369A1", 4)
        sp.line(22, 38, 52, 15, wh, 2)
    elif bid == "skyindra":
        sp.line(8, 16, 56, 12, sv[4], 3)
        sp.rect(31, 14, 2, 12, gd[4])
        sp.shade_bevel("#236653", 14, 26, 36, 24, corner_cut=4)
        sp.rect(19, 31, 11, 10, "#7DD3FC")
        sp.rect(34, 31, 11, 10, "#7DD3FC")
    elif bid == "cinevista":
        sp.disc(28, 32, 18, gd[4])
        sp.disc(28, 32, 15, gd[3])
        for hx, hy in [(28, 22), (28, 42), (18, 32), (38, 32), (28, 32)]:
            sp.disc(hx, hy, 4, "#151B20")
        sp.line(38, 38, 54, 48, "#DC2626", 5)
    elif bid == "d_bazaar":
        sp.rect(18, 14, 28, 3, sv[5])
        sp.rect(18, 14, 3, 14, sv[4])
        sp.rect(43, 14, 3, 14, sv[3])
        sp.shade_bevel("#22C55E", 12, 26, 40, 24, corner_cut=3)
        sp.disc(32, 38, 6, "#FACC15")
    elif bid == "amora":
        for ox, oy, rx in [(0, -4, 7), (-10, 4, 6), (10, 4, 6), (-6, 12, 5), (6, 12, 5)]:
            sp.disc(32 + ox, 32 + oy, rx, "#D97706")
            sp.disc(32 + ox, 32 + oy, rx - 2, "#F59E0B")
        sp.disc(32, 34, 6, "#FEF08A")
    elif bid == "rang_bharat":
        sp.line(18, 50, 42, 14, "#16A34A", 6)
        sp.disc(38, 24, 11, "#22C55E")
        sp.disc(38, 24, 7, "#3B82F6")
        sp.disc(38, 24, 4, "#D6AD59")
        sp.disc(38, 24, 2, dk)
    elif bid == "jyon":
        sp.shade_bevel("#252F38", 14, 12, 36, 40, corner_cut=4)
        sp.rect(24, 12, 16, 10, "#151B20")
        sp.line(16, 28, 32, 40, gd[5], 4)
        sp.line(32, 40, 48, 28, gd[4], 4)
    elif bid == "airwave":
        sp.line(32, 18, 20, 52, "#38BDF8", 3)
        sp.line(32, 18, 44, 52, "#0284C7", 3)
        sp.rect(23, 40, 18, 3, "#38BDF8")
        sp.disc(32, 16, 4, "#BAE6FD")
        for r in (11, 17):
            sp.rect(32 - r, 10, 2, 14, "#38BDF8")
            sp.rect(32 + r - 2, 10, 2, 14, "#38BDF8")
    elif bid == "indra24":
        sp.disc(32, 32, 16, "#DC2626")
        sp.disc(32, 32, 12, "#EF4444")
        sp.rect(8, 28, 48, 8, "#151B20")
        draw_pixel_text(sp, "24", 24, 27, wh, scale=2)
    elif bid == "jan_awaaz":
        sp.shade_bevel("#E2D4B7", 14, 14, 34, 36, corner_cut=2)
        sp.rect(18, 20, 26, 4, "#151B20")
        sp.rect(18, 28, 18, 3, "#475569")
        sp.rect(18, 34, 22, 3, "#475569")
        sp.line(34, 44, 52, 16, gd[5], 4)
    elif bid == "indra_metro":
        sp.disc(32, 32, 20, "#236653")
        sp.disc(32, 32, 15, "#0F172A")
        sp.shade_bevel("#DCE6F2", 21, 18, 22, 28, corner_cut=4)
        sp.rect(24, 22, 16, 9, "#38BDF8")
        sp.rect(24, 37, 4, 4, "#FEF08A")
        sp.rect(36, 37, 4, 4, "#FEF08A")
    elif bid == "indra_suburban":
        sp.shade_bevel("#D6AD59", 17, 12, 30, 38, corner_cut=3)
        sp.rect(20, 24, 24, 6, "#7E222B")
        sp.rect(21, 16, 9, 7, "#1E293B")
        sp.rect(34, 16, 9, 7, "#1E293B")
        sp.rect(20, 38, 5, 4, "#FEF08A")
        sp.rect(39, 38, 5, 4, "#FEF08A")
        sp.rect(14, 52, 36, 3, sv[3])
    elif bid == "skylink":
        sp.line(8, 16, 56, 20, sv[4], 2)
        sp.shade_bevel("#236653", 12, 22, 18, 16, corner_cut=2)
        sp.shade_bevel("#38BDF8", 34, 25, 18, 16, corner_cut=2)
        sp.rect(10, 48, 44, 4, "#0284C7")
    elif bid == "maya_residences":
        sp.disc(32, 30, 18, gd[4])
        sp.rect(28, 12, 8, 36, "#151B20")
        sp.rect(18, 22, 7, 26, "#1E293B")
        sp.rect(39, 25, 7, 23, "#1E293B")
        sp.rect(12, 48, 40, 4, gd[5])
    elif bid == "sd_motors":
        crest_shield(hex_ramp("#181E26"), gd)
        for y in range(12, 24, 4):
            for x in range(18 + ((y // 4) % 2) * 4, 46, 8):
                sp.rect(x, y, 4, 4, wh)
        sp.line(18, 36, 46, 26, gd[5], 4)
        draw_pixel_text(sp, "SD", 23, 39, gd[5], scale=2)
    elif bid == "black_lotus":
        sp.disc(32, 34, 16, "#1A0D18")
        for dx, dy in [(0, -14), (-11, -7), (11, -7), (-14, 3), (14, 3)]:
            sp.disc(32 + dx, 32 + dy, 8, "#BE123C")
            sp.disc(32 + dx, 32 + dy, 5, "#FB7185")
        sp.disc(32, 34, 6, "#DC2626")
    else:  # gtm
        crest_shield(hex_ramp("#236653"), gd)
        sp.rect(20, 18, 3, 22, gd[4])
        sp.rect(41, 18, 3, 22, gd[4])
        sp.line(13, 38, 51, 38, gd[5], 3)
        sp.line(21, 19, 32, 38, gd[5], 2)
        sp.line(42, 19, 32, 38, gd[5], 2)

    sp.add_outline(col=dk, diagonal=False)
    return sp


def regenerate_brands_and_ui():
    """Regenerate 32 Brands, 24 Phone App Icons, and 33 HUD Assets in pure Faithful 32x Pixel Art."""
    brands_meta = [
        ("wahindra", "Wahindra Motors", "Automotive", "Rugged All-Terrain & Utility", "#AD5637", "#151B20"),
        ("tavara", "Tavara Heavy Industries", "Automotive", "Electric Transit & Heavy Vehicles", "#2680EB", "#151B20"),
        ("maruva", "Maruva City Car", "Automotive", "High-Efficiency Compact Cars", "#236653", "#151B20"),
        ("toyora", "Toyora Motors", "Automotive", "Durable Executive & Fleet Utility", "#D6AD59", "#151B20"),
        ("royal_iron", "Royal Iron Motorcycles", "Motorcycles", "Authentic Heavy Thump Cruisers", "#B28834", "#0D1115"),
        ("veero", "Veero Roadsters", "Motorcycles", "Everyday Urban Commuter Bikes", "#DC3545", "#151B20"),
        ("hondo", "Hondo Scooters", "Motorcycles", "Agile Fuel-Efficient City Scooters", "#2680EB", "#151B20"),
        ("quoggle", "Quoggle Systems", "Technology", "Search, Cloud & Intelligent Navigation", "#2680EB", "#FFFFFF"),
        ("amazzo", "Amazzo Prime Hub", "Logistics", "Same-Day Commerce & Warehousing", "#D6AD59", "#151B20"),
        ("flippit", "Flippit Express", "E-Commerce", "Electronics & Flash Shopping", "#2680EB", "#D6AD59"),
        ("arkpay", "ARK Pay UPI", "Financial", "Instant Contactless Municipal Banking", "#236653", "#D6AD59"),
        ("zomatoo", "Zomatoo Food Express", "Delivery", "24/7 Restaurant Courier Delivery", "#DC3545", "#FFFFFF"),
        ("swiffy", "Swiffy Instant Groceries", "Delivery", "Hyper-Local 10-Minute Grocery Delivery", "#AD5637", "#FFFFFF"),
        ("indra_fuel", "Indraprastha Petroleum", "Energy", "State Refineries & High-Octane Fuel", "#2680EB", "#D6AD59"),
        ("indra_bank", "First National Bank of Indra", "Banking", "Authoritative Vault Accounts & Escrow", "#D6AD59", "#0D1115"),
        ("vayu_bharat", "Vayu Bharat Airlines", "Aviation", "Coastal & International Air Carrier", "#2680EB", "#FFFFFF"),
        ("skyindra", "SkyIndra Ropeways", "Transit", "Harbour Aerial Cableway Transit", "#236653", "#D2B997"),
        ("cinevista", "CineVista Studios", "Entertainment", "Bollywood Cinema & Film Production", "#D6AD59", "#DC3545"),
        ("d_bazaar", "D-Bazaar Megastores", "Retail", "Multi-Floor Wholesale Supermarkets", "#236653", "#FFFFFF"),
        ("amora", "Amora Indian Weaves", "Fashion", "Heritage Handloom & Modern Silk Wear", "#AD5637", "#D6AD59"),
        ("rang_bharat", "Rang Bharat Textiles", "Fashion", "Festival Costumes & Ceremonial Silks", "#D6AD59", "#236653"),
        ("jyon", "Jyon Urban Streetwear", "Fashion", "Youth Streetwear & Athletic Apparel", "#252F38", "#E8C87E"),
        ("airwave", "AirWave 5G Cellular", "Telecom", "High-Bandwidth City Telecom Network", "#2680EB", "#FFFFFF"),
        ("indra24", "Indra 24 News", "Media", "24-Hour Metropolitan Breaking News", "#DC3545", "#FFFFFF"),
        ("jan_awaaz", "Jan Awaaz Times", "Media", "Civic Journalism & Citizen Radio", "#151B20", "#D2B997"),
        ("indra_metro", "Indra Metro Rail", "Transit", "Rapid Underground & Elevated Commuter", "#2680EB", "#236653"),
        ("indra_suburban", "Indra Suburban Railway", "Transit", "Lifeline Coastal Local Train Network", "#AD5637", "#D6AD59"),
        ("skylink", "SkyLink Cable Car", "Transit", "Suspended Harbour Gondola Network", "#236653", "#FFFFFF"),
        ("maya_residences", "Maya Luxury Residences", "Real Estate", "Prime Waterfront High-Rise Condos", "#D2B997", "#151B20"),
        ("sd_motors", "SD Craft Motorsport", "Dealership", "Exclusive Luxury Supercar Showroom", "#D6AD59", "#0D1115"),
        ("black_lotus", "Black Lotus Syndicate", "Underground", "Shadow Port Cartel & Contraband", "#0D1115", "#DC3545"),
        ("gtm", "Grand Theft Mumbai", "Master Brand", "Metropolitan Roleplay Universe", "#D6AD59", "#236653")
    ]
    bdir = SOURCE / "branding"
    bdir.mkdir(parents=True, exist_ok=True)
    b_manifest = []
    b_imgs, b_titles = [], []
    for bid, name, sector, tagline, primary, accent in brands_meta:
        sp = _brand_pixel_art(bid, primary, accent)
        png_path = bdir / f"{bid}.png"
        sp.save(png_path, target_size=256)
        b_imgs.append(Image.open(png_path))
        b_titles.append(name)
        b_manifest.append({
            "id": bid, "name": name, "sector": sector, "tagline": tagline,
            "primary_hex": primary, "accent_hex": accent,
            "svg": f"creative/source/branding/{bid}.svg",
            "png": f"creative/source/branding/{bid}.png",
            "dimensions_px": [256, 256],
            "style": "faithful_32x_pixel_crest",
            "sha256": hashlib.sha256(png_path.read_bytes()).hexdigest()
        })
    (MANIFESTS / "brands.json").write_text(json.dumps(b_manifest, indent=2) + "\n", encoding="utf-8")
    v4.create_grid(b_imgs, b_titles, cols=8, cell_w=132, cell_h=150).save(PREVIEWS / "brands_contact_sheet.png", optimize=True)

    # 24 Phone App Icons (32x32 Faithful Pixel Art -> 4x NEAREST = 128x128 RGBA)
    apps = [
        ("quoggle", "Quoggle", "#1D4ED8"), ("amazzo", "Amazzo", "#B45309"),
        ("flippit", "Flippit", "#2563EB"), ("arkpay", "ARK Pay", "#1F6E54"),
        ("zomatoo", "Zomatoo", "#B91C1C"), ("swiffy", "Swiffy", "#C2410C"),
        ("fashion", "Vogue Indra", "#7E22CE"), ("property", "Properties", "#0F766E"),
        ("car_app", "Motor Mile", "#991B1B"), ("maps", "City GPS", "#15803D"),
        ("garage", "My Garage", "#1E40AF"), ("bank", "Indra Bank", "#92400E"),
        ("loans", "Municipal Loans", "#1E293B"), ("taxi", "City Cabs", "#CA8A04"),
        ("transport", "Metro & Rail", "#0369A1"), ("news", "Indra 24", "#334155"),
        ("police", "SDPD Law", "#1E3A8A"), ("medical", "Trauma Bay", "#991B1B"),
        ("events", "Festivals", "#9D174D"), ("missions", "Contracts", "#7C2D12"),
        ("careers", "City Jobs", "#3F3F46"), ("contacts", "Contacts", "#0E7490"),
        ("keys", "Key Fob", "#1F2937"), ("settings", "Settings", "#374151"),
    ]
    pdir = SOURCE / "icons"
    pdir.mkdir(parents=True, exist_ok=True)
    p_manifest = []
    p_imgs, p_titles = [], []
    for aid, title, bg_hex in apps:
        sp = s3d.PixelSprite(32, 32)
        sp.shade_bevel(bg_hex, 2, 2, 28, 28, corner_cut=2)
        if aid == "quoggle":
            sp.disc(14, 14, 7, "#38BDF8"); sp.disc(14, 14, 4, "#FFFFFF")
            sp.rect(9, 9, 4, 4, "#EF4444"); sp.rect(15, 9, 4, 4, "#FACC15")
            sp.line(19, 19, 25, 25, "#E2E8F0", 3)
        elif aid == "amazzo":
            sp.shade_bevel("#D98A36", 8, 8, 16, 13, corner_cut=1)
            sp.rect(14, 8, 4, 5, "#FEF3C7")
            sp.line(8, 24, 16, 26, "#FACC15", 2); sp.line(16, 26, 24, 23, "#FACC15", 2)
        elif aid == "flippit":
            sp.shade_bevel("#38BDF8", 9, 8, 14, 16, corner_cut=1)
            draw_pixel_text(sp, "F", 13, 12, "#FACC15", scale=2)
        elif aid == "arkpay":
            sp.shade_bevel("#D6AD59", 9, 9, 16, 10, corner_cut=1)
            sp.shade_bevel("#236653", 6, 13, 17, 11, corner_cut=1)
            sp.rect(9, 17, 4, 3, "#FDE047")
        elif aid == "zomatoo":
            sp.disc(16, 17, 8, "#E2E8F0"); sp.rect(8, 18, 16, 6, bg_hex)
            sp.rect(6, 18, 20, 2, "#F8FAFC")
            sp.line(13, 12, 19, 17, "#991B1B", 1); sp.line(19, 12, 13, 17, "#991B1B", 1)
        elif aid == "swiffy":
            sp.disc(16, 14, 7, "#FEF3C7"); sp.line(17, 9, 13, 15, "#EA580C", 2); sp.line(13, 15, 18, 15, "#EA580C", 1); sp.line(18, 15, 14, 21, "#EA580C", 2)
        elif aid == "fashion":
            sp.line(10, 14, 16, 10, "#F5D0FE", 2); sp.line(16, 10, 22, 14, "#F5D0FE", 2)
            sp.shade_bevel("#EC4899", 9, 14, 14, 12, corner_cut=1)
            sp.rect(14, 14, 4, 12, "#FDF4FF")
        elif aid == "property":
            for i in range(6): sp.rect(8 + i, 14 - i, 16 - 2 * i, 2, "#D6AD59")
            sp.shade_bevel("#E2E8F0", 9, 15, 14, 10, corner_cut=0)
            sp.rect(14, 19, 4, 6, "#78350F")
        elif aid == "car_app" or aid == "taxi":
            col_c = "#F5B800" if aid == "taxi" else "#EF4444"
            sp.shade_bevel(col_c, 6, 14, 20, 8, corner_cut=1)
            sp.shade_bevel(col_c, 9, 9, 14, 6, corner_cut=2)
            sp.rect(11, 10, 10, 4, "#38BDF8")
            sp.disc(10, 22, 3, "#111827"); sp.disc(22, 22, 3, "#111827")
        elif aid == "maps":
            sp.rect(7, 8, 18, 16, "#BBF7D0")
            sp.line(7, 20, 25, 10, "#94A3B8", 3)
            sp.disc(16, 12, 4, "#DC2626"); sp.disc(16, 12, 2, "#FFFFFF")
        elif aid == "garage":
            sp.line(9, 9, 23, 23, "#E2E8F0", 3)
            sp.disc(10, 10, 3, "#CBD5E1"); sp.disc(22, 22, 3, "#D6AD59")
        elif aid == "bank":
            sp.rect(8, 22, 16, 3, "#FDE047")
            sp.rect(9, 14, 3, 8, "#F8FAFC"); sp.rect(15, 14, 3, 8, "#F8FAFC"); sp.rect(21, 14, 3, 8, "#F8FAFC")
            for i in range(5): sp.rect(7 + i, 13 - i, 18 - 2 * i, 1, "#FACC15")
        elif aid == "loans":
            sp.shade_bevel("#E2E8F0", 8, 6, 15, 20, corner_cut=1)
            draw_pixel_text(sp, "₹", 13, 11, "#15803D", scale=2)
            sp.disc(21, 21, 4, "#22C55E")
        elif aid == "transport":
            sp.shade_bevel("#E2E8F0", 9, 6, 14, 18, corner_cut=2)
            sp.rect(11, 9, 10, 6, "#0EA5E9")
            sp.rect(11, 19, 3, 3, "#FDE047"); sp.rect(18, 19, 3, 3, "#FDE047")
        elif aid == "news":
            sp.shade_bevel("#F1F5F9", 6, 7, 20, 18, corner_cut=1)
            sp.rect(8, 9, 16, 5, "#DC2626")
            sp.rect(8, 16, 7, 6, "#38BDF8"); sp.rect(17, 16, 7, 2, "#334155"); sp.rect(17, 20, 7, 2, "#334155")
        elif aid == "police":
            sp.shade_bevel("#D6AD59", 9, 8, 14, 16, corner_cut=3)
            sp.disc(16, 16, 4, "#FEF08A")
        elif aid == "medical":
            sp.shade_bevel("#F8FAFC", 7, 9, 18, 14, corner_cut=1)
            sp.rect(14, 11, 4, 10, "#DC2626"); sp.rect(11, 14, 10, 4, "#DC2626")
        elif aid == "events":
            sp.shade_bevel("#F59E0B", 7, 10, 18, 12, corner_cut=1)
            sp.disc(16, 16, 3, "#FEF08A")
        elif aid == "missions":
            sp.disc(16, 16, 9, "#DC2626"); sp.disc(16, 16, 6, "#FFFFFF"); sp.disc(16, 16, 3, "#DC2626")
        elif aid == "careers":
            sp.rect(12, 8, 8, 3, "#D6AD59")
            sp.shade_bevel("#92400E", 7, 11, 18, 13, corner_cut=1)
            sp.rect(14, 16, 4, 3, "#FACC15")
        elif aid == "contacts":
            sp.shade_bevel("#14B8A6", 7, 7, 18, 18, corner_cut=1)
            sp.disc(16, 13, 3, "#FFFFFF"); sp.rect(11, 17, 10, 5, "#FFFFFF")
        elif aid == "keys":
            sp.disc(12, 12, 5, "#D6AD59"); sp.disc(12, 12, 2, bg_hex)
            sp.line(15, 15, 24, 24, "#FACC15", 2); sp.rect(21, 23, 3, 2, "#FACC15")
        else:  # settings
            sp.disc(16, 16, 8, "#CBD5E1"); sp.disc(16, 16, 4, bg_hex)
            for gx, gy in [(15, 6), (15, 24), (6, 15), (24, 15), (9, 9), (21, 9), (9, 21), (21, 21)]:
                sp.rect(gx, gy, 3, 3, "#E2E8F0")

        sp.add_outline(col=(14, 16, 26, 255))
        out_png = pdir / f"app_{aid}.png"
        sp.save(out_png, target_size=128)
        p_imgs.append(Image.open(out_png))
        p_titles.append(title)
        p_manifest.append({
            "id": f"app_{aid}", "title": title, "png": f"creative/source/icons/app_{aid}.png",
            "svg": f"creative/source/icons/app_{aid}.svg", "dimensions_px": [128, 128],
            "native_grid": "32x32", "style": "faithful_32x_pixel",
            "sha256": hashlib.sha256(out_png.read_bytes()).hexdigest()
        })
    (MANIFESTS / "phone_icons.json").write_text(json.dumps(p_manifest, indent=2) + "\n", encoding="utf-8")
    v4.create_grid(p_imgs, p_titles, cols=6, cell_w=112, cell_h=128).save(PREVIEWS / "phone_icons_contact_sheet.png", optimize=True)

    # 33 HUD Assets (Faithful 32x Pixel Art -> crisp NEAREST integers)
    udir = SOURCE / "ui"
    udir.mkdir(parents=True, exist_ok=True)
    hud_names = [
        "wanted_star_empty", "wanted_star_filled", "health", "armour", "fuel", "battery",
        "engine_condition", "speedometer_analog", "speedometer_digital", "speedometer_compact",
        "minimap_circle", "minimap_rectangle", "player_arrow", "gps_route",
        "map_police", "map_hospital", "map_fuel", "map_shop", "map_property", "map_station",
        "map_mission", "phone_shortcut", "hotbar_frame", "hotbar_selected", "dialogue_bubble",
        "notification_frame", "wasted_title", "busted_title", "city_enter", "city_exit",
        "ark_symbol", "low_fuel", "critical_damage"
    ]
    hud_manifest = []
    hud_imgs = []
    for hid in hud_names:
        wide = hid in ("hotbar_frame", "hotbar_selected", "dialogue_bubble", "notification_frame", "wasted_title", "busted_title", "city_enter", "city_exit", "speedometer_digital", "minimap_rectangle")
        nw, nh = (64, 32) if wide else (32, 32)
        sp = s3d.PixelSprite(nw, nh)
        if "star" in hid:
            fill = "#FACC15" if "filled" in hid else "#334155"
            for y in range(4, 28):
                for x in range(4, 28):
                    ang = math.atan2(y - 16, x - 16) - math.pi / 2
                    r = math.hypot(x - 16, y - 16)
                    r_lim = 5.5 + 6.5 * (0.5 + 0.5 * math.cos(5 * ang))
                    if r <= r_lim:
                        sp.px(x, y, "#FEF08A" if ("filled" in hid and y < 14) else fill)
        elif hid == "health":
            for cx, cy in ((11, 12), (21, 12)): sp.disc(cx, cy, 6, "#DC2626")
            for i in range(11): sp.rect(6 + i, 15 + i, 20 - 2 * i, 2, "#DC2626")
            sp.line(8, 16, 13, 16, "#FFFFFF", 1); sp.line(13, 16, 15, 11, "#FFFFFF", 1); sp.line(15, 11, 18, 20, "#FFFFFF", 1); sp.line(18, 20, 24, 16, "#FFFFFF", 1)
        elif hid == "armour":
            sp.shade_bevel("#2563EB", 7, 5, 18, 18, corner_cut=2)
            for i in range(6): sp.rect(9 + i, 22 + i, 14 - 2 * i, 1, "#1D4ED8")
            sp.rect(10, 7, 6, 12, "#60A5FA")
        elif "fuel" in hid:
            col_f = "#EAB308" if "low" in hid else "#DC2626"
            sp.shade_bevel(col_f, 7, 6, 14, 20, corner_cut=1)
            sp.rect(9, 9, 10, 6, "#7DD3FC" if "low" not in hid else "#FFFFFF")
            sp.line(21, 10, 25, 16, "#CBD5E1", 2); sp.line(25, 16, 22, 23, "#CBD5E1", 2)
        elif hid == "battery":
            sp.shade_bevel("#475569", 4, 9, 22, 14, corner_cut=1)
            sp.rect(26, 13, 3, 6, "#CBD5E1")
            sp.rect(6, 11, 18, 10, "#22C55E")
            sp.line(17, 11, 13, 16, "#FEF08A", 2); sp.line(13, 16, 18, 20, "#FEF08A", 2)
        elif hid == "engine_condition":
            sp.shade_bevel("#64748B", 6, 10, 20, 14, corner_cut=2)
            sp.rect(10, 6, 12, 4, "#94A3B8"); sp.line(11, 14, 21, 20, "#FACC15", 2)
        elif hid == "speedometer_analog" or hid == "speedometer_compact":
            sp.disc(16, 17, 12, "#1E293B"); sp.disc(16, 17, 10, "#0F172A")
            sp.rect(7, 21, 18, 7, (0, 0, 0, 0))
            sp.line(16, 17, 23, 11, "#EF4444", 2); sp.disc(16, 17, 2, "#E2E8F0")
        elif hid == "speedometer_digital":
            sp.shade_bevel("#0F172A", 3, 5, 58, 22, corner_cut=3)
            sp.rect(5, 7, 54, 18, "#020617")
            draw_pixel_text(sp, "088 KM", 9, 11, "#22D3EE", scale=2)
        elif "minimap" in hid:
            if hid == "minimap_circle":
                sp.disc(16, 16, 13, "#334155"); sp.disc(16, 16, 11, "#1E3A2F")
                sp.line(6, 16, 26, 16, "#475569", 2); sp.line(16, 5, 16, 27, "#475569", 2)
                sp.line(16, 12, 13, 20, "#38BDF8", 2); sp.line(16, 12, 19, 20, "#38BDF8", 2)
            else:
                sp.shade_bevel("#334155", 4, 3, 56, 26, corner_cut=2)
                sp.rect(6, 5, 52, 22, "#1E3A2F")
                sp.rect(6, 14, 52, 4, "#475569"); sp.rect(28, 5, 4, 22, "#475569")
                sp.disc(30, 16, 3, "#38BDF8")
        elif hid == "player_arrow":
            for i in range(11): sp.rect(16 - i, 5 + i * 2, i * 2 + 1, 2, "#38BDF8" if i < 6 else "#0284C7")
        elif hid == "gps_route":
            sp.line(8, 24, 16, 15, "#22D3EE", 3); sp.line(16, 15, 24, 8, "#22D3EE", 3)
            sp.disc(8, 24, 3, "#22C55E"); sp.disc(24, 8, 3, "#EF4444")
        elif hid.startswith("map_"):
            cmap = {"map_police": "#2563EB", "map_hospital": "#DC2626", "map_fuel": "#D97706", "map_shop": "#7C3AED", "map_property": "#16A34A", "map_station": "#0284C7", "map_mission": "#CA8A04"}
            sp.disc(16, 13, 9, cmap.get(hid, "#D6AD59"))
            for i in range(5): sp.rect(11 + i, 20 + i, 10 - 2 * i, 1, cmap.get(hid, "#D6AD59"))
            sp.rect(14, 10, 4, 6, "#FFFFFF")
            if "hospital" in hid or "fuel" in hid: sp.rect(12, 12, 8, 2, "#FFFFFF")
        elif hid == "phone_shortcut":
            sp.shade_bevel("#1E293B", 9, 4, 14, 24, corner_cut=1)
            sp.rect(11, 7, 10, 17, "#0EA5E9")
            sp.rect(12, 9, 3, 3, "#22C55E"); sp.rect(17, 9, 3, 3, "#FACC15"); sp.rect(12, 14, 3, 3, "#EC4899")
        elif hid == "hotbar_frame" or hid == "hotbar_selected":
            c = "#D6AD59" if "selected" in hid else "#475569"
            sp.shade_bevel(c, 3, 4, 58, 24, corner_cut=2)
            sp.rect(6, 7, 52, 18, "#0F172A")
        elif hid == "dialogue_bubble":
            sp.shade_bevel("#38BDF8", 4, 4, 56, 20, corner_cut=3)
            sp.rect(7, 7, 50, 14, "#F8FAFC")
            sp.rect(16, 24, 6, 4, "#38BDF8")
            sp.rect(15, 13, 4, 4, "#1E293B"); sp.rect(29, 13, 4, 4, "#1E293B"); sp.rect(43, 13, 4, 4, "#1E293B")
        elif hid == "notification_frame":
            sp.shade_bevel("#1E293B", 4, 4, 56, 24, corner_cut=2)
            sp.disc(32, 15, 6, "#FACC15"); sp.rect(24, 18, 16, 3, "#FACC15"); sp.disc(40, 9, 3, "#DC2626")
        elif hid in ("wasted_title", "busted_title"):
            col_t = "#EF4444" if "wasted" in hid else "#38BDF8"
            sp.shade_bevel("#151B20", 3, 5, 58, 22, corner_cut=2)
            lbl = "WASTED" if "wasted" in hid else "BUSTED"
            draw_pixel_text(sp, lbl, 9, 11, col_t, scale=2, shadow_col="#000000")
        elif hid in ("city_enter", "city_exit"):
            col_c = "#22C55E" if "enter" in hid else "#EF4444"
            sp.shade_bevel("#1E293B", 3, 4, 58, 24, corner_cut=2)
            sp.rect(10, 8, 6, 16, "#94A3B8"); sp.rect(48, 8, 6, 16, "#94A3B8")
            sp.rect(14, 18, 36, 4, "#D6AD59")
            draw_pixel_text(sp, "IN" if "enter" in hid else "OUT", 24, 9, col_c, scale=2)
        elif hid == "ark_symbol":
            sp.disc(16, 16, 11, "#D6AD59"); sp.disc(16, 16, 9, "#FEF08A"); sp.disc(16, 16, 7, "#D97706")
            draw_pixel_text(sp, "₹", 13, 11, "#FFFBEB", scale=2)
        elif hid == "critical_damage":
            sp.shade_bevel("#DC2626", 4, 13, 24, 10, corner_cut=2)
            sp.shade_bevel("#991B1B", 8, 9, 14, 5, corner_cut=1)
            sp.disc(9, 23, 3, "#0F172A"); sp.disc(23, 23, 3, "#0F172A")
            sp.disc(15, 7, 3, "#94A3B8"); sp.disc(18, 4, 2, "#CBD5E1")

        sp.add_outline(col=(12, 14, 22, 255))
        target = (128, 64) if wide else (64, 64)
        out_png = udir / f"{hid}.png"
        sp.to_image().resize(target, Image.Resampling.NEAREST).save(out_png, format="PNG", optimize=True)
        hud_imgs.append(Image.open(out_png))
        hud_manifest.append({
            "id": hid, "png": f"creative/source/ui/{hid}.png", "dimensions_px": list(target),
            "style": "faithful_32x_hud_pixel", "sha256": hashlib.sha256(out_png.read_bytes()).hexdigest()
        })
    (MANIFESTS / "hud_manifest.json").write_text(json.dumps(hud_manifest, indent=2) + "\n", encoding="utf-8")
    v4.create_grid(hud_imgs, hud_names, cols=6, cell_w=120, cell_h=124).save(PREVIEWS / "hud_contact_sheet.png", optimize=True)
    print("SUCCESS: Regenerated Server Icon + 32 Brands + 24 Phone Icons + 33 HUD Assets in Faithful 32x Pixel Art!")


def draw_faithful_food_sprite(slug: str) -> s3d.PixelSprite:
    """Hand-crafted 32x32 Faithful 32x pixel art Indian food icons (zero blur, warm brown outlines!)."""
    sp = s3d.PixelSprite(32, 32)
    outline = (48, 22, 10, 255)
    plate_rim = (196, 206, 218, 255)
    plate_mid = (138, 152, 168, 255)
    leaf = hex_ramp("#368C48")
    gold = hex_ramp("#F59E0B")
    bread = hex_ramp("#D98A36")
    clay = hex_ramp("#AD5637")
    curry = hex_ramp("#C83E20")
    cream = hex_ramp("#FAF3E0")
    copper = hex_ramp("#C87542")

    def steel_plate(y0=18):
        for dy in range(-4, 5):
            rx = int(12 * math.sqrt(max(0.0, 1.0 - (dy / 4.5) ** 2)))
            sp.rect(16 - rx, y0 + dy, 2 * rx, 1, plate_rim if dy < 0 else plate_mid)

    def banana_leaf_base(y0=19):
        for dy in range(-4, 5):
            rx = int(13 * math.sqrt(max(0.0, 1.0 - (dy / 4.5) ** 2)))
            sp.rect(16 - rx, y0 + dy, 2 * rx, 1, leaf[4 if dy == 0 else (3 if dy < 0 else 2)])

    if slug == "chai":
        sp.shade_bevel("#C87542", 7, 11, 12, 14, corner_cut=2)
        sp.rect(6, 13, 3, 6, copper[4]); sp.rect(18, 11, 4, 3, copper[5])
        sp.shade_bevel("#D97706", 19, 17, 7, 9, corner_cut=1)
        sp.rect(20, 16, 5, 2, cream[4])
        sp.line(12, 5, 11, 9, (255, 255, 255, 200)); sp.line(22, 10, 21, 14, (255, 255, 255, 200))
    elif slug == "vada_pav":
        sp.shade_bevel("#D98A36", 6, 17, 20, 8, corner_cut=2)
        sp.shade_bevel("#EA580C", 8, 13, 16, 6, corner_cut=2)
        sp.shade_bevel("#E2953B", 6, 7, 20, 8, corner_cut=3)
        sp.line(18, 11, 27, 8, leaf[4], 2)  # green chilli
    elif slug == "samosa":
        steel_plate(22)
        for sx, sy, h in ((10, 11, 11), (17, 13, 10)):
            for i in range(h): sp.rect(sx - i // 2, sy + i, i + 2, 1, gold[4 if i < 4 else 3])
        sp.disc(22, 22, 3, leaf[4])
    elif slug == "dabeli":
        sp.shade_bevel("#D98A36", 6, 18, 20, 7, corner_cut=2)
        sp.rect(7, 13, 18, 6, curry[3])
        for px in (9, 13, 18, 21): sp.px(px, 15, "#DC2626"); sp.px(px + 1, 16, "#FEF08A")
        sp.shade_bevel("#E2953B", 6, 7, 20, 7, corner_cut=3)
    elif slug == "pav_bhaji":
        steel_plate(20)
        sp.disc(12, 18, 6, curry[3]); sp.rect(10, 14, 4, 3, "#FEF08A")
        sp.shade_bevel("#D98A36", 18, 11, 8, 8, corner_cut=2)
    elif slug == "dosa":
        banana_leaf_base(21)
        for i in range(18):
            h = max(3, 8 - i // 3)
            sp.rect(7 + i, 17 - h // 2, 2, h, bread[4 if i < 6 else 3])
        sp.disc(10, 21, 3, curry[3]); sp.disc(15, 22, 2, leaf[4])
    elif slug == "idli":
        banana_leaf_base(21)
        for ix, iy in ((11, 17), (19, 17), (15, 13)):
            sp.disc(ix, iy, 4, cream[5])
        sp.disc(21, 12, 3, curry[3])
    elif slug == "thali":
        sp.disc(16, 17, 12, plate_mid); sp.disc(16, 17, 10, plate_rim)
        for kx, ky, col in [(11, 11, curry[3]), (16, 10, gold[4]), (21, 11, leaf[4]), (12, 20, cream[5]), (20, 19, bread[4])]:
            sp.disc(kx, ky, 3, col)
    elif slug == "biryani":
        sp.shade_bevel("#AD5637", 7, 15, 18, 11, corner_cut=3)
        sp.rect(9, 12, 14, 3, copper[4])
        sp.rect(10, 9, 12, 4, gold[4]); sp.rect(12, 8, 8, 2, cream[5])
        sp.line(18, 9, 22, 6, bread[2], 2); sp.px(13, 10, "#DC2626"); sp.px(16, 11, leaf[4])
    elif slug == "lassi":
        sp.shade_bevel("#C87542", 10, 8, 12, 18, corner_cut=1)
        sp.rect(11, 7, 10, 3, cream[5]); sp.px(14, 7, leaf[4]); sp.px(18, 7, "#F43F5E")
    elif slug == "dhokla":
        steel_plate(22)
        for dx, dy in ((8, 14), (16, 14), (12, 9)):
            sp.shade_bevel("#FACC15", dx, dy, 8, 7, corner_cut=0)
            sp.px(dx + 2, dy, leaf[4]); sp.px(dx + 5, dy, "#1E293B")
    elif slug == "khandvi":
        steel_plate(21)
        for kx, ky in ((10, 14), (18, 14), (14, 10)):
            sp.shade_bevel("#FACC15", kx, ky, 6, 6, corner_cut=1)
            sp.px(kx + 2, ky, leaf[4])
    elif slug == "poha":
        steel_plate(21)
        sp.disc(14, 17, 6, gold[4])
        for px, py in ((11, 15), (15, 13), (17, 17)): sp.px(px, py, bread[1])
        sp.px(13, 14, leaf[4]); sp.disc(22, 14, 3, "#FEF08A")
    elif slug == "upma":
        steel_plate(21)
        sp.shade_bevel("#FAF3E0", 9, 11, 10, 8, corner_cut=2)
        sp.px(12, 13, "#D97706"); sp.px(15, 14, leaf[4]); sp.disc(22, 19, 3, curry[3])
    elif slug == "misal":
        steel_plate(21)
        sp.disc(13, 18, 6, curry[2]); sp.rect(10, 14, 6, 2, "#FACC15")
        sp.shade_bevel("#D98A36", 19, 13, 7, 7, corner_cut=1)
    elif slug == "puran_poli":
        steel_plate(21)
        for i in range(9): sp.rect(16 - i, 10 + i, i * 2 + 1, 1, gold[4 if i < 4 else 3])
        sp.rect(14, 14, 4, 2, "#FEF08A")
    elif slug == "bhakri":
        steel_plate(21)
        sp.disc(14, 18, 7, cream[3])
        sp.px(11, 16, bread[1]); sp.px(17, 19, bread[1]); sp.disc(14, 15, 3, "#FFFFFF"); sp.disc(22, 17, 3, "#DC2626")
    elif slug == "thepla":
        steel_plate(21)
        sp.disc(13, 19, 6, bread[3]); sp.disc(15, 16, 6, bread[4])
        sp.px(12, 15, leaf[3]); sp.px(17, 17, leaf[3]); sp.px(15, 14, leaf[4]); sp.disc(22, 18, 3, curry[3])
    elif slug == "modak":
        banana_leaf_base(21)
        for mx, my in ((11, 18), (21, 18), (16, 14)):
            for i in range(7): sp.rect(mx - i // 2, my - 5 + i, i + 2, 1, cream[5 if i < 3 else 4])
    elif slug == "jalebi":
        steel_plate(21)
        for jx, jy in ((11, 17), (20, 17), (15, 12)):
            sp.disc(jx, jy, 4, "#F97316"); sp.disc(jx, jy, 2, "#FEF08A"); sp.px(jx, jy, plate_rim)
    elif slug == "kulfi":
        sp.rect(15, 19, 3, 9, bread[2])
        for i in range(14):
            w = 3 + i // 3
            sp.rect(16 - w // 2, 6 + i, w, 1, cream[5] if i > 4 else leaf[4])
    elif slug == "falooda":
        sp.shade_bevel("#F472B6", 10, 11, 12, 16, corner_cut=1)
        sp.disc(16, 9, 4, cream[5]); sp.px(16, 5, "#DC2626"); sp.line(18, 5, 16, 14, "#38BDF8", 1)
    elif slug == "nimbu_pani":
        sp.shade_bevel("#FEF08A", 10, 10, 12, 17, corner_cut=1)
        sp.disc(21, 10, 3, "#FACC15"); sp.line(13, 5, 17, 23, "#22C55E", 1)
    elif slug == "filter_coffee":
        sp.shade_bevel("#D6AD59", 9, 18, 14, 8, corner_cut=2)
        sp.shade_bevel("#D6AD59", 11, 10, 10, 9, corner_cut=1)
        sp.rect(12, 9, 8, 2, "#592D1D")
    elif slug == "kathi_roll":
        sp.line(8, 23, 24, 9, bread[4], 7)
        sp.rect(8, 19, 8, 7, "#F8FAFC")
        sp.disc(23, 10, 3, "#DC2626"); sp.px(21, 9, leaf[4])
    elif slug == "pani_puri" or slug == "sev_puri":
        steel_plate(21)
        for px, py in ((10, 17), (16, 14), (22, 17)):
            sp.disc(px, py, 3, gold[4])
            sp.px(px, py - 1, leaf[4] if slug == "pani_puri" else "#DC2626")
    elif slug == "ragda":
        steel_plate(21)
        sp.disc(16, 18, 7, "#FACC15"); sp.disc(12, 17, 3, bread[2]); sp.disc(20, 17, 3, bread[2])
    elif slug == "sandesh":
        steel_plate(21)
        for sx, sy in ((11, 18), (21, 18), (16, 14)):
            sp.disc(sx, sy, 4, cream[5]); sp.px(sx, sy - 2, "#EA580C")
    else:  # sheera
        sp.shade_bevel("#D6AD59", 8, 16, 16, 10, corner_cut=2)
        sp.disc(16, 15, 6, gold[4]); sp.px(14, 13, cream[5]); sp.px(19, 14, "#DC2626")

    sp.add_outline(col=outline)
    return sp


def rebuild_faithful_food_all():
    """Rebuild 30 Faithful 32x Food Pixel Sprites + 30 Food 3D Models + Faithful 64x64 Food Atlas."""
    fdir = SOURCE / "icons" / "food"
    fdir.mkdir(parents=True, exist_ok=True)
    f3d_dir = SOURCE / "models" / "food"
    f3d_java = f3d_dir / "java"
    f3d_dir.mkdir(parents=True, exist_ok=True)
    f3d_java.mkdir(parents=True, exist_ok=True)

    # Faithful 64x64 Food 3D Atlas (16 swatches x 16px, hue-shifted quantized tones)
    FOOD_SWATCHES = [
        ("steel", "#95ACB5"), ("brass", "#E0B24C"), ("clay", "#AE573B"), ("banana_leaf", "#3E8B4B"),
        ("golden_fry", "#F2A833"), ("bread", "#DF9D4E"), ("cream_white", "#F7EBD2"), ("saffron", "#FFAA1D"),
        ("gravy_red", "#C43E24"), ("mint_green", "#4AA853"), ("rose_pink", "#E8688D"), ("dark_roast", "#592D1D"),
        ("pistachio", "#8BC34A"), ("jaggery", "#8E431E"), ("lemon", "#FDE047"), ("glass_ice", "#B8EBF2")
    ]
    atlas_im = Image.new("RGBA", (64, 64))
    for i, (sname, shex) in enumerate(FOOD_SWATCHES):
        tile = f32.tex_polished(shex, frame=1, flecks=True, seed=40 + i)
        # Downsample cleanly 2x NEAREST/box to 16x16 or crop 16x16 core pattern
        sub = Image.fromarray(tile).crop((0, 0, 16, 16))
        atlas_im.paste(sub, ((i % 4) * 16, (i // 4) * 16))
    tex_dir = SOURCE / "textures" / "food"
    tex_dir.mkdir(parents=True, exist_ok=True)
    atlas_path = tex_dir / "gtm_street_kitchen_atlas.png"
    atlas_im.save(atlas_path, format="PNG", optimize=True)

    swatch_map = {
        "steel": 0, "rim": 0, "ice": 15, "clay": 2, "terra": 2,
        "cream": 6, "milk": 6, "crust": 5, "bread": 5, "toast": 13,
        "gold": 4, "gravy": 8, "chilli": 8, "leaf": 3, "mint": 9,
        "pink": 10, "rice": 6, "bean": 11, "saffron": 7, "violet": 10
    }
    raw_recipes = food_art.recipes()
    manifest_items = []
    f_imgs, f_titles = [], []

    for slug, parts in raw_recipes.items():
        # 1. Sprite Icon
        sp = draw_faithful_food_sprite(slug)
        icon_file = fdir / f"{slug}.png"
        sp.save(icon_file, target_size=128)
        f_imgs.append(Image.open(icon_file))
        f_titles.append(slug.replace("_", " ").title())

        # 2. 3D Model (.geo.json + Java .json)
        cubes, elements = [], []
        for idx_p, (col, x, y, z, w, h, d) in enumerate(parts):
            sw_idx = swatch_map.get(col, 4)
            u0, v0 = (sw_idx % 4) * 16, (sw_idx // 4) * 16
            ju0, jv0 = (sw_idx % 4) * 4, (sw_idx // 4) * 4
            elements.append({
                "name": f"{slug}_part_{idx_p}",
                "from": [round(x, 3), round(y, 3), round(z, 3)],
                "to": [round(x + w, 3), round(y + h, 3), round(z + d, 3)],
                "faces": {f: {"uv": [ju0 + 0.1, jv0 + 0.1, ju0 + 3.9, jv0 + 3.9], "texture": "#atlas"}
                          for f in ("north", "south", "east", "west", "up", "down")}
            })
            cubes.append({
                "origin": [round(8 - x - w, 3), round(y, 3), round(z - 8, 3)],
                "size": [round(w, 3), round(h, 3), round(d, 3)],
                "uv": {f: {"uv": [u0 + 0.5, v0 + 0.5], "uv_size": [15, 15]}
                       for f in ("north", "south", "east", "west", "up", "down")}
            })

        geo_file = f3d_dir / f"{slug}.geo.json"
        geo_file.write_text(json.dumps({
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {
                    "identifier": f"geometry.gtm.food_{slug}",
                    "texture_width": 64, "texture_height": 64,
                    "visible_bounds_width": 1.6, "visible_bounds_height": 1.6, "visible_bounds_offset": [0, 0.4, 0]
                },
                "bones": [{"name": "root", "pivot": [0, 0, 0], "cubes": cubes}]
            }]
        }, indent=2) + "\n", encoding="utf-8")

        java_file = f3d_java / f"{slug}.json"
        java_file.write_text(json.dumps({
            "credit": "GTM Indraprastha - Faithful 32x Street Kitchen",
            "parent": "minecraft:block/block",
            "textures": {"atlas": "gtm:item/street_kitchen_atlas", "particle": "#atlas"},
            "elements": elements,
            "display": {
                "gui": {"rotation": [28, 225, 0], "translation": [0, 1, 0], "scale": [0.9, 0.9, 0.9]},
                "firstperson_righthand": {"rotation": [0, 40, 0], "translation": [1, 2, 0], "scale": [0.55, 0.55, 0.55]}
            }
        }, indent=2) + "\n", encoding="utf-8")

        manifest_items.append({
            "id": f"gtm:food_{slug}", "meal_slug": slug, "title": slug.replace("_", " ").title(),
            "model_path": f"creative/source/models/food/{slug}.geo.json",
            "java_model_path": f"creative/source/models/food/java/{slug}.json",
            "texture_atlas": "creative/source/textures/food/gtm_street_kitchen_atlas.png",
            "icon_path": f"creative/source/icons/food/{slug}.png",
            "icon_dimensions": [128, 128], "native_grid": "32x32", "cube_count": len(cubes),
            "sha256_model": hashlib.sha256(geo_file.read_bytes()).hexdigest(),
            "sha256_icon": hashlib.sha256(icon_file.read_bytes()).hexdigest()
        })

    (MANIFESTS / "food_manifest.json").write_text(json.dumps({
        "schema_version": "3.0.0", "total_food_items": len(manifest_items), "items": manifest_items
    }, indent=2) + "\n", encoding="utf-8")
    v4.create_grid(f_imgs, f_titles, cols=6, cell_w=120, cell_h=136).save(PREVIEWS / "food_contact_sheet.png", optimize=True)
    print("SUCCESS: Regenerated 30 Faithful 32x Food Pixel Icons + 30 3D Food Models + Atlas!")


if __name__ == "__main__":
    build_server_icon()
    regenerate_brands_and_ui()
    rebuild_faithful_food_all()
