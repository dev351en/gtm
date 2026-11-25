package com.sdcraft.core;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.ByteArrayOutputStream;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.ByteBuffer;
import java.time.Clock;
import java.time.Duration;
import java.time.LocalDate;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.Flow;
import java.util.concurrent.CompletionStage;

/** Bounded text-only inference transport. It has no game/action/command API. */
final class NpcConversationBackend implements AutoCloseable {
    enum Provider { OFFLINE, OPENAI_COMPATIBLE, OLLAMA }
    record Settings(Provider provider, URI endpoint, String model, String key, int dailyLimit, int playerLimit) {
        Settings {
            if (provider == null || model == null || key == null || dailyLimit < 0 || dailyLimit > 10_000
                    || playerLimit < 1 || playerLimit > 60 || model.length() > 120) throw new IllegalArgumentException("Invalid dialogue settings");
            if (provider != Provider.OFFLINE) validateEndpoint(endpoint);
            if (provider != Provider.OFFLINE && model.isBlank()) throw new IllegalArgumentException("Dialogue model missing");
        }
        @Override public String toString() { return "Settings[provider=" + provider + ", credentials=private]"; }
    }
    record Request(UUID player, UUID session, String npcId, String name, String role, String department,
                   String language, String question, String fallback) {}
    record Reply(String text, boolean generated, String status) {}
    private record Conversation(UUID player, UUID session, String npc) {}
    private record Turn(String role, String content) {}
    private record Pending(UUID token, CompletableFuture<Reply> future) {}

    private final Settings settings;
    private final Clock clock;
    private final HttpClient http;
    private final ThreadPoolExecutor workers;
    private final Map<UUID, Pending> pending = new HashMap<>();
    private final Map<UUID, Deque<Long>> rates = new HashMap<>();
    private final LinkedHashMap<Conversation, Deque<Turn>> histories = new LinkedHashMap<>(16, .75f, true);
    private LocalDate day;
    private int today;
    private boolean closed;

    NpcConversationBackend(Settings settings) { this(settings, Clock.systemUTC()); }
    NpcConversationBackend(Settings settings, Clock clock) {
        this.settings = settings; this.clock = clock; this.day = LocalDate.now(clock);
        http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).followRedirects(HttpClient.Redirect.NEVER).build();
        workers = new ThreadPoolExecutor(2, 2, 30, TimeUnit.SECONDS, new ArrayBlockingQueue<>(8), runnable -> {
            Thread thread = new Thread(runnable, "gtm-jeeva-inference"); thread.setDaemon(true); return thread;
        }, new ThreadPoolExecutor.AbortPolicy());
    }

    synchronized CompletableFuture<Reply> reply(Request request) {
        validate(request);
        if (closed) return fallback(request, "closed");
        if (settings.provider() == Provider.OFFLINE) return fallback(request, "offline");
        if (pending.containsKey(request.player())) return fallback(request, "busy");
        LocalDate current = LocalDate.now(clock);
        if (!current.equals(day)) { day = current; today = 0; }
        if (today >= settings.dailyLimit()) return fallback(request, "daily-limit");
        long now = clock.millis();
        rates.entrySet().removeIf(entry -> entry.getValue().isEmpty() || entry.getValue().peekLast() <= now - 300_000);
        Deque<Long> rate = rates.computeIfAbsent(request.player(), ignored -> new ArrayDeque<>());
        while (!rate.isEmpty() && rate.peekFirst() <= now - 300_000) rate.removeFirst();
        if (rate.size() >= settings.playerLimit()) return fallback(request, "player-limit");
        Conversation key = new Conversation(request.player(), request.session(), request.npcId());
        List<Turn> history = new ArrayList<>(histories.getOrDefault(key, new ArrayDeque<>()));
        UUID token = UUID.randomUUID();
        CompletableFuture<Reply> future = new CompletableFuture<>();
        pending.put(request.player(), new Pending(token, future));
        try {
            workers.execute(() -> {
                Reply result = infer(request, history);
                synchronized (this) {
                    Pending active = pending.get(request.player());
                    if (closed || active == null || !active.token().equals(token)) {
                        future.complete(new Reply(request.fallback(), false, "cancelled")); return;
                    }
                    pending.remove(request.player());
                    if (result.generated()) {
                        Deque<Turn> turns = histories.computeIfAbsent(key, ignored -> new ArrayDeque<>());
                        turns.addLast(new Turn("user", request.question()));
                        turns.addLast(new Turn("assistant", result.text()));
                        while (turns.size() > 8) turns.removeFirst();
                        while (histories.size() > 256) histories.remove(histories.keySet().iterator().next());
                    }
                }
                future.complete(result);
            });
            rate.addLast(now); today++;
        } catch (RejectedExecutionException full) {
            pending.remove(request.player());
            future.complete(new Reply(request.fallback(), false, "queue-full"));
        }
        return future;
    }

    private Reply infer(Request request, List<Turn> history) {
        try {
            JsonObject payload = payload(settings, request, history);
            HttpRequest.Builder builder = HttpRequest.newBuilder(settings.endpoint()).timeout(Duration.ofSeconds(8))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(payload.toString(), StandardCharsets.UTF_8));
            if (!settings.key().isBlank()) builder.header("Authorization", "Bearer " + settings.key());
            var exchange = http.sendAsync(builder.build(), ignored -> new LimitedBody());
            try {
                HttpResponse<byte[]> response = exchange.get(9, TimeUnit.SECONDS);
                if (response.statusCode() != 200) return new Reply(request.fallback(), false, "provider-unavailable");
                String result = parse(settings.provider(), new String(response.body(), StandardCharsets.UTF_8));
                return result.isBlank() ? new Reply(request.fallback(), false, "empty-response") : new Reply(result, true, "generated");
            } finally {
                if (!exchange.isDone()) exchange.cancel(true);
            }
        } catch (InterruptedException interrupted) {
            Thread.currentThread().interrupt();
            return new Reply(request.fallback(), false, "cancelled");
        } catch (Exception unavailable) {
            return new Reply(request.fallback(), false, "provider-unavailable");
        }
    }

    /** Cancel oversized bodies before accumulating them, including chunked replies. */
    private static final class LimitedBody implements HttpResponse.BodySubscriber<byte[]> {
        private final CompletableFuture<byte[]> body = new CompletableFuture<>();
        private final ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        private Flow.Subscription subscription;
        @Override public CompletionStage<byte[]> getBody() { return body; }
        @Override public void onSubscribe(Flow.Subscription value) { subscription = value; value.request(1); }
        @Override public void onNext(List<ByteBuffer> buffers) {
            for (ByteBuffer buffer : buffers) {
                if ((long) bytes.size() + buffer.remaining() > 65_536) {
                    subscription.cancel(); body.completeExceptionally(new IllegalArgumentException("Response size")); return;
                }
                byte[] part = new byte[buffer.remaining()]; buffer.get(part); bytes.writeBytes(part);
            }
            subscription.request(1);
        }
        @Override public void onError(Throwable failure) { body.completeExceptionally(failure); }
        @Override public void onComplete() { body.complete(bytes.toByteArray()); }
    }

    private static JsonObject payload(Settings settings, Request request, List<Turn> history) {
        JsonObject result = new JsonObject(); result.addProperty("model", settings.model());
        JsonArray messages = new JsonArray();
        String system = "You are " + request.name() + ", a fictional " + request.role() + " in department "
                + request.department() + " in Indraprastha, a Mumbai-inspired Minecraft city. Speak naturally in "
                + (request.language().equals("hi") ? "Hindi" : request.language().equals("hinglish") ? "Hinglish" : "English")
                + ". Stay in character. Reply in one or two short sentences, maximum 160 characters. Remember only this NPC's conversation. "
                + "You produce dialogue only: never claim to have transferred money, granted items, moved or arrested anyone. "
                + "For services, invite the player to tap your service menu or open their phone. Do not invent prices, quests, balances or completed actions. "
                + "No commands or tools can be executed by your text.";
        messages.add(message("system", system));
        for (Turn turn : history) messages.add(message(turn.role(), turn.content()));
        messages.add(message("user", request.question())); result.add("messages", messages);
        result.addProperty("stream", false);
        if (settings.provider() == Provider.OLLAMA) {
            JsonObject options = new JsonObject(); options.addProperty("num_predict", 100); options.addProperty("temperature", .65);
            result.add("options", options); result.addProperty("keep_alive", "5m");
        } else result.addProperty("max_tokens", 120);
        return result;
    }

    private static JsonObject message(String role, String content) {
        JsonObject result = new JsonObject(); result.addProperty("role", role); result.addProperty("content", content); return result;
    }
    static String parse(Provider provider, String json) {
        JsonObject root = JsonParser.parseString(json).getAsJsonObject();
        JsonObject message = provider == Provider.OLLAMA ? root.getAsJsonObject("message")
                : root.getAsJsonArray("choices").get(0).getAsJsonObject().getAsJsonObject("message");
        if (message == null || !message.has("content") || !message.get("content").isJsonPrimitive()
                || !message.get("content").getAsJsonPrimitive().isString()) return "";
        return com.sdcraft.core.gtm.RoleplayText.clean(message.get("content").getAsString());
    }
    private static void validate(Request request) {
        if (request == null || request.player() == null || request.session() == null || request.npcId() == null
                || !request.npcId().matches("[a-zA-Z0-9_-]{1,64}") || request.question() == null
                || request.question().isBlank() || request.question().length() > 640 || request.fallback() == null
                || request.name() == null || request.role() == null || request.department() == null || request.language() == null)
            throw new IllegalArgumentException("Invalid NPC dialogue request");
    }
    static void validateEndpoint(URI endpoint) {
        if (endpoint == null || endpoint.getHost() == null || endpoint.getUserInfo() != null
                || endpoint.getQuery() != null || endpoint.getFragment() != null) throw new IllegalArgumentException("Invalid dialogue endpoint");
        String host = endpoint.getHost();
        boolean loopback = host.equals("127.0.0.1") || host.equals("localhost") || host.equals("[::1]") || host.equals("::1");
        if (!"https".equals(endpoint.getScheme()) && !(loopback && "http".equals(endpoint.getScheme())))
            throw new IllegalArgumentException("Dialogue endpoint requires HTTPS or local loopback");
    }
    private static CompletableFuture<Reply> fallback(Request request, String status) {
        return CompletableFuture.completedFuture(new Reply(request.fallback(), false, status));
    }
    synchronized void forget(UUID player) {
        Pending active = pending.remove(player);
        if (active != null) active.future().complete(new Reply("", false, "cancelled"));
        // Keep the rolling request budget across logout; clear only conversation data.
        histories.keySet().removeIf(key -> key.player().equals(player));
    }
    String status() { return settings.provider().name().toLowerCase(java.util.Locale.ROOT); }
    @Override public synchronized void close() {
        if (closed) return; closed = true;
        for (Pending active : pending.values()) active.future().complete(new Reply("", false, "cancelled"));
        pending.clear(); rates.clear(); histories.clear(); workers.shutdownNow();
    }
}
