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

Java 25 compilation and **23 JUnit tests passed**, with zero failed or skipped
tests. Coverage includes analytic acceleration/stopping distance, timestep
consistency, reverse/brake behavior, inertia, empty/failing engines, partial
collision/fuel accounting, bounded steering, constant-radius turning, all 87
bundled profiles and all 65 road profiles, and the preserved fleet controller
successfully completing a curved route with the revised physics.

The render tests reproduce the original wheel orbit, check the corrected full
revolution, and verify body/front orientation. The separate build checks exercise
determinism, exact hook counts and rejection of invalid/repeated patch input.

This is source, bytecode and mathematical verification. It does not establish a
native Java/Bedrock visual playtest, driving feel on a laptop, actual per-tick
Paper collision behavior or deployment to the existing Daytona server. Those
observations must remain separate from the passing regression results.
