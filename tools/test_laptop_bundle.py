"""Offline safety/lifecycle fixtures for laptop packaging; not Minecraft client tests."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import urlopen, Request
from zipfile import ZipFile

import bootstrap_laptop_dependencies as deps
import build_laptop_bundle as bundle


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def jar(path, name, extra=None, depend=""):
    with ZipFile(path, "w") as z:
        z.writestr("plugin.yml", f"name: {name}\nversion: 1.0\nmain: fixture.Main\n{depend}")
        for key, value in (extra or {}).items(): z.writestr(key, value)


class InputSafety(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="gtm-package-unit-")
        self.root = Path(self.temp.name)

    def tearDown(self): self.temp.cleanup()

    def test_lfs_pointer_is_not_a_download(self):
        p = self.root / "world.zip"
        p.write_bytes(b"version https://git-lfs.github.com/spec/v1\noid sha256:abc\n")
        with self.assertRaisesRegex(ValueError, "LFS"):
            bundle.require_regular(p)

    def test_checksum_mismatch_fails_closed(self):
        p = self.root / "input.jar";p.write_bytes(b"data")
        e = {"filename": p.name, "bytes": 4, "checksums": {"sha256": "0" * 64}}
        with self.assertRaisesRegex(ValueError, "mismatch"):deps.verify(p, e)
        self.assertEqual(p.read_bytes(), b"data")

    def test_download_requires_pinned_https_host(self):
        for url in ("http://example.com/a", "https://user:secret@example.com/a", "https://unlisted.example/a"):
            with self.assertRaises(ValueError):deps.checked_url(url, {"example.com"})
        self.assertEqual(deps.checked_url("https://example.com/a", {"example.com"}), "https://example.com/a")

    def test_windows_zip_paths_are_checked(self):
        for name in ("../escape", "/absolute", "C:/drive", "folder\\evil", "folder/NUL.txt", "trailing. "):
            with self.assertRaises(ValueError):bundle.safe_zip_name(name)

    def test_zip_case_collision_rejected(self):
        p = self.root / "duplicate.zip"
        with ZipFile(p, "w") as z:z.writestr("world/A.txt", "a");z.writestr("world/a.txt", "b")
        with self.assertRaisesRegex(ValueError, "colliding"):bundle.inspect_zip(p)

    def test_hard_plugin_dependencies_parsed(self):
        p = self.root / "plugin.jar"
        jar(p, "Rail", depend="depend:\n  - BKCommonLib\n  - Vault\n")
        self.assertEqual(bundle.plugin_info(p)["depends"], ["BKCommonLib", "Vault"])

    def test_old_core_cannot_be_packaged(self):
        p = self.root / "old.jar"
        jar(p, "SDCraftCore", {"com/sdcraft/core/SDCraftCorePlugin.class": b"old"})
        with self.assertRaises(ValueError):bundle.plugin_info(p, core=True)

    def test_property_updates_preserve_identity_mode(self):
        p = self.root / "server.properties"
        p.write_text("online-mode=false\nlevel-name=oldcity\nserver-port=20000\n", encoding="utf-8")
        bundle.update_properties(p, {"server-ip": "127.0.0.1", "server-port": "25565"})
        self.assertEqual(bundle.read_properties(p)["online-mode"], "false")
        self.assertEqual(bundle.read_properties(p)["level-name"], "oldcity")

    @unittest.skipIf(os.name == "nt", "POSIX lock interop fixture; Windows uses msvcrt")
    def test_running_world_lock_refused(self):
        world = self.root / "world";world.mkdir();lock = world / "session.lock";lock.write_bytes(b"locked")
        code = "import fcntl,sys;f=open(sys.argv[1],'r+b');fcntl.lockf(f,fcntl.LOCK_EX);print('locked',flush=True);sys.stdin.readline()"
        child = subprocess.Popen([sys.executable, "-c", code, str(lock)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(), "locked")
            with self.assertRaisesRegex(ValueError, "running server"):
                with bundle.stopped_world_locks(self.root):pass
        finally:child.communicate("stop\n", timeout=5)


@unittest.skipUnless(os.environ.get("GTM_TEST_JAVAC"), "Set GTM_TEST_JAVAC to a genuine Java 25 javac for launcher fixtures")
class CompleteLauncherFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="gtm-launcher-fixture-")
        cls.root = Path(cls.temp.name)
        cls.javac = Path(os.environ["GTM_TEST_JAVAC"])
        cls.java = cls.javac.parent / ("java.exe" if os.name == "nt" else "java")
        # This tiny process is explicitly a launcher fixture, not Paper or gameplay.
        source = cls.root / "FixtureServer.java"
        source.write_text('public class FixtureServer { public static void main(String[] a) throws Exception { System.out.println("Done (0.01s)! For help, type help"); var r=new java.io.BufferedReader(new java.io.InputStreamReader(System.in)); String s; while((s=r.readLine())!=null) if(s.equals("stop")) {System.out.println("Fixture saved and stopped");break;} } }', encoding="utf-8")
        subprocess.run([str(cls.javac), "--release", "25", str(source)], check=True, capture_output=True)
        cls.paper = cls.root / "fixture-paper.jar"
        with ZipFile(cls.paper, "w") as z:
            z.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\nMain-Class: FixtureServer\n\n")
            z.write(cls.root / "FixtureServer.class", "FixtureServer.class")
        cls.core = cls.root / "core.jar"
        with ZipFile(cls.core, "w") as z:
            z.writestr("plugin.yml", "name: SDCraftCore\nversion: fixture\napi-version: '26.3'\ncommands:\n" + "".join(f"  {n}:\n    description: fixture\n" for n in ("login", "register", "logout", "changepassword", "gtmauth", "gtmassets")))
            z.writestr("config.yml", "authentication:\n  trust-floodgate: true\nai:\n  external-enabled: false\n")
            for name in bundle.CORE_CLASSES:z.writestr(name, b"fixture metadata only")
        cls.vault = cls.root / "Vault.jar";jar(cls.vault, "Vault")
        cls.pack = cls.root / "pack.zip"
        with ZipFile(cls.pack, "w") as z:z.writestr("pack.mcmeta", json.dumps({"pack": {"pack_format": 84, "description": "offline launcher fixture"}}))
        cls.world = cls.root / "world.zip"
        with ZipFile(cls.world, "w") as z:
            z.writestr("world/level.dat", b"fixture, not a playable world")
            z.writestr("world/dimensions/minecraft/overworld/region/r.0.0.mca", b"\0" * 8192)
        def entry(p):return {"filename": p.name, "bytes": p.stat().st_size, "checksums": {"sha256": deps.digest(p)}}
        cls.lock = cls.root / "fixture-lock.json"
        cls.lock.write_text(json.dumps({"items": {"paper": entry(cls.paper), "public-world": entry(cls.world)}}))
        cls.port, cls.pack_port = free_port(), free_port()
        while cls.pack_port == cls.port:cls.pack_port = free_port()
        cls.output = cls.root / "fixture-bundle"
        args = cls.arguments(cls.output)
        with patch.object(bundle, "REPO", cls.root / "fake-repo"):
            cls.report = bundle.build(args)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    @classmethod
    def arguments(cls, output):
        return argparse.Namespace(output=output, archive=None, port=cls.port, pack_port=cls.pack_port, heap="1G", lock=cls.lock,
            paper=cls.paper, candidate=cls.core, resource_pack=cls.pack, stopped_server=None, public_world=cls.world, online_mode="false",
            windows_runtime=None, plugin=[cls.vault], javac=cls.javac, bedrock_pack=None, geyser_mappings=None, minecraft_bundler=None)

    def launch(self, *args):
        return subprocess.run([str(self.java), "--add-modules", "jdk.httpserver", "-jar", "launcher/gtm-launcher.jar", *args],
            cwd=self.output, capture_output=True, text=True, timeout=15)

    def test_01_fresh_bundle_does_not_accept_eula(self):
        result = self.launch("--check")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("acceptance is still required", result.stdout)
        self.assertEqual(bundle.read_properties(self.output / "eula.txt")["eula"], "false")

    def test_02_preflight_and_integrity_failures(self):
        eula = self.output / "eula.txt";old = eula.read_bytes();eula.write_text("eula=true\n")
        try:
            self.assertEqual(self.launch("--check").returncode, 0)
            core = self.output / "plugins" / self.core.name;original=core.read_bytes()
            core.write_bytes(original + b"tampered")
            try:self.assertIn("checksum mismatch", self.launch("--check").stderr)
            finally:core.write_bytes(original)
        finally:eula.write_bytes(old)

    def test_03_authentication_mode_change_refused(self):
        props = self.output / "server.properties";old=props.read_bytes()
        try:
            bundle.update_properties(props, {"online-mode": "true"})
            self.assertIn("Authentication mode changed", self.launch("--check").stderr)
        finally:props.write_bytes(old)

    def test_04_port_conflict_refused(self):
        with socket.socket() as busy:
            busy.bind(("127.0.0.1", self.port));busy.listen()
            self.assertIn("already in use", self.launch("--check").stderr)

    def test_05_http_pack_and_clean_stop_lifecycle(self):
        eula = self.output / "eula.txt";old=eula.read_bytes();eula.write_text("eula=true\n")
        child = subprocess.Popen([str(self.java), "--add-modules", "jdk.httpserver", "-jar", "launcher/gtm-launcher.jar"],
            cwd=self.output, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        try:
            observed = []
            for _ in range(12):
                line = child.stdout.readline();observed.append(line)
                if "Paper startup completed" in line:break
                if not line:break
            self.assertTrue(any("Paper startup completed" in line for line in observed), "".join(observed))
            url = f"http://127.0.0.1:{self.pack_port}"
            with urlopen(url + "/gtm-pack.zip", timeout=5) as r:self.assertEqual(r.read(), self.pack.read_bytes())
            with self.assertRaises(HTTPError) as caught:urlopen(url + "/server.properties", timeout=5)
            self.assertEqual(caught.exception.code, 404)
            output,_ = child.communicate("stop\n", timeout=10)
            self.assertEqual(child.returncode, 0, output)
            self.assertIn("Fixture saved and stopped", output)
        finally:
            if child.poll() is None:child.kill();child.communicate(timeout=5)
            eula.write_bytes(old)

    def test_06_private_import_preserves_accounts_and_source(self):
        source = self.root / "private-source";source.mkdir()
        (source / "world/region").mkdir(parents=True)
        (source / "world/level.dat").write_bytes(b"private-world-fixture")
        (source / "world/region/r.0.0.mca").write_bytes(b"\0" * 8192)
        (source / "plugins/SDCraftCore").mkdir(parents=True)
        account = source / "plugins/SDCraftCore/accounts.yml";account.write_text("fixture-account: preserved\n")
        (source / "server.properties").write_text("online-mode=false\nlevel-name=world\n")
        (source / "eula.txt").write_text("eula=true\n")
        before = bundle.tree_manifest(source)
        target = self.root / "private-copy";args=self.arguments(target)
        args.stopped_server=source;args.public_world=None;args.online_mode=None
        report=bundle.build(args)
        self.assertEqual(bundle.tree_manifest(source), before)
        self.assertEqual((target / "plugins/SDCraftCore/accounts.yml").read_bytes(), account.read_bytes())
        self.assertEqual(bundle.read_properties(target / "server.properties")["online-mode"], "false")
        self.assertEqual(report["eula_acceptance"], "preserved_from_private_source")

    @unittest.skipIf(os.name == "nt", "POSIX-to-Java record-lock interoperability fixture")
    def test_07_launcher_rejects_manually_running_world(self):
        lock = self.output / "world/session.lock";lock.write_bytes(b"fixture-lock")
        code = "import fcntl,sys;f=open(sys.argv[1],'r+b');fcntl.lockf(f,fcntl.LOCK_EX);print('locked',flush=True);sys.stdin.readline()"
        child = subprocess.Popen([sys.executable, "-c", code, str(lock)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(), "locked")
            self.assertIn("world is locked", self.launch("--check").stderr)
        finally:
            child.communicate("stop\n", timeout=5)
            lock.unlink()

    def test_08_missing_world_cannot_generate_a_replacement(self):
        world = self.output / "world/level.dat";saved=world.read_bytes();world.unlink()
        try:
            result = self.launch("--check")
            self.assertIn("refusing to generate", result.stderr)
            self.assertFalse(world.exists())
        finally:world.write_bytes(saved)

    def test_09_archive_cannot_contain_itself(self):
        args=self.arguments(self.root / "self-archive")
        args.archive=args.output / "bundle.zip"
        with self.assertRaisesRegex(ValueError, "outside the assembled"):
            bundle.build(args)


if __name__ == "__main__":unittest.main(verbosity=2)
