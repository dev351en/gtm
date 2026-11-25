package com.sdcraft.core.gtm;

import static org.junit.jupiter.api.Assertions.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.*;
import java.util.concurrent.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class AuthenticationStoreTest {
    @TempDir Path temporary;
    private static char[] pass() { return "Test-only Mumbai monsoon passphrase".toCharArray(); }
    private AuthenticationStore store() throws IOException { return new AuthenticationStore(temporary.resolve("auth")); }

    @Test void credentialsSurviveRestartWithoutPlaintextOrAccountMutation() throws Exception {
        Path legacy = temporary.resolve("accounts.yml");
        Files.writeString(legacy, "existing-bank-balance: 230050\n");
        byte[] legacyBefore = Files.readAllBytes(legacy);
        UUID id = UUID.randomUUID();
        AuthenticationStore first = store();
        var proof = first.register(id, "TestPlayer", pass());
        assertTrue(first.current(proof));
        assertTrue(first.registered(id));
        byte[] disk = Files.readAllBytes(temporary.resolve("auth/credentials.snapshot"));
        assertFalse(new String(disk, StandardCharsets.ISO_8859_1).contains(new String(pass())));
        AuthenticationStore restarted = store();
        assertNotNull(restarted.verify(id, pass()));
        assertNull(restarted.verify(id, "An incorrect but long password".toCharArray()));
        assertNull(restarted.verify(UUID.randomUUID(), pass()));
        assertArrayEquals(legacyBefore, Files.readAllBytes(legacy));
    }

    @Test void samePasswordHasIndependentSaltsAndHashes() throws Exception {
        AuthenticationStore store = store();
        store.register(UUID.randomUUID(), "FirstPlayer", pass());
        store.register(UUID.randomUUID(), "SecondPlayer", pass());
        byte[] payload = new SnapshotStore(temporary.resolve("auth/credentials.snapshot"), 4 * 1024 * 1024).read().payload();
        try (DataInputStream input = new DataInputStream(new ByteArrayInputStream(payload))) {
            assertEquals(1, input.readInt());
            assertEquals(2, input.readInt());
            List<byte[]> salts = new ArrayList<>(), hashes = new ArrayList<>();
            for (int i = 0; i < 2; i++) {
                input.readLong(); input.readLong(); input.readUTF(); input.readLong(); input.readLong();
                assertEquals(600_000, input.readInt());
                salts.add(input.readNBytes(16)); hashes.add(input.readNBytes(32));
            }
            assertFalse(Arrays.equals(salts.get(0), salts.get(1)));
            assertFalse(Arrays.equals(hashes.get(0), hashes.get(1)));
        }
    }

    @Test void passwordChangeRequiresOldSecretAndInvalidatesInFlightProof() throws Exception {
        UUID id = UUID.randomUUID();
        AuthenticationStore store = store();
        var old = store.register(id, "TestPlayer", pass());
        char[] replacement = "Another test-only passphrase for Mumbai".toCharArray();
        assertNull(store.changePassword(id, "An incorrect original passphrase".toCharArray(), replacement));
        assertTrue(store.current(old));
        var changed = store.changePassword(id, pass(), replacement);
        assertNotNull(changed);
        assertFalse(store.current(old));
        assertTrue(store.current(changed));
        assertNull(store.verify(id, pass()));
        assertNotNull(store().verify(id, replacement));
    }

    @Test void registrationDoesNotReplaceCredentialsOrStealCaseVariantName() throws Exception {
        AuthenticationStore store = store();
        UUID first = UUID.randomUUID(), second = UUID.randomUUID();
        store.register(first, "OwnerName", pass());
        assertThrows(IllegalStateException.class, () -> store.register(first, "OwnerName", pass()));
        assertFalse(store.nameAvailable(second, "ownername"));
        assertThrows(IllegalStateException.class, () -> store.register(second, "ownername", pass()));
        assertEquals(1, store().size());
        assertNotNull(store.verify(first, pass()));
    }

    @Test void unicodeNormalizationAllowsEquivalentPassphraseAndChecksCodePoints() throws Exception {
        AuthenticationStore store = store();
        UUID id = UUID.randomUUID();
        store.register(id, "TestPlayer", "Café and Mumbai at sunrise".toCharArray());
        assertNotNull(store.verify(id, "Cafe\u0301 and Mumbai at sunrise".toCharArray()));
        assertDoesNotThrow(() -> AuthenticationStore.validatePassword("TestPlayer", "अच्छी सुबह मुंबई में".toCharArray()));
        assertThrows(IllegalArgumentException.class, () -> AuthenticationStore.validatePassword("TestPlayer", "too short".toCharArray()));
        assertThrows(IllegalArgumentException.class, () -> AuthenticationStore.validatePassword("TestPlayer", "passwordpassword".toCharArray()));
        assertThrows(IllegalArgumentException.class, () -> AuthenticationStore.validatePassword("TestPlayer", ("x".repeat(127) + "yz").toCharArray()));
        assertThrows(IllegalArgumentException.class, () -> AuthenticationStore.validatePassword("TestPlayer", "A valid length\nbut newline".toCharArray()));
    }

    @Test void concurrentRegistrationHasOnlyOneWinner() throws Exception {
        AuthenticationStore store = store();
        UUID id = UUID.randomUUID();
        try (ExecutorService threads = Executors.newFixedThreadPool(2)) {
            Callable<Boolean> registration = () -> {
                try { store.register(id, "TestPlayer", pass()); return true; }
                catch (IllegalStateException expected) { return false; }
            };
            var results = threads.invokeAll(List.of(registration, registration));
            assertEquals(1, (results.get(0).get() ? 1 : 0) + (results.get(1).get() ? 1 : 0));
        }
        assertEquals(1, store().size());
    }

    @Test void staleWriterCannotReplaceNewerCredentialsAndDoesNotPublishFailedState() throws Exception {
        AuthenticationStore first = store(), stale = store();
        UUID firstId = UUID.randomUUID(), secondId = UUID.randomUUID();
        first.register(firstId, "FirstPlayer", pass());
        byte[] saved = Files.readAllBytes(temporary.resolve("auth/credentials.snapshot"));
        assertThrows(ConcurrentModificationException.class, () -> stale.register(secondId, "SecondPlayer", pass()));
        assertFalse(stale.registered(secondId));
        assertArrayEquals(saved, Files.readAllBytes(temporary.resolve("auth/credentials.snapshot")));
        assertEquals(1, store().size());
    }

    @Test void corruptedCredentialStoreFailsClosedInsteadOfCreatingNewAccounts() throws Exception {
        AuthenticationStore store = store();
        store.register(UUID.randomUUID(), "TestPlayer", pass());
        Path path = temporary.resolve("auth/credentials.snapshot");
        byte[] data = Files.readAllBytes(path);
        data[data.length - 1] ^= 1;
        Files.write(path, data);
        assertThrows(IOException.class, this::store);
        assertArrayEquals(data, Files.readAllBytes(path));
    }

    @Test void consoleRecoveryChangesCredentialButPreservesIdentity() throws Exception {
        AuthenticationStore store = store();
        UUID id = UUID.randomUUID();
        var previous = store.register(id, "TestPlayer", pass());
        char[] replacement = "Recovered test account in Mumbai".toCharArray();
        var recovered = store.enrollAfterConsoleApproval(id, "TestPlayer", replacement);
        assertEquals(id, recovered.player());
        assertFalse(store.current(previous));
        assertEquals(1, store().size());
        assertNotNull(store.verify(id, replacement));
    }

    @Test void credentialFilesHaveOwnerOnlyPermissionsWhenPosixAvailable() throws Exception {
        AuthenticationStore store = store();
        store.register(UUID.randomUUID(), "TestPlayer", pass());
        if (Files.getFileStore(temporary).supportsFileAttributeView("posix")) {
            assertEquals(PosixFilePermissions.fromString("rwx------"), Files.getPosixFilePermissions(temporary.resolve("auth")));
            assertEquals(PosixFilePermissions.fromString("rw-------"), Files.getPosixFilePermissions(temporary.resolve("auth/credentials.snapshot")));
        }
    }

    @Test void cancelledWorkerCannotCommitCredentialsAfterShutdown() throws Exception {
        AuthenticationStore store = store();
        Thread.currentThread().interrupt();
        try {
            assertThrows(IllegalStateException.class, () -> store.register(UUID.randomUUID(), "TestPlayer", pass()));
        } finally { Thread.interrupted(); }
        assertEquals(0, store.size());
        assertEquals(0, store().size());
    }
}
