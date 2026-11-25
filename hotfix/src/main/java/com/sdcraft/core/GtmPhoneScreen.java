package com.sdcraft.core;

import net.kyori.adventure.key.Key;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import net.kyori.adventure.text.format.TextDecoration;
import org.bukkit.ChatColor;

/** The phone skin uses the real inventory's clickable slots and a title bitmap.
 *  It does not alter the client's native hotbar, hide items, or handle clicks. */
final class GtmPhoneScreen {
    private static final Key FONT = Key.key("gtm", "phone_screen");
    private static final Key DEFAULT = Key.key("minecraft", "default");

    private GtmPhoneScreen() {}

    static Component title(String legacy, int size, boolean home) {
        if (size != 27 && size != 36 && size != 54) {
            throw new IllegalArgumentException("Unsupported phone inventory size: " + size);
        }
        char background = home ? '\uF100' : (size == 27 ? '\uF101' : size == 36 ? '\uF102' : '\uF103');
        String title = ChatColor.stripColor(legacy);
        if (title == null) title = "GTM Phone";
        int separator = title.indexOf(" | ");
        if (separator >= 0) title = title.substring(0, separator);
        if (title.length() > 27) title = title.substring(0, 26) + "…";
        // Vanilla container label starts at (8, 6). The skin's negative space
        // moves to x=0; ascent=13 aligns its bitmap with y=0. Move back to x=8
        // after the 176px bitmap advance (177 including font spacing).
        return Component.text("\uF010" + background + "\uF011", NamedTextColor.WHITE)
                .font(FONT).decoration(TextDecoration.ITALIC, false)
                .append(Component.text(title, NamedTextColor.GOLD).font(DEFAULT));
    }
}
