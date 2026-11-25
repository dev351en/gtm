# GTM Revision 4 — state and recovery boundaries

**Review date:** 25 November 2026
**Scope:** The current implementation candidate on gtm/playable-r4. This records implemented behavior and remaining release gates; it does not certify crash recovery or full-game completion.

## What is committed together

Ledger stores financial balances and their associated mission, medical, food, loan, property and item-delivery records in plugins/SDCraftCore/accounts.yml. Its commit writes and forces a temporary file, then uses atomic replacement. A reported commit failure restores the last committed in-memory account data. There is no non-atomic replacement fallback. The transaction CSV is an audit stream, not the authoritative recovery database.

- Mission reward, career credits and the run receipt commit together. Replaying the same matching receipt does not pay again.
- A medical settlement records its decision and any combined wallet/bank debit together. An insufficient-funds decision is retained so topping up cannot turn a replay into a new charge.
- A supported paid-item purchase records its debit and item outbox entry together. Food collection changes the ticket phase and creates its delivery entry in the same account commit.
- Existing loan, food-order and property operations keep their corresponding financial and ownership state in that same ledger aggregate.
- Native vehicle/furniture purchases commit the bank debit and a stable ownership-grant UUID together. The destination module records that exact UUID, then the ledger acknowledges it. Matching retries cannot add another vehicle/furniture entitlement. The same pattern applies to paid refuelling/repair: the vehicle condition and its service receipt commit in one vehicle snapshot, and a completed service can be acknowledged after the player leaves the station.

AtomicYamlStore separately protects core runtime.yml, mission state and restoration state/configuration. It rejects malformed files, unexpected external changes and non-atomic replacements, while retaining the same in-memory configuration object when restoring a failed commit. Authentication credentials use the checksummed, versioned SnapshotStore in authentication/credentials.snapshot, separate from balances and player inventories. Neither store provides one transaction spanning all server files.

## Inventory, death and world recovery

Native road ownership, keys, parked pose, fuel/energy, condition and odometer use a separate checksummed `vehicles/parked.snapshot`. Loaded vehicles checkpoint periodically and at lifecycle actions; a forced process loss can roll back motion/energy since the last completed checkpoint. A failed checkpoint suspends driving. It does not establish a transaction spanning all files or certify the real server crash boundary.

Furniture entitlement, binding, placement, quarter-turn rotation and light intent share `furniture.snapshot`. Placement/removal changes the same entitlement instead of minting vouchers. Storage opens a real protected single chest/barrel; no second item inventory is stored. A saved container binding and the vanilla block marker are separate persistence operations. An authenticated owner can repair a matching interrupted marker without copying contents; conflicting/changed blocks fail closed. Actual vanilla inventory/chunk durability remains a client/world fault-test gate. Bound beds use real overworld beds, and lights use existing dry `LIGHT` blocks. No unsafe block replacement or fabricated inventory restoration is performed.

GtmItemDelivery adds a queued item and its receipt to vanilla player state, invokes player.saveData, and only then acknowledges the ledger delivery. A retry that sees an existing receipt invokes saveData again before acknowledging it, including after an earlier thrown save exception. Up to eight new items are inserted per retry; a full inventory leaves paid items queued.

Paper's saveData method returns no durable-write result and can report failures through logging. This design therefore does **not** establish atomic delivery across player data and accounts.yml, or prove safety against forced process termination/power loss. Do not erase a delivery receipt or grant a replacement item merely because one side appears stale: that can turn a recoverable discrepancy into a duplicate or loss.

MedicalRecovery saves a death token before charging. A thrown initial player-save failure preserves inventory and applies no medical debit. The death counter distinguishes later deaths; a separate arrival marker retains a cancelled hospital teleport without reusing its prior bill. After authentication, a surviving arrival is retried. Hospital targets must be commissioned and pass body/floor safety checks. Bukkit and vanilla remain responsible for inventory retention, drops and actual respawn persistence; the plugin does not maintain a second inventory-copy database.

RestorationEngine journals surveyed public damage before allowing controlled destruction. It restores only within configured scope, skips player-placed/private locations and preserves replacement blocks. Ordinary public signs include both sides, color, glow and wax state; interrupted sign reconstruction only resumes on a default, unmodified empty sign. Signs with plugin persistent data, beds, containers and other sensitive block entities are protected instead of being advertised as complete NBT restoration. Unloaded chunks remain queued. No surveyed zones means no automatic public-world restoration.

## Explicit retention and capacity limits

These are current code limits, not evidence of a completed archival subsystem. Financial receipt histories are retained after acknowledgement; reconnecting or restarting does not reset them.

| State | Limit and scope | Behavior at capacity |
|---|---|---|
| Mission settlement receipts | 16,384 per account | New settlement is rejected before reward/credit mutation; matching existing receipts can still be recognized. |
| Medical settlement receipts | 16,384 per account | A new settlement fails before debit; the medical handler preserves inventory without charging. |
| Item-delivery ledger records | 4,096 per account, including received entries | A new delivery is rejected before its associated purchase debit or collection transition. |
| Native asset purchase receipts | 4,096 per account, including acknowledged grants | New purchase is rejected before debit; existing matching grants can reconcile. |
| Paid vehicle service ledger receipts | 4,096 per account | New service is rejected before debit. |
| Native vehicle state | 512 vehicles and 4,096 service receipts per module; 4 MiB snapshot | New acquisition/service stops at capacity. Default active limit is 16 vehicles and ownership limit is 8 per player. |
| Furniture state | Default 2,048 entitlements globally, 32 per owner, 64 per anchor chunk; 4 MiB snapshot | New ownership/placement stops at the configured capacity; only up to 128 placements are rendered at once. |
| Vanilla item-delivery receipt IDs | 4,096 per player | New insertion stops; already-present queued receipts can still reconcile. No automatic pruning is implemented. |
| Food-order issued IDs | 2,048 per account | New ordering is rejected before debit. Existing order/refund state remains. |
| Loan issued IDs | 512 per account | New loan issuance is rejected before crediting principal. Existing debt remains. |
| Pending restoration records | 8,192 for this plugin instance | Additional controlled public damage is prevented if it cannot be journaled. |
| Tracked player-placed coordinates | 32,768 for this plugin instance | Additional tracked city placements are cancelled. Breaking a block does not automatically erase its historical exclusion. |
| AtomicYamlStore file | 16 MiB per managed file | Oversized load/commit is rejected. This limit does not apply to the separate accounts.yml implementation. |
| Authentication credentials | 10,000 identities; 4 MiB snapshot payload | New enrollment is rejected at capacity. Existing verification/change operations remain subject to valid storage. |
| Authentication attempt bookkeeping | 8,192 account/network keys, process-local | Further unknown entries fail closed until five-minute windows expire; restart resets this abuse bookkeeping, not credentials. |

An individual queued item payload is limited to 65,536 Base64 characters. The ledger remains a whole-file aggregate; bounded record counts do not demonstrate acceptable save latency under sustained use. No automatic receipt archive, history compaction or safe high-water-mark migration currently exists.

Before any retention migration, stop the server cleanly and retain a consistent copy of plugin records, vanilla player data, statistics and worlds. A reviewed migration must preserve receipt identity and distinguish active obligations from historical decisions. Do not simply delete histories to clear a limit. A migration tool, saturation checks and restoration of the backup are remaining operational work.

## Evidence and remaining gates

Executed unit/domain checks cover credential persistence/rotation/rate limits and ledger settlement/replay/failure cases. [BUILD_RUNTIME_R4_REPORT.md](BUILD_RUNTIME_R4_REPORT.md) identifies the final tested source, counts and JAR; this report does not replace that evidence.

Release verification still requires actual Paper startup, Java and Bedrock clients, ordinary restart and controlled fault injection around debit, player save, acknowledgement, death, respawn, sign/block restoration and ledger checkpointing. Verify full inventories, disconnected/dead players, cancelled teleports, competing event listeners, corrupted state and receipt saturation on disposable copies. Actual directory/write durability, save-log failures and event/counter ordering are not certified by pure Java tests.

See [AUTHENTICATION.md](AUTHENTICATION.md) for account enrollment and the transport/privacy boundary, and [PLAYABLE_R4_ACCEPTANCE.md](PLAYABLE_R4_ACCEPTANCE.md) for all 51 specification sections and missing gameplay requirements.
