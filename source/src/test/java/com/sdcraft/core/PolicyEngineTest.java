package com.sdcraft.core;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Policy Engine Deterministic Policy Tests")
class PolicyEngineTest {

    @Test
    @DisplayName("Robbery calculation enforces 25% wallet cap and $2000 maximum")
    void testRobberyMaximum() {
        // Zero or negative
        assertEquals(0L, PolicyEngine.robberyMaximumCents(0));
        assertEquals(0L, PolicyEngine.robberyMaximumCents(-100));

        // 25% of wallet
        assertEquals(12_500L, PolicyEngine.robberyMaximumCents(50_000L)); // $500 -> $125
        assertEquals(25_000L, PolicyEngine.robberyMaximumCents(100_000L)); // $1000 -> $250
        assertEquals(100_000L, PolicyEngine.robberyMaximumCents(400_000L)); // $4000 -> $1000

        // Hard cap at $2000 (200,000 cents)
        assertEquals(200_000L, PolicyEngine.robberyMaximumCents(800_000L)); // Exactly $2000
        assertEquals(200_000L, PolicyEngine.robberyMaximumCents(1_000_000L)); // > $2000 -> capped at $2000
        assertEquals(200_000L, PolicyEngine.robberyMaximumCents(100_000_000L)); // Capped
    }

    @Test
    @DisplayName("Taxi quote enforces base fare $25.00 plus $6.00 per 100 blocks")
    void testTaxiQuote() {
        // 0 blocks
        assertEquals(2500L, PolicyEngine.taxiQuoteCents(0));

        // 100 blocks -> $25 + $6 = $31 (3100 cents)
        assertEquals(3100L, PolicyEngine.taxiQuoteCents(100));

        // 250 blocks -> 2500 + 250*6 = 4000 cents ($40.00)
        assertEquals(4000L, PolicyEngine.taxiQuoteCents(250));

        // Invalid distances
        assertThrows(IllegalArgumentException.class, () -> PolicyEngine.taxiQuoteCents(-1));
        assertThrows(IllegalArgumentException.class, () -> PolicyEngine.taxiQuoteCents(1_000_001));
    }

    @Test
    @DisplayName("NPC hysteresis: spawn at <=64 blocks, persist until >96 blocks")
    void testNpcHysteresis() {
        // Inactive entity: should spawn if <= 64 blocks
        assertTrue(PolicyEngine.shouldBeActive(false, 0.0));
        assertTrue(PolicyEngine.shouldBeActive(false, 64.0));
        assertFalse(PolicyEngine.shouldBeActive(false, 64.1));
        assertFalse(PolicyEngine.shouldBeActive(false, 80.0));
        assertFalse(PolicyEngine.shouldBeActive(false, 96.0));

        // Active entity: remains active while <= 96 blocks
        assertTrue(PolicyEngine.shouldBeActive(true, 64.0));
        assertTrue(PolicyEngine.shouldBeActive(true, 80.0));
        assertTrue(PolicyEngine.shouldBeActive(true, 96.0));
        assertFalse(PolicyEngine.shouldBeActive(true, 96.1));
        assertFalse(PolicyEngine.shouldBeActive(true, 120.0));

        // Invalid distances
        assertFalse(PolicyEngine.shouldBeActive(false, -5.0));
        assertFalse(PolicyEngine.shouldBeActive(true, Double.NaN));
        assertFalse(PolicyEngine.shouldBeActive(true, Double.POSITIVE_INFINITY));
    }

    @Test
    @DisplayName("NPC hysteresis accepts lower proximity distances for a dense ambient pool")
    void configurableNpcHysteresis() {
        assertTrue(PolicyEngine.shouldBeActive(false, 56.0, 56.0, 80.0));
        assertFalse(PolicyEngine.shouldBeActive(false, 56.1, 56.0, 80.0));
        assertTrue(PolicyEngine.shouldBeActive(true, 80.0, 56.0, 80.0));
        assertFalse(PolicyEngine.shouldBeActive(true, 80.1, 56.0, 80.0));
        assertThrows(IllegalArgumentException.class,
                () -> PolicyEngine.shouldBeActive(false, 10.0, 80.0, 56.0));
    }

    @Test
    @DisplayName("Witness awareness check follows 70% immediate, 20% delayed, 10% silent")
    void testWitnessAwareness() {
        // 0..69: immediate (70%)
        assertEquals("immediate", PolicyEngine.witnessResult(0));
        assertEquals("immediate", PolicyEngine.witnessResult(35));
        assertEquals("immediate", PolicyEngine.witnessResult(69));

        // 70..89: delayed (20%)
        assertEquals("delayed", PolicyEngine.witnessResult(70));
        assertEquals("delayed", PolicyEngine.witnessResult(80));
        assertEquals("delayed", PolicyEngine.witnessResult(89));

        // 90..99: silent (10%)
        assertEquals("silent", PolicyEngine.witnessResult(90));
        assertEquals("silent", PolicyEngine.witnessResult(95));
        assertEquals("silent", PolicyEngine.witnessResult(99));

        // Invalid rolls
        assertThrows(IllegalArgumentException.class, () -> PolicyEngine.witnessResult(-1));
        assertThrows(IllegalArgumentException.class, () -> PolicyEngine.witnessResult(100));
    }

    @Test
    @DisplayName("Police responders dispatched per level 1/2/3 and bounded by free slots")
    void testPoliceResponders() {
        // Full availability (freeSlots >= severity)
        assertEquals(1, PolicyEngine.targetPoliceResponders(1, 6));
        assertEquals(2, PolicyEngine.targetPoliceResponders(2, 6));
        assertEquals(3, PolicyEngine.targetPoliceResponders(3, 6));

        // Constrained slots
        assertEquals(1, PolicyEngine.targetPoliceResponders(3, 1));
        assertEquals(2, PolicyEngine.targetPoliceResponders(3, 2));
        assertEquals(0, PolicyEngine.targetPoliceResponders(3, 0));

        // Invalid severity or negative slots
        assertThrows(IllegalArgumentException.class, () -> PolicyEngine.targetPoliceResponders(0, 5));
        assertThrows(IllegalArgumentException.class, () -> PolicyEngine.targetPoliceResponders(4, 5));
        assertThrows(IllegalArgumentException.class, () -> PolicyEngine.targetPoliceResponders(2, -1));
    }

    @Test
    @DisplayName("Money formatting properly prints dollars and cents")
    void testMoneyFormatting() {
        assertEquals("$0.00", PolicyEngine.money(0));
        assertEquals("$0.05", PolicyEngine.money(5));
        assertEquals("$1.50", PolicyEngine.money(150));
        assertEquals("$40.25", PolicyEngine.money(4025));
        assertEquals("$1000.00", PolicyEngine.money(100000));
    }
}
