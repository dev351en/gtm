package com.sdcraft.core;

/** Pure-Java, deterministic policy helpers. Financial values are integral cents. */
public final class PolicyEngine {
    private PolicyEngine() {}

    public static long robberyMaximumCents(long walletCents) {
        if (walletCents <= 0) return 0;
        // Avoid overflow for ordinary balances, guard wildly invalid values.
        return Math.min(walletCents / 4, 200_000L);
    }

    public static long taxiQuoteCents(long blocks) {
        if (blocks < 0 || blocks > 1_000_000L) throw new IllegalArgumentException("Invalid taxi distance");
        return Math.addExact(2_500L, Math.multiplyExact(blocks, 6L));
    }

    /** Hysteresis: spawn <=64 blocks; an active NPC remains until >96 blocks. */
    public static boolean shouldBeActive(boolean currentlyActive, double distanceBlocks) {
        return shouldBeActive(currentlyActive, distanceBlocks, 64.0, 96.0);
    }

    /** Configurable population hysteresis used by the ambient city pool. */
    public static boolean shouldBeActive(boolean currentlyActive, double distanceBlocks,
                                         double activationBlocks, double deactivationBlocks) {
        if (Double.isNaN(distanceBlocks) || distanceBlocks < 0 || Double.isInfinite(distanceBlocks))
            return false;
        if (activationBlocks <= 0 || deactivationBlocks < activationBlocks)
            throw new IllegalArgumentException("Invalid NPC activation distances");
        return currentlyActive ? distanceBlocks <= deactivationBlocks : distanceBlocks <= activationBlocks;
    }

    /** Returns immediate, delayed, or silent for a previously eligible witness. */
    public static String witnessResult(int roll0to99) {
        if (roll0to99 < 0 || roll0to99 > 99) throw new IllegalArgumentException("roll must be 0..99");
        return roll0to99 < 70 ? "immediate" : roll0to99 < 90 ? "delayed" : "silent";
    }

    /** Each level is 1..3. Target must be reduced if citywide police slots are exhausted. */
    public static int targetPoliceResponders(int severityLevel, int freePhysicalSlots) {
        if (severityLevel < 1 || severityLevel > 3 || freePhysicalSlots < 0)
            throw new IllegalArgumentException("bad severity or capacity");
        return Math.min(severityLevel, freePhysicalSlots);
    }

    public static String money(long cents) {
        return "$" + (cents / 100) + "." + String.format(java.util.Locale.ROOT, "%02d", Math.abs(cents % 100));
    }
}
