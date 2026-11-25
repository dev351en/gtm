package com.sdcraft.core;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import java.util.UUID;

class GtmWeaponUpgradeTest {
    private static class Port implements GtmWeaponUpgrade.GrantPort {
        boolean received, item, diskReceived, diskItem, fail;
        int free = 4, saves;
        public boolean received() { return received; }
        public int emptySlot() { return free; }
        public void putItem(int slot) { assertEquals(free, slot); item = true; }
        public void clearItem(int slot) { item = false; }
        public void markReceived(boolean value) { received = value; }
        public void save() {
            saves++;
            if (fail) throw new IllegalStateException("simulated player-data failure");
            diskReceived = received; diskItem = item;
        }
    }

    @Test void savesOneLoadedItemAndReceiptTogetherAndDoesNotDuplicateAfterRestart() {
        Port first = new Port();
        assertEquals(GtmWeaponUpgrade.Result.DELIVERED, GtmWeaponUpgrade.deliver(first));
        assertTrue(first.diskReceived); assertTrue(first.diskItem); assertEquals(1, first.saves);
        Port afterRestart = new Port();
        afterRestart.received = first.diskReceived;
        afterRestart.item = first.diskItem;
        assertEquals(GtmWeaponUpgrade.Result.ALREADY_RECEIVED, GtmWeaponUpgrade.deliver(afterRestart));
        assertEquals(0, afterRestart.saves);
    }

    @Test void fullInventoryDefersWithoutRecordingOrDroppingAndRetriesAfterAFreeSlot() {
        Port port = new Port(); port.free = -1;
        assertEquals(GtmWeaponUpgrade.Result.INVENTORY_FULL, GtmWeaponUpgrade.deliver(port));
        assertFalse(port.item); assertFalse(port.received); assertEquals(0, port.saves);
        port.free = 7;
        assertEquals(GtmWeaponUpgrade.Result.DELIVERED, GtmWeaponUpgrade.deliver(port));
    }

    @Test void failedPersistenceRollsBackBothInMemoryChangesAndAllowsRetry() {
        Port port = new Port(); port.fail = true;
        assertThrows(IllegalStateException.class, () -> GtmWeaponUpgrade.deliver(port));
        assertFalse(port.item); assertFalse(port.received);
        assertFalse(port.diskItem); assertFalse(port.diskReceived);
        port.fail = false;
        assertEquals(GtmWeaponUpgrade.Result.DELIVERED, GtmWeaponUpgrade.deliver(port));
        assertTrue(port.diskItem); assertTrue(port.diskReceived);
    }

    @Test void discardingTheGrantedItemDoesNotCreateAnotherEntitlement() {
        Port port = new Port(); GtmWeaponUpgrade.deliver(port);
        port.item = false;
        assertEquals(GtmWeaponUpgrade.Result.ALREADY_RECEIVED, GtmWeaponUpgrade.deliver(port));
        assertFalse(port.item);
    }

    @Test void identityIsStablePerPlayerAndDistinctAcrossAccounts() {
        UUID player = UUID.randomUUID();
        assertEquals(GtmWeaponUpgrade.serial(player), GtmWeaponUpgrade.serial(player));
        assertNotEquals(GtmWeaponUpgrade.serial(player), GtmWeaponUpgrade.serial(UUID.randomUUID()));
    }
}
