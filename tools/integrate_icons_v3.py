#!/usr/bin/env python3
"""Extract and integrate GTM Creative Icons V3 into the creative repository."""
import hashlib
import json
import zipfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = Path(r"C:/Users/brode/.gemini/antigravity/brain/ceee3c26-6ae4-4f1c-b357-09eb59f51997/.user_uploaded/media_1795544878544_6791d5c3.zip")
CREATIVE = ROOT / "creative"
ICONS_V3_DIR = CREATIVE / "source" / "icons_v3"
ICONS_DIR = CREATIVE / "source" / "icons"
UI_DIR = CREATIVE / "source" / "ui"
MANIFESTS_DIR = CREATIVE / "manifests"
PREVIEWS_DIR = CREATIVE / "previews"

def integrate():
    ICONS_V3_DIR.mkdir(parents=True, exist_ok=True)
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    UI_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Extracting {ZIP_PATH} into {CREATIVE}...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        for info in z.infolist():
            # Extract icons_v3 files and contact sheet
            if info.filename.startswith("creative/source/icons_v3/") and not info.is_dir():
                filename = Path(info.filename).name
                dest_file = ICONS_V3_DIR / filename
                dest_file.write_bytes(z.read(info.filename))
            elif info.filename == "creative/previews/icons_v3_contact_sheet.png":
                (PREVIEWS_DIR / "icons_v3_contact_sheet.png").write_bytes(z.read(info.filename))
            elif info.filename == "creative/manifests.json":
                (MANIFESTS_DIR / "icons_v3_manifest.json").write_bytes(z.read(info.filename))

    print(f"Extracted {len(list(ICONS_V3_DIR.glob('*.png')))} V3 icon files.")

    # Phone app mappings (24 phone apps)
    phone_app_map = {
        "bank": "bank",
        "arkpay": "arkpay",
        "loans": "loans",
        "property": "property",
        "keys": "keys",
        "car_app": "garage", # or car_app
        "garage": "garage",
        "taxi": "taxi",
        "transport": "transport",
        "maps": "maps",
        "gps_route": "gps_route",
        "missions": "missions",
        "careers": "careers",
        "zomatoo": "zomatoo",
        "swiffy": "swiffy",
        "amazzo": "amazzo",
        "flippit": "flippit",
        "fashion": "fashion",
        "medical": "medical",
        "police": "police",
        "news": "news",
        "events": "events",
        "quoggle": "quoggle",
        "settings": "settings"
    }

    # Process and update 64x64 phone icons with the high-fidelity V3 artwork
    phone_manifest_file = MANIFESTS_DIR / "phone_icons.json"
    phone_manifest = json.loads(phone_manifest_file.read_text(encoding="utf-8"))

    updated_phone_count = 0
    for icon_entry in phone_manifest:
        ident = icon_entry["id"].replace("app_", "")
        v3_name = phone_app_map.get(ident, ident)
        v3_src = ICONS_V3_DIR / f"{v3_name}.png"
        if v3_src.exists():
            with Image.open(v3_src) as img:
                # Resize cleanly to 64x64 keeping aspect ratio and high fidelity
                img_rgba = img.convert("RGBA")
                # Crop center square if rectangular
                w, h = img_rgba.size
                min_dim = min(w, h)
                left = (w - min_dim) // 2
                top = (h - min_dim) // 2
                cropped = img_rgba.crop((left, top, left + min_dim, top + min_dim))
                resized = cropped.resize((64, 64), Image.Resampling.LANCZOS)
                
                dest_path = ROOT / icon_entry["png"]
                resized.save(dest_path, optimize=True)
                
                # Update sha256 in manifest
                icon_entry["sha256"] = hashlib.sha256(dest_path.read_bytes()).hexdigest()
                icon_entry["v3_source"] = f"creative/source/icons_v3/{v3_name}.png"
                updated_phone_count += 1

    phone_manifest_file.write_text(json.dumps(phone_manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {updated_phone_count} phone icons in {phone_manifest_file.name} from V3 assets.")

    # HUD mappings (33 HUD assets)
    hud_manifest_file = MANIFESTS_DIR / "hud_manifest.json"
    hud_manifest = json.loads(hud_manifest_file.read_text(encoding="utf-8"))

    updated_hud_count = 0
    for hud_entry in hud_manifest:
        ident = hud_entry["id"]
        v3_src = ICONS_V3_DIR / f"{ident}.png"
        if v3_src.exists():
            target_dims = tuple(hud_entry["dimensions"])
            with Image.open(v3_src) as img:
                img_rgba = img.convert("RGBA")
                resized = img_rgba.resize(target_dims, Image.Resampling.LANCZOS)
                dest_path = ROOT / hud_entry["png"]
                resized.save(dest_path, optimize=True)

                hud_entry["sha256"] = hashlib.sha256(dest_path.read_bytes()).hexdigest()
                hud_entry["v3_source"] = f"creative/source/icons_v3/{ident}.png"
                updated_hud_count += 1

    hud_manifest_file.write_text(json.dumps(hud_manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {updated_hud_count} HUD components in {hud_manifest_file.name} from V3 assets.")

    print("SUCCESS: V3 Icons successfully integrated into the GTM Revision 4 Creative track!")

if __name__ == "__main__":
    integrate()
