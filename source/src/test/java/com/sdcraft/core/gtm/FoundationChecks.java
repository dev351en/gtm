package com.sdcraft.core.gtm;

/** Dependency-free executable smoke tests; run with javac and java. */
public final class FoundationChecks {
    private static int checks;
    private static void check(boolean ok) { checks++; if (!ok) throw new AssertionError("Check " + checks); }
    private static void rejects(Runnable action) { try { action.run(); throw new AssertionError("Accepted invalid input"); } catch (IllegalArgumentException | IllegalStateException expected) { checks++; } }
    public static void main(String[] args) {
        var v = new VehicleState(10, 10, 100, 0);
        check(v.condition() == VehicleState.Condition.NORMAL);
        var t = v.travel(30, .5);
        check(t.allowedDistance() == 20);
        check(t.state().energy() == 0);
        check(t.state().distance() == 20);
        check(!t.state().canPropel());
        check(t.state().travel(1, 0).allowedDistance() == 0);
        check(t.state().refill(99).energy() == 10);
        check(v.idle(12).energy() == 0);
        check(v.damage(25).state().condition() == VehicleState.Condition.DAMAGED);
        check(v.damage(50).state().condition() == VehicleState.Condition.HEAVY);
        check(v.damage(75).state().condition() == VehicleState.Condition.FAILURE);
        check(!v.damage(75).state().canPropel());
        check(v.damage(90).state().condition() == VehicleState.Condition.CRITICAL);
        var dead = v.damage(100);
        check(dead.newlyDestroyed());
        check(!dead.state().damage(100).newlyDestroyed());
        check(dead.state().condition() == VehicleState.Condition.DESTROYED);
        rejects(() -> dead.state().repair(1));
        rejects(() -> dead.state().refill(1));
        check(v.damage(30).state().repair(100).health() == 100);
        rejects(() -> v.travel(-1, .1));
        rejects(() -> v.damage(Double.NaN));
        rejects(() -> new VehicleState(0, 0, 100, 0));
        check(v.travel(1, 0).state().energy() == 10);
        check(RoleplayText.isDialogue("// bhai"));
        check(!RoleplayText.isDialogue("//set stone"));
        check(!RoleplayText.isDialogue("/login x"));
        check(RoleplayText.reservedEdit("// set stone"));
        check(RoleplayText.message("// नमस्ते").equals("नमस्ते"));
        check(RoleplayText.message("// ").isEmpty());
        check(RoleplayText.clean("a\u0000b\u00a7c").equals("abc"));
        check(RoleplayText.clean("😀".repeat(200)).codePointCount(0, RoleplayText.clean("😀".repeat(200)).length()) == 160);
        check(RoleplayText.language("भाई", "en").equals("hi"));
        check(RoleplayText.language("Bhai, move", "en").equals("hinglish"));
        check(RoleplayText.language("hello", "en").equals("en"));
        check(!RoleplayText.reaction("hi", true, 0).equals(RoleplayText.reaction("hi", true, 1)));
        check(!RoleplayText.reaction("hinglish", true, 0).equals(RoleplayText.reaction("hinglish", false, 0)));
        System.out.println("GTM foundation: " + checks + " checks passed");
    }
}
