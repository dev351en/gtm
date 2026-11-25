# Stretcher transport and lifebuoy self-rescue

The existing `gtm:transport_stretcher` and `gtm:coastal_lifebuoy_stand` models have bounded server movement adapters. A stretcher carries an explicitly consenting patient while its owner pushes from nearby. A lifebuoy station offers its owner a short surface-water journey to a checked shore, using a temporary projection of the original buoy artwork. The player's real passenger carrier travels along the route.

The original furniture identities, purchases and older FUR2 records remain readable. The focused domain/store tests pass, and the separate actual-Paper rescue scenario passed all **32 checks** on Paper 26.3 build 255. It observed real stretcher and rider movement, consent, obstacle stops, current-position exits, floating-ring travel, shore arrival and the retained real-bed mode. Native Java and Bedrock rendering, controls and seating fit remain separate acceptance gates. The current evidence is recorded in [FURNITURE_RESCUE_MOBILITY_R4_EVIDENCE.json](reports/FURNITURE_RESCUE_MOBILITY_R4_EVIDENCE.json) and the complete [actual Paper report](reports/PAPER_FURNITURE_RESCUE_R4.json).

## Model behavior

| Existing model | Working path in this candidate | Boundary |
|---|---|---|
| `gtm:transport_stretcher` | Unbound: invite one nearby patient, obtain their explicit acceptance, then push or pull the actual occupied model. Bound: use the existing real two-block bed for ordinary sleep. | Transport requires an unbound model. Stationary bed use and moving transport cannot run together. |
| `gtm:coastal_lifebuoy_stand` | Retains the existing first-aid service. Its owner can accept a short tow from source water to checked nearby shore. | Self-rescue only; no automatic capture of another swimmer. The station remains fixed. |
| `gtm:pallet_jack_manual` | Shares the typed ground-motion adapter at a lower speed. The cargo helper supplies a separately guarded real-container load. | Inventory custody, loading and unloading belong to the cargo helper. Motion does not copy or access item inventories. Bound legacy jacks keep fixed storage. |

All ownership and access checks apply to the original furniture UUID. No vehicle record, replacement furniture entitlement or collectible rescue-ring item is created.

## Use the stretcher

Acquire the original stretcher through the furniture shop, place it on clear supported floor inside your property, and leave its bed binding unset. Use **Patient transport / bound-bed sleep** to select a nearby patient, or enter:

```text
/furniture transport <owned stretcher UUID> <online patient name>
```

The owner stays on foot within 3.5 blocks and maintains line of sight. The patient must be within four blocks, authenticated, permitted to use furniture, at normal player scale and unmounted. The patient sees a confirmation menu with **Accept this trip** and **Decline**. Inviting someone does not mount or move them.

The invitation expires after 20 seconds and belongs to the exact owner and patient authentication sessions, furniture placement and patient downed episode. A wrong player cannot consume it. Declining, closing the confirmation, expiration, a changed session or a changed placement invalidates it. Accepted tokens cannot be replayed. This adapter applies no healing or revival.

| Attendant control | Result |
|---|---|
| Forward/back | Push or pull the model along its current cardinal heading, at most 0.04 blocks per server tick: 0.8 blocks per second at 20 TPS. |
| Tap left/right with forward/back released | Turn once by 90 degrees. Holding a turn key does not repeat rotation. |
| Jump | Brake immediately. |
| Open a menu | Stop motion until normal controls resume. |
| `/furniture rescuestop` | End the current trip. Either participant can request this. |
| Patient sneak/dismount | Request a checked exit beside the current stretcher position. An obstructed exit stops movement and refuses that ordinary dismount. |

The attendant is a real on-foot obstacle. Pulling the stretcher through the attendant or turning through their body is refused. Keep enough room beside or behind the model for the intended movement.

Ground travel remains on the same flat supported level and inside an authorized property volume. It does not traverse stairs, slopes, water, unloaded chunks or arbitrary public streets. Before each accepted move, the runtime checks the full model sweep, a conservative passenger envelope, the actual rider bounding box, world border, real block collision, complete floor support, property access, other furniture, vehicle bodies, nearby entities and a current safe patient exit. Rotation uses a full conservative circle around the model and passenger so intermediate corners cannot pass through a wall.

There are at most four combined specialist motion/tow sessions. A ground session lasts at most five minutes and stops sooner if its owner, patient, authentication session, permission, scale, proximity, line of sight or required passenger attachment changes. The existing explicit public-staging exception remains limited to a configured isolated test copy and its authorized administrator; it creates no production permission.

### Stationary sleep remains available

While the stretcher is unplaced, connect its ordinary bed backing to an existing complete bed that you own and can access. Then place it through the normal furniture controls. **Use** invokes the real bed's sleep behavior. A bound stretcher cannot begin transport. To move it later, remove its placement and disconnect the stationary binding through the normal owner interface before placing it unbound again.

This preserves older FUR2 stretcher records with bed bindings. It does not synthesize a bed, change the world clock during normal use or copy bed contents.

## Use the lifebuoy station

Place your original `coastal_lifebuoy_stand` on authorized shore ground. First-aid service remains available through its station menu, with that service's existing access and costs. Surface self-rescue is a separate explicit action:

```text
/furniture rescue <owned lifebuoy-station UUID>
```

Enter calm source water within 12 blocks of your visible station, then request rescue. The runtime searches a bounded, loaded route to dry shore within 2.5 blocks of that station. The confirmation states the actual route distance. Accepting begins a real passenger journey at most 0.04 blocks per tick, or 0.8 blocks per second at 20 TPS. Sneak or `/furniture rescuestop` releases the swimmer at the current local position.

The route is limited to 12 blocks, 32 stored points and 256 inspected search cells. Its water and destination must share one surface level. Every footprint column must have source water or genuine support; flowing water, bubble columns, lava, uneven water and unsupported shore are refused. Full rider headroom, current property entry permission, blocks, entities, furniture, vehicles and the station's own solid footprint are checked. Search and movement do not load chunks or alter terrain.

At acceptance, the starting position, water level, station pose, route, owner session and permissions are rechecked. A swimmer may be lifted only the short checked distance from surface water onto the float; the maximum initial vertical adjustment is 1.25 blocks. The route distance itself is traversed by the real carrier over successive ticks. A local same-position dismount adjustment at the endpoint places the player on the validated shore.

The route is revalidated during travel. A newly blocked segment, changed access, lost session, moved station or rejected projection stops the trip at its current location. A changed route requires a fresh request and acceptance. A tow expires after 30 seconds. It grants no health, air, currency, item or ownership. Ordinary Minecraft air behavior applies once the player's actual body is above the water surface.

The station stays at its original saved pose throughout the tow. The ring and its carrier are temporary, nonpersistent entities; logout, authentication loss, station removal or server shutdown ends the session. A restart never silently resumes a rescue or supplies a new ring item.

## Real carrier and safe dismount

Paper 26.3 build 255 subtracts the ordinary player's 0.6-block vehicle attachment from the marker carrier's position. The stretcher uses the shared conservative carrier height of at least 0.62 blocks above its floor. Normal-scale player feet therefore remain at least 0.02 blocks above the floor. The occupied sweep reserves feet plus 1.85 blocks and includes the actual current bounding box. The float derives its marker directly from the checked water-surface feet position plus 0.6.

Minecraft renders a normal seated passenger on the stretcher carrier. A lying medical pose and exact native cushion fit are not claimed. The authored model is preserved; actual Java/Bedrock visual review must decide whether a further compatible presentation adjustment is needed.

Normal dismount is validated at the current pose. The helper stops motion immediately, allows a valid Paper dismount event to finish, and performs cleanup only after actual detachment. This ordering matters: exact Paper temporarily clears `rider.vehicle` while dispatching the event and restores it if the event is cancelled. Neither a temporary null vehicle nor the boolean return of `leaveVehicle()` alone proves successful detachment. If another listener refuses dismount, the existing session remains frozen and retains its real carrier. No old mount-time exit is substituted.

Authentication loss or a forced cleanup stops transport without returning the patient to an obsolete origin. A currently safe local exit may be used only when the current authenticated session permits it. An unavailable exit is not replaced with an unchecked teleport.

## Position, inventory and restart semantics

Typed ground motion uses `FurnitureMotion.Kind` and an expected/current-pose check in the existing `FurnitureStore`. A movement step must match the original owner, exact asset kind and unbound state. Only after the model, interaction target, occupied carrier and any guarded cargo projection accept the new location does the store publish the one authoritative placement. Existing collision queries therefore read the same pose that movement uses.

The single furniture store retains cardinal quarter turns and reads older FUR1/FUR2 records. The later structural-geometry revision writes FUR3 on a normal saved mutation, preserving the same rescue identity and pose; it does not open a second ownership store or rewrite merely on reading. Current poses are checkpointed about every five seconds and on park/stop, ordinary furniture mutation, removal and shutdown. There are no per-tick disk writes. Graceful restart restores the latest saved pose. Abrupt process or host failure may restore an earlier checkpoint; atomic persistence with Minecraft player/chunk state is not claimed. The earlier 32-check rescue run retains its exact historical core and format provenance in the evidence manifest.

A projection failure attempts to restore the original projections. Failed restoration withdraws the live model. A persistence failure retains current in-memory placements and freezes movement; it does not replace ownership or data with defaults. Saved sessions and passenger consent are not reused after restart.

For pallet cargo, the motion helper asks the cargo adapter for the current and next payload volumes and includes them in every swept check. A turn also includes the full-circle payload envelope, including its vertical bounds. The helper only requests projection movement and reports stop/rollback; the cargo subsystem retains its durable locked custody until normal explicit delivery or recovery. This document does not imply unrestricted cargo routing.

## Native 128 artwork and exact binding

The floating projection is a technical derivative of the existing native-128 `coastal_lifebuoy_stand` source. It extracts the original buoy-face cubes and their unchanged per-face UVs from the station, excludes the post/base, recenters the face and rotates it flat. It adds no painted texture, canonical design or purchasable entitlement. The original 2048×2048 atlas of native 128 cells remains intact.

The runtime selector is `gtm:fm_rescue_ring`. Java item/model, Bedrock geometry/attachable and Geyser bindings are generated by `tools/gtm_furniture_runtime_assets.py`. Exact paths, transforms and provenance are recorded in [FURNITURE_RESCUE_RENDER_BINDINGS.json](reports/FURNITURE_RESCUE_RENDER_BINDINGS.json). The pack builder includes this overlay and the display compatibility registry includes its selector. Static binding/derivation checks do not prove native rendering.

## Verification and next acceptance

The focused source run includes the existing eight wheelchair-motion and nine mobility-store tests plus six specialist-motion and eight surface-route tests: 31 domain/store tests in total. The specialist cases cover typed speed/asset admission, preservation of bound legacy uses, expected-pose and owner rejection, one original saved entitlement, rotation/passenger bounds, bounded water-to-shore search, detours, route changes and invalid/nonfinite input. The two Python overlay regressions check extraction from the original artwork and exact resource bindings.

The separate test-only companion is documented in the source checkout at `tools/probes/furniture_rescue/README.md`; it is not part of the laptop package. Its 32-step scenario requires two normally authenticated actors in an exact disposable Paper255 path. It observes actual confirmation/decline/replay handling, real occupied stretcher travel, wall/turn/brake/current-exit behavior, permission loss, the actual floating carrier, per-tick tow displacement, changed-obstacle stop, fresh acceptance, shore arrival and retained real-bed sleep. Fixture geometry, two explicit fixture entitlements, view/position setup and injected server events are disclosed scaffolding. The normal non-OP laptop purchase flow is qualified by its separate companion.

The successful run, `20261125T005909705988Z`, sampled 173 ticks with actual mounted movement. Its largest measured step was 0.040000000000873115 blocks, within the 0.04-block step plus floating-point tolerance. After the obstacle stop, the first detached tick and the later observation both recorded the same position `(5812.1, 220.02, 5803.5)`, no carrier, no active tow and real source water below with block light 14. The translated actor remained at float height, so the companion explicitly moved only that already-stopped actor down to Y219.5 in the same column before requesting fresh consent. This is fixture setup, not evidence for native swimming or gravity. The second accepted tow reached the dry shore, and exact fixture cleanup completed.

The first actual run remains in the evidence. It passed 25 checks, then failed its assumption that the released translated actor would already be swimming again; cleanup correctly refused three source-water cells that had frozen to ice. Its stopped copy and original journal are retained at `integration-probe-r4/server-after-rescue-water-stop`. The correction added a real illuminated pool base and verified light/source states, and separated stopped-only actor setup from actual transport. Production water, movement, consent and exit rules were unchanged.

No actual rescue scenario, native Java client, native Bedrock client, public city route commissioning, Windows launcher execution or all-model acceptance is inferred from compilation or these focused tests.
