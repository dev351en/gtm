import hashlib
import json
import os
import zipfile

HERE = 'd:/Games/SDCRAFT'
CACHE = os.path.join(HERE, 'tools', 'fa_cache')
BASE_CITY = os.path.join(HERE, 'sdcraft_isolated', 'resourcepacks', 'SDCraft_Unified_26.3_CityPack.zip')
STANDALONE_FA = os.path.join(HERE, 'sdcraft_isolated', 'resourcepacks', 'FreshAnimations_v1.11.2_All_Extensions_26.3.zip')
OUT_ISOLATED = os.path.join(HERE, 'sdcraft_isolated', 'resourcepacks', 'SDCraft_Unified_26.3_CityPack.zip')
OUT_REPO = os.path.join(HERE, 'github_gtm_repo', 'resource-pack', 'EXPECT_SDCRAFT_ResourcePack_26.3.zip')

FRESH_BASE = os.path.join(CACHE, 'fresh_base.zip')
FRESH_EXT = os.path.join(CACHE, 'fresh_extensions.zip')
FRESH_PLAYER = os.path.join(CACHE, 'fresh_player.zip')

def sha1(filepath):
    h = hashlib.sha1()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def build_standalone_fa():
    print("Building standalone Fresh Animations 1.11.2 with All Extensions...")
    entries = {}

    # 1. Fresh Base
    with zipfile.ZipFile(FRESH_BASE) as z:
        for name in z.namelist():
            if not name.endswith('/') and name != 'pack.mcmeta':
                entries[name] = z.read(name)

    # 2. Fresh Extensions
    with zipfile.ZipFile(FRESH_EXT) as z:
        for name in z.namelist():
            if not name.endswith('/') and name != 'pack.mcmeta':
                entries[name] = z.read(name)
                # Also promote 26-1 overlay files directly into assets/ for direct 26.3 support
                if name.startswith('26-1/assets/'):
                    promoted = name[len('26-1/'):]
                    entries[promoted] = z.read(name)

    # 3. Fresh Player
    with zipfile.ZipFile(FRESH_PLAYER) as z:
        for name in z.namelist():
            if not name.endswith('/') and name != 'pack.mcmeta':
                entries[name] = z.read(name)

    # MCMeta
    meta = {
        "pack": {
            "description": "§a■ Fresh Animations 1.11.2 §8+ §eAll Extensions\n§8■ 26.3 Ready | By FreshLX",
            "pack_format": 84,
            "supported_formats": {"min_inclusive": 15, "max_inclusive": 999},
            "min_format": 15,
            "max_format": 999
        },
        "overlays": {
            "entries": [
                { "directory": "20-3", "formats": {"min_inclusive": 22, "max_inclusive": 999}, "min_format": 22, "max_format": 999 },
                { "directory": "21-2", "formats": {"min_inclusive": 42, "max_inclusive": 999}, "min_format": 42, "max_format": 999 },
                { "directory": "21-5", "formats": {"min_inclusive": 55, "max_inclusive": 999}, "min_format": 55, "max_format": 999 },
                { "directory": "21-6", "formats": {"min_inclusive": 63, "max_inclusive": 999}, "min_format": 63, "max_format": 999 },
                { "directory": "26-1", "formats": {"min_inclusive": 84, "max_inclusive": 999}, "min_format": 84, "max_format": 999 }
            ]
        }
    }
    entries['pack.mcmeta'] = json.dumps(meta, indent=2).encode('utf-8')

    with zipfile.ZipFile(STANDALONE_FA, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as out:
        for name in sorted(entries.keys()):
            out.writestr(name, entries[name])

    print(f"Created {STANDALONE_FA} ({os.path.getsize(STANDALONE_FA):,} bytes, {len(entries)} files)")

def build_merged_server_pack():
    print("Building merged unified server pack (Vehicles + Guns + Fresh Animations + All Extensions)...")
    entries = {}

    # 1. Base City Pack (Vehicles, Guns, Items, Brand Assets)
    with zipfile.ZipFile(BASE_CITY) as z:
        for name in z.namelist():
            if not name.endswith('/') and name != 'pack.mcmeta':
                entries[name] = z.read(name)

    # 2. Fresh Base
    with zipfile.ZipFile(FRESH_BASE) as z:
        for name in z.namelist():
            if not name.endswith('/') and name != 'pack.mcmeta' and name != 'pack.png':
                entries[name] = z.read(name)

    # 3. Fresh Extensions
    with zipfile.ZipFile(FRESH_EXT) as z:
        for name in z.namelist():
            if not name.endswith('/') and name != 'pack.mcmeta' and name != 'pack.png':
                entries[name] = z.read(name)
                if name.startswith('26-1/assets/'):
                    promoted = name[len('26-1/'):]
                    entries[promoted] = z.read(name)

    # 4. Fresh Player
    with zipfile.ZipFile(FRESH_PLAYER) as z:
        for name in z.namelist():
            if not name.endswith('/') and name != 'pack.mcmeta' and name != 'pack.png':
                entries[name] = z.read(name)

    # Merged MCMeta
    meta = {
        "pack": {
            "description": "§6SD Craft 26.3 SMP §8| §aFresh Animations 1.11.2 + Extensions §8| §e3D Vehicles & Guns",
            "pack_format": 84,
            "supported_formats": {"min_inclusive": 15, "max_inclusive": 999},
            "min_format": 15,
            "max_format": 999
        },
        "overlays": {
            "entries": [
                { "directory": "20-3", "formats": {"min_inclusive": 22, "max_inclusive": 999}, "min_format": 22, "max_format": 999 },
                { "directory": "21-2", "formats": {"min_inclusive": 42, "max_inclusive": 999}, "min_format": 42, "max_format": 999 },
                { "directory": "21-5", "formats": {"min_inclusive": 55, "max_inclusive": 999}, "min_format": 55, "max_format": 999 },
                { "directory": "21-6", "formats": {"min_inclusive": 63, "max_inclusive": 999}, "min_format": 63, "max_format": 999 },
                { "directory": "26-1", "formats": {"min_inclusive": 84, "max_inclusive": 999}, "min_format": 84, "max_format": 999 }
            ]
        }
    }
    entries['pack.mcmeta'] = json.dumps(meta, indent=2).encode('utf-8')

    temp_out = os.path.join(HERE, 'tools', 'temp_merged_pack.zip')
    with zipfile.ZipFile(temp_out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as out:
        for name in sorted(entries.keys()):
            out.writestr(name, entries[name])

    import shutil
    shutil.copy2(temp_out, OUT_ISOLATED)
    os.makedirs(os.path.dirname(OUT_REPO), exist_ok=True)
    shutil.copy2(temp_out, OUT_REPO)
    os.remove(temp_out)

    pack_sha1 = sha1(OUT_ISOLATED)
    pack_sha256 = sha256(OUT_ISOLATED)

    print(f"Created Merged Pack ({os.path.getsize(OUT_ISOLATED):,} bytes, {len(entries)} files)")
    print(f"SHA1: {pack_sha1}")
    print(f"SHA256: {pack_sha256}")
    return pack_sha1

if __name__ == '__main__':
    build_standalone_fa()
    new_sha1 = build_merged_server_pack()
    print("New Pack SHA1:", new_sha1)
