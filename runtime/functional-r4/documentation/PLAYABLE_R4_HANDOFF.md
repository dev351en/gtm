# GTM laptop integration handoff

## User objective

Finish the supplied Revision 4 master prompt, keep native 128×128 asset generation as the design default, and produce a directly usable laptop package from the existing project/Daytona export. The user authorized implementation and coherent local commits. Automatic approval review rejected external GitHub publication because trusted user-authored authorization for that destination was not established; do not retry through another tool or route. Do not ask again for routine implementation decisions, and do not represent an art catalogue or candidate ZIP as the completed game.

## Current baseline and ownership

- Integration branch: `gtm/playable-r4`, based on creative checkpoint `80d13c22a27f7cca8bb5665ea0dda66819db980a`.
- Current functional candidate plugin version: `1.0.3-r4-functional-candidate`, Java 25, Paper 26.3 build 255. The prior authenticated laptop checkpoint is commit `560dcef9df1c3883f49b68597d43f188337a111b`.
- Preserve `main`, `gtm/revision-4-foundation`, the creative PR history and all user identity/economy/world data. No forced history update or production deployment is part of this candidate.
- Keep `INDRAPRASTHA_128_V1` in `creative/design_language_128.json` and `docs/creative/DESIGN_LANGUAGE_128.md`. Native 128 masters, shared atlas cells, compatibility derivatives and unique designs have separate counts.

## Work completed in this increment

The root changelog describes authentication, atomic state, mission receipts, medical settlement, queued inventory deliveries, restoration scope, native equipment corrections, merged runtime assets and portable packaging. [BUILD_RUNTIME_R4_REPORT.md](BUILD_RUNTIME_R4_REPORT.md) preserves the prior checkpoint. The current asset gameplay increment, exact compiled artifact and executed checks are recorded in [FUNCTIONAL_RUNTIME_R4_REPORT.md](FUNCTIONAL_RUNTIME_R4_REPORT.md). INTERACTION_RUNTIME_R4_REPORT.md preserves the earlier1.0.2 checkpoint. [PLAYABLE_R4_ACCEPTANCE.md](PLAYABLE_R4_ACCEPTANCE.md) is the section-by-section implementation tracker.

Relevant source locations:

| Area | Entry points |
|---|---|
| Authentication | GtmAuthentication, gtm/AuthenticationStore, gtm/AuthenticationState, SDCraftCorePlugin lifecycle |
| Financial/state durability | Ledger, AtomicYamlStore, GtaEngine, MedicalRecovery, GtmItemDelivery |
| Public-world safety | RestorationEngine, GtmProperties, explicit service/zone configuration |
| Asset identity and packs | GtmAssetCatalog, gtm-assets.tsv, build_runtime_packs.py, gtm_legacy_pack_adapter.py |
| Native road vehicles | GtmVehicles, vehicle/*, GtmVehicleServices, vehicle/road-profiles.tsv |
| Owned functional furniture | GtmFurniture and its utilities/power/mobility/rescue/cargo/civic/access/workshop/shopping-cart adapters, furniture/* and vehicle/VehicleWorkshopStore |
| Purchases and ATM | GtmAssetShop, Ledger asset/service outboxes, GtmCivicTerminals |
| Portable server | packaging/laptop, dependencies.lock.json, bootstrap_laptop_dependencies.py, build_laptop_bundle.py |
| Verification | Current coherent Java gate,155 domain assertions, pack/profile/launcher fixtures, per-scenario exact-Paper/protocol evidence and site surveys |

## Operational boundaries

The verified world input is the sanitized public snapshot dated 2026-11-23, SHA-256 `214a00a08acdb5f73fea52ef79cdfdf773551086d31f5f95725f559ad0802dc2`. It has no private player account data or accepted EULA. The separate historical OnePack TEST_ONLY ZIP is not a current Daytona export and has no Paper runtime.

The existing Daytona sandbox was inspected read-only through its already signed-in dashboard. Its running server is `/home/daytona/sdcraft_server` in sandbox `b6a826ca-4dac-4716-b7b9-236b88b4718e`. The original accepted `eula.txt` was downloaded unchanged for the isolated copy (SHA-256 `ee27072e4a23e088522f740ddaab0c7c4145c186969e90a86254faa3a5ec5ce6`). No new acceptance was created. No consistent current private full-server export has been obtained. The available public snapshot must not be described as current private progress. Do not hot-copy the running world and claim a consistent backup; do not stop, restart, resize or overwrite the protected live sandbox. No production changes were made.

The laptop profile keeps Java and pack HTTP on loopback; the regular crossplay launcher selects a current private IPv4 for Bedrock NetherNet. It uses the owner’s installed game client. Existing owner EULA acceptance is preserved byte for byte when supplied; otherwise the launcher asks the owner at first start. Preserve imported online/offline identity policy; do not change UUID mode to make an import appear easier. Existing authentication providers require a deliberate credential migration. Local password hashes do not encrypt offline Java transport.

The native plugin now stops its local server on fatal initialization failure so a failed login/ledger service cannot leave offline access open. Each module's shutdown is isolated so an unrelated checkpoint failure cannot prevent the authentication workers closing.

## Outstanding implementation and verification

The matrix is authoritative about scope. The functional increment supplies all 87 transport profiles across road, water, air, rail, ropeway and support modes; all 200 primary furniture bindings plus 158 placeable extensions; native equipment, 30 food effects, 100 paid outfits, 24 phone apps and 120 owner-managed sign designs. Taxi and food courier services use immutable commissioned routes, explicit fleet opt-in, shared vehicle physics and durable financial receipts. Availability depends on authenticated ownership, permissions, loaded/accessible geometry and the corresponding enabled subsystem. Ornament-only objects are identified as such.

Exact Paper 26.3 build 255 now boots the core in an isolated copy with actual registered/login sessions. A translated Mineflayer 26.1 client verified pack download, menu purchase, paid item delivery and logout/login preservation. Its rendering acknowledgement is simulated and must not be called native pack rendering. Actual Paper API probes exercise inventories, frames, placements and timed mechanics; their injected events are distinguished from native client controls. The final versioned functional report records the exact JAR and completed checks.

Native Java 26.3/Bedrock rendering, Windows execution, multiplayer performance and crash-at-each-boundary qualification remain open. The public world still needs its complete property/road/facility registry and the wider campaign, city traffic, occupation and administrative systems in the master matrix. Inventory delivery and medical state span the Ledger and vanilla player save; `Player.saveData()` does not expose a reliable durable-write acknowledgement, so arbitrary-power-loss exactly-once item delivery is not claimed.

The source configuration keeps experimental flags gated. The explicit public local-workshop profile enables all 87 transport profiles and 358 furniture entitlements for isolated playtesting, using verified air-only additions, three paid properties, actual backing blocks and ordinary permissions. A narrowly scoped local owner permission allows real rail, cable and road-service commissioning only throughout the actor's bought depot/landing. No route or fleet enrollment is invented in advance. The ordinary paid profile and transport depot have actual acceptance, and the released launcher has preserved their saved state across restart. See [LOCAL_PLAYTEST_PROFILE.md](LOCAL_PLAYTEST_PROFILE.md) and [LAPTOP_DEPOT_ACCEPTANCE_R4.md](LAPTOP_DEPOT_ACCEPTANCE_R4.md). Production activation still requires the remaining integration and native client gates. The current mission board exposes all 13 legacy waypoint jobs; their declared service steps do not yet become 80 functional missions.

## Delivered asset increment and remaining work

1. Verify the exact packaged JAR/pack hashes against the final local build report. CI and draft PR#3 still refer to the older published commit; the current source is local only. Use FUNCTIONAL_RUNTIME_R4_EVIDENCE.json for the completed20-report server/protocol scope and exact hashes; the final core has644 tests/79 suites plus155 domain assertions. The exact finished ZIP and its actual fresh launcher test are identified by the accompanying post-archive receipt; retain the original run and explicit continuation when a test was corrected.
2. Obtain and inventory the intended current server export, preserve an immutable original, and apply the private-copy builder only to a stopped or otherwise verified consistent export. Reconcile all identities and dependency/authentication migrations explicitly.
3. Run actual Java/Bedrock authentication, pack, menu, medical, purchase, restoration and reconnect checks. Reproduce/fix failures before enabling additional services.
4. Complete the world registry and missing engines in dependency order using the matrix; retain actual test and client evidence with each coherent commit.

Only use a COMPLETE release filename after every applicable gate in the supplied prompt genuinely passes. Candidate archives must retain their limitations, provenance, checksums, backup and rollback instructions.
