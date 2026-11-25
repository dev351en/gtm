"""Read-only Geyser readiness tests; never contact a live server."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from check_geyser_setup import inspect, BEDROCK_MAP, BEDROCK_PACK, JAVA_PACK


class GeyserReadinessTests(unittest.TestCase):
    def fixture(self, server):
        (server / "plugins/Geyser-Spigot").mkdir(parents=True)
        (server / "plugins/Geyser-Spigot/config.yml").write_text(
            "gameplay:\n  enable-custom-content: true\n", encoding="utf-8")
        (server / "server.properties").write_text(
            "resource-pack=https://example.org/gtm.zip\n"
            "resource-pack-sha1=0123456789abcdef0123456789abcdef01234567\n",
            encoding="utf-8")
        for name in [BEDROCK_MAP, BEDROCK_PACK, JAVA_PACK]:
            p = server / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"test-only fixture")

    def test_detects_custom_items_ready_but_display_renderer_uncertain(self):
        with TemporaryDirectory() as tmp:
            server = Path(tmp)
            self.fixture(server)
            result = inspect(server)
            self.assertTrue(result["item_models_configured"])
            self.assertEqual(result["status"], "CONFIG_READY_NOT_CLIENT_CERTIFIED")
            self.assertTrue(any("ItemDisplay" in item for item in result["warnings"]))

    def test_fails_closed_if_geyser_custom_models_disabled(self):
        with TemporaryDirectory() as tmp:
            server = Path(tmp)
            self.fixture(server)
            (server / "plugins/Geyser-Spigot/config.yml").write_text(
                "gameplay:\n  enable-custom-content: false\n", encoding="utf-8")
            result = inspect(server)
            self.assertEqual(result["status"], "NEEDS_SETUP")
            self.assertFalse(result["item_models_configured"])
            self.assertTrue(any("enable-custom-content" in item for item in result["blockers"]))

    def test_missing_pack_is_not_mistaken_for_success(self):
        with TemporaryDirectory() as tmp:
            server = Path(tmp)
            self.fixture(server)
            (server / BEDROCK_PACK).unlink()
            result = inspect(server)
            self.assertEqual(result["status"], "NEEDS_SETUP")
            self.assertFalse(result["item_models_configured"])

    def test_detects_a_server_side_display_extension_without_claiming_playtest(self):
        with TemporaryDirectory() as tmp:
            server = Path(tmp)
            self.fixture(server)
            folder = server / "plugins/Geyser-Spigot/extensions"
            folder.mkdir()
            (folder / "GeyserDisplayEntity-1.0.15.jar").write_bytes(b"test-only")
            result = inspect(server)
            self.assertEqual(result["display_extensions_found"], ["GeyserDisplayEntity-1.0.15.jar"])
            self.assertEqual(result["status"], "CONFIG_READY_NOT_CLIENT_CERTIFIED")


if __name__ == "__main__":
    unittest.main()
