# Real food consumption and surveyed NPC courier delivery

This increment adds `GtmFoodCourier` to the existing thirty-food catalogue. It belongs to the functional candidate after the historical 136-test and 181-test checkpoints. Native128 artwork, food IDs, legacy orders and ordinary counter collection remain intact. The current source compiles against exact Paper `26.3.build.255-stable` under Java25. Runtime switches remain disabled in the shipped configuration until isolated commissioning and client qualification.

## Paid food, actual consumables

Every existing food ID has an explicit `food/nutrition.tsv` profile: hunger, saturation, EAT or DRINK animation, and use duration. The runtime produces the exact `gtm:food_<id>` model with actual Paper food/consumable components. Food is acquired through a reviewed finite-stock purchase and the existing durable item-delivery outbox. The user consumes the resulting ordinary inventory item; an icon or a displayed meal does not itself restore hunger.

The Ledger stores daily stock, bank debit and the food ticket in one atomic snapshot. Stock is measured in portions; a thali consumes three stock units. Refunds restore the recorded price and appropriate same-day stock only once. A previous day's cancellation cannot increase a newer day's stock. There is no copied fake inventory inside the courier.

## Food furniture serves at its actual placement

An owned vending machine, chai machine, food kiosk or other catalogue entry explicitly bound to the `food` service also functions as a physical counter. Enabling the food backend and granting the player's normal food permission is sufficient to make the first such model eligible for purchase; a separate restaurant site is not a prerequisite for buying a machine. The ordinary furniture purchase still checks the price, ownership capacity, owned property and a clear supported footprint before payment. The placed model remains subject to the same saved entitlement and placement rules as other furniture.

Food menus accept orders only when an accessible commissioned restaurant exists or the player is beside their own actual food-service placement. A machine lookup requires its current live display and interaction entity, the matching owner/model/service, the same world, an entirely loaded footprint, current ownership and property access, a clear footprint, a visible service point and distance within five blocks. Removal, suspension, obstruction or access revocation immediately prevents that fallback. Looking up the machine does not call the general city-service gate, avoiding a circular prerequisite when buying the first machine.

The machine uses the normal brand stock, reviewed bank debit, fifteen-second preparation, paid ticket and durable item outbox. A ready counter order may be collected at its restaurant or an eligible owned machine. Every payment and collection rechecks current availability; a stale menu cannot preserve access to a removed or distant machine. The machine is owner operated under the existing furniture access policy; another player's machine does not grant collection rights. It does not create unlimited or free servings. Courier orders retain their pinned route and physical rider handoff, and cannot be collected through this furniture fallback.

## Choice and physical fulfillment

The food review shows a counter option and, only when its prerequisites pass, a courier option with the actual commissioned drop-off, delivery fee and earliest estimated preparation-plus-driving time. A quote requires an authenticated permitted customer, an accessible existing restaurant counter, a nearby surveyed delivery stop, an available opted-in native scooter physically at the route origin, the correct heading, and current physical worker capacity. The native vehicle path validator checks real support, loaded chunks, world bounds, full property volume, blocks, entities, other vehicles and furniture before payment. The same checks run again before accepting the reviewed payment.

Courier payment atomically stores `Ledger.FoodDeliveryPlan` with the ticket and stock debit. The immutable plan pins order UUID, world UUID, route ID, route SHA256, destination coordinates and fee. It does not contain a guessed house coordinate or permission override. Existing counter orders have no plan and continue using their original counter workflow.

After payment, the secondary dispatch journal adopts the same order UUID. It reserves an explicitly opted-in scooter through `GtmVehicles.FleetService.COURIER`. Preparation completes before the driver starts. The shared `GtmServiceWorkers` manager supplies a nonpersistent protected Villager, sharing the physical population budget with taxis. The NPC mounts the real native vehicle driver carrier and drives through the existing bounded physics/collision/energy loop. Neither route progress nor ETA is a teleport instruction.

Arrival does not collect the ticket or create a food item. Handoff requires the paid owner, the same trip/vehicle/world/path, fleet `ARRIVED`, a real valid mounted courier, distance within three blocks, line of sight, property access, the actual paid stop and a free inventory slot. The owner may interact with the NPC or use the food order's collect button while beside it. `CourierHandoff` enforces those conditions before the Ledger atomically closes the ticket and queues the food item. The existing receipt mechanism checkpoints player inventory before acknowledging the outbox, preventing simple retry duplication.

A delivery order cannot be collected from a restaurant counter. The explicit fallback is cancellation/refund and a new reviewed counter order. Refund includes both food and delivery fee and is allowed until physical handoff. If new food service or courier dispatch is disabled, an existing authenticated owner can still open `/food` to review and refund a paid ticket. A failed active route does not block that recovery screen.

## Durable boundaries and recovery

| Boundary | Retained evidence and retry behavior |
|---|---|
| Payment committed before dispatch adoption | The Ledger plan remains. A later authenticated reconciliation adopts the same UUID without another debit. |
| Vehicle reserved before secondary assignment saves | The matching fleet lease is found by the same trip UUID; actor, vehicle and path hashes must agree before the journal adopts it. |
| NPC spawn or mount fails | The transient worker is removed. Payment and the real parked vehicle remain saved for retry or refund. |
| Owner disconnects or authentication ends | The worker is removed and native motion pauses. Re-entry uses the actual saved vehicle pose and a new authenticated connection. |
| Road/chunk/property/energy blocks movement | The native vehicle stops. The paid order remains open; ETA reports a paused condition instead of claiming arrival. |
| Restart during travel | The fleet's actual durable pose and pinned path are authoritative. Dispatch progress is observational and can move backward to that durable observation; it never repositions the vehicle forward. |
| Restart after arrival | The local stopped scooter/rider footprint is reconstructed for handoff. Old depot chunks and remaining fuel are not prerequisites for handing over already-arrived food. |
| Item handoff commits before journal closure | The authoritative ticket is COLLECTED and has one outbox receipt. Reconciliation marks the secondary dispatch delivered and releases its lease; it does not grant another item or refund. |
| Refund commits before physical cleanup | Reconciliation cancels the matching dispatch and releases the native lease. Repeating the refund cannot create another credit. |
| Ledger receipt missing or superseded unexpectedly | The dispatch pauses for ledger review. It does not invent a refund/delivery outcome from a missing receipt. |
| A closed previous order is about to be replaced | Its secondary journal settles before the Ledger's latest-food slot can be reused. |

Route, dispatch and fleet stores use checksummed snapshots and compare-and-swap publication. Corrupt snapshots or stale writers fail closed and preserve the original evidence. Dispatch history is bounded to4096 entries and prunes only terminal entries whose fleet reservation was successfully released. At most64 active dispatches can exist in the store; the runtime default is16. Physical workers default to two shared service workers, with a maximum of four. Prepared orders can wait for that shared capacity; the displayed initial estimate is explicitly an earliest estimate.

The leased scooter remains at its actual final position when released. It is not reset to the restaurant. Subsequent dispatch requires a physically available aligned scooter at that departure, or visible manual/managed repositioning. This increment does not implement an automatic depot-return optimizer, arbitrary doorstep pathfinding, customer-offline driving, or a guarantee that every city address has a commissioned route.

## Staff road commissioning

`/foodroute start <route-id> <zomatoo|swiffy>` starts beside the real commissioned food counter. Authenticated staff walk continuously along the actual loaded road. Samples are recorded every two ticks when the position advances at least0.35blocks. A skipped/teleported segment over1.5blocks, excessive step height, flight, world/session change, unloaded geometry or a fifteen-minute expired session ends the draft. `/foodroute mark` reports the current observed point count. `/foodroute finish` validates the actual aligned opted-in scooter and the entire bounded path before writing the immutable route. `/foodroute cancel` discards only the uncommitted draft; `/foodroute list` lists saved routes.

Routes hold2–2048 observed points, contiguous segments no longer than1.5blocks, and total length2–4096blocks. Surface block data is pinned with the coordinates for initial commissioning/quote validation. Initial native road preflight has a65536-probe cap; over-budget routes must be split into shorter commissioned legs. A saved route ID cannot be silently changed while paid orders reference it. No production coordinates are included in the implementation.

Permissions are `gtm.food`, `gtm.food.delivery`, `gtm.vehicles.use`, and the staff-only `gtm.food.delivery.survey`. Fleet consent also requires its existing owner/staff permission. The shipped configuration keeps `gtm.experimental-food:false` and `food-delivery.enabled:false`; courier defaults are fee500ARK cents,16 active orders and16-block drop-off offer reach. Player-specific service/property checks still apply after those switches are enabled.

## Executed verification

The final focused command was:

```sh
python /workspace/scratch/d7d343b39c16/toolchains/run-gtm-gradle.py test \
  --tests 'com.sdcraft.core.delivery.*' \
  --tests 'com.sdcraft.core.FoodConsumptionStockTest' \
  --tests 'com.sdcraft.core.FoodCourierReceiptTest' \
  --tests 'com.sdcraft.core.FoodFurnitureCounterTest' \
  --tests 'com.sdcraft.core.furniture.*'
```

Exact255 production and test compilation succeeded. **82 JUnit tests passed across nine suites, zero failures/errors/skips**: 27 courier route/dispatch/handoff/settlement tests, four cross-Ledger courier receipt tests, six consumption/finite-stock/fee tests, 38 furniture tests and seven food-machine access-boundary tests. Coverage includes different-owner/trip/vehicle/world/hash rejection, real-arrival requirements, remote/invisible/inaccessible pickup, no free inventory slot, preparation timing, corruption/stale writers, payment-before-adoption restart, arrival without food, failed outbox commit, refund idempotence and handoff-before-journal-close restart. The new machine cases reject foreign owners, unplaced or nonlive entitlements, remote/cross-world collection, a blocked sight line, lost property access, unloaded footprint chunks and mismatched models/services. This targeted count does not replace the final complete candidate build report.

A separate exact255 test companion is reproducible at `tools/probes/food_courier`. It exercises actual restaurant and owned-machine checkout, real Paper item-use ticks, all30 item components, native scooter motion, worker/rider presence, disabled-dispatch refund and physical handoff in an inspected temporary fixture in the isolated server copy. The machine scenario temporarily removes both fixed sites, buys a drink through the normal menu, waits for preparation, rejects remote and physically obstructed handoff, then collects and consumes beside the actual model. Its own README and atomic server report distinguish injected API events from native client input. It is never a production/laptop dependency. Compilation alone is not a server execution result; the latest executed probe report must be read separately.

## Remaining acceptance

Commission real restaurant/drop-off paths in the intended world, opt in real fleet owners, and perform native Java and Bedrock checks for the exact scooter, rider mount, icons, consumption animation and pickup UX. Exercise multiple customers competing for the shared worker capacity, dynamic obstructions, property revocation, disconnect/reconnect, unloaded chunks, restart after each durable boundary and a full inventory during handoff. Verify the same-state backups of Ledger, dispatch, fleet and player data during recovery. No real-client rendering, complete city delivery coverage, external food-provider integration or production activation is claimed by this source/test checkpoint.
