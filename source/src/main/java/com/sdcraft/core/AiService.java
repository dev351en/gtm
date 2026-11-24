package com.sdcraft.core;

import java.io.*;
import java.net.URI;
import java.net.http.*;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.LocalDate;
import java.util.*;
import java.util.concurrent.*;
import java.util.regex.*;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;

/**
 * Handles NPC conversation.
 * Primary mode: Offline deterministic bilingual intent-and-response engine (DialogueEngine).
 * Optional mode: OpenAI-compatible external chat completions API if explicitly enabled and configured.
 * 
 * STRICT BOUNDARY: Never authorizes actions, arrests, or balance edits directly.
 */
final class AiService {
    private final JavaPlugin plugin;
    private final HttpClient http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();
    private final Map<UUID, Deque<Long>> rate = new HashMap<>();
    private final Map<UUID, Deque<Message>> memory = new HashMap<>();
    private LocalDate day = LocalDate.now();
    private int today = 0;
    private final Properties secrets = new Properties();

    private record Message(long time, String who, String text) {}

    AiService(JavaPlugin plugin) {
        this.plugin = plugin;
        File secretFile = new File(plugin.getDataFolder(), "ai-secrets.properties");
        if (secretFile.isFile()) {
            try (FileInputStream in = new FileInputStream(secretFile)) {
                secrets.load(in);
            } catch (Exception e) {
                plugin.getLogger().warning("AI credentials file unreadable: " + e.getMessage());
            }
        }
    }

    private String quote(String s) {
        StringBuilder b = new StringBuilder("\"");
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '"' || c == '\\') b.append('\\').append(c);
            else if (c == '\n') b.append("\\n");
            else if (c == '\r') b.append("\\r");
            else if (c < 0x20) b.append(' ');
            else b.append(c);
        }
        return b.append('"').toString();
    }

    private String unquote(String s) {
        StringBuilder b = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c != '\\' || i + 1 >= s.length()) {
                b.append(c);
                continue;
            }
            char n = s.charAt(++i);
            switch (n) {
                case 'n' -> b.append('\n');
                case 'r' -> b.append('\r');
                case 't' -> b.append('\t');
                case 'u' -> {
                    if (i + 4 < s.length()) {
                        try {
                            b.append((char) Integer.parseInt(s.substring(i + 1, i + 5), 16));
                            i += 4;
                        } catch (Exception ex) {
                            b.append('?');
                        }
                    }
                }
                default -> b.append(n);
            }
        }
        return b.toString();
    }

    private String content(String json) {
        int choice = json.indexOf("\"choices\"");
        if (choice < 0) return null;
        Matcher m = Pattern.compile("\\\"content\\\"\\s*:\\s*\\\"((?:\\\\.|[^\\\"\\\\])*)\\\"").matcher(json.substring(choice));
        return m.find() ? unquote(m.group(1)) : null;
    }

    void speak(Player player, String npcId, String npcName, String role, String dept, String lang, String prompt, String fallbackGreeting) {
        UUID id = player.getUniqueId();
        long now = System.currentTimeMillis();

        // 1. If external AI is not enabled or credentials are not present, use the deterministic offline engine
        if (!plugin.getConfig().getBoolean("ai.external-enabled", false)) {
            String offlineReply = Jeeva.reply(player, npcId, npcName, role, dept, lang, prompt, fallbackGreeting);
            player.sendMessage("§6" + npcName + ": §f" + offlineReply);
            return;
        }

        String apiKey = secrets.getProperty("OPENAI_API_KEY", "");
        if (apiKey.isBlank()) {
            String offlineReply = Jeeva.reply(player, npcId, npcName, role, dept, lang, prompt, fallbackGreeting);
            player.sendMessage("§6" + npcName + ": §f" + offlineReply);
            return;
        }

        if (prompt.length() > 240) prompt = prompt.substring(0, 240);
        if (!day.equals(LocalDate.now())) {
            day = LocalDate.now();
            today = 0;
        }

        int maxDaily = plugin.getConfig().getInt("ai.daily-request-limit", 200);
        if (today >= maxDaily) {
            String offlineReply = Jeeva.reply(player, npcId, npcName, role, dept, lang, prompt, fallbackGreeting);
            player.sendMessage("§6" + npcName + ": §f" + offlineReply);
            player.sendMessage("§7[SD Craft] Daily AI quota reached. Switched to offline dialogue.");
            return;
        }

        Deque<Long> q = rate.computeIfAbsent(id, x -> new ArrayDeque<>());
        while (!q.isEmpty() && q.peekFirst() < now - 300000) q.removeFirst();
        if (q.size() >= 10) {
            String offlineReply = Jeeva.reply(player, npcId, npcName, role, dept, lang, prompt, fallbackGreeting);
            player.sendMessage("§6" + npcName + ": §f" + offlineReply);
            player.sendMessage("§7[SD Craft] Rate limit: 10 requests per 5 minutes. Switched to offline response.");
            return;
        }

        q.addLast(now);
        today++;

        Deque<Message> history = memory.computeIfAbsent(id, k -> new ArrayDeque<>());
        while (!history.isEmpty() && (history.peekFirst().time < now - 86400000L || history.size() > 8)) {
            history.removeFirst();
        }

        String system = "You are " + npcName + ", a fictional " + role + " in Minecraft SD Craft. "
            + "Answer in " + (lang.equals("hi") ? "Hindi" : "English") + " in 2-4 concise sentences. "
            + "Never execute commands or financial transactions. Direct the player to verified /sdc commands.";

        StringBuilder messages = new StringBuilder("[{\"role\":\"system\",\"content\":" + quote(system) + "}");
        for (Message m : history) {
            messages.append(", {\"role\":").append(quote(m.who)).append(",\"content\":").append(quote(m.text)).append("}");
        }
        messages.append(", {\"role\":\"user\",\"content\":").append(quote(prompt)).append("}]");

        String payload = "{\"model\":\"" + plugin.getConfig().getString("ai.model", "gpt-4.1-mini") + "\",\"max_tokens\":160,\"messages\":" + messages + "}";
        String endpoint = plugin.getConfig().getString("ai.endpoint", "https://api.openai.com/v1/chat/completions");

        if (!endpoint.equals("https://api.openai.com/v1/chat/completions")) {
            player.sendMessage("§c[SD Craft] Non-whitelisted AI endpoint; using deterministic offline engine.");
            String offlineReply = Jeeva.reply(player, npcId, npcName, role, dept, lang, prompt, fallbackGreeting);
            player.sendMessage("§6" + npcName + ": §f" + offlineReply);
            return;
        }

        HttpRequest req = HttpRequest.newBuilder(URI.create(endpoint)).timeout(Duration.ofSeconds(9))
            .header("Content-Type", "application/json").header("Authorization", "Bearer " + apiKey)
            .POST(HttpRequest.BodyPublishers.ofString(payload, StandardCharsets.UTF_8)).build();

        String question = prompt;
        player.sendMessage("§7[SD Craft] Asking " + npcName + "...");

        http.sendAsync(req, HttpResponse.BodyHandlers.ofString()).orTimeout(10, TimeUnit.SECONDS)
            .whenComplete((response, error) -> {
                String reply = (error == null && response != null && response.statusCode() == 200) ? content(response.body()) : null;
                String remoteReply = reply;
                Bukkit.getScheduler().runTask(plugin, () -> {
                    if (!player.isOnline()) return;
                    String finalReply = remoteReply == null || remoteReply.isBlank()
                        ? Jeeva.reply(player, npcId, npcName, role, dept, lang, question, fallbackGreeting)
                        : remoteReply.substring(0, Math.min(650, remoteReply.length()));
                    player.sendMessage("§6" + npcName + ": §f" + finalReply);
                    Deque<Message> hist = memory.computeIfAbsent(id, x -> new ArrayDeque<>());
                    hist.addLast(new Message(System.currentTimeMillis(), "user", question));
                    hist.addLast(new Message(System.currentTimeMillis(), "assistant", finalReply));
                    while (hist.size() > 8) hist.removeFirst();
                });
            });
    }
}
