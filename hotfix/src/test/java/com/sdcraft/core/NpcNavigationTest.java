package com.sdcraft.core;

import static org.junit.jupiter.api.Assertions.*;
import com.destroystokyo.paper.entity.Pathfinder;
import java.lang.reflect.Proxy;
import java.util.concurrent.atomic.AtomicInteger;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Mob;
import org.junit.jupiter.api.Test;

class NpcNavigationTest {
    @Test void citizensAbsentUsesPaperPathfinderForTheActualTarget() {
        Fixture fixture = new Fixture(true);
        Location target = new Location(fixture.world, 4, 68, 5);
        assertTrue(NpcNavigation.move(fixture.mob, null, target));
        assertEquals(1, fixture.moves.get());
        assertEquals(target, fixture.target);
        assertEquals(1.15, fixture.speed);
    }

    @Test void anUnloadedDestinationDoesNotStartNavigationOrLoadAChunk() {
        Fixture fixture = new Fixture(false);
        assertFalse(NpcNavigation.move(fixture.mob, null, new Location(fixture.world, 4, 68, 5)));
        assertEquals(0, fixture.moves.get());
        assertEquals(0, fixture.loads.get());
    }

    @Test void changingWorldOrInvalidatingAnActorCancelsTheMove() {
        Fixture first = new Fixture(true), second = new Fixture(true);
        assertFalse(NpcNavigation.move(first.mob, null, new Location(second.world, 4, 68, 5)));
        first.valid = false;
        assertFalse(NpcNavigation.move(first.mob, null, new Location(first.world, 4, 68, 5)));
        assertEquals(0, first.moves.get());
    }

    @Test void stoppingRetaliationStopsTheFallbackPathfinder() {
        Fixture fixture = new Fixture(true);
        NpcNavigation.stop(fixture.mob, null);
        assertEquals(1, fixture.stops.get());
    }

    private static final class Fixture {
        final AtomicInteger moves = new AtomicInteger(), stops = new AtomicInteger(), loads = new AtomicInteger();
        final World world;
        final Mob mob;
        Location target;
        double speed;
        boolean valid = true;
        Fixture(boolean loaded) {
            world = (World)Proxy.newProxyInstance(getClass().getClassLoader(), new Class<?>[]{World.class}, (proxy, method, args) -> {
                return switch (method.getName()) {
                    case "isChunkLoaded" -> loaded;
                    case "loadChunk", "getChunkAt" -> { loads.incrementAndGet(); throw new AssertionError("Must not load terrain"); }
                    case "equals" -> proxy == args[0];
                    case "hashCode" -> System.identityHashCode(proxy);
                    case "toString" -> "Loaded test world";
                    default -> throw new UnsupportedOperationException(method.getName());
                };
            });
            Pathfinder pathfinder = (Pathfinder)Proxy.newProxyInstance(getClass().getClassLoader(), new Class<?>[]{Pathfinder.class}, (proxy, method, args) -> {
                if (method.getName().equals("moveTo")) {
                    moves.incrementAndGet(); target = (Location)args[0]; speed = (double)args[1]; return true;
                }
                if (method.getName().equals("stopPathfinding")) { stops.incrementAndGet(); return null; }
                throw new UnsupportedOperationException(method.getName());
            });
            mob = (Mob)Proxy.newProxyInstance(getClass().getClassLoader(), new Class<?>[]{Mob.class}, (proxy, method, args) -> switch (method.getName()) {
                case "isValid" -> valid;
                case "getWorld" -> world;
                case "getPathfinder" -> pathfinder;
                case "toString" -> "Owned test mob";
                default -> throw new UnsupportedOperationException(method.getName());
            });
        }
    }
}
