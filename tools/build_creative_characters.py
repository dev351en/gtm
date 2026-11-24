#!/usr/bin/env python3
"""Build and validate 500 character skins and 100 outfits for GTM Revision 4 Creative Track."""
import hashlib
import json
from pathlib import Path
from PIL import Image

import generate_npc_assets

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
SKINS_DIR = CREATIVE / "source" / "skins"
OUTFITS_DIR = CREATIVE / "source" / "outfits"
MANIFESTS_DIR = CREATIVE / "manifests"

def build():
    SKINS_DIR.mkdir(parents=True, exist_ok=True)
    OUTFITS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

    # Read existing 400 surveyed positions from gtm-population.tsv
    pop_tsv = ROOT / "source" / "src" / "main" / "resources" / "gtm-population.tsv"
    pop_positions = {}
    if pop_tsv.exists():
        for line in pop_tsv.read_text(encoding="utf-8").strip().splitlines():
            parts = line.split("\t")
            if len(parts) >= 7:
                pop_positions[parts[0]] = {
                    "uuid": parts[1],
                    "name": parts[2],
                    "role": parts[3],
                    "x": int(parts[4]),
                    "y": int(parts[5]),
                    "z": int(parts[6])
                }

    # 1. Generate 500 skins
    skin_records = []
    skin_hashes = set()
    names = [f"{a} {b}" for a in generate_npc_assets.FIRST for b in generate_npc_assets.LAST]
    import random
    random.Random(42).shuffle(names)

    i = 0
    for role, count in generate_npc_assets.ROLES:
        for rank in range(count):
            i += 1
            ident = f"npc-{i:03d}"
            im = generate_npc_assets.skin(role, i)
            out_file = SKINS_DIR / f"{ident}.png"
            im.save(out_file, optimize=True)

            digest = hashlib.sha256(out_file.read_bytes()).hexdigest()
            assert digest not in skin_hashes, f"Duplicate skin hash for {ident}"
            skin_hashes.add(digest)

            is_boss = (role == "black_lotus" and rank == 0) # npc-481
            is_prisoner = (role == "black_lotus" and 1 <= rank <= 5) # npc-482..486

            # Determine anchor
            anchor = pop_positions.get(ident)
            if not anchor:
                anchor = {
                    "uuid": str(generate_npc_assets.uuid.uuid5(generate_npc_assets.NS, ident)),
                    "name": names[i - 1],
                    "role": role,
                    "x": 0, "y": 64, "z": 0 # Default municipal/civic spawn anchor
                }

            skin_records.append({
                "id": ident,
                "uuid": anchor["uuid"],
                "name": anchor["name"],
                "role": role,
                "texture": f"creative/source/skins/{ident}.png",
                "model": "classic",
                "dimensions": [64, 64],
                "sha256": digest,
                "gang_boss": is_boss,
                "initially_jailed": is_prisoner,
                "world_anchor": {
                    "x": anchor["x"],
                    "y": anchor["y"],
                    "z": anchor["z"]
                }
            })

    assert len(skin_records) == 500, f"Expected 500 skins, got {len(skin_records)}"
    assert sum(r["gang_boss"] for r in skin_records) == 1, "Expected exactly 1 gang boss (npc-481)"
    assert sum(r["initially_jailed"] for r in skin_records) == 5, "Expected exactly 5 prisoners (npc-482..486)"
    assert skin_records[480]["id"] == "npc-481" and skin_records[480]["gang_boss"] is True

    # 2. Generate 100 outfits
    outfit_records = []
    outfit_hashes = set()
    j = 0
    for cat, count in generate_npc_assets.OUTFITS:
        for _ in range(count):
            j += 1
            ident = f"outfit-{j:03d}"
            im = generate_npc_assets.outfit(cat, j)
            out_file = OUTFITS_DIR / f"{ident}.png"
            im.save(out_file, optimize=True)

            digest = hashlib.sha256(out_file.read_bytes()).hexdigest()
            assert digest not in outfit_hashes, f"Duplicate outfit hash for {ident}"
            outfit_hashes.add(digest)

            outfit_records.append({
                "id": ident,
                "category": cat,
                "texture": f"creative/source/outfits/{ident}.png",
                "model": "classic-overlay",
                "dimensions": [64, 64],
                "sha256": digest,
                "price_ark": 150 + (j % 10) * 35
            })

    assert len(outfit_records) == 100, f"Expected 100 outfits, got {len(outfit_records)}"

    # Save manifests
    skins_manifest = MANIFESTS_DIR / "npc_skins_manifest.json"
    skins_manifest.write_text(json.dumps({
        "schema_version": "1.0.0",
        "total_skins": len(skin_records),
        "gang_boss_id": "npc-481",
        "prisoner_ids": ["npc-482", "npc-483", "npc-484", "npc-485", "npc-486"],
        "skins": skin_records
    }, indent=2) + "\n", encoding="utf-8")

    outfits_manifest = MANIFESTS_DIR / "outfits_manifest.json"
    outfits_manifest.write_text(json.dumps({
        "schema_version": "1.0.0",
        "total_outfits": len(outfit_records),
        "categories": {
            "casual": 20,
            "traditional": 20,
            "formal": 15,
            "sports": 10,
            "festival": 15,
            "premium": 10,
            "utility": 10
        },
        "outfits": outfit_records
    }, indent=2) + "\n", encoding="utf-8")

    print(f"SUCCESS: Generated 500 unique NPC skins (Boss: npc-481, Prisoners: npc-482..486)")
    print(f"SUCCESS: Generated 100 unique outfit overlays across 7 categories")
    print(f"Manifests written to {skins_manifest} and {outfits_manifest}")

if __name__ == "__main__":
    build()
