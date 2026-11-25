# Owned generator and transformer runtime

The native 128×128 `gtm:diesel_generator_silent` and `gtm:transformer_station_sub` now have a finite supplied-power implementation. They keep their existing furniture identities, placements and real lever bindings. No inventory, world block, property or ownership record is duplicated to create a power network.

## Player operation

1. Own and place the generator or transformer using its existing furniture workflow. Bind each machine to an actual unused lever in your property before placement. The lever is the machine's physical running output.
2. Place and bind owned lights or ordinary lever-controlled furniture nearby. Set each consumer's normal switch to the desired state. A switched-on consumer requests power; it cannot bypass a stopped linked source.
3. Use the generator to open **Power | Generator**. Hold plain vanilla coal or charcoal and choose **Insert one held coal or charcoal**. Each item is consumed and supplies **40 game energy units**, up to 4,000 stored units. This is the game's explicit fuel recipe, not a simulation of real diesel chemistry.
4. Open **Owned output connections** and select the appropriate nearby owned objects. Each source supports at most 8 output links. Both endpoints and their entire connecting volume must be loaded and inside the owner's accessible property, with at most 16 blocks between endpoints. No chunks are forced to load by the runtime.
5. Start the generator. If using a transformer, connect the generator to it and start the transformer too. Physical LIGHT levels and lever states follow the available supply. Stop or reset each machine through its own controls.

The connection list only offers supported objects that can currently be connected. A consumer has exactly one upstream source. Generator-to-generator links and transformer chains are refused. Traffic signals are excluded from ordinary relay outputs because their phase controller has a separate authority.

## Capacity and fuel

| Element | Game load |
| --- | ---: |
| Switched-on linked LIGHT | 1 unit |
| Switched-on ordinary lever output | 2 units |
| Running transformer overhead | 1 unit, plus its active consumers |
| Generator running overhead | 1 energy unit per accepted second |

A generator supports **8 downstream load units**. A transformer supports **4 downstream consumer units**. The generator consumes its overhead plus actual eligible demand for each 20 accepted server ticks. The state store commits the energy debit before the corresponding transient power lease is applied to the world. Unloaded, unplaced, inaccessible or switched-off consumers receive no supplied power.

Exceeding a machine's capacity trips a saved cutoff. Its outputs turn off, and lowering demand alone does not reset the breaker: the owner must use **Start / reset cutoff**. If remaining energy cannot fund the next complete power lease, the generator stops. Small remaining energy is retained and can be used after reducing the load or adding another fuel item.

## Ownership, manual controls and recovery

Controls recheck authentication, current session, furniture permission, ownership, placement, loaded backing, property access, reach and line of sight. A deferred menu callback repeats those checks before consuming anything. Connections are revalidated during operation, and an invalid intermediate cannot keep downstream loads energized.

Removal, projection loss, logout/authentication loss, permission loss and shutdown stop the relevant outputs. Machine start intentions are disarmed on restart; stored fuel and links remain. The owner explicitly restarts the machine after its prerequisites are restored. There is no offline fuel burn and no replay of a pre-restart power lease.

Connected consumers retain their saved manual settings. Supplied power and a manual on-request are both necessary. Disconnecting an output returns it to those saved manual controls. Removing an entitlement's placement still uses the existing furniture restoration policy for its originally bound block. The power adapter never obtains a second reservation or silently creates a replacement lever or LIGHT.

Fuel insertion debits the real held item and submits the player's inventory plus a bounded pending-supply proof for saving before crediting the power store. A monotonic owner sequence, nonce, exact generator and material make the credit idempotent. An unresolved state-store failure retains the proof for recovery; retrying it does not also consume another item. Older, skipped or changed receipts are refused. A pending proof for one owner prevents that owner's grid from starting while it is unresolved, without stopping other owners' valid grids.

**Paper's `Player.saveData()` returns no durable-write acknowledgement.** The ordered proof/credit protocol does not claim cross-file atomicity or a proven hard-power-loss guarantee. The domain tests cover state-store commit failure, restart and receipt replay; a destructive JVM/disk interruption campaign remains a separate qualification.

## Implementation and evidence

- `GtmFurniturePower` owns session-bound controls, the connection GUI, physical fuel debit/proof recovery and transient power leases.
- `furniture/FurniturePowerStore` owns finite energy, controller capacity, exact source links, cutoff state and bounded monotonic receipt records in `furniture-power.snapshot`.
- `GtmFurniture` remains the only owner of existing backing reservations and physical LIGHT/lever writes. Its transient override is combined with each consumer's manual request. Auth-loss cancellation has an off-only path for unchanged still-reserved loaded backing.
- The shared furniture aggregate now writes FUR3 and still reads FUR1/FUR2. The separate power state preserves the original furniture and owner IDs; it does not replace that aggregate or create duplicate entitlements.

Thirteen focused power-store tests passed on Java 25 against the exact Paper 26.3 build 255 API. They cover energy exhaustion, replay and restart, monotonic receipts, ownership, one upstream source, transformer and generator overload, manual demand, operational-state exclusion, disarming, capacity, corrupt state and a failed snapshot commit that returns no power lease.

The separate companion in the source-checkout path `tools/probes/furniture_power` passed all **16 actual-Paper scenario/cleanup records** again on final core `b7c76cd3a664e1bb7e1e56fd2098f7ef0a71e921d47170ed10c4e658974715af`, in run `20261125T024626783921Z`. There were no failed or unexecuted power steps and no remaining power fixture. The [current actual server report](reports/PAPER_FURNITURE_POWER_R4.json), SHA-256 `aa7e61efdbeb7cbced0db963b155a1aae4a32e3d89b96decdabed956d4eb898f`, records consumed coal, actual LIGHT/lever changes, transformer overload, fuel exhaustion, permission/session/removal shutdown and restoration of manual control after unlinking. The [shared runtime evidence](reports/FINAL_SHARED_RUNTIME_REGRESSIONS_R4.json) retains its exact binary and input-manifest provenance.

This final repeat used the strict Java-only gameplay mode with normal Java authentication and identity rules. Geyser/Floodgate originals were preserved outside plugin admission; it is not native Java/Bedrock visual or human-input qualification. The earlier 428-case baseline pass from run `20261125T001320Z` remains [separate historical evidence](reports/PAPER_FURNITURE_POWER_BASELINE_PRE_FINAL_R4.json). The later ottoman failure in the final multi-scenario batch does not change this completed 16-record power result or establish a whole-batch pass. Real power-loss durability and production qualification remain separate.
