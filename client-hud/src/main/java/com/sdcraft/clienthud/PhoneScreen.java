package com.sdcraft.clienthud;

import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.KeyEvent;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.network.chat.Component;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.input.CharacterEvent;
import net.minecraft.client.input.PreeditEvent;

/** A non-pausing screen releases the cursor while drawing only the phone panel. */
final class PhoneScreen extends Screen {
    private boolean expanded;
    private boolean guide;
    private HudState.App selected;
    private String reply="Ask about weapons, driving, money or the city map.";
    private EditBox question;
    private HudLayout layout;

    PhoneScreen(boolean expanded){super(Component.literal("GTM Phone"));this.expanded=expanded;}
    @Override public boolean isPauseScreen(){return false;}
    @Override public boolean isInGameUi(){return true;}
    @Override public void extractBackground(GuiGraphicsExtractor g,int x,int y,float delta){}
    @Override protected void init(){
        layout=HudLayout.of(width,height);
        HudLayout.Box p=layout.phone();
        question=new EditBox(font,p.x()+9,p.bottom()-48,p.width()-18,18,Component.literal("Ask JEEVA"));
        question.setMaxLength(180);question.setHint(Component.literal("Ask JEEVA…"));question.setBordered(true);
        addRenderableWidget(question);question.setVisible(guide&&expanded);
    }
    @Override public void tick(){if(!GtmHudClient.active())onClose();}
    @Override public void extractRenderState(GuiGraphicsExtractor g,int mouseX,int mouseY,float delta){
        HudState state=GtmHudClient.state();if(state==null)return;
        layout=HudLayout.of(width,height);double mx=mouseX/layout.scale(),my=mouseY/layout.scale();
        g.pose().pushMatrix();g.pose().scale(layout.scale(),layout.scale());
        if(!expanded){HudRenderer.shortcut(g,layout);g.pose().popMatrix();return;}
        HudLayout.Box p=layout.phone();HudRenderer.panel(g,p);g.outline(p.x(),p.y(),p.width(),p.height(),HudRenderer.GOLD);
        HudRenderer.image(g,"brands","gtm",p.x()+7,p.y()+4,17,17);
        HudRenderer.text(g,guide?"JEEVA":selected==null?"GTM Phone":HudRenderer.shortened(selected.title(),119),p.x()+30,p.y()+8,HudRenderer.GOLD);
        HudRenderer.smallText(g,"×",p.right()-13,p.y()+6,HudRenderer.MUTED,1f);
        if(guide)drawGuide(g,p,(int)mx,(int)my,delta);
        else if(selected!=null)drawApp(g,p,state);
        else {
            String hover="City apps";
            for(int i=0;i<state.apps().size();i++){
                HudState.App app=state.apps().get(i);HudLayout.Box b=layout.app(i);
                g.fill(b.x(),b.y(),b.right(),b.bottom(),b.contains(mx,my)?0xFF354740:0xCC222D32);
                if(b.contains(mx,my))hover=app.title()+(app.enabled()?"":" · unavailable");
                HudRenderer.appIcon(g,app.id(),b.x()+6,b.y()+1,22);
                if(!app.enabled())g.fill(b.x(),b.y(),b.right(),b.bottom(),0x88303A3E);
            }
            HudRenderer.smallText(g,HudRenderer.shortened(hover,186),p.x()+9,p.bottom()-30,HudRenderer.MUTED,.75f);
        }
        button(g,layout.homeButton(),"HOME",mx,my);button(g,layout.guideButton(),"JEEVA",mx,my);
        g.pose().popMatrix();
    }
    private void drawApp(GuiGraphicsExtractor g,HudLayout.Box p,HudState state){
        HudRenderer.appIcon(g,selected.id(),p.x()+60,p.y()+31,46);
        String description=switch(selected.id()){
            case "app_bank","app_arkpay","app_loans"->"Wallet  ARK "+state.wallet()+"\nBank    ARK "+state.bank()+"\n\nAccount actions are validated by the server.";
            case "app_maps"->state.district()+", "+state.city()+"\n\nYour live terrain map is at the lower left. M switches its shape. Open the city service to choose a route.";
            case "app_car_app","app_garage"->"Your owned vehicles and garage. Open the service to select, call or manage a vehicle.";
            case "app_settings"->"Press M to switch the map between circle and rectangle.\n\nP opens the phone. Alt enables the HUD cursor. Keys 1–9 select your inventory.";
            default->"Open "+selected.title()+" to use its existing city service. Availability, prices and ownership are checked by the server.";
        };
        g.textWithWordWrap(font,Component.literal(description),p.x()+12,p.y()+88,p.width()-24,HudRenderer.WHITE);
        HudLayout.Box open=openButton();button(g,open,selected.enabled()?"OPEN SERVICE":"UNAVAILABLE",-1,-1);
    }
    private HudLayout.Box openButton(){HudLayout.Box p=layout.phone();return new HudLayout.Box(p.x()+12,p.bottom()-48,p.width()-24,18);}
    private void drawGuide(GuiGraphicsExtractor g,HudLayout.Box p,int mx,int my,float delta){
        HudRenderer.smallText(g,"LOCAL CITY GUIDE",p.x()+10,p.y()+25,HudRenderer.MUTED,.65f);
        g.pose().pushMatrix();g.pose().translate(p.x()+10,p.y()+40);g.pose().scale(.8f,.8f);
        g.textWithWordWrap(font,Component.literal(reply),0,0,(int)((p.width()-20)/.8),HudRenderer.WHITE);
        g.pose().popMatrix();
        question.setVisible(true);question.extractRenderState(g,mx,my,delta);
        HudRenderer.smallText(g,"Enter to ask · private",p.x()+12,p.bottom()-29,HudRenderer.MUTED,.65f);
    }
    private static void button(GuiGraphicsExtractor g,HudLayout.Box b,String label,double mx,double my){
        g.fill(b.x(),b.y(),b.right(),b.bottom(),b.contains(mx,my)?0xFF336653:0xFF263A36);
        HudRenderer.smallText(g,label,b.x()+5,b.y()+4,HudRenderer.GOLD,.7f);
    }
    @Override public boolean mouseClicked(MouseButtonEvent event,boolean doubleClick){
        if(event.button()!=InputConstants.MOUSE_BUTTON_LEFT)return super.mouseClicked(event,doubleClick);
        double x=event.x()/layout.scale(),y=event.y()/layout.scale();
        for(int i=0;i<9;i++)if(layout.slot(i).contains(x,y)){GtmHudClient.selectSlot(i);return true;}
        if(layout.map().contains(x,y)){GtmHudClient.circleMap=!GtmHudClient.circleMap;return true;}
        if(new HudLayout.Box(layout.hotbar().right()+3,10,28,28).contains(x,y)||(!expanded&&layout.phoneShortcut().contains(x,y))){expanded=true;return true;}
        if(!expanded)return true;
        HudLayout.Box p=layout.phone();
        if(new HudLayout.Box(p.right()-20,p.y(),20,22).contains(x,y)){onClose();return true;}
        if(layout.homeButton().contains(x,y)){guide=false;selected=null;question.setVisible(false);question.setFocused(false);return true;}
        if(layout.guideButton().contains(x,y)){guide=true;selected=null;question.setVisible(true);question.setFocused(true);return true;}
        if(guide){
            MouseButtonEvent adjusted=new MouseButtonEvent(x,y,event.buttonInfo());
            return question.mouseClicked(adjusted,doubleClick);
        }
        HudState state=GtmHudClient.state();if(state==null)return true;
        if(selected==null){
            for(int i=0;i<state.apps().size();i++)if(layout.app(i).contains(x,y)){selected=state.apps().get(i);return true;}
        }else if(openButton().contains(x,y)&&GtmHudClient.sendApp(selected)){
            // The popup stays visible until an authoritative service opens.
            // No inventory, money or permission changes occur in the client.
        }
        return true;
    }
    @Override public boolean charTyped(CharacterEvent event){
        return guide&&question.isFocused()?question.charTyped(event):super.charTyped(event);
    }
    @Override public boolean preeditUpdated(PreeditEvent event){
        return guide&&question.isFocused()?question.preeditUpdated(event):super.preeditUpdated(event);
    }
    @Override public boolean keyPressed(KeyEvent event){
        if(event.key()==InputConstants.KEY_ESCAPE){onClose();return true;}
        if(guide&&question.isFocused()){
            if(event.key()==InputConstants.KEY_RETURN||event.key()==InputConstants.KEY_NUMPADENTER){
                HudState s=GtmHudClient.state();if(s!=null)reply=LocalGuide.answer(question.getValue(),s);question.setValue("");return true;
            }
            return question.keyPressed(event);
        }
        if(GtmHudClient.phoneKey.matches(event)||GtmHudClient.cursorKey.matches(event)){onClose();return true;}
        if(event.key()>=InputConstants.KEY_1&&event.key()<=InputConstants.KEY_9){GtmHudClient.selectSlot(event.key()-InputConstants.KEY_1);return true;}
        return super.keyPressed(event);
    }
}
