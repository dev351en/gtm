"""Isolated 128×128 art export profile; legacy IDs and builders stay intact."""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import studio_3d_engine as s3d
from gtm128_materials import tile, PALETTE

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT=ROOT/'creative'/'generated_128'
PROFILE='INDRAPRASTHA_128_V1'

def save_json(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def register_material(name,colour,kind='metal'):
    if name in s3d.MAT_INDEX:return s3d.MAT_INDEX[name]
    if len(s3d.MATERIALS)>=256:raise ValueError('128 material atlas capacity exceeded')
    s3d.MAT_INDEX[name]=len(s3d.MATERIALS);s3d.MATERIALS.append((name,colour,kind));s3d.ATLAS_ARR=None
    return s3d.MAT_INDEX[name]

def configure(output=DEFAULT_OUTPUT):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    s3d.TILE_SIZE=128;s3d.ATLAS_SIZE=2048
    s3d.TEX_32_DIR=output/'source/textures/materials'
    s3d.ATLAS_PATH=output/'source/textures/gtm_master_atlas_128.png'
    s3d.ATLAS_RESOURCE='gtm:item/gtm_master_atlas_128'
    s3d.generate_32x32_tile=tile;s3d.ATLAS_ARR=None
    # Register the same food cells in every process so atlas indices are stable.
    import food_art
    for name,colour in food_art.PALETTE.items():
        if name in ('bread','crust','toast'):kind='food_bread'
        elif name in ('cream','milk','rice'):kind='food_rice'
        elif name in ('gravy','chilli','pink'):kind='food_sauce'
        elif name in ('leaf','mint'):kind='food_leaf'
        elif name in ('clay','terra'):kind='food_ceramic'
        elif name in ('steel','rim'):kind='metal'
        elif name=='ice':kind='glass'
        else:kind='food_grain'
        register_material('food_'+name,colour,kind)
    return output

def build_materials(output=DEFAULT_OUTPUT):
    output=configure(output);s3d.ATLAS_ARR=s3d.build_shared_atlas()
    entries=[]
    for path in sorted(s3d.TEX_32_DIR.glob('*.png')):
        name=path.stem;idx=s3d.MAT_INDEX.get(name)
        entries.append({'id':name,'path':path.relative_to(output).as_posix(),'size_px':[128,128],
                        'sha256':sha(path),'atlas_cell':None if idx is None else [idx%16,idx//16],
                        'native_grid':128,'source':'tools/gtm128_materials.py'})
    save_json(output/'manifests/materials_128.json',{'profile':PROFILE,'materials':entries,
        'atlas':{'path':'source/textures/gtm_master_atlas_128.png','size_px':[2048,2048],
        'cell_px':[128,128],'columns':16,'padding_texels':0,'sha256':sha(s3d.ATLAS_PATH)},
        'note':'The atlas is a composite of128px texture tiles; its2048px extent is not an asset-resolution exception.'})
    contact_sheet([(e['id'],output/e['path']) for e in entries],output/'previews/materials_128.png',8,'INDRAPRASTHA / NATIVE128 MATERIALS')
    return entries

def bounds(pb):
    pts=[]
    for b in pb.bones.values():
        for p in b['parts']:
            o=np.array(p['origin'],float);size=np.array(p['size'],float)
            corners=[o+size*np.array([x,y,z]) for x in (0,1) for y in (0,1) for z in (0,1)]
            if p.get('rot'):
                pivot=np.array(p.get('pivot') or (o+size*.5),float)
                rx,ry,rz=np.radians(p['rot']);cx,sx=math.cos(rx),math.sin(rx);cy,sy=math.cos(ry),math.sin(ry);cz,sz=math.cos(rz),math.sin(rz)
                r=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
                corners=[pivot+r@(q-pivot) for q in corners]
            pts.extend(corners)
    if not pts:raise ValueError('Empty geometry')
    a=np.asarray(pts);return a.min(axis=0),a.max(axis=0)

def export_model(pb,asset_id,title,category,output=DEFAULT_OUTPUT,metadata=None):
    output=Path(output);slug=asset_id.removeprefix('gtm:')
    if not slug or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789_' for c in slug):raise ValueError(asset_id)
    if not category or '/' in category or '..' in category:raise ValueError(category)
    for b in pb.bones.values():
        for p in b['parts']:
            for mat in [p['mat'],*p.get('face_mats',{}).values()]:
                if mat not in s3d.MAT_INDEX:raise ValueError(f'{asset_id}: undefined material {mat}')
    geo=output/f'source/models/{category}/{slug}.geo.json'
    java=output/f'source/models/{category}/java/{slug}.json'
    icon=output/f'source/icons/{category}/{slug}.png'
    cubes=pb.export_bedrock_geo('geometry.gtm.'+slug,geo)
    pb.export_java_item(java)
    camera=metadata or {}
    pb.render_icon(icon,size=128,grid=128,yaw_deg=camera.get('preview_yaw_deg',-38),pitch_deg=camera.get('preview_pitch_deg',24))
    # Keep source bones editable and recoverable, not just platform exports.
    editable=output/f'source/models/{category}/editable/{slug}.parts.json'
    save_json(editable,{'schema_version':1,'id':'gtm:'+slug,'units_per_block':16,'bones':pb.bones})
    j=json.loads(java.read_text());j['credit']='Original GTM / SD Craft — Indraprastha128 profile'
    # Target26.3 supports free multi-axis element rotations (introduced1.21.11).
    # Preserve the authored X->Y->Z rotation; do not clamp it to the old angle set.
    parts=[p for b in pb.bones.values() for p in b['parts']]
    for e,p in zip(j['elements'],parts):
        if p.get('rot') and e.get('rotation'):
            pivot=e['rotation']['origin'];rx,ry,rz=p['rot']
            e['rotation']={'origin':pivot,'x':rx,'y':ry,'z':rz}
    save_json(java,j)
    low,high=bounds(pb);span=high-low
    g=json.loads(geo.read_text());desc=g['minecraft:geometry'][0]['description']
    desc['visible_bounds_width']=round(max(span[0],span[2])/16+1,3)
    desc['visible_bounds_height']=round(span[1]/16+1,3)
    desc['visible_bounds_offset']=[round(v/16,3) for v in (low+high)*.5]
    save_json(geo,g)
    record=dict(metadata or {})
    for stale in ('json_path','model_path','variants','sha256','status'):
        record.pop(stale,None)
    record.update({'id':'gtm:'+slug,'title':title,'category':category,'profile':PROFILE,
        'geometry':'geometry.gtm.'+slug,'geometry_path':geo.relative_to(output).as_posix(),
        'java_model_path':java.relative_to(output).as_posix(),'icon_path':icon.relative_to(output).as_posix(),
        'editable_source':editable.relative_to(output).as_posix(),'icon_size_px':[128,128],'native_render_grid':128,
        'material_tile_px':[128,128],'atlas_path':'source/textures/gtm_master_atlas_128.png',
        'cube_count':cubes,'bone_count':len(pb.bones),'local_axes':'x right, y up, z forward;16units per block',
        'actual_bounds_blocks':{'min':[round(v/16,4) for v in low],'max':[round(v/16,4) for v in high]},
        'pivots':[{'id':name,'position_units':b['pivot'],'parent':b['parent']} for name,b in pb.bones.items()],
        'java_rotation_approximations':0,'java_rotation_format':'multi_axis_1.21.11_plus','status':'art_generated','engine_binding':'pending_review',
        'client_verification':'not_run','rights':'Original project procedural art; SD Craft project source',
        'sha256':{'geometry':sha(geo),'java_model':sha(java),'icon':sha(icon),'editable':sha(editable)}})
    return record

def contact_sheet(entries,dest,cols=8,title='GTM / INDRAPRASTHA128'):
    dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
    cw,ch=152,164;header=62;rows=math.ceil(len(entries)/cols)
    im=Image.new('RGB',(cols*cw+24,header+rows*ch+16),'#151B20');d=ImageDraw.Draw(im)
    try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11);head=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)
    except OSError:font=head=ImageFont.load_default()
    d.text((18,16),title,fill='#D6AD59',font=head)
    for i,(label,path) in enumerate(entries):
        x=12+(i%cols)*cw;y=header+(i//cols)*ch
        d.rectangle((x,y,x+cw-6,y+ch-7),fill='#202A30')
        src=Image.open(path).convert('RGBA');src.thumbnail((128,128),Image.Resampling.NEAREST)
        im.paste(src,(x+(cw-6-src.width)//2,y+5+(128-src.height)//2),src)
        label=str(label)
        while d.textlength(label,font=font)>cw-16 and len(label)>3:label=label[:-2]+'…'
        d.text((x+7,y+140),label,fill='#D2B997',font=font)
    im.save(dest,optimize=True)
    return dest

def batch_manifest(name,entries,output=DEFAULT_OUTPUT):
    output=Path(output)
    save_json(output/f'manifests/{name}_128.json',{'profile':PROFILE,'count':len(entries),'assets':entries})
    contact_sheet([(r['title'],output/r['icon_path']) for r in entries],output/f'previews/{name}_128.png',8,name.upper()+' / NATIVE128')
    return entries

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate native128 material tiles and their shared atlas')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps({'material_tiles':len(build_materials(args.output)), 'profile':PROFILE}))
