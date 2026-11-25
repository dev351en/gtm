package com.sdcraft.core;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CrossplayPhonePolicyTest {
    @Test void serverDeliveredJavaPackEnablesOriginalFontWithoutFabric() {
        assertTrue(CrossplayPhonePolicy.useCustomFontTitle(true, true));
        assertFalse(CrossplayPhonePolicy.useCustomFontTitle(true, false));
        assertFalse(CrossplayPhonePolicy.useCustomFontTitle(false, true));
        assertFalse(CrossplayPhonePolicy.useCustomFontTitle(false, false));
    }

    @Test void modelledPhoneRemainsServerAuthoritative() {
        assertEquals("server-only inventory + sidebar + map",
                CrossplayPhonePolicy.mode(true));
        assertTrue(CrossplayPhonePolicy.mode(false).contains("not guaranteed"));
    }
}
