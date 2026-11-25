package com.sdcraft.core;

import java.nio.charset.StandardCharsets;
import java.util.UUID;
import org.bukkit.NamespacedKey;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.persistence.PersistentDataType;

/**
 * Once-only repair grant for existing authenticated accounts that received the
 * old QualityArmory starter. The item and receipt are saved in the same player
 * snapshot, so no money transaction or cross-file receipt is required.
 */
final class GtmWeaponUpgrade {
    enum Result { DELIVERED, ALREADY_RECEIVED, INVENTORY_FULL, UNAVAILABLE }

    interface GrantPort {
        boolean received();
        int emptySlot();
        void putItem(int slot);
        void clearItem(int slot);
        void markReceived(boolean received);
        void save();
    }

    static Result deliver(GrantPort port) {
        if (port.received()) return Result.ALREADY_RECEIVED;
        int slot = port.emptySlot();
        if (slot < 0) return Result.INVENTORY_FULL;
        try {
            port.putItem(slot);
            port.markReceived(true);
            port.save();
            return Result.DELIVERED;
        } catch (RuntimeException failure) {
            // This also allows a later attempt if the player-data writer rejects
            // the save. Nothing is taken from the player's original inventory.
            port.clearItem(slot);
            port.markReceived(false);
            throw failure;
        }
    }

    static UUID serial(UUID player) {
        return UUID.nameUUIDFromBytes(("gtm:native-starter-firearm:v1:" + player)
                .getBytes(StandardCharsets.UTF_8));
    }

    static Result offer(SDCraftCorePlugin plugin, Player player) {
        if (!plugin.isAuthenticated(player)) return Result.UNAVAILABLE;
        plugin.guns().refreshVisuals(player);
        GtmEquipment equipment = plugin.equipment();
        if (equipment == null || !equipment.available(player)
                || !plugin.getConfig().getBoolean("equipment.repair-starter", true)) return Result.UNAVAILABLE;
        NamespacedKey receipt = new NamespacedKey(plugin, "native_weapon_upgrade_v1");
        if (player.getPersistentDataContainer().has(receipt, PersistentDataType.BYTE))
            return Result.ALREADY_RECEIVED;
        ItemStack pistol = equipment.create("gtm:kavach_9");
        pistol.editMeta(meta -> meta.getPersistentDataContainer().set(
                new NamespacedKey(plugin, "equipment_serial"), PersistentDataType.STRING,
                serial(player.getUniqueId()).toString()));
        Result result = deliver(new GrantPort() {
            public boolean received() { return player.getPersistentDataContainer().has(receipt, PersistentDataType.BYTE); }
            public int emptySlot() { return player.getInventory().firstEmpty(); }
            public void putItem(int slot) { player.getInventory().setItem(slot, pistol); }
            public void clearItem(int slot) { player.getInventory().setItem(slot, null); }
            public void markReceived(boolean value) {
                if (value) player.getPersistentDataContainer().set(receipt, PersistentDataType.BYTE, (byte) 1);
                else player.getPersistentDataContainer().remove(receipt);
            }
            public void save() { player.saveData(); }
        });
        if (result == Result.DELIVERED) {
            player.sendMessage("§6[GTM] §fYour native128 Kavach service pistol is ready in your inventory.");
            player.sendMessage("§7Right-click to fire · Sneak + right-click to reload · /gun for equipment and ammunition.");
        } else if (result == Result.INVENTORY_FULL) {
            player.sendMessage("§eFree one inventory slot and open /gun to receive your native128 starter pistol.");
        }
        return result;
    }
}
