package com.sdcraft.core;

import com.sdcraft.core.gtm.Finish;
import java.nio.file.*;
import java.util.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import static org.junit.jupiter.api.Assertions.*;

class FinishLedgerTest {
    @TempDir Path folder;

    @Test void designsHaveDistinctStableIds() {
        Set<String> ids = new HashSet<>();
        for (String family : List.of("pistol","shotgun","smg","rifle"))
            for (int i=0; i<Finish.COUNT_PER_FAMILY; i++) assertTrue(ids.add(new Finish(family,i).id()));
        assertEquals(300,ids.size());
        assertThrows(IllegalArgumentException.class, () -> new Finish("rifle",75));
        assertThrows(IllegalArgumentException.class, () -> new Finish("other",0));
    }

    @Test void ownedDesignCanBeReappliedAfterRestartWithoutCharging() throws Exception {
        Ledger ledger = new Ledger(folder.toFile());
        UUID id = UUID.randomUUID();
        ledger.register(id);
        Finish f = new Finish("pistol", 0);
        assertTrue(ledger.acquireFinish(id,f));
        long remaining = 100000L - f.priceCents();
        ledger = new Ledger(folder.toFile());
        assertTrue(ledger.ownsFinish(id,f));
        assertTrue(ledger.acquireFinish(id,f));
        assertEquals(remaining,ledger.bank(id));
        assertTrue(ledger.chargeBank(id,remaining,"test"));
        assertFalse(ledger.acquireFinish(id,new Finish("pistol",1)));
        assertFalse(ledger.ownsFinish(id,new Finish("pistol",1)));
    }

    @Test void failedCommitRestoresBothBalanceAndEntitlement() throws Exception {
        Ledger ledger = new Ledger(folder.toFile());
        UUID id = UUID.randomUUID();
        ledger.register(id);
        Path file = folder.resolve("accounts.yml");
        Files.move(file,folder.resolve("copy.yml"));
        Files.createDirectory(file);
        Files.writeString(file.resolve("in-use"),"test");
        var finish = new Finish("smg",4);
        assertThrows(java.io.IOException.class, () -> ledger.acquireFinish(id,finish));
        assertFalse(ledger.ownsFinish(id,finish));
        assertEquals(100000,ledger.bank(id));
    }
}
