#!/usr/bin/env python3
"""Generate the isolated Indraprastha native128 art catalogue and staging packs.

Run from a complete repository checkout. Each exporter uses a separate Python
process so its material registry cannot affect another exporter. This command
does not change runtime registries, install packs, or deploy a server.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
GENERATORS = (
    "gtm128_core.py",
    "gtm128_models.py",
    "gtm128_equipment_food.py",
    "gtm128_characters.py",
    "gtm128_ui.py",
    "gtm128_world.py",
    "gtm128_festival_additions.py",
    "gtm128_vehicle_states.py",
)
CHECKS_AND_PACKS = ("gtm128_validate.py", "gtm128_packs.py")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "creative/generated_128")
    parser.add_argument("--verify-only", action="store_true",
                        help="Validate existing art and rebuild/resolve its staging packs")
    parser.add_argument("--plan", action="store_true",
                        help="Print the ordered commands without generating files")
    args = parser.parse_args()
    output = args.output.resolve()
    stages = CHECKS_AND_PACKS if args.verify_only else GENERATORS + CHECKS_AND_PACKS
    for number, script in enumerate(stages, 1):
        command = [sys.executable, str(ROOT / "tools" / script), "--output", str(output)]
        print(f"[{number}/{len(stages)}] {script} --output {output}", flush=True)
        if not args.plan:
            subprocess.run(command, cwd=ROOT, check=True)
    if not args.plan:
        print(f"Finished: {output}", flush=True)
        print("Art and static pack checks passed; live client/runtime verification remains pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
