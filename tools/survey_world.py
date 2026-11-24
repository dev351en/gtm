"""Read modern Java Anvil block palettes at the published GTM service sites."""
import argparse
from functools import lru_cache
import io
import json
import math
from pathlib import Path
import struct
import zipfile
import zlib

import yaml


class Nbt:
    def __init__(self, data):
        self.stream = io.BytesIO(data)

    def number(self, fmt):
        return struct.unpack(">" + fmt, self.stream.read(struct.calcsize(">" + fmt)))[0]

    def string(self):
        return self.stream.read(self.number("H")).decode("utf-8", errors="replace")

    def value(self, tag):
        if tag in range(1, 7):
            return self.number("bhiqfd"[tag - 1])
        if tag == 8:
            return self.string()
        if tag == 10:
            obj = {}
            while kind := self.number("B"):
                key = self.string()
                obj[key] = self.value(kind)
            return obj
        if tag == 9:
            kind = self.number("B")
            return [self.value(kind) for _ in range(self.number("i"))]
        if tag in (7, 11, 12):
            count = self.number("i")
            code = {7: "B", 11: "i", 12: "Q"}[tag]
            size = struct.calcsize(">" + code)
            return struct.unpack(f">{count}{code}", self.stream.read(count * size))
        raise ValueError(f"Unsupported NBT tag {tag}")

    def root(self):
        tag = self.number("B")
        self.string()
        return self.value(tag)


class Survey:
    def __init__(self, archive):
        self.archive = archive

    @lru_cache(maxsize=4)
    def region(self, rx, rz):
        name = f"world/dimensions/minecraft/overworld/region/r.{rx}.{rz}.mca"
        return self.archive.read(name)

    @lru_cache(maxsize=64)
    def chunk(self, cx, cz):
        raw = self.region(cx // 32, cz // 32)
        idx = 4 * ((cx % 32) + 32 * (cz % 32))
        offset = int.from_bytes(raw[idx:idx+3], "big") * 4096
        if not offset:
            raise ValueError(f"Missing chunk {cx},{cz}")
        size = struct.unpack_from(">I", raw, offset)[0]
        if raw[offset+4] != 2:
            raise ValueError("Unsupported region compression")
        chunk = Nbt(zlib.decompress(raw[offset+5:offset+4+size])).root()
        if (chunk["xPos"], chunk["zPos"]) != (cx, cz):
            raise ValueError("Chunk coordinates disagree with header")
        return {s["Y"]: s["block_states"] for s in chunk["sections"] if "block_states" in s}

    def block(self, x, y, z):
        state = self.chunk(x // 16, z // 16).get(y // 16)
        if state is None:
            raise ValueError("Section missing")
        palette = state["palette"]
        index = 0
        if len(palette) > 1:
            bits = max(4, (len(palette) - 1).bit_length())
            per_word = 64 // bits
            pos = (y % 16) * 256 + (z % 16) * 16 + x % 16
            word = state["data"][pos // per_word]
            index = (word >> ((pos % per_word) * bits)) & ((1 << bits) - 1)
        return palette[index]["Name"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("world_zip", type=Path)
    parser.add_argument("sites", type=Path)
    args = parser.parse_args()
    sites = yaml.safe_load(args.sites.read_text())["sites"]
    with zipfile.ZipFile(args.world_zip) as archive:
        survey = Survey(archive)
        report = {}
        for name, site in sites.items():
            if site["world"] != "world":
                continue
            x, y, z = (math.floor(site[k]) for k in ("x", "y", "z"))
            report[name] = {"position": [x, y, z],
                            "floor_feet_head": [survey.block(x, h, z) for h in (y-1, y, y+1)]}
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
