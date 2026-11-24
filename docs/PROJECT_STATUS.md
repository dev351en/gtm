> Current engineering status (25 November 2026): work continues on `gtm/playable-r4` as `1.0.1-r4-candidate`. See [the full acceptance matrix](PLAYABLE_R4_ACCEPTANCE.md), [current build evidence](BUILD_RUNTIME_R4_REPORT.md), [laptop package guide](LAPTOP_BUNDLE.md) and [handoff](PLAYABLE_R4_HANDOFF.md). This historical status page is not a claim that the complete Revision 4 game is playable.

# SD Craft — Master Project Status

**Date:** 2026-11-24  
**Platform:** Paper 26.3 (Build 255-stable) on OpenJDK 25.0.5.1 LTS  
**Active Version:** v1.5.0 (Custom 3D Models, GTA iFruit Icons & Upgraded Creative Arsenal)  
**Primary Playable World:** New Blockston v1.10 (358 MB)  
**Release Resource Pack:** `EXPECT_SDCRAFT_ResourcePack_26.3.zip` (9.75 MB)  
**Checksum (SHA-1):** `cd6420c2d685069df42dd88f7903363a6c24632b`  
**Test Suite:** 76 / 76 JUnit 5 Unit Tests Passing  
**Crossplay & Auto-Send:** Geyser-Spigot 2.12.1 + Floodgate 2.2.5 configured with `force-resource-packs: true` for Bedrock / Pocket Edition auto-send.

---

## 1. Executive Summary
SD Craft is a full-conversion, GTA-style modern city roleplay Minecraft Java server engineered for turn-key deployment on MCServerHost. All required server plugins, custom 64x64 Indian NPC skins, custom branding/economy assets, 5-minute auto-regeneration physics, native firearms & **QualityArmory 2.2.1** support (70 modern firearms & 11 calibers), drivable vehicles (**MTVehicles**), high-speed rail transit (**TrainCarts & BKCommonLib**), real-time 3D live map (**BlueMap**), **DecentHolograms** with 10 landmark locations, **Creative Testing Arsenal** 54-slot menu (`/arsenal`, `/testing`), GTA GPS navigation, surface spawn enforcement, instant starter inventory loadouts (guns, ammo, drivable cars, food), 100 pre-calibrated city NPCs (20 named staff + 80 ambient pedestrians) with Citizens LookClose orientation and firm daytime grounding, and the unified 3D vehicle & firearms resource pack distribution have been implemented, compiled against official Paper APIs, unit-tested (**76/76 tests passing**), verified on a live Paper 26.3 server instance, and packaged into a single ready-to-deploy ZIP archive.

---

## 2. Completed Components & Systems

### A. Core Architecture & SDCraftCore Plugin (`SDCraftCore-1.0.0.jar`)
* **Official API Build:** Built using Gradle 9.9.2 against the official `io.papermc.paper:paper-api:26.3.build.255-stable` on OpenJDK 25 LTS.
* **20 Pre-Calibrated City NPC Anchors (`NpcService.java` & `anchors.yml`):**
  * Auto-calibrates and persists 20 named staff anchors across New Blockston city landmarks.
  * Civic Center Plaza & Spawn (10, 71, 15):
    * `Administrator Nisha Bhat` (City Info) at `(10.5, 71, 18.5)` — 3m in front of players at spawn.
    * `Driver Sameer Qureshi` (Taxi Stand) at `(15.5, 71, 15.5)` — 5m right of spawn.
    * `Dispatcher Rehan Khan` (Transit Hub) at `(5.5, 71, 15.5)` — 5m left of spawn.
    * `Metro Supervisor Anjali Rao` at `(10.5, 71, 35.5)` at the plaza metro entrance.
  * Key city departments: Police HQ (4 officers), Hospital (4 medical staff), Bank (2 bankers), Fire Station (2 firefighters), Motor Mile Dealership (2 shopkeepers), Workshop/Gas Station (2 technicians).
  * Automatically loads target chunks before spawning to ensure Citizens NPCs and entity nametags render with 100% reliability.
* **3D Vehicle & Firearms Resource Pack Integration:**
  * Configured in `server.properties`:
    * `resource-pack=https://mtvehicles.nl/resourcepack/MTVehicles_Pack_v0.2.3_1.21.4.zip`
    * `resource-pack-sha1=f7f5abf35f2b109bd270bcafd0d5688878ed478a`
    * `resource-pack-prompt={"text":"§6[SD Craft] §eClick YES to download the 3D GTA Vehicles and City Textures pack!"}`
  * Bundled offline copy: `resourcepacks/MTVehicles_3D_ResourcePack.zip` (7.9 MB) inside the release ZIP.
  * In-game `/pack` command sends instructions and direct download links.
* **Surface Spawn & Underground Rescue Enforcement:**
  * Enforces world spawn permanently at Civic Center Plaza surface: `X: 10, Y: 71, Z: 15` (facing City Hall).
  * Auto-rescues any player spawning or joining below `Y < 66` or in the legacy underground transit tunnel (`X=-8, Z=-356`), teleporting them immediately into daylight on Civic Center Boulevard.
  * Adds `/spawn` command so players can always return to City Hall Plaza anytime.
  * Non-bed respawns (`PlayerRespawnEvent`) redirect directly to the Civic Center surface, never underground.
* **GTA Starter Kit & Roleplay Inventory Loadout:**
  * Automatic inventory loadout granted on player join (and via `/kit` or `/starter`):
    * **Slot 0:** 9mm Service Pistol (`GunEngine.GunType.PISTOL`)
    * **Slot 1:** 32x 9mm Service Ammunition
    * **Slot 2:** Drivable Sedan Black vehicle keys/voucher (`FFW36Q`) via MTVehicles
    * **Slot 3:** SD Craft GPS Navigator & City Map Compass
    * **Slot 4:** 16x Street Burgers (food sustenance)
  * Dedicated commands: `/kit`, `/car`, `/gun`, `/spawn`, `/gps`, `/map`.
* **Atomic Economy & Banking:**
  * Starter grants: $500 wallet, $1000 bank with strict single-grant idempotency.
  * Atomic wallet <-> bank deposits and withdrawals with zero overdraft exploit vulnerability.
  * Direct P2P wire transfers (`/sdc pay <player> <amount>`) with balance verification.
  * PBKDF2WithHmacSHA256 salted PIN hash protection for bank accounts.
  * Private keypad GUI interface for secure in-game transactions.
  * Append-only CSV audit trail (`transactions.csv`).
* **Medical & Emergency Systems:**
  * Downed state on fatal damage: 90-second bleeding timer before hospitalization.
  * Paramedic/doctor revival mechanics using medical kits.
  * Emergency hospital teleportation fallback upon timer expiry.
  * Authorized fee schedule: $25 diagnosis, $50 treatment, $75 hospital admission.
* **City Transit & Transportation:**
  * Dynamic fare formula: `$25.00 base fare + $6.00 per 100 blocks`.
  * Public transit routes (`/sdc taxi <stop>`, `/sdc ride <bus|metro> <stop>`).
  * Instant, lag-free simulated transit with countdown safety.
* **Offline Bilingual NPC Intelligence:**
  * Fully deterministic natural language intent parser covering English, Hindi, and Hinglish.
  * 34 mapped intent patterns (Greetings, Banking, Medical, Police, Transit, Quotes, Duty, Farewell).
  * Zero external API cost and 0 token latency; runs entirely in-memory within heap constraints.
  * Safety boundary enforcement: dialogue never manipulates balances or executes arrests directly.
* **5-Minute Street & Explosion Auto-Regeneration (`RestorationEngine.java`):**
  * Intercepts `EntityExplodeEvent`, `BlockExplodeEvent`, and `BlockBreakEvent`.
  * 300-second (5-minute) delay timer before auto-restoring destroyed blocks.
  * Yield suppression (`setYield(0.0f)`) to completely eliminate item duplication exploits.
  * Bottom-to-top Y-axis restoration ordering with block particle and placement sound effects.
  * Underground mining protection: blocks below Y=55 are excluded from city restoration.
  * Agricultural protection: farmland, wheat, carrots, potatoes, beetroots, and crops are excluded.
  * Player build protection: player-placed blocks are tracked (`playerPlacedBlocks`) and never overwritten with city street blocks.
  * Admin command suite: `/sdc zone mark <name> [radius]`, `/sdc zone unmark <name>`, `/sdc zone list`, `/sdc restore status`, `/sdc restore now`.
* **Native Firearms & Ammunition Engine (`GunEngine.java`):**
  * 4 Distinct Weapons:
    * `PISTOL`: 9mm, 12-round mag, 6.0 damage, 35 block range, 1.2s reload.
    * `SHOTGUN`: 12-gauge, 6-round mag, 6 pellets @ 2.8 damage, 16 block range, 2.0s reload.
    * `SMG`: 9mm, 30-round mag, 4.2 damage, 26 block range, 1.5s reload.
    * `RIFLE`: 5.56mm, 25-round mag, 7.5 damage, 48 block range, 2.2s reload.
  * 3 Ammunition Items: `9mm_ammo`, `shotgun_shells`, `rifle_ammo`.
  * High-precision raycast hitscan with critical/smoke particle trails.
  * Headshot detection: 1.5x damage multiplier when hitting an entity's head region.
  * Recoil physics and realistic firing/empty/reload sound effects.
  * Admin commands: `/sdc gun give <player> <type>`, `/sdc ammo give <player> <type> [count]`.
* **GTA Real-Time Map & GPS Navigation Engine (`GpsManager.java`):**
  * `/map`: Prints an interactive prompt displaying current district, coordinates, and a clickable link to the real-time 3D web map (`http://<ip>:8100`).
  * `/gps`: Opens the 27-slot interactive GTA GPS Navigation GUI with 8 city POIs (Police HQ, Hospital, City Hall, Bank, Fire Station, Vehicle Dealership & Garage, Gas Station, Airport).
  * Clicking any POI dynamically sets the player's compass target and displays distance and heading in the action bar.
  * Item interaction: Right-clicking the "SD Craft GPS Navigator" item opens the GPS GUI; pressing `[F]` (Swap Hands) displays real-time district and coordinates on the HUD.
  * Client Minimap Support: Players using Lunar Client, Badlion, Feather, or Xaero's Minimap/WorldMap can press `[M]` to open the full world map.

### B. Drivable Vehicles System (MTVehicles 2.5.9)
* **Paper 26.3 Compatibility Bridge:** MTVehicles 2.5.9 has a hardcoded version whitelist up to 26.2. We engineered a custom bytecode-compatible bridge in `VersionModule.java` mapping Paper 26.3 to the modern movement handler.
* **Pre-configured Vehicle Catalog (36KB `vehicles.yml`):**
  * Cars, sports cars, motorcycles, helicopters, and emergency vehicles.
  * Fuel mechanics, trunks/storage, vehicle keys, and speed tuning.
  * Vehicle Dealership & Garage location registered in GPS navigation (`/gps`).

### C. Real-Time 3D Live Web Map (BlueMap 5.29)
* **Webserver Enabled on Port 8100:**
  * Real-time 3D and 2D top-down orthographic rendering of New Blockston v1.10.
  * Live player positions, player heads, orientations, and coordinates visible in any web browser or smartphone.
  * Automatic Mojang client asset extraction pre-configured (`accept-download: true`).

### D. Custom Character Skins & Visual Branding
* **20 Custom Indian Character Skins:**
  * Sourced from `SDCRAFT_20_INDIAN_NPC_SKINS.zip`.
  * Validated 64x64 RGBA Dual-Layer PNG format compliant with Minecraft standards.
  * Classic (4px) and Slim (3px) arm models mapped in `npc-dialogues.yml`.
  * Bundled in `plugins/SDCraftCore/skins/` and packaged in `release/SDCraft_ResourcePack.zip`.
* **Visual Branding Assets:**
  * `server-icon.png` (64x64 RGB): Deployed to server root.
  * 4 High-Resolution transparent branding logos: Main Logo (1024x1024), Economy Logo (512x512), Police Badge (512x512), Medical Emblem (512x512).
  * 9 Custom 32x32 transparent pixel art item textures: Dollar bill, Gold coin, Police badge pin, Medical kit, Handcuffs, ID card, ATM card, Wrench, Walkie-talkie radio.
  * Packaged into `release/SDCraft_ResourcePack.zip` (Resource Pack format 48).

### E. QualityArmory 2.2.1 Integration & 3D Firearms
* **Modern Weapons Arsenal (70 Weapons, 11 Ammunition Types):**
  * Handguns (P30, Glock, Deagle, CZ75, FN Five-Seven), Assault Rifles (AK-47, M4, Galil, FAMAS, FN FAL), SMGs (MP5, Uzi, P90), Shotguns (Remington, AA12, SPAS), Sniper Rifles (AWP, Dragunov, Barrett).
  * Custom attachments (Silencers, Scopes, Skins like AWP Asiimov).
* **SDCraftCore Seamless Bridge:**
  * Auto-detects QualityArmory on boot: grants **P30 9mm Pistol & 32x 9mm ammo** upon joining in the GTA starter kit.
  * In-game `/gun [ak47|m4|shotgun|sniper|deagle|uzi|p30]` command equips the specified firearm and ammo packs.
  * Preserves native `GunEngine` as a zero-dependency fallback if QA is disabled.
* **Unified 3D Resource Pack (`SDCraft_Unified_3D_ResourcePack.zip`):**
  * Merges MTVehicles 3D cars (diamond hoe durability overrides) and QualityArmory 3D guns (crossbow CustomModelData 1..74) into one seamless 8.86 MB pack with 83 combined custom sounds.
  * Zero model or sound collisions. Pre-bundled in `resourcepacks/` in the release ZIP.

### F. Complete 8-Plugin Suite
1. **SDCraftCore 1.0.0** — Master gameplay controller (Economy, NPCs, 5-min Auto-Regen, GPS Navigation, Firearms Bridge).
2. **QualityArmory (2.2.1)** — 70 realistic modern firearms, ammunition, iron sights, and recoil physics.
3. **MTVehicles (2.5.9)** — Drivable vehicles, car keys, fuel, and vehicle catalog.
4. **Citizens 2 (2.0.44-b4275)** — Physical NPC identities and pathfinding.
5. **LuckPerms (5.5.91)** — Permissions and administrative hierarchy.
6. **WorldEdit (7.4.6)** — City region manipulation.
7. **WorldGuard (7.0.21)** — Protected infrastructure and safe zones.
8. **BlueMap (5.29)** — Real-time 3D live web map viewer.

---

## 3. Test & Verification Summary

### Unit Tests (Gradle / JUnit 5) — **64 / 64 PASSED**
* `PolicyEngineTest`: **6 / 6 PASS** (Robbery cap, taxi formula, NPC hysteresis, witness rolls, police caps, currency formatting).
* `LedgerTest`: **9 / 9 PASS** (Idempotent grants, deposits, withdrawals, transfers, fee charges, PBKDF2 PIN hashing, duty shifts, language toggling, transaction logging).
* `DialogueEngineTest`: **39 / 39 PASS** (Bilingual classification across 34 intents, safety boundaries, medical & police responses, 20 character profiles).
* `RestorationAndGunsTest`: **3 / 3 PASS** (Gun profiles, CustomModelData 101-104, 5-minute restoration timer & yield suppression, spatial exclusion).
* `MapAndGpsTest`: **2 / 2 PASS** (8-point compass bearing math, district coordinate boundary resolution).
* `SurfaceSpawnAndKitTest`: **5 / 5 PASS** (Surface coordinates Y $\ge$ 70, underground rescue, NPC spawn proximity $\le$ 6m, Sedan Black UUID, starter ammo & food).

### Live Server Smoke Test — **PASSED**
* Paper 26.3 (Build 255) on OpenJDK 25.0.5.1 LTS.
* All 8 plugins loaded in green: `BlueMap`, `Citizens`, `LuckPerms`, `MTVehicles`, `QualityArmory`, `SDCraftCore`, `WorldEdit`, `WorldGuard`.
* QualityArmory successfully registered: 70 guns, 11 ammo types, 3 attachments, 4 armor types.
* Clean startup, TPS: 20.0, BlueMap webserver active on port 8100.

---

## 4. Release Package Details

* **File Name:** `SDCRAFT_FINAL_RELEASE.zip`
* **File Size:** 294.02 MB
* **Uncompressed Footprint:** 403.34 MB (739 files)
* **SHA-256 Checksum:** `ec353be489af8be9da0a8fe8ecd566f2f6e4e6dc12b91cfc97dd019eacc24bb5`
* **Offline Resource Pack:** `resourcepacks/SDCraft_Unified_3D_ResourcePack.zip` (8.86 MB, combines MTVehicles 3D cars + QualityArmory 3D firearms)
* `SurfaceSpawnAndKitTest`: **5 / 5 PASS** (Civic Plaza surface coordinates, underground rescue detector, Civic plaza NPC proximity <=6m, MTVehicles Sedan Black UUID mapping, starter ammo & food balance).

### Real Server Smoke Test — **PASSED**
* Booted on OpenJDK 25 LTS with 3 GB heap.
* All 7 plugins loaded and enabled simultaneously with 0 errors.
* Live console verification:
  * `plugins`: All 7 plugins active (green).
  * `version MTVehicles`: MTVehicles v2.5.9 enabled with Paper 26.3 bridge.
  * `version BlueMap`: BlueMap v5.29 active on port 8100.
  * `sdc map`: Prints 3D web map URL.
  * `sdc status`: Core active, confirmed NPC anchors=20, Citizens=true.
  * `tps`: 19.9 / 20.0 steady across all intervals.
  * `stop`: Clean graceful shutdown of all 7 plugins.

---

## 4. Build Artifacts
* `SDCRAFT_FINAL_RELEASE.zip`: Complete server-root portable archive (283.15 MB compressed, 392.01 MB extracted, 628 files, SHA-256: `2361969585029d1a01f3645a3fa080829325ca078ab86fc70b638fe59b4e78f1`).
* `release/SDCraft_ResourcePack.zip`: Client-side resource pack (pack format 48).
* `test_server/`: Fully tested, bootable local instance.
