# GTM laptop integration handoff

## User objective

Finish the supplied Revision 4 master prompt, keep native 128×128 asset generation as the design default, and produce a directly usable laptop package from the existing project/Daytona export. The user authorized implementation, coherent commits and development-branch pushes. Do not ask again for routine implementation decisions, and do not represent an art catalogue or candidate ZIP as the completed game.

## Current baseline and ownership

- Integration branch: `gtm/playable-r4`, based on creative checkpoint `80d13c22a27f7cca8bb5665ea0dda66819db980a`.
- Candidate plugin version: `1.0.1-r4-candidate`, Java 25, Paper 26.3 build 255.
- Preserve `main`, `gtm/revision-4-foundation`, the creative PR history and all user identity/economy/world data. No forced history update or production deployment is part of this candidate.
- Keep `INDRAPRASTHA_128_V1` in `creative/design_language_128.json` and `docs/creative/DESIGN_LANGUAGE_128.md`. Native128 masters, shared atlas cells, compatibility derivatives and unique designs have separate counts.

## Work completed in this increment

The root changelog describes authentication, atomic state, mission receipts, medical settlement, queued inventory deliveries, restoration scope, native equipment corrections, merged runtime assets and portable packaging. The current compiled artifact and exact tests are recorded in [BUILD_RUNTIME_R4_REPORT.md](BUILD_RUNTIME_R4_REPORT.md). [PLAYABLE_R4_ACCEPTANCE.md](PLAYABLE_R4_ACCEPTANCE.md) is the section-by-section implementation tracker.

Relevant source locations:

| Area | Entry points |
|---|---|
| Authentication | GtmAuthentication, gtm/AuthenticationStore, gtm/AuthenticationState, SDCraftCorePlugin lifecycle |
| Financial/state durability | Ledger, AtomicYamlStore, GtaEngine, MedicalRecovery, GtmItemDelivery |
| Public-world safety | RestorationEngine, GtmProperties, explicit service/zone configuration |
| Asset identity and packs | GtmAssetCatalog, gtm-assets.tsv, build_runtime_packs.py, gtm_legacy_pack_adapter.py |
| Portable server | packaging/laptop, dependencies.lock.json, bootstrap_laptop_dependencies.py, build_laptop_bundle.py |
| Verification | Java tests, 155 domain assertions, test_runtime_packs.py, test_laptop_bundle.py, site survey JSON |

## Operational boundaries

The verified world input is the sanitized public snapshot dated 2026-11-23, SHA-256 `214a00a08acdb5f73fea52ef79cdfdf773551086d31f5f95725f559ad0802dc2`. It has no private player account data or accepted EULA. The separate historical OnePack TEST_ONLY ZIP is not a current Daytona export and has no Paper runtime.

There is no authenticated Daytona session/API credential in this workspace. Browser inspection reached the account sign-in page. Do not reuse an earlier exposed key. Obtain the actual authorized export or secure sign-in before claiming that current Daytona progress is incorporated. Do not delete, resize, restart or overwrite the protected sandbox or its snapshots. Optional external AI is not required for the deterministic local fallback.

The laptop profile is loopback only. The owner accepts the Minecraft EULA at first start and uses their own installed game client. Preserve imported online/offline identity policy; do not change UUID mode to make an import appear easier. Existing authentication providers require a deliberate credential migration. Local password hashes do not encrypt offline Java transport.

The native plugin now stops its local server on fatal initialization failure so a failed login/ledger service cannot leave offline access open. Each module's shutdown is isolated so an unrelated checkpoint failure cannot prevent the authentication workers closing.

## Outstanding implementation and verification

The matrix is authoritative about scope. Large incomplete areas include physical road/rail/ropeway/air/marine engines, working NPC occupations/traffic, persistent functional furnishing and all 46 facilities, the 30+50 campaign/finale, physical delivery, fashion, entertainment, 24 connected apps, media/government services and the real Control Centre backend.

No full Paper-world startup, real Java/Bedrock client join, Windows execution, multiplayer performance or crash-at-each-boundary test has been certified. Paper's verified `--help` bootstrap is only a bootstrap check. Current unit tests prove specific state transitions, not the full game. In particular, inventory delivery and medical state span the ledger and vanilla player save; `Player.saveData()` does not expose a reliable durable-write acknowledgement. Do not claim arbitrary-power-loss exactly-once item delivery until that boundary has been solved and fault-tested.

All experimental feature flags remain explicit gates. Do not enable them merely to make every menu visible. Commission actual sites/regions and close their integration/client checks first. The current mission board exposes all 13 legacy waypoint jobs; their declared service steps do not yet become 80 functional missions.

## Next executable work

1. Verify the exact packaged JAR/pack hashes against the final build report and CI commit, then run clean startup/restart on an owner-accepted disposable copy.
2. Obtain and inventory the intended current server export, preserve an immutable original, and apply the private-copy builder only to a stopped or otherwise verified consistent export. Reconcile all identities and dependency/authentication migrations explicitly.
3. Run actual Java/Bedrock authentication, pack, menu, medical, purchase, restoration and reconnect checks. Reproduce/fix failures before enabling additional services.
4. Complete the world registry and missing engines in dependency order using the matrix; retain actual test and client evidence with each coherent commit.

Only use a COMPLETE release filename after every applicable gate in the supplied prompt genuinely passes. Candidate archives must retain their limitations, provenance, checksums, backup and rollback instructions.
