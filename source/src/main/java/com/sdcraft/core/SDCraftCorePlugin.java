package com.sdcraft.core;

import java.io.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.EntityDamageEvent;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.player.*;
import org.bukkit.inventory.*;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.plugin.ServicePriority;
import net.milkbowl.vault.economy.Economy;

/**
 * SD Craft all-in-one core. Code supports implemented commands; high-end
 * AI/vehicle systems remain adapters.
 */
public final class SDCraftCorePlugin extends JavaPlugin implements Listener, CommandExecutor, TabCompleter {
    private Ledger ledger;
    private AiService ai;
    private GtmDialogue gtmDialogue;
    private GtmLoans gtmLoans;
    private NpcService npcs;
    private RestorationEngine restoration;
    private GunEngine guns;
    private GpsManager gps;
    private GtaEngine gta;
    private VaultWallet vaultWallet;
    private CreativeArsenalManager arsenal;
    private YamlConfiguration dialogues, data;
    private File dataFile;
    private final Map<UUID, Pending> pending = new HashMap<>();
    private final Map<UUID, Duty> duties = new HashMap<>();
    private final Map<UUID, Downed> downed = new HashMap<>();
    private final Map<UUID, Long> activeAt = new HashMap<>();
    private final Map<UUID, Long> lastReport = new HashMap<>();
    private final Map<UUID, Deque<Long>> aiRate = new HashMap<>();
    private final Map<UUID, String> guiNpc = new HashMap<>();
    private final Map<UUID, String> pinMode = new HashMap<>();
    private final Map<UUID, StringBuilder> pinDigits = new HashMap<>();
    private long timeSeconds = 0;

    private record Pending(String kind, String target, long cents, long expires, String details) {
    }

    private static final class Duty {
        String profession;
        long lastTick, creditedMs, started;
        int shift;

        Duty(String profession, int shift, long now) {
            this.profession = profession;
            this.shift = shift;
            this.lastTick = now;
            this.started = now;
        }
    }

    private record Downed(long until) {
    }

    @Override
    public void onEnable() {
        saveDefaultConfig();
        if (!new File(getDataFolder(), "npc-dialogues.yml").isFile())
            saveResource("npc-dialogues.yml", false);
        if (!new File(getDataFolder(), "missions.yml").isFile())
            saveResource("missions.yml", false);
        dialogues = YamlConfiguration.loadConfiguration(new File(getDataFolder(), "npc-dialogues.yml"));
        dataFile = new File(getDataFolder(), "runtime.yml");
        data = YamlConfiguration.loadConfiguration(dataFile);
        ledger = new Ledger(getDataFolder());
        gtmLoans = new GtmLoans(this,ledger);
        Bukkit.getPluginManager().registerEvents(gtmLoans,this);
        Objects.requireNonNull(getCommand("gtmloan")).setExecutor((sender, command, label, args) -> {
            if(sender instanceof Player p) gtmLoans.open(p);
            return true;
        });
        if (getConfig().getBoolean("economy.vault-provider-enabled", true)
                && Bukkit.getPluginManager().isPluginEnabled("Vault")) {
            vaultWallet = new VaultWallet(ledger);
            Bukkit.getServicesManager().register(Economy.class, vaultWallet, this, ServicePriority.High);
            getLogger().info("VaultUnlocked economy provider registered: SD Craft wallet.");
            // MTVehicles reads Vault during its own startup, before this provider exists.
            // Its supported console command reconnects it after all plugins have enabled.
            Bukkit.getScheduler().runTask(this, () -> {
                if (Bukkit.getPluginManager().isPluginEnabled("MTVehicles"))
                    Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mtv vault setup");
            });
        }
        ai = new AiService(this);
        restoration = new RestorationEngine(this);
        guns = new GunEngine(this);
        gps = new GpsManager(this);
        gta = new GtaEngine(this, ledger, gps);
        arsenal = new CreativeArsenalManager(this, ledger, gps, gta, guns);
        npcs = new NpcService(this, dialogues, ledger, gta);
        Objects.requireNonNull(getCommand("sdcraft")).setExecutor(this);
        Objects.requireNonNull(getCommand("sdcraft")).setTabCompleter(this);
        for (String c : List.of("map", "gps", "spawn", "car", "kit", "gun", "pack", "phone", "arsenal", "creativemenu", "testitems", "testing")) {
            if (getCommand(c) != null) {
                Objects.requireNonNull(getCommand(c)).setExecutor(this);
                Objects.requireNonNull(getCommand(c)).setTabCompleter(this);
            }
        }
        Bukkit.getPluginManager().registerEvents(this, this);
        Bukkit.getPluginManager().registerEvents(restoration, this);
        Bukkit.getPluginManager().registerEvents(guns, this);
        Bukkit.getPluginManager().registerEvents(gta, this);
        Bukkit.getPluginManager().registerEvents(npcs, this);
        gtmDialogue = new GtmDialogue(this, npcs, ledger);
        Bukkit.getPluginManager().registerEvents(gtmDialogue, this);
        World mainWorld = Bukkit.getWorld(getConfig().getString("world.name", "world"));
        if (mainWorld != null) {
            mainWorld.setSpawnLocation(10, 70, 3);
            mainWorld.setGameRule(org.bukkit.GameRules.ADVANCE_TIME, false);
            getLogger().info("SD Craft: World spawn enforced at City Hall Civic Plaza surface (10, 70, 3).");
        }
        for (World w : Bukkit.getWorlds()) {
            if (!w.getName().equals(getConfig().getString("world.name", "world")))
                continue;
            w.setGameRule(org.bukkit.GameRules.ADVANCE_TIME, false);
        }
        Bukkit.getScheduler().runTaskTimer(this, this::second, 20L, 20L);
        Bukkit.getScheduler().runTaskTimer(this, () -> npcs.tick(), 100L, 200L);
        Bukkit.getScheduler().runTaskTimer(this, () -> npcs.pulse(), 120L, 10L);
        getLogger().info(
                "SDCraftCore loaded: secure ledger, NPC service, transport, crime, medical and duty workflows. Check README for limitations.");
    }

    @Override
    public void onDisable() {
        Bukkit.getServicesManager().unregisterAll(this);
        for (UUID id : new ArrayList<>(duties.keySet()))
            clockOut(id, "server stop");
        if (gtmDialogue != null) gtmDialogue.close();
        if (gtmLoans != null) gtmLoans.close();
        if (npcs != null) npcs.close();
        if (gta != null) gta.close();
        if (data != null && dataFile != null) safeSave();
    }

    private void safeSave() {
        try {
            data.save(dataFile);
        } catch (IOException ex) {
            getLogger().severe("RUNTIME SAVE FAILED: " + ex.getMessage());
        }
    }

    public Location getSurfaceSpawn(World world) {
        if (world == null) {
            world = Bukkit.getWorld(getConfig().getString("world.name", "world"));
            if (world == null && !Bukkit.getWorlds().isEmpty()) {
                world = Bukkit.getWorlds().get(0);
            }
        }
        Location site = site("spawn");
        if (site != null && site.getWorld() != null) {
            return site;
        }
        return new Location(world, 10.5, 70.0, 3.5, 0.0f, 0.0f);
    }

    boolean isManagedNpc(Entity entity) {
        return npcs != null && npcs.identify(entity) != null;
    }

    public void grantStarterKit(Player p, boolean force) {
        PlayerInventory inv = p.getInventory();

        // 1. Firearm Check & Grant
        boolean hasGun = false;
        for (ItemStack it : inv.getContents()) {
            if (it != null && it.hasItemMeta()) {
                if (it.getItemMeta().getPersistentDataContainer().has(guns.getKeyType(), org.bukkit.persistence.PersistentDataType.STRING)) {
                    hasGun = true;
                    break;
                }
                String dn = it.getItemMeta().hasDisplayName() ? it.getItemMeta().getDisplayName().toLowerCase(Locale.ROOT) : "";
                if (dn.contains("p30") || dn.contains("pistol") || dn.contains("gun") || it.getType() == Material.CROSSBOW) {
                    hasGun = true;
                    break;
                }
            }
        }
        if (!hasGun || force) {
            if (Bukkit.getPluginManager().isPluginEnabled("QualityArmory")) {
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "qa give p30 " + p.getName());
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "qa give 9mm " + p.getName() + " 32");
                p.sendMessage("§a[SD Craft] §eQualityArmory P30 9mm Pistol & 32 rounds equipped!");
            } else {
                inv.addItem(guns.createGun(GunEngine.GunType.PISTOL));
                inv.addItem(guns.createAmmo("9mm_ammo", 32));
                p.sendMessage("§a[SD Craft] §e9mm Service Pistol & 32 rounds equipped!");
            }
        }

        // 2. Vehicles (Sedan Black UUID: FFW36Q)
        boolean hasCar = false;
        for (ItemStack it : inv.getContents()) {
            if (it != null && it.hasItemMeta() && it.getItemMeta().hasDisplayName()) {
                String dName = it.getItemMeta().getDisplayName().toLowerCase(Locale.ROOT);
                if (dName.contains("sedan") || dName.contains("car") || dName.contains("vehicle") || dName.contains("voucher")) {
                    hasCar = true;
                    break;
                }
            }
        }
        if (!hasCar || force) {
            if (Bukkit.getPluginManager().isPluginEnabled("MTVehicles")) {
                Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mtv givecar " + p.getName() + " FFW36Q");
                p.sendMessage("§a[SD Craft] §eKeys to your personal Sedan Black delivered! Right-click road to place & drive.");
            } else {
                p.sendMessage("§e[SD Craft] Vehicle dealership voucher recorded. Type /car to claim your car.");
            }
        }

        // 3. GPS Navigator Check & Grant
        boolean hasGps = false;
        for (ItemStack it : inv.getContents()) {
            if (it != null && it.getType() == Material.COMPASS && it.hasItemMeta()
                    && it.getItemMeta().hasDisplayName() && it.getItemMeta().getDisplayName().contains("GPS")) {
                hasGps = true;
                break;
            }
        }
        if (!hasGps || force) {
            inv.addItem(gps.createGpsItem());
            p.sendMessage("§a[SD Craft] §bSD Craft GPS Navigator received! Right-click to open navigation.");
        }

        boolean hasPhone = Arrays.stream(inv.getContents()).anyMatch(item -> CityItems.is(item, CityItems.PHONE));
        if (!hasPhone) inv.addItem(CityItems.phone());

        // 4. Food / Street Burgers
        boolean hasFood = false;
        for (ItemStack it : inv.getContents()) {
            if (it != null && (it.getType() == Material.COOKED_BEEF || it.getType() == Material.BREAD)) {
                hasFood = true;
                break;
            }
        }
        if (!hasFood || force) {
            ItemStack burger = new ItemStack(Material.COOKED_BEEF, 16);
            ItemMeta bMeta = burger.getItemMeta();
            if (bMeta != null) {
                bMeta.setDisplayName("§6Street Burger");
                bMeta.setLore(List.of("§7Fresh city burger from local diner", "§8Restores hunger and stamina."));
                burger.setItemMeta(bMeta);
            }
            inv.addItem(burger);
        }
    }

    @EventHandler
    public void onJoin(PlayerJoinEvent e) {
        Player p = e.getPlayer();
        UUID id = p.getUniqueId();
        activeAt.put(id, System.currentTimeMillis());
        boolean isFirstJoin = false;
        try {
            isFirstJoin = ledger.register(id);
            if (isFirstJoin)
                p.sendMessage("§a[SD Craft] Welcome! $500 wallet and $1,000 protected bank opened.");
        } catch (Exception ex) {
            getLogger().severe("ACCOUNT ERROR " + id + " " + ex.getMessage());
            p.sendMessage("§cAccount persistence error. Contact administrator.");
        }

        // Fix underground spawn issue:
        Location cur = p.getLocation();
        if (isFirstJoin || cur.getY() < 66.0 || (Math.abs(cur.getBlockX() - (-8)) < 24 && Math.abs(cur.getBlockZ() - (-356)) < 24)) {
            Location surfaceSpawn = getSurfaceSpawn(p.getWorld());
            p.teleport(surfaceSpawn);
            p.sendTitle("§6§lSD CRAFT", "§eWelcome to New Blockston City", 10, 70, 20);
            p.playSound(surfaceSpawn, Sound.UI_TOAST_CHALLENGE_COMPLETE, 0.8f, 1.0f);
            p.sendMessage("§6[SD Craft] §aSpawned on Civic Center Plaza surface (Daylight Boulevard)!");
        }

        // Grant GTA Starter Kit (Guns, Ammo, Car Keys, GPS, Food)
        Bukkit.getScheduler().runTaskLater(this, () -> {
            if (p.isOnline()) {
                if (gta.tryClaimStarter(p)) grantStarterKit(p, false);
                gta.onJoin(p);
                npcs.tick(); // Evaluate and spawn nearby city staff immediately
                p.sendMessage("§6[SD Craft 3D] §eIf vehicles look like hoes, accept the server resource pack prompt or type §b/pack§e!");
            }
        }, 15L);
    }

    @EventHandler
    public void onRespawn(PlayerRespawnEvent e) {
        if (!e.isBedSpawn() && !e.isAnchorSpawn()) {
            Location surfaceSpawn = getSurfaceSpawn(e.getPlayer().getWorld());
            e.setRespawnLocation(surfaceSpawn);
        }
    }

    @EventHandler
    public void onQuit(PlayerQuitEvent e) {
        UUID id = e.getPlayer().getUniqueId();
        clockOut(id, "disconnect");
        if(gtmLoans!=null)gtmLoans.quit(p);
        activeAt.remove(id);
        guiNpc.remove(id);
        pinMode.remove(id);
        pinDigits.remove(id);
        pending.remove(id);
    }

    @EventHandler
    public void onMove(PlayerMoveEvent e) {
        if (e.getTo() == null)
            return;
        if (e.getFrom().getBlockX() != e.getTo().getBlockX() || e.getFrom().getBlockZ() != e.getTo().getBlockZ()
                || e.getFrom().getBlockY() != e.getTo().getBlockY())
            activeAt.put(e.getPlayer().getUniqueId(), System.currentTimeMillis());
    }

    @EventHandler
    public void onInteract(PlayerInteractEntityEvent e) {
        String id = npcs.identify(e.getRightClicked());
        if (id == null)
            return;
        e.setCancelled(true);
        if (npcs.isAmbient(id)) {
            e.getPlayer().sendMessage("§6" + npcs.name(id) + " §7(" + npcs.role(id) + "): §f"
                    + npcs.greeting(id, "en"));
            if (npcs.isMerchant(id)) gta.handleNpcAction(e.getPlayer(), "view_catalog");
            return;
        }
        openNpc(e.getPlayer(), id);
    }

    @EventHandler
    public void onPlayerInteract(PlayerInteractEvent e) {
        if (e.getAction() == org.bukkit.event.block.Action.RIGHT_CLICK_AIR
                || e.getAction() == org.bukkit.event.block.Action.RIGHT_CLICK_BLOCK) {
            ItemStack item = e.getItem();
            if (CityItems.is(item, CityItems.PHONE)) {
                e.setCancelled(true);
                try { gta.handleCommand(e.getPlayer(), "phone", new String[0]); }
                catch (Exception ex) { err(e.getPlayer(), "Phone unavailable: " + ex.getMessage()); }
                return;
            }
            if (item != null && item.getType() == Material.NETHER_STAR && item.hasItemMeta()
                    && item.getItemMeta().hasDisplayName()
                    && item.getItemMeta().getDisplayName().contains("Arsenal")) {
                e.setCancelled(true);
                if (arsenal != null) arsenal.openArsenal(e.getPlayer());
                return;
            }
            if (item != null && item.getType() == Material.COMPASS && item.hasItemMeta()
                    && item.getItemMeta().hasDisplayName()
                    && item.getItemMeta().getDisplayName().contains("GPS")) {
                e.setCancelled(true);
                gps.openGpsMenu(e.getPlayer());
            }
        }
    }

    @EventHandler
    public void onSwapHands(PlayerSwapHandItemsEvent e) {
        ItemStack main = e.getMainHandItem();
        if (main != null && main.getType() == Material.COMPASS && main.hasItemMeta()
                && main.getItemMeta().hasDisplayName() && main.getItemMeta().getDisplayName().contains("GPS")) {
            e.setCancelled(true);
            Player p = e.getPlayer();
            String dist = gps.getDistrict(p.getLocation());
            p.sendActionBar(net.kyori.adventure.text.Component.text("§6[GPS] §b" + dist + " §7| §fX: "
                    + p.getLocation().getBlockX() + " Y: " + p.getLocation().getBlockY() + " Z: "
                    + p.getLocation().getBlockZ()));
            p.playSound(p.getLocation(), Sound.UI_BUTTON_CLICK, 0.6f, 1.4f);
        }
    }

    @EventHandler
    public void onInventory(InventoryClickEvent e) {
        if (arsenal != null && arsenal.handleInventory(e)) return;
        if (gta.handleInventory(e)) return;
        if (e.getWhoClicked() instanceof Player gpPlayer && e.getView().getTitle().equals(GpsManager.GUI_TITLE)) {
            e.setCancelled(true);
            gps.handleClick(gpPlayer, e.getCurrentItem());
            return;
        }
        if (e.getWhoClicked() instanceof Player pinPlayer && e.getView().getTitle().equals("SD Craft PIN")) {
            e.setCancelled(true);
            ItemStack clicked = e.getCurrentItem();
            if (clicked == null || !clicked.hasItemMeta() || !clicked.getItemMeta().hasDisplayName())
                return;
            String val = clicked.getItemMeta().getDisplayName().replace("§b", "").replace("§a", "").replace("§c", "");
            UUID uid = pinPlayer.getUniqueId();
            StringBuilder digits = pinDigits.get(uid);
            String mode = pinMode.get(uid);
            if (digits == null || mode == null)
                return;
            if (val.matches("[0-9]")) {
                if (digits.length() < 8)
                    digits.append(val);
                return;
            }
            if (val.equals("CLEAR")) {
                digits.setLength(0);
                return;
            }
            if (val.equals("CANCEL")) {
                pinMode.remove(uid);
                pinDigits.remove(uid);
                pinPlayer.closeInventory();
                return;
            }
            if (val.equals("CONFIRM")) {
                String input = digits.toString();
                digits.setLength(0);
                pinMode.remove(uid);
                pinDigits.remove(uid);
                pinPlayer.closeInventory();
                try {
                    if (mode.equals("set")) {
                        ledger.pin(uid, input);
                        msg(pinPlayer, "Secure PIN saved through private menu.");
                    } else if (ledger.verifyPin(uid, input)) {
                        executePending(pinPlayer);
                    } else
                        err(pinPlayer, "PIN invalid. No transfer authorized.");
                } catch (Exception ex) {
                    err(pinPlayer, "PIN operation failed: " + ex.getMessage());
                    getLogger().warning(ex.toString());
                }
            }
            return;
        }
        if (!(e.getWhoClicked() instanceof Player p))
            return;
        String id = guiNpc.get(p.getUniqueId());
        if (id == null || !e.getView().getTitle().startsWith("SD Craft:"))
            return;
        e.setCancelled(true);
        ItemStack item = e.getCurrentItem();
        if (item == null || !item.hasItemMeta() || !item.getItemMeta().hasDisplayName() || item.getType() == Material.GRAY_STAINED_GLASS_PANE)
            return;
        String action = item.getItemMeta().getDisplayName().replace("§b", "").trim();
        if (action.isEmpty()) return;
        p.closeInventory();
        gta.handleNpcAction(p, action);
    }

    @EventHandler
    public void onDamage(EntityDamageEvent e) {
        if (!(e.getEntity() instanceof Player p))
            return;
        UUID id = p.getUniqueId();
        if (downed.containsKey(id)) {
            e.setCancelled(true);
            return;
        }
        if (!getConfig().getBoolean("medical.downed-enabled", true))
            return;
        if (e.getFinalDamage() < p.getHealth())
            return;
        e.setCancelled(true);
        p.setHealth(Math.max(1.0, Math.min(2.0, p.getMaxHealth())));
        long until = System.currentTimeMillis() + 90000L;
        downed.put(id, new Downed(until));
        p.setInvulnerable(true);
        p.sendMessage("§c[SD Craft] DOWNED for 90 seconds. A medic can /sdc revive " + p.getName()
                + ". Hospital fallback is automatic.");
    }

    private void openPin(Player p, String mode) {
        Inventory inv = Bukkit.createInventory(null, 27, "SD Craft PIN");
        String[] names = { "1", "2", "3", "4", "5", "6", "7", "8", "9", "CLEAR", "0", "CONFIRM", "CANCEL" };
        for (int i = 0; i < names.length; i++) {
            ItemStack item = new ItemStack(Material.PAPER);
            ItemMeta meta = item.getItemMeta();
            if (meta != null) {
                meta.setDisplayName("§b" + names[i]);
                item.setItemMeta(meta);
            }
            inv.setItem(i, item);
        }
        pinDigits.put(p.getUniqueId(), new StringBuilder());
        pinMode.put(p.getUniqueId(), mode);
        p.openInventory(inv);
        p.sendMessage(
                "§7[SD Craft] Enter 4–8 PIN digits using menu buttons; then CONFIRM. Digits are not sent through chat.");
    }

    private void executePending(Player p) throws IOException {
        UUID id = p.getUniqueId();
        Pending x = pending.remove(id);
        if (x == null || x.expires < System.currentTimeMillis()) {
            err(p, "No valid pending action");
            return;
        }
        boolean ok = false;
        switch (x.kind) {
            case "deposit":
                ok = ledger.deposit(id, x.cents);
                break;
            case "withdraw":
                ok = ledger.withdraw(id, x.cents);
                break;
            case "transfer":
                ok = ledger.transfer(id, UUID.fromString(x.target), x.cents);
                break;
            case "taxi":
            case "bus":
            case "metro":
                ok = ledger.chargeWallet(id, x.cents, x.kind + " trip");
                if (ok) {
                    if (x.kind.equals("metro")) p.getInventory().addItem(CityItems.metroTicket(x.target));
                    Location dest = site(x.target);
                    if (dest != null)
                        Bukkit.getScheduler().runTaskLater(this, () -> {
                            if (p.isOnline())
                                p.teleport(dest);
                        }, 60L);
                }
                break;
            case "medical":
                ok = ledger.chargeWallet(id, x.cents, "medical:" + x.target);
                if (ok)
                    Bukkit.getScheduler().runTaskLater(this, () -> {
                        if (p.isOnline()) {
                            p.setHealth(Math.min(p.getMaxHealth(), p.getHealth() + 8));
                            p.sendMessage("§a[SD Craft] Medical care completed.");
                        }
                    }, getConfig().getLong("medical.procedure-seconds", 30) * 20L);
                break;
        }
        msg(p, ok ? "Transaction authorized and saved."
                : "Transaction declined: insufficient funds or other verification failed.");
    }

    private void openNpc(Player p, String id) {
        String lang = ledger.language(p.getUniqueId());
        String npcName = npcs.name(id);
        String npcRole = npcs.role(id);
        String npcDept = npcs.dept(id).toUpperCase(Locale.ROOT);
        String greeting = npcs.greeting(id, lang);

        p.sendMessage("§8━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        p.sendMessage("§6§l▶ §e§l" + npcName + " §7(" + npcRole + " • §6" + npcDept + "§7)");
        p.sendMessage("§f\"" + greeting + "\"");
        p.sendMessage("§7Select an action in the menu below or type §f/sdc help§7.");
        p.sendMessage("§8━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        p.playSound(p.getLocation(), Sound.ENTITY_VILLAGER_YES, 0.8f, 1.1f);
        p.sendActionBar(net.kyori.adventure.text.Component.text("§eSpeaking with §6" + npcName + " §7- §aChoose an action"));

        List<String> actions = npcs.actions(id);
        Inventory inv = Bukkit.createInventory(null, 27, "SD Craft: " + npcName);

        ItemStack border = new ItemStack(Material.GRAY_STAINED_GLASS_PANE);
        ItemMeta bMeta = border.getItemMeta();
        if (bMeta != null) {
            bMeta.setDisplayName(" ");
            border.setItemMeta(bMeta);
        }
        for (int i = 0; i < 27; i++) {
            inv.setItem(i, border);
        }

        int[] actionSlots = { 10, 11, 12, 13, 14, 15, 16, 1, 2, 3, 4, 5, 6, 7 };
        for (int i = 0; i < Math.min(actionSlots.length, actions.size()); i++) {
            String act = actions.get(i);
            Material mat = getThematicMaterial(act);
            ItemStack item = new ItemStack(mat);
            ItemMeta meta = item.getItemMeta();
            if (meta != null) {
                meta.setDisplayName("§b" + act.replace('_', ' '));
                meta.setLore(List.of(
                        "§7Official " + npcDept + " Service",
                        "§a▶ Click to proceed"
                ));
                item.setItemMeta(meta);
            }
            inv.setItem(actionSlots[i], item);
        }
        guiNpc.put(p.getUniqueId(), id);
        p.openInventory(inv);
    }

    private Material getThematicMaterial(String action) {
        String act = action.toLowerCase(Locale.ROOT);
        if (act.contains("police") || act.contains("crime") || act.contains("duty") || act.contains("report"))
            return Material.SHIELD;
        if (act.contains("bank") || act.contains("balance") || act.contains("deposit") || act.contains("withdraw") || act.contains("transfer"))
            return Material.EMERALD;
        if (act.contains("medic") || act.contains("treatment") || act.contains("hospital") || act.contains("revive") || act.contains("first_aid"))
            return Material.GOLDEN_APPLE;
        if (act.contains("transit") || act.contains("metro") || act.contains("bus") || act.contains("taxi") || act.contains("ticket"))
            return Material.COMPASS;
        if (act.contains("car") || act.contains("vehicle") || act.contains("catalog") || act.contains("test_drive") || act.contains("repair"))
            return Material.MINECART;
        if (act.contains("fire") || act.contains("rescue") || act.contains("extinguisher"))
            return Material.WATER_BUCKET;
        if (act.contains("register") || act.contains("permit") || act.contains("statement"))
            return Material.WRITABLE_BOOK;
        return Material.GOLD_INGOT;
    }

    private void second() {
        long now = System.currentTimeMillis();
        timeSeconds++;
        World world = Bukkit.getWorld(getConfig().getString("world.name", "world"));
        if (world != null) {
            long cycle = timeSeconds % 1800L;
            long tick = cycle < 1200L ? 6000L + cycle * 10L : 18000L + (cycle - 1200L) * 20L;
            world.setTime(tick % 24000L);
        }
        for (Player p : Bukkit.getOnlinePlayers()) {
            UUID id = p.getUniqueId();
            if(gtmLoans!=null)gtmLoans.tick(p,!p.isSleeping() && now-activeAt.getOrDefault(id,0L)<120000L);
            Duty d = duties.get(id);
            if (d == null)
                continue;
            int shift = shiftOf(world);
            if (d.shift != shift) {
                clockOut(id, "shift ended");
                continue;
            }
            boolean awake = !p.isSleeping();
            long active = activeAt.getOrDefault(id, 0L);
            if (awake && now - active < 120000L) {
                d.creditedMs += Math.max(0L, now - d.lastTick);
            }
            d.lastTick = now;
        }
        for (var entry : new HashMap<>(downed).entrySet()) {
            if (entry.getValue().until > now)
                continue;
            Player p = Bukkit.getPlayer(entry.getKey());
            downed.remove(entry.getKey());
            if (p == null)
                continue;
            p.setInvulnerable(false);
            p.setHealth(Math.min(p.getMaxHealth(), 10.0));
            Location dest = site("hospital");
            if (dest == null)
                dest = p.getWorld().getSpawnLocation();
            p.teleport(dest);
            p.sendMessage("§e[SD Craft] Transported to hospital fallback after the downed timer.");
        }
        pending.entrySet().removeIf(e -> e.getValue().expires < now);
        if (restoration != null)
            restoration.tick();
        gta.tick();
    }

    private int shiftOf(World w) {
        return w != null && w.getTime() >= 18000 ? 1 : 0;
    }

    private void clockOut(UUID id, String why) {
        Duty d = duties.remove(id);
        if (d == null)
            return;
        try {
            int r = Math.max(1, Math.min(7, ledger.rank(id)));
            long[] pay10 = { 12000, 14500, 17000, 19500, 22000, 24500, 27000 };
            long pay = (d.creditedMs * pay10[r - 1]) / 600000L;
            ledger.grantDuty(id, pay, d.creditedMs, 0, "duty " + d.profession + " " + why);
            Player p = Bukkit.getPlayer(id);
            if (p != null)
                p.sendMessage("§a[SD Craft] Duty ended (" + why + "). Earned " + PolicyEngine.money(pay)
                        + " from verified active time.");
        } catch (Exception ex) {
            getLogger().severe("DUTY SETTLEMENT FAILED " + id + " " + ex.getMessage());
        }
    }

    public Location site(String id) {
        String path = "sites." + id;
        World w = Bukkit.getWorld(data.getString(path + ".world", ""));
        if (w == null || !data.contains(path + ".x"))
            return null;
        return new Location(w, data.getDouble(path + ".x"), data.getDouble(path + ".y"), data.getDouble(path + ".z"));
    }

    GunEngine guns() { return guns; }
    GtmLoans loans() { return gtmLoans; }
    String profession(UUID id) { return data.getString("players." + id + ".profession", ""); }

    private boolean near(Player p, String id, int radius) {
        Location l = site(id);
        return l != null && l.getWorld().equals(p.getWorld()) && l.distanceSquared(p.getLocation()) <= radius * radius;
    }

    private void setSite(String id, Location loc) throws IOException {
        String path = "sites." + id;
        data.set(path + ".world", loc.getWorld().getName());
        data.set(path + ".x", loc.getX());
        data.set(path + ".y", loc.getY());
        data.set(path + ".z", loc.getZ());
        data.save(dataFile);
    }

    private void msg(CommandSender who, String text) {
        who.sendMessage("§6[SD Craft] §f" + text);
    }

    private void err(CommandSender who, String text) {
        who.sendMessage("§c[SD Craft] " + text);
    }

    private long dollars(String input) {
        if (!input.matches("[0-9]{1,9}(\\.[0-9]{1,2})?"))
            throw new IllegalArgumentException("Use positive amount such as 25 or 25.50");
        java.math.BigDecimal value = new java.math.BigDecimal(input).movePointRight(2);
        long a = value.longValueExact();
        if (a <= 0 || a > 100000000000L)
            throw new IllegalArgumentException("Invalid amount");
        return a;
    }

    private String commandHelp() {
        return "/sdc map, gps, spawn, car, kit, gun, pack, arsenal, testing, ammo, account, promotion, bank, pin, confirm, cancel, npc, npcs, setnpc, duty, work, fees, taxi, ride, setsite, report, rob, surrender, revive, medical, mission, status, talk, zone, restore";
    }

    @Override
    public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
        String cmdName = cmd.getName().toLowerCase(Locale.ROOT);
        if (cmdName.equals("phone")) {
            if (sender instanceof Player p) {
                try { gta.handleCommand(p, "phone", args); }
                catch (Exception ex) { err(p, ex.getMessage()); }
            }
            return true;
        }
        if (cmdName.equals("map")) {
            if (sender instanceof Player p) {
                gps.sendMapPrompt(p);
            } else {
                msg(sender, "SD Craft 3D Web Map: " + getConfig().getString("map.web-url", "http://localhost:8100"));
            }
            return true;
        }
        if (cmdName.equals("gps")) {
            if (args.length >= 2 && args[0].equalsIgnoreCase("give")) {
                if (!sender.hasPermission("sdcraft.admin")) {
                    err(sender, "Admin only");
                    return true;
                }
                Player target = Bukkit.getPlayer(args[1]);
                if (target == null) {
                    err(sender, "Player not found");
                    return true;
                }
                target.getInventory().addItem(gps.createGpsItem());
                msg(sender, "Gave SD Craft GPS Navigator to " + target.getName());
                target.sendMessage("§a[SD Craft] Received SD Craft GPS Navigator");
                return true;
            }
            if (sender instanceof Player p) {
                gps.openGpsMenu(p);
            } else {
                msg(sender, "GPS navigation menu is for players in-game.");
            }
            return true;
        }
        if (cmdName.equals("spawn")) {
            if (sender instanceof Player p) {
                Location surfaceSpawn = getSurfaceSpawn(p.getWorld());
                p.teleport(surfaceSpawn);
                p.sendMessage("§a[SD Craft] §eTeleported to City Hall Plaza surface.");
                p.playSound(surfaceSpawn, Sound.ENTITY_ENDERMAN_TELEPORT, 0.7f, 1.2f);
            } else {
                msg(sender, "Command is for in-game players.");
            }
            return true;
        }
        if (cmdName.equals("car") || cmdName.equals("vehicle") || cmdName.equals("cars")) {
            if (sender instanceof Player p) {
                try { gta.handleStandaloneCar(p, args); }
                catch (Exception ex) { err(p, ex.getMessage()); }
            } else {
                msg(sender, "Command is for in-game players.");
            }
            return true;
        }
        if (cmdName.equals("kit") || cmdName.equals("starter")) {
            if (sender instanceof Player p) {
                if (gta.tryClaimStarter(p)) grantStarterKit(p, false);
                else err(p, "The starter kit is one-time only. Use /phone for shops and missions.");
            } else {
                msg(sender, "Command is for in-game players.");
            }
            return true;
        }
        if (cmdName.equals("gun") || cmdName.equals("guns")) {
            if (sender instanceof Player p) {
                try { gta.handleStandaloneGun(p, args); }
                catch (Exception ex) { err(p, ex.getMessage()); }
            } else {
                msg(sender, "Command is for in-game players.");
            }
            return true;
        }
        if (cmdName.equals("pack") || cmdName.equals("resourcepack") || cmdName.equals("packs")) {
            if (sender instanceof Player p) {
                p.sendMessage("§e================ §6[ SD CRAFT UNIFIED RESOURCE PACK ] §e================");
                p.sendMessage("§a★ Included Systems:");
                p.sendMessage("§f  • §aFresh Animations 1.11.2 (26.3) §8+ §eAll Extensions §7(Details, Emissive, Objects, Player)");
                p.sendMessage("§f  • §b3D MTVehicles §7(Cars, Bikes, Helicopters, Speedboats)");
                p.sendMessage("§f  • §cQualityArmory Firearms §7(70 realistic modern weapons)");
                p.sendMessage("§f  • §6City Custom Items §7(Phone, ATM cards, Cash, Metro tickets)");
                p.sendMessage("§e★ Client Recommendation:");
                p.sendMessage("§7  Use §fEntity Model Features (EMF) §7+ §fETF §7or OptiFine on your client for full CEM animations!");
                p.sendMessage("§e★ Direct Download:");
                p.sendMessage("§b  resourcepacks/SDCraft_Unified_26.3_CityPack.zip §7(Mandatory SMP Pack)");
                p.sendMessage("§b  resourcepacks/FreshAnimations_v1.11.2_All_Extensions_26.3.zip §7(Standalone FA)");
                p.sendMessage("§e==================================================================");
                p.playSound(p.getLocation(), Sound.UI_BUTTON_CLICK, 0.8f, 1.2f);
            } else {
                msg(sender, "Resource pack: resourcepacks/SDCraft_Unified_26.3_CityPack.zip");
            }
            return true;
        }
        if (cmdName.equals("arsenal") || cmdName.equals("creativemenu") || cmdName.equals("testitems")) {
            if (sender instanceof Player p) {
                arsenal.openArsenal(p);
            } else {
                msg(sender, "Creative Testing Arsenal is for players in-game.");
            }
            return true;
        }
        if (cmdName.equals("testing")) {
            if (sender instanceof Player p) {
                arsenal.enableTestingMode(p);
            } else {
                msg(sender, "Testing mode is for players in-game.");
            }
            return true;
        }
        try {
            return dispatch(sender, args);
        } catch (Exception ex) {
            err(sender, ex instanceof IllegalArgumentException || ex instanceof IllegalStateException ? ex.getMessage()
                    : "Operation could not finish; review server logs.");
            if (!(ex instanceof IllegalArgumentException))
                getLogger().warning("Command error: " + ex.toString());
            return true;
        }
    }

    private boolean dispatch(CommandSender sender, String[] a) throws Exception {
        if (a.length == 0 || a[0].equalsIgnoreCase("help")) {
            msg(sender, commandHelp());
            return true;
        }
        String action = a[0].toLowerCase(Locale.ROOT);
        if (action.equals("kit") || action.equals("starter")) {
            if (sender instanceof Player p) {
                if (gta.tryClaimStarter(p)) grantStarterKit(p, false);
                else err(p, "The starter kit is one-time only.");
            }
            return true;
        }
        if (action.equals("gun") && a.length < 2) {
            if (sender instanceof Player p) gta.handleStandaloneGun(p, new String[0]);
            return true;
        }
        if (action.equals("gun") && !a[1].equalsIgnoreCase("give")) {
            if (sender instanceof Player p) gta.handleStandaloneGun(p, Arrays.copyOfRange(a, 1, a.length));
            return true;
        }
        if (action.equals("arsenal") || action.equals("creativemenu") || action.equals("testitems")) {
            if (sender instanceof Player p) arsenal.openArsenal(p);
            else msg(sender, "Creative Testing Arsenal is for players in-game.");
            return true;
        }
        if (action.equals("testing")) {
            if (sender instanceof Player p) arsenal.enableTestingMode(p);
            else msg(sender, "Testing mode is for players in-game.");
            return true;
        }
        if (gta.handles(action)) {
            if (sender instanceof Player p) return gta.handleCommand(p, action, a);
            err(sender, "This command is for players.");
            return true;
        }
        if (action.equals("status")) {
            msg(sender, "Paper core enabled; " + npcs.status() + ". Citizens="
                    + Bukkit.getPluginManager().isPluginEnabled("Citizens"));
            msg(sender, "Players " + Bukkit.getOnlinePlayers().size() + ", active duty=" + duties.size() + ", downed="
                    + downed.size() + ". AI and autonomous driving require external verified bridges.");
            return true;
        }
        if (action.equals("promotion")) {
            if (a.length == 3 && a[1].equalsIgnoreCase("approve")) {
                if (!sender.hasPermission("sdcraft.admin")) {
                    err(sender, "Admin approval required");
                    return true;
                }
                Player target = Bukkit.getPlayerExact(a[2]);
                if (target == null || !ledger.exists(target.getUniqueId())) {
                    err(sender, "Registered player must be online for promotion approval");
                    return true;
                }
                if (!ledger.approvePromotion(target.getUniqueId(), sender.getName())) {
                    err(sender, "Promotion requirements not met: use /sdc promotion status " + target.getName());
                    return true;
                }
                msg(sender, "Approved " + target.getName() + " for rank " + ledger.rank(target.getUniqueId()));
                target.sendMessage("§a[SD Craft] Your promotion to rank " + ledger.rank(target.getUniqueId())
                        + " was approved by " + sender.getName() + ".");
                return true;
            }
            if (a.length == 1 || a.length >= 2 && a[1].equalsIgnoreCase("status")) {
                Player target;
                if (a.length >= 3) {
                    if (!sender.hasPermission("sdcraft.admin")) {
                        err(sender, "Admin only");
                        return true;
                    }
                    target = Bukkit.getPlayerExact(a[2]);
                } else target = sender instanceof Player p ? p : null;
                if (target == null || !ledger.exists(target.getUniqueId())) {
                    err(sender, "Registered player must be online");
                    return true;
                }
                UUID uid = target.getUniqueId();
                int rank = ledger.rank(uid);
                if (rank >= 7) msg(sender, target.getName() + " is at maximum rank 7.");
                else msg(sender, target.getName() + " rank " + rank + " -> " + (rank + 1)
                        + ": " + ledger.credits(uid) + "/" + Ledger.requiredCreditsForRank(rank + 1)
                        + " credits, " + ledger.dutyMs(uid) / 3_600_000L + "/"
                        + Ledger.requiredDutyMsForRank(rank + 1) / 3_600_000L
                        + " verified duty hours; " + (ledger.eligibleForPromotion(uid) ? "awaiting admin approval" : "requirements incomplete"));
                return true;
            }
            err(sender, "Use /sdc promotion status [online-player] or /sdc promotion approve <online-player>");
            return true;
        }
        if (action.equals("fees")) {
            msg(sender,
                    "Stabilization free; diagnosis $25, treatment $50, admission $75; taxi $25+$6/100 blocks; bus $15; metro $10.");
            return true;
        }
        if (action.equals("map")) {
            if (sender instanceof Player p) {
                gps.sendMapPrompt(p);
            } else {
                msg(sender, "SD Craft 3D Web Map: " + getConfig().getString("map.web-url", "http://localhost:8100"));
            }
            return true;
        }
        if (action.equals("gps")) {
            if (a.length >= 3 && a[1].equalsIgnoreCase("give")) {
                if (!sender.hasPermission("sdcraft.admin")) {
                    err(sender, "Admin only");
                    return true;
                }
                Player target = Bukkit.getPlayer(a[2]);
                if (target == null) {
                    err(sender, "Player not found");
                    return true;
                }
                target.getInventory().addItem(gps.createGpsItem());
                msg(sender, "Gave SD Craft GPS Navigator to " + target.getName());
                target.sendMessage("§a[SD Craft] Received SD Craft GPS Navigator");
                return true;
            }
            if (sender instanceof Player p) {
                gps.openGpsMenu(p);
            } else {
                msg(sender, "GPS navigation menu is for players in-game.");
            }
            return true;
        }
        if (action.equals("spawn")) {
            if (sender instanceof Player p) {
                Location surfaceSpawn = getSurfaceSpawn(p.getWorld());
                p.teleport(surfaceSpawn);
                p.sendMessage("§a[SD Craft] §eTeleported to City Hall Plaza surface.");
                p.playSound(surfaceSpawn, Sound.ENTITY_ENDERMAN_TELEPORT, 0.7f, 1.2f);
            } else {
                msg(sender, "In-game only");
            }
            return true;
        }
        if (action.equals("car") || action.equals("vehicle")) {
            if (sender instanceof Player p) gta.handleStandaloneCar(p, Arrays.copyOfRange(a, 1, a.length));
            return true;
        }
        if (action.equals("kit") || action.equals("starter")) {
            if (sender instanceof Player p) {
                grantStarterKit(p, true);
                p.sendMessage("§a[SD Craft] §eStarter GTA roleplay kit claimed!");
                p.playSound(p.getLocation(), Sound.ENTITY_PLAYER_LEVELUP, 1.0f, 1.2f);
            } else {
                msg(sender, "In-game only");
            }
            return true;
        }
        if (action.equals("pack") || action.equals("resourcepack")) {
            if (sender instanceof Player p) {
                p.sendMessage("§e================ §6[ SD CRAFT 3D RESOURCE PACK ] §e================");
                p.sendMessage("§fFor vehicles, guns, phone, cash and metro tickets:");
                p.sendMessage("§aInstall §bresourcepacks/SDCraft_Unified_26.3_CityPack.zip §afrom the server files.");
                p.sendMessage("§7Drop the ZIP into your §f.minecraft/resourcepacks §7folder and enable it.");
                p.sendMessage("§e============================================================");
                p.playSound(p.getLocation(), Sound.UI_BUTTON_CLICK, 0.8f, 1.2f);
            } else {
                msg(sender, "Resource pack: resourcepacks/SDCraft_Unified_26.3_CityPack.zip");
            }
            return true;
        }
        if (action.equals("npcs")) {
            msg(sender, "Named NPCs: " + String.join(", ", npcs.ids()));
            return true;
        }
        if (action.equals("npc")) {
            if (a.length < 2) {
                err(sender, "Use /sdc npc <id>");
                return true;
            }
            if (!npcs.known(a[1])) {
                err(sender, "NPC ID missing");
                return true;
            }
            if (sender instanceof Player p)
                openNpc(p, a[1]);
            else
                msg(sender, npcs.name(a[1]) + " (" + npcs.role(a[1]) + ", skin=" + npcs.skin(a[1]) + " ["
                        + npcs.model(a[1]) + "]): " + npcs.greeting(a[1], "en"));
            return true;
        }
        if (action.equals("setnpc")) {
            if (!sender.hasPermission("sdcraft.admin") || !(sender instanceof Player p)) {
                err(sender, "Admin player only");
                return true;
            }
            if (a.length < 2 || !npcs.known(a[1])) {
                err(sender, "Use /sdc setnpc <validNpcId>");
                return true;
            }
            npcs.setAnchor(a[1], p.getLocation());
            msg(sender, "NPC anchor saved. Physical NPC activates within 64 blocks of a player.");
            npcs.tick();
            return true;
        }
        if (action.equals("setsite")) {
            if (!sender.hasPermission("sdcraft.admin") || !(sender instanceof Player p)) {
                err(sender, "Admin player only");
                return true;
            }
            if (a.length < 2 || !a[1].matches("[a-zA-Z0-9_]{2,30}")) {
                err(sender, "/sdc setsite <hospital|taxi_stop|metro_stop|bus_stop|bank|<department>>");
                return true;
            }
            setSite(a[1], p.getLocation());
            msg(sender, "Verified site " + a[1] + " saved at your feet.");
            return true;
        }
        if (!(sender instanceof Player p)) {
            err(sender, "This command is for players.");
            return true;
        }
        UUID id = p.getUniqueId();
        if (!ledger.exists(id)) {
            err(sender, "Account not initialized. Reconnect.");
            return true;
        }
        if (action.equals("account")) {
            msg(sender,
                    "Wallet " + PolicyEngine.money(ledger.wallet(id)) + " | Bank " + PolicyEngine.money(ledger.bank(id))
                            + " | rank " + ledger.rank(id) + " | career credits " + ledger.credits(id));
            msg(sender, "Use /sdc promotion to see rank requirements and approval status.");
            return true;
        }
        if (action.equals("language")) {
            if (a.length != 2) {
                err(sender, "/sdc language en|hi");
                return true;
            }
            ledger.language(id, a[1]);
            msg(sender, "Language changed to " + a[1]);
            return true;
        }
        if (action.equals("pin")) {
            if (a.length != 2 || !a[1].equalsIgnoreCase("set")) {
                err(sender, "/sdc pin set (opens a private clickable keypad; never type the PIN into chat)");
                return true;
            }
            openPin(p, "set");
            return true;
        }
        if (action.equals("bank")) {
            if (a.length < 3) {
                err(sender, "/sdc bank deposit|withdraw <amount> OR transfer <player> <amount>");
                return true;
            }
            String method = a[1].toLowerCase(Locale.ROOT);
            if (method.equals("deposit")) {
                if (!near(p, "bank", 12)) {
                    err(sender, "Visit the verified bank location.");
                    return true;
                }
                long v = dollars(a[2]);
                pending.put(id, new Pending("deposit", "", v, System.currentTimeMillis() + 30000, ""));
                msg(sender, "Deposit " + PolicyEngine.money(v) + "? /sdc confirm");
                return true;
            }
            if (method.equals("withdraw")) {
                if (!near(p, "bank", 12)) {
                    err(sender, "Visit the verified bank location.");
                    return true;
                }
                long v = dollars(a[2]);
                pending.put(id, new Pending("withdraw", "", v, System.currentTimeMillis() + 30000, ""));
                msg(sender, "Withdraw " + PolicyEngine.money(v) + "? /sdc confirm <PIN>");
                return true;
            }
            if (method.equals("transfer")) {
                if (a.length != 4) {
                    err(sender, "/sdc bank transfer <online-player> <amount>");
                    return true;
                }
                Player target = Bukkit.getPlayerExact(a[2]);
                if (target == null || !ledger.exists(target.getUniqueId())) {
                    err(sender, "Recipient must be online with a verified account");
                    return true;
                }
                long v = dollars(a[3]);
                pending.put(id, new Pending("transfer", target.getUniqueId().toString(), v,
                        System.currentTimeMillis() + 30000, target.getName()));
                msg(sender, "Transfer " + PolicyEngine.money(v) + " to " + target.getName() + "? /sdc confirm <PIN>");
                return true;
            }
            err(sender, "/sdc bank deposit|withdraw|transfer");
            return true;
        }
        if (action.equals("cancel")) {
            pending.remove(id);
            msg(sender, "Pending transaction cancelled.");
            return true;
        }
        if (action.equals("confirm")) {
            Pending x = pending.get(id);
            if (x == null || x.expires < System.currentTimeMillis()) {
                pending.remove(id);
                err(sender, "No valid pending action");
                return true;
            }
            if (x.kind.equals("withdraw") || x.kind.equals("transfer")) {
                if (!ledger.hasPin(id)) {
                    err(sender, "Set your private PIN using /sdc pin set");
                    return true;
                }
                openPin(p, "verify");
                return true;
            }
            executePending(p);
            return true;
        }
        if (action.equals("medical")) {
            if (a.length < 2) {
                err(sender, "/sdc medical stabilize|diagnosis|treatment|admission");
                return true;
            }
            String op = a[1].toLowerCase(Locale.ROOT);
            if (!near(p, "hospital", 16)) {
                err(sender, "Use the verified hospital station.");
                return true;
            }
            if (op.equals("stabilize")) {
                p.setHealth(Math.max(p.getHealth(), 6));
                msg(sender, "Emergency stabilization is free.");
                return true;
            }
            int dollars = switch (op) {
                case "diagnosis" -> 25;
                case "treatment" -> 50;
                case "admission" -> 75;
                default -> -1;
            };
            if (dollars < 0) {
                err(sender, "Unknown service");
                return true;
            }
            pending.put(id, new Pending("medical", op, dollars * 100L, System.currentTimeMillis() + 30000, ""));
            msg(sender, "Confirm " + op + " for $" + dollars + " using /sdc confirm. Care takes 20–60 seconds.");
            return true;
        }
        if (action.equals("revive")) {
            if (a.length < 2) {
                err(sender, "/sdc revive <online-player>");
                return true;
            }
            if (!sender.hasPermission("sdcraft.medic") && !sender.hasPermission("sdcraft.admin")) {
                err(sender, "Medic authorization required");
                return true;
            }
            Player victim = Bukkit.getPlayerExact(a[1]);
            if (victim == null || !downed.containsKey(victim.getUniqueId()) || !victim.getWorld().equals(p.getWorld())
                    || victim.getLocation().distanceSquared(p.getLocation()) > 36) {
                err(sender, "No nearby downed player");
                return true;
            }
            downed.remove(victim.getUniqueId());
            victim.setInvulnerable(false);
            victim.setHealth(Math.min(victim.getMaxHealth(), 10.0));
            victim.sendMessage("§a[SD Craft] Revived by medic " + p.getName());
            msg(sender, "Verified revival completed.");
            return true;
        }
        if (action.equals("work")) {
            if (a.length < 3 || !a[1].equalsIgnoreCase("join")) {
                err(sender, "/sdc work join <taxi|retail|delivery|chef|police|medic|firefighter|metro|maintenance>");
                return true;
            }
            String profession = a[2].toLowerCase(Locale.ROOT);
            if (!List.of("taxi", "retail", "delivery", "chef", "police", "medic", "firefighter", "metro", "maintenance")
                    .contains(profession)) {
                err(sender, "Unknown profession");
                return true;
            }
            if (List.of("police", "medic", "firefighter").contains(profession)
                    && !sender.hasPermission("sdcraft.profession." + profession)) {
                err(sender, "Sensitive profession needs admin permission");
                return true;
            }
            String k = "players." + id + ".profession";
            data.set(k, profession);
            safeSave();
            msg(sender, "Registered role: " + profession + ". Clock in at verified duty station with /sdc duty in.");
            return true;
        }
        if (action.equals("duty")) {
            if (a.length < 2) {
                err(sender, "/sdc duty in|out|status");
                return true;
            }
            String op = a[1].toLowerCase(Locale.ROOT);
            if (op.equals("out")) {
                clockOut(id, "clock out");
                return true;
            }
            if (op.equals("status")) {
                Duty d = duties.get(id);
                msg(sender, d == null ? "Off duty"
                        : "On duty " + d.profession + ", verified " + d.creditedMs / 1000 + " seconds");
                return true;
            }
            if (op.equals("in")) {
                if (duties.containsKey(id)) {
                    err(sender, "Already on duty");
                    return true;
                }
                String role = data.getString("players." + id + ".profession", "");
                if (role.isBlank() || !near(p, role, 16)) {
                    err(sender, "Register a profession and clock in at its verified department station.");
                    return true;
                }
                long now = System.currentTimeMillis();
                duties.put(id, new Duty(role, shiftOf(p.getWorld()), now));
                msg(sender, "Clocked in as " + role + ". Pay proportionate to verified non-AFK active time.");
                return true;
            }
        }
        if (action.equals("taxi") || action.equals("ride")) {
            String mode = action.equals("taxi") ? "taxi" : (a.length > 1 ? a[1].toLowerCase(Locale.ROOT) : "");
            String destination = action.equals("taxi") ? (a.length > 1 ? a[1] : "") : (a.length > 2 ? a[2] : "");
            if (!List.of("taxi", "bus", "metro").contains(mode)) {
                err(sender, "/sdc taxi <verified-stop> OR /sdc ride <bus|metro> <verified-stop>");
                return true;
            }
            Location target = site(destination);
            if (target == null || !target.getWorld().equals(p.getWorld())) {
                err(sender, "Unknown verified stop. Admin sets via /sdc setsite <id>");
                return true;
            }
            long cents = mode.equals("taxi") ? PolicyEngine.taxiQuoteCents(Math.round(p.getLocation().distance(target)))
                    : mode.equals("bus") ? 1500L : 1000L;
            pending.put(id, new Pending(mode, destination, cents, System.currentTimeMillis() + 30000, ""));
            msg(sender, mode + " to " + destination + " fare " + PolicyEngine.money(cents)
                    + ". /sdc confirm. Simulated transport fallback when vehicle bridge unavailable.");
            return true;
        }
        if (action.equals("report")) {
            if (a.length < 3) {
                err(sender, "/sdc report <1|2|3> <description>");
                return true;
            }
            int severity = Integer.parseInt(a[1]);
            if (severity < 1 || severity > 3)
                throw new IllegalArgumentException("Severity 1–3 only");
            long now = System.currentTimeMillis();
            if (now - lastReport.getOrDefault(id, 0L) < 60000L) {
                err(sender, "Report cooldown 60 seconds");
                return true;
            }
            lastReport.put(id, now);
            String desc = String.join(" ", Arrays.copyOfRange(a, 2, Math.min(a.length, 15)));
            String incident = UUID.randomUUID().toString().substring(0, 8);
            data.set("incidents." + incident + ".reporter", id.toString());
            data.set("incidents." + incident + ".severity", severity);
            data.set("incidents." + incident + ".description", desc);
            data.set("incidents." + incident + ".status", "reported");
            safeSave();
            msg(sender, "SDPD incident #" + incident + " reported, level " + severity
                    + "; evidence and investigation required before arrest.");
            for (Player other : Bukkit.getOnlinePlayers())
                if (other.hasPermission("sdcraft.police"))
                    other.sendMessage("§c[SDPD] Level " + severity + " incident #" + incident + " near " + p.getName()
                            + ". " + desc);
            return true;
        }
        if (action.equals("rob")) {
            if (!getConfig().getBoolean("crime.robbery-enabled", false)) {
                err(sender, "Cash robbery intentionally locked until approved protected zones are configured.");
                return true;
            }
            err(sender,
                    "Validated armed robbery requires the crime-zone integration and is not enabled by this build. No unverified money is stolen.");
            return true;
        }
        if (action.equals("surrender")) {
            msg(sender,
                    "You offered to surrender. Police arrest still requires a verified incident, evidence and a 15-second surrender opportunity.");
            return true;
        }
        if (action.equals("talk")) {
            if (a.length < 3 || !npcs.known(a[1])) {
                err(sender, "/sdc talk <npc-id> <message>");
                return true;
            }
            ai.speak(p, a[1], npcs.name(a[1]), npcs.role(a[1]), npcs.dept(a[1]), ledger.language(id),
                    String.join(" ", Arrays.copyOfRange(a, 2, a.length)), npcs.greeting(a[1], ledger.language(id)));
            return true;
        }
        if (action.equals("mission")) {
            msg(sender,
                    "Mission definitions are included in missions.yml. Verified multi-stage objectives require site calibration and an external mission executor; no credits are awarded for an unverified objective.");
            return true;
        }
        if (action.equals("zone")) {
            if (!sender.hasPermission("sdcraft.admin")) {
                err(sender, "Admin player only");
                return true;
            }
            if (a.length >= 3 && a[1].equalsIgnoreCase("mark")) {
                int rad = a.length >= 4 ? Integer.parseInt(a[3]) : 50;
                restoration.markZone(a[2], p.getLocation(), rad);
                msg(sender, "Marked restorable city zone '" + a[2] + "' (radius " + rad
                        + "m). Street damage here restores after 5 minutes.");
                return true;
            }
            if (a.length >= 3 && a[1].equalsIgnoreCase("unmark")) {
                boolean ok = restoration.unmarkZone(a[2]);
                msg(sender, ok ? "Removed restorable zone '" + a[2] + "'" : "Zone not found");
                return true;
            }
            if (a.length >= 2 && a[1].equalsIgnoreCase("list")) {
                var list = restoration.getZones();
                msg(sender, list.isEmpty() ? "No custom zones. City default active for Y>=55."
                        : "Restorable zones: " + list.stream().map(z -> z.name() + "(r=" + z.radius() + ")").toList());
                return true;
            }
            err(sender, "/sdc zone mark <name> [radius] | unmark <name> | list");
            return true;
        }
        if (action.equals("restore")) {
            if (a.length >= 2 && a[1].equalsIgnoreCase("now")) {
                if (!sender.hasPermission("sdcraft.admin")) {
                    err(sender, "Admin only");
                    return true;
                }
                int done = restoration.forceRestoreAll();
                msg(sender, "Force-restored " + done + " street blocks immediately.");
                return true;
            }
            msg(sender, "5-Minute Auto-Regeneration: " + restoration.getPendingCount()
                    + " street blocks in queue awaiting restoration.");
            return true;
        }
        if (action.equals("gun")) {
            if (!sender.hasPermission("sdcraft.admin")) {
                err(sender, "Admin only");
                return true;
            }
            if (a.length < 3 || !a[1].equalsIgnoreCase("give")) {
                err(sender, "/sdc gun give <player> <pistol|shotgun|smg|rifle>");
                return true;
            }
            Player target = Bukkit.getPlayer(a[2]);
            if (target == null) {
                err(sender, "Player not found");
                return true;
            }
            String gType = a.length >= 4 ? a[3].toUpperCase(Locale.ROOT) : "PISTOL";
            try {
                GunEngine.GunType gt = GunEngine.GunType.valueOf(gType);
                target.getInventory().addItem(guns.createGun(gt));
                msg(sender, "Gave " + gt.displayName + " to " + target.getName());
                target.sendMessage("§a[SD Craft] Received " + gt.displayName);
            } catch (Exception ex) {
                err(sender, "Unknown gun type. Choose: PISTOL, SHOTGUN, SMG, RIFLE");
            }
            return true;
        }
        if (action.equals("ammo")) {
            if (!sender.hasPermission("sdcraft.admin")) {
                err(sender, "Admin only");
                return true;
            }
            if (a.length < 3 || !a[1].equalsIgnoreCase("give")) {
                err(sender, "/sdc ammo give <player> <9mm|shotgun|rifle> [count]");
                return true;
            }
            Player target = Bukkit.getPlayer(a[2]);
            if (target == null) {
                err(sender, "Player not found");
                return true;
            }
            String aType = a.length >= 4 ? a[3].toLowerCase(Locale.ROOT) : "9mm";
            String fullType = switch (aType) {
                case "9mm" -> "9mm_ammo";
                case "shotgun" -> "shotgun_shells";
                case "rifle" -> "rifle_ammo";
                default -> aType;
            };
            int count = a.length >= 5 ? Integer.parseInt(a[4]) : 32;
            target.getInventory().addItem(guns.createAmmo(fullType, count));
            msg(sender, "Gave " + count + "x " + fullType + " to " + target.getName());
            target.sendMessage("§a[SD Craft] Received " + count + "x service ammunition");
            return true;
        }
        err(sender, "Unknown command. " + commandHelp());
        return true;
    }

    @Override
    public List<String> onTabComplete(CommandSender who, Command cmd, String alias, String[] args) {
        if (args.length == 1)
            return Arrays.asList("map", "gps", "spawn", "car", "kit", "gun", "pack", "help", "status", "account", "promotion", "language", "bank", "pin", "confirm", "cancel", "npcs",
                    "npc", "setnpc", "setsite", "duty", "work", "medical", "revive", "report", "taxi", "ride", "rob",
                    "mission", "talk", "fees", "surrender", "zone", "restore", "gun", "ammo");
        if (args.length == 2 && args[0].equalsIgnoreCase("gps"))
            return Arrays.asList("give");
        if (args.length == 2 && args[0].equalsIgnoreCase("promotion"))
            return who.hasPermission("sdcraft.admin") ? Arrays.asList("status", "approve") : Arrays.asList("status");
        if (args.length == 2 && (args[0].equalsIgnoreCase("npc") || args[0].equalsIgnoreCase("setnpc")
                || args[0].equalsIgnoreCase("talk")))
            return new ArrayList<>(npcs.ids());
        if (args.length == 2 && args[0].equalsIgnoreCase("language"))
            return Arrays.asList("en", "hi");
        if (args.length == 2 && args[0].equalsIgnoreCase("bank"))
            return Arrays.asList("deposit", "withdraw", "transfer");
        if (args.length == 2 && args[0].equalsIgnoreCase("zone"))
            return Arrays.asList("mark", "unmark", "list");
        if (args.length == 2 && args[0].equalsIgnoreCase("restore"))
            return Arrays.asList("status", "now");
        if (args.length == 2 && args[0].equalsIgnoreCase("gun"))
            return Arrays.asList("give");
        if (args.length == 2 && args[0].equalsIgnoreCase("ammo"))
            return Arrays.asList("give");
        if (args.length == 4 && args[0].equalsIgnoreCase("gun"))
            return Arrays.asList("pistol", "shotgun", "smg", "rifle");
        if (args.length == 4 && args[0].equalsIgnoreCase("ammo"))
            return Arrays.asList("9mm", "shotgun", "rifle");
        return Collections.emptyList();
    }
}
