# Native furniture runtime — Revision 4 functional expansion

## Current scope and qualification

All **200 primary native128 furniture IDs now have an explicit implemented interaction assignment**. There are **161 native behavior assignments and 39 service terminals**, with **no `UNSUPPORTED` rows**. This replaces the earlier 79 supported/conditional, 121 unavailable split. Only three intrinsically decorative primary objects use the `DECORATION` behavior. Counts describe current assignments; they do not establish that every named secondary mechanism or native-client interaction has passed.

The catalogue additionally accepts a separately generated **158-object extension**: 20 civic objects, 10 entertainment objects and 128 festival objects (the original 100 plus 28 additions). These are not additional furniture designs. The extension resource and its generator belong to the root integration work; this module supplies their shared ownership, placement, protection and interaction engine. `primaryEntries()` retains exactly the original 200, while `entries()` returns the merged 358 without duplicate IDs.

Named actual-Paper reports cover consumed-supply utility effects, finite linked power, bounded wheelchair movement, optional ottoman storage, supplied crane/jack cargo, consented rescue, progressive camera maps, consented game-identity records, traffic phases, fictional drink measurement, paid entrance scanning, retail stock sensing and timed vehicle-bay leases. See the [utility](FURNITURE_UTILITIES_R4.md), [power](FURNITURE_POWER_R4.md), [wheelchair](WHEELCHAIR_MOBILITY_R4.md), [rescue](FURNITURE_RESCUE_MOBILITY_R4.md), [cargo](FURNITURE_CARGO_R4.md), [civic](FURNITURE_CIVIC_R4.md), [traffic/drink](TRAFFIC_AND_FICTIONAL_DRINKS_R4.md) and [access-service](FURNITURE_ACCESS_SERVICES_R4.md) guides for exact conditions and separate evidence. The supplied [vehicle workshop](FURNITURE_WORKSHOP_R4.md) completed 28 records; the borrowed shopping cart completed its retained paid sequence, with all earlier failed stages preserved. The nine original [festival carts](FESTIVAL_CARTS_R4.md) completed 129 records and [festival readouts/counters/lights](FESTIVAL_FUNCTIONS_R4.md) completed 85. The [authored structural runtime](FURNITURE_STRUCTURES_R4.md) completed 38 records on six representative models; all 27 exact blueprints have separate source/resource checks. Each guide retains its tested core, fixture scope and actual limits. These reports do not establish per-model native-client rendering or full city installation.

Ordinary seating still seats one owner; a bound bed supplies one real sleeping place, while an unbound stretcher has a separate one-patient consented transport mode. Multiple sofa occupants, six automatically supplied dining chairs, a second sleeping bunk, active refrigeration and involuntary restraints are not implemented. The exact per-model table retains these capacities.

`furniture.enabled` remains the top-level experimental gate. Services additionally require a registered callback and an allowlist entry. The root integration supplies banking, actual food orders, phone apps, treatment/status, police interfaces, vehicle work, parking, wardrobe and retail callbacks. The furniture adapter never substitutes a placeholder GUI if a callback is unavailable. Actual availability still depends on the matching game subsystem, surveyed property, supplied backing blocks, ownership and authentication.

This work follows the committed `1.0.2-r4-interactions-candidate` checkpoint. Its previous 181-case build and JAR hash remain historical evidence in `INTERACTION_RUNTIME_R4_REPORT.md`. They do not cover this expansion. New combined build identity belongs to the root's functional increment report. **No real Java or Bedrock client qualification, completed city furnishing, deployment or live-world installation is claimed here.**

## Implementation and reproduction

| File | Responsibility |
|---|---|
| `GtmFurniture.java` | Paper interactions, scoped workstations, protected backing blocks, dynamic controls, transient visuals and lifecycle |
| `GtmFurnitureUtilities.java` | Supplied self-only fire/water/air/treatment/processing effects and actual-container scale readings |
| `GtmFurniturePower.java` | Finite supplied generation, owner links, physical LIGHT/lever output and cutoff |
| `GtmFurnitureMobility.java` | One owned wheelchair's actual passenger/projection motion and guarded pose checkpoints |
| `GtmFurnitureRescueMobility.java` | Explicit patient/self-rescue consent, one carried patient or swimmer, and typed on-foot jack movement |
| `GtmFurnitureCargo.java` | Actual supplied-content pickup, protected custody, checked hoist/jack transport and once-only real output |
| `GtmFurnitureShoppingCart.java` | One movable loan component from an unchanged fixed nest, current whole-body collision and the same supplied cargo custody |
| `GtmFurnitureWorkshop.java` | Supplied maintenance with actual road handling consequences and an owned real-vehicle hoist |
| `GtmFurnitureStructures.java`, `furniture/FurnitureStructures.java` | Exact authored solid colliders, traversable openings, validated existing stage floors and deliberate geometry revision |
| `furniture/FurnitureSeasonalRules.java` | Actual game-midnight/weather readouts and narrow old-ornament compatibility for real festival actions |
| `GtmFurnitureAccessServices.java` | Exact paid serials, real entrance scanning, active stock sensing and timed leases for real vehicle bays |
| `furniture/FurnitureCargoStore.java`, `FurnitureCargoGeometry.java` | Exclusive bounded cargo receipts, exact slot fingerprints and authored-frame hoist clearance |
| `furniture/CargoItemIdentity.java` | Complete typed native item identity across compound-order/gzip differences, with no second output or receipt rewrite |
| `GtmFurnitureCivic.java` | Owned actual camera-map views and explicitly consented fictional game-identity records |
| `GtmTrafficSignals.java` | Commissioned loaded intersection phases, real lever/label and native-vehicle stop policy |
| `GtmAlcohol.java` | Actual fictional consumption receipts, bounded adverse game effects and consented exposure measurement |
| `FurnitureTargeting.java` | Loaded-chunk, bounded targeting shared with acquisition and GUI; visible-cell LIGHT targeting |
| `furniture/FurnitureCatalog.java` | Strict primary and additive catalogues, explicit behavior and accepted backing types |
| `furniture/FurnitureBounds.java` | Finite bounds and exact quarter turns |
| `furniture/FurnitureServicePolicy.java` | Shared dynamic backend and customer eligibility gate before payment/use |
| `furniture/FurnitureSettings.java` | Bounded plain text, light levels, switches, clock/alarm and music state |
| `furniture/FurnitureStore.java` | Paid grant identity, binding, placement, typed controls, CAS persistence and backwards-compatible FUR1/FUR2 reading into FUR3 |
| `furniture/capabilities.tsv` | Exactly 200 primary IDs with authored bounds and native128 profile |
| `furniture/extensions.tsv` | Separately owned additive civic, entertainment and festival descriptors |
| `tools/build_furniture_runtime_profiles.py` | Explicit per-ID semantic assignment; fails if any primary ID is missing or repeated |
| `FurnitureRuntimeTest.java` | 16 original ownership, collision, backing, corruption and replay cases, updated for expanded coverage |
| `FurnitureExpansionTest.java` | 20 additional settings, real processor types, extensions, migration and dynamic service cases |
| `FurnitureOptionalStorageTest.java` | Eight exact ottoman optional-binding, owner, exclusivity and FUR1/FUR2 compatibility cases |

Rebuild the primary registry from the repository root:

```sh
python tools/build_furniture_runtime_profiles.py
```

Run the combined production build from `source/`, using the isolated official toolchain:

```sh
python /workspace/scratch/d7d343b39c16/toolchains/run-gtm-gradle.py clean check jar
```

The art source remains `creative/generated_128/manifests/furniture_128.json`, and the profile remains `INDRAPRASTHA_128_V1`. Original source geometry, icons, textures and asset IDs remain unchanged. Normal placed displays use their source item-model IDs; moving buoy/cart components and hoist partitions use explicit technical derivatives of the same authored cubes and native128 UVs. These are not new primary designs or entitlements. The module never manufactures a transferable furniture voucher or freely obtainable inventory paper item.

## Actual native functions

| Behavior | Implemented operation | Boundary |
|---|---|---|
| `SEAT` | One owner mounts a marker carrier with actual rider clearance and a safe exit. The exact wheelchair adds low-speed flat-floor movement with collision/property checks; the exact storage ottoman adds an optional real inventory and separate Open storage control. | One occupant per model. Public-street wheelchair travel, assisted pushing, swinging transport and native visual fit remain outside current qualification; see [wheelchair limits](WHEELCHAIR_MOBILITY_R4.md). Existing unbound ottomans remain seats. |
| `STORAGE` | Opens a real, protected single chest or barrel. | Contents remain in the vanilla block. A cabinet does not mint stock or automatically refrigerate, medicate or dispense it. |
| `BED` | Uses the actual bound bed with `sleep(location, false)`. An exact unbound stretcher additionally carries one explicitly consenting patient under its owning attendant's controls. | Normal overworld sleep rules; both real bed halves loaded and owned. One bound bed, no synthetic extra bunk or healing. A bound stretcher cannot move as transport. |
| `LIGHT` | Saved on/off plus brightness 0–15 changes the real bound LIGHT block. Sneaking use cycles levels; ordinary use toggles. | Existing dry LIGHT only. The original level is restored on release. Accent brightness is not counted as emitted world light. |
| `SMOKER`, `FURNACE`, `BREWING` | Opens the real corresponding processing inventory, retaining fuel, ingredients, progress and output in the real block. | The registry rejects a chest/barrel as a smoker or furnace. Only smokers are assigned among current primary designs; the other two families are available for reviewed extensions. |
| `CRAFTING`, `LOOM`, `STONECUTTER`, `GRINDSTONE`, `ANVIL`, `SMITHING`, `CARTOGRAPHY` | Opens the real vanilla workstation menu and uses its actual ingredient, XP and recipe rules. | No invented output stacks. The session is tied to one instance, owner, authenticated connection and reach. Some available families have no current primary assignment. |
| `COPYING` | A real crafting menu permits only the vanilla `minecraft:book_cloning` recipe. | Actual supplied original and writable books are required. Other recipes/results are blocked. |
| `READING` | Opens the owner's held written book, or starts normal use of the owner's held food. | The table supplies neither books nor food. Consumption still passes through normal server events. |
| `WASH` | Uses real cauldron water. Ordinary wash models remove leather dye or one banner pattern; the exact eyewash instead spends one level to extinguish its owner and remove game Poison/Blindness. | Self/owned supplied effects only, with no clinical cleanliness claim. Refill uses real water. World/player save boundaries remain vanilla, so no cross-domain crash atomicity is claimed. |
| `UTILITY` | Exact utility IDs supply a bounded hose, actual air counter, gradual self-treatment, first-aid-kit processing or in-place tool repair. Six workshop IDs perform distinct supplied maintenance/hoist operations; the fixed shopping-cart nest lends one controlled cart component. | No automatic resume/refund or free output replay. Utility effects have their named live proof; workshop/cart live gates remain separate. DOWNED players cannot use these treatments to revive. |
| `CLOCK` | Shows actual world time, saved 12/24-hour format and an optional minute alarm. | Alarm-day receipt is committed before sound. It fires at most once per observed world day while the owner is nearby; missed days are not replayed. |
| `DISPLAY` | Saves bounded owner-edited plain text and shows it using a nonpersistent TextDisplay. | Up to 160 UTF-16 code units and four lines. Control characters and formatting escapes are rejected; no commands, links or rich-text actions execute. |
| `MUSIC` | Plays one of four short original note sequences to the nearby owner, with saved volume/melody. | Bounded scheduling, nonce checks, distance checks, cooldown and no global sound broadcast. |
| `BARRIER` | Folds the native model horizontally into an 8% profile with matching collision. The exact turnstile opens only through a commissioned paid serial; the retail gate adds an explicitly armed active-stock crossing sensor. | The full closed footprint remains reserved. Closing waits for occupants; opening grants no private-property permission. The fold is a simple animation, not independently rigged hinges. |
| `POWER` | Ordinary models retain saved real lever control. The generator consumes plain coal/charcoal for finite game energy and drives linked owned LIGHT/lever loads; the transformer distributes that supply with a bounded capacity and latched overload cutoff. The exact traffic signal adds inspected intersection phases and actual native-road stop lines. | Explicit commissioned links/intersections and real reserved backing blocks only. It models finite game energy and vehicle control, not electrical voltage. Original lever data is retained for release; source/link/session changes require safe cutoff. |
| `BRIDGE` | Controls an existing real trapdoor loading flap. | The real block supplies walkable collision; the display is not falsely treated as a platform. Moving/closing refuses occupants. Original restoration waits for a clear flap. |
| `CARGO` | The crane moves exact supplied contents through its checked under-beam opening; the unbound pallet jack carries supplied contents with its actual original moving pose. Explicit protected pickup/output operates on existing owned real containers. | One loaded owned chunk, finite exact payload, exclusive durable custody and no automatic output replay. Existing bound jacks remain fixed real storage. [Cargo rules and crash boundary](FURNITURE_CARGO_R4.md) apply. |
| `DISPOSAL` | Opens a real paper bin. Explicit `/furniture shred <id> confirm` destroys eligible plain paper/books. | This operation is intentionally destructive and requires confirmation. Other materials and custom PDC/item-model items remain. The inventory must be closed first. |
| `FAN` | Toggles bounded air movement affecting only the consenting nearby owner. | No pushing others, flight grant or force across obstructed/unauthorized space; no thermal simulation. |
| `SCALE` | The luggage scale measures carried items or actual nearby owned bound storage, with a session tare; the height backdrop measures current player height. | Read-only measurement of actual state, labelled game counts/blocks rather than kilograms or a medical measurement. |
| `STATUS` | Ordinary server status shows tick time, online population and owned placement count. The exact weather kiosk shows actual loaded-world rain/thunder, time, state timers and weather-cycle state. | No secrets, invented network activity or real-world forecast. |
| `PARTICLES` | Toggles bounded owner-visible water, smoke or fragrance visuals. | Only intrinsically ambient decorative fixtures use it; no harmful effect or world-block mutation. |
| `DECORATION` | Intrinsic ornaments have owned placement, rotation, removal and a saved cosmetic accent. Exact reviewed gateways/arches and bandstands additionally use authored solid colliders with real openings or an existing supported stage floor. | Only two planters and the doorway toran are intrinsically decorative in the primary set. Structure blueprints are explicit; the generic decorative behavior alone does not promise walk-through space, precipitation shielding or a physical stage. |
| `SERVICE` | Calls an allowlisted actual service, with exact handlers for camera maps, consented records, fictional exposure, surface rescue, paid ticket validation and timed vehicle-bay leases. | Each handler retains its current session, property, supply/receipt and consent checks. Category enablement does not commission an entrance, bay, camera or route. |

Storage and processing models retain a physically present backing block. Stationary bed mode likewise uses a real existing bed. The exact stretcher and pallet jack offer optional stationary backing alongside their distinct unbound movement modes; legacy bound placements still load. Placement near or around a backing is constrained by authored bounds and owner property. Concealment and exact alignment require the real clients; this adapter does not claim to invisibly replace the vanilla block.

## Ownership, persistence and recovery

The root Ledger commits bank debit and asset-grant intent in one durable operation. `grant(grantId, owner, sourceId)` commits the same unique entitlement in this module, and the Ledger acknowledges only afterward. Exact grant replay is idempotent; a different owner or source ID under the same UUID fails. Placement, rotation, control state and removal mutate that entitlement. Removal never duplicates it or drops a fresh item.

The furniture aggregate now writes **FUR3** payloads inside the checksummed compare-and-swap `SnapshotStore`, bounded at **16 MiB**. The decoder continues reading FUR1 and FUR2. Merely opening an old file does not rewrite it. The first successful new mutation retains UUID, owner, source ID, placement, binding and original backing data while adding the explicit geometry revision. The 24 old miniature structures keep their old reserved bounds and remain suspended until the owner deliberately removes and recommissions them at their authored placement scale. They never silently expand into other blocks or property. Exact former ornamental clock/weather/food/cart accent flags are normalized off in memory; this does not activate a machine. Existing light backings and other valid control settings remain intact. An older binary cannot read the new payload; retain the stopped-copy data backup when testing a rollback.

Invalid records, unknown IDs, wrong backing kinds/materials, invalid cross-model controls, duplicate reservations, overlapping placements, corrupt checksums and stale writes fail closed. An ordinary failed durable mutation leaves its prior aggregate unchanged. Wheelchair movement first validates and moves its real projections, then changes the one authoritative current in-memory placement; parking and roughly five-second checkpoints persist that pose. A failed motion checkpoint retains the current in-memory pose and freezes movement for retry instead of rewinding the real rider. Native displays, text displays, payload previews and seat carriers are nonpersistent; they are reconstructed only in loaded worlds/chunks. There are no furniture inventory payloads in this snapshot.

A borrowed shopping cart keeps the original nest's persisted placement fixed. Its one current loan and component pose live in a bounded separate cart snapshot, with ordinary park/checkpoint semantics. An unresolved loan prevents removal or relocation of that nest; a held load additionally retains the existing exclusive cargo receipts. Current access, loaded supported floor and the full cart/payload geometry gate reconstruction and collision publication. Loss of access removes the projection without erasing the loan, pose or cargo. No motion resumes automatically.

`gtm:ottoman_storage` keeps its primary `SEAT` and optional `NONE` requirement so existing unbound FUR1/FUR2 placements still load and sit. Only this exact seating ID may additionally bind a real chest/barrel through the existing `Binding` field. Its explicit Open storage control and optional sneak-use open that same protected vanilla inventory; removal or disconnection never copies or deletes contents. Binding is performed while unplaced, and actual storage requires the current ownership, loaded/live footprint, property entry, five-block visibility and backing-container checks. No second inventory database or new transferable entitlement is created.

Real inventory and processing state uses **normal vanilla world persistence**. The cargo sidecar temporarily stores inaccessible exact supplied bytes only while both real endpoints are exclusively locked; it supplies no second accessible inventory. A released cargo receipt discards those bytes. No claim is made of an atomic transaction spanning Minecraft player data, chunk data, furnace progress and furniture/cargo snapshots. Normal/stopped-copy restart tests must verify that boundary. Wash operations debit actual water before changing the existing held item; interruption may lose a water level, but does not create another valuable item. Shredding creates no output and cannot duplicate discarded paper.

Container markers have a separate world-save boundary from the furniture snapshot. Interrupted binding or release keeps the saved reservation protected and refuses access. `repairBinding` restores only a missing/matching marker at the same reserved block, after owner/property/loaded/reach checks, unchanged structural data, no conflicting marker, no vanilla lock and no viewers. Transient barrel lid state and furnace burning state are ignored for structural comparison. Repair never copies or clears contents.

Light changes retain both desired and prior brightness, so an interrupted intent/apply sequence can recognize the previous real level. Lever and trapdoor controls compare unchanged structural block data. Desired state is saved before application. Removal, shutdown and disabled-module cleanup restore the original known owned backing data. Restoration never force-loads a chunk. A loading flap is not closed onto an occupant; an unplaced reservation can retry restoration, and unbinding refuses to discard its restoration metadata while the flap remains blocked.

## Placement, collision and access

Every mutation runs on the Paper server thread. Every owner interaction rechecks authentication, `gtm.furniture`, current ownership, distance, placement availability, backing validity and property access. A service also needs its allowlist entry and actual callback. Workstation views additionally store the authenticated connection nonce; inventory clicks, drags, crafting preparation and periodic reconciliation close or deny an expired, moved-away or changed-session view. Auth loss closes protected inventories/workstations, dismounts seats and wakes a bound-bed sleeper.

`ownerMayBuild` must authorize the complete authored model bounds, including its quarter-turn orientation and the union with all real backing blocks. Purchase validation requires either an owned, empty, supported aimed floor or the correct unreserved real backing block. Placement repeats the full validation. No ordinary player is charged on the assumption that an unknown property or required backing block might become available later.

Target rays preflight loaded chunks before calling Bukkit tracing. LIGHT uses a bounded visible-cell scan, because ordinary collision rays skip it. Bed halves crossing chunk boundaries are checked before accessing either half. Placement rejects other blocks/entities, fluids, unsupported floors, overlap, outside-world positions and invalid backing distances. It never removes a block to make room.

Defaults remain 32 entitlements per owner, 2,048 total and 64 per anchor chunk. Active visuals remain bounded to 128 instances, at most four reconstructions per tick call, with an authenticated observer within 64 blocks. No world or chunk is force-loaded. Core normally calls the module every ten ticks. These limits can suspend far-away visuals without deleting ownership.

Walking-player collision and the injected vehicle obstacle provider use conservative AABBs. Open barriers use their folded AABB; their complete closed footprint remains reserved. A bridge uses the actual real trapdoor collision. This is not complete arbitrary-mob physics, mesh-triangle collision, rigged door animation or a virtual walkable platform engine. Hollow model openings and exact physical fit still need client qualification.

Reservations protect ordinary break/place, piston, explosion, fluid and relevant block-change events. Bound inventories block automated transfers and unauthorized open/click/drag. Beds and carriers reject unauthorized entry. Cauldrons and controlled lever/flap interactions retain the owner boundary. Plugins that bypass normal events can alter a backing block; incompatible changes suspend use rather than overwrite it speculatively.

All furniture use remains owner-only. Shared household permissions and public service kiosks require an explicit access-policy extension; the presence of a public-looking model does not silently grant other users access.

## Integration surface and controls

The existing constructor, `Options`, `Access` and purchase/grant/place/bind/use/rotate/remove methods are preserved. `Owned.settings()` is additive; the prior boolean constructor and `lightOn()` accessor remain available. `FurnitureCatalog.bundled()` reads the exact 200-row primary file then optionally merges `extensions.tsv`. Both use the same 14-column profile/header. Extensions are limited to 512 entries and cannot override any existing ID. Only the primary file enforces exactly 200 rows.

Additional public controls:

```java
static String actionLabel(FurnitureCatalog.Entry entry);
void setText(Player player, UUID id, String plainText);
void setBrightness(Player player, UUID id, int level);       // 0..15
void setClock(Player player, UUID id, boolean hours24, int alarmMinute); // -1 disables
void setMusic(Player player, UUID id, int melody, int volume); // each 0..3
void shred(Player player, UUID id, boolean confirmed);
```

The setters declare `IOException` where they commit furniture state. They call the same owner/auth/reach/property validation as ordinary use. `shred` acts on real block inventory and requires explicit confirmation. These methods support the separately owned menu. Command access is also implemented:

```text
/furniture text <entitlement UUID> your notice | second line
/furniture brightness <UUID> 0-15
/furniture alarm <UUID> HH:mm
/furniture alarm <UUID> off
/furniture format <UUID> 12|24
/furniture music <UUID> <melody 0-3> <volume 0-3>
/furniture shred <UUID> confirm
```

The normal flow remains shop → review actual mechanic/price → purchase → connect backing when required → place on surveyed owned floor → use/rotate/remove. Changing a source model ID does not manufacture an entitlement.

## Executed verification and API evidence

The first isolated Java25/Gradle9.2.1 furniture domain run passed **34 JUnit tests, zero failures, errors or skips**: the 16 original cases plus the then-current 18 expansion cases. It compiled the actual current pure furniture classes, SnapshotStore, GtmAssetCatalog and actual bundled resources. The isolated project is `/workspace/scratch/d7d343b39c16/toolchains/furniture-domain-check`; it does not replace the production build.

The first production targeted run reached Java compilation and reported only the then-missing `GtmSigns` integration class (seven dependent missing-symbol diagnostics). It reported no furniture or vehicle compilation errors, but that failed run is **not** a completed production build. The subsequent coherent production run superseded that failure: `test --tests 'com.sdcraft.core.furniture.*'` completed in 14 seconds with successful exact-build255 `compileJava` and `compileTestJava`, followed by **38 passing furniture tests**, zero failures/errors/skips. These comprise 16 original tests, 20 expansion tests and the UI agent's two `FurnitureMenuInputTest` cases. This is a targeted production test result; the root still owns the final full-check/JAR evidence.

New cases verify real smoker type enforcement; rejection of storage masquerading as a processor; cauldron/lever/flap material and exclusive binding; controls rejected on wrong models or wrong owners; notices surviving removal; folded collision without releasing the reserved footprint; interrupted light levels and off-state intent; bounded Unicode/control data; clock origin and midnight behavior; alarm once per day without catch-up; saved music without phantom items; stale settings writes; and FUR1 migration for both an active light and an unplaced reserved storage grant. Extension tests enforce separate primary count, distinct IDs, no override, known behavior and safe service identifiers. Two additional regression cases verify that disabling a backend immediately hides an allowlisted service and that a per-customer permission/commissioning refusal runs before the purchase path proceeds. The `Access.serviceEnabled` default denies sales until integration explicitly supplies a real backend gate; `serviceUnavailable` supplies customer-specific reasons.

Exact signatures were inspected with `javap` on the pinned Paper26.3 build255 API, SHA256 `16d784a1b2a6a0be74479c761d9b5cbd7271ee1d8d5ff45f8060d0fa352f1d0b`. The locally extracted matching server bytecode confirms that CraftInventoryView returns its stored top inventory and the vanilla data contains `data/minecraft/recipe/book_cloning.json`, consuming actual source/target books and yielding `minecraft:written_book`. Online primary references: [HumanEntity workstations and sleep](https://jd.papermc.io/paper/26.3/org/bukkit/entity/HumanEntity.html), [LivingEntity item use](https://jd.papermc.io/paper/26.3/org/bukkit/entity/LivingEntity.html), [PrepareItemCraftEvent](https://jd.papermc.io/paper/26.3/org/bukkit/event/inventory/PrepareItemCraftEvent.html), and [display entities](https://docs.papermc.io/paper/dev/display-entities/). Online docs may show a later patch; the compiled API stays pinned.

## Required isolated-server and real-client acceptance

These are outstanding acceptance steps, not completed claims:

1. Survey and register actual private-property floors; preserve the stopped-copy data/world backup. Test owner, authenticated non-owner and unauthenticated accounts. Confirm rejected purchase/placement never charges or consumes an entitlement.
2. Buy, replay, place, rotate, remove and replace one instance of every behavior family. Restart, unload chunks and revisit; compare unique grant count and visible entity count. No forced chunk load or duplicate physical voucher may occur.
3. Put distinctive custom-data items in storage and smoker inventories. Exercise fuel/process progress, shift-click/drag, hopper/dropper attempts, owner loss, chunk reload and stopped-copy restart. Compare actual items and fuel exactly; verify repair changes only the reservation marker.
4. Exercise all real workstation menus and normal recipes. At the copier allow book cloning only, retaining its original and consuming writable books. Walk away, revoke auth, reconnect and replay packets; no stale session may craft or extract output.
5. Test wash with exactly one dyed leather item/banner, no water, lava/empty cauldron, multiple held items and foreign players. Verify one water debit and only the intended metadata change. Refill through normal owned cauldron interaction.
6. Measure LIGHT levels0–15, toggling from level0, restart between saved intent and application, removal and disabled cleanup. Operate real lever circuits and trapdoor flaps. Ensure a blocked flap cannot close or lose its restoration reservation.
7. Place a barrier beside players, vehicles, blocks and property edges. Confirm its visual folded orientation matches dynamic collision in all four turns, closing refuses occupants, and another furniture item cannot occupy its reserved open footprint.
8. Save Unicode notices, 12/24-hour clocks, alarms and muted music. Reload and verify content. Alarm must not replay missed days; music must stop for invalid sessions/reach. Inspect both editions' TextDisplay, sounds, menus and native128 textures.
9. Check every service callback against its real permissions, fees, stock and vehicle/property prerequisites. A disabled or missing service must fail visibly without a fake replacement. Verify station-local workshop/refuel and genuine parking/wardrobe behavior in the root integration.
10. Inspect model/body alignment, bed halves, seat hip/feet/headroom and safe dismount in real Java and Bedrock. The marker seat pose offset remains an unqualified calibration. Inspect all conservative hollow-model bounds and architectural mounting positions before city furnishing.
11. Confirm decorative accents and ambient effects are bounded, furniture fans affect only the consenting owner, and cargo preview reflects the real backing inventory without creating a pickup item. Test explicit paper shredding with protected custom item metadata and non-paper items.
12. Install actual purchased/authorized furniture into surveyed world interiors only after these checks. A complete descriptor catalogue and a successful server boot alone do not satisfy the brief's furnished-world requirement.

## Exact primary model assignments

These 200 source assignments preserve each original ID. Named actual-effect reports and remaining native-client gates are tracked separately in the functionality inventory.

| Asset ID | Behavior | Title | Implemented source behavior |
|---|---|---|---|
| `gtm:sectional_sofa` | SEAT | Sectional Fabric Lounge Sofa | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:leather_armchair` | SEAT | Executive Club Leather Armchair | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:coffee_table_teak` | READING | Solid Teak Low Coffee Table | Use with a held written book to read, or held food to eat through normal consumption; no food or items are supplied. |
| `gtm:glass_end_table` | READING | Tempered Glass Corner End Table | Use with a held written book to read, or held food to eat through normal consumption; no food or items are supplied. |
| `gtm:media_console` | STORAGE | Modern Credenza TV Media Console | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:floor_arc_lamp` | LIGHT | Curved Brass Arch Floor Lamp | Controls a bound real LIGHT block with saved on/off and brightness 0-15; restores its original level on removal. |
| `gtm:bookshelf_open` | STORAGE | Open Geometric Display Bookshelf | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:accent_chair_velvet` | SEAT | Emerald Velvet Cocktail Chair | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:magazine_rack` | STORAGE | Brushed Brass Floor Magazine Stand | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:wall_display_unit` | STORAGE | Floating Backlit Wall Display Shelf | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:ottoman_storage` | SEAT | Tufted Storage Ottoman Footstool | One usable seat plus optional real owner-only chest/barrel storage. Connect an existing container while unplaced, then use the explicit Open storage control or sneak-use. Unbound legacy ottomans remain usable seats; storage items stay in the vanilla block. |
| `gtm:chaise_lounge` | SEAT | Contoured Velvet Chaise Lounge | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:nesting_tables` | READING | Trio Marble Round Nesting Tables | Use with a held written book to read, or held food to eat through normal consumption; no food or items are supplied. |
| `gtm:credenza_sideboard` | STORAGE | Fluted Oak Dining Sideboard | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:room_divider_jali` | BARRIER | Laser-Cut Wooden Jali Privacy Screen | Owner-operated folding barrier with saved open state and server-enforced closed/folded collision; closing refuses occupied space. |
| `gtm:indoor_planter` | DECORATION | Polished Terrazzo Tall Floor Planter | Intrinsically decorative object with owned placement, rotation, removal and a saved accent-light toggle. |
| `gtm:ceiling_fan_wood` | FAN | Carved Wooden 5-Blade Ceiling Fan | Owner-controlled bounded airflow pushes only its consenting nearby owner through clear authorized space. |
| `gtm:fireplace_electric` | LIGHT | Recessed Modern Electric Hearth | Controls a bound real LIGHT block with saved on/off and brightness 0-15; restores its original level on removal. |
| `gtm:wall_mirror_sunburst` | SERVICE | Gilded Brass Sunburst Wall Mirror | Invokes the actual wardrobe service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:pouffe_cushion` | SEAT | Embroidered Cotton Round Floor Pouffe | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:king_bed_upholstered` | BED | Upholstered King Master Bed | Uses one bound real bed under normal Minecraft sleep rules. Extra bunks, healing and transport are separate functions. |
| `gtm:single_cot_wood` | BED | Solid Sheesham Single Platform Bed | Uses one bound real bed under normal Minecraft sleep rules. Extra bunks, healing and transport are separate functions. |
| `gtm:nightstand_drawers` | STORAGE | Dual-Drawer Oak Bedside Nightstand | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:wardrobe_sliding` | STORAGE | 3-Door Mirrored Sliding Wardrobe | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:dresser_mirror` | STORAGE | 6-Drawer Dresser with Vanity Mirror | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:bedside_sconce` | LIGHT | Articulated Brass Reading Wall Sconce | Controls a bound real LIGHT block with saved on/off and brightness 0-15; restores its original level on removal. |
| `gtm:blanket_chest` | STORAGE | Carved Teak Storage Blanket Trunk | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:vanity_stool` | SEAT | Padded Round Vanity Dressing Stool | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:full_length_mirror` | SERVICE | Standing Cheval Full-Length Mirror | Invokes the actual wardrobe service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:clothes_valet` | STORAGE | Executive Wooden Coat & Trouser Valet | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:bed_bench_tufted` | SEAT | Upholstered Foot-of-Bed Bench | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:bunk_bed_twin` | BED | Compact Steel Bunk Bed Twin Stack | Uses one bound real bed under normal Minecraft sleep rules. Extra bunks, healing and transport are separate functions. |
| `gtm:canopy_bed_frame` | BED | Minimalist Steel Poster Canopy Bed | Uses one bound real bed under normal Minecraft sleep rules. Extra bunks, healing and transport are separate functions. |
| `gtm:corner_wardrobe` | STORAGE | Space-Saving Corner Bedroom Wardrobe | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:alarm_dock_station` | CLOCK | Smart Display Bedside Radio Clock | Displays actual world time; saved 12/24-hour mode and one alarm per world day, with no offline catch-up spam. |
| `gtm:modular_counter_base` | STORAGE | Granite-Top Modular Base Cabinet | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:kitchen_sink_double` | WASH | Under-Mount Double Stainless Sink | Uses a bound real water cauldron to wash dyed leather or remove one banner pattern, consuming one water level. |
| `gtm:gas_stove_4burner` | SMOKER | Cast-Iron 4-Burner Glass Hob Counter | Operates a bound real smoker: actual ingredients, fuel, cooking progress and output remain in the vanilla block. |
| `gtm:chimney_hood` | FAN | Stainless Steel Ductless Kitchen Hood | Owner-controlled bounded airflow pushes only its consenting nearby owner through clear authorized space. |
| `gtm:refrigerator_french` | STORAGE | Double-Door French Refrigerator | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:microwave_cabinet` | SMOKER | Built-In Convection Oven Tower | Operates a bound real smoker: actual ingredients, fuel, cooking progress and output remain in the vanilla block. |
| `gtm:dining_table_6seater` | READING | Extending Teak 6-Seater Dining Table | Use with a held written book to read, or held food to eat through normal consumption; no food or items are supplied. |
| `gtm:dining_chair_cushion` | SEAT | Ergonomic Upholstered Dining Chair | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:kitchen_island` | CRAFTING | Marble-Top Prep Island with Stool Overhang | Real vanilla crafting workbench; recipes consume the player's actual ingredients. |
| `gtm:bar_stool_swivel` | SEAT | Adjustable Leather Swivel Bar Stool | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:spice_rack_carousel` | STORAGE | 3-Tier Rotating Brass Masala Carousel | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:wall_cupboard_glass` | STORAGE | Frosted Glass Overhead Wall Cupboard | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:chai_brew_station` | SERVICE | Commercial Brass Samovar Chai Machine | Invokes the actual food service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:tandoor_clay_oven` | SMOKER | Insulated Commercial Clay Tandoor Drum | Operates a bound real smoker: actual ingredients, fuel, cooking progress and output remain in the vanilla block. |
| `gtm:ro_water_purifier` | SERVICE | Wall-Mount Active Carbon RO Filter | Invokes the actual hydration service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:cutlery_cart_mobile` | STORAGE | Stainless Mobile Kitchen Utility Cart | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:pantry_tall_unit` | STORAGE | Pull-Out Wire Basket Tall Larder Unit | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:breakfast_counter` | READING | Wall-Mounted Fold-Down Breakfast Bar | Use with a held written book to read, or held food to eat through normal consumption; no food or items are supplied. |
| `gtm:pot_rack_hanging` | STORAGE | Ceiling-Hung Wrought Iron Pan Gantry | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:dishwasher_undercounter` | WASH | Integrated High-Efficiency Dishwasher | Uses a bound real water cauldron to wash dyed leather or remove one banner pattern, consuming one water level. |
| `gtm:executive_desk_lshape` | SERVICE | Executive L-Shaped Walnut Workstation | Invokes the actual phone service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:ergonomic_task_chair` | SEAT | High-Back Mesh Synchronous Task Chair | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:dual_monitor_mount` | SERVICE | Dual 27-Inch Curved Screen Rig | Invokes the actual phone service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:filing_cabinet_fireproof` | STORAGE | 4-Drawer Heavy Gauge Lockable File | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:server_rack_half` | STATUS | 18U Sound-Dampened Network Rack | Shows actual server timing, online population and the owner's placed furniture count; exposes no private server data. |
| `gtm:conference_table_10p` | READING | Conference Boardroom Boat Table | Use with a held written book to read, or held food to eat through normal consumption; no food or items are supplied. |
| `gtm:boardroom_chair` | SEAT | Cantilever Chrome Mid-Back Guest Chair | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:magnetic_whiteboard` | DISPLAY | Mobile Rolling Dry-Erase Whiteboard | Owner-editable plain-text notice saved across restart and rendered as a bounded text display; never runs commands. |
| `gtm:reception_podium` | SERVICE | Curved Front Welcome Security Desk | Invokes the actual phone service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:credenza_creed` | STORAGE | Office Storage Buffet Credenza | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:water_dispenser` | SERVICE | Freestanding Hot/Cold Water Cooler | Invokes the actual hydration service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:printer_copier_station` | COPYING | Heavy Duty Multifunction Floor Copier | Real crafting workbench restricted to the vanilla written-book copying recipe; requires supplied originals and writable books. |
| `gtm:workstation_cubicle` | SERVICE | 2-Person Acoustic Screen Desk Pod | Invokes the actual phone service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:desk_lamp_led` | LIGHT | Balanced Arm Studio Architect Lamp | Controls a bound real LIGHT block with saved on/off and brightness 0-15; restores its original level on removal. |
| `gtm:presentation_screen` | DISPLAY | 75-Inch Smart Interactive Display Stand | Owner-editable plain-text notice saved across restart and rendered as a bounded text display; never runs commands. |
| `gtm:literature_carousel` | STORAGE | Rotating Metal Brochure Display Tower | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:acoustic_pod_solo` | SERVICE | Single-Person Soundproof Phone Booth | Invokes the actual phone service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:shredder_bin` | DISPOSAL | High-Security Cross-Cut Paper Shredder | Protected real paper bin. Opens actual contents; explicit shred confirmation removes only plain papers/books, never arbitrary items. |
| `gtm:coat_stand_tree` | STORAGE | Heavy Base Stainless Reception Coat Rack | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:cable_spine_vertical` | POWER | Flexible Articulated Underdesk Wire Spine | Controls a bound existing lever and its real redstone circuit. Saved owner switch state; restores original state on release. |
| `gtm:hospital_icu_bed` | BED | Motorized 4-Section Electric ICU Bed | Uses one bound real bed under normal Minecraft sleep rules. Extra bunks, healing and transport are separate functions. |
| `gtm:mobile_iv_pole` | UTILITY | 5-Castor Stainless Telescopic IV Pole | Hold one honey bottle and carry one paper: returns the bottle and supplies eight one-second pulses of one health and 0.5 saturation while nearby. Self only; never revives DOWNED. |
| `gtm:examination_table` | SERVICE | Padded Clinical Examination Table | Invokes the actual medical_treatment service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:defibrillator_crash_cart` | SERVICE | Red Emergency Crash Cart with Monitor | Invokes the actual medical_treatment service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:patient_privacy_screen` | BARRIER | Washable Antimicrobial 3-Fold Screen | Owner-operated folding barrier with saved open state and server-enforced closed/folded collision; closing refuses occupied space. |
| `gtm:mayo_surgical_stand` | STORAGE | Adjustable Height Surgical Instrument Tray | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:vital_signs_monitor` | SERVICE | Multi-Parameter ECG & SpO2 Mobile Cart | Invokes the actual medical_status service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:medicine_dispense_cabinet` | STORAGE | Dual-Lock Narcotic Medication Safe | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:wheelchair_standard` | SEAT | Foldable Chrome Hospital Wheelchair | Owner-driven wheelchair: forward/back on flat supported floor inside your owned parcel; tap left/right while stopped for cardinal turns, jump to brake and sneak to exit. Real passenger/model motion, swept collision and saved parking; public-street travel and assisted pushing are not implemented. |
| `gtm:transport_stretcher` | BED | Heavy-Duty Emergency Hydraulic Gurney | Unbound mode carries one explicitly consenting nearby patient at 0.8 blocks/s under the owning on-foot attendant's controls, within authorized owned ground; current-session and swept-body checks apply. Optional bound-bed mode retains ordinary sleep and disables transport. |
| `gtm:operating_theatre_lamp` | LIGHT | Dual-Head Balanced Surgical Ceiling Lamp | Controls a bound real LIGHT block with saved on/off and brightness 0-15; restores its original level on removal. |
| `gtm:autoclave_sterilizer` | UTILITY | Benchtop Hospital Grade Autoclave Unit | Hold two paper; supply one string, coal and water bucket. After eight seconds nearby, receive one usable native first-aid kit restoring eight health. Returns the bucket; canceled consumed inputs are not refunded. |
| `gtm:scrub_sink_double` | WASH | Knee-Operated Surgical Scrub Sink | Uses a bound real water cauldron to wash dyed leather or remove one banner pattern, consuming one water level. |
| `gtm:hospital_overbed_table` | READING | Hydraulic Cantilever Overbed Tray | Use with a held written book to read, or held food to eat through normal consumption; no food or items are supplied. |
| `gtm:triage_nursing_station` | SERVICE | High-Front Ergonomic Triage Desk | Invokes the actual medical_treatment service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:oxygen_cylinder_trolley` | UTILITY | Dual 50L Medical Oxygen Tank Cart | Hold one ordinary water-breathing potion: returns its bottle and supplies 20 one-second pulses of 40 actual air ticks while the owner stays within five visible blocks. Self only; never revives DOWNED. |
| `gtm:biohazard_foot_bin` | STORAGE | Hands-Free Step-On Biohazard Container | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:xray_viewing_lightbox` | LIGHT | Wall-Mount Twin LED Radiograph Viewer | Controls a bound real LIGHT block with saved on/off and brightness 0-15; restores its original level on removal. |
| `gtm:phlebotomy_chair` | SEAT | Armrest Blood Collection Donor Chair | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:hospital_bedside_locker` | STORAGE | Molded Medical Cabinet with Towel Rail | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:interrogation_table` | READING | Heavy Bolted Metal Interrogation Table | Use with a held written book to read, or held food to eat through normal consumption; no food or items are supplied. |
| `gtm:suspect_restraint_chair` | SEAT | Reinforced Fixed Frame Interrogation Seat | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:evidence_locker_grid` | STORAGE | Numbered Heavy Mesh Evidence Lockers | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:booking_fingerprint_kiosk` | SERVICE | Biometric Digital Booking Terminal | Records your own game identity, or a nearby authenticated player's explicit time-limited consent under current police authority. Persists game UUIDs, operator, case and time; current kiosk authorization gates the archive. One real book and ink sac produces one receipted written report. Fictional game records only; no real biometrics or identity matching. |
| `gtm:jail_cell_bunk_steel` | BED | Wall-Anchored Dual Steel Cell Bunks | Uses one bound real bed under normal Minecraft sleep rules. Extra bunks, healing and transport are separate functions. |
| `gtm:cell_combi_toilet_sink` | WASH | Stainless Vandal-Resistant Prison Fixture | Uses a bound real water cauldron to wash dyed leather or remove one banner pattern, consuming one water level. |
| `gtm:patrol_sergeant_desk` | SERVICE | Bullet-Resistant Acrylic Shield Desk | Invokes the actual police service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:weapon_armory_cage` | STORAGE | Vertical Racked Long-Gun Security Cage | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:wanted_bulletin_corkboard` | DISPLAY | Glass-Enclosed Police Notice Board | Owner-editable plain-text notice saved across restart and rendered as a bounded text display; never runs commands. |
| `gtm:breathalyzer_test_bench` | SERVICE | Certified Sobriety Testing Counter | Measures actual server-recorded fictional drink exposure for self or a nearby explicitly consenting player. Current sessions, range and live owned bench required. Fictional game units, never BAC or a medical result. |
| `gtm:detention_bench_handcuff` | SEAT | Floor-Bolted Steel Bench with Cuff Rail | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:mugshot_height_backdrop` | SCALE | Calibrated Wall-Mount Height Measurement | Shows measured player bounding-box height or actual carried item/stack counts in clearly labelled game units. |
| `gtm:surveillance_wall_cctv` | SERVICE | Quad-Monitor Video Observation Console | Commission up to four owned camera points within 32 blocks; one real blank map becomes an owner-bound 128×128 progressive monitor of actual loaded blocks and current entity silhouettes within 16 blocks. Direction controls and current session, range, property and loaded-volume gates pause and clear the feed; no camera teleport or chunk loading. |
| `gtm:riot_shield_rack` | STORAGE | Mobile Interlocking Lexan Shield Stand | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:traffic_radar_calibration` | SERVICE | Highway Patrol Speed Kit Calibration Desk | Invokes the actual police_speed service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:retail_cashwrap_wrap` | SERVICE | Modern Retail Cashier Counter Wrap | Invokes the actual retail service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:clothing_gondola_double` | STORAGE | Dual-Sided Garment Hanging Gondola | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:supermarket_produce_bin` | STORAGE | Slanted 3-Tier Wooden Fruit Crate Rack | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:checkout_belt_counter` | SERVICE | Electric Conveyor Checkout Counter | Invokes the actual retail service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:beverage_cooler_glass` | STORAGE | Commercial 2-Door Illuminated Drink Case | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:ice_cream_freezer` | STORAGE | Curved Glass Chest Ice Cream Showcase | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:bakery_glass_display` | SERVICE | Heated Glass Pastry & Samosa Counter | Invokes the actual food service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:mannequin_podium` | SERVICE | Square Lacquered Retail Display Plinth | Invokes the actual wardrobe service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:shoe_display_wall` | STORAGE | Slatwall Angled Footwear Display Unit | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:jewelry_glass_case` | STORAGE | Lockable Velvet-Lined Showcase Pedestal | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:pharmacy_pill_bay` | STORAGE | Gravity-Feed Medication Dispenser Wall | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:atm_lobby_enclosure` | SERVICE | First National Bank ATM Kiosk Fascia | Invokes the actual bank service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:security_turnstile_rfid` | BARRIER | Optical Glass Flap Access Barrier | Owner links this real entrance barrier to a nearby ticket validator. An authenticated permitted customer scans one acknowledged paid serial to open the passage for three seconds; consumed serials cannot replay and closing waits for a clear footprint. |
| `gtm:shopping_cart_nest` | UTILITY | Row of 10 Interlocked Wire Supermarket Carts | The fixed owned nest lends one movable cart component in its loaded owned chunk. Push on foot at 0.6 blocks/s; supplied goods use exclusive real-container cargo custody. Return only after unloading and reaching the same original nest; no new furniture entitlement or copied inventory is created. |
| `gtm:fitting_room_cubicle` | SERVICE | Curtained Boutique Dressing Booth | Invokes the actual wardrobe service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:retail_security_gate` | BARRIER | EAS Anti-Theft Sensor Pedestal Pair | Owner commissions and arms the real passage, tags actual held stock and clears tags at checkout. An authenticated permitted player crossing with this gate's active stock tag triggers a native sound and visible alarm; no crime, fine or item copy is created. |
| `gtm:snack_vending_machine` | SERVICE | Coil-Drop Snack & Cold Drink Vendor | Invokes the actual food service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:magazine_kiosk_wire` | STORAGE | Rotating Outdoor Newspaper Wire Tree | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:cosmetics_tester_bar` | SERVICE | Illuminated Mirror Makeup Sampler Unit | Invokes the actual wardrobe service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:pos_pedestal_standalone` | SERVICE | Touchscreen Tablet Self-Service Terminal | Invokes the actual retail service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:bulk_grain_dispenser` | STORAGE | Hygienic Acrylic Dal & Rice Hopper Bank | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:umbrella_stand_drip` | STORAGE | Entryway Commercial Brass Umbrella Drip Pan | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:crowd_stanchion_belt` | BARRIER | Retractable Red Nylon Queue Barrier Post | Owner-operated folding barrier with saved open state and server-enforced closed/folded collision; closing refuses occupied space. |
| `gtm:electronics_demo_bench` | SERVICE | Security-Tethered Smartphone Demo Table | Invokes the actual phone service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:luggage_scale_weigh` | SCALE | Airport & Courier Platform Floor Scale | Measures actual carried or nearby owned-container item counts with a session tare; reports game load units, not physical kilograms. |
| `gtm:park_bench_teak` | SEAT | Cast-Iron Teak Slat Garden Bench | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:street_lamppost_colonial` | LIGHT | Double-Arm Ornate Victorian Streetlamp | Controls a bound real LIGHT block with saved on/off and brightness 0-15; restores its original level on removal. |
| `gtm:bus_shelter_glass` | SEAT | Modern Cantilever Glass Transit Shelter | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:municipal_litter_bin` | STORAGE | Split Dual Wet/Dry Municipal Street Bin | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:traffic_bollard_steel` | BARRIER | Reflective Banded Cast Steel Bollard | Owner-operated folding barrier with saved open state and server-enforced closed/folded collision; closing refuses occupied space. |
| `gtm:tree_planter_curb` | DECORATION | Polished Granite Geometric Street Planter | Intrinsically decorative object with owned placement, rotation, removal and a saved accent-light toggle. |
| `gtm:vendor_kiosk_tea` | SERVICE | Pavement Steel Tapri Chai Kiosk | Invokes the actual food service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:street_market_tarp` | SERVICE | Bamboo Frame Weathered Vendor Canopy | The authored vendor counter provides real priced food orders, finite stock, preparation and visible owner collection. Its actual posts, counter and canopy keep distinct collision shapes; no rain protection or invented merchandise is supplied. |
| `gtm:drinking_fountain_pedestal` | SERVICE | Dual-Height Bubbler Chilled Fountain | Invokes the actual hydration service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:bicycle_docking_rack` | SERVICE | 6-Slot Wave Tube Public Bike Stand | Invokes the actual parking service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:fire_hydrant_brass` | UTILITY | Dual Pumper Connection High-Pressure Hydrant | Hold one ordinary water bucket: returns its empty bucket and supplies 20 seconds of hose action on owned visible FIRE within eight blocks and the burning owner. Stay within five blocks of the hydrant. |
| `gtm:traffic_signal_pole` | POWER | 4-Way Mast Arm LED Traffic Signal Light | Commission an inspected owned intersection; timed north/south and east/west phases control native player and NPC road vehicles at full-body stop lines. Real lever and phase label reflect the cycle. Explicit start; stops on ownership/session/geometry loss. |
| `gtm:speed_camera_gantry` | SERVICE | Overhead Automatic Radar Flash Housing | Invokes the actual police_speed service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:street_name_signpost` | DISPLAY | Bilingual Cast Heritage Road Sign | Owner-editable plain-text notice saved across restart and rendered as a bounded text display; never runs commands. |
| `gtm:utility_junction_box` | POWER | Ground-Mounted Electric Cable Cabinet | Controls a bound existing lever and its real redstone circuit. Saved owner switch state; restores original state on release. |
| `gtm:public_emergency_pillar` | SERVICE | Direct-to-SDPD Panic Intercom Column | Invokes the actual police service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:decorative_fountain_tier` | PARTICLES | Central Plaza 3-Tier Stone Fountain | Owner-controlled bounded ambient water, smoke or fragrance particles; saved on/off state, no harmful or block-changing effects. |
| `gtm:pavement_newspaper_stand` | STORAGE | Folding Metal Morning News Stand | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:concrete_barrier_jersey` | BARRIER | Standard Interlocking Highway Jersey Barrier | Owner-operated folding barrier with saved open state and server-enforced closed/folded collision; closing refuses occupied space. |
| `gtm:pedestrian_crossing_beacon` | LIGHT | Solar Flashing Amber Pedestrian Marker | Controls a bound real LIGHT block with saved on/off and brightness 0-15; restores its original level on removal. |
| `gtm:street_paan_stall` | SERVICE | Compact Glass-Front Betel Leaf Stall | Invokes the actual food service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:rooftop_satellite_dish` | SERVICE | High-Gain Parabolic Telecom Dish Array | Invokes the actual phone service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:security_checkpoint_barrier` | BARRIER | Counterweighted Boom Gate Arm | Owner-operated folding barrier with saved open state and server-enforced closed/folded collision; closing refuses occupied space. |
| `gtm:coastal_lifebuoy_stand` | SERVICE | Harbour Marine Ring Buoy Station | Keeps first-aid service and offers its owner an explicitly accepted source-water tow of at most 12 blocks to checked same-level shore. A temporary buoy carries the real swimmer; no health, air, items or ownership are granted. Native client rendering remains separately qualified. |
| `gtm:monument_plinth_bronze` | DISPLAY | Commemorative Municipal Bronze Plinth | Owner-editable plain-text notice saved across restart and rendered as a bounded text display; never runs commands. |
| `gtm:charpai_woven_cot` | BED | Hand-Strung Jute Rope Wooden Charpai | Uses one bound real bed under normal Minecraft sleep rules. Extra bunks, healing and transport are separate functions. |
| `gtm:jhula_swing_carved` | SEAT | Ceiling-Hung Carved Teak Jhula Swing | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:diwan_daybed_bolster` | BED | Low Wooden Diwan with Cylindrical Bolsters | Uses one bound real bed under normal Minecraft sleep rules. Extra bunks, healing and transport are separate functions. |
| `gtm:urli_brass_bowl` | PARTICLES | Carved Bell-Metal Water Urli Floating Petals | Owner-controlled bounded ambient water, smoke or fragrance particles; saved on/off state, no harmful or block-changing effects. |
| `gtm:pooja_mandir_shrine` | MUSIC | Wall-Mounted Teak Home Mandir with Dome | Plays a bounded Minecraft note sequence to the nearby owner; saved melody and volume settings, no item creation. |
| `gtm:baithak_low_table` | READING | Low Traditional Floor Baithak Chaurang | Use with a held written book to read, or held food to eat through normal consumption; no food or items are supplied. |
| `gtm:gaddi_floor_cushions` | SEAT | Satin-Covered Thick Floor Mattress & Pillows | One owner-controlled usable seat, with validated clearance and safe dismount; no involuntary restraints or transport. |
| `gtm:brass_samai_diya` | LIGHT | Multi-Tier Standing Temple Oil Lamp | Controls a bound real LIGHT block with saved on/off and brightness 0-15; restores its original level on removal. |
| `gtm:jali_partition_sheesham` | BARRIER | Intricate Lattice Folding Room Divider | Owner-operated folding barrier with saved open state and server-enforced closed/folded collision; closing refuses occupied space. |
| `gtm:sindoor_box_meenakari` | STORAGE | Enamelled Meenakari Brass Trinket Chest | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:hookah_ornate_pipe` | PARTICLES | Engraved Coastal Brass Hubbly-Bubbly Pipe | Owner-controlled bounded ambient water, smoke or fragrance particles; saved on/off state, no harmful or block-changing effects. |
| `gtm:dholak_musical_drum` | MUSIC | Two-Headed Mango Wood Rhythm Drum & Stand | Plays a bounded Minecraft note sequence to the nearby owner; saved melody and volume settings, no item creation. |
| `gtm:sitar_wooden_stand` | MUSIC | Carved Gourd Sitar Instrument & Display | Plays a bounded Minecraft note sequence to the nearby owner; saved melody and volume settings, no item creation. |
| `gtm:tiffin_carrier_brass` | STORAGE | 4-Tier Stacked Interlocking Lunch Box | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:attar_perfume_tray` | PARTICLES | Cut-Glass Concentrated Perfume Flacon Tray | Owner-controlled bounded ambient water, smoke or fragrance particles; saved on/off state, no harmful or block-changing effects. |
| `gtm:spice_box_masala_dabba` | STORAGE | Circular 7-Cup Stainless Spicewell with Lid | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:handloom_charkha` | LOOM | Historic Folding Wooden Cotton Spinning Wheel | Real vanilla loom consumes supplied banners, dyes and patterns; no free cloth or ingredients. |
| `gtm:traditional_safe_tijori` | STORAGE | Reinforced Brass Ironbound Antique Safe | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:terracotta_matka_pot` | SERVICE | Clay Cooling Water Vessel on Wicker Ring | Invokes the actual hydration service with its own access checks, costs and availability; never supplies a placeholder menu. |
| `gtm:doorway_toran_marigold` | DECORATION | Festive Fabric Marigold & Mango Leaf Arch | Intrinsically decorative object with owned placement, rotation, removal and a saved accent-light toggle. |
| `gtm:heavy_steel_workbench` | CRAFTING | Thick Plate Tool Die Workbench with Vise | Real vanilla crafting workbench; recipes consume the player's actual ingredients. |
| `gtm:parts_storage_racks` | STORAGE | Galvanized Heavy Pallet Warehouse Racking | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:hydraulic_auto_lift` | UTILITY | Twin-Post Electric Vehicle Inspection Hoist | Supplied owner-operated twin-post hoist raises and lowers a real empty road vehicle within authored clearance; retains the held pose and blocks driving until safely lowered. |
| `gtm:rolling_tool_cabinet` | STORAGE | 14-Drawer Ball-Bearing Mechanic Trolley | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:chemical_drum_pallet` | STORAGE | Spill Containment Pallet with 4 Barrels | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:diesel_generator_silent` | POWER | Sound-Attenuated 65kVA Backup GenSet | Consumes plain coal/charcoal as finite game energy; powers linked owned LIGHT/lever loads with eight-unit capacity, actual output and cutoff. |
| `gtm:air_compressor_tank` | UTILITY | Dual-Stage 200L High-Pressure Air Unit | One plain coal or charcoal powers actual tyre inflation; pressure follows accepted road distance and changes acceleration, braking and energy use. |
| `gtm:welding_rig_cart` | UTILITY | MIG/TIG Welder Cart with Gas Cylinders | Two iron ingots and one plain coal or charcoal weld up to 25 actual chassis health with a retained idempotent supply receipt; wreck recovery remains the station service. |
| `gtm:parts_washer_degreaser` | UTILITY | Recirculating Solvent Parts Cleaning Sink | Hold one damaged vanilla iron tool, shears or shield; supply one water bucket and iron nugget. Returns the bucket and repairs up to32 actual durability damage, preserving enchantments. |
| `gtm:industrial_drill_press` | STONECUTTER | Floor-Mount Gear-Head Column Drill | Real vanilla stonecutter processes supplied stone materials into actual recipe outputs. |
| `gtm:tire_changer_machine` | UTILITY | Pneumatic Clamping Car Tire Machine | Four leather and two iron ingots replace the game tyre set; tread follows accepted distance and changes braking and maximum speed. |
| `gtm:wheel_balancer_digital` | UTILITY | Digital Spin Dynamic Wheel Balancer | Plain coal or charcoal plus an iron nugget balances actual wheels; balance follows accepted distance and changes steering and maximum speed. |
| `gtm:overhead_crane_gantry` | CARGO | Steel I-Beam Electric Chain Hoist Trolley | Moves supplied contents from its existing real source to an empty owned container through the inspected central hoist opening. Requires a raised work surface, one loaded owned chunk and exclusive durable custody; no automatic restart or repeated output. |
| `gtm:eyewash_safety_shower` | WASH | Emergency Drench Shower & Eyewash Station | Consumes one water level from its real bound cauldron to rinse the authenticated owner, extinguishing actual fire and removing game Poison/Blindness; no revival. |
| `gtm:flammable_safety_cabinet` | STORAGE | Double-Walled Yellow Hazmat Locker | Opens a bound real single chest or barrel. Owner-only actual item storage; no invented stock or dispensing. |
| `gtm:pallet_jack_manual` | CARGO | Hydraulic 2500kg Hand Pallet Truck | Unbound mode pushes one supplied real-container load at 0.6 blocks/s with its owner on foot, inside a commissioned owned chunk. Explicit unloading moves the exact contents once; custody remains locked on interruption. Optional bound mode retains fixed real storage. |
| `gtm:dock_leveler_plate` | BRIDGE | Hydraulic Loading Bay Bridge Plate | Controls a bound existing real trapdoor loading flap; actual block supplies walkable collision and saved open state. |
| `gtm:industrial_exhaust_fan` | FAN | Wall-Mount 1.2m Louvered Extraction Fan | Owner-controlled bounded airflow pushes only its consenting nearby owner through clear authorized space. |
| `gtm:motor_oil_dispense_rack` | UTILITY | Gravity 4-Drum Bulk Oil Spigot Bar | A slime ball and honeycomb provide the fictional game lubricant recipe; oil service restores actual engine efficiency without adding vehicle fuel. |
| `gtm:transformer_station_sub` | POWER | Enclosed High-Voltage Stepdown Substation | Distributes one linked generator supply to owned LIGHT/lever loads; four-unit capacity and latched overload cutoff. |
