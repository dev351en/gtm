# Staging commissioning — dev.4 banking and properties

These are opt-in integrations, NOT deployment approval or evidence of live client compatibility. Existing production is the intended eventual host. Do not copy a candidate JAR over production while the build, backup and access checks are incomplete.

## ARK loans
- Enable `gtm.experimental-loans` on a test instance only, grant `gtm.loans` only after verified authentication. Existing accounts.yml remains authoritative.
- Open the existing phone item, then ARK Bank Loans; fallback /gtmloan.
- Initial staging offers 1,000 or 3,000 ARK, 8% total flat interest, 14 active game days, 2 days grace. One loan day is 30 minutes of active play (movement within 120 seconds, online, awake; count game-loop seconds, not wall clock). Up to one minute of activity can be lost on crash. No new interest while offline. Fixed principal choices are provisional for economy balancing.
- Issue and repay use a single account-file atomic replacement, persistent issued-ID history (512 per account, fail closed when full), current loan ID and expected repayment value. CSV audit is diagnostic; a failure is logged, not presented as a failed payment. This does not guarantee audit completeness or power-loss durability.
- Test full/incomplete repayments, insufficient funds, stale menus, logout, restart and loan due notification on both Java and Bedrock. Recovery officers, collateral repossession and credit scoring remain pending.

## Properties
- Default `gtm.experimental-properties: false`, `gtm.property-regions: []`. Survey required. No invented coordinates are supplied.
- Each list entry: id (stable UUID), name, world (loaded world), min-x, min-y, min-z, max-x, max-y, max-z (inclusive integer block coordinates), price-cents. Maximum 256, overlapping cuboids rejected. A malformed enabled registry fails startup rather than silently opening private regions.
- After verified login grant `gtm.properties`. Phone -> Indraprastha Properties, fallback /gtmproperty. Select a listing then confirm purchase; bank deduction and ownership committed together.
- Collect physical key (temporary vanilla tripwire hook). Right-click block within your flat to toggle lock. Replacing keys invalidates old tokens and clears guest grants. Only owner may use key; duplicated items do not transfer ownership.
- Explicit `gtm.properties.admin` bypass, entry audit in server logger. Existing accounts and property records are not regenerated.
- Guards cover walking/teleport crossings, direct block/entity interactions, break/place and located container opens. Egress from a region already occupied is permitted; do not claim total anti-bypass protection. Vehicle passenger movement, portal/respawn cases, indirect edits (pistons/explosions), third-party commands, block multi-place, property evacuation, WorldGuard/restoration coordination and guest-management UI still require integration tests or work. No property locations, furnishings or custom key models are installed.
- Enable on staging only, verify boundary behavior, bypasses, permission ordering, inventory handling, account reload and rollback. Offline account authentication remains a prerequisite.

## Rollback
Export a consistent stopped-server backup before deploying a candidate. Preserve accounts.yml and transactions.csv. Revert the plugin and configuration; do not automatically restore an old account file over newer committed player transactions. Test migration and recovery on an isolated copy. No new Daytona sandbox or paid resources may be allocated without verified credit, quota and disk budget. 
