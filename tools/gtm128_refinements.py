"""Semantic geometry repairs found while reviewing the128 contact sheets."""
import math
import studio_3d_engine as s3d

def transport(pb,vid,category,dims):
    W,H,L=[v*16 for v in dims]
    # The previous greenhouse assigned an opaque door graphic to side windows.
    # Restore glazing and split it with actual pillars and door-frame detail.
    for b in pb.bones.values():
        for p in b['parts']:
            if p['mat']=='glass_tint':
                for face in ('east','west'):
                    if p['face_mats'].get(face,'').startswith('car_door_'):p['face_mats'][face]='glass_tint'
            if category=='bus' and p['mat']=='car_door_bus':
                p['mat']='glass_tint'
                y=p['origin'][1];height=p['size'][1]
                # Frames divide the continuous window strip without making a new ID.
                for x in (-W*.486,W*.486):
                    for k in range(1,8):
                        z=-L*.4+L*.1*k
                        pb.cbox(x,y,z,.8,height,1.1,mat='fire_red',bone='chassis',name='window_pillar')
    if category in ('hatchback','sedan','luxury'):
        # Fine lower sills and window divider improve the native128 silhouette.
        for x in (-W*.47,W*.47):pb.cbox(x,H*.22,0,.65,1.0,L*.48,mat='chrome',bone='chassis',name='lower_sill')
    if category=='marine':
        # Side glazing and rail stanchions make the existing hull readable as a boat.
        for x in (-W*.35,W*.35):
            pb.cbox(x,23,-min(L,140)*.14,.5,6,min(L,140)*.25,mat='glass_tint',bone='hull',name='bridge_glazing')
        for x in (-W*.43,W*.43):
            for k in range(5):pb.cbox(x,18,-min(L,140)*.32+k*min(L,140)*.16,.55,4,.55,mat='chrome',bone='hull',name='deck_rail_post')
            pb.cbox(x,22,0,.6,.6,min(L,140)*.72,mat='chrome',bone='hull',name='deck_handrail')
    # Distinguish inherited equal meshes with relevant designed construction.
    if vid=='sedan_amaze':
        for x in (-W*.34,W*.34):
            pb.cbox(x,H*.25,L*.485,W*.17,1.1,1.4,mat='headlight_face',bone='chassis',name='split_daylight')
            pb.cbox(x,H*.14,L*.482,W*.18,2.2,1.0,mat='grille_black',bone='chassis',name='fog_lamp_recess')
        pb.cbox(0,H*.39,-L*.39,W*.86,1.1,L*.11,mat='paint_red',bone='chassis',name='raised_boot_lip')
    elif vid=='moto_bullet350':
        pb.cbox(3.2,4,-L*.10,1.8,1.8,L*.64,mat='chrome',bone='chassis',name='long_classic_exhaust')
        pb.cbox(0,10,-L*.21,5.8,2.1,L*.30,mat='leather_tan',bone='chassis',name='wide_touring_saddle')
        pb.cbox(0,15.5,L*.31,4.8,.7,3.1,mat='chrome',bone='chassis',name='headlamp_eyebrow')
        pb.cbox(0,12.8,-L*.38,6.1,.7,1.0,mat='chrome',bone='chassis',name='rear_grab_handle')
    elif vid=='scooter_jupiter':
        for x in (-3.1,3.1):pb.cbox(x,6,L*.18,1.2,6.8,4.0,mat='paint_silver',bone='chassis',name='sculpted_leg_shield')
        pb.cbox(0,5,0,7.4,1.2,L*.44,mat='steel_dark',bone='chassis',name='wide_step_through_floor')
        pb.cbox(0,12.5,L*.28,5.8,1.5,2.6,mat='headlight_face',bone='chassis',name='wide_handlebar_lamp')
    elif vid=='local_driving_cab':
        # Cab bulkhead, desk and controls make this the leading coach.
        pb.cbox(0,7,L*.31,W*.82,12,1.2,mat='steel_light',bone='root',name='driver_bulkhead')
        pb.cbox(0,12,L*.39,W*.68,2.8,L*.10,mat='police_navy',bone='root',name='driver_console')
        pb.cbox(-W*.22,15,L*.40,4.2,3.2,.7,mat='screen_pc',bone='root',name='cab_controls')
        pb.cbox(0,H*.55,L*.48,W*.42,2.2,.8,mat='headlight_face',bone='root',name='cab_route_display')
    elif vid=='metro_accessible':
        # A lower boarding step and a deliberately open wheelchair bay.
        pb.cbox(W*.51,5,L*.16,3.8,1.2,L*.16,mat='hazard_yellow',bone='root',name='low_boarding_threshold')
        pb.cbox(W*.42,9,L*.16,.7,12,1.0,mat='chrome',bone='root',name='accessible_grab_rail')
        pb.cbox(W*.43,17,L*.12,.8,.8,L*.13,mat='chrome',bone='root',name='accessible_horizontal_rail')
        pb.cbox(W*.49,15,L*.23,.6,4.2,4.2,mat='paint_blue',bone='root',name='accessible_bay_marker')
    return pb

def stepped_disc(pb,x,y,z,rx,rz,height,mat,bone='base'):
    # Eight horizontal bands approximate an ellipse using axis-aligned cubes.
    for i in range(8):
        zz=-1+(i+.5)/4;half=math.sqrt(max(.0,1-zz*zz))*rx
        pb.cbox(x,y,z+zz*rz,half*2,height,rz/4,mat=mat,bone=bone)

def furniture(pb,fid,category,dims):
    W,H,D=[max(.1,v)*16 for v in dims]
    fixed={'wall_mirror_sunburst','full_length_mirror','dresser_mirror','ceiling_fan_wood','glass_end_table','nesting_tables',
      'floor_arc_lamp','pouffe_cushion','gaddi_floor_cushions','clothes_valet','nightstand_drawers','blanket_chest',
      'dholak_musical_drum','handloom_charkha','tiffin_carrier_brass','pot_rack_hanging','surveillance_wall_cctv',
      'clothing_gondola_double','shoe_display_wall','supermarket_produce_bin','gas_stove_4burner'}
    if fid not in fixed:return pb
    q=s3d.PartBuilder();q.add_bone('base',(0,0,0))
    def b(x,y,z,w,h,d,mat='wood_teak',**kw):q.cbox(x,y,z,w,h,d,mat=mat,bone='base',**kw)
    if fid=='ceiling_fan_wood':
        b(0,H*.73,0,1.2,H*.27,1.2,'chrome');stepped_disc(q,0,H*.64,0,W*.11,D*.11,2,'brass')
        for i in range(5):
            a=i*72
            q.cbox(0,H*.61,D*.25,W*.16,1.0,D*.5,mat='wood_teak',bone='base',rot=[0,a,0],pivot=[0,H*.61,0],name='fan_blade')
    elif 'mirror' in fid:
        if fid=='wall_mirror_sunburst':
            for i in range(12):
                a=i*30;r=min(W,H)*.4
                b(0,H*.5,0,1.2,r*2,1,'brass',rot=[0,0,a],pivot=[0,H*.5,0])
            b(0,H*.18,.8,W*.52,H*.64,1.2,'chrome');b(0,H*.2,1.5,W*.46,H*.60,.4,'glass_clear')
        elif fid=='full_length_mirror':
            for x in (-W*.35,W*.35):b(x,0,0,1.2,H*.88,1.2,'wood_sheesham');b(x,0,0,2,1,D*.8,'wood_sheesham')
            b(0,H*.1,0,W*.68,H*.88,1.3,'brass');b(0,H*.13,1,W*.60,H*.81,.5,'glass_clear')
        else:
            b(0,0,0,W,H*.48,D,'wood_teak');b(0,H*.48,-D*.35,W*.85,H*.52,1.0,'wood_sheesham');b(0,H*.52,-D*.30,W*.75,H*.43,.5,'glass_clear')
            for x in (-W*.25,W*.25):
                for y in (H*.12,H*.3):b(x,y,D*.51,W*.15,.7,.7,'brass')
    elif fid in ('glass_end_table','nesting_tables'):
        count=3 if fid=='nesting_tables' else 1
        for i in range(count):
            hh=H*(1-i*.22);ww=W*(.65 if count>1 else .94)*(1-i*.15);dd=D*(.65 if count>1 else .94)*(1-i*.15);xx=(i-1)*W*.25 if count>1 else 0
            stepped_disc(q,xx,hh-1,0,ww*.5,dd*.5,1,'glass_clear' if count==1 else 'marble')
            for x in (-ww*.32,ww*.32):
                for z in (-dd*.32,dd*.32):b(xx+x,0,z,.8,hh-1,.8,'brass')
    elif fid=='floor_arc_lamp':
        stepped_disc(q,-W*.25,0,-D*.25,W*.28,D*.23,1.2,'steel_dark')
        for k in range(5):b(-W*.25+k*W*.08,H*k*.16,-D*.25+k*D*.09,1.0,H*.18,1.0,'brass')
        b(W*.12,H*.77,D*.20,W*.42,1.4,D*.33,'brass');b(W*.12,H*.74,D*.20,W*.34,.7,D*.27,'headlight')
    elif fid in ('pouffe_cushion','gaddi_floor_cushions'):
        for i in range(3 if fid.startswith('gaddi') else 1):
            y=i*H*.26;scale=1-i*.08;b(0,y,0,W*.8*scale,H*.25,D*.8*scale,'fabric_emerald' if i%2 else 'fabric_maroon');b(0,y+H*.25,0,W*.69*scale,.4,D*.69*scale,'gold_filigree')
    elif fid=='clothes_valet':
        b(0,0,0,W*.7,1,D*.7,'wood_sheesham');b(0,1,0,1.3,H*.9,1.3,'wood_sheesham');b(0,H*.72,0,W*.72,.8,.8,'brass')
        for x,a in ((-W*.18,25),(W*.18,-25)):b(x,H*.82,0,W*.4,.8,.8,'brass',rot=[0,0,a])
        b(0,H*.42,D*.16,W*.58,1,D*.22,'wood_teak')
    elif fid in ('nightstand_drawers','blanket_chest'):
        b(0,1,0,W*.92,H*.83,D*.9,'wood_teak');b(0,H*.84,0,W,.9,D,'wood_sheesham')
        for x in (-W*.36,W*.36):
            for z in (-D*.35,D*.35):b(x,0,z,1.4,2,1.4,'wood_sheesham')
        for y in ((H*.25,H*.6) if fid=='nightstand_drawers' else (H*.5,)):
            b(0,y,D*.46,W*.82,.5,.4,'wood_sheesham');b(0,y+1,D*.5,W*.20,.8,.6,'brass')
    elif fid=='dholak_musical_drum':
        for k in range(7):
            t=(k+.5)/7;w=W*(.65+.27*math.sin(t*math.pi));b(0,H*.13+k*H*.1,0,w,H*.1,D*.85,'wood_sheesham')
        b(0,H*.1,0,W*.68,1,D*.9,'linen_white');b(0,H*.83,0,W*.68,1,D*.9,'linen_white')
        for x in (-W*.38,W*.38):
            for z in (-D*.38,D*.38):b(x,H*.15,z,.5,H*.68,.5,'brass')
    elif fid=='handloom_charkha':
        for z in (-D*.35,D*.35):b(0,0,z,W,1,1,'wood_sheesham')
        b(-W*.25,1,0,1,H*.62,1,'wood_teak')
        cy=H*.52;r=min(W,H)*.38
        for i in range(12):
            a=i*math.pi/6;b(-W*.25+math.sin(a)*r,cy+math.cos(a)*r,0,2.3,1.1,1.2,'wood_teak',rot=[0,0,-i*30])
        for i in range(6):b(-W*.25,cy,0,1,r*2,1,'wood_teak',rot=[0,0,i*30],pivot=[-W*.25,cy,0])
        b(W*.28,1,0,1,H*.35,1,'wood_teak');b(W*.28,H*.35,0,W*.25,.8,.8,'chrome')
    elif fid=='tiffin_carrier_brass':
        for i in range(4):stepped_disc(q,0,i*H*.2,0,W*.42,D*.42,H*.18,'brass')
        for x in (-W*.44,W*.44):b(x,0,0,.7,H*.88,.7,'chrome')
        b(0,H*.88,0,W*.88,.8,.9,'chrome');b(0,H*.91,0,W*.32,1.0,1.1,'leather_black')
    elif fid=='pot_rack_hanging':
        for x in (-W*.42,W*.42):b(x,H*.45,0,.65,H*.55,.65,'chrome')
        for z in (-D*.38,D*.38):b(0,H*.45,z,W,.7,.7,'steel_dark')
        for x in (-W*.3,0,W*.3):
            b(x,H*.2,0,.7,H*.27,.7,'chrome');stepped_disc(q,x,H*.07,0,W*.13,D*.32,1.1,'copper')
    elif fid=='surveillance_wall_cctv':
        for row in range(2):
            for col in range(3):
                x=(col-1)*W*.32;y=row*H*.49;b(x,y,0,W*.30,H*.45,1,'steel_dark');b(x,y+H*.03,.7,W*.26,H*.38,.5,'screen_pc')
        b(0,H*.96,0,W,.5,1,'steel_dark')
    elif fid=='clothing_gondola_double':
        for x in (-W*.44,W*.44):b(x,0,0,1,H,1,'steel_dark');b(x,0,0,2,1,D*.95,'steel_dark')
        for z in (-D*.32,D*.32):
            b(0,H*.85,z,W*.91,1,1,'chrome')
            for i in range(5):
                x=-W*.34+i*W*.17;b(x,H*.37,z,W*.11,H*.43,.8,('fabric_navy','fabric_emerald','linen_white','fabric_maroon','police_khaki')[i]);b(x,H*.77,z,W*.14,.6,.9,'brass')
    elif fid in ('shoe_display_wall','supermarket_produce_bin'):
        levels=4 if fid.startswith('shoe') else 3
        for i in range(levels):
            y=H*.05+i*H*.23;b(0,y,0,W,1,D,'wood_oak')
            for k in range(4):
                x=-W*.36+k*W*.24
                if levels==4:b(x,y+1,D*.12,W*.13,1.5,D*.5,'leather_black');b(x,y+2,D*.02,W*.13,1.3,D*.25,'leather_tan')
                else:stepped_disc(q,x,y+1,0,W*.09,D*.26,2,('paint_red','leaf_green','paint_saffron','marigold')[(k+i)%4])
        for x in (-W*.47,W*.47):b(x,0,-D*.4,1,H,1,'wood_sheesham')
    elif fid=='gas_stove_4burner':
        b(0,0,0,W,H*.8,D,'stainless');b(0,H*.82,0,W,1,D,'steel_dark')
        for x in (-W*.27,W*.27):
            for z in (-D*.27,D*.27):stepped_disc(q,x,H*.88,z,W*.15,D*.15,.7,'steel_dark');b(x,H*.92,z,W*.28,.4,.6,'chrome');b(x,H*.92,z,.6,.4,D*.28,'chrome')
        b(0,H*.18,D*.51,W*.78,H*.45,.6,'glass_tint')
        for x in (-W*.32,-W*.11,W*.11,W*.32):b(x,H*.68,D*.53,W*.07,H*.06,.8,'graphite')
    return q
