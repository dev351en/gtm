# EXPECT SDCRAFT — Master Changelog & AI Developer Guide

> **Note for Future AI Agents & Developers (ChatGPT, Claude, Gemini, etc.):**  
> This file contains the complete, authoritative record of all changes, architecture decisions, coordinate registries, and operational instructions for the EXPECT SDCRAFT project. Read this file first before making changes to ensure full compatibility with the Paper 26.3 runtime, the custom SDCraftCore engine, and the existing city ecosystem.

---

## [1.6.0-dev.2] — 2026-11-24: Civic rules and prototype character catalogue

- Implemented immutable, integer-ARK-cent loan schedules with bounded flat interest, grace periods, active-day advancement, overdue checks and repayment validation.
- Added property owner/guest/admin access rules, key-bound lock toggles and rekeying; added food order preparation, dispatch, delivery and refund state transitions; added deterministic five-of-nineteen jail rotation excluding the gang boss.
- Executed CivicChecks using OpenJDK 21: 78 checks passed. Committed exact source blobs match local git hashes. These are portable domain rules only; existing ledger, world protection, money transfer, NPC movement and persistence integration remain pending. Immutable old snapshots must not be replayed; transactional persistence is required before enabling real loans or orders.
- Added tools/generate_npc_assets.py; generated and validated 500 distinct 64x64 RGBA skin prototypes, 100 distinct 64x64 outfit overlays, deterministic registries with 20 gang members (one boss, five initially jailed). Preview inspected locally. Procedural first-pass designs are not final art; in-game skin/outfit rendering and existing NPC identity migration not tested.
- Local asset ZIP GTM_DEV2_CIVIC_ASSETS.zip contains 607 files, 445876 bytes, CRC verified. Generator committed, binary archive delivered separately, not a full server release.
- Production is now the user's intended game host for verified incremental updates, but remains untouched: DNS resolution for app.daytona.io and github.com fails from the execution environment, no Daytona connector available, full Paper/JDK25 build and account billing/quota verification blocked. No new sandbox, no spending, no live deployment. Do not use the exposed key; rotate it and configure secure deployment credentials.
- Added CodeMC VaultUnlockedAPI 2.20 fallback when the original local VaultUnlocked 2.20.3 JAR is absent; kept original local dependency preference. Gradle check now runs both domain smoke suites. Added Java 25/Gradle 9.2.1 GitHub Actions verification, with read-only repository permission and no deployment. Full build still unverified: no workflow run returned by connector at time of recording. Dependency availability/API compatibility must be checked in the actual build.
- Remaining Revision 4.0 scope stays open; no claim of complete gameplay.

---

## [1.6.0-dev.1] — 2026-11-24: GTM Revision 4.0 foundation (not a playable release)

- Created isolated development branch `gtm/revision-4-foundation`; no changes to production, main, world or Daytona.
- Added platform-neutral VehicleState rules: bounded energy consumption, odometer, idle/refill, health thresholds, repair, one-time destruction transition. Not yet wired to vehicle movement or persistence.
- Added RoleplayText parser: explicit double slash plus whitespace, bounded Unicode text, editor command protection, language detection and varied reaction strings.
- Added experimental GtmDialogue Paper adapter for submitted local dialogue, nearby visible NPC targeting and temporary moving text displays. Disabled by default, permission explicitly required. No live validation; current reply engine English/Hindi, not full Hinglish or AI inference.
- Local dependency-free javac/Java 21 smoke checks: 36 passed; checked source blob hashes. Full Paper Java 25 build and client tests blocked by environment/dependencies; existing reported tests not rerun.
- Added PROJECT_SPEC.md, AGENTS.md and docs/FOUNDATION_TEST_REPORT.md with scope, test reproduction and audit blockers.
- Asset production, building renovation, crossplay HUD, transport integration, banking, gangs, missions, dashboard, external AI and deployment remain pending. No release ZIP claiming completed game.
- Do not deploy this development revision. Verify authentication, build dependencies, world geometry, account quotas and backups before staging; never expose credentials.

---

## [1.5.0] — 2026-11-24: Custom 3D Models, GTA iFruit Icons, Creative Arsenal Upgrade & Resource Pack 26.3 Deployment

### 🌟 Release Overview
Integrated **12 custom 3D Blockbench models**, **51 procedural textures**, and **8 high-definition GTA Online / iFruit application icons** into the unified `EXPECT_SDCRAFT_ResourcePack_26.3.zip` distribution. Overhauled the 54-slot **Creative Testing Arsenal** (`/arsenal`, `/testing`, `/creativemenu`) so all items, firearms, roleplay tools, and vehicle keys render as genuine 3D models directly within inventory slots. Recompiled `SDCraftCore-1.0.0.jar` against Paper 26.3 on OpenJDK 25 LTS, deployed to Daytona Cloud VPS, verified zero-secret Git state, and pushed to GitHub [`dev351en/gtm`](https://github.com/dev351en/gtm).

---

### 1. 3D Model Registry & Item Predicates (Minecraft 1.21.4 Format)
Integrated 12 Blockbench 3D model definitions with complete first-person, third-person, ground, and GUI transforms:

| Item / Asset Name | Base Item | CustomModelData | Resource Identifier | In-Game Behavior & Transforms |
| :--- | :--- | :--- | :--- | :--- |
| **3D Smartphone** | `PAPER` | `900002` | `sdcraft:item/smartphone_3d` | Dual-camera bezel-less phone; right-click opens iFruit OS |
| **SDPD Detective Badge** | `PAPER` | `900004` | `sdcraft:item/police_badge_3d` | Gold 7-point star in folding black leather badge wallet |
| **Tactical Medkit** | `PAPER` | `900005` | `sdcraft:item/medkit_3d` | Cordura nylon field medic trauma pouch with cross |
| **VIP ATM Card** | `PAPER` | `900009` | `sdcraft:item/atm_card_3d` | Maze Bank Platinum credit/debit card with EMV chip |
| **3D Cash Bundle** | `PAPER` | `900001` | `sdcraft:item/cash_bundle_3d` | Stacked $100 currency bills bound by paper banking strap |
| **Car Key Fob** | `PAPER` | `900010` | `sdcraft:item/car_key_fob_3d` | Keyless vehicle remote; delivered with MTVehicles |
| **Fuel Jerry Can** | `PAPER` | `900011` | `sdcraft:item/jerry_can_3d` | 100L metal fuel jerry can; refuels vehicles to 100% |
| **Louisville Baseball Bat**| `PAPER` | `900012` | `sdcraft:item/baseball_bat_3d`| Turned ash wood sports bat with wrapped athletic grip |
| **9mm Service Pistol** | `IRON_HOE` | `101` | `sdcraft:item/gun_pistol_3d` | Semi-automatic 9x19mm service sidearm (`GunEngine`) |
| **12-Gauge Shotgun** | `GOLDEN_HOE` | `102` | `sdcraft:item/gun_shotgun_3d` | Tactical pump-action police scattergun (`GunEngine`) |
| **Tactical Micro-SMG** | `DIAMOND_HOE` | `103` | `sdcraft:item/gun_smg_3d` | High-cadence CQB 9mm submachine gun (`GunEngine`) |
| **M4 Assault Rifle** | `NETHERITE_HOE`| `104` | `sdcraft:item/gun_rifle_3d` | 5.56 NATO tactical military assault rifle (`GunEngine`)|

**Minecraft 1.21.4 Model Definitions (`assets/minecraft/items/`):**
- `paper.json`: Range dispatch on `"property": "minecraft:custom_model_data"` mapping models `900001` through `900027`.
- `iron_hoe.json`: Threshold `101.0` -> `sdcraft:item/gun_pistol_3d`.
- `golden_hoe.json`: Threshold `102.0` -> `sdcraft:item/gun_shotgun_3d`.
- `diamond_hoe.json`: Threshold `103.0` -> `sdcraft:item/gun_smg_3d`.
- `netherite_hoe.json`: Threshold `104.0` -> `sdcraft:item/gun_rifle_3d`.

---

### 2. High-Resolution GTA iFruit Application Icons
8 custom transparent 2D icons added for the `/phone` iFruit smartphone GUI:
- `app_gps` (CMD `900020`): Live GPS district navigation
- `app_jobs` (CMD `900021`): Career & employment registry
- `app_gear` (CMD `900022`): Ammu-Nation weapons & tactical gear
- `app_garage` (CMD `900023`): Motorsport vehicle retrieval
- `app_bank` (CMD `900024`): Maze Bank atomic financial transfers
- `app_safety` (CMD `900025`): SDPD wanted level & legal assistance
- `app_medical` (CMD `900026`): Mount Zonah trauma services
- `app_settings` (CMD `900027`): Roleplay profile & preferences

---

### 3. Upgraded Creative Testing Arsenal (`CreativeArsenalManager.java`)
The 54-slot developer and testing GUI (`/arsenal`, `/testing`, `/creativemenu`) was completely overhauled to replace vanilla placeholder items with custom 3D models:
- **Slot 7 (Fuel)**: `CityItems.jerryCan()` — renders 3D Jerry Can; clicking delivers 100L fuel canister and refills vehicle.
- **Slot 8 (Melee)**: `CityItems.baseballBat()` — renders 3D Louisville Bat; clicking equips the sports melee weapon.
- **Slot 9 (Pistol)**: `guns.createGun(GunType.PISTOL)` — renders 3D 9mm Pistol; clicking equips gun + 24 rounds.
- **Slot 12 (SMG)**: `guns.createGun(GunType.SMG)` — renders 3D Micro-SMG; clicking equips gun + 60 rounds.
- **Slot 14 (Rifle)**: `guns.createGun(GunType.RIFLE)` — renders 3D M4 Rifle; clicking equips gun + 50 rounds.
- **Slot 15 (Shotgun)**: `guns.createGun(GunType.SHOTGUN)` — renders 3D Shotgun; clicking equips gun + 12 shells.
- **Slot 27 (Cash)**: `CityItems.cashIcon()` — renders 3D Cash Bundle; clicking adds $10,000 cash to wallet.
- **Slot 28 (Bank)**: `CityItems.atmCard()` — renders 3D VIP ATM Card; clicking wires $1,000,000 to Maze Bank.
- **Slot 29 (Phone)**: `CityItems.phone()` — renders 3D Smartphone; clicking equips phone (right-click opens `/phone`).
- **Slot 31 (Medkit)**: `CityItems.medkit()` — renders 3D Medical Pouch; clicking restores 100% HP.
- **Slot 32 (Metro)**: `CityItems.metroTicket("Central Metro")` — renders TrainCarts all-access rail ticket.
- **Slot 33 (Police)**: `CityItems.policeBadge()` — renders 3D SDPD Detective Badge; clicking equips badge + restraints.
- **Vehicle Dispensing**: `giveVehicle()` now automatically delivers a 3D Car Key Fob (`CityItems.carKeyFob(name)`).

---

### 4. Master Resource Pack & Deployment Details
- **Archive Path**: `resource-pack/EXPECT_SDCRAFT_ResourcePack_26.3.zip`
- **File Size**: 9.75 MB (10,222,698 bytes)
- **Verified SHA-1**: `cd6420c2d685069df42dd88f7903363a6c24632b`
- **Deployments**:
  - `server.properties` on Daytona VPS: `resource-pack-sha1=cd6420c2d685069df42dd88f7903363a6c24632b`
  - GitHub Repository: Committed and pushed to `main` (`c7f5dcb`)
  - Local Client Cache: Synchronized to `%APPDATA%\.minecraft\resourcepacks\EXPECT_SDCRAFT_ResourcePack_26.3.zip`
- **Security Check**:
  - Git commit diff checked: zero API keys, zero authtokens, zero credentials committed.

---

## [1.4.0] — 2026-11-24: MCServerHost Direct Cloud Deployment & Vehicle Rendering Root-Cause Fix

### 🌟 Release Overview
Integrated and configured the user's dedicated **MCServerHost** cloud server (`51.79.229.238:23040`) for zero-proxy, direct public multiplayer. Solved the critical 3-part bug chain causing vehicles to render as vanilla diamond hoes and the server resource pack to be rejected. Deployed the verified monotonic resource pack across GitHub, Daytona VPS, and MCServerHost, installed the universal **Complementary Reimagined r5.10** shaderpack, and configured the user's Minecraft client for automatic server-side pack downloads.

---

### 1. Dedicated Public Hosting (MCServerHost)
- **Direct Server IP for Players/Friends**: `51.79.229.238:23040`
- **Host Provider**: MCServerHost (Pterodactyl container architecture)
- **SFTP Management**: `51.79.229.238:2022` (User: `3512dev.stuff@gmail.com.38f3f401`)
- **Key Advantage**: Dedicated public IP and port (`23040`). Friends can connect directly from the Minecraft multiplayer menu with **zero** local batch scripts, SSH tunnels, or Ngrok proxies.
- **Server Properties Synchronized**:
  - `server-ip=0.0.0.0`
  - `server-port=23040`
  - `resource-pack=https\://raw.githubusercontent.com/dev351en/gtm/main/resource-pack/EXPECT_SDCRAFT_ResourcePack_26.3.zip`
  - `resource-pack-sha1=fcb712e1d90d378ff7a154ff39d32e3db92e6eaa`
  - `resource-pack-id=e92b5f0b-4866-4dca-a73b-7712db625bb6`
  - `resource-pack-prompt=` (cleared to avoid Gson control-character parser errors)
  - `require-resource-pack=true`

---

### 2. Vehicle Rendering & Resource Pack Root-Cause Fix
Extensive decompilation and JSON schema validation identified the exact 3 bugs causing MTVehicles models to fail:
1. **Gson MalformedJsonException in `server.properties`**:
   - `resource-pack-prompt` contained literal unescaped `\n` and `§` formatting characters.
   - Paper's internal Gson parser threw `MalformedJsonException: Unescaped control characters (\u0000-\u001F) in server.properties`.
   - Result: Paper set `serverPackInfo = Optional.empty()`, completely suppressing server-side pack prompts on join.
   - **Fix**: Cleared `resource-pack-prompt=` to use Minecraft's clean native prompt.
2. **Damaged Property Short-Circuit in `diamond_hoe.json`**:
   - In `assets/minecraft/items/diamond_hoe.json`, all 230 MTVehicles custom models were nested inside `on_false` of `"property": "damaged"`, while `on_true` was hardcoded to `minecraft:item/diamond_hoe`.
   - Since MTVehicles spawns vehicles with custom item damage (e.g., 1009, 1029), Minecraft evaluated `damaged == true` and rendered the vanilla diamond hoe.
   - **Fix**: Rebuilt the root definition using `minecraft:range_dispatch` directly on `"property": "damage"`.
3. **Non-Monotonic Threshold Ordering**:
   - Entry 230 had `threshold: 0` placed after `0.8169`, violating Minecraft 1.21.4's strict rule that thresholds must be strictly increasing.
   - Result: Client log logged `JsonParseException: Thresholds must be strictly increasing` and discarded all overrides.
   - **Fix**: Re-sorted and deduplicated all 229 damage entries with strictly increasing monotonic thresholds and `fallback: minecraft:item/diamond_hoe`.

---

### 3. Client Automation & Universal Shaders
- **Multiplayer Server List (`servers.dat`)**:
  - `§6§lSD CRAFT SMP §a(Direct Cloud Server)`: `51.79.229.238:23040` (`acceptTextures: 1` — automatic download).
  - `§6§lSD CRAFT SMP §7(Daytona VPS)`: `localhost:25565` (`acceptTextures: 1`).
- **Local Pack Cache**: Fixed pack copied directly to `%APPDATA%\.minecraft\resourcepacks\EXPECT_SDCRAFT_ResourcePack_26.3.zip` and activated in `options.txt`.
- **Universal Shaders**: Installed **Complementary Reimagined r5.10** (`ComplementaryReimagined_r5.10.zip`) into `%APPDATA%\.minecraft\shaderpacks\`.

---

## [1.3.0] — 2026-11-24: Daytona Cloud 24/7 VPS Hosting & Public 3D BlueMap Deployment

### 🌟 Release Overview
Successfully provisioned and deployed the complete EXPECT SDCRAFT Paper 26.3 server to a dedicated high-performance Daytona Cloud VPS (`daytona-large`, 4 vCPU, 8 GB RAM, 64-core host pool with 700+ GB host RAM) running Debian 13 GNU/Linux and OpenJDK 25.0.5.1. The server runs 24/7 in background persistence (`autostop: 0`, `autopause: 0`) inside a detached tmux session with all 24 plugins active. Public 3D BlueMap web visualization and 1-click zero-config SSH tunneling are fully established.

---

### 1. Cloud Infrastructure & Environment
- **Platform**: Daytona Cloud (`https://app.daytona.io/api`)
- **Sandbox ID**: `b6a826ca-4dac-4716-b7b9-236b88b4718e` (Region: `eu`)
- **Container Specs**: 4 vCPU, 8 GB RAM, 10 GB Disk (`daytona-large`), hosted on a 64 vCPU host node with ~750 GB RAM pool.
- **Java Runtime**: OpenJDK 25.0.5.1 (`openjdk-25-jdk` Debian package).
- **Minecraft Server Binary**: Paper 26.3 Build 255 (`paper-26.3-255.jar`), Mojang SHA-256 pre-verified cache (`cache/mojang_26.3.jar`).
- **Memory Flags**: `-Xms2048M -Xmx4096M -XX:+UseG1GC` inside `/home/daytona/sdcraft_server/start.sh`.
- **Background Execution**: Server runs continuously inside `tmux` session `minecraft` with automated crash protection.
- **Persistence**: `autostop = 0` and `autopause = 0` locked via Daytona SDK.

---

### 2. Live Public 3D BlueMap
- **Public URL**: `https://8100-b6a826ca-4dac-4716-b7b9-236b88b4718e.daytonaproxy01.eu/`
- **Configuration**:
  - BlueMap v5.29 configured with `accept-download: true` in `plugins/BlueMap/core.conf`.
  - Client resource pack `minecraft-client-26.3.jar` (41.4 MB, SHA-1 `e877b6a07acd633fb3bb475002175cec036e7b87`) uploaded directly to `/home/daytona/sdcraft_server/bluemap/minecraft-client-26.3.jar`.
  - Integrated HTTP webserver active on port 8100, bound to all network interfaces (`0.0.0.0:8100`).
  - Daytona sandbox configured with `public: True` to allow credential-free public web access.

---

### 3. One-Click Connection & Management Tooling
Created automated launchers in the root workspace:
1. `connect_daytona_server.bat` (`tools/daytona_tunnel.py`):
   - Authenticates with Daytona API using account key.
   - Generates a fresh 24-hour secure SSH session token.
   - Binds `localhost:25565` to the Daytona cloud server via `ssh -N -L 25565:localhost:25565`.
   - Allows instant connection in Minecraft (Java Edition 26.3) to `localhost:25565`.
2. `connect_daytona_ssh.bat` (`tools/daytona_ssh_shell.py`):
   - One-click interactive Linux shell directly into `/home/daytona/sdcraft_server`.
3. `mc_console.bat` (`tools/daytona_mc_cmd.py`):
   - Direct interactive console prompt to issue live server commands (`op`, `whitelist`, `say`, `dh reload`, `bluemap`, etc.).

---

## [1.2.0] — 2026-11-24: City Holograms, Creative Arsenal, Fixed NPCs, Fresh Animations 26.3, & Bedrock Auto-Send

### 🌟 Release Overview
This major release implements city-wide visual polishing, automated creative testing tools, fixed daytime NPC grounding with dynamic tracking, full integration of **Fresh Animations 1.11.2** with all extensions, and Bedrock/Pocket Edition (PE) auto-sending capabilities via Geyser. All 76 automated JUnit 5 tests pass on JDK 25.

---

### 1. DecentHolograms Integration across 10 Key Locations
Engineered 10 permanent YAML configurations deployed to `plugins/DecentHolograms/holograms/` (and mirrored in `config/DecentHolograms/holograms/`). All holograms use 0.28-block line spacing, high-contrast hex formatting, bilingual titles (English / Hindi), and situational action prompts:

| Hologram ID | Configuration File | World Coordinates (X, Y, Z) | Visual Theme & Purpose |
|---|---|---|---|
| `spawn_welcome` | `spawn_welcome.yml` | `world: 10.5, 74.0, 15.5` | Neon Cyan / Gold Civic Center arrival board with quick-start rules and `/phone` prompt. |
| `city_hall` | `city_hall.yml` | `world: 10.5, 75.0, -25.5` | Deep Aqua / Gold Civic directory for civil services, licenses, and Mayor's office. |
| `police_hq` | `police_hq.yml` | `world: 142.5, 74.5, 65.5` | Red / Blue emergency beacon for Police Department, 911 dispatch, and duty enrollment. |
| `general_hospital` | `general_hospital.yml` | `world: -85.5, 74.5, 110.5` | Emerald / Mint medical cross board for ER intake, triage, diagnostics, and paramedic duty. |
| `central_bank` | `central_bank.yml` | `world: -45.5, 75.0, -15.5` | Yellow / White Vault board displaying interest rates, ATM access, loans, and teller lines. |
| `motor_dealership` | `motor_dealership.yml` | `world: 210.5, 74.0, -80.5` | Neon Orange / Gold showroom banner for MTVehicles, test drives, and custom paint jobs. |
| `metro_transit` | `metro_transit.yml` | `world: 10.5, 73.5, 36.5` | Lime / White subway board for TrainCarts rapid transit, $10 fares, and station maps. |
| `gas_station` | `gas_station.yml` | `world: 95.5, 73.5, -120.5` | Gold / Green fuel depot sign with Octane pricing, repair kits, snacks, and car wash. |
| `fire_rescue` | `fire_rescue.yml` | `world: 65.5, 74.5, 185.5` | Flame Orange / Yellow rescue station for 911 dispatch, extinguishers, and gear. |
| `testing_arsenal` | `testing_arsenal.yml` | `world: 14.5, 73.5, 15.5` | Purple / Magenta staff portal advertising `/testing` and `/arsenal` instant access. |

---

### 2. GTA Creative Testing Arsenal & Rapid Exploration Suite
Implemented `CreativeArsenalManager.java` in package `com.sdcraft.core` and registered in `SDCraftCorePlugin.java`:
- **54-Slot Testing Chest GUI**:
  - **Vehicles (7 MTVehicles types)**: Sedan, Sports Car, SUV, Police Cruiser, Ambulance, Fire Engine, Offroad Truck.
  - **Firearms & Munitions (QualityArmory)**: 9mm Service Pistol, Tactical Shotgun, Combat Rifle, Submachine Gun, High-Caliber Sniper, RPG Launcher, and matched ammo boxes.
  - **City Equipment**: City Smartphone, GPS Unit, First Aid Medkit, Metro Transit Pass, Restraint Cuffs, Fire Extinguisher, Diagnostic Repair Tool.
  - **Currency Test Grants**: Instant test credits ($1,000, $5,000, $10,000) deposited directly into SDCraft Wallet.
  - **One-Click Landmark Teleports**: Direct transport to Spawn, Police HQ, General Hospital, Central Bank, Motor Dealership, Metro Station, Gas Station, and Fire Rescue.
- **Commands Added to `plugin.yml`**:
  - `/arsenal`, `/creativemenu`, `/testitems`: Directly opens the 54-slot Testing Arsenal GUI.
  - `/testing`: One-step developer command. Sets player to Creative Mode (`GameMode.CREATIVE`), grants flight (`setAllowFlight(true)`), godmode (`setInvulnerable(true)`), grants $10,000 wallet cash, gives the right-clickable "Testing Arsenal Star" (`Material.NETHER_STAR`), and immediately opens the Arsenal GUI.
- **Physical Star Item**: Right-clicking the "Testing Arsenal Star" at any time anywhere on the map reopens the testing menu immediately.

---

### 3. Hardened NPC Grounding & Bilingual Dialogues
- **Firm Daytime Grounding (`NpcService.java`)**:
  - Citizens `LookClose` trait (`net.citizensnpcs.trait.LookClose`) attached to all 20 named service staff. NPCs dynamically turn their heads and bodies to track players within a 6-block radius.
  - Disabled wandering AI for service staff on duty.
  - Disabled physical entity collision (`setCollidable(false)`) and gravity (`setGravity(false)`) to prevent players or vehicles from shoving service NPCs off their designated service stations.
  - Invulnerability (`setProtected(true)`) strictly enforced.
- **Revamped Interaction Dialogues & Menus**:
  - Integrated GTA-themed chat box headers with bilingual subtitles (English & Hindi).
  - Emits friendly confirmation chime (`Sound.ENTITY_VILLAGER_YES`, pitch 1.0) on interaction.
  - Action Bar prompts (e.g. `[SD CRAFT] Service Staff Available • Shift+Right-Click for quick menu`).
  - GUI menus feature charcoal gray glass borders and custom thematic icons (Shield for Police, Golden Apple for Medics, Emerald for Bankers, Compass for Transit).

---

### 4. Fresh Animations 1.11.2 & All Extensions (Modrinth 26.3)
- **Base Pack**: Upgraded to official Modrinth `FreshAnimations_v1.11.2_26.1+.zip` (compatible with Paper 26.3).
- **All 7 Official Extensions Merged**:
  1. `FA+Details-v1.10.1` (Blinking eyes, expressive eyebrows, dynamic mouth movements)
  2. `FA+Objects-v1.10.1` (Animated held items, dynamic food consumption, responsive bows/tools)
  3. `FA+Emissive-v1.10.1` (Glowing eyes for Endermen, Spiders, Phantoms, glowing cores)
  4. `FA+Spiders-v1.10.1` (Realistic multi-jointed 8-legged creeping, lunging, wall-climbing)
  5. `FA+Creepers-v1.10.1` (Menacing stalking animations, swelling fuse expansions)
  6. `FA+Quivers-v1.10.1` (Dynamic skeleton bone rattling and back-mounted quivers)
  7. `FA+Player-v1.1` (Smooth sprint cycles, swimming, crawling, falling, and idle breathing)
- **Unified Distribution**:
  - Combined into canonical server pack: `resource-pack/EXPECT_SDCRAFT_ResourcePack_26.3.zip` (9.91 MB, 1,674 files).
  - SHA-1: `b0d7f272c6bb2b7084c05b5874920f7aca2bbd86`
  - SHA-256: `ecd789f6cba84f9a19200553a23d3840436dbae2742fdb05a5d71ac3da7a5560`
  - `server.properties` configured with `require-resource-pack=true` and custom bilingual prompt.

---

### 5. Geyser & Floodgate Bedrock / PE Crossplay Auto-Send
- Added `Geyser-Spigot` (v2.12.1 b1308) and `floodgate-spigot` (v2.2.5 b141) integration.
- Configured `plugins/Geyser-Spigot/config.yml` with `force-resource-packs: true`.
- Bedrock players connecting from phones, tablets, consoles, or Windows 10/11 Bedrock edition are automatically served Bedrock `.mcpack` files placed in `plugins/Geyser-Spigot/packs/` without needing manual installation.

---

### 6. Automated Verification & Test Suite
- **76 / 76 JUnit 5 Unit Tests Passing** across 9 test classes:
  - `CreativeArsenalAndHologramTest` (5 tests) — Verifies vehicle mapping, QA firearms, coordinates, and hologram definitions.
  - `DialogueEngineTest` (36 tests) — Intent classification across English, Hindi, Hinglish, safety bounds, and 20 character profiles.
  - `LedgerTest` (11 tests) — Vault economy, PBKDF2 PIN hashing, deposits, withdrawals, duty salaries, and transaction auditing.
  - `MapAndGpsTest` (2 tests) — District boundary detection and compass navigation math.
  - `NpcPopulationTest` (3 tests) — 100-character generation (20 named + 80 ambient) and behavior distributions.
  - `PolicyEngineTest` (7 tests) — Police response levels, witness rates, taxi meters ($25 base + $6/100m), and robbery caps.
  - `RestorationAndGunsTest` (3 tests) — 5-minute block regeneration and firearm ballistics.
  - `SurfaceSpawnAndKitTest` (5 tests) — Surface spawn Y>=70, underground rescue, starter kit balancing, and landmark anchors.
  - `VaultWalletTest` (1 test) — Vault integration and double-precision cent currency math.

---

## 🛠️ Instructions for Future AI Agents & Developers (ChatGPT, Claude, etc.)

When tasked with extending or updating EXPECT SDCRAFT, strictly observe the following protocols:

### A. Development Environment & Build Tools
1. **JDK & Gradle Setup**:
   The project requires **Java 25** (`io.papermc.paper:paper-api:26.3.build.255-stable`).
   Always compile and test using:
   ```cmd
   set JAVA_HOME=D:\DevTools\jdk-25
   set PATH=D:\DevTools\jdk-25\bin;D:\DevTools\gradle-9.9.2\bin;%PATH%
   cd /d d:\Games\SDCRAFT\github_gtm_repo\source
   gradle test --no-daemon
   ```
2. **Offline Dependency Stub**:
   `source/build.gradle.kts` depends on `../plugins/VaultUnlocked-2.20.3.jar` for Vault API interfaces. Ensure this file remains in `plugins/`.

### B. Adding Items to Creative Arsenal (`CreativeArsenalManager.java`)
- Modify `CreativeArsenalManager.java` in `source/src/main/java/com/sdcraft/core/`.
- Slots are 0-indexed in a standard 54-slot chest (Rows 1–6).
- Use `createGuiItem(Material mat, String name, String... lore)` for consistent formatting.
- Handle click actions in `handleArsenalClick(InventoryClickEvent event, SDCraftCorePlugin plugin)` in `CreativeArsenalManager.java`.
- Run `gradle test --no-daemon` to verify against `CreativeArsenalAndHologramTest.java`.

### C. Adding or Modifying Holograms
- Holograms live in `plugins/DecentHolograms/holograms/<id>.yml` and `config/DecentHolograms/holograms/<id>.yml`.
- Standard line height spacing is `0.28`.
- Use `tools/generate_holograms.py` if regenerating or batch-updating hologram definitions.

### D. Updating Server Resource Pack
- Python build tool: `tools/build_merged_pack.py`.
- If new models, textures, or animations are added, run `python tools/build_merged_pack.py`.
- Calculate the new SHA-1 hash using `Get-FileHash -Algorithm SHA1`.
- Update both `server.properties` and `config/server.properties` with the new hash.
- Update `resource-pack/README.md` and `README.md`.

### E. Git & Repository Management
- Do NOT commit heavy 3rd-party JAR binaries (>50 MB) like `Geyser-Spigot.jar` to Git. Keep them in `.gitignore`.
- Always update this `CHANGELOG.md` file whenever making new updates so other agents maintain context.
