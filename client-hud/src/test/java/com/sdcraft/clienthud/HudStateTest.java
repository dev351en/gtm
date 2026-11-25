package com.sdcraft.clienthud;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class HudStateTest {
    static String snapshot(String extra){return "{\"v\":1,\"active\":true,\"session\":\"test-session\",\"revision\":5,\"city\":\"Indraprastha\",\"district\":\"Station\",\"wanted\":2,\"wallet\":\"123.45\",\"bank\":\"678.90\""+extra+"}";}
    @Test void decodesOnlyKnownAppsAndBoundedVehicleMarkers(){
        HudState s=HudState.decode(snapshot(",\"apps\":[{\"id\":\"app_bank\",\"title\":\"Bank\",\"enabled\":true}],\"vehicle\":{\"speed\":-9,\"fuel\":92,\"body\":100,\"energyKind\":\"battery\",\"seats\":4,\"occupiedSeats\":2},\"markers\":[{\"id\":\"bank_01\",\"kind\":\"shop\",\"label\":\"Bank\",\"x\":10,\"z\":-20}]"));
        assertEquals("123.45",s.wallet());assertEquals(2,s.wanted());assertEquals(4,s.vehicle().seats());
        assertTrue(s.apps().getFirst().enabled());assertEquals(-20,s.markers().getFirst().z());
    }
    @Test void rejectsUnboundedUnsupportedAndControlBearingPackets(){
        assertThrows(RuntimeException.class,()->HudState.decode(snapshot("").replace("\"v\":1","\"v\":2")));
        assertThrows(RuntimeException.class,()->HudState.decode(snapshot("").replace("Station","x".repeat(65))));
        assertThrows(RuntimeException.class,()->HudState.decode(snapshot("").replace("Station","§cInjected")));
        assertThrows(RuntimeException.class,()->HudState.decode("{\"v\":1,\"active\":true,\"padding\":\""+"界".repeat(6000)+"\"}"));
    }
    @Test void rejectsUnknownAndDuplicateServiceActions(){
        assertThrows(RuntimeException.class,()->HudState.decode(snapshot(",\"apps\":[{\"id\":\"op_me\"}]")));
        assertThrows(RuntimeException.class,()->HudState.decode(snapshot(",\"apps\":[{\"id\":\"app_bank\"},{\"id\":\"app_bank\"}]")));
    }
    @Test void rejectsNonsensicalWorldAndEconomicState(){
        assertThrows(RuntimeException.class,()->HudState.decode(snapshot("").replace("\"wanted\":2","\"wanted\":6")));
        assertThrows(RuntimeException.class,()->HudState.decode(snapshot("").replace("\"revision\":5","\"revision\":-1")));
        assertThrows(RuntimeException.class,()->HudState.decode(snapshot(",\"vehicle\":{\"fuel\":101}")));
        assertThrows(RuntimeException.class,()->HudState.decode(snapshot(",\"markers\":[{\"x\":30000001}]")));
    }
    @Test void explicitRevocationContainsNoPrivateDisplayState(){assertNull(HudState.decode("{\"v\":1,\"active\":false}"));}
    @Test void offlineGuideUsesSnapshotAndDoesNotClaimExternalAi(){
        HudState s=HudState.decode(snapshot(""));
        assertTrue(LocalGuide.answer("bank balance",s).contains("123.45"));
        assertTrue(LocalGuide.answer("gun reload",s).contains("sneak + right-click"));
        assertTrue(LocalGuide.answer("invent me a mission",s).contains("do not invent"));
    }
}
