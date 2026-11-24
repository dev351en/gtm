"""Bind 400 extra Revision 4 NPC identities to walkable positions in the public snapshot."""
import argparse
import json
import math
import random
import zipfile
from pathlib import Path

import yaml
from survey_world import Survey

ROOT = Path(__file__).resolve().parents[1]
FLOORS = {"minecraft:"+m for m in ("smooth_stone","polished_andesite","stone_bricks","bricks",
          "oak_planks","spruce_planks","smooth_quartz","quartz_bricks","light_gray_concrete",
          "polished_granite","polished_diorite","sandstone","smooth_sandstone","terracotta")}


def usable(survey,x,y,z):
    return (survey.block(x,y-1,z) in FLOORS and survey.block(x,y,z)=="minecraft:air"
            and survey.block(x,y+1,z)=="minecraft:air")


def generate(world,registry,dest):
    records=json.loads(registry.read_text())
    sites=yaml.safe_load((ROOT/"config/SDCraftCore/runtime.yml").read_text())["sites"]
    centres=[sites[k] for k in ("bank","hospital","police","fire","dealership","gas_station","airport","metro","spawn")]
    rng=random.Random(41827)
    with zipfile.ZipFile(world) as archive:
        survey=Survey(archive)
        used=set()
        rows=[]
        for i,record in enumerate(records[100:],101):
            for attempt in range(2400):
                centre=centres[(i+attempt//100)%len(centres)]
                x=math.floor(centre["x"])+rng.randint(-45,45)
                z=math.floor(centre["z"])+rng.randint(-45,45)
                if (x,z) in used: continue
                y0=math.floor(centre["y"])
                for delta in (0,-1,1,-2,2,-3,3,-4,4,-5,5):
                    y=y0+delta
                    if usable(survey,x,y,z) and sum(usable(survey,x+dx,y,z+dz) for dx,dz in
                            ((1,0),(-1,0),(0,1),(0,-1)))>=2:
                        break
                else: continue
                break
            else: raise ValueError(f"Could not survey anchor for {record['id']}")
            used.add((x,z))
            rows.append("\t".join(map(str,(record["id"],record["uuid"],record["name"],record["role"],x,y,z))))
    if len(rows)!=400: raise ValueError("Expected 400 additional identities")
    dest.write_text("\n".join(rows)+"\n",encoding="utf-8")
    print("400 unique additional positions verified for floor support, headroom and two adjacent open positions.")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("world_zip",type=Path)
    parser.add_argument("npc_registry",type=Path)
    parser.add_argument("output_tsv",type=Path)
    args=parser.parse_args()
    generate(args.world_zip,args.npc_registry,args.output_tsv)
