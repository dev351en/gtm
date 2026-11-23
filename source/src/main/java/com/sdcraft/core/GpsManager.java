package com.sdcraft.core;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Player;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.ItemMeta;

/**
 * GTA-style Real-Time GPS & Map Navigator for SD Craft.
 * Supports interactive GUI waypoint tracking, district detection,
 * compass target routing, and BlueMap 3D web map integration.
 */
public final class GpsManager {
    public static final String GUI_TITLE = "§8[GTA GPS] City Navigation";
    private final SDCraftCorePlugin plugin;

    public record Waypoint(String id, String name, Material icon, int slot, int x, int y, int z, String district, String description) {}

    private final Map<String, Waypoint> waypoints = new LinkedHashMap<>();

    public GpsManager(SDCraftCorePlugin plugin) {
        this.plugin = plugin;
        registerDefaultWaypoints();
    }

    private void registerDefaultWaypoints() {
        // Standard New Blockston v1.10 Key Landmark Coordinates
        addWaypoint(new Waypoint("police", "§c🚨 Police Headquarters", Material.IRON_BARS, 10, 120, 68, -45, "Downtown", "SDPD Central Station & Booking"));
        addWaypoint(new Waypoint("hospital", "§a🏥 City General Hospital", Material.GLISTERING_MELON_SLICE, 11, -85, 68, 140, "Westside", "Emergency Room & Trauma Center"));
        addWaypoint(new Waypoint("city_hall", "§6🏛️ City Hall & Licensing", Material.BOOK, 12, 10, 70, 15, "Civic Center", "Municipal Services & Records"));
        addWaypoint(new Waypoint("bank", "§e🏦 Central Bank & ATMs", Material.GOLD_BLOCK, 13, 60, 69, -110, "Financial District", "Secure Vaults & Banking Services"));
        addWaypoint(new Waypoint("fire", "§4🚒 Central Fire Station", Material.CAMPFIRE, 14, 190, 68, 80, "Midtown", "Fire & Rescue Operations"));
        addWaypoint(new Waypoint("dealership", "§b🚗 Vehicle Dealership & Garage", Material.MINECART, 15, -150, 68, -80, "Motor Mile", "MTVehicles Spawning & Customization"));
        addWaypoint(new Waypoint("gas_station", "§e⛽ Gas Station & Workshop", Material.HOPPER, 16, -220, 68, 60, "East Boulevard", "Vehicle Refueling & Repairs"));
        addWaypoint(new Waypoint("airport", "§9✈️ Blockston International Airport", Material.RECOVERY_COMPASS, 22, -380, 65, -310, "South Terminal", "Helipads & Transit Terminal"));
    }

    private void addWaypoint(Waypoint wp) {
        waypoints.put(wp.id, wp);
    }

    public Waypoint getWaypoint(String id) {
        return waypoints.get(id);
    }

    public Collection<Waypoint> getWaypoints() {
        return Collections.unmodifiableCollection(waypoints.values());
    }

    public void openGpsMenu(Player p) {
        Inventory inv = Bukkit.createInventory(null, 27, GUI_TITLE);

        // Fill background with dark stained glass
        ItemStack filler = new ItemStack(Material.GRAY_STAINED_GLASS_PANE);
        ItemMeta fMeta = filler.getItemMeta();
        if (fMeta != null) {
            fMeta.setDisplayName(" ");
            filler.setItemMeta(fMeta);
        }
        for (int i = 0; i < 27; i++) {
            inv.setItem(i, filler);
        }

        Location pLoc = p.getLocation();
        for (Waypoint wp : waypoints.values()) {
            Location dest = resolveLocation(p.getWorld(), wp);
            int distance = (int) Math.round(pLoc.distance(dest));
            String direction = getDirection(pLoc, dest);

            ItemStack item = new ItemStack(wp.icon);
            ItemMeta meta = item.getItemMeta();
            if (meta != null) {
                meta.setDisplayName(wp.name);
                meta.setLore(List.of(
                    "§7District: §b" + wp.district,
                    "§7Details: §f" + wp.description,
                    "§7Distance: §e" + distance + "m §8(" + direction + ")",
                    " ",
                    "§a➤ Click to set Compass GPS waypoint!"
                ));
                item.setItemMeta(meta);
            }
            inv.setItem(wp.slot, item);
        }

        // Live Web Map Button (Slot 4)
        ItemStack mapButton = new ItemStack(Material.MAP);
        ItemMeta mMeta = mapButton.getItemMeta();
        if (mMeta != null) {
            mMeta.setDisplayName("§6🌐 Open Live Real-Time 3D Web Map");
            mMeta.setLore(List.of(
                "§7Port: §f8100",
                "§7View all live player positions in 3D/2D!",
                " ",
                "§e➤ Click to receive clickable browser link in chat."
            ));
            mapButton.setItemMeta(mMeta);
        }
        inv.setItem(4, mapButton);

        p.openInventory(inv);
        p.playSound(p.getLocation(), Sound.UI_BUTTON_CLICK, 0.8f, 1.2f);
    }

    public Location resolveLocation(World world, Waypoint wp) {
        // If an admin calibrated a real site location via /sdc setsite, prioritize that
        Location site = plugin.site(wp.id);
        if (site != null && site.getWorld() != null && site.getWorld().equals(world)) {
            return site;
        }
        return new Location(world, wp.x, wp.y, wp.z);
    }

    public boolean handleClick(Player p, ItemStack clicked) {
        if (clicked == null || !clicked.hasItemMeta() || !clicked.getItemMeta().hasDisplayName()) {
            return false;
        }
        String name = clicked.getItemMeta().getDisplayName();

        if (name.contains("Open Live Real-Time 3D Web Map")) {
            p.closeInventory();
            sendMapPrompt(p);
            return true;
        }

        for (Waypoint wp : waypoints.values()) {
            if (name.equals(wp.name)) {
                Location target = resolveLocation(p.getWorld(), wp);
                p.setCompassTarget(target);
                int dist = (int) Math.round(p.getLocation().distance(target));
                String dir = getDirection(p.getLocation(), target);

                p.closeInventory();
                p.playSound(p.getLocation(), Sound.ENTITY_EXPERIENCE_ORB_PICKUP, 1.0f, 1.0f);
                p.sendMessage("§6[GPS Waypoint Set] " + wp.name + " §7(§e" + dist + "m " + dir + "§7 in " + wp.district + ")");
                p.sendActionBar(net.kyori.adventure.text.Component.text("§6[GPS Navigator] §e" + wp.name + " §7- §b" + dist + "m " + dir));
                return true;
            }
        }
        return false;
    }

    public void sendMapPrompt(Player p) {
        String webUrl = plugin.getConfig().getString("map.web-url", "http://localhost:8100");
        Location loc = p.getLocation();
        String district = getDistrict(loc);

        p.sendMessage("§e================ §6[ SD CRAFT GTA LIVE MAP ] §e================");
        p.sendMessage("§7Current District: §b" + district + " §7| Location: §fX: " + loc.getBlockX() + ", Y: " + loc.getBlockY() + ", Z: " + loc.getBlockZ());
        p.sendMessage("§a➤ Real-Time 3D Web Map: §n" + webUrl + "§r");
        p.sendMessage("§7(Click URL or open in browser to view live player markers and 3D city streets)");
        p.sendMessage("§7Minimap Key: If running Lunar, Badlion, or Xaero's WorldMap, press §e[M]§7 anytime!");
        p.sendMessage("§7Navigation: Type §e/gps§7 or right-click your GPS Compass for turn-by-turn waypoints.");
        p.sendMessage("§e============================================================");
        p.playSound(p.getLocation(), Sound.BLOCK_NOTE_BLOCK_PLING, 1.0f, 1.5f);
    }

    public String getDistrict(Location loc) {
        int x = loc.getBlockX();
        int z = loc.getBlockZ();

        if (x >= 50 && x <= 200 && z >= -100 && z <= 50) return "Downtown City Center";
        if (x >= -50 && x < 50 && z >= -50 && z <= 50) return "Civic Center";
        if (x >= 30 && x <= 150 && z < -100 && z >= -250) return "Financial District";
        if (x >= -250 && x < -100 && z >= -100 && z <= 50) return "Motor Mile & Industrial";
        if (x >= -200 && x < -50 && z > 50 && z <= 250) return "Westside Residential";
        if (x >= 150 && x <= 350 && z > 50 && z <= 250) return "Midtown District";
        if (x <= -250 && z <= -150) return "Airport International Zone";
        if (x < -180 && z >= 50 && z <= 300) return "East Commercial Boulevard";
        return "New Blockston Metro";
    }

    public String getDirection(Location from, Location to) {
        double dx = to.getX() - from.getX();
        double dz = to.getZ() - from.getZ();
        double angle = Math.toDegrees(Math.atan2(dx, -dz));
        if (angle < 0) angle += 360.0;

        if (angle >= 337.5 || angle < 22.5) return "North";
        if (angle >= 22.5 && angle < 67.5) return "North-East";
        if (angle >= 67.5 && angle < 112.5) return "East";
        if (angle >= 112.5 && angle < 157.5) return "South-East";
        if (angle >= 157.5 && angle < 202.5) return "South";
        if (angle >= 202.5 && angle < 247.5) return "South-West";
        if (angle >= 247.5 && angle < 292.5) return "West";
        return "North-West";
    }

    public ItemStack createGpsItem() {
        ItemStack item = new ItemStack(Material.COMPASS);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName("§6SD Craft GPS Navigator");
            meta.setLore(List.of(
                "§7Official city navigation device.",
                "§eRight-Click: §fOpen City Navigation Menu",
                "§ePress [F]: §fShow live district and coordinates",
                "§ePress [M]: §fOpen full map (if using minimap mod)",
                "§7Type §b/map§7 for real-time 3D web map"
            ));
            item.setItemMeta(meta);
        }
        return item;
    }
}
