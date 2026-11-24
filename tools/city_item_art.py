"""Civic, entertainment and fictional arcade equipment for the city catalogue."""
def equipment():
    designs={}
    for i,shape in enumerate(("prism","comet","halo","lattice","pulse","lotus")):
        for j,edition in enumerate(("arcade","parade","relay","arena","night")):
            p=[]
            def box(c,x,y,z,w,h,d):p.append((c,x,y,z,w,h,d))
            c=("ice","chilli","mint","gold","violet")[j]
            # Fictional light-tag game props, drawn around crystals, fins and luminous tiles.
            box("steel",4,6,6,7+i*.3,2.4,3.4)
            box("toast",5,3,6.5,2,3,2.4);box(c,5,8.4,6.4,4,1.2,2.6)
            if i==0:box(c,10,7,6.5,4,1.4,2);box("milk",12,8.4,7,1,1,1)
            elif i==1:box(c,8,6.4,5.5,5,1,.8);box(c,8,6.4,9.4,5,1,.8)
            elif i==2:
                for yy in (5.5,9):box(c,10,yy,6,3,1,3)
                box(c,12,6.5,6,1,2.5,3)
            elif i==3:
                for xx in (9,11,13):box(c,xx,5.5,5.6,.7,3.5,4)
            elif i==4:box(c,9,5,6,4,1,3);box("ice",10,9,6.5,2,2,2)
            else:
                for zz in (5,7,9):box(c,10,7,zz,2,1.5,1)
            if j==0:box("gold",4,8.5,6.5,1.2,1.3,2.5)
            elif j==1:box("gold",3,6,6,1,3,3);box(c,2,7,7,1,2,1)
            elif j==2:box("rim",6,9,7,1,3,1);box(c,5.5,12,6.5,2,.6,2)
            elif j==3:box(c,3,3.8,6.8,2,1.2,1.8);box("steel",3,5,7,1,1,1.4)
            else:box("ice",7,5,6,3,.6,3);box(c,8,4,7,1,1,1)
            designs["tag_"+shape+"_"+edition]=("protection",shape.title()+" "+edition.title()+" Light Tag",p)
    for i,shape in enumerate(("festival_shield","rescue_helmet","marshal_vest","padded_bracer","visor")):
        for j,edition in enumerate(("local","metro","harbour","hill","night")):
            c=("leaf","violet","ice","terra","steel")[j];p=[]
            def box(c,x,y,z,w,h,d):p.append((c,x,y,z,w,h,d))
            if i==0:box(c,4,3,7,8,8,2);box(c,5,2,7,6,1,2);box("rim",3.5,10,7,9,1.5,2)
            if i==1:box(c,4,6,4,8,4,8);box(c,5,10,5,6,1.5,6);box("rim",3.5,6,3,9,1,9)
            if i==2:
                box(c,4,3,6,8,7,4)
                for xx in (4,10):box(c,xx,10,6,2,2,4)
                box("rim",4,5,5.7,8,1,.5)
            if i==3:box(c,5,3,6,6,8,4);box("rim",4.5,3,5.5,7,1,5);box("rim",4.5,10,5.5,7,1,5)
            if i==4:box("ice",3,7,5,10,3,1);box(c,3,10,5,10,1,1);box(c,3,8,6,1,1,4);box(c,12,8,6,1,1,4)
            z=(6.4,3.4,5.2,5.5,4.4)[i];y=(7,8,7,7,8)[i]
            if j==0:box("gold",7,y,z,2,1,.7)
            if j==1:box("gold",5,y,z,6,.6,.7);box("rim",6,y+1,z,4,.6,.7)
            if j==2:box("rim",7,y-1,z,1,3,.7);box("gold",6,y,z,3,1,.8)
            if j==3:box("cream",6,y,z,1,1,.7);box("cream",7,y+1,z,2,1,.7);box("cream",9,y,z,1,1,.7)
            if j==4:box("mint",5,y,z,2,1,.7);box("mint",9,y,z,2,1,.7)
            designs[shape+"_"+edition]=("protection",edition.title()+" "+shape.replace("_"," ").title(),p)
    return designs


def objects():
    out=equipment()
    def put(cat,name,parts):out[name]=(cat,name.replace("_"," ").title(),parts)
    def stand(c,w=7,h=8):
        return [("steel",5,1,5,6,1,6),("steel",7.4,2,7.4,1.2,h,1.2),(c,(16-w)/2,4+h/2,7,w,4,1)]
    def case(c,w,h,d):
        return [(c,(16-w)/2,2,(16-d)/2,w,h,d),("rim",(16-w)/2,2+h,(16-d)/2,w,.65,d)]
    def panel(c,x,y,w,h):return [(c,x,y,5,w,h,.5)]
    civic={
      "bus_stop_flag":stand("leaf",6)+panel("cream",6,9,3,1),
      "metro_roundel":stand("violet",8,9)+panel("ice",5,10,6,.7),
      "district_marker":stand("terra",9,6)+panel("gold",5,8,5,.6),
      "queue_post":[("steel",5,1,5,6,1,6),("rim",7.2,2,7.2,1.6,8,1.6),("chilli",6.7,10,6.7,2.6,1,2.6)],
      "parking_meter":stand("steel",4,8)+panel("ice",7,9,2,1.6),
      "platform_clock":stand("rim",6,10)+panel("toast",8,10,1,2)+panel("toast",7,10,1,.6),
      "postal_box":case("chilli",6,7,5)+panel("toast",6,7,4,.7),
      "street_bin":case("leaf",5,6,5)+panel("cream",6.5,5,3,.7),
      "first_aid_cabinet":case("cream",8,6,4)+panel("chilli",7,3,2,4)+panel("chilli",6,4,4,2),
      "hydration_station":case("steel",7,7,5)+[("ice",5.5,9.7,6,5,2,4),("rim",7,4,4.8,2,1,1)],
      "road_cone":[("toast",4,1,4,8,1,8),("terra",5,2,5,6,2,6),("milk",6,4,6,4,2,4),("terra",7,6,7,2,3,2)],
      "hazard_bollard":case("gold",3,8,3)+[("toast",6.4,6,6.4,3.2,1,3.2)],
      "road_barrier":[("steel",3,1,6,2,5,4),("steel",11,1,6,2,5,4),("terra",2,5,7,12,2,2),("cream",6,5,6.8,3,2,.4)],
      "civic_bench_sign":stand("cream",10,4)+panel("leaf",5,7,6,.7),
      "help_intercom":case("steel",4,8,3)+panel("gold",7,5,2,1)+panel("toast",7,8,2,.5),
      "taxi_call_post":stand("gold",5,7)+panel("toast",6.5,8.5,3,1),
      "ticket_validator":case("steel",4,6,4)+panel("mint",6.5,5,3,2),
      "news_display":stand("rim",10,6)+panel("ice",4,8,8,2.5),
      "service_kiosk":case("steel",9,8,6)+panel("ice",5,6,6,2.5)+[("gold",3.5,10.7,4,9,1,8)],
      "council_lectern":case("toast",6,6,4)+[("bread",3.5,8.7,4.5,9,1,7),("steel",9,9.7,8,.5,2,.5)]
    }
    for name,parts in civic.items():put("civic",name,parts)
    entertain={
      "tabla_pair":case("terra",5,4,5)+[("cream",6,6.7,6,4,.5,4),("toast",10,2,7,3,5,3),("cream",10,7,7,3,.7,3)],
      "dhol":case("gold",9,4,5)+[("cream",3,2,5,1,5,6),("cream",12,2,5,1,5,6)],
      "harmonium":case("toast",9,4,6)+[("milk",4,6.7,5,8,.5,2),("chilli",5,6.7,8,6,1,2)],
      "studio_mic":stand("toast",2,6)+[("steel",6.5,9,6.5,3,3,3)],
      "dj_deck":case("steel",12,2,7)+[("toast",3,4.7,6,4,.5,4),("violet",9,4.7,6,4,.5,4)],
      "speaker_stack":case("toast",7,10,5)+panel("steel",6,4,4,3)+panel("steel",6,9,3,2),
      "cinema_projector":case("steel",8,4,5)+[("toast",5,6.7,6,2,3,2),("toast",9,6.7,6,2,3,2),("ice",11,4,6,2,2,2)],
      "dance_tile":[("steel",2,1,2,12,1,12),("pink",3,2,3,4,.5,4),("ice",9,2,3,4,.5,4),("mint",3,2,9,4,.5,4),("gold",9,2,9,4,.5,4)],
      "stage_spotlight":stand("steel",3,4)+[("toast",5,7,5,6,4,5),("gold",6,8,4,4,2,1)],
      "radio_receiver":case("toast",10,5,4)+panel("gold",4,4,4,2)+[("steel",11,7.7,8,.5,5,.5)]
    }
    for name,parts in entertain.items():put("entertainment",name,parts)
    for i,name in enumerate(("confetti_puck","glow_beacon","colour_capsule","spark_orb","mist_totem")):
        c=("pink","mint","violet","gold","ice")[i]
        put("effect",name,case(c,6-i*.6,2+i,6-i*.6)+[("rim",6.5,4.7+i,6.5,3,.7,3),("milk",7.5,5.4+i,7.5,1,.6+i*.2,1)])
    put("property","flat_key",[("gold",3,6,7,4,4,1),("toast",4,7,6.9,2,2,.3),("gold",7,7,7,6,1.5,1),("gold",11,6,7,1,1,1)])
    put("property","property_deed",[("cream",3,2,3,10,1,10),("terra",10,3,4,2,.5,7),("gold",9.5,3.5,9,3,.5,2)])
    return out
