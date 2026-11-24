# EXPECT SDCRAFT — Creative Track Changelog (Revision 4 — V3 Faithful 32x Pixel & Model Overhaul)

## Executive Summary
This document records all creative deliverables produced by **Antigravity** for **GTM Revision 4** on branch `gtm/creative-r4` (`Indraprastha` metropolis, Faithful-32x-inspired pixel & voxel aesthetic, core palette: Graphite `#151B20`, ARK Gold `#D6AD59`, Emerald `#236653`, Sandstone `#D2B997`, Terracotta `#AD5637`).

Every texture, icon, and 3D model was regenerated taking inspiration from **Faithful 32x** Minecraft pixel art (`tools/faithful_32x_palette.py` quantized hue-shifted ramps, 1px directional bevels, pixel-clustered wood/cobble/brick/metal/crystal textures, `512x512` per-face UV atlas, razor-sharp `NEAREST` upscaled pixel sprites, and pixel-locked isometric Z-buffer renders), visually audited across 14 contact sheets, and verified by `tools/validate_creative_r4.py` with **0 errors**. No production servers, gameplay engines, or player ledgers were modified.

---

## Verified Deliverables Summary (V3 Faithful 32x Audit)

| Domain | Deliverable | Quantity / Spec | Faithful 32x Upgrade Applied | Manifest / Pack Path |
| :--- | :--- | :--- | :--- | :--- |
| **Domain 1** | **Server Icon** | 1 icon (`64x64` opaque RGB) | Hand-pixelled `64x64` Faithful pixel-art GTM Sea-Link golden shield crest | `creative/source/icons/server-icon.png` |
| **Domain 1** | **Fictional Brands** | 32 brands (`256x256` RGBA + SVGs) | Bespoke `64x64` Faithful pixel-art emblems upscaled `4x NEAREST` with 1px dark outlines | `creative/manifests/brands.json` |
| **Domain 1** | **Phone App Icons** | 24 icons (`128x128` RGBA) | Native `32x32` beveled rounded-tile pixel sprites upscaled `4x NEAREST` | `creative/manifests/phone_icons.json` |
| **Domain 1** | **HUD Screen Assets** | 33 assets (`64x64` / `128x64` RGBA) | Faithful pixel-art Minecraft HUD icons, speedometers, minimaps & crisp banners | `creative/manifests/hud_manifest.json` |
| **Domain 1** | **Web Dashboard Tokens** | 14 responsive panels | Graphite/Gold dark theme tokens | `creative/source/ui/dashboard_tokens.json` |
| **Domain 2** | **Transport 3D + Icons** | 87 models + 87 icons (`128x128`) | Per-face UVs (headlights, grilles, windshields w/ wipers, alloy hubs, SDPD/taxi/ambulance/train liveries) + pixel-locked Faithful isometric sprites | `creative/manifests/transport_art_manifest.json` |
| **Domain 2** | **Vehicle Migration Map** | 65 legacy-to-approved mappings | Preserves active `gtm:` IDs for engine binding | `creative/manifests/transport_catalog_mapping.json` |
| **Domain 3** | **Furniture 3D + Icons** | 200 models + 200 icons (`128x128`) | Real-world archetypes w/ bookcase spines, ECG/ATM/PC displays, stoves, drawers & mandir jali + pixel-locked icons | `creative/manifests/furniture_art_manifest.json` |
| **Domain 3** | **Furniture Migration Map**| 200 legacy-to-functional mappings | Preserves legacy furniture IDs cleanly | `creative/manifests/furniture_catalog_mapping.json` |
| **Domain 3** | **Municipal Facilities** | 46 facility surveys with bounds | Full local entrance, room & safety bounds | `creative/manifests/facilities_manifest.json` |
| **Domain 4** | **NPC Character Skins** | 500 unique `64x64` RGBA skins | Dual-layer pixel-art shading; Boss `npc-481` + orange detention Prisoners `npc-482..486` | `creative/manifests/npc_skins_manifest.json` |
| **Domain 4** | **Outfits & Overlays** | 100 unique `64x64` overlays | 7 categories rendered in assembled Front+Back previews | `creative/manifests/outfits_manifest.json` |
| **Domain 5** | **Equipment & Hero Props** | 92 props + 11 User Hero 3D models | Hero JSONs mapped to Faithful `32x32` textures + bespoke `32x32` pixel inventory sprites | `creative/manifests/equipment_manifest.json` |
| **Domain 5** | **Weapons & Finishes** | 30 weapons × 10 finishes (`300` PNGs) | Unique sculpted silhouettes (revolver, derringer, coach gun, bullpup, talwar, khanda, lathi) + `48x48` pixel sprites + `64x64` pixel finishes | `creative/manifests/finishes_migration.json` |
| **Domain 5** | **Food 3D + Icons** | 30 meals (`128x128` icons + Bedrock/Java 3D) | Hand-crafted `32x32` Faithful pixel food sprites + `64x64` stepped food atlas + 3D models | `creative/manifests/food_manifest.json` |
| **Domain 6** | **Festivals 3D + Icons** | 100 installations across 8 themes | Dual Bedrock/Java exports textured w/ toran, rangoli & glowstone lamp tiles + pixel icons | `creative/manifests/festivals_manifest.json` |
| **Domain 6** | **Bilingual Signage** | 120 signs (`512x256` RGBA) | Rendered via DirectWrite Chromium (`msedge`) for crisp Marathi/Devanagari conjunct shaping | `creative/manifests/signage_manifest.json` |
| **Domain 7** | **32×32 Model & World Packs** | 148 model `32x32` textures + 98 world `32x32` block textures | Packaged into `GTM_Indraprastha_World_32x_Java.zip` & `GTM_Indraprastha_World_32x_Bedrock.mcpack` + installed locally | `creative/packs/GTM_Indraprastha_World_32x_Java.zip` |
| **QA / Reports** | **Validation & Previews** | 14 Contact Sheets + Automated QA Gate | Verified Faithful pixel-locked rendering, atlas UVs, counts, hashes & ZIP integrity | `creative/reports/ASSET_VALIDATION_REPORT.json` |
