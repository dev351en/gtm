# SD Craft release gates — current

The isolated candidate is boot-tested and portable, but it is not yet a public
production deployment. The following gates remain explicit:

1. Confirm the target host’s Java 25, Paper 26.3, memory, disk, SFTP/upload,
   startup, and backup capabilities.
2. Run the packaged ZIP with disposable player accounts and test login, starter
   kit, phone GUI, wallet/bank/Vault/MTVehicles transactions, GPS, missions,
   NPC spawning/dialogue/caps, ambient walking/retaliation/loot, transport,
   crime, medical, duty, and promotion.
3. Confirm the configured GitHub raw resource-pack URL is public and returns
   unchanged ZIP bytes matching SHA1
   `4633349625598AF3EFF64CAF24C74FB953BF0A4D`.
4. Obtain explicit owner approval before enabling BlueMap’s required Mojang
   client-resource download acceptance.
5. Configure `online-mode`/SimpleLogin/proxy authentication and operator
   identities for the actual host. Do not expose offline mode without a tested
   authentication gate.
6. Validate third-party plugin redistribution terms and retain their licenses
   or attribution files in the release package.
7. Measure memory, TPS, disk growth, and logs on the target host with 3–4
   players before public use. Keep the proximity-managed population within 6
   police and 94 non-police; reduce those caps if the target host loses TPS.
8. Preserve the Aternos backup. Replace the isolated world with a newer Aternos
   save only when the owner explicitly selects that save and it has been copied
   into a separate backup first.
9. Obtain final deployment approval and a fresh target-host backup before any
   upload or live-server mutation.

Features such as NPC autonomous vehicle driving, full heists, event-driven
witness intelligence, and persistent external-AI conversation memory remain
partial or disabled unless separately implemented and tested.
