# GTM local laptop candidate

The portable tooling assembles a **new private local server folder**. It does not contact Daytona, start a tunnel, deploy to a protected sandbox, accept the Minecraft EULA, invent an operator, or migrate player UUIDs. A runnable candidate and a completed Revision 4 game are separate claims.

## Two source profiles

| Profile | Input | Identity and data behavior |
|---|---|---|
| `private_stopped_server_copy` | An existing stopped private server directory | Preserves its `online-mode`, world, player identities, accounts, permissions and plugin data. Refuses a live world lock, changing source files, symlinks and conflicting login providers. |
| `public_world_2026_11_23_fresh_accounts` | Exact pinned sanitized public world ZIP | Starts fresh accounts on the dated public city snapshot. Requires an explicit online/offline mode choice. Makes no claim to contain the current Daytona world or private account data. |

Both modes require the current rebuilt core, the pinned Paper runtime and an explicit final Java resource pack. An old core without the built-in authentication classes and commands is rejected. The builder only writes to a new directory outside the repository. Preserve the original private export separately as rollback.

The pinned public world uses `world/dimensions/minecraft/overworld/region`. The tools also recognize the legacy `world/region` layout. They do not rearrange region files or generate a replacement city when the expected world is absent.

## Acquire pinned inputs

`packaging/dependencies.lock.json` records exact sizes, strong hashes, original metadata sources and allowed download/redirect hosts. The bootstrap tool does not select a moving latest version. Files already present in its cache are reverified; it refuses mismatched cache files and Git LFS pointers.

```sh
python tools/bootstrap_laptop_dependencies.py \
  --cache /private/gtm-inputs \
  --ids paper vault public-world windows-java25
```

The Windows runtime is the original Temurin x64 Java 25 archive. Its legal files remain inside the bundle. A Linux or macOS user can use the shell launcher with their own Java 25 installation. Python and Gradle are **builder dependencies**, not laptop runtime dependencies.

For a private owner installation, the optional `minecraft-bundler` input caches the exact original Mojang dependency named by the pinned Paper JAR. Pass it with `--minecraft-bundler /private/gtm-inputs/mojang_26.3.jar` to avoid that first-start download. This cache is verified against Paper's embedded SHA-256. It does not accept the EULA, does not include a game client and must not be published as a public server distribution.

Optional crossplay inputs are separate:

```sh
python tools/bootstrap_laptop_dependencies.py \
  --cache /private/gtm-inputs --ids geyser floodgate
```

The current lock records Paper 26.3 build 255, Geyser 2.12.1 build 1308 and Floodgate 2.2.5 build 141. Geyser's descriptor reports `2.12.1-SNAPSHOT`; the exact build and SHA-256 remain pinned. These downloads and static configuration are not a real-client crossplay test.

## Build a new public-world candidate

Build and test the Java core and merged runtime packs first. Use their final bytes, not an older bundled JAR or the source-art archive. Adjust only filesystem paths in this example:

```sh
python tools/build_laptop_bundle.py \
  --public-world /private/gtm-inputs/EXPECT_SDCRAFT_PUBLIC_WORLD_2026-11-23.zip \
  --online-mode false \
  --candidate source/build/libs/SDCraftCore-1.0.1-r4-candidate.jar \
  --paper /private/gtm-inputs/paper-26.3-255.jar \
  --plugin /private/gtm-inputs/VaultUnlocked-2.20.3.jar \
  --resource-pack build/runtime-packs/GTM_Runtime_128_Java.zip \
  --windows-runtime /private/gtm-inputs/OpenJDK25U-jre_x64_windows_hotspot_25.0.5.1_2.zip \
  --javac /path/to/java25/bin/javac \
  --output /private/GTM_Laptop_Candidate \
  --archive /private/GTM_Laptop_Candidate.zip
```

The explicit fresh offline profile uses the core's local authentication guard. It does not authenticate by player name or IP. Existing identities that lack an enrolled credential, protected names and operators require local-console enrollment. The console command is `gtmauth enroll <online-player>`; the player chooses the passphrase inside that enrolled connection. Account records and password hashes remain separate. Do not paste a password into the server console.

For crossplay, add both verified plugin paths, `--bedrock-pack` with the final merged `.mcpack`, and `--geyser-mappings` with the reviewed runtime mapping JSON. The fresh Geyser configuration follows its pinned configuration schema 12, uses Floodgate authentication and binds its TCP/UDP port 19132 to loopback. The pack and mapping inputs are copied with recorded integrity hashes. A private imported Geyser configuration is preserved; if it is not already a reviewed loopback profile, the builder stops instead of rewriting identity/key settings.

## Copy an existing private server safely

Pass `--stopped-server /private/stopped-export` instead of `--public-world`; omit `--online-mode`. The builder checks world session locks, hashes all source files, copies them, verifies the source and copy, replaces only the copied core, applies the documented local network/pack/logging settings, and checks the original again before finalization.

It preserves worlds, player UUIDs, balances, inventories, vehicle ownership, permission data, Floodgate keys and authentication stores. It never restores an older account file over newer transactions. Existing SimpleLogin, AuthMe or LoginSecurity installations require a deliberate authentication migration; the builder refuses them rather than dropping their databases or allowing first-claim account takeover.

The local copy binds Paper to `127.0.0.1`, disables RCON/query and password-command logging, and uses the exact bundled pack through its own loopback HTTP server. Every configuration difference is recorded in `launcher/build-report.json`. Original server files are unchanged.

## Startup behavior

Run `Start-GTM.bat` on Windows or `sh Start-GTM.sh` on Linux/macOS. Both resolve their own extracted folder and run a compiled Java launcher. The Java launcher checks:

- Java 25, immutable JAR/runtime/pack SHA-256 values and unexpected plugin JARs;
- the existing city world, region layout, session lock and unchanged authentication mode;
- disk headroom, heap versus physical memory and port conflicts;
- a matching local resource-pack URL and SHA-1;
- Geyser TCP and UDP port availability when that optional profile is included.

The pack HTTP server exposes one exact ZIP path, accepts GET/HEAD only and cannot browse the filesystem. It exits with the server. The launcher prints readiness only after Paper's actual `Done` line. That line proves server startup, not every gameplay requirement.

No fresh public input has an accepted EULA. The first start links the official EULA and requires the owner to type `I ACCEPT`. The builder never supplies that acceptance. `--accept-eula` is an explicit operator option, not a default launcher flag. `--check` performs preflight without starting Paper; exit code 2 means EULA acceptance remains outstanding.

Enter `stop` in the local console for a clean save. A shutdown hook requests that same graceful stop. Before each launch, the previous `logs/latest.log` is copied into `launcher/log-history`; only the launcher's ten retained copies are rotated. Minecraft and plugin data are never included in this log rotation.

Paper's first boot may download its official Minecraft libraries. The package does not contain a Minecraft client or a Microsoft account. Starting a server does not sign the user into the game. Public/LAN hosting is a separate reviewed networking profile; these scripts never start Ngrok, Playit or SSH tunnels.

## Verification and evidence

Run the focused offline fixtures with a genuine Java 25 compiler:

```sh
GTM_TEST_JAVAC=/path/to/java25/bin/javac \
  python -m unittest discover -s tools -p test_laptop_bundle.py -v
```

The fixtures cover strong-hash rejection, unresolved LFS pointers, HTTPS host restrictions, archive traversal/Windows path collisions, plugin identity/dependencies, old-core rejection, held world locks, private-source/account-byte preservation, auth-mode refusal, port conflicts, EULA behavior and the actual launcher HTTP/process/clean-stop lifecycle. Their tiny process is explicitly a launcher fixture, not a Minecraft server. Real Paper boot, Windows execution, Java/Bedrock clients and gameplay acceptance must be reported separately.

The source code for the launcher is `packaging/laptop/GtmLauncher.java`. The builder compiles it with `javac --release 25` and includes the resulting JAR. `launcher/integrity.sha256`, `dependency-lock.json` and `build-report.json` travel with every bundle. Do not edit the integrity hashes to conceal a failed check; rebuild from trusted final inputs.

The bundle also includes a `documentation/` snapshot with the acceptance matrix, handoff, authentication and state recovery guides, build evidence, public-world site survey, and native 128 generation report. Start with `PLAYABLE_R4_ACCEPTANCE.md` for the concrete gameplay still missing. `documentation/SHA256SUMS` records the exact included evidence files. The final archive hash belongs in the external delivery receipt so the archive does not try to contain its own hash.

## Original upstream references

- [Paper getting started and Java requirement](https://docs.papermc.io/paper/getting-started/)
- [Pinned Paper metadata](https://fill.papermc.io/v3/projects/paper/versions/26.3/builds/255)
- [Minecraft EULA](https://www.minecraft.net/en-us/eula)
- [Geyser setup and current transport requirements](https://geysermc.org/wiki/geyser/setup/)
- [Geyser resource packs](https://geysermc.org/wiki/geyser/packs/)
- [Geyser configuration source](https://github.com/GeyserMC/Geyser/blob/d2cf20058c6c875f7036deb6f6c59e0c39775199/core/src/main/java/org/geysermc/geyser/configuration/GeyserConfig.java)
- [Daytona filesystem operations for a separately authorized private export](https://www.daytona.io/docs/en/file-system-operations/)

Third-party files retain their original terms. This tooling prepares a private owner copy; it is not authorization to publish a server archive or bundle a Minecraft client.
