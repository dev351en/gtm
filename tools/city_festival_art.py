"""Manual festival installations for Indraprastha, in shared voxel geometry."""
THEMES = [
    ("diwali","Diwali","clay","gold","saffron","lamp"),
    ("holi","Holi","violet","pink","mint","splash"),
    ("ganesh","Ganesh Chaturthi","terra","gold","cream","petal"),
    ("navratri","Navratri","leaf","chilli","gold","sticks"),
    ("eid","Eid","steel","mint","gold","crescent"),
    ("sankranti","Makar Sankranti","bread","ice","chilli","kite"),
    ("christmas","Christmas","leaf","chilli","milk","tree"),
    ("new_year","New Year","violet","rim","gold","star")
]


def motif(kind,x,y,z,s,a,b):
    # Flat emblems face the viewer. Local point grid is centred at (x,y).
    pixels={
        "lamp":["....X....","...XXX...","....X....","XYYYYYYYX",".YYYYYYY.","..XXXXX.."],
        "splash":["X...X..X.",".X..X.X..","..XYYY...","XXYYYYYXX","..YYYYY..",".X.YYY.X.","X...X...X"],
        "petal":["....X....","..X.X.X..","X.XXXXX.X",".XXYYYXX.","..XYYYX..","...XXX..."],
        "sticks":["X......Y.",".X....Y..","..X..Y...","...XY....","...YX....","..Y..X...",".Y....X.."],
        "crescent":["...XXXX..","..XX.....",".XX...Y..",".XX..YYY.",".XX...Y..","..XX....X","...XXXXX."],
        "kite":["....X....","...XYX...","..XYYYX..",".XXYYYXX.","..XYYYX..","...XYX...","....X...."],
        "tree":["....Y....","...XXX...","..XYXXX..","...XXX...",".XXXYXXX.","..XXXXX..","...YYY..."],
        "star":["....X....","....X....",".YYXXXYY.","..XXXXX..","...XYX...","..X...X..",".X.....X."]
    }[kind]
    parts=[]
    for row,line in enumerate(pixels):
        col=0
        while col<len(line):
            char=line[col];end=col+1
            while end<len(line) and line[end]==char:end+=1
            if char!=".":parts.append((a if char=="X" else b,x+(col-4.5)*s,y+(len(pixels)-1-row)*s,z,(end-col)*s,s,.5))
            col=end
    return parts


def festival():
    out={}
    forms=("gateway","street_banner","window_lantern","counterpiece","procession_cart","stage_backdrop",
           "door_emblem","parade_standard","street_arch","balcony_screen","market_booth","bandstand","square_beacon")
    for i,(key,label,frame,a,b,symbol) in enumerate(THEMES):
        for j,form in enumerate(forms[:13 if i<4 else 12]):
            p=[]
            def box(c,x,y,z,w,h,d):p.append((c,x,y,z,w,h,d))
            if j in (0,5,8,9,10,11):
                width=(12,11,14,10,11,13)[(0,5,8,9,10,11).index(j)]
                x=(16-width)/2
                for xx in (x,x+width-1):
                    box(frame,xx,1,8,1,9+j%3,1.5)
                    box(b,xx-.4,1,7.6,1.8,1,2.3)
                box(a,x,10+j%3,7.8,width,1.2,1.9)
                if j in (5,9):box(frame,x+.9,3,9,width-1.8,7,1)
                if j in (10,11):box(frame,x,3,4,width,1.2,6);box(b,x-.5,11+j%3,5,width+1,.7,5)
                if j==8:box(b,x+2,11+j%3,8,width-4,1.5,1.5)
                base=6 if j!=9 else 4;s=.6 if j in (0,8) else .8
            elif j in (1,7,12):
                box(frame,6,1,6,4,1,4);box(frame,7.4,2,7.5,1.2,10,1.2)
                if j==1:box(a,4,11,7,8,1,1);box(frame,4.5,5,7,7,6,.7)
                if j==7:box(b,7,12,7,2,1,2)
                if j==12:box(a,5,9,5,6,3,6);box(b,6,12,6,4,1,4)
                base=6;s=.7
            elif j==2:
                box(frame,5,4,5,6,1,6);box(frame,5,10,5,6,1,6);box(a,7,11,7,2,2,2)
                for xx in (5,10):
                    for zz in (5,10):box(frame,xx,5,zz,.6,5,.6)
                base=5;s=.6
            elif j==3:
                box(frame,3,1,4,10,1,8);box(a,5,2,6,6,1,4);base=3;s=.8
            elif j==4:
                box(frame,2,3,4,12,2,8)
                for xx in (2,12):
                    for zz in (4,10):box("toast",xx,1,zz,2,2,2)
                box(b,4,5,6,8,1,4);base=6;s=.8
            else:
                box(frame,3,4,9,10,7,1);box(b,3.5,4.4,8.7,9,.7,.5);base=5;s=.8
            front=4.5 if j in (2,12) else 6.7 if j in (1,7) else 7.2
            p+=motif(symbol,8,base,front,s,a,b)
            out[key+"_"+form]=("festival",label+" "+form.replace("_"," ").title(),p)
    return out
