# Owned wheelchair mobility

`gtm:wheelchair_standard` now has a bounded movement implementation in the furniture engine. The same purchased furniture UUID owns the model, seat, placement and parked pose. It does not create a vehicle entitlement, duplicate item or second ownership store. The `SEAT` catalogue behavior and existing FUR2 placement representation remain compatible.

The fresh expanded laptop profile passed the complete **22-check ordinary paid wheelchair scenario** and a **six-check real translated-protocol continuation** on the same chair. The actor bought, placed, mounted, moved, turned, braked and safely dismounted; the saved entitlement reopened at the actual latest pose. Native Java/Bedrock controls and visual model fit remain separate gates. The earlier failed baseline dismount and its later successful continuations remain recorded below.

## Use

Purchase the wheelchair through the ordinary furniture shop while aiming at clear floor in your own property. Place it with its owned controls, then use **Sit and drive within your parcel**. The owner occupies the real passenger carrier; another player cannot take control.

| Control | Result |
|---|---|
| Forward/back | Move along the chair's facing at at most 0.06 blocks per server tick: 1.2 blocks per second at 20 TPS. |
| Tap left/right with forward/back released | Turn by one quarter turn. Holding a turn key does not spin continuously. |
| Jump | Stop immediately. There is no jump or stair-climbing action. |
| Sneak | Use the normal protected dismount flow beside the chair's current position. |
| Open an inventory | Stop movement. Release and press movement again after closing the interface. |

Motion stays on one flat floor in the same world, inside the complete owner-controlled placement volume. Walls, holes, partial support, water, unloaded chunks, world-border limits, other furniture, vehicle bodies, nearby entities and unsafe exits stop movement. The whole turning sweep and passenger headroom are checked. There is no public-street wheelchair mode, continuous heading, slope traversal or helper pushing. Stretcher and cargo adapters are separate candidates described in [FURNITURE_RESCUE_MOBILITY_R4.md](FURNITURE_RESCUE_MOBILITY_R4.md); their work does not upgrade wheelchair acceptance.

Ordinary ownership and authentication checks remain active. The existing explicit staging exception still requires both `gtm.furniture.admin` and `furniture.allow-public-staging-placement`; it creates no permission or production default. The laptop local workshop sets that exception to false and uses a normally registered non-OP actor. There are at most eight simultaneous wheelchair control sessions.

## Position and recovery

`FurnitureStore` holds one authoritative current placement. Each accepted motion step updates that placement only after the display, interaction target and actual occupied carrier accept their new positions. The existing furniture collision and reservation queries therefore see the chair's current location. A stale expected-pose callback, wrong owner, different model, long/diagonal step, height/world change or overlapping placement is refused.

Movement does not write a snapshot every tick. The current placement is checkpointed about every five seconds while the server is ticking, and on park, normal dismount, authentication loss, logout, despawn/unload and shutdown. Any ordinary durable furniture operation also includes the current motion poses in its snapshot. Graceful restart restores the latest successfully saved placement. An abrupt process or host failure can return the chair to the previous checkpoint, normally at most five seconds of travel earlier; a stalled server can extend that interval. Ownership remains the same UUID in either case. No atomic transaction with Minecraft player/chunk state is claimed.

If a projection move is rejected, the helper restores all projections before accepting another pose; if restoration fails, the live projections are withdrawn. A failed snapshot freezes all wheelchair movement, retains the authoritative current pose and retries saving. A successful retry does not silently resume a held input on an already frozen session. The owner must park/remount after the problem is resolved. Saved data is never replaced with a default or another entitlement to hide a persistence failure.

The cached dismount point is replaced after every successful movement step. Normal dismount also computes a fresh exit against current support, access, furniture, vehicles and entities. Authentication loss therefore does not intentionally return the player to the chair's original mount position.

## Exact Paper carrier calibration

The target is Paper 26.3 build255. Its marker ArmorStand has zero-height dimensions and therefore a zero-height default passenger attachment. The ordinary player has a vehicle attachment of `(0, 0.6, 0)`. `Entity.positionRider` subtracts that player attachment from the carrier's passenger position, so actual player feet are 0.6 blocks below the marker.

The authored wheelchair cushion/hip marker is 0.48 blocks above its floor. This helper deliberately places its marker at floor +0.62, giving a normal-scale rider actual feet at floor +0.02. That is a conservative 0.14-block allowance above the authored cushion, which must be reviewed on actual Java and Bedrock clients. Only normal-scale players are admitted; a scale change stops movement. Shared domain constants derive both carrier position and passenger bounds. The conservative passenger top is feet +1.85, or 1.87 blocks above this chair's floor, so a normal two-block opening remains usable. The collision sweep also includes the real rider's current AABB. Server mobility proof does not establish exact visual sitting pose.

The exact installed server JAR SHA256 is `f5cfa195ce74686a119cfde524ab80d930458b3a8ad24ef4f0c0a156b2a35855`. The relevant `ArmorStand`, `Avatar`, `EntityAttachment` and `Entity` disassembly is retained in `integration-probe-r4/paper255-marker-passenger-offset-javap.txt`, SHA256 `37cd3a3a11627ddcd01a0b821f7c5e1c2599cb3e2fb95ffbeef356584e76e4a0` in the engineering workspace. General furniture/vehicle carrier changes are separately owned by the integration work.

## Executed verification and remaining gates

The targeted Java25 production build compiled the actual Paper255 adapter and passed **17 tests** in `WheelchairMotionTest` and `FurnitureMobilityStoreTest`, with no failures or skipped cases. They cover all four headings; reverse, brake, dismount and rising-edge turns; intermediate rotation corners, calibrated actual passenger headroom and normal two-block clearance; finite/world bounds; one current entitlement; no per-step disk writes; checkpoint/reopen; ordinary mutation flushing; ownership/model/stale-pose rejection; furniture overlap and chunk limits; I/O failure/retry; stale durable-writer refusal; and removal without duplication. The run log is `integration-probe-r4/wheelchair-domain-gradle.log`. A later coherent source compile reran those 17 cases alongside 14 specialist motion/route cases: **31 passed**, with no failures, errors or skips, in `integration-probe-r4/specialist-next/mobility/rescue-motion-gradle-final.log`.

### Current fresh-profile pass

Run `20261125T012027919838Z`, on core SHA-256 `0b49d8e47935b4693f409ad51168a4a292f54b4536dc58ce717ab0bc45209d5c`, passed all 22 ordinary purchase/motion/park checks and all six subsequent protocol-input checks. The original 100/125/20 ARK workshop, storage and food purchases left 75,500 cents; the normal 75 ARK wheelchair purchase left 68,000 cents. The new chair UUID is `c7c4654e-46f4-4338-a48f-7eac15279a1d`. Both scenarios used this one entitlement, without OP, positive permission, item, currency or world-block grants.

The full movement scenario used disclosed server input-event injection, then checked actual detach and saved-state reopen. The continuation received two real translated-client input transitions, with zero companion input injections, and moved the same occupied chair 0.60 blocks from x−171.5 to x−172.1. Release stopped it; ordinary dismount used the current west exit at x−173.0938, with health 20 and bank 68,000 cents retained. The companion only added read-only exit observations; no production movement guard or pass assertion was weakened for this run.

### Retained baseline history

The separate laptop companion acquired the chair through the normal paid shop, placed and mounted it through owned controls, and fed explicit `PlayerInputEvent` objects through the actual registered listener. Run `20261125T002732408524Z` reported 21 passing steps and then failed the final parked/reopened check because the rider remained mounted. The passing observations include the real feet at floor +0.02, marker minus playerY of 0.6, retained health, reverse/forward motion, one-edge turns, brake, matching display/interaction/store positions and a full-body stop before the paid parcel boundary. The earlier dismount step's `leaveVehicle()` return value alone did not establish successful detachment; the following actual passenger assertion exposed that failure.

The same ordinary 75 ARK purchase remains UUID `6125a2d1-dd9d-4110-869f-a8f69a4c2b4f`, and the account bank remains 68,000 cents. After a normal restart, read-only diagnosis found the west exit clear at the same saved chair pose. A follow-up mount attempt then exposed a companion timing error: the actor initially occupied the saved chair footprint, so normal reconstruction had not yet run after stepping aside. The corrected continuation waits for the ordinary reconciliation, reuses that paid chair, and records production exit predicates before and during the actual dismount event. No ownership edit, credit, second purchase, permission grant or forced dismount is used to qualify it.

Run `20261125T003905455521Z` completed both continuations on the existing baseline core. **Parking passed 4/4 checks:** the ordinary owner mounted the reconstructed chair, dismounted to the current west exit at approximately `(-172.4938, 68, -72.02)`, and reopened the identical saved entitlement and pose. The exit predicates remained valid before the request, at both observed event priorities and after detachment; the event was not cancelled. **Translated-protocol movement passed 6/6 checks:** two actual input transitions, with zero companion input injections, moved the chair and rider 0.60 blocks backward from x−171.5 to x−172.1. Releasing input stopped it; normal dismount used the new west exit at x−173.0938, and FUR2 reopened that exact updated pose. Both retained health 20 and the same 68,000-cent bank.

The original blocked dismount's event-time obstruction was not captured. Later passes do not establish a guessed cause for that historical failure. The separate continuation validates actual current-pose dismount and persistence without erasing the earlier result or repeating the paid purchase.

Those actual results and remaining gates are retained in [WHEELCHAIR_MOBILITY_R4_EVIDENCE.json](reports/WHEELCHAIR_MOBILITY_R4_EVIDENCE.json), with the underlying reports in [PAPER_WHEELCHAIR_MOBILITY_R4.json](reports/PAPER_WHEELCHAIR_MOBILITY_R4.json). Event injection and view/position setup are explicit scaffolding. Translated protocol control and native client rendering/control remain distinct evidence gates.

This document does not claim a completed all-model furniture or master-specification acceptance campaign. The wheelchair change adds actual bounded mobility to this one existing design; broader specialist behavior and world commissioning remain separately tracked.
