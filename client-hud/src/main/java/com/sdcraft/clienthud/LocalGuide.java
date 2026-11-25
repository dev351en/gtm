package com.sdcraft.clienthud;

import java.util.Locale;

/** Explicit offline city guide backed by the current authenticated HUD snapshot. */
final class LocalGuide {
    static String answer(String question,HudState state){
        String q=question.toLowerCase(Locale.ROOT).trim();
        if(q.matches(".*(money|bank|wallet|balance|ark|paisa).*"))return "Your wallet is ARK "+state.wallet()+" and your bank balance is ARK "+state.bank()+". Open ARKPay or Bank in the phone for the server's account services. Purchases always require server confirmation.";
        if(q.matches(".*(gun|weapon|ammo|reload|shoot|fire|bandook).*"))return "Open Equipment from the phone or use /gun. Right-click fires; sneak + right-click reloads with matching ammunition. Combat is blocked in protected safe areas. The selected gun is the real item in your top-left hotbar.";
        if(q.matches(".*(drive|car|vehicle|fuel|garage|seat|gaadi).*"))return "Open Car App or Garage. W accelerates, A/D steer, S brakes before reversing, Space brakes and Shift exits. The lower-right instruments show live speed, fuel or battery, body condition and seats. Your current vehicle: "+(state.vehicle()==null?"none.":Math.round(state.vehicle().fuel())+"% energy remaining.");
        if(q.matches(".*(police|wanted|star|arrest).*"))return "Your current wanted level is "+state.wanted()+" of 5. The stars at the upper right come from the server. Police services are available through the phone; ordinary debt alone is not a police assault event.";
        if(q.matches(".*(map|where|location|district|gps).*"))return "You are in "+state.district()+", "+state.city()+". The bottom-left map shows actual loaded surface terrain with north at the top. Your arrow follows your position and heading. M switches circular and rectangular views; available service markers come from the server.";
        if(q.matches(".*(phone|control|help|inventory|hotbar).*"))return "P opens or closes this phone. Alt enables the HUD cursor: click a hotbar slot to select it or click the phone. Keys 1–9 and the mouse wheel still select the real inventory. Esc returns to play. This phone does not pause the server.";
        return "I can explain weapons, driving, money, wanted level, the minimap and phone controls. Ask about one of these topics. This is the local city guide; I do not invent live quests, transactions or external AI answers.";
    }
}
