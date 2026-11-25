# Shopping cart: fixed nest, real supplied cargo

The existing `gtm:shopping_cart_nest` now lends one owner-operated cart component. The original purchased nest stays in place. Its owner can push the component over flat owned floor, carry actual supplied items between real storage containers, unload once, and return the empty cart to that same nest.

This replaces the former generic garage callback for this model. It does not add another canonical model, furniture entitlement or vehicle record. The existing furniture record remains the authority for the nest; a bounded cart-loan record is the authority for the component's current pose. Older FUR1/FUR2 furniture records remain readable. The later structural revision writes FUR3 during normal saved mutations while retaining this same nest identity and placement.

## Current verification

The bounded ordinary paid sequence is complete on actual Paper 26.3 build 255. The same normally registered, non-OP account bought the nest, two storage models and one chai; carried that real purchased item; used the real destination; and returned the same empty loan component. The final four checks passed in [PAPER_SHOPPING_CART_R4.json](reports/PAPER_SHOPPING_CART_R4.json). The account retained **49128 cents** after the original **1300-cent** debit, and the destination retained exactly one original paid item. The closed loan and released cargo receipt refused replay.

This was a sequence of retained-state continuations. Five earlier failed stages remain part of the evidence; it is not an uninterrupted 50-check pass. The [evidence manifest](reports/SHOPPING_CART_R4_EVIDENCE.json) records every exact report hash, archive, companion and core used:

| Stage | Actual records | Result and retained state |
|---|---|---|
| Original paid setup | 37 passed, 1 failed | Paid purchases, backing, placement and exclusive pickup worked. A deliberate loaded-return refusal parked motion; the observer had omitted the required resume. |
| Motion and authentication | 8 passed, 1 failed | Real movement, player-body obstruction, logout and normal login worked. The selected owner approach was blocked by the supplied lamp. |
| Destination approach | 2 passed, 1 failed | The cart reached normal unloading range. Its safe motor stopped before the bridge slab while the observer demanded a point 0.06 block farther. |
| Ordinary unload | 4 passed, 1 failed | The original item was written once. A production fingerprint defect treated native NBT compound ordering as a different item and safely retained locks for verification. |
| Corrected Verify and empty return | 4 passed, 1 failed | Ordinary Verify released that existing output. The same empty cart travelled 9.63 blocks; the observer then demanded its old borrow coordinate despite already being within the normal return radius. |
| Physical return completion | **4 passed, 0 failed** | Ordinary Return closed the original loan at its physically reached pose. Native item equality, destination access, closed snapshots, replay refusal and unchanged paid balance passed. |

Across these stages, the observer recorded **631 distinct movement samples totalling 18.93 blocks**, with no step exceeding 0.03 block apart from floating-point rounding. The final completion moved no cart, repeated no Verify or unload, and made no new purchase. A separate preflight refusal caused by the original report's missing later-added `scenario` field was corrected only for that exact archived hash; it did not run another gameplay scenario.

The initial four stages used core `b19aeb13…`; corrected Verify and return travel used `fd4ec8b7…`; the final four checks used `b7c76cd3…`. Full hashes are in the evidence manifest. The final coherent core gate passed **644 tests across 79 suites plus 155 domain checks**. The cart's original motion/store gate passed **15/15** within its **69-test, nine-suite** specialist gate, and its pack/technical-derivative fixtures passed **18/18**. These checks establish the described server behavior and resource bindings. Native Java/Bedrock rendered appearance, Windows execution and hard-power-loss recovery remain separate, unclaimed qualifications.

## Use in the laptop depot

Buy the Local Waterfront Depot through the ordinary property interface before placing the nest. In the explicit local profile, the cart nest and most other furniture cost 1 ARK each. The original workshop storage and wheelchair prices remain unchanged for continuity of the earlier paid acceptance. These prices are local playtest settings; the normal production defaults are not changed.

The reviewed cargo deck is the 16 × 16 chunk at X −144 through −129 and Z −128 through −113, with standing floor Y64. It includes two empty real barrels at **(−142,64,−125)** and **(−142,64,−115)**. Connect each barrel to a separately owned storage design through the normal furniture controls. The small `gtm:clothes_valet` storage model can stand beside each barrel without occupying the cart lane.

An example arrangement used by the acceptance companion is:

| Object | Placement or backing | Purpose |
|---|---|---|
| Fixed cart nest | Centre (−140.5,64,−126.5), turn 0 | The original purchased entitlement and physical return point |
| Source barrel | Block (−142,64,−125) | Real supplied contents |
| Source storage model | Centre (−143.5,64,−124.5) | Ordinary protected access to the source barrel |
| Destination barrel | Block (−142,64,−115) | Empty real output inventory |
| Destination storage model | Centre (−143.5,64,−114.5) | Ordinary protected access to the destination barrel |
| Initial borrowed cart | Approximately (−140.5,64,−124.492) | Clear space beside the source and fixed nest |
| Delivery position | Approximately (−140.5,64,−114.6) | Within reach of the actual destination barrel, before the real bridge slab |

The normal placement interface selects block-centred floor positions and uses the player's cardinal facing. If the nest is placed facing north, use its ordinary Rotate control twice before borrowing. The component is then pushed south toward the destination. Stand on a clear side with line of sight when passing the real lamp near Z−118, and stop before the bridge slab beginning at Z−114. The destination is already within normal unloading reach there. The existing city, public bridge, paid depot and both original barrels come from the exact guarded local-profile patch described in [LOCAL_PLAYTEST_PROFILE.md](LOCAL_PLAYTEST_PROFILE.md); the cart companion adds no world blocks.

### Borrow and push

Use the nest to open **Shopping cart | Borrow / return**. Choose **Borrow the cart**, approach the visible component, then choose **Push the empty cart**. Only one loan can be active for an owner, and only one component can belong to a nest at a time.

The equivalent normal commands are:

```text
/furniture cart borrow <nest UUID>
/furniture cart push <nest UUID>
/furniture cart cargo <nest UUID>
/furniture cart park <nest UUID>
/furniture cart return <nest UUID>
```

Stay on foot, within 3.5 blocks and with line of sight to the current cart. W and S move it along its current cardinal direction at a maximum **0.03 blocks per server tick**, or 0.6 blocks per second at 20 ticks per second. Release forward/back input before tapping A or D for a 90-degree turn. A held turn key does not repeatedly spin the cart. Jump brakes; sneak parks. A five-minute control session also parks and requires a fresh explicit start.

The cart remains on the same flat floor and inside the nest's 16 × 16 chunk. Its whole body, supported footprint, payload and full rotational sweep must fit. Missing floor, water, hazards, blocks, people, other furniture, vehicles, a property boundary or a cargo-envelope boundary stop movement. This is a real local cart, with an explicit bounded area; it does not provide automatic city shopping journeys, stairs or arbitrary cross-chunk transport.

### Carry actual supplied purchases

Put your own items in the real source container and leave the real destination empty. Food purchased through an ordinary counter is one useful load. Open **Load / carry / unload supplied purchases**, select both actual connected containers, and commission their route. All three original furniture identities, both real blocks and the entire cargo envelope must remain in the same loaded owned chunk.

The normal command sequence is:

```text
/furniture cargo commission <nest UUID> <source furniture UUID> <destination furniture UUID>
/furniture cargo start <nest UUID>
/furniture cargo continue <nest UUID>
/furniture cargo unload <nest UUID>
```

Pickup records exclusive custody before emptying the source. Both endpoint inventories then remain locked, including against ordinary opening, inventory transfers, pistons and block removal. The moving display is a sealed visual load; it is not another accessible inventory. The real supplied items are retained in the existing bounded cargo receipt with their exact metadata.

Push to within 1.6 blocks of the destination and choose **Unload**. The real destination is filled once through the existing intent/observation/release flow. Repeating an unload cannot replay the payload. An occupied or changed destination refuses output and retains custody for explicit recovery. Verification compares the complete typed item data while allowing native serialization to reorder compound keys; it preserves the original receipt and supplied bytes. If an already-written output remains awaiting confirmation, use the ordinary **Verify** control. Verify observes the existing destination; it does not perform another unload. To carry an active load back, physically return to the source and use:

```text
/furniture cargo return <nest UUID>
```

That command returns the supplied contents to their source. `/furniture cart return` returns the empty borrowed cart to the fixed nest; it cannot resolve or discard an active load.

## Parking, authentication and saved state

Normal logout, death/downed state, an owner teleport, loss of current permissions or property access, a missing projection, an expired session, or a failed movement check stops pushing. The current loan and cargo receipt are retained. A normally authenticated owner must explicitly continue; reconnecting never starts movement or output by itself.

The component's current pose is authoritative in memory for every movement and collision query. It is checkpointed every five seconds and when parked, instead of writing a file on every tick. Compare-and-set checks reject a callback using an older loan or pose. A failed checkpoint keeps the current pose and dirty state and freezes movement for a later successful checkpoint; it does not invent a replacement component.

The fixed nest cannot be removed, rotated or rebound while a loan is active. The component can only be returned when it is unloaded, its owner is beside it, and it is physically within 2.75 blocks of the exact original nest. Returned operation records remain closed. The loan store retains up to 512 historical operations and stops new borrowing at capacity rather than deleting its replay records. At most 32 loans can be active globally, with at most one per owner.

A saved pose is not published as an invisible obstacle after its owner loses access. A visible parked component and its collision volume are reconstructed only after the original nest, normally authenticated owner, supported dry floor, full current body/payload permissions and existing furniture/vehicle obstacles pass again. The durable loan and exclusive cargo locks survive a refused reconstruction. A parked loaded cart uses a small sealed-load visual; when the cargo module is actively moving its own load display, the duplicate parked display is removed.

These stores do not claim an atomic transaction across Minecraft world saves, player saves and all sidecars after a hard power loss. The existing cargo recovery rules continue to refuse uncertain output writes and retain locks. Read-only snapshot reopen tests and a normal server stop are separate from destructive crash qualification.

## Exact native128 artwork relationship

The existing canonical design is titled **Row of 10 Interlocked Wire Supermarket Carts**, but its actual source is one elongated 22-cube, four-wheel frame. It does not contain ten independently authored cart meshes. Moving that entire row as a single shopping cart would misrepresent the artwork.

The technical selector **`gtm:fm_shopping_cart_short`** therefore reuses the same native128 atlas and icon bytes while shortening the existing geometry into one loan component:

- All 22 original cube/material parts are retained.
- Each of the four wheel/post groups moves 12.8 model units toward the centre along Z.
- The two long frame cubes shorten by 25.6 model units along Z, retaining their original UV mappings.
- Both platforms use the same resulting geometry at unit scale with ItemDisplay transform `NONE`.
- Physical local bounds are X ±0.3621875, Y 0–0.825 and Z ±0.544 blocks. The sealed basket envelope is X ±0.28, Y 0.30–0.78 and Z ±0.32.

The exact original source hashes are guarded by the technical overlay builder. The original nest files, source ID, native128 painted pixels, paid entitlement and canonical design count are unchanged. The final Java/Bedrock resource graph and display bridge mapping contain the technical selector explicitly. Matching mesh extents and valid bindings establish static compatibility; native rendered appearance remains a separate client gate.

## Ordinary-account acceptance companion

`tools/probes/laptop_cart` is a separate test-only plugin and is never included in the laptop deliverable. It accepts only the exact authorized `integration-probe-r4/laptop-profile-validation` path and the single normally registered, non-OP `GtmLaptopQA` actor. The prior paid depot, workshop, vehicle, taxi/courier and launcher-reconnect state is preserved.

The original 50-record plan bought the nest and two storage models through the normal shop/outbox, bound and placed them through ordinary controls, paid for a chai, waited for preparation, collected its real item, and carried that supplied portion to the actual destination. The completed sequential evidence above observes the current cart pose and moving payload over real Paper ticks, collision with the actor's actual body, ordinary logout/login, paused-load reconstruction, exact once-only output, physical empty return and retained replay records. The canonical final report contains four completion records; the five earlier reports supply the preserved preceding observations and failures.

The companion discloses menu/block/input event injection, stopped-only setup teleports, and one remove-before-insert move of an actually purchased food portion from player inventory into the opened real source barrel. It never invokes an item factory, grants an entitlement, changes a balance, edits ownership, attaches permissions or bypasses authentication. The source and destination are genuine supplied profile blocks, so there is no world fixture to erase. A failed run retains all paid progress and unresolved custody for a narrow continuation instead of resetting the account.
