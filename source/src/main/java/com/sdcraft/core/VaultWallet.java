package com.sdcraft.core;

import java.io.IOException;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import net.milkbowl.vault.economy.AbstractEconomy;
import net.milkbowl.vault.economy.EconomyResponse;
import net.milkbowl.vault.economy.EconomyResponse.ResponseType;
import org.bukkit.Bukkit;
import org.bukkit.OfflinePlayer;

/** Exposes the SD Craft cash wallet to Vault. The city bank stays private to SD Craft. */
final class VaultWallet extends AbstractEconomy {
    private final Ledger ledger;

    VaultWallet(Ledger ledger) { this.ledger = ledger; }

    @Override public boolean isEnabled() { return true; }
    @Override public String getName() { return "SDCraft Wallet"; }
    @Override public boolean hasBankSupport() { return false; }
    @Override public int fractionalDigits() { return 2; }
    @Override public String format(double amount) { return String.format(Locale.US, "$%,.2f", amount); }
    @Override public String currencyNamePlural() { return "dollars"; }
    @Override public String currencyNameSingular() { return "dollar"; }

    private OfflinePlayer player(String name) { return Bukkit.getOfflinePlayer(name); }
    private long balance(UUID id) { return ledger.exists(id) ? ledger.wallet(id) : 0; }
    private static long cents(double amount) {
        if (!Double.isFinite(amount) || amount < 0 || amount > 1_000_000_000D)
            throw new IllegalArgumentException("Invalid amount");
        double scaled = amount * 100D;
        if (Math.abs(scaled - Math.rint(scaled)) > 0.000001D)
            throw new IllegalArgumentException("Only cent precision is supported");
        return Math.round(scaled);
    }
    private EconomyResponse response(double amount, long balance, ResponseType type, String error) {
        return new EconomyResponse(amount, balance / 100D, type, error);
    }
    private EconomyResponse failure(UUID id, String reason) {
        return response(0, balance(id), ResponseType.FAILURE, reason);
    }
    private EconomyResponse transact(OfflinePlayer player, double amount, boolean credit) {
        UUID id = player.getUniqueId();
        if (!ledger.exists(id)) return failure(id, "Player has no SD Craft account");
        try {
            long value = cents(amount);
            if (value == 0) return response(0, balance(id), ResponseType.SUCCESS, "");
            if (credit) ledger.creditWallet(id, value, "Vault deposit");
            else if (!ledger.chargeWallet(id, value, "Vault withdrawal"))
                return failure(id, "Insufficient wallet funds");
            return response(amount, balance(id), ResponseType.SUCCESS, "");
        } catch (IllegalArgumentException | ArithmeticException e) {
            return failure(id, e.getMessage());
        } catch (IOException | IllegalStateException e) {
            return failure(id, "Wallet transaction failed: " + e.getMessage());
        }
    }
    private EconomyResponse noBank() {
        return response(0, 0, ResponseType.NOT_IMPLEMENTED, "SD Craft shared banks are unsupported");
    }

    @Override public boolean hasAccount(String name) { return hasAccount(player(name)); }
    @Override public boolean hasAccount(String name, String world) { return hasAccount(name); }
    @Override public boolean hasAccount(OfflinePlayer player) { return ledger.exists(player.getUniqueId()); }
    @Override public boolean hasAccount(OfflinePlayer player, String world) { return hasAccount(player); }
    @Override public double getBalance(String name) { return getBalance(player(name)); }
    @Override public double getBalance(String name, String world) { return getBalance(name); }
    @Override public double getBalance(OfflinePlayer player) { return balance(player.getUniqueId()) / 100D; }
    @Override public double getBalance(OfflinePlayer player, String world) { return getBalance(player); }
    @Override public boolean has(String name, double amount) { return has(player(name), amount); }
    @Override public boolean has(String name, String world, double amount) { return has(name, amount); }
    @Override public boolean has(OfflinePlayer player, double amount) {
        try { return hasAccount(player) && balance(player.getUniqueId()) >= cents(amount); }
        catch (IllegalArgumentException e) { return false; }
    }
    @Override public boolean has(OfflinePlayer player, String world, double amount) { return has(player, amount); }
    @Override public EconomyResponse withdrawPlayer(String name, double amount) { return withdrawPlayer(player(name), amount); }
    @Override public EconomyResponse withdrawPlayer(String name, String world, double amount) { return withdrawPlayer(name, amount); }
    @Override public EconomyResponse withdrawPlayer(OfflinePlayer player, double amount) { return transact(player, amount, false); }
    @Override public EconomyResponse withdrawPlayer(OfflinePlayer player, String world, double amount) {
        return withdrawPlayer(player, amount);
    }
    @Override public EconomyResponse depositPlayer(String name, double amount) { return depositPlayer(player(name), amount); }
    @Override public EconomyResponse depositPlayer(String name, String world, double amount) { return depositPlayer(name, amount); }
    @Override public EconomyResponse depositPlayer(OfflinePlayer player, double amount) { return transact(player, amount, true); }
    @Override public EconomyResponse depositPlayer(OfflinePlayer player, String world, double amount) {
        return depositPlayer(player, amount);
    }
    @Override public boolean createPlayerAccount(String name) { return createPlayerAccount(player(name)); }
    @Override public boolean createPlayerAccount(String name, String world) { return createPlayerAccount(name); }
    @Override public boolean createPlayerAccount(OfflinePlayer player) {
        try { return ledger.register(player.getUniqueId()); }
        catch (IOException | IllegalStateException e) { return false; }
    }
    @Override public boolean createPlayerAccount(OfflinePlayer player, String world) {
        return createPlayerAccount(player);
    }
    @Override public EconomyResponse createBank(String name, String owner) { return noBank(); }
    @Override public EconomyResponse deleteBank(String name) { return noBank(); }
    @Override public EconomyResponse bankBalance(String name) { return noBank(); }
    @Override public EconomyResponse bankHas(String name, double amount) { return noBank(); }
    @Override public EconomyResponse bankWithdraw(String name, double amount) { return noBank(); }
    @Override public EconomyResponse bankDeposit(String name, double amount) { return noBank(); }
    @Override public EconomyResponse isBankOwner(String name, String owner) { return noBank(); }
    @Override public EconomyResponse isBankMember(String name, String member) { return noBank(); }
    @Override public List<String> getBanks() { return List.of(); }
}
