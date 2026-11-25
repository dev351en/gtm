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
            boolean customGuiEnabled, boolean hasCompatibleJavaPack) {
        // This signal is produced only after a successful Java pack load;
        // the calling service explicitly excludes Geyser/Floodgate players.
        // A server resource pack is NOT a client-side mod.
        return customGuiEnabled && hasCompatibleJavaPack;
    }

    /**
     * Distinct vanilla item icons remain recognizable to Bedrock and Java
     * when resource-pack mappings are missing or fail to load.
     */
    static String iconMaterialName(String id) {
        return switch (id) {
            case "app_quoggle", "app_maps" -> "COMPASS";
            case "app_amazzo", "app_flippit" -> "CHEST";
            case "app_arkpay", "app_bank", "app_loans" -> "GOLD_INGOT";
            case "app_zomatoo", "app_swiffy" -> "COOKED_BEEF";
            case "app_fashion" -> "LEATHER_CHESTPLATE";
            case "app_property", "app_keys" -> "IRON_DOOR";
            case "app_car_app", "app_garage", "app_taxi" -> "MINECART";
            case "app_transport" -> "RAIL";
            case "app_news" -> "WRITABLE_BOOK";
            case "app_police" -> "SHIELD";
            case "app_medical" -> "POTION";
            case "app_events" -> "FIREWORK_ROCKET";
            case "app_missions", "app_careers" -> "MAP";
            case "app_contacts" -> "PLAYER_HEAD";
            case "app_settings" -> "COMPARATOR";
            case "phone_shortcut" -> "CLOCK";
            case "hotbar_frame" -> "ITEM_FRAME";
            case "notification_frame" -> "BELL";
            default -> "PAPER";
        };
    }

    static String mode(boolean crossplaySafe) {
        return crossplaySafe ? "server-only inventory + sidebar + map" :
                "legacy custom-font inventory (crossplay not guaranteed)";
    }
}
