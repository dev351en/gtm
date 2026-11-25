package com.sdcraft.core;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ConsoleSecurityTest {
    private static final String TOKEN = "owner-token-abcdefghijklmnopqrstuvwxyz0123456789";

    @Test void bearerRequiresExactStrongToken() {
        assertTrue(ConsoleSecurity.authorized(TOKEN, "Bearer " + TOKEN));
        for (String header : new String[]{"", "Basic " + TOKEN, "bearer " + TOKEN, "Bearer " + TOKEN + "x", "Bearer " + TOKEN + " ", "Bearer "})
            assertFalse(ConsoleSecurity.authorized(TOKEN, header));
        assertFalse(ConsoleSecurity.authorized(TOKEN, null));
        assertFalse(ConsoleSecurity.authorized(null, "Bearer " + TOKEN));
        assertFalse(ConsoleSecurity.authorized("short", "Bearer short"));
    }

    @Test void allowsOnlyBoundLoopbackHostAndSameOrigin() {
        assertTrue(ConsoleSecurity.localRequest("127.0.0.1:8765", null, 8765));
        assertTrue(ConsoleSecurity.localRequest("localhost:8765", "http://localhost:8765", 8765));
        assertTrue(ConsoleSecurity.localRequest("127.0.0.1:8765", "http://127.0.0.1:8765", 8765));
        for (String host : new String[]{"evil.example:8765", "localhost.evil.example:8765", "127.0.0.1", "127.0.0.1:8766", "[::1]:8765", "localhost:8765@evil.example", "localhost:8765,evil.example"})
            assertFalse(ConsoleSecurity.localRequest(host, null, 8765), host);
        assertFalse(ConsoleSecurity.localRequest(null, null, 8765));
    }

    @Test void rejectsCrossOriginAndSandboxedOriginEvenWithLocalHost() {
        for (String origin : new String[]{"https://evil.example", "http://localhost:8766", "null", "http://localhost:8765.evil.example", "https://localhost:8765", "http://127.0.0.1:8765/path"})
            assertFalse(ConsoleSecurity.localRequest("localhost:8765", origin, 8765), origin);
    }

    @Test void normalizesOneOptionalLeadingSlashWithoutChangingCommandArguments() {
        assertEquals("save-all flush", ConsoleSecurity.command(" /save-all flush ", false));
        assertEquals("say Hello city!", ConsoleSecurity.command("say Hello city!", false));
        assertEquals("list", ConsoleSecurity.command("/ list", false));
        assertThrows(IllegalArgumentException.class, () -> ConsoleSecurity.command("// list", false));
    }

    @Test void rejectsMultilineControlAndOversizedCommands() {
        for (String command : new String[]{"", " ", "/", "list\nstop", "list\rstop", "list\u0000stop", "list\u0085stop", "list\u2028stop", "x".repeat(241)})
            assertThrows(IllegalArgumentException.class, () -> ConsoleSecurity.command(command, true));
        assertThrows(IllegalArgumentException.class, () -> ConsoleSecurity.command(null, true));
    }

    @Test void lifecycleAliasesAndNamespacesRequireConfirmation() {
        for (String command : new String[]{"stop", "restart", "reload", "rl", "minecraft:stop", "bukkit:reload", "/Spigot:Restart", "/ stop"}) {
            assertThrows(ConsoleSecurity.ConfirmationRequired.class, () -> ConsoleSecurity.command(command, false), command);
            assertNotNull(ConsoleSecurity.command(command, true));
        }
    }

    @Test void wrappedLifecycleCommandsCannotBypassConfirmation() {
        for (String command : new String[]{"execute run stop", "minecraft:execute as @a run minecraft:stop", "execute as @a run execute at @s run bukkit:reload"}) {
            assertThrows(ConsoleSecurity.ConfirmationRequired.class, () -> ConsoleSecurity.command(command, false), command);
            assertEquals(command, ConsoleSecurity.command(command, true));
        }
        assertEquals("execute run say stop", ConsoleSecurity.command("execute run say stop", false));
        assertEquals("say run stop", ConsoleSecurity.command("say run stop", false));
    }

    @Test void credentialsNeverBecomeConsoleCommandsEvenWithConfirmation() {
        for (String command : new String[]{"login secret", "l secret", "register secret secret", "reg secret secret", "AuthMe:Login secret", "changepassword old new", "gtmauth enroll someone secret", "/ login secret", "execute run minecraft:login secret"})
            assertThrows(IllegalArgumentException.class, () -> ConsoleSecurity.command(command, true), command);
    }

    @Test void redactsBearerAndUrlTokensWithoutDeletingOrdinaryContext() {
        assertEquals("Authorization: Bearer [redacted]", ConsoleSecurity.redact("Authorization: Bearer " + TOKEN));
        assertEquals("http://127.0.0.1:8765/#token=[redacted]", ConsoleSecurity.redact("http://127.0.0.1:8765/#token=" + TOKEN));
        assertEquals("Server has 3 players", ConsoleSecurity.redact("Server has 3 players"));
        assertEquals("", ConsoleSecurity.redact(null));
    }

    @Test void redactsQuotedJsonSecretsIncludingSpaces() {
        String input = "{\"token\":\"long secret with spaces\",\"player\":\"owner\",'password':'two words',api_key=abcd}";
        String redacted = ConsoleSecurity.redact(input);
        for (String secret : new String[]{"long secret", "two words", "abcd"}) assertFalse(redacted.contains(secret));
        assertTrue(redacted.contains("\"player\":\"owner\""));
    }

    @Test void redactsNamespacedAccountLogsAndPreservesNextLine() {
        String input = "[INFO] Alex issued server command: /authme:login one two\n[INFO] Ready";
        assertEquals("[INFO] Alex issued server command: /authme:login [redacted]\n[INFO] Ready", ConsoleSecurity.redact(input));
        assertFalse(ConsoleSecurity.redact("command: gtmauth enroll owner private pass").contains("private"));
    }

    @Test void removesAnsiColourSequences() {
        assertEquals("Ready", ConsoleSecurity.redact("\u001b[32mReady\u001b[0m"));
    }
}
