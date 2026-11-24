# GTM Revision 4 — full specification acceptance matrix

**Audit date:** 25 November 2026  
**Development branch:** gtm/playable-r4  
**Scope:** All 51 numbered sections of the supplied Revision 4 master prompt, including its 35 logical gameplay systems.

## Release assessment

**This is an implementation candidate, not a completed Revision 4 game.** Native 128 artwork and static pack validation are complete for the documented art batch. The engineering increment adds account isolation, safer state/transactions, medical settlement and bounded restoration. Many transport, city, campaign, commerce and administration requirements still lack runtime implementations.

Do not name a distribution GTM_INDRAPRASTHA_COMPLETE.zip, claim all master systems are playable, or describe the remaining work as only a login/deployment issue. A ZIP, successful build or password check does not close missing gameplay requirements.

This matrix records acceptance evidence and dependencies; it does not replace the approved scope or authorize production writes. [BUILD_RUNTIME_R4_REPORT.md](BUILD_RUNTIME_R4_REPORT.md) records actual builds and tests. Subsequent edits require a final build of the packaged source/JAR.

### Evidence interpretation

- **IMPLEMENTED** identifies a concrete artifact or narrow source behavior; it does not imply live integration.
- **BUILD_VERIFIED / AUTOMATED_TESTED** apply only to the named executed checks.
- **IN_PROGRESS** means substantive requirements remain despite existing work.
- **NOT_STARTED** means no runtime implementation satisfying that requirement was found.
- **BLOCKED** identifies required external dependencies or unavailable verification.
- No static result is promoted to **CLIENT_VERIFIED** or **RELEASE_READY**.

## All 51 master-prompt sections

Paths are repository-relative. Java class names refer to source/src/main/java/com/sdcraft/core unless otherwise stated.

| Section | Requirement | Current evidence and state | Acceptance work still required |
|---:|---|---|---|
| 1 | Principal engineering and complete execution | IN_PROGRESS: existing SDCraftCore is being extended with concrete code/art. | Complete integrated gameplay; role descriptions and catalogues do not satisfy runtime requirements. |
| 2 | Preserve the existing project | IMPLEMENTED as a constraint: established UUIDs, accounts and source IDs remain the baseline. PROJECT_SPEC.md, AGENTS.md. | Verify the selected imported server/world, dependency compatibility and migrations against the actual installation; preserve backups. |
| 3 | Autonomous implementation | IN_PROGRESS: independent art, build, packaging and engine slices are active. | Continue executable work through acceptance gates; record real blockers without invented results. |
| 4 | Persistent project memory | IN_PROGRESS: changelogs, contracts, handoff, reports and this matrix exist. | Keep a versioned implementation tracker, API/migration documentation, crossplay report and handoff aligned with the delivered commit. |
| 5 | Audit and regression repair | BUILD_VERIFIED for executed increments: Java 25 Gradle build/tests run. Account/testing-grant/save/restoration defects are being repaired; AtomicYamlStore now also protects core runtime.yml. Paper --help bootstrap exited successfully without accepting the EULA. | Complete actual server startup/restart and regressions; a help/bootstrap invocation is not a server boot. Unresolved coordinates, vehicle integration, crossplay and world configuration remain. |
| 6 | Complete production targets | IN_PROGRESS: primary-art counts, 500 skins, 100 outfits and supporting art are documented in GENERATION_128_REPORT.md. | Reach functional targets: 30 approved firearms, 30 main missions, 50 side jobs, 24 real apps, vehicles/furniture and 46 facilities. Do not substitute variants/platform files for designs or behavior. |
| 7 | Engineering/creative integration | IN_PROGRESS: stable IDs, manifests, design profile and catalogue checks exist. | Bind approved models, animations, collisions, skins and interfaces to working engines; review legacy migrations. |
| 8 | Original GTM branding/art direction | IMPLEMENTED for the native 128 art batch; creative/design_language_128.json. | Replace old runtime branding/UI labels, verify installed presentation and audit legacy-pack rights. |
| 9 | Asset/resource-pack contract | AUTOMATED_TESTED for the art batch: 1,073 model pairs and 1,103 item definitions including aliases; static references/CRCs resolve. | Verify actual dispatch/rendering, animations, collisions and pack delivery in both editions. Extra IDs and finishes are not all unique geometry. |
| 10 | Shared authoritative crossplay | IN_PROGRESS: shared Paper rules and Geyser/Floodgate configuration exist; auth can use Floodgate API confirmation. | Implement/verify edition input, rendering, entity mappings and forms. Java compilation does not prove Bedrock/touch/controller support. |
| 11 | HUD, minimap and phone shortcut | IN_PROGRESS: phone item/menu, GtaEngine sidebar and GpsManager compass/BlueMap link exist. | Implement cached live minimap layouts/rotation/zoom/routes/markers, requested HUD positions, driving instruments and verified command-free equivalents. GPS still has coordinate fallbacks. |
| 12 | 65 approved road vehicles | IMPLEMENTED for art and explicit damage variants; transport_128.json. | Bind all 65 to drivable correctly scaled vehicles with persistent identities, seats, pivots and controls. Runtime retains the legacy MTVehicles bridge. |
| 13 | Custom vehicle engine | IN_PROGRESS: gtm/VehicleState has tested portable energy/health rules; GtaEngine has legacy purchase/issuance paths. | Integrate authoritative motion/steering/collision/passengers, fuel/charging, odometer, locks/theft, garages, insurance, recovery, visible states and durable transactions. |
| 14 | Traffic and NPC driving | NOT_STARTED as a complete runtime; gtm/RouteGraph is an abstract tested graph. | Survey lanes/junctions/signals; implement left-hand traffic, shared player/NPC mechanics, pedestrians, delivery/police/transit and bounded distant simulation. |
| 15 | Local trains, metro and SkyLink | IN_PROGRESS: art and TrainCarts/BKCommonLib setup/configuration exist. | Commission surveyed tracks/cables/stations, propulsion, doors/seats/tickets/schedules/reservations/energy; verify routes and restart. A ropeway must actually hang and move on its cable path. |
| 16 | Helicopters and boats | IMPLEMENTED for four helicopter/eight boat art records, not custom runtime. | Implement flight/water movement, seats, collision, fuel/damage, rotors/docking, NPC service and surveyed facilities. |
| 17 | Functional furniture | IN_PROGRESS: 200 art records and GtmCityModels catalogue; earlier runtime has three optional nonpersistent fixtures. | Add owned persistent placement/rotation/removal, seating/storage/lighting/services, collisions, furnished interiors and actual showroom vehicles. |
| 18 | World transformation/46 facilities | IN_PROGRESS: PUBLIC_WORLD_SITES.json, targets, survey/patch tools and a limited reversible world patch exist. | Inspect/renovate all targeted buildings and apartments, interiors/navigation/signs/connections on the selected world copy. A facility manifest does not certify construction. |
| 19 | City boundary and survival | IN_PROGRESS: restoration is restricted to explicit surveyed public zones. | Add editable geographical boundaries, enter/leave presentation and shared city/wilderness policies; verify permanent survival outside and medical recovery across dimensions. |
| 20 | 500 working NPC identities | IN_PROGRESS: NpcService, CityRoster and population TSV provide opt-in identities and bounded activation. | Bind skins, actual occupational jobs, homes/workplaces/schedules/emotions/relationships. Name-based skin lookup and wandering do not complete these requirements. |
| 21 | JEEVA and dialogue | IN_PROGRESS: DialogueEngine/Jeeva/GtmDialogue provide local multilingual responses, PDC familiarity and guarded near-miss/bubble paths. | Complete event-driven behavior and validated reactions; verify targeting/bubbles crossplay. Optional external AI is disabled and is not required for local fallback. |
| 22 | Fictional weapons/cosmetics | IN_PROGRESS: GunEngine has four native firearm families; the shop delivers those supported families through the paid-item queue and rejects unsupported purchases. Finish entitlements persist in Ledger/GtmFinishes. | Implement all 30 approved firearms, melee/protection/effects and integrations/migrations. The 30 additional weapon-source art IDs include melee/special props. Verify actual gun/item behavior and delivery on clients. |
| 23 | Wanted, police and cinematics | IN_PROGRESS: wanted/jail, player-officer arrest/surrender and safe-zone paths exist in GtaEngine. | Implement NPC investigation/patrol/pursuit/dispatch/search, vehicle/helicopter response, pursuit-aware decay, custody/bail and accessible cinematics; verify live combat/reconnects. |
| 24 | Black Lotus and 30+50 campaign | IN_PROGRESS: gang identities/rotation and 13 legacy waypoint jobs exist; the expanded 54-slot mission UI exposes all 13. | Implement chaptered campaign, 50 side jobs with real objectives, independent progression, boss/government finale, pursuit, epilogue/credits/free roam. Old declared job steps are not executed by the route engine. |
| 25 | Medical death recovery | IN_PROGRESS with financial unit evidence: MedicalRecovery and Ledger.settleMedicalOnce. | Verify death/drop/keep-inventory/respawn/reconnect, safe commissioned hospital, all dimensions, other death plugins and crash boundaries. Bukkit owns inventory; no second inventory-copy store is claimed. |
| 26 | Durable public restoration | IN_PROGRESS: RestorationEngine/AtomicYamlStore implement surveyed scope, bounded durable queue, placed-block exclusions and public signs. | Test explosions, doors/signs, restart/replay, replacement edits, private contents and saturation on a disposable world. Sensitive block entities are protected, not claimed fully restored with NBT. |
| 27 | Economy/banking/lending | IN_PROGRESS: atomic Ledger snapshots, Vault bridge and narrow loan/repayment rules have tests. | Complete business accounts/statements, four loan types, credit/restructuring/collateral/recovery employees and economic simulation. Every reward/purchase/delivery needs replay-safe outcomes. |
| 28 | Property/access | IN_PROGRESS: GtmProperties/RegionBounds and ledger ownership/key/guest methods; default surveyed registry is empty. | Inspect and populate apartments/properties; complete rentals/transfers/guest UI, movement/vehicle/portal/container bypasses, overrides and restoration coordination. |
| 29 | Food/commerce | IN_PROGRESS: 30 food models, FoodCatalogue, GtmFood and order/refund records exist. Ledger collection and the paid-item delivery outbox commit together, with inventory receipt reconciliation. | Commission stores/vendors/stock/receipts/refunds/consumption and test actual inventory delivery, full inventories, reconnects and crash boundaries. Current food flow is counter collection, not a full commerce network. |
| 30 | Zomatoo/Swiffy delivery | NOT_STARTED beyond counter ordering and art. | Add addresses, fees/preparation/dispatch, actual nearby scooter/NPC travel, tracking/failure recovery and persistent receipts. Counter pickup or instant teleport is not delivery implementation. |
| 31 | 100 purchasable outfits | IMPLEMENTED for 128 masters, compatibility overlays and previews only. | Implement sellers, wardrobe/preview/purchase/entitlement/application and crossplay cosmetics. Appearance must not grant authority. |
| 32 | Nightclub/entertainment/alcohol effects | IMPLEMENTED for related art only; complete runtime NOT_STARTED. | Furnish and operate venues/music/dancers/services; implement personal blackout and persisted seven-day/abstinence effects without changing the shared clock. |
| 33 | City-wide manual festivals | IN_PROGRESS: persistent staff switchboard, particles/fixture and correct approved 128 selection preserving legacy IDs. | Integrate eight themes across displays/clothes/products/news/missions/venues with reversible placement, overlap/restart safety and runtime theme migration. |
| 34 | 24 phone apps and Car App | IN_PROGRESS: phone item, six base actions and several gated civic apps exist. | Connect every named application to real services. Fashion, broader commerce, news, contacts/keys/settings and Car App are incomplete; decorative icons are not completed apps. |
| 35 | Media/event news/digital infrastructure | NOT_STARTED as a complete runtime; concepts/art exist. | Implement verified event feed, contextual news, reporter behavior, distribution and furnished studios. Keep fictional facilities separate from real administration. |
| 36 | Brands/signage/managed displays | IMPLEMENTED for 32 brands and 120 bilingual sign sources. | Install verified displays, changing ads/headlines/station/festival content, upload validation and scheduling; verify original branding in game. |
| 37 | Government/daily life/clock | IN_PROGRESS: professions/duty and 20-minute day/10-minute night clock exist. | Implement licenses/registration/permits and deterministic service decisions; connect NPC work, businesses, transit and lighting to the clock. |
| 38 | Authentication/account security | IN_PROGRESS with compiled source and automated store/session tests; GtmAuthentication, AuthenticationStore, AuthenticationState. Failed core initialization requests server shutdown to prevent an unprotected offline world. | Verify real login/logout/reconnect/inventory/permission/Floodgate and controlled legacy enrollment. Test initial inventory-packet privacy separately from blocked inventory actions. Maintain secured transport; stored hashes do not encrypt offline Java TCP. |
| 39 | Reusable 35-system framework | IN_PROGRESS: portable rules coexist with the established combined plugin; city-specific assumptions remain. | Version APIs/config/migrations, separate city content and implement missing logical systems; document licenses and independent installation. Extra empty JARs would not meet this target. |
| 40 | Protected Daytona infrastructure | IN_PROGRESS: preflight/helpers and local package tooling; no live production mutation is part of this candidate. | Verify actual quota/credits/disk/ports/lifecycle/backups, bounded storage/logs and rollback before deployment. Preserve the protected sandbox; external AI provisioning is optional. |
| 41 | GTM Control Centre dashboard | NOT_STARTED as the requested web/backend service; GtmControlCentre is a staff inventory switch. | Implement authenticated roles/audit and real enabled controls for files/uploads/config/services/storage/backups/rollback/authorized hosting. Design panels are not operational controls. |
| 42 | Graphical access/commands/accessibility | IN_PROGRESS: phone/NPC menus, aliases, authentication commands and admin gating exist. | Make all ordinary gameplay reachable graphically with fallbacks/help/tab completion, reduced effects and tested touch/controller equivalents; avoid plugin command collisions. |
| 43 | Performance/resource engineering | IN_PROGRESS: bounded NPC admission, auth workers/queue and restoration batches exist; HUD allocation is being improved. | Measure CPU/memory/TPS/disk/network with 3–4 and up to ten players; implement remaining traffic/map/AI budgets. No measured 20-TPS release claim exists. |
| 44 | Automated regression/feature tests | AUTOMATED_TESTED only for executed JUnit/domain/static checks; the final build report identifies the tested source and artifact. | Add event/engine integration, clean install/upgrade/restart, concurrency/fault and final ZIP checks, including process termination during debit, player save, acknowledgement, death and world repair. Existing test success is not full specification coverage. |
| 45 | Creative/crossplay verification | AUTOMATED_TESTED for source/pack checks and recorded art reviews. | Test actual Java and Bedrock models/skins/HUD/phone/input/vehicles/seats/furniture/bubbles/cinematics and record platform differences. |
| 46 | World QA | IN_PROGRESS: limited survey and reversible patch evidence exists. | Produce building-level actual-location/entrance/floor/interior/route/light/sign/collision reports, protected-data comparison, patch hashes and rollback evidence. |
| 47 | GitHub workflow | IN_PROGRESS: a development branch and coherent increments are being prepared. | Commit/push verified work/evidence, inspect CI/PR state and preserve protected history. Record actual push results rather than assuming them. |
| 48 | Release verification lifecycle | BLOCKED at full integration/client readiness. | Close implementation → build → automated → integration → client → release gates for every applicable requirement. ZIP creation is not a playability test. |
| 49 | Integrated/reusable distributions | IN_PROGRESS: candidate plugin/art/packs and laptop/Daytona tooling are being assembled. | Include selected verified world/patch, configurations/migrations, real services, reports/checksums/licenses/rollback; meet all gates before using COMPLETE. |
| 50 | Dependency-aware execution | IN_PROGRESS: baseline/build, auth/state and art binding are active. | Continue transport/city services/roleplay/digital/world/infrastructure and final integration against shared contracts. |
| 51 | Autonomous continuity/truthful completion | IN_PROGRESS: concrete changes and explicit limitations persist in repository records. | Keep executing independent work and retain branch/commit/changes/tests/blockers/next actions. Do not substitute fake completion percentages for remaining requirements. |

## Dependencies for the remaining gates

1. **Account/session safety and transactions:** stable UUIDs, protected login, durable state and reward/purchase/delivery receipts. All gameplay entry points and delayed callbacks depend on this.
2. **One commissioned world registry:** actual services/properties/buildings/roads/rails/waterways/helipads, collision metadata, public/private boundaries and reversible modifications.
3. **Physical engines and bounded NPC jobs:** vehicles/traffic/rail/SkyLink/aviation/marine/furniture and occupations using shared authoritative rules.
4. **Economy, ownership and complete tasks:** commerce, deliveries, fashion, loans, government, combat/police/medical and a real 30+50 campaign; test reachability and persistence together.
5. **Edition presentation and digital services:** installed packs/mappings/skins, HUD/minimap/forms, 24 apps, Car App, verified news, displays and reversible city-wide festivals.
6. **Operational release:** real dashboard/backend, dependency/license review, clean portable installation, world rollback, actual client passes and measured performance before production deployment.

## Persistence and event-integration limits

Ledger debit and paid-item queue creation are one committed account update. Delivery writes the inventory and a receipt to vanilla player data before acknowledging that queue entry. This closes several ordinary retry and reconnect gaps, but Paper's player.saveData method returns no durable-write result; a logged write failure or power loss can still cross the player-data/ledger boundary. No claim of atomic item delivery across two files, crash certification or loss-free forced termination is made. Fault injection and actual client inventory checks remain release gates. Receipt capacity is bounded and needs an explicit archival/maintenance policy before sustained operation.

Medical decisions are keyed by a death receipt and use one ledger settlement. A recorded death counter separates later deaths, while an arrival marker keeps a cancelled hospital teleport retryable without reusing the earlier bill. Initial player-save exceptions preserve inventory without applying a charge. Inventory retention/drop behavior remains owned by Bukkit events and vanilla player data; real death, respawn, cancelled teleports, counter timing and save failures still require integration checks. Restoration journals block data and ordinary public-sign content before controlled damage and retries metadata only on a default, unmodified empty sign. Signs containing plugin persistent data and other sensitive block entities, including beds and containers, are protected rather than represented as complete NBT restoration.

## Hard external requirements

- A verified compatible Java 25/Paper/dependency set, legitimate artifacts and redistribution terms. Paper API compilation is not a runnable server distribution.
- The actual selected server/world copy, hashes and backup baseline. Manifests and LFS pointers cannot certify structures/routes.
- Actual Java and Bedrock clients for rendering, controls, authentication and interactions. Static validators cannot replace them.
- Signed-skin or other verified rendering integration for arbitrary custom Java NPC/player appearance; PNGs alone do not provide signed profiles.
- A verified network arrangement for Java TCP, the bundled Geyser transport and private administration. Geyser 2.12.1 build 1308's verified template uses NetherNet and loopback TCP/UDP 19132. Do not assume legacy UDP-only behavior or that a Java SSH tunnel provides external Bedrock reachability.
- Actual Daytona storage/quota/credit information and a fresh backup if deployment is later attempted. External AI and authorized music remain separate optional integrations.

## Evidence references

- [Native 128 generation report](creative/GENERATION_128_REPORT.md).
- [Authentication implementation and migration boundary](AUTHENTICATION.md).
- [State recovery, receipt limits and persistence boundaries](STATE_RECOVERY_R4.md).
- [Current build/runtime report](BUILD_RUNTIME_R4_REPORT.md).
- [Historical foundation verification](FOUNDATION_TEST_REPORT.md).

Unit tests do not exercise real Paper event ordering, inventory/death/respawn semantics, Geyser rendering or production networking. Those gaps remain open even when compilation, package CRCs and domain assertions pass.
