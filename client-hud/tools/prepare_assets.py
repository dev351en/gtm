#!/usr/bin/env python3
"""Copy existing approved art, unchanged, into the optional client component.

Brand logos are the tracked colourful 256px originals, not the later gold badge
substitutes. HUD and unbranded services retain native128 masters from the checked
functional runtime pack. This performs no image generation or resampling.
"""
from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import struct
import shutil
import sys
import tempfile
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / 'build/generated/assets'
sys.path.insert(0, str(ROOT / 'tools'))
from assemble_functional_runtime import copy_verified

def preserved_pack() -> bytes:
    relative = 'resourcepacks/GTM_Local_Java.zip'
    manifest = json.loads((ROOT / 'runtime/functional-r4/manifest.json').read_text())
    record = next(entry for entry in manifest['files'] if entry['path'] == relative)
    with tempfile.TemporaryDirectory(prefix='gtm-hud-art-') as folder:
        target = Path(folder) / 'source.zip'
        copy_verified(ROOT.resolve(), record, target, 'runtime/functional-r4/' + relative)
        return target.read_bytes()

def dimensions(data: bytes) -> tuple[int, int]:
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Expected an unchanged PNG asset')
    return struct.unpack('>II', data[16:24])

def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    assets = OUT / 'assets/gtmhud/textures'
    report = []
    with ZipFile(io.BytesIO(preserved_pack())) as pack:
        for manifest, group, prefix in [('hud_128.json', 'hud', 'hud/'), ('phone_128.json', 'apps', '')]:
            document = json.loads((ROOT / 'creative/generated_128/manifests' / manifest).read_text())
            for entry in document['assets']:
                source = 'assets/gtm/textures/ui/' + prefix + entry['id'] + '.png'
                content = pack.read(source)
                if hashlib.sha256(content).hexdigest() != entry['sha256'] or dimensions(content) != (128, 128):
                    raise ValueError('Native128 provenance mismatch: ' + source)
                destination = assets / group / (entry['id'] + '.png')
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(content)
                report.append(dict(id=entry['id'], group=group, source=source, pixels=[128,128], sha256=entry['sha256'], changed=False))
    for source in sorted((ROOT / 'creative/source/branding').glob('*.png')):
        content = source.read_bytes()
        if dimensions(content) != (256, 256):
            raise ValueError('Unexpected approved brand dimensions: ' + str(source))
        destination = assets / 'brands' / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        report.append(dict(id=source.stem, group='brands', source=source.relative_to(ROOT).as_posix(), pixels=[256,256], sha256=hashlib.sha256(content).hexdigest(), changed=False))
    (OUT / 'gtm-hud-art-provenance.json').write_text(json.dumps(dict(schema='GTM_HUD_ART_V1', assets=report), indent=2) + '\n')
    print(f'Copied {len(report)} existing assets without modification; original colourful256 brand logos and native128 HUD/service glyphs.')

if __name__ == '__main__':
    main()
