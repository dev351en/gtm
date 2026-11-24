#!/usr/bin/env python3
"""
Faithful 32x Inspired Pixel-Art Texture Synthesizer for GTM Indraprastha.

Design Principles (Faithful 32x Aesthetic):
- Strict discrete integer 32x32 pixel grid: zero continuous trig/sine gradients or Gaussian blur.
- Hue-shifted quantized color ramps (6 tones: deep shadow, cool shadow, mid_dark, mid, highlight, specular).
  * Shadows shift cooler (slate/indigo/plum) for crisp separation.
  * Highlights shift warmer (cream/gold/ivory) for sunlight readability.
- 1-pixel directional bevels (top-left warm light, bottom-right cool shadow) and pixel-clustered motifs
  (cobblestone facets, plank seams + grain knots, glowing crystal nodules, diamond sea prism cores,
  overlapping leaf clusters, corrugated steel ribs, headlights, grilles, ECG screens, books, and car trims).
"""
import numpy as np
from PIL import Image, ImageColor


def hex_to_rgb(h: str) -> np.ndarray:
    return np.array(ImageColor.getrgb(h), dtype=np.float32)


def make_ramp(hex_base: str, contrast: float = 1.0) -> np.ndarray:
    """Return a 6x3 uint8 hue-shifted palette: [0:deep, 1:shadow, 2:mid_dark, 3:mid, 4:hi, 5:spec]."""
    b = hex_to_rgb(hex_base)
    cool = np.array([18.0, 20.0, 52.0], dtype=np.float32)
    warm = np.array([255.0, 246.0, 214.0], dtype=np.float32)

    t0 = b * (1.0 - 0.56 * contrast) + cool * (0.34 * contrast)
    t1 = b * (1.0 - 0.32 * contrast) + cool * (0.16 * contrast)
    t2 = b * (1.0 - 0.14 * contrast) + cool * (0.04 * contrast)
    t3 = b.copy()
    t4 = b * (1.0 - 0.24 * contrast) + warm * (0.24 * contrast)
    t5 = b * (1.0 - 0.48 * contrast) + warm * (0.48 * contrast)
    ramp = np.stack([t0, t1, t2, t3, t4, t5], axis=0)
    return np.clip(ramp, 0, 255).astype(np.uint8)


def _blank(alpha: int = 255) -> np.ndarray:
    arr = np.zeros((32, 32, 4), dtype=np.uint8)
    arr[:, :, 3] = alpha
    return arr


def _apply_indices(idx_map: np.ndarray, ramp: np.ndarray, alpha_map: np.ndarray = None) -> np.ndarray:
    out = _blank()
    clipped = np.clip(idx_map, 0, len(ramp) - 1)
    out[:, :, :3] = ramp[clipped]
    if alpha_map is not None:
        out[:, :, 3] = alpha_map
    return out


def _hash_grid(seed: int) -> np.ndarray:
    yy, xx = np.mgrid[0:32, 0:32]
    v = ((xx + seed * 17) * 374761393 + (yy + seed * 31) * 668265263) & 0xFFFFFFFF
    v = ((v ^ (v >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((v >> 24) & 0xFF).astype(np.int32)


def tex_planks(hex_col: str, vertical: bool = False, seed: int = 1) -> np.ndarray:
    """Faithful 32x 4-board wood planks with 1px seams, top bevel highlights, knots & butt-joints."""
    ramp = make_ramp(hex_col, contrast=0.95)
    h = _hash_grid(seed)
    idx = np.full((32, 32), 3, dtype=np.int32)

    for y in range(32):
        board = y // 8
        ly = y % 8
        joint_x = ((board * 13 + seed * 5) % 22) + 5
        for x in range(32):
            # Grain streak 2..4px horizontal clusters
            cluster = ((x + board * 5 + (ly * 7)) // 4)
            hv = h[y, x]
            if ly == 7 or x == joint_x:
                idx[y, x] = 0
            elif ly == 0 or x == (joint_x + 1) % 32:
                idx[y, x] = 4
            elif ly == 6 or x == (joint_x - 1) % 32:
                idx[y, x] = 1
            elif hv < 28:
                idx[y, x] = 2
            elif hv > 228:
                idx[y, x] = 4
            elif ((cluster + board) % 5 == 0) and (ly in (2, 3, 5)):
                idx[y, x] = 2
            else:
                idx[y, x] = 3

        # Knot detail on board 1 and 3
        if board in (1, 3) and ly in (2, 3, 4):
            kx = 10 if board == 1 else 21
            for dx in range(-1, 2):
                px = (kx + dx) % 32
                if ly == 3 and dx == 0:
                    idx[y, px] = 1
                else:
                    idx[y, px] = 2

    out = _apply_indices(idx, ramp)
    if vertical:
        out = np.transpose(out, (1, 0, 2)).copy()
    return out


def tex_log_side(hex_col: str, birch: bool = False, seed: int = 1) -> np.ndarray:
    """Faithful 32x bark stripes or creamy birch lenticel knots."""
    ramp = make_ramp(hex_col, contrast=1.05 if not birch else 0.72)
    h = _hash_grid(seed + 19)
    idx = np.full((32, 32), 3, dtype=np.int32)

    if birch:
        idx[:, :] = 4
        idx[(h < 45)] = 3
        idx[(h > 220)] = 5
        # Characteristic horizontal charcoal knots
        rng = np.random.default_rng(700 + seed)
        dark = make_ramp("#2A2D34", contrast=1.0)
        out = _apply_indices(idx, ramp)
        for _ in range(11):
            ky = int(rng.integers(2, 30))
            kx = int(rng.integers(0, 32))
            kw = int(rng.integers(4, 11))
            for dx in range(kw):
                px = (kx + dx) % 32
                out[ky, px, :3] = dark[1] if dx % 3 != 0 else dark[0]
                if ky + 1 < 32 and 1 <= dx <= kw - 2:
                    out[ky + 1, px, :3] = dark[0] if dx % 2 == 0 else dark[2]
                if ky - 1 >= 0:
                    out[ky - 1, px, :3] = ramp[5]
        return out

    # Furrowed bark (oak / spruce / dark oak)
    for x in range(32):
        col_kind = (x + (seed % 3)) % 4
        for y in range(32):
            wobble = (h[y // 2 * 2, x] >> 6) % 2
            ridge = (x + wobble) % 4
            if ridge == 0:
                idx[y, x] = 0 if h[y, x] < 160 else 1
            elif ridge == 1:
                idx[y, x] = 4 if h[y, x] > 110 else 3
            elif ridge == 2:
                idx[y, x] = 3 if h[y, x] > 60 else 2
            else:
                idx[y, x] = 2 if h[y, x] < 180 else 1
    return _apply_indices(idx, ramp)


def tex_log_top(bark_hex: str, heart_hex: str, seed: int = 1) -> np.ndarray:
    """Faithful 32x concentric irregular growth rings with outer bark rim."""
    bark = make_ramp(bark_hex, contrast=1.0)
    heart = make_ramp(heart_hex, contrast=0.9)
    h = _hash_grid(seed + 41)
    out = _blank()
    for y in range(32):
        for x in range(32):
            dx = abs(x - 15.5)
            dy = abs(y - 15.5)
            cheb = max(dx, dy)
            eucl = np.sqrt(dx * dx + dy * dy)
            r = cheb * 0.45 + eucl * 0.55 + ((h[y, x] & 3) - 1.5) * 0.35
            if r >= 13.4:
                c = bark[1 if (x + y) % 2 == 0 else 2]
            elif r >= 11.6:
                c = bark[4]
            elif int(r) in (9, 6, 3):
                c = heart[1 if h[y, x] < 170 else 2]
            elif int(r) in (8, 5, 2):
                c = heart[4 if h[y, x] > 90 else 3]
            else:
                c = heart[3 if h[y, x] > 40 else 2]
            out[y, x, :3] = c
    return out


def tex_cobble(hex_col: str, mossy_hex: str = None, seed: int = 1) -> np.ndarray:
    """Faithful 32x interlocking beveled cobblestones on wrapping 32x32 torus."""
    ramp = make_ramp(hex_col, contrast=1.08)
    rng = np.random.default_rng(310 + seed * 17)
    pts = rng.uniform(0, 32, size=(16, 2))
    cell_tone = rng.choice([2, 3, 3, 4], size=16)

    cid = np.zeros((32, 32), dtype=np.int32)
    edge = np.zeros((32, 32), dtype=bool)

    for y in range(32):
        for x in range(32):
            dists = []
            for i, (px, py) in enumerate(pts):
                dx = abs(x - px)
                dx = min(dx, 32.0 - dx)
                dy = abs(y - py)
                dy = min(dy, 32.0 - dy)
                dists.append((dx * dx + dy * dy, i))
            dists.sort()
            d1, i1 = dists[0]
            d2, _ = dists[1]
            cid[y, x] = i1
            if np.sqrt(d2) - np.sqrt(d1) < 1.35:
                edge[y, x] = True

    idx = np.zeros((32, 32), dtype=np.int32)
    h = _hash_grid(seed + 77)
    for y in range(32):
        for x in range(32):
            if edge[y, x]:
                idx[y, x] = 0
            elif edge[(y - 1) % 32, x] or edge[y, (x - 1) % 32]:
                idx[y, x] = 5 if edge[(y - 1) % 32, x] and edge[y, (x - 1) % 32] else 4
            elif edge[(y + 1) % 32, x] or edge[y, (x + 1) % 32]:
                idx[y, x] = 1
            else:
                base = int(cell_tone[cid[y, x]])
                if h[y, x] < 36:
                    base = max(1, base - 1)
                elif h[y, x] > 224:
                    base = min(4, base + 1)
                idx[y, x] = base

    out = _apply_indices(idx, ramp)
    if mossy_hex:
        mramp = make_ramp(mossy_hex, contrast=1.0)
        for y in range(32):
            for x in range(32):
                if (edge[y, x] or edge[(y - 1) % 32, x]) and (h[y, x] > 105):
                    out[y, x, :3] = mramp[4 if h[y, x] > 185 else 3]
                elif h[y, x] > 218 and ((x + y) % 3 == 0):
                    out[y, x, :3] = mramp[2]
    return out


def tex_bricks(hex_col: str, mortar_hex: str, bw: int = 16, bh: int = 8,
               cracked: bool = False, mossy_hex: str = None, seed: int = 1) -> np.ndarray:
    """Faithful 32x staggered masonry bricks with crisp 1px top lip & deep underside shadow."""
    ramp = make_ramp(hex_col, contrast=0.95)
    mortar = make_ramp(mortar_hex, contrast=0.8)
    h = _hash_grid(seed + 53)
    out = _blank()

    for y in range(32):
        row = y // bh
        ly = y % bh
        off = (row % 2) * (bw // 2)
        for x in range(32):
            bx = (x + off) // bw
            lx = (x + off) % bw
            if ly == 0 or lx == 0:
                out[y, x, :3] = mortar[2 if h[y, x] > 90 else 1]
                continue

            brick_hash = (row * 17 + bx * 31 + seed * 7) % 5
            base_tone = 3 if brick_hash in (1, 2, 3) else (2 if brick_hash == 0 else 4)
            if ly == 1 or lx == 1:
                t = min(5, base_tone + 1)
            elif ly == bh - 1 or lx == bw - 1:
                t = max(0, base_tone - 2)
            elif h[y, x] < 32:
                t = max(1, base_tone - 1)
            elif h[y, x] > 228:
                t = min(4, base_tone + 1)
            else:
                t = base_tone
            out[y, x, :3] = ramp[t]

    if cracked:
        for cx, cy in [(5, 3), (6, 4), (7, 4), (7, 5), (8, 6), (20, 11), (21, 12), (20, 13), (12, 20), (13, 21), (14, 22)]:
            out[cy, cx, :3] = ramp[0]
            if cy - 1 >= 0:
                out[cy - 1, cx, :3] = ramp[4]

    if mossy_hex:
        mramp = make_ramp(mossy_hex, contrast=1.0)
        for y in range(32):
            for x in range(32):
                if (y % bh in (0, 1, bh - 1) or (x + (y // bh) * 8) % bw in (0, 1)) and h[y, x] > 128:
                    out[y, x, :3] = mramp[3 if h[y, x] < 200 else 4]
                elif h[y, x] > 234:
                    out[y, x, :3] = mramp[2]
    return out


def tex_polished(hex_col: str, frame: int = 2, flecks: bool = True, seed: int = 1) -> np.ndarray:
    """Faithful 32x honed tile / polished stone / architectural concrete block."""
    ramp = make_ramp(hex_col, contrast=0.88)
    h = _hash_grid(seed + 111)
    idx = np.full((32, 32), 3, dtype=np.int32)

    if flecks:
        for y in range(32):
            for x in range(32):
                # Clustered 2x1 / 1x2 subtle stone specks (zero noisy static!)
                if ((x + y * 3 + seed) % 19 == 0) and (h[y, x] > 120):
                    idx[y, x] = 4
                elif ((x * 5 + y + seed) % 23 == 0) and (h[y, x] < 135):
                    idx[y, x] = 2

    # Faithful stepped 2px bezel rim
    if frame >= 2:
        idx[0, :31] = 5
        idx[:31, 0] = 5
        idx[1, 1:30] = 4
        idx[1:30, 1] = 4
        idx[31, 1:] = 0
        idx[1:, 31] = 0
        idx[30, 2:31] = 1
        idx[2:31, 30] = 1
        # Notched corners
        idx[0, 31] = 2
        idx[31, 0] = 2
        idx[1, 30] = 2
        idx[30, 1] = 2
    else:
        idx[0, :] = 4
        idx[:, 0] = 4
        idx[31, :] = 1
        idx[:, 31] = 1
    return _apply_indices(idx, ramp)


def tex_stone_rough(hex_col: str, contrast: float = 0.85, seed: int = 1) -> np.ndarray:
    """Faithful 32x horizontal sedimentary / volcanic rock strata clusters."""
    ramp = make_ramp(hex_col, contrast=contrast)
    h = _hash_grid(seed + 29)
    idx = np.full((32, 32), 3, dtype=np.int32)
    for y in range(32):
        for x in range(32):
            band = ((x // 3) * 13 + y * 7 + seed * 11) % 17
            hv = h[y, x]
            if band in (0, 1) and hv > 70:
                idx[y, x] = 2
            elif band in (2,) and hv < 90:
                idx[y, x] = 1
            elif band in (7, 8) and hv > 100:
                idx[y, x] = 4
            elif hv > 240:
                idx[y, x] = 4
            elif hv < 16:
                idx[y, x] = 2
    return _apply_indices(idx, ramp)


def tex_metal_block(hex_col: str, rivets: bool = True, specular: bool = True, seed: int = 1) -> np.ndarray:
    """Faithful 32x iron/gold/copper/steel panel with quantized diagonal gleam & corner bevels."""
    ramp = make_ramp(hex_col, contrast=1.08)
    idx = np.full((32, 32), 3, dtype=np.int32)

    for y in range(32):
        for x in range(32):
            if y < 2 or x < 2:
                idx[y, x] = 5 if (y == 0 or x == 0) else 4
            elif y >= 30 or x >= 30:
                idx[y, x] = 0 if (y == 31 or x == 31) else 1
            elif y == 2 or x == 2:
                idx[y, x] = 2
            elif y == 29 or x == 29:
                idx[y, x] = 4
            elif specular:
                d = x + y
                if d in (13, 14, 15, 29, 30):
                    idx[y, x] = 5
                elif d in (11, 12, 16, 17, 28, 31):
                    idx[y, x] = 4
                elif d in (44, 45, 46, 47):
                    idx[y, x] = 2

    if rivets:
        for ry, rx in ((4, 4), (4, 26), (26, 4), (26, 26)):
            idx[ry, rx] = 5
            idx[ry + 1, rx + 1] = 0
            idx[ry, rx + 1] = 2
            idx[ry + 1, rx] = 2

    return _apply_indices(idx, ramp)


def tex_glass(hex_col: str, frame_hex: str, alpha: int = 115, is_water: bool = False) -> np.ndarray:
    """Faithful 32x beveled glass pane with crisp stepped diagonal crystal sky glints."""
    ramp = make_ramp(hex_col, contrast=0.85)
    framp = make_ramp(frame_hex, contrast=0.9)
    out = _blank(alpha=alpha)
    out[:, :, :3] = ramp[2]

    if is_water:
        h = _hash_grid(73)
        for y in range(32):
            for x in range(32):
                band = ((x + (y // 2) * 3) + (h[y, x] >> 6)) % 14
                if band in (0, 1):
                    out[y, x, :3] = ramp[4]
                elif band in (5, 6, 7):
                    out[y, x, :3] = ramp[1]
                elif h[y, x] > 238:
                    out[y, x, :3] = ramp[5]
        out[:, :, 3] = 205
        return out

    # Crisp 2px outer frame + inner 1px step
    for y in range(32):
        for x in range(32):
            if x == 0 or y == 0 or x == 31 or y == 31:
                out[y, x, :3] = framp[1 if (x == 31 or y == 31) else 4]
                out[y, x, 3] = 245
            elif x == 1 or y == 1 or x == 30 or y == 30:
                out[y, x, :3] = framp[2 if (x == 30 or y == 30) else 5]
                out[y, x, 3] = 230

    # Faithful diagonal crystal reflection clusters (top-left & bottom-right)
    glints = [
        (4, 7), (5, 6), (6, 5), (7, 4),
        (5, 8), (6, 7), (7, 6), (8, 5),
        (6, 12), (7, 11), (8, 10), (9, 9), (10, 8), (11, 7), (12, 6),
        (21, 26), (22, 25), (23, 24), (24, 23), (25, 22), (26, 21),
    ]
    for gx, gy in glints:
        out[gy, gx, :3] = [245, 252, 255]
        out[gy, gx, 3] = 235
    return out


def tex_glowstone() -> np.ndarray:
    """Faithful 32x interlocking crystal glowstone nodules inside bronze crevices."""
    out = _blank()
    crystal_ramp = make_ramp("#F7B93E", contrast=1.15)
    mortar_ramp = make_ramp("#6D3D19", contrast=1.0)
    rng = np.random.default_rng(888)
    pts = rng.uniform(0, 32, size=(18, 2))
    for y in range(32):
        for x in range(32):
            dists = sorted(
                ((min(abs(x - px), 32 - abs(x - px)) ** 2 + min(abs(y - py), 32 - abs(y - py)) ** 2, i)
                 for i, (px, py) in enumerate(pts))
            )
            gap = np.sqrt(dists[1][0]) - np.sqrt(dists[0][0])
            if gap < 1.1:
                out[y, x, :3] = mortar_ramp[0 if gap < 0.55 else 2]
            elif gap < 2.2:
                out[y, x, :3] = crystal_ramp[2]
            elif gap < 3.6:
                out[y, x, :3] = crystal_ramp[4]
            else:
                out[y, x, :3] = crystal_ramp[5]
    return out


def tex_sea_lantern() -> np.ndarray:
    """Faithful 32x teal border frame + glowing cyan prism diamond core."""
    frame = make_ramp("#2A686E", contrast=1.0)
    core = make_ramp("#8EEBE0", contrast=0.95)
    out = _blank()
    for y in range(32):
        for x in range(32):
            dx = abs(x - 15.5)
            dy = abs(y - 15.5)
            box_d = max(dx, dy)
            manh = dx + dy
            if box_d > 14.2:
                out[y, x, :3] = frame[1 if (x >= 16 or y >= 16) else 4]
            elif box_d > 11.8:
                out[y, x, :3] = frame[2]
            elif box_d > 10.2:
                out[y, x, :3] = core[2]
            elif manh > 13.5:
                out[y, x, :3] = core[3]
            elif manh > 8.0:
                out[y, x, :3] = core[4]
            else:
                out[y, x, :3] = core[5]
    return out


def tex_redstone_lamp(lit: bool = True) -> np.ndarray:
    """Faithful 32x carved oak frame lattice + amber/glowing crystal interior."""
    wood = make_ramp("#522E16", contrast=1.0)
    bulb = make_ramp("#F5B642" if lit else "#4F3120", contrast=1.1 if lit else 0.9)
    out = _blank()
    for y in range(32):
        for x in range(32):
            dx = abs(x - 15.5)
            dy = abs(y - 15.5)
            is_frame = (max(dx, dy) > 13.4) or (abs(dx - dy) < 1.8 and max(dx, dy) > 8.5) or ((x in (15, 16) or y in (15, 16)) and max(dx, dy) > 9.5)
            if is_frame:
                out[y, x, :3] = wood[4 if (x < 16 and y < 16 and (x < 2 or y < 2)) else (0 if (x > 29 or y > 29) else 2)]
            else:
                d = dx + dy
                if d < 5.5:
                    out[y, x, :3] = bulb[5]
                elif d < 11.0:
                    out[y, x, :3] = bulb[4]
                elif d < 16.0:
                    out[y, x, :3] = bulb[3]
                else:
                    out[y, x, :3] = bulb[1]
    return out


def tex_leaves(hex_col: str, seed: int = 1) -> np.ndarray:
    """Faithful 32x discrete diamond/oval leaf sprig clusters with dark undersides & cutout holes."""
    ramp = make_ramp(hex_col, contrast=1.12)
    out = np.zeros((32, 32, 4), dtype=np.uint8)
    rng = np.random.default_rng(420 + seed * 29)
    for _ in range(34):
        cx = int(rng.integers(0, 32))
        cy = int(rng.integers(0, 32))
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if abs(dx) + abs(dy) <= 3:
                    px = (cx + dx) % 32
                    py = (cy + dy) % 32
                    if dx + dy <= -2:
                        tone = 5
                    elif dx + dy <= 0:
                        tone = 4
                    elif dx + dy == 1:
                        tone = 3
                    elif dx + dy == 2:
                        tone = 2
                    else:
                        tone = 0
                    out[py, px, :3] = ramp[tone]
                    out[py, px, 3] = 255
    return out


def tex_grass_top(hex_col: str, seed: int = 1) -> np.ndarray:
    ramp = make_ramp(hex_col, contrast=0.92)
    h = _hash_grid(seed + 131)
    idx = np.full((32, 32), 3, dtype=np.int32)
    for y in range(32):
        for x in range(32):
            v = h[y, x]
            if ((x + y * 2) % 7 == 0) and v > 95:
                idx[y, x] = 4
                if y + 1 < 32:
                    idx[y + 1, x] = 2
            elif v < 40:
                idx[y, x] = 2
            elif v > 215:
                idx[y, x] = 5 if (x + y) % 2 == 0 else 4
    return _apply_indices(idx, ramp)


def tex_grass_side(grass_hex: str, dirt_hex: str, seed: int = 1) -> np.ndarray:
    out = tex_dirt_sand_gravel(dirt_hex, style="dirt", seed=seed + 5)
    gramp = make_ramp(grass_hex, contrast=0.95)
    h = _hash_grid(seed + 211)
    heights = [6 + ((x * 5 + (h[0, x] >> 5)) % 6) for x in range(32)]
    for x in range(32):
        gh = heights[x]
        for y in range(gh):
            if y == gh - 1:
                out[y, x, :3] = gramp[1]
            elif y <= 1:
                out[y, x, :3] = gramp[4 if h[y, x] > 100 else 3]
            else:
                out[y, x, :3] = gramp[3 if h[y, x] > 70 else 2]
        # 1px crisp cast shadow on dirt beneath turf overhang
        if gh < 32:
            out[gh, x, :3] = (out[gh, x, :3].astype(np.float32) * 0.72).astype(np.uint8)
    return out


def tex_dirt_sand_gravel(hex_col: str, style: str = "dirt", seed: int = 1) -> np.ndarray:
    ramp = make_ramp(hex_col, contrast=0.88 if style != "sand" else 0.72)
    h = _hash_grid(seed + 67)
    idx = np.full((32, 32), 3, dtype=np.int32)
    if style == "sand":
        for y in range(32):
            for x in range(32):
                ripple = (y + ((x + y // 4) // 5)) % 6
                if ripple == 0 and h[y, x] > 80:
                    idx[y, x] = 4
                elif ripple == 3 and h[y, x] < 160:
                    idx[y, x] = 2
                elif h[y, x] > 235:
                    idx[y, x] = 5
    elif style == "gravel":
        for y in range(32):
            for x in range(32):
                cx, cy = (x // 4) * 4 + 2, (y // 4) * 4 + 2
                cell = h[cy % 32, cx % 32]
                dist = abs(x - cx) + abs(y - cy)
                if dist >= 3 and h[y, x] < 150:
                    idx[y, x] = 1
                elif (x - cx <= -1 and y - cy <= -1) and cell > 90:
                    idx[y, x] = 5 if cell > 180 else 4
                elif cell < 65:
                    idx[y, x] = 2
                elif cell > 205:
                    idx[y, x] = 4
    else:  # dirt / soil / asphalt
        for y in range(32):
            for x in range(32):
                clod = ((x // 2) * 11 + (y // 2) * 23 + seed * 3) % 13
                if clod in (0, 1) and h[y, x] > 90:
                    idx[y, x] = 2
                elif clod == 6 and h[y, x] > 120:
                    idx[y, x] = 4
                elif clod == 11 and h[y, x] < 110:
                    idx[y, x] = 1
                elif h[y, x] > 238:
                    idx[y, x] = 4
    return _apply_indices(idx, ramp)


def tex_fabric(hex_col: str, stitch: bool = True, seed: int = 1) -> np.ndarray:
    """Faithful 32x diagonal/crosshatch woven textile with stitched border."""
    ramp = make_ramp(hex_col, contrast=0.86)
    idx = np.full((32, 32), 3, dtype=np.int32)
    for y in range(32):
        for x in range(32):
            if (x % 2) ^ (y % 2):
                idx[y, x] = 2 if ((x // 2 + y // 2) % 2 == 0) else 3
            else:
                idx[y, x] = 4 if ((x + y) % 8 == 0) else 3
    if stitch:
        idx[0, :] = 4
        idx[:, 0] = 4
        idx[31, :] = 1
        idx[:, 31] = 1
        for k in range(3, 29, 4):
            idx[2, k:k + 2] = 5
            idx[29, k:k + 2] = 5
    return _apply_indices(idx, ramp)


def tex_carbon_mesh(hex_col: str, mesh: bool = False) -> np.ndarray:
    ramp = make_ramp(hex_col, contrast=0.95)
    idx = np.full((32, 32), 2, dtype=np.int32)
    for y in range(32):
        for x in range(32):
            if mesh:
                idx[y, x] = 0 if (x % 3 == 0 or y % 3 == 0) else (4 if (x % 3 == 1 and y % 3 == 1) else 3)
            else:
                tw = (x // 2 + y // 2) % 2
                idx[y, x] = 4 if (tw == 0 and (x % 2 == 0)) else (3 if tw == 0 else 1)
    return _apply_indices(idx, ramp)


def tex_tire_tread(hex_col: str = "#1C1F26") -> np.ndarray:
    ramp = make_ramp(hex_col, contrast=1.05)
    idx = np.full((32, 32), 2, dtype=np.int32)
    for y in range(32):
        for x in range(32):
            d = abs(x - 15.5)
            band = int(d + y * 1.1) % 6
            if band in (0, 1):
                idx[y, x] = 0
            elif band == 2:
                idx[y, x] = 4
            if x in (0, 1, 30, 31):
                idx[y, x] = 3
    return _apply_indices(idx, ramp)


def tex_hazard(col1: str = "#F5B800", col2: str = "#191C22") -> np.ndarray:
    r1 = make_ramp(col1, contrast=0.95)
    r2 = make_ramp(col2, contrast=0.95)
    out = _blank()
    for y in range(32):
        for x in range(32):
            s = ((x + y) // 6) % 2 == 0
            t = 4 if (y == 0 or x == 0) else (1 if (y == 31 or x == 31) else 3)
            out[y, x, :3] = (r1 if s else r2)[t]
    return out


# ---------------- PER-FACE AUTOMOTIVE / ARCHITECTURAL / PROP 32x32 TILES ----------------

def tex_headlight(bezel_hex: str = "#222730") -> np.ndarray:
    """Faithful 32x quad-reflector automotive headlight lens w/ amber turn blinker."""
    out = tex_metal_block("#DCE4EE", rivets=False, specular=True)
    dark = make_ramp(bezel_hex, contrast=1.0)
    amber = make_ramp("#F59E0B", contrast=1.0)
    # Dark outer frame
    out[0:3, :, :3] = dark[1]
    out[29:32, :, :3] = dark[0]
    out[:, 0:3, :3] = dark[1]
    out[:, 29:32, :3] = dark[0]
    # Bright xenon projector orb + ring
    for y in range(5, 27):
        for x in range(5, 21):
            d = np.sqrt((x - 12.5) ** 2 + (y - 15.5) ** 2)
            if d < 3.5:
                out[y, x, :3] = [255, 255, 246]
            elif d < 6.0:
                out[y, x, :3] = [255, 242, 185]
            elif d < 8.0:
                out[y, x, :3] = [180, 200, 224]
            else:
                out[y, x, :3] = dark[2]
    # Vertical amber indicator bar on right
    for y in range(5, 27):
        for x in range(23, 28):
            out[y, x, :3] = amber[4 if (y % 4 != 0) else 2]
    return out


def tex_taillight(bezel_hex: str = "#1C1F24") -> np.ndarray:
    """Faithful 32x segmented LED ruby taillight bar + reverse lamp."""
    dark = make_ramp(bezel_hex, contrast=1.0)
    red = make_ramp("#DC2626", contrast=1.15)
    amber = make_ramp("#F59E0B", contrast=1.0)
    out = _blank()
    out[:, :, :3] = dark[1]
    for y in range(4, 28):
        for x in range(3, 29):
            if y < 14 and x < 22:
                out[y, x, :3] = red[5 if (x % 5 in (1, 2) and y in (7, 8, 9)) else (4 if y < 9 else 3)]
            elif y >= 17 and x < 22:
                out[y, x, :3] = red[4 if y < 22 else 2]
            elif x >= 23 and y < 15:
                out[y, x, :3] = amber[4 if (y % 3 != 0) else 2]
            elif x >= 23 and y >= 17:
                out[y, x, :3] = [242, 246, 252]
    return out


def tex_grille(chrome_slats: bool = True) -> np.ndarray:
    dark = make_ramp("#171A20", contrast=1.0)
    cr = make_ramp("#D2DCE8" if chrome_slats else "#475569", contrast=1.05)
    out = _blank()
    out[:, :, :3] = dark[0]
    for y in range(32):
        if y in (0, 1, 30, 31):
            out[y, :, :3] = cr[4 if y < 2 else 1]
        elif y % 5 in (2, 3):
            out[y, 2:30, :3] = cr[4 if y % 5 == 2 else 2]
    # Center badge diamond
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if abs(dx) + abs(dy) <= 3:
                out[16 + dy, 16 + dx, :3] = cr[5 if abs(dx) + abs(dy) <= 1 else 2]
    return out


def tex_windshield(tint_hex: str = "#2A4C66", body_hex: str = "#B8C4D0") -> np.ndarray:
    """Faithful 32x tinted auto windshield with pillared frame, diagonal gleam & twin wipers."""
    out = tex_glass(tint_hex, "#191E26", alpha=235)
    bramp = make_ramp(body_hex, contrast=0.95)
    out[:, 0:2, :3] = bramp[3]
    out[:, 30:32, :3] = bramp[2]
    out[0:2, :, :3] = bramp[4]
    out[28:32, :, :3] = bramp[2]
    # Twin wiper arms at bottom glass
    for i in range(9):
        out[26 - i // 3, 5 + i, :3] = [18, 22, 28]
        out[26 - i // 3, 18 + i, :3] = [18, 22, 28]
    return out


def tex_car_door(body_hex: str, trim: str = "standard") -> np.ndarray:
    """Faithful 32x side door panel (window sill, chrome handle, optional taxi/police/BEST stripes)."""
    bramp = make_ramp(body_hex, contrast=1.0)
    out = tex_polished(body_hex, frame=1, flecks=False, seed=3)
    # Upper window cutout (y=2..14)
    glass = tex_glass("#25455C", "#161B22", alpha=240)
    out[2:14, 2:30] = glass[2:14, 2:30]
    out[14, :, :3] = bramp[5]  # window beltline catchlight
    out[15, :, :3] = [22, 26, 32]
    # Chrome/black door handle
    out[17:19, 20:26, :3] = [215, 225, 238] if trim != "police" else [240, 244, 248]

    if trim == "taxi":
        # Black/Yellow checkered strip along y=20..23
        out[20:24, :, :3] = [22, 24, 28]
        for x in range(0, 32, 4):
            out[20:22, x:x + 2, :3] = [245, 190, 0]
            out[22:24, (x + 2) % 32:(x + 2) % 32 + 2, :3] = [245, 190, 0]
    elif trim == "police":
        # White/Gold SDPD patrol door panel & gold star shield
        out[16:28, 4:28, :3] = [242, 245, 250]
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if abs(dx) + abs(dy) <= 3:
                    out[21 + dy, 16 + dx, :3] = [218, 172, 65] if abs(dx) + abs(dy) > 1 else [250, 225, 120]
    elif trim == "ambulance":
        out[20:23, :, :3] = [218, 38, 38]
        out[17:26, 14:18, :3] = [218, 38, 38]
        out[20:23, 11:21, :3] = [218, 38, 38]
    elif trim == "train":
        out[18:22, :, :3] = [245, 182, 24]
        out[23:27, :, :3] = [135, 32, 42]
    return out


def tex_car_wheel_hub(rim_hex: str = "#BCC7D4") -> np.ndarray:
    """Faithful 32x side wheel face: rubber sidewall ring + 5-spoke alloy rim + lug hub."""
    tire = make_ramp("#1A1D24", contrast=1.05)
    rim = make_ramp(rim_hex, contrast=1.1)
    out = _blank()
    for y in range(32):
        for x in range(32):
            dx, dy = x - 15.5, y - 15.5
            r = np.sqrt(dx * dx + dy * dy)
            if r > 15.0:
                out[y, x, :3] = tire[0]
            elif r > 9.5:
                out[y, x, :3] = tire[3 if int(r) % 2 == 0 else 2]
            elif r > 8.3:
                out[y, x, :3] = rim[5 if dx + dy < 0 else 1]
            elif r > 3.2:
                ang = np.arctan2(dy, dx)
                spoke = abs(np.sin(ang * 2.5)) > 0.72
                out[y, x, :3] = rim[4 if spoke else 0]
            else:
                out[y, x, :3] = [225, 180, 65] if r < 1.8 else rim[2]
    return out


def tex_license_plate() -> np.ndarray:
    out = _blank()
    out[:, :, :3] = [244, 246, 250]
    out[0:2, :, :3] = [30, 35, 44]
    out[30:32, :, :3] = [30, 35, 44]
    out[:, 0:2, :3] = [30, 35, 44]
    out[:, 30:32, :3] = [30, 35, 44]
    out[2:30, 2:6, :3] = [30, 82, 168]  # IND blue plate band
    # Stamped dark digit clusters
    for bx in (8, 12, 17, 21, 25):
        out[11:21, bx:bx + 2, :3] = [24, 28, 34]
        out[11:13, bx:bx + 3, :3] = [24, 28, 34]
        out[19:21, bx:bx + 3, :3] = [24, 28, 34]
    return out


def tex_bookshelf() -> np.ndarray:
    """Faithful 32x library bookcase w/ oak shelves & vivid vertical cloth-bound books."""
    out = tex_planks("#8D6034", seed=9)
    spines = ["#B8292F", "#1D4E89", "#236653", "#D6AD59", "#6B21A8", "#AD5637", "#0E7490", "#D97706"]
    for shelf_y in (2, 18):
        out[shelf_y:shelf_y + 12, 2:30, :3] = [28, 20, 14]
        x = 3
        i = shelf_y
        while x < 28:
            bw = 2 if (i % 3 != 0) else 3
            bh = 10 + (i % 2)
            col = make_ramp(spines[i % len(spines)], contrast=1.0)
            y0 = shelf_y + (12 - bh)
            out[y0:shelf_y + 12, x:x + bw, :3] = col[3]
            out[y0:y0 + 1, x:x + bw, :3] = col[5]
            out[y0 + 3, x:x + bw, :3] = [235, 200, 110]
            x += bw + (1 if i % 4 == 0 else 0)
            i += 1
    return out


def tex_screen_ui(kind: str = "ecg") -> np.ndarray:
    """Faithful 32x glowing electronic screen (ECG monitor, TV/PC, ATM keypad, Arcade)."""
    out = tex_metal_block("#1C222B", rivets=False, specular=False)
    out[3:29, 3:29, :3] = [12, 24, 34]
    if kind == "ecg":
        # ICU vital wave
        out[16, 4:10, :3] = [34, 211, 238]
        for gx, gy in [(10, 16), (11, 12), (12, 7), (13, 21), (14, 16), (15, 16), (16, 13), (17, 16)]:
            out[gy, gx, :3] = [110, 250, 170]
        out[16, 18:28, :3] = [34, 211, 238]
        out[6:9, 20:27, :3] = [239, 68, 68]
    elif kind == "atm":
        out[4:16, 4:28, :3] = [20, 110, 92]
        out[7:10, 8:24, :3] = [230, 190, 90]
        for ky in range(18, 28, 3):
            for kx in range(6, 26, 4):
                out[ky:ky + 2, kx:kx + 2, :3] = [180, 194, 210]
    else:  # pc / tv / display
        out[4:28, 4:28, :3] = [24, 62, 112]
        out[6:10, 6:18, :3] = [100, 210, 250]
        out[13:24, 6:26, :3] = [44, 108, 175]
        out[15:22, 8:15, :3] = [235, 185, 72]
    return out


def tex_appliance_front(kind: str = "stove") -> np.ndarray:
    out = tex_metal_block("#CBD5E1" if kind != "mandir" else "#7A4624", rivets=False, specular=True)
    if kind == "stove":
        out[2:29, 2:30, :3] = [34, 40, 48]
        for cx, cy in ((9, 9), (22, 9), (9, 22), (22, 22)):
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    r = abs(dx) + abs(dy)
                    if 3 <= r <= 5:
                        out[cy + dy, cx + dx, :3] = [95, 105, 118]
                    elif r <= 2:
                        out[cy + dy, cx + dx, :3] = [240, 110, 32]
    elif kind == "drawer":
        out = tex_planks("#8D562E", seed=21)
        for dy in (7, 15, 23):
            out[dy - 3:dy - 1, 12:20, :3] = [225, 185, 78]
    elif kind == "mandir":
        # Intricate Indian teak lattice / jali arch
        out[4:28, 4:28, :3] = [48, 24, 12]
        for y in range(4, 28, 4):
            out[y, 4:28, :3] = [224, 178, 72]
        for x in range(4, 28, 4):
            out[4:28, x, :3] = [224, 178, 72]
        out[10:22, 11:21, :3] = [245, 158, 11]
    elif kind == "speaker":
        out = tex_carbon_mesh("#1B2028", mesh=False)
        for cy, rr in ((10, 6), (22, 7)):
            for y in range(32):
                for x in range(32):
                    d = np.sqrt((x - 15.5) ** 2 + (y - cy) ** 2)
                    if abs(d - rr) < 1.3:
                        out[y, x, :3] = [175, 185, 200]
                    elif d < 2.2:
                        out[y, x, :3] = [214, 173, 89]
    return out
