# SD Craft - current project status

Date: 2026-11-24  
Target: Paper 26.3 build 255, Java 25, MCServerHost 3.5 GB RAM / 10 GB disk,
approximately 3-4 players.

## Current verified artifact

[EXPECT_SDCRAFT_NPC100_2026-11-24.zip](D:\Games\SDCRAFT\EXPECT_SDCRAFT_NPC100_2026-11-24.zip)  
SHA256: `9e7abd30aa4c2821b0ab5a19bfa598a4de0849f488a84fc60fe9952f897f4d37`  
Size: 405,682,396 bytes  
Archive entries: 745

The NPC100 payload was booted in a new disposable directory with Java 25 using
the exact packaged SDCraftCore JAR hash. It reached `Done`, loaded 20 plugins,
reported `configured=100` and 100 anchors, connected the SD Craft wallet, and
stopped cleanly. The final ZIP passed CRC and content verification. Paper's
one-time world migration occurred only in that disposable copy; the canonical
world and Aternos backup were not overwritten.

## Verified implementation

- 71 SDCraftCore JUnit tests pass.
- SDCraftCore registers the Vault `SD Craft Wallet` and automatically runs
  `mtv vault setup` after startup; the smoke log confirms MTVehicles uses it.
- ProtocolLib and SimpleLogin load without the plaintext-password warning;
  SimpleLogin uses a valid one-day session.
- The original runtime and named-NPC defaults use audited walkable coordinates.
- The dense-city update configures 100 NPC identities: 20 protected service
  characters plus 80 proximity-managed pedestrians and merchants. Ambient
  characters wander; about 30% retaliate, others flee, and defeated ambient
  NPCs provide controlled loot with a respawn cooldown.
- GTA layer includes phone/shop/garage, GPS, wanted/arrest/jail/fines,
  waypoint missions, duty/salary/credits, and approval-based promotion.
- The 15-PNG branding bundle is generated and validated.
- The unified city pack contains branding, phone, cash, metro ticket, vehicle,
  and QualityArmory content. Current SHA1:
  `4633349625598AF3EFF64CAF24C74FB953BF0A4D`.

## Honest remaining gates

- The unified pack is public at `github.com/dev351en/gtm`; the direct GitHub
  URL, SHA1, stable UUID, and required-pack setting are in `server.properties`.
- BlueMap is installed but needs owner approval for its Mojang client-resource
  download acceptance before it can render.
- A real-player interaction pass remains for login, phone, economy, NPC
  walking/retaliation/loot, missions, transport, crime, medical, Bedrock UI,
  and promotion.
- WorldGuard safe-zone regions and event-driven robbery are not enabled;
  robbery remains disabled.
- Autonomous NPC vehicle driving, full heists, and several advanced simulation
  systems remain partial, as documented in `sdcraft_isolated/docs/FEATURE_MATRIX.md`.
- No live host or Aternos deployment has been performed.

## Authoritative files

- Gameplay specification: `sdcraft_isolated/docs/SDCRAFT_CODEX_FULL_CHAT_SUMMARY.md`
- Integration evidence: `sdcraft_isolated/INTEGRATION_STATUS_2026-11-23.md`
- Feature matrix: `sdcraft_isolated/docs/FEATURE_MATRIX.md`
- Release gates: `sdcraft_isolated/docs/RELEASE_REQUIREMENTS.md`
- Gemini handoff: `GEMINI_HANDOFF_PROMPT.md`
- Public repository: `https://github.com/dev351en/gtm`

Do not overwrite the Aternos backup or a live host while testing. Obtain final
deployment approval and make a fresh target-host backup first.
