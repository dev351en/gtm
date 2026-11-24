# Creative data contract v1 — proposed interchange, not a live runtime API

The engine agent will review these data formats before adding runtime loaders. Do not change existing Java signatures or register new IDs from this document automatically. All positions in a structure or asset manifest are local unless explicitly identified as surveyed world coordinates. Use lowercase snake_case names and stable identifiers, no guessed live coordinates.

## Paths
Proposed art workspace: creative/source/{models,textures,skins,outfits,icons,branding,signage,ui,structures}/, creative/manifests/, creative/previews/, creative/reports/. Existing tools/city_*_art.py and tools/build_*_packs.py are the legacy export pipeline; prefer adding an isolated art-only importer rather than changing runtime registries. Generated binaries may be delivered as separate validated packs, not repeated in git; source and manifests must be versioned. Use relative paths inside bundle. Never reference files outside the asset workspace or include secrets.

## Existing exact pack contract
- Current model IDs from gtm-city-models.tsv (479) and FoodCatalogue.java (30) are enumerated in CREATIVE_CATALOGUE.json. Java food base minecraft:bread; city base minecraft:paper. Actual runtime item_model is gtm:<id>.
- Java item definition assets/gtm/items/<id>.json points to gtm:item/<id>, mesh assets/gtm/models/item/<id>.json, PNG under assets/gtm/textures/. Use valid installed target pack metadata; confirm version range against actual target rather than assuming old README values are current.
- Bedrock models/entity/*.geo.json geometry identifier geometry.gtm.<id>, attachables/<id>.json with identifier gtm:<id>, valid render controller, texture atlas, textures/items/gtm_<id>.png and textures/item_texture.json. Existing Geyser v2 mapping maps base item to a definition with model and bedrock_identifier both gtm:<id> and bedrock_options.icon gtm_<id>. Retain actual installed mapping conventions; no conflicting global IDs.
- Existing exporter accepts parts as (palette swatch, x,y,z,width,height,depth) inside 0..16; shared atlas 32×32 and existing icon export 48×48. For advanced full-size assets, separate editable geometry plus local block dimensions and anchors. Existing checker expects equal cube/element counts and single-bone geometry; do not bypass it when introducing articulated models. Add an art-only validator for proposed multi-bone assets and mark pending engine adaptation.
- Reproduce:
  python tools/build_food_packs.py <output>
  python tools/build_finish_packs.py <output>
  python tools/build_city_packs.py <output>
  python tools/check_client_packs.py <output>
  python tools/generate_npc_assets.py --output <output>
  Inspect each script's current CLI before running; no production destinations.

## Example model art manifest (illustrative values only)
```json
{
  "schema_version": 1,
  "asset_id": "gtm:scooter_city",
  "category": "road",
  "status": "draft",
  "source": "source/models/scooter_city.bbmodel",
  "base_item": "minecraft:paper",
  "java_item": "assets/gtm/items/scooter_city.json",
  "bedrock_geometry": "geometry.gtm.scooter_city",
  "icon": "source/icons/scooter_city.png",
  "dimensions_blocks": [0.8, 1.4, 1.9],
  "local_axes": "x right, y up, z forward; verify adapter conversion",
  "anchors": [{"id": "driver_seat", "position": [0,0.8,0], "yaw": 0}],
  "pivots": [{"id":"front_wheel","position":[0,0.3,0.6]}],
  "collision_boxes": [{"min":[-0.4,0,-0.95],"max":[0.4,1.4,0.95]}],
  "variants": ["normal","damaged","critical","wreck"],
  "license": "original; author and redistribution permission recorded in manifest",
  "engine_binding": "review_required"
}
```
Do not treat sample dimensions as approved physical values. Render scale, axes, pivots, seat count and collision must match the specific model. Use art variants only; no real-world construction specs or gameplay values.

## Example structure manifest
```json
{
  "schema_version": 1,
  "structure_id": "bank_01",
  "facility_id": "bank_01",
  "status": "survey_required",
  "source_world_sha256": null,
  "world": null,
  "world_origin": null,
  "local_bounds": {"min":[0,0,0],"max":[15,8,19]},
  "rotation_degrees": 0,
  "schematic": null,
  "entrances": [{"id":"main_entrance","local":[7,0,0],"access":"public"}],
  "rooms": [{"id":"lobby","function":"public_service","local_bounds":{"min":[1,0,1],"max":[14,4,18]},"access":"public"}],
  "placements": [{"asset_id":"gtm:filing_cabinet_metro","local":[4,0,8],"yaw":90,"role":"storage"}],
  "service_anchors": [],
  "protected_regions": [],
  "checks": {"floor_and_headroom":"pending","navigation":"pending","collisions":"pending","visual_review":"pending"},
  "rollback": null
}
```
This is a hypothetical sample only; never place it without survey. When surveyed, bind source hash, world, origin, rotation, inclusive bounds, schematic or patch hash, block change manifest and rollback. Export actual Minecraft blocks as .schem/.nbt or verified offline patch in addition to JSON metadata; JSON alone is not a loadable world. Existing structures need stable ID, condition, purpose, floor plans, room connections, ownership/public access, furnishing placements and checked entrances. Do not store real player access keys in art files.

## Icon and signage manifests
```json
{
  "schema_version": 1,
  "id": "app_zomatoo",
  "kind": "phone_icon",
  "source_svg": "source/icons/app_zomatoo.svg",
  "png": "source/icons/app_zomatoo.png",
  "size_px": [64,64],
  "alpha": true,
  "theme": "normal",
  "label": {"en":"Zomatoo","hi":"ज़ोमैटो"},
  "status": "draft"
}
```
Use original SVG source and power-of-two raster sizes where practical, 64×64 app master and 32×32 preview. Server icon 64×64 RGB opaque; skins 64×64 RGBA classic/slim, fully covered base surfaces, transparent outer layers where intended. Signs use chosen aspect ratio and 128–512 px native raster size as a starting budget, readable at in-world viewing distance. Sign records add semantic role, local placement anchor, orientation, dimensions_blocks, English/Hindi label, normal artwork, festival artwork IDs and optional dynamic display surface. Actual bitmap pixels are PNG, not JSON.

## NPC/outfit identity record
Fields: existing_npc_id, existing_uuid (if runtime defines one), role, skin_path, model classic/slim, license, preview_path, optional outfit_id. The 400 surveyed extra NPC IDs and UUIDs in the queue are immutable; derive remaining 100 IDs from actual legacy registry, not ordinal guesses. Outfit slots are proposed IDs and do not confer permissions. Keep runtime skin binding and authentication separate.

## Festival placement record
Fields: festival_id, structure_id, placement_id, asset_id, local_position, yaw, normal_asset_id or null, sign_swap_ids, restore_method, collision_check, source_world_hash. Manual activation only. Preserve normal-state visuals; do not overwrite player property or remove ordinary blocks. No unverified world coordinates.

## Validation evidence
Each output entry must record relative file paths, SHA-256, size, source author/rights, status (draft, art_validated, engine_binding_pending, client_verified, blocked), render evidence and actual checks. Use a separate legacy_id -> proposed_id migration table with explicit rationale; no deletion or reassignment of existing IDs without engine review. Never mark creative assets as working physics, banking, NPC behavior or deployed gameplay.
