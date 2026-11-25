package com.sdcraft.clienthud;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class HudSessionTest {
    @Test void explicitPhoneRequestOpensOncePerAcceptedRevision(){
        HudSession s=new HudSession();HudState first=HudState.decode(HudStateTest.snapshot(",\"openPhone\":true"));
        s.accept(first,1000);assertTrue(s.consumeOpenPhone(1000));assertFalse(s.consumeOpenPhone(1000));
        s.accept(first,1001);assertFalse(s.consumeOpenPhone(1001));
        s.accept(HudState.decode(HudStateTest.snapshot(",\"openPhone\":true").replace("\"revision\":5","\"revision\":6")),1002);
        assertTrue(s.consumeOpenPhone(1002));s.accept(null,1003);assertFalse(s.consumeOpenPhone(1003));
    }
    @Test void lostServerConnectionExpiresPrivateHudAndAllowsVanillaFallback(){
        HudSession s=new HudSession();s.accept(HudState.decode(HudStateTest.snapshot("")),1000);
        assertNotNull(s.current(11000));assertNull(s.current(11001));
    }
    @Test void clockReversalAndLogoutClearState(){
        HudSession s=new HudSession();s.accept(HudState.decode(HudStateTest.snapshot("")),1000);assertNull(s.current(999));
        s.accept(HudState.decode(HudStateTest.snapshot("")),1000);s.accept(null,1001);assertNull(s.current(1001));
    }
    @Test void staleRevisionCannotRefreshHeartbeatOrOverwriteLatestMoney(){
        HudSession s=new HudSession();s.accept(HudState.decode(HudStateTest.snapshot("")),1000);
        assertFalse(s.accept(HudState.decode(HudStateTest.snapshot("").replace("\"revision\":5","\"revision\":4").replace("123.45","999999")),9000));
        assertEquals("123.45",s.current(9000).wallet());assertNull(s.current(11001));
    }
    @Test void newLoginResetsActionSequenceAndClearRemovesEntitlement(){
        HudSession s=new HudSession();s.accept(HudState.decode(HudStateTest.snapshot("")),1000);
        assertEquals(1,s.nextSequence());assertEquals(2,s.nextSequence());
        s.accept(HudState.decode(HudStateTest.snapshot("").replace("test-session","new-login")),1001);
        assertEquals(1,s.nextSequence());s.clear();assertNull(s.current(1002));
    }
}
