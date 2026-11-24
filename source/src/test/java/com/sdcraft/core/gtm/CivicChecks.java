package com.sdcraft.core.gtm;

import java.util.*;
import static com.sdcraft.core.gtm.CivicRules.*;

public final class CivicChecks {
    private static int count;
    private static void check(boolean pass) { count++; if (!pass) throw new AssertionError("Check " + count); }
    private static void rejects(Runnable action) {
        try { action.run(); throw new AssertionError("Expected rejection"); }
        catch (IllegalArgumentException | IllegalStateException | SecurityException expected) { count++; }
    }
    public static void main(String[] args) {
        var loan = Loan.issue(10000, 800, 14, 2);
        check(loan.total() == 10800); check(loan.due() == 0); check(!loan.overdue());
        var day1 = loan.advanceActiveDay(); check(day1.due() == 772); check(!day1.overdue());
        var day3 = day1.advanceActiveDay().advanceActiveDay(); check(day3.overdue());
        var repaid = day3.repay(772); check(!repaid.overdue()); check(repaid.outstanding() == 10028);
        rejects(() -> loan.repay(10801)); rejects(() -> loan.repay(0)); rejects(() -> Loan.issue(10000, -1, 14, 2));
        var end = loan; for (int i = 0; i < 100; i++) end = end.advanceActiveDay();
        check(end.elapsed() == 16); check(end.due() == 10800); check(end.repay(10800).outstanding() == 0);
        check(!end.repay(10800).overdue()); check(Loan.issue(1, 1, 1, 0).total() == 2);
        UUID owner = UUID.randomUUID(), guest = UUID.randomUUID(), stranger = UUID.randomUUID();
        var vacant = Property.vacant(UUID.randomUUID()); check(!vacant.canEnter(owner, false)); check(vacant.canEnter(stranger, true));
        var home = vacant.purchase(owner); check(home.canEnter(owner, false)); check(!home.canEnter(stranger, false));
        rejects(() -> home.purchase(guest)); rejects(() -> home.lock(stranger, home.key(), true)); rejects(() -> home.lock(owner, UUID.randomUUID(), true));
        var shared = home.guest(owner, guest, true); check(shared.canEnter(guest, false));
        var locked = shared.lock(owner, shared.key(), true); check(!locked.canEnter(guest, false)); check(locked.canEnter(owner, false));
        check(locked.canEnter(stranger, true)); check(!locked.canEnter(null, false));
        var rekeyed = shared.rekey(owner); rejects(() -> rekeyed.lock(owner, home.key(), false)); check(!rekeyed.canEnter(guest, false));
        var order = Order.paid(UUID.randomUUID(), owner, 5000); rejects(() -> order.deliver(guest));
        var prep = order.prepare(); rejects(prep::prepare); var trip = prep.dispatch(guest);
        rejects(() -> trip.deliver(stranger)); check(trip.deliver(guest).phase() == OrderPhase.DELIVERED);
        rejects(() -> trip.deliver(guest).refund()); check(trip.refund().phase() == OrderPhase.REFUNDED); rejects(() -> trip.refund().refund());
        var gang = new ArrayList<UUID>(); for (int i = 0; i < 20; i++) gang.add(new UUID(0, i));
        UUID boss = gang.getFirst(); var seen = new HashSet<UUID>();
        for (int day = 0; day < 19; day++) { var jail = prisonRotation(gang, boss, day); check(jail.size() == 5); check(!jail.contains(boss)); seen.addAll(jail); }
        check(seen.size() == 19); check(prisonRotation(gang, boss, 0).equals(prisonRotation(gang, boss, 19)));
        rejects(() -> prisonRotation(gang.subList(0, 19), boss, 0));
        System.out.println("GTM civic rules: " + count + " checks passed");
    }
}
