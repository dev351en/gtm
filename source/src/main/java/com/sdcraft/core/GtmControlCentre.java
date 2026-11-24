package com.sdcraft.core;

import com.sdcraft.core.gtm.SnapshotStore;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.UUID;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.inventory.*;
import org.bukkit.inventory.*;

/** Staff-only manual festival switchboard. Player-local particles expire naturally. */
final class GtmControlCentre implements CommandExecutor, Listener {
    enum Festival {
        OFF("City calendar", Material.CLOCK, 0),
        DIWALI("Diwali", Material.LANTERN, 0xffb32e),
        HOLI("Holi", Material.MAGENTA_DYE, 0xd842a4),
        GANESH_CHATURTHI("Ganesh Chaturthi", Material.ORANGE_TULIP, 0xf79044),
        NAVRATRI("Navratri", Material.PURPLE_DYE, 0x964bd6),
        EID("Eid", Material.EMERALD, 0x55ad87),
        MAKAR_SANKRANTI("Makar Sankranti", Material.FEATHER, 0x66c6e4),
        CHRISTMAS("Christmas", Material.SPRUCE_SAPLING, 0x4cbd67),
        NEW_YEAR("New Year", Material.FIREWORK_STAR, 0xf7de84);

        final String label;
        final Material icon;
        final int color;
        Festival(String label, Material icon, int color) {
            this.label = label;
            this.icon = icon;
            this.color = color;
        }
    }

    private final SDCraftCorePlugin plugin;
    private final SnapshotStore store;
    private final GtmCityModels models;
    private long revision;
    private Festival active;

    GtmControlCentre(SDCraftCorePlugin plugin, GtmCityModels models) throws IOException {
        this.models = models;
        this.plugin = plugin;
        store = new SnapshotStore(plugin.getDataFolder().toPath().resolve("festival.snapshot"), 64);
        var saved = store.read();
        revision = saved.version();
        active = revision == 0 ? Festival.OFF : Festival.valueOf(new String(saved.payload(), StandardCharsets.UTF_8));
        refreshTheme();
    }

    private void refreshTheme() {
        if (models == null) return;
        String theme = switch (active) {
            case OFF -> null;
            case GANESH_CHATURTHI -> "ganesh";
            case MAKAR_SANKRANTI -> "sankranti";
            default -> active.name().toLowerCase(Locale.ROOT);
        };
        models.theme(theme);
    }

    private static final class Panel implements InventoryHolder {
        final long revision;
        final Inventory inventory;
        Panel(long revision) {
            this.revision = revision;
            inventory = Bukkit.createInventory(this, 9, "GTM Control Centre");
        }
        public Inventory getInventory() { return inventory; }
    }

    private void open(Player player) {
        var panel = new Panel(revision);
        for (Festival event : Festival.values()) {
            ItemStack item = new ItemStack(event.icon);
            item.editMeta(meta -> meta.setDisplayName((active == event ? "§a● " : "§7") +
                (event == Festival.OFF ? "End festival" : event.label)));
            panel.inventory.setItem(event.ordinal(), item);
        }
        player.openInventory(panel.inventory);
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!sender.hasPermission("gtm.control") || !plugin.getConfig().getBoolean("gtm.experimental-festivals")) {
            sender.sendMessage("GTM Control Centre is unavailable.");
            return true;
        }
        if (args.length == 0 && sender instanceof Player player) open(player);
        else if (args.length == 0 || (args.length == 1 && args[0].equalsIgnoreCase("status")))
            sender.sendMessage("Active festival: " + active.name());
        else if (args.length == 1) {
            try {
                select(sender, Festival.valueOf(args[0].toUpperCase(Locale.ROOT)));
            } catch (IllegalArgumentException ex) {
                sender.sendMessage("Choose one of " + java.util.Arrays.toString(Festival.values()));
            }
        } else sender.sendMessage("/gtmcontrol [status|festival|off]");
        return true;
    }

    private void select(CommandSender sender, Festival event) {
        if (event == active) return;
        try {
            revision = store.commit(revision, UUID.randomUUID(), event.name().getBytes(StandardCharsets.UTF_8)).version();
        } catch (IOException | IllegalStateException | java.util.ConcurrentModificationException ex) {
            sender.sendMessage("Festival change could not be saved.");
            plugin.getLogger().warning("Festival commit failed: " + ex.getClass().getSimpleName());
            return;
        }
        active = event;
        refreshTheme();
        plugin.getLogger().info(sender.getName() + " selected festival " + event.name());
        sender.sendMessage("Active festival: " + event.name());
        World world = city();
        if (world != null) for (Player p : world.getPlayers())
            p.sendMessage(event == Festival.OFF ? "The city festival has ended." : event.label + " has begun in Indraprastha.");
    }

    private World city() { return Bukkit.getWorld(plugin.getConfig().getString("world.name", "world")); }

    void pulse() {
        if (active == Festival.OFF || !plugin.getConfig().getBoolean("gtm.experimental-festivals")) return;
        World world = city();
        if (world == null) return;
        var dust = new Particle.DustOptions(Color.fromRGB(active.color), 1.1f);
        for (Player p : world.getPlayers()) {
            if (p.hasMetadata("NPC")) continue;
            p.spawnParticle(Particle.DUST, p.getLocation().add(0, 2.5, 0), 8, 3, 1, 3, 0, dust);
        }
    }

    @EventHandler
    public void click(InventoryClickEvent event) {
        if (!(event.getView().getTopInventory().getHolder() instanceof Panel panel)) return;
        event.setCancelled(true);
        int slot = event.getRawSlot();
        if (!(event.getWhoClicked() instanceof Player p) || !p.hasPermission("gtm.control") ||
            !plugin.getConfig().getBoolean("gtm.experimental-festivals") ||
            slot < 0 || slot >= Festival.values().length ||
            (event.getClick() != ClickType.LEFT && event.getClick() != ClickType.RIGHT)) return;
        Bukkit.getScheduler().runTask(plugin, () -> {
            if (!p.isOnline() || !p.hasPermission("gtm.control") || !plugin.getConfig().getBoolean("gtm.experimental-festivals") ||
                p.getOpenInventory().getTopInventory().getHolder() != panel) return;
            if (panel.revision == revision) select(p, Festival.values()[slot]);
            open(p);
        });
    }

    @EventHandler
    public void drag(InventoryDragEvent event) {
        if (event.getView().getTopInventory().getHolder() instanceof Panel) event.setCancelled(true);
    }
}
