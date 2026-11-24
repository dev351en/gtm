package com.sdcraft.core;

import com.sdcraft.core.gtm.RoleplayText;
import java.util.Locale;
import org.bukkit.NamespacedKey;
import org.bukkit.entity.Player;
import org.bukkit.persistence.PersistentDataType;

/** Local dialogue shared by player chat and NPC bubbles. Memory follows player saves. */
final class Jeeva {
    private Jeeva() {}

    static String reply(Player player, String id, String name, String role, String dept,
                        String preference, String prompt, String greeting) {
        String lang = RoleplayText.language(prompt, preference);
        String answer = DialogueEngine.respond(id, name, role, dept, lang, prompt, greeting);
        // Only NPC registry IDs are accepted. Store one small record per encountered identity.
        if (id == null || !id.matches("[a-z0-9_-]{1,48}")) return answer;
        NamespacedKey key = new NamespacedKey("gtm", "jeeva/" + id.toLowerCase(Locale.ROOT));
        var memory = player.getPersistentDataContainer();
        long[] previous = memory.get(key, PersistentDataType.LONG_ARRAY);
        long now = System.currentTimeMillis();
        long visits = previous == null || previous.length != 2 ? 0 : previous[0];
        if (visits == 0 || now - previous[1] >= 300_000) {
            memory.set(key, PersistentDataType.LONG_ARRAY, new long[]{Math.min(1_000_000, visits+1), now});
        }
        if (visits < 1 || DialogueEngine.classify(prompt) != DialogueEngine.Intent.GREETING) return answer;
        return switch (lang) {
            case "hi" -> "फिर मिलकर अच्छा लगा! मैं " + name + " हूँ। आज क्या मदद चाहिए?";
            case "hinglish" -> "Arre, phir mil gaye! Main " + name + ". Aaj kya madad chahiye?";
            default -> "Good to see you again! It's " + name + ". What brings you back?";
        };
    }
}
