# EXPECT SDCRAFT — Master Changelog & AI Developer Guide

> **Note for Future AI Agents & Developers (ChatGPT, Claude, Gemini, etc.):**  
> This file contains the complete, authoritative record of all changes, architecture decisions, coordinate registries, and operational instructions for the EXPECT SDCRAFT project. Read this file first before making changes to ensure full compatibility with the Paper 26.3 runtime, the custom SDCraftCore engine, and the existing city ecosystem.

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
