# GTM owned vehicles and furniture — current interaction candidate

**Date:** 25 November 2026
**Version:** `1.0.2-r4-interactions-candidate`
**Target:** Paper 26.3 build 255, Java 25
**Prior checkpoint:** `560dcef9df1c3883f49b68597d43f188337a111b`

This increment adds actual gameplay adapters to existing native 128 assets. It is not a completed implementation of all 51 master-prompt sections, and it has not been certified by a real Java or Bedrock play session. The shipped native vehicle and furniture flags remain disabled pending their runtime gates. The separate historical [1.0.1 build report](BUILD_RUNTIME_R4_REPORT.md) describes the earlier authentication, resource-pack and laptop checkpoint.

## Auto-rickshaws are already included

| Stable ID | Model | Implemented road seats |
|---|---|---|
| `gtm:rickshaw_traditional` | Indra Auto CNG Passenger | Driver and two rear passengers |
| `gtm:rickshaw_electric` | Indra Mayuri E-Rickshaw | Driver and two rear passengers |
| `gtm:rickshaw_cargo` | Indra Loader Cargo 3-Wheeler | Driver; cargo storage/hauling remains unimplemented |

No replacement artwork or new identity was needed. All three retain their native128 normal, damaged, critical and wreck models. The road registry contains 65 exact authored profiles and 260 model-state transforms. The other 62 road profiles have an additional qualification option; rail, ropeway, helicopters and boats are outside this road engine.

## What the vehicle code actually does

`GtmVehicles` receives authenticated server input and computes acceleration, braking, reverse travel and steering. Body sweeps check loaded terrain, collision shapes, other vehicles, pedestrians, furniture and private property access. Real players mount passenger carriers; the displayed model supplies the appearance. The driver and passengers retain a connection nonce, and every occupant's property access is checked during motion. Logout, permission/session loss, death and teleportation end stale vehicle control.

Fuel/battery state, condition and distance travelled are server state. Movement consumes energy for accepted travel; exhausted or failed vehicles stop propelling. Damage changes the visible state model. The speed display uses accepted horizontal displacement, with the explicit game convention of one block per metre and kilometres per hour equal to blocks per second multiplied by 3.6. This is not a statement about real vehicle performance.

The garage has owned vehicles, shop and service controls. Ownership and keys are UUID records rather than decorative inventory items. One configured starter auto uses a deterministic grant ID, so repeated login or kit requests do not mint additional cars. New native records do not migrate, overwrite or delete existing MTVehicles ownership.

New refuelling and repair work requires the authenticated owner, a stopped nearby vehicle, the actual registered gas/maintenance site, property access and sufficient bank funds. A full vehicle rejects an unnecessary paid service. The service condition and its receipt commit together; a retry acknowledges already-completed work even after leaving the site.

See [VEHICLE_RUNTIME_R4.md](VEHICLE_RUNTIME_R4.md) for the exact geometry, limits, persistence and API evidence. [NATIVE_VEHICLE_CLIENT_ACCEPTANCE.md](NATIVE_VEHICLE_CLIENT_ACCEPTANCE.md) records the required real-client checks. Wheel animation, headlights/indicators, full dashboard choices, theft, insurance, towing, cargo handling, NPC traffic and the remaining transport engines are still separate implementation work.

## What the furniture code actually does

The explicit 200-ID capability registry distinguishes 79 implemented or conditional behavior bindings from 121 unsupported designs. The default bank-only service allowlist would expose 73 designs if the furniture runtime were enabled. That count is not 73 client-certified models, and the shipped runtime itself remains gated.

| Behavior family | Models | Actual interaction |
|---|---:|---|
| Seats | 20 | One real owner-controlled player seat; no implied transport, restraints or extra sofa seats |
| Storage | 38 | Opens a protected existing single chest or barrel; items remain in vanilla storage |
| Beds | 6 | Uses a bound real overworld bed under normal sleep rules; no healing implied |
| Lights | 7 | Toggles an existing dry `LIGHT` block between zero and its saved brightness |
| Workbench | 1 | Opens the real crafting workbench and consumes normal recipe ingredients |
| Conditional service terminals | 7 | Only work when their real service callback is configured; this increment includes an ATM account interface |
| Unsupported specialist/surface designs | 121 | Excluded from the functional shop until their specific behavior exists |

The furniture menu has an owned collection and direct place, bind, use, rotate, remove, disconnect and storage-repair controls. It does not require entering entitlement UUIDs. World targeting expires and rechecks ownership, authentication, permission, loaded chunks and property boundaries. Purchases requiring backing blocks reject payment unless a suitable real block is available. Other purchases require a suitable owned footprint before payment.

The same saved entitlement moves between available and placed state. Removing a placement preserves the backing block and its contents. The module does not create transferable vouchers or copy container inventories. A matching interrupted container reservation can be repaired by its authenticated owner; changed/conflicting blocks fail closed. Real property ownership remains valid when its owner is offline. No apartments or facility interiors are claimed to be commissioned by these source changes.

The ATM interface provides actual deposits and withdrawals on the existing account. Withdrawals retain the private bank PIN workflow. Unimplemented police, wardrobe or medical terminals are not made functional merely by opening a generic menu. Food terminals remain conditional on the existing food service and a commissioned counter.

See [FURNITURE_RUNTIME_R4.md](FURNITURE_RUNTIME_R4.md) for every model's capability, source geometry, block requirements and pending validation. The [primary model functionality CSV](reports/PRIMARY_MODEL_FUNCTIONALITY_R4.csv) distinguishes art availability from runtime behavior across the original 509 designs.

## Purchase and recovery behavior

The financial ledger writes the bank debit and ownership/service intent together. The receiving module saves the same receipt UUID before acknowledgment. Matching retries preserve one purchase and one resulting entitlement/service; mismatched receipt contents are rejected. A reported financial save failure restores the committed balance and intent. The new tests cover restart, replay, insufficient funds, changed requests, failed saves and acknowledgment recovery.

Road state uses `vehicles/parked.snapshot`; furniture uses `furniture.snapshot`. Both use the existing bounded checksummed snapshot store. Periodic road checkpoints can rewind recent motion/energy after a forced process loss. Furniture bindings and vanilla block/player data remain separate persistence boundaries. These mechanisms are not a claim that arbitrary power loss across every Minecraft file has been solved. [STATE_RECOVERY_R4.md](STATE_RECOVERY_R4.md) records limits and recovery boundaries.

## Verification and artifact identity

The coordinated clean Java build and the final `check jar` after all source amendments passed 181 JUnit cases across 24 suites, with zero failures, errors or skipped cases, plus 155 domain smoke assertions. This includes 21 road-domain tests, 16 furniture-domain tests and 8 purchase/service ledger tests. Production Java/resources did not change during or after the final run. [Machine-readable evidence](INTERACTION_RUNTIME_R4_EVIDENCE.json) records the final candidate and its complete input digest.

| Final artifact | Value |
|---|---|
| Plugin | `source/build/libs/SDCraftCore-1.0.2-r4-interactions-candidate.jar` |
| Size | 627,146 bytes |
| SHA-256 | `14231bdedace63be6f37a282c78d45afa39bd22e3beefbbd5810adfbc99afe78` |
| Source/build-input SHA-256 | `d3880782715a64f9f54024a61f7e5f79f09c899ad24b50253a02e392a61e6ef9` over 115 sorted input files |
| JAR validation | ZIP CRC passed; classfile major 69; descriptor and embedded catalogues match source |

Read-only generation checks verify 65 road profiles and 260 state transforms against their native source. All 460 unique road-state/furniture model IDs resolve to Java item definitions and explicit Bedrock paper mappings in the merged packs. This is a resource-graph check, not visual or input compatibility evidence.

The isolated MockBukkit probe initializes with its advertised Paper 26.3 build 200 baseline. The exact target build 255 cannot initialize that mock because its registry fixture lacks `minecraft:world_clock`. No production dependency was downgraded. Five initial metadata/entity/mounting/scheduler capability checks passed. The focused final-menu probe passed 12 cases, with zero failures and two unsupported LIGHT block-ray cases. It uses the actual menu/targeting source and a fake backend, so it tests dispatch and access checks rather than full module behavior. Unsupported mock paths remain unverified. The exact build255 plugin compilation, pure domain tests and source/bytecode inspection do not replace a running Paper world.

No Minecraft EULA was accepted by the agent, no actual Paper world was started, and no real Java/Bedrock client session, Windows execution, multiplayer benchmark or complete crash-injection campaign has been certified. The laptop package uses the inspected public world snapshot dated 23 November 2026, not a current private Daytona export. No protected Daytona sandbox, production world or main branch was changed.

## Next release gates

1. Obtain the intended consistent private server export or deliberately continue with the dated public world; preserve the original and identity policy.
2. Use an owner-accepted disposable server copy for exact-target boot/restart and the documented vehicle/furniture checks.
3. Verify native Java and Bedrock rendering, input, seats, body collision, storage, permissions, disconnects and paid recovery. Record failures and fix them before normal activation.
4. Commission actual properties/interiors and complete the remaining model-specific and master-prompt systems. A candidate ZIP or unit-test total is not a completed game.
