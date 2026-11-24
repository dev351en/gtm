package com.sdcraft.core.gtm;

import java.util.*;

/** Portable game-domain rules. All money is integer ARK cents; no Bukkit dependency. */
public final class CivicRules {
    private CivicRules() {}
    public static final long MAX_PRINCIPAL = 100_000_000L;
    public record Loan(long principal, long total, int days, int grace, int elapsed, long paid) {
        public Loan {
            if (principal <= 0 || principal > MAX_PRINCIPAL || total < principal || total > principal * 2
                || days < 1 || days > 365 || grace < 0 || grace > 30 || elapsed < 0 || elapsed > 395
                || paid < 0 || paid > total) throw new IllegalArgumentException("Invalid loan");
        }
        public static Loan issue(long principal, int basisPoints, int days, int grace) {
            if (principal <= 0 || principal > MAX_PRINCIPAL || basisPoints < 0 || basisPoints > 10000)
                throw new IllegalArgumentException("Invalid loan terms");
            long interest = (principal * basisPoints + 9999) / 10000;
            return new Loan(principal, principal + interest, days, grace, 0, 0);
        }
        private long scheduled(int day) { return (total * Math.min(days, Math.max(0, day)) + days - 1) / days; }
        public long outstanding() { return total - paid; }
        public long due() { return Math.max(0, scheduled(elapsed) - paid); }
        public boolean overdue() { return paid < scheduled(elapsed - grace); }
        public Loan advanceActiveDay() { return new Loan(principal, total, days, grace, Math.min(days + grace, elapsed + 1), paid); }
        public Loan repay(long amount) {
            if (amount <= 0 || amount > outstanding()) throw new IllegalArgumentException("Invalid repayment");
            return new Loan(principal, total, days, grace, elapsed, paid + amount);
        }
    }
    /** Credentials are opaque server records, never the item's visible name. */
    public record Property(UUID id, UUID owner, UUID key, boolean locked, Set<UUID> guests) {
        public Property {
            Objects.requireNonNull(id); Objects.requireNonNull(key); guests = Set.copyOf(guests);
            if (owner == null && (!locked || !guests.isEmpty())) throw new IllegalArgumentException("Unowned property must be closed");
        }
        public static Property vacant(UUID id) { return new Property(id, null, UUID.randomUUID(), true, Set.of()); }
        public Property purchase(UUID buyer) {
            Objects.requireNonNull(buyer);
            if (owner != null) throw new IllegalStateException("Already owned");
            return new Property(id, buyer, UUID.randomUUID(), false, Set.of());
        }
        public boolean canEnter(UUID actor, boolean admin) {
            return admin || actor != null && owner != null && (actor.equals(owner) || !locked && guests.contains(actor));
        }
        public Property lock(UUID actor, UUID presentedKey, boolean value) {
            if (owner == null || !owner.equals(actor) || !key.equals(presentedKey)) throw new SecurityException("Invalid key or owner");
            return new Property(id, owner, key, value, guests);
        }
        public Property guest(UUID actor, UUID guest, boolean allow) {
            if (owner == null || !owner.equals(actor)) throw new SecurityException("Not owner");
            Objects.requireNonNull(guest);
            Set<UUID> next = new HashSet<>(guests);
            if (allow) next.add(guest); else next.remove(guest);
            return new Property(id, owner, key, locked, next);
        }
        public Property rekey(UUID actor) {
            if (owner == null || !owner.equals(actor)) throw new SecurityException("Not owner");
            return new Property(id, owner, UUID.randomUUID(), true, Set.of());
        }
    }
    public enum OrderPhase { PAID, PREPARING, EN_ROUTE, DELIVERED, REFUNDED }
    public record Order(UUID id, UUID customer, long price, OrderPhase phase, UUID rider) {
        public Order {
            Objects.requireNonNull(id); Objects.requireNonNull(customer); Objects.requireNonNull(phase);
            if (price <= 0 || price > MAX_PRINCIPAL || ((phase == OrderPhase.EN_ROUTE || phase == OrderPhase.DELIVERED) && rider == null)
                || ((phase == OrderPhase.PAID || phase == OrderPhase.PREPARING) && rider != null)) throw new IllegalArgumentException("Invalid order");
        }
        public static Order paid(UUID id, UUID customer, long price) { return new Order(id, customer, price, OrderPhase.PAID, null); }
        public Order prepare() { require(OrderPhase.PAID); return new Order(id, customer, price, OrderPhase.PREPARING, null); }
        public Order dispatch(UUID driver) { require(OrderPhase.PREPARING); return new Order(id, customer, price, OrderPhase.EN_ROUTE, Objects.requireNonNull(driver)); }
        public Order deliver(UUID driver) {
            require(OrderPhase.EN_ROUTE);
            if (!rider.equals(driver)) throw new SecurityException("Wrong delivery rider");
            return new Order(id, customer, price, OrderPhase.DELIVERED, rider);
        }
        public Order refund() {
            if (phase == OrderPhase.DELIVERED || phase == OrderPhase.REFUNDED) throw new IllegalStateException("Order closed");
            return new Order(id, customer, price, OrderPhase.REFUNDED, rider);
        }
        private void require(OrderPhase expected) { if (phase != expected) throw new IllegalStateException("Invalid order transition"); }
    }
    /** A fixed roster of 19 ordinary gang identities; the boss is never in normal rotation. */
    public static Set<UUID> prisonRotation(List<UUID> members, UUID boss, long epoch) {
        Objects.requireNonNull(boss);
        List<UUID> roster = List.copyOf(members);
        if (roster.size() != 20 || new HashSet<>(roster).size() != 20 || !roster.contains(boss)) throw new IllegalArgumentException("Expected 20 unique identities including boss");
        List<UUID> ordinary = roster.stream().filter(id -> !id.equals(boss)).sorted().toList();
        int start = Math.floorMod(epoch, ordinary.size());
        Set<UUID> jailed = new LinkedHashSet<>();
        for (int i = 0; i < 5; i++) jailed.add(ordinary.get((start+i)%ordinary.size()));
        return Collections.unmodifiableSet(jailed);
    }
}
