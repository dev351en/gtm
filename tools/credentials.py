import os
import sys
from pathlib import Path

def _load_env_file():
    candidates = [
        Path.cwd() / ".secrets.env",
        Path.cwd() / ".env",
        Path(__file__).resolve().parent / ".secrets.env",
        Path(__file__).resolve().parent.parent / ".secrets.env",
        Path(__file__).resolve().parent.parent / ".env",
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            if k not in os.environ:
                                os.environ[k] = v
                return
            except Exception:
                pass

_load_env_file()

def get_daytona_api_key():
    key = os.environ.get("DAYTONA_API_KEY")
    if not key or "your_daytona" in key:
        print("[!] ERROR: DAYTONA_API_KEY is not configured.", file=sys.stderr)
        print("    Please set DAYTONA_API_KEY in your local .secrets.env file.", file=sys.stderr)
        sys.exit(1)
    return key

def get_daytona_sandbox_id():
    sb = os.environ.get("DAYTONA_SANDBOX_ID", "b6a826ca-4dac-4716-b7b9-236b88b4718e")
    return sb

def get_ngrok_authtoken():
    return os.environ.get("NGROK_AUTHTOKEN", "")
