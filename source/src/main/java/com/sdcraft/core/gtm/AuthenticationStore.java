package com.sdcraft.core.gtm;

import java.io.*;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.*;
import java.text.Normalizer;
import java.util.*;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

/**
 * Password credentials only; never changes player UUIDs, balances or inventory.
 * Expensive operations belong on the bounded authentication worker pool.
 *
 * References: OWASP Password Storage Cheat Sheet (PBKDF2-HMAC-SHA256: 600,000);
 * NIST SP 800-63B-4 section 3.1.1 (15-character single-factor minimum, NFC).
 */
public final class AuthenticationStore {
    public static final int ITERATIONS = 600_000;
    public static final int MIN_PASSWORD_LENGTH = 15;
    public static final int MAX_PASSWORD_LENGTH = 128;
    private static final int FORMAT = 1, MAX_ACCOUNTS = 10_000;
    private static final SecureRandom RANDOM = new SecureRandom();
    private static final Set<String> BLOCKLIST = Set.of(
        "passwordpassword", "passwordpassword1", "123456789012345", "1234567890123456",
        "12345678901234567890", "qwertyuiopasdfgh", "qwertyuiopasdfghjkl",
        "minecraftminecraft", "minecraft123456", "grandtheftmumbai", "indraprastha2026",
        "letmeinletmein123", "thisisapassword", "changemeplease123", "correcthorsebatterystaple"
    );
    private record Credential(UUID id, String name, UUID generation, int iterations, byte[] salt, byte[] hash) {}
    public record Proof(UUID player, UUID generation) {}
    private final SnapshotStore snapshots;
    private final Path file;
    private long revision;
    private volatile Map<UUID, Credential> credentials;

    public AuthenticationStore(Path folder) throws IOException {
        Path directory = folder.toAbsolutePath().normalize();
        if (Files.isSymbolicLink(directory)) throw new IOException("Authentication directory must not be a symlink");
        Files.createDirectories(directory);
        privatePermissions(directory, true);
        file = directory.resolve("credentials.snapshot");
        snapshots = new SnapshotStore(file, 4 * 1024 * 1024);
        var loaded = snapshots.read();
        revision = loaded.version();
        credentials = loaded.version() == 0 ? Map.of() : decode(loaded.payload());
        if (Files.exists(file)) privatePermissions(file, false);
    }

    public boolean registered(UUID id) { return credentials.containsKey(Objects.requireNonNull(id)); }
    public int size() { return credentials.size(); }
    public boolean nameAvailable(UUID id, String name) {
        String normalized = canonicalName(name);
        return credentials.values().stream().noneMatch(c -> !c.id().equals(id) && canonicalName(c.name()).equals(normalized));
    }
    public boolean current(Proof proof) {
        if (proof == null) return false;
        Credential c = credentials.get(proof.player());
        return c != null && c.generation().equals(proof.generation());
    }

    /** Returns a version-bound proof; a later password change invalidates it. */
    public Proof verify(UUID id, char[] password) {
        Credential credential = credentials.get(Objects.requireNonNull(id));
        char[] normalized = normalize(password);
        try {
            if (credential == null) {
                // Unknown accounts still pay the password-work cost after the rate limiter.
                byte[] dummy = derive(normalized, new byte[16], ITERATIONS);
                Arrays.fill(dummy, (byte) 0);
                return null;
            }
            byte[] candidate = derive(normalized, credential.salt(), credential.iterations());
            boolean equal = MessageDigest.isEqual(credential.hash(), candidate);
            Arrays.fill(candidate, (byte) 0);
            Proof proof = new Proof(id, credential.generation());
            return equal && current(proof) ? proof : null;
        } finally { Arrays.fill(normalized, '\0'); }
    }

    /** Refuses replacement and case-insensitive name collisions. */
    public Proof register(UUID id, String name, char[] password) throws IOException {
        Objects.requireNonNull(id);
        validatePassword(name, password);
        Credential next = create(id, name, password);
        synchronized (this) {
            if (credentials.containsKey(id)) throw new IllegalStateException("Account already has credentials");
            if (!nameAvailable(id, name)) throw new IllegalStateException("Name is already bound to another identity");
            if (credentials.size() >= MAX_ACCOUNTS) throw new IllegalStateException("Authentication account limit reached");
            commit(next);
        }
        return new Proof(id, next.generation());
    }

    public Proof changePassword(UUID id, char[] oldPassword, char[] newPassword) throws IOException {
        Proof proof = verify(id, oldPassword);
        if (proof == null) return null;
        Credential before = credentials.get(id);
        validatePassword(before.name(), newPassword);
        Credential next = create(id, before.name(), newPassword);
        synchronized (this) {
            if (!current(proof)) return null;
            commit(next);
        }
        return new Proof(id, next.generation());
    }

    /** Caller must hold a console-issued, connection-bound enrollment approval. */
    public Proof enrollAfterConsoleApproval(UUID id, String name, char[] password) throws IOException {
        Objects.requireNonNull(id);
        validatePassword(name, password);
        Credential next = create(id, name, password);
        synchronized (this) {
            if (!nameAvailable(id, name)) throw new IllegalStateException("Name is already bound to another identity");
            if (!registered(id) && credentials.size() >= MAX_ACCOUNTS)
                throw new IllegalStateException("Authentication account limit reached");
            commit(next);
        }
        return new Proof(id, next.generation());
    }

    private void commit(Credential credential) throws IOException {
        if (Thread.currentThread().isInterrupted()) throw new IllegalStateException("Authentication operation cancelled");
        Map<UUID, Credential> candidate = new HashMap<>(credentials);
        candidate.put(credential.id(), credential);
        byte[] bytes = encode(candidate);
        // Publish in-memory credentials only after the atomic disk commit succeeds.
        revision = snapshots.commit(revision, UUID.randomUUID(), bytes).version();
        credentials = Map.copyOf(candidate);
        privatePermissions(file, false);
    }

    private static Credential create(UUID id, String name, char[] password) {
        canonicalName(name);
        byte[] salt = new byte[16];
        RANDOM.nextBytes(salt);
        char[] normalized = normalize(password);
        try {
            return new Credential(id, name, UUID.randomUUID(), ITERATIONS, salt, derive(normalized, salt, ITERATIONS));
        } finally { Arrays.fill(normalized, '\0'); }
    }

    private static byte[] derive(char[] password, byte[] salt, int iterations) {
        PBEKeySpec spec = new PBEKeySpec(password, salt, iterations, 256);
        try { return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).getEncoded(); }
        catch (GeneralSecurityException e) { throw new IllegalStateException("Password hashing is unavailable", e); }
        finally { spec.clearPassword(); }
    }

    private static char[] normalize(char[] password) {
        Objects.requireNonNull(password);
        if (password.length > MAX_PASSWORD_LENGTH * 2) throw new IllegalArgumentException("Password is too long");
        String value = Normalizer.normalize(new String(password), Normalizer.Form.NFC);
        if (value.codePointCount(0, value.length()) > MAX_PASSWORD_LENGTH)
            throw new IllegalArgumentException("Password is too long");
        return value.toCharArray();
    }

    public static void validatePassword(String playerName, char[] password) {
        char[] normalized = normalize(password);
        try {
            String value = new String(normalized);
            int length = value.codePointCount(0, value.length());
            if (length < MIN_PASSWORD_LENGTH || length > MAX_PASSWORD_LENGTH)
                throw new IllegalArgumentException("Use a passphrase of 15–128 characters");
            if (value.codePoints().anyMatch(Character::isISOControl))
                throw new IllegalArgumentException("Control characters are not allowed in a passphrase");
            String folded = value.toLowerCase(Locale.ROOT);
            String name = canonicalName(playerName);
            if (BLOCKLIST.contains(folded) || folded.equals(name) || folded.equals(name + name)
                    || folded.equals(name + "123456789") || value.codePoints().distinct().count() == 1)
                throw new IllegalArgumentException("Choose a less predictable passphrase");
        } finally { Arrays.fill(normalized, '\0'); }
    }

    public static String canonicalName(String name) {
        Objects.requireNonNull(name);
        if (name.isBlank() || name.length() > 64 || name.codePoints().anyMatch(Character::isISOControl))
            throw new IllegalArgumentException("Invalid player name");
        return Normalizer.normalize(name, Normalizer.Form.NFC).toLowerCase(Locale.ROOT);
    }

    private static byte[] encode(Map<UUID, Credential> records) throws IOException {
        var bytes = new ByteArrayOutputStream();
        try (var out = new DataOutputStream(bytes)) {
            out.writeInt(FORMAT);
            out.writeInt(records.size());
            for (UUID id : records.keySet().stream().sorted().toList()) {
                Credential c = records.get(id);
                out.writeLong(id.getMostSignificantBits()); out.writeLong(id.getLeastSignificantBits());
                out.writeUTF(c.name());
                out.writeLong(c.generation().getMostSignificantBits()); out.writeLong(c.generation().getLeastSignificantBits());
                out.writeInt(c.iterations()); out.write(c.salt()); out.write(c.hash());
            }
        }
        return bytes.toByteArray();
    }

    private static Map<UUID, Credential> decode(byte[] payload) throws IOException {
        Map<UUID, Credential> records = new HashMap<>();
        Set<String> names = new HashSet<>();
        try (var in = new DataInputStream(new ByteArrayInputStream(payload))) {
            if (in.readInt() != FORMAT) throw new IOException("Unknown authentication schema");
            int count = in.readInt();
            if (count < 0 || count > MAX_ACCOUNTS) throw new IOException("Invalid authentication account count");
            for (int i = 0; i < count; i++) {
                UUID id = new UUID(in.readLong(), in.readLong());
                String name = in.readUTF();
                UUID generation = new UUID(in.readLong(), in.readLong());
                int iterations = in.readInt();
                byte[] salt = in.readNBytes(16), hash = in.readNBytes(32);
                if (iterations < ITERATIONS || iterations > 2_000_000 || salt.length != 16 || hash.length != 32
                        || generation.equals(new UUID(0, 0)) || !names.add(canonicalName(name))
                        || records.putIfAbsent(id, new Credential(id, name, generation, iterations, salt, hash)) != null)
                    throw new IOException("Invalid authentication record");
            }
            if (in.read() != -1) throw new IOException("Trailing authentication bytes");
        } catch (IllegalArgumentException e) { throw new IOException("Invalid authentication record", e); }
        return Map.copyOf(records);
    }

    private static void privatePermissions(Path path, boolean directory) throws IOException {
        if (Files.getFileStore(path).supportsFileAttributeView("posix"))
            Files.setPosixFilePermissions(path, PosixFilePermissions.fromString(directory ? "rwx------" : "rw-------"));
    }
}
