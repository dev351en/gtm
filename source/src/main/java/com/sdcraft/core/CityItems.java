package com.sdcraft.core;

import java.util.List;
import org.bukkit.Material;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

/** Model IDs reserved in the SD Craft 26.3 resource pack. */
final class CityItems {
    static final int CASH = 900001;
    static final int PHONE = 900002;
    static final int METRO_TICKET = 900003;

    private CityItems() {}

    static ItemStack make(int model, String name, String... lore) {
        ItemStack item = new ItemStack(Material.PAPER);
        ItemMeta meta = item.getItemMeta();
        meta.setCustomModelData(model);
        meta.setDisplayName(name);
        meta.setLore(List.of(lore));
        item.setItemMeta(meta);
        return item;
    }

    static boolean is(ItemStack item, int model) {
        return item != null && item.getType() == Material.PAPER && item.hasItemMeta()
                && item.getItemMeta().hasCustomModelData()
                && item.getItemMeta().getCustomModelData() == model;
    }

    static ItemStack phone() {
        return make(PHONE, "§6SD Craft City Phone", "§7Right-click to open city services.");
    }

    static ItemStack metroTicket(String destination) {
        return make(METRO_TICKET, "§bNew Blockston Metro Ticket",
                "§7Destination: §f" + destination, "§8Fare paid; souvenir receipt, not reusable.");
    }

    static ItemStack cashIcon() {
        return make(CASH, "§aCity Cash", "§7Wallet balance is stored securely on the server.");
    }
}
