package com.sdcraft.core.vehicle;

import java.util.Objects;
import org.joml.Matrix4f;

/**
 * Converts an authored vehicle transform to the ItemDisplay coordinate system.
 *
 * <p>Minecraft renders an ItemDisplay as entity-orientation * transformation *
 * rotateY(180 degrees) * item-transform. The vehicle profiles and articulation
 * pivots are in the original model's coordinates, so the otherwise invisible
 * built-in rotation must be cancelled on the RIGHT of the authored matrix.
 * Rotating the entity instead would also rotate its seats/collision and would
 * still leave the animated wheel pivot in the wrong space.</p>
 *
 * <p>Reference: Mojang, Minecraft Snapshot 23w16a, "Display entity / Rendering
 * changes", https://www.minecraft.net/en-us/article/minecraft-snapshot-23w16a</p>
 */
public final class VehicleRenderTransform {
    private VehicleRenderTransform() {}

    /** Applied exactly once to each newly constructed body or animation matrix. */
    public static Matrix4f compensateItemFacing(Matrix4f authored) {
        return Objects.requireNonNull(authored, "Vehicle transform").rotateY((float) Math.PI);
    }
}
