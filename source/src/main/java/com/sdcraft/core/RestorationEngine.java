package com.sdcraft.core;

import java.io.File;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.block.data.BlockData;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.block.BlockExplodeEvent;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.plugin.java.JavaPlugin;

/**
 * 5-Minute Real Auto-Regeneration System.
 * Restores street and structure damage caused by explosions or vandalism after 300 seconds (5 minutes).
 * Excludes underground mining (Y < minY), farming areas, and player-built new structures.
 */
public final class RestorationEngine implements Listener {

    public record RestoreRecord(Location location, BlockData blockData, long restoreAt) {}
    public record RestorableZone(String name, String world, int x, int y, int z, int radius) {}

    private final JavaPlugin plugin;
    private final File zonesFile;
    private final YamlConfiguration zonesConfig;

    // In-memory queue of blocks awaiting restoration (keyed by block location)
    private final Map<Location, RestoreRecord> pendingRestores = new ConcurrentHashMap<>();

    // Track player-placed blocks so player constructions are NOT overwritten as city streets
    private final Set<Location> playerPlacedBlocks = Collections.newSetFromMap(new ConcurrentHashMap<>());

    // Admin defined restorable zones
    private final Map<String, RestorableZone> zones = new HashMap<>();

    // Default 5 minutes (300 seconds)
    private static final long DEFAULT_DELAY_MS = 300_000L;
    private static final int DEFAULT_MIN_Y = 55; // Ground level boundary (excludes underground mining)

    public RestorationEngine(JavaPlugin plugin) {
        this.plugin = plugin;
        this.zonesFile = new File(plugin.getDataFolder(), "restorable_zones.yml");
        this.zonesConfig = YamlConfiguration.loadConfiguration(zonesFile);
        loadZones();
    }

    private void loadZones() {
        zones.clear();
        ConfigurationSection sec = zonesConfig.getConfigurationSection("zones");
        if (sec != null) {
            for (String key : sec.getKeys(false)) {
                String w = sec.getString(key + ".world", "world");
                int x = sec.getInt(key + ".x");
                int y = sec.getInt(key + ".y");
                int z = sec.getInt(key + ".z");
                int r = sec.getInt(key + ".radius", 50);
                zones.put(key, new RestorableZone(key, w, x, y, z, r));
            }
        }
    }

    public void saveZones() {
        zonesConfig.set("zones", null);
        for (RestorableZone z : zones.values()) {
            String p = "zones." + z.name;
            zonesConfig.set(p + ".world", z.world);
            zonesConfig.set(p + ".x", z.x);
            zonesConfig.set(p + ".y", z.y);
            zonesConfig.set(p + ".z", z.z);
            zonesConfig.set(p + ".radius", z.radius);
        }
        try {
            zonesConfig.save(zonesFile);
        } catch (IOException e) {
            plugin.getLogger().warning("Failed to save restorable_zones.yml: " + e.getMessage());
        }
    }

    public boolean markZone(String name, Location loc, int radius) {
        zones.put(name, new RestorableZone(name, loc.getWorld().getName(), loc.getBlockX(), loc.getBlockY(), loc.getBlockZ(), radius));
        saveZones();
        return true;
    }

    public boolean unmarkZone(String name) {
        if (zones.remove(name) != null) {
            saveZones();
            return true;
        }
        return false;
    }

    public Collection<RestorableZone> getZones() {
        return Collections.unmodifiableCollection(zones.values());
    }

    public int getPendingCount() {
        return pendingRestores.size();
    }

    /**
     * Determines if a block location is eligible for 5-minute auto-regeneration.
     */
    public boolean isRestorable(Block block) {
        Location loc = block.getLocation();

        // 1. Exclude underground mining and deep caves
        int minY = plugin.getConfig().getInt("restoration.min-y", DEFAULT_MIN_Y);
        if (loc.getBlockY() < minY) {
            return false;
        }

        // 2. Exclude crops, farmlands, and agricultural areas
        Material mat = block.getType();
        if (mat == Material.FARMLAND || mat == Material.WHEAT || mat == Material.CARROTS ||
            mat == Material.POTATOES || mat == Material.BEETROOTS || mat == Material.PUMPKIN_STEM ||
            mat == Material.MELON_STEM || mat == Material.SUGAR_CANE) {
            return false;
        }

        // 3. Exclude player-placed structures (if a player built it, don't restore street over it)
        if (playerPlacedBlocks.contains(loc)) {
            return false;
        }

        // 4. If admin zones are defined, check if inside any zone
        if (!zones.isEmpty()) {
            for (RestorableZone zone : zones.values()) {
                if (zone.world.equalsIgnoreCase(loc.getWorld().getName())) {
                    double distSq = Math.pow(zone.x - loc.getBlockX(), 2) + Math.pow(zone.z - loc.getBlockZ(), 2);
                    if (distSq <= Math.pow(zone.radius, 2)) {
                        return true;
                    }
                }
            }
            return false;
        }

        // 5. Default fallback: City overworld above minY
        String cityWorld = plugin.getConfig().getString("world.name", "world");
        return loc.getWorld().getName().equalsIgnoreCase(cityWorld);
    }

    /**
     * Track player-placed blocks to respect player builds.
     */
    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBlockPlace(BlockPlaceEvent e) {
        Location loc = e.getBlock().getLocation();
        playerPlacedBlocks.add(loc);
    }

    /**
     * Handle entity explosions (TNT, creeper, rockets, tanks).
     */
    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onEntityExplode(EntityExplodeEvent e) {
        handleExplosion(e.blockList(), e.getYield());
        // Set yield to 0 for restorable blocks to prevent item duplication exploits
        e.setYield(0.0f);
    }

    /**
     * Handle block explosions (respawn anchors, beds, custom bombs).
     */
    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onBlockExplode(BlockExplodeEvent e) {
        handleExplosion(e.blockList(), e.getYield());
        e.setYield(0.0f);
    }

    private void handleExplosion(List<Block> blocks, float originalYield) {
        long restoreAt = System.currentTimeMillis() + plugin.getConfig().getLong("restoration.delay-ms", DEFAULT_DELAY_MS);

        for (Block b : blocks) {
            if (b.getType().isAir()) continue;

            if (isRestorable(b)) {
                Location loc = b.getLocation();
                // Store block data if not already queued
                if (!pendingRestores.containsKey(loc)) {
                    pendingRestores.put(loc, new RestoreRecord(loc, b.getBlockData().clone(), restoreAt));
                }
            }
        }
    }

    /**
     * Handle block vandalism/break in city streets.
     */
    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onBlockBreak(BlockBreakEvent e) {
        Player p = e.getPlayer();
        Block b = e.getBlock();

        // If player has admin bypass in creative, don't queue auto-restore
        if (p.hasPermission("sdcraft.admin") && p.getGameMode() == GameMode.CREATIVE) {
            playerPlacedBlocks.remove(b.getLocation());
            pendingRestores.remove(b.getLocation());
            return;
        }

        if (isRestorable(b)) {
            Location loc = b.getLocation();
            long restoreAt = System.currentTimeMillis() + plugin.getConfig().getLong("restoration.delay-ms", DEFAULT_DELAY_MS);
            pendingRestores.put(loc, new RestoreRecord(loc, b.getBlockData().clone(), restoreAt));
            // Prevent drops to prevent duplication of city infrastructure
            e.setDropItems(false);
            e.setExpToDrop(0);
        } else {
            // Player breaking their own or mining block
            playerPlacedBlocks.remove(b.getLocation());
        }
    }

    /**
     * Tick loop called every second by main plugin timer.
     * Restores blocks whose 5-minute timer has expired, ordered bottom-to-top.
     */
    public void tick() {
        if (pendingRestores.isEmpty()) return;

        long now = System.currentTimeMillis();
        List<RestoreRecord> ready = new ArrayList<>();

        for (RestoreRecord rec : pendingRestores.values()) {
            if (now >= rec.restoreAt) {
                ready.add(rec);
            }
        }

        if (ready.isEmpty()) return;

        // Sort bottom-to-top (ascending Y) so foundations restore before hanging blocks
        ready.sort(Comparator.comparingInt(r -> r.location.getBlockY()));

        for (RestoreRecord rec : ready) {
            pendingRestores.remove(rec.location);
            restoreBlock(rec);
        }
    }

    /**
     * Force restores all currently pending blocks immediately (admin command).
     */
    public int forceRestoreAll() {
        int count = pendingRestores.size();
        List<RestoreRecord> all = new ArrayList<>(pendingRestores.values());
        all.sort(Comparator.comparingInt(r -> r.location.getBlockY()));

        for (RestoreRecord rec : all) {
            pendingRestores.remove(rec.location);
            restoreBlock(rec);
        }
        return count;
    }

    private void restoreBlock(RestoreRecord rec) {
        Block b = rec.location.getBlock();
        World w = rec.location.getWorld();
        if (w == null) return;

        // Apply original block data without physics update
        b.setBlockData(rec.blockData, false);

        // Visual and auditory restoration cue
        w.spawnParticle(Particle.SMOKE, rec.location.clone().add(0.5, 0.5, 0.5), 4, 0.2, 0.2, 0.2, 0.01);
        w.playSound(rec.location, Sound.BLOCK_STONE_PLACE, 0.4f, 1.2f);
    }
}
