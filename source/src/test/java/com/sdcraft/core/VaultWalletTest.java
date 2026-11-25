package com.sdcraft.core;

import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import net.milkbowl.vault.economy.EconomyResponse;
import org.bukkit.OfflinePlayer;
import org.bukkit.entity.Player;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import static org.junit.jupiter.api.Assertions.*;

class VaultWalletTest {
    @TempDir Path folder;

    @Test
    void vaultTransactionsUseTheCityWalletWithCentPrecision() throws Exception {
        UUID id = UUID.randomUUID();
        Ledger ledger = new Ledger(folder.toFile());
        ledger.register(id);
        OfflinePlayer player = (OfflinePlayer) Proxy.newProxyInstance(
                OfflinePlayer.class.getClassLoader(), new Class<?>[] { OfflinePlayer.class },
                (proxy, method, args) -> switch (method.getName()) {
                    case "getUniqueId" -> id;
                    case "isOnline" -> false;
                    default -> null;
                });
        VaultWallet vault = new VaultWallet(ledger, authenticated -> true);

        assertEquals(500.00, vault.getBalance(player));
        assertEquals(500.00, vault.getBalance(player, "world"));
        EconomyResponse credit = vault.depositPlayer(player, 12.34);
        assertTrue(credit.transactionSuccess());
        assertEquals(512.34, credit.balance);
        assertEquals(51_234L, ledger.wallet(id));

        EconomyResponse debit = vault.withdrawPlayer(player, 2.34);
        assertTrue(debit.transactionSuccess());
        assertEquals(510.00, debit.balance);
        assertEquals(51_000L, ledger.wallet(id));
        assertTrue(vault.has(player, "world", 510.00));
        assertEquals(100_000L, ledger.bank(id));

        assertFalse(vault.withdrawPlayer(player, 999).transactionSuccess());
        assertFalse(vault.depositPlayer(player, 0.001).transactionSuccess());
        assertFalse(vault.depositPlayer(player, Double.NaN).transactionSuccess());
        assertEquals(51_000L, ledger.wallet(id));
    }

    @Test
    void anOnlineSessionMustAuthenticateBeforeAnyWalletMutation() throws Exception {
        UUID id = UUID.randomUUID();
        Ledger ledger = new Ledger(folder.toFile());
        ledger.register(id);
        Player player = (Player) Proxy.newProxyInstance(Player.class.getClassLoader(),
                new Class<?>[] { Player.class }, (proxy, method, args) -> switch (method.getName()) {
                    case "getUniqueId" -> id;
                    case "isOnline" -> true;
                    case "getPlayer" -> proxy;
                    default -> null;
                });
        AtomicBoolean authenticated = new AtomicBoolean(false);
        VaultWallet vault = new VaultWallet(ledger, session -> session == player && authenticated.get());

        assertFalse(vault.depositPlayer(player, 20).transactionSuccess());
        assertFalse(vault.withdrawPlayer(player, "world", 20).transactionSuccess());
        assertEquals(50_000L, ledger.wallet(id));
        authenticated.set(true);
        assertTrue(vault.depositPlayer(player, 20).transactionSuccess());
        assertEquals(52_000L, ledger.wallet(id));
        authenticated.set(false);
        assertFalse(vault.withdrawPlayer(player, 20).transactionSuccess());
        assertEquals(52_000L, new Ledger(folder.toFile()).wallet(id));
    }

    @Test
    void externalPluginsCannotReserveUnregisteredOfflineIdentities() throws Exception {
        UUID id = UUID.randomUUID();
        Ledger ledger = new Ledger(folder.toFile());
        OfflinePlayer player = (OfflinePlayer) Proxy.newProxyInstance(
                OfflinePlayer.class.getClassLoader(), new Class<?>[] { OfflinePlayer.class },
                (proxy, method, args) -> method.getName().equals("getUniqueId") ? id : null);
        VaultWallet vault = new VaultWallet(ledger, authenticated -> false);
        assertFalse(vault.createPlayerAccount(player));
        assertFalse(ledger.exists(id));
        assertFalse(vault.depositPlayer(player, 500).transactionSuccess());
        assertFalse(ledger.exists(id));
    }
}
