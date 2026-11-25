package com.sdcraft.core;

import java.nio.charset.StandardCharsets;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class HudSessionTest {
    @Test void handshakeDoesNotAuthenticateOrAuthorizeAnAction() {
        HudSession session = new HudSession(1000);
        UUID login = UUID.randomUUID();
        assertTrue(session.fresh(1000));
        assertFalse(session.accept(login, login.toString(), 1, 1000));
        assertFalse(session.accept(null, "", 1, 1000));
    }
    @Test void accountSessionNonceSequenceAndRateAreAllRequired() {
        HudSession session = new HudSession(1000); UUID login = UUID.randomUUID(); session.authenticate(login);
        assertFalse(session.accept(login, UUID.randomUUID().toString(), 1, 1000));
        assertTrue(session.accept(login, login.toString(), 1, 1000));
        assertFalse(session.accept(login, login.toString(), 1, 1500));
        assertFalse(session.accept(login, login.toString(), 2, 1100));
        assertTrue(session.accept(login, login.toString(), 2, 1500));
        assertFalse(session.accept(login, login.toString(), Long.MAX_VALUE, 2000));
    }
    @Test void reconnectCannotReplayOldAccountOrCapability() {
        HudSession session = new HudSession(0); UUID old = UUID.randomUUID(); session.authenticate(old);
        assertTrue(session.accept(old, old.toString(), 1, 0));
        UUID next = UUID.randomUUID(); session.authenticate(next);
        assertFalse(session.accept(next, old.toString(), 2, 500));
        assertTrue(session.accept(next, next.toString(), 1, 500));
        assertFalse(session.accept(next, next.toString(), 2, 16_000));
        session.hello(17_000);
        assertTrue(session.accept(next, next.toString(), 2, 17_000));
        session.authenticate(null);
        assertFalse(session.accept(next, next.toString(), 3, 18_000));
    }
    @Test void malformedUtf8SizeAndNonObjectMessagesAreRejected() {
        assertThrows(Exception.class, () -> GtmClientHud.object(new byte[]{(byte)0xc3, 0x28}));
        assertThrows(IllegalArgumentException.class, () -> GtmClientHud.object(new byte[16_385]));
        assertThrows(IllegalArgumentException.class, () -> GtmClientHud.object("[]".getBytes(StandardCharsets.UTF_8)));
    }
    @Test void protocolDoesNotCoerceStringsOrFractionsToAuthority() throws Exception {
        var object = GtmClientHud.object("{\"v\":1,\"sequence\":1.5,\"session\":7}".getBytes(StandardCharsets.UTF_8));
        assertEquals(1, GtmClientHud.integer(object, "v"));
        assertThrows(IllegalArgumentException.class, () -> GtmClientHud.integer(object, "sequence"));
        assertThrows(IllegalArgumentException.class, () -> GtmClientHud.string(object, "session", 36));
        object.addProperty("v", "1");
        assertThrows(IllegalArgumentException.class, () -> GtmClientHud.integer(object, "v"));
    }
}
