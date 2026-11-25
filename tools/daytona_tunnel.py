#!/usr/bin/env python3
"""Connect a laptop to the existing Daytona game, without deploying or restarting it.

Only the documented v0 sandbox GET and SSH-access create/revoke endpoints are
used. Python's standard library is sufficient; no Daytona SDK is installed.
The SSH session and token created here are the only resources cleaned up.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import socket
import struct
import subprocess
import sys
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, Request, build_opener
import uuid

DEFAULT_SANDBOX = "b6a826ca-4dac-4716-b7b9-236b88b4718e"
API_ROOT = "https://app.daytona.io/api"
SSH_HOST = "ssh.app.daytona.io"
LOCAL_HOST = "127.0.0.1"
GAME_PORT = 25565
TOKEN_MINUTES = 60
MAX_RESPONSE = 1024 * 1024
MAX_STATUS = 65536
REPO_ROOT = Path(__file__).resolve().parents[1]


class ConnectionFailure(Exception):
    """A deliberately credential-free error suitable for the owner console."""


def load_settings(root: Path = REPO_ROOT, environ=None) -> dict:
    """Read only two known settings; never execute a dotenv file or print it."""
    source = os.environ if environ is None else environ
    values = {key: source[key] for key in ("DAYTONA_API_KEY", "DAYTONA_SANDBOX_ID") if key in source}
    secret_file = root / ".secrets.env"
    if secret_file.exists():
        if secret_file.is_symlink() or not secret_file.is_file() or secret_file.stat().st_size > 65536:
            raise ConnectionFailure("The local .secrets.env must be a regular file smaller than 64 KiB.")
        try:
            lines = secret_file.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeError):
            raise ConnectionFailure("The local .secrets.env could not be read as UTF-8.") from None
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if key not in ("DAYTONA_API_KEY", "DAYTONA_SANDBOX_ID") or key in values:
                continue
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            values[key] = value
    key = values.get("DAYTONA_API_KEY", "")
    if not isinstance(key, str) or not 16 <= len(key) <= 4096 or not re.fullmatch(r"[!-~]+", key):
        raise ConnectionFailure("Set DAYTONA_API_KEY in your environment or local .secrets.env. Never commit that file.")
    sandbox = values.get("DAYTONA_SANDBOX_ID", DEFAULT_SANDBOX)
    try:
        parsed = str(uuid.UUID(sandbox))
    except (ValueError, TypeError, AttributeError):
        raise ConnectionFailure("DAYTONA_SANDBOX_ID must be the existing sandbox's UUID.") from None
    if parsed != sandbox.lower():
        raise ConnectionFailure("DAYTONA_SANDBOX_ID must use the full hyphenated UUID.")
    return {"key": key, "sandbox": parsed}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward the owner's authorization to another endpoint.
        return None


class DaytonaAccess:
    def __init__(self, settings: dict, opener=None):
        self.key = settings["key"]
        self.sandbox = settings["sandbox"]
        self.opener = opener or build_opener(NoRedirect())

    def _request(self, method: str, suffix: str = "") -> dict:
        path = "/sandbox/" + quote(self.sandbox, safe="") + suffix
        request = Request(API_ROOT + path, method=method,
                          data=b"" if method == "POST" else None,
                          headers={"Authorization": "Bearer " + self.key,
                                   "Accept": "application/json",
                                   "User-Agent": "GTM-existing-Daytona-connector/1.0"})
        try:
            with self.opener.open(request, timeout=15) as response:
                raw = response.read(MAX_RESPONSE + 1)
        except HTTPError as exc:
            raise ConnectionFailure(f"Daytona {method} request failed (HTTP {exc.code}). Check your account access and sandbox state.") from None
        except (URLError, TimeoutError, OSError):
            raise ConnectionFailure("Daytona could not be reached over verified HTTPS. No automatic retry was made.") from None
        if len(raw) > MAX_RESPONSE:
            raise ConnectionFailure("Daytona returned an unexpectedly large response.")
        if not raw and method == "DELETE":
            return {}
        try:
            result = json.loads(raw)
        except (ValueError, UnicodeError):
            raise ConnectionFailure("Daytona returned an unreadable response.") from None
        if not isinstance(result, dict):
            raise ConnectionFailure("Daytona returned an unexpected response type.")
        return result

    def require_running(self):
        details = self._request("GET")
        if details.get("id") != self.sandbox:
            raise ConnectionFailure("Daytona did not confirm the requested sandbox identity.")
        if str(details.get("state", "")).lower() != "started":
            raise ConnectionFailure("The existing Daytona sandbox is not started. Check it in your Daytona dashboard; this connector does not start or restart it.")

    def create_token(self) -> str:
        response = self._request("POST", f"/ssh-access?expiresInMinutes={TOKEN_MINUTES}")
        token = response.get("token")
        # The documented token is opaque. Pass it as one -l argument without a
        # shell; do not assume that it will always use today's JWT alphabet.
        if not isinstance(token, str) or not re.fullmatch(r"[!-~]{1,4096}", token):
            raise ConnectionFailure("Daytona returned an invalid SSH access token. No SSH process was started.")
        return token

    def revoke_token(self, token: str):
        # Always revoke this exact token, never all sessions for the sandbox.
        self._request("DELETE", "/ssh-access?token=" + quote(token, safe=""))


def require_free_port():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
                listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            listener.bind((LOCAL_HOST, GAME_PORT))
    except OSError:
        raise ConnectionFailure("127.0.0.1:25565 is already in use. Close the local game server or previous tunnel before connecting; nothing was stopped automatically.") from None


def require_ssh() -> str:
    executable = shutil.which("ssh")
    if not executable:
        raise ConnectionFailure("OpenSSH Client was not found. Enable the Windows OpenSSH Client optional feature, then run this launcher again.")
    return executable


def ssh_command(executable: str, token: str) -> list[str]:
    return [executable, "-F", os.devnull, "-N", "-T",
            "-L", f"{LOCAL_HOST}:{GAME_PORT}:{LOCAL_HOST}:{GAME_PORT}",
            "-o", "ExitOnForwardFailure=yes", "-o", "StrictHostKeyChecking=accept-new",
            "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
            "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=3",
            "-o", "ForwardAgent=no", "-o", "GatewayPorts=no",
            "-o", "PasswordAuthentication=no", "-o", "KbdInteractiveAuthentication=no",
            "-o", "PubkeyAuthentication=no", "-o", "LogLevel=DEBUG1",
            "-l", token, SSH_HOST]


class OwnedSshProcess:
    """Drain bounded diagnostics privately; never echo a token-bearing SSH error."""
    def __init__(self, command: list[str], popen=subprocess.Popen):
        try:
            self.process = popen(command, shell=False, stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        except OSError:
            raise ConnectionFailure("OpenSSH could not start. Check the Windows OpenSSH Client installation.") from None
        self._errors = bytearray()
        self._forward_ready = threading.Event()
        self._reader = threading.Thread(target=self._drain, daemon=True)
        self._reader.start()

    def _drain(self):
        listener_seen = False
        continuation = False
        try:
            while True:
                # readline returns each diagnostic promptly instead of waiting
                # for a full buffered read. Keep both lines and retained bytes
                # bounded; never echo any diagnostic (it can include the token).
                chunk = self.process.stderr.readline(4096)
                if not chunk:
                    return
                self._errors.extend(chunk)
                if len(self._errors) > 8192:
                    del self._errors[:-8192]
                if not continuation and chunk.endswith(b"\n"):
                    line = chunk.rstrip(b"\r\n")
                    if line == b"debug1: Local forwarding listening on 127.0.0.1 port 25565.":
                        listener_seen = True
                    elif listener_seen and line == b"debug1: Entering interactive session.":
                        # OpenSSH logs the listener attempt BEFORE bind(). Its
                        # session-loop diagnostic occurs AFTER forwarding setup;
                        # ExitOnForwardFailure aborts before this on bind failure.
                        self._forward_ready.set()
                continuation = not chunk.endswith(b"\n")
        except (OSError, ValueError):
            pass

    def forwarding_ready(self):
        return self._forward_ready.is_set()

    def poll(self):
        return self.process.poll()

    def failure(self) -> ConnectionFailure:
        self._reader.join(timeout=0.1)
        data = bytes(self._errors).lower()
        if b"host identification has changed" in data or b"host key verification failed" in data:
            return ConnectionFailure("SSH host-key verification failed. Verify the Daytona gateway fingerprint before changing your known_hosts file.")
        if b"address already in use" in data or b"cannot listen to port" in data or b"could not request local forwarding" in data:
            return ConnectionFailure("SSH could not bind localhost:25565. Close the conflicting local server or tunnel and retry.")
        if b"bad configuration option" in data or b"unsupported option" in data:
            return ConnectionFailure("This OpenSSH version does not support the required secure options. Update the Windows OpenSSH Client.")
        return ConnectionFailure("The SSH connection ended. Check the Daytona sandbox, access permissions, network, and the gateway host key.")

    def close(self):
        # No taskkill, killall, process-name search, or remote command is used.
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=3)
        self._reader.join(timeout=1)
        self.process.stderr.close()


def encode_varint(value: int) -> bytes:
    result = bytearray()
    value &= 0xffffffff
    while True:
        byte = value & 0x7f
        value >>= 7
        result.append(byte | (0x80 if value else 0))
        if not value:
            return bytes(result)


def read_varint(read) -> int:
    value = 0
    for index in range(5):
        chunk = read(1)
        if len(chunk) != 1:
            raise ValueError("Truncated VarInt")
        byte = chunk[0]
        value |= (byte & 0x7f) << (index * 7)
        if not byte & 0x80:
            if value > 0x7fffffff:
                raise ValueError("Negative or oversized packet value")
            return value
    raise ValueError("Oversized VarInt")


def decode_status(packet: bytes) -> dict:
    from io import BytesIO
    source = BytesIO(packet)
    if read_varint(source.read) != 0:
        raise ValueError("Not a Minecraft status response")
    length = read_varint(source.read)
    if length > MAX_STATUS:
        raise ValueError("Oversized Minecraft status")
    payload = source.read(length)
    if len(payload) != length or source.read(1):
        raise ValueError("Invalid Minecraft status packet length")
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("Invalid Minecraft status")
    version = data.get("version")
    players = data.get("players")
    if (not isinstance(version, dict) or not isinstance(version.get("name"), str)
            or not version["name"] or len(version["name"]) > 128
            or type(version.get("protocol")) is not int or version["protocol"] < 0
            or not isinstance(players, dict)
            or any(type(players.get(key)) is not int or players[key] < 0 for key in ("online", "max"))):
        raise ValueError("Invalid Minecraft status fields")
    # Remote MOTD and names are never rendered into the console.
    return {"version": re.sub(r"[^A-Za-z0-9 ._+/-]", "", version["name"])[:80],
            "protocol": version["protocol"]}


def minecraft_status(timeout: float = 2.0, connector=socket.create_connection,
                     clock=time.monotonic, nonce_factory=os.urandom) -> dict:
    deadline = clock() + timeout
    with connector((LOCAL_HOST, GAME_PORT), timeout=timeout) as sock:
        def remaining():
            left = deadline - clock()
            if left <= 0:
                raise TimeoutError("Minecraft status deadline")
            sock.settimeout(left)

        def receive(count):
            result = bytearray()
            while len(result) < count:
                remaining()
                chunk = sock.recv(count - len(result))
                if not chunk:
                    raise ValueError("Minecraft server closed status connection")
                result.extend(chunk)
            return bytes(result)

        def packet():
            size = read_varint(receive)
            if size > MAX_STATUS + 16:
                raise ValueError("Oversized Minecraft packet")
            return receive(size)

        hostname = b"localhost"
        hello = b"\x00" + encode_varint(-1) + encode_varint(len(hostname)) + hostname + struct.pack(">H", GAME_PORT) + b"\x01"
        remaining()
        sock.sendall(encode_varint(len(hello)) + hello + b"\x01\x00")
        status = decode_status(packet())
        nonce = nonce_factory(8)
        remaining()
        sock.sendall(b"\x09\x01" + nonce)
        if packet() != b"\x01" + nonce:
            raise ValueError("Minecraft status ping did not match")
        return status


def wait_for_game(ssh, timeout=45.0, probe=minecraft_status,
                  clock=time.monotonic, sleep=time.sleep) -> dict:
    deadline = clock() + timeout
    while clock() < deadline:
        if ssh.poll() is not None:
            raise ssh.failure()
        # A live SSH process can still be handshaking. Do not probe a different
        # Minecraft process that won the local port after require_free_port().
        if not ssh.forwarding_ready():
            sleep(min(0.1, max(0, deadline - clock())))
            continue
        try:
            status = probe(timeout=min(2.0, deadline - clock()))
        except (OSError, ValueError, UnicodeError):
            sleep(min(0.4, max(0, deadline - clock())))
            continue
        # The tunnel must still be alive after the completed status-and-ping.
        if ssh.poll() is not None:
            raise ssh.failure()
        return status
    raise ConnectionFailure("The SSH tunnel did not establish a verified Minecraft status-and-ping connection within 45 seconds. Check OpenSSH and Paper on Daytona; no restart was attempted.")


def monitor_game(ssh, probe=minecraft_status, clock=time.monotonic, sleep=time.sleep):
    failures = 0
    next_check = clock() + 10
    while True:
        if ssh.poll() is not None:
            raise ssh.failure()
        if clock() >= next_check:
            try:
                probe(timeout=2.0)
                failures = 0
            except (OSError, ValueError, UnicodeError):
                failures += 1
                if failures >= 3:
                    raise ConnectionFailure("Minecraft stopped responding through the tunnel. The local connection is closing; the Daytona server was not changed.")
            next_check = clock() + 10
        sleep(0.5)


def run_connection(settings: dict, check_only=False):
    executable = require_ssh()
    require_free_port()
    if check_only:
        print("Local credentials, OpenSSH, and port checks passed. No Daytona request or game connection was made.")
        return
    access = DaytonaAccess(settings)
    token = None
    ssh = None
    try:
        print("Checking the existing Daytona sandbox; no server deployment or restart will be performed.")
        access.require_running()
        token = access.create_token()
        ssh = OwnedSshProcess(ssh_command(executable, token))
        print("Checking the game through the secure localhost tunnel...")
        status = wait_for_game(ssh)
        print("\nREADY: the existing Daytona Minecraft server answered the status and ping checks.")
        print("Server version: " + status["version"])
        print("Open the matching Minecraft Java Edition client, then Multiplayer > Direct Connection.")
        print("Server address: 127.0.0.1:25565")
        print("Keep this window open while playing. Press Ctrl+C to disconnect this tunnel.")
        monitor_game(ssh)
    finally:
        try:
            if ssh is not None:
                ssh.close()
        finally:
            if token is not None:
                try:
                    access.revoke_token(token)
                except ConnectionFailure:
                    print("The local tunnel closed, but revocation of this session token could not be confirmed. Its Daytona expiration still applies.")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check local prerequisites without contacting Daytona")
    args = parser.parse_args(argv)
    try:
        if sys.version_info < (3, 10):
            raise ConnectionFailure("Python 3.10 or newer is required for this connector.")
        run_connection(load_settings(), check_only=args.check)
        return 0
    except KeyboardInterrupt:
        print("\nDisconnected this laptop tunnel. The Daytona game server was left running.")
        return 0
    except ConnectionFailure as exc:
        print("Connection stopped: " + str(exc), file=sys.stderr)
        return 1
    except Exception:
        # A traceback may contain URLs or command arguments with credentials.
        print("Connection stopped because of an unexpected local error. No credentials or raw diagnostics were printed.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
