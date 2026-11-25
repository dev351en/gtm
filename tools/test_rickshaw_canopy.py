"""Traditional-auto canopy regression tests using the preserved actual packs."""
from copy import deepcopy
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from zipfile import ZipFile

import build_repaired_packs as packs
import repair_rickshaw_canopy as repair


class RickshawCanopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.java = packs.read_bytes(packs.preserved_bytes("resourcepacks/GTM_Local_Java.zip"))
        cls.bedrock = packs.read_bytes(packs.preserved_bytes("plugins/Geyser-Spigot/packs/GTM_Local_Bedrock.mcpack"))
        cls.new_java, cls.new_bedrock = dict(cls.java), dict(cls.bedrock)
        cls.report = repair.repair_packs(cls.new_java, cls.new_bedrock)

    def test_only_explicit_canopy_geometry_files_change(self):
        self.assertEqual(set(self.java), set(self.new_java))
        self.assertEqual(set(self.bedrock), set(self.new_bedrock))
        self.assertEqual({p for p in self.java if self.java[p] != self.new_java[p]}, repair.JAVA_PATHS)
        self.assertEqual({p for p in self.bedrock if self.bedrock[p] != self.new_bedrock[p]}, repair.BEDROCK_PATHS)
        for old, new in [(self.java, self.new_java), (self.bedrock, self.new_bedrock)]:
            for path in old:
                if path.endswith(".png") or "wheel_" in path or "_wreck" in path:
                    self.assertEqual(old[path], new[path], path)

    def test_java_changes_only_roof_height_and_post_upper_endpoints(self):
        for path in repair.JAVA_PATHS:
            old, new = json.loads(self.java[path]), json.loads(self.new_java[path])
            self.assertEqual({k: v for k, v in old.items() if k != "elements"},
                             {k: v for k, v in new.items() if k != "elements"}, path)
            changed = []
            for before, after in zip(old["elements"], new["elements"]):
                name = before.get("name")
                if name not in repair.PART_NAMES:
                    self.assertEqual(before, after, path + "/" + str(name))
                    continue
                changed.append(name)
                restored = deepcopy(after)
                restored["to"][1] = before["to"][1]
                if name == "part_10":
                    restored["from"][1] = before["from"][1]
                    self.assertAlmostEqual(before["to"][1] - before["from"][1],
                                           after["to"][1] - after["from"][1], places=5)
                self.assertEqual(before, restored, path + "/" + name)
            self.assertEqual(set(changed), repair.PART_NAMES)

    def test_rendered_roof_clears_seated_avatar_and_matches_collision(self):
        # Exhaust the pitch envelope of a normal adult avatar with a vanilla
        # helmet, including the higher rear seats. Yaw does not alter height.
        head_max = max(.05 + .9375 * (1.501 - (y * math.cos(math.radians(pitch))
                                            - z * math.sin(math.radians(pitch))) / 16)
                       for pitch in range(-90, 91) for y in (-9, 1) for z in (-5, 5))
        for state, (suffix, scale) in repair.STATES.items():
            for name in ("rickshaw_traditional" + suffix, "vt_rickshaw_traditional_" + state + "_body"):
                data = json.loads(self.new_java["assets/gtm/models/item/" + name + ".json"])
                roof = next(e for e in data["elements"] if e.get("name") == "part_10")
                # Both preserved render translations are scale/2, cancelling
                # the item-model origin's -8/16; worldY is modelY*scale/16.
                bottom, top = (roof[k][1] * scale / 16 for k in ("from", "to"))
                self.assertGreater(bottom - head_max, .02, name)
                self.assertLessEqual(top, repair.COLLISION_MAX_Y, name)
                self.assertAlmostEqual(bottom, 26.2 / 16 + repair.RAISE_BLOCKS, places=4)
                for post in (e for e in data["elements"] if e.get("name") in repair.POST_NAMES):
                    self.assertGreater(post["to"][1], roof["from"][1], name)
                    self.assertLess(post["to"][1], roof["to"][1], name)

    def test_bedrock_raw_and_bridge_preserve_identity_uvs_and_wheels(self):
        for path in repair.BEDROCK_PATHS:
            before, after = json.loads(self.bedrock[path]), json.loads(self.new_bedrock[path])
            old, new = before["minecraft:geometry"][0], after["minecraft:geometry"][0]
            self.assertEqual(old["description"]["identifier"], new["description"]["identifier"])
            changed = 0
            for a, b in zip(old["bones"], new["bones"]):
                self.assertEqual({k: v for k, v in a.items() if k != "cubes"},
                                 {k: v for k, v in b.items() if k != "cubes"})
                self.assertEqual(len(a.get("cubes", [])), len(b.get("cubes", [])))
                for x, y in zip(a.get("cubes", []), b.get("cubes", [])):
                    if x == y:
                        continue
                    changed += 1
                    restored = deepcopy(y)
                    restored["origin"][1] = x["origin"][1]
                    restored["size"][1] = x["size"][1]
                    self.assertEqual(x, restored, path)
            self.assertEqual(changed, 5, path)
            if "/rd/" not in path:
                self.assertAlmostEqual(new["description"]["visible_bounds_height"]
                                       - old["description"]["visible_bounds_height"], .45)
                self.assertAlmostEqual(new["description"]["visible_bounds_offset"][1]
                                       - old["description"]["visible_bounds_offset"][1], .225)
            else:
                self.assertEqual(old["description"], new["description"])
                bounds = new["description"]
                center = bounds["visible_bounds_offset"]
                half = [bounds["visible_bounds_width"] / 2,
                        bounds["visible_bounds_height"] / 2,
                        bounds["visible_bounds_width"] / 2]
                for bone in new["bones"]:
                    for cube in bone.get("cubes", []):
                        for axis in range(3):
                            low = cube["origin"][axis] / 16
                            high = (cube["origin"][axis] + cube["size"][axis]) / 16
                            self.assertGreaterEqual(low, center[axis] - half[axis], path)
                            self.assertLessEqual(high, center[axis] + half[axis], path)

    def test_loaded_profile_resource_changes_one_row_and_retains_all_driving_fields(self):
        with ZipFile(repair.CORE) as core:
            original = core.read(repair.PROFILE_PATH).decode().splitlines()
        updated = repair.PROFILE_RESOURCE.read_text().splitlines()
        self.assertEqual(len(original), len(updated))
        changed = [(a, b) for a, b in zip(original, updated) if a != b]
        self.assertEqual(len(changed), 1)
        old, new = (line.split("\t") for line in changed[0])
        self.assertEqual(old[0], repair.MODEL_ID)
        self.assertEqual(new[0], repair.MODEL_ID)
        for index in range(13):
            if index not in {5, 12}:
                self.assertEqual(old[index], new[index])
        self.assertEqual(float(new[5].split(",")[4]), repair.COLLISION_MAX_Y)
        self.assertEqual(new[12].split("|", 1)[0], repair.sha(
            self.new_bedrock["models/entity/rickshaw_traditional.geo.json"]))
        self.assertEqual(sum(not line.startswith("#") and bool(line) for line in updated), 87)

    def test_unknown_or_repeated_inputs_are_rejected_without_mutation(self):
        first = next(iter(repair.JAVA_PATHS))
        altered = dict(self.java)
        altered[first] += b" "
        for java, bedrock in [(altered, dict(self.bedrock)), (dict(self.new_java), dict(self.new_bedrock))]:
            before = dict(java), dict(bedrock)
            with self.assertRaises(ValueError):
                repair.repair_packs(java, bedrock)
            self.assertEqual(before, (java, bedrock))
        with tempfile.TemporaryDirectory() as folder, mock.patch.object(repair, "PROFILE_RESOURCE", Path(folder) / "missing.tsv"):
            java, bedrock = dict(self.java), dict(self.bedrock)
            with self.assertRaises(ValueError):
                repair.repair_packs(java, bedrock)
            self.assertEqual(java, self.java)
            self.assertEqual(bedrock, self.bedrock)

    def test_plan_is_deterministic(self):
        self.assertEqual(repair.build_plan(self.java, self.bedrock), repair.build_plan(self.java, self.bedrock))


if __name__ == "__main__":
    unittest.main()
