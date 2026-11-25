# Walkable gateways, arches, bandstands and the market counter

The 27 reviewed structural models now use their authored posts, beams, platforms and counters as separate collision volumes. Their openings remain traversable. The complete rendered envelope still has to fit loaded, accessible, owned space on a safe real foundation. This change retains every canonical model ID, ownership ID, source primitive, original UV and native 128-pixel texture cell.

## Place and use a structure

Buy the original named model through the ordinary furniture shop. Open your owned furniture, choose **Place**, and aim at the top of a nearby solid floor. The entire structure must fit your property, including its height, any real connected backing block and the supporting floor. A clear 16 × 16 yard can accommodate each reviewed footprint if its full height is available; the original 8 × 8 starter workshop cannot accommodate the large festival structures.

For gateways and arches, approach the actual left support post to use the controls, rotate or retrieve the placement. The small clickable control sits on that post. Each action checks your current authenticated session, permission, ownership, distance and unobstructed sight line to that actual point. A large arch's centre is several blocks from its post; opening a menu remotely does not authorize a later action.

People and vehicles still collide with actual rigid supports. The central opening is not filled with a rectangular collision box. Rotation transforms the rendered structure, every physical primitive, the control point and the full ownership footprint together. An obstructed or inaccessible proposed rotation is refused without changing the saved placement.

The native midnight arch keeps its real light function: connect an existing owned dry `LIGHT` block before placing it, then use its light switch or brightness control. The connection reserves that exact real block; removal and disconnection restore its original state. Decorative display glow is separate from actual emitted world light.

## Exact reviewed models and dimensions

Dimensions are in world blocks: width × height × depth, in the default orientation. Rotating 90° exchanges width and depth. The eight legacy themes use the same authored frame families with their original theme decorations.

| Theme | Gateway, 12.8 × 10.2 × 2.7 | Street arch, 14.8 × 13.5 × 2.7 | Bandstand, 14 × 12.7 × 6 |
|---|---|---|---|
| Diwali | `gtm:diwali_gateway` | `gtm:diwali_street_arch` | `gtm:diwali_bandstand` |
| Holi | `gtm:holi_gateway` | `gtm:holi_street_arch` | `gtm:holi_bandstand` |
| Ganesh | `gtm:ganesh_gateway` | `gtm:ganesh_street_arch` | `gtm:ganesh_bandstand` |
| Navratri | `gtm:navratri_gateway` | `gtm:navratri_street_arch` | `gtm:navratri_bandstand` |
| Eid | `gtm:eid_gateway` | `gtm:eid_street_arch` | `gtm:eid_bandstand` |
| Sankranti | `gtm:sankranti_gateway` | `gtm:sankranti_street_arch` | `gtm:sankranti_bandstand` |
| Christmas | `gtm:christmas_gateway` | `gtm:christmas_street_arch` | `gtm:christmas_bandstand` |
| New Year | `gtm:new_year_gateway` | `gtm:new_year_street_arch` | `gtm:new_year_bandstand` |

| Additional exact model | Full dimensions | Physical behavior |
|---|---|---|
| `gtm:independence_day_civic_gateway` | 3 × 2.25 × 0.625 | Original native size; nine rigid authored base/post/header cubes. The opening has 1.875 blocks of rigid headroom. Flexible hanging decorations remain visible and nonblocking. |
| `gtm:new_year_midnight_light_arch` | 2.875 × 2.4375 × 0.5625 | Original native size; eleven rigid authored cubes with a clear upright centre opening. Flexible lights remain visible and nonblocking. Its reserved native `LIGHT` provides the actual light output. |
| `gtm:street_market_tarp` | Approximately 2.45 × 2.25228 × 2.39752 | All seven source primitives remain physical, including the 2.25 × 0.924 × 2.15 solid counter, four posts, sloped roof and counter detail. Approach the front edge for the real paid food workflow. |

The market tarp is an actual vendor counter. It has real priced food ordering, finite stock, preparation and owner collection through the existing food service. Its solid counter is not hollowed out. Its item-display roof does not create native weather-blocking blocks, so this model makes no rain-protection claim. The paid food lifecycle is qualified separately in the [festival functions guide](FESTIVAL_FUNCTIONS_R4.md).

## Build a real bandstand floor first

Each bandstand requires **78 existing full solid blocks**, a 13 × 6 rectangle, whose top matches the authored platform. Accepted floor materials include stone, smooth stone, cobblestone, stone bricks, bricks, deepslate bricks, polished andesite, full concrete blocks and full planks. Hazardous, partial, liquid, missing or misaligned floor cells are refused.

The platform top is 3.2 blocks above the model's base. Ordinary placement targets that real floor top, then derives the base and half-cell alignment from the same blueprint used for rendering and collision. It does not manufacture a platform, debit invented supplies, hold the player in the air or teleport the player onto the stage. Build ordinary access steps outside the structure's full envelope. Keep the spaces under and around the authored platform clear except for its required native floor and foundation; additional blocks in that reserved volume can obstruct placement.

For the paid laptop depot, the original deck has its walking surface at **y64**. Placing a stage with its platform top at y64 would push its body below the reviewed owned volume and into the existing waterfront. An example that fits the depot yard is:

| Part | Exact location |
|---|---|
| Model anchor, default orientation | `(-120.5, 63.8, -120)` |
| Actual platform blocks | x `-127..-115`, z `-124..-119`, y `66` — 78 blocks |
| Actual walkable platform top | y `67` |
| Full stage envelope | x `-127.5..-113.5`, y `63.8..76.5`, z `-124..-118` |
| Suggested aiming block | Top of `(-121, 66, -120)` |

Build and approach the actual floor with ordinary supplied blocks and safe stairs. The existing depot deck is the full lower foundation. No automatic profile/world patch supplies this stage floor. Other already built solid floors can be used when their full matching platform, lower foundation, access and ownership volume satisfy the same checks.

Removing or changing a required floor cell suspends the model's projection and usable controls while retaining its exact owned placement. Restoring the same valid support allows the ordinary loaded-world reconciliation to reconstruct it. A failed reconstruction never moves the structure or discards its entitlement.

## Existing saved miniatures

The original 24 legacy festival gateway/arch/bandstand meshes were previously placed at miniature scale even though their source manifests specified the much larger structural dimensions above. Their old nearby placements must not silently expand into one another.

The existing furniture aggregate now writes **FUR3** with an explicit per-entitlement geometry revision, and still reads FUR1/FUR2. Those old 24 placed miniatures load with their original small envelopes, original UUIDs, owner, pose, binding and settings. They remain safely suspended and retrievable. Their owner menu explains that recommissioning is required.

To use the full structure, approach the old saved location, remove the placement through the ordinary controls, then deliberately place that same owned model in a suitable clear property. Only this successful new placement selects the current geometry revision. Failed placement, stale storage writes and unrelated settings edits do not upgrade, relocate or delete the old instance. The later Independence gateway, midnight arch and market tarp retain their original physical size.

## Geometry and native 128 provenance

The exact 24 legacy manifest `placement_bounds` match their raw source cube dimensions after the reviewed unit conversion and subtraction of the original one-unit ground offset. The technical item meshes use scale 16 to reproduce those intended dimensions. The later three models use half-size technical meshes and scale 2, preserving their existing physical size. This conversion is restricted to the 27 exact IDs above.

Each technical selector is `gtm:fs_` followed by the original canonical slug. Java and Bedrock meshes preserve every source cube, pivot, rotation and UV, and reuse the original 2048 × 2048 atlas and 128 × 128 icon bytes. The atlas still contains the original 16 × 16 grid of native 128-pixel cells. These 27 selectors are runtime parts, excluded from the ordinary staff paper catalogue; they are not new canonical assets or new painted designs.

The single generated structure blueprint supplies rendering scale, complete ownership bounds, physical solids, control point, optional platform cells and original source geometry digest. Primitive AABBs conservatively enclose authored rotations. Rigid and flexible parts of the two later arches are explicitly enumerated; flexible decorations are still rendered.

The source-checkout implementation and regeneration tools are `tools/gtm_structure_geometry.py`, `tools/gtm_structure_runtime_assets.py` and `tools/test_structure_runtime_assets.py`. Their relative source paths are not runtime files in the laptop documentation package.

## Qualification and scope

The coherent source gate passed **167 cases in 18 suites**, including eight structural geometry cases and six FUR1/FUR2/FUR3 migration cases, with no failures, errors or skips. Six Python structure tests verify the exact allowlist, both platform meshes, source primitive/UV equivalence, unchanged texture/icon bytes, reviewed solid indices, runtime-only catalogue classification and all 27 actual Bedrock display bindings. These passed within the final 24-case combined pack gate.

The actual tested sealed core `b7c76cd3a664e1bb7e1e56fd2098f7ef0a71e921d47170ed10c4e658974715af`, from source snapshot `8df6f572928534b3e857dde033acb0a5b0afe3680817950505d23e34b9fc3e06`, passed **644 Java cases in 79 suites plus 155 domain assertions**, with zero failures, errors or skips. Its registry contains 3,554 bindings, including the 27 additional structural runtime selectors. The evidence retains the earlier 639-case structural build as historical provenance.

The [actual Paper report](reports/PAPER_FURNITURE_STRUCTURES_R4.json) records **38 passes: 37 scenario checks and complete fixture cleanup**, with no failed or unexecuted structure steps. Run `20261125T024626783921Z` used Paper 26.3 build 255, this exact core and a normally authenticated Java protocol client. Six representative models were placed: the Diwali gateway, street arch and bandstand, Independence gateway, midnight light arch and market tarp. The remaining themes share the exact tested blueprint families and are covered by source/resource checks; they were not each individually walked in this runtime scenario.

Seven walks covered the gateway, both later arches, full-size street arch, stage entry, stage floor and rotated arch. Paper received **256 movement events over 38 blocks**, with no teleport events during those measured walks and a maximum step of approximately 0.15 blocks. The same scenario observed real light levels changing to 9, off and back to 9; post-local control and current permission/sight checks; preserved settings after stale callbacks; ordinary rotation; a fresh FUR3 reader; and suspension followed by normal reconstruction when one real platform cell was removed and restored. The counter remained solid while exposing its actual food-service approach point. Its separate paid ordering, preparation, collection and consumption evidence is in the [85-pass festival report](reports/PAPER_FESTIVAL_FUNCTIONS_R4.json).

This was an explicit **Java-only gameplay run**. The exact pinned Geyser and Floodgate JARs were preserved outside plugin admission; normal Java authentication and identity rules stayed active. The Java pack hash was `5b5e132a2c670b07e8c0c389e086bd2dee1002ed7de72a6bdcd93acc6d6cba9a`. The preserved Bedrock pack was `d02cc8f41f6f97799dedab824b6fd23049c01556475e0031a50824543b507aab`, and the corrected display-mapping file was `c9e7b290e689b4cc77862d68bce7fe3c0c02e0b4aaa748eaaed60d8f0965cc09`, including all 27 structural selectors among 1,934 display mappings. Those preserved inputs establish pack provenance; this Java-only run did not exercise their Bedrock runtime. The [component evidence record](reports/FURNITURE_STRUCTURES_R4_EVIDENCE.json) contains the exact raw-report, companion, input-manifest, mapping and harness hashes.

The later ottoman scenario in this same multi-scenario batch failed after these structure checks completed. The 38-pass structure result and its cleanup are retained without relabeling the whole batch as successful.

The real protocol walks demonstrate server-received continuous movement on existing native floor blocks. Test grants, explicit setup positioning, journaled fixture blocks, private menu opening and negative injected guard events are separately identified test scaffolding. This evidence does not certify native Java/Bedrock rendering, human-operated input, every unique theme in a real client, physical rain shielding or hard-power-loss durability.
