# Java-only startup and optional plugin recovery

Use `Start-GTM-Java-Only.bat` on Windows or `sh Start-GTM-Java-Only.sh` on Linux for Java play. Both call the packaged launcher with `--java-only`. The regular launcher accepts that flag too. The existing owner EULA step, ordinary account registration and login remain in place.

Before Paper starts, the launcher verifies the two reviewed optional Geyser and Floodgate plugin JARs against their exact descriptors, pinned SHA-256 values and the bundle's sealed integrity manifest. It records a reversible journal and moves those two files into `launcher/java-only/files`, outside Paper's plugin scan. Their configuration folders, keys, packs, existing caches and authentication/account data stay in their original locations. Paper then starts through its unchanged normal main class with the remaining ordinary plugins, including the core authentication service.

After Paper exits, the launcher verifies and restores the identical original JARs. A completed journal is retained in `launcher/java-only/history`. A later normal crossplay start therefore uses the same optional plugin bytes and identity material as before. Setting `bedrock.enabled=false`, or having no enabled Bedrock profile, selects the same Java-only exclusion.

## Interrupted runs

If the launcher was interrupted, first stop any remaining Minecraft process normally. On the next real launch, recovery checks the exact pending journal, manifest and plugin bytes, refuses a matching live child, and obtains exclusive nonblocking locks on every existing `session.lock` in the bundle. It restores only a verified original that is currently in the preserved location. It never overwrites an existing destination or recreates missing plugin bytes.

The journal handles partial exclusion and partial restoration: each original must exist exactly once, in its original or preserved location. Duplicate, missing, altered, aliased or symbolic files cause a refusal for review. An unresolved selection remains preserved if Paper is still alive or a world remains locked. Do not delete files from `launcher/java-only` or replace plugins during a run.

`--check --java-only` performs a read-only inspection of both a normal bundle and a valid interrupted selection. It does not move JARs, start Paper, accept the EULA or rewrite the journal. A real launch performs any safe recovery before normal integrity preflight and a new selection.

The journal is forced to disk before moves, moves never request replacement, and child identity is recorded immediately after process creation. This is not a certification of atomic recovery from arbitrary hard power loss across process creation, directory metadata, world saves and account snapshots. The launcher preserves ambiguous states for review.

## Why the port setting was insufficient

Inspection used only the exact bundled JAR bytes, through offline Java25 disassembly; no Geyser class was initialized and no network request was made for this audit.

| Pinned implementation | Observed order |
| --- | --- |
| `GeyserImpl.initialize()` | At bytecode22, invokes `EncryptionUtils.getMojangPublicKey()` when signed Bedrock login validation is enabled. At187 it loads registries; at193 it starts `AssetUtils.generateAssetCache()`. Only at239 does it call `startInstance()`. |
| `EncryptionUtils` static initializer | At42, calls `getDiscoveryData()`; at48, calls `getOpenIdConfiguration()`. The former performs an HTTPS request to the Minecraft client-discovery service. |
| `GeyserImpl.startInstance()` | At298–349, reads `geyserUdpPort`, compares it with `-1`, and throws `UnsupportedOperationException`. This occurs after the preceding initialization. |
| Paper255 `DirectoryProviderSource.walkFiles` | Scans the plugin directory to depth1. The preserved sibling launcher directory is outside that scan; nested plugin data need no relocation. |

The child still receives `-DgeyserUdpPort=-1` as additional protection, but successful exclusion is what prevents the optional bootstrap from being loaded. The core, Paper entry point, Bedrock endpoint settings and authentication implementation are not patched.

## Verified scope

The dedicated offline gate passed **18 tests**, with zero failures, errors or skips. It uses the actual two reviewed JARs, reads descriptors without loading plugin classes, and covers exact restoration, partial exclusion/restoration, a completed journal interrupted before archival, read-only pending inspection, all-world lock refusal, a real live child process, manifest and byte changes, descriptor aliases, duplicate JARs, symbolic paths, traversal, missing copies and destination collisions. Synthetic plugin descriptors with unreviewed bytes are refused. Original fixture inputs and all sentinel world/configuration/key/account files remained byte-identical. The small child waits on its local standard input and opens no listener.

The separate complete-launcher fixture also passed: its actual child scan contained no optional bootstrap descriptors, and both original JARs were restored exactly after exit. The complete packaging gate discovered38 tests:35 passed and3 private-IPv4 cases were skipped because this environment had no eligible interface. That fixture uses a small local FixtureServer and pack HTTP listener; it does not initialize Paper or Geyser. The actual pristine released-launcher smoke, native Java/Bedrock clients and Windows execution remain separate records. See [LAUNCHER_JAVA_ONLY_R4.json](reports/LAUNCHER_JAVA_ONLY_R4.json) and [the exact 18-test log](reports/LAUNCHER_JAVA_ONLY_FIXTURES_R4.log).
