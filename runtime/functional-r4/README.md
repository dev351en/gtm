# Preserved GTM functional runtime

This directory contains the exact recovered compiled **SDCraftCore 1.0.3-r4-functional-candidate** and native **128×128** runtime art. It is a preserved binary/asset payload, not an assembled server or an automatic updater.

The full payload inventory and byte hashes are in [manifest.json](manifest.json). It preserves the recovered files without recompiling them.

## Contents

| Path | Purpose |
| --- | --- |
| `plugins/SDCraftCore-1.0.3-r4-functional-candidate.jar` | Functional game engine, SHA-256 `b7c76cd3a664e1bb7e1e56fd2098f7ef0a71e921d47170ed10c4e658974715af`. |
| `resourcepacks/GTM_Local_Java.zip` | Merged Java art pack, SHA-256 `5b5e132a2c670b07e8c0c389e086bd2dee1002ed7de72a6bdcd93acc6d6cba9a`. |
| `plugins/Geyser-Spigot/packs/GTM_Local_Bedrock.mcpack` | Matching Bedrock art pack; actual native-client rendering remains unverified. |
| `plugins/Geyser-Spigot/custom_mappings/gtm_native128.json` | Item/model mappings. |
| `plugins/Geyser-Spigot/extensions/` | Display bridge JAR and its GTM display mappings. |
| `licenses/` | Display bridge's corresponding source ZIP and AGPL license; retain together with its binary. |
| `launcher/gtm-launcher.jar` and four `Start-GTM*` wrappers | Preserved local launcher artifacts; their complete runtime/configuration belongs to the separately assembled owner package. |
| `documentation/` | Preserved implementation notes and verification evidence, with their original checksums. |

The Java engine/pack pair is 19,415,919 bytes. Optional Bedrock pack, mappings, bridge, and its license/source add 18,427,084 bytes. Launcher artifacts add 34,828 bytes. The manifest, this README, and documentation are additional publication material.

No world, cached Mojang server bundler, EULA acceptance, private credentials, account data, Floodgate keys, complete Paper installation, or Windows Java runtime is supplied here.

## Assemble downloadable artifacts

Large inputs may be stored as numbered chunks to fit publication transport limits. Do not use a chunk as a resource pack. From the repository root, run:

```sh
python tools/assemble_functional_runtime.py --output dist/functional-r4
```

The assembler checks each input chunk, reconstructs the original bytes, and checks the whole-file size/SHA-256 before producing:

- `GTM_Functional_Runtime_1.0.3.zip` — the preserved binary/asset/launcher/documentation payload; it is not a full server or automatic update installer.
- `GTM_Runtime_128_Java.zip` and `GTM_Runtime_128_Bedrock.mcpack` — exact complete resource packs.
- `GTM_Indraprastha_128_Assets.zip` — exact editable artwork archive.
- `SHA256SUMS` and `assembly-report.json` — output integrity/provenance records.

The [publication workflow](../../.github/workflows/publish-functional-runtime.yml) can create GitHub Release `gtm-functional-r4-1.0.3` after verification passes. This document describes that workflow; it does not assert that the run or release already succeeded. A release of this payload still does not deploy the existing Daytona server.

## Which BAT starts which game?

**To reach the same existing Daytona server**, use [Start-Daytona.bat](../../Start-Daytona.bat) at the repository root. Read [the connection guide](../../docs/DAYTONA_LAPTOP_CONNECTION.md). It opens a verified SSH forward to a running server; it does not install this payload or restart anything remotely. After READY, join `127.0.0.1:25565` from your matching Minecraft Java client.

**To start the separately saved local laptop copy**, extract the complete `GTM_128_Laptop_Playable_26.3.zip` and run its `Start-GTM-Java-Only.bat`. That package uses the sanitized 2026-11-23 public-world snapshot with its own workshop profile. It is not the current Daytona world.

The four wrappers preserved in this directory are source artifacts of that full package. Running them directly from this partial payload is not a supported complete installation. They need the full launcher configuration, correct integrity manifest, Paper, Java 25, plugins, and a coherent world. The Minecraft client is supplied by the player.

## Existing-server installation boundary

Do not drag this entire directory into an existing server or replace its configuration with the local workshop examples. The recovered workshop profile changes 490 configuration keys relative to the core defaults, including 445 prices plus feature flags, caps, properties, and services. Those values belong to a surveyed fresh public copy.

A target-specific installation must first inspect a **stopped coherent copy** of the actual server and preserve a complete backup. Preserve worlds, player UUIDs, inventories, money, ownership, routes, permissions, authentication records, existing Floodgate/proxy keys, and online-mode. Verify Java 25/Paper 26.3 compatibility and existing plugin identities. Replace only explicitly selected immutable core/pack files, keep the previous core outside plugin scanning, reject duplicates, and record a reviewed config merge.

The built-in authentication provider refuses to run alongside enabled SimpleLogin, AuthMe, or LoginSecurity. Their data must not be silently discarded. An existing offline account without a built-in credential requires verified local-console enrollment; it cannot be claimed merely by reconnecting under its name. See [authentication](documentation/AUTHENTICATION.md) and [state recovery](documentation/STATE_RECOVERY_R4.md).

Resource-pack serving must use the actual selected pack and SHA-1:

`717ac30ea44352a14d6e53d5d93ea53d01d0befc`

Preserve an existing remote server's connection policy. A localhost pack URL is suitable for its intended local installation, not an arbitrary remote deployment. The optional Bedrock bridge here was built for pinned Geyser 2.12.1 build 1308; preserve existing keys/configuration and verify installed-version compatibility before integration.

Generate a correct new integrity manifest from the actual chosen installation. Editing hashes merely to conceal a mismatch is not verification. Read back copied bytes and check that the original export remained unchanged. Persistent state may migrate at first boot, so rollback requires a coherent stopped backup and must not overwrite later player progress.

This payload does not perform those installation steps, provide a migration for every existing login provider, commission physical routes, or furnish an unseen city. No protected Daytona deployment is claimed.

## Provenance and test limits

The recovered binary matches the final preserved core hash. Historical evidence records 644 JUnit tests in 79 suites and 155 domain assertions for its source checkout, plus actual Linux Paper startup, normal authentication, resource-pack delivery, and clean shutdown. See [the functional runtime report](documentation/FUNCTIONAL_RUNTIME_R4_REPORT.md) for exact component versions and historical continuations.

The original temporary source commit `628c01bcd7ed5d95b21c9ea049990346135a0604` was not pushed and was not recovered. The repository's earlier `source/` tree does not reproduce these binaries. Source digests in the documentation record expected files/hashes; they are not a replacement for the source files. Only the optional display bridge has its corresponding source in this payload.

The new repository-root Daytona connector separately passed 39 offline fixtures using synthetic responses/processes. That does not establish native Windows execution, a real credentialed Daytona connection, or deployment of this core on Daytona.

Native Java/Bedrock visual verification, every model's client behavior, native Windows execution, the private-server migration, and the complete Revision 4 city/campaign remain unverified or incomplete. Traditional, electric, and cargo auto-rickshaws are implemented in the preserved runtime. Appropriate property, placement, backing blocks, supplies, and commissioned routes remain necessary for operational models. Consult [the functionality inventory](documentation/FUNCTIONALITY_INVENTORY_R4.md) for role-specific scope.

Editable art is separately preserved in [the artwork payload](../../creative/delivery/); assembly reconstructs `GTM_Indraprastha_128_Assets.zip`. That archive does not restore the missing engine or launcher code.

