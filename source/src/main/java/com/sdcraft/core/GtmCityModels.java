package com.sdcraft.core;

import java.io.*;
import java.util.*;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.world.ChunkUnloadEvent;
import org.bukkit.inventory.*;

/** Staff catalogue plus nonpersistent street furnishings at surveyed staging fixtures. */
final class GtmCityModels implements CommandExecutor, Listener {
    private record Design(String id, String category, String title) {}
    private record Fixture(int x,int y,int z,Material floor,String design,boolean seasonal) {}
    private static final List<Fixture> FIXTURES = List.of(
        new Fixture(117,66,-42,Material.OAK_PLANKS,"filing_cabinet_metro",false),
        new Fixture(126,66,-60,Material.OAK_PLANKS,"council_lectern",true),
        new Fixture(-378,65,-321,Material.STONE_BRICKS,"luggage_rack_art_deco",false)
    );
    private final SDCraftCorePlugin plugin;
    private final Map<String,Design> designs = new LinkedHashMap<>();
    private final Map<Fixture,ArmorStand> installed = new HashMap<>();
    private String theme;

    GtmCityModels(SDCraftCorePlugin plugin) throws IOException {
        this.plugin=plugin;
        for (var entry : GtmAssetCatalog.bundled().paperModels()) {
            designs.put(entry.key(), new Design(entry.key(), entry.category(), entry.title()));
        }
        for (var fixture : FIXTURES) {
            if (!designs.containsKey(fixture.design()))
                throw new IOException("Missing surveyed fixture model: " + fixture.design());
        }
    }

    private static final class Shelf implements InventoryHolder {
        final String category;
        final List<Design> entries;
        final int page;
        final Inventory inventory;
        Shelf(String category,List<Design> entries,int page) {
            this.category=category; this.entries=entries; this.page=page;
            inventory=Bukkit.createInventory(this,54,"GTM Models • "+category);
        }
        public Inventory getInventory(){ return inventory; }
    }

    private ItemStack model(Design design) {
        ItemStack item=new ItemStack(Material.PAPER);
        item.editMeta(meta -> {
            meta.setItemModel(new NamespacedKey("gtm",design.id()));
            meta.setDisplayName(design.title());
        });
        return item;
    }

    private void open(Player p,String category,int page) {
        List<Design> list=designs.values().stream().filter(d -> category.equals("all") || d.category().equals(category)).toList();
        if (list.isEmpty()) { p.sendMessage("Categories: "+String.join(", ",designs.values().stream().map(Design::category).distinct().sorted().toList())); return; }
        Shelf shelf=new Shelf(category,list,page);
        for (int i=page*45;i<Math.min(page*45+45,list.size());i++) shelf.inventory.setItem(i%45,model(list.get(i)));
        if (page>0) shelf.inventory.setItem(45,new ItemStack(Material.ARROW));
        if ((page+1)*45<list.size()) shelf.inventory.setItem(53,new ItemStack(Material.ARROW));
        p.openInventory(shelf.inventory);
    }

    public boolean onCommand(CommandSender sender,Command command,String label,String[] args) {
        if (sender instanceof Player p && plugin.isAuthenticated(p) && p.hasPermission("gtm.models") && plugin.getConfig().getBoolean("gtm.experimental-models"))
            open(p,args.length==0?"all":args[0].toLowerCase(Locale.ROOT),0);
        else sender.sendMessage("GTM model catalogue unavailable.");
        return true;
    }

    @EventHandler public void click(InventoryClickEvent event) {
        if (!(event.getView().getTopInventory().getHolder() instanceof Shelf shelf)) return;
        event.setCancelled(true);
        int slot=event.getRawSlot();
        if (!(event.getWhoClicked() instanceof Player p) || (event.getClick()!=ClickType.LEFT && event.getClick()!=ClickType.RIGHT)
                || slot<0 || slot>=54 || shelf.inventory.getItem(slot)==null) return;
        Bukkit.getScheduler().runTask(plugin,()->{
            if (!p.isOnline() || !plugin.isAuthenticated(p) || !p.hasPermission("gtm.models") || !plugin.getConfig().getBoolean("gtm.experimental-models")
                || p.getOpenInventory().getTopInventory().getHolder()!=shelf) return;
            if (slot==45 || slot==53) open(p,shelf.category,shelf.page+(slot==45?-1:1));
            else if (slot<45) {
                var design=shelf.entries.get(45*shelf.page+slot);
                if (!p.getInventory().addItem(model(design)).isEmpty()) p.sendMessage("Inventory full.");
            }
        });
    }
    @EventHandler public void drag(InventoryDragEvent event) {
        if (event.getView().getTopInventory().getHolder() instanceof Shelf) event.setCancelled(true);
    }

    void theme(String next) {
        if (Objects.equals(theme,next)) return;
        theme=next;
        for (Fixture f:FIXTURES) if (f.seasonal()) remove(f);
    }

    void refresh() {
        if (!plugin.getConfig().getBoolean("gtm.experimental-furnishings")) { close(); return; }
        World world=Bukkit.getWorld(plugin.getConfig().getString("world.name","world"));
        if (world==null) { close();return; }
        for (Fixture f:FIXTURES) {
            if (!world.isChunkLoaded(f.x()>>4,f.z()>>4)) { remove(f);continue; }
            Location at=new Location(world,f.x()+.5,f.y(),f.z()+.5);
            if (world.getBlockAt(f.x(),f.y()-1,f.z()).getType()!=f.floor() || !at.getBlock().isEmpty()
                || !world.getBlockAt(f.x(),f.y()+1,f.z()).isEmpty()) { remove(f);continue; }
            if (world.getPlayers().stream().noneMatch(p -> !p.hasMetadata("NPC") && p.getLocation().distanceSquared(at)<48*48)) { remove(f);continue; }
            ArmorStand stand=installed.get(f);
            if (stand!=null && stand.isValid()) continue;
            String id=f.seasonal() && theme!=null ? theme+"_counterpiece" : f.design();
            Design design=designs.get(id);
            if (design==null) { remove(f); continue; }
            installed.put(f,world.spawn(at.clone().subtract(0,1.1,0),ArmorStand.class,a->{
                a.setPersistent(false); a.setVisible(false); a.setGravity(false); a.setMarker(true); a.setInvulnerable(true);
                a.addDisabledSlots(EquipmentSlot.HEAD, EquipmentSlot.HAND, EquipmentSlot.OFF_HAND, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET);
                a.getEquipment().setHelmet(model(design));
            }));
        }
    }
    @EventHandler public void unload(ChunkUnloadEvent e) {
        for (Fixture f:FIXTURES) {
            ArmorStand a=installed.get(f);
            if (a!=null && a.getWorld().equals(e.getWorld()) && (f.x()>>4)==e.getChunk().getX() && (f.z()>>4)==e.getChunk().getZ()) remove(f);
        }
    }
    private void remove(Fixture f) { ArmorStand a=installed.remove(f); if (a!=null) a.remove(); }
    void close() { for (Fixture f:FIXTURES) remove(f); }
}
