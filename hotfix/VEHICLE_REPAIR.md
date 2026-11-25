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
source. The adapter itself is retained and receives two stack-neutral calls through
the build-only ASM transformer `tools/PatchVehicleBytecode.java`.

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

## Executed verification

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

The final native visual check of the newly raised canopy is pending the staging
restart and matching pack reload. Native Bedrock driving, laptop performance,
broad collision/terrain coverage and deployment to the existing Daytona server
remain outside the observations recorded here.
