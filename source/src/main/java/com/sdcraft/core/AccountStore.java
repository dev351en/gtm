package com.sdcraft.core;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.AtomicMoveNotSupportedException;
import java.util.UUID;
import org.bukkit.configuration.file.YamlConfiguration;

/** Private, demonstration-only starting ledger; not integrated with Vault or purchases.
 * All uses must remain on the server main thread. No PINs or transfer endpoints. */
final class AccountStore {
    private final File file;
    private final YamlConfiguration data;

    AccountStore(File pluginFolder) {
        file = new File(pluginFolder, "players.yml");
        data = YamlConfiguration.loadConfiguration(file);
    }

    boolean ensureOnce(UUID uuid) throws IOException {
        String key = "players." + uuid;
        if (data.getBoolean(key + ".starter-granted", false)) return false;
        // If an existing account was written by another system, halt rather than overwrite it.
        if (data.contains(key)) throw new IllegalStateException("Ambiguous existing player record: " + uuid);
        data.set(key + ".wallet-cents", 50_000L);
        data.set(key + ".bank-cents", 100_000L);
        data.set(key + ".language", "en");
        data.set(key + ".starter-granted", true);
        saveAtomically();
        return true;
    }

    long wallet(UUID uuid) { return data.getLong("players." + uuid + ".wallet-cents", 0L); }
    long bank(UUID uuid) { return data.getLong("players." + uuid + ".bank-cents", 0L); }
    String language(UUID uuid) { return data.getString("players." + uuid + ".language", "en"); }
    boolean registered(UUID uuid) { return data.getBoolean("players." + uuid + ".starter-granted", false); }

    void language(UUID uuid, String lang) throws IOException {
        if (!registered(uuid)) throw new IllegalStateException("No player account");
        if (!lang.equals("en") && !lang.equals("hi")) throw new IllegalArgumentException("Invalid language");
        data.set("players." + uuid + ".language", lang);
        saveAtomically();
    }

    private void saveAtomically() throws IOException {
        Path dest = file.toPath();
        Files.createDirectories(dest.getParent());
        Path temporary = Files.createTempFile(dest.getParent(), "players-", ".tmp");
        try {
            Files.writeString(temporary, data.saveToString(), StandardCharsets.UTF_8);
            try {
                Files.move(temporary, dest, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
            } catch (AtomicMoveNotSupportedException ex) {
                Files.move(temporary, dest, StandardCopyOption.REPLACE_EXISTING);
            }
        } finally {
            Files.deleteIfExists(temporary);
        }
    }
}
