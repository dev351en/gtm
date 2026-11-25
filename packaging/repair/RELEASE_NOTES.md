# GTM 1.0.5-r4-spec-candidate — HUD, NPC and passengers

This candidate corrects the mismatch between the approved UI and the earlier inventory-phone repair. The **optional Java client HUD** puts nine real item slots at the top left, the terrain minimap at the bottom left, wanted stars/wallet/bank at the top right and the clickable phone at the bottom right. The phone uses the existing colourful custom logos.

**Install the server update and the optional client component to obtain that layout.** A resource pack alone does not relocate the Java hotbar or provide a clickable overlay. Ordinary clients retain access through the existing server menus. The optional Fabric component is for Minecraft 26.3 / Java 25; exact dependencies and controls are in `client/README.md`. Some phone apps hand detailed transactions to their existing server inventory UI.

## Runtime repairs

- The traditional auto has one driver and **three rear passenger places**, with a widened real bench/body/canopy, matching wheel pivots and collision bounds. Occupied driver seats no longer prevent boarding a free passenger seat through the garage. Locked guest access remains protected. Two emergency cars expose their already-authored front passenger cushions.
- Nearby NPC right-click selection and explicit `// message` conversation work through one authenticated path, with temporary overhead responses. The dialogue permission is available to ordinary authenticated players. WorldEdit commands and staff service menus retain their gates.
- All population modes share the32 physical-actor/four admissions limits, ownership tags, loaded-chunk checks and separation rules. Without Citizens, Paper pathfinding handles wandering, fleeing and retaliation. Protected staff remain protected; eligible tough ambient NPCs can fight back with line-of-sight and cooldown rules.
- Native/legacy weapon target checks recognize strictly owned attackable NPCs while retaining shooter authentication. The earlier native guns, pack-reference fixes, ordinary equipment access and Control Centre remain included.
- A bounded text-only provider adapter supports an existing local Ollama or HTTPS OpenAI-compatible service. **The default is explicitly offline/scripted; no live language model is installed or claimed.** Mode and fallback outcomes are visible in player chat, `/sdc status` and the Control Centre.
- The stopped-server updater now accepts the exact reviewed 1.0.3 and released 1.0.4 cores, preserves existing data/configuration, checks integrity, records backups and supports rollback. It never installs client mods or updates Daytona automatically.

## Verification record

The maintained server compiled on Java 25 and passed92JUnit tests. The optional client passed18JUnit tests after native play exposed a shortcut conflict and map clipping. Pack checks passed12tests, auto geometry9, updater24 and publication17;826 equipment compatibility assertions and exact bytecode transformation checks also passed. Counts describe the specific checks, not the number of gameplay features.

A real Fabric 26.3 client joined the staged Paper server through ordinary registration without op. The requested four-corner layout, live account values, real slot selection, original colourful phone logos, popup click, `/phone`, phone-item routing and authorized Bank menu handoff were observed. Final exact-artifact screenshots and native NPC/passenger results belong in `SPEC_REPAIR_2026-11-25.md` and the included evidence records. Compilation and headless protocol checks are distinguished from native rendering.

The build is a maintained source overlay plus narrowly hash-checked patches over the preserved 1.0.3 core. It does not claim recovery of all missing original source. `build-report.json`, `pack-repair-report.json`, `client/build-report.json` and `SHA256SUMS` identify exact output bytes.

## Remaining work

This is **not a fully finished Revision 4 release**. Bedrock's equivalent custom HUD and native crossplay acceptance are outstanding. An actual generative model must be configured and tested separately. The fleet audit records 30 civilian cars with only two authored front seats and four buses without passenger interiors; rear rows and full interiors are unfinished. Broad terrain/suspension testing, full police pursuit/arrest, Citizens-present human NPCs, Windows execution, audio and the wider campaign/furnished city remain open.

No protected production server or main branch is deployed by this candidate. Use the included installation and rollback guide, and preserve the existing owner configuration.
