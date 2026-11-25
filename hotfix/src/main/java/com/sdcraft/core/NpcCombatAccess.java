package com.sdcraft.core;

import org.bukkit.entity.Player;

/** Target-only compatibility hook; it must never be used to authorize a shooter. */
public final class NpcCombatAccess {
    private NpcCombatAccess() {}

    public static boolean authenticatedPlayerOrAmbient(SDCraftCorePlugin plugin, Player target) {
        return plugin.isAuthenticated(target) || plugin.isAttackableNpc(target);
    }
}
