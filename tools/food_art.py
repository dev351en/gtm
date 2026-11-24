"""Original voxel recipes. A part is (palette swatch, x, y, z, width, height, depth)."""
PALETTE = {
    "steel": "#8aa2aa", "rim": "#d0dede", "clay": "#aa5237", "terra": "#d77e4d",
    "cream": "#f3dea8", "milk": "#fff2d7", "crust": "#bf702e", "bread": "#e4a74b",
    "toast": "#8c4727", "gold": "#ffbd3e", "gravy": "#bc4e23", "chilli": "#d4382c",
    "leaf": "#347043", "mint": "#84aa48", "pink": "#dd7e82", "rice": "#f2e8bc",
    "bean": "#713d31", "saffron": "#efa328", "violet": "#7e405d", "ice": "#c4eae9"
}


def plate():
    return [("steel",2,1,3,12,1,10),("rim",3,1,2,10,1,1),("rim",3,1,13,10,1,1)]


def bowl(base, filling):
    return [(base,4,1,4,8,1,8),(base,3,2,3,10,2,10),(filling,4,4,4,8,1,8)]


def cup(base, filling, tall, handle=False):
    parts = [(base,6,1,6,4,1,4),(base,5,2,5,6,tall,6),(filling,5.5,2+tall,5.5,5,.5,5)]
    if handle:
        parts += [(base,11,3,7,2,1,2),(base,12,4,7,1,2,2),(base,11,6,7,2,1,2)]
    return parts


def bun(x,z, filling):
    return [("bread",x,2,z,5,1,5),(filling,x,3,z,5,2,5),("crust",x,5,z,5,1,5),("bread",x+1,6,z,3,1,5)]


def dumpling(x,z,color):
    return [(color,x,2,z,4,2,4),(color,x+1,4,z+1,2,1,2)]


def cubes(points, color, size=1, y=5):
    return [(color,x,y,z,size,1,size) for x,z in points]


def recipes():
    p = plate()
    return {
        "chai": cup("clay","toast",5,True),
        "vada_pav": p + bun(5,5,"gold") + [("leaf",4,4,6,7,1,2)],
        "samosa": p + [("crust",4,2,5,8,2,6),("bread",5,4,6,6,2,4),("gold",6,6,7,4,2,2),("crust",7,8,7,2,1,1)],
        "dabeli": p + bun(5,5,"gravy") + cubes([(5,5),(7,6),(9,5)],"pink",1,5),
        "pav_bhaji": p + bun(3,5,"bread") + [("clay",9,2,5,4,2,6),("gravy",9,4,5,4,1,6),("cream",10,5,7,2,1,2)],
        "dosa": p + [("bread",3,2,6,10,2,5),("gold",3,4,7,10,1,3),("toast",3,3,7,1,1,3),("leaf",3,2,3,4,1,2)],
        "idli": p + dumpling(3,4,"milk") + dumpling(8,7,"milk") + [("gravy",3,2,10,3,1,2)],
        "thali": p + [("rice",3,2,4,4,2,4),("bread",3,2,9,5,1,3),("gravy",9,2,4,3,2,3),("gold",9,2,9,3,2,3),("leaf",8,2,7,2,1,2)],
        "biryani": bowl("clay","rice") + cubes([(5,5),(8,8),(10,5)],"saffron",2) + cubes([(6,9),(10,10)],"mint"),
        "lassi": cup("steel","milk",8) + [("pink",7,10.5,7,2,1,2)],
        "dhokla": p + [("gold",3,2,4,4,3,4),("gold",8,2,7,4,3,4)] + cubes([(4,5),(9,8)],"mint"),
        "khandvi": p + [("gold",x,2,4,2,2,7) for x in (4,7,10)] + cubes([(4,6),(7,8),(10,5)],"leaf",1,4),
        "poha": bowl("leaf","gold") + cubes([(5,5),(9,7),(7,10)],"bean") + [("cream",9,5,9,3,1,2)],
        "misal": bowl("steel","gravy") + cubes([(5,6),(8,9),(10,7)],"gold",2) + cubes([(7,5),(5,10)],"pink"),
        "upma": bowl("rim","cream") + cubes([(5,5),(7,9)],"terra",2) + cubes([(9,7),(6,10)],"mint"),
        "puran_poli": p + [("toast",3,2,5,10,1,6),("bread",4,3,4,8,1,8),("cream",7,4,7,2,1,2)],
        "bhakri": p + [("toast",3,2,5,10,1,6),("cream",4,2,4,8,1,8),("leaf",3,3,8,4,1,1),("gravy",10,3,5,2,1,2)],
        "thepla": p + [("gold",3,2,5,9,1,7),("bread",4,3,4,9,1,7)] + cubes([(5,5),(7,8),(10,7)],"leaf",1,4),
        "modak": p + dumpling(6,6,"milk") + [("cream",7,5,7,2,2,2),("milk",7,7,7,1,1,1)],
        "jalebi": p + [("saffron",4,2,4,8,1,2),("saffron",10,2,6,2,1,6),("saffron",4,2,10,6,1,2),("saffron",4,2,6,2,1,4),("gold",6,2,7,3,1,2)],
        "kulfi": [("toast",7,1,7,2,4,2),("cream",5,5,5,6,6,6),("gold",6,11,6,4,2,4),("mint",6,9,4.8,1,1,.3)],
        "falooda": cup("pink","milk",8) + [("pink",6,10.5,6,3,2,3),("chilli",7,12.5,7,1,1,1),("cream",10,9,8,1,5,1)],
        "nimbu_pani": cup("ice","cream",7) + [("gold",9,8,4,3,3,1),("mint",6,9.5,6,2,1,2)],
        "filter_coffee": [("rim",3,1,3,10,1,10)] + [(c,x,y+1,z,w,h,d) for c,x,y,z,w,h,d in cup("steel","toast",4)],
        "kathi_roll": p + [("bread",4,2,5,8,3,5),("cream",6,2,5,4,3.1,5),("chilli",12,3,6,1,1,2),("leaf",3,3,7,1,1,2)],
        "pani_puri": p + sum((dumpling(x,z,"bread") for x,z in [(3,4),(8,4),(6,9)]),[]) + cubes([(4,5),(9,5),(7,10)],"leaf"),
        "sev_puri": p + [("bread",x,2,z,4,1,4) for x,z in [(3,4),(8,8)]] + cubes([(4,5),(9,9)],"gravy",2,3) + cubes([(4,5),(10,10)],"gold",1,4),
        "ragda": bowl("terra","cream") + cubes([(5,6),(8,8)],"crust",3) + cubes([(6,7),(9,9)],"leaf",1,6),
        "sandesh": p + [("milk",4,2,4,5,2,4),("milk",8,2,9,4,2,3),("mint",6,4,5,1,1,2),("saffron",9,4,10,2,1,1)],
        "sheera": bowl("clay","gold") + [("cream",5,5,6,3,1,1),("cream",8,5,8,1,1,3),("bean",9,5,5,2,1,2)]
    }
