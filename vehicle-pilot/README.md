# GTM Java Auto-Rickshaw Vehicle Pilot v0.1

**A new standalone Paper plugin, not a mandatory client mod.** This choice respects the owner's vanilla Java PC and FoldCraft Java Android clients (max 2 GB Minecraft heap).

The reproducible, byte-verified source snapshot is `ci-source.tar.xz`; expand it using `tar -xJf ci-source.tar.xz`. Its SHA256 is `204324d4b185a5d5aa4fdbf84e8f0f85f8bfbd395185455763facf97d5721ad5`. Java 25 + Paper 26.3 API 26.3.build.258-stable compile is checked by [the workflow](../.github/workflows/vehicle-rickshaw-pilot.yml), together with four deterministic vehicle physics unit tests and an isolated Paper server boot.

The actual 123-part, 128×128 UV-mapped Blockbench source, generated Java resource-pack model, standalone GTM vehicle Java pack, combined GTM resource pack, editable Java source and installation notes are packaged in the downloadable development ZIP delivered to the owner. This GitHub branch deliberately contains **no production-world files, player data or Daytona mutations**.

Runtime implementation: one modelled ItemDisplay, four invisible mount anchors and one Interaction hitbox per rickshaw; WASD motion, braking, limited collision checks, fifth rider rejected, commands /gtmrickshaw spawn|give|remove|status, capped at six rickshaws by default. First-stage pilot only; fuel, damage, ownership, garages and true mobile play certification are pending.

The plugin source is not yet integrated into GTM's main SDCraftCore and has not been installed on the protected server. A static pack audit or CI boot does not prove passenger seat alignment or real FoldCraft frame rate. See the package's TEST_PLAN.md for manual acceptance.
