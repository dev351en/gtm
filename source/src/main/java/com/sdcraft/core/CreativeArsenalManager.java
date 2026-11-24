package com.sdcraft.core;

import java.util.List;
import java.util.Locale;
import java.util.Map;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Sound;
import org.bukkit.World;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

/**
 * Creative Arsenal and Instant Developer Testing System for SDCraft.
 * Provides a 54-slot GUI for 1-click access to all MTVehicles, QualityArmory weapons,
 * ammunition, cash injections, fast city landmark teleports, and creative/godmode toggles.
 */
public final class CreativeArsenalManager {
    public static final String GUI_TITLE = "§6§lSD CRAFT §8- §eTesting Arsenal";

    private final SDCraftCorePlugin plugin;
    private final Ledger ledger;
    private final GpsManager gps;
    private final GtaEngine gta;
    private final GunEngine guns;

    public CreativeArsenalManager(SDCraftCorePlugin plugin, Ledger ledger, GpsManager gps, GtaEngine gta, GunEngine guns) {
        this.plugin = plugin;
        this.ledger = ledger;
        this.gps = gps;
        this.gta = gta;
        this.guns = guns;
    }

    private ItemStack item(Material mat, String name, String... lore) {
        ItemStack stack = new ItemStack(mat);
        ItemMeta meta = stack.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(name);
            meta.setLore(List.of(lore));
            stack.setItemMeta(meta);
        }
        return stack;
    }

    /**
     * Opens the 54-slot Testing Arsenal GUI for the specified player.
     */
    public void openArsenal(Player player) {
        Inventory inv = Bukkit.createInventory(null, 54, GUI_TITLE);

        // ROW 1: MTVehicles (Slots 0 - 8)
        inv.setItem(0, item(Material.MINECART, "§e§lSedan Black (Civic Car)",
                "§7MTVehicles ID: §fFFW36Q",
                "§8Everyday reliable city cruiser.",
                "§a▶ Click to receive vehicle keys!"));
        inv.setItem(1, item(Material.MINECART, "§c§lSportscar GT (Supercar)",
                "§7MTVehicles ID: §fW32FND",
                "§8High-speed racing supercar.",
                "§a▶ Click to receive vehicle keys!"));
        inv.setItem(2, item(Material.CHEST_MINECART, "§9§lPolice Cruiser (SDPD)",
                "§7MTVehicles ID: §fJSJ4ST",
                "§8Official law enforcement patrol car.",
                "§a▶ Click to receive vehicle keys!"));
        inv.setItem(3, item(Material.FURNACE_MINECART, "§9§lPolice SUV Interceptor",
                "§7MTVehicles ID: §fHVN8HB",
                "§8Heavy pursuit armored interceptor.",
                "§a▶ Click to receive vehicle keys!"));
        inv.setItem(4, item(Material.HOPPER_MINECART, "§b§lPolice Motorcycle (Highway)",
                "§7MTVehicles ID: §f384A4N",
                "§8Fast response traffic bike.",
                "§a▶ Click to receive vehicle keys!"));
        inv.setItem(5, item(Material.TNT_MINECART, "§4§lApache Military Helicopter",
                "§7MTVehicles ID: §fRJRN9P",
                "§8Aerial attack and transport chopper.",
                "§a▶ Click to receive vehicle keys!"));
        inv.setItem(6, item(Material.OAK_BOAT, "§3§lOcean Speedboat",
                "§7MTVehicles ID: §fPLV871",
                "§8High-performance nautical speedboat.",
                "§a▶ Click to receive vehicle keys!"));
        // Slot 7: 3D Jerry Can Model (cmd 900011)
        ItemStack fuelCan = CityItems.jerryCan();
        ItemMeta fuelMeta = fuelCan.getItemMeta();
        if (fuelMeta != null) {
            fuelMeta.setDisplayName("§6§lJerry Can (Fuel 100L)");
            fuelMeta.setLore(List.of(
                    "§7MTVehicles Fuel Supply",
                    "§8Refuels any vehicle to 100% capacity.",
                    "§a▶ Click to receive fuel can!"));
            fuelCan.setItemMeta(fuelMeta);
        }
        inv.setItem(7, fuelCan);

        // Slot 8: 3D Baseball Bat (cmd 900012)
        ItemStack bat = CityItems.baseballBat();
        ItemMeta batMeta = bat.getItemMeta();
        if (batMeta != null) {
            batMeta.setDisplayName("§e§lLouisville Ash Baseball Bat");
            batMeta.setLore(List.of(
                    "§7Street Defense Melee Weapon",
                    "§8Heavy bludgeoning sports bat.",
                    "§a▶ Click to receive baseball bat!"));
            bat.setItemMeta(batMeta);
        }
        inv.setItem(8, bat);

        // ROW 2: QualityArmory & 3D Firearms (Slots 9 - 17)
        ItemStack p30 = guns.createGun(GunEngine.GunType.PISTOL);
        ItemMeta p30Meta = p30.getItemMeta();
        if (p30Meta != null) {
            p30Meta.setDisplayName("§f§lP30 9mm Service Pistol");
            p30Meta.setLore(List.of(
                    "§7Standard 9x19mm Sidearm",
                    "§8Compact, accurate semi-automatic.",
                    "§a▶ Click to equip firearm!"));
            p30.setItemMeta(p30Meta);
        }
        inv.setItem(9, p30);

        inv.setItem(10, item(Material.STONE_HOE, "§7§lGlock 17 Tactical",
                "§7QualityArmory ID: §fglock",
                "§8Standard police and civilian firearm.",
                "§a▶ Click to equip firearm!"));
        inv.setItem(11, item(Material.GOLDEN_HOE, "§e§lDesert Eagle .50 Heavy",
                "§7QualityArmory ID: §fdeagle",
                "§8Massive stopping power handgun.",
                "§a▶ Click to equip firearm!"));

        ItemStack smg = guns.createGun(GunEngine.GunType.SMG);
        ItemMeta smgMeta = smg.getItemMeta();
        if (smgMeta != null) {
            smgMeta.setDisplayName("§b§lTactical Micro-SMG (MP5)");
            smgMeta.setLore(List.of(
                    "§7Rapid Close-Quarters SMG",
                    "§8High fire-rate 9mm spray.",
                    "§a▶ Click to equip firearm!"));
            smg.setItemMeta(smgMeta);
        }
        inv.setItem(12, smg);

        inv.setItem(13, item(Material.WOODEN_HOE, "§6§lAK-47 Assault Rifle",
                "§7QualityArmory ID: §fak47",
                "§8Rugged 7.62x39mm assault rifle.",
                "§a▶ Click to equip firearm!"));

        ItemStack m4 = guns.createGun(GunEngine.GunType.RIFLE);
        ItemMeta m4Meta = m4.getItemMeta();
        if (m4Meta != null) {
            m4Meta.setDisplayName("§9§lM4 Urban Assault Rifle");
            m4Meta.setLore(List.of(
                    "§7Tactical 5.56 NATO Carbine",
                    "§8High-damage military precision rifle.",
                    "§a▶ Click to equip firearm!"));
            m4.setItemMeta(m4Meta);
        }
        inv.setItem(14, m4);

        ItemStack shotgun = guns.createGun(GunEngine.GunType.SHOTGUN);
        ItemMeta shotgunMeta = shotgun.getItemMeta();
        if (shotgunMeta != null) {
            shotgunMeta.setDisplayName("§c§l12-Gauge Tactical Shotgun");
            shotgunMeta.setLore(List.of(
                    "§7Pump-Action Police Scattergun",
                    "§8Devastating close-range pellets.",
                    "§a▶ Click to equip firearm!"));
            shotgun.setItemMeta(shotgunMeta);
        }
        inv.setItem(15, shotgun);

        inv.setItem(16, item(Material.BOW, "§2§lAWP Sniper Rifle",
                "§7QualityArmory ID: §fawp",
                "§8Long-range precision bolt-action sniper.",
                "§a▶ Click to equip firearm!"));
        inv.setItem(17, item(Material.NETHERITE_HOE, "§4§lBarrett .50 Anti-Material",
                "§7QualityArmory ID: §fbarrett",
                "§8High-caliber anti-vehicle sniper rifle.",
                "§a▶ Click to equip firearm!"));

        // ROW 3: Ammunition Caches (Slots 18 - 26)
        inv.setItem(18, item(Material.IRON_NUGGET, "§f§l9mm Pistol Ammo (x64)",
                "§7Fits: P30, Glock, MP5",
                "§a▶ Click to receive 64 rounds!"));
        inv.setItem(19, item(Material.GOLD_NUGGET, "§e§l.50 AE Ammo (x64)",
                "§7Fits: Desert Eagle .50",
                "§a▶ Click to receive 64 rounds!"));
        inv.setItem(20, item(Material.ARROW, "§b§l5.56mm NATO Ammo (x64)",
                "§7Fits: M4A1 Carbine",
                "§a▶ Click to receive 64 rounds!"));
        inv.setItem(21, item(Material.FIREWORK_STAR, "§6§l7.62mm Rifle Ammo (x64)",
                "§7Fits: AK-47 Rifle",
                "§a▶ Click to receive 64 rounds!"));
        inv.setItem(22, item(Material.GUNPOWDER, "§c§l12-Gauge Buckshot (x64)",
                "§7Fits: Remington 870 Shotgun",
                "§a▶ Click to receive 64 shells!"));
        inv.setItem(23, item(Material.PRISMARINE_SHARD, "§2§l.338 Sniper Rounds (x64)",
                "§7Fits: AWP Precision Rifle",
                "§a▶ Click to receive 64 rounds!"));
        inv.setItem(24, item(Material.BLAZE_ROD, "§4§l.50 BMG Heavy Ammo (x64)",
                "§7Fits: Barrett .50 Cal",
                "§a▶ Click to receive 64 rounds!"));
        inv.setItem(25, item(Material.AMETHYST_SHARD, "§d§lFull Ammo Supply Crate",
                "§7Contains full 64 stacks of ALL ammo types.",
                "§a▶ Click to receive entire ammo box!"));
        inv.setItem(26, item(Material.NETHERITE_CHESTPLATE, "§9§lSWAT Heavy Kevlar Armor",
                "§7Level IV ballistic chestplate.",
                "§8Immunity to standard bullet trauma.",
                "§a▶ Click to equip armor!"));

        // ROW 4: Roleplay Gear, Economy & Kits (Slots 27 - 35)
        ItemStack cash = CityItems.cashIcon();
        ItemMeta cashMeta = cash.getItemMeta();
        if (cashMeta != null) {
            cashMeta.setDisplayName("§a§l$10,000 Cash Injection");
            cashMeta.setLore(List.of(
                    "§7Instant wallet credit for testing.",
                    "§8Transfers $10,000 directly to cash wallet.",
                    "§a▶ Click to add cash!"));
            cash.setItemMeta(cashMeta);
        }
        inv.setItem(27, cash);

        ItemStack atm = CityItems.atmCard();
        ItemMeta atmMeta = atm.getItemMeta();
        if (atmMeta != null) {
            atmMeta.setDisplayName("§2§l$1,000,000 Millionaire Wire (VIP Card)");
            atmMeta.setLore(List.of(
                    "§7Instant protected bank account deposit.",
                    "§8Deposits 1 Million into First National Bank.",
                    "§a▶ Click to wire transfer!"));
            atm.setItemMeta(atmMeta);
        }
        inv.setItem(28, atm);

        ItemStack phone = CityItems.phone();
        ItemMeta phoneMeta = phone.getItemMeta();
        if (phoneMeta != null) {
            phoneMeta.setDisplayName("§6§lSan Andreas City Smartphone");
            phoneMeta.setLore(List.of(
                    "§7City Services Phone (/phone)",
                    "§8Access banking, vehicle recovery, and police.",
                    "§a▶ Click to receive phone!"));
            phone.setItemMeta(phoneMeta);
        }
        inv.setItem(29, phone);

        inv.setItem(30, item(Material.COMPASS, "§b§lLive GPS Navigator",
                "§7GPS Waypoint System (/gps)",
                "§8Real-time district display and route compass.",
                "§a▶ Click to receive GPS!"));

        ItemStack medkit = CityItems.medkit();
        ItemMeta medkitMeta = medkit.getItemMeta();
        if (medkitMeta != null) {
            medkitMeta.setDisplayName("§c§lParamedic Trauma & Revive Kit");
            medkitMeta.setLore(List.of(
                    "§7Emergency Hospital Medical Kit",
                    "§8Restores full health and revives downed players.",
                    "§a▶ Click to receive medkit!"));
            medkit.setItemMeta(medkitMeta);
        }
        inv.setItem(31, medkit);

        ItemStack ticket = CityItems.metroTicket("Central Metro");
        ItemMeta ticketMeta = ticket.getItemMeta();
        if (ticketMeta != null) {
            ticketMeta.setDisplayName("§e§lTrainCarts Metro Unlimited Pass");
            ticketMeta.setLore(List.of(
                    "§7San Andreas Rail Pass",
                    "§8Unlimited travel across all subway lines.",
                    "§a▶ Click to receive metro ticket!"));
            ticket.setItemMeta(ticketMeta);
        }
        inv.setItem(32, ticket);

        ItemStack badge = CityItems.policeBadge();
        ItemMeta badgeMeta = badge.getItemMeta();
        if (badgeMeta != null) {
            badgeMeta.setDisplayName("§9§lSDPD Detective Badge & Gear");
            badgeMeta.setLore(List.of(
                    "§7Law Enforcement Identification & Restraints",
                    "§8San Diego Police Department",
                    "§a▶ Click to receive police kit!"));
            badge.setItemMeta(badgeMeta);
        }
        inv.setItem(33, badge);
        inv.setItem(34, item(Material.TRIPWIRE_HOOK, "§7§lCriminal Lockpick Kit",
                "§7Black Market Infiltration Tool",
                "§8Used for lockpicking and heist testing.",
                "§a▶ Click to receive lockpick!"));
        inv.setItem(35, item(Material.NETHER_STAR, "§e§lPardon: Clear Wanted Stars (0★)",
                "§7Immediate Legal Cleansing",
                "§8Resets criminal record and clears police pursuit.",
                "§a▶ Click to wipe wanted level!"));

        // ROW 5: Fast Landmark Teleports (Slots 36 - 44)
        inv.setItem(36, item(Material.BEACON, "§e§lTP: Civic Plaza (City Spawn)",
                "§7Coordinates: §f10.5, 70.0, 3.5",
                "§8City Hall, Welcome Hologram, Plaza",
                "§a▶ Click to teleport!"));
        inv.setItem(37, item(Material.BLUE_CONCRETE, "§9§lTP: Police Headquarters (SDPD)",
                "§7Coordinates: §f120.5, 66.0, -45.5",
                "§8Precinct 1, Armory, Booking Cells",
                "§a▶ Click to teleport!"));
        inv.setItem(38, item(Material.RED_CONCRETE, "§c§lTP: Mount Zonah Hospital",
                "§7Coordinates: §f-61.5, 65.0, 140.5",
                "§8Trauma Center, Medical Bay, Ambulance",
                "§a▶ Click to teleport!"));
        inv.setItem(39, item(Material.GOLD_BLOCK, "§6§lTP: First National Bank",
                "§7Coordinates: §f56.5, 68.0, -118.5",
                "§8Financial District, Vaults, ATMs",
                "§a▶ Click to teleport!"));
        inv.setItem(40, item(Material.YELLOW_CONCRETE, "§e§lTP: Motor Mile Dealership",
                "§7Coordinates: §f-150.5, 69.0, -82.5",
                "§8Showroom, Car Test Tracks, Mechanics",
                "§a▶ Click to teleport!"));
        inv.setItem(41, item(Material.LIGHT_BLUE_CONCRETE, "§b§lTP: Central Metro Station",
                "§7Coordinates: §f26.5, 68.0, 63.5",
                "§8High-Speed Rail, TrainCarts Hub",
                "§a▶ Click to teleport!"));
        inv.setItem(42, item(Material.ORANGE_CONCRETE, "§6§lTP: Highway Gas Station",
                "§7Coordinates: §f-204.5, 70.0, 60.5",
                "§8Refueling Station, Convenience Mart",
                "§a▶ Click to teleport!"));
        inv.setItem(43, item(Material.RED_TERRACOTTA, "§4§lTP: Fire Station 4",
                "§7Coordinates: §f190.5, 70.0, 86.5",
                "§8Fire Engines, Emergency Response",
                "§a▶ Click to teleport!"));
        inv.setItem(44, item(Material.PURPLE_CONCRETE, "§5§lTP: Airport Runway",
                "§7Coordinates: §f-350.0, 68.0, -200.0",
                "§8Wide open test runway for cars and aircraft",
                "§a▶ Click to teleport!"));

        // ROW 6: Creative Modes & World Controls (Slots 45 - 53)
        inv.setItem(45, item(Material.GRASS_BLOCK, "§a§lGamemode: CREATIVE",
                "§7Instant Creative Testing Mode",
                "§8Unlimited blocks, instant break, flight.",
                "§a▶ Click to switch mode!"));
        inv.setItem(46, item(Material.IRON_SWORD, "§c§lGamemode: SURVIVAL",
                "§7Standard Roleplay Survival Mode",
                "§8Standard damage, stamina and physics.",
                "§a▶ Click to switch mode!"));
        inv.setItem(47, item(Material.MAP, "§e§lGamemode: ADVENTURE",
                "§7Visitor Adventure Mode",
                "§8Interaction with doors and NPCs without block breaking.",
                "§a▶ Click to switch mode!"));
        inv.setItem(48, item(Material.ELYTRA, "§b§lFly & Godmode (Toggle)",
                "§7Toggles Flight & Invulnerability",
                "§8Enables flying speed and prevents damage.",
                "§a▶ Click to toggle fly!"));
        inv.setItem(49, item(Material.SUNFLOWER, "§e§lSet Time: Daylight Noon",
                "§7Clear City Sunlight",
                "§8Sets world time to 6000 ticks (Midday).",
                "§a▶ Click to set time!"));
        inv.setItem(50, item(Material.WATER_BUCKET, "§b§lWeather: Clear Skies",
                "§7Removes Rain & Thunderstorms",
                "§8Sets city weather to sunny and clear.",
                "§a▶ Click to clear weather!"));
        inv.setItem(51, item(Material.BOOKSHELF, "§d§lApply 3D Vehicles Pack (/pack)",
                "§7Download & Setup Instructions",
                "§8Shows resource pack link for 3D cars and weapons.",
                "§a▶ Click to send instructions!"));
        inv.setItem(52, item(Material.FILLED_MAP, "§3§lBlueMap Live 3D Web Map (/map)",
                "§7Real-Time City Browser Map",
                "§8Displays link to live web map with player markers.",
                "§a▶ Click to view web map link!"));
        inv.setItem(53, item(Material.BARRIER, "§c§lClose Arsenal",
                "§7Exit testing menu.",
                "§c▶ Click to close!"));

        player.openInventory(inv);
        player.playSound(player.getLocation(), Sound.BLOCK_CHEST_OPEN, 0.7f, 1.2f);
    }

    /**
     * Activates instant testing mode for a player: sets Creative mode, flight, godmode,
     * injects starter test funds, and opens the Arsenal GUI.
     */
    public void enableTestingMode(Player player) {
        player.setGameMode(GameMode.CREATIVE);
        player.setAllowFlight(true);
        player.setFlying(true);
        player.setInvulnerable(true);

        try {
            if (ledger.exists(player.getUniqueId())) {
                ledger.creditWallet(player.getUniqueId(), 1_000_000L, "testing mode initial cash");
            }
        } catch (Exception ignored) {}

        ItemStack star = item(Material.NETHER_STAR, "§6§lTesting Arsenal §7(Right-Click)",
                "§7Right-click anywhere to open the",
                "§754-slot Vehicles & Weapons menu.");
        giveItem(player, star);

        player.sendTitle("§6§lTESTING MODE", "§aCreative & Testing Arsenal Active", 10, 60, 20);
        player.playSound(player.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 0.8f, 1.2f);
        player.sendMessage("§8━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        player.sendMessage("§6§l[SD CRAFT] §aInstant Testing Mode Activated!");
        player.sendMessage("§f• Gamemode set to §eCREATIVE §fwith Flight & Godmode enabled.");
        player.sendMessage("§f• Added §a$10,000 §ftest funds to your wallet.");
        player.sendMessage("§f• Right-click the §6Testing Arsenal Star §for type §b/arsenal §fanytime!");
        player.sendMessage("§8━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        openArsenal(player);
    }

    /**
     * Handles inventory click events in the Arsenal GUI.
     * Returns true if the click was handled.
     */
    public boolean handleInventory(InventoryClickEvent e) {
        if (!(e.getWhoClicked() instanceof Player player)) return false;
        if (!e.getView().getTitle().equals(GUI_TITLE)) return false;

        e.setCancelled(true);
        int slot = e.getRawSlot();
        if (slot < 0 || slot >= 54) return true;

        String name = player.getName();
        World world = player.getWorld();

        switch (slot) {
            // MTVehicles
            case 0 -> giveVehicle(player, "FFW36Q", "Sedan Black");
            case 1 -> giveVehicle(player, "W32FND", "Sportscar GT");
            case 2 -> giveVehicle(player, "JSJ4ST", "Police Cruiser");
            case 3 -> giveVehicle(player, "HVN8HB", "Police SUV Interceptor");
            case 4 -> giveVehicle(player, "384A4N", "Police Motorcycle");
            case 5 -> giveVehicle(player, "RJRN9P", "Apache Military Helicopter");
            case 6 -> giveVehicle(player, "PLV871", "Ocean Speedboat");
            case 7 -> {
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mtv givefuel " + name + " 100");
                giveItem(player, CityItems.jerryCan());
                player.sendMessage("§a[Arsenal] §e100L Jerry Can fuel delivered!");
                player.playSound(player.getLocation(), Sound.ITEM_BOTTLE_FILL, 0.8f, 1.2f);
            }
            case 8 -> {
                giveItem(player, CityItems.baseballBat());
                player.sendMessage("§a[Arsenal] §eLouisville Baseball Bat equipped!");
                player.playSound(player.getLocation(), Sound.ENTITY_ITEM_PICKUP, 0.8f, 1.2f);
            }

            // QualityArmory Firearms & 3D Weapons
            case 9 -> giveGun(player, "p30", GunEngine.GunType.PISTOL, "P30 9mm Pistol");
            case 10 -> giveGun(player, "glock", GunEngine.GunType.PISTOL, "Glock 17 Tactical");
            case 11 -> giveGun(player, "deagle", GunEngine.GunType.PISTOL, "Desert Eagle .50");
            case 12 -> giveGun(player, "mp5", GunEngine.GunType.SMG, "Tactical Micro-SMG (MP5)");
            case 13 -> giveGun(player, "ak47", GunEngine.GunType.RIFLE, "AK-47 Assault Rifle");
            case 14 -> giveGun(player, "m4", GunEngine.GunType.RIFLE, "M4 Urban Assault Rifle");
            case 15 -> giveGun(player, "remington", GunEngine.GunType.SHOTGUN, "12-Gauge Tactical Shotgun");
            case 16 -> giveGun(player, "awp", GunEngine.GunType.RIFLE, "AWP Precision Sniper");
            case 17 -> giveGun(player, "barrett", GunEngine.GunType.RIFLE, "Barrett .50 Anti-Material");

            // Ammunition Caches
            case 18 -> giveAmmo(player, "9mm", "9mm_ammo", 64, "9mm Pistol Ammo");
            case 19 -> giveAmmo(player, "50ae", "50cal_ammo", 64, ".50 AE Heavy Ammo");
            case 20 -> giveAmmo(player, "556", "556_ammo", 64, "5.56mm NATO Ammo");
            case 21 -> giveAmmo(player, "762", "762_ammo", 64, "7.62mm Rifle Ammo");
            case 22 -> giveAmmo(player, "12gauge", "shotgun_ammo", 64, "12-Gauge Buckshot");
            case 23 -> giveAmmo(player, "338", "sniper_ammo", 64, ".338 Sniper Rounds");
            case 24 -> giveAmmo(player, "50bmg", "50bmg_ammo", 64, ".50 BMG Heavy Ammo");
            case 25 -> {
                giveAmmo(player, "9mm", "9mm_ammo", 64, "9mm");
                giveAmmo(player, "50ae", "50cal_ammo", 64, ".50 AE");
                giveAmmo(player, "556", "556_ammo", 64, "5.56 NATO");
                giveAmmo(player, "762", "762_ammo", 64, "7.62 Soviet");
                giveAmmo(player, "12gauge", "shotgun_ammo", 64, "12-Gauge");
                giveAmmo(player, "338", "sniper_ammo", 64, ".338 Lapua");
                giveAmmo(player, "50bmg", "50bmg_ammo", 64, ".50 BMG");
                player.sendMessage("§a[Arsenal] §dFull ammunition crate unpacked into inventory!");
                player.playSound(player.getLocation(), Sound.ITEM_ARMOR_EQUIP_CHAIN, 0.9f, 1.1f);
            }
            case 26 -> {
                ItemStack armor = item(Material.NETHERITE_CHESTPLATE, "§9§lSWAT Heavy Kevlar Armor",
                        "§7Ballistic Protection Level IV");
                player.getInventory().setChestplate(armor);
                player.sendMessage("§a[Arsenal] §9Heavy Kevlar SWAT Armor equipped!");
                player.playSound(player.getLocation(), Sound.ITEM_ARMOR_EQUIP_NETHERITE, 0.8f, 1.0f);
            }

            // Roleplay Gear, Economy & Kits
            case 27 -> {
                try {
                    ledger.creditWallet(player.getUniqueId(), 1_000_000L, "arsenal test funds");
                    giveItem(player, CityItems.cashIcon());
                    player.sendMessage("§a[Arsenal] §e$10,000 cash added to your wallet! (Balance: "
                            + PolicyEngine.money(ledger.wallet(player.getUniqueId())) + ")");
                    player.playSound(player.getLocation(), Sound.ENTITY_EXPERIENCE_ORB_PICKUP, 0.8f, 1.2f);
                } catch (Exception ex) {
                    player.sendMessage("§cError updating ledger: " + ex.getMessage());
                }
            }
            case 28 -> {
                try {
                    ledger.reward(player.getUniqueId(), 100_000_000L, "arsenal wire transfer");
                    giveItem(player, CityItems.atmCard());
                    player.sendMessage("§a[Arsenal] §2$1,000,000 wired to your First National Bank account & VIP Card issued!");
                    player.playSound(player.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 0.8f, 1.2f);
                } catch (Exception ex) {
                    player.sendMessage("§cError updating ledger: " + ex.getMessage());
                }
            }
            case 29 -> {
                giveItem(player, CityItems.phone());
                player.sendMessage("§a[Arsenal] §6San Andreas Smartphone equipped! Right-click to open.");
                player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.8f, 1.4f);
            }
            case 30 -> {
                giveItem(player, gps.createGpsItem());
                player.sendMessage("§a[Arsenal] §bGPS Navigator equipped! Right-click to view waypoints.");
                player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.8f, 1.4f);
            }
            case 31 -> {
                giveItem(player, CityItems.medkit());
                giveItem(player, new ItemStack(Material.ENCHANTED_GOLDEN_APPLE, 2));
                player.setHealth(player.getMaxHealth());
                player.sendMessage("§a[Arsenal] §cParamedic Trauma Medkit equipped & health fully restored!");
                player.playSound(player.getLocation(), Sound.ENTITY_PLAYER_LEVELUP, 0.7f, 1.5f);
            }
            case 32 -> {
                giveItem(player, CityItems.metroTicket("Central Metro"));
                player.sendMessage("§a[Arsenal] §eTrainCarts Metro All-Access Ticket received!");
                player.playSound(player.getLocation(), Sound.ENTITY_ITEM_PICKUP, 0.7f, 1.2f);
            }
            case 33 -> {
                giveItem(player, CityItems.policeBadge());
                giveItem(player, item(Material.LEAD, "§9§lPolice Restraints", "§7Detain criminal suspects."));
                player.sendMessage("§a[Arsenal] §9SDPD Badge & Police Restraints equipped!");
                player.playSound(player.getLocation(), Sound.ITEM_ARMOR_EQUIP_IRON, 0.7f, 1.2f);
            }
            case 34 -> {
                giveItem(player, item(Material.TRIPWIRE_HOOK, "§7§lCriminal Lockpick Kit", "§7Used for heist testing."));
                player.sendMessage("§a[Arsenal] §7Lockpick kit acquired.");
                player.playSound(player.getLocation(), Sound.BLOCK_CHEST_LOCKED, 0.7f, 1.2f);
            }
            case 35 -> {
                gta.clearWanted(player);
                player.sendMessage("§a[Arsenal] §ePardon issued! Wanted level wiped to 0★.");
                player.playSound(player.getLocation(), Sound.ENTITY_PLAYER_LEVELUP, 0.8f, 1.5f);
            }

            // Fast Teleports
            case 36 -> tp(player, new Location(world, 10.5, 70.0, 3.5, 0f, 0f), "Civic Plaza Spawn");
            case 37 -> tp(player, new Location(world, 120.5, 66.0, -45.5, 180f, 0f), "Police Headquarters (SDPD)");
            case 38 -> tp(player, new Location(world, -61.5, 65.0, 140.5, 270f, 0f), "Mount Zonah Hospital");
            case 39 -> tp(player, new Location(world, 56.5, 68.0, -118.5, 90f, 0f), "First National Bank");
            case 40 -> tp(player, new Location(world, -150.5, 69.0, -82.5, 180f, 0f), "Motor Mile Dealership");
            case 41 -> tp(player, new Location(world, 26.5, 68.0, 63.5, 0f, 0f), "Central Metro Station");
            case 42 -> tp(player, new Location(world, -204.5, 70.0, 60.5, 180f, 0f), "Highway Gas Station");
            case 43 -> tp(player, new Location(world, 190.5, 70.0, 86.5, 180f, 0f), "Fire & Rescue Station 4");
            case 44 -> tp(player, new Location(world, -350.0, 68.0, -200.0, 90f, 0f), "Airport Runway");

            // Creative Modes & World Controls
            case 45 -> {
                player.setGameMode(GameMode.CREATIVE);
                player.sendMessage("§a[Arsenal] §eGamemode set to §aCREATIVE§e. Build and explore freely!");
                player.playSound(player.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 0.7f, 1.2f);
            }
            case 46 -> {
                player.setGameMode(GameMode.SURVIVAL);
                player.sendMessage("§a[Arsenal] §eGamemode set to §cSURVIVAL§e. Roleplay damage active.");
                player.playSound(player.getLocation(), Sound.BLOCK_BEACON_DEACTIVATE, 0.7f, 1.2f);
            }
            case 47 -> {
                player.setGameMode(GameMode.ADVENTURE);
                player.sendMessage("§a[Arsenal] §eGamemode set to §bADVENTURE§e.");
                player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.7f, 1.2f);
            }
            case 48 -> {
                boolean fly = !player.getAllowFlight();
                player.setAllowFlight(fly);
                player.setFlying(fly);
                player.setInvulnerable(fly);
                player.sendMessage("§a[Arsenal] §eFlight & Invulnerability: " + (fly ? "§aENABLED" : "§cDISABLED"));
                player.playSound(player.getLocation(), Sound.ENTITY_ILLUSIONER_PREPARE_MIRROR, 0.7f, 1.4f);
            }
            case 49 -> {
                world.setTime(6000L);
                player.sendMessage("§a[Arsenal] §eWorld time set to Daylight Noon (6000 ticks).");
                player.playSound(player.getLocation(), Sound.ITEM_FLINTANDSTEEL_USE, 0.8f, 1.2f);
            }
            case 50 -> {
                world.setClearWeatherDuration(12000);
                player.sendMessage("§a[Arsenal] §eWeather cleared to sunny skies.");
                player.playSound(player.getLocation(), Sound.ITEM_BUCKET_EMPTY, 0.8f, 1.2f);
            }
            case 51 -> {
                player.closeInventory();
                player.performCommand("pack");
            }
            case 52 -> {
                player.closeInventory();
                player.performCommand("map");
            }
            case 53 -> {
                player.closeInventory();
            }
        }
        return true;
    }

    private void giveVehicle(Player player, String uuid, String vehicleName) {
        if (Bukkit.getPluginManager().isPluginEnabled("MTVehicles")) {
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mtv givecar " + player.getName() + " " + uuid);
            giveItem(player, CityItems.carKeyFob(vehicleName));
            player.sendMessage("§a[Arsenal] §eKeys to your §6" + vehicleName + " §edelivered! Right-click road to place.");
        } else {
            giveItem(player, CityItems.carKeyFob(vehicleName));
            player.sendMessage("§e[Arsenal] Key Fob delivered for " + vehicleName + ".");
        }
        player.playSound(player.getLocation(), Sound.ENTITY_ITEM_PICKUP, 0.8f, 1.2f);
    }

    private void giveGun(Player player, String qaId, GunEngine.GunType fallbackType, String gunName) {
        if (fallbackType != null) {
            giveItem(player, guns.createGun(fallbackType));
            giveItem(player, guns.createAmmo(fallbackType.ammoType, fallbackType.maxAmmo * 2));
            player.sendMessage("§a[Arsenal] §eEquipped §6" + gunName + " §e(3D Custom Weapon).");
        } else if (Bukkit.getPluginManager().isPluginEnabled("QualityArmory")) {
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "qa give " + qaId + " " + player.getName());
            player.sendMessage("§a[Arsenal] §eEquipped §6" + gunName + " §e(QualityArmory).");
        }
        player.playSound(player.getLocation(), Sound.ITEM_ARMOR_EQUIP_IRON, 0.8f, 1.2f);
    }

    private void giveAmmo(Player player, String qaId, String fallbackId, int amount, String ammoName) {
        if (Bukkit.getPluginManager().isPluginEnabled("QualityArmory")) {
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "qa give " + qaId + " " + player.getName() + " " + amount);
        } else {
            giveItem(player, guns.createAmmo(fallbackId, amount));
        }
        player.sendMessage("§a[Arsenal] §eReceived §f" + amount + " rounds §eof §6" + ammoName + "§e.");
        player.playSound(player.getLocation(), Sound.ITEM_ARMOR_EQUIP_GENERIC, 0.7f, 1.4f);
    }

    private void giveItem(Player player, ItemStack item) {
        Map<Integer, ItemStack> leftover = player.getInventory().addItem(item);
        if (!leftover.isEmpty()) {
            for (ItemStack rem : leftover.values()) {
                player.getWorld().dropItem(player.getLocation(), rem);
            }
        }
    }

    private void tp(Player player, Location target, String locationName) {
        Location ground = target.clone();
        if (ground.getWorld() == null) ground.setWorld(player.getWorld());
        player.teleport(ground);
        player.sendTitle("§6§l" + locationName, "§eFast Landmark Teleport", 5, 40, 10);
        player.playSound(ground, Sound.ENTITY_ENDERMAN_TELEPORT, 0.8f, 1.2f);
        player.sendMessage("§a[Arsenal] §eTeleported to §6" + locationName + " §7("
                + ground.getBlockX() + ", " + ground.getBlockY() + ", " + ground.getBlockZ() + ")§e.");
    }
}
