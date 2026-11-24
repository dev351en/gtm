"""Resolve every custom item through Java, Geyser v2 and Bedrock resource graphs."""
import argparse
from pathlib import Path
import io
import json
from zipfile import ZipFile
from PIL import Image


def read_json(pack,path):
    return json.loads(pack.read(path))


def verify(root, title, mapping, count):
    rows=json.loads((root/mapping).read_text())
    if rows["format_version"]!=2:
        raise ValueError("Wrong Geyser schema")
    with ZipFile(root/f"GTM_{title}_Java.zip") as java, ZipFile(root/f"GTM_{title}_Bedrock.mcpack") as bed:
        if java.testzip() or bed.testzip():
            raise ValueError("Invalid ZIP member")
        geometry={}
        for name in bed.namelist():
            if name.endswith(".geo.json"):
                for mesh in read_json(bed,name)["minecraft:geometry"]:
                    geometry[mesh["description"]["identifier"]]=mesh
        icons=read_json(bed,"textures/item_texture.json")["texture_data"]
        seen=set()
        for base,items in rows["items"].items():
            for row in items:
                model=row["model"]
                if model!=row["bedrock_identifier"] or row["type"]!="definition" or model in seen:
                    raise ValueError(f"Conflicting definition {model}")
                seen.add(model)
                _,key=model.split(":")
                item=read_json(java,"assets/gtm/items/"+key+".json")["model"]
                name=item["model"].split(":")[1]
                mesh=read_json(java,"assets/gtm/models/"+name+".json")
                textures=mesh["textures"].copy()
                if not mesh.get("elements"):
                    parent=mesh["parent"].split(":")[1]
                    mesh=read_json(java,"assets/gtm/models/"+parent+".json")
                    textures={**mesh["textures"],**textures}
                for element in mesh["elements"]:
                    for face in element["faces"].values():
                        tex=textures[face["texture"].removeprefix("#")].split(":")[1]
                        java.getinfo("assets/gtm/textures/"+tex+".png")
                attach=read_json(bed,"attachables/"+key+".json")["minecraft:attachable"]["description"]
                identifier=attach["geometry"]["default"]
                if attach["identifier"]!=model or len(geometry[identifier]["bones"][0]["cubes"])!=len(mesh["elements"]):
                    raise ValueError(f"Client geometry mismatch {model}")
                bed.getinfo(attach["textures"]["default"]+".png")
                icon=icons[row["bedrock_options"]["icon"]]["textures"]+".png"
                with Image.open(io.BytesIO(bed.read(icon))) as img:
                    if not img.getbbox(): raise ValueError("Empty icon")
        if len(seen)!=count:
            raise ValueError(f"Expected {count} items, found {len(seen)}")
        print(f"{title}: {count} item, geometry, texture and icon references passed")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packs",type=Path)
    args=parser.parse_args()
    verify(args.packs,"Street_Kitchen","gtm_kitchen_mappings.json",30)
    verify(args.packs,"Finish_Studio","gtm_finish_mappings.json",300)
