# Native phone, HUD and image-sign runtime

This increment connects the existing 24 phone icons, 33 HUD assets and 120 bilingual sign designs to authenticated server workflows. It is part of `1.0.3-r4-functional-candidate`. Source compilation, domain tests and resource-pack graph checks are distinct from an actual Paper player test and from native Java/Bedrock visual qualification. The isolated server companion records its own results separately.

The artwork remains `INDRAPRASTHA_128_V1`: square masters are unchanged native 128×128 PNGs; each original wide sign is 256×128, composed of two explicit 128×128 tiles. Inventory thumbnails, equipment UV exports, world-display coordinate adapters and articulated transport parts are compatibility derivatives, not new original designs.

## Phone entry and actions

The existing phone item and `/phone` fallback route through `GtmPhoneApps.open(Player)`. Swapping hands while holding the phone provides another native control. The home inventory shows all 24 exact app identities; clicks carry server-held actions, not transferable item vouchers. Every callback checks the same authenticated connection, current permission and the backend gate again before opening a service. Inventory drag, shift-click and replayed clicks cannot take menu items or repeat a purchase.

| Original icon ID | Action supplied by the runtime |
|---|---|
| `app_quoggle` | Search the actual commissioned destination registry; select a real venue as a GPS target. |
| `app_amazzo` | Open the real equipment, furniture, sign or wardrobe catalogue. |
| `app_flippit` | Open owned furnishings, sign management and home shopping. |
| `app_arkpay` | Select an authenticated online recipient and use the core's PIN-protected account transfer flow. |
| `app_zomatoo` | Open the Zomatoo ordering/collection backend. |
| `app_swiffy` | Open the Swiffy ordering/collection backend. |
| `app_fashion` | Open the owned wardrobe purchase/equip/remove backend. |
| `app_property` | Open actual property purchase, ownership and key controls. |
| `app_car_app` | Show current vehicle telemetry, real vehicle controls, navigation, local music, verified news and actual service callbacks. |
| `app_maps` | Select a commissioned destination; give or refresh a reusable live terrain map. |
| `app_garage` | Open the owned vehicle garage. |
| `app_bank` | Open actual deposit, withdrawal and PIN controls. |
| `app_loans` | Open the existing lending and repayment backend. |
| `app_taxi` | Resolve the current taxi backend gate. An uncommissioned NPC route is explicitly unavailable; teleporting is not substituted for a driven trip. |
| `app_transport` | Open the current commissioned transport service. Owning a rail model alone does not establish a passenger timetable. |
| `app_news` | Read trusted recorded game events and current backend bulletins. Private account notices are filtered by UUID. |
| `app_police` | Open actual wanted-status and lawful-surrender controls. |
| `app_medical` | Open game health, treatment and hospital-navigation services. |
| `app_events` | Read the active festival/calendar state and available authorized controls. |
| `app_missions` | Open the actual mission backend; existing campaign counts remain unchanged. |
| `app_careers` | Open registered job and duty workflows. |
| `app_contacts` | Save/remove private UUID contacts selected from authenticated online players. A changed display name cannot transfer a contact's identity. |
| `app_keys` | Open actual owned-property and vehicle-key workflows. |
| `app_settings` | Persist map layout, rotation, zoom, status HUD, instrument style, reduced effects and original-music volume. |

The service provider is `GtmCityServices`; an unavailable flag, permission, commissioned site or vehicle mode remains a precise gate. A gate is not counted as completion of the gated service. Internal `openPage(Player,String)` accepts only maps, news, contacts and directory; other values return home.

Traffic now reports the model, movement mode and accepted speed of nearby accessible active vehicles; it omits owner identities, fuel and damage state. Commissioned taxi endpoints join the real destination registry. Their surveyed path appears only near its actual pickup and only while every supplied point is loaded and accessible. The calendar publishes committed festival changes as public news, while taxi receipts remain private. Retrying an identical notice after restart preserves its first publication timestamp and does not write a duplicate; changing its audience or content is rejected.

The music catalogue contains three original note-block compositions: Sea Link Evening, Monsoon Steps and Market Morning. Players can search their names, play them locally, save a private playlist, change volume and stop playback. Playback is connection-bound and ends on logout. No external music service, streaming subscription, unofficial endpoint or JioSaavn integration is claimed.

The requested external music integration was checked against [JioSaavn's official Terms of Use](https://corporate.saavn.com/terms/) on 24 November 2026. The provider requires its supplied interface or a separate agreement and excludes unofficial automated access. The project has no provider-authorized integration agreement, credentials or streaming contract. An unofficial scraping wrapper therefore cannot satisfy this requirement. An approved provider interface and playback rights remain concrete missing inputs; this finding does not assert that a partner API cannot exist. The original local tracks continue to work without those inputs.

## Terrain and HUD

`GtmPhoneHud` renders the current world's already-loaded terrain into a contextual 128×128 map. Sampling is bounded globally to 128 new terrain lookups per five ticks, divided between players with a rotating sample cursor. An 8,192-cell cache expires old terrain; this renderer does not request new chunks. Unknown terrain remains visibly unknown. The circle/rectangle preference, rotation and zoom change the actual projection. Health and armor use current player values.

Registered police, medical, fuel, shop, property, station and mission destinations use their exact native marker assets. A backend may supply surveyed route points; otherwise the map explicitly labels the dotted line as a **bearing**, not a certified road route. No fallback coordinates are invented.

| Native HUD assets | Runtime use |
|---|---|
| `wanted_star_empty`, `wanted_star_filled`, `health`, `armour`, `ark_symbol` | Current wanted, health, armor and wallet status. |
| `fuel`, `battery`, `engine_condition`, `low_fuel`, `critical_damage` | Actual authenticated rider telemetry and threshold warnings. |
| `speedometer_analog`, `speedometer_digital`, `speedometer_compact` | Saved instrument choice with current accepted movement speed. |
| `minimap_circle`, `minimap_rectangle`, `player_arrow`, `gps_route` | Actual map layout, heading and navigation controls. |
| `map_police`, `map_hospital`, `map_fuel`, `map_shop`, `map_property`, `map_station`, `map_mission` | Real registered venue markers. |
| `phone_shortcut`, `notification_frame` | Phone navigation and contextual status messages. |
| `dialogue_bubble` | Private connection-bound dialogue display, with ordinary text fallback. |
| `wasted_title`, `busted_title`, `city_enter`, `city_exit` | Core cinematic hooks and actual city-boundary transitions. |
| `hotbar_frame`, `hotbar_selected` | A live view of all nine actual hotbar slots, direct selection and selected-slot advance, with real held-item events and item conservation. A relocated top-left hotbar remains a separate layout target. |

The Java pack has two bitmap font providers backed by the exact native PNGs. Glyphs are used only when the backend identifies a compatible Java client with the loaded pack; other clients receive real text values. This is not a claim that Java shaders or Bedrock custom HUD positioning have been qualified. The minimap is a held vanilla map, not a permanently anchored lower-left screen widget. The three speedometer artworks now drive reusable native128 live instrument maps, including an analog needle that follows accepted vehicle speed. See [the current controls and24-check server result](PHONE_CONTROLS_R4.md). Fixed corner positioning remains an open master-spec layout requirement.

## Owned image signs

`GtmSigns` loads all six authored categories: 20 transport, 20 road, 15 civic, 25 store, 25 commercial and 15 public-safety designs. The catalogue preserves the exact IDs and English/Marathi labels. A player can create an owned display within the configured quota, choose a real two-block wall, place it, change its interaction, schedule artwork, upload an authorized image, restore its original art and remove it without deleting wall blocks.

Placement uses two protected vanilla item frames with two 128×128 maps. This path is independent of the optional Geyser ItemDisplay extension. Both wall tiles and their front space must be loaded, visible, close enough, plain solid blocks, and entirely within the owner's permitted property or an explicitly authorized staging area. Storage/block entities cannot become wall backing. The complete footprint is reserved, including tiles crossing chunk boundaries. The server checks ownership, permission, line of sight and property access again when a display is used or edited.

Frame break/damage, wall break/place, liquids, fire, explosions and pistons are guarded. A lost property grant suspends the image and stops reserving the former owner's wall. The old owner may remove the suspended entitlement's placement without modifying the new owner's blocks. Only bounded nearby displays activate. Unloaded walls and invalid backing suspend admission. A persistence failure pauses new admissions until repair/restart, avoiding an endless creation of map IDs against a broken snapshot.

Each display supports an explicit link:

- Posted information reads the actual bilingual design. A road-safety label alone does not create a speed limit, toll, towing area or enforcement zone.
- A destination link resolves an existing commissioned venue at use time and sets a real GPS target.
- A service link opens the actual available backend, with the viewer's own authentication and permissions.
- A news link alternates original art with recorded **public** game headlines. Personal account notices and private contacts never become public billboards.

Owners can select up to eight existing artworks in the same category, choose a real 30/60/120/300-second interval and choose all-day, daytime or overnight UTC windows. Outside a cycling window the original design is shown. Scheduled rendering does not claim a world festival scheduler or a live station timetable that has not been commissioned.

The optional upload dashboard starts only when enabled and opened by an authorized owner. It binds to `127.0.0.1`, validates the exact Host/Origin, and uses one-use five-minute capabilities tied to the actual authenticated connection and owned sign. Two bounded workers accept only PNG bytes up to 256 KiB, reject dimensions other than 256×128 before pixel decoding, strip metadata by canonical re-encoding and reject wholly transparent files. Filenames are content hashes under the owner UUID, with a 32-image quota and symlink checks. Ownership, wall access and session are checked again on the server thread before saving. HTTP acceptance reports validation/submission; the in-game message confirms the actual saved result. No external URL fetch is offered. Nearby players can see an uploaded image once it is displayed in the world.

Vanilla maps quantize colors to Minecraft's map palette. Exact source masters are preserved, but actual frame orientation, color conversion, bilingual readability and Java/Bedrock viewing still require native-client inspection.

## Furniture menu additions

The existing owned-furniture menu now uses `GtmFurniture.actionLabel` and the expanded catalogue. Real smoker/furnace/brewing and other workstation actions retain their actual backing requirements. Cauldrons, power switches and bridge trapdoors have explicit binding instructions. The menu delegates every placement, use and setting change to the furniture module's existing owner, reach, backing, collision and property checks.

Placed lights expose saved brightness; displays accept bounded plain Unicode text; clocks expose 12/24-hour format and an exact world-time alarm; music furniture exposes the original tune and volume controls. Paper shredders use a separate permanent-deletion confirmation explaining that eligible plain paper/books, including written pages, are deleted. Native model items and unrelated contents remain protected by the backend. Text input expires after 30 seconds, is connection-bound and never becomes a command.

## Historical integration checkpoint and current evidence

The isolated exact Paper 26.3 build255 / Java25 compilation passed. The focused domain run passed **33 tests, zero failures, errors or skips**: 14 phone/projection/catalogue, 12 sign-store/catalogue, five PNG boundary/storage and two furniture-input cases. These tests cover wrong-owner mutation, retained private audience, same-payload receipt replay after restart, changed-payload rejection, saved preferences/playlists, failed compare-and-swap publication, cross-chunk wall quota, map-ID uniqueness, midnight schedule behavior, exact semi-transparent pixel preservation, bad image dimensions/formats, tampering, upload quota and symlink redirection.

At this historical checkpoint, the merged pack graph resolved 3,523 definition IDs plus 21 existing legacy selectors. It retains 1,073 original model pairs and all 1,759 protected active Java resources. Added runtime bindings are 177 UI/signs, 400 bindings for 100 outfit designs and 1,263 articulated transport partitions. Food/equipment components cover 30 foods, 113 held equipment designs, 20 protection entries and 300 native finishes; five Java vest equipment assets are present. The display extension helper supplies 1,903 separate world-display mappings while preserving original held geometry. See `build/runtime-packs-functional-shortpaths/runtime-pack-validation.json` and `gtm_display_mappings.json` for complete identities and hashes.

Actual Geyser pack loading exposed 53 technical paths of at least 80 characters. The rebuilt Bedrock pack uses shorter `rt` and `rd` folders, with a longest path of 72 UTF-8 bytes. All 4,429 renamed payloads and every PNG remain byte-identical; only the manifest's derived version changes. Item/geometry identities, both mapping files, the Java pack and the runtime catalogue remain byte-identical. A new build gate rejects any future path of 80 bytes or longer, and the focused pack suite passes 14 tests. The next actual Geyser load remains a separate check from this static correction.

The focused pack suite is recorded in the accompanying evidence file. The separate actual-Paper probe companion has compiled against build255 under the isolated integration workspace; its execution results must be read independently. At this checkpoint no native Java/Bedrock image inspection, fully relocated HUD, external music provider, comprehensive multiplayer performance test or complete master game is claimed. No production world, Daytona service or publication was changed by this module work.

The later specialist pack adds one technical lifebuoy selector, giving3,524 definition bindings and1,904 world-display mappings without adding a canonical design. Current pack hashes and actual Geyser initialization belong to the final functional evidence; the older short-path correction above remains provenance.
