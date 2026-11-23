import com.sdcraft.core.PolicyEngine;

public final class PolicyEngineTest {
    private static void eq(Object actual, Object expected) {
        if (!actual.equals(expected)) throw new AssertionError("expected " + expected + ", got " + actual);
    }
    private static void check(boolean result) { if (!result) throw new AssertionError("check failed"); }
    public static void main(String[] args) {
        eq(PolicyEngine.robberyMaximumCents(50_000), 12_500L);
        eq(PolicyEngine.robberyMaximumCents(1_000_000), 200_000L);
        eq(PolicyEngine.robberyMaximumCents(0), 0L);
        eq(PolicyEngine.taxiQuoteCents(0), 2500L);
        eq(PolicyEngine.taxiQuoteCents(100), 3100L);
        eq(PolicyEngine.taxiQuoteCents(250), 4000L);
        check(PolicyEngine.shouldBeActive(false,64));
        check(!PolicyEngine.shouldBeActive(false,80));
        check(PolicyEngine.shouldBeActive(true,80));
        check(PolicyEngine.shouldBeActive(true,96));
        check(!PolicyEngine.shouldBeActive(true,97));
        eq(PolicyEngine.witnessResult(0), "immediate");
        eq(PolicyEngine.witnessResult(69), "immediate");
        eq(PolicyEngine.witnessResult(70), "delayed");
        eq(PolicyEngine.witnessResult(89), "delayed");
        eq(PolicyEngine.witnessResult(90), "silent");
        eq(PolicyEngine.targetPoliceResponders(3,2), 2);
        eq(PolicyEngine.targetPoliceResponders(2,6), 2);
        eq(PolicyEngine.money(4025), "$40.25");
        System.out.println("PASS: 18 core NPC/crime/transport policy checks");
    }
}
