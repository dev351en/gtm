"""Destructive-edge regression tests for the stopped-server repair transaction."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import install_runtime_repair as repair

ROOT = Path(__file__).resolve().parents[1]
CORE = "plugins/SDCraftCore-1.0.4-r4-repair.jar"
OLD_CORE = "plugins/SDCraftCore-1.0.3-r4-functional-candidate.jar"


def archive(entries):
    output = io.BytesIO()
    with ZipFile(output, "w") as handle:
        for name, value in entries.items():
            handle.writestr(name, value)
    return output.getvalue()


def put(root, name, data):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def free_port():
    with socket.socket() as handle:
        handle.bind(("127.0.0.1", 0))
        return handle.getsockname()[1]


def snapshot(server):
    return {path.relative_to(server).as_posix(): path.read_bytes()
            for path in server.rglob("*") if path.is_file()
            and repair.BACKUPS not in path.relative_to(server).parts
            and path.name != ".gtm-repair.lock"}


class RepairTransactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = (ROOT / "runtime/functional-r4" / OLD_CORE).read_bytes()
        if repair.digest(cls.base) != repair.BASE_CORE:
            raise RuntimeError("Preserved integration-test core has changed")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.server, self.payload = self.root / "server", self.root / "payload"
        self.server.mkdir()
        self.payload.mkdir()
        self.files = {
            CORE: archive({"plugin.yml": "name: SDCraftCore\nversion: 1.0.4-r4-repair\n", "marker": "new-runtime"}),
            repair.JAVA_PACK: archive({"pack.mcmeta": '{"pack":{"pack_format":80,"description":"repair-test"}}'}),
            repair.BEDROCK_PACK: archive({"manifest.json": '{"test":"new-bedrock"}'}),
            repair.MAPPINGS: b'{"format_version":2,"items":{}}\n',
            "Open-Control-Centre.bat": b"@echo off\r\n",
            "tools/open_control_centre.py": b"# verified local opener\n",
        }
        for name, data in self.files.items():
            put(self.payload, name, data)
        self.manifest = {
            "schema": "GTM_RUNTIME_REPAIR_V1", "version": "1.0.4-r4-repair",
            "base_core_sha256": repair.BASE_CORE, "base_bedrock_sha256": repair.BASE_BEDROCK,
            "files": [{"path": name, "sha256": repair.digest(data), "bytes": len(data),
                       "optional_bedrock": name in {repair.BEDROCK_PACK, repair.MAPPINGS}}
                      for name, data in self.files.items()],
            "java_pack": {"path": repair.JAVA_PACK,
                          "sha1": hashlib.sha1(self.files[repair.JAVA_PACK]).hexdigest(),
                          "id": "9d799a4b-4a9c-5fec-ab81-8e41b444667f",
                          "url": "https://example.invalid/pinned-version/GTM.zip"},
        }
        self.write_manifest()
        put(self.server, OLD_CORE, self.base)
        put(self.server, "plugins/TrustedOther.jar", archive({"plugin.yml": "name: TrustedOther\n"}))
        put(self.server, "server.properties", (
            "# Keep this profile\r\nserver-port=" + str(free_port()) +
            "\r\nlevel-name=world\r\nonline-mode=false\r\nenable-rcon=false\r\n"
            "resource-pack=https://example.invalid/old.zip\r\nresource-pack-sha1=" + "a" * 40 +
            "\r\nmotd=Indraprastha · unchanged\r\n").encode())
        for name, data in {
            "world/level.dat": b"actual-world-sentinel\0\1",
            "world/region/r.0.0.mca": b"region-sentinel\0\2",
            "world/session.lock": b"\xe2\x98\x83",
            "world_nether/level.dat": b"nether-sentinel",
            "world_nether/session.lock": b"\xe2\x98\x83",
            "plugins/SDCraftCore/config.yml": b"experimental:\n  dialogue: false\nprivate-setting: keep\n",
            "plugins/SDCraftCore/accounts.db": b"registered-account-sentinel",
            "plugins/SDCraftCore/vehicles.yml": b"owned-vehicles-sentinel",
            "plugins/AuthMe/authme.db": b"password-hash-sentinel",
            "permissions.yml": b"custom-permissions-sentinel",
            "resourcepacks/OldJava.zip": b"keep-unrelated-old-download",
        }.items():
            put(self.server, name, data)
        self.before = snapshot(self.server)

    def write_manifest(self):
        (self.payload / "repair-manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def installed(self, bedrock=False):
        return repair.apply(self.payload, self.server, bedrock)

    def assert_preserved(self, before=None):
        before = before or self.before
        for name, data in before.items():
            if name not in {OLD_CORE, "server.properties", "launcher/launcher.properties", "launcher/integrity.sha256"}:
                self.assertEqual((self.server / name).read_bytes(), data, name)

    def test_apply_preserves_world_accounts_flags_and_unrelated_plugins(self):
        result = self.installed()
        self.assertEqual(result["status"], "installed")
        self.assertEqual((self.server / CORE).read_bytes(), self.files[CORE])
        self.assertFalse((self.server / OLD_CORE).exists())
        self.assertFalse((self.server / repair.BEDROCK_PACK).exists())
        self.assert_preserved()
        original = repair.properties(self.before["server.properties"])
        updated = repair.properties((self.server / "server.properties").read_bytes())
        for key, value in original.items():
            if key not in {"resource-pack", "resource-pack-sha1", "resource-pack-id"}:
                self.assertEqual(updated[key], value)
        self.assertEqual(updated["resource-pack-sha1"], self.manifest["java_pack"]["sha1"])
        backup = self.server / repair.BACKUPS / result["backup"]
        receipt = json.loads((backup / repair.RECEIPT).read_text())
        self.assertEqual(receipt["status"], "committed")
        self.assertEqual((backup / "files" / OLD_CORE).read_bytes(), self.base)

    def test_repeat_is_idempotent(self):
        self.installed()
        before = snapshot(self.server)
        backups = list((self.server / repair.BACKUPS).iterdir())
        self.assertEqual(self.installed()["status"], "already_installed")
        self.assertEqual(snapshot(self.server), before)
        self.assertEqual(list((self.server / repair.BACKUPS).iterdir()), backups)

    def test_explicit_rollback_restores_exact_original_files(self):
        result = self.installed()
        self.assertEqual(repair.rollback(self.server, result["backup"])["status"], "rolled_back")
        self.assertEqual(snapshot(self.server), self.before)
        self.assertEqual(repair.rollback(self.server, result["backup"])["status"], "already_rolled_back")

    def test_failure_mid_commit_automatically_restores_every_file(self):
        original = repair.commit_change
        calls = []
        def fail(server, backup, row):
            calls.append(row["path"])
            if len(calls) == 3:
                raise OSError("simulated disk replacement failure")
            return original(server, backup, row)
        with patch.object(repair, "commit_change", side_effect=fail), self.assertRaisesRegex(repair.RepairError, "original files were restored"):
            self.installed()
        self.assertEqual(snapshot(self.server), self.before)
        receipt = next((self.server / repair.BACKUPS).glob("*/" + repair.RECEIPT))
        self.assertEqual(json.loads(receipt.read_text())["status"], "rolled_back")

    def test_corrupt_payload_stops_before_touching_server(self):
        (self.payload / CORE).write_bytes(b"bad")
        with self.assertRaisesRegex(repair.RepairError, "mismatch"):
            self.installed()
        self.assertEqual(snapshot(self.server), self.before)
        self.assertFalse((self.server / repair.BACKUPS).exists())

    def test_receipt_recovers_interrupted_transaction(self):
        class AbruptInterruption(BaseException):
            pass
        original = repair.commit_change
        calls = []
        def interrupt(server, backup, row):
            calls.append(row["path"])
            if len(calls) == 3:
                raise AbruptInterruption()
            return original(server, backup, row)
        with patch.object(repair, "commit_change", side_effect=interrupt), self.assertRaises(AbruptInterruption):
            self.installed()
        directory = next((self.server / repair.BACKUPS).iterdir())
        self.assertEqual(json.loads((directory / repair.RECEIPT).read_text())["status"], "prepared")
        with self.assertRaisesRegex(repair.RepairError, "Unfinished repair"):
            self.installed()
        repair.rollback(self.server, directory.name)
        self.assertEqual(snapshot(self.server), self.before)

    def test_incorrect_sha1_stops_before_touching_server(self):
        self.manifest["java_pack"]["sha1"] = "0" * 40
        self.write_manifest()
        with self.assertRaisesRegex(repair.RepairError, "SHA-1 mismatch"):
            self.installed()
        self.assertEqual(snapshot(self.server), self.before)

    def test_manifest_cannot_escape_or_replace_world_or_accounts(self):
        for name in ("../outside", "/tmp/outside", "plugins/../world/level.dat", "world/level.dat", "plugins/SDCraftCore/accounts.db", "C:\\server\\plugins\\evil.jar", "plugins/NUL.jar"):
            with self.subTest(name=name):
                self.manifest["files"][0]["path"] = name
                self.write_manifest()
                with self.assertRaises(repair.RepairError):
                    self.installed()
                self.assertEqual(snapshot(self.server), self.before)

    def test_unknown_or_duplicate_unknown_core_refused(self):
        put(self.server, "plugins/renamed-other-core.jar", archive({"plugin.yml": "name: 'SDCraftCore'\n", "unknown": "not-reviewed"}))
        before = snapshot(self.server)
        with self.assertRaisesRegex(repair.RepairError, "Unsupported or unrecognized"):
            self.installed()
        self.assertEqual(snapshot(self.server), before)

    def test_duplicate_known_old_core_removed_and_restored(self):
        put(self.server, "plugins/renamed-copy.jar", self.base)
        before = snapshot(self.server)
        result = self.installed()
        self.assertFalse((self.server / "plugins/renamed-copy.jar").exists())
        self.assertEqual(repair.core_files(self.server), [(CORE, repair.digest(self.files[CORE]))])
        repair.rollback(self.server, result["backup"])
        self.assertEqual(snapshot(self.server), before)

    def test_running_loopback_port_refused(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen()
            file = self.server / "server.properties"
            file.write_bytes(repair.update_properties(file.read_bytes(), {"server-port": str(listener.getsockname()[1])}))
            before = snapshot(self.server)
            with self.assertRaisesRegex(repair.RepairError, "running on loopback"):
                self.installed()
            self.assertEqual(snapshot(self.server), before)

    @unittest.skipUnless(os.name == "posix", "POSIX cross-process Java-compatible lock test")
    def test_real_world_session_lock_refused(self):
        code = "import fcntl,sys; f=open(sys.argv[1], 'r+b'); fcntl.lockf(f, fcntl.LOCK_EX); print('ready', flush=True); sys.stdin.read()"
        child = subprocess.Popen([sys.executable, "-c", code, str(self.server / "world/session.lock")], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(), "ready")
            with self.assertRaisesRegex(repair.RepairError, "lock held"):
                self.installed()
            self.assertEqual(snapshot(self.server), self.before)
        finally:
            child.communicate("stop", timeout=5)

    def test_missing_sanitized_world_lock_can_be_updated(self):
        (self.server / "world/session.lock").unlink()
        before = snapshot(self.server)
        result = self.installed()
        repair.rollback(self.server, result["backup"])
        self.assertEqual(snapshot(self.server), before)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_payload_refused(self):
        outside = put(self.root, "outside-core.jar", self.files[CORE])
        path = self.payload / CORE
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaisesRegex(repair.RepairError, "Symlink"):
            self.installed()
        self.assertEqual(snapshot(self.server), self.before)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_destination_directory_refused(self):
        outside = self.root / "outside"
        outside.mkdir()
        shutil.rmtree(self.server / "resourcepacks")
        (self.server / "resourcepacks").symlink_to(outside, target_is_directory=True)
        before = snapshot(self.server)
        with self.assertRaisesRegex(repair.RepairError, "Symlink"):
            self.installed()
        self.assertEqual(snapshot(self.server), before)
        self.assertEqual(list(outside.iterdir()), [])

    def test_rollback_refuses_newer_user_edits(self):
        result = self.installed()
        file = self.server / "server.properties"
        file.write_bytes(file.read_bytes() + b"# User edit after installation\n")
        before = snapshot(self.server)
        with self.assertRaisesRegex(repair.RepairError, "changed since repair"):
            repair.rollback(self.server, result["backup"])
        self.assertEqual(snapshot(self.server), before)

    def test_corrupt_backup_refused_before_restoring_anything(self):
        result = self.installed()
        original = self.server / repair.BACKUPS / result["backup"] / "files" / OLD_CORE
        original.write_bytes(b"damaged backup")
        before = snapshot(self.server)
        with self.assertRaisesRegex(repair.RepairError, "Backup checksum mismatch"):
            repair.rollback(self.server, result["backup"])
        self.assertEqual(snapshot(self.server), before)

    def test_optional_bedrock_removes_only_fingerprinted_old_pack(self):
        old = b"known base bedrock fixture"
        old_path = "plugins/Geyser-Spigot/packs/GTM_128_Original.mcpack"
        other_path = "plugins/Geyser-Spigot/packs/unrelated.mcpack"
        put(self.server, old_path, old)
        put(self.server, other_path, b"third-party-pack")
        put(self.server, "plugins/Geyser-Spigot/config.yml", b"bedrock:\n  address: 0.0.0.0\n")
        self.manifest["base_bedrock_sha256"] = repair.digest(old)
        self.write_manifest()
        before = snapshot(self.server)
        with patch.object(repair, "BASE_BEDROCK", repair.digest(old)):
            result = self.installed(True)
        self.assertFalse((self.server / old_path).exists())
        self.assertEqual((self.server / other_path).read_bytes(), b"third-party-pack")
        self.assertEqual((self.server / repair.BEDROCK_PACK).read_bytes(), self.files[repair.BEDROCK_PACK])
        repair.rollback(self.server, result["backup"])
        self.assertEqual(snapshot(self.server), before)

    def test_bedrock_is_not_enabled_or_installed_without_opt_in(self):
        put(self.server, "plugins/Geyser-Spigot/config.yml", b"enabled: false\n")
        put(self.server, repair.MAPPINGS, b"existing mappings")
        self.installed()
        self.assertEqual((self.server / repair.MAPPINGS).read_bytes(), b"existing mappings")
        self.assertEqual((self.server / "plugins/Geyser-Spigot/config.yml").read_bytes(), b"enabled: false\n")
        self.assertFalse((self.server / repair.BEDROCK_PACK).exists())

    def test_portable_launcher_still_has_complete_valid_integrity(self):
        pack_port = free_port()
        pack_url = f"http://127.0.0.1:{pack_port}/gtm-pack.zip"
        file = self.server / "server.properties"
        file.write_bytes(repair.update_properties(file.read_bytes(), {"resource-pack": pack_url}))
        put(self.server, "launcher/launcher.properties", (
            "# Preserve launcher controls\nresource.pack=resourcepacks/OldJava.zip\n"
            "pack.file=resourcepacks/OldJava.zip\npack.sha1=" + "a" * 40 +
            "\npack.bind=127.0.0.1\npack.client.host=127.0.0.1\npack.port=" + str(pack_port) +
            "\nallow.network=false\nexpected.online.mode=false\nmax.heap=2G\nbedrock.enabled=false\n").encode())
        tracked = [OLD_CORE, "plugins/TrustedOther.jar", "resourcepacks/OldJava.zip", "launcher/launcher.properties"]
        put(self.server, "launcher/integrity.sha256", ("# Keep this header\n" + "".join(repair.sha256(self.server / name) + "  " + name + "\n" for name in tracked)).encode())
        before = snapshot(self.server)
        result = self.installed()
        cfg = repair.properties((self.server / "launcher/launcher.properties").read_bytes())
        self.assertEqual(cfg["resource.pack"], repair.JAVA_PACK)
        self.assertEqual(cfg["pack.file"], repair.JAVA_PACK)
        self.assertEqual(cfg["allow.network"], "false")
        self.assertEqual(cfg["bedrock.enabled"], "false")
        self.assertEqual(cfg["pack.sha1"], self.manifest["java_pack"]["sha1"])
        current = repair.properties((self.server / "server.properties").read_bytes())
        self.assertEqual(current["resource-pack"], pack_url)
        names = []
        for line in (self.server / "launcher/integrity.sha256").read_text().splitlines():
            if line.startswith("#"):
                continue
            expected, name = line.split("  ", 1)
            self.assertEqual(repair.sha256(self.server / name), expected, name)
            names.append(name)
        self.assertNotIn(OLD_CORE, names)
        self.assertIn(CORE, names)
        self.assertIn(repair.JAVA_PACK, names)
        self.assertEqual(self.installed()["status"], "already_installed")
        repair.rollback(self.server, result["backup"])
        self.assertEqual(snapshot(self.server), before)

    def test_properties_preserve_comments_unicode_continuations_and_crlf(self):
        original = "# café comment\r\nmotd=नमस्ते\r\nother : hello\\\r\n  world\r\nresource-pack=old\r\nresource-pack=newest\r\n".encode()
        updated = repair.update_properties(original, {"resource-pack": "https://example.invalid/new"})
        self.assertIn("# café comment\r\nmotd=नमस्ते\r\nother : hello\\\r\n  world\r\n".encode(), updated)
        self.assertEqual(updated.count(b"resource-pack="), 1)
        self.assertEqual(repair.properties(updated)["other"], "helloworld")

    @unittest.skipUnless(os.name == "posix", "POSIX shell wrapper")
    def test_shell_wrapper_with_space_paths_applies_and_rolls_back(self):
        renamed = self.root / "server with spaces"
        self.server.rename(renamed)
        self.server = renamed
        payload = self.root / "payload with spaces"
        self.payload.rename(payload)
        self.payload = payload
        shutil.copy2(ROOT / "packaging/repair/Update-GTM.sh", payload / "Update-GTM.sh")
        shutil.copy2(ROOT / "tools/install_runtime_repair.py", payload / "install_runtime_repair.py")
        arguments = ["sh", str(payload / "Update-GTM.sh"), str(self.server)]
        result = subprocess.run(arguments, capture_output=True, text=True, check=True)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "installed")
        rollback = subprocess.run(arguments + ["--rollback", report["backup"]], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(rollback.stdout)["status"], "rolled_back")
        self.assertEqual(snapshot(self.server), self.before)


if __name__ == "__main__":
    unittest.main()
