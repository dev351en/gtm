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
movement after throttle/brake inputs, exit/reboard, quit/login/reboard and
parking. It positions only its own accounts at the observed starting point or a
server-selected safe-exit point and never moves the GUI observer. Its block
coordinate comparisons verify shared displacement, not exact braking speed.
Its pack statuses are explicitly **headless acknowledgements after byte/ZIP
validation**, not rendered-client evidence. Final observed results are recorded
below; the original blocked-parking phase is retained without relabelling its
timeout as a pass.

## Final 1.0.5 multiplayer and native acceptance

The actual isolated Paper 26.3 server ran core SHA-256
`17d9a549c83d16fa5cc15af66aa29dccbe45cef7793e49a47476d552c3bd447a`,
Java pack `77782c8cade9ca7ac07d408e2f1425b8d73eb8d78408cca0a5454c14b28f8188`,
and optional native client HUD
`b1bf80057b30e94c7d04b1d49ad06d442972f0cf0b441f710b5c513cfe92ab84`.
The composite [network acceptance record](../docs/repair-evidence/vehicle-passenger-network.json)
preserves the exact outcomes of both live phases.

On 25 November 2026, the main run passed **eight substantive assertions**:
ordinary owner/guest authentication, locked-guest refusal, driver plus three
simultaneous passengers, fifth-rider rejection, common driven displacement,
normal passenger exit and automatic reboarding, and quit/login seat reuse.
The owner occupied carrier 662; the three passengers occupied 663, 664 and 665.
All four players moved **two blocks along the same axis**, retaining those
carriers after ordinary forward/brake inputs. These integer coordinates verify
shared movement; they do not independently establish an exact stopping speed.

The final fully occupied `/car park` attempt **correctly refused the fourth
exit**. Three players had already reached valid right/left/rear standing points;
another ordinarily delivered test auto blocked the front point. The preserved
engine checks four cardinal exit points, so it kept the remaining passenger
seated and reported that clear exit space was required. The original probe
therefore ended with a parking timeout; its eight earlier passes remain valid.
No collision or access check was weakened to force a pass.

A separate, narrow followup reconnected the **same owner and previously blocked
guest**, after the other actors had cleared those points. It passed **three
checks**: ordinary login without new actors/grants, normal passenger boarding
and safe exit, and owner parking/saving of the now-empty same vehicle. The
private test-session credentials, stored with mode `0600`, were deleted, all
protocol actors disconnected, the GUI exited normally, and Paper then shut down
with exit code `0`.
The initial harness corrections and crowded-spawn delivery deferral are also
disclosed in the composite record; they are not presented as vehicle test passes.

The independent [native observation](../docs/repair-evidence/vehicle-native-observation.json)
contains unchanged Minecraft F2 captures of the **driver and three rear
passengers**, with heads beneath the canopy and wheels on the ground. One native
GUI rendered the four real network actors; this was not four GUI clients.
The same non-operator GUI account then boarded the unlocked auto through an
ordinary empty-hand right-click and safely exited using Left Shift. The garage
inventory click adapter remains source/bytecode/unit tested, rather than being
claimed as part of this mouse-interaction acceptance.

### Ordinary owner and passenger controls

The auto holds **one driver plus three passengers**. `/car` shows owned vehicles;
the preserved garage item lore includes the full vehicle UUID. Use that UUID
when sharing the command path or choosing between nearby vehicles.

| Action | Control | Observed behavior |
| --- | --- | --- |
| Owner toggles guest access | `/car lock <UUID>` | Switches between locked and unlocked; the successful test exercised both states. |
| Passenger boards | Right-click the unlocked nearby auto with an empty hand | Native GUI mounted a passenger in a free seat. |
| Explicit passenger boarding | `/car passenger <UUID>` | Three ordinary guests boarded the same unlocked, stopped auto. A fifth occupant was refused. |
| Automatic boarding | `/car enter <UUID>` | An ordinary guest reboarded a passenger seat while the owner retained the driver seat. |
| Leave | Left Shift, or `/car exit` | Uses a checked safe standing point; clear space if the game refuses an unsafe exit. |
| Park and save | `/car park <UUID>` | Owner/key access required. It safely exits occupants when space permits and saves the vehicle; it does not remove or despawn it. |

Unlocking passenger access does not give guests driving keys. The owner or an
authorized keyholder retains driver access. Locked non-owner UUIDs are filtered
by the preserved resolver, so a command may report an ambiguous/unavailable UUID
instead of exposing that locked vehicle. This is separate from the visible
right-click interaction and is covered by the lock/unlock acceptance sequence.

### Driving engine and remaining fleet work

Driving uses the preserved server-side `GtmVehicles` engine with the maintained
`RoadPhysics` replacement at a 20 Hz game-tick timestep. It applies acceleration,
coasting, braking through zero before reverse, bounded steering and accepted
collision movement, then moves every seat carrier with the same body pose.
The repair is a kinematic driving system; it does not claim a rigid-body
suspension simulation or broad terrain/slope certification.

The [87-model audit](../docs/repair-evidence/vehicle-capacity-audit.json) and its
[CSV table](../docs/repair-evidence/vehicle-capacity-audit.csv) remain the capacity
reference. The traditional auto now has one driver and three passenger places;
the two omitted existing emergency
front passenger seats are enabled. Thirty civilian car models currently have
two authored front seats, and four bus models still need usable passenger
interiors. Their missing rear seats/interiors have not been replaced by hidden
carriers or guessed capacities.
