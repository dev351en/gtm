package com.sdcraft.core.gtm;

/** Server-authoritative, platform-neutral vehicle condition and energy rules. */
public record VehicleState(double capacity, double energy, double health, double distance) {
    public VehicleState {
        if (!Double.isFinite(capacity) || capacity <= 0 || !Double.isFinite(energy) || energy < 0 || energy > capacity
                || !Double.isFinite(health) || health < 0 || health > 100 || !Double.isFinite(distance) || distance < 0)
            throw new IllegalArgumentException("Invalid vehicle state");
    }
    public enum Condition { NORMAL, DAMAGED, HEAVY, FAILURE, CRITICAL, DESTROYED }
    public Condition condition() {
        if (health == 0) return Condition.DESTROYED;
        if (health <= 10) return Condition.CRITICAL;
        if (health <= 25) return Condition.FAILURE;
        if (health <= 50) return Condition.HEAVY;
        if (health <= 75) return Condition.DAMAGED;
        return Condition.NORMAL;
    }
    public boolean canPropel() { return energy > 0 && health > 25; }
    public double energyPercent() { return energy / capacity * 100; }
    public record Travel(VehicleState state, double allowedDistance) {}
    /** Inputs are game units: blocks and energy units per block, not real-world specifications. */
    public Travel travel(double requested, double rate) {
        nonnegative(requested); nonnegative(rate);
        if (!canPropel() || requested == 0) return new Travel(this, 0);
        double allowed = rate == 0 ? requested : Math.min(requested, energy / rate);
        double cost = allowed * rate;
        return new Travel(new VehicleState(capacity, Math.max(0, energy - cost), health, distance + allowed), allowed);
    }
    public VehicleState idle(double cost) {
        nonnegative(cost);
        if (!canPropel()) return this;
        return new VehicleState(capacity, Math.max(0, energy - cost), health, distance);
    }
    public VehicleState refill(double amount) {
        nonnegative(amount);
        if (health == 0) throw new IllegalStateException("Destroyed vehicle requires recovery");
        return new VehicleState(capacity, energy + Math.min(amount, capacity - energy), health, distance);
    }
    public record Damage(VehicleState state, boolean newlyDestroyed) {}
    public Damage damage(double amount) {
        nonnegative(amount);
        double next = Math.max(0, health - amount);
        return new Damage(new VehicleState(capacity, energy, next, distance), health > 0 && next == 0);
    }
    public VehicleState repair(double amount) {
        nonnegative(amount);
        if (health == 0) throw new IllegalStateException("Destroyed vehicle requires recovery");
        return new VehicleState(capacity, energy, health + Math.min(amount, 100 - health), distance);
    }
    private static void nonnegative(double v) {
        if (!Double.isFinite(v) || v < 0) throw new IllegalArgumentException("Expected finite nonnegative value");
    }
}
