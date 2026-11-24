package com.sdcraft.core;

import java.io.IOException;
import java.util.*;
import org.bukkit.*;
import org.bukkit.enchantments.Enchantment;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.entity.PlayerDeathEvent;
import org.bukkit.event.player.PlayerRespawnEvent;
import org.bukkit.inventory.ItemStack;
import org.bukkit.persistence.PersistentDataType;

/** Hospital death policy. Financial settlement is replay-safe; vanilla owns inventory persistence. */
final class MedicalRecovery implements Listener {
    private final SDCraftCorePlugin plugin;
    private final Ledger ledger;
    private final NamespacedKey deathKey;
    private final NamespacedKey deathCounterKey,arrivalKey;
    private final long fee;
    private static final Set<Material> HAZARDS=Set.of(Material.FIRE,Material.SOUL_FIRE,Material.LAVA,
            Material.CACTUS,Material.SWEET_BERRY_BUSH,Material.WITHER_ROSE,Material.POWDER_SNOW);

    MedicalRecovery(SDCraftCorePlugin plugin,Ledger ledger) {
        this.plugin=plugin;this.ledger=ledger;deathKey=new NamespacedKey(plugin,"medical_death");
        deathCounterKey=new NamespacedKey(plugin,"medical_death_counter");arrivalKey=new NamespacedKey(plugin,"medical_arrival_pending");
        fee=plugin.getConfig().getLong("medical.recovery-fee-cents",7500L);
        if(fee<0||fee>100000000000L)throw new IllegalArgumentException("Invalid medical recovery fee");
    }

    private Location hospital() {
        Location configured=plugin.site("hospital");
        if(configured==null||configured.getWorld()==null)return null;
        World world=configured.getWorld();
        if(configured.getBlockY()<=world.getMinHeight()||configured.getBlockY()+1>=world.getMaxHeight()
                ||!world.getWorldBorder().isInside(configured))return null;
        // Never excavate, build a platform, or substitute guessed facility coordinates.
        if(!configured.getBlock().isPassable()||!configured.clone().add(0,1,0).getBlock().isPassable()
                ||HAZARDS.contains(configured.getBlock().getType())||HAZARDS.contains(configured.clone().add(0,1,0).getBlock().getType()))return null;
        Material floor=configured.clone().subtract(0,1,0).getBlock().getType();
        return floor.isSolid()&&!HAZARDS.contains(floor)&&floor!=Material.MAGMA_BLOCK&&floor!=Material.CAMPFIRE&&floor!=Material.SOUL_CAMPFIRE
                ?configured.clone().add(.0,.05,.0):null;
    }

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void death(PlayerDeathEvent event) {
        Player player=event.getEntity();
        if(!plugin.isAuthenticated(player)||plugin.isManagedNpc(player)||!ledger.exists(player.getUniqueId()))return;
        var data=player.getPersistentDataContainer();
        String existing=data.get(deathKey,PersistentDataType.STRING);
        UUID death;
        int counter=player.getStatistic(Statistic.DEATHS);
        try{death=deathIdentifier(existing,data.get(deathCounterKey,PersistentDataType.INTEGER),counter);}
        catch(IllegalArgumentException corrupt){
            preserve(event);
            plugin.getLogger().severe("Invalid death receipt for "+player.getUniqueId()+"; no medical charge applied.");
            return;
        }
        data.set(deathKey,PersistentDataType.STRING,death.toString());
        data.set(deathCounterKey,PersistentDataType.INTEGER,counter);
        data.set(arrivalKey,PersistentDataType.BYTE,(byte)1);
        // Save the receipt token before asking the ledger to settle. No inventory restoration
        // from a second database is attempted: that would introduce duplicate item grants.
        try{player.saveData();}
        catch(RuntimeException ex){
            preserve(event);
            plugin.getLogger().severe("Player death checkpoint failed for "+player.getUniqueId()+"; inventory preserved and no medical charge applied.");
            return;
        }
        boolean insured=true;
        Location hospital=hospital();
        if(hospital==null){
            plugin.getLogger().warning("Hospital has no safe commissioned arrival; medical fee waived for "+player.getUniqueId());
        }else{
            try{insured=ledger.settleMedicalOnce(player.getUniqueId(),death,fee);}
            catch(IOException|RuntimeException ex){
                plugin.getLogger().severe("Medical settlement unavailable for "+player.getUniqueId()+"; items preserved, no retry debit: "+ex.getClass().getSimpleName());
            }
        }
        if(insured)preserve(event);
        else{
            event.setKeepInventory(false);event.setKeepLevel(false);
            // Explicitly apply the uninsured policy even when a world has keepInventory enabled.
            event.getDrops().clear();
            for(ItemStack item:player.getInventory().getContents())
                if(item!=null&&!item.getType().isAir()&&!item.containsEnchantment(Enchantment.VANISHING_CURSE))event.getDrops().add(item.clone());
        }
        player.sendTitle("§c§lWASTED",hospital==null?"§7Recovery point unavailable":insured?"§fHospital recovery • inventory secured":"§7Hospital recovery • belongings remain at the scene",5,60,20);
    }

    private static void preserve(PlayerDeathEvent event){
        event.setKeepInventory(true);event.getDrops().clear();
        event.setKeepLevel(true);event.setDroppedExp(0);
    }

    @EventHandler(priority=EventPriority.HIGHEST)
    public void respawn(PlayerRespawnEvent event){
        Player player=event.getPlayer();
        if(!plugin.isAuthenticated(player)||plugin.isManagedNpc(player))return;
        String token=player.getPersistentDataContainer().get(deathKey,PersistentDataType.STRING);
        if(token==null)return; // End portal transitions and ordinary joins are not deaths.
        Location target=hospital();
        if(target!=null)event.setRespawnLocation(target);
        Bukkit.getScheduler().runTask(plugin,()->{
            if(!player.isOnline()||!plugin.isAuthenticated(player)||player.isDead())return;
            var data=player.getPersistentDataContainer();
            if(!token.equals(data.get(deathKey,PersistentDataType.STRING)))return;
            finishAliveRecovery(player);
            if(target!=null&&!data.has(arrivalKey,PersistentDataType.BYTE))player.sendMessage("§aIndraprastha Hospital • You can return to the city.");
        });
    }

    /** A disconnect before respawn must not make the next death reuse an old settlement. */
    void afterAuthentication(Player player){
        if(!plugin.isAuthenticated(player)||player.isDead())return;
        finishAliveRecovery(player);
    }

    private void finishAliveRecovery(Player player){
        var data=player.getPersistentDataContainer();
        String token=data.get(deathKey,PersistentDataType.STRING);
        if(token==null&&!data.has(arrivalKey,PersistentDataType.BYTE))return;
        try{if(token!=null)UUID.fromString(token);}catch(IllegalArgumentException ex){
            plugin.getLogger().severe("Medical recovery token invalid for "+player.getUniqueId());return;
        }
        // An alive character has completed the death lifecycle. Arrival remains a separate
        // retryable obligation if another plugin cancels teleport; it cannot reuse a bill.
        data.remove(deathKey);data.remove(deathCounterKey);
        Location target=hospital();
        boolean arrived=target!=null&&target.getWorld().equals(player.getWorld())&&target.distanceSquared(player.getLocation())<=4;
        if(!arrived&&target!=null)arrived=player.teleport(target);
        if(arrived)data.remove(arrivalKey);else data.set(arrivalKey,PersistentDataType.BYTE,(byte)1);
        try{player.saveData();}
        catch(RuntimeException ex){plugin.getLogger().severe("Alive recovery checkpoint pending for "+player.getUniqueId());}
    }

    static UUID deathIdentifier(String token,Integer recordedCounter,int currentCounter){
        if(token!=null&&recordedCounter!=null&&recordedCounter==currentCounter)return UUID.fromString(token);
        return UUID.randomUUID();
    }
}
