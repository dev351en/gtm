package com.sdcraft.core;

/**
 * Server-only phone presentation decisions.
 *
 * Vanilla Java, Geyser/Bedrock and other clients understand ordinary
 * inventory menus. A custom Java font bitmap is not a cross-edition
 * container protocol, so it must never be the default for crossplay.
 *
 * All phone actions continue to use GtmPhoneApps' authenticated,
 * server-authoritative inventory handlers.
 */
final class CrossplayPhonePolicy {
    private CrossplayPhonePolicy() {}

    /**
     * The safe default applies even when an upgraded server retained
     * phone.custom-gui=true from an earlier release.
     *
     * Operators may explicitly opt out for a Java-only installation.
     * The crossplay release never asks players to install client code.
     */
    static boolean useCustomFontTitle(
            boolean crossplaySafe,
            boolean customGuiEnabled,
            boolean hasCompatibleGtmPack) {
        return !crossplaySafe && customGuiEnabled && hasCompatibleGtmPack;
    }

    /**
     * Distinct vanilla item icons remain recognizable to Bedrock and Java
     * when resource-pack mappings are missing or fail to load.
     */
    static org.bukkit.Material iconMaterial(String id) {
        return switch (id) {
            case "app_quoggle", "app_maps" -> org.bukkit.Material.COMPASS;
            case "app_amazzo", "app_flippit" -> org.bukkit.Material.CHEST;
            case "app_arkpay", "app_bank", "app_loans" -> org.bukkit.Material.GOLD_INGOT;
            case "app_zomatoo", "app_swiffy" -> org.bukkit.Material.COOKED_BEEF;
            case "app_fashion" -> org.bukkit.Material.LEATHER_CHESTPLATE;
            case "app_property", "app_keys" -> org.bukkit.Material.IRON_DOOR;
            case "app_car_app", "app_garage", "app_taxi" -> org.bukkit.Material.MINECART;
            case "app_transport" -> org.bukkit.Material.RAIL;
            case "app_news" -> org.bukkit.Material.WRITABLE_BOOK;
            case "app_police" -> org.bukkit.Material.SHIELD;
            case "app_medical" -> org.bukkit.Material.POTION;
            case "app_events" -> org.bukkit.Material.FIREWORK_ROCKET;
            case "app_missions", "app_careers" -> org.bukkit.Material.MAP;
            case "app_contacts" -> org.bukkit.Material.PLAYER_HEAD;
            case "app_settings" -> org.bukkit.Material.COMPARATOR;
            case "phone_shortcut" -> org.bukkit.Material.CLOCK;
            case "hotbar_frame" -> org.bukkit.Material.ITEM_FRAME;
            case "notification_frame" -> org.bukkit.Material.BELL;
            default -> org.bukkit.Material.PAPER;
        };
    }

    static String mode(boolean crossplaySafe) {
        return crossplaySafe ? "server-only inventory + sidebar + map" :
                "legacy custom-font inventory (crossplay not guaranteed)";
    }
}
