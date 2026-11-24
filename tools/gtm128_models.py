"""Regenerate the existing transport/furniture/festival catalogue at native128."""
import argparse
import json
from pathlib import Path
import gtm128_core as core
import regenerate_transport_all as transport
import build_creative_transport as transport_specs
import regenerate_furniture_all as furniture
import build_creative_furniture_facilities as furniture_specs
import regenerate_equipment_finishes_festivals as equipment
import city_festival_art
import gtm128_refinements as refine

ROOT=Path(__file__).resolve().parents[1]

def previous(name,key=None):
    data=json.loads((ROOT/f'creative/manifests/{name}.json').read_text())
    return {r['id']:r for r in (data[key] if key else data)}

def build(output=core.DEFAULT_OUTPUT):
    output=core.configure(output)
    prior=previous('transport_art_manifest'); rows=[]
    for vid,title,mfg,cat,dims,variants in transport_specs.ROAD_TARGETS:
        pb=transport.build_road_vehicle(vid,title,mfg,cat,dims)
        pb=refine.transport(pb,vid,cat,dims)
        meta={**prior.get('gtm:'+vid,{}),'subcategory':cat,'manufacturer':mfg,'dimensions_blocks':dims,
              'design_variants_requested':variants,'generated_variant':'normal',
              'variant_note':'This record is the normal art state. Separate damaged/critical/wreck artwork is emitted by gtm128_vehicle_states.py and listed in vehicle_states_128.json.'}
        rows.append(core.export_model(pb,vid,title,'transport',output,meta))
    for vid,title,mfg,cat,dims,interior in transport_specs.RAIL_ROPEWAY_TARGETS:
        pb=transport.build_rail_or_ropeway(vid,cat,dims)
        pb=refine.transport(pb,vid,cat,dims)
        rows.append(core.export_model(pb,vid,title,'transport',output,{**prior.get('gtm:'+vid,{}),'subcategory':cat,
            'dimensions_blocks':dims,'interior_description':interior,'generated_variant':'normal'}))
    for vid,title,subcat,cat,dims,pivots in transport_specs.HELI_MARINE_TARGETS:
        pb=transport.build_helicopter_or_marine(vid,cat,dims,pivots)
        pb=refine.transport(pb,vid,cat,dims)
        rows.append(core.export_model(pb,vid,title,'transport',output,{**prior.get('gtm:'+vid,{}),'subcategory':cat,
            'dimensions_blocks':dims,'generated_variant':'normal'}))
    assert len(rows)==87
    core.batch_manifest('transport',rows,output); print('Transport87 generated',flush=True)
    prior=previous('furniture_art_manifest');rows=[]
    for cat,items in furniture_specs.FURNITURE_CATEGORIES.items():
        for fid,title,dims,itype in items:
            pb=furniture.build_furniture_piece(fid,cat,dims,itype)
            pb=refine.furniture(pb,fid,cat,dims)
            meta={**prior.get('gtm:'+fid,{}),'subcategory':cat,'dimensions_blocks':dims,'interaction_type':itype}
            rows.append(core.export_model(pb,fid,title,'furniture',output,meta))
    assert len(rows)==200
    core.batch_manifest('furniture',rows,output);print('Furniture200 generated',flush=True)
    swatches={'steel':'steel_light','rim':'stainless','clay':'terracotta','terra':'terracotta','cream':'linen_white',
        'milk':'paint_white','crust':'wood_oak','bread':'bamboo','toast':'wood_sheesham','gold':'festival_toran',
        'gravy':'paint_red','chilli':'fire_red','leaf':'leaf_green','mint':'paint_emerald','pink':'festival_rangoli',
        'rice':'fabric_beige','bean':'leather_tan','saffron':'glowstone_lamp','violet':'neon_magenta','ice':'sea_prism'}
    prior=previous('festivals_manifest','festivals');rows=[]
    for fid,(cat,title,parts) in city_festival_art.festival().items():
        pb=equipment.recipe_to_partbuilder(parts,swatches,slug=fid)
        rows.append(core.export_model(pb,fid,title,'festivals',output,{**prior.get('gtm:'+fid,{}),
            'activation_mode':'manual_staff_only','world_placement':'not_applied','source_family':'legacy_active_catalogue',
            'theme_migration_status':'proposal_preserved_not_applied'}))
    assert len(rows)==100
    core.batch_manifest('festivals',rows,output);print('Festivals100 generated',flush=True)
    return {'transport':87,'furniture':200,'festivals':100}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=core.DEFAULT_OUTPUT)
    args=p.parse_args();print(json.dumps(build(args.output)))
