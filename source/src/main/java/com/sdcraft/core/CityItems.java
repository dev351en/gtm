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
    static final int POLICE_BADGE = 900004;
    static final int MEDKIT = 900005;
    static final int ATM_CARD = 900009;
    static final int CAR_KEY_FOB = 900010;
    static final int JERRY_CAN = 900011;
    static final int BASEBALL_BAT = 900012;

    // Custom GTA Online / iFruit Mobile App Icons
    static final int APP_GPS = 900020;
    static final int APP_JOBS = 900021;
    static final int APP_GEAR = 900022; // Ammu-Nation / Weapon store
    static final int APP_GARAGE = 900023; // Motorsport garage
    static final int APP_BANK = 900024; // Maze Bank
    static final int APP_SAFETY = 900025; // LSPD Wanted & Bail
    static final int APP_MEDICAL = 900026; // Pillbox Hospital
    static final int APP_SETTINGS = 900027; // Profile & Settings

    private CityItems() {}

    static ItemStack make(int model, String name, String... lore) {
        ItemStack item = new ItemStack(Material.PAPER);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setCustomModelData(model);
            meta.setDisplayName(name);
            meta.setLore(List.of(lore));
            item.setItemMeta(meta);
        }
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
        return make(CASH, "§aCity Cash Bundle", "§7Wallet balance is stored securely on the server.");
    }

    static ItemStack policeBadge() {
        return make(POLICE_BADGE, "§9§lSDPD Detective Badge", "§7San Diego Police Department", "§8Official Law Enforcement Identification");
    }

    static ItemStack medkit() {
        return make(MEDKIT, "§c§lTactical First Aid Medkit", "§7Pillbox Hill Medical Center", "§aRight-click to bandage & restore health.");
    }

    static ItemStack atmCard() {
        return make(ATM_CARD, "§e§lMaze Bank VIP Platinum Card", "§7Linked to personal bank vault balance.");
    }

    static ItemStack carKeyFob(String vehicleName) {
        return make(CAR_KEY_FOB, "§6§lVehicle Key Fob §7(" + vehicleName + ")", "§7Electronic smart key & remote lock/unlock.", "§eRight-click near vehicle to unlock.");
    }

    static ItemStack jerryCan() {
        return make(JERRY_CAN, "§c§lJerry Can (Fuel 100L)", "§7High-octane emergency vehicle fuel.", "§aRight-click vehicle to refuel 100%.");
    }

    static ItemStack baseballBat() {
        return make(BASEBALL_BAT, "§e§lLouisville Ash Baseball Bat", "§7Solid hardwood sports melee weapon.", "§cHeavy bludgeoning impact.");
    }
}
