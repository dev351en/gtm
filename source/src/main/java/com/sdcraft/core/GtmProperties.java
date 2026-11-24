package com.sdcraft.core;

import com.sdcraft.core.gtm.RegionBounds;
import com.sdcraft.core.gtm.CivicRules.Property;
import java.io.IOException;
import java.util.*;
import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.block.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataType;

/** Survey-driven staging property service. No world edits or guessed coordinates. */
final class GtmProperties implements Listener {
    private record Definition(UUID id,String name,RegionBounds region,long price) {}
    private final SDCraftCorePlugin plugin;
    private final Ledger ledger;
    private final List<Definition> definitions;
    private final NamespacedKey keyProperty,keyValue;
    private final boolean enabled;
    private static final class Menu implements InventoryHolder {
        final UUID viewer; final List<Definition> page; final Definition detail; final int pageNumber;
        Inventory inventory; boolean consumed;
        Menu(UUID viewer,List<Definition> page,Definition detail,int pageNumber){
            this.viewer=viewer;this.page=page;this.detail=detail;this.pageNumber=pageNumber;
        }
        @Override public Inventory getInventory(){return inventory;}
    }
    GtmProperties(SDCraftCorePlugin plugin,Ledger ledger){
        this.plugin=plugin;this.ledger=ledger;
        keyProperty=new NamespacedKey(plugin,"property_id");keyValue=new NamespacedKey(plugin,"property_key");
        enabled=plugin.getConfig().getBoolean("gtm.experimental-properties",false);
        List<Definition> loaded=new ArrayList<>();
        if(enabled){
            Set<UUID> ids=new HashSet<>();
            for(Map<?,?> entry:plugin.getConfig().getMapList("gtm.property-regions")){
                UUID id=UUID.fromString(String.valueOf(entry.get("id")));
                String name=String.valueOf(entry.get("name")),world=String.valueOf(entry.get("world"));
                if(!ids.add(id)||name.isBlank()||name.equals("null")||name.length()>60||Bukkit.getWorld(world)==null)
                    throw new IllegalArgumentException("Invalid property identity or world");
                long price=number(entry.get("price-cents"));
                if(price<=0||price>100000000000L)throw new IllegalArgumentException("Invalid property price");
                RegionBounds b=new RegionBounds(world,coord(entry,"min-x"),coord(entry,"min-y"),coord(entry,"min-z"),coord(entry,"max-x"),coord(entry,"max-y"),coord(entry,"max-z"));
                if(loaded.stream().anyMatch(d->d.region().overlaps(b)))throw new IllegalArgumentException("Overlapping property regions");
                loaded.add(new Definition(id,name,b,price));
                if(loaded.size()>256)throw new IllegalArgumentException("Property registry exceeds 256 entries");
            }
            if(loaded.isEmpty())throw new IllegalArgumentException("No surveyed property regions configured");
        }
        definitions=List.copyOf(loaded);
    }
    private static long number(Object v){
        if(!(v instanceof Byte||v instanceof Short||v instanceof Integer||v instanceof Long))throw new IllegalArgumentException("Integer required");
        return ((Number)v).longValue();
    }
    private static int coord(Map<?,?> entry,String key){return Math.toIntExact(number(entry.get(key)));}
    boolean available(Player p){return enabled&&p.hasPermission("gtm.properties")&&ledger.exists(p.getUniqueId());}
    private Definition at(Location l){
        if(!enabled||l==null||l.getWorld()==null)return null;
        for(Definition d:definitions)if(d.region().contains(l.getWorld().getName(),l.getX(),l.getY(),l.getZ()))return d;
        return null;
    }
    private boolean permitted(Player p,Definition d){
        if(d==null)return true;
        if(p.hasPermission("gtm.properties.admin"))return true;
        try{return ledger.property(d.id()).canEnter(p.getUniqueId(),false);}
        catch(RuntimeException e){return false;}
    }
    private void crossing(PlayerMoveEvent e){
        if(!enabled||e.getTo()==null)return;
        Location a=e.getFrom(),b=e.getTo();
        if(Objects.equals(a.getWorld(),b.getWorld())&&a.getBlockX()==b.getBlockX()&&a.getBlockY()==b.getBlockY()&&a.getBlockZ()==b.getBlockZ())return;
        Definition destination=at(b),origin=at(a);
        if(destination==null||destination.equals(origin))return; // Permit egress for players already inside; deny their interactions.
        Player p=e.getPlayer();
        if(!permitted(p,destination)){e.setCancelled(true);p.sendActionBar(net.kyori.adventure.text.Component.text("Private property — access denied"));return;}
        if(p.hasPermission("gtm.properties.admin")&&!ledger.property(destination.id()).canEnter(p.getUniqueId(),false))
            plugin.getLogger().info("Property admin entry "+p.getUniqueId()+" "+destination.id());
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void move(PlayerMoveEvent e){if(!(e instanceof PlayerTeleportEvent))crossing(e);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void teleport(PlayerTeleportEvent e){crossing(e);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void blockBreak(BlockBreakEvent e){if(!permitted(e.getPlayer(),at(e.getBlock().getLocation())))e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void blockPlace(BlockPlaceEvent e){if(!permitted(e.getPlayer(),at(e.getBlockPlaced().getLocation())))e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void entityInteract(PlayerInteractEntityEvent e){if(!permitted(e.getPlayer(),at(e.getRightClicked().getLocation())))e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void container(InventoryOpenEvent e){
        if(e.getPlayer() instanceof Player p&&!permitted(p,at(e.getInventory().getLocation())))e.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void interact(PlayerInteractEvent e){
        if(!enabled)return;
        Player p=e.getPlayer();Block block=e.getClickedBlock();Definition d=block==null?at(p.getLocation()):at(block.getLocation());
        if(!permitted(p,d)){e.setCancelled(true);return;}
        if(d==null||e.getHand()!=EquipmentSlot.HAND||!available(p)||e.getAction()!=Action.RIGHT_CLICK_BLOCK)return;
        ItemStack item=e.getItem();if(item==null||!item.hasItemMeta())return;
        var data=item.getItemMeta().getPersistentDataContainer();
        String id=data.get(keyProperty,PersistentDataType.STRING),key=data.get(keyValue,PersistentDataType.STRING);
        if(id==null||key==null)return;
        e.setCancelled(true);
        try{
            if(!d.id().toString().equals(id))throw new SecurityException("Wrong property");
            Property current=ledger.property(d.id());
            ledger.propertyLock(p.getUniqueId(),d.id(),UUID.fromString(key),!current.locked());
            p.sendMessage(current.locked()?"§aProperty unlocked.":"§aProperty locked.");
        }catch(IOException|RuntimeException ex){p.sendMessage("§cInvalid key or property service unavailable.");}
    }
    private ItemStack item(Material material,String name,String... lore){
        ItemStack i=new ItemStack(material);ItemMeta m=i.getItemMeta();
        if(m!=null){m.setDisplayName(name);m.setLore(List.of(lore));i.setItemMeta(m);}return i;
    }
    private String ark(long cents){return String.format(Locale.ROOT,"%,.2f ARK",cents/100d);}
    void open(Player p){openPage(p,0);}
    private void openPage(Player p,int number){
        if(!available(p)){p.sendMessage("§cProperty service unavailable.");return;}
        int start=Math.max(0,number)*45;if(start>=definitions.size())return;
        List<Definition> page=definitions.subList(start,Math.min(start+45,definitions.size()));
        Menu m=new Menu(p.getUniqueId(),List.copyOf(page),null,number);Inventory inv=Bukkit.createInventory(m,54,"§8Indraprastha | Properties");m.inventory=inv;
        try{
            for(int j=0;j<page.size();j++){
                Definition d=page.get(j);Property state=ledger.property(d.id());
                String status=state.owner()==null?ark(d.price()):p.getUniqueId().equals(state.owner())?"Owned by you":"Unavailable";
                inv.setItem(j,item(Material.OAK_DOOR,"§e"+d.name(),status,"Click for details"));
            }
            if(number>0)inv.setItem(45,item(Material.ARROW,"Previous page"));
            if(start+45<definitions.size())inv.setItem(53,item(Material.ARROW,"Next page"));
            p.openInventory(inv);
        }catch(RuntimeException e){p.sendMessage("§cProperty records unavailable.");}
    }
    private void detail(Player p,Definition d,int page){
        if(!available(p))return;
        Property state=ledger.property(d.id());Menu m=new Menu(p.getUniqueId(),List.of(),d,page);
        Inventory inv=Bukkit.createInventory(m,27,"§8Property | "+d.name());m.inventory=inv;
        inv.setItem(4,item(Material.OAK_DOOR,"§e"+d.name(),"Bank: "+ark(ledger.bank(p.getUniqueId()))));
        if(state.owner()==null)inv.setItem(13,item(Material.EMERALD,"§aConfirm purchase",ark(d.price()),"Private access upon purchase"));
        if(p.getUniqueId().equals(state.owner())){
            inv.setItem(11,item(Material.TRIPWIRE_HOOK,"§aCollect key","Right-click a block in your property to lock/unlock"));
            inv.setItem(13,item(Material.IRON_DOOR,state.locked()?"§eLocked":"§aUnlocked","Use a registered physical key"));
            inv.setItem(15,item(Material.GOLD_NUGGET,"§eReplace keys","Invalidates previous keys and guest access"));
        }
        inv.setItem(22,item(Material.ARROW,"Back to properties"));p.openInventory(inv);
    }
    private void giveKey(Player p,Definition d){
        Property state=ledger.property(d.id());if(!p.getUniqueId().equals(state.owner()))throw new SecurityException();
        ItemStack i=item(Material.TRIPWIRE_HOOK,"§6"+d.name()+" key","Owner-bound; copied or old keys cannot grant access");
        ItemMeta m=i.getItemMeta();m.getPersistentDataContainer().set(keyProperty,PersistentDataType.STRING,d.id().toString());
        m.getPersistentDataContainer().set(keyValue,PersistentDataType.STRING,state.key().toString());i.setItemMeta(m);
        if(!p.getInventory().addItem(i).isEmpty())p.sendMessage("§eInventory full. Collect your key later.");
        else p.sendMessage("§aProperty key issued.");
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void click(InventoryClickEvent e){
        if(!(e.getView().getTopInventory().getHolder() instanceof Menu m))return;e.setCancelled(true);
        if(!(e.getWhoClicked() instanceof Player p)||!p.getUniqueId().equals(m.viewer)||m.consumed||!available(p))return;
        if(e.getClick()!=ClickType.LEFT&&e.getClick()!=ClickType.RIGHT)return;
        int slot=e.getRawSlot();if(slot<0||slot>=m.inventory.getSize()||m.inventory.getItem(slot)==null)return;
        m.consumed=true;
        Bukkit.getScheduler().runTask(plugin,()->{
            if(!p.isOnline()||!available(p)||p.getOpenInventory().getTopInventory().getHolder()!=m)return;
            try{
                if(m.detail==null){
                    if(slot<m.page.size())detail(p,m.page.get(slot),m.pageNumber);
                    else if(slot==45)openPage(p,m.pageNumber-1);
                    else if(slot==53)openPage(p,m.pageNumber+1);
                    return;
                }
                Definition d=m.detail;Property state=ledger.property(d.id());
                if(slot==22){openPage(p,m.pageNumber);return;}
                if(slot==13&&state.owner()==null){
                    boolean ok=ledger.purchaseProperty(p.getUniqueId(),d.id(),d.price());
                    p.sendMessage(ok?"§aProperty purchased.":"§cProperty unavailable or insufficient bank funds.");
                }else if(slot==11&&p.getUniqueId().equals(state.owner()))giveKey(p,d);
                else if(slot==15&&p.getUniqueId().equals(state.owner())){ledger.propertyRekey(p.getUniqueId(),d.id());giveKey(p,d);}
                detail(p,d,m.pageNumber);
            }catch(IOException|RuntimeException ex){plugin.getLogger().warning("Property operation failed: "+ex.getClass().getSimpleName());p.sendMessage("§cProperty operation unavailable.");p.closeInventory();}
        });
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void drag(InventoryDragEvent e){if(e.getView().getTopInventory().getHolder() instanceof Menu)e.setCancelled(true);}
}
