#!/usr/bin/env python3
"""Deterministic original 64x64 classic-skin prototypes and outfit overlays (Pillow)."""
import argparse, hashlib, json, random, uuid
from pathlib import Path
from PIL import Image, ImageDraw

ROLES = [("civilian",95),("shopkeeper",25),("food_seller",25),("fashion_seller",15),("road_transport",55),("police",40),("healthcare",30),("fire_rescue",15),("government",30),("rail_ropeway",25),("industrial",35),("professional",30),("story",20),("media",20),("entertainment",10),("aviation_marine",10),("black_lotus",20)]
OUTFITS = [("casual",20),("traditional",20),("formal",15),("sports",10),("festival",15),("premium",10),("utility",10)]
FIRST = "Aarav Aditi Aman Amrita Anaya Arjun Anil Anita Dev Diya Farhan Fatima Gauri Harish Isha Jai Jaya Karan Kavita Kiran Krishna Leela Manav Maya Meera Mohan Naina Neha Nikhil Pooja Priya Rahul Raj Ramesh Rani Riya Rohit Saira Sameer Sanjay Shreya Simran Sohan Tara Varun Veena Vikram Yash Zoya".split()
LAST = "Sharma Patil Deshmukh Kulkarni Khan Shah Joshi Verma Rao Mehta Singh Iyer Naik Fernandes Kapoor Das Gupta Shetty Menon More Jadhav Sethi Pawar Ansari Chavan".split()
TONES = [(224,173,126),(190,138,93),(162,109,72),(135,86,58),(111,71,49),(211,151,107),(174,123,88)]
COLORS = [(45,84,108),(99,54,69),(53,100,76),(132,106,72),(69,68,87),(167,124,74),(114,67,50),(76,98,105),(194,177,145),(45,47,54)]
UNIFORMS = {"police":(165,144,97),"healthcare":(220,228,224),"fire_rescue":(172,67,40),"government":(207,208,194),"rail_ropeway":(57,84,111),"industrial":(102,112,100),"media":(53,77,105),"black_lotus":(46,48,52),"aviation_marine":(59,89,108)}
NS = uuid.UUID("5c434a15-a08d-4f77-ae59-815d2b9b7ad1")

def shade(c, delta): return tuple(max(0,min(255,v+delta)) for v in c)

def box(d,x,y,w,h,c):
    if w>0 and h>0: d.rectangle((x,y,x+w-1,y+h-1),fill=(*c,255))

def cuboid(d,u,v,w,h,z,c):
    # Standard Minecraft unfolded UV: top, bottom, right, front, left, back.
    box(d,u+z,v,w,z,shade(c,13)); box(d,u+z+w,v,w,z,shade(c,-20))
    for x,ww,s in [(u,z,-12),(u+z,w,0),(u+z+w,z,-8),(u+2*z+w,w,-15)]:
        box(d,x,v+z,ww,h,shade(c,s))

def clothes(d,role,idx,shirt,pants,overlay=False):
    torso=(16,32) if overlay else (16,16)
    arms=[(40,32),(48,48)] if overlay else [(40,16),(32,48)]
    legs=[(0,32),(0,48)] if overlay else [(0,16),(16,48)]
    u,v=torso; cuboid(d,u,v,8,12,4,shirt); x,y=u+4,v+4
    trim=shade(shirt,35); dark=shade(shirt,-35)
    box(d,x,y,8,1,dark); box(d,x+3,y+1,2,2,trim)
    if idx%3==0:
        box(d,x+3,y+3,2,8,dark); box(d,x+4,y+4,1,1,trim); box(d,x+4,y+7,1,1,trim)
    elif idx%3==1:
        box(d,x,y+5,8,1,trim); box(d,x,y+6,8,1,dark)
    else:
        box(d,x+1,y+4,2,2,trim); box(d,x+5,y+4,2,2,dark)
    if role in UNIFORMS or role in ("road_transport","food_seller"):
        box(d,x+5,y+2,2,1,(224,186,91)); box(d,x+1,y+3,2,1,(216,218,211))
    box(d,x,y+11,8,1,shade(pants,-15))
    for u,v in arms:
        cuboid(d,u,v,4,12,4,shirt)
        if not overlay:
            # Skin hands filled by caller, preserving full sleeves.
            box(d,u,v+13,16,1,dark)
    for u,v in legs:
        cuboid(d,u,v,4,12,4,pants)
        box(d,u,v+14,16,2,(39,39,43))

def skin(role,idx):
    rng=random.Random(20261124+idx*997); im=Image.new("RGBA",(64,64)); d=ImageDraw.Draw(im)
    tone=TONES[idx%len(TONES)]; hair=[(32,27,25),(44,35,29),(62,43,32),(31,30,33),(98,87,75)][(idx//7)%5]
    cuboid(d,0,0,8,8,8,tone)
    box(d,8,0,8,8,hair)
    for x in (0,8,16,24):
        box(d,x,8,8,2,hair)
    box(d,8,10,1,4,hair); box(d,15,10,1,4,hair)
    if idx%4==0: box(d,9,10,5,1,hair)
    if idx%4==1: box(d,12,10,3,2,hair)
    box(d,9,12,2,1,(235,232,218)); box(d,13,12,2,1,(235,232,218))
    box(d,10,12,1,1,(36,35,36)); box(d,13,12,1,1,(36,35,36))
    box(d,11,13,1,1,shade(tone,-22)); box(d,11,15,2,1,shade(tone,-38))
    if idx%5==0: box(d,10,14,4,1,hair)
    if idx%7==0:
        box(d,10,11,1,1,(65,61,57)); box(d,13,11,1,1,(65,61,57)); box(d,11,12,2,1,(65,61,57))
    shirt=UNIFORMS.get(role, COLORS[(idx//3)%len(COLORS)])
    if role=="road_transport": shirt=(177,54,57) if idx%2==0 else (208,112,44)
    shirt=shade(shirt,rng.randint(-9,9)); pants=COLORS[(idx*3+1)%len(COLORS)] if role not in UNIFORMS else (53,57,61)
    clothes(d,role,idx,shirt,pants)
    for u,v in [(40,16),(32,48)]: box(d,u,v+14,16,2,tone)
    # Distinct small fabric tag using the per-character serial, not an invisible pixel marker.
    for j in range(9):
        if idx & (1<<j): box(d,20+j%3,28+j//3,1,1,shade(shirt,22))
    return im

def outfit(category,idx):
    im=Image.new("RGBA",(64,64)); d=ImageDraw.Draw(im)
    shirt=shade(COLORS[(idx//3)%len(COLORS)],(idx%10-5)*4)
    pants=COLORS[(idx*7+2)%len(COLORS)]
    clothes(d,category,idx,shirt,pants,True)
    x,y=20,36; light=shade(shirt,55); dark=shade(shirt,-40)
    if category=="traditional":
        box(d,x+3,y,2,10,light); box(d,x,y+10,8,2,light)
        for u,v in [(0,32),(0,48)]: box(d,u,v+4,16,4,shirt)
    elif category=="formal":
        box(d,x+2,y,4,7,(227,227,219)); box(d,x+3,y+1,2,7,dark)
        box(d,x+1,y+1,1,4,light); box(d,x+6,y+1,1,4,light)
    elif category=="sports":
        for u,v in [(40,32),(48,48)]: box(d,u+4,v+4,1,12,light)
        box(d,x,y+3,8,2,light)
    elif category=="festival":
        for k in range(0,8,2): box(d,x+k,y+8,1,2,(222,181,82))
        box(d,x,y+10,8,2,(190,135,70))
    elif category=="premium":
        box(d,x,y,8,1,light); box(d,x+1,y+3,6,1,light); box(d,x+5,y+7,2,2,dark)
    elif category=="utility":
        for a in (1,5): box(d,x+a,y+5,2,3,dark); box(d,x+a,y+5,2,1,light)
    return im

def generate(dest):
    dest.mkdir(parents=True,exist_ok=True); (dest/"npc-skins").mkdir(exist_ok=True); (dest/"outfits").mkdir(exist_ok=True)
    records=[]; hashes=set(); names=[f"{a} {b}" for a in FIRST for b in LAST]; random.Random(42).shuffle(names)
    i=0
    for role,count in ROLES:
        for rank in range(count):
            i+=1; ident=f"npc-{i:03d}"; im=skin(role,i)
            path=f"npc-skins/{ident}.png"; im.save(dest/path,optimize=True)
            digest=hashlib.sha256(im.tobytes()).hexdigest(); assert digest not in hashes; hashes.add(digest)
            records.append({"id":ident,"uuid":str(uuid.uuid5(NS,ident)),"name":names[i-1],"role":role,"skin":path,"model":"classic","gang_boss":role=="black_lotus" and rank==0,"initially_jailed":role=="black_lotus" and 1<=rank<=5})
    outfits=[]; outfit_hashes=set(); j=0
    for cat,count in OUTFITS:
        for _ in range(count):
            j+=1; ident=f"outfit-{j:03d}"; path=f"outfits/{ident}.png"; im=outfit(cat,j); im.save(dest/path,optimize=True)
            digest=hashlib.sha256(im.tobytes()).hexdigest(); assert digest not in outfit_hashes; outfit_hashes.add(digest)
            outfits.append({"id":ident,"category":cat,"texture":path,"model":"classic-overlay","price_ark":150+(j%10)*35})
    assert len(records)==500 and len(outfits)==100 and sum(r["initially_jailed"] for r in records)==5
    (dest/"NPC_REGISTRY.json").write_text(json.dumps(records,indent=2)+"\n",encoding="utf-8")
    (dest/"OUTFIT_REGISTRY.json").write_text(json.dumps(outfits,indent=2)+"\n",encoding="utf-8")
    for item in records+outfits:
        with Image.open(dest/(item.get("skin") or item["texture"])) as im: assert im.size==(64,64) and im.mode=="RGBA"
    print(f"Generated {len(records)} unique NPC skin textures and {len(outfits)} outfit overlays; 5 initial prisoners, 1 boss")

if __name__=="__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,required=True); generate(parser.parse_args().output)
