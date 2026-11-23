# SD Craft feature matrix — 2026-11-23

This matrix describes the current isolated Paper 26.3 candidate. “Implemented”
means code and configuration exist; “runtime pending” means a real player or
host interaction is still required. No row is a promise that has not been
tested.

| Feature | Status | Evidence / limitation |
|---|---|---|
| New Blockston world | Included | Isolated world copy is packed; it is not asserted to be the newest Aternos save. |
| Paper 26.3 / Java 25 | Tested | Disposable full server reaches `Done` with 22 plugins. |
| 60 approved NPC policy choices | Included | Preserved in the user handoff and blueprint/dialogue files. |
| City population | Implemented; player test pending | 100 configured identities: 20 protected named service NPCs plus 80 generated pedestrians and merchants. |
| NPC proximity spawning | Boot tested | Citizens reflection with villager fallback; 56/80 block hysteresis; 100 anchors generated on the live Paper world copy. |
| Active NPC limits | Implemented | Maximum 6 police and 94 non-police, with offscreen abstraction and proximity despawning. |
| Ambient walking/combat/loot | Implemented; player test pending | Pedestrians wander near home anchors; about 30% retaliate, others flee, and defeated ambient NPCs yield controlled wallet/food loot with a respawn cooldown. |
| Wandering civilian traffic | Not implemented | Background civilian target remains a design requirement. |
| Police idle patrol | Partial | Up to two idle police anchors; no road patrol/pursuit AI. |
| Wallet and bank starter grant | Implemented; unit tested | One-time $500 wallet / $1,000 bank grant with atomic YAML ledger. |
| Vault economy | Startup tested | Vault reports `SD Craft Wallet`; MTVehicles reconnect is automatic. |
| Bank transfers and PIN | Implemented; player smoke pending | Ledger, confirmations, PIN hash, and audit trail exist. |
| Loans, interest, mortgages, tax | Not implemented | Policy only. |
| Robbery / bank heist | Disabled by policy | Requires verified protected zones and event-driven theft pipeline. |
| Wanted, surrender, arrest, jail, fines | Implemented; player smoke pending | GTA layer commands and persisted timers exist. |
| Police dispatch / witnesses | Partial | Human police messaging and policy checks; no full pursuit or witness intelligence. |
| Medical fees and treatment | Implemented; player smoke pending | Site-based diagnosis/treatment/admission flows. SimpleRevive owns downed state. |
| Taxi, bus, metro | Implemented as simulated transport; player smoke pending | Fare quote and verified destination teleport; no autonomous vehicle movement. |
| Physical TrainCarts rail service | Plugin boot-tested; infrastructure pending | TrainCarts 2.0.5 and BKCommonLib 2.0.6 load on Paper 26.3, report the SD Craft economy hook, and use guarded low-memory settings. No rails, stations, saved trains, or live routes have been built in the city yet. |
| Jobs, duty salary, credits, promotion approval | Implemented; player smoke pending | Duty tracking, thresholds, and human approval command are present. |
| Waypoint missions | Implemented; player smoke pending | Persisted checkpoint routes pay on verified arrival. Passenger/theft/evidence events remain partial. |
| Offline English/Hindi/Hinglish dialogue | Implemented; unit tested | Deterministic local parser and scripted fallback; external AI is off by default. |
| External AI | Disabled by default | Optional adapter requires owner-supplied secrets and provider budget controls. |
| Shop and garage basics | Implemented; player smoke pending | Phone/shop/garage flows charge the SD ledger; negotiation depth remains limited. |
| Construction / automatic repairs | Partial | Restoration engine can restore eligible damage; no full maintenance world-edit workflow. |
| PvP civic safe zones | Partial | Core safe-radius checks exist; WorldGuard regions are not yet configured. |
| Five-minute restoration | Implemented; unit tested | Damage queue, player-build exclusion, crop/underground exclusion, and yield suppression. |
| 30-minute shared service clock | Implemented in policy/config | Needs real player duty/shift smoke test. |
| BlueMap | Installed; pending owner acceptance | 5.29 loads but needs its optional client-resource download acceptance before rendering. |
| Unified city resource pack | Built and CRC tested | Local pack includes vehicle/gun assets, branding, cash, phone, tickets, and model mappings; public HTTPS hosting is pending. |
| 15-image branding bundle | Built and validated | Exactly 15 PNG files with required dimensions, alpha modes, and ZIP integrity. |
| Vehicle plugin | Startup tested | MTVehicles 2.5.9 loads with the 26.3 compatibility bridge; player driving/economy smoke is pending. |
| NPC autonomous vehicle driving | Not implemented | Do not describe simulated transport as autonomous driving. |
| Bedrock UI | Partial | CommandPanels fallback exists; Geyser/Floodgate player test is pending. |

## Release gates still open

- Confirm the GitHub raw resource-pack URL remains public and returns the ZIP
  whose SHA1 is `4633349625598AF3EFF64CAF24C74FB953BF0A4D`.
- Obtain owner approval before enabling BlueMap’s Mojang client-resource
  download acceptance.
- Perform a real player interaction pass on the packaged ZIP, including login,
  phone, economy, NPCs, missions, transport, crime, medical, and promotion.
- Keep the Aternos backup and production host untouched until final deployment
  approval and a fresh target-host backup exist.
