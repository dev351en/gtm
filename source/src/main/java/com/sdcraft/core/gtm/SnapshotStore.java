package com.sdcraft.core.gtm;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import static java.nio.file.StandardOpenOption.*;

/** Bounded, checksummed, compare-and-swap storage for a single aggregate. No Java deserialization. */
public final class SnapshotStore {
    private static final int MAGIC = 0x47544d31;
    private static final int HEADER = 4 + 8 + 16 + 4 + 32;
    private final Path path, lock;
    private final int limit;
    public record Snapshot(long version, UUID operation, byte[] payload) {
        public Snapshot { Objects.requireNonNull(operation); payload = payload.clone(); }
        @Override public byte[] payload() { return payload.clone(); }
    }
    public SnapshotStore(Path path, int limit) throws IOException {
        if (limit < 1 || limit > 16 * 1024 * 1024) throw new IllegalArgumentException("Invalid size limit");
        Path absolute = path.toAbsolutePath().normalize();
        Files.createDirectories(absolute.getParent());
        this.path = absolute.getParent().toRealPath().resolve(absolute.getFileName());
        this.lock = this.path.resolveSibling(this.path.getFileName() + ".lock");
        this.limit = limit;
    }
    public synchronized Snapshot read() throws IOException {
        try (var channel = FileChannel.open(lock, CREATE, WRITE); var ignored = channel.lock()) { return load(); }
    }
    /** Replay of the latest operation is harmless; older operations cannot overwrite newer state. */
    public synchronized Snapshot commit(long expected, UUID operation, byte[] payload) throws IOException {
        Objects.requireNonNull(operation); Objects.requireNonNull(payload);
        if (expected < 0 || payload.length > limit || operation.equals(new UUID(0,0))) throw new IllegalArgumentException("Invalid commit");
        byte[] copy = payload.clone();
        try (var channel = FileChannel.open(lock, CREATE, WRITE); var ignored = channel.lock()) {
            Snapshot old = load();
            if (old.operation().equals(operation)) {
                if (old.version() == expected + 1 && Arrays.equals(old.payload(), copy)) return old;
                throw new IllegalStateException("Operation identifier reused");
            }
            if (old.version() != expected) throw new ConcurrentModificationException("Stale snapshot");
            long next = Math.addExact(expected, 1);
            ByteBuffer data = ByteBuffer.allocate(HEADER + copy.length);
            data.putInt(MAGIC).putLong(next).putLong(operation.getMostSignificantBits()).putLong(operation.getLeastSignificantBits()).putInt(copy.length);
            byte[] prefix = Arrays.copyOf(data.array(), data.position());
            data.put(digest(prefix,copy)).put(copy).flip();
            Path tmp = Files.createTempFile(path.getParent(), ".gtm-", ".tmp");
            try {
                try (var output = FileChannel.open(tmp, WRITE, TRUNCATE_EXISTING)) {
                    while(data.hasRemaining()) output.write(data);
                    output.force(true);
                }
                // Fail closed on filesystems without atomic replacement; never truncate live data.
                Files.move(tmp, path, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            } finally { Files.deleteIfExists(tmp); }
            return new Snapshot(next, operation, copy);
        }
    }
    private Snapshot load() throws IOException {
        if (Files.notExists(path)) return new Snapshot(0, new UUID(0,0), new byte[0]);
        if (Files.isSymbolicLink(path)) throw new IOException("Snapshot symlink rejected");
        try (var input = new DataInputStream(new BufferedInputStream(Files.newInputStream(path)))) {
            byte[] prefix = input.readNBytes(HEADER-32);
            if (prefix.length != HEADER-32) throw new IOException("Truncated header");
            ByteBuffer h = ByteBuffer.wrap(prefix);
            int magic=h.getInt(); long version=h.getLong(); UUID op=new UUID(h.getLong(),h.getLong()); int size=h.getInt();
            if (magic!=MAGIC || version<1 || op.equals(new UUID(0,0)) || size<0 || size>limit) throw new IOException("Invalid header");
            byte[] checksum=input.readNBytes(32), payload=input.readNBytes(size);
            if (payload.length!=size || input.read()!=-1 || !MessageDigest.isEqual(checksum,digest(prefix,payload))) throw new IOException("Corrupt snapshot");
            return new Snapshot(version,op,payload);
        }
    }
    private static byte[] digest(byte[] header,byte[] payload) {
        try { MessageDigest d=MessageDigest.getInstance("SHA-256"); d.update(header); return d.digest(payload); }
        catch(NoSuchAlgorithmException e) { throw new AssertionError(e); }
    }
}
