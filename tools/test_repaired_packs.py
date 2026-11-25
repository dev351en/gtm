"""Regressions for the visible missing-icon fault and cross-platform bindings."""
from copy import deepcopy
import io
import json
import unittest

from PIL import Image

import build_repaired_packs as repair


class RepairedPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.java = repair.read_bytes(repair.preserved_bytes("resourcepacks/GTM_Local_Java.zip"))
        cls.bedrock = repair.read_bytes(repair.preserved_bytes("plugins/Geyser-Spigot/packs/GTM_Local_Bedrock.mcpack"))
        cls.mappings = json.loads(repair.preserved_bytes("plugins/Geyser-Spigot/custom_mappings/gtm_native128.json"))

    def patched(self):
        java, bedrock, mappings = dict(self.java), dict(self.bedrock), deepcopy(self.mappings)
        repair.add_screens(java)
        repair.add_aliases(java, bedrock, mappings)
        return java, bedrock, mappings

    def test_old_pack_without_runtime_app_definitions_is_rejected(self):
        # The previous active download had sdcraft legacy items but no gtm app
        # definitions. A permissive CRC/count-only validator accepted it.
        wrong = {key: value for key, value in self.java.items() if not key.startswith("assets/gtm/items/app_")}
        with self.assertRaisesRegex(ValueError, "Missing runtime UI item definition"):
            repair.validate_java(wrong, require_skin=False)

    def test_all_actual_core_ui_bindings_resolve(self):
        java, _, _ = self.patched()
        report = repair.validate_java(java)
        self.assertEqual(24, report["phone_apps"])
        self.assertEqual(57, report["runtime_ui_items"])
        self.assertEqual(4, report["phone_skins"])

    def test_missing_generated_layer_texture_is_rejected(self):
        java, _, _ = self.patched()
        # Generated item meshes have no faces. Validate inherited layer0 too.
        del java["assets/gtm/textures/ui/phone/app_bank.png"]
        with self.assertRaisesRegex(ValueError, "Missing model texture"):
            repair.validate_java(java)

    def test_missing_font_bitmap_is_rejected(self):
        java, _, _ = self.patched()
        del java["assets/gtm/textures/gui/phone_home.png"]
        with self.assertRaisesRegex(ValueError, "Missing font bitmap"):
            repair.validate_java(java)

    def test_aliases_use_correct_original_base_items(self):
        _, bedrock, mappings = self.patched()
        self.assertEqual(4, repair.validate_bedrock(bedrock, mappings)["weapon_aliases"])
        row = next(value for value in mappings["items"]["minecraft:iron_hoe"] if value.get("model") == "gtm:core_pistol")
        mappings["items"]["minecraft:iron_hoe"].remove(row)
        mappings["items"]["minecraft:paper"].append(row)
        with self.assertRaisesRegex(ValueError, "wrong base material"):
            repair.validate_bedrock(bedrock, mappings)

    def test_skin_and_alias_overlay_preserves_all_original_art_bytes(self):
        java, bedrock, _ = self.patched()
        for name, data in self.java.items():
            self.assertEqual(data, java[name], name)
        for name, data in self.bedrock.items():
            self.assertEqual(data, bedrock[name], name)

    def test_skin_bounds_match_native_inventory_and_font_advance(self):
        java, _, _ = self.patched()
        font = json.loads(java["assets/gtm/font/phone_screen.json"])
        self.assertEqual({"\uf010": -8, "\uf011": -169}, font["providers"][0]["advances"])
        for name, (rows, _) in repair.SCREENS.items():
            image = Image.open(io.BytesIO(java[f"assets/gtm/textures/gui/phone_{name}.png"]))
            self.assertEqual((176, 114 + rows * 18), image.size)
            self.assertEqual((0, 0, 176, image.height), image.getchannel("A").getbbox())
            # Nine native hotbar wells must fit inside the background.
            self.assertLess(7 + 8 * 18 + 17, image.width)
            self.assertLess(rows * 18 + 88 + 17, image.height)


if __name__ == "__main__":
    unittest.main()
