package com.sdcraft.core;

import static org.junit.jupiter.api.Assertions.*;
import java.util.List;
import org.bukkit.util.BoundingBox;
import org.junit.jupiter.api.Test;

class NpcTerrainTest {
    @Test void fullBlocksAndTopSlabsSupportCenteredStanding() {
        assertTrue(NpcTerrain.supportsStanding(List.of(new BoundingBox(0, 0, 0, 1, 1, 1))));
        assertTrue(NpcTerrain.supportsStanding(List.of(new BoundingBox(0, .5, 0, 1, 1, 1))));
    }

    @Test void theActualWallAnchorCannotEmbedAnNpcInTallCollision() {
        assertFalse(NpcTerrain.supportsStanding(List.of(new BoundingBox(.25, 0, .25, .75, 1.5, .75))));
        assertFalse(NpcTerrain.supportsStanding(List.of(new BoundingBox(0, 0, 0, 1, 1, 1),
                new BoundingBox(.25, 1, .25, .75, 1.5, .75))));
    }

    @Test void partialOrMissingSupportDefersRatherThanSpawningInAir() {
        assertFalse(NpcTerrain.supportsStanding(List.of()));
        assertFalse(NpcTerrain.supportsStanding(List.of(new BoundingBox(0, 0, 0, 1, .5, 1))));
        assertFalse(NpcTerrain.supportsStanding(List.of(new BoundingBox(0, 0, 0, 1, .5, 1),
                new BoundingBox(0, .5, .5, 1, 1, 1))));
    }
}
