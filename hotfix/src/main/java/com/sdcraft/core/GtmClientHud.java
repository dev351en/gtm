package com.sdcraft.core;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.nio.ByteBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.plugin.messaging.PluginMessageListener;
import org.bukkit.scheduler.BukkitTask;

/** Optional client HUD transport. Every action reuses an existing server gate. */
final class GtmClientHud implements PluginMessageListener, Listener, AutoCloseable {
    static final String HELLO = "gtm:hud_hello", STATE = "gtm:hud_state", ACTION = "gtm:hud_action";
    static final int MAX_PAYLOAD = 16_384;
    private final SDCraftCorePlugin core;
    private final GtmPhoneApps phone;
    private final Map<UUID, HudSession> clients = new HashMap<>();
    private final Map<UUID, Long> helloLimits = new HashMap<>();
    private final BukkitTask task;
    private boolean closed;

    GtmClientHud(SDCraftCorePlugin core, GtmPhoneApps phone) {
        this.core = core;
        this.phone = phone;
        var messenger = core.getServer().getMessenger();
        messenger.registerIncomingPluginChannel(core, HELLO, this);
        messenger.registerIncomingPluginChannel(core, ACTION, this);
        messenger.registerOutgoingPluginChannel(core, STATE);
        Bukkit.getPluginManager().registerEvents(this, core);
        task = Bukkit.getScheduler().runTaskTimer(core, this::pulse, 10L, 20L);
    }

    boolean capable(Player player) {
        HudSession client = clients.get(player.getUniqueId());
        return !closed && client != null && client.fresh(System.currentTimeMillis());
    }

    boolean active(Player player) {
        return capable(player) && phone.available(player) && core.hasLoadedGtmPack(player)
                && phone.preferences(player.getUniqueId()).hud() && !core.isDowned(player);
    }

    @Override public void onPluginMessageReceived(String channel, Player player, byte[] bytes) {
        if (closed || !player.isOnline() || bytes.length == 0 || bytes.length > MAX_PAYLOAD) return;
        try {
            JsonObject message = object(bytes);
            if (integer(message, "v") != 1) return;
            long now = System.currentTimeMillis();
            if (HELLO.equals(channel)) {
                if (!"gtm-hud-1.0.0".equals(string(message, "client", 48))) return;
                Long prior = helloLimits.get(player.getUniqueId());
                if (prior != null && now - prior < 500) return;
                helloLimits.put(player.getUniqueId(), now);
                clients.computeIfAbsent(player.getUniqueId(), ignored -> new HudSession(now)).hello(now);
                publish(player);
            } else if (ACTION.equals(channel) && active(player)) {
                HudSession client = clients.get(player.getUniqueId());
                UUID login = core.authenticatedSession(player);
                String kind = string(message, "action", 24);
                if (!kind.equals("app") && !kind.equals("assistant") && !kind.equals("phone")) return;
                String app = kind.equals("app") ? string(message, "app", 64) : "";
                if (kind.equals("app") && !phone.clientAppAvailable(player, app)) return;
                if (!client.accept(login, string(message, "session", 36), integer(message, "sequence"), now)) return;
                if (kind.equals("app")) phone.openClientApp(player, app);
                else if (kind.equals("assistant")) phone.openPage(player, "assistant");
                else phone.open(player);
            }
        } catch (com.google.gson.JsonParseException | IllegalArgumentException | CharacterCodingException rejected) {
            // Untrusted client input never becomes a command, log text or authority.
        } catch (Exception unavailable) {
            player.sendMessage("§eThat phone service is temporarily unavailable. Please try again.");
        }
    }

    private void pulse() {
        if (closed) return;
        clients.keySet().removeIf(id -> Bukkit.getPlayer(id) == null);
        helloLimits.keySet().removeIf(id -> Bukkit.getPlayer(id) == null);
        for (UUID id : java.util.List.copyOf(clients.keySet())) {
            Player player = Bukkit.getPlayer(id);
            if (player != null) {
                try { publish(player); }
                catch (RuntimeException unavailable) { sendInactive(player); }
            }
        }
    }

    private void publish(Player player) {
        publish(player, false);
    }

    boolean openPhone(Player player) {
        if (!active(player)) return false;
        publish(player, true);
        return true;
    }

    private void publish(Player player, boolean openPhone) {
        HudSession client = clients.get(player.getUniqueId());
        if (client == null) return;
        UUID login = core.authenticatedSession(player);
        client.authenticate(login);
        JsonObject data = new JsonObject();
        data.addProperty("v", 1);
        data.addProperty("revision", client.revision());
        boolean enabled = active(player);
        data.addProperty("active", enabled);
        if (enabled) {
            if (openPhone) data.addProperty("openPhone", true);
            data.addProperty("session", login.toString());
            data.addProperty("city", "Indraprastha");
            data.addProperty("district", clean(phone.services().district(player), 96));
            data.addProperty("wanted", Math.max(0, Math.min(5, phone.services().wanted(player))));
            data.addProperty("wallet", money(phone.services().wallet(player)));
            data.addProperty("bank", money(phone.services().bank(player)));
            JsonArray apps = new JsonArray();
            for (var app : phone.clientApps(player)) {
                JsonObject value = new JsonObject();
                value.addProperty("id", app.id());
                value.addProperty("title", app.title());
                value.addProperty("enabled", app.enabled());
                value.addProperty("detail", clean(app.detail(), 160));
                apps.add(value);
            }
            data.add("apps", apps);
            JsonElement vehicle = com.google.gson.JsonNull.INSTANCE;
            var driving = phone.services().driving(player);
            if (driving.isPresent()) {
                var drive = driving.get();
                JsonObject value = new JsonObject();
                value.addProperty("title", clean(drive.title(), 96));
                value.addProperty("speed", finite(Math.abs(drive.blocksPerSecond()) * 3.6, 0, 1000));
                value.addProperty("reverse", drive.blocksPerSecond() < -.05);
                value.addProperty("fuel", finite(drive.energyPercent(), 0, 100));
                value.addProperty("energyKind", clean(drive.energyKind(), 24));
                value.addProperty("body", finite(drive.health(), 0, 100));
                value.addProperty("seats", drive.seats());
                value.addProperty("occupiedSeats", drive.occupiedSeats());
                vehicle = value;
            }
            data.add("vehicle", vehicle);
            JsonArray markers = new JsonArray();
            for (var destination : phone.destinations(player)) {
                if (markers.size() == 32) break;
                var at = destination.location();
                if (!at.getWorld().equals(player.getWorld())) continue;
                JsonObject value = new JsonObject();
                value.addProperty("id", destination.id());
                value.addProperty("kind", destination.category());
                value.addProperty("label", clean(destination.title(), 80));
                value.addProperty("x", at.getX());
                value.addProperty("z", at.getZ());
                markers.add(value);
            }
            data.add("markers", markers);
        }
        byte[] bytes = data.toString().getBytes(StandardCharsets.UTF_8);
        if (bytes.length <= MAX_PAYLOAD) player.sendPluginMessage(core, STATE, bytes);
    }

    void authenticationLost(Player player) {
        HudSession client = clients.get(player.getUniqueId());
        if (client == null) return;
        client.authenticate(null);
        sendInactive(player);
    }

    private void sendInactive(Player player) {
        HudSession client = clients.get(player.getUniqueId());
        if (client == null) return;
        if (player.isOnline()) player.sendPluginMessage(core, STATE,
                ("{\"v\":1,\"active\":false,\"revision\":" + client.revision() + "}").getBytes(StandardCharsets.UTF_8));
    }

    @EventHandler public void quit(PlayerQuitEvent event) {
        clients.remove(event.getPlayer().getUniqueId());
        helloLimits.remove(event.getPlayer().getUniqueId());
    }

    @Override public void close() {
        if (closed) return;
        for (UUID id : java.util.List.copyOf(clients.keySet())) {
            Player player = Bukkit.getPlayer(id);
            if (player != null) authenticationLost(player);
        }
        closed = true;
        task.cancel();
        core.getServer().getMessenger().unregisterIncomingPluginChannel(core, HELLO, this);
        core.getServer().getMessenger().unregisterIncomingPluginChannel(core, ACTION, this);
        core.getServer().getMessenger().unregisterOutgoingPluginChannel(core, STATE);
        clients.clear(); helloLimits.clear();
    }

    static JsonObject object(byte[] bytes) throws CharacterCodingException {
        if (bytes.length == 0 || bytes.length > MAX_PAYLOAD) throw new IllegalArgumentException("HUD size");
        String text = StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT)
                .onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(bytes)).toString();
        JsonElement value = JsonParser.parseString(text);
        if (!value.isJsonObject() || value.getAsJsonObject().size() > 8) throw new IllegalArgumentException("HUD object");
        return value.getAsJsonObject();
    }
    static String string(JsonObject value, String key, int max) {
        JsonElement item = value.get(key);
        if (item == null || !item.isJsonPrimitive() || !item.getAsJsonPrimitive().isString()) throw new IllegalArgumentException("HUD string");
        String result = item.getAsString();
        if (result.length() > max || result.codePoints().anyMatch(Character::isISOControl)) throw new IllegalArgumentException("HUD string bound");
        return result;
    }
    static long integer(JsonObject value, String key) {
        JsonElement item = value.get(key);
        if (item == null || !item.isJsonPrimitive() || !item.getAsJsonPrimitive().isNumber()) throw new IllegalArgumentException("HUD integer");
        try { return item.getAsBigDecimal().longValueExact(); }
        catch (ArithmeticException failure) { throw new IllegalArgumentException("HUD integer bound"); }
    }
    private static String clean(String value, int max) {
        String stripped = ChatColor.stripColor(value == null ? "" : value);
        return stripped.codePoints().filter(cp -> !Character.isISOControl(cp)).limit(max)
                .collect(StringBuilder::new, StringBuilder::appendCodePoint, StringBuilder::append).toString();
    }
    private static String money(long cents) { return java.math.BigDecimal.valueOf(cents, 2).toPlainString(); }
    private static double finite(double value, double min, double max) { return Double.isFinite(value) ? Math.max(min, Math.min(max, value)) : min; }
}
