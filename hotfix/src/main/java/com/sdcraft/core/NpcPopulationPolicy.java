package com.sdcraft.core;

/** Bounds physical actors independently of the size of the persistent roster. */
final class NpcPopulationPolicy {
    static final int MAX_PHYSICAL = 32;
    static final int MAX_ADMISSIONS = 4;

    private NpcPopulationPolicy() {}

    record Budget(int total, int police, int other, int admissions) {
        boolean permits(int active, int activePolice, int activeOther, boolean officer) {
            return active < total && (officer ? activePolice < police : activeOther < other);
        }
    }

    static Budget budget(int configuredTotal, int configuredPolice, int configuredOther,
                         int serviceWorkers, int configuredAdmissions) {
        int workers = Math.max(0, Math.min(MAX_PHYSICAL, serviceWorkers));
        int total = Math.max(0, Math.max(0, Math.min(MAX_PHYSICAL, configuredTotal)) - workers);
        int police = Math.max(0, Math.min(total, configuredPolice));
        int other = Math.max(0, Math.min(total, Math.max(0, Math.min(MAX_PHYSICAL, configuredOther)) - workers));
        int admissions = Math.max(0, Math.min(MAX_ADMISSIONS, configuredAdmissions));
        return new Budget(total, police, other, admissions);
    }

    static boolean active(boolean alreadyActive, double nearestSquared,
                          double activation, double deactivation) {
        if (!Double.isFinite(nearestSquared) || nearestSquared < 0) return false;
        double enter = Math.max(8.0, Math.min(96.0, activation));
        double leave = Math.max(enter + 8.0, Math.min(128.0, deactivation));
        double limit = alreadyActive ? leave : enter;
        return nearestSquared <= limit * limit;
    }

    static boolean mayRetaliate(boolean authenticated, boolean alive, boolean survival,
                               boolean sameWorld, boolean protectedArea, boolean downed,
                               double distanceSquared, long now, long expires) {
        return authenticated && alive && survival && sameWorld && !protectedArea && !downed
                && now <= expires && Double.isFinite(distanceSquared)
                && distanceSquared >= 0 && distanceSquared <= 24.0 * 24.0;
    }

    static boolean mayStrike(double distanceSquared, boolean lineOfSight,
                             long now, long previousStrike) {
        return lineOfSight && distanceSquared >= 0 && distanceSquared <= 2.8 * 2.8
                && now - previousStrike >= 1_100;
    }

    static boolean mayHoldConversation(boolean authenticated, boolean sameSession, boolean alive,
                                       boolean lineOfSight, boolean combat, double distanceSquared,
                                       long now, long expires) {
        return authenticated && sameSession && alive && lineOfSight && !combat && now < expires
                && Double.isFinite(distanceSquared) && distanceSquared >= 0 && distanceSquared <= 49;
    }
}
