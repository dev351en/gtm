# Vehicle rendering and handling repair

## Reproduced defect

The preserved `1.0.3-r4-functional-candidate` adapter applies each authored model
transform and wheel rotation without cancelling Minecraft's additional
`ItemDisplay` Y rotation. Mojang documents the rendering order as item transform,
Y rotation of 180 degrees, display transformation, then entity orientation:
[Minecraft Snapshot 23w16a](https://www.minecraft.net/en-us/article/minecraft-snapshot-23w16a).

The consequence is concrete: the traditional auto's front wheel is rendered on
the opposite side of its authored pivot. A 90-degree wheel animation moves its
centre above two blocks, higher than the 1.7875-block roof. The same mismatch
reverses the model relative to its seats and collision geometry. A regression test
reproduces that displacement using the actual profile's scale, translation and
front-wheel pivot. The corrected transform keeps the pivot fixed through a full
revolution, including the client's built-in rotation.

`VehicleRenderTransform.compensateItemFacing` appends the inverse Y rotation on
the right of the authored matrix. This is applied once in `setModel` and once in
`animate`; entity yaw, seat coordinates, ownership, vehicles and saved positions
are not remapped.

## Preservation and build boundary

The latest full engine source is still unavailable. `RoadPhysics` is a maintained
replacement using the original public method and record signatures, reconstructed
from the owner-provided binary's API. It is not represented as the lost original
source. The adapter itself is retained and receives four bounded hooks through
the build-only ASM transformer `tools/PatchVehicleBytecode.java`.

Two hooks correct the rendering transforms. The later seating repair changes
the garage's one `enter` call to the maintained `VehicleBoarding` adapter and
adds actual loaded capacity/access guidance to its existing lore callback. The
adapter delegates to the engine's normal `/car enter` path; it does not replace
authentication, locks, keys, reservations, proximity, collision or safe exits.

The transformer checks the entire original core SHA-256, the vehicle class
SHA-256, class identity, method descriptors, invocation descriptors and exact
call counts. It rejects changed, corrupt and already-patched input. It writes a
separate output and never updates the preserved original JAR. ASM is a build-time
dependency and is not required in the game.

## Road handling changes

- Acceleration, braking and coast-down integrate the actual velocity change
  during each tick. Releasing the throttle retains momentum and then stops.
- Opposing throttle brakes to a complete stop before reverse acceleration.
- Low-speed steering retains the authored turning lock. At higher speeds, the
  steering angle is limited to keep lateral acceleration bounded.
- Turns follow an exact bicycle-model arc, with accepted collision distance
  used for fuel and odometer updates. A complete turn no longer risks being
  classified as a stop simply because its chord is shorter than its arc.
- An empty or failed engine cannot add speed; existing momentum coasts down and
  braking still works. A nearly empty tank cannot purchase unfunded acceleration.
- The shared rail/ropeway caller still receives its original proposal contract.
  These modes read speed times the timestep themselves and are intentionally
  unaffected by the road integration change.

## Executed verification of the initial rendering/handling repair

Java 25 compilation and **24 vehicle JUnit tests passed**, with zero failed or skipped
tests. Coverage includes analytic acceleration/stopping distance, timestep
consistency, reverse/brake behavior, inertia, empty/failing engines, partial
collision/fuel accounting, bounded steering, constant-radius turning, all 87
bundled profiles and all 65 road profiles, and the preserved fleet controller
successfully completing a curved route with the revised physics.

The render tests reproduce the original wheel orbit, check the corrected full
revolution, and verify body/front orientation. The new resource-loading test
reads the actual bundled vehicle catalogue and confirms the traditional auto's
raised collision roof, unchanged driver seat/handling and exact repaired geometry
hash. All **53 aggregate repair-module JUnit tests passed** after rebuilding the
overlay with the new profile resource. The separate build checks exercise
determinism, exact hook counts and rejection of invalid/repeated patch input.

## Native client observation and canopy correction

The actual Java 26.3 client mounted the starter traditional auto in staging.
The tester observed forward acceleration (14 km/h), simultaneous forward/steering
(15 km/h), reverse (9 km/h), braking to zero, and safe exit. Fuel changed to 99%
while body health remained 100%. Front and side screenshots at 14:51–14:52 UTC on
25 November 2026 show the front wheel below the chassis, without the previous
above-roof orbit. These observations are a bounded road-driving check, not a
terrain, slope, multiplayer or Bedrock stress test.

The elevated side screenshot also revealed a separate, genuine defect: the
driver's head intersected the canopy. The low front camera hid that intersection.
The preserved profile places the driver carrier at y=0.62. Minecraft 26.3's
`Avatar.DEFAULT_VEHICLE_ATTACHMENT` is 0.6, leaving the player's feet at y=0.02.
The local client bytecode confirms a player render scale of 0.9375, root lift of
1.501, and outer head box reaching 8.5 model units above its pivot. The visible
head therefore reaches approximately y=1.925 at level pitch and y=1.977 at a
15-degree pitch. The original canopy spans y=1.6375–1.7875.

[`tools/repair_rickshaw_canopy.py`](../tools/repair_rickshaw_canopy.py) raises only
that model's canopy by **0.45 blocks** and extends its four support posts. Its
normal, damaged and critical static/animated body models receive the same
world-space correction. Collapsed wreck art is preserved. Six Java model files
and twelve corresponding Bedrock source/display geometry files change; all
texture bytes, UVs, wheel geometry, pivots, item IDs, seat positions and handling
parameters remain unchanged. The helper rejects unexpected or previously
modified inputs using their exact SHA-256 values.

The new roof underside is y=2.0875. This clears the higher rear seat's avatar,
including a vanilla helmet throughout the head-pitch range, by at least 0.027
blocks. The runtime profile's maximum y is rounded upward to **2.238** to enclose
the actual rendered canopy. The other 86 profile rows remain byte-for-byte
unchanged. Bedrock source bounds grow with the canopy; the display bridge's
existing broad culling bounds already enclose it and are checked explicitly.

**Seven canopy regression tests passed** against the actual preserved packs.
They check world-space head clearance, post attachment, collision bounds, exact
scope of geometry edits, unchanged wheels and textures, one-row profile changes,
deterministic output, and rejection of incorrect or repeated input. The normal
repaired geometry's SHA-256 is
`256ff4ca40ae1a310995214a9b261ccfd5e7024a5af73bbdc7d6f31a11c3abf3`;
the maintained profile resource is
`cbafba36c9a031ffe5ed54421946e0a0e21198f4561bfa13b282fc94e698d4a4`.

The initial raised-canopy build subsequently passed the actual Java visual
check; see `docs/repair-evidence/canopy-clearance.json` and
`docs/repair-evidence/vehicle-canopy-final.png`. That historical image predates
the wider four-seat cabin described below. Native Bedrock driving, laptop
performance, broad collision/terrain coverage and deployment to the existing
Daytona server remain outside these observations.

## Driver plus three passengers: the subsequent 1.0.5 repair

The loaded traditional-auto profile originally contained **three total seats**:
driver, rear left and rear right. It did not satisfy the owner's requirement
for **three passengers in addition to the driver**. The garage also always
requested the driver seat, unlike world right-click and `/car enter`, which
already choose a free passenger seat when the driver is unavailable. Locked
vehicles correctly reject ordinary guests until the owner unlocks them.

The traditional auto now contains four actual carrier positions. The existing
rear seat names and indices remain; `rear_center` is appended. Rear x positions
are -0.6, +0.6 and 0, with their original y=0.65 and z=-0.624. The driver is
unchanged. Three 0.6-block-wide mounted player bounds fit across an existing
bench widened from 0.988 to **1.828 blocks**; forward-facing vanilla helmet
boxes have positive clearance between neighbours. This is not a claim that
every possible independent arm/head animation has no visual intersection.

The floor, rear body and canopy widen by **0.84 block total**. Posts and rear
wheel assemblies move outward **0.42 block per side**. The rear animation
pivots move from x=±0.546 to x=±0.966; their y, z, radius and axis are unchanged.
All four art states retain matching width. Normal/damaged/critical states keep
the previously verified 0.45-block canopy lift; the wreck remains collapsed
and the engine already disallows boarding a wreck. Front wheel, driver, nose,
all textures/UVs, item IDs, depth, energy and handling are preserved.

The profile collision width is now **2.14 blocks**, length remains 2.6, and
maxY remains 2.238. The existing `occupiedBounds` includes all four players.
There are sixteen changed Java meshes and thirty-two corresponding raw/display
Bedrock meshes, all protected by original per-file hashes. The Bedrock display
export mirrors X (`8 - Java highX`); the repair and tests account for this,
instead of silently moving a left wheel in the wrong direction.

Two additional omissions were corrected without changing artwork:
`gtm:emerg_police_suv` and `gtm:emerg_patrol_sedan` each have an authored pair of
front leather seat blocks, but previously exposed only the driver. Their
opposite front cushion now has a passenger anchor. The other **84 profile
rows** and every unrelated animated-part row remain unchanged.

Current resource fingerprints:

| Resource | SHA-256 |
| --- | --- |
| Normal raw traditional-auto geometry | `bac1c4669f190a5a65a3aa313b528799bbeacdfb18e36c41f5e284c1e4d5a29a` |
| Maintained road-profiles.tsv | `a78b5cc05343395dbb94b928af0ac9cd86fff16e745a38a5cf9bc28d4b711bf3` |
| Maintained animated-parts.tsv | `3b2a112fe587c9b02ca01246fc4c506e8a755c827e80a4bb353a3bf79cf8f783` |
| Patched GtmVehicles.class | `0677ac5af1e338e47bcf0c9db7395bd00ff4d3a61d6836587d881186638986f8` |

Nine geometry tests and twelve pack regressions passed against the exact
preserved inputs. Seven additional Java boarding tests cover loaded capacities,
locks/keys, unsupported passenger claims, four separated carrier transforms,
rear wheel pivots over complete revolutions, and the two emergency seats.
At the vehicle handoff, all **87 current aggregate JUnit tests**, **826 original
equipment compatibility assertions** and **five bytecode-patcher checks**
passed. The final aggregate build report may include later unrelated tests.

## Fleet capacity audit and remaining interior work

[`vehicle-capacity-audit.json`](../docs/repair-evidence/vehicle-capacity-audit.json)
and its [CSV table](../docs/repair-evidence/vehicle-capacity-audit.csv) record all
87 model IDs, names, loaded driver/passenger counts, actual seat-related geometry,
anchors and source fingerprints. Reproduce them with
`python tools/audit_vehicle_capacity.py`.

All thirty civilian car models contain only two authored front seat cuboids;
none has a rear bench. The four buses are exterior body/window shells without
passenger cushions or a usable aisle. Creating hidden passenger carriers inside
those shells would not finish their interiors. Their current runtime capacity
is explicitly displayed, and the audit records the required hollow cabin,
real seating, doors and avatar headroom work. No capacity is inferred from a
real-world model name. Other transport modes keep their existing profile seats;
the audit distinguishes stored anchors from independently checked seating art.

## Runtime boarding and passenger lifecycle

The preserved engine creates one marker ArmorStand per profile seat and an
equally sized occupant array; no hardcoded three-seat limit exists. Admission
checks authentication, living session, range, line of sight, stopped movement,
vehicle/key/service access and the entire occupied property footprint. Driver
input comes only from the driver carrier. Passenger carriers follow the same
accepted body pose. The actual staged Paper26.3 `CraftEntity.teleport0` uses
`TeleportTransition.PassengerTeleportationMode.POSITION_RIDER`, so ordinary
carrier teleports retain and reposition their passengers.

Safe exit, quit, death, cancelled teleport recovery, parking, chunk deactivation
and shutdown already iterate occupants and clear their rider records/carriers.
Those paths remain preserved. `tools/probe_vehicle_passengers.py` is the bounded
staging acceptance probe: fresh ordinary network Player registrations, locked
guest rejection, four simultaneous carriers, fifth-rider refusal, shared
movement/braking, exit/reboard, quit/login/reboard and parking. It positions only
its own accounts at an observed starting point and never moves the GUI observer.
Its pack statuses are explicitly **headless acknowledgements after byte/ZIP
validation**, not rendered-client evidence. Its resulting JSON must be read
before claiming those live multiplayer checks passed.
