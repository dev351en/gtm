# CCTV and fictional game booking furniture

## Implemented behavior

The exact existing model IDs `gtm:surveillance_wall_cctv` and `gtm:booking_fingerprint_kiosk` now have their own native gameplay helpers. They preserve the original ownership IDs and placement rules. Opening either requires the current authenticated owner, furniture permission, a live unobstructed placement, current property access, visibility and a position within five blocks.

### CCTV wall

The owner can commission four real camera points within 32 blocks of a placed wall. A point captures the owner's actual eye position and direction, and its full installation footprint must be loaded and inside owned accessible property. From the point, use:

```
/furniture civic camera <wall-instance-uuid> add Camera name
```

Return to the wall and use its camera controls. Hold exactly one ordinary blank map to issue a real monitor, or hold the previously issued monitor to reopen it. Each issued physical monitor consumes one blank map. The wall retains its original native MapView identity; reopening an existing monitor consumes nothing. The monitor is bound to its owner and wall, and other viewers receive a paused canvas.

The 128×128 canvas uses a native 128×104 perspective viewport with status strips. It progressively samples actual loaded block map colours and projects the current bounding boxes of up to 16 real living entities or vehicles. Only currently authenticated players appear as player silhouettes. It is a schematic block-and-entity security view; it does not reproduce resource-pack mesh textures or promise a video frame rate. The footer reports update progress and the age of the last completed frame. Direction controls turn by 15 degrees or tilt by 10 degrees, within a 75-degree pitch limit.

The view has a 16-block range and a 70-degree horizontal field of view. Across at most four simultaneous viewers, the task permits at most 4,096 ray-cell visits and 512 completed ray pixels per tick. A cache is limited to the current progressive frame. Entity gathering is bounded to 128 examined candidates and 16 visible silhouettes. A ray stops at its first real non-air block or at a withheld cell; entity silhouettes are clipped against the first block depth.

Before sampling and rendering, the complete conservative viewing volume must remain loaded, inside the world height and border, and accessible under the current native property policy. Sampling never loads a chunk. Each block access additionally checks its exact chunk. The owner must remain authenticated in the same session, hold the correct monitor, keep furniture permission, and remain beside the live owned wall. Losing any condition clears the displayed viewport and labels it paused. Removal, unload, authentication loss, direction changes and plugin shutdown stop the view. A new connection must explicitly reopen it. Previously observed information cannot be erased from a viewer's memory or an offline client's historical image cache; the server does not continue providing it.

### Booking kiosk

The kiosk records fictional game-account facts, not real fingerprints or biometric measurements. Its ordinary self-identification action records the owner's own game UUID, current account name, kiosk ID, case ID, label and time. Self-identification grants no authority over another player.

Recording another account requires the existing `sdcraft.police` or `sdcraft.admin` policy and a nearby authenticated, living, non-downed player. The target receives explicit accept and decline commands. Consent is bound to the exact operator UUID/session, target UUID/session, kiosk and request ID. It lasts 60 seconds. Acceptance rechecks both sessions, current operator authority, ownership and placement, the target's distance from the kiosk, a six-block operator/target distance, mutual line of sight, and both accounts' full property access to their corridor.

```
/furniture civic book <kiosk-instance-uuid> self Optional case label
/furniture civic book <kiosk-instance-uuid> request ExactPlayerName Optional case label
/furniture civic accept <request-uuid>
/furniture civic decline <request-uuid>
```

The consent commands work for a normal authenticated target who does not own the kiosk or have furniture permission. They do not bypass authentication. Requests create no case until successful acceptance. Authentication loss, removal, decline or an invalid acceptance cancels the request. No wanted level, custody state, real-world identity or biometric match is invented.

The bounded archive retains at most 4,096 immutable case records. Reading or exporting requires the original operator at that same currently usable owned kiosk. Third-party cases also require current police authority. Menu actions recheck these conditions after scheduling, and open civic menus close within five ticks if current source or case authority is lost.

To export a case, hold exactly one ordinary `BOOK` and carry one ordinary `INK_SAC`. Both actual supplies produce one real `WRITTEN_BOOK` containing the saved case facts and export receipt. Custom items and authored books are not consumed. The output replaces the held book slot. Each case permits one supplied export; the archive remains available under current authorization. Vanilla book-copying rules are separate from this one-export receipt.

## Persistence and limits

`furniture-civic.snapshot` contains bounded camera positions, original map IDs, immutable case facts and one export receipt per exported case. It contains no inventory. Camera sessions and pending consent requests are transient and cannot resume after restart. Map IDs cannot be reused across walls, and a missing saved MapView fails closed for review instead of silently replacing its identity.

The case-book output, consumed inputs and a pending receipt proof share the existing vanilla player-data checkpoint. A matching proof can acknowledge the original export without producing another book or charging again. Malformed or contradictory proofs are retained and block further export. Paper's `Player.saveData()` has no durable-write acknowledgement, so this does not establish cross-file atomicity or recovery from arbitrary power loss. Unresolved proof and snapshot failures require review; no second inventory database is created.

## Verification

The focused Java 25 source run passed 23 JUnit tests across three suites: camera perspective axes and conservative volume, exact first-surface/depth clipping, finite global sampling budget, negative-coordinate DDA, withheld cells, store identity/restart/corruption, immutable cases and one-export receipts, consent sessions/deadline/authority/range, and saved-proof parsing. A peer read-only review found no concrete defect in the pure store/projection classes. The full core gate is owned by the coordinating build step.

The isolated actual-Paper companion is `tools/probes/furniture_civic` (source checkout: `tools/probes/furniture_civic/README.md`). Its fresh run **passed all 30 records**, with no remaining fixture or unexecuted steps: [PAPER_FURNITURE_CIVIC_R4.json](reports/PAPER_FURNITURE_CIVIC_R4.json), run `20261125T010315569119Z`, core SHA-256 `04a899018a732096efeb4ed17b58f33fe061c4382579cb57299a2fbc33a98631`. It observed real sampled colours after block changes, a real moving player's silhouette, actual monitor item consumption, access-loss clearing, current property denial, normal reauthentication, explicit consent, real book/ink consumption and the written result. Restart readers, exact receipt replay and malformed-proof rejection also passed.

An earlier run reached the post-login step before the ordinary furniture task had restored its projections. The corrected companion waits for valid display and interaction entities after the new nonce, while continuously requiring the former camera session to remain stopped. It does not invoke production reconciliation. The civic production implementation was unchanged for the successful retry. These server, protocol and recording-MapCanvas checks do not establish native Java or Bedrock screen rendering.
