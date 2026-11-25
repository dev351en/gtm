#!/usr/bin/env python3
"""Publish an immutable, verified repair candidate with GitHub Actions' token.

The workflow invokes this only for an explicit [publish-repair] commit after its
build/check job succeeds. It never contacts or restarts a game server.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile

from package_repair_candidate import ASSETS, JAVA_NAME
from publish_functional_runtime import PublicationError, api, gh

TAG = "gtm-repair-1.0.4-20261125"


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_assets(folder: Path, repo: str) -> dict:
    if any(not (folder / name).is_file() or (folder / name).is_symlink() for name in ASSETS):
        raise PublicationError("The complete verified repair release is required")
    sums = {}
    for line in (folder / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        if not re.fullmatch(r"[0-9a-f]{64}  [A-Za-z0-9_.-]+", line):
            raise PublicationError("Invalid release checksum line")
        digest, name = line.split("  ", 1)
        if name in sums or name not in ASSETS - {"SHA256SUMS"}:
            raise PublicationError("Duplicate or unexpected release checksum")
        sums[name] = digest
    if set(sums) != ASSETS - {"SHA256SUMS"}:
        raise PublicationError("Release checksums are incomplete")
    hashes = {name: hash_file(folder / name) for name in ASSETS}
    if any(hashes[name] != expected for name, expected in sums.items()):
        raise PublicationError("Release bytes changed after packaging")
    report = json.loads((folder / "release-report.json").read_text())
    url = f"https://github.com/{repo}/releases/download/{TAG}/{JAVA_NAME}"
    if report.get("status") != "PASS" or report.get("pack_url") != url:
        raise PublicationError("Repair pack URL does not point to this exact release")
    return hashes


def find_release(repo: str):
    matches = []
    for page in range(1, 21):
        rows = api(f"repos/{repo}/releases?per_page=100&page={page}")
        if (not isinstance(rows, list) or len(rows) > 100
                or any(not isinstance(row, dict) for row in rows)):
            raise PublicationError("Unexpected release metadata")
        matches.extend(row for row in rows if row.get("tag_name") == TAG)
        if len(matches) > 1: raise PublicationError("Ambiguous release tag; no release changed")
        if len(rows) < 100:
            return read_release(repo, matches[0].get("id")) if matches else None
    raise PublicationError("Release lookup exceeded its bounded page limit")


def read_release(repo: str, release_id: int) -> dict:
    if type(release_id) is not int or release_id <= 0:
        raise PublicationError("GitHub returned an invalid repair release ID")
    result = api(f"repos/{repo}/releases/{release_id}")
    if (not isinstance(result, dict) or result.get("id") != release_id
            or result.get("tag_name") != TAG or type(result.get("draft")) is not bool):
        raise PublicationError("GitHub returned a different repair release identity")
    return result


def require_tag_target(repo: str, commit: str, *, required: bool = False) -> None:
    reference = api(f"repos/{repo}/git/ref/tags/{TAG}", allow_missing=True)
    if reference is None:
        if required:
            raise PublicationError("Published repair tag is missing; its source commit is unconfirmed")
        return
    if not isinstance(reference, dict):
        raise PublicationError("GitHub returned an invalid repair tag")
    target = reference.get("object", {})
    # An annotated tag names a tag object, not its final commit. Resolve a
    # bounded chain and reject unexpected object types without moving any ref.
    for _ in range(4):
        if not isinstance(target, dict) or target.get("type") != "tag":
            break
        sha = target.get("sha", "")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise PublicationError("GitHub returned an invalid annotated repair tag")
        annotated = api(f"repos/{repo}/git/tags/{sha}")
        if not isinstance(annotated, dict):
            raise PublicationError("GitHub returned an invalid annotated repair tag")
        target = annotated.get("object", {})
    if (not isinstance(target, dict) or target.get("type") != "commit"
            or target.get("sha") != commit):
        raise PublicationError("Existing repair tag points elsewhere; it was not moved")


def names(release: dict) -> set:
    rows = release.get("assets", [])
    if (not isinstance(rows, list)
            or any(not isinstance(row, dict) or not isinstance(row.get("name"), str) for row in rows)):
        raise PublicationError("Unexpected repair release asset metadata")
    result = [row.get("name") for row in rows]
    if len(result) != len(set(result)) or not set(result).issubset(ASSETS):
        raise PublicationError("Release contains unexpected or duplicate assets")
    return set(result)


def verify_remote(repo: str, release: dict, expected: dict) -> None:
    selected = names(release)
    if not selected: return
    with tempfile.TemporaryDirectory(prefix="gtm-repair-readback-") as folder:
        gh(["release", "download", TAG, "--repo", repo, "--dir", folder, "--pattern", "*"],
           stage="Verify uploaded repair assets")
        found = {p.name for p in Path(folder).iterdir() if p.is_file()}
        if found != selected or any(hash_file(Path(folder) / name) != expected[name] for name in found):
            raise PublicationError("Existing release assets differ; nothing was overwritten")


def publish(folder: Path, repo: str, commit: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise PublicationError("An explicit repository and full commit SHA are required")
    expected = local_assets(folder, repo)
    release = find_release(repo)
    # Identical asset bytes do not establish source provenance. Check the ref
    # even on the idempotent already-published path before reporting success.
    require_tag_target(repo, commit, required=release is not None and release.get("draft") is False)
    if release and not release.get("draft"):
        if release.get("prerelease") is not True or names(release) != ASSETS:
            raise PublicationError("The existing public release is different or incomplete")
        verify_remote(repo, release, expected)
        print("Identical verified candidate already published: " + release["html_url"])
        return
    if release is None:
        notes = Path(__file__).resolve().parents[1] / "packaging/repair/RELEASE_NOTES.md"
        if not notes.is_file(): raise PublicationError("Reviewed release notes are required")
        gh(["release", "create", TAG, "--repo", repo, "--target", commit,
            "--draft", "--prerelease", "--latest=false", "--title", "GTM 1.0.4 runtime repair candidate",
            "--notes-file", str(notes)], stage="Create repair candidate draft")
        release = find_release(repo)
    if not release or not release.get("draft") or release.get("target_commitish") != commit:
        raise PublicationError("Draft release does not match this exact source commit")
    verify_remote(repo, release, expected)
    missing = ASSETS - names(release)
    if missing:
        gh(["release", "upload", TAG, "--repo", repo, *(str(folder / name) for name in sorted(missing))],
           stage="Upload verified repair candidate")
    confirmed = read_release(repo, release["id"])
    if confirmed.get("draft") is not True or confirmed.get("target_commitish") != commit:
        raise PublicationError("Repair draft changed before publication; no publication was attempted")
    if names(confirmed) != ASSETS: raise PublicationError("Repair upload is incomplete; draft retained")
    verify_remote(repo, confirmed, expected)
    require_tag_target(repo, commit)
    gh(["release", "edit", TAG, "--repo", repo, "--draft=false", "--prerelease", "--latest=false"],
       stage="Publish verified repair candidate")
    confirmed = read_release(repo, release["id"])
    if confirmed.get("draft") or not confirmed.get("prerelease") or names(confirmed) != ASSETS:
        raise PublicationError("Final publication state is unconfirmed")
    require_tag_target(repo, commit, required=True)
    print("Published verified repair candidate: " + confirmed["html_url"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    try: publish(args.directory, args.repo, args.commit); return 0
    except (OSError, ValueError, RuntimeError) as failure:
        print("Repair publication stopped: " + str(failure), file=sys.stderr); return 1


if __name__ == "__main__": sys.exit(main())
