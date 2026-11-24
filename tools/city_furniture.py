"""Indraprastha furnishings drawn in 16-unit item space. Dimensions are model units."""
from itertools import product

STYLES = ("Irani", "Deccan", "Konkan", "Art Deco", "Metro")
# Primary, secondary and accent swatches. Styles also change the construction.
FINISH = (("toast","cream","terra"),("clay","gold","leaf"),("leaf","bread","cream"),
          ("steel","violet","gold"),("steel","rim","chilli"))


def furniture():
    designs = {}
    groups = {
        "seat": ["canteen_stool","cafe_chair","platform_bench","reading_chair","waiting_sofa","bar_stool","park_settee","clinic_chair"],
        "table": ["chai_table","study_desk","dining_table","workbench","reception_desk","market_counter","coffee_table","drafting_table"],
        "storage": ["bookcase","locker","wardrobe","filing_cabinet","display_case","pantry","bedside_chest","shoe_rack"],
        "fixture": ["ward_bed","exam_couch","salon_recliner","daybed","platform_trolley","porter_cart","luggage_rack","tea_cart"],
        "appliance": ["radio_console","ticket_machine","fridge","oven","water_cooler","washing_machine","juice_stall","news_kiosk"]
    }
    for group, names in groups.items():
        for k,name in enumerate(names):
            for style,label in enumerate(STYLES):
                primary,secondary,accent=FINISH[style]
                parts=[]
                def box(c,x,y,z,w,h,d):
                    parts.append((c,x,y,z,w,h,d))
                def supports(x,z,w,d,h):
                    if style==0:
                        for xx,zz in product((x,x+w-1),(z,z+d-1)):
                            box(primary,xx,1,zz,1,h,1)
                        box(accent,x,2,z,w,.6,.7)
                    elif style==1:
                        for xx in (x,x+w-2):
                            box(primary,xx,1,z,2,h,d)
                            box(accent,xx,1,z-.2,2,.75,d+.4)
                    elif style==2:
                        for zz in (z,z+d-1):
                            box(primary,x,1,zz,w,h,1)
                        box(secondary,x+w/2-.5,2,z,1,1,d)
                    elif style==3:
                        box(primary,x+w/2-1,1,z+d/2-1,2,h,2)
                        box(accent,x+1,1,z+1,w-2,.7,d-2)
                    else:
                        for xx in (x,x+w-1):
                            box(primary,xx,1,z,1,h,1)
                            box(primary,xx,1,z+d-1,1,h,1)
                            box(accent,xx,.6,z,1,.7,d)
                if group=="seat":
                    w,d,h=((5,5,5),(6,6,5),(13,5,5),(7,7,4),(13,8,4),(5,5,8),(12,6,4),(6,5,5))[k]
                    x,z=(16-w)/2,(16-d)/2
                    supports(x,z,w,d,h)
                    box(secondary,x-.3,h+1,z-.3,w+.6,1.2,d+.6)
                    if k not in (0,5):
                        back=(4,5,4,6,5,4,5,3)[k]
                        box(primary,x,h+2,z+d-1,w,back,1)
                        box(accent,x+.5,h+back+1,z+d-1.2,w-1,.6,.5)
                    if k in (3,4,6,7):
                        for xx in (x,x+w-1): box(primary,xx,h+2,z+1,1,2.2,d-2)
                    if k==5: box(accent,x-1,4,z+1,w+2,.6,1)
                elif group=="table":
                    w,d,h=((7,6,4),(10,6,6),(13,8,6),(12,7,7),(12,6,7),(13,6,6),(9,7,3),(10,8,6))[k]
                    x,z=(16-w)/2,(16-d)/2
                    supports(x+.5,z+.5,w-1,d-1,h)
                    box(secondary,x,h+1,z,w,1,d)
                    if k in (1,3): box(primary,x+.5,h-1,z+.5,3.5,2,d-1)
                    if k in (4,5): box(primary,x,h+2,z+d-1,w,2,1); box(accent,x,h+4,z+d-1,w,.5,1)
                    if k==7:
                        for j in range(3): box(primary,x,h+2+j*.6,z+2*j,w,1,2)
                elif group=="storage":
                    w,d,h=((10,5,11),(6,5,12),(10,6,12),(7,5,9),(11,5,9),(9,6,10),(5,5,5),(10,5,5))[k]
                    x,z=(16-w)/2,(16-d)/2
                    supports(x,z,w,d,2)
                    for xx in (x,x+w-1): box(primary,xx,3,z,1,h,d)
                    box(primary,x+1,3,z+d-.7,w-2,h,.7)
                    for yy in (3,3+h-.8): box(secondary,x+.7,yy,z,w-1.4,.8,d)
                    levels=3 if k in (0,3,5,7) else 2
                    for j in range(1,levels): box(secondary,x+1,3+j*h/levels,z,w-2,.65,d-.7)
                    if k in (1,2,3,6):
                        for j in range(levels):
                            box(secondary,x+1,3+j*h/levels+.35,z-.25,w-2,h/levels-.6,.65)
                            box(accent,x+w/2-1,3+(j+.55)*h/levels,z-.5,2,.5,.5)
                    if k==4: box("ice",x+1,4,z+.3,.45,h-2,d-1)
                elif group=="fixture":
                    w,d,h=((7,13,4),(6,12,6),(5,10,5),(8,12,3),(10,11,3),(6,10,3),(10,8,4),(8,8,5))[k]
                    x,z=(16-w)/2,(16-d)/2
                    supports(x,z,w,d,h)
                    box(secondary,x,h+1,z,w,1,d)
                    if k<4:
                        box("cream",x+.4,h+2,z+.3,w-.8,1.3,d-.6)
                        box(accent,x+1,h+3.3,z+d-3,w-2,.9,2)
                        box(primary,x,h+2,z+d-1,w,3 if k!=2 else 5,1)
                    else:
                        for xx in (x,x+w-1): box(primary,xx,h+2,z+d-1,1,5,1)
                        box(accent,x,h+7,z+d-1,w,1,1)
                        if k>=6: box(secondary,x,h+4,z,w,.7,d)
                else:
                    w,d,h=((9,5,5),(6,5,10),(7,6,11),(8,6,6),(5,5,7),(7,6,6),(10,6,6),(11,6,7))[k]
                    x,z=(16-w)/2,(16-d)/2
                    supports(x,z,w,d,2)
                    box(primary,x,3,z,w,h,d)
                    box(secondary,x+.5,3.5,z-.3,w-1,h-1,.5)
                    if k in (0,1,3,5):
                        box("steel",x+1,4,z-.6,w-2,h/2,.4)
                        box(accent,x+1,3+h-1.3,z-.7,1,.6,.4)
                    if k==2: box(accent,x+1,6,z-.8,.5,3,.7)
                    if k==4: box("ice",x+.5,3+h,z+.5,w-1,3,d-1);box(accent,x+1,6,z-.7,1,.6,.7)
                    if k>=6:
                        for xx in (x,x+w-1): box(primary,xx,h+3,z+d-1,1,4,1)
                        box(accent,x-.5,h+7,z-.5,w+1,1,d+1)
                key=name+"_"+label.lower().replace(" ","_")
                designs[key]=(name.replace("_"," ").title()+" · "+label,parts)
    return designs
