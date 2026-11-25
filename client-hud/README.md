# GTM City HUD — optional Java client component

This component implements the requested four-corner interface in the game:

| Position | Actual function |
| --- | --- |
| Top left | Nine real hotbar slots, selected item, health, armour and food |
| Bottom left | Live terrain minimap, north indicator, player heading and server markers |
| Top right | Current wanted stars, wallet and protected bank balance |
| Bottom right | Persistent phone button and an interactive phone popup with the existing custom brand logos |

**It is an optional client mod for Minecraft Java 26.3.** A server resource pack cannot provide this persistent renderer and mouse input by itself. The GTM server still accepts unmodified Java and Bedrock clients; those clients retain their server-supported interface. Installing the server repair does not install this mod on anyone's computer.

The client activates its replacement HUD only after the compatible GTM server confirms authentication and the required resource pack. On an ordinary server, before authentication, after logout, or when the state expires, the normal Minecraft HUD remains available.

## Install into a separate Minecraft profile

Use the following exact version set for this candidate:

| Component | Version |
| --- | --- |
| Minecraft Java Edition | `26.3` |
| Java runtime | `25` |
| Fabric Loader | `0.20.1` |
| Fabric API | `0.167.0+26.3` |
| GTM City HUD | `1.0.0` |

1. Install and launch Minecraft Java 26.3 through your normal licensed launcher, then close Minecraft and the launcher.
2. Download the [official Fabric installer](https://fabricmc.net/use/installer/). On its **Client** tab select Minecraft `26.3`, Loader `0.20.1`, and **Create Profile**. Fabric provides [Windows, macOS and Linux instructions](https://docs.fabricmc.net/players/installing-fabric/).
3. In Minecraft Launcher, open **Installations → the new Fabric profile → Edit**. Name it **GTM City HUD** and set **Game Directory** to a new dedicated folder, for example `C:\Games\GTM-HUD` on Windows or a new `GTM-HUD` folder under your home directory. This keeps its mods and settings separate. This is the [separate game-directory procedure documented by Fabric](https://wiki.fabricmc.net/player%3Atutorials%3Ainstall_mcl%3Awindows).
4. Create a `mods` subfolder inside that game directory. Put these **two JAR files** inside it:
   - `GTM-Client-HUD-1.0.0.jar` from this GTM release.
   - [`fabric-api-0.167.0+26.3.jar`](https://maven.fabricmc.net/net/fabricmc/fabric-api/fabric-api/0.167.0+26.3/fabric-api-0.167.0+26.3.jar) from Fabric's official Maven repository.
5. Launch the **GTM City HUD** profile. Join the updated GTM server, accept its resource pack and sign in normally. No operator permission is needed for the HUD or phone.

The Fabric API file's SHA-256 is:

```text
ec6c9dbd884d68ae071fdc96cbdd91f2a5256bf3085a3b457e475827b31cad19
```

The GTM JAR's exact SHA-256 and byte count are recorded in the included `build-report.json`. The source checkout generates that report at `client-hud/build/build-report.json`. Fabric's [mod installation guide](https://docs.fabricmc.net/players/installing-mods) explains how the profile's `mods` folder is loaded. The mod belongs in that **client** folder, not the Paper server's `plugins` folder. Third-party launchers should create an equivalent isolated Fabric 26.3 instance using their documented installation flow.

To remove the HUD, close Minecraft and remove `GTM-Client-HUD-1.0.0.jar` from this profile, or choose your ordinary Minecraft profile. This does not delete any GTM account, money, inventory, vehicle or server-world data.

## Controls and service behaviour

| Control | Result |
| --- | --- |
| `P` | Open the phone popup; press again outside its text field to close |
| Left `Alt` | Release the cursor for the HUD; click the bottom-right phone or a top-left hotbar slot |
| `Esc` | Close the phone/cursor overlay and resume mouse look |
| `1`–`9`, mouse wheel | Select the normal Minecraft hotbar slot |
| `M` | Switch the minimap between circle and rectangle |
| `/phone` or use the real phone item | Open the same client popup on a compatible authenticated server |

The GTM keys appear in Minecraft's Controls settings and can be rebound. While the GTM HUD is active, its default `P` action takes precedence over the vanilla Social Interactions shortcut without rewriting the user's saved bindings. On other servers, vanilla shortcuts continue to work.

The phone uses the server's actual enabled-app list. Click an app to see its detail, then **Open Service** to request the existing server service. Bank, shop, garage and other transactional services may open their established server inventory menus. Those transaction menus have not all been converted into client popup forms. Prices, ownership, permissions and purchases remain checked by the server.

**JEEVA in this popup is labelled “Local City Guide”.** Its private question box provides offline guidance about driving, guns, police, the map and the current account balances. It does not call a language model, invent missions or execute financial actions. Any separately configured server NPC conversation provider is a different service.

The minimap reads the terrain that Minecraft has already loaded. It is north-up and shows the player's current heading, real surface colours and the server's supplied markers. It refreshes a complete terrain tile about every 16 client ticks. Unloaded areas remain blank; underground rooms are not exposed. Circles and rectangles use the apertures measured from the existing native 128 frame art. These are world-derived pixels rather than a fixed city-map illustration.

When the server reports a driven vehicle, its speed, fuel or battery, body condition and occupied-seat count appear beside the phone. The phone cursor overlay does not pause a multiplayer world: stop safely before typing.

## Verification and limits

The component has been launched in an actual official Java 26.3 client with Fabric 0.20.1 and the pinned Fabric API, connected to an isolated Paper 26.3/SDCraftCore 1.0.5 server as an ordinary newly registered player. Native testing observed the four-corner HUD, real account balances, original-colour phone app logos, cursor clicks, normal slot selection, the server `/phone` route, phone-item route, a bank-service handoff and a private JEEVA reply using the current balances.

The native test found a default-key conflict and minimap-frame clipping defect. Both were fixed, rebuilt and rechecked in the running client. The full HUD acceptance checkpoint passed on client SHA-256 `b1bf80057b30e94c7d04b1d49ad06d442972f0cf0b441f710b5c513cfe92ab84` with core `23c0020eb0e54093feeccba4f7e72681f0cc2a7e2e7965ef7aa8a683ccfe97cc`. It also verified pre-login fallback, repeated `P` open/close, both map shapes, real slot selection, the command/item phone routes, bank-menu handoff and private guide input. There were zero rejected HUD snapshots, missing model textures, duplicate sprites or model-loading errors in that session through the HUD handoff.

The delivered server core is `17d9a549…`. Its subsequent change raises the NPC dialogue bubble above the actor's nameplate; the HUD bridge, vehicle, combat and console classes are unchanged. The [current repair record](../docs/SPEC_REPAIR_2026-11-25.md) documents that byte comparison and the separate final presentation check. The HUD screenshots retain their actual original checkpoint hashes.

The [native evidence record](../docs/repair-evidence/spec-hud-native-java.json) records exact client, server and pack hashes together. Unmodified F2 captures show the [complete HUD](../docs/repair-evidence/spec-hud-native-java.png), [phone](../docs/repair-evidence/spec-phone-native-java.png), [Bank detail and rectangular map](../docs/repair-evidence/spec-hud-bank-native-java.png), and [local guide](../docs/repair-evidence/spec-hud-guide-native-java.png). No generated image is used as acceptance evidence.

Current automated coverage is **18 passing JUnit tests**: bounded snapshot decoding, invalid or unknown app rejection, session expiry and replay handling, one-shot phone requests, all nine slot targets, 24 app targets, scaled corner layout, and circle/rectangle map clipping. These checks complement native screenshots; they do not replace a running-client test.

Known scope:

- This component supports **Java 26.3 only**. It is not a Bedrock add-on and does not implement touch controls or a native Bedrock HUD.
- Actual native testing used Linux with a software-rendered client. Windows/macOS native acceptance and other HUD-mod combinations have not been completed.
- The test desktop has no working audio output. Audio quality is not verified by the visual test.
- The optional mod does not change the server's authentication requirements, grant operator access, add client-side transaction authority or connect to an external AI provider.
- The persistent popup and guide are custom client interfaces; existing service transaction windows still use their server menus as described above.

## Build the exact JAR from source

Use a complete repository checkout, Python 3.11 or newer, and JDK 25. No image-generation tool or Java trust-store modification is required. From the repository root:

```bash
python3 client-hud/tools/build_verified.py --java-home "$JAVA_HOME"
```

On Windows PowerShell, where `JAVA_HOME` points to JDK 25:

```powershell
py -3 client-hud/tools/build_verified.py --java-home "$env:JAVA_HOME"
```

This is the reproducible release/CI build command. It downloads inputs from the official Mojang and Fabric repositories, checks every pinned fingerprint in `dependencies.lock.json`, compiles against the unobfuscated 26.3 client APIs, runs JUnit and writes:

- `client-hud/build/libs/GTM-Client-HUD-1.0.0.jar`
- `client-hud/build/build-report.json`
- `client-hud/build/test-results/verified/`

For an already populated build cache, `--client-root`, `--fabric-dir` and `--junit-console` may point to the verified inputs; fingerprints are still enforced. Minecraft binaries are compile inputs and are never put in the distributed mod.

The module also includes a Fabric Loom 1.19.4 / Gradle 9.8 build definition for normal development. The direct verified build above is the release path and does not rely on Gradle's Java process having outbound network access.

## Existing artwork and server boundary

The JAR includes 89 existing PNG assets, copied without modification: 32 original colourful 256 brand logos, 33 native 128 HUD elements and 24 native 128 service icons. `gtm-hud-art-provenance.json` inside the JAR records each source, pixel size and SHA-256. The component uses the original Quoggle, Amazzo, Flippit, ARKPay, Zomatoo and Swiffy logos; existing bank, vehicle, transport and other brand art is mapped to the corresponding service. No new logos, textures or resampled asset files are generated.

The bridge uses bounded UTF-8 JSON on `gtm:hud_hello`, `gtm:hud_state` and `gtm:hud_action`. State is scoped to a fresh authenticated login, expires on the client after 10 seconds without a refresh and clears on disconnect. App requests carry a login session and increasing sequence number; the server checks authorization and rate limits. Selecting a hotbar slot uses Minecraft's normal selected-slot packet. Wallets, inventories and purchases remain server-owned.

Implementation references: [Fabric HUD API](https://docs.fabricmc.net/develop/rendering/hud), [Fabric custom screens](https://docs.fabricmc.net/develop/rendering/gui/custom-screens), [Fabric networking](https://docs.fabricmc.net/develop/networking), and [Paper plugin messaging](https://docs.papermc.io/paper/dev/plugin-messaging/).
