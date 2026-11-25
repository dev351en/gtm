/* Reconstructed from preserved 1.0.3 runtime; native firearms and matching ammunition replace legacy QA menu grants. */
package com.sdcraft.core;

import com.sdcraft.core.CityItems;
import com.sdcraft.core.GpsManager;
import com.sdcraft.core.GtaEngine;
import com.sdcraft.core.GunEngine;
import com.sdcraft.core.Ledger;
import com.sdcraft.core.PolicyEngine;
import com.sdcraft.core.SDCraftCorePlugin;
import java.util.Map;
import java.util.ArrayList;
import com.sdcraft.core.equipment.EquipmentCatalog;
import java.util.List;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Sound;
import org.bukkit.World;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.HumanEntity;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

public final class CreativeArsenalManager {
    public static final String GUI_TITLE = "\u00a76\u00a7lSD CRAFT \u00a78- \u00a7eTesting Arsenal";
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

    private ItemStack item(Material mat, String name, String ... lore) {
        ItemStack stack = new ItemStack(mat);
        ItemMeta meta = stack.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(name);
            meta.setLore(List.of(lore));
            stack.setItemMeta(meta);
        }
        return stack;
    }

    public void openArsenal(Player player) {
        if (!this.plugin.isAuthenticated(player) || !player.hasPermission("sdcraft.admin")) return;
        Inventory inv = Bukkit.createInventory(null, (int)54, (String)GUI_TITLE);
        inv.setItem(0, this.item(Material.MINECART, "\u00a7e\u00a7lSedan Black (Civic Car)", "\u00a77MTVehicles ID: \u00a7fFFW36Q", "\u00a78Everyday reliable city cruiser.", "\u00a7a\u25b6 Click to receive vehicle keys!"));
        inv.setItem(1, this.item(Material.MINECART, "\u00a7c\u00a7lSportscar GT (Supercar)", "\u00a77MTVehicles ID: \u00a7fW32FND", "\u00a78High-speed racing supercar.", "\u00a7a\u25b6 Click to receive vehicle keys!"));
        inv.setItem(2, this.item(Material.CHEST_MINECART, "\u00a79\u00a7lPolice Cruiser (SDPD)", "\u00a77MTVehicles ID: \u00a7fJSJ4ST", "\u00a78Official law enforcement patrol car.", "\u00a7a\u25b6 Click to receive vehicle keys!"));
        inv.setItem(3, this.item(Material.FURNACE_MINECART, "\u00a79\u00a7lPolice SUV Interceptor", "\u00a77MTVehicles ID: \u00a7fHVN8HB", "\u00a78Heavy pursuit armored interceptor.", "\u00a7a\u25b6 Click to receive vehicle keys!"));
        inv.setItem(4, this.item(Material.HOPPER_MINECART, "\u00a7b\u00a7lPolice Motorcycle (Highway)", "\u00a77MTVehicles ID: \u00a7f384A4N", "\u00a78Fast response traffic bike.", "\u00a7a\u25b6 Click to receive vehicle keys!"));
        inv.setItem(5, this.item(Material.TNT_MINECART, "\u00a74\u00a7lApache Military Helicopter", "\u00a77MTVehicles ID: \u00a7fRJRN9P", "\u00a78Aerial attack and transport chopper.", "\u00a7a\u25b6 Click to receive vehicle keys!"));
        inv.setItem(6, this.item(Material.OAK_BOAT, "\u00a73\u00a7lOcean Speedboat", "\u00a77MTVehicles ID: \u00a7fPLV871", "\u00a78High-performance nautical speedboat.", "\u00a7a\u25b6 Click to receive vehicle keys!"));
        ItemStack fuelCan = CityItems.jerryCan();
        ItemMeta fuelMeta = fuelCan.getItemMeta();
        if (fuelMeta != null) {
            fuelMeta.setDisplayName("\u00a76\u00a7lJerry Can (Fuel 100L)");
            fuelMeta.setLore(List.of("\u00a77MTVehicles Fuel Supply", "\u00a78Refuels any vehicle to 100% capacity.", "\u00a7a\u25b6 Click to receive fuel can!"));
            fuelCan.setItemMeta(fuelMeta);
        }
        inv.setItem(7, fuelCan);
        ItemStack bat = CityItems.baseballBat();
        ItemMeta batMeta = bat.getItemMeta();
        if (batMeta != null) {
            batMeta.setDisplayName("\u00a7e\u00a7lLouisville Ash Baseball Bat");
            batMeta.setLore(List.of("\u00a77Street Defense Melee Weapon", "\u00a78Heavy bludgeoning sports bat.", "\u00a7a\u25b6 Click to receive baseball bat!"));
            bat.setItemMeta(batMeta);
        }
        inv.setItem(8, bat);
        String[] nativeIds = {"kavach_9", "deccan_compact", "rajput_45", "viper_sub", "trishul_ar", "indrayani_carbine", "sher_pump", "brahmos_precision", "vajra_heavy"};
        GunEngine.GunType[] fallback = {GunEngine.GunType.PISTOL, GunEngine.GunType.PISTOL, GunEngine.GunType.PISTOL,
                GunEngine.GunType.SMG, GunEngine.GunType.RIFLE, GunEngine.GunType.RIFLE,
                GunEngine.GunType.SHOTGUN, GunEngine.GunType.RIFLE, GunEngine.GunType.RIFLE};
        for (int i = 0; i < nativeIds.length; i++) {
            ItemStack preview = this.nativeGun(player, "gtm:" + nativeIds[i], fallback[i]);
            preview.editMeta(meta -> {
                var lore = new ArrayList<String>(meta.getLore() == null ? List.of() : meta.getLore());
                lore.add("\u00a7aClick to receive this working firearm and matching ammunition");
                meta.setLore(lore);
            });
            inv.setItem(9 + i, preview);
        }
        inv.setItem(18, this.guns.createAmmo("9mm_ammo", 64));
        inv.setItem(19, this.guns.createAmmo("9mm_ammo", 64));
        inv.setItem(20, this.guns.createAmmo("rifle_ammo", 64));
        inv.setItem(21, this.guns.createAmmo("rifle_ammo", 64));
        inv.setItem(22, this.guns.createAmmo("shotgun_shells", 64));
        inv.setItem(23, this.guns.createAmmo("rifle_ammo", 64));
        inv.setItem(24, this.guns.createAmmo("rifle_ammo", 64));
        inv.setItem(25, this.item(Material.AMETHYST_SHARD, "\u00a7dFull native ammunition crate",
                "\u00a77Includes sidearm, scatter and rifle ammunition", "\u00a7aClick to receive"));
        inv.setItem(26, this.item(Material.NETHERITE_CHESTPLATE, "\u00a79\u00a7lSWAT Heavy Kevlar Armor", "\u00a77Level IV ballistic chestplate.", "\u00a78Immunity to standard bullet trauma.", "\u00a7a\u25b6 Click to equip armor!"));
        ItemStack cash = CityItems.cashIcon();
        ItemMeta cashMeta = cash.getItemMeta();
        if (cashMeta != null) {
            cashMeta.setDisplayName("\u00a7a\u00a7l$10,000 Cash Injection");
            cashMeta.setLore(List.of("\u00a77Instant wallet credit for testing.", "\u00a78Transfers $10,000 directly to cash wallet.", "\u00a7a\u25b6 Click to add cash!"));
            cash.setItemMeta(cashMeta);
        }
        inv.setItem(27, cash);
        ItemStack atm = CityItems.atmCard();
        ItemMeta atmMeta = atm.getItemMeta();
        if (atmMeta != null) {
            atmMeta.setDisplayName("\u00a72\u00a7l$1,000,000 Millionaire Wire (VIP Card)");
            atmMeta.setLore(List.of("\u00a77Instant protected bank account deposit.", "\u00a78Deposits 1 Million into First National Bank.", "\u00a7a\u25b6 Click to wire transfer!"));
            atm.setItemMeta(atmMeta);
        }
        inv.setItem(28, atm);
        ItemStack phone = CityItems.phone();
        ItemMeta phoneMeta = phone.getItemMeta();
        if (phoneMeta != null) {
            phoneMeta.setDisplayName("\u00a76\u00a7lSan Andreas City Smartphone");
            phoneMeta.setLore(List.of("\u00a77City Services Phone (/phone)", "\u00a78Access banking, vehicle recovery, and police.", "\u00a7a\u25b6 Click to receive phone!"));
            phone.setItemMeta(phoneMeta);
        }
        inv.setItem(29, phone);
        inv.setItem(30, this.item(Material.COMPASS, "\u00a7b\u00a7lLive GPS Navigator", "\u00a77GPS Waypoint System (/gps)", "\u00a78Real-time district display and route compass.", "\u00a7a\u25b6 Click to receive GPS!"));
        ItemStack medkit = CityItems.medkit();
        ItemMeta medkitMeta = medkit.getItemMeta();
        if (medkitMeta != null) {
            medkitMeta.setDisplayName("\u00a7c\u00a7lParamedic Trauma & Revive Kit");
            medkitMeta.setLore(List.of("\u00a77Emergency Hospital Medical Kit", "\u00a78Restores full health and revives downed players.", "\u00a7a\u25b6 Click to receive medkit!"));
            medkit.setItemMeta(medkitMeta);
        }
        inv.setItem(31, medkit);
        ItemStack ticket = CityItems.metroTicket("Central Metro");
        ItemMeta ticketMeta = ticket.getItemMeta();
        if (ticketMeta != null) {
            ticketMeta.setDisplayName("\u00a7e\u00a7lTrainCarts Metro Unlimited Pass");
            ticketMeta.setLore(List.of("\u00a77San Andreas Rail Pass", "\u00a78Unlimited travel across all subway lines.", "\u00a7a\u25b6 Click to receive metro ticket!"));
            ticket.setItemMeta(ticketMeta);
        }
        inv.setItem(32, ticket);
        ItemStack badge = CityItems.policeBadge();
        ItemMeta badgeMeta = badge.getItemMeta();
        if (badgeMeta != null) {
            badgeMeta.setDisplayName("\u00a79\u00a7lSDPD Detective Badge & Gear");
            badgeMeta.setLore(List.of("\u00a77Law Enforcement Identification & Restraints", "\u00a78San Diego Police Department", "\u00a7a\u25b6 Click to receive police kit!"));
            badge.setItemMeta(badgeMeta);
        }
        inv.setItem(33, badge);
        inv.setItem(34, this.item(Material.TRIPWIRE_HOOK, "\u00a77\u00a7lCriminal Lockpick Kit", "\u00a77Black Market Infiltration Tool", "\u00a78Used for lockpicking and heist testing.", "\u00a7a\u25b6 Click to receive lockpick!"));
        inv.setItem(35, this.item(Material.NETHER_STAR, "\u00a7e\u00a7lPardon: Clear Wanted Stars (0\u2605)", "\u00a77Immediate Legal Cleansing", "\u00a78Resets criminal record and clears police pursuit.", "\u00a7a\u25b6 Click to wipe wanted level!"));
        inv.setItem(36, this.item(Material.BEACON, "\u00a7e\u00a7lTP: Civic Plaza (City Spawn)", "\u00a77Coordinates: \u00a7f10.5, 70.0, 3.5", "\u00a78City Hall, Welcome Hologram, Plaza", "\u00a7a\u25b6 Click to teleport!"));
        inv.setItem(37, this.item(Material.BLUE_CONCRETE, "\u00a79\u00a7lTP: Police Headquarters (SDPD)", "\u00a77Coordinates: \u00a7f120.5, 66.0, -45.5", "\u00a78Precinct 1, Armory, Booking Cells", "\u00a7a\u25b6 Click to teleport!"));
        inv.setItem(38, this.item(Material.RED_CONCRETE, "\u00a7c\u00a7lTP: Mount Zonah Hospital", "\u00a77Coordinates: \u00a7f-61.5, 65.0, 140.5", "\u00a78Trauma Center, Medical Bay, Ambulance", "\u00a7a\u25b6 Click to teleport!"));
        inv.setItem(39, this.item(Material.GOLD_BLOCK, "\u00a76\u00a7lTP: First National Bank", "\u00a77Coordinates: \u00a7f56.5, 68.0, -118.5", "\u00a78Financial District, Vaults, ATMs", "\u00a7a\u25b6 Click to teleport!"));
        inv.setItem(40, this.item(Material.YELLOW_CONCRETE, "\u00a7e\u00a7lTP: Motor Mile Dealership", "\u00a77Coordinates: \u00a7f-150.5, 69.0, -82.5", "\u00a78Showroom, Car Test Tracks, Mechanics", "\u00a7a\u25b6 Click to teleport!"));
        inv.setItem(41, this.item(Material.LIGHT_BLUE_CONCRETE, "\u00a7b\u00a7lTP: Central Metro Station", "\u00a77Coordinates: \u00a7f26.5, 68.0, 63.5", "\u00a78High-Speed Rail, TrainCarts Hub", "\u00a7a\u25b6 Click to teleport!"));
        inv.setItem(42, this.item(Material.ORANGE_CONCRETE, "\u00a76\u00a7lTP: Highway Gas Station", "\u00a77Coordinates: \u00a7f-204.5, 70.0, 60.5", "\u00a78Refueling Station, Convenience Mart", "\u00a7a\u25b6 Click to teleport!"));
        inv.setItem(43, this.item(Material.RED_TERRACOTTA, "\u00a74\u00a7lTP: Fire Station 4", "\u00a77Coordinates: \u00a7f190.5, 70.0, 86.5", "\u00a78Fire Engines, Emergency Response", "\u00a7a\u25b6 Click to teleport!"));
        inv.setItem(44, this.item(Material.PURPLE_CONCRETE, "\u00a75\u00a7lTP: Airport Runway", "\u00a77Coordinates: \u00a7f-350.0, 68.0, -200.0", "\u00a78Wide open test runway for cars and aircraft", "\u00a7a\u25b6 Click to teleport!"));
        inv.setItem(45, this.item(Material.GRASS_BLOCK, "\u00a7a\u00a7lGamemode: CREATIVE", "\u00a77Instant Creative Testing Mode", "\u00a78Unlimited blocks, instant break, flight.", "\u00a7a\u25b6 Click to switch mode!"));
        inv.setItem(46, this.item(Material.IRON_SWORD, "\u00a7c\u00a7lGamemode: SURVIVAL", "\u00a77Standard Roleplay Survival Mode", "\u00a78Standard damage, stamina and physics.", "\u00a7a\u25b6 Click to switch mode!"));
        inv.setItem(47, this.item(Material.MAP, "\u00a7e\u00a7lGamemode: ADVENTURE", "\u00a77Visitor Adventure Mode", "\u00a78Interaction with doors and NPCs without block breaking.", "\u00a7a\u25b6 Click to switch mode!"));
        inv.setItem(48, this.item(Material.ELYTRA, "\u00a7b\u00a7lFly & Godmode (Toggle)", "\u00a77Toggles Flight & Invulnerability", "\u00a78Enables flying speed and prevents damage.", "\u00a7a\u25b6 Click to toggle fly!"));
        inv.setItem(49, this.item(Material.SUNFLOWER, "\u00a7e\u00a7lSet Time: Daylight Noon", "\u00a77Clear City Sunlight", "\u00a78Sets world time to 6000 ticks (Midday).", "\u00a7a\u25b6 Click to set time!"));
        inv.setItem(50, this.item(Material.WATER_BUCKET, "\u00a7b\u00a7lWeather: Clear Skies", "\u00a77Removes Rain & Thunderstorms", "\u00a78Sets city weather to sunny and clear.", "\u00a7a\u25b6 Click to clear weather!"));
        inv.setItem(51, this.item(Material.BOOKSHELF, "\u00a7d\u00a7lApply 3D Vehicles Pack (/pack)", "\u00a77Download & Setup Instructions", "\u00a78Shows resource pack link for 3D cars and weapons.", "\u00a7a\u25b6 Click to send instructions!"));
        inv.setItem(52, this.item(Material.FILLED_MAP, "\u00a73\u00a7lBlueMap Live 3D Web Map (/map)", "\u00a77Real-Time City Browser Map", "\u00a78Displays link to live web map with player markers.", "\u00a7a\u25b6 Click to view web map link!"));
        inv.setItem(53, this.item(Material.BARRIER, "\u00a7c\u00a7lClose Arsenal", "\u00a77Exit testing menu.", "\u00a7c\u25b6 Click to close!"));
        player.openInventory(inv);
        player.playSound(player.getLocation(), Sound.BLOCK_CHEST_OPEN, 0.7f, 1.2f);
    }

    public void enableTestingMode(Player player) {
        if (!this.plugin.isAuthenticated(player) || !player.hasPermission("sdcraft.admin")) return;
        player.setGameMode(GameMode.CREATIVE);
        player.setAllowFlight(true);
        player.setFlying(true);
        player.setInvulnerable(true);
        try {
            if (this.ledger.exists(player.getUniqueId())) {
                this.ledger.creditWallet(player.getUniqueId(), 1000000L, "testing mode initial cash");
            }
        }
        catch (Exception exception) {
            // empty catch block
        }
        ItemStack star = this.item(Material.NETHER_STAR, "\u00a76\u00a7lTesting Arsenal \u00a77(Right-Click)", "\u00a77Right-click anywhere to open the", "\u00a7754-slot Vehicles & Weapons menu.");
        this.giveItem(player, star);
        player.sendTitle("\u00a76\u00a7lTESTING MODE", "\u00a7aCreative & Testing Arsenal Active", 10, 60, 20);
        player.playSound(player.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 0.8f, 1.2f);
        player.sendMessage("\u00a78\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501");
        player.sendMessage("\u00a76\u00a7l[SD CRAFT] \u00a7aInstant Testing Mode Activated!");
        player.sendMessage("\u00a7f\u2022 Gamemode set to \u00a7eCREATIVE \u00a7fwith Flight & Godmode enabled.");
        player.sendMessage("\u00a7f\u2022 Added \u00a7a$10,000 \u00a7ftest funds to your wallet.");
        player.sendMessage("\u00a7f\u2022 Right-click the \u00a76Testing Arsenal Star \u00a7for type \u00a7b/arsenal \u00a7fanytime!");
        player.sendMessage("\u00a78\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501");
        this.openArsenal(player);
    }

    public boolean handleInventory(InventoryClickEvent e) {
        HumanEntity humanEntity = e.getWhoClicked();
        if (!(humanEntity instanceof Player)) {
            return false;
        }
        Player player = (Player)humanEntity;
        if (!e.getView().getTitle().equals(GUI_TITLE)) {
            return false;
        }
        e.setCancelled(true);
        if (!this.plugin.isAuthenticated(player) || !player.hasPermission("sdcraft.admin")) {
            player.closeInventory();
            return true;
        }
        int slot = e.getRawSlot();
        if (slot < 0 || slot >= 54) {
            return true;
        }
        String name = player.getName();
        World world = player.getWorld();
        switch (slot) {
            case 0: {
                this.giveVehicle(player, "FFW36Q", "Sedan Black");
                break;
            }
            case 1: {
                this.giveVehicle(player, "W32FND", "Sportscar GT");
                break;
            }
            case 2: {
                this.giveVehicle(player, "JSJ4ST", "Police Cruiser");
                break;
            }
            case 3: {
                this.giveVehicle(player, "HVN8HB", "Police SUV Interceptor");
                break;
            }
            case 4: {
                this.giveVehicle(player, "384A4N", "Police Motorcycle");
                break;
            }
            case 5: {
                this.giveVehicle(player, "RJRN9P", "Apache Military Helicopter");
                break;
            }
            case 6: {
                this.giveVehicle(player, "PLV871", "Ocean Speedboat");
                break;
            }
            case 7: {
                Bukkit.dispatchCommand((CommandSender)Bukkit.getConsoleSender(), (String)("mtv givefuel " + name + " 100"));
                this.giveItem(player, CityItems.jerryCan());
                player.sendMessage("\u00a7a[Arsenal] \u00a7e100L Jerry Can fuel delivered!");
                player.playSound(player.getLocation(), Sound.ITEM_BOTTLE_FILL, 0.8f, 1.2f);
                break;
            }
            case 8: {
                this.giveItem(player, CityItems.baseballBat());
                player.sendMessage("\u00a7a[Arsenal] \u00a7eLouisville Baseball Bat equipped!");
                player.playSound(player.getLocation(), Sound.ENTITY_ITEM_PICKUP, 0.8f, 1.2f);
                break;
            }
            case 9: {
                this.giveGun(player, "p30", GunEngine.GunType.PISTOL, "P30 9mm Pistol");
                break;
            }
            case 10: {
                this.giveGun(player, "glock", GunEngine.GunType.PISTOL, "Glock 17 Tactical");
                break;
            }
            case 11: {
                this.giveGun(player, "deagle", GunEngine.GunType.PISTOL, "Desert Eagle .50");
                break;
            }
            case 12: {
                this.giveGun(player, "mp5", GunEngine.GunType.SMG, "Tactical Micro-SMG (MP5)");
                break;
            }
            case 13: {
                this.giveGun(player, "ak47", GunEngine.GunType.RIFLE, "AK-47 Assault Rifle");
                break;
            }
            case 14: {
                this.giveGun(player, "m4", GunEngine.GunType.RIFLE, "M4 Urban Assault Rifle");
                break;
            }
            case 15: {
                this.giveGun(player, "remington", GunEngine.GunType.SHOTGUN, "12-Gauge Tactical Shotgun");
                break;
            }
            case 16: {
                this.giveGun(player, "awp", GunEngine.GunType.RIFLE, "AWP Precision Sniper");
                break;
            }
            case 17: {
                this.giveGun(player, "barrett", GunEngine.GunType.RIFLE, "Barrett .50 Anti-Material");
                break;
            }
            case 18: {
                this.giveAmmo(player, "9mm", "9mm_ammo", 64, "9mm Pistol Ammo");
                break;
            }
            case 19: {
                this.giveAmmo(player, "50ae", "50cal_ammo", 64, ".50 AE Heavy Ammo");
                break;
            }
            case 20: {
                this.giveAmmo(player, "556", "556_ammo", 64, "5.56mm NATO Ammo");
                break;
            }
            case 21: {
                this.giveAmmo(player, "762", "762_ammo", 64, "7.62mm Rifle Ammo");
                break;
            }
            case 22: {
                this.giveAmmo(player, "12gauge", "shotgun_ammo", 64, "12-Gauge Buckshot");
                break;
            }
            case 23: {
                this.giveAmmo(player, "338", "sniper_ammo", 64, ".338 Sniper Rounds");
                break;
            }
            case 24: {
                this.giveAmmo(player, "50bmg", "50bmg_ammo", 64, ".50 BMG Heavy Ammo");
                break;
            }
            case 25: {
                this.giveAmmo(player, "9mm", "9mm_ammo", 64, "Sidearm");
                this.giveAmmo(player, "12gauge", "shotgun_shells", 64, "Scatter");
                this.giveAmmo(player, "556", "rifle_ammo", 64, "Rifle");
                player.playSound(player.getLocation(), Sound.ITEM_ARMOR_EQUIP_CHAIN, 0.9f, 1.1f);
                break;
            }
            case 26: {
                ItemStack armor = this.item(Material.NETHERITE_CHESTPLATE, "\u00a79\u00a7lSWAT Heavy Kevlar Armor", "\u00a77Ballistic Protection Level IV");
                player.getInventory().setChestplate(armor);
                player.sendMessage("\u00a7a[Arsenal] \u00a79Heavy Kevlar SWAT Armor equipped!");
                player.playSound(player.getLocation(), Sound.ITEM_ARMOR_EQUIP_NETHERITE, 0.8f, 1.0f);
                break;
            }
            case 27: {
                try {
                    this.ledger.creditWallet(player.getUniqueId(), 1000000L, "arsenal test funds");
                    this.giveItem(player, CityItems.cashIcon());
                    player.sendMessage("\u00a7a[Arsenal] \u00a7e$10,000 cash added to your wallet! (Balance: " + PolicyEngine.money(this.ledger.wallet(player.getUniqueId())) + ")");
                    player.playSound(player.getLocation(), Sound.ENTITY_EXPERIENCE_ORB_PICKUP, 0.8f, 1.2f);
                }
                catch (Exception ex) {
                    player.sendMessage("\u00a7cError updating ledger: " + ex.getMessage());
                }
                break;
            }
            case 28: {
                try {
                    this.ledger.reward(player.getUniqueId(), 100000000L, "arsenal wire transfer");
                    this.giveItem(player, CityItems.atmCard());
                    player.sendMessage("\u00a7a[Arsenal] \u00a72$1,000,000 wired to your First National Bank account & VIP Card issued!");
                    player.playSound(player.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 0.8f, 1.2f);
                }
                catch (Exception ex) {
                    player.sendMessage("\u00a7cError updating ledger: " + ex.getMessage());
                }
                break;
            }
            case 29: {
                this.giveItem(player, CityItems.phone());
                player.sendMessage("\u00a7a[Arsenal] \u00a76San Andreas Smartphone equipped! Right-click to open.");
                player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.8f, 1.4f);
                break;
            }
            case 30: {
                this.giveItem(player, this.gps.createGpsItem());
                player.sendMessage("\u00a7a[Arsenal] \u00a7bGPS Navigator equipped! Right-click to view waypoints.");
                player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.8f, 1.4f);
                break;
            }
            case 31: {
                this.giveItem(player, CityItems.medkit());
                this.giveItem(player, new ItemStack(Material.ENCHANTED_GOLDEN_APPLE, 2));
                player.setHealth(player.getMaxHealth());
                player.sendMessage("\u00a7a[Arsenal] \u00a7cParamedic Trauma Medkit equipped & health fully restored!");
                player.playSound(player.getLocation(), Sound.ENTITY_PLAYER_LEVELUP, 0.7f, 1.5f);
                break;
            }
            case 32: {
                this.giveItem(player, CityItems.metroTicket("Central Metro"));
                player.sendMessage("\u00a7a[Arsenal] \u00a7eTrainCarts Metro All-Access Ticket received!");
                player.playSound(player.getLocation(), Sound.ENTITY_ITEM_PICKUP, 0.7f, 1.2f);
                break;
            }
            case 33: {
                this.giveItem(player, CityItems.policeBadge());
                this.giveItem(player, this.item(Material.LEAD, "\u00a79\u00a7lPolice Restraints", "\u00a77Detain criminal suspects."));
                player.sendMessage("\u00a7a[Arsenal] \u00a79SDPD Badge & Police Restraints equipped!");
                player.playSound(player.getLocation(), Sound.ITEM_ARMOR_EQUIP_IRON, 0.7f, 1.2f);
                break;
            }
            case 34: {
                this.giveItem(player, this.item(Material.TRIPWIRE_HOOK, "\u00a77\u00a7lCriminal Lockpick Kit", "\u00a77Used for heist testing."));
                player.sendMessage("\u00a7a[Arsenal] \u00a77Lockpick kit acquired.");
                player.playSound(player.getLocation(), Sound.BLOCK_CHEST_LOCKED, 0.7f, 1.2f);
                break;
            }
            case 35: {
                this.gta.clearWanted(player);
                player.sendMessage("\u00a7a[Arsenal] \u00a7ePardon issued! Wanted level wiped to 0\u2605.");
                player.playSound(player.getLocation(), Sound.ENTITY_PLAYER_LEVELUP, 0.8f, 1.5f);
                break;
            }
            case 36: {
                this.tp(player, new Location(world, 10.5, 70.0, 3.5, 0.0f, 0.0f), "Civic Plaza Spawn");
                break;
            }
            case 37: {
                this.tp(player, new Location(world, 120.5, 66.0, -45.5, 180.0f, 0.0f), "Police Headquarters (SDPD)");
                break;
            }
            case 38: {
                this.tp(player, new Location(world, -61.5, 65.0, 140.5, 270.0f, 0.0f), "Mount Zonah Hospital");
                break;
            }
            case 39: {
                this.tp(player, new Location(world, 56.5, 68.0, -118.5, 90.0f, 0.0f), "First National Bank");
                break;
            }
            case 40: {
                this.tp(player, new Location(world, -150.5, 69.0, -82.5, 180.0f, 0.0f), "Motor Mile Dealership");
                break;
            }
            case 41: {
                this.tp(player, new Location(world, 26.5, 68.0, 63.5, 0.0f, 0.0f), "Central Metro Station");
                break;
            }
            case 42: {
                this.tp(player, new Location(world, -204.5, 70.0, 60.5, 180.0f, 0.0f), "Highway Gas Station");
                break;
            }
            case 43: {
                this.tp(player, new Location(world, 190.5, 70.0, 86.5, 180.0f, 0.0f), "Fire & Rescue Station 4");
                break;
            }
            case 44: {
                this.tp(player, new Location(world, -350.0, 68.0, -200.0, 90.0f, 0.0f), "Airport Runway");
                break;
            }
            case 45: {
                player.setGameMode(GameMode.CREATIVE);
                player.sendMessage("\u00a7a[Arsenal] \u00a7eGamemode set to \u00a7aCREATIVE\u00a7e. Build and explore freely!");
                player.playSound(player.getLocation(), Sound.BLOCK_BEACON_ACTIVATE, 0.7f, 1.2f);
                break;
            }
            case 46: {
                player.setGameMode(GameMode.SURVIVAL);
                player.sendMessage("\u00a7a[Arsenal] \u00a7eGamemode set to \u00a7cSURVIVAL\u00a7e. Roleplay damage active.");
                player.playSound(player.getLocation(), Sound.BLOCK_BEACON_DEACTIVATE, 0.7f, 1.2f);
                break;
            }
            case 47: {
                player.setGameMode(GameMode.ADVENTURE);
                player.sendMessage("\u00a7a[Arsenal] \u00a7eGamemode set to \u00a7bADVENTURE\u00a7e.");
                player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.7f, 1.2f);
                break;
            }
            case 48: {
                boolean fly = !player.getAllowFlight();
                player.setAllowFlight(fly);
                player.setFlying(fly);
                player.setInvulnerable(fly);
                player.sendMessage("\u00a7a[Arsenal] \u00a7eFlight & Invulnerability: " + (fly ? "\u00a7aENABLED" : "\u00a7cDISABLED"));
                player.playSound(player.getLocation(), Sound.ENTITY_ILLUSIONER_PREPARE_MIRROR, 0.7f, 1.4f);
                break;
            }
            case 49: {
                world.setTime(6000L);
                player.sendMessage("\u00a7a[Arsenal] \u00a7eWorld time set to Daylight Noon (6000 ticks).");
                player.playSound(player.getLocation(), Sound.ITEM_FLINTANDSTEEL_USE, 0.8f, 1.2f);
                break;
            }
            case 50: {
                world.setClearWeatherDuration(12000);
                player.sendMessage("\u00a7a[Arsenal] \u00a7eWeather cleared to sunny skies.");
                player.playSound(player.getLocation(), Sound.ITEM_BUCKET_EMPTY, 0.8f, 1.2f);
                break;
            }
            case 51: {
                player.closeInventory();
                player.performCommand("pack");
                break;
            }
            case 52: {
                player.closeInventory();
                player.performCommand("map");
                break;
            }
            case 53: {
                player.closeInventory();
            }
        }
        return true;
    }

    private void giveVehicle(Player player, String uuid, String vehicleName) {
        if (Bukkit.getPluginManager().isPluginEnabled("MTVehicles")) {
            Bukkit.dispatchCommand((CommandSender)Bukkit.getConsoleSender(), (String)("mtv givecar " + player.getName() + " " + uuid));
            this.giveItem(player, CityItems.carKeyFob(vehicleName));
            player.sendMessage("\u00a7a[Arsenal] \u00a7eKeys to your \u00a76" + vehicleName + " \u00a7edelivered! Right-click road to place.");
        } else {
            this.giveItem(player, CityItems.carKeyFob(vehicleName));
            player.sendMessage("\u00a7e[Arsenal] Key Fob delivered for " + vehicleName + ".");
        }
        player.playSound(player.getLocation(), Sound.ENTITY_ITEM_PICKUP, 0.8f, 1.2f);
    }

    private ItemStack nativeGun(Player player, String id, GunEngine.GunType fallback) {
        GtmEquipment equipment = this.plugin.equipment();
        if (equipment != null && equipment.available(player)) return equipment.create(id);
        return this.guns.createGun(fallback);
    }

    private void giveGun(Player player, String legacyId, GunEngine.GunType fallbackType, String ignoredOldName) {
        String id = nativeWeaponId(legacyId);
        GtmEquipment equipment = this.plugin.equipment();
        if (equipment != null && equipment.available(player)) {
            EquipmentCatalog.Entry entry = equipment.catalog().find(id).orElseThrow();
            this.giveItem(player, equipment.create(id));
            this.giveItem(player, this.guns.createAmmo(entry.ammo(), Math.min(64, entry.capacity() * 2)));
            player.sendMessage("\u00a7a[Arsenal] \u00a7eEquipped \u00a76" + entry.title()
                    + "\u00a7e. Right-click to fire; sneak + right-click to reload.");
        } else {
            this.giveItem(player, this.guns.createGun(fallbackType));
            this.giveItem(player, this.guns.createAmmo(fallbackType.ammoType, fallbackType.maxAmmo * 2));
            player.sendMessage("\u00a7a[Arsenal] \u00a7eEquipped " + fallbackType.displayName);
        }
        player.playSound(player.getLocation(), Sound.ITEM_ARMOR_EQUIP_IRON, 0.8f, 1.2f);
    }

    static String nativeWeaponId(String legacyId) {
        return "gtm:" + switch (legacyId) {
            case "p30" -> "kavach_9";
            case "glock" -> "deccan_compact";
            case "deagle" -> "rajput_45";
            case "mp5" -> "viper_sub";
            case "ak47" -> "trishul_ar";
            case "m4" -> "indrayani_carbine";
            case "remington" -> "sher_pump";
            case "awp" -> "brahmos_precision";
            case "barrett" -> "vajra_heavy";
            default -> throw new IllegalArgumentException("Unknown arsenal firearm");
        };
    }

    private void giveAmmo(Player player, String qaId, String fallbackId, int amount, String ammoName) {
        String canonical = GunEngine.canonicalAmmo(fallbackId);
        this.giveItem(player, this.guns.createAmmo(canonical, amount));
        player.sendMessage("\u00a7a[Arsenal] \u00a7eReceived " + amount + " matching native "
                + canonical.replace('_', ' ') + " rounds.");
        player.playSound(player.getLocation(), Sound.ITEM_ARMOR_EQUIP_GENERIC, 0.7f, 1.4f);
    }

    private void giveItem(Player player, ItemStack item) {
        Map<Integer, ItemStack> leftover = player.getInventory().addItem(new ItemStack[]{item});
        if (!leftover.isEmpty()) {
            for (ItemStack rem : leftover.values()) {
                player.getWorld().dropItem(player.getLocation(), rem);
            }
        }
    }

    private void tp(Player player, Location target, String locationName) {
        Location ground = target.clone();
        if (ground.getWorld() == null) {
            ground.setWorld(player.getWorld());
        }
        player.teleport(ground);
        player.sendTitle("\u00a76\u00a7l" + locationName, "\u00a7eFast Landmark Teleport", 5, 40, 10);
        player.playSound(ground, Sound.ENTITY_ENDERMAN_TELEPORT, 0.8f, 1.2f);
        player.sendMessage("\u00a7a[Arsenal] \u00a7eTeleported to \u00a76" + locationName + " \u00a77(" + ground.getBlockX() + ", " + ground.getBlockY() + ", " + ground.getBlockZ() + ")\u00a7e.");
    }
}

