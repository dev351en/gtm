# Paid local depot — actual gameplay acceptance

The surveyed laptop depot now has actual ordinary-account acceptance for rail, water, air, ropeway, taxi and food-courier play. The checks use the original public world copy and the same normally registered, non-operator `GtmLaptopQA` account that bought the workshop, storage furniture, meal, sign and wheelchair. The server is Paper 26.3 build 255. This is server/protocol evidence; it does not certify native artwork rendering, human controls or execution on Windows.

## What passed

| Operation | Observed result |
|---|---|
| Property and vehicles | The account paid for the depot and landing claims, then bought ten original vehicle models through the paged normal catalogue and durable item/vehicle delivery path. No account, balance, ownership, permission or item grant was injected. |
| Rail | The owner surveyed the actual connected 88-rail guide, bought a driving cab and two coaches, coupled the real owned vehicles, drove the cab from received protocol input, spent energy and parked safely. |
| Ferry | The purchased ferry moved on original water from received driver input, consumed energy and allowed a safe exit onto the original shore. The owned service interface remained usable. |
| Helicopter | The purchased helicopter climbed and landed using received input, consumed energy and allowed a supported safe exit. |
| Ropeway | Two purchased terminal models defined an actual 56-block cable guide. The owner started the route, the occupied purchased cabin moved, terminal energy decreased and the passenger exited safely. |
| Taxi | The owner opted the purchased electric auto-rickshaw into service and walked a real 12-block route. A normal paid reservation assigned a managed driver, carried its actual passenger and released them at the recorded destination. |
| Courier | The owner bought the original Activa scooter, explicitly offered it for courier service and continuously walked the real 14-block delivery route. After actual food preparation, the physical NPC scooter arrived and handed over exactly one purchased consumable through the existing outbox. |
| Persistence | Paid claims, exact vehicle UUIDs, rail coupling, cable guide and account balance reopened unchanged before the fleet continuation. Normal release-launcher restart is recorded separately. |

The movement records retain every observed origin, destination, energy reading and maximum step. Examples include a 1.25-block helicopter climb followed by landing, a taxi journey of approximately 11.74 blocks with a maximum observed step of 0.1785 blocks, and a courier journey of approximately 13.58 blocks with a maximum observed step of 0.1995 blocks. The route walks produced 40 + 40 + 2 + 94 real server movement events and zero teleport events during those measured segments. Explicit test positioning was used only outside active driving and route walking.

## Honest run history

The first run passed 65 checks and stopped at the first taxi walk. The protocol test client retained a stale mounted-vehicle reference even after the server had sent its real dismount packet. The corrected client clears that stale reference only after receiving a `set_passengers` packet that excludes the player. It does not force a server exit or bypass vehicle rules.

All purchases, debits, claims and vehicle poses from that run were retained. A separate continuation first verified the archived report hash and the actual nine already-purchased vehicles, claims, rail coupling, cable guide and balance, then completed 20 checks. It bought only the remaining scooter. The original failure and both raw reports remain available; this is not represented as one fresh 83-check pass.

| Balance point | Cents |
|---|---:|
| Before depot purchases | 68,000 |
| At retained first-run boundary | 54,600 |
| After successful taxi/courier continuation | 50,428 |
| Total depot, vehicle and service debit | 17,572 |

The exact core for both runs is SHA-256 `0b49d8e47935b4693f409ad51168a4a292f54b4536dc58ce717ab0bc45209d5c`, from the coherent 522-test build. The original companion hash is `ad60e49ce866b0a7cfffe5cde05798dd5df598656903c4a0c62c8c81fed4b3aa`; the continuation companion hash is `966c9e2e1e1dfd742cfdcfcf8a45ac38000452d02d286267a7cc1c01ccfdf767`.

## Reproduction and limits

Use [LOCAL_PLAYTEST_PROFILE.md](LOCAL_PLAYTEST_PROFILE.md) for the paid parcels and surveyed facilities and [LOCAL_OWNER_TRANSPORT_R4.md](LOCAL_OWNER_TRANSPORT_R4.md) for ordinary route commands. New laptop players start with normal account funds and the ordinary starter auto; the QA account, purchases and saved routes are not included in a fresh release ZIP.

The companion invokes ordinary inventory listeners for menu clicks and uses read-only reflection for exact-state assertions. A separate translated protocol client sends actual bounded walking and driver-input packets. Resource-pack downloads are hash-verified; rendering acknowledgement is explicitly simulated because that client has no renderer. The evidence establishes these measured server actions, not native Java/Bedrock visual qualification, city-wide transport coverage or a complete campaign.

Evidence:

- [LAPTOP_DEPOT_R4_EVIDENCE.json](reports/LAPTOP_DEPOT_R4_EVIDENCE.json) — combined provenance, movement and paid continuity.
- [PAPER_LAPTOP_DEPOT_INITIAL_R4.json](reports/PAPER_LAPTOP_DEPOT_INITIAL_R4.json) — original 65 passes and retained harness failure.
- [PAPER_LAPTOP_DEPOT_FLEET_CONTINUATION_R4.json](reports/PAPER_LAPTOP_DEPOT_FLEET_CONTINUATION_R4.json) — successful 20-check continuation.
