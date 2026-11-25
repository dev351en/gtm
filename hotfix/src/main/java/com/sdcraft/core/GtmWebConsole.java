package com.sdcraft.core;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import com.google.gson.JsonParser;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.InputStream;
import java.lang.management.ManagementFactory;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.SecureRandom;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicBoolean;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.scheduler.BukkitTask;

/** Actual local HTTP control centre. It never exposes a listener to the public network. */
final class GtmWebConsole implements AutoCloseable {
    private static final Gson JSON = new Gson();
    private static final int MAX_BODY = 8192;
    private final SDCraftCorePlugin plugin;
    private final HttpServer server;
    private final ThreadPoolExecutor workers;
    private final ConsoleCommandQueue commands;
    private final AtomicBoolean closed = new AtomicBoolean();
    private final String token;
    private final int port;
    private final Path audit;
    private final Path tokenFile;
    private final BukkitTask ticker;
    private final Properties serverProperties = new Properties();
    private volatile String snapshot = "{\"ready\":false}";

    GtmWebConsole(SDCraftCorePlugin plugin) throws IOException {
        this.plugin = plugin;
        this.port = plugin.getConfig().getInt("web-console.port", 8765);
        if (port < 1024 || port > 65535) throw new IOException("Invalid web-console port");
        byte[] entropy = new byte[32];
        new SecureRandom().nextBytes(entropy);
        token = Base64.getUrlEncoder().withoutPadding().encodeToString(entropy);
        tokenFile = plugin.getDataFolder().toPath().resolve("console-access.token");
        audit = plugin.getDataFolder().toPath().resolve("console-audit.log");
        Path properties = plugin.getDataFolder().toPath().toAbsolutePath().getParent().getParent().resolve("server.properties");
        if (Files.isRegularFile(properties)) try (InputStream in = Files.newInputStream(properties)) { serverProperties.load(in); }
        server = HttpServer.create(new InetSocketAddress("127.0.0.1", port), 16);
        workers = new ThreadPoolExecutor(2, 4, 30, TimeUnit.SECONDS, new ArrayBlockingQueue<>(32), task -> {
            Thread t = new Thread(task, "GTM-local-console"); t.setDaemon(true); return t;
        }, new ThreadPoolExecutor.AbortPolicy());
        commands = new ConsoleCommandQueue(work -> {
            BukkitTask task = Bukkit.getScheduler().runTask(plugin, work);
            return task::cancel;
        }, command -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), command),
            (id, phase, command, outcome) -> Files.writeString(audit,
                Instant.now() + "\towner-console\t" + id + "\t" + phase + "\t" + redact(command) + "\t" + outcome + "\n",
                StandardCharsets.UTF_8, StandardOpenOption.CREATE, StandardOpenOption.APPEND));
        BukkitTask scheduledTicker = null;
        try {
            server.setExecutor(workers);
            server.createContext("/", this::request);
            // Bind first: a second failed startup must not replace the token of
            // a console that is already using the configured port.
            writeToken();
            refresh();
            scheduledTicker = Bukkit.getScheduler().runTaskTimer(plugin, this::refresh, 20, 20);
            server.start();
        } catch (IOException | RuntimeException failure) {
            if (scheduledTicker != null) scheduledTicker.cancel();
            commands.close();
            server.stop(0);
            workers.shutdownNow();
            removeOwnedToken();
            throw failure;
        }
        ticker = scheduledTicker;
        plugin.getLogger().info("GTM Control Centre listening on http://127.0.0.1:" + port + ". Use /gtmweb as an authenticated administrator, or Open-Control-Centre.bat.");
    }

    String ownerUrl() { return "http://127.0.0.1:" + port + "/#token=" + token; }

    private void writeToken() throws IOException {
        Path directory = tokenFile.toAbsolutePath().getParent();
        Files.createDirectories(directory);
        if (Files.isSymbolicLink(tokenFile)) throw new IOException("Console token path must be a regular local file");
        Path temporary = Files.getFileStore(directory).supportsFileAttributeView("posix")
                ? Files.createTempFile(directory, ".console-access-", ".tmp", PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")))
                : Files.createTempFile(directory, ".console-access-", ".tmp");
        try {
            Files.writeString(temporary, token + "\n", StandardCharsets.UTF_8, StandardOpenOption.TRUNCATE_EXISTING);
            try { Files.move(temporary, tokenFile, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING); }
            catch (AtomicMoveNotSupportedException unsupported) { Files.move(temporary, tokenFile, StandardCopyOption.REPLACE_EXISTING); }
        } finally { Files.deleteIfExists(temporary); }
    }

    private void removeOwnedToken() {
        try {
            if (!Files.isSymbolicLink(tokenFile) && Files.isRegularFile(tokenFile)
                    && Files.readString(tokenFile, StandardCharsets.UTF_8).strip().equals(token)) Files.deleteIfExists(tokenFile);
        } catch (IOException unavailable) { plugin.getLogger().warning("The retired console token file could not be removed."); }
    }

    private String redact(String value) { return ConsoleSecurity.redact(value).replace(token, "[redacted]"); }

    private void refresh() {
        if (closed.get()) return;
        // Only this main-thread callback reads live game state.
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("ready", true);
        data.put("at", Instant.now().toString());
        data.put("version", plugin.getDescription().getVersion());
        data.put("minecraft", Bukkit.getMinecraftVersion());
        data.put("server", Bukkit.getName());
        double tps = Bukkit.getTPS()[0], mspt = Bukkit.getAverageTickTime();
        data.put("tps", Double.isFinite(tps) ? tps : 0);
        data.put("mspt", Double.isFinite(mspt) ? mspt : 0);
        data.put("commandBusy", commands.busy());
        data.put("uptimeSeconds", ManagementFactory.getRuntimeMXBean().getUptime() / 1000);
        Runtime runtime = Runtime.getRuntime();
        data.put("heapUsedMb", (runtime.totalMemory() - runtime.freeMemory()) / 1048576);
        data.put("heapMaxMb", runtime.maxMemory() / 1048576);
        data.put("maxPlayers", Bukkit.getMaxPlayers());
        List<Map<String, Object>> players = new ArrayList<>();
        for (Player p : Bukkit.getOnlinePlayers()) {
            if (p.hasMetadata("NPC")) continue;
            Map<String, Object> entry = new LinkedHashMap<>();
            entry.put("name", p.getName()); entry.put("uuid", p.getUniqueId().toString());
            entry.put("authenticated", plugin.isAuthenticated(p)); entry.put("packLoaded", plugin.hasLoadedGtmPack(p));
            entry.put("world", p.getWorld().getName()); entry.put("x", p.getLocation().getBlockX());
            entry.put("y", p.getLocation().getBlockY()); entry.put("z", p.getLocation().getBlockZ());
            entry.put("ping", p.getPing()); entry.put("health", p.getHealth());
            players.add(entry);
        }
        data.put("players", players);
        List<Map<String, Object>> worlds = new ArrayList<>();
        Bukkit.getWorlds().forEach(w -> worlds.add(Map.of("name", w.getName(), "chunks", w.getLoadedChunks().length,
                "entities", w.getEntityCount(), "time", w.getTime())));
        data.put("worlds", worlds);
        Map<String, Object> features = new LinkedHashMap<>();
        for (String key : List.of("phone.enabled", "vehicles.enabled", "equipment.enabled", "furniture.enabled", "wardrobe.enabled", "taxi.enabled", "food-delivery.enabled"))
            features.put(key, plugin.getConfig().getBoolean(key, key.equals("phone.enabled")));
        features.put("ai.external-enabled", plugin.getConfig().getBoolean("ai.external-enabled", false));
        data.put("features", features);
        data.put("pack", Map.of("url", serverProperties.getProperty("resource-pack", ""),
                "sha1", serverProperties.getProperty("resource-pack-sha1", ""),
                "required", serverProperties.getProperty("require-resource-pack", "false")));
        data.put("plugins", java.util.Arrays.stream(Bukkit.getPluginManager().getPlugins()).map(p -> Map.of(
                "name", p.getName(), "version", p.getDescription().getVersion(), "enabled", p.isEnabled())).toList());
        snapshot = JSON.toJson(data);
    }

    private void request(HttpExchange exchange) throws IOException {
        try {
            var headers = exchange.getResponseHeaders();
            headers.set("X-Content-Type-Options", "nosniff");
            headers.set("Referrer-Policy", "no-referrer");
            headers.set("X-Frame-Options", "DENY");
            headers.set("Cache-Control", "no-store");
            headers.set("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'");
            if (!ConsoleSecurity.localRequest(exchange.getRequestHeaders().getFirst("Host"), exchange.getRequestHeaders().getFirst("Origin"), port)) {
                json(exchange, 403, Map.of("error", "Use the localhost control centre address.")); return;
            }
            String path = exchange.getRequestURI().getPath(), method = exchange.getRequestMethod();
            if (path.equals("/") || path.equals("/console.css") || path.equals("/console.js")) {
                if (!method.equals("GET")) { json(exchange, 405, Map.of("error", "GET required")); return; }
                String file = path.equals("/") ? "index.html" : path.substring(1);
                try (InputStream in = getClass().getResourceAsStream("/web-console/" + file)) {
                    if (in == null) { json(exchange, 404, Map.of("error", "Console assets unavailable")); return; }
                    send(exchange, 200, file.endsWith("html") ? "text/html; charset=utf-8" : file.endsWith("css") ? "text/css; charset=utf-8" : "text/javascript; charset=utf-8", in.readAllBytes());
                }
                return;
            }
            if (!path.startsWith("/api/")) { json(exchange, 404, Map.of("error", "Not found")); return; }
            if (!ConsoleSecurity.authorized(token, exchange.getRequestHeaders().getFirst("Authorization"))) {
                json(exchange, 401, Map.of("error", "Sign in using the local console token or open /gtmweb as an administrator.")); return;
            }
            if (path.equals("/api/status") && method.equals("GET")) {
                send(exchange, 200, "application/json; charset=utf-8", snapshot.getBytes(StandardCharsets.UTF_8)); return;
            }
            if (path.equals("/api/logs") && method.equals("GET")) {
                json(exchange, 200, Map.of("lines", recentLog())); return;
            }
            if (path.equals("/api/command") && method.equals("POST")) { command(exchange); return; }
            if (path.equals("/api/guide") && method.equals("POST")) {
                JsonObject body = body(exchange);
                String question = string(body, "question", 500);
                if (question.isBlank()) throw new IllegalArgumentException("Enter a question for the local guide.");
                json(exchange, 200, Map.of("mode", "local", "answer", guide(question))); return;
            }
            json(exchange, 404, Map.of("error", "Unknown endpoint or method"));
        } catch (ConsoleSecurity.ConfirmationRequired ex) {
            json(exchange, 409, Map.of("error", ex.getMessage(), "confirmationRequired", true));
        } catch (IllegalArgumentException | IllegalStateException ex) {
            json(exchange, 400, Map.of("error", "Invalid request: " + redact(ex.getMessage())));
        } catch (Exception ex) {
            plugin.getLogger().warning("Control Centre request failed: " + ex.getClass().getSimpleName());
            json(exchange, 503, Map.of("error", "The request could not finish. Check the game server status before retrying."));
        } finally { exchange.close(); }
    }

    private JsonObject body(HttpExchange e) throws IOException {
        if (!String.valueOf(e.getRequestHeaders().getFirst("Content-Type")).split(";", 2)[0].strip().equalsIgnoreCase("application/json"))
            throw new IllegalArgumentException("JSON content type required");
        byte[] bytes = e.getRequestBody().readNBytes(MAX_BODY + 1);
        if (bytes.length > MAX_BODY) throw new IllegalArgumentException("Request is too large");
        try {
            JsonElement result = JsonParser.parseString(new String(bytes, StandardCharsets.UTF_8));
            if (!result.isJsonObject()) throw new IllegalArgumentException("JSON object required");
            return result.getAsJsonObject();
        } catch (JsonParseException invalid) { throw new IllegalArgumentException("Valid JSON object required"); }
    }

    private static String string(JsonObject body, String key, int maximum) {
        JsonElement value = body.get(key);
        if (value == null || !value.isJsonPrimitive() || !value.getAsJsonPrimitive().isString())
            throw new IllegalArgumentException("A text " + key + " is required.");
        String text = value.getAsString();
        if (text.length() > maximum) throw new IllegalArgumentException(key + " exceeds " + maximum + " characters.");
        return text;
    }

    private void command(HttpExchange e) throws Exception {
        JsonObject body = body(e);
        String text = string(body, "command", 240);
        JsonElement confirmation = body.get("confirmed");
        if (confirmation != null && (!confirmation.isJsonPrimitive() || !confirmation.getAsJsonPrimitive().isBoolean()))
            throw new IllegalArgumentException("Confirmation must be true or false.");
        String command = ConsoleSecurity.command(text, confirmation != null && confirmation.getAsBoolean());
        if (command.contains(token)) throw new IllegalArgumentException("Do not enter a console access token as a server command.");
        ConsoleCommandQueue.Ticket ticket;
        try { ticket = commands.submit(command); }
        catch (ConsoleCommandQueue.Busy busy) { json(e, 429, Map.of("error", busy.getMessage())); return; }
        try {
            ConsoleCommandQueue.Result result = ticket.result().get(5, TimeUnit.SECONDS);
            json(e, 200, Map.of("accepted", result.accepted(), "command", redact(result.command()), "requestId", result.id().toString(),
                    "lines", result.auditWarning().isEmpty() ? List.of() : List.of(result.auditWarning()), "running", false));
        }
        catch (TimeoutException timeout) {
            if (ticket.cancelBeforeStart()) json(e, 504, Map.of("error", "The server did not start this command in time. It was cancelled before execution."));
            else json(e, 202, Map.of("accepted", true, "command", redact(command), "requestId", ticket.id().toString(), "running", true,
                    "lines", List.of("The command started and is still running. Wait for the server log before repeating it.")));
        } catch (InterruptedException interrupted) {
            ticket.cancelBeforeStart();
            Thread.currentThread().interrupt();
            throw interrupted;
        }
    }

    private List<String> recentLog() throws IOException {
        Path file = plugin.getDataFolder().toPath().toAbsolutePath().getParent().getParent().resolve("logs/latest.log");
        if (!Files.isRegularFile(file)) return List.of("The server has not created a log yet.");
        // Bound both I/O and output even on long-running servers.
        try (var channel = Files.newByteChannel(file, StandardOpenOption.READ)) {
            channel.position(Math.max(0, channel.size() - 32768));
            java.nio.ByteBuffer buffer = java.nio.ByteBuffer.allocate(32768);
            channel.read(buffer); buffer.flip();
            String text = StandardCharsets.UTF_8.decode(buffer).toString();
            List<String> all = text.lines().map(this::redact).toList();
            return all.subList(Math.max(0, all.size() - 120), all.size());
        }
    }

    private String guide(String question) {
        String q = question.toLowerCase(Locale.ROOT);
        if (q.contains("gun") || q.contains("weapon")) return "Open Phone → Equipment or /gun. The first page now shows the native fictional firearms. Buy a weapon normally; right-click to fire and sneak + right-click to reload with its matching ammunition. Existing possessions are kept. The repair saves one native Kavach-9 starter and its receipt together in player data. If your inventory is full, clear a slot and use /gun to retry.";
        if (q.contains("car") || q.contains("drive") || q.contains("vehicle")) return "Use Phone → Car App or /car for your owned garage. Choose a vehicle and a clear supported road location. W/S control throttle and braking/reverse; A/D steer, Space brakes, Shift exits. The repair corrects model/pivot alignment and smooths steering. Fuel, damage and permissions remain active.";
        if (q.contains("pack") || q.contains("texture") || q.contains("icon")) return "The original phone icons were missing because the server advertised the old pack. The Assets panel shows the current advertised URL and SHA-1. Players must accept the matching repaired pack; /pack requests it again. A successful download and a client visual check are separate checks.";
        if (q.contains("backup") || q.contains("update")) return "Use the supplied Update-GTM installer with the server stopped. It verifies the repair manifest, copies only runtime files, backs up replaced files, preserves world/accounts/progress and provides a rollback manifest. The web console's Save world button flushes the current world; it is not a complete backup.";
        if (q.contains("ai") || q.contains("jeeva")) return "JEEVA here is the local city guide. It works without a paid API. In-game Phone → JEEVA provides service shortcuts and deterministic assistance. This control centre does not claim a live language model or enable external billing.";
        if (q.contains("tps") || q.contains("lag") || q.contains("status") || q.contains("player")) return "The Overview and Players panels read live Paper state once each second: TPS, average tick time, memory, player authentication and resource-pack status. Use 'list' in Console for the server's own player response. Long ticks are visible in the live log; the dashboard does not change hosting limits.";
        return "I can help with phone textures, weapons, driving, live status and the repair installer. Choose one of the quick questions, or ask about those systems. This is a local guide, so I will not invent a server action or claim that a change has been deployed.";
    }

    private static void json(HttpExchange e, int status, Object object) throws IOException {
        send(e, status, "application/json; charset=utf-8", JSON.toJson(object).getBytes(StandardCharsets.UTF_8));
    }
    private static void send(HttpExchange e, int status, String type, byte[] content) throws IOException {
        e.getResponseHeaders().set("Content-Type", type);
        e.sendResponseHeaders(status, content.length);
        e.getResponseBody().write(content);
    }
    @Override public void close() {
        if (!closed.compareAndSet(false, true)) return;
        commands.close();
        ticker.cancel();
        server.stop(0);
        workers.shutdownNow();
        removeOwnedToken();
    }
}
