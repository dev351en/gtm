#!/usr/bin/env python3
"""Launch Daytona SSH loopback + local Ngrok TCP bridge for multiplayer access.

Daytona sandboxes block outbound Ngrok control traffic, so Ngrok must run locally
on Windows pointing at the verified IPv4 loopback SSH tunnel (127.0.0.1:25565).
"""
from __future__ import annotations

import argparse
from collections import deque
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from daytona_tunnel import (  # noqa: E402
    ConnectionFailure,
    DaytonaAccess,
    GAME_PORT,
    LOCAL_HOST,
    OwnedSshProcess,
    load_settings,
    minecraft_status,
    require_free_port,
    require_ssh,
    ssh_command,
    wait_for_game,
)

REPO_ROOT = SCRIPT_DIR.parent
BLUEMAP_URL = "https://8100-b6a826ca-4dac-4716-b7b9-236b88b4718e.daytonaproxy01.eu/"
NGROK_API_URL = "http://127.0.0.1:4040/api/tunnels"
SDCRAFT_ROOT = Path(r"d:\Games\SDCRAFT")


def find_ngrok_bin(root: Path = REPO_ROOT) -> str:
    """Locate ngrok.exe across repo, parent SDCRAFT tools, or system PATH."""
    env_bin = os.environ.get("NGROK_BIN", "").strip()
    candidates = [
        Path(env_bin) if env_bin else None,
        SCRIPT_DIR / "ngrok" / "ngrok.exe",
        root.parent / "tools" / "ngrok" / "ngrok.exe",
        SDCRAFT_ROOT / "tools" / "ngrok" / "ngrok.exe",
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return str(candidate)
    which_bin = shutil.which("ngrok")
    if which_bin:
        return which_bin
    raise ConnectionFailure(
        "ngrok.exe was not found. Install Ngrok into tools\\ngrok\\ngrok.exe or add ngrok to PATH."
    )


def load_ngrok_authtoken(root: Path = REPO_ROOT) -> str:
    """Read NGROK_AUTHTOKEN from env, .secrets.env, or tools/ngrok_authtoken.txt without echoing it."""
    token = os.environ.get("NGROK_AUTHTOKEN", "").strip()
    if token:
        return token
    for secret_file in (root / ".secrets.env", root.parent / ".secrets.env"):
        if not secret_file.is_file():
            continue
        try:
            for raw_line in secret_file.read_text(encoding="utf-8-sig").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key.strip() == "NGROK_AUTHTOKEN":
                    cleaned = value.strip().strip("\"'")
                    if cleaned:
                        return cleaned
        except (OSError, UnicodeError):
            pass
    token_file = SCRIPT_DIR / "ngrok_authtoken.txt"
    if token_file.is_file():
        try:
            return token_file.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError):
            pass
    return ""


def _ngrok_config_has_token() -> bool:
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "ngrok" / "ngrok.yml",
        Path.home() / ".config" / "ngrok" / "ngrok.yml",
    ]
    for cfg in candidates:
        if not cfg.is_file():
            continue
        try:
            text = cfg.read_text(encoding="utf-8", errors="ignore")
            if any(line.strip().startswith("authtoken:") and len(line.split(":", 1)[1].strip()) > 8 for line in text.splitlines()):
                return True
        except OSError:
            pass
    return False


def ensure_ngrok_configured(ngrok_bin: str, token: str):
    """Ensure ngrok.yml has a valid authtoken before starting a TCP tunnel."""
    if token:
        try:
            res = subprocess.run(
                [ngrok_bin, "config", "add-authtoken", token],
                shell=False,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=10,
            )
        except OSError:
            raise ConnectionFailure("Failed to execute ngrok config add-authtoken.") from None
        if res.returncode != 0:
            raise ConnectionFailure("Ngrok rejected the configured authtoken.")
        return
    if not _ngrok_config_has_token():
        raise ConnectionFailure(
            "NGROK_AUTHTOKEN is missing. Set it in .secrets.env or run `ngrok config add-authtoken <token>`."
        )


def cleanup_stale_tunnels():
    """Stop orphaned Daytona SSH tunnels and stale Ngrok processes on Windows."""
    if os.name != "nt":
        return
    ps = shutil.which("powershell") or shutil.which("pwsh")
    if not ps:
        return
    script = (
        "$ErrorActionPreference='SilentlyContinue';"
        "$procs = Get-CimInstance Win32_Process | Where-Object { "
        "($_.Name -ieq 'ngrok.exe') -or "
        "($_.Name -ieq 'ssh.exe' -and $_.CommandLine -like '*ssh.app.daytona.io*') };"
        "foreach ($p in $procs) { Stop-Process -Id $p.ProcessId -Force }"
    )
    try:
        subprocess.run(
            [ps, "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            timeout=8,
        )
    except Exception:
        pass
    time.sleep(0.5)


class OwnedNgrokProcess:
    """Manage local Ngrok TCP child process and keep a bounded log tail."""

    def __init__(self, ngrok_bin: str):
        try:
            self.process = subprocess.Popen(
                [ngrok_bin, "tcp", f"{LOCAL_HOST}:{GAME_PORT}", "--log=stdout", "--log-format=logfmt"],
                shell=False,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        except OSError:
            raise ConnectionFailure("Could not start ngrok.exe.") from None
        self._lines: deque[str] = deque(maxlen=40)
        self._reader = threading.Thread(target=self._drain, daemon=True)
        self._reader.start()

    def _drain(self):
        try:
            while True:
                raw = self.process.stdout.readline(4096)
                if not raw:
                    return
                text = raw.decode("utf-8", errors="replace").strip()
                if text:
                    self._lines.append(text)
        except (OSError, ValueError):
            pass

    def poll(self):
        return self.process.poll()

    def log_tail(self, count: int = 6) -> str:
        tail = list(self._lines)[-count:]
        return "\n".join(tail)

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=3)
        self._reader.join(timeout=1)
        if self.process.stdout:
            self.process.stdout.close()


def wait_for_ngrok_address(ngrok: OwnedNgrokProcess, ssh: OwnedSshProcess, timeout: float = 20.0) -> str:
    """Poll Ngrok's local inspector API until tcp:// URL appears or exit clearly on error."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if ssh.poll() is not None:
            raise ssh.failure()
        if ngrok.poll() is not None:
            tail = ngrok.log_tail()
            raise ConnectionFailure(
                "Ngrok exited before opening a TCP tunnel.\n" + (tail or "Check your NGROK_AUTHTOKEN and internet connection.")
            )
        try:
            req = Request(NGROK_API_URL, headers={"Accept": "application/json"})
            with urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for tunnel in data.get("tunnels", []):
                public_url = str(tunnel.get("public_url", "")).strip()
                if tunnel.get("proto") == "tcp" and public_url.startswith("tcp://"):
                    return public_url.removeprefix("tcp://").strip()
        except (URLError, TimeoutError, ValueError, OSError):
            pass
        time.sleep(0.5)
    tail = ngrok.log_tail()
    raise ConnectionFailure(
        "Timed out waiting for Ngrok public TCP address." + (("\n" + tail) if tail else "")
    )


def probe_public_address(public_addr: str) -> dict | None:
    """Attempt a real Minecraft status+ping probe over the public Ngrok host:port."""
    if ":" not in public_addr:
        return None
    host, port_text = public_addr.rsplit(":", 1)
    host = host.strip()
    try:
        port = int(port_text.strip())
    except ValueError:
        return None
    for _ in range(3):
        try:
            return minecraft_status(
                timeout=4.0,
                connector=lambda _addr, timeout=4.0: socket.create_connection((host, port), timeout=timeout),
            )
        except (OSError, ValueError, UnicodeError):
            time.sleep(1.0)
    return None


def write_active_address(public_addr: str):
    """Write ACTIVE_SERVER_ADDRESS.txt cleanly only inside existing d:\\Games\\SDCRAFT workspace."""
    if not SDCRAFT_ROOT.is_dir():
        return
    target = SDCRAFT_ROOT / "ACTIVE_SERVER_ADDRESS.txt"
    content = (
        f"PUBLIC ADDRESS FOR FRIENDS (copy exact line, no leading space):\n{public_addr}\n\n"
        f"LOCAL ADDRESS FOR YOU:\n127.0.0.1:25565\n\n"
        f"BLUEMAP:\n{BLUEMAP_URL}\n"
    )
    target.write_text(content, encoding="utf-8")


def monitor_tunnels(ssh: OwnedSshProcess, ngrok: OwnedNgrokProcess):
    """Keep monitoring both tunnels until interrupted or one drops."""
    failures = 0
    next_check = time.monotonic() + 10
    while True:
        if ssh.poll() is not None:
            raise ssh.failure()
        if ngrok.poll() is not None:
            tail = ngrok.log_tail()
            raise ConnectionFailure("Ngrok tunnel closed unexpectedly." + (("\n" + tail) if tail else ""))
        if time.monotonic() >= next_check:
            try:
                minecraft_status(timeout=2.0)
                failures = 0
            except (OSError, ValueError, UnicodeError):
                failures += 1
                if failures >= 3:
                    raise ConnectionFailure("Minecraft stopped responding through the Daytona SSH tunnel.")
            next_check = time.monotonic() + 10
        time.sleep(0.5)


def run_multiplayer(settings: dict, check_only: bool = False):
    print("=" * 65)
    print("    SDCRAFT - DAYTONA CLOUD + NGROK MULTIPLAYER LAUNCHER")
    print("=" * 65)
    executable = require_ssh()
    ngrok_bin = find_ngrok_bin()
    ngrok_token = load_ngrok_authtoken()
    if check_only:
        ensure_ngrok_configured(ngrok_bin, ngrok_token)
        require_free_port()
        print("Checks passed: Daytona settings, OpenSSH, Ngrok binary/token, and 127.0.0.1:25565.")
        return

    print("[1/4] Cleaning stale tunnels and verifying Ngrok configuration...")
    cleanup_stale_tunnels()
    require_free_port()
    ensure_ngrok_configured(ngrok_bin, ngrok_token)

    access = DaytonaAccess(settings)
    token = None
    ssh = None
    ngrok = None
    try:
        print("[2/4] Connecting to Daytona Cloud sandbox and starting SSH tunnel...")
        access.require_running()
        token = access.create_token()
        ssh = OwnedSshProcess(ssh_command(executable, token))
        local_status = wait_for_game(ssh)
        print(f"      Local tunnel verified: {local_status['version']} on 127.0.0.1:25565")

        print("[3/4] Launching local Ngrok TCP tunnel to 127.0.0.1:25565...")
        ngrok = OwnedNgrokProcess(ngrok_bin)

        print("[4/4] Retrieving and verifying Ngrok public address...")
        public_addr = wait_for_ngrok_address(ngrok, ssh)
        public_status = probe_public_address(public_addr)
        write_active_address(public_addr)

        print("\n" + "=" * 65)
        print("  >>> SERVER IS ONLINE & ACCESSIBLE WORLDWIDE! <<<")
        print("=" * 65)
        print(f"  PUBLIC IP FOR FRIENDS : {public_addr}")
        print("  LOCAL IP FOR YOU      : 127.0.0.1:25565")
        if public_status:
            print(f"  PUBLIC PING CHECK     : OK ({public_status['version']})")
        else:
            print("  PUBLIC PING CHECK     : Waiting/loopback filtered (local SSH tunnel OK)")
        print("  BLUEMAP (BROWSER)     :")
        print(f"    {BLUEMAP_URL}")
        print("=" * 65)
        print("Keep this window open while playing. Press Ctrl+C to disconnect.\n")

        monitor_tunnels(ssh, ngrok)
    finally:
        try:
            if ngrok is not None:
                ngrok.close()
        finally:
            try:
                if ssh is not None:
                    ssh.close()
            finally:
                if token is not None:
                    try:
                        access.revoke_token(token)
                    except ConnectionFailure:
                        print("Note: local tunnel closed; Daytona session token will expire automatically.")


def _raise_interrupt(_signum, _frame):
    raise KeyboardInterrupt


def main(argv=None) -> int:
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, _raise_interrupt)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify local prerequisites without opening tunnels")
    args = parser.parse_args(argv)
    try:
        if sys.version_info < (3, 10):
            raise ConnectionFailure("Python 3.10 or newer is required for this launcher.")
        run_multiplayer(load_settings(), check_only=args.check)
        return 0
    except KeyboardInterrupt:
        print("\nShutting down Ngrok and Daytona SSH tunnels cleanly...")
        return 0
    except ConnectionFailure as exc:
        print("Multiplayer stopped: " + str(exc), file=sys.stderr)
        return 1
    except Exception:
        print("Multiplayer stopped because of an unexpected local error.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
