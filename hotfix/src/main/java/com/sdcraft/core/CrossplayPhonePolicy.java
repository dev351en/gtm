package com.sdcraft.core;

/**
 * Server-only phone presentation decisions.
 *
 * Vanilla Java and Geyser/Bedrock accept server-backed inventory menus.
 * Modelled PAPER items are mapped through both resource packs and Geyser;
 * Java bitmap fonts are used only after the Java pack is accepted.
 *
 * All phone actions continue to use GtmPhoneApps' authenticated,
 * server-authoritative inventory handlers.
 */
final class CrossplayPhonePolicy {
    private CrossplayPhonePolicy() {}

    /**
     * Java may use its server-delivered font skin once its pack is accepted;
     * Bedrock receives the standard inventory title and mapped model icons.
     */
    static boolean useCustomFontTitle(
            boolean customGuiEnabled, boolean hasCompatibleJavaPack) {
        // This signal is produced only after a successful Java pack load;
        // the calling service explicitly excludes Geyser/Floodgate players.
        // A server resource pack is NOT a client-side mod.
        return customGuiEnabled && hasCompatibleJavaPack;
    }

    static String mode(boolean crossplaySafe) {
        return crossplaySafe ? "server-only inventory + sidebar + map" :
                "legacy custom-font inventory (crossplay not guaranteed)";
    }
}
