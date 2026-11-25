# Approved HUD, NPC and passenger recovery — 25 November 2026

## What was wrong

The earlier 1.0.4 repair corrected broken resource references and added an inventory phone skin, but it did not implement the approved HUD. A dark inventory window, sidebar and generated preview were not substitutes for the requested top-left inventory, bottom-left map, top-right wanted/cash/bank and bottom-right clickable phone. This record supersedes that UI acceptance claim. The [1.0.4 report](RUNTIME_REPAIR_2026-11-25.md) remains historical evidence for its exact bytes.

The user also identified incorrect auto capacity and NPCs that crowded the world without conversation or defensive behavior. Inspection found concrete causes: a dialogue flag and permission that ordinary players could not use; an ambient greeting path disconnected from conversational UI; no Paper navigation fallback without Citizens; population caps applied only to one roster mode; missing persistent ownership/reconciliation; and weapon target gates treating Citizens player-shaped NPCs as unauthenticated real players.

This candidate implements the requested Java HUD and repairs those runtime paths. It does not certify the complete Revision 4 city, every vehicle interior, Bedrock HUD, or a connected generative model.

## Four-corner Java HUD

The implementation is in [client-hud](../client-hud/README.md), with the authenticated bridge in [GtmClientHud.java](../hotfix/src/main/java/com/sdcraft/core/GtmClientHud.java).

| Requested behavior | Implementation and practical limit |
| --- | --- |
| Top-left inventory | Nine actual hotbar items, counts, selected slot and held-item behavior. The full carried inventory remains accessible normally. |
| Bottom-left map | Loaded-terrain minimap with circle/rectangle modes and available commissioned-service markers. It is not a fabricated map image or an unexplored-world oracle. |
| Top-right stars and money | Server wanted level, wallet and bank. Client-supplied numbers have no financial authority. |
| Lower-right phone | Persistent shortcut and a non-pausing popup. `/phone` and real phone-item use route to that popup when the client component is active. |
| Original app logos | The earlier colourful brand PNGs are copied byte-for-byte. Existing native128 HUD and service art is retained. No replacement logos were generated. |
| App actions | Existing app registry, access gates and service routes. Detailed transactional screens can hand off to the existing server inventory UI. |
| Vehicle instruments | Real driving speed, reverse state, energy/body and occupied-seat data, when supplied by the active vehicle. |

The project specification retains **no mandatory client mods**. Ordinary Java access is preserved. The exact movable hotbar, terrain map and clickable overlay use an **optional Fabric client**; a vanilla Java resource pack does not provide that arbitrary input/rendering capability. This is an explicit platform distinction. The component targets the actual Minecraft 26.3 client, Java 25, Loader 0.20.1 and API 0.167.0+26.3. Its build downloads pinned official inputs and never redistributes Minecraft binaries. See the [Fabric HUD API](https://docs.fabricmc.net/develop/rendering/hud).

### Session and action boundaries

The bridge uses `gtm:hud_hello`, `gtm:hud_state` and `gtm:hud_action` with bounded UTF-8 JSON. A capability hello is not authentication. Active state requires the current authenticated login, phone access, successful pack load, enabled HUD preference and a player who is not downed. State expires on the client; logout, disconnect and session changes clear it. App actions require the current session, monotonically increasing sequence, rate limit and a known enabled app. Arbitrary command strings are never accepted. A delayed provider response likewise cannot speak to a different login or a different selected NPC.

## NPC conversation, population and combat

The maintained [NPC repair record](../hotfix/NPC_REPAIR.md) describes the recovered adapter and exact target-gate patch. Named identities, roster records and service protections are retained.

- Right-click selects a real nearby NPC. `// ` followed by text uses the selected NPC, with distance, line-of-sight, identity, authentication and expiry checks. Sneak-right-click permits conversation without opening a staff service menu.
- Responses appear in chat and temporary overhead text. Bubbles are bounded, nonpersistent, cleaned up and maintained by one task. Proximity greetings have per-player/per-NPC cooldowns.
- A hard maximum of 32 physical NPC/service actors and four admissions per reconciliation applies in both 100- and 500-identity modes. The roster is not a promise to render 500 mobs simultaneously. Loaded chunks, separation, chunk budgets and activation hysteresis reduce crowding without rewriting identity anchors.
- Owned entities have explicit identity/schema tags and a private live identity index. Chunk/restart reconciliation can adopt or reject duplicate owned materializations. Untagged old mobs are not deleted from names alone; an occupied legacy anchor is deferred for owner review.
- Citizens remains supported. Without Citizens, Paper mobs now receive real pathfinding requests. Ordinary ambient pedestrians flee when attacked; the existing designated tough subset can chase and retaliate. Service NPCs remain protected. Melee respects visibility, cooldowns, authentication and safe areas.
- Native and legacy weapons can target strictly owned attackable NPCs. The preserved native equipment class receives exactly two hash-checked target-authentication substitutions; shooter checks and the real-player tag minigame gate remain.

### Generative provider status

**No live language model is configured or certified by this package.** The default is an explicit local scripted fallback. The new backend supports existing local Ollama and HTTPS OpenAI-compatible chat endpoints. It uses two workers, a bounded queue, one pending request per player, short conversation history, response size/time limits, session cancellation and visible fallback reasons. The provider produces text only; it has no game-command, item or finance API. Local wire fixtures verify its protocol and failure behavior; they are not proof that a language model ran.

For an existing local Ollama installation with a model already available, the server owner can select it in the retained `plugins/SDCraftCore/config.yml`:

```yaml
dialogue:
  enabled: true
  proximity-greetings: true
ai:
  provider: ollama
  local-endpoint: http://127.0.0.1:11434/api/chat
  local-model: YOUR_ALREADY_INSTALLED_MODEL
  daily-request-limit: 200
  per-player-five-minute-limit: 10
```

`YOUR_ALREADY_INSTALLED_MODEL` is a placeholder to replace with the owner's actual model name. The request uses Ollama's documented nonstreaming [chat endpoint](https://docs.ollama.com/api/chat). HTTP is accepted only for loopback; remote services require HTTPS. The limit of 200 is a process-lifetime daily counter, reset by a server restart; it is not a durable billing cap.

For an existing HTTPS provider, use `provider: openai-compatible`, `endpoint: https://YOUR_EXISTING_PROVIDER/chat-endpoint` and its valid `model`. Put `JEEVA_API_KEY=...` in the private `plugins/SDCraftCore/ai-secrets.properties` file if required. `OPENAI_API_KEY` is accepted only for the official OpenAI host. Do not commit secrets. The update neither provisions hosting nor purchases inference. Invalid configuration or an unreachable provider uses local replies with an explicit notice. `/sdc status` and the local Control Centre expose configured mode and last result without credentials.

The previous `gtm.experimental-dialogue: false` no longer silently blocks the repaired public path. `dialogue.enabled: false` remains an explicit owner control. Permission metadata now permits ordinary authenticated players by default; other authentication and proximity gates remain.

## Vehicles and driving

The traditional auto now has **four total seats: one driver and three rear passengers**. Its actual rear bench/body/canopy has been widened 0.84 blocks overall; passenger anchors, bounds and rear wheel animation pivots agree with that geometry. The retained canopy lift provides headroom. Locked vehicles still reject guests. Garage boarding selects an available passenger place when the driver's seat is occupied, rather than displacing the driver.

The patrol sedan and police SUV now expose the existing second front cushion as a passenger seat. Other 84 profiles retain their measured capacity. The [87-profile capacity audit](repair-evidence/vehicle-capacity-audit.json) and [CSV](repair-evidence/vehicle-capacity-audit.csv) identify every anchor, source mesh fingerprint and missing interior work. Thirty civilian cars currently have two authored front seat cuboids and no rear row; four buses have no authored passenger interior. Those are unfinished models, not repaired five-seat cars or functioning passenger buses.

Driving uses the maintained server-authoritative `GtmVehicles` / `RoadPhysics` kinematic model: integrated acceleration/braking, stopping before reverse, bounded bicycle-arc steering, collision-limited accepted motion, fuel, health and odometer. It is not a full suspension/tyre/rigid-body engine. The earlier flat-road acceleration/steering/braking/reverse tests are recorded in the 1.0.4 report; new multi-occupant checks are recorded separately. The [vehicle repair record](../hotfix/VEHICLE_REPAIR.md) explains exact geometry and bytecode boundaries.

## Build and verification

The original 1.0.3 core is preserved at SHA-256 `b7c76cd3a664e1bb7e1e56fd2098f7ef0a71e921d47170ed10c4e658974715af`. The maintained Java overlay plus exact vehicle/NPC target patches produce `1.0.5-r4-spec-candidate`. This is not a full rebuild of missing original source from the older `source/` tree.

Executed local checks at this checkpoint:

- Java 25 maintained server compilation and **94 JUnit tests** passed: 31 vehicle, 22 console, 18 NPC, 11 provider, five HUD session and seven native equipment/upgrade tests.
- **18 client JUnit tests** passed after correcting the shortcut conflict and minimap clipping discovered by native play.
- **826 equipment compatibility assertions**, five vehicle patch checks and the NPC two-target patch checks passed. These counts describe boundary/compatibility assertions, not hundreds of gameplay scenarios.
- **12 pack**, **nine auto geometry**, **24 updater** and **17 publication** Python tests passed.
- The actual Fabric client joined staged Paper 26.3 with an ordinary newly registered, non-op account. The four corners, live balances, real slot selection, clickable popup, original colourful logos, phone-item command routing and authorized Bank service handoff were observed. The initial pass identified shortcut/map clipping defects for correction before final evidence.

Final native acceptance, exact artifact hashes, independent CI and final screenshots are recorded below when completed. Earlier evidence is not silently relabelled as proof for this build.

## Installation, rollback and remaining work

Use [the updater guide](../packaging/repair/README.md) and [optional client instructions](../client-hud/README.md). The updater supports only the fingerprinted preserved 1.0.3 and released 1.0.4 inputs, preserves existing data/configuration, checks running-server locks, backs up every change and supports explicit rollback. It does not install client mods or update Daytona remotely.

Remaining acceptance includes native Bedrock HUD/crossplay, Citizens-present human NPC testing, an actual configured generative model, broad vehicle terrain/interior work, full police pursuit/arrest, campaign/city commissioning and Windows execution. Audio is not certified in the isolated client. The protected production server and `main` are unchanged. None of these open items is closed by a generated preview or a successful compilation.
