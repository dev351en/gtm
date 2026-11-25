package com.sdcraft.core.gtm;

import static org.junit.jupiter.api.Assertions.*;
import java.util.*;
import org.junit.jupiter.api.Test;

class AuthenticationStateTest {
    @Test void unverifiedConnectionNeverStartsAuthenticated() {
        var state = new AuthenticationState();
        UUID id = UUID.randomUUID();
        var connection = state.begin(id, 1000, 120_000);
        assertTrue(state.current(connection));
        assertFalse(state.authenticated(id, 1001));
        assertFalse(state.authenticated(UUID.randomUUID(), 1001));
        assertTrue(state.authenticate(connection, 1001, 600_000));
        assertTrue(state.authenticated(id, 1002));
    }

    @Test void hashCompletionFromDisconnectedSessionCannotAuthenticateReplacement() {
        var state = new AuthenticationState();
        UUID id = UUID.randomUUID();
        var previous = state.begin(id, 1000, 120_000);
        state.end(id);
        var next = state.begin(id, 2000, 120_000);
        assertNotEquals(previous.nonce(), next.nonce());
        assertFalse(state.authenticate(previous, 2001, 600_000));
        assertFalse(state.authenticated(id, 2002));
        assertTrue(state.authenticate(next, 2003, 600_000));
    }

    @Test void timeoutAndLogoutInvalidateAccessAndLateCompletions() {
        var state = new AuthenticationState();
        UUID id = UUID.randomUUID();
        var expired = state.begin(id, 1000, 100);
        assertFalse(state.authenticate(expired, 1100, 1000));
        var connection = state.begin(id, 2000, 100);
        assertTrue(state.authenticate(connection, 2010, 1000));
        assertTrue(state.authenticated(id, 3009));
        assertFalse(state.authenticated(id, 3010));
        state.end(id);
        assertFalse(state.current(connection));
        assertFalse(state.authenticate(connection, 3011, 1000));
    }

    @Test void accountBudgetSurvivesReconnectAndIpChanges() {
        var state = new AuthenticationState();
        UUID id = UUID.randomUUID();
        for (int i = 0; i < 5; i++) assertTrue(state.acquireAttempt(id, "network-" + i, 1000 + i));
        state.begin(id, 2000, 120_000);
        state.end(id);
        assertFalse(state.acquireAttempt(id, "new-network", 2001));
        assertTrue(state.acquireAttempt(id, "new-network", 301_000));
    }

    @Test void networkBudgetPreventsAccountSprayingAndIsNotResetBySuccessfulLogin() {
        var state = new AuthenticationState();
        for (int i = 0; i < 20; i++) {
            UUID id = UUID.randomUUID();
            assertTrue(state.acquireAttempt(id, "shared-network", 1000 + i));
            state.authenticatedAttempt(id);
        }
        assertFalse(state.acquireAttempt(UUID.randomUUID(), "shared-network", 2000));
        assertTrue(state.acquireAttempt(UUID.randomUUID(), "another-network", 2000));
    }

    @Test void authenticatedAccountCanRetryWithoutClearingOtherPeoplesLimits() {
        var state = new AuthenticationState();
        UUID first = UUID.randomUUID(), second = UUID.randomUUID();
        for (int i = 0; i < 5; i++) {
            assertTrue(state.acquireAttempt(first, "a", i));
            assertTrue(state.acquireAttempt(second, "b", i));
        }
        state.authenticatedAttempt(first);
        assertTrue(state.acquireAttempt(first, "a", 10));
        assertFalse(state.acquireAttempt(second, "b", 10));
    }

    @Test void unknownIdentityFloodHasBoundedBookkeepingAndRecoversAfterWindow() {
        var state = new AuthenticationState();
        for (int i = 0; i < 4096; i++)
            assertTrue(state.acquireAttempt(UUID.randomUUID(), "network-" + i, 1000));
        assertFalse(state.acquireAttempt(UUID.randomUUID(), "overflow-network", 1000));
        assertTrue(state.acquireAttempt(UUID.randomUUID(), "next-window", 301_000));
    }

    @Test void passphrasesWithSpacesQuotesAndUnicodeReachHasherWithoutTruncation() {
        assertEquals(List.of("Mumbai monsoon café", "Mumbai monsoon café"),
            AuthenticationState.arguments("\"Mumbai monsoon café\" \"Mumbai monsoon café\""));
        assertEquals(List.of("A \"quoted\" password"), AuthenticationState.arguments("\"A \\\"quoted\\\" password\""));
        assertEquals(List.of("C:\\test"), AuthenticationState.arguments("\"C:\\\\test\""));
        assertEquals(List.of("single\\slash", "phrase"), AuthenticationState.arguments("single\\slash phrase"));
        assertEquals(List.of("pass-one", "pass-two"), AuthenticationState.arguments("pass-one   pass-two"));
        assertThrows(IllegalArgumentException.class, () -> AuthenticationState.arguments("\"not closed"));
        assertThrows(IllegalArgumentException.class, () -> AuthenticationState.arguments("x".repeat(1025)));
        assertThrows(IllegalArgumentException.class, () -> AuthenticationState.arguments("first\nsecond"));
    }
}
