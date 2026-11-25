package com.sdcraft.core.gtm;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** Connection-bound sessions and bounded attempt budgets. No Bukkit or password contents. */
public final class AuthenticationState {
    public record Connection(UUID player, UUID nonce) {}
    private record Session(Connection connection, long deadline, boolean authenticated) {}
    private record Budget(long start, int used) {}
    private static final int MAX_BUDGETS = 8_192;
    private static final long WINDOW_MS = 300_000;
    private final Map<UUID, Session> sessions = new ConcurrentHashMap<>();
    private final Map<String, Budget> budgets = new HashMap<>();

    public Connection begin(UUID player, long now, long timeoutMs) {
        if (now < 0 || timeoutMs <= 0) throw new IllegalArgumentException("Invalid clock");
        Connection connection = new Connection(Objects.requireNonNull(player), UUID.randomUUID());
        sessions.put(player, new Session(connection, Math.addExact(now, timeoutMs), false));
        return connection;
    }
    public boolean current(Connection connection) {
        Session session = sessions.get(connection.player());
        return session != null && session.connection().equals(connection);
    }
    public boolean authenticate(Connection connection, long now, long lifetimeMs) {
        if (now < 0 || lifetimeMs <= 0) throw new IllegalArgumentException("Invalid clock");
        Session current = sessions.get(connection.player());
        if (current == null || !current.connection().equals(connection) || current.deadline() <= now) return false;
        return sessions.replace(connection.player(), current,
                new Session(connection, Math.addExact(now, lifetimeMs), true));
    }
    public boolean authenticated(UUID player, long now) {
        Session session = sessions.get(player);
        return session != null && session.authenticated() && session.deadline() > now;
    }
    public boolean expired(UUID player, long now) {
        Session session = sessions.get(player);
        return session == null || session.deadline() <= now;
    }
    public void end(UUID player) { sessions.remove(player); }
    public void clear() { sessions.clear(); }

    /** Five attempts per identity and twenty per network address per five-minute window. */
    public synchronized boolean acquireAttempt(UUID player, String address, long now) {
        Objects.requireNonNull(player);
        if (now < 0 || address == null || address.length() > 128) throw new IllegalArgumentException("Invalid attempt");
        budgets.entrySet().removeIf(e -> now - e.getValue().start() >= WINDOW_MS);
        String accountKey = "account:" + player, networkKey = "network:" + address;
        if (budgets.size() + (budgets.containsKey(accountKey) ? 0 : 1)
                + (budgets.containsKey(networkKey) ? 0 : 1) > MAX_BUDGETS) return false;
        Budget account = budgets.getOrDefault(accountKey, new Budget(now, 0));
        Budget network = budgets.getOrDefault(networkKey, new Budget(now, 0));
        if (account.used() >= 5 || network.used() >= 20) return false;
        budgets.put(accountKey, new Budget(account.start(), account.used() + 1));
        budgets.put(networkKey, new Budget(network.start(), network.used() + 1));
        return true;
    }
    public synchronized void authenticatedAttempt(UUID player) { budgets.remove("account:" + player); }

    /** Quoted arguments allow passphrases with spaces; malformed input never falls through to commands. */
    public static List<String> arguments(String text) {
        if (text == null || text.length() > 1_024) throw new IllegalArgumentException("Authentication command is too long");
        List<String> values = new ArrayList<>();
        StringBuilder value = new StringBuilder();
        boolean quoted = false, escaped = false, started = false;
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (Character.isISOControl(c)) throw new IllegalArgumentException("Invalid command character");
            if (escaped) { value.append(c); escaped = false; started = true; }
            else if (c == '\\' && i + 1 < text.length() && (text.charAt(i + 1) == '\\' || text.charAt(i + 1) == '"')) {
                escaped = true; started = true;
            }
            else if (c == '"') { quoted = !quoted; started = true; }
            else if (Character.isWhitespace(c) && !quoted) {
                if (started) { values.add(value.toString()); value.setLength(0); started = false; }
            } else { value.append(c); started = true; }
            if (values.size() > 4) throw new IllegalArgumentException("Too many authentication arguments");
        }
        if (quoted || escaped) throw new IllegalArgumentException("Close the quoted passphrase");
        if (started) values.add(value.toString());
        if (values.size() > 4) throw new IllegalArgumentException("Too many authentication arguments");
        return List.copyOf(values);
    }
}
