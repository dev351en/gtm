package com.sdcraft.core;

import java.util.Collection;
import org.bukkit.util.BoundingBox;

/** Paper collision boxes are block-local; standing feet are at local y=1. */
final class NpcTerrain {
    private NpcTerrain() {}

    static boolean supportsStanding(Collection<BoundingBox> boxes) {
        boolean support = false;
        for (BoundingBox box : boxes) {
            boolean overlapsFeet = box.getMaxX() > .2 && box.getMinX() < .8
                    && box.getMaxZ() > .2 && box.getMinZ() < .8;
            if (overlapsFeet && box.getMaxY() > 1.00001) return false;
            if (Math.abs(box.getMaxY() - 1) < .00001 && box.getMinX() <= .2 && box.getMaxX() >= .8
                    && box.getMinZ() <= .2 && box.getMaxZ() >= .8) support = true;
        }
        return support;
    }
}
