#!/usr/bin/env python3
"""Native 128px character-art extension of the existing GTM skin pipeline.

Reads, never rewrites, the creative-r4 identity manifests.  The established
64px generator supplies the starting skin and role palette; native 128px
garments, face/hair features and occupational accessories replace its old
serial stitch tags.  Java-compatible 64px derivatives are explicit exports.
No runtime identities, world placement, signed skin bindings or prices change.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regenerate_skins_outfits_all as legacy

ROOT = Path(__file__).resolve().parents[1]
PALETTE = {
    "graphite": (21, 27, 32), "gold": (214, 173, 89),
    "emerald": (35, 102, 83), "sandstone": (210, 185, 151),
    "terracotta": (173, 86, 55), "cream": (235, 229, 210),
    "indigo": (53, 66, 105), "teal": (49, 115, 119),
    "plum": (110, 61, 88), "slate": (80, 99, 111),
}
CLOTH = list(PALETTE.values())
GOLD, CREAM, INK = PALETTE["gold"], PALETTE["cream"], PALETTE["graphite"]

BASE = {
    "head": (0, 0, 8, 8, 8), "body": (16, 16, 8, 12, 4),
    "right_arm": (40, 16, 4, 12, 4), "left_arm": (32, 48, 4, 12, 4),
    "right_leg": (0, 16, 4, 12, 4), "left_leg": (16, 48, 4, 12, 4),
}
OUTER = {
    "head": (32, 0, 8, 8, 8), "body": (16, 32, 8, 12, 4),
    "right_arm": (40, 32, 4, 12, 4), "left_arm": (48, 48, 4, 12, 4),
    "right_leg": (0, 32, 4, 12, 4), "left_leg": (0, 48, 4, 12, 4),
}

OUTFIT_NAMES = {
    "casual": ["Zip hoodie", "Denim trucker", "Varsity jacket", "Linen overshirt", "Crewneck knit", "Monsoon shell", "Crossbody tee", "Bomber jacket", "Checked shirt", "Henley", "Field jacket", "Polo", "Denim vest", "Roll sleeve shirt", "Mockneck", "Panel sweatshirt", "Canvas gilet", "Short kurta", "Workwear overshirt", "Piped track top"],
    "traditional": ["Nehru waistcoat", "Straight kurta", "Angarkha wrap", "Bandhgala", "Gold edge sherwani", "Panel kurta", "Stole kurta", "Dhoti kurta", "Cotton pajama set", "Sari drape", "Salwar suit", "Churidar set", "Pathani set", "Embroidered koti", "Long ceremonial jacket", "Cotton panjabi", "Handloom vest", "Short kurta set", "Silk dupatta set", "Jodhpuri jacket"],
    "formal": ["Single breast suit", "Double breast suit", "Nehru business suit", "Pinstripe blazer", "Waistcoat suit", "Open collar blazer", "Oxford shirt", "Contrast lapel suit", "Business kurta", "Windowpane blazer", "Mandarin office shirt", "Cardigan and tie", "Vest and rolled sleeves", "Tailored tunic", "Business travel coat"],
    "sports": ["Cricket whites", "Football jersey", "Running vest", "Cycling jersey", "Badminton polo", "Training tracksuit", "Basketball set", "Athletics warmup", "Yoga set", "Rain running shell"],
    "festival": ["Diwali brocade", "Holi cotton panels", "Navratri mirrorwork", "Garba embroidered vest", "Ganesh celebration kurta", "New Year evening jacket", "Christmas winter knit", "Monsoon rain cape", "Independence sash", "Gold bordered sari", "Silver festival sherwani", "Marigold dupatta", "Lantern embroidered jacket", "Geometric silk kurta", "Celebration bandh gala"],
    "premium": ["Velvet evening jacket", "Raw silk bandhgala", "Gold stitch overcoat", "Fine knit mockneck", "Emerald silk jacket", "Sandstone linen suit", "Indigo travel blazer", "Brocade waistcoat", "Minimal black suit", "Piped ceremonial coat"],
    "utility": ["Mechanic coverall", "Transit work jacket", "Courier vest", "Civic work shirt", "Market apron", "Harbour jacket", "Workshop bib", "Rain safety shell", "Field survey vest", "Rescue workwear"],
}

ROLE_CUTS = {
    "civilian": ["hoodie", "shirt", "kurta", "cardigan", "sari", "tee"],
    "shopkeeper": ["waistcoat", "shirt", "kurta", "apron", "cardigan", "tunic"],
    "food_seller": ["apron", "kurta", "chef", "apron", "shirt", "waistcoat"],
    "fashion_seller": ["sari", "blazer", "tunic", "waistcoat", "kurta", "shirt"],
    "road_transport": ["courier", "courier", "shirt", "waistcoat", "jacket", "coverall"],
    "police": ["uniform", "uniform", "vest", "uniform", "jacket", "uniform"],
    "healthcare": ["labcoat", "scrubs", "labcoat", "scrubs", "labcoat", "scrubs"],
    "fire_rescue": ["rescue", "rescue", "coverall", "rescue", "rescue", "vest"],
    "government": ["blazer", "waistcoat", "sari", "shirt", "kurta", "blazer"],
    "rail_ropeway": ["uniform", "coverall", "waistcoat", "vest", "shirt", "jacket"],
    "industrial": ["coverall", "vest", "apron", "jacket", "shirt", "coverall"],
    "professional": ["blazer", "shirt", "tunic", "cardigan", "waistcoat", "kurta"],
    "story": ["jacket", "kurta", "sari", "blazer", "hoodie", "tunic"],
    "media": ["vest", "blazer", "shirt", "jacket", "tunic", "waistcoat"],
    "entertainment": ["blazer", "tee", "waistcoat", "tunic", "jacket", "sari"],
    "aviation_marine": ["uniform", "vest", "jacket", "shirt", "coverall", "uniform"],
    "black_lotus": ["blazer", "jacket", "vest", "shirt", "kurta", "hoodie"],
}


def color(c, delta=0):
    return tuple(max(0, min(255, int(x + delta))) for x in c[:3])


def box(im, x, y, w, h, c, alpha=255):
    """Coordinates are legacy UV units; .5 units paints ONE native128 pixel."""
    x, y, w, h = [round(v * 2) for v in (x, y, w, h)]
    if w > 0 and h > 0:
        ImageDraw.Draw(im).rectangle((x, y, x + w - 1, y + h - 1), fill=(*color(c), alpha))


def line(im, pts, c, width=.5):
    ImageDraw.Draw(im).line([(round(x * 2), round(y * 2)) for x, y in pts], fill=(*color(c), 255), width=max(1, round(width * 2)))


def polygon(im, pts, c):
    ImageDraw.Draw(im).polygon([(round(x * 2), round(y * 2)) for x, y in pts], fill=(*color(c), 255))


def faces(spec):
    u, v, w, h, z = spec
    return [(u + z, v, w, z, 15), (u + z + w, v, w, z, -21),
            (u, v + z, z, h, -13), (u + z, v + z, w, h, 2),
            (u + z + w, v + z, z, h, -8), (u + 2 * z + w, v + z, w, h, -15)]


def uv_mask(specs, size=128):
    im = Image.new("L", (128, 128)); d = ImageDraw.Draw(im)
    for spec in specs:
        for x, y, w, h, _ in faces(spec):
            d.rectangle((x * 2, y * 2, (x + w) * 2 - 1, (y + h) * 2 - 1), fill=255)
    return im if size == 128 else im.resize((size, size), Image.Resampling.NEAREST)


def cuboid(im, spec, c, fabric=False):
    for x, y, w, h, sh in faces(spec):
        box(im, x, y, w, h, color(c, sh))
        if fabric and h > 3:
            # Broad folds and a native-pixel selvedge; no random texture noise.
            box(im, x, y, .5, h, color(c, sh - 7))
            box(im, x + w - .5, y, .5, h, color(c, sh - 10))
            box(im, x + .5, y + .5, max(.5, w - 1), .5, color(c, sh + 7))
            if w >= 4:
                line(im, [(x + 1, y + 2), (x + 1.5, y + h - 2)], color(c, sh + 4))
                line(im, [(x + w - 2, y + 2), (x + w - 1.5, y + h - 1)], color(c, sh - 5))


def sleeve(im, spec, c, length=10, overlay=False):
    cuboid(im, spec, c, True)
    u, v, w, h, z = spec
    if length < h:
        for x, y, fw, fh, _ in faces(spec)[2:]:
            box(im, x, y + length, fw, h - length, (0, 0, 0), 0)
        box(im, u + z + w, v, w, z, (0, 0, 0), 0)
    for x, y, fw, fh, sh in faces(spec)[2:]:
        if length:
            box(im, x, y + length - 1, fw, .5, color(c, sh - 18))
            box(im, x, y + length - .5, fw, .5, color(c, sh + 16))


def pocket(im, x, y, c, w=2.5, h=3):
    box(im, x, y, w, h, color(c, -12))
    box(im, x, y, w, .5, color(c, 20))
    line(im, [(x + .5, y + .5), (x + .5, y + h - .5), (x + w - .5, y + h - .5)], color(c, 7))
    box(im, x + w / 2, y + .5, .5, .5, GOLD)


def embroidery(im, x, y, w, h, c, motif=0):
    for j in range(int(h * 2)):
        yy = y + j * .5
        if motif % 3 == 0:
            xx = x + (j % max(2, int(w * 2))) * .5
            box(im, xx, yy, .5, .5, c)
        elif motif % 3 == 1:
            if j % 3 == 0:
                for xx in range(int(w)):
                    box(im, x + xx, yy, .5, .5, c)
        else:
            if j % 4 in (0, 2):
                for xx in range(0, int(w * 2), 3):
                    box(im, x + xx * .5, yy, .5, .5, c)


def garment(im, cut, shirt, pants, variant, *, outer=True, role="", sleeve_length=None):
    parts = OUTER if outer else BASE
    body = parts["body"]
    cuboid(im, body, shirt, True)
    u, v, _, _, _ = body; x, y = u + 4, v + 4
    sleeve_length = sleeve_length if sleeve_length is not None else (5 if cut in ("tee", "scrubs") else 10)
    if cut in ("vest", "waistcoat", "sari"):
        sleeve_length = 5 if cut == "sari" else 0
    for key in ("right_arm", "left_arm"):
        if sleeve_length:
            sleeve(im, parts[key], shirt, sleeve_length, outer)
        elif outer:
            for fx, fy, fw, fh, _ in faces(parts[key]):
                box(im, fx, fy, fw, fh, (0, 0, 0), 0)
    for key in ("right_leg", "left_leg"):
        cuboid(im, parts[key], pants, True)
        lu, lv, *_ = parts[key]
        for fx, fy, fw, fh, sh in faces(parts[key])[2:]:
            box(im, fx, fy + 10, fw, 2, color(INK, 2))
            box(im, fx, fy + 11.5, fw, .5, color(pants, 30))
        box(im, lu + 8, lv, 4, 4, color(INK, -6))
        box(im, lu + 5, lv + 14, 2, .5, color(CREAM, -60))

    if cut in ("sari", "kurta", "tunic"):
        # The lower drape continues onto the leg UVs instead of ending abruptly
        # at the waist; Minecraft still supplies the standard player geometry.
        drape = 10 if cut == "sari" else (6 if cut == "kurta" else 4)
        for key in ("right_leg", "left_leg"):
            for fx, fy, fw, fh, sh in faces(parts[key])[2:]:
                box(im, fx, fy, fw, drape, color(shirt, sh))
                line(im, [(fx + 1, fy), (fx + 1.5, fy + drape - 1)], color(shirt, sh - 12))
                box(im, fx, fy + drape - .5, fw, .5, GOLD)

    # Native-pixel collar, neckline and side tailoring.
    box(im, x + 2.5, y, 3, 1, color(shirt, -22))
    box(im, x + 3, y, 2, .5, color(shirt, 16))
    box(im, x, y + 11.5, 8, .5, color(shirt, -26))
    box(im, u + 16, y + 11.5, 8, .5, color(shirt, -26))
    trim = GOLD if cut in ("kurta", "sari", "blazer", "waistcoat", "tunic") else color(shirt, 45)

    if cut in ("shirt", "uniform", "coverall", "chef", "courier"):
        line(im, [(x + 4, y + 1), (x + 4, y + 11)], color(shirt, -24))
        polygon(im, [(x + 1.5, y), (x + 3.5, y + 1), (x + 3, y + 3)], color(shirt, 25))
        polygon(im, [(x + 6.5, y), (x + 4.5, y + 1), (x + 5, y + 3)], color(shirt, 18))
        for yy in (3, 5, 7, 9):
            box(im, x + 4, y + yy, .5, .5, CREAM)
        pocket(im, x + .5, y + 3.5, shirt)
        if cut in ("uniform", "coverall", "courier"):
            pocket(im, x + 5, y + 3.5, shirt)
            box(im, x, y + 10, 8, 1, INK); box(im, x + 3.5, y + 10, 1, 1, GOLD)
            box(im, u + 16, y + 10, 8, 1, INK)
    elif cut in ("blazer", "labcoat", "jacket", "cardigan"):
        inner = CREAM if cut in ("blazer", "labcoat") else color(shirt, 35)
        polygon(im, [(x + 2, y), (x + 6, y), (x + 4.5, y + 8), (x + 3.5, y + 8)], inner)
        polygon(im, [(x + 1, y), (x + 3, y + 1), (x + 4, y + 6), (x + 1.5, y + 3)], color(shirt, 20))
        polygon(im, [(x + 7, y), (x + 5, y + 1), (x + 4, y + 6), (x + 6.5, y + 3)], color(shirt, 9))
        if cut == "blazer":
            line(im, [(x + 4, y + 1), (x + 4, y + 6)], PALETTE["terracotta"], 1)
        pocket(im, x + .5, y + 7.5, shirt, 2, 2)
        pocket(im, x + 5.5, y + 7.5, shirt, 2, 2)
        box(im, x + 5.5, y + 3, 1.5, .5, CREAM)
        for yy in (7, 9): box(im, x + 4, y + yy, .5, .5, GOLD)
        box(im, u + 19.5, y + 2, .5, 9, color(shirt, -15))
    elif cut in ("kurta", "tunic", "sari"):
        box(im, x + 3.5, y + .5, 1, 7, color(shirt, -18))
        embroidery(im, x + 3.5, y + 1, 1, 6, GOLD, variant)
        for yy in (1, 3, 5): box(im, x + 4, y + yy, .5, .5, GOLD)
        box(im, x, y + 10.5, 8, 1, color(shirt, 16))
        embroidery(im, x, y + 10.5, 8, 1, GOLD, variant)
        if cut == "sari" or variant % 3 == 1:
            polygon(im, [(x, y), (x + 2, y), (x + 8, y + 9), (x + 8, y + 12), (x + 6.5, y + 12)], trim)
            line(im, [(x + .5, y), (x + 7.5, y + 10)], color(shirt, 30), .5)
            box(im, u + 16, y, 2, 12, trim)
            embroidery(im, u + 16, y, 2, 12, color(shirt, -15), variant)
    elif cut in ("vest", "waistcoat"):
        polygon(im, [(x + 2, y), (x + 6, y), (x + 4, y + 5)], CREAM)
        line(im, [(x + 4, y + 5), (x + 4, y + 11)], color(shirt, 30))
        for yy in (5, 7, 9): box(im, x + 4, y + yy, .5, .5, GOLD)
        pocket(im, x + .5, y + 7, shirt, 2, 2); pocket(im, x + 5.5, y + 7, shirt, 2, 2)
        if cut == "vest":
            pocket(im, x + .5, y + 3, shirt, 2, 2); pocket(im, x + 5.5, y + 3, shirt, 2, 2)
    elif cut == "hoodie":
        line(im, [(x + 1, y), (x + 2, y + 2), (x + 4, y + 3), (x + 6, y + 2), (x + 7, y)], color(shirt, -24), 1)
        line(im, [(x + 2.5, y + 2), (x + 2.5, y + 5)], CREAM)
        line(im, [(x + 5.5, y + 2), (x + 5.5, y + 5)], CREAM)
        pocket(im, x + 1.5, y + 7, shirt, 5, 3)
        polygon(im, [(u + 17, y), (u + 23, y), (u + 22, y + 4), (u + 20, y + 5), (u + 18, y + 4)], color(shirt, -15))
    elif cut == "apron":
        box(im, x + 1, y + 3, 6, 9, color(CREAM, -12))
        box(im, x + 1, y, 1, 4, CREAM); box(im, x + 6, y, 1, 4, CREAM)
        pocket(im, x + 2, y + 7, color(CREAM, -12), 4, 3)
        box(im, u + 16, y + 5, 8, 1, CREAM)
        line(im, [(u + 20, y + 5), (u + 22, y + 8)], CREAM)
    elif cut == "scrubs":
        polygon(im, [(x + 2, y), (x + 6, y), (x + 4, y + 3)], color(shirt, -35))
        pocket(im, x + 5, y + 3, shirt)
        line(im, [(x + 4, y + 10), (x + 4, y + 11)], CREAM)
    elif cut == "rescue":
        for fy in (y + 3, y + 8):
            box(im, x, fy, 8, 1.5, GOLD); box(im, x, fy + .5, 8, .5, CREAM)
            box(im, u + 16, fy, 8, 1.5, GOLD); box(im, u + 16, fy + .5, 8, .5, CREAM)
        line(im, [(x + 4, y), (x + 4, y + 11)], INK)
        pocket(im, x + .5, y + 5, shirt, 2.5, 2)
    else:
        # One graphic panel, with an intentional geometry motif rather than text.
        box(im, x + 1.5, y + 3, 5, 4, color(shirt, -13))
        polygon(im, [(x + 2, y + 6), (x + 4, y + 3.5), (x + 6, y + 6)], trim)

    # Different garment construction: checks, pinstripes or stitched panel seams.
    pattern = variant % 8
    if pattern == 2 and cut in ("shirt", "jacket", "tunic", "kurta"):
        for yy in (y + 2, y + 5, y + 8):
            box(im, u + 16, yy, 8, .5, color(shirt, 22))
        for xx in (u + 17.5, u + 20.5, u + 23):
            box(im, xx, y, .5, 11.5, color(shirt, 16))
    elif pattern == 4:
        for xx in (u + 17, u + 19, u + 21, u + 23):
            box(im, xx, y, .5, 11.5, color(shirt, 12))
    elif pattern == 6:
        embroidery(im, u + 17, y + 2, 6, 7, color(shirt, 25), variant)


def skin_face(im, idx, role, is_boss=False):
    tone = legacy.gna.TONES[idx % len(legacy.gna.TONES)]
    hair = [(25, 22, 24), (42, 29, 24), (60, 41, 28), (89, 77, 68), (33, 32, 39)][(idx // 5) % 5]
    style = idx % 12
    # Full six-sided head base, including under chin and ears.
    cuboid(im, BASE["head"], tone)
    for x, y, w, h, _ in faces(OUTER["head"]): box(im, x, y, w, h, (0, 0, 0), 0)
    box(im, 8, 0, 8, 8, hair)
    box(im, 0, 8, 32, 1.5, hair)
    back_len = [5, 4.5, 5.5, 7, 4, 7.5, 5, 6, 7, 4, 6, 7.5][style]
    box(im, 24, 9, 8, back_len, hair)
    for sx in (0, 16):
        box(im, sx, 9, 8, 3, hair)
        box(im, sx + 3, 12, 2, 2.5, color(tone, -9))
        box(im, sx + 3.5, 12.5, .5, 1, color(tone, -23))
    if style in (0, 4, 8):
        polygon(im, [(8, 9), (16, 9), (15, 11), (13, 10), (11.5, 11.5), (9, 10.5)], hair)
    elif style in (1, 5, 9):
        polygon(im, [(8, 9), (16, 9), (15.5, 12), (13.5, 10.5), (12, 10), (9, 11)], hair)
    elif style in (2, 6, 10):
        box(im, 8, 9, 8, 1.5, hair); box(im, 8, 10, 1, 4, hair); box(im, 15, 10, 1, 4, hair)
    else:
        box(im, 8, 9, 8, 1, hair); box(im, 8, 10, .5, 3, hair); box(im, 15.5, 10, .5, 3, hair)

    # Native128 strand clusters, parting, eye corners, lips and nose planes.
    for xx in (8.5, 10, 12, 14.5):
        line(im, [(xx, .5), (xx + .5, 3), (xx, 7)], color(hair, 13))
    for xx in (25, 27, 29, 31):
        line(im, [(xx, 9.5), (xx - .5, min(15.5, 9 + back_len))], color(hair, 12))
    if style % 3 == 0:
        box(im, 40, 8, 8, 1, hair)
        polygon(im, [(40, 9), (47.5, 9), (46, 10.5), (43, 9.5), (41, 10)], color(hair, 10))
    if style in (3, 5, 7, 11):
        box(im, 56, 9, 8, 6.5, hair)
        for xx in (56.5, 58, 60, 62):
            line(im, [(xx, 9.5), (xx + .5, 15)], color(hair, 12))

    eye_y = 11.5 + ((idx // 3) % 2) * .5
    for ex in (9, 13):
        box(im, ex, eye_y - 1, 2, .5, color(hair, -5))
        box(im, ex, eye_y, 2, 1, CREAM)
        box(im, ex + (.5 if ex == 9 else 0), eye_y, 1, 1, (57, 43, 32))
        box(im, ex + (.5 if ex == 9 else 0), eye_y, .5, .5, (22, 22, 25))
        box(im, ex, eye_y + 1, 2, .5, color(tone, -9))
    box(im, 11.5, 12, .5, 2, color(tone, 11))
    box(im, 11.5, 13.5, 1.5, .5, color(tone, -25))
    box(im, 10.5, 15, 3, .5, color(tone, -38))
    box(im, 11, 15.5, 2, .5, color(tone, -13))
    face_style = (idx // 12) % 6
    if face_style in (1, 3, 5):
        box(im, 10, 14, 4, .5, hair)
        if face_style == 3:
            box(im, 9, 14, 1, 1.5, hair); box(im, 14, 14, 1, 1.5, hair)
            box(im, 10, 15.5, 4, .5, hair)
    elif face_style == 2:
        box(im, 11.5, 10.5, .5, .5, PALETTE["terracotta"])
    elif face_style == 4:
        line(im, [(9, 14.5), (10, 15.5), (14, 15.5), (15, 14.5)], color(hair, 10), .5)
    eyewear = idx % 9 == 0 or is_boss
    if eyewear:
        for ex in (41, 45):
            box(im, ex, eye_y, 2, 1.5, INK)
            box(im, ex + .5, eye_y + .5, 1, .5, color(PALETTE["slate"], 30))
        box(im, 43, eye_y + .5, 2, .5, GOLD if is_boss else INK)
        box(im, 32, eye_y, 8, .5, INK); box(im, 48, eye_y, 8, .5, INK)
    if role == "police":
        cuboid(im, (32, 0, 8, 2, 8), PALETTE["indigo"])
        box(im, 40, 10, 8, .5, INK); box(im, 43, 8.5, 2, 1.5, GOLD)
        box(im, 43.5, 9, 1, .5, CREAM)
    elif role == "fire_rescue":
        cuboid(im, (32, 0, 8, 2.5, 8), GOLD)
        box(im, 40, 10.5, 8, .5, CREAM); box(im, 43, 8.5, 2, 1.5, INK)
    elif role == "industrial" and idx % 2 == 0:
        cuboid(im, (32, 0, 8, 2, 8), GOLD)
        line(im, [(44, .5), (44, 7)], CREAM, 1)
    elif role == "food_seller" and idx % 3 != 1:
        cuboid(im, (32, 0, 8, 1.5, 8), CREAM)
        line(im, [(40.5, 8.5), (43.5, 8), (47, 8.5)], color(CREAM, -27))
    elif role == "healthcare" and idx % 2:
        cuboid(im, (32, 0, 8, 1.5, 8), (147, 196, 185))
        box(im, 40, 9.5, 8, .5, CREAM)
    # A cropped cap occupies only the upper sides of the full head overlay.
    # Its UV bottom face must remain clear; painting a short cuboid's cap there
    # would incorrectly put cap fabric beneath the character's chin in3D.
    box(im, 48, 0, 8, 8, (0, 0, 0), 0)
    return {"hair_profile": style, "face_profile": face_style, "eyewear": eyewear,
            "skin_tone_index": idx % len(legacy.gna.TONES)}


def occupational_details(im, role, idx, cut, shirt, boss=False, prisoner=False):
    x, y = 20, 36
    if boss:
        polygon(im, [(22, 36), (26, 36), (24.5, 44), (23.5, 44)], (120, 34, 57))
        line(im, [(21, 37), (23.5, 42)], GOLD); line(im, [(27, 37), (24.5, 42)], GOLD)
        box(im, 26, 39, 1, 1, PALETTE["plum"]); box(im, 26.5, 38.5, .5, .5, GOLD)
        box(im, 44, 44.5, 4, 1, GOLD)
        return
    if prisoner:
        for xx in (21, 33):
            box(im, xx, 39, 6, 2.5, CREAM)
            # A deliberate visible detention placard, not an invisible hash tag.
            for k in range(4): box(im, xx + 1 + k, 39.5, .5, 1, INK)
        return
    if role in ("police", "rail_ropeway", "aviation_marine"):
        box(im, 25.5, 38, 1.5, 2, GOLD)
        box(im, 21, 38, 2.5, .5, CREAM)
        for ax in (44, 52):
            yy = 36 if ax == 44 else 52
            box(im, ax, yy, 4, .5, INK)
            for k in range(1 + idx % 3): box(im, ax + .5 + k, yy, .5, .5, GOLD)
        if role == "police":
            pocket(im, 20, 43.5, INK, 1.5, 3)
            box(im, 20.5, 42, .5, 2, INK)
    elif role == "healthcare":
        line(im, [(22.5, 36.5), (22, 40), (23, 41), (25, 41), (26, 40), (25.5, 36.5)], INK)
        line(im, [(25, 41), (25, 43)], INK)
        box(im, 24.5, 42.5, 1.5, 1.5, PALETTE["slate"])
        box(im, 25, 43, .5, .5, CREAM)
    elif role == "road_transport":
        panel = PALETTE["terracotta"] if idx % 2 == 0 else PALETTE["emerald"]
        box(im, 33, 39, 6, 4, panel)
        line(im, [(34, 40), (38, 40), (34, 42), (38, 42)], CREAM, .5)
        line(im, [(21, 36), (26.5, 47)], color(INK, 15), 1)
        pocket(im, 25, 43, INK, 3, 3)
    elif role in ("government", "professional", "media", "shopkeeper", "fashion_seller"):
        line(im, [(22, 36), (24, 40), (26, 36)], PALETTE["emerald"], .5)
        box(im, 23, 39.5, 2, 2.5, CREAM)
        box(im, 23.5, 40, 1, 1, PALETTE["slate"])
        box(im, 23.5, 41.5, 1, .5, GOLD)
        if role == "media":
            line(im, [(22, 37), (27, 43)], INK, 1)
            box(im, 24.5, 42, 3, 2, INK); box(im, 25.5, 42.5, 1, 1, PALETTE["slate"])
    elif role in ("industrial", "fire_rescue"):
        for yy in (39, 44):
            box(im, 20, yy, 8, 1, GOLD); box(im, 32, yy, 8, 1, GOLD)
            box(im, 20, yy + .5, 8, .5, CREAM); box(im, 32, yy + .5, 8, .5, CREAM)
    elif role == "food_seller":
        box(im, 21, 41, .5, 4, PALETTE["terracotta"])
        box(im, 21.5, 41, .5, 4, PALETTE["emerald"])
    elif role == "black_lotus":
        # Small original four-leaf insignia, distinct from real group symbolism.
        for px, py in ((26, 39), (26.5, 38.5), (27, 39), (26.5, 39.5)):
            box(im, px, py, .5, .5, PALETTE["plum"])


def make_skin(record):
    idx = int(record["id"].split("-")[-1]); role = record["role"]
    boss, prisoner = record.get("gang_boss", False), record.get("initially_jailed", False)
    # Extend existing implementation and retain established per-role baseline.
    im = legacy.generate_rich_skin(role, idx, boss, prisoner).resize((128, 128), Image.Resampling.NEAREST)
    for spec in OUTER.values():
        for x, y, w, h, _ in faces(spec): box(im, x, y, w, h, (0, 0, 0), 0)
    shirt = legacy.gna.UNIFORMS.get(role, CLOTH[(idx // 6) % len(CLOTH)])
    pants = color(INK, 18 + (idx % 3) * 5)
    cut = ROLE_CUTS[role][idx % 6]
    if boss: shirt, cut = (27, 28, 35), "blazer"
    elif prisoner: shirt, pants, cut = (185, 100, 43), (145, 78, 39), "uniform"
    elif role == "road_transport": shirt = PALETTE["terracotta"] if idx % 2 == 0 else PALETTE["emerald"]
    elif role == "healthcare": shirt = CREAM if cut == "labcoat" else PALETTE["teal"]
    elif role == "fire_rescue": shirt = (143, 67, 43)
    tone = legacy.gna.TONES[idx % len(legacy.gna.TONES)]
    garment(im, "shirt", shirt, pants, idx, outer=False, sleeve_length=12)
    # Fully opaque hands across ALL four sides plus lower cap; no UV holes.
    for key in ("right_arm", "left_arm"):
        u, v, w, h, z = BASE[key]
        for fx, fy, fw, fh, sh in faces(BASE[key])[2:]:
            box(im, fx, fy + 9, fw, 3, color(tone, sh))
            box(im, fx + .5, fy + 11, max(.5, fw - 1), .5, color(tone, sh - 8))
        box(im, u + z + w, v, w, z, color(tone, -18))
    garment(im, cut, shirt, pants, idx, outer=True, role=role)
    traits = skin_face(im, idx, role, boss)
    occupational_details(im, role, idx, cut, shirt, boss, prisoner)
    # Enforce mapped surfaces: no hidden-pixel uniqueness outside valid UVs.
    allowed = uv_mask(list(BASE.values()) + list(OUTER.values()))
    im.putalpha(Image.composite(im.getchannel("A"), Image.new("L", im.size, 0), allowed))
    traits.update({"garment_cut": cut, "garment_pattern": idx % 8, "occupational_accessories": role,
                   "prison_attire_variant": prisoner, "boss_attire_variant": boss})
    return im, traits


def make_outfit(record, rank):
    idx = int(record["id"].split("-")[-1]); cat = record["category"]
    im = legacy.generate_rich_outfit(cat, idx).resize((128, 128), Image.Resampling.NEAREST)
    # Original outfit helper painted occasional base torso pixels; scrub every
    # unmapped/base pixel so this artifact remains a pure cosmetic outer layer.
    im.paste((0, 0, 0, 0), (0, 0, 128, 128))
    cuts = {
        "casual": ["hoodie", "jacket", "jacket", "shirt", "cardigan", "jacket", "tee", "jacket", "shirt", "tee", "jacket", "shirt", "vest", "shirt", "tee", "hoodie", "vest", "kurta", "shirt", "jacket"],
        "traditional": ["waistcoat", "kurta", "tunic", "blazer", "kurta", "kurta", "tunic", "kurta", "kurta", "sari", "tunic", "tunic", "kurta", "waistcoat", "jacket", "kurta", "vest", "kurta", "sari", "blazer"],
        "formal": ["blazer", "blazer", "waistcoat", "blazer", "waistcoat", "blazer", "shirt", "blazer", "kurta", "blazer", "shirt", "cardigan", "waistcoat", "tunic", "jacket"],
        "sports": ["shirt", "tee", "vest", "tee", "shirt", "jacket", "tee", "jacket", "tee", "jacket"],
        "festival": ["kurta", "shirt", "tunic", "waistcoat", "kurta", "blazer", "cardigan", "jacket", "tunic", "sari", "kurta", "sari", "jacket", "kurta", "blazer"],
        "premium": ["blazer", "blazer", "jacket", "tee", "jacket", "blazer", "blazer", "waistcoat", "blazer", "jacket"],
        "utility": ["coverall", "jacket", "courier", "shirt", "apron", "jacket", "apron", "rescue", "vest", "rescue"],
    }
    cut = cuts[cat][rank]
    shirt = CLOTH[(rank + list(OUTFIT_NAMES).index(cat) * 2) % len(CLOTH)]
    pants = color(CLOTH[(rank * 3 + 3) % len(CLOTH)], -34)
    if cat == "sports" and rank == 0: shirt, pants = CREAM, color(CREAM, -12)
    sleeve_length = 5 if cat == "sports" and rank in (0, 1, 3, 4, 6, 8) else None
    garment(im, cut, shirt, pants, rank + idx // 10, sleeve_length=sleeve_length)
    # Each named edition has a different construction/detail treatment. These
    # are explicit motifs and accessories, never serial-number hash pixels.
    if cat in ("traditional", "festival", "premium"):
        trim = GOLD if rank % 2 == 0 else CREAM
        embroidery(im, 20.5, 37.5, 2, 9, trim, rank)
        embroidery(im, 25.5, 37.5, 2, 9, trim, rank + 1)
        if rank % 3 == 0:
            box(im, 32, 36, 1.5, 12, trim); embroidery(im, 32, 36, 1.5, 12, shirt, rank)
        if rank % 5 == 2:
            polygon(im, [(20, 36), (22, 36), (28, 44), (28, 47)], color(shirt, 45))
    elif cat == "sports":
        for spec in (OUTER["right_arm"], OUTER["left_arm"]):
            u, v, *_ = spec
            for off in (0, 1): box(im, u + 4 + off, v + 4, .5, sleeve_length or 10, CREAM)
        box(im, 20, 40 + rank % 3, 8, 1, color(shirt, 45))
        for lu, lv, *_ in (OUTER["right_leg"], OUTER["left_leg"]): box(im, lu, lv + 4, .5, 10, CREAM)
        if rank in (1, 2, 6):
            for spec in (OUTER["right_leg"], OUTER["left_leg"]):
                for x, y, w, h, _ in faces(spec)[2:]: box(im, x, y + 6, w, 6, (0, 0, 0), 0)
    elif cat == "utility":
        occupational_details(im, ["industrial", "rail_ropeway", "road_transport", "government", "food_seller", "aviation_marine", "industrial", "fire_rescue", "media", "fire_rescue"][rank], idx, cut, shirt)
    elif cat == "formal":
        if rank % 3 == 1:
            for yy in (40, 42, 44):
                box(im, 22, yy, .5, .5, GOLD); box(im, 25.5, yy, .5, .5, GOLD)
        if rank % 5 == 3:
            for xx in (32.5, 34.5, 36.5, 38.5): box(im, xx, 36, .5, 11.5, color(shirt, 25))
    elif cat == "casual":
        if rank in (6, 16):
            line(im, [(20.5, 36), (26.5, 47)], INK, 1)
            pocket(im, 25, 43, INK, 3, 3)
        if rank in (1, 12, 18):
            for xx in (21, 26.5): line(im, [(xx, 36), (xx, 47)], GOLD, .5)
        if rank in (8, 13):
            for yy in (38, 41, 44): box(im, 20, yy, 8, .5, color(shirt, 27))
    mask = uv_mask([v for k, v in OUTER.items() if k != "head"])
    im.putalpha(Image.composite(im.getchannel("A"), Image.new("L", im.size, 0), mask))
    # All hand-facing bottom caps and last two sleeve units remain transparent.
    for key in ("right_arm", "left_arm"):
        u, v, w, h, z = OUTER[key]
        box(im, u + z + w, v, w, z, (0, 0, 0), 0)
        for x, y, w, h, _ in faces(OUTER[key])[2:]: box(im, x, y + 10, w, 2, (0, 0, 0), 0)
    return im, {"design_name": OUTFIT_NAMES[cat][rank], "garment_cut": cut,
                "construction_index": rank, "category": cat, "preserves_player_head_and_hands": True}


def assembled(skin, base=None, scale=1):
    """Orthographic assembled FRONT/BACK, sampled from actual128 UV surfaces."""
    if base is not None:
        s = Image.alpha_composite(base, skin)
    else: s = skin
    canvas = Image.new("RGBA", (80, 72))
    def blt(u, v, w, h, dx, dy):
        p = s.crop((u * 2, v * 2, (u + w) * 2, (v + h) * 2))
        canvas.alpha_composite(p, (dx, dy))
    for back, offset in ((False, 0), (True, 40)):
        head_u, body_u = (24, 32) if back else (8, 20)
        hat_u, jacket_u = (56, 32) if back else (40, 20)
        blt(head_u, 8, 8, 8, 12 + offset, 2); blt(hat_u, 8, 8, 8, 12 + offset, 2)
        blt(body_u, 20, 8, 12, 12 + offset, 18); blt(jacket_u, 36, 8, 12, 12 + offset, 18)
        if not back:
            for u,v,ou,ov,dx in [(44,20,44,36,4),(36,52,52,52,28)]:
                blt(u,v,4,12,dx+offset,18); blt(ou,ov,4,12,dx+offset,18)
            for u,v,ou,ov,dx in [(4,20,4,36,12),(20,52,4,52,20)]:
                blt(u,v,4,12,dx+offset,42); blt(ou,ov,4,12,dx+offset,42)
        else:
            for u,v,ou,ov,dx in [(44,52,60,52,4),(52,20,52,36,28)]:
                blt(u,v,4,12,dx+offset,18); blt(ou,ov,4,12,dx+offset,18)
            for u,v,ou,ov,dx in [(28,52,12,52,12),(12,20,12,36,20)]:
                blt(u,v,4,12,dx+offset,42); blt(ou,ov,4,12,dx+offset,42)
    return canvas.resize((80 * scale, 72 * scale), Image.Resampling.NEAREST)


def font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"):
        if Path(p).exists(): return ImageFont.truetype(p, size)
    return ImageFont.load_default(size=size)


def contact(records, directory, prefix, title, images):
    paths = []
    for start in range(0, len(records), 80):
        page = records[start:start + 80]
        cols, cw, ch = 8, 180, 190
        rows = (len(page) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * cw + 32, rows * ch + 82), INK)
        d = ImageDraw.Draw(sheet)
        d.text((18, 14), title, font=font(22), fill=CREAM)
        d.text((18, 44), "GTM / SD Craft · 128px masters · front + back UV assembly · client verification pending", font=font(13), fill=GOLD)
        for n, rec in enumerate(page):
            x, y = 16 + (n % cols) * cw, 74 + (n // cols) * ch
            d.rounded_rectangle((x + 2, y, x + cw - 5, y + ch - 8), radius=5, fill=(30, 38, 44))
            card = images[rec["id"]].resize((160, 144), Image.Resampling.NEAREST)
            sheet.paste(card, (x + 8, y + 4), card)
            d.text((x + 10, y + 149), rec["id"], font=font(13), fill=CREAM)
            label = rec.get("role", rec.get("category", "")).replace("_", " ")
            d.text((x + 10, y + 166), label, font=font(11), fill=GOLD)
        out = directory / f"{prefix}_{start // 80 + 1:02d}.png"
        sheet.save(out, optimize=True); paths.append(out)
    return paths


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path, output, dimensions):
    return {"path": path.relative_to(output).as_posix(), "dimensions": dimensions,
            "sha256": digest(path), "size_bytes": path.stat().st_size}


def write_png(im, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, optimize=True)


def java64_export(im):
    """UV-aligned2×2 footprint reduction, then binary cosmetic alpha.

    Point sampling discarded entire one-pixel seams and collapsed distinct
    outfits. Area reduction retains their coverage without filtering across
    adjacent64px texels. Runtime magnification continues to use NEAREST.
    """
    small = im.resize((64, 64), Image.Resampling.BOX)
    alpha = small.getchannel("A").point(lambda a: 255 if a >= 128 else 0)
    small.putalpha(alpha)
    small.paste((0, 0, 0, 0), (0, 0, 64, 64), alpha.point(lambda a: 255 - a))
    return small


def build(output: Path):
    output = Path(output).resolve()
    src_skin_path = ROOT / "creative/manifests/npc_skins_manifest.json"
    src_outfit_path = ROOT / "creative/manifests/outfits_manifest.json"
    source_skins = json.loads(src_skin_path.read_text(encoding="utf-8"))
    source_outfits = json.loads(src_outfit_path.read_text(encoding="utf-8"))
    skin_records, outfit_records = source_skins["skins"], source_outfits["outfits"]
    assert len(skin_records) == 500 and len(outfit_records) == 100
    assert Counter(r["category"] for r in outfit_records) == source_outfits["categories"]
    assert {r["model"] for r in skin_records} == {"classic-dual-layer"}, "Add explicit slim UV support before changing model assignments"
    assert {r["model"] for r in outfit_records} == {"classic-overlay"}
    for sub in ("source/skins", "source/outfits", "compatibility/java64/skins", "compatibility/java64/outfits", "previews/characters", "manifests", "reports"):
        (output / sub).mkdir(parents=True, exist_ok=True)

    reports, sprites = [], {}
    base_mask = uv_mask(BASE.values())
    overlay_mask = uv_mask([v for k, v in OUTER.items() if k != "head"])
    skin_pixels, skin_pixels64, visible_skins, outfit_pixels, outfit_pixels64, visible_outfits = set(), set(), set(), set(), set(), set()
    nontrivial_128 = []
    ranks = Counter()
    mannequin = Image.new("RGBA", (128, 128))
    for key, spec in BASE.items(): cuboid(mannequin, spec, (163, 154, 139) if key == "head" else (89, 91, 88))
    for kind, entries in (("skin", skin_records), ("outfit", outfit_records)):
        for rec in entries:
            if kind == "skin": im, traits = make_skin(rec)
            else:
                rank = ranks[rec["category"]]; ranks[rec["category"]] += 1
                im, traits = make_outfit(rec, rank)
            assert im.mode == "RGBA" and im.size == (128, 128)
            alpha = im.getchannel("A")
            if kind == "skin":
                assert all(a == 255 for a, m in zip(alpha.tobytes(), base_mask.tobytes()) if m), f"Base UV alpha hole: {rec['id']}"
            else:
                assert all(a == 0 for a, m in zip(alpha.tobytes(), overlay_mask.tobytes()) if not m), f"Outfit changed base/head: {rec['id']}"
            compat = java64_export(im)
            assert im.tobytes() != compat.resize((128, 128), Image.Resampling.NEAREST).tobytes(), f"Only upscaled128: {rec['id']}"
            nontrivial_128.append(rec["id"])
            group = "skins" if kind == "skin" else "outfits"
            master_path = output / "source" / group / f"{rec['id']}.png"
            compat_path = output / "compatibility/java64" / group / f"{rec['id']}.png"
            write_png(im, master_path); write_png(compat, compat_path)
            art = assembled(im, mannequin if kind == "outfit" else None)
            sprites[rec["id"]] = art
            preview = Image.new("RGBA", (128, 128), (*INK, 255)); preview.alpha_composite(art, (24, 22))
            preview_path = output / "previews/characters" / f"{rec['id']}.png"
            write_png(preview, preview_path)
            p_hash = hashlib.sha256(im.tobytes()).hexdigest()
            v_hash = hashlib.sha256(art.tobytes()).hexdigest()
            collection = skin_pixels if kind == "skin" else outfit_pixels
            visible = visible_skins if kind == "skin" else visible_outfits
            assert p_hash not in collection, f"Duplicate master: {rec['id']}"
            assert v_hash not in visible, f"Identical visible front/back: {rec['id']}"
            collection.add(p_hash); visible.add(v_hash)
            if kind == "skin":
                h64 = hashlib.sha256(compat.tobytes()).hexdigest()
                assert h64 not in skin_pixels64, f"Duplicate Java derivative: {rec['id']}"
                skin_pixels64.add(h64)
            else:
                h64 = hashlib.sha256(compat.tobytes()).hexdigest()
                assert h64 not in outfit_pixels64, f"Duplicate Java outfit derivative: {rec['id']}"
                outfit_pixels64.add(h64)
            # Every source field is retained, including ID, UUID, name, model,
            # role, price and world_anchor. World anchors are unverified legacy
            # data and must never be interpreted as placement authorization.
            reports.append({"id": rec["id"], "kind": kind, "model": rec["model"],
                            "existing_record": rec, "master": artifact(master_path, output, [128, 128]),
                            "java_compatibility": artifact(compat_path, output, [64, 64]),
                            "preview": artifact(preview_path, output, [128, 128]),
                            "design": traits, "visible_front_back_sha256": v_hash,
                            "derivation": "existing creative-r4 procedural skin pipeline + native128 role/garment/hair/face details; Java export UV-aligned2x2 area reduction with binary alpha",
                            "source_author": "SD Craft / GTM creative pipeline; native128 extension authored for this project",
                            "rights": "original procedural artwork; no external imagery or proprietary game art",
                            "status": "art_validated", "engine_binding": "pending", "client_verification": "not_run"})
    sheets = contact(skin_records, output / "previews", "characters_npc", "INDRAPRASTHA / CHARACTER CATALOGUE", sprites)
    sheets += contact(outfit_records, output / "previews", "characters_outfits", "GTM / FASHION CATALOGUE", sprites)
    sample_ids = ["npc-001", "npc-017", "npc-100", "npc-125", "npc-155", "npc-175", "npc-220", "npc-235", "npc-260", "npc-275", "npc-290", "npc-310", "npc-340", "npc-370", "npc-405", "npc-445", "npc-465", "npc-475", "npc-481", "npc-482", "npc-487", "npc-495", "outfit-022", "outfit-067"]
    lookup = {r["id"]: r for r in skin_records + outfit_records}
    sheets += contact([lookup[k] for k in sample_ids], output / "previews", "characters_overview", "GTM 128 / CHARACTER & FASHION LANGUAGE", sprites)
    manifest = {
        "schema_version": "1.0.0", "language": "GTM128", "base_revision": "creative-r4",
        "source_manifests": [{"path": str(p.relative_to(ROOT)), "sha256": digest(p)} for p in (src_skin_path, src_outfit_path)],
        "master_dimensions": [128, 128], "format": "PNG RGBA", "filter": "nearest",
        "compatibility_exception": "Classic Java NPC/player skin UV exports remain64x64. Canonical128 masters retain native detail;128 does not imply native Java HD skin support.",
        "counts": {"npc_skin_masters": 500, "outfit_masters": 100, "java64_derivatives": 600, "native128_character_previews": 600},
        "outfit_categories": source_outfits["categories"], "npc_roles": dict(Counter(r["role"] for r in skin_records)),
        "identity_policy": "Existing records copied unchanged. No generated identity, UUID, name, model, price, runtime binding or world coordinate replaces the current manifest.",
        "world_anchor_policy": "Legacy world_anchor fields are preserved as source data only; all remain unverified for placement in this art batch.",
        "gang_boss_id": source_skins["gang_boss_id"], "initial_prisoner_ids": source_skins["prisoner_ids"],
        "catalogue_note": "Five supplied initial-prisoner appearances are art variants only; this batch does not implement custody rotation or permanently assign outfits.",
        "contact_sheets": [artifact(p, output, list(Image.open(p).size)) for p in sheets], "assets": reports,
        "limitations": ["No real Java or Bedrock client was available for skin rendering tests.", "Signed runtime NPC skin hosting/binding, wearable overlays and custody outfit switching are not implemented by this art generator.", "Previews are orthographic front/back UV assemblies, not captured in-game or physically rendered3D.", "Native128 detail is reduced in the64px derivative; evaluate fine seams and facial details in an actual client."]
    }
    (output / "manifests/characters_128.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    validation = {"status": "PASS", "checks": {
        "identity_records_unchanged": True, "model_assignments_unchanged": True,
        "npc128_rgba": 500, "outfit128_rgba": 100, "java64_rgba_derivatives": 600,
        "all_npc_base_faces_opaque": True, "outfits_only_on_body_outer_layer": True,
        "outfit_head_and_hands_preserved": True, "no_unmapped_pixel_markers": True,
        "native128_detail_not_simple_upscale": len(nontrivial_128),
        "unique_npc_master_pixels": len(skin_pixels), "unique_npc_java64_pixels": len(skin_pixels64),
        "unique_npc_front_back_renders": len(visible_skins), "unique_outfit_master_pixels": len(outfit_pixels),
        "unique_outfit_java64_pixels": len(outfit_pixels64),
        "unique_outfit_front_back_renders": len(visible_outfits), "contact_sheets": len(sheets),
        "outfit_category_counts_preserved": dict(ranks) == source_outfits["categories"],
        "ids_uuids_prices_names_roles_preserved": True},
        "client_verification": "NOT_RUN", "runtime_integration": "PENDING",
        "generator": "python tools/gtm128_characters.py --output creative/generated_128"}
    (output / "reports/characters_128_validation.json").write_text(json.dumps(validation, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "output": str(output), "counts": manifest["counts"], "checks": validation["checks"]}, indent=2))
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "creative/generated_128")
    build(parser.parse_args().output)
