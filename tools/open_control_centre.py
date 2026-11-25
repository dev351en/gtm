#!/usr/bin/env python3
"""Open the actual GTM local control centre; keep owner tokens out of logs.

With --daytona, forward only the existing server's loopback console through a
new owner-authorized SSH session. No server installation, restart or remote
shell command from a browser is performed.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener
import webbrowser

ROOT = Path(__file__).resolve().parent.parent
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_-]{43}")


def token_value(text: str) -> str:
    value = text.strip()
    if not TOKEN_PATTERN.fullmatch(value): raise RuntimeError("The console token is invalid. Start the repaired game server first.")
    return value


def verify(token: str, port: int) -> dict:
    request = Request(f"http://127.0.0.1:{port}/api/status", headers={"Authorization": "Bearer " + token})
    # Never forward a local owner token to a system proxy.
    with build_opener(ProxyHandler({})).open(request, timeout=3) as response:
        raw = response.read(65537)
    if len(raw) > 65536: raise RuntimeError("The console returned an unexpected response.")
    result = json.loads(raw)
    if not isinstance(result, dict) or not result.get("ready") or not result.get("version"):
        raise RuntimeError("The repaired server console is not ready.")
    return result


def open_local(root: Path, port: int, check: bool) -> None:
    file = root / "plugins/SDCraftCore/console-access.token"
    if file.is_symlink() or not file.is_file() or file.stat().st_size > 128:
        raise RuntimeError("Start the repaired server first. Its local console token has not been created.")
    token = token_value(file.read_text(encoding="utf-8"))
    status = verify(token, port)
    print("Connected to GTM Control Centre " + status["version"] + ".")
    if not check:
        if not webbrowser.open(f"http://127.0.0.1:{port}/#token={token}", new=2):
            raise RuntimeError("The dashboard is running, but the default browser could not be launched. Configure your default browser and run this opener again.")
        print("Requested the private dashboard in your default browser.")


def open_daytona(root: Path, remote_root: str, port: int, check: bool) -> None:
    try:
        from daytona_tunnel import DaytonaAccess, load_settings, require_ssh, SSH_HOST
    except ImportError:
        raise RuntimeError("Run the Daytona console opener from the updated GitHub repository, which includes tools/daytona_tunnel.py.") from None
    if not remote_root.startswith("/") or any(c in remote_root for c in "\r\n\0"):
        raise RuntimeError("The remote server directory must be an absolute path.")
    settings_root = root
    if not (settings_root / ".secrets.env").is_file() and (root.parent / ".secrets.env").is_file(): settings_root = root.parent
    access = DaytonaAccess(load_settings(settings_root))
    access.require_running()
    ssh = require_ssh()
    session = access.create_token()
    process = None
    common = [ssh, "-F", os.devnull, "-T", "-o", "StrictHostKeyChecking=accept-new", "-o", "BatchMode=yes",
              "-o", "ConnectTimeout=15", "-o", "ForwardAgent=no", "-o", "PasswordAuthentication=no",
              "-o", "KbdInteractiveAuthentication=no", "-o", "PubkeyAuthentication=no", "-o", "LogLevel=ERROR"]
    try:
        read = subprocess.run(common + ["-l", session, SSH_HOST, "cat -- " + shlex.quote(remote_root.rstrip("/") + "/plugins/SDCraftCore/console-access.token")],
                              stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20, check=False)
        if read.returncode or len(read.stdout) > 128:
            raise RuntimeError("The repaired console token was not found on the existing Daytona server. Install the repair and start Paper first.")
        token = token_value(read.stdout.decode("ascii"))
        existing = False
        try: verify(token, port); existing = True
        except (OSError, ValueError, RuntimeError): pass
        if not existing:
            with socket.socket() as free: free.bind(("127.0.0.1", port))
            process = subprocess.Popen(common + ["-N", "-L", f"127.0.0.1:{port}:127.0.0.1:{port}",
                    "-o", "ExitOnForwardFailure=yes", "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=3",
                    "-o", "GatewayPorts=no", "-l", session, SSH_HOST], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            deadline = time.monotonic() + 25
            while True:
                if process.poll() is not None: raise RuntimeError("The console tunnel could not start. Check OpenSSH, the port and your existing Daytona access.")
                try: verify(token, port); break
                except (OSError, ValueError, RuntimeError):
                    if time.monotonic() >= deadline: raise RuntimeError("The existing server's console did not respond. No server changes were made.") from None
                    time.sleep(.3)
        print("Verified the existing Daytona Control Centre through localhost.")
        if not check:
            if not webbrowser.open(f"http://127.0.0.1:{port}/#token={token}", new=2):
                raise RuntimeError("The console tunnel worked, but the default browser could not be launched. Configure your default browser and run this opener again.")
            print("Requested the private dashboard in your default browser.")
            if process is not None:
                print("Keep this window open for the dashboard. Ctrl+C closes only this console tunnel.")
                while process.poll() is None: time.sleep(.5)
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try: process.wait(timeout=3)
            except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=3)
        try: access.revoke_token(session)
        except Exception: print("This console session's token revocation could not be confirmed; its normal expiry still applies.")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", type=Path, default=ROOT)
    parser.add_argument("--daytona", action="store_true")
    parser.add_argument("--remote-root", default="/home/daytona/sdcraft_server")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if not 1024 <= args.port <= 65535: raise RuntimeError("Choose a valid console port.")
        if args.daytona: open_daytona(args.server, args.remote_root, args.port, args.check)
        else: open_local(args.server, args.port, args.check)
        return 0
    except KeyboardInterrupt:
        print("Closed this console connection. The game server was left running."); return 0
    except (HTTPError, URLError, OSError):
        print("The local console could not be reached. Start the repaired server, or use --daytona for its secure tunnel.", file=sys.stderr); return 1
    except (ValueError, UnicodeError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr); return 1
    except Exception:
        print("Console connection failed. No credentials or private diagnostics were printed.", file=sys.stderr); return 1


if __name__ == "__main__": sys.exit(main())
