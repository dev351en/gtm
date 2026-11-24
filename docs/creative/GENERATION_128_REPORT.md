# GTM / Indraprastha — native 128 generation report

**Checkpoint:** 25 November 2026  
**Profile:** `INDRAPRASTHA_128_V1`  
**Output root:** `creative/generated_128`  
**Result:** Asset generation and static validation complete; live client, runtime integration, world placement and deployment remain unverified.

The batch contains native 128×128 art masters, editable model sources, Java/Bedrock exports, compatibility derivatives, manifests and review previews. It preserves the established source IDs and NPC identity records. The [source validation report](../../creative/generated_128/reports/validation_128.json) records **zero errors** and `PASS_WITH_WARNINGS`; its one warning is the unrun client/runtime gate. The [pack validation report](../../creative/generated_128/reports/pack_validation_128.json) records **zero errors**, **1,073 model pairs**, **1,103 resolved item definitions** and **171,492 Java texture-face references**.

These results describe generated art and static package consistency. They do not establish a playable Revision 4 release.

## 1. Persistent design rule

The [design language](DESIGN_LANGUAGE_128.md) and [machine-readable profile](../../creative/design_language_128.json) govern future generation. New square texture, icon, NPC skin and outfit masters are authored at **128×128**, with actual detail on that grid. A smaller bitmap enlarged to 128 pixels does not meet the profile.

| Output | Resolution and meaning |
|---|---|
| Square texture, model icon, UI/identity, skin and outfit master | 128×128 native artwork |
| Shared model atlas | 2048×2048 container; 16×16 cells of 128×128, with a capacity of 256 slots |
| Java skin/outfit compatibility derivative | 64×64, with the body UV layout and intentional outer-layer transparency retained |
| Server-list icon | 64×64 opaque compatibility export from its 128 master |
| Bilingual sign | One 256×128 composite assembled from two native 128×128 tiles |
| Contact sheets and direction boards | Variable preview layouts; not additional designs |

The graphite, ARK gold, emerald, sandstone and terracotta palette remains the shared identity. Material and subject colours still serve the object: readable food, recognizable transport liveries, occupational clothing and theme-specific festival art. Existing source IDs, defined NPC UUIDs, classic/slim assignments and legacy records are preserved. Export paths and proposals do not create new runtime identity bindings.

## 2. Model count reconciliation

One model pair means the Java and Bedrock export of one art record. Counting both platform files as separate designs would double the inventory incorrectly.

| Group | Model pairs | Counting rule |
|---|---:|---|
| Primary transport | 87 | Existing primary source IDs retained |
| Primary furniture | 200 | Existing primary source IDs retained |
| Primary equipment | 92 | Existing primary source IDs retained |
| Primary festivals | 100 | All legacy festival art retained |
| Primary food | 30 | Existing food art IDs retained |
| **Primary subtotal** | **509** | The original catalogue boundary remains fixed |
| Existing weapon-source IDs | 30 | Includes melee/special props; not 30 verified firearms |
| Hero props | 11 | Additional source records |
| Festival additions | 28 | Added to meet the approved selection while preserving legacy art |
| **Additional subtotal** | **69** | Separate from the 509 primary models |
| Road damage variants | 195 | 65 road parents × damaged, critical and wreck states |
| Cosmetic finish variants | 300 | Finish exports share underlying geometry |
| **Total exported model pairs** | **1,073** | 509 + 69 + 195 + 300 |

The package resolves **1,103 item definitions** because it includes the 1,073 art/variant definitions plus **30 exact food runtime aliases**. For example, `gtm:chai` resolves to the preserved art ID `gtm:food_chai`. Aliases do not add geometry or new designs. Road, furniture and finish migrations remain review proposals; the pack report labels runtime mapping `proposal_only_not_installed`.

### Geometry uniqueness has a precise scope

The source validator finds **509 exact geometry definitions for the 509 primary IDs**, with no exact duplicates in that group. For the **69 additional IDs**, it finds **55 exact definitions and seven duplicate groups**. Those groups, recorded with full IDs in the source report, involve existing weapon-source records. They have not been concealed by counting colour changes as new geometry.

The geometry fingerprint compares sorted cube origins, sizes, rotations and pivots, plus nonzero bone transforms; it ignores labels, UVs, materials and colours. A different fingerprint is evidence of a coordinate difference, not proof that two objects are meaningfully different artistic designs. The 300 finishes are explicitly excluded from unique-geometry claims. Damage states are separately identified variants and do not increase the primary count.

## 3. Other completed source assets

The following quantities come from the final [source inventory](../../creative/generated_128/reports/validation_128.json) and its linked manifests.

| Asset family | Completed source quantity | Derivatives and interpretation |
|---|---:|---|
| NPC skins | 500 native 128×128 masters | 500 distinct 64×64 compatibility exports; existing identity and model data retained |
| Outfits | 100 native 128×128 masters | 100 distinct 64×64 compatibility exports; overlay transparency retained |
| Phone assets | 24 | Native 128 masters |
| HUD assets | 33 | Art exports; live HUD behaviour is not implemented by this batch |
| Fictional brands | 32 | Original identities with native raster and editable sources where applicable |
| Identity assets | 4 | Includes the server identity master and its compatibility export |
| Bilingual signs | 120 | English/Marathi content retained; two native tiles per assembled sign |
| Material tiles | 168 | 132 bound into the atlas; 36 valid standalone source tiles remain unreferenced by authored geometry |
| World textures | 98 | Native 128 masters and package copies |

All **600 character masters** passed the native-grid checks. Base skin UV surfaces and intentional outer-layer alpha were checked separately, and compatibility images retained their UV alignment. The original outfit category totals remain: casual 20, traditional 20, formal 15, sports 10, festival 15, premium 10 and utility 10. The [character validation](../../creative/generated_128/reports/characters_128_validation.json) and [character review](../../creative/generated_128/reports/characters_128_review.json) provide the batch-specific evidence. Assembled front/back previews are art review aids, not screenshots of a running Minecraft client.

### Approved festival selection

The [approved selection manifest](../../creative/generated_128/manifests/approved_festival_selection_128.json) selects **100 installations: 72 legacy records plus 28 additions**. All 100 original legacy IDs remain available, including the 28 not selected for this approved collection. The new additions are 10 Independence Day, 10 Monsoon, four Christmas and four New Year records.

| Approved theme | Selected count |
|---|---:|
| Diwali | 12 |
| Holi | 12 |
| Navratri | 12 |
| Ganesh Chaturthi | 12 |
| Christmas | 16 |
| New Year | 16 |
| Independence Day | 10 |
| Monsoon | 10 |
| **Total** | **100** |

The selection normalizes the legacy theme labels `ganesh` and `new` only in selection metadata and retains their source labels. Its 100 records have 100 exact geometry definitions. Festival activation remains manual/proposed; no calendar automation, world placement or engine binding was performed.

### Road condition variants

The [vehicle-state manifest](../../creative/generated_128/manifests/vehicle_states_128.json) contains 195 damaged/critical/wreck art records for the 65 road parents. Parent geometry and editable-source hashes are retained for comparison. These state-specific visual exports and the [four-state review sheets](../../creative/generated_128/reports/vehicle_states_128_visual_review.json) support art review; they do not implement collision, physics, damage progression, repair logic or spawning.

## 4. Static verification recorded

The source validation snapshot accounts for **3,934 PNGs** and **7,066 resolved active paths**, and checks the generated JSON records. It records **26,188 Bedrock cubes and 26,188 Java elements**. All declared active paths and hashes resolve within the generated bundle. Original-record and recipe references remain provenance into the existing repository, rather than new runtime bindings. Aggregate JSON file totals may change as final package metadata is written; the model and asset counts above define the deliverable scope.

The image inventory includes 3,172 files at 128×128, 601 at 64×64, 120 sign composites at 256×128 and one shared atlas at 2048×2048, plus larger preview layouts. These are file counts, including previews and derivatives, and must not be presented as counts of unique designs. The 601 smaller files are the 600 character compatibility exports plus the server-list icon.

The pack check records:

- 1,103 item definitions resolved and 1,073 model geometries resolved.
- 171,492 Java texture-face references checked.
- Matching Bedrock multi-bone cube counts and texture dimensions.
- Nonempty 128×128 RGBA model icons.
- Passing archive CRC checks.
- Zero errors, with live client verification explicitly `not_run`.

The Java pack declares target **26.3**, resource format **97.1**. The pack report preserves the official format and rotation-source URLs used for that exporter decision. Final source validation records no rotation approximations. These are exporter and static checks; actual client acceptance still requires a live client run.

## 5. Candidate packages

Both archives are under `creative/generated_128/packs`. Archive sizes and hashes below are copied from the final pack report.

| Archive | Bytes | Members |
|---|---:|---:|
| [GTM_Indraprastha_128_Java.zip](../../creative/generated_128/packs/GTM_Indraprastha_128_Java.zip) | 2,714,932 | 2,670 |
| [GTM_Indraprastha_128_Bedrock.mcpack](../../creative/generated_128/packs/GTM_Indraprastha_128_Bedrock.mcpack) | 7,182,625 | 3,745 |

SHA-256:

```text
GTM_Indraprastha_128_Java.zip
150d4af541c7bd9a3536d9e0d9ba4850502b3b16354bebfe8df43e7484d05616

GTM_Indraprastha_128_Bedrock.mcpack
ee90c787640377659fad7524f16c909401cbfd298b638939d38250fdd0d8e0b8
```

These are statically checked candidate art/resource packs. This batch did not install them in a live client, change production runtime registries or deploy them to a server.

## 6. Rebuild entry point

Run the following from the repository root to install the declared Python dependencies and rebuild the isolated art batch:

```bash
python -m pip install -r tools/requirements-gtm128.txt
python tools/build_gtm128.py
```

The recorded generation environment uses **Python 3.12, Pillow 13.0.0 and NumPy 2.3.5**. Typography also requires Pillow's libraqm support and the fonts `DejaVuSans.ttf`, `DejaVuSans-Bold.ttf`, `NotoSansDevanagari-Regular.ttf` and `NotoSansDevanagari-Bold.ttf`. Font resolution and `GTM128_FONT_DIR` are documented in the design language; fonts are not bundled by the exporter.

The orchestration entry point runs ten stages in isolated subprocesses. It also supports:

```bash
python tools/build_gtm128.py --plan
python tools/build_gtm128.py --verify-only
```

After validation, `python tools/package_gtm128.py` assembles the complete artwork,
editable exports, staging packs, design guide, reports and SHA-256 inventory into
`creative/generated_128/delivery/GTM_Indraprastha_128_Assets.zip`. The optional
`--overview /path/to/overview.png` argument adds a supplied contact-sheet overview.

`--plan` describes the work. `--verify-only` checks existing generated assets and assembles/verifies the packages without regenerating all art. The final `--verify-only` run completed with exit code 0, zero source errors and unchanged archive hashes/sizes. The delivered assets were generated by the individual exporters. A full clean run of the new orchestration entry point is not claimed by this report.

## 7. Handoff boundaries and evidence

The remaining work is engineering integration and live verification: review mapping proposals, connect authoritative item/NPC/outfit interfaces, verify signed skin application and Java/Bedrock appearance, validate scale and interactions, inspect actual world geometry before placement, and satisfy staging/deployment gates. Generated previews do not verify drivable/enterable vehicles, usable furniture, operational HUDs, navigable buildings or gameplay balance.

The completed art checkpoint is documented in these authoritative records:

- [Design language](DESIGN_LANGUAGE_128.md) and [machine-readable profile](../../creative/design_language_128.json).
- [Final source validation](../../creative/generated_128/reports/validation_128.json).
- [Final pack validation](../../creative/generated_128/reports/pack_validation_128.json).
- [Generated manifests](../../creative/generated_128/manifests), containing source IDs, export paths, hashes, derivation and status.
- [Character validation](../../creative/generated_128/reports/characters_128_validation.json), [UI validation](../../creative/generated_128/reports/ui_128_validation.json), [equipment/food checks](../../creative/generated_128/reports/equipment_food_checks.json) and [festival-addition checks](../../creative/generated_128/reports/festival_additions_checks.json).
- [UI visual review](../../creative/generated_128/reports/ui_128_visual_review.json), [character review](../../creative/generated_128/reports/characters_128_review.json) and [vehicle-state review](../../creative/generated_128/reports/vehicle_states_128_visual_review.json).

The source report records the reproduction command `python tools/gtm128_validate.py --output creative/generated_128`. This documentation checkpoint summarizes already completed generation and checks; it does not claim a new engine build, live-client session or deployment.
