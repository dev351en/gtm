# Weapon repair

## Cause

The preserved 1.0.3 runtime contains the native equipment engine and native128 models. The ordinary starter kit still prefers QualityArmory. The old administrator arsenal presents real-brand labels while delivering four generic native types, then prefers QualityArmory ammunition even when the issued guns are native. Several fallback ammunition IDs do not match the reload engine. The native equipment catalogue places thirty light-tag items before the functional firearms, pushing the requested models out of the first page.

## Source provenance and preserved behavior

`GunEngine.java` and `CreativeArsenalManager.java` were reconstructed from the preserved core JAR with CFR 0.152, corrected to source-compatible Java and changed in the focused ways below. `equipment/EquipmentCatalog.java` retains the original record and action API; its TSV parser was reconstructed against `javap -c -private` because CFR could not recover that method. It preserves the original header, ten columns, duplicate rejection, record validation and exactly 133 catalogue identities. Every record and its derived instructions, ranged, pellets, reload and key behavior were compared with the original binary using an isolated class loader.

The replacement GunEngine preserves the recovered runtime's item-bound reload delay, authenticated use, loaded-chunk ray bounds, aggregate scatter damage and protected-property/player checks. It does not restore the older source tree's delayed callback that could reload the wrong held gun.

## Resulting behavior

- `/equipment` shows functional native firearms first. Original IDs and values are preserved; ordering alone changes.
- The nine firearm slots in the administrator arsenal preview and issue nine distinct native fictional weapons when the native equipment service is enabled. Spare ammunition matches the native reload engine. The older four-family native engine remains the fallback.
- Right-click fires; sneak plus right-click reloads. The preserved native engine supplies firing, reload, ammunition, health-damage and protection behavior.
- Four-family native guns get explicit `gtm:core_pistol`, `core_shotgun`, `core_smg` and `core_rifle` model aliases from the repaired Java/Geyser packs. Base materials and metadata remain stable. Existing explicit finish models are preserved.
- Incorrectly tagged old native ammo is normalized in place without changing its quantity or unrelated metadata. QualityArmory possessions are not converted.
- `GtmWeaponUpgrade.offer(plugin, player)` gives each existing authenticated player one loaded native Kavach pistol. Its item and once-only marker are saved together in that player's data, with a deterministic serial. Full inventory defers until `/gun` or the next login; no existing item is discarded and no balance changes. Native equipment flags and permissions apply. `equipment.repair-starter: false` disables the optional repair grant.

The upgrade helper uses Paper Player.saveData, the same boundary as the existing item-delivery engine. Java-level rollback is tested when the save throws. This is not a new guarantee for a physical disk failure that Paper only logs.

## Executed checks

- Java25 compilation against actual Paper 26.3.build.255-stable API and preserved core JAR.
- Seven JUnit tests: once-only replay/restart; full-inventory defer/retry; save-failure rollback/retry; discarded-item entitlement retention; deterministic identity; nine distinct functional arsenal models; legacy ammo compatibility.
- EquipmentCompatibilityChecks: 826 assertions comparing all 133 original records and derived behavior, plus matching rejection of malformed, duplicate and incomplete catalogues. These are compatibility assertions, not 826 independent gameplay scenarios.

Actual client acceptance is tracked in the integrated repair report. Bedrock client acceptance remains distinct from Java/Geyser pack validation.
