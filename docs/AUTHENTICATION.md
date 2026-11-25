# GTM authentication and account preservation

The candidate core includes offline-account authentication. It does not require a new login plugin and does not replace existing player UUIDs, financial records or inventories.

## Player flow

An unverified offline connection is isolated until authentication succeeds. New identities use:

    /register <passphrase> <repeat>
    /login <passphrase>
    /changepassword <old-passphrase> <new-passphrase> <repeat>
    /logout

Use double quotes around passphrases containing spaces. The policy accepts 15–128 Unicode characters, normalizes to NFC, and rejects control characters and a small list of predictable values. It does not require a mixture of uppercase letters, numbers and symbols. Backslashes are literal unless they escape a quote or another backslash.

Successful authentication activates the existing ledger/account and starter flow. Reconnecting requires another login. Player names, IP addresses and administrator permissions never establish a trusted offline session.

Direct Mojang online-mode connections can use their verified identity. If the installed Floodgate API confirms a connected Bedrock player and authentication.trust-floodgate remains enabled, that verified identity can also authenticate automatically. A username or UUID prefix alone is not trusted. Floodgate keys and proxy forwarding must remain correctly configured.

## Existing accounts, staff and recovery

An existing ledger identity without a local authentication record cannot be claimed by the first person connecting under its offline name. Operators and configured reserved names receive the same protection.

After independently verifying the connecting person's identity, the owner can use the **local server console**:

    gtmauth status
    gtmauth enroll <online-player>

Enrollment is bound to that current connection, expires after ten minutes, and permits the player to choose a passphrase with /register. It also serves as controlled password recovery. Disconnecting invalidates the approval. Enrollment never prints a temporary password, changes a balance or transfers an account to another UUID. In-game operator permissions do not authorize recovery.

Preserve online-mode, Floodgate identity rules and account files when importing a server. Changing offline/online UUID policy is a separate migration. The built-in provider refuses to start alongside enabled SimpleLogin, AuthMe or LoginSecurity providers; their credentials must not be silently discarded or bypassed.

## Isolation and callback checks

Until authentication, the core prevents commands except its authentication commands, chat, movement/teleports, inventory use and transfers, block/item/entity interactions, attacks, projectile use, mounts and related actions. It does not grant welcome balances or starter equipment before login. Minecraft continues to own inventory persistence; authentication does not clear or duplicate inventory into a second store.

Blocking inventory actions is not a claim that every initial vanilla inventory packet is hidden from an offline client. Actual pre-authentication inventory privacy and edition-specific packet behavior remain client verification gates.

Core phone, NPC, inventory and scheduled career paths check authentication. Civic/model/festival callbacks also check it. NPC activation/combat and delayed AI replies reject unauthenticated actors; delayed AI replies additionally require the original connection nonce. Testing-arsenal grants require authenticated sdcraft.admin permission.

Each connection receives a random nonce. A password check finishing after disconnect cannot authenticate a replacement connection with the same UUID. Default login timeout is 120 seconds and authenticated session lifetime is 12 hours, with bounded configurable ranges.

## Credential persistence and work limits

Credentials are separate from finances, under plugins/SDCraftCore/authentication/credentials.snapshot. Records contain schema, UUID/name, credential generation, independent salt, work factor and hash. No plaintext password is stored.

The existing bounded, checksummed SnapshotStore provides atomic replacement. Corrupt/stale stores fail closed, and memory publishes only after a successful commit. POSIX filesystems receive owner-only directory/file permissions. Password changes invalidate old proofs.

Fatal core initialization errors request a server shutdown. Merely disabling a failed authentication plugin would leave an offline-mode server accepting unprotected players, so startup does not intentionally fall back to unauthenticated gameplay.

PBKDF2-HMAC-SHA256 uses 600,000 iterations, a random 128-bit salt, a 256-bit result and constant-time hash comparison. Hashing and credential writes run on a bounded pool: default two workers and 16 queued operations, with ceilings of two workers and 32 queued jobs. Owned password arrays are cleared after work/cancellation.

Attempt budgets permit five checks per identity and twenty per network address in five minutes. Reconnects/IP changes do not reset the identity budget. Successful authentication resets its account budget, not the network budget. Bookkeeping is bounded and process-local, not advertised as a persistent abuse database.

Primary guidance:

- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).
- [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html).
- [Floodgate API](https://geysermc.org/wiki/floodgate/api/).

The JDK-provider implementation is not a claim of FIPS certification.

## Deployment boundary and evidence

Hashing stored passwords does not encrypt a vanilla offline-mode Java network connection. The portable candidate uses a local/loopback or otherwise secured transport boundary. Public offline Java exposure needs a separately verified secure connection design. Server command logging must remain disabled. The core cancels/redacts credential commands before Bukkit dispatch; unrelated plugins and client histories must not be assumed to redact secrets.

Automated tests exercise persistence, stored-byte checks, independent salts, credential rotation, concurrent/duplicate identities, stale/corrupt stores, permissions, cancelled workers, stale-session callbacks, expiry, rate limits and Unicode arguments. See [BUILD_RUNTIME_R4_REPORT.md](BUILD_RUNTIME_R4_REPORT.md) for executed build evidence.

Real Java/Bedrock login, inventory, logout, reconnect, protected-name enrollment and administrator recovery still require client verification. Third-party authentication migration and public-host transport remain explicit gates.

The credential store is capped at 10,000 identities and a 4 MiB payload; the attempt budget map is capped at 8,192 account/network keys. Financial delivery/mission/medical histories have separate finite capacities and no automatic archival workflow. See [STATE_RECOVERY_R4.md](STATE_RECOVERY_R4.md) for the exact limits, recovery boundaries and required retention work.
