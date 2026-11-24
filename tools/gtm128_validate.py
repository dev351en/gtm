#!/usr/bin/env python3
"""Independent static validation of the isolated GTM128 creative export.

Validates the assets actually on disk, not completion claims. Geometry hashes
discard materials/UVs/names and report exact duplicate shapes separately from
catalogue counts. This does not certify Minecraft client rendering or gameplay.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
LOCAL_ABSOLUTE = re.compile(r"^(?:/(?!/)|[A-Za-z]:[\\/]|file://)")


def no_duplicate_keys(pairs):
    result = {}
    for k, v in pairs:
        if k in result: raise ValueError(f"Duplicate JSON key: {k}")
        result[k] = v
    return result


def strict_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"Non-finite JSON value: {x}")))


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def finite_vec(x, n):
    return isinstance(x, list) and len(x) == n and all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in x)


def shape_signature(geometry):
    """Exact static cube definition signature independent of names/materials.

    Zero rotations and bone labels are discarded. Nonzero bone transforms are
    retained, so this is deliberately conservative about declaring equality.
    It is not a proof that numerically different shapes are artistically unique.
    """
    bones = {b["name"]: b for b in geometry["bones"]}
    shapes = []
    for bone in geometry["bones"]:
        transforms = []
        b = bone; visited = set()
        while b and b.get("name") not in visited:
            visited.add(b.get("name"))
            if any(b.get("rotation", [0, 0, 0])):
                transforms.append({"rotation": b["rotation"], "pivot": b.get("pivot", [0, 0, 0])})
            b = bones.get(b.get("parent"))
        for cube in bone.get("cubes", []):
            item = {"origin": cube["origin"], "size": cube["size"]}
            if any(cube.get("rotation", [0, 0, 0])):
                item["rotation"] = cube["rotation"]
                item["pivot"] = cube.get("pivot", [cube["origin"][i] + cube["size"][i] / 2 for i in range(3)])
            if cube.get("inflate"): item["inflate"] = cube["inflate"]
            if transforms: item["bone_transforms"] = transforms
            # Normalize numeric representation without changing precision.
            def normal(x):
                if isinstance(x, (int, float)): return round(float(x), 6)
                if isinstance(x, list): return [normal(v) for v in x]
                if isinstance(x, dict): return {k: normal(v) for k, v in x.items()}
                return x
            shapes.append(json.dumps(normal(item), sort_keys=True, separators=(",", ":")))
    return hashlib.sha256("\n".join(sorted(shapes)).encode()).hexdigest()


class Validator:
    def __init__(self, output):
        self.output = Path(output).resolve()
        self.errors = []; self.warnings = []; self.counts = Counter()
        self.parsed = {}; self.png = {}; self.hashes = {}
        self.primary_shapes = defaultdict(list); self.additional_shapes = defaultdict(list)
        self.model_shapes = {}; self.model_cube_counts = {}; self.rotation_approximations = []
        self.active_paths = set(); self.provenance_missing = set()
        self.approved_festival_selection = []
        self.material_records = {}

    def clean(self, text):
        return str(text).replace(str(self.output) + "/", "").replace(str(ROOT) + "/", "")

    def error(self, code, asset, detail): self.errors.append({"check": code, "asset": self.clean(asset), "detail": self.clean(detail)})
    def warning(self, code, asset, detail): self.warnings.append({"check": code, "asset": self.clean(asset), "detail": self.clean(detail)})

    def load(self, rel):
        if rel in self.parsed: return self.parsed[rel]
        path = self.output / rel
        if not path.is_file(): self.error("missing_json", rel, "Required JSON file is absent"); return {}
        try:
            obj = strict_json(path); self.parsed[rel] = obj
            self.scan_values(obj, rel)
            return obj
        except Exception as e: self.error("json_parse", rel, str(e)); return {}

    def scan_values(self, obj, location):
        if isinstance(obj, dict):
            for k, v in obj.items(): self.scan_values(v, f"{location}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj): self.scan_values(v, f"{location}[{i}]")
        elif isinstance(obj, str) and LOCAL_ABSOLUTE.match(obj):
            self.error("absolute_local_path", location, "Local machine path leaked into an export; use a relative source reference")
        elif isinstance(obj, float) and not math.isfinite(obj):
            self.error("finite_number", location, "Non-finite numerical value")

    def file(self, rel, asset, expected_hash=None):
        if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
            self.error("safe_path", asset, f"Invalid relative source path: {rel!r}"); return None
        path = self.output / rel
        if not path.is_file(): self.error("source_path", asset, f"Missing active source: {rel}"); return None
        self.active_paths.add(rel)
        if expected_hash:
            if rel not in self.hashes: self.hashes[rel] = sha(path)
            if self.hashes[rel] != expected_hash: self.error("sha256", asset, f"Hash mismatch: {rel}")
        return path

    def png_file(self, rel, asset, dims=None, expected_hash=None):
        path = self.file(rel, asset, expected_hash)
        if path is None: return None
        if rel not in self.png:
            try:
                with Image.open(path) as im:
                    im.load()
                    if im.format != "PNG": self.error("png_format", rel, str(im.format))
                    rgba = im.convert("RGBA")
                    self.png[rel] = {"size": list(im.size), "mode": im.mode,
                                     "alpha_bbox": rgba.getchannel("A").getbbox(),
                                     "pixel_sha256": hashlib.sha256(rgba.tobytes()).hexdigest()}
            except Exception as e:
                self.error("png_decode", rel, str(e)); return None
        info = self.png[rel]
        if dims is not None and list(dims) != info["size"]:
            self.error("png_dimensions", asset, f"{rel}: expected {dims}, got {info['size']}")
        if info["alpha_bbox"] is None: self.error("empty_image", asset, f"Fully transparent PNG: {rel}")
        return info

    def unique_ids(self, records, group, expected=None):
        ids = [r.get("id") for r in records]
        if len(ids) != len(set(ids)): self.error("unique_ids", group, "Duplicate IDs within manifest group")
        if expected is not None and len(ids) != expected: self.error("count", group, f"Expected {expected}, found {len(ids)}")
        return set(ids)

    def source_ids(self, records, source_file, source_key=None):
        try:
            old = strict_json(ROOT / source_file)
            if source_key: old = old[source_key]
            wanted = {r["id"] for r in old}; actual = {r["id"] for r in records}
            if actual != wanted: self.error("preserved_ids", source_file, f"missing={sorted(wanted-actual)}, extra={sorted(actual-wanted)}")
        except Exception as e: self.error("source_manifest", source_file, str(e))

    def model(self, r, primary=True, finish=False, variant=False):
        ident = r["id"]
        geo_path, java_path = r["geometry_path"], r["java_model_path"]
        hashes = r.get("sha256") if isinstance(r.get("sha256"), dict) else {}
        gh = r.get("sha256_bedrock_geometry") if finish else hashes.get("geometry")
        jh = r.get("sha256_java_model") if finish else hashes.get("java_model")
        if self.file(geo_path, ident, gh) is None or self.file(java_path, ident, jh) is None: return
        geo_json, java = self.load(geo_path), self.load(java_path)
        geos = geo_json.get("minecraft:geometry", [])
        if len(geos) != 1: self.error("geometry_count", ident, f"Expected one geometry definition, got {len(geos)}"); return
        geo = geos[0]; desc = geo.get("description", {})
        expected_id = "geometry." + ident.replace(":", ".")
        if desc.get("identifier") != expected_id: self.error("geometry_identifier", ident, f"Expected {expected_id}, got {desc.get('identifier')}")
        if r.get("geometry", expected_id) != expected_id: self.error("manifest_geometry_identifier", ident, f"Manifest disagrees with geometry identifier {expected_id}")
        texture_rel = r.get("texture") if finish else r.get("atlas_path")
        pinfo = self.png_file(texture_rel, ident, [desc.get("texture_width"), desc.get("texture_height")], r.get("sha256") if finish else None)
        width, height = desc.get("texture_width", 0), desc.get("texture_height", 0)
        if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
            self.error("geometry_texture_size", ident, "Invalid declared texture dimensions")
            return
        bones = geo.get("bones", []); names = [b.get("name") for b in bones]
        if not bones or len(names) != len(set(names)): self.error("bone_names", ident, "Missing or duplicate bones")
        by_name = {b.get("name"): b for b in bones}
        cube_count = 0
        for b in bones:
            parent = b.get("parent")
            if parent and parent not in by_name: self.error("bone_parent", ident, f"Unknown parent {parent}")
            seen = set(); current = b
            while current and current.get("parent"):
                n = current.get("name")
                if n in seen: self.error("bone_cycle", ident, f"Cycle at bone {n}"); break
                seen.add(n); current = by_name.get(current.get("parent"))
            for key in ("pivot", "rotation"):
                if key in b and not finite_vec(b[key], 3): self.error("bone_transform", ident, f"Invalid {key}")
            for cube in b.get("cubes", []):
                cube_count += 1
                if not finite_vec(cube.get("origin"), 3) or not finite_vec(cube.get("size"), 3):
                    self.error("cube_coordinates", ident, "Malformed cube origin/size"); continue
                if any(v <= 0 for v in cube["size"]): self.error("cube_volume", ident, f"Nonpositive cube extent {cube['size']}")
                for key in ("rotation", "pivot"):
                    if key in cube and not finite_vec(cube[key], 3): self.error("cube_transform", ident, f"Malformed cube {key}")
                uv = cube.get("uv")
                if not isinstance(uv, dict): self.error("bedrock_uv", ident, "Expected explicit per-face UV dictionary"); continue
                if set(uv) != {"north", "south", "east", "west", "up", "down"}: self.error("bedrock_uv_faces", ident, "Missing cube face UVs")
                for face, val in uv.items():
                    a, size = val.get("uv"), val.get("uv_size")
                    if not finite_vec(a, 2) or not finite_vec(size, 2): self.error("bedrock_uv", ident, f"Invalid {face} UV"); continue
                    for axis, limit in enumerate((width, height)):
                        lo, hi = sorted((a[axis], a[axis] + size[axis]))
                        if lo < -1e-6 or hi > limit + 1e-6: self.error("bedrock_uv_bounds", ident, f"{face} outside texture{width}x{height}")
        elements = java.get("elements", [])
        if not cube_count or not elements: self.error("nonempty_model", ident, "No rendered cube geometry")
        if len(elements) != cube_count: self.error("edition_cube_count", ident, f"Java{len(elements)} versus Bedrock{cube_count}")
        if "cube_count" in r and r["cube_count"] != cube_count: self.error("manifest_cube_count", ident, f"Manifest{r['cube_count']} versus actual{cube_count}")
        if "bone_count" in r and r["bone_count"] != len(bones): self.error("manifest_bone_count", ident, f"Manifest{r['bone_count']} versus actual{len(bones)}")
        if "actual_bounds_blocks" in r:
            bounds = r["actual_bounds_blocks"]
            if not finite_vec(bounds.get("min"), 3) or not finite_vec(bounds.get("max"), 3) or any(bounds["min"][i] >= bounds["max"][i] for i in range(3)):
                self.error("model_local_bounds", ident, "Malformed or empty local bounds")
        for pivot in r.get("pivots", []):
            if pivot.get("id") not in by_name or not finite_vec(pivot.get("position_units"), 3):
                self.error("manifest_pivot", ident, "Pivot does not match an emitted bone or is malformed")
        textures = java.get("textures", {})
        for key, val in textures.items():
            if val.startswith("#"):
                if val[1:] not in textures: self.error("java_texture_alias", ident, f"Unresolved {val}")
            else:
                if val == "gtm:item/gtm_master_atlas_128": tex = "source/textures/gtm_master_atlas_128.png"
                elif val.startswith("gtm:item/finishes/"): tex = "source/textures/finishes/" + val.rsplit("/", 1)[-1] + ".png"
                else: self.error("java_texture_reference", ident, f"Unknown texture binding {val}"); continue
                self.file(tex, ident)
        for e in elements:
            if not finite_vec(e.get("from"), 3) or not finite_vec(e.get("to"), 3): self.error("java_coordinates", ident, "Malformed element bounds"); continue
            if any(e["to"][i] <= e["from"][i] for i in range(3)): self.error("java_element_volume", ident, "Nonpositive Java element extent")
            if any(v < -16.001 or v > 32.001 for v in e["from"] + e["to"]): self.error("java_element_bounds", ident, "Element is outside conventional Java model range -16..32")
            if "rotation" in e:
                rot = e["rotation"]
                if any(k in rot for k in ("x", "y", "z")):
                    if not all(isinstance(rot.get(k, 0), (int, float)) and math.isfinite(rot.get(k, 0)) for k in ("x", "y", "z")):
                        self.error("java_rotation", ident, f"Nonfinite multi-axis rotation {rot}")
                elif rot.get("axis") not in ("x", "y", "z") or not isinstance(rot.get("angle"), (int, float)) or not math.isfinite(rot.get("angle", math.nan)):
                    self.error("java_rotation", ident, f"Malformed legacy axis/angle rotation {rot}")
                if not finite_vec(rot.get("origin"), 3): self.error("java_rotation_origin", ident, "Invalid pivot")
            if set(e.get("faces", {})) != {"north", "south", "east", "west", "up", "down"}: self.error("java_faces", ident, "Incomplete six-face definition")
            for face in e.get("faces", {}).values():
                uv = face.get("uv")
                if not finite_vec(uv, 4) or min(uv) < -1e-6 or max(uv) > 16.000001: self.error("java_uv", ident, "UV outside0..16 or malformed")
                ref = face.get("texture", "")
                if not ref.startswith("#") or ref[1:] not in textures: self.error("java_face_texture", ident, f"Unresolved face texture {ref}")
        if not finish:
            self.png_file(r["icon_path"], ident, [128, 128], hashes.get("icon"))
            if self.file(r["editable_source"], ident, hashes.get("editable")):
                edit = self.load(r["editable_source"])
                parts = sum(len(b.get("parts", [])) for b in edit.get("bones", {}).values())
                if parts != cube_count: self.error("editable_part_count", ident, f"Editable{parts} versus geometry{cube_count}")
                for name, bone in edit.get("bones", {}).items():
                    emitted = by_name.get(name, {}).get("cubes", [])
                    authored = bone.get("parts", [])
                    if len(authored) != len(emitted): self.error("editable_bone_part_count", ident, f"Bone{name} has mismatched authored/emitted cubes"); continue
                    for part, cube in zip(authored, emitted):
                        for face, uv in cube.get("uv", {}).items():
                            material_name = part.get("face_mats", {}).get(face, part.get("mat"))
                            material = self.material_records.get(material_name)
                            if not material or material.get("atlas_cell") is None:
                                self.error("authored_material_binding", ident, f"Unbound material{material_name}"); continue
                            cell = [int(v // 128) for v in uv.get("uv", [])]
                            if cell != material["atlas_cell"]:
                                self.error("authored_material_cell", ident, f"Material{material_name}: expected cell{material['atlas_cell']}, actual{cell}")
            signature = shape_signature(geo)
            if not variant:
                (self.primary_shapes if primary else self.additional_shapes)[signature].append(ident)
                self.model_shapes[ident] = signature; self.model_cube_counts[ident] = cube_count
        else:
            source_id = r["geometry_id"]
            if source_id not in self.model_cube_counts: self.error("finish_source_geometry", ident, f"Missing source {source_id}")
            elif self.model_cube_counts[source_id] != cube_count: self.error("finish_shared_cube_count", ident, f"Different source cube count for {source_id}")
            if "icon_path" in r: self.png_file(r["icon_path"], ident, [128, 128], r.get("sha256_icon"))
        approximations = r.get("java_rotation_approximations", 0)
        if approximations: self.rotation_approximations.append({"id": ident, "approximated_parts": approximations})
        self.counts["finish_model_pairs" if finish else "damage_variant_model_pairs" if variant else "primary_model_pairs" if primary else "additional_model_pairs"] += 1
        self.counts["bedrock_cubes"] += cube_count
        self.counts["java_elements"] += len(elements)

    def characters(self):
        d = self.load("manifests/characters_128.json")
        old_skins = strict_json(ROOT / "creative/manifests/npc_skins_manifest.json")["skins"]
        old_outfits = strict_json(ROOT / "creative/manifests/outfits_manifest.json")["outfits"]
        originals = {r["id"]: r for r in old_skins + old_outfits}
        if len({r["uuid"] for r in old_skins}) != 500: self.error("unique_npc_uuid", "source_npcs", "Original NPC manifest does not contain500 distinctUUIDs")
        rows = d.get("assets", [])
        self.unique_ids(rows, "characters", 600)
        if {r.get("id") for r in rows} != set(originals): self.error("character_identity_set", "characters", "IDs differ from original manifests")
        sys.path.insert(0, str(ROOT / "tools"))
        from gtm128_characters import BASE, OUTER, uv_mask, assembled, java64_export
        base_mask = uv_mask(BASE.values()); outfit_mask = uv_mask([v for k, v in OUTER.items() if k != "head"])
        unique = defaultdict(set); native_count = 0
        for r in rows:
            ident, kind = r["id"], r["kind"]
            if r.get("existing_record") != originals.get(ident): self.error("immutable_character_record", ident, "An existing ID/name/UUID/model/role/price/anchor record changed")
            if r.get("model") != originals.get(ident, {}).get("model"): self.error("immutable_character_model", ident, "Model assignment changed")
            for key, dim in (("master", [128, 128]), ("java_compatibility", [64, 64]), ("preview", [128, 128])):
                item = r[key]; self.png_file(item["path"], ident, dim, item["sha256"])
            p = self.output / r["master"]["path"]
            if not p.exists(): continue
            with Image.open(p) as source: im = source.convert("RGBA")
            with Image.open(self.output / r["java_compatibility"]["path"]) as source: compat = source.convert("RGBA")
            if im.tobytes() == compat.resize((128, 128), Image.Resampling.NEAREST).tobytes(): self.error("native128_character_detail", ident, "128 image is only a64 image enlarged")
            else: native_count += 1
            if java64_export(im).tobytes() != compat.tobytes(): self.error("character_derivation", ident, "64 export differs from defined UV-aligned reduction")
            alpha = im.getchannel("A").tobytes()
            if kind == "skin":
                if any(a != 255 for a, m in zip(alpha, base_mask.tobytes()) if m): self.error("opaque_character_base", ident, "Transparent mapped base skin pixel")
                if im.crop((96, 0, 112, 16)).getchannel("A").getbbox() is not None: self.error("cap_under_chin_uv", ident, "Head overlay bottom must remain clear for cropped caps")
            else:
                if any(a != 0 for a, m in zip(alpha, outfit_mask.tobytes()) if not m): self.error("outfit_layer_mask", ident, "Outfit paints head/base/unmapped pixels")
            unique[kind + "128"].add(hashlib.sha256(im.tobytes()).hexdigest())
            unique[kind + "64"].add(hashlib.sha256(compat.tobytes()).hexdigest())
        for key, target in (("skin128", 500), ("skin64", 500), ("outfit128", 100), ("outfit64", 100)):
            self.counts["distinct_" + key] = len(unique[key])
            if len(unique[key]) != target: self.error("character_unique_pixels", key, f"Expected{target}, got{len(unique[key])}")
        self.counts["characters_native128_verified"] = native_count
        for r in d.get("contact_sheets", []): self.png_file(r["path"], "character_contact_sheet", r["dimensions"], r["sha256"])

    def run(self):
        # Parse every exported JSON independently, including all model sources.
        for p in sorted(self.output.rglob("*.json")):
            rel = p.relative_to(self.output).as_posix()
            if rel != "reports/validation_128.json": self.load(rel)
        required = ("transport", "furniture", "festivals", "equipment_food", "finishes", "characters", "materials", "world", "phone", "hud", "brands", "signage", "identity")
        for name in required:
            self.load(f"manifests/{name}_128.json")
        self.material_records = {r["id"]: r for r in self.load("manifests/materials_128.json").get("materials", [])}
        for name, count, source, source_key in [
            ("transport", 87, "creative/manifests/transport_art_manifest.json", None),
            ("furniture", 200, "creative/manifests/furniture_art_manifest.json", None),
            ("festivals", 100, "creative/manifests/festivals_manifest.json", "festivals")]:
            records = self.load(f"manifests/{name}_128.json").get("assets", [])
            self.unique_ids(records, name, count); self.source_ids(records, source, source_key)
            for r in records: self.model(r)
        eq = self.load("manifests/equipment_food_128.json")
        for group, count in (("equipment", 92), ("food", 30), ("weapons", 30), ("hero_props", 11)):
            rows = eq.get(group, []); self.unique_ids(rows, group, count)
            if group == "equipment": self.source_ids(rows, "creative/manifests/equipment_manifest.json", "equipment")
            elif group == "food": self.source_ids(rows, "creative/manifests/food_manifest.json", "items")
            elif group == "hero_props": self.source_ids(rows, "creative/manifests/equipment_manifest.json", "hero_props")
            for r in rows: self.model(r, primary=group in ("equipment", "food"))
        additions_path = self.output / "manifests/festival_additions_128.json"
        if additions_path.exists():
            additions_manifest = self.load("manifests/festival_additions_128.json")
            additions = additions_manifest.get("assets", [])
            self.unique_ids(additions, "festival_additions", 28)
            added_themes = dict(Counter(r.get("theme") for r in additions))
            expected_added_themes = {"independence_day": 10, "monsoon": 10, "christmas": 4, "new_year": 4}
            if added_themes != expected_added_themes or additions_manifest.get("theme_counts") != expected_added_themes:
                self.error("festival_addition_theme_counts", "festival_additions", str(added_themes))
            for r in additions:
                if r["id"] in self.model_shapes: self.error("festival_addition_id", r["id"], "Addition conflicts with a preserved source ID")
                self.model(r, primary=False)
            self.counts["festival_additional_models"] = len(additions)
            selected_manifest = self.load("manifests/approved_festival_selection_128.json")
            selected = selected_manifest.get("selections", [])
            self.unique_ids(selected, "approved_festival_selection", 100)
            expected_themes = {"diwali": 12, "holi": 12, "navratri": 12, "christmas": 16, "new_year": 16, "independence_day": 10, "ganesh_chaturthi": 12, "monsoon": 10}
            selected_themes = dict(Counter(r.get("theme") for r in selected))
            if selected_themes != expected_themes or selected_manifest.get("theme_counts") != expected_themes:
                self.error("approved_festival_theme_counts", "festival_selection", str(selected_themes))
            legacy_festivals = {r["id"]: r for r in self.load("manifests/festivals_128.json").get("assets", [])}
            added_festivals = {r["id"]: r for r in additions}
            for r in selected:
                source = legacy_festivals if r.get("source") == "legacy" else added_festivals if r.get("source") == "addition" else {}
                if r["id"] not in source: self.error("approved_festival_reference", r["id"], "Selection does not resolve to its declared source group"); continue
                actual_theme = source[r["id"]]["theme"]
                actual_theme = {"ganesh": "ganesh_chaturthi", "new": "new_year"}.get(actual_theme, actual_theme)
                if r.get("theme") != actual_theme: self.error("approved_festival_theme", r["id"], f"Selection theme disagrees with its artwork: {actual_theme}")
            if set(selected_manifest.get("retained_legacy_ids", [])) != set(legacy_festivals):
                self.error("retained_festival_ids", "festival_selection", "All100 legacy festival IDs must remain retained")
            unselected = set(legacy_festivals) - {r["id"] for r in selected}
            if set(selected_manifest.get("unselected_legacy_ids", [])) != unselected or len(unselected) != 28:
                self.error("unselected_festival_ids", "festival_selection", "Expected28 unselected retained legacy designs")
            self.approved_festival_selection = selected
            self.counts["approved_festival_selection"] = len(selected)
        finishes = self.load("manifests/finishes_128.json")
        rows = finishes.get("mappings_128", []); self.unique_ids(rows, "finishes", 300)
        original_finish_mappings = strict_json(ROOT / "creative/manifests/finishes_migration.json")["mappings"]
        if finishes.get("mappings") != original_finish_mappings:
            self.error("original_finish_mapping_preserved", "finishes", "The original repository migration proposal was changed")
        old_mapping = {r["legacy_id"]: r for r in finishes.get("mappings", [])}
        preserved = []
        finishes_by_weapon = defaultdict(list)
        for r in rows:
            mapping = r.get("legacy_mapping", {})
            if mapping != old_mapping.get(mapping.get("legacy_id")): self.error("finish_mapping_preserved", r["id"], "Legacy mapping changed")
            preserved.append(mapping.get("legacy_id"))
            self.png_file(r["texture"], r["id"], [128, 128], r["sha256"])
            self.model(r, primary=False, finish=True)
            finishes_by_weapon[r["geometry_id"]].append(r)
        if len(set(preserved)) != 300: self.error("finish_legacy_bijection", "finishes", "Not300 distinct legacy IDs")
        if len(finishes_by_weapon) != 30: self.error("finish_weapon_count", "finishes", "Expected30 existing source models")
        for weapon, variants in finishes_by_weapon.items():
            if len(variants) != 10 or len({v["collection_id"] for v in variants}) != 10:
                self.error("finish_collection_count", weapon, "Expected ten distinct collection names")
            pixels = {self.png.get(v["texture"], {}).get("pixel_sha256") for v in variants}
            if len(pixels) != 10: self.error("finish_visual_uniqueness", weapon, "Collection textures are not ten distinct pixel images")
        state_path = self.output / "manifests/vehicle_states_128.json"
        if state_path.exists():
            states = self.load("manifests/vehicle_states_128.json").get("assets", [])
            self.unique_ids(states, "vehicle_damage_states", 195)
            road_ids = {r["id"] for r in strict_json(ROOT / "creative/manifests/transport_art_manifest.json") if r["category"] == "road"}
            parents = {r["id"]: r for r in self.load("manifests/transport_128.json").get("assets", [])}
            state_keys = set()
            for r in states:
                parent = r.get("parent_id"); state = r.get("state")
                if parent not in road_ids or state not in ("damaged", "critical", "wreck"):
                    self.error("vehicle_state_parent", r["id"], f"Unknown road parent/state: {parent}/{state}")
                if (parent, state) in state_keys: self.error("vehicle_state_unique", r["id"], "Duplicate parent-state combination")
                state_keys.add((parent, state))
                if parent in parents:
                    self.file(parents[parent]["geometry_path"], r["id"], r.get("normal_source_sha256"))
                    self.file(parents[parent]["editable_source"], r["id"], r.get("normal_editable_sha256"))
                self.model(r, primary=False, variant=True)
            if state_keys != {(p, s) for p in road_ids for s in ("damaged", "critical", "wreck")}:
                self.error("vehicle_state_coverage", "road_states", "Expected all65roads multiplied by three damage states")
        self.characters()
        catalogue = strict_json(ROOT / "docs/creative/CREATIVE_CATALOGUE.json")
        for name, count in (("phone", 24), ("hud", 33), ("brands", 32), ("identity", 4), ("signage", 120)):
            records = self.load(f"manifests/{name}_128.json").get("assets", [])
            ids = self.unique_ids(records, name, count)
            if name == "phone": wanted = {r["id"] for r in catalogue["phone_icons"]}
            elif name == "hud": wanted = {r["id"] for r in catalogue["hud_icons"]}
            elif name == "brands": wanted = set(catalogue["brands"])
            else: wanted = ids
            if ids != wanted: self.error("preserved_ui_ids", name, f"missing={sorted(wanted-ids)}, extra={sorted(ids-wanted)}")
            if name == "signage":
                self.source_ids(records, "creative/manifests/signage_manifest.json", "signs")
                old_signs = {r["id"]: r for r in strict_json(ROOT / "creative/manifests/signage_manifest.json")["signs"]}
            for r in records:
                self.png_file(r["png"], r["id"], r["dimensions_px"], r["sha256"])
                svg = self.file(r["svg"], r["id"])
                if svg:
                    try: ET.parse(svg)
                    except Exception as e: self.error("svg_parse", r["id"], str(e))
                for tile in r.get("tiles", []): self.png_file(tile["path"], r["id"], [128, 128], tile["sha256"])
                if name == "signage":
                    for label in ("english_text", "marathi_text"):
                        if r.get(label) != old_signs[r["id"]].get(label): self.error("sign_label_preserved", r["id"], f"Changed{label}")
                    if len(r.get("tiles", [])) != 2: self.error("sign_tile_count", r["id"], "Expected two native128 tiles")
                    else:
                        with Image.open(self.output / r["png"]) as im:
                            for tile in r["tiles"]:
                                x, y = tile["origin_px"]
                                with Image.open(self.output / tile["path"]) as tm:
                                    if im.crop((x, y, x + 128, y + 128)).tobytes() != tm.tobytes(): self.error("sign_tile_composition", r["id"], "Tile pixels differ from declared composite rectangle")
            self.counts[name + "_assets"] = len(records)
        materials = self.load("manifests/materials_128.json")
        rows = materials.get("materials", []); self.unique_ids(rows, "materials")
        for r in rows: self.png_file(r["path"], r["id"], [128, 128], r["sha256"])
        atlas = materials.get("atlas", {})
        self.png_file(atlas["path"], "master_atlas", atlas["size_px"], atlas["sha256"])
        if atlas.get("cell_px") != [128, 128]: self.error("atlas_cell", "materials", "Material atlas tiles are not128x128")
        seen_cells = set()
        standalone_tiles = []
        with Image.open(self.output / atlas["path"]) as atlas_im:
            for r in rows:
                if r.get("atlas_cell") is None:
                    standalone_tiles.append(r["id"])
                    continue
                cell = tuple(r.get("atlas_cell", []))
                if len(cell) != 2 or cell in seen_cells or any(v < 0 or v >= 16 for v in cell):
                    self.error("material_atlas_cell", r["id"], f"Invalid or reused atlas cell{cell}"); continue
                seen_cells.add(cell); x, y = (v * 128 for v in cell)
                with Image.open(self.output / r["path"]) as tile:
                    if atlas_im.crop((x, y, x + 128, y + 128)).tobytes() != tile.tobytes(): self.error("material_atlas_pixels", r["id"], "Atlas cell pixels differ from material tile")
        self.counts["material_tiles"] = len(rows)
        self.counts["material_tiles_bound_to_atlas"] = len(seen_cells)
        self.counts["standalone_material_tiles"] = len(standalone_tiles)
        world = self.load("manifests/world_128.json").get("textures", [])
        self.unique_ids(world, "world", 98)
        for r in world: self.png_file(r["path"], r["id"], [128, 128], r["sha256"])
        self.counts["world_textures"] = len(world)
        # Inventory all PNGs, applying only explicit exceptions to128px sources.
        size_counts = Counter(); modes = Counter()
        for p in sorted(self.output.rglob("*.png")):
            rel = p.relative_to(self.output).as_posix()
            info = self.png_file(rel, rel)
            if not info: continue
            size = info["size"]; size_counts[f"{size[0]}x{size[1]}"] += 1; modes[info["mode"]] += 1
            if rel.startswith("previews/"): continue
            if rel.startswith("compatibility/java64/"):
                if size != [64, 64]: self.error("java_skin_dimensions", rel, str(size))
            elif rel == "source/branding/core/server-icon.png":
                if size != [64, 64] or info["mode"] != "RGB": self.error("server_icon_exception", rel, "Must be64x64 opaqueRGB")
            elif rel == atlas.get("path"):
                if size != atlas.get("size_px"): self.error("atlas_dimensions", rel, str(size))
            elif rel.startswith("source/signage/") and "_tile_" not in rel:
                if size != [256, 128]: self.error("sign_composition_dimensions", rel, str(size))
            elif rel.startswith("source/") and size != [128, 128]:
                self.error("native128_source_dimensions", rel, f"Unexplained size exception {size}")
            if rel.startswith("source/") and rel != "source/branding/core/server-icon.png" and info["mode"] != "RGBA":
                self.error("source_rgba", rel, str(info["mode"]))
        self.counts["png_files"] = len(self.png); self.counts["json_files"] = len(self.parsed)
        self.counts["resolved_active_paths"] = len(self.active_paths)
        primary_dupes = [v for v in self.primary_shapes.values() if len(v) > 1]
        additional_dupes = [v for v in self.additional_shapes.values() if len(v) > 1]
        if primary_dupes:
            self.warning("duplicate_primary_geometry", "primary_catalogue", f"509 IDs resolve to{len(self.primary_shapes)} exact static cube definitions;{len(primary_dupes)} duplicate groups. Do not describe the catalogue as509 unique3D designs.")
        if self.rotation_approximations:
            self.warning("java_rotation_approximations", "models", f"{len(self.rotation_approximations)} model exports declare rotation approximations; actual crossplay appearance must be inspected in clients.")
        self.warning("runtime_and_client_gate", "release", "Static source validation only. Engine binding, actual Java/Bedrock clients, signed NPC skins, gameplay, physics, world placement and deployment remain unverified.")
        report = {
            "schema_version": 1, "status": "FAIL" if self.errors else "PASS_WITH_WARNINGS" if self.warnings else "PASS",
            "scope": "isolated generated128 source art; no production or live-world changes",
            "counts": dict(self.counts), "image_sizes": dict(size_counts), "image_modes": dict(modes),
            "resolution_policy": {"native_masters": [128, 128], "java_skin_outfit_compatibility": [64, 64], "server_icon": [64, 64], "sign_composites": [256, 128], "master_atlas": atlas.get("size_px"), "previews": "contact-sheet layouts; native character previews128x128"},
            "geometry_audit": {"primary_catalogue_ids": sum(len(v) for v in self.primary_shapes.values()),
                "primary_exact_geometry_definitions": len(self.primary_shapes), "primary_duplicate_groups": primary_dupes,
                "additional_source_ids": sum(len(v) for v in self.additional_shapes.values()),
                "additional_exact_geometry_definitions": len(self.additional_shapes), "additional_duplicate_groups": additional_dupes,
                "approved_festival_selection_exact_definitions": len({self.model_shapes.get(r["id"]) for r in self.approved_festival_selection}) if self.approved_festival_selection else None,
                "finish_variants_are_not_unique_geometry": True,
                "method": "Sorted cube origins/sizes/rotations/pivots plus nonzero bone transforms; names, UVs, materials and colors ignored. Exact difference is not proof of meaningful artistic uniqueness."},
            "rotation_approximations": self.rotation_approximations,
            "reference_policy": "All active export paths and declared hashes resolved under this bundle. Existing_record/legacy_mapping/source_recipe references are retained provenance into the original repository, not new runtime or bundle asset bindings.",
            "standalone_material_tiles": standalone_tiles,
            "errors": self.errors, "warnings": self.warnings, "client_verification": "NOT_RUN", "runtime_integration": "PENDING",
            "reproduce": "python tools/gtm128_validate.py --output creative/generated_128"
        }
        destination = self.output / "reports/validation_128.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "counts": report["counts"], "errors": self.errors[:25], "error_count": len(self.errors), "warnings": self.warnings, "primary_geometry_definitions": len(self.primary_shapes)}, indent=2))
        return report


def validate(output): return Validator(output).run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "creative/generated_128")
    args = parser.parse_args()
    report = validate(args.output)
    raise SystemExit(1 if report["errors"] else 0)
