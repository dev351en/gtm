"""Voxel-scale showroom miniatures of fictional Indraprastha transport."""
NAMES = ("City", "Touring", "Rescue", "Utility", "Courier")


def transport():
    result={}
    kinds=("rickshaw","scooter","motorcycle","hatchback","sedan","estate","taxi","suv",
           "minibus","city_bus","cargo_lorry","pickup","ambulance")
    for k,kind in enumerate(kinds):
        for style,label in enumerate(NAMES):
            p=[]
            def box(c,x,y,z,w,h,d): p.append((c,x,y,z,w,h,d))
            paint=("chilli","leaf","steel","gold","violet")[style]
            length=(9,8,10,9,11,12,10,11,12,14,13,12,12)[k]
            width=(6,2,2,6,6,6,6,7,7,7,7,6,7)[k]
            if style==1: length+=.6
            x,z=(16-width)/2,(16-length)/2
            for axle in (z+1,z+length-2.5):
                xs=[7.4] if k in (1,2) or (k==0 and axle==z+1) else [x-.5,x+width-.7]
                for xx in xs:
                    box("toast",xx,1,axle,1.2,2,2)
                    box("rim",xx-.05,1.6,axle+.55,1.3,.7,.9)
            if k in (1,2):
                box(paint,x,2.3,z+2,width,1.5,length-4)
                box("steel",7.5,2,z+1,1,3,1);box("steel",6.5,5,z+1,3,.6,1)
                box("toast",x,4,z+length/2,width,1,2.8)
                if k==2: box(paint,x-.45,3.5,z+2.5,width+.9,1.4,2)
            else:
                box("steel",x,2,z,width,1,length)
                box(paint,x,3,z,width,1.5,length)
                tall=k in (0,8,9,10,12)
                cab=length-1 if k in (0,8,9,12) else 3 if k in (10,11) else length-4
                cabz=z+(.8 if tall or k==11 else 2)
                glass=2.6 if tall else 1.8
                box("ice",x+.4,4.5,cabz,width-.8,glass,cab)
                for zz in (cabz,cabz+cab-1):
                    for xx in (x,x+width-.6): box(paint,xx,4.5,zz,.6,glass,1)
                box(paint,x,4.5+glass,cabz,width,.7,cab)
                for xx in (x+.4,x+width-1.3):
                    box("cream",xx,3.4,z-.1,.9,.6,.2)
                    box("chilli",xx,3.4,z+length-.1,.8,.6,.2)
                if k in (8,9):
                    for step in range(2,int(cab)-1,2):
                        box(paint,x,4.5,cabz+step,width,glass,.4)
                if k==10: box("clay",x,4.5,z+4.3,width,3.6,length-4.6)
                if k==11:
                    for xx in (x,x+width-.6): box(paint,xx,4.5,z+4.3,.6,1.2,length-4.5)
                if k==6: box("gold",7,7,cabz+1,2,.8,1)
                if k==12: box("chilli",x-.1,4.6,cabz+4,.3,2,1);box("chilli",x-.1,5.2,cabz+3,.3,.7,3)
            top=5 if k in (1,2) else 7.9 if k in (0,8,9,10,12) else 7
            if style==1: box("steel",x,top,z+2,width,.6,2.5)
            if style==2: box("ice",x,top,z+2,width,.9,.9);box("chilli",x,top+.9,z+2,width/2,.3,.9)
            if style==3: box("steel",x,3,z+length-1,width,2,.7);box("gold",x,5,z+length-1,width,.5,.7)
            if style==4: box("terra",x,4.5,z+length-2,width,2.5,2.3);box("cream",x+width/2-.3,7,z+length-2,.6,.1,2.3)
            result[kind+"_"+label.lower()]=("road",label+" "+kind.replace("_"," ").title(),p)
    for i,kind in enumerate(("local_motor","local_trailer","metro_lead","metro_middle","inspection_railcar",
                              "platform_shunter","parcel_van","maintenance_wagon","skylink_cabin","skylink_accessible")):
        p=[]
        def box(c,x,y,z,w,h,d): p.append((c,x,y,z,w,h,d))
        if i<8:
            length=13 if i<4 else 9+i%3
            z=(16-length)/2
            box("steel",4,2,z,8,1,length)
            for zz in (z+1,z+length-3):
                box("toast",4.5,1,zz,7,1,2)
            color=("violet","gold","mint","steel","chilli","leaf","terra","rim")[i]
            cabin=length if i<5 or i==6 else 4
            box(color,4,3,z,8,2,length)
            box("ice",4.4,5,z+.4,7.2,2,cabin-.7)
            box("rim",4,7,z,8,.7,cabin)
            for step in range(1,int(cabin),2+(i%2)): box(color,4,5,z+step,8,2,.4)
            if i in (0,2,4): box("steel",6,7.7,z+1,4,.8,2+i%3)
            if i in (5,7): box(color,4,5,z+length-1,8,1+i%2,1)
            if i==3: box("steel",5.5,7.7,z+4,5,1,3); box("rim",6,8.7,z+4.5,4,.3,2)
            if i==6: box("terra",4,5,z+4,8,2,3)
        else:
            width=7+(i-8)*2;x=(16-width)/2
            box("gold",x,2,4,width,2,8);box("ice",x+.3,4,4.3,width-.6,4,7.4)
            box("steel",x,8,4,width,.8,8);box("steel",7.5,8.8,7.5,1,3,1);box("toast",6,11.8,7,4,1,2)
            for zz in (4,11): box("gold",x,4,zz,width,4,.5)
        result[kind]=("rail",kind.replace("_"," ").title(),p)
    for i,kind in enumerate(("harbour_scout","city_medivac","monsoon_rescue","broadcast_helicopter")):
        paint=("leaf","milk","gold","violet")[i];p=[]
        def box(c,x,y,z,w,h,d):p.append((c,x,y,z,w,h,d))
        width=4+i*.3;x=(16-width)/2
        box(paint,x,4,3,width,3,6+i*.35);box("ice",x+.4,5,2,width-.8,2,2)
        box(paint,7.3,5.7,9,1.4,1,4);box(paint,7.5,6.7,12,1,2,1.2)
        box("steel",7.5,7.4,5.5,1,1.5,1);box("toast",1,9,5.5,14,.5,1);box("steel",7.5,9,.5,1,.5,12)
        for xx in (x,x+width-1):box("steel",xx,2.5,2.8,1,.6,7.5);box("steel",xx,3,5,.6,1,3)
        if i:box(("milk","chilli","gold","steel")[i],x-.8,4,4+i,.8,1+i*.4,2)
        result[kind]=("helicopter",kind.replace("_"," ").title(),p)
    for i,kind in enumerate(("harbour_ferry","patrol_launch","fishing_trawler","water_taxi","rescue_rib","cargo_barge","sailing_dinghy","pilot_boat")):
        p=[]
        def box(c,x,y,z,w,h,d):p.append((c,x,y,z,w,h,d))
        c=("steel","cream","terra","gold","chilli","toast","leaf","violet")[i];w=5+(i%4)*.7;x=(16-w)/2
        box(c,x,2,4,w,2,9);box(c,x+.5,2.5,3,w-1,1.5,1);box(c,x+1,3,2,w-2,1,1)
        box("bread",x+.4,4,4,w-.8,.4,8.5)
        if i==6:
            box("toast",7.5,4.4,6,1,7,1)
            for j in range(4):box("cream",8.5,4.8+j*1.4,6,3.8-j*.8,1.4,.4)
        elif i==5:box("terra",x+.5,4.4,5,w-1,2,3);box("steel",x+.5,4.4,9,w-1,2.5,2.5)
        elif i==4:
            for xx in (x-.3,x+w-.7):box("gold",xx,4,3.5,1,1,9)
            box("steel",7,4.4,6,2,1.4,1)
        else:
            cabin=3+i%3;box("ice",x+.6,4.4,5,w-1.2,2,cabin);box(c,x+.2,6.4,4.8,w-.4,.6,cabin+.4)
            if i==2:box("steel",7.5,4.4,10,1,5,1);box("steel",5,9,10,6,.5,.5)
            if i==0:box("rim",x+.2,4.4,10,w-.4,1.5,1.5)
        result[kind]=("marine",kind.replace("_"," ").title(),p)
    return result
