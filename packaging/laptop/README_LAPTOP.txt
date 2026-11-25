GTM — LOCAL LAPTOP CANDIDATE

This folder starts a local Paper server. It does not connect to, restart,
overwrite or otherwise operate a Daytona sandbox. It is not a complete-game
or live Java/Bedrock certification.

Read documentation/PLAYABLE_R4_ACCEPTANCE.md for the requirements matrix and
concrete missing gameplay, and documentation/README.txt for the release
guides, build evidence, recovery report, public site survey and native 128
generation report. The documentation is part of this candidate release.

Check launcher/build-report.json for the source profile. The public-world
profile uses the sanitized city snapshot dated 2026-11-23 with fresh accounts;
it is not the current private Daytona world. Private-import mode preserves
the selected stopped server's player identities and data.

1. Extract the whole folder to a location you can write to. Do not run from
   inside the ZIP, a cloud-sync folder, or over an existing Minecraft server.
2. On Windows run Start-GTM.bat. On Linux/macOS run sh Start-GTM.sh with Java 25.
   A bundled Windows runtime, when included, is under runtime/java.
3. If the Minecraft EULA has not been accepted for this installation, the
   launcher shows its official URL and asks you to type I ACCEPT. Acceptance
   is not silently supplied by the build tool.
4. Wait for Paper's real Done message. Join with the matching Java client at
   127.0.0.1:25565 (or the port in server.properties). Accept the exact bundled
   resource pack. Its local HTTP server runs only while this launcher runs.
5. Use the core's register/login instructions. Existing saved identities may
   require console enrollment; the launcher never creates an administrator,
   resets a password or changes UUID policy. Do not share passwords in chat.
   A fresh offline account uses /register <passphrase> <repeat>, then /login
   <passphrase> on later visits. Follow the in-game length/quoting guidance.
   To administer your local instance, authenticate first, then use the local
   console to op your own exact player name. No operator is pre-created.
6. Enter stop in this console before closing the window. The launcher keeps
   copies of the last ten previous latest.log files in launcher/log-history.

The initial Paper boot may need internet access for its official Minecraft
libraries. The normal Java client needs its own legitimately installed game
and account. No Minecraft client or account credentials are bundled here.

Settings: launcher/launcher.properties controls heap and the local pack port.
Use Start-GTM.bat --check for preflight without starting Paper. Exit code 2
means first-start EULA acceptance is outstanding. Only --accept-eula is an
explicit command-line acceptance; never add it without the owner's decision.

The local profile binds to loopback. Opening it to LAN/internet is a separate
configuration step and requires a verified authentication/network profile.
Geyser requires its matching server plugins, Bedrock packs and transport ports;
an included pack alone does not establish working crossplay. No tunnels are
started, and no external AI or paid service is required.

Preserve worlds, player UUIDs, plugin databases, authentication stores,
accounts.yml, transactions.csv and permissions together. Stop before backup.
Keep the original private export as rollback. Do not restore an old account
file over transactions made after the backup. Do not publish this private
folder or upload it to a public Git repository.

launcher/build-report.json records provenance, exact inputs and configuration
changes. launcher/integrity.sha256 records immutable JAR and pack bytes.
If a checksum fails, restore the trusted file or rebuild a new verified bundle.
Do not bypass the preflight by editing its hashes blindly.
