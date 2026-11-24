"""Original native-128 procedural materials for the Indraprastha art profile.

This extends the repository's code-authored texture system. All motifs are drawn
on the 128 grid; no legacy PNG is loaded, enlarged, or relabelled as native art.
"""
import hashlib
import math
import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont

SIZE = 128
PALETTE = {"graphite":"#151B20", "gold":"#D6AD59", "emerald":"#236653", "sandstone":"#D2B997", "terracotta":"#AD5637"}

def rgb(c):
    return ImageColor.getrgb(c) if isinstance(c, str) else tuple(c[:3])

def tone(c, scale=1, lift=0):
    return tuple(max(0,min(255,round(v*scale+lift))) for v in rgb(c))

def tile(name, colour, kind, idx=0):
    """Return uint8 RGBA native-128 tile with stable structural detail."""
    seed = int.from_bytes(hashlib.sha256((name+':'+str(idx)).encode()).digest()[:8], 'big')
    rng = np.random.default_rng(seed)
    c=rgb(colour); dark=tone(c,.64); mid=tone(c,.88); hi=tone(c,1.12,7); shine=tone(c,1.22,16)
    im=Image.new('RGBA',(128,128),c+(255,)); d=ImageDraw.Draw(im)
    def rect(b,fill,outline=None,width=1): d.rectangle(b,fill=fill,outline=outline,width=width)
    def line(p,fill,width=1): d.line(p,fill=fill,width=width)
    def rim(b=(1,1,126,126), thick=2):
        x,y,x2,y2=b; line((x,y,x2,y),hi,thick); line((x,y,x,y2),hi,thick)
        line((x,y2,x2,y2),dark,thick); line((x2,y,x2,y2),dark,thick)
    def screws():
        for x,y in ((7,7),(120,7),(7,120),(120,120)):
            d.ellipse((x-3,y-3,x+3,y+3),fill=dark);d.ellipse((x-2,y-2,x+2,y+2),fill=hi);line((x-1,y,x+1,y),mid)
    def text(x,y,t,fill,size=11):
        try:f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',size)
        except OSError:f=ImageFont.load_default()
        d.text((x,y),t,font=f,fill=fill,stroke_width=0)
    # Each material family has coherent construction-scale features and fine seams.
    if kind in ('wood','wood_v','bark','planks','log','log_top'):
        for y in range(0,128,32):
            rect((0,y,127,y+31),tone(c,.91+(y//32%3)*.045));line((0,y,127,y),dark,2);line((0,y+2,127,y+2),hi)
            seam=24+(y//32*29)%80;line((seam,y,seam,y+31),dark,2);line((seam+2,y,seam+2,y+31),hi)
            for gy in range(y+6,min(y+31,128),7):
                points=[(x,gy+round(1.7*math.sin((x+seed%23)/15))) for x in range(128)]
                line(points,tone(c,.78 if gy%2 else 1.08),1)
            for x in (6,120):rect((x,y+7,x+1,y+8),dark)
        if kind in ('wood_v','bark','log'):im=im.transpose(Image.Transpose.ROTATE_90);d=ImageDraw.Draw(im)
        if kind=='bark':
            for x in range(4,128,11):line([(x+(y//19)%3,y) for y in range(128)],dark,2)
        if kind=='log_top':
            for r in range(8,88,8):d.ellipse((64-r,64-r,64+r,64+r),outline=tone(c,.72+(r//8%2)*.27),width=2)
    elif kind in ('bricks','brick','cobble','polished','stone','dirt','sand','gravel'):
        if kind in ('bricks','brick'):
            rect((0,0,127,127),tone(c,.56))
            for row,y in enumerate(range(-1,128,24)):
                for col,x in enumerate(range(-48 if row%2 else 0,128,48)):
                    cc=tone(c,.9+((row*7+col*3)%5)*.025)
                    rect((x+2,y+2,x+46,y+22),cc);line((x+3,y+3,x+45,y+3),hi);line((x+3,y+3,x+3,y+21),hi);line((x+3,y+21,x+45,y+21),mid)
        elif kind=='cobble':
            rect((0,0,127,127),dark)
            for y in range(-8,128,25):
                for x in range(-16 if y%2 else 0,128,30):
                    dx=int(rng.integers(-4,5)); dy=int(rng.integers(-3,4));cc=tone(c,float(rng.choice([.85,.92,1.,1.04])))
                    poly=[(x+3+dx,y+2+dy),(x+24+dx,y+1+dy),(x+28+dx,y+8+dy),(x+26+dx,y+20+dy),(x+5+dx,y+23+dy),(x+1+dx,y+15+dy)]
                    d.polygon(poly,fill=cc);line(poly[:3],hi,1);line(poly[3:]+[poly[0]],mid,1)
        else:
            # Deterministic connected clusters, not pixel noise.
            for i in range(36 if kind!='polished' else 12):
                x,y=rng.integers(2,124,2);w,h=rng.integers(2,7,2)
                rect((int(x),int(y),int(min(127,x+w)),int(min(127,y+h))),tone(c,float(rng.choice([.93,.97,1.025]))))
            if kind=='polished':rim(thick=1)
    elif kind in ('fabric','carbon','mesh','tread'):
        if kind=='fabric':
            for y in range(0,128,4):line((0,y,127,y),mid)
            for x in range(0,128,4):line((x,0,x,127),tone(c,1.04))
            for x in range(7,124,7):line((x,4,x+3,4),hi);line((x,122,x+3,122),dark)
            line((3,0,3,127),dark);line((124,0,124,127),hi)
        elif kind=='tread':
            for y in range(-20,150,18):
                for x in range(0,128,32):
                    d.polygon([(x,y),(x+12,y+7),(x+25,y+2),(x+25,y+8),(x+12,y+13),(x,y+6)],fill=dark)
                    line((x+2,y+1,x+12,y+6,x+24,y+2),hi)
            for x in (5,121):line((x,0,x,127),dark,3)
        else:
            for y in range(0,128,8):
                for x in range(0,128,8):
                    if kind=='mesh':rect((x+2,y+2,x+5,y+5),dark);line((x+1,y+1,x+6,y+1),hi)
                    else:rect((x,y,x+6,y+3),hi if (x//8+y//8)%2 else dark);rect((x+3,y+4,x+6,y+7),mid)
    elif kind in ('glass','water'):
        rect((0,0,127,127),c+(165 if kind=='glass' else 255,))
        if kind=='glass':
            d.polygon([(0,0),(38,0),(128,90),(128,128)],fill=hi+(145,));d.polygon([(48,0),(56,0),(128,72),(128,80)],fill=shine+(190,));rim(thick=2)
        else:
            for y in range(8,128,16):
                for x in range((y//16%2)*12,128,40):line((x,y,x+18,y),hi,2);line((x+7,y+3,x+24,y+3),mid,2)
    elif kind in ('leaves','grass','grass_side'):
        for y in range(-8,128,16):
            for x in range(-8,128,16):
                xx=x+int(rng.integers(-4,5)); yy=y+int(rng.integers(-4,5));col=tone(c,float(rng.choice([.8,.94,1.08,1.15])))
                d.polygon([(xx,yy+7),(xx+7,yy),(xx+15,yy+4),(xx+16,yy+10),(xx+8,yy+15),(xx+1,yy+13)],fill=col);line((xx+3,yy+10,xx+12,yy+5),hi)
    elif kind=='hazard':
        for k in range(-128,256,40):d.polygon([(k,0),(k+18,0),(k-110,128),(k-128,128)],fill=(24,28,33))
        rim(thick=2);screws()
    elif kind.startswith('food_'):
        if kind in ('food_rice','food_grain','food_bread'):
            for i in range(200 if kind=='food_rice' else 80):
                x,y=rng.integers(3,125,2);col=tone(c,float(rng.choice([.84,.95,1.09])))
                if kind=='food_rice':line((int(x),int(y),int(x+3),int(y+1)),col,2)
                else:d.ellipse((int(x),int(y),int(x+2),int(y+2)),fill=col)
        elif kind=='food_leaf':
            for x in range(-64,192,20):line((64,64,x,0),hi,2);line((64,64,x,128),dark,2)
        elif kind=='food_sauce':
            for i in range(25):
                x,y=rng.integers(5,120,2);d.ellipse((int(x),int(y),int(x+5),int(y+3)),fill=hi)
        else:rim(thick=3)
    else:
        # Paint/metal substrates use broad discrete highlight bands and tiny joinery.
        for k in range(8):rect((0,k*16,127,k*16+15),tone(c,1.07-k*.018))
        rim(thick=2)
        if kind in ('metal','chrome'):screws()
        if kind=='chrome':
            d.polygon([(0,0),(31,0),(127,96),(127,122)],fill=shine);line((4,1,127,124),hi,2)
        if kind=='weapon_slide':
            for x in range(83,116,6):rect((x,18,x+2,109),dark);line((x+3,18,x+3,109),hi)
            line((13,8,109,8),shine,2)
    # Native per-face graphic treatments are laid on top of these substrates.
    d=ImageDraw.Draw(im)
    if kind in ('detail_headlight','headlight','detail_taillight','taillight','lamp_blue','lamp_amber'):
        rect((4,15,123,112),(29,36,43));rect((8,19,119,108),c);rim((8,19,119,108),2)
        for x in range(15,116,7):line((x,25,x,102),hi)
        for y in range(28,100,9):line((12,y,115,y),mid)
        rect((18,28,107,33),shine);rect((18,96,107,100),dark)
    elif kind.startswith('detail_grille'):
        rect((0,0,127,127),(18,25,31));
        for y in range(8,124,11):rect((7,y,120,y+4),(166,181,190) if 'chrome' in kind else (63,74,82));line((8,y,119,y),(218,228,230) if 'chrome' in kind else (80,91,98))
        rect((52,49,75,72),(21,27,32));d.polygon([(57,65),(62,55),(68,65),(62,61)],fill=(214,173,89))
    elif kind=='detail_windshield':
        rect((0,0,127,127),(20,30,38));d.polygon([(10,4),(117,4),(124,117),(3,117)],fill=(38,74,91));d.polygon([(19,9),(38,9),(112,111),(93,111)],fill=(74,112,124));line((8,109,62,76),dark,3);line((65,109,116,76),dark,3)
        for x in (5,122):line((x,10,x,115),(171,185,186),2)
    elif kind.startswith('door_'):
        rect((3,3,124,124),c);rim((3,3,124,124),2);line((5,41,122,41),dark,2);rect((82,49,108,54),(156,169,172));line((8,109,119,109),dark,3)
        if kind=='door_taxi':rect((4,69,123,88),(222,167,44));text(25,71,'CITY TAXI',(21,27,32),12)
        elif kind=='door_police':rect((4,67,123,89),(217,226,230));text(32,69,'SDPD',(23,39,66),17)
        elif kind=='door_amb':rect((4,68,123,81),(184,42,39));rect((52,47,75,94),(235,241,236));rect((59,51,68,91),(188,40,38));rect((54,66,73,76),(188,40,38))
        elif kind=='door_train':rect((4,6,123,92),(101,125,130));line((63,4,63,123),dark,3);rect((13,17,52,66),(42,78,93));rect((74,17,113,66),(42,78,93));text(20,100,'IP TRANSIT',dark,10)
    elif kind=='wheel_side':
        rect((0,0,127,127),(26,31,35));d.ellipse((3,3,124,124),fill=(38,43,46),outline=(11,16,21),width=4);d.ellipse((22,22,105,105),fill=c,outline=hi,width=3)
        for k in range(8):
            a=k*math.pi/4;px=64+round(math.cos(a)*34);py=64+round(math.sin(a)*34);line((64,64,px,py),dark,8);line((64,62,px,py-2),hi,3)
        d.ellipse((51,51,76,76),fill=dark,outline=hi,width=2)
    elif kind=='plate':
        rect((0,0,127,127),(220,226,217));rect((3,34,124,92),(244,241,218),outline=(29,40,46),width=3);rect((6,38,17,88),(26,77,133));text(23,49,'IP 01',(22,30,35),20);text(26,72,'SD CRAFT',(22,30,35),9)
    elif kind in ('detail_ecg','detail_atm','detail_pc'):
        rect((4,4,123,123),(19,26,31));rect((10,12,117,108),(24,44,52));rect((10,12,117,24),(35,102,83));text(15,14,'JEEVA' if kind=='detail_ecg' else 'ARK', (228,220,192),8)
        if kind=='detail_ecg':
            for y in range(36,100,12):line((12,y,115,y),(31,62,65))
            line([(12,66),(30,66),(37,60),(43,72),(49,43),(55,88),(62,60),(69,66),(115,66)],(108,222,165),2);text(79,34,'72',(214,173,89),17)
        else:
            for y in (35,53,71):rect((17,y,58,y+10),(53,86,89));rect((66,y,108,y+10),(93,119,117))
            rect((22,112,106,116),(90,108,108))
    elif kind=='detail_bookshelf':
        rect((0,0,127,127),(87,49,27))
        cols=['#236653','#AD5637','#D2B997','#23435A','#86683F','#6B343A']
        for row in range(3):
            y=row*42
            for j,x in enumerate(range(5,124,12)):
                height=25+(j*7+row*5)%10;rect((x,y+39-height,x+9,y+36),rgb(cols[(j+row)%6]));line((x+1,y+14,x+1,y+34),hi);rect((x+3,y+24,x+6,y+25),(210,185,146))
            rect((0,y+38,127,y+41),(147,100,51));line((0,y+38,127,y+38),(187,140,82))
    elif kind in ('detail_drawer','detail_stove','detail_speaker','detail_mandir'):
        if kind=='detail_drawer':
            for y in (4,45,86):rect((4,y,123,y+36),c,outline=dark,width=2);rect((49,y+13,78,y+17),(210,178,115));line((5,y+2,120,y+2),hi)
        elif kind=='detail_stove':
            rect((7,32,120,116),(31,38,44));rect((16,43,111,105),(45,59,66));line((20,48,105,48),(113,138,143),2)
            for x in (23,51,79,107):d.ellipse((x-7,8,x+7,22),fill=dark,outline=hi,width=2)
        elif kind=='detail_speaker':
            rect((3,3,124,124),(23,29,33));
            for r in (49,44,30,17):d.ellipse((64-r,64-r,64+r,64+r),outline=(57+r,61+r,63+r),width=2)
            for y in range(10,121,6):
                for x in range(10,121,6):d.point((x,y),fill=(16,23,29))
        else:
            for x in range(-128,256,16):line((x,0,x-128,128),hi,3);line((x,0,x+128,128),dark,3)
            rim((2,2,125,125),4)
    elif kind in ('hero_cross','hero_jerry','hero_bills','hero_card','detail_muzzle'):
        if kind=='hero_cross':rect((51,23,76,105),(244,240,224));rect((24,51,104,77),(244,240,224))
        elif kind=='hero_jerry':line((20,20,107,107),dark,6);line((107,20,20,107),dark,6);line((24,20,108,104),hi,2);rim((12,12,115,115),3)
        elif kind=='hero_bills':
            rect((6,6,121,121),None,outline=hi,width=2);rect((48,0,80,127),(214,173,89));text(51,51,'ARK',(50,48,34),12)
        elif kind=='hero_card':
            rect((17,47,45,72),(214,173,89));line((20,59,42,59),dark);line((31,49,31,70),dark);text(16,15,'ARK',(214,173,89),18);text(15,96,'INDRAPRASTHA',(210,185,151),8)
        else:
            for r,co in ((47,hi),(39,dark),(28,(8,15,20))):d.ellipse((64-r,64-r,64+r,64+r),fill=co)
    elif kind in ('detail_toran','detail_rangoli','glowstone','sea_lantern'):
        if kind=='detail_toran':
            line([(x,22+round(10*math.sin(x/128*math.pi))) for x in range(128)],(35,102,83),3)
            for x in range(10,128,18):d.polygon([(x,31),(x+8,31),(x+4,70)],fill=(214,173,89));d.ellipse((x,61,x+8,70),fill=(235,129,42))
        elif kind=='detail_rangoli':
            for k in range(8):
                a=k*math.pi/4;x=64+round(math.cos(a)*31);y=64+round(math.sin(a)*31);d.ellipse((x-13,y-13,x+13,y+13),fill=(214,173,89),outline=(235,214,168),width=2)
            d.ellipse((48,48,80,80),fill=(35,102,83),outline=(244,226,182),width=2)
        else:
            for y in range(4,128,24):
                for x in range(4,128,24):rect((x,y,x+18,y+18),shine);rect((x+2,y+2,x+15,y+15),hi)
    return np.array(im,dtype=np.uint8)
