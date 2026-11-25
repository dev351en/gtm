package com.sdcraft.core;

import org.bukkit.Location;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Mob;

/** Uses Citizens when present, and Paper's actual pathfinder for the villager fallback. */
final class NpcNavigation {
    private NpcNavigation() {}

    static boolean move(Entity entity, Object citizens, Location target) {
        if (entity == null || target == null || target.getWorld() == null || !entity.isValid()
                || !entity.getWorld().equals(target.getWorld())
                || !target.getWorld().isChunkLoaded(target.getBlockX() >> 4, target.getBlockZ() >> 4)) {
            return false;
        }
        if (citizens != null) {
            try {
                Object navigator = citizens.getClass().getMethod("getNavigator").invoke(citizens);
                navigator.getClass().getMethod("setTarget", Location.class).invoke(navigator, target);
                return true;
            } catch (ReflectiveOperationException ignored) {
                // A mob-backed Citizens implementation can still use Paper below.
            }
        }
        if (entity instanceof Mob mob) return mob.getPathfinder().moveTo(target, 1.15);
        return false;
    }

    static void stop(Entity entity, Object citizens) {
        if (citizens != null) {
            try {
                Object navigator = citizens.getClass().getMethod("getNavigator").invoke(citizens);
                navigator.getClass().getMethod("cancelNavigation").invoke(navigator);
            } catch (ReflectiveOperationException ignored) { }
        }
        if (entity instanceof Mob mob && mob.isValid()) mob.getPathfinder().stopPathfinding();
    }
}
