# Read-only starter property and food-counter survey

The pinned public world contains a suitable **static geometry candidate** for an optional local furnishing playtest: an existing **8 × 8 brick courtyard**, with eight clear blocks above its floor, and a separate **4 × 4 clear counter space** nearby. This survey does not register a property, assign an owner, place a model, commission a restaurant, or enable a feature.

The source is `EXPECT_SDCRAFT_PUBLIC_WORLD_2026-11-23.zip`, SHA-256 `214a00a08acdb5f73fea52ef79cdfdf773551086d31f5f95725f559ad0802dc2`. The archive hash was identical before and after the survey. All world and configuration operations were read-only. The reproducible cell checks, state digests and full approach trace are in [the survey JSON](reports/PUBLIC_WORLD_STARTER_PROPERTY_SURVEY_R4.json).

## Candidate geometry

All coordinates refer to world `world`. Integer ranges in this table are inclusive block coordinates.

| Area | X range | Z range | Floor | Clear air | Complete checks |
|---|---:|---:|---:|---:|---:|
| Proposed private furnishing parcel | −179 through −172 | −75 through −68 | y67, all brick | y68 through y75 | 64 floor cells and 512 air cells |
| Separate public food-counter space | −186 through −183 | −74 through −71 | y67, all brick | y68 through y74 | 16 floor cells and 112 air cells |
| Public corridor immediately west of parcel | −182 through −180 | −75 through −68 | y67, brick and stone brick | y68 through y71 | 24 floor cells and 96 air cells |

The proposed parcel's continuous bounds are **[−179, −171) × [67, 76) × [−75, −67)** in X/Y/Z order. Its normal standing/placement height is **y68**. A useful pedestrian entrance is **(−178.5, 68, −74.5)**. Every cell was decoded from modern Anvil block palettes; checks were not limited to corners or sample columns.

Keep the parcel bounds exact. The surrounding one-block border contains **12 existing oak-stair cells at y68**. Those cells are outside the proposed parcel and are not proposed for removal or replacement. The route and public west corridor must remain outside private furniture footprints.

No saved entity position was found within the larger inspected volume **x −205..−140, y60..82, z −110..−60**. The complete corresponding entity region was decoded, including nested passengers. This does not predict future mob spawns, players, or runtime display entities; the runtime must still perform its normal loaded-world collision checks.

## Food-counter candidate

The proposed service point is **(−184.0, 68.0, −72.0)**. It is outside the private parcel and can be reached along the existing brick surface. The nearby public corridor provides access without entering the private claim.

For a future reviewed service placement, the current `gtm:vendor_kiosk_tea` model at yaw 0 has local bounds **(−1.078, 0, −0.866) to (1.078, 2.3815, 0.866)**. At that point its complete bounds would be **(−185.078, 68, −72.866) to (−182.922, 70.3815, −71.134)**, contained in the checked counter space. This confirms geometric room only. The counter has not been placed or granted; staff/service ownership, the actual commissioned `food_<brand>` service location, stock, access, and feature permissions remain required.

The empty parcel contains no bed, chest/barrel, cooking processor, cauldron, lever, trapdoor, or LIGHT backing block. Seats, suitable freestanding workstations and other supported non-backing furniture can use the parcel after legitimate ownership is recorded. Designs that require an existing vanilla backing block remain unavailable until that real block is legitimately installed and bound. Nothing in this survey supplies inventory contents or entitlement tokens.

## Approach evidence

The published dealership seed **(−150.5, 67, −82.5)** was verified against the saved floor and used as the start of a conservative pedestrian trace. The verified route reaches the parcel via the west side of the existing structures. It has **102 horizontal block steps**, with **103 complete full-cube floor checks and 309 air checks**. Every route cell has three complete air blocks above its supporting floor.

This route includes one **one-block upward jump**, from **(−157.5, 67, −84.5)** to **(−158.5, 68, −84.5)**. The adjacent cells and overhead space were checked. The rest of the trace is level at y68. No doors need to be opened and no blocks need to change. Key turns are recorded below; the JSON contains every intermediate cell and all turns.

| Order | Block-centre position | Role |
|---|---|---|
| 1 | (−150.5, 67, −82.5) | Checked dealership starting point |
| 2 | (−157.5, 67, −84.5) | Lower side of the one-block rise |
| 3 | (−158.5, 68, −84.5) | Upper side of the jump |
| 4 | (−167.5, 68, −87.5) | Follow the pavement north; intervening bends are in the full trace |
| 5 | (−169.5, 68, −97.5) | Turn west |
| 6 | (−196.5, 68, −97.5) | Turn south |
| 7 | (−196.5, 68, −76.5) | Turn east onto the brick approach |
| 8 | (−192.5, 68, −74.5) | Continue east toward the courtyard |
| 9 | (−178.5, 68, −74.5) | Parcel entrance |

The reader rejects stairs, slabs, closed doors, vegetation, liquids and unknown support materials when constructing this conservative route. A shorter live pedestrian route may exist, but it was not substituted for the checked route. This is **not a scooter/courier route**, wheelchair-accessible route, or native-client walking qualification. Courier staff must survey and validate a separate continuous driving route through the actual server vehicle collision engine before offering delivery.

The chef seed at **(10.5, 70, 3.5)** was also inspected. Its immediate clear floor lies on the narrow gray/white paved arrival route, so no private parcel is proposed at that seed. The larger empty brick courtyard avoids allocating that arrival corridor to furniture.

## Applying this to an optional isolated laptop playtest

The base configuration remains untouched. Ordinary furniture placement currently requires a real owned registered property; the empty base property registry is therefore still a deliberate blocker. A separately reviewed local playtest configuration can use the exact integer bounds above with a legitimate property identifier and price, enable the property/furniture modules, and let an authenticated account acquire ownership through the existing property purchase workflow. The survey does not invent those commercial or ownership values.

Before activation, check the copied world's current blocks and entities again, then walk the approach with the actual client. Verify property purchase, owner placement/rotation/removal, guest/stranger refusal, and safe egress without relaxing the normal checks. Explicit permissions for `gtm.properties`, `gtm.furniture`, and any selected food service are required; a module flag alone is insufficient. Food orders should use the separate commissioned counter, with real stock, debit, preparation and pickup behavior.

This finding is saved-block evidence only. It does not supersede the outstanding real Java/Bedrock model, interaction, restart, and crossplay qualification gates.

## Reproduction

From the repository root:

```sh
python tools/survey_starter_property.py \
  /workspace/scratch/d7d343b39c16/laptop-inputs/EXPECT_SDCRAFT_PUBLIC_WORLD_2026-11-23.zip
```

The script imports the existing `tools/survey_world.py` reader, rechecks every stated cell, checks saved entities, recomputes the approach, and refuses to publish the proposal if those clearances fail or the input archive changes while being read. It writes only its JSON report. No server, world, base configuration, property registry or service data is opened for writing.
