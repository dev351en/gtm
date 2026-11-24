package com.sdcraft.core;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.bukkit.configuration.file.YamlConfiguration;
import java.nio.file.*;
import java.io.IOException;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;

final class GtmLedgerTest {
    @TempDir Path dir;

    @Test void loansAndBalancePersistTogether() throws Exception {
        UUID user=UUID.randomUUID(), id=UUID.randomUUID();
        Ledger l=new Ledger(dir.toFile()); assertTrue(l.register(user));
        assertEquals(100000,l.bank(user));
        assertTrue(l.issueLoan(user,id,100000,800,14,2));
        assertFalse(l.issueLoan(user,id,100000,800,14,2));
        assertFalse(l.issueLoan(user,UUID.randomUUID(),100000,800,14,2));
        assertEquals(200000,l.bank(user));
        assertEquals(108000,l.loan(user).orElseThrow().terms().outstanding());
        for(int i=0;i<30;i++)assertFalse(l.advanceLoanClock(user,60));
        assertEquals(1,l.loan(user).orElseThrow().terms().elapsed());
        long due=l.loan(user).orElseThrow().terms().due();
        assertTrue(l.repayLoan(user,id,0,due));
        assertFalse(l.repayLoan(user,id,0,due));
        assertFalse(l.repayLoan(user,UUID.randomUUID(),due,1));
        Ledger reopened=new Ledger(dir.toFile());
        assertEquals(200000-due,reopened.bank(user));
        assertEquals(due,reopened.loan(user).orElseThrow().terms().paid());
        assertEquals(1,reopened.loan(user).orElseThrow().terms().elapsed());
        assertTrue(reopened.repayLoan(user,id,due,108000-due));
        assertEquals(92000,reopened.bank(user));
        assertFalse(reopened.issueLoan(user,id,100000,800,14,2));
    }

    @Test void failedAtomicWriteRestoresInMemoryState() throws Exception {
        UUID user=UUID.randomUUID();
        Ledger l=new Ledger(dir.toFile()); l.register(user);
        Path file=dir.resolve("accounts.yml"), backup=dir.resolve("accounts-original.yml");
        Files.move(file,backup); Files.createDirectory(file); Files.writeString(file.resolve("blocker"),"occupied");
        assertThrows(IOException.class,()->l.issueLoan(user,UUID.randomUUID(),100000,800,14,2));
        assertEquals(100000,l.bank(user)); assertTrue(l.loan(user).isEmpty());
        assertThrows(IOException.class,()->l.deposit(user,1000));
        assertEquals(50000,l.wallet(user)); assertEquals(100000,l.bank(user));
        Files.delete(file.resolve("blocker")); Files.delete(file); Files.move(backup,file);
        assertTrue(l.deposit(user,1000));
        Ledger reopened=new Ledger(dir.toFile());
        assertEquals(49000,reopened.wallet(user)); assertEquals(101000,reopened.bank(user));
    }

    @Test void auditFailureDoesNotTurnCommittedPaymentIntoRetry() throws Exception {
        UUID user=UUID.randomUUID();
        Ledger l=new Ledger(dir.toFile()); l.register(user);
        Path csv=dir.resolve("transactions.csv"); Files.delete(csv); Files.createDirectory(csv);
        assertTrue(l.deposit(user,1000));
        assertEquals(49000,l.wallet(user)); assertEquals(101000,new Ledger(dir.toFile()).bank(user));
    }

    @Test void malformedLedgerFailsClosed() throws Exception {
        Path file=dir.resolve("accounts.yml");
        Files.writeString(file,"accounts: [broken\n");
        assertThrows(IllegalStateException.class,()->new Ledger(dir.toFile()));
        assertEquals("accounts: [broken\n",Files.readString(file));
    }

    @Test void overflowCannotPartiallyDebitSender() throws Exception {
        UUID user=UUID.randomUUID(), other=UUID.randomUUID();
        Ledger l=new Ledger(dir.toFile()); l.register(user); l.register(other);
        Path file=dir.resolve("accounts.yml");
        YamlConfiguration y=new YamlConfiguration(); y.load(file.toFile());
        y.set("accounts."+other+".bank",Long.MAX_VALUE); y.save(file.toFile());
        Ledger reopened=new Ledger(dir.toFile());
        assertThrows(ArithmeticException.class,()->reopened.transfer(user,other,1));
        assertEquals(100000,reopened.bank(user)); assertEquals(Long.MAX_VALUE,reopened.bank(other));
    }

    @Test void loanClockGraceAndInsufficientFunds() throws Exception {
        UUID user=UUID.randomUUID(), id=UUID.randomUUID();
        Ledger l=new Ledger(dir.toFile()); l.register(user);
        assertTrue(l.issueLoan(user,id,100000,800,14,2));
        assertTrue(l.chargeBank(user,200000,"test"));
        assertFalse(l.repayLoan(user,id,0,100));
        assertEquals(0,l.loan(user).orElseThrow().terms().paid());
        // One second before the grace boundary, no overdue state.
        for(int i=0;i<89;i++)assertFalse(l.advanceLoanClock(user,60));
        assertFalse(l.loan(user).orElseThrow().terms().overdue());
        assertTrue(l.advanceLoanClock(user,60));
        assertTrue(new Ledger(dir.toFile()).loan(user).orElseThrow().terms().overdue());
    }

    @Test void purchaseAndKeyLifecyclePersistAtomically() throws Exception {
        UUID owner=UUID.randomUUID(),guest=UUID.randomUUID(),property=UUID.randomUUID();
        Ledger l=new Ledger(dir.toFile());l.register(owner);l.register(guest);
        assertFalse(l.property(property).canEnter(owner,false));
        assertFalse(l.purchaseProperty(owner,property,100001));
        assertNull(l.property(property).owner());
        assertTrue(l.purchaseProperty(owner,property,75000));
        assertFalse(l.purchaseProperty(guest,property,75000));
        assertEquals(25000,l.bank(owner));assertEquals(100000,l.bank(guest));
        l.propertyGuest(owner,property,guest,true);
        UUID key=l.property(property).key();
        assertTrue(l.property(property).canEnter(guest,false));
        assertThrows(SecurityException.class,()->l.propertyLock(guest,property,key,true));
        assertTrue(l.propertyLock(owner,property,key,true));
        assertFalse(l.property(property).canEnter(guest,false));
        assertTrue(l.property(property).canEnter(owner,false));
        UUID replacement=l.propertyRekey(owner,property);
        assertNotEquals(key,replacement);
        assertThrows(SecurityException.class,()->l.propertyLock(owner,property,key,false));
        Ledger reopened=new Ledger(dir.toFile());
        assertEquals(owner,reopened.property(property).owner());
        assertEquals(replacement,reopened.property(property).key());
        assertEquals(25000,reopened.bank(owner));
        assertTrue(reopened.propertyLock(owner,property,replacement,false));
        assertFalse(reopened.property(property).canEnter(guest,false));
    }

    @Test void failedPurchaseDoesNotCreateOwnership() throws Exception {
        UUID owner=UUID.randomUUID(),property=UUID.randomUUID();
        Ledger l=new Ledger(dir.toFile());l.register(owner);
        Path file=dir.resolve("accounts.yml"), backup=dir.resolve("accounts-backup.yml");
        Files.move(file,backup); Files.createDirectory(file); Files.writeString(file.resolve("blocker"),"occupied");
        assertThrows(IOException.class,()->l.purchaseProperty(owner,property,75000));
        assertEquals(100000,l.bank(owner));assertNull(l.property(property).owner());
        Files.delete(file.resolve("blocker"));Files.delete(file);Files.move(backup,file);
        assertTrue(l.purchaseProperty(owner,property,75000));
        assertEquals(owner,new Ledger(dir.toFile()).property(property).owner());
    }
}
