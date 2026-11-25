# GTM playable R4: build and runtime resource integration

> Historical `1.0.1-r4-candidate` checkpoint, committed as `560dcef9df1c3883f49b68597d43f188337a111b`. The subsequent vehicle/furniture work is recorded in [INTERACTION_RUNTIME_R4_REPORT.md](INTERACTION_RUNTIME_R4_REPORT.md). The hashes and counts below belong only to this checkpoint.

The reviewed working tree builds successfully as **SDCraftCore 1.0.1-r4-candidate** against **Paper 26.3 build 255**, using genuine Java 25 and Gradle 9.2.1. The final run passed **136 JUnit cases**, **155 domain smoke assertions**, **10 resource-pack tests**, and **18 laptop packaging/launcher tests**, with no failures or skipped tests. The corrected delivery and medical failure-handling changes are included in this result.

This report covers the compiled candidate, unit/domain tests, resource graphs, compatibility adapters and packaging fixtures. Actual Java/Bedrock client sessions and a running Paper world are separate acceptance gates. See [the machine-readable evidence](BUILD_RUNTIME_R4_EVIDENCE.json) and [the playable acceptance report](PLAYABLE_R4_ACCEPTANCE.md).

## Final artifacts

| Artifact | Size in bytes | SHA-256 |
| --- | ---: | --- |
| `source/build/libs/SDCraftCore-1.0.1-r4-candidate.jar` | 413,463 | `857b71cb9eee7d4be58fbfc5995cdd6a8cca02c37aee12a7bc541fd542486892` |
| `build/runtime-packs/GTM_Runtime_128_Java.zip` | 13,449,648 | `6dd9b5cb653918956ed2b099f768b8bb91033c7d8ad0475606d77f6ba45d9334` |
| `build/runtime-packs/GTM_Runtime_128_Bedrock.mcpack` | 8,412,504 | `cee842bdbcacb03d3f45e7808febf1120cfd64ee50ca71725e92f10913ea0363` |
| `build/runtime-packs/gtm_runtime_mappings.json` | 323,130 | `36d0893d4a86f3a61c2385d44b729a848cdaae9d28b83df69accee53e1a6f702` |

The final JAR supersedes every earlier candidate hash from this session. Its ZIP CRC passes, all project classfiles have major version 69 (Java 25), its plugin descriptor declares version `1.0.1-r4-candidate` and API `26.3`, and its embedded `gtm-assets.tsv` exactly matches the generated source resource. The Java pack SHA-1 for resource-pack configuration is `dfc13328983246e81d8f42afa835cbe989b3faf5`.

## Build environment and resolved blockers

The workspace initially contained only a Java 21 runtime, with neither `javac` nor Gradle. The existing domain-check script therefore stopped before compilation. Official distributions were downloaded into an isolated workspace toolchain directory and verified before use; no system Java aliases were changed.

| Verified input | SHA-256 |
| --- | --- |
| Temurin `25.0.5.1+2`, Linux x64 JDK archive | `760f91b22c3efc9bd1b64ff950598231be82928cc807e30691a0e7a2995a62c0` |
| Gradle `9.2.1`, binary distribution | `72f44c9f8ebcb1af43838f45ee5c4aa9c5444898b3468ab3f4af7b6076c5bc3f` |
| Paper API `26.3.build.255-stable` | `16d784a1b2a6a0be74479c761d9b5cbd7271ee1d8d5ff45f8060d0fa352f1d0b` |
| Paper server `26.3-255` | `a7116085a8ba88cf00771d5e61a2925007942092650811da7327dc23243f0cec` |
| Existing VaultUnlocked `2.20.3` | `fbc6651aca11e13376c115df66eeffa79592e79517be398299aa6beb49c22695` |

The JDK download/checksum came from the [official Adoptium API](https://adoptium.net/installation/ci-scripts/); Gradle was checked against its [official checksum reference](https://gradle.org/release-checksums/). The isolated Gradle launcher uses the workspace's current unauthenticated proxy and the system Java truststore. TLS verification remains enabled. Proxy addresses are not committed.

Citizens' Maven host returned HTTP 403 during the initial full build. Source inspection showed that `NpcService` accesses Citizens entirely through reflection and the plugin descriptor already declares it as a soft dependency. The unused Citizens compile-time dependency and repository were removed from `build.gradle.kts`. Optional runtime Citizens integration and its fallback remain unchanged. Paper and Vault dependencies resolved and compiled normally.

The committed baseline `80d13c2`, with that build-only dependency correction, passed 94 JUnit cases and all 155 domain assertions in an isolated source copy. Subsequent shared-tree builds verified the actual new implementation. The final build uses the complete corrected working tree, whose source digest is recorded in the evidence JSON.

## Verification performed

| Verification | Final result |
| --- | --- |
| Gradle `clean check jar` | Passed; 136 JUnit cases in 21 suites, zero failures/errors/skips |
| Foundation smoke main | 36 assertions passed |
| Civic smoke main | 78 assertions passed |
| Infrastructure smoke main | 29 assertions passed |
| Near-miss smoke main | 12 assertions passed |
| Runtime resource/compatibility tests | 10 passed |
| Laptop packaging/Java launcher fixtures | 18 passed; genuine Java 25 explicitly supplied |
| Merged pack CRC and resource graphs | Passed |
| Git whitespace check | Passed |

The JUnit run includes all 19 authentication cases, atomic persistence, mission and medical settlement, delivery receipts, the new medical receipt-generation regression, six asset-catalog tests, and Vault tests for authenticated online mutation, session revocation and refusal to reserve unregistered identities. Existing financial, dialogue, population, geometry and policy tests also remain passing.

`javap` on the exact resolved Paper API confirms that `EntityDeathEvent` implements `Cancellable`; `PlayerDeathEvent` inherits this behavior. The compiled medical listener uses `ignoreCancelled=true` before billing. One existing nonblocking warning remains: `GunEngine` uses the deprecated `Sound.valueOf(String)` API.

## Native128 catalog and compatibility policy

`GtmAssetCatalog` loads the generated, immutable `gtm-assets.tsv` resource. It rejects malformed identifiers, duplicates, unknown provenance, missing alias targets, cross-material aliases and implicit ID reassignment. Catalog availability grants no money, item ownership or permission.

The runtime resource set resolves **1,683 item-model definitions**. Another **21 existing core CustomModelData items** have explicit Bedrock compatibility adapters, yielding **1,704 globally unique Bedrock identifiers**.

| Preserved or generated group | Count | Treatment |
| --- | ---: | --- |
| Existing city IDs | 479 | Every ID, semantic title and category retained |
| Existing food IDs | 30 | Exact aliases such as `gtm:chai` to `gtm:food_chai` |
| Existing finish ownership IDs | 300 | Actual `01`–`75` IDs retained for all four families |
| Native128 model records | 1,073 | Complete paired geometry, texture and icon references |
| Native128 food aliases | 30 | Reuse the food geometry and icon |
| Legacy city/finish compatibility entries | 580 | Original assets retained where safe native replacement is unavailable |
| Core CMD adapters | 21 | Four guns and seventeen existing paper items |

The 1,073 native model records comprise 509 primary designs, 69 additional base models, 195 road damage variants and 300 cosmetic variants. Aliases, legacy assets and variants do not inflate the unique primary design count.

Of the legacy city IDs, 199 have an exact matching native128 identifier. The remaining 280 retain their original geometry. The staff `/gtmassets` browser now exposes **787 city decorations**: all 479 existing entries plus 308 additive entries. It excludes food, raw weapon sources, cosmetic swatches and damage-state previews. Authentication, permissions and the existing feature flag still apply. The three surveyed fixture identifiers remain unchanged; this integration does not enable furnishings or place new objects.

Two unsafe proposed migrations were deliberately left unapplied. The creative furniture/transport tables contain positional substitutions such as a bar stool mapped to a coffee table. The creative finish proposal also uses zero-based IDs ending in `00`–`74`, while the actual runtime and ledger use `01`–`75`. The merged pack retains the real legacy IDs and adds the new authored IDs separately, preserving all existing entitlements.

## Merged pack behavior

`tools/build_runtime_packs.py` first reproduces and validates the existing 30-food, 479-city and 300-finish compatibility packs, then merges the approved native128 resources. It preserves **1,759 existing active Java pack files byte-for-byte**, including current HUD, gun, vehicle and animation resources. The 98 intended world textures are added through their explicit Java/Bedrock path mappings. Existing animation overlay metadata and license files remain present. The only repeated input ZIP entry was a byte-identical metro-ticket model; identical duplicates are deduplicated, while conflicting duplicates fail the build.

The old Java pack referenced eight missing phone app models. The merger now fills those missing files using semantic native128 artwork:

| Existing phone button | Native artwork |
| --- | --- |
| GPS | City GPS / `app_maps` |
| Jobs | City Jobs / `app_careers` |
| Gear | Generated pistol icon |
| Garage | `app_garage` |
| Bank | `app_bank` |
| Safety | SDPD / `app_police` |
| Medical | `app_medical` |
| Settings | `app_settings` |

The Bedrock adapter preserves the original core mesh dimensions, pivots and source texture pixels. Three-dimensional compatibility icons are rendered directly at 128 pixels; flat icons retain their original image bytes. These are compatibility exports, not additional authored designs. The mapping follows the official [Geyser v2 item-model and legacy-CMD contract](https://geysermc.org/wiki/geyser/custom-items/).

Validation resolves 207,383 Java texture-face references, all mapped Bedrock attachables/icons/material atlases, inherited Java finish meshes, multi-bone cube counts, and finite UV rectangles inside their bound atlas. The report distinguishes 1,103 native128 icons from 601 compatibility icons. The compatibility preview was visually inspected after generation.

## Reproduction and CI

With Java 25, Gradle 9.2.1 and the pinned Python requirements installed:

```sh
cd source
gradle --no-daemon clean check jar
cd ..
python -m unittest discover -s tools -p 'test_runtime_packs.py'
GTM_TEST_JAVAC="$JAVA_HOME/bin/javac" python -m unittest discover -s tools -p 'test_laptop_bundle.py'
python tools/build_runtime_packs.py --output build/runtime-packs --check-resource
```

The pack command requires the completed native128 input bundle at `creative/generated_128`, including its generated packs and source icon used by the gear button. Use `--write-resource` only when deliberately regenerating the committed catalog. `--check-resource` refuses a stale catalog.

The verification workflow now covers pushes to `gtm/playable-r4`, `gtm/creative-r4` and `gtm/revision-4-foundation`, and PRs into those branches or `main`. Source, tools, generated art, resource-pack and packaging changes trigger it. It runs the Java, pack-preservation and laptop tests, supplies a genuine Java 25 compiler to the launcher fixtures, and retains test evidence and a candidate JAR. It does not deploy. CI's pack unit tests do not claim to regenerate or visually inspect the entire art bundle.

## Remaining acceptance boundaries

No live Java or Bedrock client test was performed by this build/integration worker. Held-item orientation, mobile input, world placement, actual server startup and sustained multiplayer behavior require their corresponding runtime evidence. Existing third-party MTVehicles/QualityArmory art is preserved, but its old damage/CMD override trees have not been converted or client-qualified by this work. The 21 reviewed compatibility adapters cover the native core items only. The unverified external vehicle-sales path remains disabled by the engine changes.

No live Daytona instance, production world, player credentials, existing ownership data or external deployment was used or modified. Final laptop assembly and its acceptance status are recorded separately.
