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

    static String mode(boolean crossplaySafe) {
        return crossplaySafe ? "server-only inventory + sidebar + map" :
                "legacy custom-font inventory (crossplay not guaranteed)";
    }
}
