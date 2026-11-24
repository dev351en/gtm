"""Rehearse a GTM plugin deployment and rollback on a new private copy of a stopped server.

The input tree is only read. No service is started and no network calls are made.
"""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import stat
import tempfile
from zipfile import ZipFile

PLUGIN = Path("plugins/SDCraftCore-1.0.0.jar")


def digest(path):
    with path.open("rb") as src:
        return hashlib.file_digest(src, "sha256").hexdigest()


def manifest(root):
    result = {}
    for base, dirs, files in os.walk(root):
        for name in dirs + files:
            path = Path(base)/name
            mode = path.lstat().st_mode
            if stat.S_ISDIR(mode):
                continue
            if not stat.S_ISREG(mode):
                raise ValueError("Special files and symlinks require manual backup handling")
            result[path.relative_to(root)] = digest(path)
    return result


def rehearse(source, candidate, dest):
    source, candidate, dest = source.resolve(strict=True), candidate.resolve(strict=True), dest.resolve()
    if dest == source or dest.is_relative_to(source) or dest.exists():
        raise ValueError("Destination must be a new directory outside the server")
    if not (source/PLUGIN).is_file() or not (source/"server.properties").is_file():
        raise ValueError("Expected a server with an installed SDCraftCore plugin")
    with ZipFile(candidate) as jar:
        if jar.testzip() or "com/sdcraft/core/SDCraftCorePlugin.class" not in jar.namelist() or "plugin.yml" not in jar.namelist():
            raise ValueError("Invalid SDCraftCore JAR")
    candidate_hash = digest(candidate)
    original = manifest(source)
    # One private rollback snapshot plus one independent staging copy.
    dest.mkdir(mode=0o700)
    try:
        with tempfile.TemporaryDirectory(dir=dest) as tmp:
            work = Path(tmp)
            backup, stage = work/"rollback", work/"staging"
            shutil.copytree(source, backup, symlinks=True)
            if manifest(backup) != original or manifest(source) != original:
                raise ValueError("Server changed while snapshotting")
            shutil.copytree(backup, stage)
            shutil.copy2(candidate,stage/PLUGIN)
            expected = dict(original)
            expected[PLUGIN] = candidate_hash
            if manifest(stage) != expected:
                raise ValueError("Staging candidate verification failed")
            shutil.copy2(backup/PLUGIN,stage/PLUGIN)
            if manifest(stage) != original:
                raise ValueError("Rollback rehearsal failed")
            shutil.copy2(candidate,stage/PLUGIN)
            if manifest(stage) != expected or manifest(source) != original:
                raise ValueError("Staging readback failed")
            backup.rename(dest/"rollback")
            stage.rename(dest/"staging")
    except BaseException:
        # Remove only the newly created rehearsal directory.
        shutil.rmtree(dest)
        raise
    print(f"Verified backup, candidate and rollback for {len(original)} files. Staging is stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stopped_server",type=Path)
    parser.add_argument("candidate_jar",type=Path)
    parser.add_argument("new_directory",type=Path)
    args = parser.parse_args()
    rehearse(args.stopped_server,args.candidate_jar,args.new_directory)
