# GTM 1.0.4-r4-repair — acceptance notes

**Draft: native Java validation is in progress; Bedrock validation is outstanding.**

This is an installable repair for the preserved 1.0.3 functional runtime. It combines a compiled, maintained source overlay with the original supported binary. It is not a rebuild of the missing original 1.0.3 source from the repository's older `source/` tree.

## Included changes

- A matching resource pack with all 24 phone apps and the native128 equipment. A real-client failure revealed that existing UI, finish and outfit PNGs were not registered in Minecraft's item atlas. The repair now registers those directories and checks atlas membership as well as file existence.
- A custom Java inventory phone skin, compact sidebar HUD, JEEVA guide, and shortcuts to equipment, garage and settings. The GUI uses working inventory controls. JEEVA provides local city help and service navigation; it is an offline guide.
- Native firearms appear first in the equipment catalogue, the admin arsenal exposes distinct native weapons, legacy ammunition is repaired, and an existing account can receive its once-only native service pistol. First-person gun placement is corrected while retaining the authored models and textures.
- Vehicle wheel transforms compensate the client's extra display rotation. Road handling uses integrated acceleration/braking, momentum, brake-before-reverse behavior and bounded steering at speed.
- A real localhost Control Centre with live server status, players, resource-pack state, redacted logs, an owner command console and the local guide. The Daytona opener uses a localhost SSH tunnel to an existing running server.
- A hash-verified updater with backups, automatic recovery on replacement failure and explicit rollback. The portable launcher's local pack URL and integrity checks are maintained.

## Executed checks

- Java 25 compilation and **52 JUnit tests** passed, including **23 vehicle tests** and **22 console tests**. The remaining seven cover native weapons and equipment upgrade behavior.
- **826 compatibility assertions** compare the 133 preserved equipment records and derived behavior with the original binary. These are compatibility assertions, not 826 gameplay tests.
- **10 pack regression tests** passed, including missing item-atlas registration, duplicate atlas membership, missing files, native binding preservation and gun-pose metadata.
- **22 updater regression/integration tests** passed, including real process-held world locks, a listening server port, failed replacements, interrupted transactions, rollback, symlinks and space-containing paths.
- On an independent copy of the full recovered laptop bundle, the real repair installed, the original launcher passed `--check --java-only`, and rollback restored **all 1,013 original files byte-for-byte**.
- The isolated running Paper server passed **23 HTTP checks** for the Control Centre.

## Remaining acceptance boundary

Native Java playtesting is underway. Its first run exposed missing phone atlas entries and an off-screen held-gun pose; those defects have been corrected and require the new pack to be rechecked in the client. Pack acceptance alone is not proof that every texture renders.

Bedrock/Geyser mappings have static validation, but there is no completed native Bedrock client playtest. The preserved NetherNet laptop launcher also requires an active private LAN IPv4 interface, which this test sandbox does not provide. Bedrock uses its native inventory GUI rather than Java's custom font background.

The installer has been exercised on Linux. The Windows batch wrapper and Windows lock implementation have been reviewed but have not been executed on Windows. No deployment to the user's existing Daytona server is claimed by these results.

The current checks, source provenance, installation and rollback instructions are detailed in `RUNTIME_REPAIR_2026-11-25.md`. This acceptance note must be updated with the native-client result before the release is marked ready.
