#!/usr/bin/env python3
"""Native 128px GTM UI/identity/signage assets; extends the existing creative catalogue.

This is an art-only deterministic exporter. It does not register items, assign live
world coordinates, install resource packs, or claim live client validation.
PNG and editable SVG are emitted from the same native-coordinate primitives.
Signs use two 128px tiles; their 256x128 composite is also supplied.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import re
import textwrap
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw, ImageFont, features

ROOT = Path(__file__).resolve().parents[1]
PALETTE = dict(graphite="#151B20", gold="#D6AD59", emerald="#236653", sandstone="#D2B997", terracotta="#AD5637", paper="#F2EBDD", dark="#0C1116", edge="#52616B", blue="#416D90", red="#C9574E")
G, AU, EM, SA, TC, WHITE = (PALETTE[k] for k in ["graphite","gold","emerald","sandstone","terracotta","paper"])
def resolve_font(filename):
    roots=[Path(os.environ.get("GTM128_FONT_DIR",".")),ROOT/"fonts",Path("/usr/share/fonts/truetype/dejavu"),Path("/usr/share/fonts/truetype/noto"),Path("C:/Windows/Fonts"),Path("/Library/Fonts")]
    for directory in roots:
        candidate=directory/filename
        if candidate.is_file():return candidate
    raise FileNotFoundError(f"{filename} is required; set GTM128_FONT_DIR to a directory with DejaVu Sans and Noto Sans Devanagari TTF files")

LATIN = resolve_font("DejaVuSans.ttf")
BOLD = resolve_font("DejaVuSans-Bold.ttf")
DEVA = resolve_font("NotoSansDevanagari-Regular.ttf")
DEVAB = resolve_font("NotoSansDevanagari-Bold.ttf")

def font(size=14, bold=False, text=""):
    devanagari = any("\u0900" <= x <= "\u097f" for x in text)
    p = (DEVAB if bold else DEVA) if devanagari else (BOLD if bold else LATIN)
    return ImageFont.truetype(str(p), max(5,int(size)), layout_engine=ImageFont.Layout.RAQM)

def rgba(v):
    if v is None: return None
    if isinstance(v, tuple): return v
    return v

class Canvas:
    def __init__(self,w=128,h=128,bg=(0,0,0,0),shared=None,ox=0,oy=0,s=1):
        self.w,self.h,self.ox,self.oy,self.s=w,h,ox,oy,s
        if shared:
            self.im,self.d,self.svg=shared
        else:
            self.im=Image.new("RGBA",(w,h),bg); self.d=ImageDraw.Draw(self.im); self.svg=[]
            if isinstance(bg,str): self.r(0,0,w,h,bg)
    def group(self,x=0,y=0,s=1):
        return Canvas(self.w,self.h,shared=(self.im,self.d,self.svg),ox=self.ox+x*self.s,oy=self.oy+y*self.s,s=self.s*s)
    def pt(self,x,y): return (round(self.ox+x*self.s),round(self.oy+y*self.s))
    def style(self,fill,stroke,width):
        return f'fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{max(1,round(width*self.s))}" stroke-linejoin="miter"'
    def r(self,x,y,w,h,fill=None,stroke=None,lw=1):
        a,b=self.pt(x,y),self.pt(x+w,y+h)
        self.d.rectangle([a,(b[0]-1,b[1]-1)],fill=rgba(fill),outline=rgba(stroke),width=max(1,round(lw*self.s)))
        self.svg.append(f'<rect x="{a[0]}" y="{a[1]}" width="{b[0]-a[0]}" height="{b[1]-a[1]}" {self.style(fill,stroke,lw)}/>')
    def poly(self,pts,fill=None,stroke=None,lw=1):
        p=[self.pt(*a) for a in pts];self.d.polygon(p,fill=rgba(fill))
        if stroke:self.d.line(p+[p[0]],fill=stroke,width=max(1,round(lw*self.s)),joint="curve")
        self.svg.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in p)}" {self.style(fill,stroke,lw)}/>')
    def line(self,pts,color=WHITE,lw=3):
        p=[self.pt(*a) for a in pts];self.d.line(p,fill=color,width=max(1,round(lw*self.s)),joint="curve")
        self.svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in p)}" fill="none" stroke="{color}" stroke-width="{max(1,round(lw*self.s))}" stroke-linejoin="miter"/>')
    def c(self,x,y,r,fill=None,stroke=None,lw=1):
        a,b=self.pt(x-r,y-r),self.pt(x+r,y+r)
        self.d.ellipse([a,b],fill=rgba(fill),outline=rgba(stroke),width=max(1,round(lw*self.s)))
        xx,yy=self.pt(x,y);rr=round(r*self.s)
        self.svg.append(f'<circle cx="{xx}" cy="{yy}" r="{rr}" {self.style(fill,stroke,lw)}/>')
    def arc(self,x,y,r,start,end,color=WHITE,lw=3):
        pts=[]
        for i in range(max(3,int(abs(end-start)/4))+1):
            a=math.radians(start+(end-start)*i/max(3,int(abs(end-start)/4)))
            pts.append((x+math.cos(a)*r,y+math.sin(a)*r))
        self.line(pts,color,lw)
    def text(self,x,y,t,size=14,color=WHITE,bold=False,anchor="la",maxw=None):
        # Text is shaped natively at output resolution using libraqm/HarfBuzz.
        n=max(5,round(size*self.s));f=font(n,bold,t)
        if maxw:
            while self.d.textlength(t,font=f)>maxw*self.s and n>5:
                n-=1;f=font(n,bold,t)
        pos=self.pt(x,y)
        devanagari = any("\u0900" <= v <= "\u097f" for v in t)
        # Noto Devanagari lacks U+2022 and ampersand; use actual Latin glyphs
        # for those runs instead of silently drawing a missing-glyph box.
        if devanagari and any(ch in t for ch in "•&"):
            runs=[r for r in re.split(r"([•&])",t) if r]
            fs=[font(n,bold,r) for r in runs]
            widths=[self.d.textlength(r,font=rf) for r,rf in zip(runs,fs)]
            dx=pos[0]-(sum(widths)/2 if anchor=="ma" else sum(widths) if anchor=="ra" else 0)
            for r,rf,ww in zip(runs,fs,widths):
                self.d.text((round(dx),pos[1]),r,font=rf,fill=color,anchor="la");dx+=ww
        else:self.d.text(pos,t,font=f,fill=color,anchor=anchor)
        family="Noto Sans Devanagari, DejaVu Sans" if devanagari else "DejaVu Sans"
        anch={"la":"start","ma":"middle","ra":"end"}.get(anchor,"start")
        # SVG text uses top anchor to mirror Pillow's ascender coordinate.
        self.svg.append(f'<text x="{pos[0]}" y="{pos[1]}" fill="{color}" font-family="{family}" font-size="{n}" font-weight="{700 if bold else 400}" text-anchor="{anch}" dominant-baseline="text-before-edge">{escape(t)}</text>')
    def save(self,stem:Path,title):
        stem.parent.mkdir(parents=True,exist_ok=True)
        self.im.save(stem.with_suffix(".png"),optimize=True)
        xml=f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" role="img"><title>{escape(title)}</title>'+"".join(self.svg)+"</svg>\n"
        stem.with_suffix(".svg").write_text(xml,encoding="utf-8")

def star(c,cx=64,cy=62,r=31,fill=AU,stroke=None,lw=2):
    p=[]
    for i in range(10):
        a=-math.pi/2+i*math.pi/5;rr=r if i%2==0 else r*.43
        p.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr))
    c.poly(p,fill,stroke,lw)

def shield(c,fill=AU):
    c.poly([(64,30),(92,40),(89,72),(79,88),(64,99),(49,88),(39,72),(36,40)],fill)
    c.poly([(64,37),(84,44),(82,70),(75,82),(64,91),(53,82),(46,70),(44,44)],G)

def ark(c,color=AU):
    # Original A-K monogram: A's right stem is the shared K upright.
    c.poly([(32,90),(53,36),(64,36),(64,90),(55,90),(55,73),(43,73),(37,90)],color)
    c.poly([(47,63),(55,63),(55,43)],G)
    c.poly([(64,62),(83,36),(96,36),(73,65),(97,90),(84,90),(64,70)],color)

def bridge(c,color=AU):
    c.r(30,46,5,39,color);c.r(90,46,5,39,color)
    c.line([(26,79),(101,79)],color,4)
    c.line([(21,75),(32,49),(62,76),(93,49),(108,75)],color,2)
    for x in [39,46,53,72,79,86]:
        c.line([(x,63-abs(62-x)*.3),(x,78)],color,1)
    c.line([(27,90),(44,93),(62,90),(80,93),(100,90)],SA,2)

def glyph(c,key,col=WHITE):
    """Distinct original silhouettes using the shared 128-pixel construction grid."""
    if key in {"search","quoggle"}:
        c.c(58,55,22,None,col,7);c.c(58,55,11,None,AU,2);c.poly([(73,69),(82,68),(101,91),(91,100)],col);c.r(44,43,4,10,AU)
    elif key in {"box","amazzo"}:
        c.poly([(32,46),(63,30),(97,46),(64,63)],AU);c.poly([(32,46),(64,63),(64,99),(32,82)],SA);c.poly([(64,63),(97,46),(97,82),(64,99)],col)
        c.line([(48,38),(80,55),(80,70)],G,4);c.line([(40,72),(54,79)],G,3)
    elif key in {"flippit","shopping"}:
        c.poly([(36,47),(90,47),(96,99),(30,99)],col);c.arc(63,45,17,180,360,AU,5)
        if key=="flippit":c.poly([(49,63),(78,63),(78,70),(59,70),(59,77),(73,77),(73,84),(59,84),(59,95),(49,95)],G)
        else:c.r(47,69,34,6,G);c.r(54,80,21,4,AU)
    elif key in {"ark","arkpay"}:ark(c,col)
    elif key in {"food","zomatoo"}:
        c.r(32,83,67,7,col);c.r(39,78,53,5,AU);c.arc(65,76,28,180,360,col,5);c.c(65,43,4,AU)
        c.line([(49,29),(46,35),(49,39)],SA,2);c.line([(78,26),(75,33),(78,38)],SA,2)
    elif key in {"delivery","swiffy"}:
        c.c(42,87,11,None,col,5);c.c(88,87,11,None,col,5);c.line([(42,86),(54,67),(77,67),(88,86)],col,5);c.line([(69,87),(78,57),(88,57)],col,4)
        c.r(33,43,28,22,AU);c.r(43,43,6,22,G);c.line([(17,55),(28,55)],SA,3);c.line([(22,64),(28,64)],SA,2)
    elif key in {"fashion","amora"}:
        c.arc(65,40,8,180,380,AU,4);c.line([(65,48),(32,74),(33,79),(96,79),(97,74),(65,51)],col,5);c.line([(51,84),(47,98),(82,98),(78,84)],AU,3)
    elif key in {"home","property","maya"}:
        c.poly([(26,59),(63,28),(102,59),(94,67),(64,42),(34,67)],col);c.r(39,60,49,39,col);c.r(59,73,13,26,G);c.r(44,68,9,9,AU);c.r(76,68,7,9,AU)
    elif key in {"car","taxi","sd_motors"}:
        c.poly([(31,69),(40,46),(86,46),(97,69),(99,92),(28,92)],col);c.poly([(43,51),(83,51),(89,67),(37,67)],G)
        c.r(33,74,13,7,AU);c.r(81,74,13,7,AU);c.r(51,78,25,5,G);c.r(33,91,10,9,AU);c.r(84,91,10,9,AU)
        if key=="taxi":c.r(52,35,24,9,AU);c.text(64,34,"TAXI",6,G,True,"ma")
    elif key in {"map","maps"}:
        c.poly([(27,44),(50,36),(77,44),(100,36),(100,92),(77,100),(50,92),(27,100)],SA)
        c.line([(50,38),(50,92)],G,2);c.line([(77,46),(77,98)],G,2);c.line([(35,85),(43,65),(68,72),(86,55)],EM,5)
        c.c(80,42,14,col);c.poly([(69,50),(80,68),(91,50)],col);c.c(80,42,5,G)
    elif key=="garage":
        c.poly([(25,53),(64,29),(103,53)],col);c.r(31,52,65,48,col);c.r(41,61,45,39,G)
        for y in [65,73,81]:c.line([(43,y),(84,y)],AU,3)
        c.r(59,88,11,4,col)
    elif key in {"bank","indra_bank"}:
        c.poly([(27,46),(64,27),(101,46)],col);c.r(29,49,70,5,AU)
        for x in [36,59,82]:c.r(x,58,9,30,col);c.r(x-2,87,13,5,AU)
        c.r(27,96,74,6,col)
    elif key=="loans":
        c.r(35,30,48,61,col);c.poly([(68,30),(83,45),(68,45)],AU)
        for y in [48,57,66]:c.r(43,y,27,3,G)
        c.c(83,84,20,AU,G,2);c.line([(83,73),(83,95)],G,4);c.line([(73,84),(93,84)],G,4)
    elif key in {"train","transport","indra_metro"}:
        c.poly([(39,30),(89,30),(96,41),(96,84),(86,94),(40,94),(31,84),(31,41)],col);c.r(40,43,47,28,G);c.r(62,43,3,28,AU)
        c.r(40,77,10,6,AU);c.r(77,77,10,6,AU);c.line([(46,95),(36,105)],col,4);c.line([(82,95),(92,105)],col,4)
        c.r(52,34,24,4,AU)
    elif key in {"news","indra24"}:
        c.r(28,36,72,61,col);c.r(35,44,58,13,AU);c.r(35,64,24,23,G)
        for y in [65,73,82]:c.r(66,y,25,3,G)
        c.text(64,42,"24",11,G,True,"ma")
    elif key=="police":
        shield(c,col);star(c,64,61,17,AU)
    elif key in {"medical","health"}:
        c.r(33,45,61,49,col);c.r(49,33,29,12,None,col,5);c.r(58,53,13,32,G);c.r(48,63,33,12,G);c.r(60,55,8,28,AU);c.r(51,65,26,8,AU)
    elif key=="heart":
        c.poly([(63,99),(30,68),(28,49),(38,36),(53,36),(64,47),(75,36),(90,36),(100,49),(98,67)],col)
        c.line([(36,62),(49,62),(56,51),(66,78),(75,62),(91,62)],WHITE,4)
    elif key in {"event","events"}:
        c.r(31,36,66,63,col);c.r(31,36,66,17,AU);c.r(44,28,5,17,WHITE);c.r(79,28,5,17,WHITE)
        star(c,64,75,19,G)
    elif key in {"missions","target"}:
        c.c(64,64,31,None,col,5);c.c(64,64,18,None,AU,4);c.c(64,64,5,col)
        for a in [0,90,180,270]:
            r=math.radians(a);c.line([(64+24*math.cos(r),64+24*math.sin(r)),(64+40*math.cos(r),64+40*math.sin(r))],col,4)
    elif key in {"careers","briefcase"}:
        c.r(47,31,34,14,None,AU,5);c.r(28,47,72,49,col);c.r(28,65,72,5,G);c.r(59,61,12,15,AU);c.r(34,87,60,3,SA)
    elif key=="contacts":
        c.r(30,29,66,71,col);c.r(30,29,11,71,AU);c.c(67,51,12,G);c.arc(67,85,19,180,360,G,13)
        c.r(93,40,7,11,AU);c.r(93,61,7,11,AU)
    elif key=="keys":
        c.c(47,49,19,None,col,8);c.line([(60,62),(96,98)],col,9);c.line([(79,79),(89,69)],AU,7);c.line([(90,90),(101,79)],AU,7)
    elif key in {"settings","gear"}:
        for i in range(8):
            a=i*math.pi/4;u,v=math.cos(a),math.sin(a)
            c.poly([(64+u*23-v*7,64+v*23+u*7),(64+u*38-v*7,64+v*38+u*7),(64+u*38+v*7,64+v*38-u*7),(64+u*23+v*7,64+v*23-u*7)],col)
        c.c(64,64,29,col);c.c(64,64,17,G);c.c(64,64,7,AU)
    elif key=="fuel":
        c.r(34,33,43,64,col);c.r(41,40,29,22,G);c.r(44,43,23,4,AU);c.r(29,97,53,6,col)
        c.line([(78,51),(91,58),(91,84),(101,84),(101,44),(91,35)],col,4);c.line([(95,35),(104,44)],AU,5)
    elif key=="battery":
        c.r(29,43,68,44,None,col,5);c.r(97,55,8,19,col);c.r(37,51,38,28,EM);c.poly([(66,48),(52,68),(65,68),(58,84),(80,61),(66,61)],AU)
    elif key=="engine":
        c.poly([(38,47),(75,47),(86,58),(95,58),(95,88),(77,88),(68,98),(39,98),(30,87),(30,61)],col)
        c.r(45,36,25,6,AU);c.r(54,42,6,10,col);c.r(18,62,8,24,col);c.r(26,71,10,5,col);c.r(39,62,35,6,G);c.r(39,75,35,6,G)
    elif key=="phone":
        c.r(41,24,47,81,col);c.r(46,33,37,58,G);c.r(56,28,17,3,G);c.c(64,98,3,G)
        for y in [43,56,69]:
            for x in [51,62,73]:c.r(x,y,7,7,AU if x==51 else EM)
    elif key=="lotus":
        c.poly([(64,26),(79,48),(76,69),(64,88),(52,69),(49,48)],col)
        c.poly([(30,44),(51,54),(57,80),(64,89),(43,83),(31,66)],AU);c.poly([(98,44),(77,54),(71,80),(64,89),(85,83),(97,66)],AU)
        c.line([(33,96),(95,96)],col,3)
    elif key=="airwave":
        c.poly([(61,53),(68,53),(78,98),(72,98),(69,84),(59,84),(56,98),(50,98)],col);c.c(64,48,5,AU)
        for r in [20,31]:c.arc(64,48,r,205,335,col,4)
    elif key=="plane":
        c.poly([(61,25),(68,25),(71,55),(103,75),(103,83),(70,72),(70,94),(80,101),(80,106),(64,101),(48,106),(48,101),(58,94),(58,72),(25,83),(25,75),(57,55)],col)
    elif key=="gondola":
        c.line([(21,30),(108,30)],col,4);c.r(59,31,8,20,AU);c.poly([(42,49),(85,49),(95,62),(92,99),(35,99),(32,62)],col)
        c.r(40,59,20,24,G);c.r(65,59,20,24,G);c.r(47,89,33,4,AU)
    elif key=="boat":
        c.poly([(22,77),(106,77),(91,98),(38,98)],col);c.r(38,48,48,28,col);c.r(48,37,29,11,AU)
        c.r(44,54,15,13,G);c.r(66,54,14,13,G);c.line([(22,108),(37,104),(51,108),(65,104),(80,108),(95,104),(108,108)],AU,3)
    elif key=="bus":
        c.r(24,43,80,47,col);c.r(30,49,66,18,G)
        for x in [44,62,80]:c.r(x,49,3,18,AU)
        c.c(42,91,11,G);c.c(42,91,5,AU);c.c(86,91,11,G);c.c(86,91,5,AU);c.r(29,74,67,4,AU)
    elif key=="truck":
        c.r(21,43,52,41,col);c.poly([(78,55),(96,55),(109,71),(109,87),(78,87)],col);c.r(83,60,11,11,G)
        for x in [28,40,52,64]:c.r(x,48,2,29,AU)
        c.c(39,90,11,G);c.c(39,90,5,AU);c.c(89,90,11,G);c.c(89,90,5,AU)
    elif key=="helicopter":
        c.line([(24,30),(106,30)],col,4);c.r(63,31,5,16,AU);c.poly([(44,47),(78,47),(97,60),(97,79),(45,79),(34,66)],col)
        c.poly([(77,53),(88,61),(88,69),(72,69),(72,53)],G);c.poly([(43,59),(19,50),(19,38),(13,38),(11,66),(41,69)],col)
        c.line([(48,81),(48,89),(90,89)],AU,3);c.line([(79,81),(79,89)],AU,3)
    elif key=="film":
        c.r(30,46,69,52,col);c.poly([(29,31),(96,25),(99,40),(32,46)],AU)
        for x in [36,56,76]:c.line([(x,29),(x+12,42)],G,6)
        c.poly([(56,58),(56,87),(80,73)],G)
    elif key=="textile":
        c.poly([(31,30),(96,30),(96,97),(31,97)],col)
        for x in [39,55,71,87]:c.line([(x,32),(x,95)],G,3)
        for y in [40,56,72,88]:c.line([(33,y),(94,y)],AU,5)
    else:raise ValueError(f"Undefined glyph {key}")

APP_GLYPHS={"quoggle":"search","amazzo":"box","flippit":"flippit","arkpay":"ark","zomatoo":"food","swiffy":"delivery","fashion":"fashion","property":"home","car_app":"car","maps":"map","garage":"garage","bank":"bank","loans":"loans","taxi":"taxi","transport":"train","news":"news","police":"police","medical":"medical","events":"event","missions":"target","careers":"briefcase","contacts":"contacts","keys":"keys","settings":"gear"}

def tile(c,accent=AU):
    c.poly([(17,4),(111,4),(124,17),(124,111),(111,124),(17,124),(4,111),(4,17)],"#090E12")
    c.poly([(18,7),(110,7),(121,18),(121,108),(108,121),(18,121),(7,110),(7,18)],G,accent,2)
    c.line([(18,10),(109,10),(118,19)],SA,1)
    c.poly([(12,96),(35,119),(108,119),(118,109),(118,96)],"#0E151A")
    c.r(18,112,30,2,accent);c.r(52,112,7,2,accent)

def app_image(key):
    c=Canvas();accent=EM if key in {"arkpay","bank","maps","transport"} else TC if key in {"zomatoo","swiffy","medical"} else AU
    tile(c,accent);glyph(c,APP_GLYPHS[key],WHITE)
    return c

def brand_image(key):
    c=Canvas();c.poly([(64,5),(113,25),(116,83),(95,111),(64,123),(33,111),(12,83),(15,25)],G,AU,2)
    c.line([(20,28),(64,11),(108,28)],SA,1)
    g=c.group(17,7,.74)
    if key=="wahindra":
        g.poly([(22,81),(39,35),(54,68),(65,40),(78,68),(91,35),(107,81),(95,81),(88,61),(78,89),(65,64),(53,89),(40,61),(33,81)],SA)
    elif key=="tavara":
        g.poly([(28,34),(100,34),(100,48),(72,48),(72,95),(56,95),(56,48),(28,48)],AU)
        g.line([(32,62),(45,62)],SA,3);g.line([(83,62),(97,62)],SA,3);g.line([(32,72),(45,72)],SA,3);g.line([(83,72),(97,72)],SA,3)
    elif key=="maruva":
        g.poly([(26,92),(34,33),(64,65),(94,33),(102,92),(89,92),(85,59),(64,82),(43,59),(39,92)],EM)
        g.poly([(58,38),(68,23),(77,38),(68,52)],AU)
    elif key=="toyora":
        g.poly([(64,24),(101,65),(64,103),(27,65)],AU);g.poly([(64,36),(87,64),(64,89),(41,64)],G)
        g.r(47,51,35,7,SA);g.r(61,58,7,23,SA)
    elif key=="royal_iron":
        g.poly([(31,41),(43,54),(64,30),(86,54),(98,41),(90,72),(39,72)],AU)
        g.r(40,79,49,7,SA);g.line([(17,55),(33,61),(33,68),(17,63)],SA,3);g.line([(111,55),(96,61),(96,68),(111,63)],SA,3)
    elif key=="veero":
        g.poly([(22,36),(38,36),(64,79),(89,36),(105,36),(64,105)],TC);g.poly([(65,24),(49,57),(63,57),(55,76),(80,44),(67,44)],AU)
    elif key=="hondo":
        g.poly([(35,31),(47,31),(47,57),(80,57),(80,31),(92,31),(92,96),(80,96),(80,70),(47,70),(47,96),(35,96)],SA)
        g.line([(21,104),(49,101),(76,90),(108,69)],AU,3)
    elif key=="jyon":
        g.poly([(35,29),(94,29),(94,41),(74,41),(74,81),(62,96),(38,96),(26,83),(35,73),(44,82),(58,82),(61,77),(61,41),(35,41)],SA)
        g.poly([(82,58),(106,58),(89,79),(105,79),(105,89),(72,89),(90,69),(82,69)],TC)
    elif key=="jan_awaaz":
        g.poly([(27,45),(67,45),(96,27),(96,88),(67,71),(27,71)],SA);g.r(45,72,13,27,AU);g.line([(103,39),(113,32)],AU,3);g.line([(104,58),(117,58)],AU,3)
    elif key=="indra_suburban":
        glyph(g,"train",SA);g.r(33,69,61,8,TC)
    elif key=="skyindra":
        glyph(g,"gondola",SA);g.poly([(47,72),(64,56),(81,72),(72,72),(64,65),(56,72)],AU)
    elif key=="rang_bharat":glyph(g,"textile",EM)
    elif key=="black_lotus":glyph(g,"lotus",SA)
    elif key=="gtm":
        bridge(g);g.text(64,24,"GTM",22,WHITE,True,"ma")
    else:
        choice={"quoggle":"search","amazzo":"box","flippit":"shopping","arkpay":"ark","zomatoo":"food","swiffy":"delivery","indra_fuel":"fuel","indra_bank":"bank","vayu_bharat":"plane","skylink":"gondola","cinevista":"film","d_bazaar":"shopping","amora":"fashion","airwave":"airwave","indra24":"news","indra_metro":"train","maya_residences":"home","sd_motors":"car"}[key]
        glyph(g,choice,SA)
    label={"wahindra":"WAHINDRA","tavara":"TAVARA","maruva":"MARUVA","toyora":"TOYORA","royal_iron":"ROYAL IRON","veero":"VEERO","hondo":"HONDO","indra_suburban":"SUBURBAN","maya_residences":"MAYA","rang_bharat":"RANG BHARAT","vayu_bharat":"VAYU BHARAT","black_lotus":"BLACK LOTUS","sd_motors":"SD MOTORS"}.get(key,key.replace("_"," ").upper())
    c.text(64,96,label,11,WHITE,True,"ma",maxw=98);c.r(45,113,38,1,AU)
    return c

def warning(c,col=TC):
    c.poly([(64,27),(105,97),(23,97)],col);c.poly([(64,40),(94,91),(34,91)],G);c.r(61,54,7,21,col);c.r(61,81,7,7,col)

def hud_image(key):
    c=Canvas()
    if key.startswith("wanted_star"):
        star(c,r=39,fill=AU if key.endswith("filled") else G,stroke=WHITE if key.endswith("filled") else AU,lw=3)
        if key.endswith("filled"):c.line([(64,29),(57,51),(39,55)],SA,2)
    elif key in {"health","armour","fuel","battery","engine_condition","phone_shortcut","ark_symbol"}:
        glyph(c,{"health":"heart","armour":"police","fuel":"fuel","battery":"battery","engine_condition":"engine","phone_shortcut":"phone","ark_symbol":"ark"}[key],EM if key=="health" else SA)
    elif key=="low_fuel":
        glyph(c.group(14,17,.68),"fuel",AU);c.poly([(90,70),(111,106),(69,106)],TC);c.r(88,81,5,12,G);c.r(88,98,5,4,G)
    elif key=="critical_damage":warning(c);c.line([(40,103),(87,113)],TC,3)
    elif key=="speedometer_analog":
        c.c(64,64,51,G,AU,2);c.arc(64,66,41,145,395,SA,3);c.arc(64,66,41,325,395,TC,4)
        for i in range(11):
            a=math.radians(145+i*25);c.line([(64+35*math.cos(a),66+35*math.sin(a)),(64+41*math.cos(a),66+41*math.sin(a))],SA,2)
        c.line([(64,66),(89,42)],WHITE,3);c.c(64,66,5,AU);c.text(64,82,"km/h",10,SA,False,"ma")
    elif key=="speedometer_digital":
        c.poly([(14,34),(114,34),(119,40),(119,97),(9,97),(9,40)],G,AU,2);c.text(64,43,"000",37,WHITE,True,"ma");c.text(64,84,"KM / H",8,AU,True,"ma")
        c.r(19,101,75,3,EM);c.r(98,101,12,3,TC)
    elif key=="speedometer_compact":
        c.r(18,37,92,56,G,SA,2);c.text(57,42,"00",32,WHITE,True,"ma");c.text(94,63,"km/h",8,AU,False,"ma");c.r(26,84,75,3,EM)
    elif key in {"minimap_circle","minimap_rectangle"}:
        if key.endswith("circle"):c.c(64,64,53,None,G,8);c.c(64,64,48,None,AU,2)
        else:c.r(7,22,114,85,None,G,8);c.r(12,27,104,75,None,AU,2)
        # Empty frame: no invented map terrain or live navigation baked into art.
        c.r(61,8 if key.endswith("circle") else 17,6,8,WHITE)
        c.text(64,3 if key.endswith("circle") else 8,"N",6,G,True,"ma")
    elif key=="player_arrow":c.poly([(64,25),(94,103),(64,83),(34,103)],SA,G,3);c.line([(64,35),(64,72)],WHITE,2)
    elif key=="gps_route":
        c.line([(28,96),(28,70),(74,70),(74,35),(96,35)],G,13);c.line([(28,96),(28,70),(74,70),(74,35),(96,35)],AU,7);c.poly([(91,22),(108,35),(91,48)],AU)
    elif key.startswith("map_"):
        c.poly([(64,122),(43,97),(17,85),(11,38),(29,14),(98,14),(117,38),(111,85),(85,97)],G,AU,2)
        glyph(c.group(27,12,.58),{"police":"police","hospital":"medical","fuel":"fuel","shop":"shopping","property":"home","station":"train","mission":"target"}[key[4:]],SA)
    elif key in {"hotbar_frame","hotbar_selected"}:
        col=AU if key.endswith("selected") else "#617078";c.r(10,10,108,108,None,G,9);c.r(14,14,100,100,None,col,3)
        if key.endswith("selected"):
            for x,y in [(7,7),(106,7),(7,106),(106,106)]:c.r(x,y,15,15,AU)
            c.r(38,120,51,3,AU)
    elif key=="dialogue_bubble":
        c.poly([(15,24),(113,24),(113,88),(58,88),(37,108),(37,88),(15,88)],G,SA,2)
        for x in [43,64,85]:c.c(x,55,5,AU)
    elif key=="notification_frame":
        c.r(8,35,112,59,G,SA,2);c.r(8,35,5,59,AU);c.c(30,64,6,AU);c.r(46,50,63,4,WHITE);c.r(46,64,47,3,SA);c.r(46,77,55,3,SA)
    elif key in {"wasted_title","busted_title"}:
        c.r(0,33,128,63,G);c.r(0,33,128,2,TC if key.startswith("wasted") else AU);c.text(64,49,"WASTED" if key.startswith("wasted") else "BUSTED",24,WHITE,True,"ma",122)
        c.r(35,84,58,2,TC if key.startswith("wasted") else AU)
    elif key in {"city_enter","city_exit"}:
        bridge(c.group(17,6,.74),AU if key.endswith("enter") else SA);c.r(9,81,110,32,G,AU,1)
        c.text(64,84,"INDRAPRASTHA",10,WHITE,True,"ma",104);c.text(64,99,"WELCOME" if key.endswith("enter") else "LEAVING CITY",6,AU,False,"ma")
    else:raise ValueError(key)
    return c

def wrap_native(text,px,size,bold=False):
    words=text.split();lines=[];cur="";d=ImageDraw.Draw(Image.new("L",(1,1)));f=font(size,bold,text)
    for word in words:
        n=(cur+" "+word).strip()
        if cur and d.textlength(n,font=f)>px:lines.append(cur);cur=word
        else:cur=n
    if cur:lines.append(cur)
    return lines

def sign_image(rec,index):
    category=rec["category"];colors={"transport":("#18362F",AU),"road":("#203A32",WHITE),"civic":(G,SA),"store":("#32251E",AU),"commercial":("#242837",AU),"public_safety":("#39211D",SA)}
    bg,col=colors[category];c=Canvas(256,128,bg);c.r(0,0,256,4,col);c.r(5,8,246,115,None,col,1)
    c.text(13,11,"INDRAPRASTHA",8,col,True);c.text(241,11,category.upper().replace("_"," "),7,col,True,"ra")
    slug=rec["slug"]+" "+rec["english_text"].lower()
    key="train" if category=="transport" else "map" if category=="road" else "bank" if category=="civic" else "shopping" if category=="store" else "lotus" if category=="commercial" else "police"
    if any(w in slug for w in ["hospital","medical","trauma","first_aid"]):key="medical"
    elif any(w in slug for w in ["fuel","petrol"]):key="fuel"
    elif any(w in slug for w in ["sky","gondola","ropeway"]):key="gondola"
    elif any(w in slug for w in ["airport","airline"]):key="plane"
    elif any(w in slug for w in ["helipad","heliport","helicopter"]):key="helicopter"
    elif any(w in slug for w in ["aerodrome"]):key="plane"
    elif any(w in slug for w in ["pier","ferry","dock","port gate"]):key="boat"
    elif any(w in slug for w in ["bus","shuttle"]):key="bus"
    elif any(w in slug for w in ["freight","logistics","container"]):key="truck"
    elif any(w in slug for w in ["food","zomatoo","swiffy","restaurant","cafe"]):key="food"
    elif any(w in slug for w in ["police","crime"]):key="police"
    elif any(w in slug for w in ["bank","arkpay"]):key="bank"
    brand=rec.get("embedded_brand")
    if brand:
        emblem=brand_image(brand)
        c.im.alpha_composite(emblem.im.resize((48,48),Image.Resampling.NEAREST),(8,43))
        c.svg.append('<g transform="translate(8 43) scale(0.375)">'+"".join(emblem.svg)+'</g>')
    else:glyph(c.group(3,36,.47),key,col)
    english=rec["english_text"];deva=rec["marathi_text"]
    size=16
    while len(wrap_native(english,183,size,True))>2 and size>10:size-=1
    ens=wrap_native(english,183,size,True)
    for i,t in enumerate(ens):c.text(61,29+i*(size+2),t,size,WHITE,True,maxw=183)
    ds=14
    while len(wrap_native(deva,183,ds))>2 and ds>10:ds-=1
    devs=wrap_native(deva,183,ds)
    for i,t in enumerate(devs):c.text(61,72+i*(ds+4),t,ds,col,maxw=183)
    c.r(13,111,230,1,col);c.text(13,113,"SD CRAFT  /  GTM",6,col);c.text(241,113,f"{index+1:03d}",6,col,False,"ra")
    return c

def data(stem:Path,root:Path,id:str,title:str,**kwargs):
    png=stem.with_suffix(".png");svg=stem.with_suffix(".svg")
    im=Image.open(png);return dict(id=id,title=title,png=png.relative_to(root).as_posix(),svg=svg.relative_to(root).as_posix(),dimensions_px=list(im.size),mode=im.mode,native_grid="128x128",design_language="INDRAPRASTHA_128_V1",sha256=hashlib.sha256(png.read_bytes()).hexdigest(),size_bytes=png.stat().st_size,status="art_generated",client_verification="pending",author="Original procedural artwork created for SD Craft",rights="No third-party image assets; text fonts are system-provided Noto and DejaVu.",**kwargs)

def sheet(root,records,name,cols=6,cellw=160,cellh=160):
    rows=math.ceil(len(records)/cols);im=Image.new("RGB",(cols*cellw+32,rows*cellh+75),G);d=ImageDraw.Draw(im)
    d.text((18,13),"GTM  /  128px  /  "+name.replace("_"," ").upper(),font=font(18,True),fill=AU)
    d.text((18,39),"Native source assets • art export • client verification pending",font=font(10),fill=SA)
    for i,r in enumerate(records):
        x=16+(i%cols)*cellw;y=67+(i//cols)*cellh;a=Image.open(root/r["png"]).convert("RGBA")
        # Contact-sheet export keeps native raster dimensions; no redesign or filters.
        im.paste(a,(x+(cellw-a.width)//2,y),a)
        label=r.get("title",r["id"]).replace("gtm:sign_","")
        if len(label)>24:label=label[:22]+"…"
        d.text((x+cellw/2,y+a.height+4),label,font=font(9),fill=SA,anchor="ma")
    p=root/"previews"/(name+".png");p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def build(output:Path):
    if not features.check_feature("raqm"):raise RuntimeError("Pillow libraqm is required for correct Devanagari shaping")
    output=Path(output);base=ROOT/"creative"/"manifests";phone=[];hud=[];brands=[];signs=[];identity=[]
    for r in json.loads((base/"phone_icons.json").read_text()):
        p=output/"source/icons/phone"/r["id"];app_image(r["id"][4:]).save(p,r["title"]);phone.append(data(p,output,r["id"],r["title"]))
    for r in json.loads((base/"hud_manifest.json").read_text()):
        p=output/"source/icons/hud"/r["id"];hud_image(r["id"]).save(p,r["id"].replace("_"," "));hud.append(data(p,output,r["id"],r["id"].replace("_"," ")))
    for r in json.loads((base/"brands.json").read_text()):
        p=output/"source/branding/brands"/r["id"];brand_image(r["id"]).save(p,r["name"]);brands.append(data(p,output,r["id"],r["name"],sector=r["sector"],tagline=r["tagline"]))
    source=json.loads((base/"signage_manifest.json").read_text())
    for i,r in enumerate(source["signs"]):
        p=output/"source/signage"/r["category"]/r["slug"];c=sign_image(r,i);c.save(p,r["english_text"]+" / "+r["marathi_text"])
        tiles=[]
        for j in range(2):
            tile_path=p.with_name(p.name+f"_tile_{j}").with_suffix(".png");c.im.crop((j*128,0,(j+1)*128,128)).save(tile_path,optimize=True)
            tiles.append(dict(path=tile_path.relative_to(output).as_posix(),dimensions_px=[128,128],origin_px=[j*128,0],sha256=hashlib.sha256(tile_path.read_bytes()).hexdigest()))
        signs.append(data(p,output,r["id"],r["english_text"],category=r["category"],english_text=r["english_text"],marathi_text=r["marathi_text"],embedded_brand=r.get("embedded_brand"),tiles=tiles,composition="Two horizontal native128 tiles; exact bilingual labels preserved",placement_context=r["placement_context"],world_coordinates=None))
    # Core identity masters are separate from the32-brand catalogue.
    for key in ["gtm_logo","sd_craft_logo","ark_currency","server_icon"]:
        c=Canvas()
        if key in {"gtm_logo","server_icon"}:
            if key=="server_icon":c.r(0,0,128,128,G)
            c.poly([(64,5),(113,25),(113,89),(92,112),(64,124),(36,112),(15,89),(15,25)],G,AU,3)
            c.text(64,22,"GTM",29,WHITE,True,"ma");bridge(c.group(4,15,.94));c.text(64,102,"SD CRAFT",9,AU,True,"ma")
        elif key=="sd_craft_logo":
            c.poly([(64,6),(113,34),(113,94),(64,122),(15,94),(15,34)],G,AU,2)
            c.poly([(34,39),(64,22),(94,39),(64,56)],AU);c.poly([(34,40),(64,58),(64,83),(34,66)],SA);c.poly([(64,58),(94,40),(94,66),(64,83)],EM)
            c.text(64,89,"SD CRAFT",14,WHITE,True,"ma",98)
        else:
            c.c(64,64,55,G,AU,3);c.c(64,64,49,None,SA,1);ark(c)
            for i in range(16):
                a=i*math.pi/8;c.r(63+52*math.cos(a),63+52*math.sin(a),2,2,SA)
        p=output/"source/branding/core"/key;c.save(p,key.replace("_"," "));identity.append(data(p,output,key,key.replace("_"," ")))
        if key=="server_icon":
            # Mandatory server-list derivative. Master remains128; derivative is not a new asset.
            derivative=output/"source/branding/core/server-icon.png";c.im.convert("RGB").resize((64,64),Image.Resampling.NEAREST).save(derivative,optimize=True)
            identity[-1]["compatibility_export"]={"png":derivative.relative_to(output).as_posix(),"dimensions_px":[64,64],"mode":"RGB","reason":"Minecraft server-list icon"}
    tokens={"schema_version":1,"name":"GTM 128 / Indraprastha","base_canvas_px":[128,128],"palette":PALETTE,"spacing_px":[2,4,8,12,16,24,32],"strokes_px":{"micro":1,"secondary":2,"primary":4},"safe_area_px":12,"material_rule":"Graphite foundation; sandstone glyphs; gold keyline; emerald success and transit; terracotta warnings and food.","raster_rule":"Author at native128 coordinates. Do not upscale32x32 icons as production masters.","sign_rule":"Use two128x128 tiles for256x128 bilingual signs; preserve typography and shaped text.","typography":{"latin":"DejaVu Sans","devanagari":"Noto Sans Devanagari","shaping":"Pillow libraqm / HarfBuzz"},"hud_safe_area":{"desktop_px_at_1920x1080":32,"touch_px_at_1920x1080":72,"must_avoid":"Native touch controls, chat, hotbar, health and armour; actual client placement pending"},"dashboard_panels":["players","console","worlds","buildings","transport","NPCs","finance","loans","properties","festivals","media","hosting","backups","updates"],"runtime_status":"Visual design data only; UI logic and live client binding pending"}
    write_json(output/"source/ui/dashboard_tokens.json",tokens)
    for name,items in [("phone_128",phone),("hud_128",hud),("brands_128",brands),("signage_128",signs),("identity_128",identity)]:
        write_json(output/"manifests"/(name+".json"),{"schema_version":1,"design_language":"INDRAPRASTHA_128_V1","count":len(items),"assets":items})
    sheet(output,phone,"phone_128",6,160,155);sheet(output,hud,"hud_128",6,160,155);sheet(output,brands,"brands_128",8,150,155);sheet(output,identity,"identity_128",4,170,160)
    for cat in source["categories"]:sheet(output,[r for r in signs if r["category"]==cat],"signage_"+cat,3,268,155)
    groups={"phone":phone,"hud":hud,"brands":brands,"signage":signs,"identity":identity}
    assert [len(groups[k]) for k in ["phone","hud","brands","signage"]]==[24,33,32,120]
    errors=[]
    for group,entries in groups.items():
        if len({r["id"] for r in entries})!=len(entries):errors.append(f"Duplicate IDs in {group}")
        if len({r["sha256"] for r in entries})!=len(entries):errors.append(f"Duplicate PNG byte hashes in {group}")
        for r in entries:
            expected=[256,128] if group=="signage" else [128,128]
            if r["dimensions_px"]!=expected:errors.append(f"Wrong dimension {r['id']}")
            if r["mode"]!="RGBA":errors.append(f"Wrong image mode {r['id']}")
            if Image.open(output/r["png"]).getbbox() is None:errors.append(f"Empty image {r['id']}")
    report={"schema_version":1,"counts":{k:len(v) for k,v in groups.items()},"sign_tiles":240,"canonical_canvas":[128,128],"composite_exception":{"signage":[256,128]},"compatibility_exception":{"server_icon":[64,64]},"errors":errors,"automated_checks":["Exact existing IDs","Per-family hash uniqueness","Native dimensions andRGBA","Nonempty PNG","Devanagari RAQM shaping available","240 square sign tiles"],"visual_review":"Contact sheets exported; review must be recorded separately","client_verification":"not_run"}
    write_json(output/"reports/ui_128_validation.json",report)
    if errors:raise RuntimeError(errors)
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,default=ROOT/"creative/generated_128");a=p.parse_args();print(json.dumps(build(a.output),ensure_ascii=False,indent=2))
