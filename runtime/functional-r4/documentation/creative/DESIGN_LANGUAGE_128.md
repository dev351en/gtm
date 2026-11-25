# GTM / Indraprastha — 128×128 design language

**Production profile:** `INDRAPRASTHA_128_V1`  
**Effective user direction:** 25 November 2026  
**Machine-readable profile:** `creative/design_language_128.json`

Use **native 128×128 artwork for all new square texture and icon masters**. This profile supersedes the earlier 32-pixel production profile for future asset generation. Preserve the existing GTM identities, material families, registry IDs and original Indian urban art direction while adding detail that actually uses the 128-pixel grid.

The profile governs art generation. A generated model, icon or texture does not establish working gameplay, correct live-world placement, signed NPC skin binding, or Java/Bedrock client verification. Those gates remain separate.

## 1. Visual identity

The setting is **Indraprastha**, the original coastal Indian metropolis in **GTM — Grand Theft Mumbai**, created by **SD Craft**. Draw from public transport, workshops, apartment interiors, street commerce, coastal infrastructure, local textiles and contemporary Indian city life. Maintain a coherent voxel world with readable silhouettes and purposeful detail.

Use original fictional identities. Preserve **ARK Coins**, **JEEVA AI**, **SD Motors**, **SD Interiors**, **Indraprastha SkyLink** and **GTM Control Centre** where their approved assets require them. The ARK mark is a geometric A–K monogram with a shared upright. Keep its shape consistent across banking, payment, coins and interface art.

| Colour | Hex | Primary role |
|---|---|---|
| Graphite | `#151B20` | Main interface surfaces, dark metal, structural contrast |
| ARK gold | `#D6AD59` | Brand identity, important edges, ownership and currency |
| Emerald | `#236653` | Transit, navigation, banking and contextual positive states |
| Sandstone | `#D2B997` | Warm neutral glyphs, stone, furnishings and secondary text |
| Terracotta | `#AD5637` | Warm accents, street materials, selected food and warning contexts |

Supporting paper white, blue, red and material-specific colours are allowed when the object needs them. Food should remain identifiable, vehicles retain their approved liveries, and festival colours should suit the festival. Do not recolour every subject gold merely to match the interface.

## 2. Resolution and export rules

| Asset | Canonical source | Additional output or exception |
|---|---|---|
| Material and world texture | 128×128 RGBA PNG | Pack-specific copies may reuse the same bytes |
| Inventory render | 128×128 RGBA PNG | Larger contact sheets are previews |
| Phone, HUD and square brand icon | 128×128 RGBA PNG | Editable SVG where appropriate |
| NPC skin | 128×128 RGBA master | 64×64 Java-compatible derivative; preserve classic/slim layout |
| Outfit overlay | 128×128 RGBA master | 64×64 compatibility derivative where its integration requires it |
| Server icon | 128×128 identity master | 64×64 opaque RGB server-list export |
| Bilingual wide sign | Two 128×128 tiles | 256×128 assembled composite and editable SVG |
| Shared model atlas | 2048×2048 RGBA | A 16×16 grid of 128×128 material cells; at most 256 slots |
| Contact sheet or art-direction board | Composition-specific | Clearly marked as preview, not counted as another asset |

The shared atlas is a container of native 128-pixel cells. Its 2048-pixel size is intentional and does not change the base design resolution. Keep Java and Bedrock UV references consistent with the atlas dimensions and material slot mapping. Do not shrink the whole atlas to 128 pixels.

Compatibility exports, preview images, two platform exports and tiled sign pieces are **derivatives of one design**. Do not count them as additional unique models, brands, skins or signs.

## 3. Native detail and pixel treatment

Author silhouettes, material features and meaningful details directly on the 128 grid. A 32×32 sprite enlarged four times is not a 128 master. A 64×64 inventory render enlarged twice is not a native 128 render. Regenerate the source, render at the required resolution, and verify the output dimensions.

Use a clear hierarchy of detail:

1. The silhouette establishes the object at inventory scale.
2. Broad surfaces, windows, cloth panels and major colour areas establish its identity.
3. Small features explain the material or function: seams, door handles, panel joints, headlights, embroidery, buttons, book spines and restrained wear.

Keep most decorative variation subordinate to the silhouette. Avoid random noise, indiscriminate scratches, soft photographic blur and uniformly bright edging. Dark material must retain enough separation to distinguish connected parts. Metal may use stepped reflective bands; cloth may use a restrained weave; wood may use directional grain and visible joints.

Pixel/voxel renders should retain deliberate hard edges. Vector icons and typography may use intentional antialiasing when drawn natively at the target resolution. Do not add blur or resample a small bitmap to simulate higher resolution.

Inspect fine grilles, wire patterns, wheel spokes, fabric weaves and tightly repeated stripes at 128 pixels. If a detail becomes bright speckling or unstable noise, simplify its spacing or contrast for the inventory representation. The full-size model may retain richer texture detail.

## 4. Composition and safe space

For isolated object and identity masters, reserve approximately **12 pixels of clear space** around important content. Use an optically balanced subject size rather than forcing every object into the same bounding box. Long items may use a diagonal composition; tall items should retain legible tops and bases.

Phone tiles use the existing clipped-corner frame. The frame may approach a 4-pixel outer margin; the functional glyph remains comfortably inside it. Main glyph strokes are normally 4 pixels, supporting lines 2 pixels and carefully chosen fine details 1 pixel. Small strokes must survive a reduced-size readability check.

HUD frames can be mostly transparent. A minimap frame should not contain invented terrain or a fabricated live route. A speedometer design should be identified as artwork when its values are examples. Keep nine native item slots in interface compositions; the phone remains an additional interaction rather than a fictional tenth hotbar slot.

Use the established three-quarter isometric camera and lighting convention for model contact sheets. Keep all faces correctly oriented. Centre the complete model, including rotors, mirrors, wheels, signs and suspended parts. Do not crop a vehicle or installation to make it look larger.

## 5. Typography and bilingual signs

Retain the exact approved English and Marathi/Hindi labels from the relevant manifest unless a separately recorded copy correction is required. Devanagari must be shaped using an appropriate text engine; do not draw one code point at a time. The current native exporter uses **Noto Sans Devanagari** with **Pillow libraqm/HarfBuzz** and **DejaVu Sans** for Latin text and unsupported punctuation.

At 256×128, use a simple layout: a small system label, a recognizable service or brand mark, an English destination or message, a Devanagari line, and a restrained footer. Wrap complete words and reduce font size only as needed. Preserve enough space for matras and conjuncts. Avoid clipped headlines, missing-glyph boxes and text that runs into the frame.

Each wide sign must declare its two tile origins, `[0, 0]` and `[128, 0]`, and its assembled dimensions `[256, 128]`. Reassembling those two source tiles must recover the composite exactly. Commercial signs should display their assigned fictional brand rather than an unrelated decorative emblem.

Editable SVG text may require the named fonts on the editing machine. The PNG is the fixed raster deliverable. For reproducible UI exports, install the same font files or set `GTM128_FONT_DIR` to a directory containing the four required DejaVu/Noto TTF files; validation records their hashes. Fonts are not bundled by this exporter.

## 6. Character, model and material invariants

Preserve every existing NPC ID, UUID where defined, occupation and classic/slim assignment. Preserve the Minecraft body UV layout when adding 128-pixel detail. Opaque base body surfaces and intentionally transparent outer layers must be checked separately. Keep the 64-pixel compatibility derivative aligned with its source. Appearance generation does not create or change a persistent NPC identity.

Model art retains existing IDs, axes, pivots, anchors and per-platform references unless a documented migration is approved. A higher-resolution atlas does not justify changing runtime item IDs or Java signatures. Material reuse is expected. Cosmetic finish variants share their underlying geometry.

Road damage artwork has four review states: **normal, damaged, critical and wreck**. Preserve each normal source unchanged. Damage variants must alter visible structure: buckle panels and fracture glazing for damaged; expose the chassis and remove selected panels or tyres for critical; collapse the upper structure or lay a two-wheeler on its side for wreck. Recolouring alone does not establish a damage state. Reuse the existing material registry, render every state at 128×128, and compare all four states in one contact-sheet row. Record the parent geometry and editable-source hashes in each derived manifest record. The generated `_damaged`, `_critical` and `_wreck` identifiers are proposed art IDs pending engine binding; their 195 exports are separate from the 509 primary designs. These visual exports do not implement physics, handling changes or runtime registration.

An image hash distinguishes files; it does not prove that two designs are meaningfully different. Assess model silhouettes and functional features as well as coordinate hashes. A colour change, a new label or a tiny hidden cube must not be used to inflate the unique-model count. Keep inherited design discrepancies documented rather than hiding them behind a resolution upgrade.

For repeating world textures, inspect a tiled preview. Preserve intended edge continuity or a deliberate mortar/joint pattern. For glass and outer-layer textures, inspect both light and dark backgrounds for alpha fringes. Atlas UVs must sample the intended cell without leaking neighbouring materials.

## 7. Reusable generation brief

Use this prompt scaffold for a new asset, supplying actual registry information:

```text
Project: GTM — Grand Theft Mumbai / SD Craft / Indraprastha.
Profile: INDRAPRASTHA_128_V1, native128 artwork.
Asset ID: [exact existing or approved ID].
Asset role: [material tile / inventory render / phone icon / skin / sign].
Subject: [specific form, function and distinctive features].
Style: original Indian urban voxel/pixel art; clean silhouette;
purposeful material detail; graphite, ARK gold, emerald, sandstone,
and terracotta, with necessary contextual colours.
Canvas: 128x128 RGBA, authored at native resolution.
Composition: [established camera / front-facing glyph / exact UV layout].
Safe area: protect important details with approximately 12px clear space.
Transparency: [transparent outside subject / full-bleed material].
Required invariants: [ID, UV layout, livery, labels, anchors, geometry].
Exact text: [approved words, or none].
Avoid: copied logos, random decoration, soft blur, unreadable noise,
cropped parts, unrequested labels, enlarged 32x32 or 64x64 artwork.
Deliver: source, PNG, manifest references, preview, and actual checks.
```

For a **vehicle inventory render**, specify the actual fictional manufacturer, body form and livery; match the library's camera and render directly at 128. Keep windows, wheel position, door breaks and lighting readable. For a **material**, replace the safe margin with full-bleed tiling requirements. For a **skin**, replace the camera and composition with its exact classic/slim UV map. For a **sign**, specify the 256×128 composite and two native 128 tiles, preserving both labels verbatim.

Generated concept art is useful reference. It becomes a resource-pack asset only after its dimensions, transparency, geometry/UV relationship, source identifiers and import paths pass the relevant checks.

## 8. Delivery and verification

Preserve the source generator and design profile alongside the manifest. Record relative paths, dimensions, mode, author/rights, file size, SHA-256, source ID, compatibility derivatives and actual verification status. Use isolated generation outputs such as `creative/generated_128/`.

Before calling an art batch generated and checked:

- Verify expected IDs and counts against the current catalogue.
- Open every output file; validate JSON/SVG syntax and PNG dimensions/modes.
- Check UV bounds, material references and geometry parity for relevant exports.
- Check alpha and body-surface coverage where relevant.
- Verify sign tile reconstruction and compatible 64-pixel derivatives.
- Inspect contact sheets covering every design, plus enlarged examples where details are uncertain.
- Check inventory readability at 128 pixels and at a smaller display size.
- Detect duplicate file/pixel hashes and distinguish legitimate shared materials from duplicate designs.
- Repeat deterministic generation where reproducibility is a stated property and compare hashes.
- Validate packaged archive integrity and report exact sizes.

Record visual review separately from automated generation so rerunning a script does not fabricate a new human review. Use truthful statuses such as `art_generated`, `art_validated`, `engine_binding_pending` and `client_verification_pending`. Live Java and Bedrock tests remain necessary before any release-ready claim.
