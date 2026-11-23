# SD Craft plugin upload checklist

The portable release contains 20 valid Paper plugin JARs. Each JAR opens as a
valid ZIP/JAR and contains a Paper or Bukkit plugin descriptor.

| File | Server plugin name | Version |
|---|---|---|
| `bluemap-5.29-paper.jar` | BlueMap | 5.29 |
| `Citizens-2.0.44-b4275.jar` | Citizens | 2.0.44 build 4275 |
| `ClearLag-2.0.3.jar` | ClearLag | 2.0.3 |
| `CommandPanels-4.2.5.jar` | CommandPanels | 4.2.5 |
| `DecentHolograms-2.10.2.jar` | DecentHolograms | 2.10.2 |
| `DreamDisplays-1.10.10.jar` | DreamDisplays | 1.10.10 |
| `GSit-3.8.0.jar` | GSit | 3.8.0 |
| `LuckPerms-Bukkit-5.5.91.jar` | LuckPerms | 5.5.91 |
| `MTVehicles.jar` | MTVehicles | 2.5.9 |
| `PlayerCorpses-1.0.0.jar` | PlayerCorpses | 1.0.0 |
| `ProtocolLib-5.5.0-dev-2026-11-22.jar` | ProtocolLib | 5.5 development build |
| `QualityArmory.jar` | QualityArmory | 2.2.1 |
| `SDCraftCore-1.0.0.jar` | SDCraftCore | 1.0.0 |
| `SimpleLogin-1.16.7.jar` | SimpleLogin | 1.16.7 |
| `SimpleRevive-1.5.0.0.jar` | SimpleRevive | 1.5.0.0 |
| `SkinsRestorer-15.12.6.jar` | SkinsRestorer | 15.12.6 |
| `SmoothElevator-1.4.jar` | Elevador | 1.4 |
| `VaultUnlocked-2.20.3.jar` | Vault | 2.20.3 |
| `worldedit-bukkit-7.4.6.jar` | WorldEdit | 7.4.6 |
| `worldguard-bukkit-7.0.21.jar` | WorldGuard | 7.0.21 |

The `/plugins` command shows descriptor names, so SmoothElevator appears as
`Elevador` and VaultUnlocked appears as `Vault`.

## Correct host upload

1. Stop the server and create a fresh host backup.
2. Extract the release into the server root. The server root must directly
   contain `plugins/`, `world/`, `server.properties`, and
   `paper-26.3-255.jar`; do not leave them inside an extra enclosing folder.
3. Confirm all 20 JARs exist in the host's root-level `plugins/` folder.
4. Start with Java 25 and Paper 26.3 build 255.
5. Wait for the console to print `Done`, then run `plugins` in the console.
6. If fewer than 20 load, download `logs/latest.log`; the first `ERROR`,
   `SEVERE`, `Could not load`, or `Unknown/missing dependency` line identifies
   the host-side problem.

Do not upload this release over a running server. Do not overwrite the Aternos
backup.

## Previously discussed but not server plugins

- VoxelMap Updated is client-side Fabric software, not a Paper server plugin.
- Invisible Item Frames did not provide a compatible Paper 26.3 build.
- Placeable Items did not provide a compatible Paper 26.3 build.

Those three are intentionally absent rather than disguised as working server
plugins.
