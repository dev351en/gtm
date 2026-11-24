"""Boundary tests for preservation and strict runtime resource resolution."""
import json
import io
from pathlib import Path
import tempfile
import unittest
import warnings
from zipfile import ZipFile

import build_runtime_packs as packs
import gtm_legacy_pack_adapter as legacy
from PIL import Image


class RuntimePackTests(unittest.TestCase):
    def test_existing_core_dispatch_keeps_its_four_gun_numbers_and_phone_selectors(self):
        source = packs.read_archive(packs.ROOT / "resource-pack/EXPECT_SDCRAFT_ResourcePack_26.3.zip")
        bindings = legacy.legacy_bindings(source)
        self.assertEqual(21, len(bindings))
        self.assertEqual({101, 102, 103, 104}, {b["custom_model_data"] for b in bindings if b["base_item"] != "minecraft:paper"})
        self.assertEqual(set(range(900020, 900028)), {b["custom_model_data"] for b in bindings if 900020 <= b["custom_model_data"] <= 900027})

    def test_phone_model_repair_uses_semantic_icons_and_never_replaces_an_existing_model(self):
        java = {f"assets/gtm/textures/ui/phone/{name}.png": b"native128" for name in legacy.PHONE_MODELS.values()}
        java["assets/sdcraft/models/item/app_bank.json"] = b"preserved existing bank model"
        with tempfile.TemporaryDirectory() as folder:
            icon = Path(folder) / "source/icons/hero_props/hero_pistol.png"
            icon.parent.mkdir(parents=True)
            icon.write_bytes(b"native128 pistol icon")
            repaired = legacy.repair_phone_models(java, Path(folder))
        self.assertEqual(7, len(repaired))
        self.assertEqual(b"preserved existing bank model", java["assets/sdcraft/models/item/app_bank.json"])
        self.assertEqual("gtm:ui/phone/app_maps", json.loads(java["assets/sdcraft/models/item/app_gps.json"])["textures"]["layer0"])
        self.assertEqual("gtm:ui/phone/app_careers", json.loads(java["assets/sdcraft/models/item/app_jobs.json"])["textures"]["layer0"])

    def test_legacy_mesh_adapter_preserves_texture_pixels_dimensions_and_rotation(self):
        image = Image.new("RGBA", (8, 8), (20, 90, 160, 255))
        image.putpixel((2, 3), (220, 30, 70, 255))
        texture = legacy.png(image)
        model = {"textures": {"surface": "sdcraft:item/test"}, "elements": [{
            "from": [1, 2, 3], "to": [5, 7, 9], "rotation": {"axis": "z", "angle": 22.5, "origin": [8, 8, 8]},
            "faces": {face: {"texture": "#surface"} for face in ("north", "south", "east", "west", "up", "down")}}]}
        java = self.legacy_fixture(model, texture)
        bed, mappings, detail = legacy.bridge(java, packs.java_model, packs.texture_reference)
        entry = next(iter(detail.values()))
        key = entry["bedrock_identifier"].split(":")[1]
        geometry = json.loads(bed[f"models/entity/{key}.geo.json"])["minecraft:geometry"][0]
        cube = geometry["bones"][0]["cubes"][0]
        self.assertEqual([3, -6, -5], cube["origin"])
        self.assertEqual([4, 5, 6], cube["size"])
        self.assertEqual([0, 0, -22.5], cube["rotation"])
        self.assertEqual([0, 0, 0], cube["pivot"])
        with Image.open(io.BytesIO(bed[f"textures/sdcraft_compat/{key}.png"])) as atlas:
            self.assertEqual(image.tobytes(), atlas.crop((0, 0, 8, 8)).tobytes())
        with Image.open(io.BytesIO(bed[f"textures/items/sdcraft_{key}.png"])) as icon:
            self.assertEqual((128, 128), icon.size)
            self.assertIsNotNone(icon.getchannel("A").getbbox())
        self.assertEqual(101, mappings["items"]["minecraft:iron_hoe"][0]["custom_model_data"])

    def test_flat_phone_icon_keeps_its_original_master_bytes(self):
        image = Image.new("RGBA", (128, 128), (30, 170, 90, 255))
        texture = legacy.png(image)
        java = self.legacy_fixture({"parent": "minecraft:item/generated", "textures": {"layer0": "sdcraft:item/test"}}, texture)
        bed, _, detail = legacy.bridge(java, packs.java_model, packs.texture_reference)
        entry = next(iter(detail.values()))
        key = entry["bedrock_identifier"].split(":")[1]
        self.assertEqual(texture, bed[f"textures/items/sdcraft_{key}.png"])
        self.assertEqual("flat_generated_item", entry["source_render_kind"])

    @staticmethod
    def legacy_fixture(model, texture):
        return {"assets/minecraft/items/iron_hoe.json": packs.encoded({"model": {
                    "type": "range_dispatch", "property": "custom_model_data", "entries": [
                        {"threshold": 101, "model": {"type": "minecraft:model", "model": "sdcraft:item/test"}}]}}),
                "assets/sdcraft/models/item/test.json": packs.encoded(model),
                "assets/sdcraft/textures/item/test.png": texture}

    def test_identical_legacy_zip_duplicates_are_deduplicated_but_conflicts_are_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "pack.zip"
            for second, accepted in [(b"same", True), (b"changed", False)]:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    with ZipFile(path, "w") as z:
                        z.writestr("assets/model.json", b"same")
                        z.writestr("assets/model.json", second)
                if accepted:
                    self.assertEqual({"assets/model.json": b"same"}, packs.read_archive(path))
                else:
                    with self.assertRaisesRegex(ValueError, "Conflicting duplicate"):
                        packs.read_archive(path)

    def test_pack_members_cannot_escape_or_use_windows_path_separators(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "pack.zip"
            for member in ("../outside.json", "/absolute.json", "assets\\outside.json"):
                with ZipFile(path, "w") as z:
                    z.writestr(member, b"{}")
                with self.assertRaisesRegex(ValueError, "Unsafe pack entry"):
                    packs.read_archive(path)

    def test_native_geometry_replaces_only_matching_identifier_in_legacy_collection(self):
        geometry = lambda name, marker: {"description": {"identifier": name}, "marker": marker}
        old = {"models/entity/old.geo.json": packs.encoded({"minecraft:geometry": [
            geometry("geometry.gtm.same", "old"), geometry("geometry.gtm.keep", "preserved")]}),
            "textures/old_hud.png": b"active hud"}
        new = {"models/entity/new.geo.json": packs.encoded({"minecraft:geometry": [geometry("geometry.gtm.same", "native128")]})}
        packs.merge_bedrock(old, new)
        models = [g for key, value in old.items() if key.endswith(".geo.json") for g in json.loads(value)["minecraft:geometry"]]
        self.assertEqual({"geometry.gtm.keep": "preserved", "geometry.gtm.same": "native128"},
                         {g["description"]["identifier"]: g["marker"] for g in models})
        self.assertEqual(b"active hud", old["textures/old_hud.png"])

    def test_icon_and_render_controller_merges_retain_unrelated_existing_entries(self):
        target = {"textures/item_texture.json": packs.encoded({"texture_data": {"legacy": {"textures": "old"}}}),
                  "render_controllers/shared.json": packs.encoded({"render_controllers": {"old": {"geometry": "Old"}}})}
        source = {"textures/item_texture.json": packs.encoded({"texture_data": {"new": {"textures": "new"}}}),
                  "render_controllers/shared.json": packs.encoded({"render_controllers": {"new": {"geometry": "New"}}})}
        packs.merge_bedrock(target, source)
        self.assertEqual({"legacy", "new"}, set(json.loads(target["textures/item_texture.json"])["texture_data"]))
        self.assertEqual({"old", "new"}, set(json.loads(target["render_controllers/shared.json"])["render_controllers"]))

    def test_parent_texture_inheritance_resolves_and_cycles_fail_closed(self):
        files = {"assets/gtm/models/item/base.json": packs.encoded({"textures": {"surface": "#finish"}, "elements": [{"marker": 1}]}),
                 "assets/gtm/models/item/child.json": packs.encoded({"parent": "gtm:item/base", "textures": {"finish": "gtm:finish/one"}})}
        model = packs.java_model(files, "gtm:item/child")
        self.assertEqual([{"marker": 1}], model["elements"])
        self.assertEqual("gtm:finish/one", packs.texture_reference(model["textures"], "#surface"))
        files["assets/gtm/models/item/base.json"] = packs.encoded({"parent": "gtm:item/child"})
        with self.assertRaisesRegex(ValueError, "parent cycle"):
            packs.java_model(files, "gtm:item/child")
        with self.assertRaisesRegex(ValueError, "cyclic"):
            packs.texture_reference({"a": "#b", "b": "#a"}, "#a")

    def test_positional_art_proposals_cannot_reassign_stools_or_finish_entitlements(self):
        old = {"bar_stool_irani": ["furniture", "Bar Stool · Irani"]}
        native = {"gtm:coffee_table_teak": {"runtime_category": "furniture", "runtime_kind": "city", "title": "Coffee Table"}}
        mapping = {}
        for key, base in [("bar_stool_irani", "paper"), ("coffee_table_teak", "paper"), ("pistol_75", "iron_hoe")]:
            packs.merge_mappings(mapping, {"format_version": 2, "items": {"minecraft:" + base: [
                {"type": "definition", "model": "gtm:" + key, "bedrock_identifier": "gtm:" + key}]}})
        rows = packs.catalogue(mapping, native, old)
        self.assertEqual("gtm:bar_stool_irani", rows["gtm:bar_stool_irani"][5])
        self.assertEqual("LEGACY_COMPATIBILITY", rows["gtm:bar_stool_irani"][4])
        self.assertEqual("gtm:pistol_75", rows["gtm:pistol_75"][5])
        self.assertEqual("NATIVE_128", rows["gtm:coffee_table_teak"][4])
        self.assertNotIn("gtm:pistol_00", rows)


if __name__ == "__main__":
    unittest.main()
