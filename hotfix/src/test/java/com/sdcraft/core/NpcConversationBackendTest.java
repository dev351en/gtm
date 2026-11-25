package com.sdcraft.core;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class NpcConversationBackendTest {
    private HttpServer server;
    private java.util.concurrent.ExecutorService threads;
    private NpcConversationBackend backend;
    private final List<JsonObject> requests = new CopyOnWriteArrayList<>();
    private final AtomicReference<String> response = new AtomicReference<>("{\"choices\":[{\"message\":{\"content\":\"Namaste, how can I help?\"}}]}");
    private final UUID player = UUID.randomUUID(), login = UUID.randomUUID();

    @AfterEach void close() {
        if (backend != null) backend.close();
        if (server != null) server.stop(0);
        if (threads != null) threads.shutdownNow();
    }
    private void start(int daily, int perPlayer, Clock clock) throws Exception {
        server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        threads = Executors.newCachedThreadPool(runnable -> { Thread t = new Thread(runnable); t.setDaemon(true); return t; });
        server.setExecutor(threads);
        server.createContext("/chat", exchange -> {
            requests.add(JsonParser.parseString(new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8)).getAsJsonObject());
            byte[] bytes = response.get().getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, bytes.length);
            try (var stream = exchange.getResponseBody()) { stream.write(bytes); }
        });
        server.start();
        backend = new NpcConversationBackend(new NpcConversationBackend.Settings(NpcConversationBackend.Provider.OPENAI_COMPATIBLE,
                URI.create("http://127.0.0.1:" + server.getAddress().getPort() + "/chat"), "fixture-model", "", daily, perPlayer), clock);
    }
    private NpcConversationBackend.Request request(String npc, UUID session, String question) {
        return new NpcConversationBackend.Request(player, session, npc, "Asha", "shopkeeper", "retail", "hinglish", question, "Local fallback");
    }
    private NpcConversationBackend.Reply ask(String npc, String text) throws Exception {
        return backend.reply(request(npc, login, text)).get(3, TimeUnit.SECONDS);
    }

    @Test void offlineDialogueDoesNotContactAnyProvider() throws Exception {
        backend = new NpcConversationBackend(new NpcConversationBackend.Settings(NpcConversationBackend.Provider.OFFLINE, null, "", "", 0, 10));
        var reply = ask("npc_a", "Hello");
        assertFalse(reply.generated()); assertEquals("offline", reply.status()); assertEquals("Local fallback", reply.text());
    }
    @Test void actualHttpRoundTripBuildsBoundedTextOnlyContext() throws Exception {
        start(200, 10, Clock.systemUTC());
        var reply = ask("npc_a", "Bhai, kya kaam karte ho?");
        assertTrue(reply.generated()); assertEquals("Namaste, how can I help?", reply.text());
        var sent = requests.getFirst();
        assertEquals("fixture-model", sent.get("model").getAsString());
        assertFalse(sent.get("stream").getAsBoolean()); assertFalse(sent.has("tools"));
        assertTrue(sent.getAsJsonArray("messages").get(0).getAsJsonObject().get("content").getAsString().contains("Hinglish"));
        assertEquals(2, sent.getAsJsonArray("messages").size());
    }
    @Test void memoryIsIsolatedByNpcAndAuthenticatedSession() throws Exception {
        start(200, 10, Clock.systemUTC());
        ask("npc_a", "A private conversation");
        ask("npc_b", "Different NPC");
        assertEquals(2, requests.get(1).getAsJsonArray("messages").size());
        ask("npc_a", "Continue A");
        assertEquals(4, requests.get(2).getAsJsonArray("messages").size());
        assertFalse(requests.get(2).toString().contains("Different NPC"));
        backend.reply(request("npc_a", UUID.randomUUID(), "New login")).get(3, TimeUnit.SECONDS);
        assertEquals(2, requests.get(3).getAsJsonArray("messages").size());
    }
    @Test void logoutClearsMemoryButDoesNotResetAccountQuota() throws Exception {
        start(200, 1, Clock.systemUTC()); ask("npc_a", "First request"); backend.forget(player);
        var reply = backend.reply(request("npc_a", UUID.randomUUID(), "Try quota reset")).get(3, TimeUnit.SECONDS);
        assertEquals("player-limit", reply.status()); assertEquals(1, requests.size());
    }
    @Test void quotaAndRollingWindowUseActualElapsedTime() throws Exception {
        MutableClock clock = new MutableClock(); start(2, 1, clock);
        assertTrue(ask("npc_a", "First").generated());
        assertEquals("player-limit", ask("npc_b", "Second").status());
        clock.advance(300_001);
        assertTrue(ask("npc_a", "Second after window").generated());
        assertEquals("daily-limit", ask("npc_b", "Daily cap").status());
        clock.advance(86_400_000);
        assertTrue(ask("npc_b", "Next day").generated());
    }
    @Test void oversizedAndMalformedBodiesFallBackWithoutInventingGeneratedSuccess() throws Exception {
        start(200, 10, Clock.systemUTC());
        response.set("x".repeat(70_000));
        assertFalse(ask("npc_a", "Oversized").generated());
        response.set("{bad json");
        var failed = ask("npc_a", "Malformed");
        assertFalse(failed.generated()); assertEquals("Local fallback", failed.text());
        response.set("{\"choices\":[{\"message\":{\"content\":\"Recovered\"}}]}");
        assertTrue(ask("npc_a", "Recovered").generated());
    }
    @Test void outputIsPlainBoundedTextAndOllamaEnvelopeIsSupported() {
        String answer = NpcConversationBackend.parse(NpcConversationBackend.Provider.OLLAMA,
                "{\"message\":{\"content\":\"§cNamaste\\n" + "a".repeat(300) + "\"}}");
        assertFalse(answer.contains("§")); assertFalse(answer.contains("\n")); assertEquals(160, answer.codePointCount(0, answer.length()));
    }
    @Test void logoutCancelsPendingReplyAndOldCompletionCannotBecomeNewSessionMemory() throws Exception {
        start(200, 10, Clock.systemUTC());
        CountDownLatch arrived = new CountDownLatch(1), release = new CountDownLatch(1);
        server.removeContext("/chat");
        server.createContext("/chat", exchange -> {
            JsonObject body = JsonParser.parseString(new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8)).getAsJsonObject();
            requests.add(body);
            if (body.toString().contains("old slow question")) {
                arrived.countDown();
                try { release.await(5, TimeUnit.SECONDS); } catch (InterruptedException stopped) { Thread.currentThread().interrupt(); }
            }
            byte[] bytes = response.get().getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, bytes.length);
            try (var output = exchange.getResponseBody()) { output.write(bytes); }
        });
        try {
            var old = backend.reply(request("npc_a", login, "old slow question"));
            assertTrue(arrived.await(2, TimeUnit.SECONDS));
            assertEquals("busy", ask("npc_b", "Concurrent request").status());
            backend.forget(player);
            assertEquals("cancelled", old.get(1, TimeUnit.SECONDS).status());
            UUID nextLogin = UUID.randomUUID();
            assertTrue(backend.reply(request("npc_a", nextLogin, "Fresh session")).get(3, TimeUnit.SECONDS).generated());
            assertEquals(2, requests.getLast().getAsJsonArray("messages").size());
            release.countDown();
            assertFalse(requests.getLast().toString().contains("old slow question"));
        } finally { release.countDown(); }
    }
    @Test void stalledProviderCannotLeaveNpcReplyLoadingIndefinitely() throws Exception {
        start(200, 10, Clock.systemUTC());
        CountDownLatch release = new CountDownLatch(1);
        server.removeContext("/chat");
        server.createContext("/chat", exchange -> {
            exchange.getRequestBody().readAllBytes(); exchange.sendResponseHeaders(200, 1000);
            try (var output = exchange.getResponseBody()) {
                output.write('{'); output.flush();
                try { release.await(12, TimeUnit.SECONDS); } catch (InterruptedException stopped) { Thread.currentThread().interrupt(); }
            }
        });
        try {
            long start = System.nanoTime();
            var result = backend.reply(request("npc_a", login, "Delayed provider")).get(11, TimeUnit.SECONDS);
            assertFalse(result.generated()); assertEquals("Local fallback", result.text());
            assertTrue(TimeUnit.NANOSECONDS.toSeconds(System.nanoTime() - start) <= 10);
        } finally { release.countDown(); }
    }
    @Test void endpointsRejectUnencryptedRemoteOrCredentialBearingUrls() {
        assertThrows(IllegalArgumentException.class, () -> NpcConversationBackend.validateEndpoint(URI.create("http://example.com/chat")));
        assertThrows(IllegalArgumentException.class, () -> NpcConversationBackend.validateEndpoint(URI.create("https://user:password@example.com/chat")));
        assertThrows(IllegalArgumentException.class, () -> NpcConversationBackend.validateEndpoint(URI.create("https://example.com/chat?key=secret")));
        assertDoesNotThrow(() -> NpcConversationBackend.validateEndpoint(URI.create("http://127.0.0.1:11434/api/chat")));
        assertDoesNotThrow(() -> NpcConversationBackend.validateEndpoint(URI.create("https://api.openai.com/v1/chat/completions")));
    }
    @Test void closeAndInvalidIdentityCannotStartInference() throws Exception {
        start(200, 10, Clock.systemUTC()); backend.close();
        assertEquals("closed", ask("npc_a", "After shutdown").status()); assertTrue(requests.isEmpty());
        assertThrows(IllegalArgumentException.class, () -> backend.reply(request("../../other-npc", login, "Invalid")));
    }

    private static final class MutableClock extends Clock {
        private long now = Instant.parse("2026-11-25T12:00:00Z").toEpochMilli();
        void advance(long millis) { now += millis; }
        @Override public ZoneId getZone() { return ZoneOffset.UTC; }
        @Override public Clock withZone(ZoneId zone) { return this; }
        @Override public Instant instant() { return Instant.ofEpochMilli(now); }
    }
}
