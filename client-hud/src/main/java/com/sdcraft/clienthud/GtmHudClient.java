package com.sdcraft.clienthud;

import com.google.gson.JsonObject;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keymapping.v1.KeyMappingHelper;
import net.fabricmc.fabric.api.client.keymapping.v1.KeyMappingContext;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.hud.*;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.network.protocol.common.ServerboundCustomPayloadPacket;
import net.minecraft.network.protocol.game.ServerboundSetCarriedItemPacket;
import net.minecraft.resources.Identifier;
import com.mojang.blaze3d.platform.InputConstants;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class GtmHudClient implements ClientModInitializer {
    static final Logger LOG=LoggerFactory.getLogger("GTM-HUD");
    static final HudSession SESSION=new HudSession();
    static final TerrainMinimap MAP=new TerrainMinimap();
    static KeyMapping phoneKey,cursorKey,mapKey;
    static boolean circleMap=true;
    private static long lastHello;
    private static boolean wasActive;
    static Identifier id(String value){return Identifier.fromNamespaceAndPath("gtmhud",value);}
    static HudState state(){return SESSION.current(System.currentTimeMillis());}
    static boolean active(){return Minecraft.getInstance().player!=null&&state()!=null;}

    @Override public void onInitializeClient() {
        PayloadTypeRegistry.serverboundPlay().register(HudPayloads.Hello.TYPE,HudPayloads.Hello.CODEC);
        PayloadTypeRegistry.serverboundPlay().register(HudPayloads.Action.TYPE,HudPayloads.Action.CODEC);
        PayloadTypeRegistry.clientboundPlay().register(HudPayloads.State.TYPE,HudPayloads.State.CODEC);
        ClientPlayNetworking.registerGlobalReceiver(HudPayloads.State.TYPE,(payload,context)->{
            try {
                long now=System.currentTimeMillis();
                if(SESSION.accept(HudState.decode(payload.json()),now)&&SESSION.consumeOpenPhone(now))
                    context.client().gui.setScreen(new PhoneScreen(true));
            }
            catch(RuntimeException bad){SESSION.clear();LOG.warn("Rejected an invalid GTM HUD snapshot: {}",bad.getClass().getSimpleName());}
        });
        ClientPlayConnectionEvents.JOIN.register((handler,sender,client)->{reset();hello(client);});
        ClientPlayConnectionEvents.DISCONNECT.register((handler,client)->reset());
        KeyMapping.Category category=KeyMapping.Category.register(id("city"));
        phoneKey=KeyMappingHelper.registerKeyMapping(new KeyMapping("key.gtmhud.phone",InputConstants.KEY_P,category),KeyMappingContext.IN_GAME);
        cursorKey=KeyMappingHelper.registerKeyMapping(new KeyMapping("key.gtmhud.cursor",InputConstants.KEY_LALT,category),KeyMappingContext.IN_GAME);
        mapKey=KeyMappingHelper.registerKeyMapping(new KeyMapping("key.gtmhud.map",InputConstants.KEY_M,category),KeyMappingContext.IN_GAME);
        for(Identifier element:new Identifier[]{VanillaHudElements.HOTBAR,VanillaHudElements.HEALTH_BAR,
                VanillaHudElements.ARMOR_BAR,VanillaHudElements.FOOD_BAR,VanillaHudElements.INFO_BAR,
                VanillaHudElements.EXPERIENCE_LEVEL,VanillaHudElements.INFO_BAR_FOREGROUND,
                VanillaHudElements.HELD_ITEM_TOOLTIP,VanillaHudElements.SCOREBOARD}) {
            HudElementRegistry.replaceElement(element,original->(graphics,delta)->{
                if(!active()) original.extractRenderState(graphics,delta);
            });
        }
        // A GTM vehicle has its authoritative condition in the corner vehicle
        // panel. Keep vanilla mount health on other servers/ordinary mounts.
        HudElementRegistry.replaceElement(VanillaHudElements.MOUNT_HEALTH,original->(graphics,delta)->{
            HudState current=state();
            if(current==null||current.vehicle()==null)original.extractRenderState(graphics,delta);
        });
        HudElementRegistry.attachElementBefore(VanillaHudElements.CHAT,id("city_hud"),HudRenderer::extract);
        ClientTickEvents.START_CLIENT_TICK.register(GtmHudClient::keys);
        ClientTickEvents.END_CLIENT_TICK.register(GtmHudClient::tick);
        LOG.info("Optional GTM four-corner HUD initialized for Minecraft26.3; vanilla rendering remains until authenticated server capability.");
    }
    private static void reset(){SESSION.clear();lastHello=0;wasActive=false;MAP.clear();}
    private static void hello(Minecraft client){
        if(client.getConnection()==null)return;
        // Paper and vanilla servers need no Fabric negotiation; unknown optional
        // plugin channels are ignored. Never change the server or require the mod.
        client.getConnection().send(new ServerboundCustomPayloadPacket(new HudPayloads.Hello("{\"v\":1,\"client\":\"gtm-hud-1.0.0\"}")));
        lastHello=System.currentTimeMillis();
    }
    private static void tick(Minecraft client){
        if(client.player==null||client.level==null)return;
        long now=System.currentTimeMillis();
        if(now-lastHello>=5000)hello(client);
        boolean active=active();
        if(!active){
            if(wasActive){MAP.clear();if(client.gui.screen() instanceof PhoneScreen)client.gui.setScreen(null);}
            wasActive=false;return;
        }
        wasActive=true; MAP.tick(client,circleMap);
    }
    private static void keys(Minecraft client){
        // Run before vanilla handles P (Social Interactions). Rebinding a user's
        // controls is unnecessary: only the current authenticated GTM press is
        // consumed, and ordinary servers retain the original shortcut.
        boolean phone=false,cursor=false,map=false;
        while(phoneKey.consumeClick())phone=true;
        while(cursorKey.consumeClick())cursor=true;
        while(mapKey.consumeClick())map=!map;
        if(!active()||client.gui.screen()!=null)return;
        if(map)circleMap=!circleMap;
        if(phone||cursor){
            KeyMapping used=phone?phoneKey:cursorKey;
            for(KeyMapping other:client.options.keyMappings)
                if(other!=used&&other.same(used))while(other.consumeClick()){}
            client.gui.setScreen(new PhoneScreen(phone));
        }
    }
    static boolean sendApp(HudState.App app){
        HudState s=state();Minecraft client=Minecraft.getInstance();
        if(s==null||!app.enabled()||client.getConnection()==null)return false;
        JsonObject message=new JsonObject();message.addProperty("v",1);message.addProperty("session",s.session());
        message.addProperty("sequence",SESSION.nextSequence());message.addProperty("action","app");message.addProperty("app",app.id());
        client.getConnection().send(new ServerboundCustomPayloadPacket(new HudPayloads.Action(message.toString())));
        return true;
    }
    static void selectSlot(int slot){
        Minecraft client=Minecraft.getInstance();
        if(slot<0||slot>8||!active()||client.getConnection()==null)return;
        client.player.getInventory().setSelectedSlot(slot);
        client.getConnection().send(new ServerboundSetCarriedItemPacket(slot));
    }
}
