# Live hotbar, map and vehicle instruments

The original `hotbar_frame`, `hotbar_selected`, `minimap_circle`, `minimap_rectangle` and three `speedometer_*` native128 assets now drive actual controls and current game-state displays. Their 128×128 artwork remains unchanged. The server renders dynamic instrument readings on the same native pixel grid.

## Use the controls

Open `/phone` and choose **Your hotbar**. Its nine previews reflect the actual nine hotbar slots, including their existing item data. Select a preview to hold that real slot, or select the highlighted-slot control to advance to the next slot. The interface neither moves items between slots nor creates an inventory copy. Refresh updates all nine previews from the current inventory.

Choose **Live map** to receive or refresh the reusable terrain map. Phone settings change its circular or rectangular layout, zoom and rotation. The renderer samples already loaded world terrain within a bounded budget; unobserved terrain remains unknown. Registered destinations and current navigation use their existing saved data. A direct bearing is labelled as a bearing when no surveyed route exists.

Open **Motor Mile** and choose **Live vehicle dashboard** to receive or refresh its reusable map. Hold that item while occupying a supported vehicle. It shows the accepted movement speed, energy or battery, and actual condition. Phone settings select **Analog**, **Digital** or **Compact**. All three use the same current vehicle state. The analog needle changes with accepted speed; reverse motion has an explicit reverse label. The dial stops at its labelled 120 km/h limit while the numeric reading continues to report the actual speed. Leaving the vehicle produces an explicit **No active vehicle** display.

Terrain and dashboard items select different contexts of one saved per-world map identity. The server does not allocate another map every time a player refreshes a control. Current map mode, world and immutable display preferences form the short-lived frame-cache key, so a newly selected layout or instrument style takes effect immediately.

## Action and inventory rules

Every menu selection is bound to the current authenticated connection, the current inventory menu and a one-use action. The callback rechecks permission, player state and the selected source slot. Hotbar selection dispatches Paper's actual `PlayerItemHeldEvent`; cancellation prevents the selection. Current authorization and the previous held slot are checked again after other event listeners have run. An old menu or a deferred click from a revoked session cannot change the current slot.

The dashboard consumes the vehicle engine's current `DriveData`. It does not estimate speed from elapsed time, animate a fabricated fuel value or supply its own movement state. Dynamic images are drawn into a new native128 frame; the authored master image is never modified. Ordinary map-palette conversion still applies when Minecraft displays that frame.

## Evidence and scope

The coherent Java25 build containing these controls and the local owner-transport gate passed **522 JUnit tests across 63 suites**, with no failures, errors or skips. The three focused dashboard tests cover real-value image changes in all styles, preservation of source pixels, reverse indication, analog limits, and rejection of invalid dimensions or non-finite readings. The frozen core has SHA-256 `0b49d8e47935b4693f409ad51168a4a292f54b4536dc58ce717ab0bc45209d5c`.

The isolated `GTMPhoneControlsProbe` separately exercises real inventory bytes, current authorization, actual map delivery, real rendered frames and actual accepted vehicle motion from translated client input. Its report must identify the exact installed core and test companion. The successful ordinary-account run passed **24 of 24 checks**, with no skipped/unexecuted cases or retained fixture. Its original auto travelled **1.9115 blocks** in 19 observed moving samples. The accepted vehicle reading changed from 0 to 1.25 blocks/second, with real energy consumption; the moving analog raster changed accordingly. The account was not an operator, and the probe granted no currency, vehicle or positive permission. See [the actual report](reports/PAPER_PHONE_CONTROLS_R4.json) and [its exact input hashes](reports/PHONE_CONTROLS_R4_EVIDENCE.json). Earlier runs exposed a layout-cache bug and a fixture account/vehicle mismatch; both remain recorded as failures. The production cache was corrected, and the fixture was run with the existing auto's actual owner without changing its ownership.

These are working vanilla-map and inventory-menu controls. A permanently repositioned corner hotbar, a fixed corner minimap, native Java/Bedrock visual fit and human client input remain separate qualifications. The protocol test downloads and checks the real resource pack but does not render the native client interface. The test companion and its setup fixtures do not belong in the playable ZIP.
