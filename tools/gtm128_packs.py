"""Build and resolve complete128 art resource graphs. Never installs a pack."""
import argparse
import copy
import hashlib
import io
import json
import uuid
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
from PIL import Image
import gtm128_core as core

def encoded(data):return (json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n').encode()

def archive(path,files):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(path,'w') as z:
        for name,content in sorted(files.items()):
            if name.startswith('/') or '..' in Path(name).parts:raise ValueError('Unsafe archive path')
            info=ZipInfo(name,(2026,11,25,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,content)
    with ZipFile(path) as z:
        bad=z.testzip()
        if bad:raise ValueError('Invalid archive member '+bad)
    return {'path':str(path),'size_bytes':path.stat().st_size,'sha256':core.sha(path),'members':len(files)}

def read(output,name):return json.loads((output/'manifests'/name).read_text())

def model_records(output):
    rows=[]
    for name in ('transport','furniture','festivals'):
        rows.extend(read(output,name+'_128.json')['assets'])
    extra=read(output,'equipment_food_128.json')
    for name in ('equipment','food','weapons','hero_props'):rows.extend(extra[name])
    rows.extend(read(output,'finishes_128.json')['mappings_128'])
    for name in ('vehicle_states','festival_additions'):
        data=read(output,name+'_128.json')
        options=[v for v in data.values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'java_model_path' in v[0]]
        if len(options)!=1:raise ValueError('Ambiguous model entries in '+name)
        rows.extend(options[0])
    if len({r['id'] for r in rows})!=len(rows):raise ValueError('Overlapping art IDs')
    return rows

def build(output=core.DEFAULT_OUTPUT):
    output=Path(output);records=model_records(output);java={};bed={};mapping={'minecraft:paper':[],'minecraft:bread':[]};icons={}
    java['pack.mcmeta']=encoded({'pack':{'description':'GTM Indraprastha128 • SD Craft • art staging',
                                        'min_format':[97,1],'max_format':[97,1]}})
    uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'https://github.com/dev351en/gtm/indraprastha128/'+s))
    bed['manifest.json']=encoded({'format_version':2,'header':{'name':'GTM Indraprastha128 — Art Staging',
        'description':'Native128 art; runtime and client integration pending. SD Craft.',
        'uuid':uid('header'),'version':[1,0,0],'min_engine_version':[1,21,80]},
        'modules':[{'type':'resources','uuid':uid('resources'),'version':[1,0,0]}]})
    bed['render_controllers/gtm128.json']=encoded({'format_version':'1.8.0','render_controllers':{
        'controller.render.gtm128':{'geometry':'Geometry.default','materials':[{'*':'Material.default'}],'textures':['Texture.default']}}})
    shared=(output/'source/textures/gtm_master_atlas_128.png').read_bytes()
    java['assets/gtm/textures/item/gtm_master_atlas_128.png']=shared
    bed['textures/gtm/gtm_master_atlas_128.png']=shared
    def insert(path,content,target):
        if path in target and target[path]!=content:raise ValueError('Conflicting pack member '+path)
        target[path]=content
    for r in records:
        key=r['id'].split(':',1)[1];j=json.loads((output/r['java_model_path']).read_text())
        g=json.loads((output/r['geometry_path']).read_text());g=copy.deepcopy(g)
        geometry=g['minecraft:geometry'][0];gid=geometry['description']['identifier']
        # The attachable adapter binds the root to the actual item slot while
        # retaining the editable multi-bone articulation and all child pivots.
        geometry['bones'][0]['binding']='q.item_slot_to_bone_name(c.item_slot)'
        surface='textures/gtm/gtm_master_atlas_128'
        if r.get('texture'):
            data=(output/r['texture']).read_bytes();surface='textures/gtm/finishes/'+key
            bed[surface+'.png']=data
            for tex in j['textures'].values():
                if isinstance(tex,str) and not tex.startswith('#'):
                    ns,rel=tex.split(':',1);insert(f'assets/{ns}/textures/{rel}.png',data,java)
        java[f'assets/gtm/models/item/{key}.json']=encoded(j)
        java[f'assets/gtm/items/{key}.json']=encoded({'model':{'type':'minecraft:model','model':'gtm:item/'+key}})
        bed[f'models/entity/{key}.geo.json']=encoded(g)
        bed[f'attachables/{key}.json']=encoded({'format_version':'1.10.0','minecraft:attachable':{'description':{
            'identifier':r['id'],'materials':{'default':'entity_alphatest'},'textures':{'default':surface},
            'geometry':{'default':gid},'render_controllers':['controller.render.gtm128']}}})
        icon=r.get('icon_path') or r.get('icon')
        if not icon:raise ValueError('Missing icon '+key)
        bed[f'textures/items/gtm_{key}.png']=(output/icon).read_bytes()
        icons['gtm_'+key]={'textures':'textures/items/gtm_'+key}
        base='minecraft:bread' if r.get('category')=='food' else 'minecraft:paper'
        mapping[base].append({'type':'definition','model':r['id'],'bedrock_identifier':r['id'],
            'display_name':r.get('title',key),'bedrock_options':{'icon':'gtm_'+key}})
    # Explicit semantic aliases preserve the existing30 FoodCatalogue runtime
    # keys (gtm:chai) alongside the creative IDs (gtm:food_chai).
    food_aliases=[]
    for r in read(output,'equipment_food_128.json')['food']:
        creative=r['id'].split(':')[1];key=creative.removeprefix('food_')
        if key==creative:continue
        java[f'assets/gtm/items/{key}.json']=encoded({'model':{'type':'minecraft:model','model':'gtm:item/'+creative}})
        a=json.loads(bed[f'attachables/{creative}.json']);a['minecraft:attachable']['description']['identifier']='gtm:'+key
        bed[f'attachables/{key}.json']=encoded(a)
        mapping['minecraft:bread'].append({'type':'definition','model':'gtm:'+key,'bedrock_identifier':'gtm:'+key,
            'display_name':r['title'],'bedrock_options':{'icon':'gtm_'+creative}})
        food_aliases.append({'runtime_id':'gtm:'+key,'art_id':r['id']})
    # Independent world layer, using paths checked against Mojang's terrain data.
    world=read(output,'world_128.json')['textures']
    for r in world:
        data=(output/r['path']).read_bytes();insert(r['java_texture'],data,java);insert(r['bedrock_texture'],data,bed)
    # UI textures are supplied as art, without replacing native HUD/input code.
    for family in ('phone','hud','brands','identity'):
        for r in read(output,family+'_128.json')['assets']:
            key=r['id'];data=(output/r['png']).read_bytes()
            java[f'assets/gtm/textures/ui/{family}/{key}.png']=data;bed[f'textures/ui/gtm/{family}/{key}.png']=data
    pack_icon=(output/'source/branding/core/server_icon_master.png')
    if not pack_icon.exists():
        identity=read(output,'identity_128.json')['assets'];pack_icon=output/next(x['png'] for x in identity if 'server' in x['id'])
    java['pack.png']=pack_icon.read_bytes();bed['pack_icon.png']=pack_icon.read_bytes()
    bed['textures/item_texture.json']=encoded({'resource_pack_name':'gtm_indraprastha128','texture_name':'atlas.items','texture_data':icons})
    packs=output/'packs';packs.mkdir(exist_ok=True)
    jr=archive(packs/'GTM_Indraprastha_128_Java.zip',java);br=archive(packs/'GTM_Indraprastha_128_Bedrock.mcpack',bed)
    proposed={'format_version':2,'items':{k:v for k,v in mapping.items() if v}}
    core.save_json(packs/'Geyser_v2_128_ART_PROPOSAL.json',proposed)
    checks=validate_pack_graph(java,bed,proposed,len(records)+len(food_aliases))
    report={'profile':core.PROFILE,'target_java':'26.3','java_resource_format':[97,1],
        'format_source':'https://www.minecraft.net/en-us/article/minecraft-java-edition-26-3',
        'rotation_source':'https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-11',
        'base_art_models':509,'additional_base_models':69,'road_damage_variants':195,'cosmetic_variants':300,
        'total_model_pairs':len(records),'food_runtime_aliases':food_aliases,'world_textures':len(world),
        'packs':[{**x,'path':Path(x['path']).relative_to(output).as_posix()} for x in (jr,br)],
        'checks':checks,'errors':[],'client_verification':'not_run','runtime_mapping_status':'proposal_only_not_installed',
        'legacy_mapping_policy':'Only exact30 food aliases included. Road/furniture/finish migrations remain review proposals.'}
    core.save_json(output/'reports/pack_validation_128.json',report)
    return report

def validate_pack_graph(java,bed,mappings,expected):
    geom={}
    for path,data in bed.items():
        if path.endswith('.geo.json'):
            for g in json.loads(data)['minecraft:geometry']:
                gid=g['description']['identifier']
                if gid in geom:raise ValueError('Duplicated geometry identifier '+gid)
                geom[gid]=g
    icons=json.loads(bed['textures/item_texture.json'])['texture_data'];seen=set();faces=0
    for rows in mappings['items'].values():
        for r in rows:
            aid=r['model'];key=aid.split(':')[1]
            if aid in seen or aid!=r['bedrock_identifier']:raise ValueError('Invalid mapping '+aid)
            seen.add(aid)
            item=json.loads(java[f'assets/gtm/items/{key}.json'])['model'];model_path=item['model'].split(':')[1]
            j=json.loads(java['assets/gtm/models/'+model_path+'.json']);tex=j['textures']
            for e in j['elements']:
                for f in e['faces'].values():
                    ref=f['texture'];walk=set()
                    while ref.startswith('#'):
                        if ref in walk:raise ValueError('Texture reference cycle '+aid)
                        walk.add(ref);ref=tex[ref[1:]]
                    ns,part=ref.split(':',1)
                    if f'assets/{ns}/textures/{part}.png' not in java:raise ValueError('Missing Java texture '+ref)
                    faces+=1
            attach=json.loads(bed[f'attachables/{key}.json'])['minecraft:attachable']['description']
            g=geom[attach['geometry']['default']]
            if attach['identifier']!=aid:raise ValueError('Attachable ID mismatch')
            if sum(len(b.get('cubes',[])) for b in g['bones'])!=len(j['elements']):raise ValueError('Platform geometry count mismatch '+aid)
            surface=attach['textures']['default']+'.png'
            with Image.open(io.BytesIO(bed[surface])) as im:
                if im.size!=(g['description']['texture_width'],g['description']['texture_height']):raise ValueError('Geometry texture dimensions mismatch '+aid)
            icon=icons[r['bedrock_options']['icon']]['textures']+'.png'
            with Image.open(io.BytesIO(bed[icon])) as im:
                if im.size!=(128,128) or not im.convert('RGBA').getchannel('A').getbbox():raise ValueError('Invalid128 icon '+aid)
    if len(seen)!=expected:raise ValueError('Wrong definition count')
    return {'item_definitions_resolved':len(seen),'model_geometries_resolved':len(geom),'java_texture_face_references':faces,
        'bedrock_multi_bone_cube_counts':'matched','texture_dimensions':'matched','icons':'all128_rgba_nonempty',
        'zip_crc':'passed','live_client':'not_run'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=core.DEFAULT_OUTPUT);a=p.parse_args()
    print(json.dumps(build(a.output),indent=2))
