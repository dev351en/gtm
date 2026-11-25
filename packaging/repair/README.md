# GTM 1.0.4 runtime repair

This package updates an existing **1.0.3-r4-functional-candidate** GTM server. It contains the repaired plugin, matching native128 resource packs, a verified updater, and the local Control Centre opener. Keep the complete extracted package together.

**Acceptance status: draft, 25 November 2026.** Build, regression, server HTTP and updater checks have passed. Native Java client testing is in progress after correcting an atlas defect found during that test. Bedrock client testing is not complete. See `RELEASE_NOTES.md` for the current verification boundary; this package is not yet declared a fully accepted Java/Bedrock release.

## Install into your existing server

Use Python **3.10 or newer**. Keep your existing Java 25 server runtime and launcher. The updater preserves worlds, accounts, owned assets, configuration and feature flags.

1. Stop Paper and close its launcher. The updater refuses a running server.
2. Extract this repair ZIP into a separate folder.
3. Run the updater from the extracted repair folder, supplying the folder containing your existing `server.properties` and worlds.

**Windows:**

```bat
Update-GTM.bat "C:\path\to\existing\GTM-server" --bedrock
```

**Linux/macOS:**

```bash
sh Update-GTM.sh /path/to/existing/GTM-server --bedrock
```

Use `--bedrock` for an existing Geyser installation. Omit it for a Java-only update. An unsupported core binary, checksum failure or unsafe path stops the update. Keep the backup ID printed on success.

Start your existing server normally, connect with the matching Minecraft version and accept the updated resource pack. The phone skin requires the pack to finish loading. Open `/phone`, `/gun` or `/car` to reach the repaired phone, native equipment and garage. Right-click fires a gun; sneak + right-click reloads using its matching ammunition.

## Open the Control Centre

After the repaired server starts, double-click **Open-Control-Centre.bat inside your server folder**. On Linux/macOS:

```bash
python3 /path/to/existing/GTM-server/tools/open_control_centre.py --server /path/to/existing/GTM-server
```

The dashboard connects to the running server on `127.0.0.1:8765`. It shows live status, players, pack loading, logs, an owner command console and a local guide. Its owner token is private; the opener handles it automatically.

For an already repaired and running Daytona server, run this from the updated GitHub repository using your existing Daytona access configuration:

```bash
python tools/open_control_centre.py --daytona
```

Keep that terminal open while using the dashboard. This opens a localhost SSH tunnel; it does not install the update or restart the remote server. The in-game JEEVA guide and web guide use an offline fallback; they do not require a paid AI account.

## Roll back

Stop Paper and its launcher, then use the backup ID printed by the updater:

```bat
Update-GTM.bat "C:\path\to\existing\GTM-server" --rollback BACKUP_ID
```

```bash
sh Update-GTM.sh /path/to/existing/GTM-server --rollback BACKUP_ID
```

Rollback restores only the files changed by this repair. It refuses to overwrite files edited after installation. An interrupted update prints the receipt ID that must be rolled back before applying again. Detailed implementation and acceptance evidence are in `RUNTIME_REPAIR_2026-11-25.md`, `build-report.json`, `pack-repair-report.json` and the included verification reports.
