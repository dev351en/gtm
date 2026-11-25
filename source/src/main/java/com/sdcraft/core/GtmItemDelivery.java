package com.sdcraft.core;

import java.io.IOException;
import java.util.*;
import org.bukkit.NamespacedKey;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.persistence.PersistentDataType;

/** Paid items remain queued until inventory space exists; reconnects reconcile saved player receipts. */
final class GtmItemDelivery {
    private final SDCraftCorePlugin plugin;
    private final Ledger ledger;
    private final NamespacedKey receiptsKey;
    GtmItemDelivery(SDCraftCorePlugin plugin,Ledger ledger){
        this.plugin=plugin;this.ledger=ledger;receiptsKey=new NamespacedKey(plugin,"item_delivery_receipts");
    }
    static String encode(ItemStack item){return Base64.getEncoder().encodeToString(item.serializeAsBytes());}
    boolean purchase(Player player,ItemStack item,long price,boolean bank,String description) throws IOException {
        if(!plugin.isAuthenticated(player))throw new IllegalStateException("Authenticate first");
        if(player.getInventory().firstEmpty()<0)throw new IllegalStateException("Free one inventory slot before purchasing");
        boolean paid=ledger.purchaseDelivery(player.getUniqueId(),UUID.randomUUID(),price,bank,description,encode(item));
        if(paid)retry(player);
        return paid;
    }
    void retry(Player player){
        if(!plugin.isAuthenticated(player)||!ledger.exists(player.getUniqueId()))return;
        try{
            List<Ledger.ItemDelivery> pending=ledger.pendingDeliveries(player.getUniqueId());
            if(pending.isEmpty())return;
            var data=player.getPersistentDataContainer();
            String stored=data.getOrDefault(receiptsKey,PersistentDataType.STRING,"");
            Set<String> receipts=new LinkedHashSet<>();
            if(!stored.isBlank())for(String id:stored.split("\\n")){UUID.fromString(id);receipts.add(id);}
            int delivered=0;
            for(var delivery:pending){
                String id=delivery.id().toString();
                if(receipts.contains(id)){
                    // A previous saveData call may have thrown after the in-memory receipt
                    // was added. Reattempt that checkpoint before closing the durable queue.
                    player.saveData();
                    ledger.acknowledgeDelivery(player.getUniqueId(),delivery.id());continue;
                }
                if(delivered>=8||receipts.size()>=4096)break;
                int slot=player.getInventory().firstEmpty();if(slot<0)break;
                ItemStack item=ItemStack.deserializeBytes(Base64.getDecoder().decode(delivery.payload()));
                if(item.getType().isAir()||item.getAmount()<1||item.getAmount()>item.getMaxStackSize())throw new IllegalStateException("Invalid queued item");
                player.getInventory().setItem(slot,item);
                receipts.add(id);data.set(receiptsKey,PersistentDataType.STRING,String.join("\n",receipts));
                // Inventory and receipt are part of the same vanilla player-data save. Leave
                // the financial outbox pending if saveData or acknowledgement reports failure.
                player.saveData();
                ledger.acknowledgeDelivery(player.getUniqueId(),delivery.id());
                delivered++;
            }
            if(delivered>0)player.sendMessage("§a"+delivered+" paid item delivery received.");
        }catch(IOException|RuntimeException ex){
            plugin.getLogger().warning("Item delivery awaits reconciliation for "+player.getUniqueId()+": "+ex.getClass().getSimpleName());
        }
    }
}
