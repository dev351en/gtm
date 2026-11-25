package com.sdcraft.core;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Pattern;

/** Small, dependency-free policy shared by the HTTP adapter and regression checks. */
final class ConsoleSecurity {
    private static final Set<String> CONFIRM = Set.of("stop", "restart", "reload", "rl");
    private static final Set<String> PRIVATE = Set.of("login", "l", "register", "reg", "changepassword", "changepass", "password", "gtmauth");
    private static final Pattern AUTH_COMMAND = Pattern.compile("(?i)((?:issued server command:|command:)\\s*/?(?:[a-z0-9_.-]+:)?(?:login|l|register|reg|changepassword|changepass|password|gtmauth)\\b)[^\\r\\n]*");
    private static final Pattern NAMED_SECRET = Pattern.compile("(?i)((?:[\\\"']?)(?:api[_-]?key|token|password|secret)(?:[\\\"']?)\\s*[=:]\\s*)(?:\\\"[^\\\"\\r\\n]*\\\"|'[^'\\r\\n]*'|[^\\s,;]+)");

    static boolean authorized(String expected, String header) {
        if (expected == null || expected.length() < 32 || header == null || !header.startsWith("Bearer ")) return false;
        return MessageDigest.isEqual(expected.getBytes(StandardCharsets.UTF_8), header.substring(7).getBytes(StandardCharsets.UTF_8));
    }

    static boolean localRequest(String host, String origin, int port) {
        String a = "127.0.0.1:" + port, b = "localhost:" + port;
        if (!a.equals(host) && !b.equals(host)) return false;
        return origin == null || origin.equals("http://" + a) || origin.equals("http://" + b);
    }

    static String command(String input, boolean confirmed) {
        if (input == null || input.isBlank() || input.length() > 240 || input.codePoints().anyMatch(c -> Character.isISOControl(c) || c == 0x2028 || c == 0x2029))
            throw new IllegalArgumentException("Enter one server command, up to 240 characters.");
        String command = input.strip();
        if (command.startsWith("/")) command = command.substring(1).stripLeading();
        if (command.isBlank() || command.startsWith("/")) throw new IllegalArgumentException("Enter a server command without a leading slash.");
        inspectCommand(command, confirmed);
        return command;
    }

    private static void inspectCommand(String command, boolean confirmed) {
        String[] words = command.split("\\s+");
        String simple = simpleName(words[0]);
        inspectName(simple, confirmed);
        // Vanilla execute can wrap another execute or a lifecycle/auth command.
        // Check the actual command after each run, rather than a say message.
        if (simple.equals("execute")) {
            for (int i = 1; i + 1 < words.length; i++) {
                if (!words[i].equalsIgnoreCase("run")) continue;
                String nested = simpleName(words[++i]);
                inspectName(nested, confirmed);
                if (!nested.equals("execute")) break;
            }
        }
    }

    private static String simpleName(String name) {
        name = name.toLowerCase(Locale.ROOT);
        return name.contains(":") ? name.substring(name.lastIndexOf(':') + 1) : name;
    }

    private static void inspectName(String name, boolean confirmed) {
        if (PRIVATE.contains(name)) throw new IllegalArgumentException("Use the game's private authentication flow for account credentials.");
        if (CONFIRM.contains(name) && !confirmed) throw new ConfirmationRequired("Confirm this server lifecycle command before running it.");
    }

    static String redact(String text) {
        if (text == null) return "";
        String redacted = text.replaceAll("(?i)(Bearer\\s+)[A-Za-z0-9._~+/=-]+", "$1[redacted]");
        redacted = NAMED_SECRET.matcher(redacted).replaceAll("$1[redacted]");
        redacted = AUTH_COMMAND.matcher(redacted).replaceAll("$1 [redacted]");
        return redacted.replaceAll("\\u001B\\[[;\\d]*m", "");
    }

    static final class ConfirmationRequired extends IllegalArgumentException {
        ConfirmationRequired(String message) { super(message); }
    }
}
