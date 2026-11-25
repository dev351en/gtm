package com.sdcraft.clienthud;

import java.util.Map;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.resources.Identifier;

final class HudRenderer {
    static final int GOLD=0xFFD6AD59,WHITE=0xFFF3E9D6,MUTED=0xFF9AAEB3,PANEL=0xDD151B20,LINE=0xFF42545C;
    static final Map<String,String> BRANDS=Map.ofEntries(
            Map.entry("app_quoggle","quoggle"),Map.entry("app_amazzo","amazzo"),Map.entry("app_flippit","flippit"),
            Map.entry("app_arkpay","arkpay"),Map.entry("app_zomatoo","zomatoo"),Map.entry("app_swiffy","swiffy"),
            Map.entry("app_fashion","amora"),Map.entry("app_property","maya_residences"),Map.entry("app_car_app","sd_motors"),
            Map.entry("app_garage","sd_motors"),Map.entry("app_bank","indra_bank"),Map.entry("app_loans","indra_bank"),
            Map.entry("app_transport","indra_metro"),Map.entry("app_news","indra24"),Map.entry("app_events","rang_bharat"));

    static void extract(GuiGraphicsExtractor g,DeltaTracker delta){
        Minecraft mc=Minecraft.getInstance();HudState state=GtmHudClient.state();
        if(state==null||mc.player==null||mc.gui.hud.isHidden())return;
        HudLayout layout=HudLayout.of(g.guiWidth(),g.guiHeight());
        g.pose().pushMatrix();g.pose().scale(layout.scale(),layout.scale());
        hotbar(g,layout,mc);status(g,layout,state);minimap(g,layout,mc,state);
        boolean phoneScreen=mc.gui.screen() instanceof PhoneScreen;
        if(!phoneScreen)shortcut(g,layout);
        if(state.vehicle()!=null&&!phoneScreen)vehicle(g,layout,state.vehicle());
        g.pose().popMatrix();
    }
    static void panel(GuiGraphicsExtractor g,HudLayout.Box b){
        g.fill(b.x(),b.y(),b.right(),b.bottom(),PANEL);g.outline(b.x(),b.y(),b.width(),b.height(),LINE);
    }
    static void text(GuiGraphicsExtractor g,String text,int x,int y,int colour){g.text(Minecraft.getInstance().font,text,x,y,colour,true);}
    static void smallText(GuiGraphicsExtractor g,String text,int x,int y,int colour,float scale){
        g.pose().pushMatrix();g.pose().translate(x,y);g.pose().scale(scale,scale);
        text(g,text,0,0,colour);g.pose().popMatrix();
    }
    static void image(GuiGraphicsExtractor g,String category,String file,int x,int y,int w,int h){
        int source=category.equals("brands")?256:128;
        texture(g,GtmHudClient.id("textures/"+category+"/"+file+".png"),source,x,y,w,h);
    }
    static void texture(GuiGraphicsExtractor g,Identifier id,int source,int x,int y,int w,int h){
        g.blit(RenderPipelines.GUI_TEXTURED,id,x,y,0,0,w,h,source,source,source,source);
    }
    static void appIcon(GuiGraphicsExtractor g,String id,int x,int y,int size){
        String brand=BRANDS.get(id);image(g,brand==null?"apps":"brands",brand==null?id:brand,x,y,size,size);
    }
    static String shortened(String value,int pixels){return Minecraft.getInstance().font.plainSubstrByWidth(value,Math.max(0,pixels));}
    private static void hotbar(GuiGraphicsExtractor g,HudLayout l,Minecraft mc){
        int selected=mc.player.getInventory().getSelectedSlot();
        for(int i=0;i<9;i++){
            HudLayout.Box b=l.slot(i);g.fill(b.x()+2,b.y()+2,b.right()-2,b.bottom()-2,PANEL);
            image(g,"hud",i==selected?"hotbar_selected":"hotbar_frame",b.x(),b.y(),24,24);
            var stack=mc.player.getInventory().getItem(i);
            g.item(stack,b.x()+4,b.y()+4);g.itemDecorations(mc.font,stack,b.x()+4,b.y()+4);
            smallText(g,Integer.toString(i+1),b.x()+10,b.bottom()+1,i==selected?GOLD:MUTED,.65f);
        }
        image(g,"hud","phone_shortcut",l.hotbar().right()+5,12,22,22);
        smallText(g,"P",l.hotbar().right()+13,35,GOLD,.65f);
        int y=46;
        image(g,"hud","health",10,y-3,13,13);
        meter(g,26,y,68,mc.player.getHealth()/Math.max(1,mc.player.getMaxHealth()),0xFF63B786);
        image(g,"hud","armour",102,y-3,13,13);meter(g,118,y,48,mc.player.getArmorValue()/20.0,0xFF6AA7CF);
        smallText(g,"Food "+mc.player.getFoodData().getFoodLevel()+"/20",174,y-1,MUTED,.7f);
        if(!mc.player.getMainHandItem().isEmpty())smallText(g,shortened(mc.player.getMainHandItem().getHoverName().getString(),210),10,58,WHITE,.7f);
    }
    private static void meter(GuiGraphicsExtractor g,int x,int y,int w,double fraction,int colour){
        g.fill(x,y,x+w,y+4,0xBB283239);g.fill(x,y,x+(int)Math.round(w*Math.max(0,Math.min(1,fraction))),y+4,colour);
    }
    private static void status(GuiGraphicsExtractor g,HudLayout l,HudState state){
        HudLayout.Box b=l.status();panel(g,b);
        smallText(g,"GTM · "+shortened(state.city(),120),b.x()+7,b.y()+5,GOLD,.7f);
        for(int i=0;i<5;i++)image(g,"hud",i<state.wanted()?"wanted_star_filled":"wanted_star_empty",b.x()+48+i*19,b.y()+14,17,17);
        image(g,"hud","ark_symbol",b.x()+6,b.y()+32,17,17);
        text(g,state.wallet(),b.x()+28,b.y()+32,GOLD);
        smallText(g,"BANK  "+state.bank(),b.x()+28,b.y()+46,MUTED,.8f);
    }
    private static void minimap(GuiGraphicsExtractor g,HudLayout l,Minecraft mc,HudState state){
        HudLayout.Box b=l.map();int x=b.x(),y=b.y(),size=MinimapGeometry.DRAW_SIZE;
        if(GtmHudClient.MAP.ready())texture(g,TerrainMinimap.TEXTURE,128,x,y,size,size);
        image(g,"hud",GtmHudClient.circleMap?"minimap_circle":"minimap_rectangle",b.x(),b.y(),126,126);
        smallText(g,"N",b.x()+61,b.y()+6,WHITE,.7f);
        if(GtmHudClient.MAP.ready()){
            double cx=GtmHudClient.MAP.centerX(),cz=GtmHudClient.MAP.centerZ();
            for(HudState.Marker m:state.markers()){
                double dx=MinimapGeometry.drawOffset(m.x()-cx),dz=MinimapGeometry.drawOffset(m.z()-cz);
                if(!MinimapGeometry.markerVisible(GtmHudClient.circleMap,dx,dz))continue;
                String kind=switch(m.kind()){case "police","hospital","fuel","property","station","mission"->m.kind();default->"shop";};
                image(g,"hud","map_"+kind,(int)(x+size/2.0+dx)-5,(int)(y+size/2.0+dz)-5,10,10);
            }
            float px=(float)(x+size/2.0+MinimapGeometry.drawOffset(mc.player.getX()-cx));
            float py=(float)(y+size/2.0+MinimapGeometry.drawOffset(mc.player.getZ()-cz));
            g.pose().pushMatrix();g.pose().translate(px,py);g.pose().rotate((float)Math.toRadians(mc.player.getYRot()+180));
            image(g,"hud","player_arrow",-7,-7,14,14);g.pose().popMatrix();
        }else smallText(g,"Loading terrain…",b.x()+24,b.y()+59,MUTED,.7f);
        smallText(g,shortened(state.district(),150),b.x()+3,b.y()+127,WHITE,.75f);
        smallText(g,"M · "+(GtmHudClient.circleMap?"Circle":"Rectangle"),b.x()+3,b.y()+138,MUTED,.6f);
    }
    static void shortcut(GuiGraphicsExtractor g,HudLayout l){
        HudLayout.Box b=l.phoneShortcut();panel(g,b);image(g,"hud","phone_shortcut",b.x()+13,b.y()+2,28,28);
        smallText(g,"PHONE [P]",b.x()+6,b.y()+32,GOLD,.7f);
        smallText(g,"Alt · cursor",b.x()+5,b.y()+41,MUTED,.55f);
    }
    private static void vehicle(GuiGraphicsExtractor g,HudLayout l,HudState.Vehicle v){
        HudLayout.Box b=new HudLayout.Box(l.width()-176,l.height()-83,104,73);panel(g,b);
        image(g,"hud","speedometer_compact",b.x()+5,b.y()+4,22,22);
        text(g,Math.round(Math.abs(v.speed()))+" km/h",b.x()+31,b.y()+11,WHITE);
        boolean battery=v.energyKind().equalsIgnoreCase("battery")||v.energyKind().equalsIgnoreCase("electric");
        image(g,"hud",battery?"battery":"fuel",b.x()+6,b.y()+31,12,12);
        smallText(g,Math.round(v.fuel())+"% "+(battery?"battery":"fuel"),b.x()+24,b.y()+34,GOLD,.75f);
        image(g,"hud","engine_condition",b.x()+6,b.y()+47,12,12);
        smallText(g,Math.round(v.body())+"% body",b.x()+24,b.y()+50,MUTED,.75f);
        if(v.seats()>0)smallText(g,v.occupiedSeats()+" / "+v.seats()+" seats",b.x()+24,b.y()+63,MUTED,.65f);
    }
}
