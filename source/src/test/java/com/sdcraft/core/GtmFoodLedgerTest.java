package com.sdcraft.core;

import com.sdcraft.core.gtm.FoodCatalogue;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.nio.file.*;
import java.io.IOException;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;

final class GtmFoodLedgerTest {
    @TempDir Path dir;
    @Test void ordersDebitOnceAndPersistAcrossRestarts() throws Exception {
        UUID user=UUID.randomUUID(),id=UUID.randomUUID();
        Ledger l=new Ledger(dir.toFile());l.register(user);
        assertTrue(l.orderFood(user,id,"zomatoo","vada_pav","food_zomatoo",1000));
        assertEquals(98000,l.bank(user));
        assertFalse(l.orderFood(user,id,"zomatoo","vada_pav","food_zomatoo",1000));
        assertFalse(l.orderFood(user,UUID.randomUUID(),"swiffy","chai","food_swiffy",1000));
        Ledger reopened=new Ledger(dir.toFile());
        var t=reopened.foodOrder(user).orElseThrow();
        assertEquals(id,t.id());assertEquals(16000,t.readyAt());assertEquals(2000,t.price());
        assertFalse(reopened.collectFood(user,id,15999));
        assertFalse(reopened.collectFood(user,UUID.randomUUID(),16000));
        assertTrue(reopened.collectFood(user,id,16000));
        assertFalse(reopened.collectFood(user,id,16001));assertFalse(reopened.refundFood(user,id));
        Ledger after=new Ledger(dir.toFile());
        assertEquals(FoodCatalogue.Phase.COLLECTED,after.foodOrder(user).orElseThrow().phase());
        assertEquals(98000,after.bank(user));
    }
    @Test void cancellationIsAtomicAndOldOrderCannotReplay() throws Exception {
        UUID user=UUID.randomUUID(),id=UUID.randomUUID(),second=UUID.randomUUID();
        Ledger l=new Ledger(dir.toFile());l.register(user);
        assertTrue(l.orderFood(user,id,"swiffy","chai","food_swiffy",0));
        assertTrue(l.refundFood(user,id));assertFalse(l.refundFood(user,id));assertEquals(100000,l.bank(user));
        assertTrue(l.orderFood(user,second,"zomatoo","biryani","food_zomatoo",0));
        assertFalse(l.refundFood(user,id));assertTrue(l.refundFood(user,second));
        Ledger r=new Ledger(dir.toFile());
        assertFalse(r.orderFood(user,id,"swiffy","chai","food_swiffy",0));assertEquals(100000,r.bank(user));
    }
    @Test void failedPaymentAndRefundLeaveNoPartialState() throws Exception {
        UUID user=UUID.randomUUID(),id=UUID.randomUUID();
        Ledger l=new Ledger(dir.toFile());l.register(user);
        Path file=dir.resolve("accounts.yml"), backup=dir.resolve("backup.yml");
        Files.move(file,backup);Files.createDirectory(file);Files.writeString(file.resolve("blocker"),"occupied");
        assertThrows(IOException.class,()->l.orderFood(user,id,"swiffy","chai","food_swiffy",0));
        assertEquals(100000,l.bank(user));assertTrue(l.foodOrder(user).isEmpty());
        Files.delete(file.resolve("blocker"));Files.delete(file);Files.move(backup,file);
        assertTrue(l.orderFood(user,id,"swiffy","chai","food_swiffy",0));
        Files.move(file,backup);Files.createDirectory(file);Files.writeString(file.resolve("blocker"),"occupied");
        assertThrows(IOException.class,()->l.refundFood(user,id));
        assertEquals(99000,l.bank(user));assertTrue(l.foodOrder(user).orElseThrow().open());
    }
    @Test void invalidCatalogueAndInsufficientFundsFailClosed() throws Exception {
        UUID user=UUID.randomUUID();
        Ledger l=new Ledger(dir.toFile());l.register(user);
        assertThrows(IllegalArgumentException.class,()->l.orderFood(user,UUID.randomUUID(),"swiffy","unknown","food_swiffy",0));
        assertThrows(IllegalArgumentException.class,()->l.orderFood(user,UUID.randomUUID(),"unknown","chai","food_swiffy",0));
        assertTrue(l.chargeBank(user,100000,"test"));
        assertFalse(l.orderFood(user,UUID.randomUUID(),"swiffy","chai","food_swiffy",0));
        assertTrue(l.foodOrder(user).isEmpty());assertEquals(0,l.bank(user));
    }
}
