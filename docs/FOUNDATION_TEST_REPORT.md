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
