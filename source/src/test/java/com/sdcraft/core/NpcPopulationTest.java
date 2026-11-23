package com.sdcraft.core;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class NpcPopulationTest {
    @Test
    @DisplayName("100-person target generates 80 ambient profiles after 20 named NPCs")
    void ambientPopulationBudget() {
        assertEquals(80, NpcService.generatedAmbientCount(100, 20));
        assertEquals(0, NpcService.generatedAmbientCount(20, 20));
        assertEquals(0, NpcService.generatedAmbientCount(10, 20));
    }

    @Test
    @DisplayName("Tough pedestrian selection is deterministic and respects percentage bounds")
    void deterministicToughSelection() {
        int tough = 0;
        for (int i = 0; i < 80; i++) if (NpcService.deterministicTough(i, 30)) tough++;
        assertTrue(tough >= 20 && tough <= 28, "30% policy should generate a stable minority of tough NPCs");
        assertFalse(NpcService.deterministicTough(5, 0));
        assertTrue(NpcService.deterministicTough(5, 100));
    }

    @Test
    @DisplayName("Invalid population policy is rejected")
    void invalidPopulationPolicy() {
        assertThrows(IllegalArgumentException.class, () -> NpcService.generatedAmbientCount(-1, 20));
        assertThrows(IllegalArgumentException.class, () -> NpcService.deterministicTough(0, 101));
    }
}
