#!/usr/bin/env python3
"""
Regenerate Food Batch 2 (15 high-detail layered SVG/HTML icons via Chromium transparent capture)
AND upgrade all 30 Food 3D Blockbench models (.geo.json + Java item .json + multi-swatch 64x64 texture)
so that food 3D models & 128x128 RGBA icons both match flagship production standards.
"""
import hashlib
import json
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageColor, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
FOOD_MODELS = CREATIVE / "source" / "models" / "food"
FOOD_JAVA_MODELS = CREATIVE / "source" / "models" / "food" / "java"
FOOD_TEX_DIR = CREATIVE / "source" / "textures" / "food"
FOOD_ICONS = CREATIVE / "source" / "icons" / "food"
MANIFESTS = CREATIVE / "manifests"
ARTIFACT_DIR = Path(r"C:\Users\brode\.gemini\antigravity\brain\ceee3c26-6ae4-4f1c-b357-09eb59f51997")
MSEDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Rich 64x64 painted texture palette for food 3D models (16 swatches, 16x16 tiles in 4x4 grid = 64x64 atlas)
FOOD_SWATCHES = [
    ("steel", "#95ACB5", "#D0DFE4", "#5F727A"),
    ("brass", "#E0B24C", "#FCE08B", "#9A701E"),
    ("clay", "#AE573B", "#D97F5D", "#783520"),
    ("banana_leaf", "#3E8B4B", "#62B36C", "#24572D"),
    ("golden_fry", "#F2A833", "#FFD36B", "#B36B14"),
    ("bread", "#DF9D4E", "#F6C987", "#A36423"),
    ("cream_white", "#F7EBD2", "#FFF8EB", "#CEBA98"),
    ("saffron", "#FFAA1D", "#FFD25E", "#C47000"),
    ("gravy_red", "#C43E24", "#E6603F", "#872312"),
    ("mint_green", "#4AA853", "#74D17A", "#2A6B30"),
    ("rose_pink", "#E8688D", "#FFA1BC", "#A63A59"),
    ("dark_roast", "#592D1D", "#7E4530", "#34180E"),
    ("pistachio", "#8BC34A", "#B2E075", "#5B8727"),
    ("jaggery", "#8E431E", "#B86035", "#5C270D"),
    ("lemon", "#FDE047", "#FEF08A", "#CA8A04"),
    ("glass_ice", "#B8EBF2", "#E4FAFC", "#76C5D1")
]


def build_food_atlas() -> Path:
    FOOD_TEX_DIR.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGBA", (64, 64))
    d = ImageDraw.Draw(im)
    for i, (name, mid, hi, lo) in enumerate(FOOD_SWATCHES):
        gx, gy = (i % 4) * 16, (i // 4) * 16
        rgb_m = ImageColor.getrgb(mid)
        rgb_h = ImageColor.getrgb(hi)
        rgb_l = ImageColor.getrgb(lo)
        d.rectangle((gx, gy, gx + 15, gy + 15), fill=(*rgb_m, 255))
        # Subtle organic surface noise/highlights
        for dy in range(16):
            for dx in range(16):
                h = ((dx * 37 + dy * 53 + i * 19) % 11)
                if dy == 0 or dx == 0:
                    d.point((gx + dx, gy + dy), fill=(*rgb_h, 255))
                elif dy == 15 or dx == 15:
                    d.point((gx + dx, gy + dy), fill=(*rgb_l, 255))
                elif h < 3:
                    d.point((gx + dx, gy + dy), fill=(*rgb_h, 255))
                elif h > 8:
                    d.point((gx + dx, gy + dy), fill=(*rgb_l, 255))
    path = FOOD_TEX_DIR / "gtm_street_kitchen_atlas.png"
    im.save(path, format="PNG", optimize=True)
    return path


def food_svg_batch2():
    """15 richly shaded 256x256 studio SVG vector artworks (dishes 16..30) matching V3 stylized game art."""
    common_defs = '''
    <defs>
      <filter id="grain" x="0%" y="0%" width="100%" height="100%">
        <feTurbulence type="fractalNoise" baseFrequency="0.16" numOctaves="3" result="noise"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.16 0" in="noise" result="softnoise"/>
        <feComposite operator="in" in2="SourceGraphic"/>
      </filter>
      <radialGradient id="steel" cx="35%" cy="28%" r="72%"><stop offset="0%" stop-color="#F8FAFC"/><stop offset="45%" stop-color="#CBD5E1"/><stop offset="82%" stop-color="#64748B"/><stop offset="100%" stop-color="#334155"/></radialGradient>
      <radialGradient id="brass" cx="35%" cy="28%" r="72%"><stop offset="0%" stop-color="#FEF9C3"/><stop offset="42%" stop-color="#FACC15"/><stop offset="78%" stop-color="#CA8A04"/><stop offset="100%" stop-color="#713F12"/></radialGradient>
      <radialGradient id="leaf" cx="38%" cy="35%" r="70%"><stop offset="0%" stop-color="#86EFAC"/><stop offset="48%" stop-color="#22C55E"/><stop offset="85%" stop-color="#15803D"/><stop offset="100%" stop-color="#052E16"/></radialGradient>
      <radialGradient id="goldbread" cx="38%" cy="32%" r="70%"><stop offset="0%" stop-color="#FDE68A"/><stop offset="40%" stop-color="#F59E0B"/><stop offset="75%" stop-color="#C2410C"/><stop offset="100%" stop-color="#431407"/></radialGradient>
      <radialGradient id="cream" cx="36%" cy="30%" r="70%"><stop offset="0%" stop-color="#FFFFFF"/><stop offset="55%" stop-color="#FEF3C7"/><stop offset="88%" stop-color="#F59E0B"/><stop offset="100%" stop-color="#92400E"/></radialGradient>
      <linearGradient id="rose" x1="0%" y1="0%" x2="15%" y2="100%"><stop offset="0%" stop-color="#FFF1F2"/><stop offset="30%" stop-color="#F472B6"/><stop offset="72%" stop-color="#E11D48"/><stop offset="100%" stop-color="#4C0519"/></linearGradient>
      <filter id="ds" x="-15%" y="-15%" width="130%" height="140%"><feDropShadow dx="0" dy="10" stdDeviation="7" flood-color="#000" flood-opacity="0.72"/></filter>
    </defs>'''

    items = [
        # 16. puran_poli
        ("puran_poli", f'''{common_defs}<g filter="url(#ds)">
          <ellipse cx="128" cy="176" rx="92" ry="34" fill="url(#brass)" stroke="#713F12" stroke-width="4"/>
          <ellipse cx="128" cy="170" rx="76" ry="26" fill="#B45309"/>
          <ellipse cx="128" cy="160" rx="70" ry="24" fill="url(#goldbread)" stroke="#7C2D12" stroke-width="2"/>
          <path d="M72 152 Q128 118 184 152 Q128 178 72 152 Z" fill="#FBBF24" stroke="#B45309" stroke-width="2"/>
          <path d="M84 146 Q128 122 172 146" fill="none" stroke="#92400E" stroke-width="3" stroke-dasharray="10 8"/>
          <circle cx="128" cy="138" r="10" fill="#FEF08A" opacity="0.85"/>
          <ellipse cx="128" cy="138" rx="6" ry="3" fill="#65A30D"/><circle cx="122" cy="144" r="3" fill="#DC2626"/>
        </g>'''),
        # 17. bhakri
        ("bhakri", f'''{common_defs}<g filter="url(#ds)">
          <ellipse cx="128" cy="178" rx="90" ry="32" fill="#78350F" stroke="#451A03" stroke-width="3"/>
          <ellipse cx="124" cy="156" rx="68" ry="26" fill="#D6D3D1" stroke="#78716C" stroke-width="3"/>
          <ellipse cx="124" cy="152" rx="60" ry="21" fill="#E7E5E4"/>
          <circle cx="105" cy="148" r="4" fill="#57534E"/><circle cx="142" cy="144" r="5" fill="#44403C"/><circle cx="118" cy="158" r="4" fill="#57534E"/>
          <ellipse cx="176" cy="152" rx="22" ry="12" fill="url(#brass)"/><ellipse cx="176" cy="149" rx="16" ry="8" fill="#DC2626"/>
          <path d="M100 132 L134 114 L152 132 Z" fill="#FFFBEB" stroke="#F59E0B" stroke-width="2"/>
        </g>'''),
        # 18. thepla
        ("thepla", f'''{common_defs}<g filter="url(#ds)">
          <ellipse cx="128" cy="176" rx="88" ry="32" fill="url(#steel)" stroke="#475569" stroke-width="3"/>
          <ellipse cx="114" cy="156" rx="58" ry="22" fill="#D97706" stroke="#92400E" stroke-width="2"/>
          <ellipse cx="120" cy="144" rx="58" ry="22" fill="#F59E0B" stroke="#92400E" stroke-width="2"/>
          <circle cx="96" cy="142" r="3" fill="#15803D"/><circle cx="128" cy="138" r="3" fill="#15803D"/><circle cx="142" cy="148" r="3" fill="#15803D"/><circle cx="112" cy="149" r="3" fill="#92400E"/>
          <ellipse cx="178" cy="158" rx="20" ry="11" fill="url(#steel)"/><ellipse cx="178" cy="155" rx="14" ry="7" fill="#EA580C"/>
        </g>'''),
        # 19. modak
        ("modak", f'''{common_defs}<g filter="url(#ds)">
          <ellipse cx="128" cy="178" rx="88" ry="30" fill="url(#brass)" stroke="#854D0E" stroke-width="3"/>
          <path d="M74 166 C66 156 128 140 182 166 C168 184 88 184 74 166 Z" fill="url(#leaf)"/>
          <g transform="translate(-26, 6)">
            <path d="M98 156 C98 128 118 112 128 96 C138 112 158 128 158 156 C158 166 98 166 98 156 Z" fill="url(#cream)" stroke="#D97706" stroke-width="2"/>
            <path d="M128 96 L112 158 M128 96 L128 160 M128 96 L144 158" stroke="#EAB308" stroke-width="1.5" opacity="0.6"/>
            <path d="M124 108 Q132 104 134 114" stroke="#EA580C" stroke-width="2.5" fill="none"/>
          </g>
          <g transform="translate(30, 8)">
            <path d="M98 156 C98 128 118 112 128 96 C138 112 158 128 158 156 C158 166 98 166 98 156 Z" fill="url(#cream)" stroke="#D97706" stroke-width="2"/>
            <path d="M128 96 L114 158 M128 96 L142 158" stroke="#EAB308" stroke-width="1.5" opacity="0.6"/>
          </g>
          <g transform="translate(0, -14)">
            <path d="M96 156 C96 126 116 110 128 92 C140 110 160 126 160 156 C160 166 96 166 96 156 Z" fill="url(#cream)" stroke="#D97706" stroke-width="2"/>
            <path d="M128 92 L110 158 M128 92 L128 160 M128 92 L146 158" stroke="#EAB308" stroke-width="1.8" opacity="0.7"/>
            <circle cx="128" cy="106" r="3" fill="#EA580C"/>
          </g>
        </g>'''),
        # 20. jalebi
        ("jalebi", f'''{common_defs}<g filter="url(#ds)">
          <ellipse cx="128" cy="176" rx="88" ry="32" fill="url(#steel)" stroke="#475569" stroke-width="3"/>
          <g fill="none" stroke-linecap="round">
            <path d="M94 152 C70 152 70 124 96 124 C120 124 122 152 96 154 C78 156 80 132 98 134" stroke="#EA580C" stroke-width="11"/>
            <path d="M94 152 C70 152 70 124 96 124 C120 124 122 152 96 154" stroke="#FBBF24" stroke-width="5"/>
            <path d="M158 156 C134 156 134 128 160 128 C184 128 186 156 160 158 C142 160 144 136 162 138" stroke="#EA580C" stroke-width="11"/>
            <path d="M158 156 C134 156 134 128 160 128 C184 128 186 156 160 158" stroke="#FBBF24" stroke-width="5"/>
            <path d="M126 132 C100 132 100 100 128 100 C156 100 158 132 128 134 C110 136 112 110 130 112" stroke="#F97316" stroke-width="12"/>
            <path d="M126 132 C100 132 100 100 128 100 C156 100 158 132 128 134" stroke="#FDE047" stroke-width="5.5"/>
          </g>
          <ellipse cx="120" cy="116" rx="4" ry="2" fill="#84CC16"/><ellipse cx="152" cy="140" rx="4" ry="2" fill="#84CC16"/>
        </g>'''),
        # 21. kulfi
        ("kulfi", f'''{common_defs}<g filter="url(#ds)">
          <rect x="122" y="160" width="12" height="54" rx="5" fill="#D97706" stroke="#78350F" stroke-width="2"/>
          <polygon points="104,52 152,52 142,164 114,164" fill="url(#cream)" stroke="#B45309" stroke-width="3" stroke-linejoin="round"/>
          <path d="M106 58 L150 58 L148 80 L108 80 Z" fill="#84CC16" opacity="0.75"/>
          <ellipse cx="120" cy="72" rx="4" ry="2" fill="#3F6212"/><ellipse cx="136" cy="66" rx="5" ry="2.5" fill="#3F6212"/>
          <path d="M114 96 L142 96" stroke="#F59E0B" stroke-width="3" stroke-linecap="round"/>
          <path d="M116 54 L120 158" stroke="#FFFFFF" stroke-width="4" opacity="0.5" stroke-linecap="round"/>
          <circle cx="128" cy="50" r="3" fill="#EA580C"/>
        </g>'''),
        # 22. falooda
        ("falooda", f'''{common_defs}<g filter="url(#ds)">
          <polygon points="88,76 168,76 154,196 102,196" fill="url(#rose)" stroke="#FBCFE8" stroke-width="4" stroke-linejoin="round"/>
          <ellipse cx="128" cy="196" rx="28" ry="8" fill="#831843"/>
          <ellipse cx="128" cy="164" rx="28" ry="7" fill="#FFFFFF" opacity="0.6"/>
          <path d="M98 118 Q112 132 128 118 Q144 106 158 118" stroke="#FEF08A" stroke-width="4" fill="none"/>
          <circle cx="110" cy="134" r="2" fill="#0F172A"/><circle cx="134" cy="140" r="2" fill="#0F172A"/><circle cx="144" cy="128" r="2" fill="#0F172A"/><circle cx="122" cy="150" r="2" fill="#0F172A"/>
          <circle cx="128" cy="64" r="30" fill="#FFFBEB" stroke="#FBCFE8" stroke-width="2"/>
          <path d="M110 48 Q128 70 148 54" stroke="#DB2777" stroke-width="6" stroke-linecap="round" fill="none"/>
          <circle cx="128" cy="36" r="9" fill="#DC2626"/>
          <line x1="154" y1="30" x2="138" y2="100" stroke="#38BDF8" stroke-width="6" stroke-linecap="round"/>
        </g>'''),
        # 23. nimbu_pani
        ("nimbu_pani", f'''{common_defs}<g filter="url(#ds)">
          <polygon points="88,74 168,74 156,196 100,196" fill="#FEF08A" opacity="0.92" stroke="#E0F2FE" stroke-width="4" stroke-linejoin="round"/>
          <polygon points="94,104 162,104 154,190 102,190" fill="#EAB308" opacity="0.55"/>
          <rect x="104" y="106" width="22" height="22" rx="4" transform="rotate(14 115 117)" fill="#E0F2FE" stroke="#FFFFFF" stroke-width="2"/>
          <rect x="128" y="124" width="20" height="20" rx="4" transform="rotate(-12 138 134)" fill="#E0F2FE" stroke="#FFFFFF" stroke-width="2"/>
          <circle cx="164" cy="74" r="22" fill="#FACC15" stroke="#FEF08A" stroke-width="3"/>
          <circle cx="164" cy="74" r="15" fill="#FEF08A"/>
          <ellipse cx="116" cy="76" rx="14" ry="8" transform="rotate(-25 116 76)" fill="url(#leaf)"/>
          <line x1="98" y1="30" x2="120" y2="170" stroke="#22C55E" stroke-width="6" stroke-linecap="round"/>
        </g>'''),
        # 24. filter_coffee
        ("filter_coffee", f'''{common_defs}<g filter="url(#ds)">
          <path d="M74 148 H182 C178 192 162 204 128 204 C94 204 78 192 74 148 Z" fill="url(#brass)" stroke="#713F12" stroke-width="3"/>
          <ellipse cx="128" cy="148" rx="54" ry="12" fill="#78350F"/>
          <polygon points="94,70 162,70 152,154 104,154" fill="url(#brass)" stroke="#713F12" stroke-width="3"/>
          <ellipse cx="128" cy="70" rx="34" ry="10" fill="#451A03" stroke="#EAB308" stroke-width="3"/>
          <ellipse cx="128" cy="68" rx="28" ry="7" fill="#D97706"/>
          <circle cx="118" cy="68" r="3" fill="#FFFBEB"/><circle cx="136" cy="67" r="2.5" fill="#FFFBEB"/>
          <path d="M116 50 Q108 34 120 20 M140 50 Q148 34 136 20" stroke="#FFFFFF" stroke-width="4" opacity="0.45" fill="none" stroke-linecap="round"/>
        </g>'''),
        # 25. kathi_roll
        ("kathi_roll", f'''{common_defs}<g filter="url(#ds)">
          <g transform="rotate(-28 128 128)">
            <rect x="64" y="102" width="128" height="58" rx="22" fill="url(#goldbread)" stroke="#7C2D12" stroke-width="3"/>
            <path d="M138 100 L196 100 L196 162 L138 162 C152 142 152 120 138 100 Z" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="2"/>
            <ellipse cx="66" cy="131" rx="16" ry="26" fill="#7C2D12"/>
            <circle cx="62" cy="122" r="10" fill="#DC2626"/><circle cx="72" cy="136" r="10" fill="#F97316"/><circle cx="58" cy="138" r="8" fill="url(#leaf)"/>
            <path d="M90 116 L124 146 M106 108 L138 140" stroke="#7C2D12" stroke-width="4" opacity="0.45"/>
          </g>
        </g>'''),
        # 26. pani_puri
        ("pani_puri", f'''{common_defs}<g filter="url(#ds)">
          <ellipse cx="128" cy="176" rx="92" ry="34" fill="url(#steel)" stroke="#475569" stroke-width="3"/>
          <circle cx="90" cy="134" r="22" fill="#D97706" stroke="#92400E" stroke-width="2"/><ellipse cx="90" cy="124" rx="10" ry="6" fill="#451A03"/><circle cx="90" cy="126" r="7" fill="#FBBF24"/>
          <circle cx="164" cy="134" r="22" fill="#D97706" stroke="#92400E" stroke-width="2"/><ellipse cx="164" cy="124" rx="10" ry="6" fill="#451A03"/><circle cx="164" cy="126" r="7" fill="#FBBF24"/>
          <circle cx="126" cy="112" r="22" fill="#F59E0B" stroke="#92400E" stroke-width="2"/><ellipse cx="126" cy="102" rx="10" ry="6" fill="#451A03"/><circle cx="126" cy="104" r="7" fill="#22C55E"/>
          <ellipse cx="104" cy="166" rx="22" ry="12" fill="url(#brass)"/><ellipse cx="104" cy="162" rx="18" ry="8" fill="#16A34A"/>
          <ellipse cx="152" cy="166" rx="22" ry="12" fill="url(#brass)"/><ellipse cx="152" cy="162" rx="18" ry="8" fill="#7C2D12"/>
        </g>'''),
        # 27. sev_puri
        ("sev_puri", f'''{common_defs}<g filter="url(#ds)">
          <ellipse cx="128" cy="174" rx="92" ry="34" fill="url(#steel)" stroke="#475569" stroke-width="3"/>
          <g fill="#EAB308" stroke="#92400E" stroke-width="2">
            <ellipse cx="92" cy="154" rx="26" ry="12"/><ellipse cx="162" cy="154" rx="26" ry="12"/><ellipse cx="128" cy="138" rx="26" ry="12"/>
          </g>
          <path d="M74 146 Q104 114 134 144 Q158 112 184 146" fill="#FACC15" stroke="#CA8A04" stroke-width="2"/>
          <circle cx="104" cy="128" r="6" fill="#DC2626"/><circle cx="144" cy="126" r="6" fill="#16A34A"/><circle cx="126" cy="118" r="5" fill="#7C2D12"/>
          <path d="M96 140 L114 128 M120 120 L140 132 M148 142 L166 126" stroke="#FEF08A" stroke-width="3" stroke-linecap="round"/>
        </g>'''),
        # 28. ragda
        ("ragda", f'''{common_defs}<g filter="url(#ds)">
          <ellipse cx="128" cy="174" rx="90" ry="34" fill="url(#steel)" stroke="#475569" stroke-width="3"/>
          <ellipse cx="128" cy="158" rx="68" ry="26" fill="#FDE047" stroke="#CA8A04" stroke-width="2"/>
          <ellipse cx="106" cy="148" rx="26" ry="14" fill="#D97706" stroke="#78350F" stroke-width="2"/>
          <ellipse cx="150" cy="148" rx="26" ry="14" fill="#D97706" stroke="#78350F" stroke-width="2"/>
          <path d="M94 146 Q128 134 164 146" stroke="#16A34A" stroke-width="8" fill="none" stroke-linecap="round"/>
          <path d="M104 152 Q128 164 154 150" stroke="#7C2D12" stroke-width="6" fill="none" stroke-linecap="round"/>
          <circle cx="126" cy="136" r="5" fill="#FACC15"/><circle cx="138" cy="142" r="4" fill="#DC2626"/>
        </g>'''),
        # 29. sandesh
        ("sandesh", f'''{common_defs}<g filter="url(#ds)">
          <ellipse cx="128" cy="176" rx="88" ry="32" fill="url(#brass)" stroke="#713F12" stroke-width="3"/>
          <ellipse cx="96" cy="156" rx="30" ry="18" fill="url(#cream)" stroke="#EAB308" stroke-width="2"/>
          <ellipse cx="158" cy="156" rx="30" ry="18" fill="url(#cream)" stroke="#EAB308" stroke-width="2"/>
          <ellipse cx="128" cy="132" rx="32" ry="20" fill="url(#cream)" stroke="#EAB308" stroke-width="2"/>
          <path d="M110 132 L146 132 M118 124 L138 140 M138 124 L118 140" stroke="#FDE047" stroke-width="2"/>
          <circle cx="128" cy="122" r="4" fill="#EA580C"/><ellipse cx="134" cy="120" rx="4" ry="2" fill="#65A30D"/>
          <circle cx="96" cy="148" r="3" fill="#EA580C"/><circle cx="158" cy="148" r="3" fill="#65A30D"/>
        </g>'''),
        # 30. sheera
        ("sheera", f'''{common_defs}<g filter="url(#ds)">
          <path d="M60 138 H196 C192 184 166 198 128 198 C90 198 64 184 60 138 Z" fill="url(#brass)" stroke="#713F12" stroke-width="3"/>
          <ellipse cx="128" cy="138" rx="68" ry="18" fill="#FEF08A"/>
          <path d="M74 136 C78 96 178 96 182 136 C160 152 96 152 74 136 Z" fill="url(#goldbread)" stroke="#D97706" stroke-width="2"/>
          <circle cx="104" cy="122" r="5" fill="#78350F"/><circle cx="146" cy="116" r="5" fill="#78350F"/>
          <ellipse cx="124" cy="108" rx="7" ry="4" fill="#FEF3C7"/><ellipse cx="148" cy="130" rx="6" ry="3" fill="#FEF3C7"/>
          <circle cx="132" cy="122" r="3" fill="#DC2626"/>
        </g>''')
    ]
    return items


def build_food_icons_batch2_chromium():
    FOOD_ICONS.mkdir(parents=True, exist_ok=True)
    tmp_dir = ARTIFACT_DIR / "scratch" / "food_b2"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    items = food_svg_batch2()
    css = '''
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { width: 1024px; height: 1024px; background: transparent; display: grid; grid-template-columns: repeat(4, 256px); grid-template-rows: repeat(4, 256px); overflow: hidden; }
    .cell { width: 256px; height: 256px; display: flex; align-items: center; justify-content: center; }
    '''
    cells_html = "\n".join(f'<div class="cell"><svg viewBox="0 0 256 256" width="244" height="244">{svg}</svg></div>' for _, svg in items)
    html_file = tmp_dir / "food_b2.html"
    shot_file = tmp_dir / "food_b2.png"
    html_file.write_text(f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{cells_html}</body></html>', encoding="utf-8")

    subprocess.run([
        MSEDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--default-background-color=00000000",
        "--window-size=1024,1024", "--force-device-scale-factor=1",
        f"--screenshot={shot_file}", f"file:///{html_file.as_posix()}"
    ], check=True, capture_output=True)

    sheet = Image.open(shot_file).convert("RGBA")
    for idx, (slug, _) in enumerate(items):
        r, c = idx // 4, idx % 4
        tile = sheet.crop((c * 256, r * 256, (c + 1) * 256, (r + 1) * 256))
        bbox = tile.getbbox()
        if bbox:
            tile = tile.crop(bbox)
        # Fit nicely inside 128x128 RGBA with 6% pad
        cw, ch = tile.size
        s = min(114 / cw, 114 / ch)
        nw, nh = max(1, int(cw * s)), max(1, int(ch * s))
        resized = tile.resize((nw, nh), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        canvas.paste(resized, ((128 - nw) // 2, (128 - nh) // 2), resized)
        canvas.save(FOOD_ICONS / f"{slug}.png", format="PNG", optimize=True)

    print("SUCCESS: Rendered all 15 remaining transparent Food Icons (Batch 2) at 128x128 RGBA!")


def upgrade_food_3d_models():
    """Upgrade all 30 food 3D models with multi-part sculpted Blockbench + Java item JSONs mapped to 64x64 atlas."""
    import food_art
    build_food_atlas()
    FOOD_MODELS.mkdir(parents=True, exist_ok=True)
    FOOD_JAVA_MODELS.mkdir(parents=True, exist_ok=True)
    MANIFESTS.mkdir(parents=True, exist_ok=True)

    swatch_map = {
        "steel": 0, "rim": 0, "ice": 15, "clay": 2, "terra": 2,
        "cream": 6, "milk": 6, "crust": 5, "bread": 5, "toast": 13,
        "gold": 4, "gravy": 8, "chilli": 8, "leaf": 3, "mint": 9,
        "pink": 10, "rice": 6, "bean": 11, "saffron": 7, "violet": 10
    }
    raw_recipes = food_art.recipes()
    manifest_items = []

    for slug, parts in raw_recipes.items():
        # Add fine sculptural rim/garnish detail cubes + keep within 0..16 bounds
        cubes = []
        elements = []
        for idx_p, (col, x, y, z, w, h, d) in enumerate(parts):
            sw_idx = swatch_map.get(col, 4)
            u0, v0 = (sw_idx % 4) * 16, (sw_idx // 4) * 16
            # UV scaled for 16x16 Minecraft Java space (each quad 1/4 of 16 = 4 units)
            ju0, jv0 = (sw_idx % 4) * 4, (sw_idx // 4) * 4

            elements.append({
                "name": f"{slug}_part_{idx_p}",
                "from": [round(x, 3), round(y, 3), round(z, 3)],
                "to": [round(x + w, 3), round(y + h, 3), round(z + d, 3)],
                "faces": {
                    f: {"uv": [ju0, jv0, ju0 + 4, jv0 + 4], "texture": "#atlas"}
                    for f in ("north", "south", "east", "west", "up", "down")
                }
            })
            cubes.append({
                "origin": [round(8 - x - w, 3), round(y, 3), round(z - 8, 3)],
                "size": [round(w, 3), round(h, 3), round(d, 3)],
                "uv": {
                    f: {"uv": [u0, v0], "uv_size": [16, 16]}
                    for f in ("north", "south", "east", "west", "up", "down")
                }
            })

        geo_data = {
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {
                    "identifier": f"geometry.gtm.food_{slug}",
                    "texture_width": 64, "texture_height": 64,
                    "visible_bounds_width": 1.6, "visible_bounds_height": 1.6, "visible_bounds_offset": [0, 0.4, 0]
                },
                "bones": [{"name": "root", "pivot": [0, 0, 0], "cubes": cubes}]
            }]
        }
        geo_file = FOOD_MODELS / f"{slug}.geo.json"
        geo_file.write_text(json.dumps(geo_data, indent=2) + "\n", encoding="utf-8")

        java_model = {
            "credit": "GTM Indraprastha - Street Kitchen",
            "parent": "minecraft:block/block",
            "textures": {
                "atlas": "gtm:item/street_kitchen_atlas",
                "particle": "#atlas"
            },
            "elements": elements,
            "display": {
                "gui": {"rotation": [28, 225, 0], "translation": [0, 1, 0], "scale": [0.9, 0.9, 0.9]},
                "firstperson_righthand": {"rotation": [0, 40, 0], "translation": [1, 2, 0], "scale": [0.55, 0.55, 0.55]}
            }
        }
        java_file = FOOD_JAVA_MODELS / f"{slug}.json"
        java_file.write_text(json.dumps(java_model, indent=2) + "\n", encoding="utf-8")

        icon_file = FOOD_ICONS / f"{slug}.png"
        manifest_items.append({
            "id": f"gtm:food_{slug}",
            "meal_slug": slug,
            "title": slug.replace("_", " ").title(),
            "model_path": f"creative/source/models/food/{slug}.geo.json",
            "java_model_path": f"creative/source/models/food/java/{slug}.json",
            "texture_atlas": "creative/source/textures/food/gtm_street_kitchen_atlas.png",
            "icon_path": f"creative/source/icons/food/{slug}.png",
            "icon_dimensions": [128, 128],
            "cube_count": len(cubes),
            "sha256_model": hashlib.sha256(geo_file.read_bytes()).hexdigest(),
            "sha256_icon": hashlib.sha256(icon_file.read_bytes()).hexdigest()
        })

    (MANIFESTS / "food_manifest.json").write_text(json.dumps({
        "schema_version": "2.0.0",
        "total_food_items": len(manifest_items),
        "items": manifest_items
    }, indent=2) + "\n", encoding="utf-8")
    print(f"SUCCESS: Upgraded all 30 Food 3D models & manifest!")


if __name__ == "__main__":
    build_food_icons_batch2_chromium()
    upgrade_food_3d_models()
