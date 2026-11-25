"""Actual-pack regressions for the raised, widened four-seat traditional auto."""
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

    def test_only_explicit_traditional_auto_geometry_files_change(self):
        self.assertEqual(16, len(repair.JAVA_PATHS))
        self.assertEqual(32, len(repair.BEDROCK_PATHS))
        for old, new, paths in [(self.java, self.new_java, repair.JAVA_PATHS),
                                (self.bedrock, self.new_bedrock, repair.BEDROCK_PATHS)]:
            self.assertEqual(set(old), set(new))
            self.assertEqual({p for p in old if old[p] != new[p]}, paths)
            for path in old:
                if path.endswith(".png") or "wheel_fl" in path:
                    self.assertEqual(old[path], new[path], path)

    def test_java_preserves_original_materials_shapes_depth_and_driver(self):
        for path in repair.JAVA_PATHS:
            old, new = json.loads(self.java[path]), json.loads(self.new_java[path])
            self.assertEqual({k: v for k, v in old.items() if k != "elements"},
                             {k: v for k, v in new.items() if k != "elements"}, path)
            self.assertEqual(len(old["elements"]), len(new["elements"]))
            for before, after in zip(old["elements"], new["elements"]):
                name = before.get("name")
                restored = deepcopy(after)
                restored["from"], restored["to"] = before["from"], before["to"]
                self.assertEqual(before, restored, path + "/" + name)
                self.assertEqual(before["from"][2], after["from"][2])
                self.assertEqual(before["to"][2], after["to"][2])
                if name not in repair.POST_NAMES | {"part_10"} or "_wreck" in path:
                    self.assertEqual(before["from"][1], after["from"][1])
                    self.assertEqual(before["to"][1], after["to"][1])
                if name not in repair.PART_NAMES and name not in {"tire_v", "tire_h", "tire_d", "rim"}:
                    self.assertEqual(before, after)
                if name in {"tire_v", "tire_h", "tire_d", "rim"}:
                    for axis in range(3):
                        self.assertAlmostEqual(before["to"][axis] - before["from"][axis],
                                               after["to"][axis] - after["from"][axis], places=5)
                    if (before["from"][2] + before["to"][2]) / 2 > 8:
                        self.assertEqual(before, after, "The driver/front wheel must not move")

    def test_rendered_roof_clears_three_seated_avatars_and_preserves_wreck_height(self):
        head_max = max(.05 + .9375 * (1.501 - (y * math.cos(math.radians(pitch))
                                            - z * math.sin(math.radians(pitch))) / 16)
                       for pitch in range(-90, 91) for y in (-9, 1) for z in (-5, 5))
        for state, (suffix, scale) in repair.STATES.items():
            for name in ("rickshaw_traditional" + suffix, "vt_rickshaw_traditional_" + state + "_body"):
                data = json.loads(self.new_java["assets/gtm/models/item/" + name + ".json"])
                roof = next(e for e in data["elements"] if e.get("name") == "part_10")
                bottom, top = (roof[k][1] * scale / 16 for k in ("from", "to"))
                if state == "wreck":
                    self.assertLess(top, 1.21, name)
                    continue
                self.assertGreater(bottom - head_max, .02, name)
                self.assertLessEqual(top, repair.COLLISION_MAX_Y, name)
                self.assertAlmostEqual(bottom, 26.2 / 16 + repair.RAISE_BLOCKS, places=4)
                for post in (e for e in data["elements"] if e.get("name") in repair.POST_NAMES):
                    self.assertGreater(post["to"][1], roof["from"][1], name)
                    self.assertLess(post["to"][1], roof["to"][1], name)

    def test_three_distinct_passengers_fit_the_existing_widened_bench(self):
        for state, (suffix, scale) in repair.STATES.items():
            name = "assets/gtm/models/item/rickshaw_traditional" + suffix + ".json"
            model = json.loads(self.new_java[name])
            bench = next(e for e in model["elements"] if e.get("name") == "part_5")
            left, right = ((bench[k][0] - 8) * scale / 16 for k in ("from", "to"))
            self.assertAlmostEqual(1.828, right - left, places=4)
            seats = sorted(repair.PASSENGER_X)
            for x in seats:
                self.assertGreaterEqual(x - .3, left)
                self.assertLessEqual(x + .3, right)
                self.assertLessEqual(abs(x) + .3, repair.COLLISION_HALF_WIDTH)
            for a, b in zip(seats, seats[1:]):
                self.assertGreaterEqual(b - a, .6)
                # Forward-facing vanilla helmets are .5859375 block wide.
                self.assertGreater(b - a, .9375 * 10 / 16)
            self.assertGreater(math.hypot(.6, -.624 - .208), .6)
            for post in (e for e in model["elements"] if e.get("name") in repair.POST_NAMES):
                self.assertTrue(post["to"][0] < bench["from"][0] or post["from"][0] > bench["to"][0])

    def test_bedrock_raw_and_mirrored_display_exports_match_java(self):
        for state, (suffix, scale) in repair.STATES.items():
            names = ["rickshaw_traditional" + suffix]
            names += ["vt_rickshaw_traditional_" + state + "_" + p for p in ("body", "wheel_rl", "wheel_rr")]
            for name in names:
                parts = json.loads(self.new_java["assets/gtm/models/item/" + name + ".json"])["elements"]
                for kind in ("rd/", "rt/" if name.startswith("vt_") else ""):
                    path = "models/entity/" + kind + name + ".geo.json"
                    old = json.loads(self.bedrock[path])["minecraft:geometry"][0]
                    new = json.loads(self.new_bedrock[path])["minecraft:geometry"][0]
                    self.assertEqual(old["description"]["identifier"], new["description"]["identifier"])
                    cubes = [c for bone in new["bones"] for c in bone.get("cubes", [])]
                    before = [c for bone in old["bones"] for c in bone.get("cubes", [])]
                    self.assertEqual(len(cubes), len(parts))
                    for original, cube, part in zip(before, cubes, parts):
                        self.assertEqual({k:v for k,v in original.items() if k not in {"origin","size","pivot"}},
                                         {k:v for k,v in cube.items() if k not in {"origin","size","pivot"}})
                        for axis in range(3):
                            if kind == "rd/":
                                low = 8-part["to"][axis] if axis == 0 else part["from"][axis]-8
                                size = part["to"][axis]-part["from"][axis]
                                self.assertAlmostEqual(low, cube["origin"][axis], places=5)
                                self.assertAlmostEqual(size, cube["size"][axis], places=5)
                            else:
                                translation = (0, scale*8, -.272 if state in {"normal","damaged"} else 0)
                                low = (part["from"][axis]-8)*scale+translation[axis]
                                self.assertAlmostEqual(low, cube["origin"][axis], delta=.003)
                    desc = new["description"]
                    center = desc["visible_bounds_offset"]
                    half = [desc["visible_bounds_width"]/2, desc["visible_bounds_height"]/2, desc["visible_bounds_width"]/2]
                    for cube in cubes:
                        for axis in range(3):
                            self.assertGreaterEqual(cube["origin"][axis]/16, center[axis]-half[axis], path)
                            self.assertLessEqual((cube["origin"][axis]+cube["size"][axis])/16, center[axis]+half[axis], path)

    def test_loaded_profile_has_driver_plus_three_and_retains_other84_profiles(self):
        with ZipFile(repair.CORE) as core:
            original = core.read(repair.PROFILE_PATH).decode().splitlines()
        updated = repair.PROFILE_RESOURCE.read_text().splitlines()
        self.assertEqual(len(original), len(updated))
        changed = [(a,b) for a,b in zip(original,updated) if a != b]
        self.assertEqual(len(changed), 3)
        old,new = next((a.split("\t"),b.split("\t")) for a,b in changed if a.startswith(repair.MODEL_ID+"\t"))
        self.assertEqual(old[0], repair.MODEL_ID)
        for index in range(13):
            if index not in {5,6,12}: self.assertEqual(old[index],new[index])
        seats = new[6].split(";")
        self.assertEqual(4,len(seats))
        self.assertEqual(old[6].split(";")[0],seats[0])
        self.assertEqual(3,sum(":passenger:" in s for s in seats))
        self.assertEqual(new[12].split("|",1)[0], repair.sha(self.new_bedrock["models/entity/rickshaw_traditional.geo.json"]))
        self.assertEqual(87,sum(not line.startswith("#") and bool(line) for line in updated))
        for old_line,new_line in changed:
            before,after = old_line.split("\t"),new_line.split("\t")
            if before[0] == repair.MODEL_ID: continue
            self.assertIn(before[0],repair.EXISTING_FRONT_PASSENGERS)
            for index in range(13):
                if index not in {6,12}: self.assertEqual(before[index],after[index])
            self.assertEqual(before[6],after[6].split(";")[0])
            self.assertEqual(2,len(after[6].split(";")))
            driver = [float(x) for x in before[6].rsplit(":",1)[1].split(",")]
            passenger = [float(x) for x in after[6].split(";")[1].rsplit(":",1)[1].split(",")]
            self.assertEqual([-driver[0],driver[1],driver[2]],passenger)

    def test_only_eight_rear_animation_pivots_change_and_match_wheel_meshes(self):
        with ZipFile(repair.CORE) as core:
            original = core.read(repair.ANIMATION_PATH).decode().splitlines()
        updated = repair.ANIMATION_RESOURCE.read_text().splitlines()
        changes = [(a.split("\t"),b.split("\t")) for a,b in zip(original,updated) if a != b]
        self.assertEqual(8,len(changes))
        for old,new in changes:
            self.assertEqual(old[:5],new[:5]);self.assertEqual(old[6:],new[6:])
            pivot = [float(x) for x in new[5].split(",")]
            self.assertEqual([.2,-.78],pivot[1:])
            self.assertAlmostEqual(.966,abs(pivot[0]))
            path = "models/entity/rt/" + new[3].split(":",1)[1] + ".geo.json"
            bone = next(b for b in json.loads(self.new_bedrock[path])["minecraft:geometry"][0]["bones"] if b["name"]==new[2])
            self.assertEqual(pivot,[x/16 for x in bone["pivot"]])
            for cube in bone.get("cubes",[]):
                self.assertGreaterEqual(cube["origin"][1],0)
                self.assertLessEqual(cube["origin"][1]+cube["size"][1],6.4)
                self.assertLessEqual(abs(cube["origin"][0]/16),repair.COLLISION_HALF_WIDTH)
                self.assertLessEqual(abs((cube["origin"][0]+cube["size"][0])/16),repair.COLLISION_HALF_WIDTH)

    def test_unknown_repeated_or_mismatched_runtime_inputs_fail_without_mutation(self):
        first = next(iter(repair.JAVA_PATHS))
        altered = dict(self.java);altered[first] += b" "
        for java,bedrock in [(altered,dict(self.bedrock)),(dict(self.new_java),dict(self.new_bedrock))]:
            before = dict(java),dict(bedrock)
            with self.assertRaises(ValueError): repair.repair_packs(java,bedrock)
            self.assertEqual(before,(java,bedrock))
        for resource in ("PROFILE_RESOURCE","ANIMATION_RESOURCE"):
            with tempfile.TemporaryDirectory() as folder, mock.patch.object(repair,resource,Path(folder)/"missing.tsv"):
                java,bedrock = dict(self.java),dict(self.bedrock)
                with self.assertRaises(ValueError): repair.repair_packs(java,bedrock)
                self.assertEqual(java,self.java);self.assertEqual(bedrock,self.bedrock)

    def test_plan_is_deterministic(self):
        self.assertEqual(repair.build_plan(self.java,self.bedrock),repair.build_plan(self.java,self.bedrock))


if __name__ == "__main__":
    unittest.main()
