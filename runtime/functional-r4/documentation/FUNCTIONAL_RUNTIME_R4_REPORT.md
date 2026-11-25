# GTM 128 — functional asset gameplay build

The laptop build connects the generated native 128 assets to actual game rules and supplies a local workshop and transport depot for using them. The exact functionality inventory contains **1,155 canonical asset IDs**, including the original **509 primary designs**. All 1,155 are enabled by the explicit public local-playtest profile; each row retains its ownership, supply, backing, route and permission requirements. Technical render parts, aliases, damage variants and platform exports are excluded from that design count.

This is a playable local asset gameplay increment. The wider 51-section campaign, city-government and production specification remains tracked separately in [the acceptance matrix](PLAYABLE_R4_ACCEPTANCE.md). Native Java/Bedrock presentation and Windows execution have not been observed in this environment.

## Exact delivered inputs

| Input | Identity |
|---|---|
| Core | `1.0.3-r4-functional-candidate`; Java 25; Paper 26.3 build 255 |
| Core SHA-256 | `b7c76cd3a664e1bb7e1e56fd2098f7ef0a71e921d47170ed10c4e658974715af` |
| Frozen source SHA-256 | `8df6f572928534b3e857dde033acb0a5b0afe3680817950505d23e34b9fc3e06` |
| Java pack SHA-256 | `5b5e132a2c670b07e8c0c389e086bd2dee1002ed7de72a6bdcd93acc6d6cba9a` |
| Bedrock pack SHA-256 | `d02cc8f41f6f97799dedab824b6fd23049c01556475e0031a50824543b507aab` |
| Public city | Sanitized snapshot dated 23 November 2026; SHA-256 `214a00a08acdb5f73fea52ef79cdfdf773551086d31f5f95725f559ad0802dc2` |
| Art contract | `INDRAPRASTHA_128_V1`; native 128 masters and original UVs/pixels retained |
| Runtime catalogue | 3,554 bindings, including 1,294 technical parts; these are not additional unique designs |

The package is assembled afresh from the public city and pinned dependencies. Played QA worlds, synthetic credentials, test companions and the private live Daytona world are not distribution inputs. The existing owner EULA file is retained unchanged; no new acceptance is invented. The launcher integrity manifest records the actual immutable JAR and pack bytes. The download receipt records the finished ZIP and its separate final launcher smoke result.

## What the assets actually do

| Canonical category | Count | Supplied gameplay role |
|---|---:|---|
| Vehicles |87|Owned deployment, seats, accepted movement, collision, energy, servicing and safe exits across road, water, air, rail and ropeway/support profiles. Traditional, electric and cargo auto-rickshaws are included. Rail/cable and managed taxi/courier trips require real commissioned routes.|
| Furniture and placeable extensions |358|Owned placement and retrieval; seating, actual-backed storage/sleep/processing, lights, books/food use, services and the specialist actions below. Capacity and prerequisites remain explicit per model.|
| Equipment after overlap removal |103|Supported held/worn tools, protection, ranged/melee actions, finite supplies and existing service operations. Registry memberships overlap30 placeable IDs and do not add duplicate designs.|
| Food |30|Finite paid stock, real preparation, local collection or commissioned courier delivery, actual consumption and nutrition.|
| Signs |120|Owned persistent two-tile map signs, selected original designs, schedules, information/service links and authorized local image uploads. Posted text alone does not create enforcement.|
| UI assets |57|24 phone app actions plus actual status, hotbar selection, terrain map and vehicle dashboard controls. Map rasters use128 pixels; the vanilla client retains its own screen layout.|
| Outfits |100|Paid wardrobe ownership, actual cosmetic equipment slots, selection/reapplication and removal without replacing unrelated gear.|
| Weapon finishes |300|Paid appearance changes on their exact compatible weapons while preserving source identity, ammunition and gameplay.|

The furniture work includes supplied fire/water/air/treatment utilities; finite linked power; an owned moving wheelchair; consented stretcher and lifebuoy transport; crane/jack cargo custody; security map views and consented fictional identity records; actual traffic phases; receipt-backed entrance scanning; retail item sensing; timed leases for real vehicle bays; supplied vehicle maintenance and lifting; a borrowed shopping-cart component; nine pushable festival carts; paid festival food counters; actual game-time/weather readouts; and emitted LIGHT control.

The 27 revised structure blueprints use authored solid parts with walk-through openings. Large festival gateways, arches and bandstands use the intended authored dimensions. A bandstand needs an existing compatible real floor; it does not manufacture support blocks. The surveyed depot guide explains the raised backing and normal stairs needed there. New saves write FUR3 while reading FUR1/FUR2. An old miniature structure remains owned and suspended until its owner deliberately removes and places it again; simply loading a save does not enlarge overlapping objects or rewrite the file.

The inventory explicitly classifies **52 ornamental furniture placements**. Plants, banners, garlands and similar artwork serve a visual placement role. The ceremony lectern has no live microphone, the low shelter umbrella does not shield precipitation, and the chai-shelter artwork does not dispense food. A model name is not used as evidence of an unimplemented operation. Other exact limits include one owning occupant per ordinary seat, one real bed per sleeping binding, no automatic refrigeration, and no commercial audio/video streaming. See [the inventory guide](FUNCTIONALITY_INVENTORY_R4.md) and its complete [CSV](reports/PRIMARY_MODEL_FUNCTIONALITY_R4.csv) and [JSON](reports/PRIMARY_MODEL_FUNCTIONALITY_R4.json).

## Executed validation

The coherent source build passed **644 JUnit tests in 79 suites**, with zero failures, errors or skipped tests, plus the existing **155 domain assertions**. The exact [build log](reports/FUNCTIONAL_FINAL_BUILD.log) and [source digest](reports/FUNCTIONAL_SOURCE_DIGEST.json) are included. Native pack validation passed 14 merged-pack tests and 10 furniture/structure overlay tests; all 12,170 Bedrock archive entries remain below the 80-byte path limit, with a maximum of 72 bytes. Original painted pixels, UVs and canonical identities were preserved.

The reports below are actual Paper 26.3 scenarios with normally authenticated protocol actors. Their scopes include real inventory contents, receipts, world blocks, emitted light, accepted movement and restart behavior. Some companions explicitly inject menu/input events or stage an inspected fixture; received network input and walking are identified separately. Exact tested binary/configuration hashes remain attached to each report. Earlier passing reports are not relabeled as tests of the final binary.

| Executed area | Passing records | Tested core | Verified scope |
|---|---:|---|---|
|[UI, signs and shared furniture](reports/PAPER_UI_FURNITURE_R4.json)|26|`b7c76cd3`|Real frame/map items, paid actions, placement, storage, seating, processing and safe removal.|
|[Equipment and appearance actions](reports/PAPER_EQUIPMENT_R4.json)|24|`b7c76cd3`|Held/worn operation, protection, finite supplies and compatible appearance effects.|
|[Food and physical courier](reports/PAPER_FOOD_COURIER_R4.json)|28|`b19aeb13`|Paid stock, preparation, real vehicle delivery and consumption.|
|[Six transport modes](reports/PAPER_TRANSPORT_R4.json)|31|`b19aeb13`|Accepted motion, energy, seats, collision, articulated parts and route restrictions.|
|[Furniture power](reports/PAPER_FURNITURE_POWER_R4.json)|16|`b7c76cd3`|Finite supplied energy and linked native light outputs.|
|[Furniture utilities](reports/PAPER_FURNITURE_UTILITIES_R4.json)|27|`b7c76cd3`|Actual supplies, native world effects and current access checks.|
|[Ottoman storage](reports/PAPER_OTTOMAN_STORAGE_R4.json)|11|`b7c76cd3`|Optional real storage backing, actual contents, permission withdrawal/recovery and seating.|
|[Medical recovery](reports/PAPER_MEDICAL_R4.json)|21|`30b161ad`|Two authenticated accounts, authorized defibrillator revival, saved downed episodes and safe recovery.|
|[Rescue furniture](reports/PAPER_FURNITURE_RESCUE_R4.json)|32|`30b161ad`|Consented physical stretcher/lifebuoy transport, shore release and bed use.|
|[Furniture cargo](reports/PAPER_FURNITURE_CARGO_R4.json)|26|`b7c76cd3`|Exclusive real-item custody, physical movement, delivery/recovery and replay refusal.|
|[Civic furniture](reports/PAPER_FURNITURE_CIVIC_R4.json)|30|`04a89901`|Bounded camera/map, booking and fictional record services.|
|[Traffic signals](reports/PAPER_TRAFFIC_SIGNALS_R4.json)|12|`30b161ad`|Real junction phases and shared movement stop rules.|
|[Fictional drinks](reports/PAPER_FICTIONAL_ALCOHOL_R4.json)|18|`30b161ad`|Paid consumption, game exposure effects and personal recovery.|
|[Phone controls](reports/PAPER_PHONE_CONTROLS_R4.json)|24|`0b49d8e4`|Saved map/layout choices, actual hotbar selection and moving vehicle telemetry.|
|[Entrance, retail and parking](reports/PAPER_FURNITURE_ACCESS_R4.json)|29|`f66438dc`|Paid single-use tickets, actual barriers, carried-stock alarm and real timed parking expiry.|
|[Vehicle workshop](reports/PAPER_FURNITURE_WORKSHOP_R4.json)|28|`b7c76cd3`|Six supplied service models, real condition changes, held-load recovery and lift release; cleanup applies to its workshop only.|
|[Paid shopping-cart final return](reports/PAPER_SHOPPING_CART_R4.json)|4|`b7c76cd3`|Final continuation of the retained six-stage paid chain, with one original item and closed replay records.|
|[Nine paid festival carts](reports/PAPER_FESTIVAL_CARTS_R4.json)|129|`b7c76cd3`|Nine ordinary purchases, physical push/turn/park/remove and original paid-item transfer.|
|[Festival clocks, food and lights](reports/PAPER_FESTIVAL_FUNCTIONS_R4.json)|85|`b7c76cd3`|Actual game time/weather, nine paid prepared orders, emitted LIGHT and complete fixture restoration.|
|[Walk-through structures](reports/PAPER_FURNITURE_STRUCTURES_R4.json)|38|`b7c76cd3`|Authored geometry, real floor backing and seven received protocol walks through openings/on the stage.|

The ordinary paid local profile separately passed 24 checks. Its wheelchair passed 22 movement checks plus six received-protocol checks on the same paid chair. The paid depot retained its first 65 passing checks and one protocol-harness failure; the corrected 20-check continuation completed on the same purchases, vehicles and balance. The original account and purchases then passed ten checks through the unmodified packaged launcher after a restart. These histories are preserved in the [profile](LOCAL_PLAYTEST_PROFILE.md), [wheelchair](WHEELCHAIR_MOBILITY_R4.md) and [depot](LAPTOP_DEPOT_ACCEPTANCE_R4.md) evidence.

The cart evidence preserves each actual attempt and continuation. One production defect involved byte-order-sensitive item serialization after a real destination write. The correction compares complete typed native item data, ignoring only compound key order and gzip representation. Ordinary Verify acknowledged the existing output without creating another item. Subsequent physical return and ordinary near-nest closure retained the original entitlement, completed receipt and exact paid item. Fixture-path and observer-goal corrections are identified separately from production changes.

Workshop testing also exposed two recovery defects: whole-envelope collision incorrectly blocked an otherwise clear lift bay, and repeated blocked vehicle admissions could starve a later saved vehicle. The production fixes use precise frame/arm clearance and a bounded rotating admission cursor. The same ownership, authenticated-session, full-geometry and collision rules remain. Final workshop evidence includes logout/reauthentication, suspended held-load recovery, real bounded lowering and boarding after release.

The final resource audit also found and repaired 27 missing Bedrock display-bridge targets for the structural projections. The complete bridge now contains 1,934 world-display bindings, including those 27 selectors, while retaining the original native 128 pixels, UVs and ordinary item identities. The separate [binding report](reports/STRUCTURE_DISPLAY_BINDINGS_R4.json) records the regression and exact revised pack hashes.

The final shared checks include a corrected 11-record ottoman test. The earlier test attempted another interaction in the same tick that it restored permission, before the normal projection reconciliation. The corrected companion observes withdrawal during denial, waits normal server ticks after restoring the existing permission, then verifies the same furniture identity, storage and seating. The production core was unchanged. Both snapshots of the earlier failed test remain preserved as one attempt.

The launcher's [Java-only mode](LAUNCHER_JAVA_ONLY_R4.md) now excludes the two exact optional crossplay JARs before Paper scans plugins and restores their original bytes after shutdown. Merely setting a negative Bedrock port occurred after Geyser discovery initialization, so that old setting was insufficient. The new reversible journal preserves configuration, keys, identities and world/account data. Its 18 dedicated filesystem/process checks passed; the full packaging gate passed 35 of 38 cases, with 3 private-IPv4 cases explicitly skipped.

Launcher/profile fixtures distinguish executed Linux/JVM checks from unavailable private-network conditions. The exact finished archive is checked with the released launcher and a fresh normal account in a separate post-archive smoke run; that run's report and ZIP checksum belong to the accompanying receipt. A Java-only run does not qualify a native Bedrock connection.

## Starting the local game

Extract the entire ZIP to a writable folder. On Windows, run **Start-GTM-Java-Only.bat** for local Java play; the package includes the Windows Java 25 runtime. Join with your installed matching Java client at **127.0.0.1:25565**, accept the bundled resource pack, and follow the normal register/login prompt. First Paper boot may require internet access for official Minecraft libraries. The Minecraft client itself is not included.

Use `/phone`, `/car`, `/car shop`, `/gtmproperty`, `/furniture`, `/gtmsigns`, `/equipment` and `/wardrobe`. The normal new account receives its starter auto and 1000ARK. In this explicit local profile, most furniture/vehicles cost 1 ARK, the magazine rack costs 125 ARK and the wheelchair 75 ARK. The three paid properties cost 100 ARK, 100 ARK and 25 ARK. Purchases, supplies, collision, current access and vehicle energy remain active rules. Follow **LOCAL_PLAYTEST_README.txt** for exact sites, compatible backing blocks and route commissioning. Enter `stop` in the server console before closing it.

The regular Start-GTM launcher also configures the included Geyser transport on a current private IPv4 interface. Follow the printed address and [network guide](LAPTOP_BEDROCK_NETWORK_R4.md); native Bedrock authentication, rendering and human controls remain unverified. No external AI or paid service is required for these local functions.

## Practical boundaries

The public 23 November city is not a fresh export of private Daytona progress. The protected live server was not restarted, resized or overwritten. This release does not claim the full 30-main/50-side mission campaign, the complete 46-facility city renovation, broad population simulation or government/control-dashboard systems in the original matrix. It also does not claim native Java/Bedrock visual acceptance, Windows execution, multiplayer load certification or arbitrary-power-loss atomicity across separate game save files.

Those limits are distinct from the supplied asset actions and the executable local package. Keep the included reports with their exact hashes, and preserve the whole stopped world/account/transaction set when backing up your own play.
