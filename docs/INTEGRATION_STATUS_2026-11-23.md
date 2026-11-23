# SD Craft integration status — 2026-11-23

The user-supplied project handoff is preserved at
`docs/SDCRAFT_CODEX_FULL_CHAT_SUMMARY.md`. Its approved gameplay rules guide
future work; statements about completed features still require file and
runtime verification. Promotion now requires the approved credits and
verified duty hours, followed by `/sdc promotion approve <online-player>`
from an administrator. `/sdc promotion` shows the next requirements. Existing
persisted ranks are not automatically reduced.

`sdcraft_isolated` is the current editable Paper server folder. The rebuilt
`plugins/SDCraftCore-1.0.0.jar` matches `source/build/libs/SDCraftCore-1.0.0.jar`.
The source compiles against Paper 26.3 and all 67 JUnit tests pass.
The new GTA layer has not yet had an in-game multiplayer smoke test.

## Gameplay now in source

- One-time starter kit; `/car buy` and `/gun` charge the server ledger.
- `/phone`, shop, mission board, garage status, HUD, wanted stars, surrender,
  police arrest, fines and jail timer.
- Mission checkpoint routes are persisted and pay on arrival. These are
  waypoint missions; passenger, vehicle theft, evidence, and heist interactions
  are not yet verified by game events.
- Crime damage in the configured civic safe zones is cancelled. Cash robbery
  remains disabled. A bank heist mission definition exists but is disabled by
  the same robbery switch.
- SimpleRevive owns the downed state; SDCraftCore's downed handler is disabled.

## Plugin installations

The `plugins/` folder contains verified Modrinth Paper 26.3 releases of
SimpleLogin, GSit, DreamDisplays, PlayerCorpses, SimpleRevive,
DecentHolograms, ClearLag++, SkinsRestorer, and The Smooth Elevator, alongside
Paper and the existing plugin suite. SHA-512 hashes were checked against the
Modrinth version API at download time.

VoxelMap Updated is Fabric client software. Invisible Item Frames and
Placeable Items do not publish a Paper 26.3 build, so none of those three was
placed in the server's `plugins/` folder.

## City Phone custom GUI

CommandPanels 4.2.5 is installed in `plugins/`. Its Modrinth SHA-512 was
verified before installation. `plugins/CommandPanels/panels/sd_phone.yml`
defines the Java inventory phone and `sd_phone_bedrock.yml` defines its
Floodgate form fallback. `/phone` dispatches the `cityphone` panel when
CommandPanels is enabled; SDCraftCore's original menu remains a fallback.
Buttons call SDCraftCore commands so transactions still use its ledger.

The phone header and bank icon now use reserved custom model IDs from the
unified 26.3 resource pack. Players receive a City Phone item in the starter
kit; right-clicking it opens the same GUI. A paid metro trip issues a cosmetic
ticket receipt. The bank icon uses cash artwork, while the ledger remains
digital so decorative items cannot be redeemed for extra balance.
The new panel still needs an in-game smoke test, including a Bedrock test on
a server with Geyser and Floodgate installed.

## Vault economy and city resource pack

VaultUnlocked 2.20.3 (plugin name `Vault`) is installed in `plugins/` with a
verified Modrinth SHA-512. SDCraftCore registers `SDCraft Wallet` as a Vault
legacy economy provider when Vault is enabled. The Vault balance is the same wallet that SD
Craft shops, fares, and ATM transfers use; the protected city bank remains
separate. Vault shared-bank operations are unsupported. Currency is dollars
with two decimal places. There is no account migration to another provider.
`economy.vault-provider-enabled` now defaults to true and controls provider
registration in both the source and deployed local config.
On a disposable Paper 26.3 server, both plugins enabled successfully and
`vault-info` reported `Economy Legacy: SDCraft Wallet`. VaultUnlocked's modern
economy interface is not registered.

`resourcepacks/SDCraft_Unified_26.3_CityPack.zip` combines the existing
vehicle/gun assets with SD Craft cash, City Phone, and metro ticket models.
The item model IDs are PAPER 900001, 900002, and 900003 respectively. The
pack declares the Minecraft 26.3 resource pack version 97.1. Rebuild it via
`python resourcepacks/build_city_pack.py` from `sdcraft_isolated`; the script
reads the existing unified pack and `../rp_staging` city textures.

The unified pack is configured for the public GitHub repository at
`dev351en/gtm` using the direct `raw.githubusercontent.com` ZIP URL.
`server.properties` contains SHA1
`4633349625598AF3EFF64CAF24C74FB953BF0A4D`, stable resource-pack UUID
`04332dfe-5f85-5c4f-84cc-5609be67b115`, and requires clients to accept the
pack. Keep the published ZIP bytes unchanged. Java 26.3 client visual
validation and a real economy-plugin transaction test are still needed.

## Before production

1. Run a disposable server and inspect plugin startup logs, commands, and
   real player interactions. Compile and unit tests do not verify cross-plugin
   behavior.
2. Check each provisional site in `plugins/SDCraftCore/runtime.yml` in-game,
   especially `jail`, `bank`, `hospital`, and mission checkpoints. Use
   `/sdc setsite <id>` while standing at the intended safe block to correct it.
3. Confirm the GitHub raw resource-pack URL remains public and its downloaded
   bytes match SHA1 `4633349625598AF3EFF64CAF24C74FB953BF0A4D`.
4. Configure authentication at the host/proxy level. The current
   `online-mode=false` installation relies on SimpleLogin and must not expose
   unauthenticated admin access. Confirm its login gate and OP identities.
5. DreamDisplays requires a compatible client installation for viewers.
6. The host's website/panel URL and access method are still needed to deploy
   these local server files remotely.

## Verified continuation update — 2026-11-23

The isolated world was audited read-only from its Anvil region files. The
original provisional points for spawn, hospital, metro, gas station, and other
services placed several destinations over water or unsafe blocks. `runtime.yml`
and all 20 `anchors.yml` entries now use audited walkable coordinates. The
validator reports `38/38` site and anchor coordinates with a solid floor and
two clear player-height blocks:

`uv run --with pyyaml,nbtlib python docs/validate_sites.py`

The source fallback spawn is now `(10, 70, 3)` and the isolated world spawn is
set to the same audited City Hall road surface. `SurfaceSpawnAndKitTest` was
updated to test the audited coordinates; the core rebuild still passes all 67
tests.

The full disposable Paper 26.3 smoke server was rerun after the coordinate and
core changes. It loaded 20 plugins, reached `Done`, reported
`Economy Legacy: SDCraft Wallet`, and logged the automatic MTVehicles Vault
reconnect. `sdc status` reported 20 confirmed anchors and the configured 6/20
population caps. BlueMap remains intentionally pending its owner-controlled
resource-download acceptance.

`resourcepacks/SDCRAFT_ASSETS_OVERHAUL.zip` is the validated 15-PNG artwork
bundle. Rebuilding the unified pack after adding its pack icon and item models
produces SHA1 `4633349625598AF3EFF64CAF24C74FB953BF0A4D`. The old SHA1 in the
earlier paragraphs is historical and must not be used for this current ZIP.

## Dense city population update - 2026-11-24

The configured population is now 100 identities: 20 protected named service
NPCs plus 80 generated ambient pedestrians. The generated population includes
merchants, commuters, workers, students, tourists, delivery characters,
security characters, and two additional patrol officers. The active caps are
6 police and 94 non-police.

Ambient NPCs use 56/80-block activation hysteresis, remain abstract while
offscreen, and receive lightweight Citizens navigation near their home anchor.
About 30 percent are configured to retaliate briefly when attacked; other
pedestrians flee. Defeating an ambient NPC grants a controlled $3-$15 wallet
drop, a $5 merchant bonus, occasional food/material loot, a wanted response,
and a three-minute respawn cooldown. Named service NPCs remain protected.

The rebuilt core passes 71 tests. A fresh disposable Paper boot loaded all 20
plugins, reached `Done`, registered the Vault wallet, generated 100 NPC anchors,
and reported `configured=100, active police=0/6, other=0/94` with no players
online. Actual wandering, retaliation, defeat loot, and multi-player
performance still require a real-player staging test before production.
