"""Create a new public world ZIP with surveyed taxi and hospital pickup markings.

Only recolor existing road concrete. Keep the source ZIP as the rollback copy.
"""
import argparse
from collections import defaultdict
import hashlib
import os
from pathlib import Path
import struct
import tempfile
from zipfile import ZipFile
import zlib

from survey_world import Nbt, Survey

BASE_SHA256 = "214a00a08acdb5f73fea52ef79cdfdf773551086d31f5f95725f559ad0802dc2"
REGIONS = "world/dimensions/minecraft/overworld/region/"


def markings():
    result = {}
    # Two white L-shaped bay corners along the City Hall taxi lane.
    for x in (12, 18):
        for z in (2, 3):
            result[x,69,z] = "minecraft:white_concrete"
    for x in (13,14,16,17):
        result[x,69,3] = "minecraft:white_concrete"
    # Yellow stop box at the hospital kerb, with a gap for the ambulance entrance.
    for z in (135,136,137,142,143,144):
        result[-61,64,z] = "minecraft:yellow_concrete"
    for z in (135,144):
        result[-60,64,z] = "minecraft:yellow_concrete"
    return result


def paint_region(raw, chunks):
    region = bytearray(raw)
    for (cx,cz), edits in chunks.items():
        index = 4*((cx%32)+32*(cz%32))
        offset = int.from_bytes(region[index:index+3], "big")*4096
        capacity = region[index+3]*4096
        size = struct.unpack_from(">I", region, offset)[0]
        if not offset or region[offset+4] != 2 or size+4 > capacity:
            raise ValueError("Unexpected chunk storage")
        chunk = bytearray(zlib.decompress(region[offset+5:offset+4+size]))
        nbt = Nbt(chunk).root()
        if (nbt["xPos"], nbt["zPos"]) != (cx,cz):
            raise ValueError("Unexpected chunk position")
        by_y = defaultdict(list)
        for pos, color in edits:
            by_y[pos[1]//16].append((pos,color))
        for sy, section_edits in by_y.items():
            state = next(s["block_states"] for s in nbt["sections"] if s["Y"] == sy)
            words = list(state["data"])
            original = struct.pack(f">{len(words)}Q", *words)
            start = chunk.find(original)
            if start < 0 or chunk.count(original) != 1:
                raise ValueError("Ambiguous block array")
            palette = state["palette"]
            bits = max(4,(len(palette)-1).bit_length())
            width = 64//bits
            for (x,y,z), color in section_edits:
                idx = (y%16)*256+(z%16)*16+x%16
                word, shift = idx//width, (idx%width)*bits
                mask = (1<<bits)-1
                old = palette[(words[word]>>shift)&mask]
                if old != {"Name":"minecraft:gray_concrete"}:
                    raise ValueError(f"Road preimage changed at {x,y,z}")
                new = palette.index({"Name":color})
                words[word] = (words[word] & ~(mask<<shift)) | (new<<shift)
            chunk[start:start+len(original)] = struct.pack(f">{len(words)}Q", *words)
        compressed = zlib.compress(chunk)
        payload = struct.pack(">IB",len(compressed)+1,2)+compressed
        if len(payload)>capacity:
            raise ValueError("Replacement exceeds existing chunk allocation")
        region[offset:offset+capacity] = payload.ljust(capacity,b"\0")
    return bytes(region)


def apply(source, dest):
    with source.open("rb") as reader:
        if hashlib.file_digest(reader,"sha256").hexdigest() != BASE_SHA256:
            raise ValueError("This patch requires the published world snapshot")
    if dest.exists():
        raise FileExistsError(dest)
    edits = markings()
    groups = defaultdict(lambda:defaultdict(list))
    for pos, color in edits.items():
        x,y,z = pos
        groups[f"{REGIONS}r.{x//512}.{z//512}.mca"][x//16,z//16].append((pos,color))
    dest.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
        candidate = Path(tmp)/"world.zip"
        with ZipFile(source) as before, ZipFile(candidate,"w") as after:
            survey = Survey(before)
            for x,y,z in edits:
                if any(survey.block(x,k,z) != "minecraft:air" for k in (y+1,y+2)):
                    raise ValueError(f"Occupied road at {x,y,z}")
            for info in before.infolist():
                data = before.read(info)
                if info.filename in groups:
                    data = paint_region(data,groups[info.filename])
                after.writestr(info,data)
        with ZipFile(candidate) as check, ZipFile(source) as before:
            survey = Survey(check)
            for pos, color in edits.items():
                if survey.block(*pos) != color:
                    raise ValueError(f"Readback mismatch at {pos}")
            if check.testzip() or check.namelist() != before.namelist():
                raise ValueError("World verification failed")
            for name in check.namelist():
                if name not in groups and check.read(name) != before.read(name):
                    raise ValueError(f"Unexpected change in {name}")
        os.link(candidate, dest)
    print(f"Verified {len(edits)} concrete changes in {len(groups)} regions. Original retained.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("published_world",type=Path)
    parser.add_argument("new_world",type=Path)
    args = parser.parse_args()
    apply(args.published_world,args.new_world)
