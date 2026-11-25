#!/usr/bin/env python3
"""Fetch explicitly pinned laptop inputs. Never contacts or changes Daytona.

Only HTTPS URLs in the reviewed lock are accepted. Existing cache files are
rechecked; mismatched files are never silently used or overwritten.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

REPO = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = REPO / "packaging/dependencies.lock.json"
USER_AGENT = "GTM-private-laptop-builder/1.0 (owner initiated; no deployment)"


def digest(path: Path, algorithm: str = "sha256") -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def validate_entry(entry: dict) -> None:
    name = entry.get("filename", "")
    if not name or Path(name).name != name or "/" in name or "\\" in name or ":" in name:
        raise ValueError("Dependency filename must be one plain filename")
    if type(entry.get("bytes")) is not int or entry["bytes"] <= 0:
        raise ValueError("Dependency requires an exact positive byte count")
    checksums = entry.get("checksums", {})
    if not any(k in checksums for k in ("sha256", "sha512")):
        raise ValueError("Dependency requires SHA-256 or SHA-512 from its source")
    for algorithm, value in checksums.items():
        if algorithm not in ("sha256", "sha512") or len(value) != hashlib.new(algorithm).digest_size * 2:
            raise ValueError("Invalid locked checksum")
        if any(c not in "0123456789abcdef" for c in value.lower()):
            raise ValueError("Invalid checksum characters")


def verify(path: Path, entry: dict) -> Path:
    validate_entry(entry)
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Missing regular dependency: {path.name}")
    with path.open("rb") as stream:
        if stream.read(80).startswith(b"version https://git-lfs.github.com/spec/v1"):
            raise ValueError(f"Unresolved Git LFS pointer: {path.name}")
    if path.stat().st_size != entry["bytes"]:
        raise ValueError(f"Byte-count mismatch: {path.name}")
    for algorithm, expected in entry["checksums"].items():
        if digest(path, algorithm) != expected.lower():
            raise ValueError(f"{algorithm.upper()} mismatch: {path.name}")
    return path


def checked_url(url: str, allowed_hosts: set[str]) -> str:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.fragment:
        raise ValueError("Only credential-free HTTPS dependency URLs are allowed")
    if parsed.hostname not in allowed_hosts or parsed.port not in (None, 443):
        raise ValueError("Dependency URL or redirect is outside its locked hosts")
    return url


class LockedRedirects(HTTPRedirectHandler):
    def __init__(self, hosts: set[str]):
        self.hosts = hosts

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return super().redirect_request(req, fp, code, msg, headers, checked_url(newurl, self.hosts))


def fetch(entry: dict, cache: Path, repo: Path = REPO) -> Path:
    validate_entry(entry)
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / entry["filename"]
    if dest.exists():
        return verify(dest, entry)
    if shutil.disk_usage(cache).free < entry["bytes"] + 128 * 1024 * 1024:
        raise ValueError("Insufficient free space for the pinned download")
    tmp = cache / (entry["filename"] + ".part-" + str(os.getpid()))
    try:
        with tmp.open("xb") as out:
            if "repository_path" in entry:
                source = (repo / entry["repository_path"]).resolve(strict=True)
                if not source.is_relative_to(repo.resolve()):
                    raise ValueError("Repository dependency escaped repository root")
                verify(source, entry)
                with source.open("rb") as stream:
                    shutil.copyfileobj(stream, out, 1024 * 1024)
            else:
                hosts = set(entry.get("allowed_hosts", []))
                url = checked_url(entry["url"], hosts)
                request = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
                with build_opener(LockedRedirects(hosts)).open(request, timeout=30) as stream:
                    checked_url(stream.url, hosts)
                    total = 0
                    while chunk := stream.read(1024 * 1024):
                        total += len(chunk)
                        if total > entry["bytes"]:
                            raise ValueError("Dependency response exceeds locked byte count")
                        out.write(chunk)
            out.flush()
            os.fsync(out.fileno())
        verify(tmp, entry)
        # Never replace a cache file another process created in the meantime.
        if dest.exists():
            verify(dest, entry)
        else:
            tmp.rename(dest)
        return dest
    finally:
        tmp.unlink(missing_ok=True)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    p.add_argument("--cache", type=Path, required=True)
    p.add_argument("--ids", nargs="+", required=True, help="Explicit keys from the dependency lock")
    args = p.parse_args(argv)
    try:
        lock = json.loads(args.lock.read_text(encoding="utf-8"))
        for key in args.ids:
            if key not in lock["items"]:
                raise ValueError(f"Unknown dependency ID: {key}")
            result = fetch(lock["items"][key], args.cache)
            print(json.dumps({"id": key, "path": str(result.resolve()), "sha256": digest(result), "verified": True}), flush=True)
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"Dependency bootstrap stopped: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
