# Third-party plugin inventory — isolated candidate

The `plugins/` directory contains the exact JARs used by the Paper 26.3 smoke
test. Their presence is not a claim that every license permits redistribution;
review each project’s current license and hosting terms before publishing the
ZIP.

Bundled integrations include Paper, VaultUnlocked, LuckPerms, WorldEdit,
WorldGuard, Citizens, BlueMap, MTVehicles, QualityArmory, CommandPanels,
ProtocolLib, SimpleLogin, SimpleRevive, PlayerCorpses, GSit, DreamDisplays,
DecentHolograms, ClearLag++, SkinsRestorer, The Smooth Elevator, TrainCarts,
and BKCommonLib.

Train integration acquired from the official Modrinth projects:

- `TrainCarts-2.0.5-1787.jar` - Train_Carts 2.0.5 build 1787, MIT,
  <https://modrinth.com/plugin/traincarts>
  SHA-512: `241A0B54CE666CD5DA2136A0212C237AEF975FA477B1C4BD227BFF92D06DB5416CA14974E6F5091CF483A2CD103F5A7AC2BD33C9FA9E46FE52A2C6D31266E726`
- `BKCommonLib-2.0.6-2110.jar` - BKCommonLib 2.0.6 build 2110, MIT,
  <https://modrinth.com/plugin/bkcommonlib>
  SHA-512: `873AE3F31E2944667B11639663235D2AE921C16F1A03096AA7402345A0A10B6615CC7D6490527961C423DEE9224D0206CD3C3231E291AA33D6DF190204165748`

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
- TrainCarts Ticket Shop was not bundled because its current release does not
  declare Paper/Minecraft 26.3 support and SD Craft already owns metro fares in
  its single authoritative wallet ledger.

No credentials, API keys, Aternos backup, or live-host data belongs in this
manifest or release archive.
