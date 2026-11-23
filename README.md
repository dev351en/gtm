# EXPECT SDCRAFT

EXPECT SDCRAFT is a GTA-inspired Minecraft city-roleplay server for Paper 26.3.
The project combines a persistent city world, custom economy and mission logic,
NPC services, vehicles, phone-style menus, transport, medical workflows, crime,
duty systems, and a unified custom resource pack.

## Downloads

### Required resource pack

[Download EXPECT SDCRAFT Resource Pack 26.3](https://raw.githubusercontent.com/dev351en/gtm/main/resource-pack/EXPECT_SDCRAFT_ResourcePack_26.3.zip)

- SHA-1: `4633349625598AF3EFF64CAF24C74FB953BF0A4D`
- SHA-256: `F9788645400314EA8BA182EAAD725C1BEEBFED4EDFCA7DD566CE9663D5122B3E`
- Minecraft resource-pack version: `97.1`

The server configuration uses that exact GitHub raw URL and requires players
to accept the pack.

### Public world snapshot

[Download the privacy-sanitized world](https://github.com/dev351en/gtm/raw/refs/heads/main/downloads/EXPECT_SDCRAFT_PUBLIC_WORLD_2026-11-23.zip)

The public snapshot excludes player data, statistics, advancements, session
locks, UUID files, and scoreboard data. Back up a server before replacing its
world.

## Verified server target

- Paper 26.3 build 255
- Java 25
- Approximately 3-4 concurrent players
- 3.5 GB RAM and 10 GB disk target
- 22 validated plugin JARs in the private portable server build
- 71 SDCraftCore automated tests
- 38/38 audited original service coordinates
- 100 configured NPC identities and 100 generated runtime anchors

The exact portable server archive reached `Done`, reported all 22 plugins,
registered `SDCraft Wallet` with Vault, connected MTVehicles to that wallet,
reported a 100-person population policy with 100 anchors, and enabled
TrainCarts 2.0.5 with its required BKCommonLib 2.0.6 dependency.

## TrainCarts integration

The private portable build includes the official Paper 26.3 versions of
TrainCarts and BKCommonLib. A full-server boot reached `Done`; `train version`
reported both exact builds and the startup log confirmed TrainCarts detected
the SDCraftCore Vault economy. Conservative example configurations are in
`config/Train_Carts/` and `config/BKCommonLib/`.

This installs the train engine only. A physical rail line, stations, saved
train, and route signs have not been built in the city world yet. See the
[TrainCarts setup guide](docs/TRAINCARTS_SETUP.md) before staging a route.

## Dense city population

- 20 protected named service NPCs
- 80 generated pedestrians, merchants, workers, commuters and patrol officers
- 56/80-block proximity activation so offscreen NPCs do not consume resources
- Lightweight wandering near each pedestrian's home district
- About 30% of ambient NPCs retaliate when attacked; others flee
- Controlled $3-$15 loot, merchant bonus, occasional food/material drops and
  a three-minute respawn cooldown

The 100-person boot and configuration are verified. Real-player wandering,
combat, loot and multiplayer performance testing remains required.

## Repository layout

- `resource-pack/` - direct-download unified resource pack and hash details
- `downloads/` - privacy-sanitized world archive through Git LFS
- `source/` - SDCraftCore Java source and tests
- `config/` - safe server and SDCraftCore configuration examples
- `docs/` - implementation status, feature matrix, plugin checklist, and gates

## Server resource-pack configuration

```properties
resource-pack=https\://raw.githubusercontent.com/dev351en/gtm/main/resource-pack/EXPECT_SDCRAFT_ResourcePack_26.3.zip
resource-pack-sha1=4633349625598AF3EFF64CAF24C74FB953BF0A4D
resource-pack-id=04332dfe-5f85-5c4f-84cc-5609be67b115
resource-pack-prompt={"text":"[SD Craft] Accept the city pack for vehicles, phone, money and metro tickets."}
require-resource-pack=true
```

## Full server archive

The complete host-upload archive is intentionally not committed to this public
repository. It contains third-party plugin JARs whose licenses and distribution
terms differ; at least two currently declare All Rights Reserved. Publish those
JARs only with permission from their authors. The local tested artifact is
named `EXPECT_SDCRAFT_TRAINCARTS_2026-11-24.zip`.

## Important limitations

- BlueMap needs the server owner's Mojang-resource download acceptance.
- Real-player Java and Bedrock interaction testing remains required.
- Robbery remains disabled until protected regions and event behavior are
  verified.
- Autonomous NPC vehicle driving and full heists are not represented as
  complete features.
- TrainCarts is installed and boot-tested, but the physical railway and
  real-player route test remain pending.
- VoxelMap is client-side software; Invisible Item Frames and Placeable Items
  did not provide compatible Paper 26.3 server builds.

See [the feature matrix](docs/FEATURE_MATRIX.md) and
[release requirements](docs/RELEASE_REQUIREMENTS.md) before production use.

## Safety and licensing

Never overwrite an Aternos backup or live host without a fresh backup. Files
from third-party projects remain governed by their respective licenses. No
credentials, login databases, API keys, or private player records belong in
this public repository.
