package com.sdcraft.core;

import java.util.Locale;
import java.util.Optional;
import org.bukkit.entity.Player;

/** Bounded, deterministic help backed by this authenticated player's state.
 * No prompt is executed, sent to a provider, or used to grant an entitlement. */
final class GtmPhoneAssistant {
    private GtmPhoneAssistant() {}

    static String answer(Player player, GtmPhoneApps phone, String prompt) {
        String question = prompt.toLowerCase(Locale.ROOT);
        if (question.isBlank() || question.equals("help") || question.contains("start")) {
            return "Welcome to Indraprastha. Use City GPS for destinations, Equipment for usable weapons, "
                    + "My Garage for owned vehicles, and City Jobs for work. Hold your phone and right-click "
                    + "or press the swap-hands key to return here.";
        }
        if (has(question, "bank", "cash", "money", "wallet", "balance", "paisa")) {
            return String.format(Locale.ROOT,
                    "Your wallet holds ARK %.2f and your bank holds ARK %.2f. Open Indra Bank for deposits "
                    + "and withdrawals. ARK Pay uses the account PIN flow; JEEVA never asks for your PIN.",
                    phone.services().wallet(player) / 100.0, phone.services().bank(player) / 100.0);
        }
        if (has(question, "driv", "car", "vehicle", "rickshaw", "fuel", "brake")) {
            Optional<GtmPhoneApps.DriveData> drive = phone.services().driving(player);
            String state = drive.map(d -> String.format(Locale.ROOT,
                    "You are in %s at %.1f km/h, with %.0f%% energy and %.0f%% condition. ",
                    d.title(), Math.abs(d.blocksPerSecond()) * 3.6, d.energyPercent(), d.health()))
                    .orElse("You are currently on foot. ");
            return state + "Open My Garage to use an owned vehicle. While driving, W accelerates, S brakes "
                    + "then reverses, and A/D steer. Motor Mile provides the real controls and live dashboard.";
        }
        if (has(question, "weapon", "gun", "shoot", "ammo", "reload")) {
            return "Open Equipment from the phone's right-hand shortcut or Amazzo. Select Weapons for usable "
                    + "firearms and matching ammunition. Right-click fires; sneak and right-click to reload. "
                    + "The shop checks your access and funds. Cosmetic previews alone do not issue equipment.";
        }
        if (has(question, "job", "work", "mission", "contract")) {
            return "City Jobs opens the registered work and duty workflows. Contracts opens the mission board. "
                    + "Only missions and services registered on this server are available; use City GPS to find their locations.";
        }
        if (has(question, "npc", "talk", "speak", "conversation", "jeeva", "ai")) {
            return "Right-click a city NPC for their real services. Where NPC dialogue is enabled, stand nearby "
                    + "and type // followed by a space and your message. JEEVA here is the offline city guide, "
                    + "with rule-based replies and live account status; it is not a connected generative AI model.";
        }
        if (has(question, "map", "where", "navigate", "location", "hospital", "police")) {
            return "City GPS contains " + phone.destinations(player).size() + " commissioned destinations. "
                    + "Choose one to set your actual navigation target, then select Live map. The map follows "
                    + "loaded terrain. Change its shape, rotation and zoom in Settings.";
        }
        return DialogueEngine.respond("jeeva", "JEEVA", "city guide", "civic", "en", prompt,
                "I can help with driving, weapons, banking, jobs, maps and NPC conversations. Choose a topic or ask about one of these game systems.");
    }

    private static boolean has(String text, String... words) {
        for (String word : words) if (text.contains(word)) return true;
        return false;
    }
}
