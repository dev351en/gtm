# Paid entrances, timed parking and retail stock sensing

## Exact models and implemented actions

The existing `gtm:ticket_validator`, `gtm:security_turnstile_rfid`, `gtm:parking_meter` and `gtm:retail_security_gate` keep their IDs, authored geometry and native 128-pixel artwork. They now have distinct controls in `GtmFurnitureAccessServices`. FUR1/FUR2 ownership records and existing binding kinds are unchanged.

| Model | Required setup | Actual effect |
|---|---|---|
| Ticket validator | Its owner links an accessible owned turnstile within eight blocks; both models and the whole supported entrance approach must be loaded and inside authorized owned property. | Takes 1 ARK from the customer's bank through the existing paid-item outbox and delivers one serial ticket. The ticket has a fixed five-minute lifetime and the exact paid buyer/link/payload must match when scanned. |
| RFID turnstile | Current commissioned validator link. The owner must remain authenticated with furniture access. | A successful scan durably consumes the serial, removes the actual ticket and opens the real barrier collision and display for three seconds. Closing waits for the original full footprint to clear. |
| Parking meter | Owner inspects a supported bay around their actual stopped empty ROAD vehicle. Another permitted customer may then use that commissioned bay for their own real vehicle. | Takes 1 ARK for a fixed three-minute lease tied to the customer, vehicle and exact bay. A real paper receipt and a native text display show the lease and remaining time. Expiry releases the bay reservation and displays EXPIRED. |
| Retail security gate | Owner explicitly commissions and arms the real passage, then tags held stock. | A permitted authenticated visitor crossing the actual sensor plane with that gate's active stock tag triggers a native sound, particles and visible alarm. Owner checkout clears only that tag from the actual held stack. |

Parking expiry does not fine, seize, move or immobilize a vehicle. A meter records paid use of its inspected bay; it does not create vehicle ownership or guarantee that an unrelated driver cannot physically enter an unenclosed space. Retail sensing does not invent theft, identity checks, fines or item ownership from a tag.

## Player controls

Use each placed model to open its specific menu. Owner setup and customer actions are visible separately. Equivalent commands are:

```text
/furniture access link <validator-id> <turnstile-id>
/furniture access ticket <validator-or-turnstile-id>
/furniture access scan <validator-or-turnstile-id>
/furniture access bay <meter-id> <owner-vehicle-id>
/furniture access park <meter-id> <customer-vehicle-id>
/furniture access recover <meter-id>
/furniture access arm <retail-gate-id>
/furniture access tag <retail-gate-id>
/furniture access clear <retail-gate-id>
/furniture access disarm <retail-gate-id>
```

The scanner requires exactly one real paid paper ticket in the main hand. A copied spent serial, a changed item, an unpaid or unacknowledged outbox record, a different buyer, an expired ticket or a changed commissioning cannot open the entrance. The receipt's display name alone never proves payment.

The parking customer must be within five visible blocks of the meter and within eight blocks of the actual projected vehicle. The vehicle must be owned by that customer, stationary below 0.05 blocks per second, empty, a ROAD model and completely inside the commissioned bay. The bay is bounded to ten by four by ten blocks and its center is within eight blocks of the meter. The whole footprint retains loaded-world, border, support, native obstruction, other-furniture, other-vehicle and property checks. No ordinary summon or vehicle transfer was added.

Retail tagging modifies the actual held stack's `retail_stock_gate` PDC field and preserves item count and unrelated metadata. A foreign or malformed existing stock tag cannot be silently overwritten or removed. Tagging and clearing require the current gate owner at the current visible installation. Alarm detection uses real walking events through the model-local plane; teleports and implausibly long movement segments do not count as a sensor crossing.

## Authorization and runtime lifecycle

Furniture mode and ordinary `gtm.furniture` permission are required. Ticket validators additionally require the `transport` furniture service category; parking meters require `parking` and the enabled native vehicle runtime. These exact mechanics do not delegate to unrelated maps, garage, repair or transit menus. The local playtest profile must explicitly enable the applicable categories.

An explicitly commissioned service permits a customer to use that service only while the full installed-owner property and the customer's current `mayEnter` checks still hold. It does not make private property public. Owner commissioning is owner-only. Each menu captures a current authenticated session and has a consumed flag; deferred execution rechecks the same session, permission, actual model, proximity, line of sight and current service availability before acting.

Gate opening is a transient override shared by actual collision and display scaling. It never writes a free opening into the saved manual furniture setting. Commissioned gates initialize closed after restart. Retail sensing requires explicit rearming after restart or owner session loss. A close that would intersect an actual entity or vehicle is deferred and retried after the footprint clears. Removing or moving a controller with an outstanding ticket/lease, a live opening or armed sensor is refused through the normal furniture mutation path.

## Durable proof and interruption limits

`furniture-access.snapshot` stores bounded commissioned links/bays and exact prepared ticket/parking intents. `furniture-retail.snapshot` stores bounded owner/pose commissioning, without an armed session. `Ledger.paidDelivery` is a read-only proof of an actual priced paid-item delivery, including customer, serial, payload, price, account source and acknowledgment. Ordinary food collection outboxes cannot masquerade as such a purchase.

The service prepares a fixed intent before the normal `GtmItemDelivery` purchase with the same serial. The existing ledger writes the debit and outbox together. A failed or ambiguous delivery leaves its original intent and expiry available for reconciliation. Reconciliation never buys another item or extends time. Only an immediate financial `false` response discards an unpaid intent; an exception does not erase uncertain proof.

For a fare scan, the durable consumed bit is committed before removing the physical ticket and before opening the gate. This ordering prevents a recovered/copied ticket from replaying an opening. It can lose the ticket's use if interruption occurs after consumption but before opening. The ledger, service snapshot and vanilla player save are separate files; Paper's `saveData` call is not a proven cross-file durable transaction or disk acknowledgment. There is no automatic speculative refund or output replay. Snapshot stale writers and malformed inputs fail closed, and a backward clock does not silently release an outstanding reservation.

## Verification status

The focused Java25 gate passed 38 cases: 28 new receipt, lease, sensor-geometry, ledger-proof and public-access-boundary checks plus ten existing delivery/utility regressions. The combined isolated source build passed 562 cases in 69 suites with zero failures, errors or skips. Its immutable artifact is `integration-probe-r4/functional-access-562`, core SHA256 `f66438dce5698f926e644cb10ed5f08cd83182b704f2d34c665a3c6b8325dd9f`.

The separate `tools/probes/furniture_access` companion passed **all 29 checks**, including cleanup, on that immutable core in the isolated Paper 26.3 build 255 copy. The [raw report](reports/PAPER_FURNITURE_ACCESS_R4.json) has SHA256 `d2a98409756d0c11ebbd752c62f459e5cef80bc0f317c62cf44f956bae0daa1e`; the [evidence manifest](reports/FURNITURE_ACCESS_R4_EVIDENCE.json) records the exact core, companion and both runtime configurations. The companion JAR has SHA256 `09ea709f36bb256489a7f9cdd1f1a19f574e99ea29dffaa936268b4eca64578f`.

The normally authenticated non-OP customer paid the actual one-ARK fare and one-ARK parking charge. The paid serial opened a real traversable entrance once, then closing restored its collider and a copied spent serial refused. Actual carried stock tags triggered the native alarm, and owner checkout cleared only that tag while preserving the item. The real three-minute parking lease was observed expired **182,448 ms after its recorded creation**, with no timestamp rewrite, extra debit, extra time, fine or vehicle movement. Permission revocation, stale menus, foreign use, remote and obstructed access, safe delayed closure, durable snapshot reopen and reserved-controller mutation refusal all passed.

The report declares its supplied QA furniture and stock, temporary forged ticket test, injected Paper menu/movement events, and reversible relocation of two existing autos. Both original vehicle poses and the inspected fixture were restored, while actual charges, the paid receipt and current vehicle conditions were retained. It grants no currency, vehicle ownership or customer permissions. The owner uses the pre-existing explicit staging exception; this scenario does not prove a furniture-shop purchase. The earlier clean refusal from an older configuration missing the `transport` and `parking` categories remains historical evidence; the unchanged companion passed after those categories were explicitly enabled. Native Java/Bedrock appearance and hard-crash recovery remain separately qualified.
