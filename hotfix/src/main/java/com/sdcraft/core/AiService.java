package com.sdcraft.core;

import com.sdcraft.core.gtm.RoleplayText;
import java.io.InputStream;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;
import java.util.Objects;
import java.util.Properties;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;

/** Shared NPC dialogue path for commands, selected conversations and bubbles. */
final class AiService implements AutoCloseable {
    private final SDCraftCorePlugin core;
    private final NpcConversationBackend backend;
    private final Map<UUID, String> reportedMode = new HashMap<>();
    private volatile String lastResult = "not-contacted";
    private volatile boolean closed;

    AiService(JavaPlugin plugin) {
        if (!(plugin instanceof SDCraftCorePlugin value)) throw new IllegalArgumentException("GTM core required");
        core = value;
        Properties secrets = new Properties();
        Path secret = core.getDataFolder().toPath().resolve("ai-secrets.properties");
        if (Files.isRegularFile(secret) && !Files.isSymbolicLink(secret)) {
            try (InputStream stream = Files.newInputStream(secret)) { secrets.load(stream); }
            catch (Exception ignored) { core.getLogger().warning("JEEVA private configuration could not be read; local dialogue remains available."); }
        }
        NpcConversationBackend.Settings settings;
        try {
            String requested = core.getConfig().getString("ai.provider",
                    core.getConfig().getBoolean("ai.external-enabled", false) ? "openai-compatible" : "offline").toLowerCase(Locale.ROOT);
            NpcConversationBackend.Provider provider = switch (requested) {
                case "offline" -> NpcConversationBackend.Provider.OFFLINE;
                case "ollama" -> NpcConversationBackend.Provider.OLLAMA;
                case "openai-compatible" -> NpcConversationBackend.Provider.OPENAI_COMPATIBLE;
                default -> throw new IllegalArgumentException("Unknown configured provider");
            };
            URI endpoint = URI.create(core.getConfig().getString(provider == NpcConversationBackend.Provider.OLLAMA ? "ai.local-endpoint" : "ai.endpoint",
                    provider == NpcConversationBackend.Provider.OLLAMA ? "http://127.0.0.1:11434/api/chat" : "https://api.openai.com/v1/chat/completions"));
            String key = secrets.getProperty("JEEVA_API_KEY", "");
            if (key.isBlank() && "api.openai.com".equals(endpoint.getHost())) key = secrets.getProperty("OPENAI_API_KEY", "");
            if (provider == NpcConversationBackend.Provider.OPENAI_COMPATIBLE && "api.openai.com".equals(endpoint.getHost()) && key.isBlank())
                throw new IllegalArgumentException("Configured OpenAI credential missing");
            String model = core.getConfig().getString(provider == NpcConversationBackend.Provider.OLLAMA ? "ai.local-model" : "ai.model",
                    provider == NpcConversationBackend.Provider.OLLAMA ? "" : "gpt-4.1-mini");
            settings = new NpcConversationBackend.Settings(provider, endpoint, model, key,
                    core.getConfig().getInt("ai.daily-request-limit", 200), core.getConfig().getInt("ai.per-player-five-minute-limit", 10));
        } catch (RuntimeException invalid) {
            core.getLogger().warning("JEEVA generative provider is not configured correctly; local dialogue remains available. No remote request was made.");
            settings = new NpcConversationBackend.Settings(NpcConversationBackend.Provider.OFFLINE, null, "", "", 0, 10);
        }
        backend = new NpcConversationBackend(settings);
        core.getLogger().info("JEEVA conversation backend: " + backend.status() + ". Dialogue never executes commands or financial actions.");
    }

    void speak(Player player, String id, String name, String role, String department, String language, String prompt, String greeting) {
        reply(player, id, name, role, department, language, prompt, greeting,
                answer -> player.sendMessage("§6" + name + ": §f" + answer));
    }

    void reply(Player player, String id, String name, String role, String department, String language, String prompt,
               String greeting, Consumer<String> deliver) {
        if (closed || !core.isAuthenticated(player)) return;
        UUID session = core.authenticatedSession(player);
        String question = RoleplayText.clean(prompt);
        if (question.isBlank()) return;
        String selectedLanguage = RoleplayText.language(question, language);
        String local = Jeeva.reply(player, id, name, role, department, selectedLanguage, question, greeting);
        var request = new NpcConversationBackend.Request(player.getUniqueId(), session, id, name, role, department, selectedLanguage, question, local);
        backend.reply(request).whenComplete((answer, failure) -> {
            if (closed) return;
            Runnable dispatch = () -> {
                if (closed || !player.isOnline() || !Objects.equals(session, core.authenticatedSession(player))) return;
                if (answer != null && answer.status().equals("cancelled")) return;
                String resultStatus = answer == null ? "provider-unavailable" : answer.status();
                lastResult = resultStatus;
                String mode = answer != null && answer.generated() ? "generated" : resultStatus;
                if (!mode.equals(reportedMode.put(player.getUniqueId(), mode)) && !mode.equals("generated")) {
                    player.sendMessage(mode.equals("offline")
                            ? "§7[JEEVA] Local dialogue is active; no generative AI model is connected."
                            : "§7[JEEVA] The generative service is " + mode.replace('-', ' ') + "; this reply uses local dialogue.");
                }
                String text = failure == null && answer != null ? answer.text() : local;
                if (!text.isBlank()) deliver.accept(RoleplayText.clean(text));
            };
            if (Bukkit.isPrimaryThread()) dispatch.run();
            else if (core.isEnabled()) {
                try { Bukkit.getScheduler().runTask(core, dispatch); }
                catch (org.bukkit.plugin.IllegalPluginAccessException stopped) { /* Plugin disabled after the check. */ }
            }
        });
    }

    void forget(UUID player) { backend.forget(player); reportedMode.remove(player); }
    String status() { return "configured=" + backend.status() + ", last-result=" + lastResult; }
    @Override public void close() { closed = true; backend.close(); reportedMode.clear(); }
}
