package com.sdcraft.core;

import com.sdcraft.core.gtm.FoodCatalogue;
import java.io.IOException;
import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.inventory.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.ItemMeta;

/** Staging food ordering and surveyed counter collection; physical scooter delivery remains separate. */
final class GtmFood implements Listener {
    private final SDCraftCorePlugin plugin;
    private final Ledger ledger;
    private static final class Menu implements InventoryHolder {
        final UUID viewer,orderId=UUID.randomUUID();
        final String brand;
        final FoodCatalogue.Ticket ticket;
        final String meal;
        Inventory inv;
        boolean consumed;
        Menu(UUID viewer,String brand,FoodCatalogue.Ticket ticket,String meal){this.viewer=viewer;this.brand=brand;this.ticket=ticket;this.meal=meal;}
        @Override public Inventory getInventory(){return inv;}
    }
    GtmFood(SDCraftCorePlugin plugin,Ledger ledger){this.plugin=plugin;this.ledger=ledger;}
    boolean available(Player p){
        return plugin.isAuthenticated(p)&&plugin.getConfig().getBoolean("gtm.experimental-food",false)&&p.hasPermission("gtm.food")&&ledger.exists(p.getUniqueId());
    }
    private Location vendor(String brand){return plugin.site("food_"+brand);}
    private String name(String brand){return brand.equals("zomatoo")?"Zomatoo":"Swiffy";}
    private String ark(long cents){return String.format(Locale.ROOT,"%,.2f ARK",cents/100d);}
    private ItemStack item(Material material,String title,String... lore){
        ItemStack i=new ItemStack(material);ItemMeta m=i.getItemMeta();
        if(m!=null){m.setDisplayName(title);m.setLore(List.of(lore));i.setItemMeta(m);}return i;
    }
    private ItemStack mealItem(FoodCatalogue.Meal meal, String title, String... lore) {
        ItemStack stack = item(Material.BREAD, title, lore);
        stack.editMeta(meta -> meta.setItemModel(new NamespacedKey("gtm", meal.id())));
        return stack;
    }
    void open(Player p,String brand){
        if(!available(p)||!FoodCatalogue.validBrand(brand)){p.sendMessage("§cFood service unavailable.");return;}
        try {
            var t=ledger.foodOrder(p.getUniqueId()).filter(FoodCatalogue.Ticket::open).orElse(null);
            Menu m=new Menu(p.getUniqueId(),brand,t,null);Inventory inv=Bukkit.createInventory(m,t==null?45:27,"§8"+name(brand)+" | Food orders");m.inv=inv;
            if(t!=null){
                Location v=plugin.site(t.vendor());
                inv.setItem(4,item(Material.PAPER,"§e"+name(t.brand())+" order: "+FoodCatalogue.get(t.meal()).name(),ark(t.price()),
                    t.ready(System.currentTimeMillis())?"Ready for counter collection":"Preparing your order",
                    v==null?"Counter unavailable — cancel for refund":"Counter: "+v.getWorld().getName()+" "+v.getBlockX()+", "+v.getBlockY()+", "+v.getBlockZ()));
                inv.setItem(13,item(Material.BREAD,"§aCollect at counter","Within 5 blocks of surveyed food counter"));
                inv.setItem(15,item(Material.BARRIER,"§cCancel and refund",ark(t.price())));
            }else if(vendor(brand)!=null){
                for(int i=0;i<FoodCatalogue.ITEMS.size();i++){
                    var food=FoodCatalogue.ITEMS.get(i);
                    inv.setItem(i,mealItem(food,"§e"+food.name(),ark(food.cents()),"Counter collection — click to review"));
                }
            }else inv.setItem(13,item(Material.BARRIER,"§cCounter not commissioned","No orders or payments accepted"));
            inv.setItem(inv.getSize()-5,item(Material.CLOCK,"§7Collection pilot","Scooter delivery is not enabled yet."));
            p.openInventory(inv);
        }catch(RuntimeException e){p.sendMessage("§cFood order record unavailable.");}
    }
    private void confirm(Player p,String brand,String meal){
        var food=FoodCatalogue.get(meal);
        Menu m=new Menu(p.getUniqueId(),brand,null,meal);Inventory inv=Bukkit.createInventory(m,27,"§8Confirm "+name(brand)+" order");m.inv=inv;
        inv.setItem(4,mealItem(food,"§e"+food.name(),ark(food.cents()),"Preparation: 15 seconds","Collect from surveyed counter; cancel for refund"));
        inv.setItem(13,item(Material.EMERALD,"§aConfirm bank payment",ark(food.cents())));
        inv.setItem(22,item(Material.ARROW,"Back"));p.openInventory(inv);
    }
    private void collect(Player p,FoodCatalogue.Ticket t) throws IOException {
        if(!t.ready(System.currentTimeMillis())){p.sendMessage("§eYour food is still being prepared.");return;}
        Location v=plugin.site(t.vendor());
        if(v==null||!v.getWorld().equals(p.getWorld())||v.distanceSquared(p.getLocation())>25){p.sendMessage("§eVisit the order counter to collect your food.");return;}
        if(p.getInventory().firstEmpty()<0){p.sendMessage("§eFree an inventory slot first.");return;}
        var meal=FoodCatalogue.get(t.meal());
        ItemStack food=mealItem(meal,"§6"+meal.name(),"Order receipt: "+t.id());food.setAmount(meal.portions());
        if(!ledger.collectFoodToDelivery(p.getUniqueId(),t.id(),System.currentTimeMillis(),GtmItemDelivery.encode(food)))return;
        plugin.deliveries().retry(p);
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void click(InventoryClickEvent e){
        if(!(e.getView().getTopInventory().getHolder() instanceof Menu m))return;
        e.setCancelled(true);
        if(!(e.getWhoClicked() instanceof Player p)||!p.getUniqueId().equals(m.viewer)||!available(p)||m.consumed)return;
        if(e.getClick()!=ClickType.LEFT&&e.getClick()!=ClickType.RIGHT)return;
        int slot=e.getRawSlot();if(slot<0||slot>=m.inv.getSize()||m.inv.getItem(slot)==null)return;
        m.consumed=true;
        Bukkit.getScheduler().runTask(plugin,()->{
            if(!p.isOnline()||!available(p)||p.getOpenInventory().getTopInventory().getHolder()!=m)return;
            try{
                if(m.meal!=null){
                    if(slot==13){
                        if(vendor(m.brand)==null){p.sendMessage("§cCounter unavailable; no payment taken.");}
                        else {
                            boolean ok=ledger.orderFood(p.getUniqueId(),m.orderId,m.brand,m.meal,"food_"+m.brand,System.currentTimeMillis());
                            p.sendMessage(ok?"§aOrder paid. Collect at the counter when ready.":"§eOrder exists or insufficient funds.");
                        }
                    }
                }else if(m.ticket!=null){
                    if(slot==13)collect(p,m.ticket);
                    if(slot==15)p.sendMessage(ledger.refundFood(p.getUniqueId(),m.ticket.id())?"§aPayment refunded.":"§eOrder already closed.");
                }else if(slot<FoodCatalogue.ITEMS.size()&&vendor(m.brand)!=null){
                    confirm(p,m.brand,FoodCatalogue.ITEMS.get(slot).id());return;
                }
                open(p,m.brand);
            }catch(IOException|RuntimeException ex){plugin.getLogger().warning("Food order operation failed: "+ex.getClass().getSimpleName());p.sendMessage("§cFood service unavailable. Review order status.");p.closeInventory();}
        });
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void drag(InventoryDragEvent e){if(e.getView().getTopInventory().getHolder() instanceof Menu)e.setCancelled(true);}
}
