# GTM server-only crossplay implementation (candidate)

This branch replaces the Fabric-required four-corner phone/HUD path with the existing **server-controlled interface**. No client mod is required for Java or Bedrock users to access phone services.

## What changed in maintained server code

- The plugin no longer starts `GtmClientHud` or registers its Fabric-only messaging handshake. A client HUD mod is not an installation requirement and does not control any server action.
- `/phone` and the existing phone item always call the same authenticated `GtmPhoneApps` inventory flow. Clicking a service still goes through the server's original access checks, session ownership, balances and purchases.
- `phone.crossplay-safe` defaults to **true even when absent from an upgraded existing config**. It disables Java-specific inventory-font backgrounds, custom item-model icon requirements and HUD font glyphs. Phone apps get distinct vanilla icons and readable titles/lore.
- The vanilla scoreboard sidebar retains wanted stars, wallet and bank. The server map item remains the map interface; the standard hotbar stays in its native position. These controls work without a Java client renderer.
- Existing vehicle physics, passenger boarding, guns, NPC navigation/combat, authentication, persistent records and AI fallback remain server-side. This branch **does not** rewrite or certify those mechanics.

## Installation contract

Update the **server** after a stopped-server, backed-up staging rehearsal. This is a separate server-only **1.0.6 candidate**; do not install the older 1.0.5 ZIP in its place. Java players join with their standard Minecraft installation; Bedrock/mobile players use the compatible Geyser/Floodgate bridge.

1. Extract `GTM_Server_Only_Crossplay_1.0.6.zip` into a new folder. Keep the extracted files and subfolders together.
2. Stop Paper and the launcher completely. Preserve your latest world and player-data backup.
3. From inside the extracted folder, point the updater to the *existing server root*, which already contains `server.properties` and `world`:

   **Windows:** `Update-GTM.bat "C:\\path\\to\\your\\GTM-server"`

   **Linux/macOS:** `sh Update-GTM.sh /path/to/your/GTM-server`

4. On an **existing Geyser/Floodgate server**, append `--bedrock` to update the Bedrock asset pack and custom mappings. This does not install Geyser or Floodgate where they are absent.
5. Start Paper and join as an ordinary player. Test the vanilla inventory phone using `/phone`; you do not need Fabric, any client JAR or a modded launcher.
6. Save the updater's backup ID. To roll back after stopping Paper, run the same updater with `--rollback BACKUP_ID`.

**Daytona and the production world are not changed by a GitHub PR, release asset or download.** Do not deploy this candidate there until crossplay staging passes. Bedrock pack delivery and Java pack delivery must be validated separately. No player installs a Fabric, Forge or NeoForge mod.

Use `/phone` to open the menu. Select an app using the normal inventory controls. To get a terrain map, choose Maps in the phone; for the auto, use normal use/boarding controls and the existing `/car` menu. Server HUD data uses supported scoreboard/actionbar elements.

The Java/BEDROCK menus will **not have identical pixels**. With no client code, neither server plugins nor resource packs can arbitrarily move all nine vanilla hotbar slots to the top-left, keep a mouse-clickable phone pinned to the bottom-right of every screen, or guarantee a live corner minimap on every vanilla client. This branch prioritizes shared interactions and honesty over an impossible matching screenshot.

### Configuration

```yaml
phone:
  crossplay-safe: true
```

The missing key is treated as `true` to protect existing installations. Keep the legacy client-only HUD jar out of the recommended client setup. `phone.crossplay-safe: false` only enables legacy Java-oriented font/item-model customization; it is not advised for crossplay servers.

## Verification and gates

`CrossplayPhonePolicyTest` exercises default safety, legacy opt-out and distinct vanilla menu icons. Java server tests and release packaging must run independently on GitHub Actions, which uses a Java 25 toolchain. The repository is **not** considered crossplay accepted until real vanilla Java and real Bedrock clients pass the same smoke test in one staged world:

1. A normal non-op player on each edition authenticates and opens `/phone` or the server phone item, without client mods.
2. Both can open Maps, Bank, Garage and one authorized purchase/service route without losing balances or session rights.
3. Both see wanted/money sidebar text and use map/dashboard items with native controls.
4. One Java and one Bedrock account can board the same unlocked auto and drive, exit and reconnect while seats and ownership remain correct.
5. Each edition can equip/fire/reload a legitimate weapon and talk to an NPC. Protected civilians/staff and safe zones retain their existing rules.
6. Test with a missing/declined resource pack: gameplay still works and menus remain readable using vanilla icon fallbacks.
7. Shutdown preserves all records and an updater rollback restores the pre-upgrade snapshot.

**Not claimed:** this commit has not yet been deployed to Daytona, tested on an actual Bedrock client, validated on the user's Windows launcher, or converted the Bedrock UI into native forms. This is a server-side source candidate for verification, not a certified full GTA release.
