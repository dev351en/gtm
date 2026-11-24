#!/usr/bin/env python3
"""
High-precision icon extractor & clean alpha matting pipeline for GTM Revision 4:
1. Slices & alpha-removes 32 fictional Brand Logos (256x256 RGBA) + generates 32 unique bespoke vector SVGs.
2. Accurately slices all 57 User V3 Phone/HUD icons directly from icons_v3_contact_sheet.png,
   strips card borders & bottom text labels, applies flood-fill smooth background removal, and
   saves crisp transparent RGBA PNGs (+ server-icon.png 64x64 opaque RGB).
3. Slices & alpha-removes Food Batch 1 (15 Indian dishes, 128x128 RGBA) from food_batch1_sheet.
"""
import hashlib
import json
from collections import deque
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
SOURCE = CREATIVE / "source"
MANIFESTS = CREATIVE / "manifests"
PREVIEWS = CREATIVE / "previews"

ARTIFACT_DIR = Path(r"C:\Users\brode\.gemini\antigravity\brain\ceee3c26-6ae4-4f1c-b357-09eb59f51997")
V3_SHEET = CREATIVE / "previews" / "icons_v3_contact_sheet.png"
BRANDS_B1 = ARTIFACT_DIR / "brands_batch1_sheet_1795546706698.jpg"
BRANDS_B2 = ARTIFACT_DIR / "brands_batch2_sheet_1795546747951.jpg"
FOOD_B1 = ARTIFACT_DIR / "food_batch1_sheet_1795546764988.jpg"


def remove_dark_bg_floodfill(im_rgb: Image.Image, thresh_hard: float = 22.0, thresh_soft: float = 48.0,
                             seed_points=None, keep_interior: bool = False) -> Image.Image:
    """
    Edge flood-fill background remover using Per-Pixel color distance from corner/edge backdrop median,
    with smooth anti-aliased alpha ramp so dark interiors (e.g. black cars, sunglasses) stay 100% opaque.
    """
    arr = np.array(im_rgb.convert("RGB"), dtype=np.float32)
    h, w, _ = arr.shape

    # Sample border pixels to estimate local background color
    border_samples = np.concatenate([
        arr[0, :, :], arr[h - 1, :, :], arr[:, 0, :], arr[:, w - 1, :]
    ], axis=0)
    # Use dark percentile so glowing bleed on one edge doesn't skew bg color
    bg_lum = border_samples.mean(axis=1)
    dark_samples = border_samples[bg_lum < np.percentile(bg_lum, 65)]
    if len(dark_samples) == 0:
        dark_samples = border_samples
    bg_color = np.median(dark_samples, axis=0)

    # Color + luminance distance from estimated dark background
    diff = np.linalg.norm(arr - bg_color[None, None, :], axis=2)

    # Flood fill from image perimeter to identify ONLY exterior background
    visited = np.zeros((h, w), dtype=bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if diff[y, x] < thresh_soft:
                visited[y, x] = True
                q.append((y, x))
    for y in range(1, h - 1):
        for x in (0, w - 1):
            if diff[y, x] < thresh_soft:
                visited[y, x] = True
                q.append((y, x))

    if seed_points:
        for sx, sy in seed_points:
            if 0 <= sx < w and 0 <= sy < h and not visited[sy, sx] and diff[sy, sx] < thresh_soft:
                visited[sy, sx] = True
                q.append((sy, sx))

    while q:
        cy, cx = q.popleft()
        for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                if diff[ny, nx] < thresh_soft:
                    visited[ny, nx] = True
                    q.append((ny, nx))

    alpha = np.full((h, w), 255.0, dtype=np.float32)
    # Soft ramp inside visited region
    t = np.clip((diff - thresh_hard) / max(1.0, (thresh_soft - thresh_hard)), 0.0, 1.0)
    if keep_interior:
        # Only modulate outer border band around visited area
        alpha[visited] = (t[visited] ** 1.5) * 255.0
    else:
        alpha[visited] = (t[visited] ** 1.35) * 255.0

    # Clean tiny isolated background speckles / smooth edge alpha slightly
    rgba = np.dstack([arr.astype(np.uint8), np.clip(alpha, 0, 255).astype(np.uint8)])
    out = Image.fromarray(rgba, mode="RGBA")
    # Remove semi-transparent color fringe toward bg by slight alpha contraction where alpha < 24
    out_arr = np.array(out)
    out_arr[out_arr[:, :, 3] < 20, 3] = 0
    return Image.fromarray(out_arr, mode="RGBA")


def crop_to_content_and_fit(im: Image.Image, target_w: int, target_h: int, pad_ratio: float = 0.07) -> Image.Image:
    """Crop to non-transparent bounding box and center cleanly inside target canvas."""
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    cw, ch = im.size
    usable_w = max(1, int(round(target_w * (1.0 - 2 * pad_ratio))))
    usable_h = max(1, int(round(target_h * (1.0 - 2 * pad_ratio))))
    scale = min(usable_w / cw, usable_h / ch)
    nw = max(1, int(round(cw * scale)))
    nh = max(1, int(round(ch * scale)))
    resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    canvas.paste(resized, ((target_w - nw) // 2, (target_h - nh) // 2), resized)
    return canvas


def build_brand_svg(brand_id: str, name: str, sector: str, primary: str, accent: str) -> str:
    """Return a genuinely distinct, custom geometric SVG vector emblem per brand (no generic + cross!)."""
    glyphs = {
        "wahindra": f'<path d="M56 80 L88 120 L128 96 L168 120 L200 80 L186 156 L128 196 L70 156 Z" fill="{primary}" stroke="{accent}" stroke-width="6"/><polygon points="104,70 128,44 152,70" fill="{accent}"/>',
        "tavara": f'<path d="M128 36 L204 68 V136 C204 184 128 220 128 220 C128 220 52 184 52 136 V68 Z" fill="{accent}" stroke="{primary}" stroke-width="6"/><polygon points="140,66 94,132 126,132 114,188 164,118 130,118" fill="{primary}"/>',
        "maruva": f'<path d="M34 110 Q80 90 128 110 Q176 90 222 110 L196 144 Q128 130 60 144 Z" fill="{accent}"/><circle cx="128" cy="128" r="46" fill="#151B20" stroke="{primary}" stroke-width="8"/><polygon points="128,88 144,128 128,168 112,128" fill="{primary}"/>',
        "toyora": f'<ellipse cx="96" cy="128" rx="44" ry="44" fill="none" stroke="{accent}" stroke-width="10"/><ellipse cx="160" cy="128" rx="44" ry="44" fill="none" stroke="{accent}" stroke-width="10"/><circle cx="128" cy="128" r="42" fill="#151B20" stroke="{primary}" stroke-width="10"/><polygon points="108,136 114,110 128,124 142,110 148,136" fill="{primary}"/>',
        "royal_iron": f'<rect x="116" y="48" width="24" height="160" rx="4" transform="rotate(42 128 128)" fill="{accent}"/><rect x="116" y="48" width="24" height="160" rx="4" transform="rotate(-42 128 128)" fill="{accent}"/><circle cx="128" cy="128" r="46" fill="#151B20" stroke="{primary}" stroke-width="8"/><polygon points="102,138 110,108 128,124 146,108 154,138" fill="{primary}"/>',
        "veero": f'<polygon points="48,64 128,208 208,64 174,64 128,150 82,64" fill="{primary}" stroke="#ffffff" stroke-width="4"/><polygon points="140,48 106,120 134,120 116,184 162,102 132,102" fill="#FFD166"/>',
        "hondo": f'<path d="M52 170 Q120 145 196 86 Q155 100 94 114 Q146 78 184 54 Q112 72 64 128 Z" fill="{primary}" stroke="#ffffff" stroke-width="4"/>',
        "quoggle": f'<circle cx="114" cy="114" r="56" fill="none" stroke="#E74C3C" stroke-width="16"/><circle cx="114" cy="114" r="56" fill="none" stroke="#3498DB" stroke-width="16" stroke-dasharray="176 352"/><circle cx="114" cy="114" r="36" fill="#3498DB" fill-opacity="0.35"/><line x1="156" y1="156" x2="208" y2="208" stroke="#9DAAB6" stroke-width="20" stroke-linecap="round"/>',
        "amazzo": f'<polygon points="128,54 196,90 196,154 128,190 60,154 60,90" fill="{primary}"/><path d="M64 188 Q128 224 196 184" fill="none" stroke="#ffffff" stroke-width="10" stroke-linecap="round"/><polygon points="188,174 206,180 194,198" fill="#ffffff"/>',
        "flippit": f'<polygon points="62,74 168,52 198,144 92,188" fill="{primary}"/><polygon points="168,52 204,76 198,144" fill="{accent}"/><path d="M98 110 H148 M98 134 H134" stroke="#ffffff" stroke-width="10" stroke-linecap="round"/>',
        "arkpay": f'<rect x="78" y="64" width="128" height="82" rx="12" fill="{accent}"/><rect x="50" y="106" width="128" height="82" rx="12" fill="{primary}" stroke="#ffffff" stroke-width="3"/><rect x="66" y="124" width="24" height="18" rx="3" fill="{accent}"/>',
        "zomatoo": f'<path d="M52 162 C52 104 94 74 128 74 C162 74 204 104 204 162 Z" fill="{primary}"/><rect x="40" y="162" width="176" height="16" rx="8" fill="#ffffff"/><circle cx="128" cy="64" r="12" fill="{primary}"/><line x1="104" y1="104" x2="152" y2="152" stroke="#ffffff" stroke-width="8" stroke-linecap="round"/><line x1="152" y1="104" x2="104" y2="152" stroke="#ffffff" stroke-width="8" stroke-linecap="round"/>',
        "swiffy": f'<path d="M128 42 C172 42 198 76 198 114 C198 162 128 218 128 218 C128 218 58 162 58 114 C58 76 84 42 128 42 Z" fill="{primary}"/><polygon points="140,78 104,126 128,126 118,164 156,114 132,114" fill="#FFF3D1"/>',
        "indra_fuel": f'<polygon points="128,36 216,128 128,220 40,128" fill="#202A34" stroke="{accent}" stroke-width="6"/><path d="M128 72 C156 106 164 134 152 158 C142 176 114 176 104 158 C92 134 100 106 128 72 Z" fill="#2DD4BF"/>',
        "indra_bank": f'<polygon points="48,90 128,44 208,90" fill="{accent}"/><rect x="66" y="96" width="18" height="72" fill="#D2DCE6"/><rect x="119" y="96" width="18" height="72" fill="#D2DCE6"/><rect x="172" y="96" width="18" height="72" fill="#D2DCE6"/><rect x="48" y="168" width="160" height="16" fill="{accent}"/><circle cx="128" cy="148" r="36" fill="{primary}" stroke="#151B20" stroke-width="5"/><text x="128" y="161" font-family="Segoe UI,sans-serif" font-size="38" font-weight="900" fill="#151B20" text-anchor="middle">₹</text>',
        "vayu_bharat": f'<polygon points="48,156 212,68 148,188 122,146" fill="{primary}"/><polygon points="212,68 122,146 92,130" fill="#ffffff"/>',
        "skyindra": f'<line x1="36" y1="68" x2="220" y2="54" stroke="#9DAAB6" stroke-width="8"/><line x1="128" y1="60" x2="128" y2="104" stroke="{accent}" stroke-width="8"/><rect x="74" y="104" width="108" height="76" rx="18" fill="{primary}" stroke="#ffffff" stroke-width="4"/><rect x="88" y="118" width="34" height="32" rx="4" fill="#A5F3FC"/><rect x="134" y="118" width="34" height="32" rx="4" fill="#A5F3FC"/>',
        "cinevista": f'<circle cx="116" cy="128" r="64" fill="{primary}" stroke="#151B20" stroke-width="6"/><circle cx="116" cy="92" r="14" fill="#151B20"/><circle cx="116" cy="164" r="14" fill="#151B20"/><circle cx="80" cy="128" r="14" fill="#151B20"/><circle cx="152" cy="128" r="14" fill="#151B20"/><polygon points="154,146 226,184 174,196" fill="{accent}"/>',
        "d_bazaar": f'<polygon points="62,110 194,110 176,194 80,194" fill="{primary}" stroke="#ffffff" stroke-width="4"/><path d="M90 110 C90 66 166 66 166 110" fill="none" stroke="{primary}" stroke-width="12"/><polygon points="128,128 136,148 156,148 140,160 146,180 128,168 110,180 116,160 100,148 120,148" fill="#FFD166"/>',
        "amora": f'<path d="M128 48 C156 88 184 128 128 196 C72 128 100 88 128 48 Z" fill="{primary}" stroke="{accent}" stroke-width="6"/><circle cx="128" cy="136" r="22" fill="{accent}"/>',
        "rang_bharat": f'<circle cx="128" cy="128" r="66" fill="none" stroke="{accent}" stroke-width="6"/><path d="M92 178 C92 110 154 66 178 58 C172 116 144 166 92 178 Z" fill="{primary}"/><circle cx="144" cy="108" r="14" fill="#1D4ED8" stroke="{accent}" stroke-width="4"/>',
        "jyon": f'<path d="M74 64 L128 106 L182 64 L196 146 L128 202 L60 146 Z" fill="#252F38" stroke="{accent}" stroke-width="6"/><polyline points="82,126 128,164 174,126" fill="none" stroke="{accent}" stroke-width="14"/>',
        "airwave": f'<polygon points="128,94 92,202 164,202" fill="none" stroke="{primary}" stroke-width="10"/><circle cx="128" cy="84" r="12" fill="#38BDF8"/><path d="M84 54 C62 80 62 116 84 142 M172 54 C194 80 194 116 172 142" fill="none" stroke="#38BDF8" stroke-width="10" stroke-linecap="round"/>',
        "indra24": f'<circle cx="128" cy="128" r="62" fill="{primary}"/><ellipse cx="128" cy="128" rx="92" ry="26" transform="rotate(-20 128 128)" fill="none" stroke="#ffffff" stroke-width="10"/>',
        "jan_awaaz": f'<rect x="64" y="68" width="128" height="128" rx="10" fill="{accent}"/><line x1="84" y1="96" x2="172" y2="96" stroke="#151B20" stroke-width="10"/><line x1="84" y1="124" x2="152" y2="124" stroke="#151B20" stroke-width="8"/><polygon points="184,54 206,76 134,158 104,166 112,136" fill="{primary}"/>',
        "indra_metro": f'<path d="M56 184 V104 A72 72 0 0 1 200 104 V184" fill="none" stroke="{accent}" stroke-width="12"/><rect x="86" y="88" width="84" height="92" rx="28" fill="#E2E8F0" stroke="{primary}" stroke-width="5"/><rect x="100" y="104" width="56" height="28" rx="6" fill="#0F172A"/>',
        "indra_suburban": f'<rect x="76" y="56" width="104" height="132" rx="12" fill="{accent}" stroke="{primary}" stroke-width="6"/><rect x="92" y="74" width="32" height="32" fill="#1E293B"/><rect x="132" y="74" width="32" height="32" fill="#1E293B"/><line x1="60" y1="204" x2="196" y2="204" stroke="#9DAAB6" stroke-width="8"/>',
        "skylink": f'<line x1="32" y1="54" x2="224" y2="74" stroke="#9DAAB6" stroke-width="6"/><rect x="52" y="84" width="54" height="46" rx="12" fill="{primary}"/><rect x="148" y="96" width="54" height="46" rx="12" fill="#38BDF8"/><path d="M36 188 Q128 164 220 188" fill="none" stroke="#38BDF8" stroke-width="8"/>',
        "maya_residences": f'<circle cx="128" cy="116" r="68" fill="{accent}"/><rect x="112" y="54" width="32" height="136" fill="#151B20"/><rect x="82" y="92" width="24" height="98" fill="#151B20"/><rect x="150" y="102" width="24" height="88" fill="#151B20"/><rect x="48" y="186" width="160" height="10" fill="{accent}"/>',
        "sd_motors": f'<path d="M128 42 L204 68 V142 C204 188 128 218 128 218 C128 218 52 188 52 142 V68 Z" fill="#151B20" stroke="{primary}" stroke-width="8"/><path d="M74 134 Q128 90 190 120 L166 150 Q120 132 74 134 Z" fill="{primary}"/>',
        "black_lotus": f'<polygon points="128,44 148,128 128,200 108,128" fill="#DC3545"/><polygon points="128,160 64,84 108,138" fill="#9D174D"/><polygon points="128,160 192,84 148,138" fill="#9D174D"/><polygon points="128,176 42,144 98,160" fill="#BE185D"/><polygon points="128,176 214,144 158,160" fill="#BE185D"/>',
        "gtm": f'<path d="M128 38 L206 68 V144 C206 190 128 220 128 220 C128 220 50 190 50 144 V68 Z" fill="{accent}" stroke="{primary}" stroke-width="10"/><line x1="94" y1="84" x2="94" y2="174" stroke="{primary}" stroke-width="8"/><line x1="162" y1="84" x2="162" y2="174" stroke="{primary}" stroke-width="8"/><path d="M60 156 H196 M94 84 L128 156 L162 84" stroke="{primary}" stroke-width="5"/>'
    }
    shape = glyphs.get(brand_id, f'<circle cx="128" cy="128" r="56" fill="{primary}"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">
  <defs>
    <radialGradient id="g_{brand_id}" cx="35%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#252F38"/>
      <stop offset="100%" stop-color="#0D1115"/>
    </radialGradient>
  </defs>
  <rect width="256" height="256" rx="40" fill="url(#g_{brand_id})"/>
  <rect x="6" y="6" width="244" height="244" rx="34" fill="none" stroke="{primary}" stroke-width="4" stroke-opacity="0.6"/>
  {shape}
</svg>'''


def process_brands():
    brands_meta = [
        # Batch 1 row 1..4
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
        # Batch 2 row 1..4
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

    b1 = Image.open(BRANDS_B1).convert("RGB")
    b2 = Image.open(BRANDS_B2).convert("RGB")
    out_dir = SOURCE / "branding"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    for idx, (bid, name, sector, tagline, primary, accent) in enumerate(brands_meta):
        sheet = b1 if idx < 16 else b2
        local_idx = idx % 16
        r, c = local_idx // 4, local_idx % 4
        # Each sheet is 1024x1024 -> 256x256 per cell (add 6px inset to avoid touching neighboring cell)
        x0, y0 = c * 256, r * 256
        tile = sheet.crop((x0 + 4, y0 + 4, x0 + 252, y0 + 252))

        cleaned = remove_dark_bg_floodfill(tile, thresh_hard=22.0, thresh_soft=46.0)
        final_png = crop_to_content_and_fit(cleaned, 256, 256, pad_ratio=0.06)

        png_path = out_dir / f"{bid}.png"
        final_png.save(png_path, format="PNG", optimize=True)

        svg_path = out_dir / f"{bid}.svg"
        svg_path.write_text(build_brand_svg(bid, name, sector, primary, accent), encoding="utf-8")

        manifest.append({
            "id": bid,
            "name": name,
            "sector": sector,
            "tagline": tagline,
            "primary_color": primary,
            "bg_color": "#151B20",
            "svg": str(svg_path.relative_to(ROOT)).replace("\\", "/"),
            "png": str(png_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(png_path.read_bytes()).hexdigest()
        })

    (MANIFESTS / "brands.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"SUCCESS: Extracted & alpha-cleaned all {len(manifest)} unique high-detail Brand Logos!")

    # Upgrade server-icon.png using the extracted GTM shield emblem
    gtm_icon = Image.open(out_dir / "gtm.png")
    srv_bg = Image.new("RGB", (64, 64), (16, 21, 28))
    # Radial dark gradient glow behind shield
    arr_bg = np.array(srv_bg, dtype=np.float32)
    yy, xx = np.mgrid[0:64, 0:64]
    dist = np.sqrt((xx - 31.5) ** 2 + (yy - 31.5) ** 2) / 36.0
    glow = np.clip(1.0 - dist, 0.0, 1.0)
    arr_bg[:, :, 0] += glow * 26
    arr_bg[:, :, 1] += glow * 44
    arr_bg[:, :, 2] += glow * 38
    srv_bg = Image.fromarray(np.clip(arr_bg, 0, 255).astype(np.uint8), mode="RGB")
    gtm_resized = gtm_icon.resize((54, 54), Image.Resampling.LANCZOS)
    srv_bg.paste(gtm_resized, (5, 5), gtm_resized)
    # Thin beveled gold border
    d = ImageDraw.Draw(srv_bg)
    d.rectangle((0, 0, 63, 63), outline=(214, 173, 89), width=1)
    srv_path = SOURCE / "icons" / "server-icon.png"
    srv_bg.save(srv_path, format="PNG", optimize=True)
    print("SUCCESS: Upgraded 64x64 server-icon.png with crisp GTM shield artwork!")


def clean_text_below_icon(cell_rgb: np.ndarray, card_interior_x0: int, card_interior_x1: int, y_min_frac: float = 0.56) -> int:
    """
    Inside a single V3 card crop (y=0..H), locate the clean dark horizontal gap right above the text labels
    ('quoggle', 'PHONE ICON' / 'HUD ICON'). Returns exact y_cut where icon art ends.
    """
    h, w, _ = cell_rgb.shape
    bg = np.median(cell_rgb[4:10, :], axis=(0, 1))
    diff = np.abs(cell_rgb.astype(np.float32) - bg).max(axis=2)
    # Count foreground pixels inside the center safe strip
    x_a = max(4, card_interior_x0)
    x_b = min(w - 4, card_interior_x1)
    row_fg = (diff[:, x_a:x_b] > 26).sum(axis=1)

    # Scan upward/downward from 55% to 88% of card height to find the zero/minimum gap separating icon from title text
    y_start = int(h * y_min_frac)
    y_end = int(h * 0.86)
    best_y = int(h * 0.72)

    # First find where bottom text starts by scanning upward from bottom inside 70%..95%
    # There are usually two text lines at the bottom; we want the gap right above the FIRST text line.
    gaps = [y for y in range(y_start, y_end) if row_fg[y] <= 2]
    if gaps:
        # Take the topmost gap above the white text labels in the lower half!
        # Wait: ensure it is actually ABOVE a lower active text block (> 8 fg pixels below it)
        for y in gaps:
            below_max = row_fg[y + 1:min(h - 4, y + 25)].max() if y + 1 < h - 4 else 0
            above_sum = row_fg[max(8, y - 20):y].sum()
            if below_max >= 6 and above_sum >= 20:
                best_y = y
                break
        else:
            best_y = gaps[0]
    else:
        # Take minimum activity row between 58% and 80%
        sub = row_fg[int(h * 0.58):int(h * 0.80)]
        best_y = int(h * 0.58) + int(np.argmin(sub))

    return best_y


def process_v3_icons():
    sheet = Image.open(V3_SHEET).convert("RGB")
    # Exact verified card intervals on 1122x1402 sheet:
    x_cols = [(8, 183), (194, 373), (384, 558), (567, 738), (748, 920), (932, 1105)]
    y_rows = [
        (5, 139), (142, 289), (292, 439), (443, 584), (587, 717),
        (720, 854), (856, 974), (976, 1095), (1097, 1224), (1226, 1377)
    ]

    # Exact 57 icons mapped row-by-row left-to-right
    phone_items = [
        ("app_quoggle", "Quoggle", "क्वागल"),
        ("app_amazzo", "Amazzo", "अमेज़ो"),
        ("app_flippit", "Flippit", "फ्लिपिट"),
        ("app_arkpay", "ARK Pay", "आर्क पे"),
        ("app_zomatoo", "Zomatoo", "ज़ोमैटो"),
        ("app_swiffy", "Swiffy", "स्विफी"),
        ("app_fashion", "Vogue Indra", "फैशन"),
        ("app_property", "Properties", "संपत्ति"),
        ("app_car_app", "Motor Mile", "मोटर"),
        ("app_maps", "City GPS", "मानचित्र"),
        ("app_garage", "My Garage", "गैराज"),
        ("app_bank", "Indra Bank", "बैंक"),
        ("app_loans", "Municipal Loans", "ऋण"),
        ("app_taxi", "City Cabs", "टैक्सी"),
        ("app_transport", "Metro & Rail", "मेट्रो"),
        ("app_news", "Indra 24", "समाचार"),
        ("app_police", "SDPD Law", "पुलिस"),
        ("app_medical", "Trauma Bay", "अस्पताल"),
        ("app_events", "Festivals", "उत्सव"),
        ("app_missions", "Contracts", "मिशन"),
        ("app_careers", "City Jobs", "नौकरी"),
        ("app_contacts", "Contacts", "संपर्क"),
        ("app_keys", "Key Fob", "चाबी"),
        ("app_settings", "Settings", "सेटिंग्स")
    ]
    hud_items = [
        ("wanted_star_empty", 64, 64, "top_right", False),
        ("wanted_star_filled", 64, 64, "top_right", False),
        ("health", 64, 64, "bottom_left", False),
        ("armour", 64, 64, "bottom_left", False),
        ("fuel", 64, 64, "bottom_right", False),
        ("battery", 64, 64, "bottom_right", False),
        ("engine_condition", 64, 64, "bottom_right", False),
        ("speedometer_analog", 128, 128, "bottom_right", False),
        ("speedometer_digital", 128, 64, "bottom_right", True),
        ("speedometer_compact", 128, 64, "bottom_right", False),
        ("minimap_circle", 128, 128, "bottom_left", True),
        ("minimap_rectangle", 160, 96, "bottom_left", True),
        ("player_arrow", 64, 64, "bottom_left", False),
        ("gps_route", 64, 64, "bottom_left", False),
        ("map_police", 64, 64, "bottom_left", False),
        ("map_hospital", 64, 64, "bottom_left", False),
        ("map_fuel", 64, 64, "bottom_left", False),
        ("map_shop", 64, 64, "bottom_left", False),
        ("map_property", 64, 64, "bottom_left", False),
        ("map_station", 64, 64, "bottom_left", False),
        ("map_mission", 64, 64, "bottom_left", False),
        ("phone_shortcut", 64, 64, "bottom_right", False),
        ("hotbar_frame", 182, 48, "top_left", True),
        ("hotbar_selected", 64, 64, "top_left", True),
        ("dialogue_bubble", 160, 96, "center", True),
        ("notification_frame", 160, 80, "top_center", True),
        ("wasted_title", 192, 64, "center", False),
        ("busted_title", 192, 64, "center", False),
        ("city_enter", 160, 96, "top_center", False),
        ("city_exit", 160, 96, "top_center", False),
        ("ark_symbol", 64, 64, "top_right", False),
        ("low_fuel", 64, 64, "bottom_right", False),
        ("critical_damage", 96, 64, "bottom_right", False)
    ]

    all_tiles = [(p[0], "phone", p) for p in phone_items] + [(h[0], "hud", h) for h in hud_items]
    assert len(all_tiles) == 57

    phone_manifest = []
    hud_manifest = []

    for idx, (ident, kind, meta) in enumerate(all_tiles):
        r, c = idx // 6, idx % 6
        x0, x1 = x_cols[c]
        y0, y1 = y_rows[r]
        # Scan top edge inside (x0+8:x1-8, y0:y0+16) to skip any light card outline row completely
        strip = sheet.crop((x0 + 8, y0, x1 - 8, y0 + 18))
        s_arr = np.array(strip, dtype=np.float32)
        bg_ref = np.median(s_arr[12:, :], axis=(0, 1))
        line_diff = np.abs(s_arr - bg_ref).max(axis=2)
        top_skip = 8
        for sy in range(14):
            # A thin horizontal grey card border has >= 55% pixels slightly brighter than bg but < 65 diff
            if (line_diff[sy] > 14).sum() > (x1 - x0 - 16) * 0.45 and line_diff[sy].max() < 75:
                top_skip = max(top_skip, sy + 3)

        card = sheet.crop((x0 + 8, y0 + top_skip, x1 - 8, y1 - 4))
        card_arr = np.array(card)
        cw, ch = card.size

        y_cut = clean_text_below_icon(card_arr, 12, cw - 12, y_min_frac=0.50)
        if ident == "dialogue_bubble":
            y_cut = min(y_cut, int(ch * 0.64))
            art_crop = card.crop((8, 6, cw - 8, max(20, y_cut)))
            cleaned = remove_dark_bg_floodfill(art_crop, thresh_hard=24.0, thresh_soft=56.0)
        else:
            art_crop = card.crop((2, 2, cw - 2, max(20, y_cut)))
            # Remove dark tile background via smooth edge BFS
            cleaned = remove_dark_bg_floodfill(art_crop, thresh_hard=20.0, thresh_soft=44.0)

        # Strip tiny disconnected 1-3px border fragments near top or side margins
        c_arr = np.array(cleaned)
        alpha_bin = c_arr[:, :, 3] > 25
        h_c, w_c = alpha_bin.shape
        # Check rows 0..8: if a row has tiny sparse dots (width <= 4 or > 70% faint horizontal line disconnected below)
        for ry in range(min(8, h_c)):
            active_cols = alpha_bin[ry].sum()
            if 0 < active_cols and (ry + 2 < h_c and alpha_bin[ry + 2].sum() == 0):
                c_arr[ry, :, 3] = 0
                if ry > 0:
                    c_arr[ry - 1, :, 3] = 0
        # Also run connected component size filter: discard specks < 25 pixels that aren't near center
        visited_cc = np.zeros_like(alpha_bin)
        for yy in range(h_c):
            for xx in range(w_c):
                if alpha_bin[yy, xx] and not visited_cc[yy, xx]:
                    comp = []
                    stack = [(yy, xx)]
                    visited_cc[yy, xx] = True
                    while stack:
                        cy, cx = stack.pop()
                        comp.append((cy, cx))
                        for ny, nx in ((cy-1,cx),(cy+1,cx),(cy,cx-1),(cy,cx+1)):
                            if 0 <= ny < h_c and 0 <= nx < w_c and alpha_bin[ny, nx] and not visited_cc[ny, nx]:
                                visited_cc[ny, nx] = True
                                stack.append((ny, nx))
                    # If tiny thin fragment near border (height <= 3 or area < 24), clear it
                    ys = [p[0] for p in comp]
                    if len(comp) < 28 or (max(ys) - min(ys) <= 2 and min(ys) < 10):
                        for py, px in comp:
                            c_arr[py, px, 3] = 0
        cleaned = Image.fromarray(c_arr, mode="RGBA")

        if kind == "phone":
            _, en_title, hi_title = meta
            final_im = crop_to_content_and_fit(cleaned, 128, 128, pad_ratio=0.06)
            out_png = SOURCE / "icons" / f"{ident}.png"
            final_im.save(out_png, format="PNG", optimize=True)
            phone_manifest.append({
                "id": ident,
                "title_en": en_title,
                "title_hi": hi_title,
                "bg_color": "#151B20",
                "svg": f"creative/source/icons/{ident}.svg",
                "png": f"creative/source/icons/{ident}.png",
                "dimensions": [128, 128],
                "v3_cleaned_from_sheet": True,
                "sha256": hashlib.sha256(out_png.read_bytes()).hexdigest()
            })
        else:
            _, tw, th, anchor, keep_frame = meta
            final_im = crop_to_content_and_fit(cleaned, tw, th, pad_ratio=0.04)
            out_png = SOURCE / "ui" / f"{ident}.png"
            final_im.save(out_png, format="PNG", optimize=True)
            hud_manifest.append({
                "id": ident,
                "dimensions": [tw, th],
                "anchor": anchor,
                "safe_area_java": {"x_ratio": 0.05 if "left" in anchor else 0.95, "y_ratio": 0.05 if "top" in anchor else 0.95},
                "safe_area_bedrock": {"x_ratio": 0.08 if "left" in anchor else 0.92, "y_ratio": 0.08 if "top" in anchor else 0.92},
                "png": f"creative/source/ui/{ident}.png",
                "v3_cleaned_from_sheet": True,
                "sha256": hashlib.sha256(out_png.read_bytes()).hexdigest()
            })

    (MANIFESTS / "phone_icons.json").write_text(json.dumps(phone_manifest, indent=2) + "\n", encoding="utf-8")
    (MANIFESTS / "hud_manifest.json").write_text(json.dumps(hud_manifest, indent=2) + "\n", encoding="utf-8")
    print(f"SUCCESS: Cleanly extracted & alpha-matted all 24 Phone Icons (128x128 RGBA) and 33 HUD Assets (no baked labels/card frames)!")


def process_food_batch1():
    food_b1_slugs = [
        "chai", "vada_pav", "samosa", "dabeli",
        "pav_bhaji", "dosa", "idli", "thali",
        "biryani", "lassi", "dhokla", "khandvi",
        "poha", "misal", "upma"
    ]
    sheet = Image.open(FOOD_B1).convert("RGB")
    out_dir = SOURCE / "icons" / "food"
    out_dir.mkdir(parents=True, exist_ok=True)

    for idx, slug in enumerate(food_b1_slugs):
        r, c = idx // 4, idx % 4
        x0, y0 = c * 256, r * 256
        # Crop upper area strictly above white text labels (~y: 8..214 inside 256x256 cell)
        cell = sheet.crop((x0 + 4, y0 + 4, x0 + 252, y0 + 216))
        cleaned = remove_dark_bg_floodfill(cell, thresh_hard=20.0, thresh_soft=42.0)
        final_png = crop_to_content_and_fit(cleaned, 128, 128, pad_ratio=0.05)
        final_png.save(out_dir / f"{slug}.png", format="PNG", optimize=True)

    print(f"SUCCESS: Extracted & alpha-matted 15 high-res transparent Food Icons (128x128 RGBA) from Food Batch 1!")


if __name__ == "__main__":
    process_brands()
    process_v3_icons()
    process_food_batch1()
