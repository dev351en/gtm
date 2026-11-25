# Native transport and managed fleet — Revision 4

**Date:** 25 November 2026

**Target:** Paper 26.3 build 255, Java 25

**Evidence boundary:** Implemented source, exact-API compilation and automated domain tests. This report does not certify a Java or Bedrock client session, an installed city network, production deployment or every transport requirement in the master brief.

This increment gives all **87 existing native transport IDs** an explicit mode and a corresponding interaction path. The 65 road models use the authoritative road engine. The additional 22 models use water, flight, surveyed rail or suspended cable guidance; the two SkyLink support models operate as stationary infrastructure. Native128 artwork, existing vehicle/owner UUIDs, financial accounts and legacy plugin data remain intact. Existing MTVehicles ownership is not automatically migrated or deleted.

The earlier three-auto, 1.0.2 checkpoint remains documented in [INTERACTION_RUNTIME_R4_REPORT.md](INTERACTION_RUNTIME_R4_REPORT.md). Its JAR hash and passing build are historical evidence, not evidence for this larger increment. The final integrated report is the authority for the assembled JAR, configurations, resource packs and executed server probes.

## Coverage and actual use

| Mode | Models | Implemented use | Required environment |
|---|---:|---|---|
| `ROAD` | 65 | Real driver/passenger carriers; steering, throttle, reverse/brake; collision, fuel, damage, parking; explicit taxi/courier fleet operation | Supported clear road, loaded chunks and complete-volume property access |
| `WATER` | 8 | Helm controls, inertia/rudder response, passengers, water support, fuel and actual docking/parking | Actual loaded level source water with a second water block beneath the hull probes; safe shore/dock exit |
| `AIR` | 4 | Takeoff, descent, hover/yaw, passengers, rotor-part capability, fuel and damage | Real supported landing pad, full authored rotor clearance and altitude limit |
| `RAIL` | 6 | Driving cabs, powered intermediate cars, passive trailers, passengers and same-owner coupling | Commissioned connected vanilla rails with unchanged shape anchors and actual clearance |
| `ROPEWAY` | 2 | Hanging passenger cabins, terminal operation, endpoint dwell and boarding gates | Cable polyline commissioned from real owned terminals/grips |
| `ROPEWAY_SUPPORT` | 2 | Terminal start/stop, terminal energy, grip anchors and optional machinery animation | Terminals on inspected support; grips mounted to a previously commissioned cable |

The auto-rickshaws retain their exact IDs:

| ID | Energy | Seats and cargo |
|---|---|---|
| `gtm:rickshaw_traditional` | CNG | Driver and two rear passengers; explicit taxi fleet eligibility |
| `gtm:rickshaw_electric` | Electric | Driver and two rear passengers; explicit taxi fleet eligibility |
| `gtm:rickshaw_cargo` | CNG | Driver plus a 27-slot binding to one actual owned chest/barrel inventory |

Water profiles are `marine_ferry`, `marine_speedboat`, `marine_police_launch`, `marine_rescue`, `marine_fishing`, `marine_yacht`, `marine_cargo` and `marine_water_taxi`, all with prefix `gtm:`. Ferry/yacht expose eight passenger anchors, water taxi four, and the others two. Fishing/cargo boats have the real-container interface. These are bounded runtime capacities, not claims that every authored deck or real-world passenger capacity is implemented.

Flight profiles `heli_police`, `heli_media`, `heli_rescue` and `heli_civilian` each have one pilot and three passengers. Rail profiles are `local_driving_cab`, `local_motor`, `local_trailer`, `metro_lead`, `metro_middle` and `metro_accessible`. The two cabs have one driver and six passengers; other coaches have six passengers and no invented driver seat. Motor/intermediate cars contribute traction energy; trailer/accessible cars are passive followers. `skylink_cabin` and `skylink_accessible` have four bounded passenger anchors each. `skylink_grip` and `skylink_terminal_machinery` have no seats and are not steerable road vehicles.

## Native dimensions, seats and animation

The profile generator (source checkout: `tools/build_vehicle_runtime_profiles.py`) reads current native128 transport/road-state manifests and editable meshes. It writes `source/src/main/resources/vehicle/road-profiles.tsv` without modifying original IDs or source artwork. Bounds include the actual authored extent. The rescue helicopter retains its **11.88-block rotor width**; the local driving cab retains its **14.865-block total length**, including protruding source geometry. These dimensions must fit inspected terrain and tracks.

Java item models are normalized for inventory rendering. Profiles derive the inverse scale/translation from the source extents; `ItemDisplay` uses the `NONE` item transform and that model-specific transform. Displays render the body. Invisible marker carriers attach actual riders, while separate `Interaction` entities provide clickable body segments. Server movement/collision is independent of those tiny or nonexistent native collision boxes.

Auto, motorcycle, scooter and tractor hip anchors use actual cushions/saddles. Cars retain the manifest driver and corresponding front-passenger anchors. Large road vehicles do not advertise unverified full bus decks or rear rows. The non-road meshes lack usable humanoid seat bones for every position; their bounded runtime anchors explicitly say that client fit remains unqualified. The carrier offset of 0.6 blocks below a hip is a calibration requiring real client checks.

The generator partitions existing meshes into **1,263 Java/Bedrock animation-part pairs** covering 272 existing model-state exports. They are derivatives, not additional original designs. Wheels use authored axle pivots; helicopter main/tail rotors use distinct axes; grip wheels and terminal bullwheels have separate pivots. Native128 atlas UVs and original complete models are retained. The derivative manifest (source checkout: `creative/runtime_transport/manifest.json`) records exact bindings, hashes and normalization; the partition report (source checkout: `creative/runtime_transport/validation.json`) compares every original cube/element with its part union.

`python tools/build_vehicle_runtime_profiles.py --check` verifies the generated files without writing. Articulation defaults to disabled and has a complete-model fallback. Java `ItemDisplay` support and a Bedrock geometry export alone do not qualify Geyser display translation, model scale or equivalent animation; the parent compatibility path must be qualified before enabling it. Front-wheel steering joints and opening door meshes are not claimed by the spin animation.

## Controls and passenger protection

The `/car` garage and phone integration lead to the actual vehicle shop and service menus. Normal purchases use existing Ledger intents; this module does not charge independently or create a second wallet. `/car spawn` requires authenticated `sdcraft.admin` and is a test grant only.

| Input | Road/water | Helicopter | Rail/SkyLink |
|---|---|---|---|
| W / S | Throttle, oppose motion, reverse | Horizontal forward/reverse | Rail cab throttle/reverse; SkyLink uses terminal operation |
| A / D | Steering during travel | Yaw, including hover | Commissioned guidance controls the path |
| Jump | Brake | Climb while flight controls are active | Rail brake |
| Sprint | No road boost is claimed | Descend while flight controls are active | No additional action |
| Sneak | Safe exit request | Safe exit request, not a second descent key | Safe exit request |
| F / swap hands | Actual driver horn | Actual pilot horn | Cab driver horn |

`/car hover` holds flight movement while still consuming hover energy. Inventory menus suspend input. `/car lights`, `left`, `right`, `hazards`, `horn`, `doors`, `siren`, `rescue`, `cargo`, `dock` and `controls` expose corresponding functions. Door controls currently gate boarding rather than animate opening panels. Passengers cannot operate driving controls.

`/car lock`, `/car key <vehicle> <authenticated-player> <give|revoke>` and `/car park` retain durable owner/key rules. Unlocking passengers does not grant driving keys. Item lore, cosmetic possession and names never grant ownership. A managed fleet reservation also prevents a human driver taking over its paid service.

Each real player rider captures an authentication nonce. Admission, parked occupancy and every movement step recheck authentication, life state, `gtm.vehicles.use`, keys/invitations and complete occupied-volume property permission. Logout, permission revocation, session replacement, death or external teleport ends that use. Passengers cannot inherit a driver's property permission. Entry requires a stopped vehicle and actual line of sight; failed/exceptional mounts roll back admission state.

Safe exits check real support/headroom, living entities, other bodies and furniture. With no safe position, voluntary exit is refused. A canceled exit teleport stops the vehicle and attempts to restore the same valid rider; forced logout/death/external teleport cleanup still detaches without overriding a legitimate destination.

## Mode physics and collision

Road simulation uses fixed 0.05-second steps, bounded acceleration, braking, drag, speed and wheelbase steering. It does not pivot a parked vehicle. Consumption follows accepted distance plus the profile's running load/idle term. A separate stationary ignition/idle model is not claimed. Exhausted/failed engines cannot propel, and low condition reduces performance.

Water uses separate inertia and steering. Jump provides no vertical thrust. The adapter probes actual level source water with sufficient depth and applies a 0.45-block draft; it refuses land, shallow/uneven surfaces, solids and unloaded boundaries. `/car dock` saves the stopped actual position after safe exit; it never teleports to a presumed marina.

Flight has bounded motion, 2.5-block/second powered climb/descent, yaw and a hover/load cost. Accepted three-dimensional travel consumes energy. With no power the craft loses horizontal/yaw propulsion and descends at a bounded game rate, subject to collision/landing checks. Full rotor clearance is required. Real skid-support probes reject hazardous or obstructed landing terrain. These are fictional game mechanics, not an aerodynamic simulation.

Rails use all ten real vanilla `Rail.Shape` values, including grades and quarter curves. Staff survey connected loaded rails; ambiguous connections, waterlogged guidance and changed shape anchors are rejected. Powered rails are not required. Consists require the same owner/world/route and already aligned actual positions. A coach without a driving seat is delivered only into a clear authored gap behind the tail of an owned consist that leads to an actual cab. It is not left as an isolated unsteerable vehicle. Coupling checks the signed gap and matching orientation. Cycles, branching followers and more than eight linked records are rejected. The head preflights followers; followers also check swept movement substeps. Energy loss, missing coaches, tight wheelbase curvature, changed tracks or physical conflicts stop the consist.

SkyLink cabins hang below a cable polyline derived from actual supports. First commission the route between real owned terminal machines; a grip can then be mounted at a loaded clear position on that existing cable. A new explicitly linked route may include it as an intermediate anchor. A cabin may overlap the mechanical attachment of its own linked, same-owner grip; other grips, terminals and foreign bodies remain colliders. Grips do not snap to ground under a hanging cabin. The authenticated commissioning owner starts the route from a real terminal. Cabins use inset endpoints, ten-second dwell and reversed route direction. Terminal energy is consumed by actual accepted travel. Failed, moved, missing or inaccessible support infrastructure stops operation. This does not create an entire cable network or assume terminal coordinates.

`PaperRoadCollision` checks voxel shapes, liquids/hazards, support, borders, living entities, other active native bodies and nearby furniture. Oriented tests avoid relying on a renderer footprint. A pedestrian guard blocks walking through active bodies while permitting egress from an existing intersection. Same-world teleport events check the destination person volume instead of treating the whole intervening city as a walked path; this avoids blocking hospital/service travel across a parked car. All simulation probes require loaded chunks and a shared bounded budget; no driver generates terrain, excavates a route or places a platform.

Defaults are 16 active vehicles, eight per owner and 16,384 collision checks per tick; validated maxima are 32 active and 16 per owner. The primary registry holds 512 records. Admission adds at most two nearby records per second; distant unoccupied records save and leave active simulation. Simulation order rotates to share the budget. These are cost bounds, not a measured player-capacity certification.

Telemetry uses actual accepted movement. The game convention is **one block = one metre**, so km/h is accepted blocks/second × 3.6. Road speed is horizontal; flight telemetry includes three-dimensional travel. The phone receives fuel type/percentage, condition, seats and a distance-only range estimate. A combined authenticated HUD suppresses the legacy action bar. Range excludes future idle/hover, detours and collisions and is not a fuel guarantee.

## Cargo, lights and emergency roles

Cargo-capable profiles bind one existing owned single chest or barrel. `/car cargo bind <vehicle>` records its exact address and random marker before applying the marker. `/car cargo open` opens that same vanilla inventory. No item contents are copied into a virtual hold or restored from another file.

Access requires the authenticated nearby registered owner, a stopped vehicle, current backing-container property ownership and a matching marker. Hoppers, inventory pickup, explosions, pistons, unauthorized open/click/drag and adjacent chest merging are guarded. `repair` reconciles a missing matching marker; `unbind` releases the binding without copying contents. The backing depot chunk must already be loaded in the same world. This is an actual inventory binding with that operational limit, not a claim that a vanilla chest block physically travels with the model.

Headlights create real temporary level-13 `LIGHT` blocks in a short unobstructed beam. Only air variants are replaced. A bounded write-ahead journal records original air; cleanup restores matching unwaterlogged lights and preserves different replacement blocks. Loaded-chunk recovery also starts when driving is disabled. Indicators use timed amber particles; horns are rate-limited sounds; low condition emits smoke. Operator/session checks apply. World-file and journal writes are not a power-loss transaction.

Role metadata follows existing model IDs. Siren/rescue controls require `gtm.vehicles.emergency` or administrator permission. Medical/rescue vehicles offer a stopped nearby authenticated person a seat, which they must accept within ten seconds through normal boarding/property checks. No unconsented rescue teleport occurs. Hoists, firefighting water, media broadcast, pursuit flight and a complete ambulance workflow remain separate gaps.

## Managed taxi and courier services

`ManagedRoadRoute` and `FleetStore` serve the root taxi/food adapters. A customer's meal/fare never buys a scooter implicitly or seizes an unlocked private vehicle. Its registered owner explicitly uses `/car fleet offer <vehicle> <taxi|courier|both>` with fleet/staff permission. Withdrawal refuses an outstanding reservation. Owner identity, keys and financial accounts remain unchanged.

A route has 2–2,048 immutable points in one world, contiguous segments at most 1.5 blocks, bounded height transitions, total length at most 4,096 blocks, and a SHA-256 world/geometry/order fingerprint. Initial validation checks every sampled full footprint against property, loaded chunks, support, blocks, entities, furniture and native bodies. Height must agree with real support within 0.12 blocks. One 65,536-probe budget bounds this survey; over-budget routes require shorter legs. The actual vehicle must already be within 0.75 blocks and 60 degrees of its route origin. No booking/resume reposition teleport is allowed.

Reservations are durable and exclusive before the service adapter charges its own Ledger intent. Exact trip-ID replay reconciles the same vehicle, actor, service, route and passenger set; changed identities/fingerprints fail. Paused/arrived trips retain the vehicle until explicit settlement release. A released receipt cannot restart movement.

The caller supplies a nearby valid nonpersistent NPC with no purchased-item inventory. This adapter mounts it in the real driver carrier and owns its active mount lifecycle. It uses the same `RoadPhysics`, physical substeps and fuel accounting as a human driver. A captured authenticated customer/dispatcher and nonce always supplies property authority; the NPC is not an authenticated player and no null access actor is used. Taxi movement waits until all invited passengers are actually mounted. The food Ledger outbox, not the NPC inventory, owns meal issuance.

The controller anticipates turns/braking, bounds cruise speed and measures progress from accepted motion. A persistent blocker pauses after a bounded wait. Authentication/access loss, missing driver, depleted energy, vehicle failure or an unloaded boundary stops at the actual position. Restart uses the saved pose and pinned route; an incompatible pose requires intervention. Explicit authenticated `managedBoard` by the recorded taxi actor refreshes that actor's nonce after restart/relogin. Another invitee cannot refresh it.

Release stops the NPC and saves actual pose. With no safe passenger exit, it fails while retaining the reservation for retry. Trusted settlement can release using the recorded actor UUID after disconnection without changing ownership. Released vehicles remain at the actual destination: another job can select them only when physically near its origin. Return/reposition requires a visible manual/managed trip; automatic fleet circulation is not supplied here.

Limits are 512 fleet consents, 64 outstanding reservations, 65,536 total active route points and 4,096 retained trip receipts, plus the shared NPC/vehicle physical ceilings. Receipts are not silently discarded to reuse operation IDs.

## Persistence and public API

`vehicles/parked.snapshot` retains its existing schema: stable vehicle/owner/model/world IDs, actual pose, fuel, condition, odometer, keys, lock and paid-service receipts. Ownership commits before transient entities. Sequence numbers prevent older asynchronous checkpoints replacing newer lifecycle saves. Parent Ledger debit/grant intent is committed together and acknowledged only after the module's idempotent grant succeeds.

`transport.snapshot` contains surveyed guides, consist links and cargo addresses. `fleet.snapshot` contains fleet consent, pinned reservations and trip receipts. `headlights.snapshot` contains light recovery metadata. Checksummed compare-and-swap writes preserve malformed data on rejection. Startup cross-checks transport/fleet bindings against primary vehicle identities; unsafe stores stop the feature and participate in core fail-closed initialization.

Paid refuel/repair requires a real commissioned site or registered furniture service anchor. Non-road modes require explicit facilities; a road gas station is not inferred to be a marina/helipad. The module requires the nearby owner and stopped actual speed; aircraft must be landed. Service state and its receipt commit together. Matching replay can be acknowledged after the owner leaves; the service receipt ceiling is 4,096.

Ordinary checkpoints use one background writer; critical transitions save synchronously. Managed-trip checkpoints save actual vehicle state before route progress. These files and Paper player/world data are not one transaction: abrupt termination can rewind movement or require paused-trip reconciliation. Recovery does not clone cargo, financial grants or vehicle identities.

| API group | Purpose |
|---|---|
| `setTransportOptions`, `setArticulationEnabled` | Explicit mode/capability options before start |
| `setObstacleProvider`, `setVolumeAccess`, `setCargoOwnership`, `setInstrumentHud` | Furniture geometry, full property gates, container ownership and combined instruments |
| `catalog`, `owned`, `find`, `isPurchasable` | Exact profiles and current active/parked state |
| `validateAcquisition`, `grant` | Real delivery feasibility and idempotent Ledger grant |
| `validateService`, `applyService`, `serviceApplied` | Paid owner services and exact replay |
| `telemetry`, `nearbyTelemetry`, `traceCombat`, `applyCombatDamage` | Read-only instruments/inspection and bounded body hits; combat caller selects nearer block/living/body hit |
| `useControl`, `enter`, `exit`, `park`, `onAuthenticationLost` | Controls, safe rider lifecycle and cleanup |
| `commissionFleet`, `availableFleet`, `validateManagedPath` | Explicit consent and reviewable fleet/route availability |
| `reserveManagedDrive`, `beginManagedDrive`, `managedBoard` | Durable parked reservation, real NPC driver and invited boarding |
| `managedPassenger`, `managedSnapshot`, `managedTrip` | Actual passenger state, telemetry and NPC-to-trip mapping |
| `pauseManagedDrive`, `cancelManagedDrive`, `releaseManagedDrive` | Stop/save, cancellation and exact trusted settlement release |

`ManagedSnapshot.status()` is `RESERVED`, `RUNNING`, `PAUSED`, `ARRIVED`, `CANCELLED` or `RELEASED`. Accessors are `trip`, `vehicle`, `actor`, `reason`, defensive `position`, accepted `progress`, `routeLength`, `blocksPerSecond`, `energyPercent`, `health`, `etaSeconds` and `routeHash`. This does not expose mutable state or grant payment authority.

## Configuration and API evidence

Normal source defaults keep driving, all-road admission, articulation, each non-road mode and taxi disabled pending qualification. `vehicles.transport.max-routes` is 32, matching the registry cap; altitude defaults to 160. A local staging profile must enable modes deliberately. When driving alone is enabled and `all-road-models` remains false, the three autos are the narrow selection. No paid plugin or automatic live-world modification is introduced.

Compilation targets the exact build-255 API. Local `javap` inspection established that `Player.getCurrentInput` provides directional/jump/sneak/sprint input, voxel boxes are block-local, and this exact `CraftEntity.teleport` path retains passengers using `POSITION_RIDER`. Passenger retention is the current default; the old `RETAIN_PASSENGERS` requirement is not assumed. Cross-world vehicle teleport is not used.

Primary references:

- [Paper26.3 player input](https://jd.papermc.io/paper/26.3/org/bukkit/entity/Player.html#getCurrentInput()).
- [Entity movement API](https://jd.papermc.io/paper/26.3/org/bukkit/entity/Entity.html).
- [Passenger-retention deprecation](https://jd.papermc.io/paper/26.3/io/papermc/paper/entity/TeleportFlag.EntityState.html).
- [Block voxel shapes](https://jd.papermc.io/paper/26.3/org/bukkit/block/Block.html#getCollisionShape()).

## Executed checks and qualification gates

The exact-API aggregate build's current XML records **64 vehicle-domain JUnit tests, zero failures/errors/skips**: 22 road,24 transport and18 fleet cases. They cover all87 profiles, native dimensions, explicit seat/mode roles, animated-part bindings, water/air motion and energy, rail shapes/guides, consist/cargo ownership, corrupt/failing/stale snapshots, straight and curved accepted NPC movement, route fingerprints, reservation exclusivity, restart persistence and replay/release rules. The final two regressions distinguish a cabin's own linked grip from unrelated support bodies and distinguish service-teleport destination checks from swept walking. The earlier62-case targeted gate remains a historical checkpoint; its first fleet run exposed cruise overshoot and a failure-injection setup error that were corrected before it passed.

From `source/`, use the verified Java25/Gradle toolchain for `test --tests 'com.sdcraft.core.vehicle.*' jar`; the normal aggregate gate is `check jar`. Profile and animation files additionally have generator `--check` and exact partition checks. Domain tests do not simulate Bukkit world physics, native clients or network reconnect. The parent integrated report records the final JAR and actually executed isolated Paper probes.

The separate transport companion (source checkout: `tools/probes/transport_runtime/README.md`) has compiled successfully against exact Paper255 with Java25. Its12 deterministic QA grants cover autos, cargo, real NPC fleet travel, water/air admission, rail coupling and terminal-powered cable travel in an inspected disposable fixture. It has no automatic startup scenario, contains no core implementation and must not be shipped with the laptop bundle. Its build record says `COMPILED_NOT_EXECUTED`; runtime results must come from the actual server report after the operator's controlled installation and authenticated run. Direct API calls, injected protection events and test-player setup teleports are explicitly separate from native client controls/rendering.

| Acceptance scenario | Required real observation |
|---|---|
| Autos, car, motorcycle and large commercial model | Actual seats/camera, body blocking, retained passengers, steering/brake/reverse, fuel and saved pose |
| Every watercraft on inspected water | No road snapping, hull support, occupied collision, real docking/safe exit and mode-specific service |
| Four helicopters on a real pad | Full rotor/body fit, takeoff/hover/load, climb/descent, ceiling, power-loss descent, landing and passengers |
| Local/metro three-car sets | Actual track fit, grades/curves, swept coupling, retained passengers, conflicts and changed-track refusal |
| Both SkyLink cabins and two support types | Suspension from actual cable points, terminal permission/energy, dwell, boarding and changed-support refusal |
| Cargo/lights | One actual inventory, no outsider/hopper transfers, marker/unload/restart behavior and light restoration |
| Taxi/courier | Owner fleet opt-in, visible seated NPC, accepted movement/fuel, blocking pause, arrival without endpoint teleport |
| Real disconnect/login/restart | No stale controller, one payment/identity, actor-only session refresh, actual-pose resume and safe-exit reservation retention |
| Interrupted/corrupt saves | Stopped simulation, preserved source data, no duplicated grants/items; observed cross-file limits recorded |
| Exact Java and Bedrock clients/packs | Complete correct-sized model, seat/camera/input equivalence and qualified animation/fallback |

Remaining master-brief gaps include a surveyed citywide left-hand road graph, traffic signals/junction reservation, autonomous police/bus traffic, distant abstract traffic, scheduled rail ticketing/careers, custom-track integration, autonomous water/air services, road boost, opening door meshes, theft/insurance/towing, resale/transfer and full customization. Some source models still need richer authored seats/interiors and non-road damage art. Implemented bounded interactions and passing domain tests do not close those gaps or authorize deployment.
