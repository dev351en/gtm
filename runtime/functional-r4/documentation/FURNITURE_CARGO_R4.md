# Supplied cargo transport — Revision 4 candidate

## What the owned cargo controllers do

`gtm:overhead_crane_gantry` moves supplied contents from its existing real backing container to another empty, owned container through a checked hoist path. `gtm:pallet_jack_manual` can be placed without a backing, pick up supplied contents from a separate owned container, carry that load with the original jack's authoritative moving pose, and unload into the commissioned destination. Its existing bound mode remains ordinary fixed real storage.

The same exclusive custody mechanism also serves the single borrowed shopping-cart component and nine original festival carts described below. Their movement providers differ; their real source/destination inventories, receipts and once-only output rules remain shared.

The original model IDs, entitlement UUIDs and owned placements are retained. The current furniture reader accepts FUR1/FUR2 records and writes FUR3 on a successful durable mutation; cargo keeps its separate custody journal. The moving chest display represents sealed custody; it is not an accessible container or a pickup item. Exactly one real source is emptied before movement begins. Exactly one checked destination receives the exact supplied slot contents after arrival. Item names, quantities, durability, enchantments and metadata travel with the supplied payload.

These are bounded native game mechanics. They are not general industrial crane physics, arbitrary-world logistics, a new storage entitlement, or a certification of the machine's real-world load rating. The authored 128×128 art remains unchanged. Real Java/Bedrock visual fit and controls require separate client qualification.

## Controls and commissioning

Use the placed machine to open **Cargo | Real supplied contents**. Select the source and destination by right-clicking the actual existing backing containers; the crane already uses its own backing as the source. **Commission the selected route** checks the current loaded geometry, property, exact container identities and bounded envelope. **Lift supplied contents** begins the explicitly supplied transfer. A source must contain items and the destination must be empty.

The command equivalents are:

```text
/furniture cargo commission <controller UUID> <source furniture UUID> <destination furniture UUID>
/furniture cargo start <controller UUID>
/furniture cargo continue <controller UUID>
/furniture cargo unload <controller UUID>
/furniture cargo return <controller UUID>
/furniture cargo verify <controller UUID>
/furniture cargo pause <controller UUID>
```

For a crane, the source UUID is the controller's own UUID. A movable jack uses two other existing owned furniture entitlements whose current backing blocks are single chests or barrels. No source or destination inventory is created by commissioning.

Both endpoints and the complete movement envelope must fit **one already loaded chunk**, within an owned volume no larger than **16 × 8 × 16 blocks**. All placements, live projections, block structure, ownership, property access and current sessions are checked again before use. Selecting a container requires visibility and five-block reach. Starting and continuing require the current visible controller within five blocks; the on-foot jack driver additionally stays within 3.5 blocks.

### Crane setup

The existing authored frame measures approximately **3.33 × 0.8762 × 0.528 blocks**. Its two cross-braces leave a central opening approximately **0.58 blocks wide**. The runtime uses all five authored frame cubes for payload collision instead of treating the entire catalogue box as empty space.

Place the crane on a raised, fully supported work strip. The tops of its source and destination containers must be level with the crane's feet. Their centers lie on opposite front/back sides of the central opening, 0.75–2.5 blocks from its center, with the centerline aligned. The source remains the crane's existing owned backing. The destination belongs to another placed, owned storage model; that model's own footprint must also remain out of the path.

The small sealed payload is **0.24 blocks wide**. It rises from 0.18 to 0.55 blocks above the work surface, moves through the central opening below the beam, and lowers above the destination. Each server step is at most **0.035 blocks**, approximately **0.7 blocks/second** at 20 TPS. The entire segment between steps is checked for blocks, other furniture, vehicles, entities, ownership, world border and loaded geometry. A new obstacle stops the hoist with custody retained.

### Pallet-jack controls

Place the jack unbound on flat supported floor, within two blocks of the selected source. The owner pushes on foot with **W/S**, releases forward/back input and taps **A/D** for a cardinal turn, and uses **jump** to brake. Movement is limited to **0.03 blocks/tick**, approximately **0.6 blocks/second**. Every turn includes the whole circular sweep of the jack and its supplied payload; another player, vehicle, floor gap or inaccessible block stops movement.

The original furniture record supplies the authoritative current pose. A successful projection precedes the expected-pose compare-and-swap update, and parking or periodic checkpoints save that same pose. Cargo adds neither a second vehicle identity nor a second inventory.

Push beside the commissioned destination, within **1.6 blocks**, then choose **Unload at destination**. Unloading requires visibility, current owner access and an unchanged empty target. A paused jack can be pushed back to its source and explicitly returned there. There is no remote unload or automatic output merely because a destination is nearby.

Existing bound jacks stay stationary. Their control opens the actual connected inventory. Remove the placement and disconnect that backing before using unbound transport; disconnecting does not move or erase its real stored contents.

### Borrowed shopping-cart component

The same custody protocol accepts `gtm:shopping_cart_nest` as an explicit controller kind. Its original owned placement remains fixed. The owner borrows one movable component from that nest, then uses **Load / carry / unload supplied purchases** at the current cart. Two separately owned real container backings remain the source and destination; the fixed nest is never itself an inventory endpoint. The commissioned envelope contains the unchanged nest, the current loan body and both endpoints inside the same owned loaded chunk.

Pickup, loaded movement, arrival and output use the loan's actual current pose and basket bounds. They never substitute a fabricated furniture placement for the fixed nest. Movement belongs to the cart helper; cargo supplies its current receipt, allowed envelope and one visible sealed load. The original nest and every other cart remain obstacles. The owner must stay on foot within 3.5 blocks while pushing, and ordinary explicit unload still requires the current endpoint, visibility, reach and exact contents. Empty pushing cannot move a sealed load around the custody checks, and return is refused while any receipt remains unresolved.

This extension adds no transferable furniture or vehicle entitlement and no second accessible inventory. The combined focused gate passed **69 tests**, including 15 cart cases, 21 cargo custody cases, five cargo geometry cases, four marker cases and 24 workshop cases. The two added cargo tests prove distinct controller/endpoints, the same exclusive once-only output protocol and reopening earlier crane/jack records. The later [ordinary paid cart sequence](reports/SHOPPING_CART_R4_EVIDENCE.json) completed lending, real movement, exact supplied output verification and empty Return on the same paid identities. Its five earlier failed stages remain retained, as detailed in the native paid-food correction section below; the separate crane/jack report is not substituted for that evidence.

### Original festival carts

The eight `diwali`, `holi`, `ganesh`, `navratri`, `eid`, `sankranti`, `christmas` and `new_year` `_procession_cart` models and `gtm:christmas_gift_cart` use their original owned furniture pose. They have no loan component and create no additional entitlement. Their visible menu offers empty **Push**, **Park** and real supplied **Cargo** controls; the command form is `/furniture festivalcart push|park|cargo <UUID>`.

The on-foot owner pushes at at most **0.025 blocks per tick**, approximately **0.5 blocks/second**, with the existing supported-ground, current-session, full swept-body, turn, property and obstacle checks. A loaded cart can move only through its existing custody continuation, within the one-chunk commissioned envelope. Its real payload position follows the exact authored cart body; a title or decorative box does not supply items. [The festival-cart guide](FESTIVAL_CARTS_R4.md) records the exact controls and source tests.

The separate [ordinary paid nine-model report](reports/PAPER_FESTIVAL_CARTS_R4.json) completed **129 passing records** on core `b7c76cd3a664e1bb7e1e56fd2098f7ef0a71e921d47170ed10c4e658974715af`. The same normal account paid 900 cents for nine distinct original carts, then produced 714 moving samples over 22 trips and 17.85 blocks; the maximum observed step was 0.025 blocks. Every model completed actual movement and turns. The gift cart additionally transported the earlier purchased chai through the shared custody path, with one unload, independent full native item equality, empty source, exactly one destination stack, released receipt and replay refusal. This loaded transfer was observed on the gift cart; the other eight use the same source-reviewed cargo implementation. No items, money, permissions or fixture blocks were granted. Injected control events and stopped owner repositioning are explicitly recorded, so this evidence does not certify native client rendering. [The component evidence](reports/FESTIVAL_CARTS_R4_EVIDENCE.json) pins the core, pack, companion and raw-report hashes.

## Custody, conservation and restart behavior

`FurnitureCargoStore` records one exact supplied payload, its original serialized slot fingerprint, the current owner/controller/endpoint identities, commissioned envelope, phase and release status. It stores **27 real slots**, at most **32 KiB per slot** and **512 KiB per load**, in a checksummed 8 MiB compare-and-swap snapshot. There are at most **eight unresolved loads**, **512 saved routes**, and **256 retained receipt records**. Released receipts discard their serialized item bytes; bounded receipt history does not become another storage service.

Native Paper item serialization can reorder compound fields after a real inventory write. Endpoint verification first accepts exact original bytes; if they differ, `CargoItemIdentity` compares the **complete typed NBT** with compound keys sorted. It preserves `DataVersion`, every known or unknown component, amount, tag type, exact floating-point bits, array/list order, strings and all 27 slot positions. Only gzip representation and compound-key ordering are ignored. No receipt or payload bytes are rewritten to normalize them. Metadata is validated before pickup; compressed, expanded, nesting and node limits fail before source debit. A verification pair may expand at most 8 MiB, each item at most 1 MiB, with a maximum depth of 64 and 32768 nodes.

| Phase | World condition and permitted next action |
|---|---|
| `PREPARED` | The durable receipt and exclusive controller/endpoint locks exist before the source debit. If the original source is still exact and the destination empty, explicit verification can abort without writing items. If both are empty and both exact world lock markers remain, explicit continuation can acknowledge pickup. |
| `IN_TRANSIT` | Both actual inventories are empty and locked. The original supplied bytes remain inaccessible custody data. The current owner may explicitly continue physical movement or request one checked output after arrival. |
| `PLACING` | Destination intent was committed before one real destination write. A restart or error may only inspect existing contents; this phase never repeats the output write. |
| `RETURNING` | Source-return intent was committed before one real source write. Recovery only observes that existing write; it never repeats it. |
| `COMMITTED`, `RETURNED`, `ABORTED` | Exact endpoint fingerprints have been observed. Owned matching world lock markers are cleared, then the receipt releases its locks and discards payload bytes. An interrupted release can be verified without producing items. |

Prepared locks are authoritative even before the world markers are written. The two actual block entities also carry a receipt and role marker. Unexpected item content, a different owner or binding, changed block structure, missing in-transit marker, conflicting marker, unloaded geometry, revoked permission or stale snapshot causes refusal while retaining unresolved custody.

The normal inventory-open, click, drag, hopper, pickup, block-break, explosion and piston paths cannot access reserved endpoints. Furniture removal, placement, rotation, rebinding, unbinding and connection repair cannot move or erase a reserved controller or endpoint. Unknown surviving cargo markers are treated as locked, not as permission to claim items.

Logout, auth loss, withdrawal, timeout, chunk loss or plugin close stops only the transient motion/display. The unresolved supplied load remains locked. **Nothing automatically resumes or outputs on restart.** The owner must return, authenticate, satisfy the current property and endpoint checks, and explicitly continue or verify. A receipt alone never grants ownership or access.

An ambiguous output fingerprint is deliberately not repaired by filling missing slots. It remains locked for review. This prevents a second output when an interrupted first write may already have been observed elsewhere.

### Persistence boundary

The sidecar receipt is atomically replaced as one checksummed aggregate. Minecraft chunk data and player inventories have their normal separate save boundaries. Requiring both endpoints in the same chunk reduces split endpoint saves, but **does not prove an atomic durable transaction across chunk saves, the cargo sidecar, player saves or third-party direct inventory mutation**. There is no claimed world-save fsync acknowledgment or automatic hard-kill recovery. Keep a stopped-copy backup for upgrade and crash qualification. Direct inventory mutations by another plugin bypassing standard Paper events are not treated as authorized cargo writes.

## Source and verification

| File | Responsibility |
|---|---|
| `source/src/main/java/com/sdcraft/core/GtmFurnitureCargo.java` | Current owner/session/world checks, menu and route selection, real inventory debit/output, world lock markers, physical hoist and jack payload projections, recovery and lifecycle |
| `source/src/main/java/com/sdcraft/core/furniture/FurnitureCargoStore.java` | Bounded exact payload custody, exclusive reservations, phase transitions, fingerprints and durable release |
| `source/src/main/java/com/sdcraft/core/furniture/CargoItemIdentity.java` | Full typed native item identity across gzip/compound ordering changes; original durable hash and once-only output semantics remain unchanged |
| `source/src/main/java/com/sdcraft/core/furniture/FurnitureCargoGeometry.java` | The five authored frame cubes, central-opening path and bounded swept hoist steps |
| `source/src/main/java/com/sdcraft/core/GtmFurnitureRescueMobility.java` | Shared typed on-foot pallet/festival-cart motion, input, supported ground, full turns, projection rollback and pose checkpoints |
| `source/src/main/java/com/sdcraft/core/GtmFurnitureShoppingCart.java` | Fixed-nest loan component pose, supported owner-controlled pushing and cargo projection callbacks |
| `source/src/main/java/com/sdcraft/core/GtmFurniture.java` | Exact optional binding compatibility, current live access adapter and reserved furniture/inventory gates |
| `tools/probes/furniture_cargo/` | Separate disposable actual-Paper companion; never distributed as gameplay |

The focused Java 25 build passed **52 cases** with no failures, errors or skips: 19 cargo custody tests, five authored-frame/motion tests, eight optional storage compatibility tests, nine existing wheelchair store tests, five traffic rules tests and six fictional alcohol state tests. The cargo tests cover exact supplied bytes, defensive copies, source/destination mismatch, ownership, same-chunk envelopes, exclusive locks, output intent ordering, replay refusal, interrupted output, retained locks, explicit return, corrupt snapshots, stale writers and bounded history. Four additional PDC boundary tests cover wrong-typed, orphaned, mismatched and absent world markers. The coherent **504-case** gate included all four. Its initial core was `faf17a716255864d9c74a666845d90b595b62b5ac92166336812e4ce099de281`; the first successful actual run after the shared redstone correction remains a separate historical baseline. The current coherent core includes the complete typed-item correction and passed **644 JUnit tests in 79 suites plus 155 domain assertions**.

### Completed actual server effects

The [named actual-Paper report](reports/PAPER_FURNITURE_CARGO_R4.json) passed **all 25 scenario records and cleanup: 26/26**, with no unexecuted steps and `fixture_remains=false`. The latest regression ran on Paper 26.3 build 255, Java 25.0.5.1, in controlled cohort `20261125T024626783921Z`; [exact final shared regression provenance](reports/FINAL_SHARED_RUNTIME_REGRESSIONS_R4.json) records the input hashes and each scenario's outcome independently. Real metadata conservation, hoist obstruction, current access refusal, pushed jack movement, destination arrival, protected containers, once-only output and the original bound-storage mode all passed. Earlier passing reports remain as [core504](reports/PAPER_FURNITURE_CARGO_BASELINE_504_R4.json) and [core591](reports/PAPER_FURNITURE_CARGO_BASELINE_B19_R4.json) baselines.

| Evidence | Value |
|---|---|
| Actual tested core SHA256 | `b7c76cd3a664e1bb7e1e56fd2098f7ef0a71e921d47170ed10c4e658974715af` |
| Separate companion SHA256 | `2e3986208dcfab3c5f6437c7b9b5300fcc8ecb4b2c0d4022e87e1ad3d5dd0b83` |
| Named report SHA256 | `f66420aad6945eb5cf74a3f7625e83ee8842fc351890304f9e02a7f9ecd3585b` |
| Observed crane travel | 2.685 blocks across 78 moving samples; maximum step approximately 0.035 blocks |
| Observed original jack travel | 9.99 blocks across 333 moving samples out of 421 samples; maximum step approximately 0.03 blocks |
| Disclosed fixture input | 430 injected Paper input events; six owner repositions, each after both production motion sessions stopped and followed by explicit continuation |
| Cleanup | Original actor state and journaled blocks restored; all supplied cargo receipts resolved; no currency grant |

The supplied test payload contained a counted named/PDC-tagged stack, a damaged enchanted tool and a separate paper stack. The actual destination inventory retained their complete metadata. Permission restoration alone did not resume transport; destination arrival alone did not output contents. The same jack entitlement subsequently opened its real bound barrel and refused transport in that fixed mode.

The report qualifies these bounded actual server effects. It discloses input-event injection, stopped-only fixture repositioning and read-only snapshot reopen. The final run was explicitly Java-only, with the two optional crossplay plugins preserved outside plugin discovery and normal authentication unchanged. It does not qualify Bedrock connectivity. Native Java/Bedrock rendering, human driving input and full JVM crash persistence remain separate qualifications. Five unplaced stable QA entitlements and bounded released receipt metadata remain only in the disposable copy; unresolved or unexpected contents were never erased to obtain a pass.

The first actual cohort `20261125T004418185096Z` passed 14 scenario steps, including two completed crane loads and exclusive jack pickup, then failed the jack movement assertion. Its observer teleported the active owner; the production participant-teleport guard correctly canceled motion. Cleanup retained the unresolved cargo as `FAIL_CLEANUP`. The corrected companion pauses both actual sessions before each owner reposition and explicitly resumes afterward. The failed clone is retained; the successful rerun used a fresh controlled backup, without modifying receipts or relaxing the gameplay guard.

### Native paid-food metadata correction

The later ordinary shopping-cart run exposed a real item-serialization issue beyond that plain-payload regression. Its paid chai reached the destination once, but `ItemStack.deserializeBytes(...).serializeAsBytes()` reordered the `minecraft:food` and `minecraft:item_model` compound entries. Raw fingerprint comparison therefore retained the receipt in `PLACING` with both endpoints locked. The source was empty, and the destination held exactly one paid drink; no second output was attempted.

[The read-only Paper diagnosis](reports/PAPER_SHOPPING_CART_CUSTODY_DIAGNOSIS_R4.json) found `ItemStack.equals` and `isSimilar` both true and no structured component differences. [The typed NBT comparison](reports/SHOPPING_CART_CUSTODY_NBT_DIAGNOSIS_R4.json) independently preserves all types/values/list order/count and proves the compound order difference. Regression fixtures retain the original 411-byte item and a 409-byte roundtrip with the exact hash observed on Paper. The frozen fixture provenance explicitly identifies reconstruction of that observed ordering. The subsequent actual Verify run also exported the native 409-byte roundtrip directly: SHA256 `5e0f011b6ddebf6952a20af78c7e1665dbd0643cd92a3da33ed9a839338a46b7`, exactly matching the regression fixture. That later direct export is recorded in [the completed cart evidence](reports/SHOPPING_CART_R4_EVIDENCE.json); the frozen source fixture was not rewritten.

The correction above changes only complete metadata verification. The original receipt and hash remain durable. Explicit **Verify** may observe the already written item and release the exact owned lock markers; it never calls the output writer. Changed material, count, slot, list order, `DataVersion`, numeric tag type, float bits, opaque component, malformed metadata or ambiguous partial contents still leave the load locked. Eleven focused tests cover these rules, bounded expansion and original-hash preservation across reopening a `PLACING` receipt.

Actual normal **Verify** then succeeded on core `fd4ec8b7ffd59e381693c255fdad3fd37f9010256d5d13b5814dc28af193a15b`: the same receipt became committed and released, the source remained empty, and full native `ItemStack.equals` confirmed the single original destination drink. The empty cart moved 9.63 blocks in 321 actual moving samples toward its unchanged nest. An observer then demanded the old exact borrow coordinate even though the reached pose was already inside the normal 2.75-block return radius; that failed observation is retained.

[The final four-check ordinary Return report](reports/PAPER_SHOPPING_CART_R4.json) passed on core `b7c76cd3a664e1bb7e1e56fd2098f7ef0a71e921d47170ed10c4e658974715af`, without repeating Verify, unload, purchases or motion. It confirmed the returned loan, committed released receipt with no retained payload, ordinary destination access, one full original native item, empty source and replay refusal. The original 1,300-cent paid debit and final 49,128-cent bank balance remained. [The six-stage evidence chain](reports/SHOPPING_CART_R4_EVIDENCE.json) preserves all five earlier failed stages and their own binary hashes; this is a completed bounded sequence, not a new uninterrupted 50-check claim. The cart companion granted no items, money, permissions or fixture blocks.
