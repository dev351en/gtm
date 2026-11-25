# Traffic signals and consumption-linked fictional exposure

## What the original assets do

`gtm:traffic_signal_pole` retains its original native128 art, POWER backing and ownership identity. Its Use control now commissions and runs an actual four-way signal. Both manually driven native road vehicles and managed NPC vehicles use the same complete-body stop-line policy. The original bound lever powers during the north/south green phase, and a nearby text display identifies the current phase and remaining time.

`gtm:breathalyzer_test_bench` retains its original native128 art and owned furniture identity. Its Use control measures the current fictional exposure derived from actual consumed-drink receipts. The owner can test themself or request the closest nearby authenticated player's explicit consent. The reading is expressed in **fictional game units**. It is not blood alcohol concentration, medical advice, a sobriety certification, or an automatic crime/arrest rule.

These are platform implementations. Source tests, actual Paper behavior and native client visual acceptance remain separate evidence levels. See the final release evidence for the exact JAR, pack and executed report hashes.

## Commissioning a signal

Place the owned pole and bind its real lever through ordinary furniture controls. Use the pole, select the intersection floor, then right-click the top of a real solid floor within eight blocks of both yourself and the pole. The whole loaded nine-by-nine-block envelope must remain within the owner's accessible property. Its three-block-wide crossing needs full support and clear headroom. The adapter refuses overlapping commissioned envelopes, missing chunks, hazards, inaccessible property and changed backing geometry.

Start the surveyed controller explicitly. The cycle starts with one second of all-red clearance, then alternates ten seconds of green, two seconds of amber and one second of all-red for the north/south and east/west approaches. Stop lines sit three blocks from the selected center. Braking uses actual vehicle speed and handling; substeps cannot move a vehicle's complete occupied body through a red or amber line. A vehicle already within the junction may clear it. Reversing uses the real direction of travel.

A red light is a planned wait. It does not apply collision damage or permanently pause an NPC trip after the ordinary obstruction timeout. Geometry, owner session, ownership and current permission remain live checks. Loss of those conditions stops the controller and turns its output off. Stopping releases the road policy; this subsystem does not silently create a public traffic authority or keep an unattended controller operating. A restart preserves surveyed geometry and requires another explicit start. At most sixteen controllers run at once, with 128 saved commissioning records.

Signals do not create roads, junctions, route surveys, taxi fleets or public build permission. Actual roads and service routes still require their existing setup and validation.

## Restricted fictional drink

The optional counter item is a clearly labelled variant of the existing `gtm:food_nimbu_pani` native128 cup. It introduces no new canonical art or entitlement ID. Its server item is owner-bound, serialised, limited to one per stack and has zero nutrition and saturation benefit.

Configuration is `food.fictional-alcohol.enabled`, with the separate `gtm.food.fictional-alcohol` permission. It defaults off in a generic server. The isolated laptop playtest profile enables the option and ordinary account permission. A player must be at an accessible food counter, review the stated negative consequences and explicitly confirm the 20 ARK purchase. The existing paid-delivery outbox supplies the item after payment.

Actual consumption causes four seconds of blackout, sixty seconds of weakness and a two-point health reduction that neither kills the player nor heals a player already below the one-point threshold. It records 6000 ticks of personal recovery time without setting or advancing the shared world clock. Every seven consecutive in-game drinking days adds a one-heart maximum-health penalty. Each completed abstinent game day recovers one maximum-health point. The configurable minimum maximum-health value defaults to four points. Only this subsystem's named attribute modifier is adjusted; existing modifiers are taken into account when enforcing its floor. Recovery of maximum health does not automatically heal current health.

The exposure counter increases by one fictional unit per consumed item, caps at eight units and decays with actual game ticks. A repeated same-day drink does not advance the daily streak. Clock rewinds cannot erase obligations, and moving to another world does not select a different clock. The saved city spawn world supplies the clock.

## Consumption, consent and recovery guards

The consumer must be authenticated, alive, not downed, on foot and the owner of an unused serial. Creative mode, swimming, sleeping, invalid items and receipt exhaustion are refused. After all event listeners run, the adapter rechecks final event cancellation and substitution and verifies that the exact token no longer exists anywhere in the player's inventory. A cancelled event or an item moved to another slot cannot produce a positive reading.

The persistent consumed-token snapshot is separate from the vanilla player record. Unacknowledged health loss remains an obligation after a logout or downed transition. The next eligible authenticated session applies it once, saving health and its applied-token receipts together in the existing vanilla player record. Malformed or wrong-type receipt markers fail closed. Receipt replay cannot grant another item or repeatedly damage the player. The bounded store retains up to 512 consumption receipts per player and 2048 player records; it does not silently evict old replay protection.

Testing another player requires an explicit short-lived confirmation bound to both current session nonces and the same actual bench. Both players must still be alive, authenticated, within four blocks, visible and allowed throughout their current property corridor. Moving away, changing session, losing the bench or declining consent prevents the reading.

Snapshot commits and `Player.saveData()` are ordinary server persistence mechanisms. They are not claimed to form a hard-power-loss atomic transaction across the consumed snapshot, the financial outbox and vanilla player files. A failed checkpoint retains the relevant record and stops new consumption rather than erasing obligations or inventing a refund.

## Validation

The Java25 domain suite covers phase ordering, complete-body stop lines, reverse approaches, braking and clearing, ownership and overlapping commissioning, persistent/replayed consumption, the seven-day rule, completed-day abstinence, exposure bounds and clock rewind. The full integration build includes these cases.

The isolated `GTMStreetSystemsProbe` separately exercises actual Paper geometry, lever output, NPC driving and waits, ordinary paid-item delivery, real Paper consumption, effects, receipt-linked readings, consent, cancelled/substituted event regressions, malformed harm markers and real health attributes. Its setup grants, temporary counter/configuration, inventory samples, positions and separate synthetic multi-day rule clock are explicitly test scaffolding. The probe never advances the world clock to simulate a drink's personal recovery. Its test JAR must not be included in the laptop ZIP.

Native Java and Bedrock rendering, client animation, accessibility and human controls still require genuine client acceptance. A translated protocol client downloading a pack does not establish those visual results.

## Recorded actual-server acceptance

The traffic scenario passed **12 checks** on core SHA-256 `30b161ad40bd20d490748d29149f617369de95d1c819d729510a7e659fe7905f`. It observed real phase/lever changes, an actual redstone event, an NPC-driven auto stopping at the red line, waiting beyond the ordinary obstruction timeout, and arriving after green. The fictional-drink scenario passed **18 checks** on the same core: an ordinary paid purchase, one real Paper item-consumption event, actual negative effects and consumption-linked exposure, consent, cancellation/substitution/replay guards, and the real health-attribute rules under its declared isolated rule-clock fixture. Both scenarios restored their inspected temporary fixtures with no unexecuted steps. Their raw reports are [traffic](reports/PAPER_TRAFFIC_SIGNALS_R4.json) and [fictional consumption](reports/PAPER_FICTIONAL_ALCOHOL_R4.json). These are server mechanics results, with test setup and injected interactions disclosed in each report.
