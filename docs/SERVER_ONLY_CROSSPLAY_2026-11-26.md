# GTM 1.0.7: original models on unmodified Java + Bedrock clients

**Status: source/build candidate. Not certified on real Bedrock hardware yet.**

The goal is a Paper server that owns gameplay, while both Minecraft editions download their matching **server-delivered resource pack**. A resource pack is *not* a client-side Java mod. The server cannot display custom PNGs or 3D geometry if a client has not loaded the textures/models; it must distribute the packs and validate the mappings.

## What 1.0.7 fixes

- `/phone` and the existing phone item still open authenticated, server-owned inventory menus and invoke the actual service handlers. No Fabric handshake is needed.
- **All original phone logos are restored:** each clickable icon is an actual `minecraft:paper` stack with its namespaced `minecraft:item_model` component. Java reads `assets/gtm/items/*.json` from the delivered Java pack; Geyser maps the *same base item + model ID* to a custom Bedrock item in `gtm_native128.json`. Bedrock's pack supplies its texture and attachable. Do **not** turn these into generic chests/compasses/minecarts: doing so breaks the mappings.
- On Java, custom font-based phone backgrounds and wanted glyphs activate **only after that player's Java resource pack loads**. Bedrock uses a compatible inventory title and plain HUD text; the custom item artwork remains mapped.
- The existing server-owned phone, guns, cars, NPC behavior, property rights, purchases and money stay in the Paper plugin. This patch does not make untested gameplay suddenly proven.
- The build checks **all Geyser v2 definitions** for valid Java model references, Bedrock icon PNGs and attachable geometry, including the 24 phone apps and HUD assets. Missing models now fail CI instead of silently shipping replacements.

## Install on a stopped staging server

1. Extract `GTM_Server_Only_Crossplay_1.0.7.zip`. Keep everything together.
2. Stop Paper/Daytona and back up the complete server, including worlds, inventories and plugins.
3. Run `Update-GTM.bat "C:\path\to\your\GTM-server" --bedrock` from inside the extracted folder (Windows) or `sh Update-GTM.sh /path/to/server --bedrock` (Linux). Omit `--bedrock` only on a Java-only server. This update requires an existing Geyser installation and copies the Bedrock pack and mappings into its directories.
4. Configure Geyser: under `plugins/Geyser-Spigot/config.yml`, set `enable-custom-content: true` in the relevant Geyser configuration section. Restart Paper/Geyser so mappings are registered. Allow the client to download the server resource packs on connection.
5. Run the included read-only check: `python tools/check_geyser_setup.py "C:\path\to\your\GTM-server"`. Fix any blockers before testing. The check will also explain whether a Bedrock display-entity renderer is missing.
6. Join as a normal Java and Bedrock player **without any client mod**, open `/phone`, and check actual original logos, models and app clicks on both platforms.
7. Retain the updater's backup ID. To reverse a stopped-server update, run the updater with `--rollback BACKUP_ID` and restore the server backup if needed.

The server's Java `resource-pack` URL/SHA are set by the updater; the `--bedrock` path installs the Geyser `.mcpack` plus custom mappings. Geyser does not convert Java packs automatically. The installed Geyser version must support its v2 item-model mappings. Test resource-pack acceptance with real clients; **a passing file audit is not a network/client test**.

## Vehicle, furniture and weapon models

Items held or shown in inventory have a defined Java/Bedrock mapping. **Moving 3D ItemDisplay entities are a different issue:** vanilla Bedrock has no Java ItemDisplay entity, and Geyser's base item mappings alone do not guarantee display-entity rendering. GTM uses ItemDisplay for vehicle/body visuals, so a compatible **server-side Geyser display renderer/extension** and real Bedrock gameplay tests are required before saying its vehicles appear correctly for Bedrock players. This is still no client-side mod.

One potential server extension is [GeyserDisplayEntity](https://github.com/GeyserExtensionists/GeyserDisplayEntity). It reports support for Geyser 26.2, but its latest release has **not been validated with GTM's Geyser 26.3 setup**. Do not install an unverified extension into production as a purported fix; test a pinned compatible build in staging and check model scale, yaw, canopy, wheel animations and passenger synchronization. Java-side ItemDisplay visuals continue to work using the Java pack.

For native tracks/railways, Paper plugins can operate rail blocks/track state and modelled train entities on the server, with edition-specific assets. That is the same architecture: logic stays server-side; textures and 3D geometry are rendered from packs the clients accept.

## What is still not possible without a client mod

Neither edition allows a Paper plugin to freely move the nine-slot vanilla hotbar to the upper left, pin a fully mouse-clickable phone to arbitrary screen coordinates, or guarantee a live corner minimap. GTM instead uses the normal hotbar, inventory-based phone, sidebar/actionbar and map items. Java gets a custom inventory skin when its pack is accepted. Bedrock's standard inventory remains usable with the original mapped app icons.

## Acceptance gates

Static model reference integrity and Java 25 tests are checked in CI. Release certification remains blocked until two normal non-op players, one on vanilla Java and one on Bedrock, demonstrate:

1. Actual original phone logo textures and functioning clicks, including Bank, Garage, Maps, equipment and permissions on both clients.
2. Actual visible and animated three-dimensional vehicle and furniture models (not paper or invisible displays) on Bedrock, with compatible server-side display support.
3. A traditional auto driven with one driver and three passengers; fifth player rejected; safe exit and reconnect from both editions.
4. Equipped gun models, correct server damage/reload, NPC conversation and retaliation/fleeing as designed.
5. Java and Bedrock pack delivery, acceptance, reconnect, operator restart and rollback on the user's actual server.

This branch changes no world, ownership database, account, remote Daytona instance or production server. It is a repair candidate, not a certification that all remaining GTM content works.
