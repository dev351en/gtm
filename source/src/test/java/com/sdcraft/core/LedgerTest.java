package com.sdcraft.core;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Ledger Financial & Security Unit Tests")
class LedgerTest {

    @TempDir
    Path tempFolder;

    private Ledger ledger;
    private final UUID player1 = UUID.randomUUID();
    private final UUID player2 = UUID.randomUUID();

    @BeforeEach
    void setUp() {
        ledger = new Ledger(tempFolder.toFile());
    }

    @Test
    @DisplayName("Starter grant gives $500 wallet and $1000 bank exactly once (Idempotency)")
    void testStarterGrantIdempotency() throws Exception {
        // First registration succeeds
        assertTrue(ledger.register(player1));
        assertTrue(ledger.exists(player1));
        assertEquals(50_000L, ledger.wallet(player1)); // $500.00
        assertEquals(100_000L, ledger.bank(player1));   // $1000.00
        assertEquals("en", ledger.language(player1));

        // Second registration must return false (idempotent, does NOT duplicate funds)
        assertFalse(ledger.register(player1));
        assertEquals(50_000L, ledger.wallet(player1));
        assertEquals(100_000L, ledger.bank(player1));
    }

    @Test
    @DisplayName("Deposit transfers funds from wallet to bank atomically")
    void testDeposit() throws Exception {
        ledger.register(player1);

        // Deposit $200 (20,000 cents)
        assertTrue(ledger.deposit(player1, 20_000L));
        assertEquals(30_000L, ledger.wallet(player1)); // 500 - 200 = 300
        assertEquals(120_000L, ledger.bank(player1));  // 1000 + 200 = 1200

        // Attempt deposit greater than wallet balance -> must fail without changing balances
        assertFalse(ledger.deposit(player1, 40_000L));
        assertEquals(30_000L, ledger.wallet(player1));
        assertEquals(120_000L, ledger.bank(player1));

        // Invalid non-positive amount
        assertThrows(IllegalArgumentException.class, () -> ledger.deposit(player1, 0L));
        assertThrows(IllegalArgumentException.class, () -> ledger.deposit(player1, -500L));
    }

    @Test
    @DisplayName("Withdraw transfers funds from bank to wallet atomically")
    void testWithdraw() throws Exception {
        ledger.register(player1);

        // Withdraw $300 (30,000 cents)
        assertTrue(ledger.withdraw(player1, 30_000L));
        assertEquals(80_000L, ledger.wallet(player1)); // 500 + 300 = 800
        assertEquals(70_000L, ledger.bank(player1));   // 1000 - 300 = 700

        // Overdraft attempt -> must fail without balance change
        assertFalse(ledger.withdraw(player1, 80_000L));
        assertEquals(80_000L, ledger.wallet(player1));
        assertEquals(70_000L, ledger.bank(player1));

        assertThrows(IllegalArgumentException.class, () -> ledger.withdraw(player1, -100L));
    }

    @Test
    @DisplayName("Transfer sends bank funds between two registered players")
    void testTransfer() throws Exception {
        ledger.register(player1);
        ledger.register(player2);

        // Transfer $250 from player1 to player2
        assertTrue(ledger.transfer(player1, player2, 25_000L));
        assertEquals(75_000L, ledger.bank(player1));  // 1000 - 250 = 750
        assertEquals(125_000L, ledger.bank(player2)); // 1000 + 250 = 1250

        // Self-transfer prohibited
        assertFalse(ledger.transfer(player1, player1, 10_000L));

        // Transfer exceeding balance prohibited
        assertFalse(ledger.transfer(player1, player2, 100_000L));
    }

    @Test
    @DisplayName("Charge wallet and charge bank deduct funds properly")
    void testCharges() throws Exception {
        ledger.register(player1);

        // Charge wallet $25 (medical diagnosis)
        assertTrue(ledger.chargeWallet(player1, 2500L, "medical diagnosis"));
        assertEquals(47_500L, ledger.wallet(player1));

        // Charge bank $15 (bus ride)
        assertTrue(ledger.chargeBank(player1, 1500L, "bus fare"));
        assertEquals(98_500L, ledger.bank(player1));

        // Charge beyond balance fails
        assertFalse(ledger.chargeWallet(player1, 50_000L, "luxury item"));
        assertEquals(47_500L, ledger.wallet(player1));
    }

    @Test
    @DisplayName("External Vault wallet credit and debit use the same persisted cash balance")
    void testVaultWalletLedgerPath() throws Exception {
        ledger.register(player1);
        ledger.creditWallet(player1, 1_250L, "Vault deposit");
        assertEquals(51_250L, ledger.wallet(player1));
        assertTrue(ledger.chargeWallet(player1, 725L, "Vault withdrawal"));
        assertEquals(50_525L, new Ledger(tempFolder.toFile()).wallet(player1));
        assertEquals(100_000L, ledger.bank(player1));
        assertThrows(IllegalArgumentException.class, () -> ledger.creditWallet(player1, 0, "invalid"));
    }

    @Test
    @DisplayName("PIN security: PBKDF2WithHmacSHA256 hashing, salt generation, constant-time verification")
    void testPinSecurity() throws Exception {
        ledger.register(player1);

        assertFalse(ledger.hasPin(player1));
        assertFalse(ledger.verifyPin(player1, "1234"));

        // Invalid PIN formats (must be 4-8 digits)
        assertThrows(IllegalArgumentException.class, () -> ledger.pin(player1, "123"));       // Too short
        assertThrows(IllegalArgumentException.class, () -> ledger.pin(player1, "123456789")); // Too long
        assertThrows(IllegalArgumentException.class, () -> ledger.pin(player1, "abcd"));      // Non-digits

        // Valid PIN
        ledger.pin(player1, "4829");
        assertTrue(ledger.hasPin(player1));

        // Correct verification
        assertTrue(ledger.verifyPin(player1, "4829"));

        // Incorrect PIN rejected
        assertFalse(ledger.verifyPin(player1, "4820"));
        assertFalse(ledger.verifyPin(player1, "0000"));
        assertFalse(ledger.verifyPin(player1, ""));
    }

    @Test
    @DisplayName("Duty salary credits active duty earnings and career points")
    void testDutyGrant() throws Exception {
        ledger.register(player1);

        // Grant 10 minutes of duty pay: $120.00 (12000 cents), 600,000 ms, 1 career credit
        ledger.grantDuty(player1, 12_000L, 600_000L, 1, "police patrol");
        assertEquals(112_000L, ledger.bank(player1));
        assertEquals(600_000L, ledger.dutyMs(player1));
        assertEquals(1, ledger.credits(player1));

        // Invalid credits (> 3)
        assertThrows(IllegalArgumentException.class, () -> ledger.grantDuty(player1, 1000L, 1000L, 5, "invalid"));
    }

    @Test
    @DisplayName("Rank requires credits, verified duty time, and explicit admin approval")
    void testPromotionRequiresHumanApproval() throws Exception {
        ledger.register(player1);
        for (int i = 0; i < 5; i++) ledger.rewardCareer(player1, 100L, 2, "verified mission");
        assertEquals(10, ledger.credits(player1));
        assertEquals(1, ledger.rank(player1));
        assertFalse(ledger.eligibleForPromotion(player1));
        assertFalse(ledger.approvePromotion(player1, "admin"));

        ledger.grantDuty(player1, 0, 3_600_000L, 0, "verified duty");
        assertTrue(ledger.eligibleForPromotion(player1));
        assertEquals(1, ledger.rank(player1));
        assertTrue(ledger.approvePromotion(player1, "admin"));
        assertEquals(2, new Ledger(tempFolder.toFile()).rank(player1));
        assertFalse(ledger.approvePromotion(player1, "admin"));

        assertEquals(25, Ledger.requiredCreditsForRank(3));
        assertEquals(10_800_000L, Ledger.requiredDutyMsForRank(3));
        assertThrows(IllegalArgumentException.class, () -> ledger.approvePromotion(player1, ""));
    }

    @Test
    @DisplayName("Language preference switching")
    void testLanguage() throws Exception {
        ledger.register(player1);
        assertEquals("en", ledger.language(player1));

        ledger.language(player1, "hi");
        assertEquals("hi", ledger.language(player1));

        assertThrows(IllegalArgumentException.class, () -> ledger.language(player1, "fr"));
    }

    @Test
    @DisplayName("Transactions log file is created and appended")
    void testTransactionLog() throws Exception {
        ledger.register(player1);
        ledger.deposit(player1, 10_000L);

        File logFile = new File(tempFolder.toFile(), "transactions.csv");
        assertTrue(logFile.exists());
        assertTrue(logFile.length() > 0);
    }
}
