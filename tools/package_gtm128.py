#!/usr/bin/env python3
"""Package validated native128 artwork, editable exports, packs and review evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from gtm128_packs import archive

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "GTM_Indraprastha_128"


def package(output: Path, destination: Path, overview: Path | None = None) -> dict:
    output = output.resolve()
    source_report = json.loads((output / "reports/validation_128.json").read_text())
    pack_report = json.loads((output / "reports/pack_validation_128.json").read_text())
    if source_report["errors"] or pack_report["errors"]:
        raise ValueError("Cannot package art with failed validation")
    for record in pack_report["packs"]:
        path = output / record["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError("Pack changed after validation: " + record["path"])

    files = {}
    for directory in ("source", "compatibility", "manifests", "reports", "previews", "packs"):
        for path in sorted((output / directory).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                files[PREFIX + "/" + path.relative_to(output).as_posix()] = path.read_bytes()
    for path in (ROOT / "docs/creative/DESIGN_LANGUAGE_128.md",
                 ROOT / "docs/creative/GENERATION_128_REPORT.md",
                 ROOT / "creative/design_language_128.json"):
        if path.suffix == ".md":
            text = path.read_text(encoding="utf-8")
            text = text.replace("../../creative/generated_128/", "")
            text = text.replace("../../creative/design_language_128.json", "design_language_128.json")
            files[PREFIX + "/" + path.name] = text.encode("utf-8")
        else:
            files[PREFIX + "/" + path.name] = path.read_bytes()
    if overview is not None:
        files["GTM_128_Asset_Overview.png"] = overview.read_bytes()

    readme = """# GTM / Indraprastha — native 128×128 asset collection

Generation checkpoint: 25 November 2026. Profile: INDRAPRASTHA_128_V1.

This bundle contains the generated art catalogue, editable model/texture exports,
Java and Bedrock staging packs, contact sheets, manifests and validation evidence.
It is an asset-generation delivery. Runtime integration, live client testing and
production deployment remain separate work.

## What is included

| Family | Count |
| --- | ---: |
| Primary models | 509: 87 transport, 200 furniture, 100 legacy festival, 92 equipment, 30 food |
| Additional base models | 69: 30 preserved weapon-source models, 11 hero props, 28 festival additions |
| Road damage variants | 195: 65 road vehicles × damaged, critical and wreck |
| Cosmetic finish variants | 300: 30 existing source IDs × 10 finish collections |
| Native NPC skin masters | 500 |
| Native outfit masters | 100 |
| Java 64×64 skin/outfit compatibility exports | 600 |
| Phone / HUD / fictional brands / core identities | 24 / 33 / 32 / 4 |
| Bilingual signs | 120 composites, each assembled from two 128×128 tiles |
| Material / world texture tiles | 168 / 98 |

The 509 primary models have 509 exact geometry definitions. Finish variants share
their source geometry by design. The additional 69 source IDs include inherited
geometry reuse; they are not 69 newly unique designs. The 30 weapon-source IDs
include melee and special props, so they are not a claim of 30 unique firearms.

The approved 100-design festival selection uses 72 preserved models plus 28 new
designs across the eight requested themes. All 100 legacy festival IDs remain
available. The selection does not place or activate installations in a world.

## Open the files

All paths below are inside `GTM_Indraprastha_128/`.

- `source/`: native PNGs, editable SVGs, Java models, Bedrock geometry and editable
  `.parts.json` model recipes. The shared 2048×2048 atlas contains 128×128 cells.
- `compatibility/java64/`: 64×64 skin/outfit derivatives. Use these when the target
  Java skin integration requires 64 pixels; retain the 128-pixel art masters.
- `previews/`: contact sheets and individual character views. These are art
  previews, not screenshots from a running Java or Bedrock client.
- `manifests/`: stable IDs, relative file paths, dimensions, source metadata and
  hashes. Resolve paths relative to `GTM_Indraprastha_128/`.
- `reports/`: source validation, pack graph checks, reproducibility evidence and
  visual-review records. Zero validation errors; live client checks are pending.
- `DESIGN_LANGUAGE_128.md` and `design_language_128.json`: the reusable native128
  art rules, palette, UV/alpha requirements and future-generation prompt scaffold.
- `GENERATION_128_REPORT.md`: detailed handoff, actual checks and remaining scope.

## Staging resource packs

`packs/GTM_Indraprastha_128_Java.zip` targets Java 26.3 resource format 97.1.
`packs/GTM_Indraprastha_128_Bedrock.mcpack` is the paired Bedrock resource export.
The pack graphs resolve 1,073 model pairs and 1,103 item definitions, including
30 explicit aliases for the existing FoodCatalogue runtime IDs.

Import or load these in a development client for the pending visual checks.
Generating a resource definition does not spawn a vehicle, create an NPC,
implement physics or register a server item. The artwork includes proposed IDs
for additions and damage states that still need engineering binding.

`packs/Geyser_v2_128_ART_PROPOSAL.json` is an uninstalled integration proposal.
Review it against the installed Geyser/runtime version before applying it.
NPC skin signing/binding, wearable overlays, HUD interaction, vehicle physics
and legacy migration activation have not been performed by this art export.

## Reproduce and extend

Source and design rules: https://github.com/dev351en/gtm/tree/gtm/creative-r4
Creative review: https://github.com/dev351en/gtm/pull/2

From a complete checkout, install `tools/requirements-gtm128.txt`, supply the
DejaVu/Noto fonts and RAQM support described in the design guide, then run:

```bash
python tools/build_gtm128.py
```

`--plan` lists the ordered stages. `--verify-only` validates existing artwork and
rebuilds/resolves its staging packs. The source report records the checks actually
run; it does not claim that live clients or a clean full orchestration were run.

Use `python tools/package_gtm128.py --overview /path/to/overview.png` to assemble
this delivery layout; the overview argument is optional. `SHA256SUMS.txt` lists
every included file except itself. Platform copies, compatibility exports and
preview images do not add to unique design counts.
"""
    files["START_HERE.md"] = readme.encode("utf-8")
    files["SHA256SUMS.txt"] = "".join(
        hashlib.sha256(data).hexdigest() + "  " + name + "\n"
        for name, data in sorted(files.items())
    ).encode("utf-8")
    return archive(destination, files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "creative/generated_128")
    parser.add_argument("--archive", type=Path,
                        default=ROOT / "creative/generated_128/delivery/GTM_Indraprastha_128_Assets.zip")
    parser.add_argument("--overview", type=Path)
    args = parser.parse_args()
    print(json.dumps(package(args.output, args.archive, args.overview), indent=2))
