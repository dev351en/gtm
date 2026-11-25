package com.sdcraft.core;

import java.nio.file.*;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import static org.junit.jupiter.api.Assertions.*;

class MedicalSettlementTest {
    @TempDir Path directory;
    @Test void aNewDeathCannotReuseAPendingEarlierReceipt() {
        UUID previous=UUID.randomUUID();
        assertEquals(previous,MedicalRecovery.deathIdentifier(previous.toString(),4,4));
        assertNotEquals(previous,MedicalRecovery.deathIdentifier(previous.toString(),4,5));
        assertNotEquals(previous,MedicalRecovery.deathIdentifier(previous.toString(),null,5));
    }
    @Test void walletAndBankDebitAndReceiptCommitTogether() throws Exception {
        var ledger=new Ledger(directory.toFile());var user=UUID.randomUUID();var death=UUID.randomUUID();ledger.register(user);
        assertTrue(ledger.settleMedicalOnce(user,death,75000));
        assertEquals(0,ledger.wallet(user));assertEquals(75000,ledger.bank(user));
        var reopened=new Ledger(directory.toFile());
        assertTrue(reopened.settleMedicalOnce(user,death,75000));assertEquals(75000,reopened.bank(user));
        assertThrows(IllegalStateException.class,()->reopened.settleMedicalOnce(user,death,5000));
        assertTrue(reopened.settleMedicalOnce(user,UUID.randomUUID(),7500));assertEquals(67500,reopened.bank(user));
    }
    @Test void insufficientFundsAreNotPartiallyChargedOrRetriedAfterTopup() throws Exception {
        var ledger=new Ledger(directory.toFile());var user=UUID.randomUUID();var death=UUID.randomUUID();ledger.register(user);
        assertFalse(ledger.settleMedicalOnce(user,death,150001));
        assertEquals(50000,ledger.wallet(user));assertEquals(100000,ledger.bank(user));
        ledger.creditWallet(user,50000,"test top-up");
        assertFalse(ledger.settleMedicalOnce(user,death,150001));assertEquals(100000,ledger.wallet(user));
    }
    @Test void failedSaveLeavesNoDebitOrReceipt() throws Exception {
        var ledger=new Ledger(directory.toFile());var user=UUID.randomUUID();var death=UUID.randomUUID();ledger.register(user);
        Path file=directory.resolve("accounts.yml"),backup=directory.resolve("accounts.previous");
        Files.move(file,backup);Files.createDirectory(file);
        assertThrows(java.io.IOException.class,()->ledger.settleMedicalOnce(user,death,75000));
        assertEquals(50000,ledger.wallet(user));assertEquals(100000,ledger.bank(user));
        Files.delete(file);Files.move(backup,file);
        assertTrue(ledger.settleMedicalOnce(user,death,75000));assertEquals(75000,ledger.bank(user));
    }
}
