# GTM 1.0.4-r4-repair — acceptance notes

**Java-tested repair candidate: native UI, firing, reloading and basic driving smoke checks passed. The final exact-byte restart confirmed the phone, equipment catalogue, grounded wheels and repaired canopy clearance. Bedrock validation is outstanding.**

This is an installable repair for the preserved 1.0.3 functional runtime. It combines a compiled, maintained source overlay with the original supported binary. It is not a rebuild of the missing original 1.0.3 source from the repository's older `source/` tree.

## Included changes

- A matching resource pack with all 24 phone apps and the native128 equipment. A real-client failure revealed that existing UI, finish and outfit PNGs were not registered in Minecraft's item atlas. The repair now registers those directories and checks atlas membership as well as file existence.
- A custom Java inventory phone skin, compact sidebar HUD, JEEVA guide, and shortcuts to equipment, garage and settings. The GUI uses working inventory controls. JEEVA provides local city help and service navigation; it is an offline guide.
- Native firearms appear first in the equipment catalogue, the admin arsenal exposes distinct native weapons, legacy ammunition is repaired, and an existing account can receive its once-only native service pistol. First-person gun placement is corrected while retaining the authored models and textures.
- Vehicle wheel transforms compensate the client's extra display rotation. Road handling uses integrated acceleration/braking, momentum, brake-before-reverse behavior and bounded steering at speed. The traditional rickshaw canopy is raised 0.45 blocks with extended posts and matching collision bounds, preserving its seats, wheels, textures and IDs.
- A real localhost Control Centre with live server status, players, resource-pack state, redacted logs, an owner command console and the local guide. The Daytona opener uses a localhost SSH tunnel to an existing running server.
- A hash-verified updater with backups, automatic recovery on replacement failure and explicit rollback. The portable launcher's local pack URL and integrity checks are maintained.

## Executed checks

- Java 25 compilation and **53 JUnit tests** passed, including **24 vehicle tests** and **22 console tests**. The remaining seven cover native weapons and equipment upgrade behavior.
- An independent GitHub Actions run completed the full Gradle `clean check jar patchVehicle` build, all Python checks and installable-artifact packaging. Its core and pack hashes matched the local inputs at that checkpoint. That run preceded the final canopy repair. Publication of the final source commit is gated on a fresh successful run, including the seven canopy tests. [CI run](https://github.com/dev351en/gtm/actions/runs/45638152091)
- **826 compatibility assertions** compare the 133 preserved equipment records and derived behavior with the original binary. These are compatibility assertions, not 826 gameplay tests.
- **12 pack regression tests** passed, including missing item-atlas registration, duplicate atlas membership, missing files, native binding preservation and gun-pose metadata.
- **Seven canopy geometry tests** passed, covering strict input fingerprints, the bounded six-Java/twelve-Bedrock model changes, clearance at the preserved seats, display bounds and runtime collision-profile agreement.
- **22 updater regression/integration tests** passed, including real process-held world locks, a listening server port, failed replacements, interrupted transactions, rollback, symlinks and space-containing paths.
- **17 publication fixture tests** passed, including repository identity, exact tag target, asset fingerprint and rerun protections.
- On an independent copy of the full recovered laptop bundle, the **final canopy-inclusive core and pack bytes** installed through the shipped updater CLI, the original launcher passed `--check --java-only`, and rollback restored **all 1,013 original files byte-for-byte**.
- The isolated running Paper server passed **23 HTTP checks** for the Control Centre.

## Native acceptance and remaining platform limits

The actual Minecraft 26.3 client now shows the dark/gold phone, all app icons without magenta placeholders, the styled JEEVA submenu and the visible held Kavach pistol. These appeared after normal login without requiring `/pack`. The account retained exactly one pistol and 32 rounds across restart/login. The final pack reload logged zero missing-model-texture warnings, zero duplicate-sprite warnings and zero model-load failures. Unaltered final-pack phone, equipment catalogue and canopy screenshots are linked in the detailed repair report alongside the earlier JEEVA, firing/reload and driving evidence.

Native firing outside the inspected spawn safe area reduced the magazine from 12 to 11, and sneak + right-click reloaded to 12. The complete input sequence consumed two reserve rounds, leaving 30; the safe area correctly rejected firing without consuming the magazine. The owned rickshaw accelerated, steered while moving, braked to zero, reversed and allowed a safe dismount. Its front wheel remained at ground level instead of orbiting above the roof. Fuel decreased to 99% while body health remained 100%.

An elevated side view separately exposed insufficient clearance between the seated player's head and the rickshaw canopy. The canopy has now been raised and its posts extended, with a measured minimum helmet clearance of approximately 0.027 blocks across the checked seats and pitch range. The repaired roof is enclosed by the matching runtime profile. The final native-client side view confirmed the driver beneath the repaired canopy with the wheels still grounded. The inherited malformed backup model has also been corrected without changing its ten ammunition IDs or model targets. All included model JSON is now validated. The final exact-byte client restart passed using core SHA-256 `cd7db28cf7959e5c0801507c647479ebffca67616a8c543333ce24c8051ad5ac` and Java pack SHA-256 `03b6d50e96c09643b289cb4a5afd6d6aea0830267e0bf174336f8d6269e9022e`.

Bedrock/Geyser mappings have static validation, but there is no completed native Bedrock client playtest. The preserved NetherNet laptop launcher also requires an active private LAN IPv4 interface, which this test sandbox does not provide. Bedrock uses its native inventory GUI rather than Java's custom font background.

The installer has been exercised on Linux. The Windows batch wrapper and Windows lock implementation have been reviewed but have not been executed on Windows. Audio was not accepted because the isolated client has no OpenAL output device. No deployment to the user's existing Daytona server is claimed by these results.

The current checks, source provenance, installation and rollback instructions are detailed in `RUNTIME_REPAIR_2026-11-25.md`. The included native-client record and unaltered screenshots identify the observed Java result; they do not imply Bedrock or production acceptance.
