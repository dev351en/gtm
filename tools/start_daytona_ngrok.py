#!/usr/bin/env python3
"""Compatibility entrypoint redirecting Ngrok launches through the working local SSH+Ngrok bridge.

Daytona sandboxes block outbound Ngrok egress on port 443, so launching Ngrok
inside Daytona fails with connection resets. Bridging over the verified local
Daytona SSH tunnel via launch_daytona_and_ngrok keeps both local and public access working.
"""
from __future__ import annotations

from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from launch_daytona_and_ngrok import main as launch_main  # noqa: E402


def main(argv=None) -> int:
    print("[*] Daytona outbound Ngrok is blocked by sandbox firewall; starting local SSH + Ngrok bridge...")
    return launch_main(argv)


if __name__ == "__main__":
    sys.exit(main())
