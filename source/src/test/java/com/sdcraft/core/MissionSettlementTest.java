package com.sdcraft.core;

import java.io.IOException;
import java.nio.file.*;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import static org.junit.jupiter.api.Assertions.*;

final class MissionSettlementTest {
    @TempDir Path dir;

    @Test void completionReplayAfterRestartDoesNotPayTwice() throws Exception {
        UUID player=UUID.randomUUID(), run=UUID.randomUUID();Ledger ledger=new Ledger(dir.toFile());ledger.register(player);
        assertTrue(ledger.rewardCareerOnce(player,run,8500,2,"mission:delivery"));
        Ledger reopened=new Ledger(dir.toFile());
        assertFalse(reopened.rewardCareerOnce(player,run,8500,2,"mission:delivery"));
        assertEquals(108500,reopened.bank(player));assertEquals(2,reopened.credits(player));
        assertTrue(reopened.rewardCareerOnce(player,UUID.randomUUID(),8500,2,"mission:delivery"));
        assertEquals(117000,reopened.bank(player));assertEquals(4,reopened.credits(player));
    }

    @Test void receiptCannotBeReusedForDifferentReward() throws Exception {
        UUID player=UUID.randomUUID(),run=UUID.randomUUID();Ledger ledger=new Ledger(dir.toFile());ledger.register(player);
        ledger.rewardCareerOnce(player,run,5000,1,"mission:taxi");
        assertThrows(IllegalStateException.class,()->ledger.rewardCareerOnce(player,run,12000,3,"mission:bank"));
        assertEquals(105000,ledger.bank(player));assertEquals(1,ledger.credits(player));
    }

    @Test void failedPaymentCreatesNeitherRewardNorReceipt() throws Exception {
        UUID player=UUID.randomUUID(),run=UUID.randomUUID();Ledger ledger=new Ledger(dir.toFile());ledger.register(player);
        Path file=dir.resolve("accounts.yml"),backup=dir.resolve("original.yml");
        Files.move(file,backup);Files.createDirectory(file);Files.writeString(file.resolve("occupied"),"x");
        assertThrows(IOException.class,()->ledger.rewardCareerOnce(player,run,5000,1,"mission:taxi"));
        assertEquals(100000,ledger.bank(player));assertEquals(0,ledger.credits(player));
        Files.delete(file.resolve("occupied"));Files.delete(file);Files.move(backup,file);
        assertTrue(ledger.rewardCareerOnce(player,run,5000,1,"mission:taxi"));
        assertFalse(new Ledger(dir.toFile()).rewardCareerOnce(player,run,5000,1,"mission:taxi"));
    }
}
