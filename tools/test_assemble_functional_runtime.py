"""Offline reconstruction and publication boundaries using tiny synthetic files."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

import assemble_functional_runtime as assembly


def zipped(name, data):
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr(name, data)
    return buffer.getvalue()


def record(path, data, **extra):
    return {"path": path, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), **extra}


class AssemblyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.runtime = self.repo / assembly.RUNTIME_ROOT
        self.runtime.mkdir(parents=True)
        self.output = self.root / "release"
        self.java = zipped("pack.mcmeta", b'{"pack": {}}')
        self.bedrock = zipped("manifest.json", b'{"header": {}}')
        self.art = zipped("native128/source.txt", b"Synthetic native artwork")
        self.manifest = {"files": [self.add(assembly.JAVA_PATH, self.java),
                                    self.add(assembly.BEDROCK_PATH, self.bedrock),
                                    self.add("licenses/example.txt", b"Synthetic license"),
                                    self.add("documentation/example.md", b"Synthetic evidence"),
                                    self.add("Start-GTM.bat", b"@echo off\n")],
                         "artwork": record("creative/delivery/art.zip", self.art,
                                           source_repo_path="creative/delivery/art.zip")}
        art = self.repo / "creative/delivery/art.zip"
        art.parent.mkdir(parents=True)
        art.write_bytes(self.art)
        for name in assembly.CONNECTOR_FILES:
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("Synthetic connector fixture: " + name)
        self.save_manifest()

    def add(self, path, data):
        destination = self.runtime / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        return record(path, data)

    def save_manifest(self):
        (self.runtime / "manifest.json").write_text(json.dumps(self.manifest, sort_keys=True))

    def split(self, item, data):
        path = item["path"]
        parts = []
        for index, block in enumerate((data[:7], data[7:])):
            name = f"runtime/functional-r4/.parts/{Path(path).name}.part{index:03}"
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(block)
            parts.append(record(name, block))
        item["parts"] = parts
        source = self.repo / item.get("source_repo_path", assembly.RUNTIME_ROOT + "/" + path)
        source.unlink()

    def test_unsplit_payload_includes_docs_licenses_and_exact_standalone_assets(self):
        report = assembly.assemble(self.repo, self.output)
        self.assertEqual((self.output / assembly.JAVA_NAME).read_bytes(), self.java)
        self.assertEqual((self.output / assembly.BEDROCK_NAME).read_bytes(), self.bedrock)
        self.assertEqual((self.output / assembly.ART_NAME).read_bytes(), self.art)
        self.assertEqual(report["status"], "PASS")
        with ZipFile(self.output / assembly.UPDATE_NAME) as archive:
            prefix = assembly.PAYLOAD_FOLDER + "/"
            self.assertEqual(archive.read(prefix + "licenses/example.txt"), b"Synthetic license")
            self.assertIn("NOT a complete Paper server", archive.read(prefix + "README_RUNTIME_UPDATE.txt").decode())
            self.assertIn(prefix + "Start-GTM.bat", archive.namelist())
        with ZipFile(self.output / assembly.CONNECTOR_NAME) as archive:
            self.assertEqual(len(archive.namelist()), 4)
            self.assertTrue(all(".secrets" not in name for name in archive.namelist()))

    def test_repo_relative_split_parts_reconstruct_all_exact_bytes(self):
        self.split(self.manifest["files"][0], self.java)
        self.split(self.manifest["artwork"], self.art)
        self.save_manifest()
        assembly.assemble(self.repo, self.output)
        self.assertEqual((self.output / assembly.JAVA_NAME).read_bytes(), self.java)
        self.assertEqual((self.output / assembly.ART_NAME).read_bytes(), self.art)

    def test_corrupt_chunk_produces_no_output(self):
        item = self.manifest["files"][0]
        self.split(item, self.java)
        (self.repo / item["parts"][0]["path"]).write_bytes(b"corrupt")
        self.save_manifest()
        with self.assertRaises(assembly.AssemblyError):
            assembly.assemble(self.repo, self.output)
        self.assertFalse(self.output.exists())

    def test_correct_chunk_hashes_do_not_bypass_full_file_hash(self):
        item = self.manifest["files"][0]
        self.split(item, self.java)
        item["sha256"] = "0" * 64
        self.save_manifest()
        with self.assertRaises(assembly.AssemblyError):
            assembly.assemble(self.repo, self.output)
        self.assertFalse(self.output.exists())

    def test_existing_output_is_never_overwritten(self):
        self.output.mkdir()
        sentinel = self.output / assembly.JAVA_NAME
        sentinel.write_bytes(b"owner file")
        with self.assertRaises(assembly.AssemblyError):
            assembly.assemble(self.repo, self.output)
        self.assertEqual(sentinel.read_bytes(), b"owner file")

    def test_path_traversal_absolute_and_windows_aliases_are_refused(self):
        for path in ("../escape", "/absolute", "folder/../escape", "C:/escape", "foo\\bar", "file:stream", "CON.txt", "name.", "folder//file", "name?"):
            with self.subTest(path=path):
                with self.assertRaises(assembly.AssemblyError):
                    assembly.safe_relative(path)

    def test_chunk_path_cannot_escape_repository(self):
        item = self.manifest["files"][0]
        self.split(item, self.java)
        item["parts"][0]["path"] = "../secret"
        self.save_manifest()
        with self.assertRaises(assembly.AssemblyError):
            assembly.assemble(self.repo, self.output)

    def test_source_override_cannot_escape_repository(self):
        self.manifest["artwork"]["source_repo_path"] = "../secret.zip"
        self.save_manifest()
        with self.assertRaises(assembly.AssemblyError):
            assembly.assemble(self.repo, self.output)

    def test_symlink_input_is_refused(self):
        source = self.runtime / assembly.JAVA_PATH
        real = self.root / "outside.zip"
        real.write_bytes(self.java)
        source.unlink()
        source.symlink_to(real)
        with self.assertRaises(assembly.AssemblyError):
            assembly.assemble(self.repo, self.output)

    def test_case_colliding_output_paths_are_refused(self):
        self.manifest["files"].append(record("START-GTM.BAT", b"different"))
        self.save_manifest()
        with self.assertRaises(assembly.AssemblyError):
            assembly.assemble(self.repo, self.output)

    def test_unresolved_lfs_pointer_is_refused_even_if_manifest_hash_matches(self):
        pointer = b"version https://git-lfs.github.com/spec/v1\noid sha256:synthetic\nsize 10\n"
        (self.runtime / assembly.JAVA_PATH).write_bytes(pointer)
        self.manifest["files"][0] = record(assembly.JAVA_PATH, pointer)
        self.save_manifest()
        with self.assertRaises(assembly.AssemblyError):
            assembly.assemble(self.repo, self.output)

    def test_invalid_zip_with_matching_manifest_hash_is_refused(self):
        (self.runtime / assembly.JAVA_PATH).write_bytes(b"not a ZIP")
        self.manifest["files"][0] = record(assembly.JAVA_PATH, b"not a ZIP")
        self.save_manifest()
        with self.assertRaises(assembly.AssemblyError):
            assembly.assemble(self.repo, self.output)

    def test_artwork_is_required_for_complete_release(self):
        del self.manifest["artwork"]
        self.save_manifest()
        with self.assertRaises(assembly.AssemblyError):
            assembly.assemble(self.repo, self.output)

    def test_optional_git_blob_sha_is_verified(self):
        self.manifest["files"][0]["git_sha"] = "0" * 40
        self.save_manifest()
        with self.assertRaises(assembly.AssemblyError):
            assembly.assemble(self.repo, self.output)

    def test_chunk_sizes_and_duplicates_are_refused(self):
        item = self.manifest["files"][0]
        self.split(item, self.java)
        item["parts"][0]["bytes"] += 1
        self.save_manifest()
        with self.assertRaises(assembly.AssemblyError):
            assembly.assemble(self.repo, self.output)

    def test_repeated_assembly_is_byte_deterministic(self):
        assembly.assemble(self.repo, self.output)
        second = self.root / "release-second"
        assembly.assemble(self.repo, second)
        self.assertEqual({p.name: p.read_bytes() for p in self.output.iterdir()},
                         {p.name: p.read_bytes() for p in second.iterdir()})


if __name__ == "__main__":
    unittest.main()
