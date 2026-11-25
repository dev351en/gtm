# Ordinary owner transport in the local profile

The bounded local profile now permits a normally authenticated, non-OP property owner to commission their own rail, cable, taxi and courier routes. The original staff commissioning path remains available under its existing permissions. This source checkpoint passed the coherent 522-test, 63-suite gate. Actual paid depot acceptance subsequently passed rail, ferry, helicopter and ropeway operations, followed by a state-preserving taxi/courier continuation; [LAPTOP_DEPOT_ACCEPTANCE_R4.md](LAPTOP_DEPOT_ACCEPTANCE_R4.md) records the precise run history and limits.

## Configuration and ownership

The fallback requires all of the following at action time: `local-playtest.profile: public_local_workshop_v1`, `furniture.allow-public-staging-placement: false`, `vehicles.local-owner-commissioning.enabled: true`, the ordinary `gtm.vehicles.owner-commission` permission, a living authenticated permitted vehicle session, and actual ownership of the entire loaded footprint inside a configured region. Entry permission, a vehicle key or an empty unowned parcel is insufficient. No staff permission, role, account, balance or asset grant is added by this source policy.

`vehicles.local-owner-commissioning.regions` accepts one to eight nonoverlapping inclusive block regions, each at most 128 × 256 × 128 blocks, with `world`, `min-x`, `min-y`, `min-z`, `max-x`, `max-y`, `max-z`. Region definitions, player/property access, world height, all world-border corners and loaded chunks are checked. A path cannot bridge two separated regions. The surveyed local depot and landing claims are configured by the fresh-profile helper, which also preserves its exact world-change journal.

| Setting | Local profile / range | Source default |
|---|---|---|
| `vehicles.max-per-owner` | 128 maximum | 8 |
| `vehicles.max-loaded` | 32 maximum | 16 |
| `vehicles.prices.<model-without-gtm-prefix>` | Positive cents, at most 100,000,000,000 | Existing category price |
| `vehicles.transport.water`, `.air`, `.rail`, `.ropeway` | Enabled only with surveyed usable geometry | Disabled |
| `vehicles.transport.max-routes` | At most 32 | 16 |
| `vehicles.transport.max-altitude` | 160 in the surveyed depot | 256 |
| `taxi.enabled` | `true` for real taxi dispatch | Existing disabled gate |
| `transport.taxi-base-cents` | Suggested local 100; valid 1–100,000 | 2,500 |
| `transport.taxi-cents-per-block` | Suggested local 1; valid 0–100 | 6 |
| `gtm.experimental-food` | `true` for the actual food catalogue | `false` |
| `food-delivery.enabled` | `true` for real scooter delivery | `false` |
| `food-delivery.fee-cents` | Suggested local 100; valid 0–100,000 | 500 |
| `food-delivery.max-active` | Valid 1–64 | 16 |
| `food-delivery.stop-reach` | Valid 3–32 blocks | 16 |
| `service.routine-concurrent-max` | Shared real NPC worker capacity, 1–4 | 2 |

The source leaves default vehicle capacity and the owner-commissioning gate unchanged. Garage and service menus now paginate actual ownership in 45-item pages, allowing all 87 vehicle types to remain reachable within the local limit. Garage previous/next are slots 47/51; service previous/next are 45/53. Each scheduled click rechecks the current authenticated session, menu, permission and service anchor. Stale pages clamp to current ownership.

## Real route commands

Replace angle-bracket arguments with real IDs shown by the garage and route commands. Vehicles are bought through the normal paid shop. These commands do not reposition a vehicle onto a route.

### Rail

1. Aim at connected real rail within eight blocks and face the desired scan direction: `/car route scan depot_rail`.
2. Buy `gtm:local_driving_cab` beside the route, where its complete body can be delivered safely. Delivery binds a matching nearby owned route; an explicit binding is `/car route bind <cab-UUID> depot_rail`.
3. Buy a passive coach into clear aligned space behind an existing tail with a driving cab, then use `/car route couple <coach-UUID> <leader-UUID>` while the vehicles are stopped, empty and nearby.
4. Enter the driving cab and use real driver input. Rail has no autonomous route-start shortcut.

The scan reads only loaded allowed rail candidates. Commissioning checks the entire guide/support corridor; binding checks the actual model body and endpoint margins. Straight guided routes use the exact oriented swept body. Curved paths retain a conservative rotation envelope.

### Cable

1. Buy two `gtm:skylink_terminal_machinery` supports at the surveyed terminal positions.
2. Commission `/car route cable depot_cable <terminal-1-UUID> <terminal-2-UUID>`. Optional already-owned grip UUIDs go between the terminal arguments in route order.
3. Buy the cabin beside a usable part of that route; delivery binds it. Explicitly use `/car route bind <cabin-UUID> depot_cable` if needed.
4. From within eight blocks of an actual terminal, use `/car route start depot_cable` or `/car route stop depot_cable`.

Support ownership, current support poses, complete cable volume, cabin margins and current operator session remain authoritative. A changed support or loss of access stops motion.

### Taxi

1. Park an owned, stopped, empty ROAD vehicle with a real passenger seat at the intended route origin, aligned with the first segment.
2. Give explicit consent: `/car fleet offer <vehicle-UUID> taxi`.
3. At the origin: `/taxiroute start depot_taxi Destination title`.
4. Walk the real road and record `/taxiroute mark` every 0.2–8 blocks.
5. At the destination: `/taxiroute finish <full-vehicle-UUID>`.
6. Return to the pickup and use the normal taxi booking/boarding flow. The paid dispatch reserves that vehicle and a real available NPC driver.

The saved vehicle must already match the first route point within 0.75 blocks and 60 degrees. Every sampled body footprint must have actual support and clear accessible geometry. The local fallback requires the surveyed vehicle, route and full swept envelope to belong to the commissioning owner.

### Food courier

The exact supported scooter category includes `gtm:scooter_activa`, `gtm:scooter_jupiter`, `gtm:scooter_access` and `gtm:scooter_ather`.

1. Park and align the owned scooter at the intended origin within six blocks of the actual `food_swiffy` counter.
2. Consent with `/car fleet offer <scooter-UUID> courier`.
3. Begin `/foodroute start depot_delivery swiffy`.
4. Walk continuously to the delivery stop. The server observes movement every two ticks; skipped or teleported segments over 1.5 blocks are refused.
5. Use `/foodroute finish` with no UUID argument. The aligned opted-in scooter at the origin is checked against the full route.
6. Order delivery near its actual destination through the food menu. Real preparation, receipt, vehicle travel and collection guards remain active.

Taxi and courier share the existing routine-worker and physical NPC population budgets. A full worker pool pauses availability; no role or population bypass is introduced. Fleet consent can be withdrawn through the existing fleet command. Pending paid service receipts retain their original retry rules.

## Service and saved state

Non-ROAD service sites remain explicitly configured through `vehicles.services.<water|air|rail|ropeway|ropeway_support>.refuel-site` and `.repair-site`, using real existing named sites. Empty defaults do not invent a facility. Working owned furniture service anchors can also invoke the existing service boundary. Service requires the registered owner within eight blocks of the actual vehicle, current station access and a stopped vehicle; aircraft must land on supported clear geometry.

Native identities and registries remain `vehicles/parked.snapshot`, `vehicles/transport.snapshot`, `vehicles/fleet.snapshot`, `taxi-routes.gtm`, `food-delivery/routes.snapshot` and `food-delivery/dispatches.snapshot`. There is no alternate ownership or vehicle inventory store.

Focused evidence: [OWNER_TRANSPORT_FOCUSED_R4.log](reports/OWNER_TRANSPORT_FOCUSED_R4.log) records 15 tests with no failures or skips; [OWNER_TRANSPORT_SOURCE_DIGEST_R4.json](reports/OWNER_TRANSPORT_SOURCE_DIGEST_R4.json) identifies the exact focused checkpoint. The parent coherent build passed all 522 tests in 63 suites with core SHA-256 `0b49d8e47935b4693f409ad51168a4a292f54b4536dc58ce717ab0bc45209d5c`. The linked depot report adds actual ordinary-account evidence. Native-client visual qualification remains separate.
