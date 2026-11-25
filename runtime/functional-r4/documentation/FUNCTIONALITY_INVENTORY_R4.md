# Reading and reproducing the functionality inventory

The [canonical CSV](reports/PRIMARY_MODEL_FUNCTIONALITY_R4.csv) records one row per actual runtime asset ID. Its [JSON manifest](reports/PRIMARY_MODEL_FUNCTIONALITY_R4.json) records count reconciliation, exact source/report hashes, reviewed server-effect evidence and configuration provenance. The historical filename is retained; the scope is now **1,155 canonical assets**, including the original **509** designs.

| Disjoint group | Canonical rows |
|---|---:|
| Primary and additive placeable furniture | 358 |
| Native transport | 87 |
| Other equipment | 103 |
| Food | 30 |
| Outfits | 100 |
| Signs | 120 |
| UI artwork and controls | 57 |
| Owned weapon finish cosmetics | 300 |
| **Total** | **1,155** |

Thirty equipment IDs also appear in the additive placeable registry. Each appears once in the export, with both roles on that row. The 133 equipment registry memberships therefore do not add 133 new rows beside all furniture. The 300 finish cosmetics reuse existing weapon geometry. Vehicle damage states, articulated partitions, held/world variants, technical cart/buoy/hoist components, outfit pieces, compatibility skins, atlas cells and pack exports are not extra unique designs.

## Operational models, structures and ornaments

The inventory does not count every visible object as an operated machine. **52 furniture assets have an ornamental placement role**: 49 extension designs and three primary designs. Their ownership, placement and retrieval controls work, while their declared purpose remains visual. `ORNAMENTAL_PLACEMENT` identifies these rows explicitly; decorative animation or a menu does not establish another named function.

The **27 exact structural assignments** are tracked separately. They use authored rigid collision, usable openings or a real owner-built stage floor. Their full property envelopes remain reserved, and old miniature placements require deliberate owner recommissioning before the larger geometry can appear. The actual 38-check scenario exercised six representative models and seven received protocol walks; source/resource geometry checks cover all 27 blueprints. It does not claim an individual native-client walk for every theme. A structural assignment is not evidence of rain protection, a supplied stage floor or a food counter unless that exact additional action is separately declared and tested. The tarp row therefore retains both its structural proof and its separately observed paid-food-counter proof.

Three titles need particularly clear limits. The heritage podium is a ceremony lectern ornament whose microphone accessory has no live speech relay. The shelter umbrella has a low canopy and supplies no upright walk-in space or precipitation shielding. The monsoon chai rain shelter is tea-counter artwork with cup meshes; it does not dispense food, supply stock or alter weather. These limits follow the authored models and are retained on their individual rows.

## Enablement and actual use are separate facts

`default_enabled` reads only the conservative base source configuration. It is not a statement about the packaged laptop profile. `laptop_profile_enabled` separately evaluates the exact explicitly supplied built configuration; `laptop_profile_basis` lists the required boolean values and furniture service category. Without that configuration, the value is `not_evaluated`, even when source defaults are all disabled.

For an ID with distinct placed and held roles, either enabled role can make its profile flag true; the basis preserves the two alternatives. Ticket validators and their linked turnstiles require the transport category; parking requires its category and native vehicles; supplied workshop machines require the native vehicle runtime. A globally enabled furniture flag does not substitute for a disabled required category.

`laptop_profile_conditions` and `remaining_work` retain the actual prerequisites: normal authentication and permission, paid ownership, permitted loaded geometry, real ingredients/fuel, an existing compatible backing, a commissioned route/camera/bay/link when applicable, and matching packs. A true configuration flag does not prove those objects have already been installed everywhere in the city. Account authority, source data, item supplies or world commissioning are never inferred from enablement alone.

## What verification means

Each named actual-Paper effect is linked to its own complete report, check count, report digest and tested core digest. A report must contain all expected passing records and no unexecuted steps. A fixture scenario also requires clean restoration of its declared scope. Ordinary paid scenarios instead retain their purchased progress and require explicit evidence that no fixture blocks or permission/item/money grants were supplied. The wheelchair has an ordinary paid 22-check scenario and six-check protocol continuation; its earlier failed cohort remains a separate historical file.

The shopping-cart row has an explicitly completed sequential chain on the same paid account, furniture, loan, receipt and food order. Its final four-check ordinary Return report completes the retained purchase/movement/output/verification history. All five earlier failed stages remain visible, with each raw digest and actual tested core. The generator requires the closed loan, committed released receipt, empty source, one complete original native item at the destination, unchanged paid balance and zero grants or fixture writes. It does not convert that history into an uninterrupted 50-check pass.

The nine festival carts have a separate complete **129-check ordinary paid report**. Each original model was purchased, moved and turned under its owning account; no second entitlement or cart loan was created. The gift cart also carried the previously purchased native food item through the shared custody mechanism exactly once. The report independently checks full item equality, empty source, one destination stack, released receipt and replay refusal. The other eight carts use that source-reviewed cargo implementation; their individual loaded transfers are not claimed as separately observed. The generator requires all nine paid identities, nonzero actual movement for each and the retained no-grant conservation evidence.

The complete 28-check workshop report has an explicit cleanup boundary. It restored its own workshop fixture in the retained-state recovery copy. The unrelated interrupted festival journal, pending marker, before-state file and report remained unchanged. The inventory validates that boundary and does not turn a workshop pass into a whole-world restoration claim.

The seasonal-function report completed all **85 checks**, including actual world-clock and weather readouts, emitted and propagated block light at each of five backings, and nine separate paid/prepared/collected/consumed food orders. Its earlier interrupted 80-check report remains unchanged and incomplete. The completed seasonal and structural runs used an explicit Java-only server configuration with optional crossplay plugins excluded; normal Java authentication and identity rules remained intact. Installed pack hashes are input provenance, not a claim that those runs tested Bedrock connectivity or native rendering.

The generator accepts the existing report schemas' `result` or `status` fields, but rejects conflicting values, partial checks, dirty cleanup and an unreviewed replacement report. A new passing report cannot inherit an earlier core hash merely by taking the same filename. Current source hashes and older tested core hashes remain separate provenance; an old report is not relabeled as a test of a new binary.

`SERVER_ACCEPTANCE_PENDING` marks a source assignment whose named live effect has not yet passed. `IMPLEMENTED_CONDITIONAL` and `SERVICE_CONDITIONAL` preserve their actual setup limits after that effect is observed. A server-side map raster is not a native client screenshot. `native_client_verified` remains false unless that exact asset receives separate native Java and Bedrock evidence. Fixed-screen HUD positions, full city furnishing, Windows execution and arbitrary hard-crash durability are not implied by server/API acceptance.

## Reproduction

Use the exact reviewed built `plugins/SDCraftCore/config.yml` when generating the final laptop inventory:

```sh
python tools/build_functionality_inventory.py --profile-config /path/to/reviewed/plugins/SDCraftCore/config.yml
python tools/build_functionality_inventory.py --check --profile-config /path/to/reviewed/plugins/SDCraftCore/config.yml
python tools/test_functionality_inventory.py
```

The manifest records the supplied path and its SHA256 without exporting arbitrary configuration values. The generator requires the canonical counts and intentional overlaps to reconcile and hashes all referenced Java sources and registries. Regenerate after the final core sources and approved named reports have stabilized. The focused inventory suite checks canonical identity, report-specific cores, current wheelchair evidence, the completed cart chain with preserved failures and custody conservation, all nine paid festival-cart identities and actual movement, real seasonal food/light/readout effects, representative structural scope and nonteleport walking, the tarp's two separate capabilities/proofs, the workshop's limited cleanup boundary, unknown profile handling, real boolean parsing, category gates, explicit ornamental roles and the distinction between enabled flags and commissioned gameplay.
