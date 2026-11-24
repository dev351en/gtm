"""Export the 479 non-food city models and validate all 509 three-dimensional silhouettes."""
import argparse
from collections import Counter
from pathlib import Path

from build_food_packs import write_models
from city_furniture import furniture
from city_festival_art import festival
from city_item_art import objects
from city_transport_art import transport
from food_art import recipes


def catalogue():
    result={k:("furniture",*v) for k,v in furniture().items()}
    for collection in (transport(),festival(),objects()):
        if result.keys() & collection.keys(): raise ValueError("Overlapping city model ids")
        result.update(collection)
    return result


def build(dest):
    city=catalogue()
    all_models={**city,**{k:("food",k,v) for k,v in recipes().items()}}
    expected={"furniture":200,"road":65,"rail":10,"marine":8,"helicopter":4,"festival":100,
              "protection":55,"civic":20,"food":30,"entertainment":10,"effect":5,"property":2}
    if Counter(data[0] for data in all_models.values()) != expected:
        raise ValueError("Model category counts disagree with the specification")
    shapes={}
    for key,(_,_,parts) in all_models.items():
        shape=tuple(sorted(tuple(round(v,3) for v in part[1:]) for part in parts))
        if shape in shapes: raise ValueError(f"Repeated mesh for {key} and {shapes[shape]}")
        shapes[shape]=key
    write_models(dest,{k:v[2] for k,v in city.items()},{k:v[1] for k,v in city.items()},
                 "City_Collection","minecraft:paper","57a301a2-3c3f-4d99-880f-2dd16f565775",
                 "11de542d-7ecc-4aec-bc1a-28aa21d92c92","gtm_city_mappings.json")
    table="".join(f"{key}\t{category}\t{name}\n" for key,(category,name,_) in sorted(city.items()))
    (dest/"gtm-city-models.tsv").write_text(table,encoding="utf-8")
    print("Verified 509 distinct coordinate meshes across all 12 categories.")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    build(parser.parse_args().output)
