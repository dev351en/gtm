package com.sdcraft.core;

import java.nio.file.*;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import static org.junit.jupiter.api.Assertions.*;

class ItemDeliveryTest {
    @TempDir Path directory;
    @Test void paymentAndQueueSurviveRestartAndRequestReplay() throws Exception {
        var ledger=new Ledger(directory.toFile());var user=UUID.randomUUID();var purchase=UUID.randomUUID();ledger.register(user);
        assertTrue(ledger.purchaseDelivery(user,purchase,25000,true,"equipment:PISTOL","AA=="));
        assertEquals(75000,ledger.bank(user));assertEquals(1,ledger.pendingDeliveries(user).size());
        var reopened=new Ledger(directory.toFile());
        assertTrue(reopened.purchaseDelivery(user,purchase,25000,true,"equipment:PISTOL","AA=="));
        assertEquals(75000,reopened.bank(user));assertEquals(1,reopened.pendingDeliveries(user).size());
        assertThrows(IllegalStateException.class,()->reopened.purchaseDelivery(user,purchase,1000,true,"different","AA=="));
        reopened.acknowledgeDelivery(user,purchase);reopened.acknowledgeDelivery(user,purchase);
        assertTrue(new Ledger(directory.toFile()).pendingDeliveries(user).isEmpty());
    }
    @Test void insufficientPaymentAndInvalidItemNeverCreateDebtOrQueue() throws Exception {
        var ledger=new Ledger(directory.toFile());var user=UUID.randomUUID();ledger.register(user);
        assertFalse(ledger.purchaseDelivery(user,UUID.randomUUID(),100001,true,"equipment:PISTOL","AA=="));
        assertThrows(IllegalArgumentException.class,()->ledger.purchaseDelivery(user,UUID.randomUUID(),5000,true,"equipment:PISTOL",""));
        assertEquals(100000,ledger.bank(user));assertTrue(ledger.pendingDeliveries(user).isEmpty());
    }
    @Test void failedSaveRollsBackChargeAndQueue() throws Exception {
        var ledger=new Ledger(directory.toFile());var user=UUID.randomUUID();var purchase=UUID.randomUUID();ledger.register(user);
        Path file=directory.resolve("accounts.yml"),backup=directory.resolve("accounts.previous");
        Files.move(file,backup);Files.createDirectory(file);
        assertThrows(java.io.IOException.class,()->ledger.purchaseDelivery(user,purchase,25000,true,"equipment:PISTOL","AA=="));
        assertEquals(100000,ledger.bank(user));assertTrue(ledger.pendingDeliveries(user).isEmpty());
        Files.delete(file);Files.move(backup,file);
        assertTrue(ledger.purchaseDelivery(user,purchase,25000,true,"equipment:PISTOL","AA=="));
    }
    @Test void foodCollectionAndDeliveryBecomeDurableTogether() throws Exception {
        var ledger=new Ledger(directory.toFile());var user=UUID.randomUUID();var order=UUID.randomUUID();ledger.register(user);
        assertTrue(ledger.orderFood(user,order,"zomatoo","chai","food_zomatoo",1000));
        assertFalse(ledger.collectFoodToDelivery(user,order,1001,"AA=="));assertTrue(ledger.pendingDeliveries(user).isEmpty());
        assertTrue(ledger.collectFoodToDelivery(user,order,16000,"AA=="));
        assertFalse(ledger.collectFoodToDelivery(user,order,16001,"AA=="));assertFalse(ledger.refundFood(user,order));
        var reopened=new Ledger(directory.toFile());assertEquals(1,reopened.pendingDeliveries(user).size());
        assertEquals(99000,reopened.bank(user));assertFalse(reopened.foodOrder(user).orElseThrow().open());
    }
}
