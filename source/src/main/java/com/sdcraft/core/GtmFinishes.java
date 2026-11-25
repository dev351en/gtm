package com.sdcraft.core;

import com.sdcraft.core.gtm.Finish;
import java.io.IOException;
import java.util.Locale;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.inventory.*;
import org.bukkit.inventory.*;
import org.bukkit.persistence.PersistentDataType;

/** Both editions browse the same catalogue and commit purchases to the existing bank ledger. */
final class GtmFinishes implements Listener {
    private final SDCraftCorePlugin plugin;
    private final Ledger ledger;
    private final GunEngine guns;

    GtmFinishes(SDCraftCorePlugin plugin, Ledger ledger, GunEngine guns) {
        this.plugin = plugin;
        this.ledger = ledger;
        this.guns = guns;
    }

    private static final class Page implements InventoryHolder {
        final String family;
        final int offset;
        final Finish review;
        final Inventory inventory;
        Page(String family, int offset, Finish review) {
            this.family = family;
            this.offset = offset;
            this.review = review;
            inventory = Bukkit.createInventory(this, 54, review == null ? "GTM Finish Studio" : "Review finish");
        }
        public Inventory getInventory() { return inventory; }
    }

    private GunEngine.GunType held(Player p) {
        var stack = p.getInventory().getItemInMainHand();
        if (!stack.hasItemMeta()) return null;
        var name = stack.getItemMeta().getPersistentDataContainer().get(guns.getKeyType(), PersistentDataType.STRING);
        if (name == null) return null;
        for (var type : GunEngine.GunType.values())
            if (type.name().equals(name) && type.material == stack.getType()) return type;
        return null;
    }

    private boolean allowed(Player p) {
        return plugin.isAuthenticated(p) && plugin.getConfig().getBoolean("gtm.experimental-finishes") && p.hasPermission("gtm.finishes")
            && ledger.exists(p.getUniqueId());
    }

    void open(Player p, int offset, Finish review) {
        if (!allowed(p)) { p.sendMessage("Finish Studio is unavailable."); return; }
        var gun = held(p);
        if (gun == null) { p.sendMessage("Hold a native SD Craft game weapon to open the finish rack."); return; }
        String family = gun.name().toLowerCase(Locale.ROOT);
        Page page = new Page(family, offset, review);
        if (review == null) {
            for (int i=offset; i<Math.min(offset+45,Finish.COUNT_PER_FAMILY); i++) {
                var finish = new Finish(family,i);
                page.inventory.setItem(i-offset, swatch(p,gun.material,finish));
            }
            if (offset > 0) page.inventory.setItem(45, button(Material.ARROW,"Previous designs"));
            if (offset+45 < Finish.COUNT_PER_FAMILY) page.inventory.setItem(53,button(Material.ARROW,"More designs"));
        } else {
            page.inventory.setItem(13,swatch(p,gun.material,review));
            page.inventory.setItem(22,button(Material.EMERALD, ledger.ownsFinish(p.getUniqueId(),review)
                ? "Apply owned finish" : "Buy and apply for " + review.priceCents()/100 + " ARK"));
            page.inventory.setItem(45,button(Material.ARROW,"Back"));
        }
        p.openInventory(page.inventory);
    }

    private ItemStack button(Material material, String text) {
        var stack = new ItemStack(material);
        stack.editMeta(meta -> meta.setDisplayName(text));
        return stack;
    }

    private ItemStack swatch(Player p, Material material, Finish finish) {
        var item = button(material,finish.title());
        item.editMeta(meta -> {
            meta.setItemModel(new NamespacedKey("gtm",finish.id()));
            meta.setLore(java.util.List.of(ledger.ownsFinish(p.getUniqueId(),finish)
                ? "Owned" : finish.priceCents()/100 + " ARK"));
        });
        return item;
    }

    @EventHandler
    public void click(InventoryClickEvent event) {
        if (!(event.getView().getTopInventory().getHolder() instanceof Page page)) return;
        event.setCancelled(true);
        int slot = event.getRawSlot();
        if (!(event.getWhoClicked() instanceof Player p) || !allowed(p) || slot < 0 || slot >= 54 ||
            page.inventory.getItem(slot) == null || (event.getClick()!=ClickType.LEFT && event.getClick()!=ClickType.RIGHT)) return;
        Bukkit.getScheduler().runTask(plugin, () -> {
            if (!p.isOnline() || !allowed(p) || p.getOpenInventory().getTopInventory().getHolder()!=page) return;
            var gun = held(p);
            if (gun == null || !gun.name().equalsIgnoreCase(page.family)) { p.closeInventory(); return; }
            try {
                if (page.review == null && slot < 45) open(p,page.offset,new Finish(page.family,page.offset+slot));
                else if (page.review != null && slot == 22) {
                    if (!ledger.acquireFinish(p.getUniqueId(),page.review)) { p.sendMessage("Insufficient bank balance."); return; }
                    var item = p.getInventory().getItemInMainHand();
                    item.editMeta(meta -> meta.setItemModel(new NamespacedKey("gtm",page.review.id())));
                    p.getInventory().setItemInMainHand(item);
                    p.closeInventory();
                    p.sendMessage("Applied " + page.review.title() + ".");
                } else if (slot==45 || slot==53) open(p, page.review==null && slot==53 ? 45 : page.review==null ? 0 : page.offset, null);
            } catch (IOException | RuntimeException ex) {
                p.closeInventory();
                plugin.getLogger().warning("Finish operation failed: " + ex.getClass().getSimpleName());
                p.sendMessage("Check your owned finishes before retrying.");
            }
        });
    }

    @EventHandler
    public void drag(InventoryDragEvent event) {
        if (event.getView().getTopInventory().getHolder() instanceof Page) event.setCancelled(true);
    }
}
