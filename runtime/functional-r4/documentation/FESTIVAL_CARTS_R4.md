# The nine original festival carts

The eight procession carts and Christmas gift cart now have a shared slow push function and real supplied-cargo controls. Each moves its original furniture display, interaction and authoritative placement in the single furniture store. The original ownership UUID, model ID and authored scale remain unchanged. This feature creates no vehicle, borrowed component, second furniture entitlement or accessible copy of a cargo inventory.

The actual ordinary paid Paper acceptance passed **129 of 129 checks** on the final core. All nine original carts were purchased, placed, moved in two directions, turned, parked and retained, and the gift cart carried the earlier purchased chai between its real owned barrels. The [raw report](reports/PAPER_FESTIVAL_CARTS_R4.json) and [evidence manifest](reports/FESTIVAL_CARTS_R4_EVIDENCE.json) preserve the exact run and build identities. This is server gameplay evidence; native Java/Bedrock visual qualification remains separate.

## Models and reviewed geometry

| Existing model | Authored bounds, blocks | Supplied-load placement |
| --- | --- | --- |
| `gtm:diwali_procession_cart` | X ±0.375; Y 0.0625–0.675; Z ±0.25 | Small sealed parcel behind its emblem, on the platform |
| `gtm:holi_procession_cart` | X ±0.375; Y 0.0625–0.725; Z ±0.25 | Same reviewed small platform |
| `gtm:ganesh_procession_cart` | X ±0.375; Y 0.0625–0.675; Z ±0.25 | Same reviewed small platform |
| `gtm:navratri_procession_cart` | X ±0.375; Y 0.0625–0.725; Z ±0.25 | Same reviewed small platform |
| `gtm:eid_procession_cart` | X ±0.375; Y 0.0625–0.725; Z ±0.25 | Same reviewed small platform |
| `gtm:sankranti_procession_cart` | X ±0.375; Y 0.0625–0.725; Z ±0.25 | Same reviewed small platform |
| `gtm:christmas_procession_cart` | X ±0.375; Y 0.0625–0.725; Z ±0.25 | Same reviewed small platform |
| `gtm:new_year_procession_cart` | X ±0.375; Y 0.0625–0.725; Z ±0.25 | Same reviewed small platform |
| `gtm:christmas_gift_cart` | X ±0.65625; Y 0–1.14375; Z −0.53125–0.65 | Sealed supplied parcel above the existing gift stack |

These are the actual authored small carts. They receive no blanket enlargement or replacement image. The eight procession designs have different existing emblems, and the larger gift design retains its existing parcels and handle. A small vanilla chest display identifies the actual sealed supplied load; it is a technical status projection and contains no inventory. The procession load occupies a 0.2-block cube at local X 0, Y 0.477, Z 0.125. The gift load occupies a 0.3-block cube at local X −0.25, Y 1.2958, Z 0. Every bound rotates with the original saved quarter-turn pose.

The separate [large-structure guide](FURNITURE_STRUCTURES_R4.md) covers gateways, arches and bandstands. Those structures use existing real floor; they do not create support or stairs. In the supplied depot, the original large bandstand needs a walkable floor top at **y67** because its authored body extends **3.2 blocks below that top**. A reviewed floor is **13×6 real blocks at x−127..−115, y66, z−124..−119**, with ordinary safe support and stairs and a clear 16×16 owned volume. The original depot deck at y64 alone does not meet that raised-stage prerequisite. These support requirements do not change the nine carts' original scale or their flat-floor movement rules.

The authored 0.0625 minimum Y matters: normal placement puts a procession cart's saved origin 0.0625 below the supporting floor top. Support and unloading use the actual body minimum, so they do not mistake the saved origin for the wheel contact height.

## Ordinary use

Buy an original design through the ordinary furniture shop and place it on clear, fully supported owned floor. The explicit laptop profile uses a positive local playtest price of 1 ARK per cart; production prices remain separate. Right-click **Use** to open its specific push and cargo controls, or use:

```text
/furniture festivalcart push <original furniture UUID>
/furniture festivalcart park <original furniture UUID>
/furniture festivalcart cargo <original furniture UUID>
```

The authenticated owner stays on foot, within 3.5 blocks and line of sight. W/S pushes or pulls at no more than 0.025 blocks per tick, equivalent to 0.5 blocks/second at 20 ticks/second. Release W/S and tap A/D for a single 90-degree turn. Holding a turn key does not repeat the turn. Jump brakes; sneak parks. The menu and commands are checked again against the current owner session before starting.

The complete swept body must fit loaded, dry, supported owned floor. Turns reserve the full intermediate circular sweep, including the supplied payload when present. Actual blocks, other furniture, loans, vehicles, players and entities remain obstacles. The owner is an obstacle too: stand beside the direction of travel, not in front of the moving cart. Slabs and stairs are not climbed by this flat-floor motor. Empty pushing stays inside accessible owned property; it is not a public-street procession route or a passenger transport system.

## Real supplied cargo

Use two already owned, placed storage models connected to actual single chests or barrels. The source contains the owner's real supplied items; the destination is empty. The source, destination and complete route envelope must fit one loaded owned chunk. Existing storage protections and metadata are retained.

```text
/furniture cargo commission <cart UUID> <source furniture UUID> <destination furniture UUID>
/furniture cargo start <cart UUID>
/furniture cargo continue <cart UUID>
/furniture cargo pause <cart UUID>
/furniture cargo unload <cart UUID>
/furniture cargo return <cart UUID>
/furniture cargo verify <cart UUID>
```

Commissioning records the actual endpoint identities and a bounded envelope. Pickup requires the physical cart within two blocks of its source. The custody receipt and two world locks are persisted before the real source is emptied. The existing cargo mechanism holds the supplied metadata exclusively; neither container can be opened, transferred through a hopper, broken or reassigned while that receipt is unresolved.

Push the actual original cart to within 1.6 blocks of the selected destination and unload explicitly. A durable output intent precedes one real inventory write. Completion removes the transferable payload from the retained receipt. Verification observes an interrupted output; it does not replay item creation. A return requires bringing the actual load back beside its original source. Opening the empty-push controls cannot bypass outstanding cargo custody.

The normal loaded projection exists while cargo transport is active. On pause, the transient projection stops; the durable receipt and original furniture pose remain available through the same owner controls. No transfer or movement resumes automatically after a restart.

## Persistence and cancellation

All nine IDs share the exact `FESTIVAL_CART` motion allowlist. A name suffix does not enable another asset. Motion changes the original `FurnitureStore` row through expected-pose comparison; every collision query sees that one current placement. Updates are checkpointed every five seconds and when parked or stopped. A failed save freezes movement and retains the current dirty pose for review. A failed projection attempts to restore the previous projection and withdraws an inconsistent render if necessary.

Logout, disconnection, a participant teleport, removal, unload or server shutdown parks the active session. Restart reads the saved pose but does not recreate an input session. Empty removal keeps the original paid entitlement; unresolved cargo refuses conflicting mutations. Existing `FUR1`/`FUR2` IDs and placements stay readable. The later structural revision writes `FUR3` on normal saved mutations, retaining the same original cart records and poses. For these exact formerly decorative IDs, loading clears only an obsolete decoration-active flag when needed for the new utility behavior; it does not rewrite ownership, binding, position or unrelated settings merely by opening the store.

These checkpoint semantics do not claim atomic recovery from an arbitrary process or disk failure across the world file and all cargo/account snapshots. Uncertain custody remains locked for explicit inspection.

## Verification and paid local acceptance

The combined focused source gate passed **133 tests in 13 suites**, with no failures, errors or skips. It includes seven festival cart tests, six existing typed specialist-motion tests, the fifteen shopping-cart tests and twenty-two cargo receipt tests. The new tests exercise the exact nine IDs, original entitlement/FUR2 checkpoint identity, authored wheel height, all cardinal directions, half-block-per-second limits, wrong owners and kinds, stale poses, world/height/diagonal rejection, full-circle rotations and both actual load envelopes.

The separate companion is `tools/probes/laptop_festival_carts`. It is test-only and must never be shipped in the laptop ZIP. Its **129 actual passing records** used the same normally registered non-OP account after shopping-cart completion. It purchased all nine originals through the positive-price shop/outbox, placed and moved each original display in two directions with disclosed input events, parked and removed each, and retained all nine paid entitlements. The real ordinary debit was **900 cents**, taking the observed **49128-cent** account to **48228 cents**. The run completed in **71.303 seconds**, recording **714 moving samples over 17.85 blocks** across 22 trips. The maximum observed step was 0.025 blocks per tick within floating-point precision.

Its admission guard now targets the actual final four-check [shopping-cart completion](reports/PAPER_SHOPPING_CART_R4.json), whose [separate chain evidence](reports/SHOPPING_CART_R4_EVIDENCE.json) preserves all earlier attempts. Before any new purchase, it requires the exact original paid storage, nest, returned loan, released COMMITTED cargo receipt and collected food order, unchanged 49128-cent balance, the original paid chai in the north barrel and an empty south barrel. Complete native item equality is checked against the earlier read-only paid-item fixture; that fixture is never inserted into the game. Thirteen offline admission cases passed against the actual final report, including refusal of the older planned 50-check or partial seven-check boundary.

For the supplied transfer, the companion reuses the earlier actually purchased chai in the existing northern paid barrel. It introduces no new item or fixture. The actual gift cart approaches the source, carries that portion around the real lamp, reaches the other real barrel, unloads once and retains the old receipt. The inspected route stays clear of the actual bridge steps. Setup teleports apply only to an already stopped owner after full body and line-of-sight checks. Input/menu event injection, normal logout/login and read-only snapshot reopening are explicitly disclosed.

The uninterrupted festival-cart run `20261125T023919338159Z` passed on core `b7c76cd3…`, with companion `8a25bf4f…` and the repaired structure-capable packs. The byte-exact raw report SHA-256 is `33146529aab4df9abb9447aeb2ba6687940973afc3f1c30fad418434feebf885`. Paper and the translated protocol client exited cleanly. This new run does not rewrite the earlier shopping-cart chain or its preserved failures.

The supplied transfer verified complete native item equality, one occupied destination slot, an empty source, released custody and replay refusal. No fixture blocks, inventory setup, money, items or permissions were granted. It disclosed 766 input-event injections and 28 stopped owner repositions; the actual cart positions advanced through the runtime motor. The raw report retains an older FUR2 label for its snapshot check, while the tested core uses the current compatible store decoder and writes FUR3.

This same startup loaded the display extension and registered 3576 Geyser custom items, separately from the pack’s 3575 item identifiers and 1934 display bindings. Its loopback NetherNet warning and skin API DNS errors are retained in the startup evidence. These observations do not establish a native Bedrock connection. Native Java/Bedrock rendering, human controller comfort, Windows laptop execution and arbitrary hard power-loss recovery remain separate qualification gates.
