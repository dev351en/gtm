package com.sdcraft.core.gtm;

import java.util.Locale;
import java.util.Set;

/** Pure input handling; never executes commands or changes accounts. */
public final class RoleplayText {
    private RoleplayText() {}
    public static final int MAX_CODEPOINTS = 160;
    private static final Set<String> EDIT = Set.of("wand", "pos1", "pos2", "set", "replace", "copy", "paste", "cut", "undo", "redo", "stack", "move", "rotate", "schem", "schematic", "sel", "expand", "contract", "sphere", "hsphere", "cyl", "hcyl", "brush", "mask", "walls", "outline", "regen");
    /** Only the explicit prefix // followed by whitespace is dialogue. //set and other commands pass through. */
    public static boolean isDialogue(String raw) {
        return raw != null && raw.length() >= 3 && raw.startsWith("//") && Character.isWhitespace(raw.charAt(2));
    }
    /** Extra safeguard for privileged editors who use an unusual space before an edit command. */
    public static boolean reservedEdit(String raw) {
        if (!isDialogue(raw)) return false;
        String s = raw.substring(2).strip().toLowerCase(Locale.ROOT);
        return !s.isEmpty() && EDIT.contains(s.split("\\s+", 2)[0]);
    }
    public static String clean(String raw) {
        if (raw == null) return "";
        StringBuilder b = new StringBuilder();
        raw.codePoints().filter(cp -> !Character.isISOControl(cp) && Character.getType(cp) != Character.FORMAT && cp != 0xA7).limit(MAX_CODEPOINTS).forEach(b::appendCodePoint);
        return b.toString().strip();
    }
    public static String message(String raw) { return isDialogue(raw) ? clean(raw.substring(2)) : ""; }
    public static String language(String text, String preference) {
        if (text != null && text.codePoints().anyMatch(cp -> cp >= 0x0900 && cp <= 0x097F)) return "hi";
        if (text != null && text.toLowerCase(Locale.ROOT).matches("(?s).*\\b(bhai|yaar|kya|kaise|kidhar|hat|hatt|gaadi|sambhal|namaste|haan|nahi)\\b.*")) return "hinglish";
        return "hi".equals(preference) ? "hi" : "en";
    }
    public static String reaction(String lang, boolean tough, int variant) {
        String[] lines = switch (lang) {
            case "hi" -> tough ? new String[]{"अरे! गाड़ी संभाल के चलाओ!", "देख कर चलाओ भाई!", "सड़क पर ध्यान दो!"} : new String[]{"ज़रा धीरे चलाइए!", "ध्यान से, मैं यहाँ हूँ!", "सावधान!"};
            case "hinglish" -> tough ? new String[]{"Arre bhai, gaadi sambhal!", "Dekh ke chala yaar!", "Oye, road pe dhyaan de!"} : new String[]{"Bhai, zara dheere!", "Dhyaan se, main yahan hoon!", "Arre, sambhal ke!"};
            default -> tough ? new String[]{"Hey! Watch where you're going!", "Slow down already!", "Eyes on the road!"} : new String[]{"Careful, please!", "Please slow down!", "Watch out!"};
        };
        return lines[Math.floorMod(variant, lines.length)];
    }
}
