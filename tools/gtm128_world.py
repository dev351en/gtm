"""Native128 world texture layer using the exact existing block catalogue."""
import argparse
import ast
import json
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
import gtm128_core as core
from gtm128_materials import tile,rgb,tone

ROOT=Path(__file__).resolve().parents[1]

def specs():
    tree=ast.parse((ROOT/'tools/build_world_32x_pack.py').read_text())
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='specs' for t in node.targets):return ast.literal_eval(node.value)
    raise ValueError('Missing source block catalogue')

def block(name,kind,c1,c2,c3,seed):
    aliases={'asphalt':'stone','tiles':'bricks','planks':'wood','log_side':'bark','wool':'fabric','bookshelf':'detail_bookshelf',
             'grass_top':'grass','lamp_on':'glowstone','lamp_off':'metal','gem':'chrome','obsidian':'cobble'}
    im=Image.fromarray(tile(name,c1,aliases.get(kind,kind),seed),'RGBA');d=ImageDraw.Draw(im)
    if kind=='grass_side':
        base=Image.fromarray(tile(name+'_soil',c2,'dirt',seed),'RGBA');base.paste(im.crop((0,0,128,22)),(0,0));im=base;d=ImageDraw.Draw(im)
        for x in range(0,128,8):d.rectangle((x,18,x+7,22+(x//8%3)*4),fill=c1)
    elif kind in ('rails','bars'):
        im=Image.new('RGBA',(128,128));d=ImageDraw.Draw(im)
        if kind=='rails':
            for y in (8,40,72,104):d.rectangle((0,y,127,y+13),fill=c1);d.line((0,y+2,127,y+2),fill=tone(c1,1.2),width=2)
            for x in (22,94):d.rectangle((x,0,x+11,127),fill=c2);d.line((x+2,0,x+2,127),fill=tone(c2,1.2),width=2)
        else:
            for x in (14,46,78,110):d.rectangle((x,0,x+5,127),fill=c1);d.line((x,0,x,127),fill=tone(c1,1.3))
            for y in (28,90):d.rectangle((0,y,127,y+5),fill=c1)
    elif kind=='lamp_off':
        for y in (8,65):
            for x in (8,65):d.rectangle((x,y,x+53,y+53),fill=tone(c1,.65),outline=tone(c1,1.2),width=2)
    # World repeat textures have no arbitrary outer border. Opposite edges use
    # their authored periodic motifs; no blur/interpolation is introduced.
    return im

def build(output=core.DEFAULT_OUTPUT):
    output=Path(output);rows=[]
    for i,(name,kind,c1,c2,c3) in enumerate(specs()):
        im=block(name,kind,c1,c2,c3,i+1)
        path=output/f'source/textures/world/{name}.png';path.parent.mkdir(parents=True,exist_ok=True);im.save(path,optimize=True)
        bed=json.loads((ROOT/'tools/data/bedrock_world_128_mapping.json').read_text())['mappings'][name]
        rows.append({'id':'minecraft:'+name,'path':path.relative_to(output).as_posix(),'size_px':[128,128],
            'java_texture':'assets/minecraft/textures/block/'+name+'.png','bedrock_texture':bed+'.png',
            'style':kind,'native_grid':128,'sha256':core.sha(path),'status':'art_generated','client_verification':'not_run'})
    assert len(rows)==98
    core.save_json(output/'manifests/world_128.json',{'profile':core.PROFILE,'count':len(rows),'textures':rows})
    core.contact_sheet([(r['id'].split(':')[-1],output/r['path']) for r in rows],output/'previews/world_128.png',8,'WORLD / NATIVE128 TEXTURES')
    return {'world_textures':len(rows)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=core.DEFAULT_OUTPUT);a=p.parse_args();print(build(a.output))
