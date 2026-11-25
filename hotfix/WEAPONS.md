# Weapon repair

## Cause

The preserved 1.0.3 runtime contains the native equipment engine and native128 models. Its ordinary starter kit preferred QualityArmory. The old administrator arsenal presented real-brand labels while delivering four generic native types, then preferred QualityArmory ammunition even when the issued guns were native. Several fallback ammunition IDs did not match the reload engine. The native equipment catalogue placed thirty light-tag items before the functional firearms, pushing the requested models out of the first page.

## Source provenance and preserved behavior

`GunEngine.java` and `CreativeArsenalManager.java` were reconstructed from the preserved core JAR with CFR 0.152, corrected to source-compatible Java and changed in the focused ways below. `equipment/EquipmentCatalog.java` retains the original record and action API; its TSV parser was reconstructed against `javap -c -private` because CFR could not recover that method. It preserves the original header, ten columns, duplicate rejection, record validation and exactly 133 catalogue identities. Every record and its derived instructions, ranged, pellets, reload and key behavior were compared with the original binary using an isolated class loader.

The replacement GunEngine preserves the recovered runtime's item-bound reload delay, authenticated use, loaded-chunk ray bounds, aggregate scatter damage and protected-property/player checks. It does not restore the older source tree's delayed callback that could reload the wrong held gun.

## Resulting behavior

- `/equipment` and `/gun` show functional native firearms first. Original IDs and values are preserved; ordering alone changes.
- The nine firearm slots in the administrator arsenal preview and issue nine distinct native fictional weapons when the native equipment service is enabled. Spare ammunition matches the native reload engine. The older four-family native engine remains the fallback.
- Right-click fires; sneak plus right-click reloads. The preserved native engine supplies firing, reload, ammunition, health-damage and protection behavior.
- Four-family native guns get explicit `gtm:core_pistol`, `core_shotgun`, `core_smg` and `core_rifle` model aliases from the repaired Java/Geyser packs. Base materials and metadata remain stable. Existing explicit finish models are preserved.
- Incorrectly tagged old native ammo is normalized in place without changing its quantity or unrelated metadata. QualityArmory possessions are not converted.
- `GtmWeaponUpgrade.offer(plugin, player)` gives each authenticated account one loaded native Kavach pistol. The integrated fresh starter kit uses this same helper, so activation does not issue a second pistol. Its item and once-only marker are saved together in that player's data, with a deterministic serial. Full inventory defers until `/gun` or the next login; no existing item is discarded and no balance changes. Native equipment flags and permissions apply. `equipment.repair-starter: false` disables the optional repair grant.

The upgrade helper uses Paper Player.saveData, the same boundary as the existing item-delivery engine. Java-level rollback is tested when the save throws. This is not a new guarantee for a physical disk failure that Paper only logs.

## Executed checks

- Java25 compilation against actual Paper 26.3.build.255-stable API and preserved core JAR.
- Seven JUnit tests: once-only replay/restart; full-inventory defer/retry; save-failure rollback/retry; discarded-item entitlement retention; deterministic identity; nine distinct functional arsenal models; legacy ammo compatibility.
- EquipmentCompatibilityChecks: 826 assertions comparing all 133 original records and derived behavior, plus matching rejection of malformed, duplicate and incomplete catalogues. These are compatibility assertions, not 826 independent gameplay scenarios.

## Native Java acceptance

An unmodified official Minecraft Java 26.3 client connected to an isolated Paper 26.3 staging server. The test account used normal registration and login. After a complete server and client restart, it retained exactly one native Kavach and the original 32 matching reserve rounds; no second grant occurred. `/gun` displayed distinct native firearms on the first page. The repaired pack brought the held pistol into the first-person viewport.

Inside the configured safe spawn, firing was rejected without consuming magazine charge. After walking outside the 18-block safe radius, a right-click displayed `11 / 12`. Reloading restored the inventory tooltip to `Charge: 12 / 12` and consumed the matching reserve ammunition. The held modifier/click input sequence produced a second shot before the sneak state arrived, so this sequence consumed two reserve rounds in total.

Exact tested artifact hashes, authentic game screenshots, controls and scope limits are recorded in `docs/repair-evidence/native-java.json`. This smoke test does not establish damage balancing, target accuracy, audio output or Bedrock client acceptance. Final pack verification is recorded separately in that JSON so earlier gameplay checks are not attributed to untested bytes.
