package com.sdcraft.core;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

class NpcPopulationPolicyTest {
    @Test void aHundredPersonRosterStillHasThirtyTwoPhysicalActorsAndFourAdmissions() {
        var budget = NpcPopulationPolicy.budget(100, 6, 94, 0, 100);
        assertEquals(32, budget.total());
        assertEquals(6, budget.police());
        assertEquals(32, budget.other());
        assertEquals(4, budget.admissions());
        assertFalse(budget.permits(32, 2, 30, false));
        assertFalse(budget.permits(10, 6, 4, true));
    }

    @Test void serviceWorkersConsumeTheSamePhysicalAndNonPoliceBudget() {
        var budget = NpcPopulationPolicy.budget(32, 6, 30, 3, 4);
        assertEquals(29, budget.total());
        assertEquals(27, budget.other());
        assertFalse(budget.permits(27, 0, 27, false));
        assertTrue(budget.permits(27, 0, 27, true));
    }

    @Test void invalidExtremeConfigurationCannotOverflowIntoUnlimitedPopulation() {
        assertEquals(0, NpcPopulationPolicy.budget(Integer.MIN_VALUE, 6, Integer.MIN_VALUE, 4, 4).total());
        assertEquals(0, NpcPopulationPolicy.budget(32, 6, Integer.MIN_VALUE, 4, 4).other());
        assertEquals(0, NpcPopulationPolicy.budget(32, 6, 30, Integer.MAX_VALUE, -1).total());
        assertEquals(0, NpcPopulationPolicy.budget(32, 6, 30, 0, -1).admissions());
    }

    @Test void hysteresisRetainsNearbyActorsWithoutChurningAtTheActivationBoundary() {
        assertTrue(NpcPopulationPolicy.active(false, 55 * 55, 56, 80));
        assertFalse(NpcPopulationPolicy.active(false, 60 * 60, 56, 80));
        assertTrue(NpcPopulationPolicy.active(true, 60 * 60, 56, 80));
        assertFalse(NpcPopulationPolicy.active(true, 81 * 81, 56, 80));
        assertFalse(NpcPopulationPolicy.active(true, Double.POSITIVE_INFINITY, 56, 80));
        assertFalse(NpcPopulationPolicy.active(true, Double.NaN, 56, 80));
    }

    @Test void retaliationStopsOnLogoutProtectionDeathDownedExpiryOrLeavingTheWorld() {
        assertTrue(allowed(true, true, true, true, false, false, 10, 1_000, 2_000));
        assertFalse(allowed(false, true, true, true, false, false, 10, 1_000, 2_000));
        assertFalse(allowed(true, false, true, true, false, false, 10, 1_000, 2_000));
        assertFalse(allowed(true, true, false, true, false, false, 10, 1_000, 2_000));
        assertFalse(allowed(true, true, true, false, false, false, 10, 1_000, 2_000));
        assertFalse(allowed(true, true, true, true, true, false, 10, 1_000, 2_000));
        assertFalse(allowed(true, true, true, true, false, true, 10, 1_000, 2_000));
        assertFalse(allowed(true, true, true, true, false, false, 10, 2_001, 2_000));
        assertFalse(allowed(true, true, true, true, false, false, 25 * 25, 1_000, 2_000));
    }

    @Test void meleeCannotReachThroughWallsOrIgnoreItsCooldown() {
        assertTrue(NpcPopulationPolicy.mayStrike(4, true, 2_000, 0));
        assertFalse(NpcPopulationPolicy.mayStrike(4, false, 2_000, 0));
        assertFalse(NpcPopulationPolicy.mayStrike(9, true, 2_000, 0));
        assertFalse(NpcPopulationPolicy.mayStrike(4, true, 2_000, 1_500));
        assertFalse(NpcPopulationPolicy.mayStrike(Double.NaN, true, 2_000, 0));
    }

    @Test void explicitConversationHoldExpiresAndCombatAlwaysWins() {
        assertTrue(NpcPopulationPolicy.mayHoldConversation(true, true, true, true, false, 4, 1_000, 31_000));
        assertFalse(NpcPopulationPolicy.mayHoldConversation(true, true, true, true, false, 4, 31_000, 31_000));
        assertFalse(NpcPopulationPolicy.mayHoldConversation(true, true, true, true, true, 4, 1_000, 31_000));
    }

    @Test void conversationHoldCannotSurviveSessionLossDeathObstructionOrLeavingRange() {
        assertFalse(NpcPopulationPolicy.mayHoldConversation(false, true, true, true, false, 4, 1_000, 31_000));
        assertFalse(NpcPopulationPolicy.mayHoldConversation(true, false, true, true, false, 4, 1_000, 31_000));
        assertFalse(NpcPopulationPolicy.mayHoldConversation(true, true, false, true, false, 4, 1_000, 31_000));
        assertFalse(NpcPopulationPolicy.mayHoldConversation(true, true, true, false, false, 4, 1_000, 31_000));
        assertFalse(NpcPopulationPolicy.mayHoldConversation(true, true, true, true, false, 50, 1_000, 31_000));
        assertFalse(NpcPopulationPolicy.mayHoldConversation(true, true, true, true, false, Double.NaN, 1_000, 31_000));
    }

    private static boolean allowed(boolean auth, boolean alive, boolean survival, boolean sameWorld,
                                   boolean safe, boolean downed, double d, long now, long expires) {
        return NpcPopulationPolicy.mayRetaliate(auth, alive, survival, sameWorld, safe, downed, d, now, expires);
    }
}
