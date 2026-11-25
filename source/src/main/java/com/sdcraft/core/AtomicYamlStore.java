package com.sdcraft.core;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.Arrays;
import org.bukkit.configuration.InvalidConfigurationException;
import org.bukkit.configuration.file.YamlConfiguration;

/** Atomic, fail-closed YAML aggregate; failed commits restore the last durable state. */
final class AtomicYamlStore {
    private static final int LIMIT = 16 * 1024 * 1024;
    private final Path file;
    private final YamlConfiguration data = new YamlConfiguration();
    private String committed;
    private byte[] diskBytes;

    AtomicYamlStore(Path file) throws IOException {
        this.file = file.toAbsolutePath().normalize();
        Files.createDirectories(this.file.getParent());
        if (Files.isSymbolicLink(this.file)) throw new IOException("State symlinks are not supported");
        diskBytes = Files.exists(this.file) ? readBounded(this.file) : null;
        try {
            if (diskBytes != null) data.loadFromString(new String(diskBytes, StandardCharsets.UTF_8));
        } catch (InvalidConfigurationException ex) {
            throw new IOException("Invalid state; existing bytes were preserved", ex);
        }
        committed = data.saveToString();
    }

    YamlConfiguration data() { return data; }

    synchronized void commit() throws IOException {
        Path temporary = null;
        try (var channel = FileChannel.open(file.resolveSibling(file.getFileName() + ".lock"),
                StandardOpenOption.CREATE, StandardOpenOption.WRITE); var ignored = channel.lock()) {
            if (Files.isSymbolicLink(file)) throw new IOException("State symlinks are not supported");
            byte[] current = Files.exists(file) ? readBounded(file) : null;
            if (!Arrays.equals(current, diskBytes)) throw new IOException("State changed outside this server; reload required");
            String candidate = data.saveToString();
            byte[] bytes = candidate.getBytes(StandardCharsets.UTF_8);
            if (bytes.length > LIMIT) throw new IOException("State size limit exceeded");
            temporary = Files.createTempFile(file.getParent(), ".gtm-state-", ".tmp");
            try (var output = FileChannel.open(temporary, StandardOpenOption.WRITE, StandardOpenOption.TRUNCATE_EXISTING)) {
                ByteBuffer buffer = ByteBuffer.wrap(bytes);
                while (buffer.hasRemaining()) output.write(buffer);
                output.force(true);
            }
            Files.move(temporary, file, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            committed = candidate;
            diskBytes = bytes;
        } catch (IOException | RuntimeException ex) {
            try { data.loadFromString(committed); }
            catch (InvalidConfigurationException impossible) { throw new IllegalStateException("Committed state is invalid", impossible); }
            throw ex;
        } finally {
            if (temporary != null) try { Files.deleteIfExists(temporary); } catch (IOException ignored) { }
        }
    }

    private static byte[] readBounded(Path path) throws IOException {
        if (!Files.isRegularFile(path, LinkOption.NOFOLLOW_LINKS) || Files.size(path) > LIMIT)
            throw new IOException("State is not a bounded regular file");
        return Files.readAllBytes(path);
    }
}
