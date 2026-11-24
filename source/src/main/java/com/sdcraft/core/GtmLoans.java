package com.sdcraft.core;

import java.io.IOException;
import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.inventory.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.ItemMeta;

/** Opt-in banking menu. Economic changes are performed by the existing authoritative ledger. */
final class GtmLoans implements Listener {
    private final SDCraftCorePlugin plugin;
    private final Ledger ledger;
    private record Clock(UUID loan, int seconds) {}
    private final Map<UUID, Clock> clocks = new HashMap<>();
    private final Set<UUID> warned = new HashSet<>();
    private static final int RATE=800, DAYS=14, GRACE=2;
    private static final class Menu implements InventoryHolder {
        final UUID viewer, issueId=UUID.randomUUID();
        final Ledger.LoanAccount loan;
        Inventory inventory;
        boolean consumed;
        Menu(UUID viewer, Ledger.LoanAccount loan) { this.viewer=viewer; this.loan=loan; }
        @Override public Inventory getInventory() { return inventory; }
    }
    GtmLoans(SDCraftCorePlugin plugin,Ledger ledger) { this.plugin=plugin; this.ledger=ledger; }
    boolean available(Player p) {
        return plugin.isAuthenticated(p) && plugin.getConfig().getBoolean("gtm.experimental-loans",false)
                && p.hasPermission("gtm.loans") && ledger.exists(p.getUniqueId());
    }
    private String ark(long cents) { return String.format(Locale.ROOT,"%,.2f ARK",cents/100d); }
    void open(Player p) {
        if(!available(p)) { p.sendMessage("§cBanking loan service unavailable."); return; }
        try {
            var loan=ledger.loan(p.getUniqueId()).orElse(null);
            Menu holder=new Menu(p.getUniqueId(),loan);
            Inventory inv=Bukkit.createInventory(holder,27,"§8ARK National Bank | Loans"); holder.inventory=inv;
            inv.setItem(4,item(Material.GOLD_INGOT,"§6Bank balance",ark(ledger.bank(p.getUniqueId()))));
            if(loan==null||loan.terms().outstanding()==0) {
                inv.setItem(11,item(Material.PAPER,"§aBorrow 1,000 ARK","Total repayment: 1,080 ARK","14 active days; 2-day grace period","Click to accept these terms"));
                inv.setItem(15,item(Material.BOOK,"§aBorrow 3,000 ARK","Total repayment: 3,240 ARK","14 active days; 2-day grace period","Click to accept these terms"));
            } else {
                var t=loan.terms();
                inv.setItem(10,item(Material.BOOK,"§eLoan details","Outstanding: "+ark(t.outstanding()),"Due now: "+ark(t.due()),"Active days: "+t.elapsed()+"/"+t.days(),t.overdue()?"§cOVERDUE":"§aCurrent"));
                if(t.due()>0) inv.setItem(13,item(Material.GOLD_NUGGET,"§aPay due amount",ark(t.due())));
                inv.setItem(16,item(Material.EMERALD,"§aRepay in full",ark(t.outstanding())));
            }
            inv.setItem(22,item(Material.CLOCK,"§7Repayment clock","One loan day = 30 active minutes","No offline interest accrual","Interest capped at 8% of principal"));
            p.openInventory(inv);
        } catch(RuntimeException e) {
            plugin.getLogger().warning("Loan read failed for "+p.getUniqueId()+": "+e.getClass().getSimpleName());
            p.sendMessage("§cLoan record unavailable; contact an administrator.");
        }
    }
    private ItemStack item(Material type,String title,String... lore) {
        ItemStack i=new ItemStack(type); ItemMeta m=i.getItemMeta();
        if(m!=null){m.setDisplayName(title);m.setLore(List.of(lore));i.setItemMeta(m);}return i;
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void click(InventoryClickEvent e) {
        if(!(e.getView().getTopInventory().getHolder() instanceof Menu m)) return;
        e.setCancelled(true);
        if(!(e.getWhoClicked() instanceof Player p)||!p.getUniqueId().equals(m.viewer)||m.consumed||!available(p))return;
        if(e.getClick()!=ClickType.LEFT&&e.getClick()!=ClickType.RIGHT)return;
        int slot=e.getRawSlot();
        boolean issuing=m.loan==null||m.loan.terms().outstanding()==0;
        if(issuing ? slot!=11&&slot!=15 : slot!=13&&slot!=16)return;
        if(!issuing&&slot==13&&m.loan.terms().due()==0)return;
        m.consumed=true;
        Bukkit.getScheduler().runTask(plugin,()->{
            if(!p.isOnline()||!available(p))return;
            if(p.getOpenInventory().getTopInventory().getHolder()!=m)return;
            p.closeInventory();
            try {
                UUID id=p.getUniqueId(); boolean ok;
                if(issuing) {
                    long principal=slot==11?100000L:300000L;
                    ok=ledger.issueLoan(id,m.issueId,principal,RATE,DAYS,GRACE);
                    if(ok)clocks.remove(id);
                } else {
                    long amount=slot==13?m.loan.terms().due():m.loan.terms().outstanding();
                    ok=ledger.repayLoan(id,m.loan.id(),m.loan.terms().paid(),amount);
                    if(ok&&ledger.loan(id).orElseThrow().terms().outstanding()==0)clocks.remove(id);
                }
                p.sendMessage(ok?"§aBank transaction committed.":"§eLoan changed or insufficient bank balance. Review your account.");
            }catch(IOException|RuntimeException ex){
                plugin.getLogger().warning("Loan transaction failed for "+p.getUniqueId()+": "+ex.getClass().getSimpleName());
                p.sendMessage("§cBank transaction unavailable. Contact an administrator.");
            }
            open(p);
        });
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void drag(InventoryDragEvent e) {
        if(e.getView().getTopInventory().getHolder() instanceof Menu)e.setCancelled(true);
    }
    void tick(Player p,boolean active) {
        UUID id=p.getUniqueId();
        if(!active||!available(p))return;
        try {
            var loan=ledger.loan(id).orElse(null);
            if(loan==null||loan.terms().outstanding()==0||loan.terms().elapsed()>=loan.terms().days()+loan.terms().grace()) {clocks.remove(id);return;}
            Clock old=clocks.get(id);
            int seconds=old!=null&&old.loan().equals(loan.id())?Math.min(60,old.seconds()+1):1;
            clocks.put(id,new Clock(loan.id(),seconds));
            if(seconds>=60)flush(p);
        }catch(RuntimeException ex){if(warned.add(id))plugin.getLogger().warning("Loan clock unavailable for "+id);}
    }
    void flush(Player p) {
        UUID id=p.getUniqueId(); Clock c=clocks.get(id); if(c==null)return;
        try{
            var current=ledger.loan(id).orElse(null);
            if(current!=null&&current.id().equals(c.loan())&&current.terms().outstanding()>0
                    && ledger.advanceLoanClock(id,c.seconds()))p.sendMessage("§c[ARK Bank] Loan overdue. Review repayment options.");
            clocks.remove(id); warned.remove(id);
        }catch(IOException|RuntimeException e){if(warned.add(id))plugin.getLogger().warning("Loan clock write failed for "+id);}
    }
    void quit(Player p){flush(p);clocks.remove(p.getUniqueId());warned.remove(p.getUniqueId());}
    void close(){for(Player p:Bukkit.getOnlinePlayers())quit(p);clocks.clear();}
}
