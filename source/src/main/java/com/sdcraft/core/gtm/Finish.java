package com.sdcraft.core.gtm;

import java.util.List;
import java.util.Locale;

/** A finish changes the item's appearance only. The ledger owns the entitlement. */
public record Finish(String family, int index) {
    private static final List<String> FAMILIES = List.of("pistol", "shotgun", "smg", "rifle");
    private static final List<String> PATTERNS = List.of("Leheriya", "Jali", "Monsoon", "Patola", "Marine Lines",
        "Kite Festival", "Bandra Tiles", "Night Local", "Warli Steps", "Marigold", "Mill Stripe",
        "Salt Pan", "Tidal Pool", "Neon Bazaar", "Copper Circuit");
    private static final List<String> COLORS = List.of("Indigo", "Saffron", "Jade", "Gulab", "Midnight");
    public static final int COUNT_PER_FAMILY = 75;

    public Finish {
        if (!FAMILIES.contains(family) || index < 0 || index >= COUNT_PER_FAMILY)
            throw new IllegalArgumentException("Unknown finish");
    }

    public String id() { return String.format(Locale.ROOT, "%s_%02d", family, index + 1); }
    public String title() { return PATTERNS.get(index / 5) + " · " + COLORS.get(index % 5); }
    public long priceCents() { return 15000L + 1000L * (index / 5); }
}
