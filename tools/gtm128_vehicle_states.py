#!/usr/bin/env python3
"""Art-only damaged/critical/wreck exports derived from the final65 road models.

Normal geometry, IDs and materials are read-only. Variant IDs are proposals for
engine binding; this script does not implement damage physics or registration.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image
import gtm128_core as core
import studio_3d_engine as s3d
from build_creative_transport import ROAD_TARGETS

STATES=("damaged","critical","wreck")
GLASS={"glass_tint","glass_clear","windshield_front"}
PAINT={"auto_green","taxi_yellow","fire_red","police_navy","ambulance_white","lotus_dark","linen_white","car_door_bus"}

def signature(pb):
    shape=[]
    for name,bone in sorted(pb.bones.items()):
        for p in bone["parts"]:
            shape.append([name,p["origin"],p["size"],p.get("rot"),p.get("pivot")])
    return hashlib.sha256(json.dumps(shape,separators=(",",":"),sort_keys=True).encode()).hexdigest()

def center(p):return [p["origin"][i]+p["size"][i]/2 for i in range(3)]
def volume(p):return math.prod(p["size"])
def painted(p):return p["mat"].startswith("paint_") or p["mat"] in PAINT

def shard_glass(p,state):
    if state=="wreck":return []
    # Keep recognizable glazing fragments around an actual geometric opening.
    if state=="damaged":factors=[(0,.45,0,.44),(.53,.47,.0,.45),(0,.45,.53,.47)]
    else:factors=[(.0,.25,.0,.32),(.74,.26,.73,.27)]
    flat_axis=min(range(3),key=lambda a:p["size"][a]);axes=[a for a in range(3) if a!=flat_axis]
    a,b=axes;result=[]
    for i,(sa,wa,sb,wb) in enumerate(factors):
        q=copy.deepcopy(p);q["name"]=p["name"]+f"_fracture_{i}"
        q["origin"][a]+=p["size"][a]*sa;q["size"][a]*=wa
        q["origin"][b]+=p["size"][b]*sb;q["size"][b]*=wb
        q["size"]=[round(max(.12,v),3) for v in q["size"]]
        q["origin"]=[round(v,3) for v in q["origin"]]
        result.append(q)
    return result

def crush_panel(p,state,side):
    q=copy.deepcopy(p);q["name"]=p["name"]+"_retained_shell"
    # Split a large body panel so damage changes its silhouette locally.
    cut={"damaged":.23,"critical":.34,"wreck":.40}[state]
    q["size"][2]=p["size"][2]*(1-cut)
    dent=copy.deepcopy(p);dent["name"]=p["name"]+"_crumpled_front"
    dent["origin"][2]+=p["size"][2]*(1-cut)
    dent["size"][2]=p["size"][2]*cut*({"damaged":.82,"critical":.58,"wreck":.36}[state])
    shrink={"damaged":.90,"critical":.73,"wreck":.57}[state]
    oldw=dent["size"][0];dent["size"][0]*=shrink
    dent["origin"][0]+=(oldw-dent["size"][0])*(.84 if side<0 else .16)
    dent["size"][1]*={"damaged":.86,"critical":.67,"wreck":.45}[state]
    for piece in [q,dent]:
        piece["origin"]=[round(v,3) for v in piece["origin"]]
        piece["size"]=[round(max(.1,v),3) for v in piece["size"]]
    return [q,dent]

def lower_upper_structure(pb,crease,scale):
    def yy(v):return crease+(v-crease)*scale if v>crease else v
    for b in pb.bones.values():
        b["pivot"][1]=round(yy(b["pivot"][1]),3)
        for p in b["parts"]:
            bottom=p["origin"][1];top=bottom+p["size"][1]
            p["origin"][1]=round(yy(bottom),3);p["size"][1]=round(max(.1,yy(top)-yy(bottom)),3)
            if p.get("pivot"):p["pivot"][1]=round(yy(p["pivot"][1]),3)

def lean_two_wheeler(pb,degrees):
    a=math.radians(degrees);co,si=math.cos(a),math.sin(a)
    def rotate(p):return [p[0]*co-p[1]*si,p[0]*si+p[1]*co,p[2]]
    for b in pb.bones.values():
        b["pivot"]=[round(x,3) for x in rotate(b["pivot"])]
        for p in b["parts"]:
            cp=rotate(center(p));p["origin"]=[round(cp[i]-p["size"][i]/2,3) for i in range(3)]
            rr=p.get("rot") or [0,0,0];p["rot"]=[rr[0],rr[1],rr[2]+degrees];p["pivot"]=[round(x,3) for x in cp]
    low,_=core.bounds(pb);dy=-float(low[1])
    for b in pb.bones.values():
        b["pivot"][1]=round(b["pivot"][1]+dy,3)
        for p in b["parts"]:
            p["origin"][1]=round(p["origin"][1]+dy,3)
            if p.get("pivot"):p["pivot"][1]=round(p["pivot"][1]+dy,3)

def derive(normal,asset_id,category,dims,state):
    pb=s3d.PartBuilder();pb.bones=copy.deepcopy(normal.bones)
    W,H,L=[v*16 for v in dims];two=category in ("motorcycle","scooter")
    side=-1 if hashlib.sha256(asset_id.encode()).digest()[0]%2 else 1
    changes={"split_body_panels":0,"removed_lights_or_trim":0,"fractured_glazing_panels":0,"removed_glazing_panels":0,"stripped_wheels":0,"upper_structure_compressed":False,"two_wheeler_lean_degrees":0}
    candidates=[(bn,i,p) for bn,b in pb.bones.items() if not bn.startswith("wheel_") for i,p in enumerate(b["parts"]) if painted(p)]
    if not candidates:candidates=[(bn,i,p) for bn,b in pb.bones.items() if not bn.startswith("wheel_") for i,p in enumerate(b["parts"]) if p["mat"] not in GLASS]
    target=max(candidates,key=lambda r:volume(r[2]))[:2]
    for bn,b in pb.bones.items():
        parts=[]
        for i,p in enumerate(b["parts"]):
            cp=center(p);mat=p["mat"]
            if bn.startswith("wheel_"):
                # Strip a visible front tyre in critical/wreck states; keep the hub.
                if bn=="wheel_fl" and state in ("critical","wreck") and mat=="rubber_tire":
                    changes["stripped_wheels"]=1;continue
                if bn=="wheel_fl":
                    q=copy.deepcopy(p);rr=q.get("rot") or [0,0,0]
                    q["rot"]=[rr[0],rr[1]+(12 if state=="damaged" else 25),rr[2]+(5 if state=="damaged" else 17)]
                    q["pivot"]=copy.deepcopy(b["pivot"]);parts.append(q)
                else:parts.append(p)
                continue
            if mat in GLASS:
                # Damaged retains some intact glazing; higher states open every pane.
                if state=="damaged" and i%2==1:parts.append(p)
                else:
                    pieces=shard_glass(p,state);parts.extend(pieces)
                    changes["fractured_glazing_panels" if pieces else "removed_glazing_panels"]+=1
                continue
            is_light=mat in ("headlight","headlight_face","taillight","taillight_face","beacon_blue","beacon_amber")
            front_trim=cp[2]>L*.34 and mat in ("grille_chrome","grille_black","grille_mesh","license_plate_mh01","chrome")
            if (is_light or front_trim) and (state!="damaged" or cp[0]*side>0):
                changes["removed_lights_or_trim"]+=1;continue
            if (bn,i)==target:
                parts.extend(crush_panel(p,state,side));changes["split_body_panels"]+=1;continue
            # Small forward covers come away in severe states and expose the frame.
            if state!="damaged" and painted(p) and cp[2]>L*.20 and p["size"][1]<H*.11 and p["size"][0]>W*.45:
                changes["removed_lights_or_trim"]+=1;continue
            parts.append(p)
        b["parts"]=parts
    pb.add_bone("damage_structure",(0,H*.2,L*.25),"chassis" if "chassis" in pb.bones else "root")
    paint=next((p["mat"] for b in normal.bones.values() for p in b["parts"] if painted(p)),"steel_dark")
    # A displaced, tilted hood/tank panel provides a readable mid-distance cue.
    if two:
        pb.cbox(side*W*.18,H*.35,L*.11,W*.48,H*.07,L*.20,paint,bone="damage_structure",rot=[-12 if state=="damaged" else -27,0,side*12],name="dented_tank_cover")
    else:
        pb.cbox(side*W*.08,H*.33,L*.30,W*.68,H*.045,L*.20,paint,bone="damage_structure",rot=[-7 if state=="damaged" else -24,0,side*9],name="buckled_hood")
    if state in ("critical","wreck"):
        # Visual-only exposed frame and radiator, using existing shared materials.
        for x in (-W*.23,W*.23):pb.cbox(x,H*.14,L*.26,max(.6,W*.06),max(.7,H*.055),L*.40,"steel_dark",bone="damage_structure",name="exposed_frame_rail")
        pb.cbox(0,H*.20,L*.28,W*.46,H*.14,max(.6,L*.035),"grille_black",bone="damage_structure",name="exposed_radiator")
        pb.cbox(0,H*.16,L*.09,W*.42,H*.12,L*.15,"steel_light",bone="damage_structure",name="exposed_engine_mass")
    if state=="wreck":
        lower_upper_structure(pb,H*.40,.46);changes["upper_structure_compressed"]=True
        if two:lean_two_wheeler(pb,67*side);changes["two_wheeler_lean_degrees"]=67*side
        else:
            # Roof skin remains as a crumpled diagonal rather than an intact canopy.
            pb.cbox(side*W*.10,H*.57,-L*.10,W*.62,H*.035,L*.28,"steel_dark",bone="damage_structure",rot=[9,0,side*14],name="collapsed_roof_skin")
    if signature(pb)==signature(normal):raise AssertionError(f"Unchanged state {asset_id} {state}")
    return pb,changes

def build(output=core.DEFAULT_OUTPUT):
    output=core.configure(output)
    manifest=output/"manifests/transport_128.json"
    records={r["id"]:r for r in json.loads(manifest.read_text())["assets"]}
    atlas=output/"source/textures/gtm_master_atlas_128.png"
    atlas_hash=core.sha(atlas)
    # Reuse finalized materials; do not rebuild or change the shared atlas here.
    s3d.ATLAS_ARR=np.asarray(Image.open(atlas).convert("RGBA"))
    result=[];groups=[];normal_hashes={};all_signatures=set()
    for idx,(vid,title,mfg,category,dims,_) in enumerate(ROAD_TARGETS):
        parent_id="gtm:"+vid;rec=records[parent_id]
        source=output/rec["editable_source"];geometry=output/rec["geometry_path"]
        normal_hashes[str(source)]=core.sha(source);normal_hashes[str(geometry)]=core.sha(geometry)
        pb=s3d.PartBuilder();pb.bones=json.loads(source.read_text())["bones"]
        normal_sig=signature(pb);entries=[("NORMAL",output/rec["icon_path"])]
        for state in STATES:
            variant,changes=derive(pb,vid,category,dims,state);sig=signature(variant)
            if sig in all_signatures:raise AssertionError(f"Duplicate damage geometry {vid} {state}")
            all_signatures.add(sig)
            meta={"parent_id":parent_id,"state":state,"subcategory":category,"manufacturer":mfg,
                  "normal_source_sha256":core.sha(geometry),"normal_editable_sha256":core.sha(source),
                  "normal_geometry_signature":normal_sig,"geometry_signature":sig,
                  "visual_changes":changes,"proposed_art_id":True,
                  "counted_in_base_509":False,"runtime_registration":"not_performed",
                  "physics_status":"not_implemented_by_art_export","material_registry_changed":False}
            r=core.export_model(variant,vid+"_"+state,title+" / "+state,"vehicle_states",output,meta)
            result.append(r);entries.append((state.upper(),output/r["icon_path"]))
        groups.append((title,entries))
        if (idx+1)%10==0:print(f"Vehicle states: {idx+1}/65 parents generated",flush=True)
    assert len(result)==195 and len(all_signatures)==195
    for path,h in normal_hashes.items():assert core.sha(path)==h,f"Normal source changed during variant generation: {path}"
    assert core.sha(atlas)==atlas_hash,"Shared material atlas changed during variant generation"
    # Each row is one parent with normal/damaged/critical/wreck; paginate for QA.
    preview_paths=[]
    for page,start in enumerate(range(0,len(groups),13),1):
        entries=[]
        for title,row in groups[start:start+13]:
            entries.extend([(state+" / "+title,path) for state,path in row])
        path=output/f"previews/vehicle_states_{page:02d}.png"
        core.contact_sheet(entries,path,4,"ROAD STATES / NORMAL · DAMAGED · CRITICAL · WRECK")
        preview_paths.append(path.relative_to(output).as_posix())
    core.save_json(output/"manifests/vehicle_states_128.json",{"profile":core.PROFILE,"count":195,"parent_count":65,
        "states":list(STATES),"assets":result,"previews":preview_paths,"counted_in_base_509":False,
        "normal_assets_unchanged":True,"shared_atlas_unchanged":True,"engine_binding":"pending_review","client_verification":"not_run"})
    return {"parent_count":65,"variants":195,"geometry_signatures":len(all_signatures),"normal_sources_unchanged":True,"shared_atlas_unchanged":True}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,default=core.DEFAULT_OUTPUT);args=p.parse_args();print(json.dumps(build(args.output),indent=2))
