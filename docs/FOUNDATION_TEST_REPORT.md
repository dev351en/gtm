# Foundation verification — 2026-11-24
## Executed
OpenJDK 21 javac compiled the exact three dependency-free sources committed on this branch. Git blob hashes were compared with local git hash-object outputs. java com.sdcraft.core.gtm.FoundationChecks returned "GTM foundation: 36 checks passed".
Reproduce from source directory:
```sh
mkdir -p /tmp/gtm-check
javac -encoding UTF-8 -d /tmp/gtm-check src/main/java/com/sdcraft/core/gtm/*.java src/test/java/com/sdcraft/core/gtm/FoundationChecks.java
java -cp /tmp/gtm-check com.sdcraft.core.gtm.FoundationChecks
```
These are explicit smoke assertions, not JUnit discovery or live server tests.
## Not executed
Full Paper build (requires JDK 25, Gradle and local VaultUnlocked JAR; local environment only JDK 21 and GitHub DNS unavailable). Existing reported 76 tests not rerun. Experimental GtmDialogue adapter not compiled or verified on Java/Bedrock. Adapter uses deterministic existing DialogueEngine; Hindi/English reply only, Hinglish detection exists but natural Hinglish responses and proximity event wiring remain pending. Permission must be granted only after authentication. VehicleState is domain logic only, not connected to existing MTVehicles or new movement engine. No persistence, actual speedometer, visual damage, explosions or refuelling transactions yet.
## Audit findings
Existing ledger uses mutable YAML and separately appended audit log; save/append failure semantics and idempotency need work before lending. Existing starter kit still uses QualityArmory/MTVehicles; retain until tested migration. Existing population config is 100, not 500. External AI disabled and endpoint hardcoded to OpenAI. Existing city spawn fixed coordinate; survey before changing. Existing phone item already opens menu by right-click. No live world, account billing, quota, or Daytona access verified. No production changes. Rotate previously exposed credential via secure secrets.

## Dev.2 verification
CivicRules.java and CivicChecks.java compiled with javac 21; java com.sdcraft.core.gtm.CivicChecks returned 78 checks passed. Their blob hashes cb95c67c3e5a5e0c3a9b7e2f40ab5489dd2bc5f3 and 79413532e8cb3bb0b31f6b2b9b5202a86c4a6f94 match the tested files. Reproduce with the existing dependency-free javac command plus src/test/java/com/sdcraft/core/gtm/CivicChecks.java.
Asset generator tools/generate_npc_assets.py (blob ba54d4530f844a98b2be9569ecb3477742c53d93) executed successfully with Python/Pillow; output 500 unique NPC pixel hashes, 100 unique outfit pixel hashes, all 64x64 RGBA, 500 stable UUIDs and 5 initial prisoners. First-pass front views inspected. Run python tools/generate_npc_assets.py --output /tmp/gtm-assets. No pack/client test or integration with existing NPC IDs. The local ZIP passed CRC validation; generated assets are not committed individually.
No full server build or deployment. Direct DNS for Daytona and GitHub failed; GitHub connector is available. No credentials used. Production and billing untouched.

## Dev.3 verification
All four dependency-free suites rerun together under OpenJDK 21: 36 + 78 + 29 + 12 = 155 passed. New source blobs: SnapshotStore e2a48e4d6840cb9679df5295657b1dc8092a1ca8; RouteGraph 22758324b2e14ddc21cfc147260df35746a07cdf; InfrastructureChecks 8a1a5aee25c7feeb3898462f01105b0276eb2a00; NearMiss b8eab3b0a281d2faf906fd81c610db2de1572eed; NearMissChecks 41f97ad4e58f069e79c9712ec383e7334e270daf. Matches local tested sources. Run bash tools/check_gtm_domain.sh from repository root. Atomic replacement, latest-operation replay, stale revision, payload bound, truncated/corrupt input and synthetic directed routing checks passed. Not a transaction migration, full server test or proof of crash durability. NearMiss geometry tested, Paper adapter source only; experimental feature still disabled. Earlier Java 25 CI run cancelled. No production deployment or new hosting resources.

## Dev.4 build and integration verification
- Previous dev.3 full Java 25 Gradle check/jar job succeeded: https://github.com/dev351en/gtm/actions/runs/45444233893 . The runner uploaded an unreleased candidate JAR.
- Dev.4 initial run https://github.com/dev351en/gtm/actions/runs/45446234182 failed compileJava, undefined p in logout hook. Corrected by passing e.getPlayer() (commit 033ac3854d3ec603608f2c1a8563292d0d428a16). Subsequent corrected build result not yet available at time of reporting. Do not count new tests as passed until CI confirms.
- New tests: GtmLedgerTest (eight JUnit methods) and RegionBoundsTest (two JUnit methods). They cover atomic payment/debt and payment/ownership, replay protection, corrupt ledger refusal, failed-save rollback, diagnostic CSV failure, overflow, grace days, key replacement and bounds. No live Minecraft/Bedrock testing.
- tools/daytona_preflight.py compiled with Python, mock checks passed (only two allowed GET paths, redaction, invalid identifiers, fail-closed provisioning and billing). Git blob 3e35debbf6ca8ff9ecd993b6aa7ea196af83e66b matches local tested file. No live HTTP calls or credentials used; DNS remains unavailable.
- See docs/STAGING_CIVIC.md for feature flags, surveyed region schema, staging requirements and remaining access bypass gaps. Production and main untouched. No actual loans issued, properties sold or live player records accessed.
