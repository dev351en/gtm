#!/usr/bin/env python3
"""Publish the verified candidate via gh; never overwrite a release asset or tag.

The offline assembler is a separate tool. This helper is invoked only by the
authorized GitHub publication job, with its short-lived GITHUB_TOKEN supplied
to gh through GH_TOKEN. No Daytona or private server endpoint is contacted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from assemble_functional_runtime import UPDATE_NAME, JAVA_NAME, BEDROCK_NAME, ART_NAME, CONNECTOR_NAME, sha256

TAG = "gtm-functional-r4-1.0.3"
ASSET_NAMES = {UPDATE_NAME, JAVA_NAME, BEDROCK_NAME, ART_NAME, CONNECTOR_NAME, "assembly-report.json", "SHA256SUMS"}
NOTES = """# GTM functional runtime 1.0.3 candidate

Download **GTM_Daytona_Laptop_Connector.zip** to connect your laptop to the same
existing running Daytona sandbox. Extract it, read the included connection
guide, and run Start-Daytona.bat. It requires Python 3.10+, Windows OpenSSH,
and your existing locally stored Daytona credential. No credentials are included.
This connector does not deploy the new runtime or restart the server.

The runtime update ZIP contains the preserved functional core, exact Java and
Bedrock packs, optional bridge with corresponding source/license, launcher files,
and verification evidence. It is **not a complete Paper server or private-world
installer**. The separate art ZIP preserves the native128 asset sources.

The latest core/launcher source checkout was not recovered; older repository
source does not rebuild these binaries. Native Windows, native Java/Bedrock
client rendering, and live Daytona deployment remain unverified. The full city
and campaign are incomplete. See the runtime manifest and included evidence.

Every downloadable asset is hashed in SHA256SUMS. The assembler reconstructs
split repository files offline and verifies each part plus the complete file.
The published tag and asset names are never silently replaced on a rerun.
"""


class PublicationError(RuntimeError):
    pass


def gh(args, allow_missing=False, runner=subprocess.run):
    result = runner(["gh", *args], text=True, capture_output=True, timeout=300)
    if result.returncode:
        if allow_missing and "HTTP 404" in result.stderr:
            return None
        raise PublicationError("GitHub CLI operation failed. No write was automatically retried; inspect the workflow before rerunning.")
    return result.stdout


def api(path, allow_missing=False):
    data = gh(["api", path], allow_missing=allow_missing)
    return None if data is None else json.loads(data)


def verify_local(directory: Path) -> dict:
    expected = {name: directory / name for name in ASSET_NAMES}
    if any(not path.is_file() or path.is_symlink() for path in expected.values()):
        raise PublicationError("The complete assembled asset set is required")
    entries = {}
    for line in expected["SHA256SUMS"].read_text(encoding="ascii").splitlines():
        if not re.fullmatch(r"[0-9a-f]{64}  [A-Za-z0-9_.-]+", line):
            raise PublicationError("Malformed SHA256SUMS")
        digest, name = line.split("  ", 1)
        if name not in expected or name in entries or name == "SHA256SUMS":
            raise PublicationError("Unexpected checksum entry")
        entries[name] = digest
    if set(entries) != ASSET_NAMES - {"SHA256SUMS"}:
        raise PublicationError("Checksum entries do not cover every release asset")
    hashes = {name: sha256(path) for name, path in expected.items()}
    if any(hashes[name] != digest for name, digest in entries.items()):
        raise PublicationError("An assembled asset changed after verification")
    report = json.loads(expected["assembly-report.json"].read_text())
    if report.get("status") != "PASS" or report.get("server_started") is not False:
        raise PublicationError("Missing passing offline assembly report")
    return {name: {"path": path.resolve(), "sha256": hashes[name], "bytes": path.stat().st_size}
            for name, path in expected.items()}


def asset_names(release: dict) -> set:
    assets = release.get("assets")
    if not isinstance(assets, list) or any(not isinstance(row, dict) or not isinstance(row.get("name"), str) for row in assets):
        raise PublicationError("Unexpected GitHub release asset response")
    names = [row["name"] for row in assets]
    if len(set(names)) != len(names) or not set(names).issubset(ASSET_NAMES):
        raise PublicationError("Existing release has duplicate or unexpected assets; it was left unchanged")
    return set(names)


def verify_remote(repo: str, release: dict, local: dict):
    names = asset_names(release)
    if not names:
        return
    with tempfile.TemporaryDirectory(prefix="gtm-release-verify-") as folder:
        gh(["release", "download", TAG, "--repo", repo, "--dir", folder, "--pattern", "*"])
        actual = {p.name for p in Path(folder).iterdir() if p.is_file()}
        if actual != names:
            raise PublicationError("Downloaded asset set differs from the inspected release")
        for name in names:
            path = Path(folder) / name
            if path.stat().st_size != local[name]["bytes"] or sha256(path) != local[name]["sha256"]:
                raise PublicationError("Existing release asset differs: " + name + ". No asset or tag was overwritten.")


def require_tag_target(repo: str, commit: str):
    reference = api(f"repos/{repo}/git/ref/tags/{TAG}", allow_missing=True)
    if reference is None:
        return
    obj = reference.get("object", {})
    for _ in range(4):
        if obj.get("type") != "tag":
            break
        obj = api(f"repos/{repo}/git/tags/{obj['sha']}").get("object", {})
    if obj.get("type") != "commit" or obj.get("sha") != commit:
        raise PublicationError("The existing release tag points to another commit. It was not moved.")


def publish(directory: Path, repo: str, commit: str):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise PublicationError("An explicit repository and full commit SHA are required")
    local = verify_local(directory)
    endpoint = f"repos/{repo}/releases/tags/{TAG}"
    release = api(endpoint, allow_missing=True)
    if release is not None and not release.get("draft"):
        if release.get("prerelease") is not True:
            raise PublicationError("The existing public release is not marked as a candidate; it was left unchanged")
        if asset_names(release) != ASSET_NAMES:
            raise PublicationError("The published release is incomplete or different; no public assets were changed")
        verify_remote(repo, release, local)
        print("Existing published candidate has identical verified assets; it was left unchanged.")
        return
    require_tag_target(repo, commit)
    if release is None:
        with tempfile.TemporaryDirectory(prefix="gtm-release-notes-") as folder:
            notes = Path(folder) / "notes.md"
            notes.write_text(NOTES, encoding="utf-8")
            gh(["release", "create", TAG, "--repo", repo, "--target", commit,
                "--draft", "--prerelease", "--latest=false",
                "--title", "GTM functional runtime 1.0.3 candidate",
                "--notes-file", str(notes)])
        release = api(endpoint)
    elif release.get("target_commitish") != commit:
        raise PublicationError("The existing draft targets another commit; it was left unchanged")
    # A resumed draft can be completed only after all of its existing bytes match.
    verify_remote(repo, release, local)
    missing = ASSET_NAMES - asset_names(release)
    if missing:
        gh(["release", "upload", TAG, "--repo", repo,
            *(str(local[name]["path"]) for name in sorted(missing))])
    release = api(endpoint)
    if asset_names(release) != ASSET_NAMES:
        raise PublicationError("Draft upload is incomplete; publication was not attempted")
    verify_remote(repo, release, local)
    gh(["release", "edit", TAG, "--repo", repo, "--draft=false", "--prerelease", "--latest=false"])
    confirmed = api(endpoint)
    if confirmed.get("draft") or not confirmed.get("prerelease") or asset_names(confirmed) != ASSET_NAMES:
        raise PublicationError("The final release state could not be confirmed; no write was retried")
    print("Published the verified functional candidate: " + str(confirmed.get("html_url", TAG)))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args(argv)
    try:
        publish(args.directory, args.repo, args.commit)
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print("Candidate publication stopped: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
