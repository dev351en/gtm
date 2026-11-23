# Third-party plugin inventory — isolated candidate

The `plugins/` directory contains the exact JARs used by the Paper 26.3 smoke
test. Their presence is not a claim that every license permits redistribution;
review each project’s current license and hosting terms before publishing the
ZIP.

Bundled integrations include Paper, VaultUnlocked, LuckPerms, WorldEdit,
WorldGuard, Citizens, BlueMap, MTVehicles, QualityArmory, CommandPanels,
ProtocolLib, SimpleLogin, SimpleRevive, PlayerCorpses, GSit, DreamDisplays,
DecentHolograms, ClearLag++, SkinsRestorer, and The Smooth Elevator.

The exact versions and SHA-512 records used during acquisition are preserved in
the working project history and startup logs. Do not replace a JAR without
repeating Paper 26.3 startup and gameplay tests.

Important integration notes:

- SDCraftCore registers the `SD Craft Wallet` as a Vault legacy economy.
- SDCraftCore runs the supported `mtv vault setup` reconnect after enabling so
  MTVehicles uses that wallet.
- ProtocolLib is installed for SimpleLogin password-log protection.
- BlueMap remains optional until the owner approves its Mojang client-resource
  download acceptance and the target host’s disk/port budget is checked.
- Geyser/Floodgate and Bedrock client support are not bundled here.
- VoxelMap is client-side Fabric software and is not a Paper server plugin.

No credentials, API keys, Aternos backup, or live-host data belongs in this
manifest or release archive.
