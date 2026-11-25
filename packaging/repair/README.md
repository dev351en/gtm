# GTM 1.0.5 HUD, NPC and passenger repair

This update addresses the approved four-corner HUD, original phone logos, nearby NPC conversation, population crowding and the traditional auto's three passenger places. It updates an existing reviewed **1.0.3 functional** or **1.0.4 repair** server. It is an update package, not a complete Minecraft/server installation or a production deployment.

The four-corner Java HUD is implemented by the **optional client component** in `client/`. Install the server update and that component together to see it. Ordinary Java clients can still join with the server resource pack and use the inventory-based phone. The exact corner layout and clickable overlay are not provided by that resource pack alone. A Bedrock equivalent has not been implemented or accepted.

Read `RELEASE_NOTES.md` for the precise acceptance scope and `SPEC_REPAIR_2026-11-25.md` for the evidence and remaining work. The complete Revision 4 game is not certified by this candidate.

## 1. Update the existing server

Use Python **3.10 or newer**, and retain the existing Java 25 runtime and launcher. Keep the complete extracted repair folder together. The updater preserves worlds, accounts, property/vehicle ownership, configuration and unrelated plugins.

1. Stop Paper and close its launcher. The updater refuses an active world lock or a listening server port.
2. Extract this repair ZIP into a separate folder.
3. From that extracted folder, supply the folder containing the existing `server.properties` and worlds:

**Windows:**

```bat
Update-GTM.bat "C:\path\to\existing\GTM-server"
```

**Linux/macOS:**

```bash
sh Update-GTM.sh /path/to/existing/GTM-server
```

The updater accepts only the fingerprinted 1.0.3, released 1.0.4, or this exact already-installed core. An unknown binary, checksum failure or unsafe path stops the update. Retain the backup ID printed on success. The existing portable launcher keeps its local resource-pack URL; other installations use this release's versioned HTTPS pack URL.

For an existing Geyser installation, append `--bedrock` to also update its pack and mappings. This opt-in supplies asset compatibility; it does not add or certify the four-corner Bedrock HUD.

Start the server normally. A GitHub push or download does not update a running Daytona server. The private host must be updated independently after its staging gates are met.

## 2. Enable the optional HUD on the Java client

Follow **`client/README.md`** for the pinned Minecraft 26.3, Fabric Loader and Fabric API versions. The client JAR belongs in the chosen Minecraft profile's `mods` folder, not the Paper server's `plugins` folder. Use a separate profile if you want to retain your ordinary unmodified client.

Join the updated server, complete the normal login and accept its resource pack. The HUD only activates after authentication and successful pack loading. Its values come from the server account and the actual player inventory.

| Screen position | Function |
| --- | --- |
| Top left | Nine real hotbar slots and selected item; normal number keys and scrolling still work. |
| Bottom left | Minimap sampled from loaded world terrain, with available service markers. |
| Top right | Wanted stars, wallet and bank balance supplied by the server. |
| Bottom right | Persistent clickable phone shortcut and vehicle information while driving. |

Use the client guide's phone/cursor keys, `/phone`, or right-click the actual phone item. The popup uses the original colourful brand art. Service transactions retain their existing server-side gates; some apps open the existing server inventory menu for their detailed actions. Full restyling of every transaction screen is not claimed.

## 3. Talk to NPCs and use vehicles

Right-click a nearby NPC to select it, then type **`// your message`** with a space after the slashes. The response appears in chat and an overhead speech bubble. Service staff keep their service menus; sneak-right-click selects conversation without opening that menu. Ordinary authenticated players no longer need an operator grant for dialogue. WorldEdit commands retain their distinct syntax.

The default dialogue provider is explicitly **offline/scripted**. The generative provider adapter is included, but no language model or paid service is installed or enabled by this update. To use an existing local Ollama or HTTPS provider, follow the configuration section in `SPEC_REPAIR_2026-11-25.md`. `/sdc status` and the Control Centre report the configured backend and last result. Provider failures fall back with a visible notice instead of leaving an indefinite loading state.

The traditional auto now has **one driver and three passenger places**. An ordinary guest can **right-click an unlocked auto to board a free passenger seat**, then press **Shift to exit**; this route was checked in the native client. Locked vehicles reject guests. The owner can toggle passenger access with `/car lock <vehicle UUID>`; `/car` opens the owned garage. W/S apply throttle and braking/reverse, A/D steer and Space brakes. Exit requires a clear safe standing place: if parking cannot release every occupant near a wall or other players, let the players who have exited walk clear before retrying. The included fleet audit records the actual supported capacity of every profile; rear seating/interiors for the wider car and bus catalogue remain separate unfinished work.

`/gun` opens native equipment. Right-click fires; sneak-right-click reloads using the matching ammunition. Safe zones, ownership and authentication remain enforced. Ambient NPCs designated as tough can retaliate; other pedestrians flee, and protected service staff remain protected.

## Control Centre

After Paper starts, open **Open-Control-Centre.bat inside the server folder**. On Linux/macOS:

```bash
python3 /path/to/existing/GTM-server/tools/open_control_centre.py --server /path/to/existing/GTM-server
```

The dashboard connects to `127.0.0.1:8765` and shows live status, NPC dialogue backend status, players, pack loading, logs and an owner command console. Its token is private. For an already updated running Daytona server, use the repository's `python tools/open_control_centre.py --daytona` with the existing owner configuration. That command opens a local SSH tunnel; it does not deploy or restart the server. The web JEEVA tab remains a local help guide, separate from the NPC generative adapter.

## Roll back

Stop Paper and its launcher, then use the recorded backup ID:

```bat
Update-GTM.bat "C:\path\to\existing\GTM-server" --rollback BACKUP_ID
```

```bash
sh Update-GTM.sh /path/to/existing/GTM-server --rollback BACKUP_ID
```

Rollback restores only files changed by this update and refuses to overwrite later edits. An interrupted transaction must be recovered using its receipt before another update. Remove the optional HUD JAR from the separate client profile to revert that client; the server updater never writes to a Minecraft profile.
