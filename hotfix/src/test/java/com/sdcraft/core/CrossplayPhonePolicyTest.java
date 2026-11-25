package com.sdcraft.core;

import org.bukkit.Material;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class CrossplayPhonePolicyTest {
    @Test void safeDefaultRejectsCustomFontEvenWithOldSettings() {
        assertFalse(CrossplayPhonePolicy.useCustomFontTitle(true, true, true));
        assertFalse(CrossplayPhonePolicy.useCustomFontTitle(true, true, false));
        assertFalse(CrossplayPhonePolicy.useCustomFontTitle(true, false, true));
    }

    @Test void legacyFontRequiresDeliberateOptOutAndLoadedPack() {
        assertTrue(CrossplayPhonePolicy.useCustomFontTitle(false, true, true));
        assertFalse(CrossplayPhonePolicy.useCustomFontTitle(false, false, true));
        assertFalse(CrossplayPhonePolicy.useCustomFontTitle(false, true, false));
    }

    @Test void allPhoneAppsHaveVanillaIconsAndUnknownValuesAreHarmless() {
        String[] ids = {"app_quoggle", "app_amazzo", "app_flippit", "app_arkpay",
            "app_zomatoo", "app_swiffy", "app_fashion", "app_property",
            "app_car_app", "app_maps", "app_garage", "app_bank", "app_loans",
            "app_taxi", "app_transport", "app_news", "app_police", "app_medical",
            "app_events", "app_missions", "app_careers", "app_contacts",
            "app_keys", "app_settings", "phone_shortcut", "hotbar_frame",
            "notification_frame"};
        for (String id : ids) {
            Material m = CrossplayPhonePolicy.iconMaterial(id);
            assertNotNull(m);
            assertTrue(m.isItem(), id);
            assertNotEquals(Material.AIR, m, id);
        }
        assertEquals(Material.PAPER, CrossplayPhonePolicy.iconMaterial("unknown"));
    }

    @Test void modeClearlyDisclosesPlatformLimits() {
        assertTrue(CrossplayPhonePolicy.mode(true).contains("server-only"));
        assertTrue(CrossplayPhonePolicy.mode(false).contains("not guaranteed"));
    }
}
