# Supplied vehicle workshop and retained hoist

The six existing workshop models now have distinct native actions. Engine lubricant, tyre pressure, tread and wheel balance affect actual accepted ROAD motion. The hydraulic model physically raises and lowers an empty owned vehicle between its authored posts. Its two support arms move with the chassis. No canonical model ID, ownership row, painted texture or backing inventory is replaced.

## Player use

Buy and place the machine on your own supported clear property through the ordinary furniture shop. Park your own stopped empty ROAD vehicle within six blocks of it, approach the visible controls within five blocks, and right-click the machine. The menu shows the real vehicle, current maintenance gauges and the exact supplies before work. All ingredients must be plain vanilla items in your storage inventory; renamed, tagged or custom items are not consumed as substitutes.

| Existing model | Real supplied action | Recipe and effect |
|---|---|---|
| `hydraulic_auto_lift` | Captures, raises, holds and lowers an actual vehicle | One coal or charcoal supplies one complete raise/lower cycle. Up to 16 cycles may be stored. Lowering an existing held vehicle never charges another cycle. |
| `air_compressor_tank` | Inflates the real vehicle's tyres | One coal or charcoal powers one inflation. Restored pressure improves actual acceleration/braking and lowers rolling energy cost. |
| `wheel_balancer_digital` | Balances the real vehicle's wheels | One coal or charcoal and one iron nugget power the balance/weight service. Restored balance improves steering response and the bounded speed limit. |
| `tire_changer_machine` | Replaces the vehicle's worn game tyre set | Four leather and two iron ingots restore tread, which affects braking and maximum speed. The independent pressure/balance gauges remain visible. |
| `motor_oil_dispense_rack` | Services engine lubricant | One slime ball and one honeycomb are the explicitly fictional game lubricant recipe. Oil restores acceleration and engine efficiency; it does not add fuel. Electric ROAD vehicles refuse engine-oil service. |
| `welding_rig_cart` | Repairs actual native chassis damage | Two iron ingots and one coal or charcoal add at most 25 health, capped at 100. It leaves energy unchanged. A destroyed wreck requires the existing recovery service. |

Fresh/full gauges refuse unnecessary work before consuming anything. All operations recheck the current authenticated session, ordinary furniture/vehicle permissions, actual ownership, world, range, line of sight, loaded geometry and the complete owned property corridor. A deferred menu loses authority on logout, permission loss, changed machine/vehicle access or leaving the menu.

These are bounded game mechanics, not real automobile specifications or repair instructions.

## Maintenance and real road physics

Maintenance baselines are measured against the existing native vehicle odometer, which advances only when collision-checked road movement is actually accepted. Stationary time, menu inspection, blocked travel, logout and bookkeeping do not add wear. Four saved baseline distances preserve oil service, tyre replacement, inflation and balancing independently.

For each gauge, quality is `max(0, 1 - accepted_distance_since_service / interval)`. The intervals in game blocks are 8,000 for oil, 10,000 for tread, 2,400 for pressure and 6,000 for balance. Electric vehicles use full oil quality because they have no engine-oil service.

| Physics input | Actual bounded factor |
|---|---|
| Acceleration | `0.75 + 0.15 × oil + 0.10 × pressure` |
| Maximum forward/reverse speed | `0.80 + 0.10 × tread + 0.10 × balance` |
| Braking | `0.70 + 0.20 × tread + 0.10 × pressure` |
| Steering angle response | `0.80 + 0.20 × balance` |
| Energy per accepted block and active idle | `1 + 0.15 × (1 − oil) + 0.20 × (1 − pressure)` |

All full gauges use the exact original normal factor record. These factors compose with the existing health limit; they do not replace collision, fuel exhaustion or condition rules. `RoadPhysics.propose` uses the same increased energy rate as `RoadPhysics.accept`, so the final funded tick cannot move farther than the remaining energy supports. An accepted collision refusal does not manufacture odometer wear. All non-ROAD paths retain the original overload and behavior.

## Physical hoist and ownership

The original source has two posts, a crossbar and two support-arm cubes. Its old single rectangular collision envelope filled the space between the posts. The workshop now uses the actual fixed post/crossbar volumes and independently positioned arms. Only the selected lift's arms are excluded from its own guarded chassis movement; every other furniture object, vehicle, real block/hazard and living entity remains an obstacle.

Center the empty vehicle within 0.12 blocks sideways and 0.30 blocks along the bay, parallel within three degrees. The chassis must be at most 2.3 blocks wide and six blocks long. Its actual height must leave at least 0.25 blocks of stroke under the existing crossbar. Rise is capped at 1.2 blocks and shortened further by that authored clearance. Each synchronous step is at most 0.04 blocks vertically; horizontal position and heading cannot change during the hold. Actual empty chassis bounds are used instead of an imaginary seated passenger's headroom.

Before the first movement, the native base pose is saved, the exact vehicle/owner/lift/world/placement/base/stroke binding is retained, and one stored cycle is debited in the same workshop checkpoint. Boarding, ordinary parking/service, cargo authorization, fleet consent/selection/reservation/driving and normal vehicle simulation all refuse a held vehicle. Ordinary movement, rotation, unbinding and removal of its lift also refuse until it is safely released. Live projection loss reconstructs from the same native state and retained obligation rather than dropping the vehicle or making it drivable.

Each moving tick requires the original current operator session and exact still-owned live machine. Permission/authentication loss, an inaccessible or unloaded world, a changed machine or an actual obstruction stops motion and saves the current hold. Logout or a normal restart does not resume movement. The owner must return to the matching controls and explicitly choose raise or lower. Lowering verifies the original support, reaches and saves the exact base pose, then releases the obligation. A blocked lower retains the load and its diagnostics.

The technical render selectors are `gtm:fm_hoist_frame` and `gtm:fm_hoist_arms`. They reuse exact source cube UVs, the unchanged native128 atlas and icon. Half-scale meshes plus exactly doubled ItemDisplay scale keep Java element coordinates within the supported bounds. The original canonical item/entitlement remains `gtm:hydraulic_auto_lift`; these two runtime parts add no unique painted design. Native-client visual qualification remains separate.

## Persistence and limits

`vehicles/workshop.snapshot` is a bounded gameplay-state aggregate: at most 512 maintained vehicles, 512 finite-fuel machines, 32 held vehicles and 2,048 per-owner last supply receipts. It stores no item inventory. A proof bound to owner, exact machine, vehicle, operation, observed odometer and monotonic supply sequence is written into the existing player record with the actual ingredient debit. A matching repeated proof acknowledges the prior result; contradictory, stale, skipped, malformed or wrong-type proofs fail closed and remain available for diagnosis. Native welding commits the health change with its own `WORKSHOP_WELD` receipt in the existing vehicle snapshot before acknowledging workshop completion.

The current source requires a valid pending sequence before an external native weld effect. Inventory/storage journal failures pause the action and retain its proof; they do not invent refunds. The existing Paper `Player.saveData()` call offers no durable-write acknowledgement. These receipts do not establish cross-file atomicity or a hard-power-loss guarantee. The held native pose and workshop obligation are independently validated on reconstruction. A mismatching saved identity/pose is retained for review rather than silently reset.

Read-only obligation checks remain available when vehicle motion is disabled or suspended, allowing an unengaged old workshop model to be removed normally. Actual work and motion continue to require the enabled native backend. A held load remains guarded even when the backend cannot move it.

## Qualification

The initial focused source gate compiled all main/test sources and passed 88 cases: 23 new workshop rules/proof/geometry/physics checks plus 65 existing road, transport and fleet cases, with no failures or skips. A subsequent concrete skipped-weld sequence regression brings the new workshop set to 24. The final combined focused gate passed **69 tests in nine suites**: all 24 workshop, 15 cart and 30 cargo cases, with zero failures, errors or skips. [The component evidence](reports/FURNITURE_WORKSHOP_R4_EVIDENCE.json) records the exact source hashes and qualification scope; [the raw focused log](reports/WORKSHOP_CART_FOCUSED_R4.log) preserves the outcomes. The parent's full coherent gate separately covers the final generated catalogue and the two existing furniture-test expectations updated for the specialized workshop registry.

The earlier coherent source snapshot `1a2d6e991d1939227826445dcbbd3813f6e3a8a329fa7043022104c5038c46d7` passed **591 tests in 73 suites plus 155 domain assertions**, with zero failures, errors or skips. Its sealed core SHA-256 was `b19aeb13a2fde033da787e6e204b2106808105ad4cdf4d035d89113b36d9ad3f`. The later geometry/admission corrections and their regressions are included in the **644-test, 79-suite and 155-domain-assertion** build actually used for the complete workshop pass below. Historical build/source evidence remains in the component manifest.

The isolated companion in the source-checkout path `tools/probes/furniture_workshop/README.md` has 27 actual-Paper scenarios plus cleanup. It observes real supplies, accepted road wear/energy, changed physics factors, welding, saved-proof replay, real frame/arm/chassis pose, a blocking ceiling, holding locks, current permissions, ordinary logout/login, stale-menu rejection, fresh snapshot readers, invalid-projection reconstruction and supported lowering. Its test supplies/grants, positioning, direct road-control steps and receipt/event injections are explicit scaffolding. The actual results below qualify these bounded server effects, while native Java/Bedrock rendering and human control remain separate.

### Complete actual server qualification

[The canonical raw workshop report](reports/PAPER_FURNITURE_WORKSHOP_R4.json) passed **28/28 records**, with no failed or unexecuted steps, one normal reauthentication, completed workshop cleanup and no remaining workshop fixture. All six supplied machines, real road maintenance effects, saved-proof refusal, real hoist raising/holding, overhead obstruction, current permission/session loss, actual chassis reconstruction after login, supported lowering and release were observed.

| Evidence | Exact value |
|---|---|
| Controlled run | `20261125T023032130680Z` |
| Actual core SHA256 | `b7c76cd3a664e1bb7e1e56fd2098f7ef0a71e921d47170ed10c4e658974715af` |
| Coherent source snapshot SHA256 | `8df6f572928534b3e857dde033acb0a5b0afe3680817950505d23e34b9fc3e06` |
| Companion SHA256 | `ece57f5103026bcce8b8efac3633d6bbf4c95f9b22cd686b870589dde9acb6e2` |
| Raw report SHA256 | `03029d5c313a32673fb203fe104f485d0e7e5182570a4c2369cf95fd9197086b` |
| Actual Java pack SHA256 | `5b5e132a2c670b07e8c0c389e086bd2dee1002ed7de72a6bdcd93acc6d6cba9a` |
| Actual Bedrock pack SHA256 | `c10b185151751c94c6e670a3beab8e0d36e28a1c9b9478fcd745d5c6965641cf` |

The run used the explicit **retained-workshop recovery** mode in a complete disposable state copy, preserving the older same-bay records that had exposed admission starvation. It did not graft snapshots or infer missing before-state data. Its cleanup claim covers only x6296–6336, z6296–6330, y219–225 and the workshop's own actor setup. Unplaced QA furniture, the parked QA vehicle and completed supply receipts remain in that disposable copy.

The unrelated interrupted festival fixture near x7072–7135 remained outside this cleanup scope. Its pending marker, block journal, before-state file and 80-check interrupted report retained identical SHA256 values before workshop work, after cleanup and after server shutdown. Ordinary world ticks are not claimed to freeze the entire world byte-for-byte, and no claim is made that the earlier actor's unjournaled flags or the festival fixture were restored. [The component evidence](reports/FURNITURE_WORKSHOP_R4_EVIDENCE.json) records those exact boundaries and input hashes.

### Preserved earlier attempts

The first actual run on the sealed core passed seven scenario checks and clean rollback, then refused the oil action before normal projection reconstruction had completed after permission restoration. The [unaltered attempt report](reports/PAPER_FURNITURE_WORKSHOP_R4_ATTEMPT_01.json) is retained. The corrected companion waits for actual valid native projections and keeps terminal results unpublished until cleanup finishes; ten standalone report-provenance assertions pass. This initial attempt remains a failure, independently of the later complete pass.

The [second actual attempt](reports/PAPER_FURNITURE_WORKSHOP_R4_ATTEMPT_02.json) passed all supplied maintenance, real welding and saved-proof checks, but its explicit wait proved that the unheld cargo auto prevented the lift from reconstructing inside its otherwise open bay. Its final report retained 15 passing records, one failure, 12 unrun scenarios and successful cleanup. The correction admits only a verified stationary empty native vehicle whose complete physical chassis clears the actual posts, header and arms, under the current owner and full property checks. Three new geometry regressions passed in the combined 133-case gate; the later complete actual run also exercised that correction.

The [third actual attempt](reports/PAPER_FURNITURE_WORKSHOP_R4_ATTEMPT_03.json), on the later sealed `fd4ec8b7ffd59e381693c255fdad3fd37f9010256d5d13b5814dc28af193a15b` core, passed 22 records including clean rollback. Actual supplied maintenance, bounded raising, real ceiling refusal and permission-stop succeeded. After normal login, every workshop model and split lift existed, but the native held chassis was not admitted by the periodic recovery loop. The five following scenarios remained explicitly unexecuted.

The exact retained older QA records shared the bay. The source loop always began with the first records and spent its two-attempt budget on failed admissions, so earlier blocked vehicles could starve a later recoverable vehicle. Direct ordinary activation/lowering during cleanup succeeded without changing its guards. The [diagnosis and retained snapshot facts](reports/WORKSHOP_ADMISSION_RECOVERY_R4.json) distinguish those observations from the source-backed inference about live insertion order. A transient rotating cursor now keeps the same two-attempt budget and every current authorization/geometry rule while advancing past refusals. Five new scheduling regressions passed together with existing workshop, hoist, transport and fleet cases: **74 tests in seven suites**, zero failures, errors or skips. The 644-test coherent build and complete retained-state actual workshop run above then passed with this correction.
