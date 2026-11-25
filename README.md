# GTM / EXPECT SDCRAFT

## Current checkpoint — 25 November 2026

This branch preserves the **SDCraftCore `1.0.3-r4-functional-candidate` compiled runtime**, native **128×128** asset packs, and its verification records. It also adds a laptop connector for the **existing Daytona server**. The corresponding latest core/launcher source was not recovered; the existing `source/` tree is retained as its earlier published checkpoint. Building that tree does **not** reproduce the recovered `1.0.3` binary.

### Choose the server you want to play

| Your intended server | Entry point | What it does |
| --- | --- | --- |
| The same existing Daytona server and its saved progress | [Start-Daytona.bat](Start-Daytona.bat), also available as [connect_daytona_server.bat](connect_daytona_server.bat) | Opens an SSH connection to the existing running server; reports READY after a real Minecraft status response and matching ping. |
| The separately saved portable laptop world | `Start-GTM-Java-Only.bat` inside `GTM_128_Laptop_Playable_26.3.zip` | Starts the bundled local Paper server and the dated public-world/workshop copy. It does not connect to Daytona. |

For Daytona, read [the laptop connection guide](docs/DAYTONA_LAPTOP_CONNECTION.md). The connector requires Python 3.10+, Windows OpenSSH Client, and the owner's existing local Daytona API credential. Keep credentials private. Once READY appears, open your matching Minecraft Java Edition client and join **`127.0.0.1:25565`**. The script does not open/sign in to the Minecraft client, deploy the recovered update, start a stopped sandbox, or restart Paper.

**The existing Daytona server must already be running the intended update. Pushing files to GitHub does not install them there.** Live Daytona deployment and a native Windows connection have not been verified. Do not run the local portable server and the Daytona connector simultaneously on port 25565.

### What this repository contains now

- [Recovered runtime payload](runtime/functional-r4/README.md): exact compiled core, Java/Bedrock art packs, mapping files, optional display bridge with its corresponding source/license, and laptop launcher artifacts.
- [Payload manifest](runtime/functional-r4/manifest.json): exact file sizes, SHA-256 values, provenance, and limits.
- [Editable native128 artwork payload](creative/delivery/), separate from the engine source.
- [Recovery/publication record](docs/FUNCTIONAL_BUILD_RECOVERY.md) and preserved [functional runtime report](runtime/functional-r4/documentation/FUNCTIONAL_RUNTIME_R4_REPORT.md).
- Earlier repository source, tests, tooling, and history, retained without claiming they rebuild the recovered binary.

**GitHub “Download ZIP” is a repository download, not an assembled playable server.** It contains the preserved runtime payload but does not include the complete laptop world, Paper installation, Windows Java runtime, or a configured private Daytona export. Large payloads may be stored as verified chunks. Assemble them with `python tools/assemble_functional_runtime.py --output dist/functional-r4`; see [the runtime guide](runtime/functional-r4/README.md#assemble-downloadable-artifacts). The release workflow can create tag `gtm-functional-r4-1.0.3` only after its checks pass; this README does not claim that release already exists. The complete owner package is named `GTM_128_Laptop_Playable_26.3.zip`; it is a separate previously saved deliverable, not a GitHub Release download.

### Verification and remaining work

The preserved evidence records **644 JUnit tests in 79 suites plus 155 domain assertions** for the lost source checkout, and an actual Linux Paper startup/authentication/resource-pack/clean-stop run. Those historical results are tied to the recorded artifact hashes; this publication did not rebuild the missing source.

The new Daytona connector passed **39 offline tests** using synthetic responses/processes. They cover credential handling, permitted request scope, status parsing, readiness failures, and cleanup of its own SSH process. They do not establish native Windows execution or a live connection to Daytona.

The runtime includes traditional, electric, and cargo auto-rickshaws. Functional asset behavior depends on the enabled profile and appropriate in-game property, backing blocks, supplies, or commissioned routes. Native Java/Bedrock rendering, every model in every client, the complete furnished city/campaign, and current private-server compatibility remain open. See the [functional inventory](runtime/functional-r4/documentation/FUNCTIONALITY_INVENTORY_R4.md).

**Do not copy the fresh workshop configuration over an existing server.** It changes prices, property parcels, service locations, feature flags, and limits. Preserve the target's world, accounts, permissions, authentication, keys, and progress, and inspect the [runtime installation boundaries](runtime/functional-r4/README.md#existing-server-installation-boundary) before any update.

---

## Historical README — preserved earlier checkpoint

The content below is retained for project history. Its old download hashes, test counts, and deployment statements describe that earlier checkpoint; use the current section and recovered payload manifest for this publication.

# EXPECT SDCRAFT

EXPECT SDCRAFT is a GTA-inspired Minecraft city-roleplay server for Paper 26.3.
The project combines a persistent city world, custom economy and mission logic,
NPC services, vehicles, phone-style menus, transport, medical workflows, crime,
duty systems, DecentHolograms across 10 locations, a 54-slot Creative Testing Arsenal,
and a unified custom resource pack featuring Fresh Animations 1.11.2 + All Extensions.

> 📖 **Developers & AI Agents (ChatGPT / Claude):**  
> See [CHANGELOG.md](CHANGELOG.md) for the authoritative changelog, system architectures, coordinate registries, and operational instructions.

## Downloads

### Required resource pack

[Download EXPECT SDCRAFT Resource Pack 26.3](https://raw.githubusercontent.com/dev351en/gtm/main/resource-pack/EXPECT_SDCRAFT_ResourcePack_26.3.zip)

- SHA-1: `b0d7f272c6bb2b7084c05b5874920f7aca2bbd86`
- SHA-256: `ecd789f6cba84f9a19200553a23d3840436dbae2742fdb05a5d71ac3da7a5560`
- Size: 9,917,299 bytes (1,674 files)
- Minecraft resource-pack version: `97.1`

The server configuration uses that exact GitHub raw URL and requires players
to accept the pack (`require-resource-pack=true`).

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
- 24 validated plugin integrations
- **76 SDCraftCore automated tests** (100% passing on JDK 25)
- 38/38 audited original service coordinates
- 100 configured NPC identities with Citizens `LookClose` dynamic tracking and daytime grounding
- 10 DecentHolograms landmarks across city districts
- Creative Testing Arsenal GUI (`/arsenal`, `/testing`, Testing Star)
- Geyser & Floodgate Bedrock / Pocket Edition auto-send integration (`force-resource-packs: true`)

The exact portable server archive reached `Done`, reported all plugins,
registered `SDCraft Wallet` with Vault, connected MTVehicles to that wallet,
reported a 100-person population policy with 100 anchors, and enabled
TrainCarts 2.0.5 with its required BKCommonLib 2.0.6 dependency.

## Key systems & features

### 1. DecentHolograms across 10 City Landmarks
High-visibility, neon-formatted bilingual floating holograms installed at Spawn Welcome, City Hall, Police HQ, General Hospital, Central Bank, Motor Dealership, Metro Station, Gas Station, Fire Rescue, and Testing Arsenal.

### 2. Creative Testing Arsenal (`/arsenal`, `/testing`)
Instant testing suite providing access to all 7 drivable MTVehicles, 70+ QualityArmory firearms, ammunition, city equipment, currency grants, and landmark teleports. Running `/testing` activates Creative mode, flight, godmode, grants $10,000 cash, gives the right-clickable Arsenal Star, and opens the menu.

### 3. Hardened NPC Grounding & Bilingual Dialogues
All 20 named service staff have Citizens `LookClose` orientation enabled (tracking players within 6 blocks), disabled collision and gravity to prevent displacement, invulnerability, and GTA-themed chat boxes with sound effects and Action Bar prompts.

### 4. Fresh Animations 1.11.2 & All Extensions (Modrinth 26.3)
Fully integrated Fresh Animations 1.11.2 with all 7 official extensions (Details, Objects, Emissive, Spiders, Creepers, Quivers, Player) bundled alongside 3D vehicles, guns, currency, and uniform textures.

### 5. Geyser & Floodgate Bedrock / PE Crossplay
Crossplay enabled for Bedrock and Pocket Edition players with automatic `.mcpack` server distribution configured via `plugins/Geyser-Spigot/config.yml`.

## Repository layout

- `CHANGELOG.md` - comprehensive version history, architecture notes, and guide for AI agents
- `resource-pack/` - direct-download unified resource pack and hash details
- `downloads/` - privacy-sanitized world archive through Git LFS
- `source/` - SDCraftCore Java source and automated JUnit 5 tests
- `config/` - safe server, DecentHolograms, Geyser, TrainCarts, and SDCraftCore configuration examples
- `plugins/` - plugin configurations, testing stubs, and compiled SDCraftCore plugin
- `tools/` - Python utilities for building merged packs, fetching animations, and generating holograms
- `docs/` - implementation status, feature matrix, plugin checklist, and verification gates

## Server resource-pack configuration

```properties
resource-pack=https\://raw.githubusercontent.com/dev351en/gtm/main/resource-pack/EXPECT_SDCRAFT_ResourcePack_26.3.zip
resource-pack-sha1=b0d7f272c6bb2b7084c05b5874920f7aca2bbd86
resource-pack-id=04332dfe-5f85-5c4f-84cc-5609be67b115
resource-pack-prompt={"text":"§6§l[SD CRAFT SMP] §eMandatory Server Pack Required!\n§fIncludes §aFresh Animations 1.11.2§f, §bAll Extensions§f, §63D Vehicles§f, and §cFirearms§f.\n§eClick §aYES §eto download and enter the SMP."}
require-resource-pack=true
```

## Full server archive

The complete host-upload archive is intentionally not committed to this public
repository. It contains third-party plugin JARs whose licenses and distribution
terms differ. The local tested artifact is named:
`EXPECT_SDCRAFT_ARSENAL_HOLOGRAMS_2026-11-24.zip`  
(SHA-256: `dd0de9deb79703fa24b8a879dd5ee60f398ac8837ef37dfc33fdfd1dbad1dfde`)

## Safety and licensing

Never overwrite an Aternos backup or live host without a fresh backup. Files
from third-party projects remain governed by their respective licenses. No
credentials, login databases, API keys, or private player records belong in
this public repository.
