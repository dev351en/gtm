#!/usr/bin/env python3
"""Generate Visual Identity, Branding, Phone Icons, HUD, and Dashboard UI assets for GTM Revision 4."""
import os, sys, json, math, hashlib
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
SOURCE = CREATIVE / "source"
MANIFESTS = CREATIVE / "manifests"
PREVIEWS = CREATIVE / "previews"
REPORTS = CREATIVE / "reports"

# Ensure directory structure exists
for d in [
    SOURCE / "branding", SOURCE / "icons", SOURCE / "ui", SOURCE / "signage",
    SOURCE / "models", SOURCE / "textures", SOURCE / "skins", SOURCE / "outfits",
    SOURCE / "structures", MANIFESTS, PREVIEWS, REPORTS
]:
    d.mkdir(parents=True, exist_ok=True)

# Official Theme Palette
PALETTE = {
    "graphite": "#151B20",
    "graphite_dark": "#0D1115",
    "graphite_light": "#252F38",
    "ark_gold": "#D6AD59",
    "ark_gold_light": "#E8C87E",
    "ark_gold_dark": "#B28834",
    "emerald": "#236653",
    "emerald_light": "#368871",
    "emerald_dark": "#164437",
    "sandstone": "#D2B997",
    "sandstone_light": "#E5D4BC",
    "terracotta": "#AD5637",
    "terracotta_light": "#C96E4E",
    "white": "#FFFFFF",
    "gray_text": "#9DAAB6",
    "red_alert": "#DC3545",
    "blue_accent": "#2680EB"
}

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def build_server_icon():
    """Build official 64x64 opaque RGB server icon with ARK monogram on graphite."""
    im = Image.new("RGB", (64, 64), hex_to_rgb(PALETTE["graphite_dark"]))
    d = ImageDraw.Draw(im)
    # Beveled metallic border
    d.rectangle((0, 0, 63, 63), outline=hex_to_rgb(PALETTE["graphite_light"]), width=1)
    d.rectangle((2, 2, 61, 61), outline=hex_to_rgb(PALETTE["ark_gold_dark"]), width=1)
    d.rectangle((3, 3, 60, 60), outline=hex_to_rgb(PALETTE["ark_gold"]), width=1)
    
    # Inner background gradient fill
    for y in range(4, 60):
        factor = (y - 4) / 56.0
        r = int(21 * (1 - factor) + 13 * factor)
        g = int(27 * (1 - factor) + 17 * factor)
        b = int(32 * (1 - factor) + 21 * factor)
        d.line([(4, y), (59, y)], fill=(r, g, b))
        
    # ARK Monogram in gold
    gold = hex_to_rgb(PALETTE["ark_gold"])
    gold_l = hex_to_rgb(PALETTE["ark_gold_light"])
    
    # Left stroke of A (apex at 32, 12; base at 16, 50)
    d.line([(32, 12), (16, 50)], fill=gold_l, width=4)
    # Right stroke of A / Spine of K (apex at 32, 12; base at 40, 50)
    d.line([(32, 12), (36, 50)], fill=gold, width=4)
    # Crossbar of A
    d.line([(22, 34), (35, 34)], fill=gold, width=3)
    # Upper branch of K
    d.line([(36, 32), (48, 18)], fill=gold_l, width=3)
    # Lower branch of K
    d.line([(36, 32), (48, 50)], fill=gold, width=3)
    
    # SD Craft star pip at bottom center
    d.polygon([(32, 53), (33, 55), (35, 55), (33, 56), (34, 58), (32, 57), (30, 58), (31, 56), (29, 55), (31, 55)], fill=gold_l)

    icon_path = SOURCE / "icons" / "server-icon.png"
    im.save(icon_path, format="PNG")
    return icon_path

def build_brands():
    """Build all 32 original fictional brands with SVG source and 256x256 PNG."""
    brands_data = [
        ("wahindra", "Wahindra Motors", "Automotive", "Rugged All-Terrain & Utility", PALETTE["terracotta"], PALETTE["graphite"]),
        ("tavara", "Tavara Heavy Industries", "Automotive", "Electric Transit & Heavy Vehicles", PALETTE["blue_accent"], PALETTE["graphite"]),
        ("maruva", "Maruva City Car", "Automotive", "High-Efficiency Compact Cars", PALETTE["emerald"], PALETTE["graphite"]),
        ("toyora", "Toyora Motors", "Automotive", "Durable Executive & Fleet Utility", PALETTE["ark_gold"], PALETTE["graphite"]),
        ("royal_iron", "Royal Iron Motorcycles", "Motorcycles", "Authentic Heavy Thump Cruisers", PALETTE["ark_gold_dark"], PALETTE["graphite_dark"]),
        ("veero", "Veero Roadsters", "Motorcycles", "Everyday Urban Commuter Bikes", PALETTE["red_alert"], PALETTE["graphite"]),
        ("hondo", "Hondo Scooters", "Motorcycles", "Agile Fuel-Efficient City Scooters", PALETTE["blue_accent"], PALETTE["graphite"]),
        ("quoggle", "Quoggle Systems", "Technology", "Search, Cloud & Intelligent Navigation", PALETTE["blue_accent"], PALETTE["white"]),
        ("amazzo", "Amazzo Prime Hub", "Logistics", "Same-Day Commerce & Warehousing", PALETTE["ark_gold"], PALETTE["graphite"]),
        ("flippit", "Flippit Express", "E-Commerce", "Electronics & Flash Shopping", PALETTE["blue_accent"], PALETTE["ark_gold"]),
        ("arkpay", "ARK Pay UPI", "Financial", "Instant Contactless Municipal Banking", PALETTE["emerald"], PALETTE["ark_gold"]),
        ("zomatoo", "Zomatoo Food Express", "Delivery", "24/7 Restaurant Courier Delivery", PALETTE["red_alert"], PALETTE["white"]),
        ("swiffy", "Swiffy Instant Groceries", "Delivery", "Hyper-Local 10-Minute Grocery Delivery", PALETTE["terracotta"], PALETTE["white"]),
        ("indra_fuel", "Indraprastha Petroleum", "Energy", "State Refineries & High-Octane Fuel", PALETTE["blue_accent"], PALETTE["ark_gold"]),
        ("indra_bank", "First National Bank of Indra", "Banking", "Authoritative Vault Accounts & Escrow", PALETTE["ark_gold"], PALETTE["graphite_dark"]),
        ("vayu_bharat", "Vayu Bharat Airlines", "Aviation", "Coastal & International Air Carrier", PALETTE["blue_accent"], PALETTE["white"]),
        ("skyindra", "SkyIndra Ropeways", "Transit", "Harbour Aerial Cableway Transit", PALETTE["emerald"], PALETTE["sandstone"]),
        ("cinevista", "CineVista Studios", "Entertainment", "Bollywood Cinema & Film Production", PALETTE["ark_gold"], PALETTE["red_alert"]),
        ("d_bazaar", "D-Bazaar Megastores", "Retail", "Multi-Floor Wholesale Supermarkets", PALETTE["emerald"], PALETTE["white"]),
        ("amora", "Amora Indian Weaves", "Fashion", "Heritage Handloom & Modern Silk Wear", PALETTE["terracotta"], PALETTE["ark_gold"]),
        ("rang_bharat", "Rang Bharat Textiles", "Fashion", "Festival Costumes & Ceremonial Silks", PALETTE["ark_gold"], PALETTE["emerald"]),
        ("jyon", "Jyon Urban Streetwear", "Fashion", "Youth Streetwear & Athletic Apparel", PALETTE["graphite_light"], PALETTE["ark_gold_light"]),
        ("airwave", "AirWave 5G Cellular", "Telecom", "High-Bandwidth City Telecom Network", PALETTE["blue_accent"], PALETTE["white"]),
        ("indra24", "Indra 24 News", "Media", "24-Hour Metropolitan Breaking News", PALETTE["red_alert"], PALETTE["white"]),
        ("jan_awaaz", "Jan Awaaz Times", "Media", "Civic Journalism & Citizen Radio", PALETTE["graphite"], PALETTE["sandstone"]),
        ("indra_metro", "Indra Metro Rail", "Transit", "Rapid Underground & Elevated Commuter", PALETTE["blue_accent"], PALETTE["emerald"]),
        ("indra_suburban", "Indra Suburban Railway", "Transit", "Lifeline Coastal Local Train Network", PALETTE["terracotta"], PALETTE["ark_gold"]),
        ("skylink", "SkyLink Cable Car", "Transit", "Suspended Harbour Gondola Network", PALETTE["emerald"], PALETTE["white"]),
        ("maya_residences", "Maya Luxury Residences", "Real Estate", "Prime Waterfront High-Rise Condos", PALETTE["sandstone"], PALETTE["graphite"]),
        ("sd_motors", "SD Craft Motorsport", "Dealership", "Exclusive Luxury Supercar Showroom", PALETTE["ark_gold"], PALETTE["graphite_dark"]),
        ("black_lotus", "Black Lotus Syndicate", "Underground", "Shadow Port Cartel & Contraband", PALETTE["graphite_dark"], PALETTE["red_alert"]),
        ("gtm", "Grand Theft Mumbai", "Master Brand", "Metropolitan Roleplay Universe", PALETTE["ark_gold"], PALETTE["graphite_dark"])
    ]

    manifest = []
    for brand_id, name, sector, tagline, primary_col, bg_col in brands_data:
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">
  <rect width="256" height="256" rx="32" fill="{bg_col}"/>
  <rect x="8" y="8" width="240" height="240" rx="24" fill="none" stroke="{primary_col}" stroke-width="4" stroke-opacity="0.4"/>
  <circle cx="128" cy="100" r="54" fill="none" stroke="{primary_col}" stroke-width="8"/>
  <text x="128" y="112" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="900" fill="{primary_col}" text-anchor="middle">{brand_id[:3].upper()}</text>
  <text x="128" y="185" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="bold" fill="{primary_col}" text-anchor="middle">{name.upper()}</text>
  <text x="128" y="210" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{PALETTE["sandstone"]}" text-anchor="middle">{sector.upper()} • {tagline}</text>
</svg>'''
        svg_path = SOURCE / "branding" / f"{brand_id}.svg"
        svg_path.write_text(svg_content, encoding="utf-8")

        # Generate matching 256x256 raster PNG
        im = Image.new("RGBA", (256, 256), (*hex_to_rgb(bg_col), 255))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((8, 8, 247, 247), radius=24, outline=(*hex_to_rgb(primary_col), 180), width=4)
        d.ellipse((74, 46, 182, 154), outline=hex_to_rgb(primary_col), width=8)
        
        # Center symbol representation
        d.rectangle((108, 90, 148, 110), fill=hex_to_rgb(primary_col))
        d.rectangle((118, 75, 138, 125), fill=hex_to_rgb(primary_col))
        
        # Bottom label bar
        d.rounded_rectangle((24, 175, 231, 225), radius=8, fill=(*hex_to_rgb(bg_col), 200), outline=hex_to_rgb(primary_col), width=2)
        d.rectangle((40, 196, 216, 204), fill=hex_to_rgb(primary_col))

        png_path = SOURCE / "branding" / f"{brand_id}.png"
        im.save(png_path, format="PNG")

        manifest.append({
            "id": brand_id,
            "name": name,
            "sector": sector,
            "tagline": tagline,
            "primary_color": primary_col,
            "bg_color": bg_col,
            "svg": str(svg_path.relative_to(ROOT)).replace("\\", "/"),
            "png": str(png_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(png_path.read_bytes()).hexdigest()
        })

    (MANIFESTS / "brands.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated {len(manifest)} vector brand lockups and raster textures.")
    return manifest

def build_phone_icons():
    """Build all 24 phone app icons (SVG + 64x64 PNG) with dual English/Hindi labels."""
    apps = [
        ("app_quoggle", "Quoggle", "क्वागल", PALETTE["blue_accent"], "globe"),
        ("app_amazzo", "Amazzo", "अमेज़ो", PALETTE["ark_gold"], "package"),
        ("app_flippit", "Flippit", "फ्लिपिट", PALETTE["blue_accent"], "cart"),
        ("app_arkpay", "ARK Pay", "आर्क पे", PALETTE["emerald"], "wallet"),
        ("app_zomatoo", "Zomatoo", "ज़ोमैटो", PALETTE["red_alert"], "fork"),
        ("app_swiffy", "Swiffy", "स्विफी", PALETTE["terracotta"], "bolt"),
        ("app_fashion", "Vogue Indra", "फैशन", PALETTE["sandstone"], "shirt"),
        ("app_property", "Properties", "संपत्ति", PALETTE["ark_gold"], "building"),
        ("app_car_app", "Motor Mile", "मोटर", PALETTE["terracotta"], "car"),
        ("app_maps", "City GPS", "मानचित्र", PALETTE["blue_accent"], "compass"),
        ("app_garage", "My Garage", "गैराज", PALETTE["graphite_light"], "wrench"),
        ("app_bank", "Maze Bank", "मेज़ बैंक", PALETTE["emerald"], "bank"),
        ("app_loans", "Municipal Loans", "ऋण", PALETTE["ark_gold_dark"], "percent"),
        ("app_taxi", "City Cabs", "टैक्सी", PALETTE["ark_gold"], "taxi"),
        ("app_transport", "Metro & Rail", "मेट्रो", PALETTE["blue_accent"], "train"),
        ("app_news", "Indra 24", "समाचार", PALETTE["red_alert"], "newspaper"),
        ("app_police", "SDPD Law", "पुलिस", PALETTE["blue_accent"], "badge"),
        ("app_medical", "Trauma Bay", "अस्पताल", PALETTE["red_alert"], "cross"),
        ("app_events", "Festivals", "उत्सव", PALETTE["ark_gold"], "calendar"),
        ("app_missions", "Contracts", "मिशन", PALETTE["terracotta"], "target"),
        ("app_careers", "City Jobs", "नौकरी", PALETTE["sandstone"], "briefcase"),
        ("app_contacts", "Contacts", "संपर्क", PALETTE["blue_accent"], "phone"),
        ("app_keys", "Key Fob", "चाबी", PALETTE["ark_gold_light"], "key"),
        ("app_settings", "Settings", "सेटिंग्स", PALETTE["graphite_light"], "gear")
    ]

    manifest = []
    for app_id, en_title, hi_title, bg_color, glyph in apps:
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <rect width="64" height="64" rx="14" fill="{bg_color}"/>
  <rect x="2" y="2" width="60" height="60" rx="12" fill="none" stroke="{PALETTE["white"]}" stroke-width="1.5" stroke-opacity="0.3"/>
  <circle cx="32" cy="28" r="14" fill="{PALETTE["graphite_dark"]}" fill-opacity="0.25"/>
  <text x="32" y="34" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="{PALETTE["white"]}" text-anchor="middle">{glyph[:1].upper()}</text>
  <text x="32" y="52" font-family="Arial, sans-serif" font-size="7" font-weight="bold" fill="{PALETTE["white"]}" text-anchor="middle">{en_title}</text>
</svg>'''
        svg_path = SOURCE / "icons" / f"{app_id}.svg"
        svg_path.write_text(svg_content, encoding="utf-8")

        # 64x64 RGBA Raster
        im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((2, 2, 61, 61), radius=14, fill=(*hex_to_rgb(bg_color), 255), outline=(255, 255, 255, 90), width=1)
        d.ellipse((18, 14, 46, 42), fill=(0, 0, 0, 60))
        
        # Draw distinctive glyphs
        if glyph == "cross":
            d.rectangle((29, 20, 35, 36), fill=(255, 255, 255, 255))
            d.rectangle((21, 25, 43, 31), fill=(255, 255, 255, 255))
        elif glyph == "bolt":
            d.polygon([(34, 18), (25, 30), (32, 30), (28, 38), (39, 26), (32, 26)], fill=(255, 255, 255, 255))
        elif glyph == "star" or glyph == "target":
            d.ellipse((24, 20, 40, 36), outline=(255, 255, 255, 255), width=2)
            d.ellipse((29, 25, 35, 31), fill=(255, 255, 255, 255))
        elif glyph == "key":
            d.ellipse((24, 20, 34, 30), outline=(255, 255, 255, 255), width=2)
            d.line([(32, 28), (42, 38)], fill=(255, 255, 255, 255), width=2)
            d.line([(38, 34), (40, 32)], fill=(255, 255, 255, 255), width=2)
        else:
            d.rectangle((26, 22, 38, 34), outline=(255, 255, 255, 255), width=2)
            d.line([(26, 28), (38, 28)], fill=(255, 255, 255, 255), width=1)
            
        # Label indicator line
        d.line([(16, 52), (48, 52)], fill=(255, 255, 255, 180), width=2)

        png_path = SOURCE / "icons" / f"{app_id}.png"
        im.save(png_path, format="PNG")

        manifest.append({
            "id": app_id,
            "title_en": en_title,
            "title_hi": hi_title,
            "bg_color": bg_color,
            "svg": str(svg_path.relative_to(ROOT)).replace("\\", "/"),
            "png": str(png_path.relative_to(ROOT)).replace("\\", "/"),
            "dimensions": [64, 64],
            "sha256": hashlib.sha256(png_path.read_bytes()).hexdigest()
        })

    (MANIFESTS / "phone_icons.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated {len(manifest)} 64x64 phone app icons.")
    return manifest

def build_hud_assets():
    """Build all 33 HUD assets with safe zone anchors for Java and Bedrock."""
    hud_items = [
        ("wanted_star_empty", 32, 32, "top_right"),
        ("wanted_star_filled", 32, 32, "top_right"),
        ("health", 32, 32, "bottom_left"),
        ("armour", 32, 32, "bottom_left"),
        ("fuel", 32, 32, "bottom_right"),
        ("battery", 32, 32, "bottom_right"),
        ("engine_condition", 32, 32, "bottom_right"),
        ("speedometer_analog", 96, 96, "bottom_right"),
        ("speedometer_digital", 96, 48, "bottom_right"),
        ("speedometer_compact", 64, 32, "bottom_right"),
        ("minimap_circle", 128, 128, "bottom_left"),
        ("minimap_rectangle", 128, 96, "bottom_left"),
        ("player_arrow", 32, 32, "bottom_left"),
        ("gps_route", 32, 32, "bottom_left"),
        ("map_police", 24, 24, "bottom_left"),
        ("map_hospital", 24, 24, "bottom_left"),
        ("map_fuel", 24, 24, "bottom_left"),
        ("map_shop", 24, 24, "bottom_left"),
        ("map_property", 24, 24, "bottom_left"),
        ("map_station", 24, 24, "bottom_left"),
        ("map_mission", 24, 24, "bottom_left"),
        ("phone_shortcut", 48, 48, "bottom_right"),
        ("hotbar_frame", 182, 22, "top_left"),
        ("hotbar_selected", 24, 24, "top_left"),
        ("dialogue_bubble", 256, 64, "center"),
        ("notification_frame", 220, 48, "top_center"),
        ("wasted_title", 256, 64, "center"),
        ("busted_title", 256, 64, "center"),
        ("city_enter", 192, 48, "top_center"),
        ("city_exit", 192, 48, "top_center"),
        ("ark_symbol", 32, 32, "top_right"),
        ("low_fuel", 32, 32, "bottom_right"),
        ("critical_damage", 32, 32, "bottom_right")
    ]

    manifest = []
    for item_id, w, h, anchor in hud_items:
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)

        if "star" in item_id:
            fill_col = hex_to_rgb(PALETTE["ark_gold"]) if "filled" in item_id else None
            outline_col = hex_to_rgb(PALETTE["ark_gold"])
            cx, cy, r_out, r_in = w // 2, h // 2, w // 2 - 4, w // 4
            points = []
            for i in range(10):
                angle = i * math.pi / 5 - math.pi / 2
                radius = r_out if i % 2 == 0 else r_in
                points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
            d.polygon(points, fill=(*fill_col, 255) if fill_col else (0, 0, 0, 100), outline=(*outline_col, 255))
        elif "wasted" in item_id or "busted" in item_id:
            bg_col = (180, 20, 20, 220) if "wasted" in item_id else (20, 50, 160, 220)
            d.rounded_rectangle((0, 0, w - 1, h - 1), radius=8, fill=bg_col, outline=(255, 255, 255, 240), width=2)
            d.line([(10, h // 2), (w - 10, h // 2)], fill=(255, 255, 255, 180), width=3)
        elif "speedometer" in item_id:
            d.rounded_rectangle((0, 0, w - 1, h - 1), radius=12, fill=(*hex_to_rgb(PALETTE["graphite_dark"]), 210), outline=(*hex_to_rgb(PALETTE["ark_gold"]), 200), width=2)
            if "analog" in item_id:
                d.ellipse((8, 8, w - 9, h - 9), outline=hex_to_rgb(PALETTE["sandstone"]), width=2)
                d.line([(w // 2, h // 2), (w - 20, h // 2 - 15)], fill=hex_to_rgb(PALETTE["red_alert"]), width=3)
            else:
                d.rectangle((12, h // 2 - 6, w - 12, h // 2 + 6), fill=(*hex_to_rgb(PALETTE["emerald"]), 220))
        elif "minimap" in item_id:
            if "circle" in item_id:
                d.ellipse((2, 2, w - 3, h - 3), fill=(*hex_to_rgb(PALETTE["graphite_dark"]), 200), outline=(*hex_to_rgb(PALETTE["ark_gold"]), 255), width=3)
                d.ellipse((w // 2 - 4, h // 2 - 4, w // 2 + 4, h // 2 + 4), fill=(*hex_to_rgb(PALETTE["blue_accent"]), 255))
            else:
                d.rounded_rectangle((2, 2, w - 3, h - 3), radius=10, fill=(*hex_to_rgb(PALETTE["graphite_dark"]), 200), outline=(*hex_to_rgb(PALETTE["ark_gold"]), 255), width=3)
        elif "hotbar" in item_id:
            d.rectangle((0, 0, w - 1, h - 1), fill=(*hex_to_rgb(PALETTE["graphite_dark"]), 180), outline=(*hex_to_rgb(PALETTE["sandstone"]), 200), width=2)
        elif "notification" in item_id or "dialogue" in item_id or "city" in item_id:
            d.rounded_rectangle((0, 0, w - 1, h - 1), radius=8, fill=(*hex_to_rgb(PALETTE["graphite_dark"]), 230), outline=(*hex_to_rgb(PALETTE["ark_gold"]), 200), width=2)
            d.line([(8, h - 6), (w - 8, h - 6)], fill=(*hex_to_rgb(PALETTE["ark_gold"]), 180), width=2)
        else:
            d.ellipse((2, 2, w - 3, h - 3), fill=(*hex_to_rgb(PALETTE["graphite_dark"]), 200), outline=(*hex_to_rgb(PALETTE["sandstone"]), 200), width=2)
            d.rectangle((w // 4, h // 4, 3 * w // 4, 3 * h // 4), fill=(*hex_to_rgb(PALETTE["ark_gold"]), 255))

        png_path = SOURCE / "ui" / f"{item_id}.png"
        im.save(png_path, format="PNG")

        manifest.append({
            "id": item_id,
            "dimensions": [w, h],
            "anchor": anchor,
            "safe_area_java": {"x_ratio": 0.05 if "left" in anchor else 0.95, "y_ratio": 0.05 if "top" in anchor else 0.95},
            "safe_area_bedrock": {"x_ratio": 0.08 if "left" in anchor else 0.92, "y_ratio": 0.08 if "top" in anchor else 0.92},
            "png": str(png_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(png_path.read_bytes()).hexdigest()
        })

    (MANIFESTS / "hud_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated {len(manifest)} HUD and UI screen components.")
    return manifest

def build_dashboard_ui_tokens():
    """Build design tokens and responsive panel layouts for Control Centre dashboard."""
    dashboard = {
        "schema_version": 1,
        "theme": "indraprastha_dark",
        "colors": PALETTE,
        "typography": {
            "font_family_latin": "Inter, 'Segoe UI', -apple-system, sans-serif",
            "font_family_devanagari": "'Noto Sans Devanagari', 'Mangal', sans-serif",
            "font_sizes": {
                "xs": "11px", "sm": "13px", "base": "15px", "lg": "18px", "xl": "22px", "2xl": "28px", "title": "36px"
            }
        },
        "spacing_rem": {
            "1": "0.25rem", "2": "0.5rem", "3": "0.75rem", "4": "1rem", "6": "1.5rem", "8": "2rem"
        },
        "panels": [
            {"id": "panel_players", "title": "Active Citizens & Roster", "icon": "users", "category": "operations"},
            {"id": "panel_console", "title": "Command Terminal", "icon": "terminal", "category": "system"},
            {"id": "panel_worlds", "title": "Metropolitan Districts & Anvil Chunks", "icon": "map", "category": "world"},
            {"id": "panel_buildings", "title": "46 Municipal Facilities & Sites", "icon": "home", "category": "urban"},
            {"id": "panel_transport", "title": "Transit, Traffic & Fleet Management", "icon": "truck", "category": "transit"},
            {"id": "panel_npcs", "title": "500 Citizens & Syndicate Gang Roster", "icon": "user-check", "category": "society"},
            {"id": "panel_finance", "title": "ARK Vault Ledger & Cash Economy", "icon": "dollar-sign", "category": "economy"},
            {"id": "panel_loans", "title": "Municipal Credit & Debt Recovery", "icon": "credit-card", "category": "economy"},
            {"id": "panel_properties", "title": "Real Estate Registry & Ownership", "icon": "key", "category": "property"},
            {"id": "panel_festivals", "title": "Seasonal Switchboard & Themes", "icon": "calendar", "category": "culture"},
            {"id": "panel_media", "title": "Indra 24 Broadcast & Advertising", "icon": "tv", "category": "media"},
            {"id": "panel_hosting", "title": "Cloud VPS Runtime & Memory", "icon": "server", "category": "system"},
            {"id": "panel_backups", "title": "Atomic Snapshots & Rollback Vault", "icon": "archive", "category": "system"},
            {"id": "panel_updates", "title": "Pack Pipeline & Integrity Audits", "icon": "refresh-cw", "category": "system"}
        ]
    }
    tokens_path = SOURCE / "ui" / "dashboard_tokens.json"
    tokens_path.write_text(json.dumps(dashboard, indent=2), encoding="utf-8")
    print(f"Generated Control Centre dashboard tokens with {len(dashboard['panels'])} responsive panels.")
    return dashboard

if __name__ == "__main__":
    build_server_icon()
    build_brands()
    build_phone_icons()
    build_hud_assets()
    build_dashboard_ui_tokens()
    print("SUCCESS: Visual identity, UI, and branding assets complete!")
