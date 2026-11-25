/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  net.kyori.adventure.text.Component
 *  net.milkbowl.vault.economy.Economy
 *  org.bukkit.Bukkit
 *  org.bukkit.GameRules
 *  org.bukkit.Location
 *  org.bukkit.Material
 *  org.bukkit.NamespacedKey
 *  org.bukkit.Sound
 *  org.bukkit.World
 *  org.bukkit.command.Command
 *  org.bukkit.command.CommandExecutor
 *  org.bukkit.command.CommandSender
 *  org.bukkit.command.TabCompleter
 *  org.bukkit.configuration.ConfigurationSection
 *  org.bukkit.configuration.file.YamlConfiguration
 *  org.bukkit.entity.Entity
 *  org.bukkit.entity.HumanEntity
 *  org.bukkit.entity.Player
 *  org.bukkit.event.EventHandler
 *  org.bukkit.event.EventPriority
 *  org.bukkit.event.Listener
 *  org.bukkit.event.block.Action
 *  org.bukkit.event.entity.EntityDamageEvent
 *  org.bukkit.event.inventory.InventoryClickEvent
 *  org.bukkit.event.player.PlayerInteractEntityEvent
 *  org.bukkit.event.player.PlayerInteractEvent
 *  org.bukkit.event.player.PlayerJoinEvent
 *  org.bukkit.event.player.PlayerMoveEvent
 *  org.bukkit.event.player.PlayerQuitEvent
 *  org.bukkit.event.player.PlayerResourcePackStatusEvent
 *  org.bukkit.event.player.PlayerResourcePackStatusEvent$Status
 *  org.bukkit.event.player.PlayerRespawnEvent
 *  org.bukkit.event.player.PlayerSwapHandItemsEvent
 *  org.bukkit.inventory.Inventory
 *  org.bukkit.inventory.ItemStack
 *  org.bukkit.inventory.PlayerInventory
 *  org.bukkit.inventory.meta.ItemMeta
 *  org.bukkit.persistence.PersistentDataContainer
 *  org.bukkit.persistence.PersistentDataType
 *  org.bukkit.plugin.Plugin
 *  org.bukkit.plugin.ServicePriority
 *  org.bukkit.plugin.java.JavaPlugin
 *  org.bukkit.util.BoundingBox
 */
package com.sdcraft.core;

import com.sdcraft.core.AiService;
import com.sdcraft.core.AtomicYamlStore;
import com.sdcraft.core.CityItems;
import com.sdcraft.core.CreativeArsenalManager;
import com.sdcraft.core.GpsManager;
import com.sdcraft.core.GtaEngine;
import com.sdcraft.core.GtmAlcohol;
import com.sdcraft.core.GtmAssetShop;
import com.sdcraft.core.GtmAuthentication;
import com.sdcraft.core.GtmCityModels;
import com.sdcraft.core.GtmCityServices;
import com.sdcraft.core.GtmCivicTerminals;
import com.sdcraft.core.GtmControlCentre;
import com.sdcraft.core.GtmDialogue;
import com.sdcraft.core.GtmEquipment;
import com.sdcraft.core.GtmFinishes;
import com.sdcraft.core.GtmFood;
import com.sdcraft.core.GtmFoodCourier;
import com.sdcraft.core.GtmFurniture;
import com.sdcraft.core.GtmFurnitureMenu;
import com.sdcraft.core.GtmItemDelivery;
import com.sdcraft.core.GtmLoans;
import com.sdcraft.core.GtmNativeFinishes;
import com.sdcraft.core.GtmPhoneApps;
import com.sdcraft.core.GtmProperties;
import com.sdcraft.core.GtmServiceWorkers;
import com.sdcraft.core.GtmSigns;
import com.sdcraft.core.GtmTaxi;
import com.sdcraft.core.GtmVehicleServices;
import com.sdcraft.core.GtmVehicles;
import com.sdcraft.core.GtmWardrobe;
import com.sdcraft.core.GunEngine;
import com.sdcraft.core.Ledger;
import com.sdcraft.core.MedicalRecovery;
import com.sdcraft.core.NpcService;
import com.sdcraft.core.PolicyEngine;
import com.sdcraft.core.RestorationEngine;
import com.sdcraft.core.VaultWallet;
import com.sdcraft.core.furniture.FurnitureCatalog;
import com.sdcraft.core.medical.NativeDownedState;
import com.sdcraft.core.vehicle.LocalOwnerCommissioning;
import com.sdcraft.core.vehicle.RoadVehicleProfile;
import com.sdcraft.core.vehicle.TaxiRoutes;
import com.sdcraft.core.vehicle.VehicleGeometry;
import java.io.File;
import java.io.IOException;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.TreeSet;
import java.util.UUID;
import java.util.function.BiPredicate;
import java.util.function.Function;
import net.kyori.adventure.text.Component;
import net.milkbowl.vault.economy.Economy;
import org.bukkit.Bukkit;
import org.bukkit.GameRules;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.Sound;
import org.bukkit.World;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabCompleter;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Entity;
import org.bukkit.entity.HumanEntity;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.entity.EntityDamageEvent;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.player.PlayerInteractEntityEvent;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerMoveEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.event.player.PlayerResourcePackStatusEvent;
import org.bukkit.event.player.PlayerRespawnEvent;
import org.bukkit.event.player.PlayerSwapHandItemsEvent;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.PlayerInventory;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataContainer;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.Plugin;
import org.bukkit.plugin.ServicePriority;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.util.BoundingBox;

public final class SDCraftCorePlugin
extends JavaPlugin
implements Listener,
CommandExecutor,
TabCompleter {
    private Ledger ledger;
    private GtmItemDelivery itemDelivery;
    private MedicalRecovery medicalRecovery;
    private GtmAuthentication authentication;
    private AiService ai;
    private GtmDialogue gtmDialogue;
    private GtmCityModels cityModels;
    private GtmVehicles vehicles;
    private GtmFurniture furniture;
    private GtmFurnitureMenu furnitureMenu;
    private GtmAssetShop assetShop;
    private GtmVehicleServices vehicleServices;
    private GtmCivicTerminals civicTerminals;
    private GtmCityServices cityServices;
    private GtmEquipment equipment;
    private GtmNativeFinishes nativeFinishes;
    private GtmWardrobe wardrobe;
    private GtmPhoneApps phoneApps;
    private GtmClientHud clientHud;
    private GtmWebConsole webConsole;
    private GtmSigns signs;
    private GtmServiceWorkers serviceWorkers;
    private GtmTaxi taxi;
    private GtmFoodCourier foodCourier;
    private GtmControlCentre festivals;
    private final Set<UUID> loadedPacks = new HashSet<UUID>();
    private int assetRetrySeconds;
    private GtmLoans gtmLoans;
    private GtmProperties gtmProperties;
    private GtmFood gtmFood;
    private GtmAlcohol alcohol;
    private NpcService npcs;
    private RestorationEngine restoration;
    private GunEngine guns;
    private GpsManager gps;
    private GtaEngine gta;
    private VaultWallet vaultWallet;
    private CreativeArsenalManager arsenal;
    private YamlConfiguration dialogues;
    private YamlConfiguration data;
    private AtomicYamlStore runtimeStore;
    private final Map<UUID, Pending> pending = new HashMap<UUID, Pending>();
    private final Map<UUID, Duty> duties = new HashMap<UUID, Duty>();
    private final Map<UUID, NativeDownedState> downed = new HashMap<UUID, NativeDownedState>();
    private final Set<UUID> downedWarnings = new HashSet<UUID>();
    private final Map<UUID, Long> activeAt = new HashMap<UUID, Long>();
    private final Map<UUID, Long> lastReport = new HashMap<UUID, Long>();
    private final Map<UUID, Deque<Long>> aiRate = new HashMap<UUID, Deque<Long>>();
    private final Map<UUID, String> guiNpc = new HashMap<UUID, String>();
    private final Map<UUID, String> pinMode = new HashMap<UUID, String>();
    private final Map<UUID, StringBuilder> pinDigits = new HashMap<UUID, StringBuilder>();

    public void onEnable() {
        try {
            this.initialize();
        }
        catch (LinkageError | RuntimeException failure) {
            this.getLogger().severe("GTM startup failed (" + failure.getClass().getSimpleName() + "). Stopping this server to prevent gameplay without its account protection. Existing records were not replaced.");
            Bukkit.shutdown();
        }
    }

    private void initialize() {
        this.saveDefaultConfig();
        if (!new File(this.getDataFolder(), "npc-dialogues.yml").isFile()) {
            this.saveResource("npc-dialogues.yml", false);
        }
        if (!new File(this.getDataFolder(), "missions.yml").isFile()) {
            this.saveResource("missions.yml", false);
        }
        this.dialogues = YamlConfiguration.loadConfiguration((File)new File(this.getDataFolder(), "npc-dialogues.yml"));
        try {
            this.runtimeStore = new AtomicYamlStore(this.getDataFolder().toPath().resolve("runtime.yml"));
        }
        catch (IOException ex) {
            throw new IllegalStateException("Runtime records unavailable", ex);
        }
        this.data = this.runtimeStore.data();
        this.ledger = new Ledger(this.getDataFolder());
        this.itemDelivery = new GtmItemDelivery(this, this.ledger);
        this.gtmFood = new GtmFood(this, this.ledger);
        try {
            this.alcohol = new GtmAlcohol(this);
        }
        catch (IOException failure) {
            throw new IllegalStateException("Fictional drink state unavailable", failure);
        }
        Bukkit.getPluginManager().registerEvents((Listener)this.gtmFood, (Plugin)this);
        Objects.requireNonNull(this.getCommand("gtmfood")).setExecutor((sender, command, label, args) -> {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                this.gtmFood.open(p, args.length == 0 ? "zomatoo" : args[0].toLowerCase(Locale.ROOT));
            }
            return true;
        });
        this.gtmLoans = new GtmLoans(this, this.ledger);
        Bukkit.getPluginManager().registerEvents((Listener)this.gtmLoans, (Plugin)this);
        this.gtmProperties = new GtmProperties(this, this.ledger);
        Bukkit.getPluginManager().registerEvents((Listener)this.gtmProperties, (Plugin)this);
        Objects.requireNonNull(this.getCommand("gtmproperty")).setExecutor((sender, command, label, args) -> {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                this.gtmProperties.open(p);
            }
            return true;
        });
        Objects.requireNonNull(this.getCommand("gtmloan")).setExecutor((sender, command, label, args) -> {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                this.gtmLoans.open(p);
            }
            return true;
        });
        if (this.getConfig().getBoolean("economy.vault-provider-enabled", true) && Bukkit.getPluginManager().isPluginEnabled("Vault")) {
            this.vaultWallet = new VaultWallet(this.ledger, this::isAuthenticated);
            Bukkit.getServicesManager().register(Economy.class, this.vaultWallet, (Plugin)this, ServicePriority.High);
            this.getLogger().info("VaultUnlocked economy provider registered: SD Craft wallet.");
            Bukkit.getScheduler().runTask((Plugin)this, () -> {
                if (Bukkit.getPluginManager().isPluginEnabled("MTVehicles")) {
                    Bukkit.dispatchCommand((CommandSender)Bukkit.getConsoleSender(), (String)"mtv vault setup");
                }
            });
        }
        try {
            this.cityModels = new GtmCityModels(this);
            Objects.requireNonNull(this.getCommand("gtmassets")).setExecutor((CommandExecutor)this.cityModels);
            Bukkit.getPluginManager().registerEvents((Listener)this.cityModels, (Plugin)this);
            if (this.getConfig().getBoolean("gtm.experimental-furnishings")) {
                Bukkit.getScheduler().runTaskTimer((Plugin)this, this.cityModels::refresh, 40L, 60L);
            }
        }
        catch (IOException ex) {
            this.getLogger().severe("City model catalogue unavailable: " + ex.getClass().getSimpleName());
        }
        Objects.requireNonNull(this.getCommand("gtmcontrol")).setExecutor((sender, command, label, args) -> {
            sender.sendMessage("GTM Control Centre is unavailable.");
            return true;
        });
        if (this.getConfig().getBoolean("gtm.experimental-festivals", false)) {
            try {
                GtmControlCentre centre;
                this.festivals = centre = new GtmControlCentre(this, this.cityModels);
                Objects.requireNonNull(this.getCommand("gtmcontrol")).setExecutor((CommandExecutor)centre);
                Bukkit.getPluginManager().registerEvents((Listener)centre, (Plugin)this);
                Bukkit.getScheduler().runTaskTimer((Plugin)this, centre::pulse, 40L, 40L);
            }
            catch (IOException | IllegalArgumentException ex) {
                this.getLogger().severe("Festival state unavailable. Control Centre disabled: " + ex.getClass().getSimpleName());
            }
        }
        this.ai = new AiService(this);
        this.restoration = new RestorationEngine(this);
        this.guns = new GunEngine(this);
        GtmFinishes finishes = new GtmFinishes(this, this.ledger, this.guns);
        Bukkit.getPluginManager().registerEvents((Listener)finishes, (Plugin)this);
        Objects.requireNonNull(this.getCommand("gtmfinish")).setExecutor((sender, command, label, args) -> {
            if (sender instanceof Player) {
                Player player = (Player)sender;
                finishes.open(player, 0, null);
            }
            return true;
        });
        this.gps = new GpsManager(this);
        this.gta = new GtaEngine(this, this.ledger, this.gps);
        this.arsenal = new CreativeArsenalManager(this, this.ledger, this.gps, this.gta, this.guns);
        this.npcs = new NpcService(this, this.dialogues, this.ledger, this.gta);
        try {
            this.authentication = new GtmAuthentication(this, this.ledger::exists, this::onAuthenticated, this::onAuthenticationLost);
        }
        catch (IOException ex) {
            throw new IllegalStateException("Authentication storage unavailable; refusing unauthenticated gameplay", ex);
        }
        Bukkit.getPluginManager().registerEvents((Listener)this.authentication, (Plugin)this);
        this.medicalRecovery = new MedicalRecovery(this, this.ledger);
        Bukkit.getPluginManager().registerEvents((Listener)this.medicalRecovery, (Plugin)this);
        this.initializeOwnedAssets();
        this.initializeNativeInteractions();
        for (String name : List.of("register", "login", "logout", "changepassword", "gtmauth")) {
            Objects.requireNonNull(this.getCommand(name)).setExecutor((CommandExecutor)this.authentication);
            Objects.requireNonNull(this.getCommand(name)).setTabCompleter((TabCompleter)this.authentication);
        }
        Objects.requireNonNull(this.getCommand("sdcraft")).setExecutor((CommandExecutor)this);
        Objects.requireNonNull(this.getCommand("sdcraft")).setTabCompleter((TabCompleter)this);
        for (String c : List.of("map", "gps", "spawn", "car", "kit", "gun", "pack", "phone", "arsenal", "creativemenu", "testitems", "testing")) {
            if (this.getCommand(c) == null) continue;
            Objects.requireNonNull(this.getCommand(c)).setExecutor((CommandExecutor)this);
            Objects.requireNonNull(this.getCommand(c)).setTabCompleter((TabCompleter)this);
        }
        Bukkit.getPluginManager().registerEvents((Listener)this, (Plugin)this);
        Bukkit.getPluginManager().registerEvents((Listener)this.restoration, (Plugin)this);
        Bukkit.getPluginManager().registerEvents((Listener)this.guns, (Plugin)this);
        Bukkit.getPluginManager().registerEvents((Listener)this.gta, (Plugin)this);
        Bukkit.getPluginManager().registerEvents((Listener)this.npcs, (Plugin)this);
        this.gtmDialogue = new GtmDialogue(this, this.npcs, this.ledger, this.ai);
        Bukkit.getPluginManager().registerEvents((Listener)this.gtmDialogue, (Plugin)this);
        this.gtmDialogue.start();
        World mainWorld = Bukkit.getWorld((String)this.getConfig().getString("world.name", "world"));
        if (mainWorld != null) {
            if (this.getConfig().getBoolean("world.apply-city-spawn", false)) {
                mainWorld.setSpawnLocation(this.getSurfaceSpawn(mainWorld));
            }
            mainWorld.setGameRule(GameRules.ADVANCE_TIME, false);
        }
        for (World w : Bukkit.getWorlds()) {
            if (!w.getName().equals(this.getConfig().getString("world.name", "world"))) continue;
            w.setGameRule(GameRules.ADVANCE_TIME, false);
        }
        Bukkit.getScheduler().runTaskTimer((Plugin)this, this::second, 20L, 20L);
        Bukkit.getScheduler().runTaskTimer((Plugin)this, () -> this.npcs.tick(), 100L, 20L);
        Bukkit.getScheduler().runTaskTimer((Plugin)this, () -> this.npcs.pulse(), 120L, 10L);
        for (Player player : Bukkit.getOnlinePlayers()) {
            this.authentication.begin(player);
        }
        if (this.getConfig().getBoolean("web-console.enabled", true)) {
            try { this.webConsole = new GtmWebConsole(this); }
            catch (IOException | RuntimeException unavailable) { getLogger().warning("Local Control Centre unavailable: " + unavailable.getClass().getSimpleName()); }
        }
        if (getCommand("gtmweb") != null) getCommand("gtmweb").setExecutor((sender, command, label, args) -> {
            if (!(sender instanceof Player player)) {
                sender.sendMessage("Open the local Control Centre with Open-Control-Centre.bat. Its private token is in plugins/SDCraftCore/console-access.token.");
                return true;
            }
            if (!requireAuthenticated(player) || !player.hasPermission("sdcraft.admin")) return true;
            if (webConsole == null) { player.sendMessage("Control Centre is unavailable; check the server log."); return true; }
            player.sendMessage(Component.text("Open GTM Control Centre")
                .color(net.kyori.adventure.text.format.NamedTextColor.GOLD)
                .clickEvent(net.kyori.adventure.text.event.ClickEvent.openUrl(webConsole.ownerUrl())));
            return true;
        });
        this.getLogger().info("SDCraftCore loaded: secure ledger, NPC service, transport, crime, medical and duty workflows. Check README for limitations.");
    }

    public void onDisable() {
        if (clientHud != null) this.shutdownPart("optional client HUD", clientHud::close);
        if (ai != null) this.shutdownPart("NPC conversation backend", ai::close);
        if (webConsole != null) this.shutdownPart("local control centre", webConsole::close);
        Bukkit.getServicesManager().unregisterAll((Plugin)this);
        for (UUID id : new ArrayList<UUID>(this.duties.keySet())) {
            this.clockOut(id, "server stop");
        }
        if (this.phoneApps != null) {
            this.shutdownPart("phone state", this.phoneApps::close);
        }
        if (this.alcohol != null) {
            this.shutdownPart("fictional drink state", this.alcohol::close);
        }
        if (this.signs != null) {
            this.shutdownPart("owned signs", this.signs::close);
        }
        if (this.equipment != null) {
            this.shutdownPart("equipment", this.equipment::close);
        }
        if (this.taxi != null) {
            this.shutdownPart("taxi", this.taxi::close);
        }
        if (this.foodCourier != null) {
            this.shutdownPart("food couriers", this.foodCourier::close);
        }
        if (this.vehicles != null) {
            this.shutdownPart("owned vehicles", this.vehicles::close);
        }
        if (this.serviceWorkers != null) {
            this.shutdownPart("service workers", this.serviceWorkers::close);
        }
        if (this.furniture != null) {
            this.shutdownPart("owned furniture", this.furniture::close);
        }
        if (this.cityModels != null) {
            this.shutdownPart("models", this.cityModels::close);
        }
        if (this.gtmDialogue != null) {
            this.shutdownPart("dialogue", this.gtmDialogue::close);
        }
        if (this.gtmLoans != null) {
            this.shutdownPart("loans", this.gtmLoans::close);
        }
        if (this.npcs != null) {
            this.shutdownPart("population", this.npcs::close);
        }
        if (this.gta != null) {
            this.shutdownPart("mission state", this.gta::close);
        }
        if (this.authentication != null) {
            this.shutdownPart("authentication", this.authentication::close);
        }
        if (this.runtimeStore != null) {
            this.shutdownPart("runtime state", this::safeSave);
        }
    }

    private void shutdownPart(String name, Runnable close) {
        try {
            close.run();
        }
        catch (RuntimeException ex) {
            this.getLogger().severe("Shutdown checkpoint failed for " + name + ": " + ex.getClass().getSimpleName());
        }
    }

    private void initializeOwnedAssets() {
        this.civicTerminals = new GtmCivicTerminals(this, this.ledger, (player, action) -> {
            if (!this.requireAuthenticated((Player)player)) {
                return;
            }
            if (action.kind().equals("pin")) {
                this.openPin((Player)player, "set");
                return;
            }
            if (action.kind().equals("withdraw") && !this.ledger.hasPin(player.getUniqueId())) {
                player.sendMessage("\u00a7eSet your private bank PIN, then reopen the ATM to withdraw.");
                this.openPin((Player)player, "set");
                return;
            }
            this.pending.put(player.getUniqueId(), new Pending(action.kind(), "", action.cents(), System.currentTimeMillis() + 30000L, "ATM"));
            if (action.kind().equals("withdraw")) {
                this.openPin((Player)player, "verify");
            } else {
                try {
                    this.executePending((Player)player);
                }
                catch (IOException failure) {
                    this.getLogger().warning("ATM operation failed: " + failure.getClass().getSimpleName());
                    player.sendMessage("\u00a7cBank storage is unavailable. The transaction could not be completed.");
                }
            }
        });
        Bukkit.getPluginManager().registerEvents((Listener)this.civicTerminals, (Plugin)this);
        HashSet<String> services = new HashSet<String>(GtmCityServices.SERVICES);
        for (String service : this.getConfig().getStringList("furniture.services")) {
            if (service.equals("bank")) {
                services.add(service);
            }
            if (!service.equals("food") || !this.getConfig().getBoolean("gtm.experimental-food", false) || this.site("food_zomatoo") == null) continue;
            services.add(service);
        }
        try {
            this.furniture = new GtmFurniture(this, new GtmFurniture.Options(this.getConfig().getBoolean("furniture.enabled", false), this.getConfig().getInt("furniture.max-per-owner", 32), this.getConfig().getInt("furniture.max-global", 2048), this.getConfig().getInt("furniture.max-per-chunk", 64), this.getConfig().getDouble("furniture.interaction-distance", 6.0), services), new GtmFurniture.Access(){

                @Override
                public boolean authenticated(Player player) {
                    return SDCraftCorePlugin.this.isAuthenticated(player);
                }

                @Override
                public boolean ownerMayBuild(UUID owner, World world, BoundingBox bounds) {
                    return SDCraftCorePlugin.this.gtmProperties.mayBuildFurniture(owner, world, bounds);
                }

                @Override
                public boolean mayEnter(Player player, World world, BoundingBox bounds) {
                    return SDCraftCorePlugin.this.gtmProperties.mayEnter(player, world, bounds);
                }

                @Override
                public boolean serviceEnabled(String service) {
                    return SDCraftCorePlugin.this.cityServices != null && SDCraftCorePlugin.this.cityServices.enabled(service);
                }

                @Override
                public Optional<String> serviceUnavailable(Player player, String service) {
                    return SDCraftCorePlugin.this.cityServices != null && SDCraftCorePlugin.this.cityServices.available(player, service) ? Optional.empty() : Optional.of("The " + service.replace('_', ' ') + " service needs an enabled runtime, your permission and an accessible commissioned location; no payment is accepted.");
                }

                @Override
                public boolean service(Player player, String service, Location location) {
                    return SDCraftCorePlugin.this.cityServices != null && SDCraftCorePlugin.this.cityServices.open(player, service, location);
                }
            });
            this.vehicles = new GtmVehicles(this, new GtmVehicles.Options(this.getConfig().getBoolean("vehicles.enabled", false), this.getConfig().getBoolean("vehicles.all-road-models", false), this.getConfig().getInt("vehicles.max-loaded", 16), this.getConfig().getInt("vehicles.max-per-owner", 8), this.getConfig().getInt("vehicles.block-check-budget", 16384)), this.gtmProperties::mayEnter);
        }
        catch (IOException ex) {
            throw new IllegalStateException("Owned asset records unavailable; refusing to replace ownership", ex);
        }
        this.assetShop = new GtmAssetShop(this, this.ledger, new GtmAssetShop.Target(){

            @Override
            public boolean available(Player player) {
                return SDCraftCorePlugin.this.vehicles.enabled() && SDCraftCorePlugin.this.isAuthenticated(player) && player.hasPermission("gtm.vehicles.use");
            }

            @Override
            public List<GtmAssetShop.Product> products() {
                return SDCraftCorePlugin.this.vehicles.catalog().all().stream().filter(p -> SDCraftCorePlugin.this.vehicles.isPurchasable(p.id())).map(p -> {
                    String s0$;
                    String string = p.id();
                    String string2 = p.title();
                    String string3 = s0$ = p.id();
                    int tmp1$ = -1;
                    switch (s0$.hashCode()) {
                        case 103586220: {
                            if (!s0$.equals("gtm:rickshaw_traditional")) break;
                            tmp1$ = 0;
                            break;
                        }
                        case -72265928: {
                            if (!s0$.equals("gtm:rickshaw_electric")) break;
                            tmp1$ = 1;
                            break;
                        }
                        case 1009187713: {
                            if (!s0$.equals("gtm:rickshaw_cargo")) break;
                            tmp1$ = 2;
                        }
                    }
                    return new GtmAssetShop.Product(string, string2, SDCraftCorePlugin.this.nativePrice("vehicles", string3, switch (tmp1$) {
                        case 0 -> 60000L;
                        case 1 -> 80000L;
                        case 2 -> 90000L;
                        default -> 150000L;
                    }), List.of("\u00a77" + p.seats().size() + " seats \u2022 " + String.valueOf((Object)p.energy()), "\u00a77Owned, parked and saved to your account"));
                }).toList();
            }

            @Override
            public void validate(Player player, String id) {
                SDCraftCorePlugin.this.vehicles.validateAcquisition(player, id);
            }

            @Override
            public void grant(UUID grant, UUID owner, String id) throws IOException {
                SDCraftCorePlugin.this.vehicles.grant(grant, owner, id);
            }

            @Override
            public void openOwned(Player player) {
                SDCraftCorePlugin.this.vehicles.openGarage(player);
            }
        }, new GtmAssetShop.Target(){

            @Override
            public boolean available(Player player) {
                return SDCraftCorePlugin.this.getConfig().getBoolean("furniture.enabled", false) && SDCraftCorePlugin.this.isAuthenticated(player) && player.hasPermission("gtm.furniture");
            }

            @Override
            public List<GtmAssetShop.Product> products() {
                return SDCraftCorePlugin.this.furniture.catalog().entries().stream().filter(e -> SDCraftCorePlugin.this.furniture.isPurchasable(e.assetId())).map(e -> {
                    String string = e.assetId();
                    String string2 = e.title();
                    String string3 = e.assetId();
                    return new GtmAssetShop.Product(string, string2, SDCraftCorePlugin.this.nativePrice("furniture", string3, switch (e.behavior()) {
                        case FurnitureCatalog.Behavior.SEAT -> 7500L;
                        case FurnitureCatalog.Behavior.STORAGE -> 12500L;
                        case FurnitureCatalog.Behavior.BED -> 17500L;
                        case FurnitureCatalog.Behavior.LIGHT -> 5000L;
                        case FurnitureCatalog.Behavior.CRAFTING -> 10000L;
                        case FurnitureCatalog.Behavior.SERVICE -> 25000L;
                        default -> 10000L;
                    }), List.of("\u00a77" + e.description(), "\u00a77Placement requires your own property"));
                }).toList();
            }

            @Override
            public void validate(Player player, String id) {
                SDCraftCorePlugin.this.furniture.validateAcquisition(player, id);
            }

            @Override
            public void grant(UUID grant, UUID owner, String id) throws IOException {
                SDCraftCorePlugin.this.furniture.grant(grant, owner, id);
            }

            @Override
            public void openOwned(Player player) {
                SDCraftCorePlugin.this.furnitureMenu.open(player);
            }
        });
        this.furnitureMenu = new GtmFurnitureMenu(this, this.furniture, player -> this.assetShop.open((Player)player, "furniture"));
        this.vehicleServices = new GtmVehicleServices(this, this.ledger, this.vehicles);
        Bukkit.getPluginManager().registerEvents((Listener)this.furniture, (Plugin)this);
        Bukkit.getPluginManager().registerEvents((Listener)this.furnitureMenu, (Plugin)this);
        Bukkit.getPluginManager().registerEvents((Listener)this.assetShop, (Plugin)this);
        Bukkit.getPluginManager().registerEvents((Listener)this.vehicleServices, (Plugin)this);
        Objects.requireNonNull(this.getCommand("furniture")).setExecutor((sender, command, label, args) -> {
            Player player;
            if (!(sender instanceof Player) || !this.requireAuthenticated(player = (Player)sender)) {
                return true;
            }
            if (args.length == 0 || args[0].equalsIgnoreCase("owned")) {
                this.assetShop.retry(player);
                this.furnitureMenu.open(player);
            } else if (args[0].equalsIgnoreCase("shop") || args[0].equalsIgnoreCase("buy")) {
                this.assetShop.open(player, "furniture");
            } else {
                this.furniture.onCommand(sender, command, label, args);
            }
            return true;
        });
        this.vehicles.setObstacleProvider(this.furniture::collisionBoxes);
        this.vehicles.setVolumeAccess(this.gtmProperties::mayEnter);
        this.vehicles.setCargoOwnership((player, world, bounds) -> this.gtmProperties.mayBuildFurniture(player.getUniqueId(), world, bounds));
        this.vehicles.setWorkshopAccess(this.furniture.workshop());
        this.vehicles.setSignalPolicy(new GtmVehicles.SignalPolicy(){

            @Override
            public boolean brake(World world, VehicleGeometry.Pose from, VehicleGeometry.Pose to, RoadVehicleProfile profile, double speed) {
                return SDCraftCorePlugin.this.furniture.signals().brake(world, from, to, profile, speed);
            }

            @Override
            public boolean blocks(World world, VehicleGeometry.Pose from, VehicleGeometry.Pose to, RoadVehicleProfile profile) {
                return SDCraftCorePlugin.this.furniture.signals().blocks(world, from, to, profile);
            }
        });
        this.vehicles.setArticulationEnabled(this.getConfig().getBoolean("vehicles.articulation-enabled", false));
        this.vehicles.setInstrumentHud(player -> this.phoneApps != null && this.phoneApps.available((Player)player) && this.phoneApps.preferences(player.getUniqueId()).hud());
        this.vehicles.setTransportOptions(new GtmVehicles.TransportOptions(this.getConfig().getBoolean("vehicles.transport.water", false), this.getConfig().getBoolean("vehicles.transport.air", false), this.getConfig().getBoolean("vehicles.transport.rail", false), this.getConfig().getBoolean("vehicles.transport.ropeway", false), this.getConfig().getInt("vehicles.transport.max-routes", 32), this.getConfig().getInt("vehicles.transport.max-altitude", 160)));
        this.vehicles.setOwnerCommissioning(LocalOwnerCommissioning.configured(this.getConfig().getBoolean("vehicles.local-owner-commissioning.enabled", false), this.getConfig().getString("local-playtest.profile", ""), this.getConfig().getBoolean("furniture.allow-public-staging-placement", false), this.getConfig().getMapList("vehicles.local-owner-commissioning.regions")));
        this.vehicles.start();
        if (this.getConfig().getBoolean("furniture.enabled", false)) {
            Bukkit.getScheduler().runTaskTimer((Plugin)this, this.furniture::tick, 10L, 10L);
        }
    }

    private void initializeNativeInteractions() {
        try {
            this.serviceWorkers = new GtmServiceWorkers(this);
            this.taxi = new GtmTaxi(this, this.ledger, this.vehicles);
            this.foodCourier = new GtmFoodCourier(this, this.ledger, this.gtmFood, this.vehicles);
            this.cityServices = new GtmCityServices(this, this.ledger);
            this.equipment = new GtmEquipment(this, this.ledger, new GtmEquipment.Services(){

                @Override
                public boolean available(Player p, String service) {
                    return SDCraftCorePlugin.this.cityServices.available(p, service);
                }

                @Override
                public boolean open(Player p, String service) {
                    return SDCraftCorePlugin.this.cityServices.open(p, service, null);
                }

                @Override
                public boolean safeZone(Location at) {
                    return SDCraftCorePlugin.this.gta.isSafeZone(at);
                }

                @Override
                public void crime(Player p, String reason) {
                    SDCraftCorePlugin.this.gta.recordCrime(p, 1, reason);
                }
            });
            this.nativeFinishes = new GtmNativeFinishes(this, this.ledger, this.equipment);
            this.wardrobe = new GtmWardrobe(this, this.ledger);
            this.phoneApps = new GtmPhoneApps(this, new GtmPhoneApps.Services(){

                @Override
                public GtmPhoneApps.Gate gate(Player p, GtmPhoneApps.Action action) {
                    return SDCraftCorePlugin.this.cityServices.gate(p, action);
                }

                @Override
                public void open(Player p, GtmPhoneApps.Action action) throws Exception {
                    SDCraftCorePlugin.this.cityServices.openAction(p, action);
                }

                @Override
                public List<GtmPhoneApps.Destination> destinations(Player p) {
                    return SDCraftCorePlugin.this.commissionedDestinations(p);
                }

                @Override
                public String district(Player p) {
                    return SDCraftCorePlugin.this.gps.getDistrict(p.getLocation());
                }

                @Override
                public boolean inCity(Player p) {
                    return p.getWorld().getName().equals(SDCraftCorePlugin.this.getConfig().getString("world.name", "world"));
                }

                @Override
                public int wanted(Player p) {
                    return SDCraftCorePlugin.this.gta.wantedLevel(p.getUniqueId());
                }

                @Override
                public long wallet(Player p) {
                    return SDCraftCorePlugin.this.ledger.wallet(p.getUniqueId());
                }

                @Override
                public long bank(Player p) {
                    return SDCraftCorePlugin.this.ledger.bank(p.getUniqueId());
                }

                @Override
                public Optional<GtmPhoneApps.DriveData> driving(Player p) {
                    return SDCraftCorePlugin.this.vehicles.telemetry(p).map(t -> new GtmPhoneApps.DriveData(t.title(), t.mode(), t.blocksPerSecond(), t.energyKind(), t.energyPercent(), t.health(), t.estimatedRange(), t.occupiedSeats(), t.seats()));
                }

                @Override
                public List<String> traffic(Player p) {
                    List<String> nearby = SDCraftCorePlugin.this.vehicles.nearbyTelemetry(p, 96.0).stream().limit(18L).map(t -> String.format(Locale.ROOT, "%s \u00b7 %s \u00b7 %.1f blocks/s", t.title(), t.mode(), Math.abs(t.blocksPerSecond()))).toList();
                    return nearby.isEmpty() ? List.of("No active accessible native vehicles within96 blocks.") : nearby;
                }

                @Override
                public List<Location> route(Player p, GtmPhoneApps.Destination destination) {
                    return SDCraftCorePlugin.this.commissionedMapRoute(p, destination);
                }

                @Override
                public GtmPhoneApps.Gate vehicleControlGate(Player p, String control) {
                    return SDCraftCorePlugin.this.vehicles.enabled() && SDCraftCorePlugin.this.isAuthenticated(p) && p.hasPermission("gtm.vehicles.use") ? GtmPhoneApps.Gate.ready() : GtmPhoneApps.Gate.blocked("Vehicle controls require an authenticated native vehicle owner or authorized driver.");
                }

                @Override
                public void vehicleControl(Player p, String control) throws Exception {
                    SDCraftCorePlugin.this.vehicles.useControl(p, control);
                }

                @Override
                public boolean glyphsAvailable(Player p) {
                    return SDCraftCorePlugin.this.loadedPacks.contains(p.getUniqueId()) && !SDCraftCorePlugin.this.bedrockPlayer(p.getUniqueId());
                }
            });
            this.signs = new GtmSigns(this, new GtmSigns.Options(this.getConfig().getBoolean("signs.enabled", false), this.getConfig().getInt("signs.max-per-owner", 16), this.getConfig().getInt("signs.max-global", 512), this.getConfig().getInt("signs.max-loaded", 64), this.getConfig().getInt("signs.max-per-chunk", 16), this.getConfig().getDouble("signs.reach", 6.0)), new GtmSigns.Access(){

                @Override
                public boolean ownerMayBuild(UUID owner, World world, BoundingBox bounds) {
                    return SDCraftCorePlugin.this.gtmProperties.mayBuildFurniture(owner, world, bounds);
                }

                @Override
                public boolean mayEnter(Player p, World world, BoundingBox bounds) {
                    return SDCraftCorePlugin.this.gtmProperties.mayEnter(p, world, bounds);
                }
            }, this.phoneApps);
            for (Listener listener : List.of(this.cityServices, this.equipment, this.nativeFinishes, this.wardrobe, this.phoneApps, this.signs, this.taxi)) {
                Bukkit.getPluginManager().registerEvents(listener, (Plugin)this);
            }
            Objects.requireNonNull(this.getCommand("equipment")).setExecutor((sender, command, label, args) -> {
                if (sender instanceof Player) {
                    Player p = (Player)sender;
                    this.equipment.open(p);
                }
                return true;
            });
            Objects.requireNonNull(this.getCommand("wardrobe")).setExecutor((sender, command, label, args) -> {
                if (sender instanceof Player) {
                    Player p = (Player)sender;
                    this.wardrobe.open(p);
                }
                return true;
            });
            Objects.requireNonNull(this.getCommand("gtmsigns")).setExecutor((sender, command, label, args) -> {
                if (sender instanceof Player) {
                    Player p = (Player)sender;
                    this.signs.open(p);
                }
                return true;
            });
            Objects.requireNonNull(this.getCommand("taxiroute")).setExecutor((CommandExecutor)this.taxi);
            Objects.requireNonNull(this.getCommand("foodroute")).setExecutor((CommandExecutor)this.foodCourier);
            this.phoneApps.start();
            if (getConfig().getBoolean("phone.client-hud-enabled", true)) {
                this.clientHud = new GtmClientHud(this, this.phoneApps);
            }
            this.signs.start();
            this.taxi.start();
            this.foodCourier.start();
        }
        catch (IOException failure) {
            throw new IllegalStateException("Native interaction records unavailable; refusing to replace player data", failure);
        }
    }

    List<GtmPhoneApps.Destination> commissionedDestinations(Player player) {
        ConfigurationSection section = this.data.getConfigurationSection("sites");
        if (!this.isAuthenticated(player)) {
            return List.of();
        }
        ArrayList<GtmPhoneApps.Destination> result = new ArrayList<GtmPhoneApps.Destination>();
        for (String id : new TreeSet<String>(section == null ? Set.of() : section.getKeys(false))) {
            Location at;
            if (result.size() >= 256) break;
            if (!id.matches("[a-z0-9_]{1,96}") || (at = this.site(id)) == null || !this.gtmProperties.mayEnter(player, at)) continue;
            String category = id.startsWith("food_") ? "food" : (id.contains("metro") || id.contains("rail") || id.contains("taxi") || id.contains("bus") ? "transport" : "city");
            result.add(new GtmPhoneApps.Destination(id, id.replace('_', ' '), category, at));
        }
        if (this.taxi != null) {
            for (TaxiRoutes.Route route : this.taxi.routes().all()) {
                TaxiRoutes.Point end;
                Location at;
                if (result.size() >= 256) break;
                World world = Bukkit.getWorld((UUID)route.world());
                if (world == null || !this.gtmProperties.mayEnter(player, at = new Location(world, (end = route.points().getLast()).x(), end.y(), end.z()))) continue;
                result.add(new GtmPhoneApps.Destination("taxi_route:" + route.id(), route.title(), "transport", at));
            }
        }
        return List.copyOf(result);
    }

    private List<Location> commissionedMapRoute(Player player, GtmPhoneApps.Destination destination) {
        TaxiRoutes.Point first;
        if (this.taxi == null || !this.isAuthenticated(player) || !destination.id().startsWith("taxi_route:")) {
            return List.of();
        }
        TaxiRoutes.Route route = this.taxi.routes().find(destination.id().substring("taxi_route:".length())).orElse(null);
        if (route == null || !route.world().equals(player.getWorld().getUID())) {
            return List.of();
        }
        World world = player.getWorld();
        Location origin = new Location(world, (first = route.points().getFirst()).x(), first.y(), first.z());
        if (origin.distanceSquared(player.getLocation()) > 64.0) {
            return List.of();
        }
        List<Location> points = route.drivingPoints().stream().map(p -> new Location(world, p.x(), p.y(), p.z())).toList();
        for (Location point : points) {
            if (world.isChunkLoaded(point.getBlockX() >> 4, point.getBlockZ() >> 4) && this.gtmProperties.mayEnter(player, point)) continue;
            return List.of();
        }
        return points;
    }

    private boolean bedrockPlayer(UUID player) {
        try {
            Class<?> type = Class.forName("org.geysermc.floodgate.api.FloodgateApi");
            Object api = type.getMethod("getInstance", new Class[0]).invoke(null, new Object[0]);
            return Boolean.TRUE.equals(type.getMethod("isFloodgatePlayer", UUID.class).invoke(api, player));
        }
        catch (LinkageError | ReflectiveOperationException unavailable) {
            try {
                Class<?> geyser = Class.forName("org.geysermc.geyser.api.GeyserApi");
                Object api = geyser.getMethod("api").invoke(null);
                return geyser.getMethod("connectionByUuid", UUID.class).invoke(api, player) != null;
            } catch (LinkageError | ReflectiveOperationException noConnectionApi) { return false; }
        }
    }

    @EventHandler
    public void resourcePack(PlayerResourcePackStatusEvent event) {
        org.bukkit.packs.ResourcePack expected = getServer().getServerResourcePack();
        if (expected == null || !expected.getId().equals(event.getID())) return;
        if (event.getStatus() == PlayerResourcePackStatusEvent.Status.SUCCESSFULLY_LOADED) {
            this.loadedPacks.add(event.getPlayer().getUniqueId());
            showRepairWelcome(event.getPlayer());
        } else if (event.getStatus() != PlayerResourcePackStatusEvent.Status.ACCEPTED && event.getStatus() != PlayerResourcePackStatusEvent.Status.DOWNLOADED) {
            this.loadedPacks.remove(event.getPlayer().getUniqueId());
        }
    }

    private long nativePrice(String family, String asset, long fallback) {
        long price = this.getConfig().getLong(family + ".prices." + asset.substring(4), fallback);
        if (price <= 0L || price > 100000000000L) {
            throw new IllegalArgumentException("Invalid configured asset price");
        }
        return price;
    }

    private void grantNativeStarter(Player player) {
        if (!(this.vehicles != null && this.vehicles.enabled() && this.getConfig().getBoolean("vehicles.starter-auto", true) && player.hasPermission("gtm.vehicles.use"))) {
            return;
        }
        UUID grant = UUID.nameUUIDFromBytes(("gtm:starter-auto:v1:" + String.valueOf(player.getUniqueId())).getBytes(StandardCharsets.UTF_8));
        try {
            this.ledger.purchaseAsset(player.getUniqueId(), grant, "vehicle", "gtm:rickshaw_traditional", 0L);
            this.assetShop.retry(player);
        }
        catch (IOException | RuntimeException ex) {
            this.getLogger().warning("Starter auto remains pending for " + String.valueOf(player.getUniqueId()) + ": " + ex.getClass().getSimpleName());
        }
    }

    private void safeSave() {
        try {
            this.runtimeStore.commit();
        }
        catch (IOException ex) {
            throw new IllegalStateException("Runtime records could not be saved; action rolled back", ex);
        }
    }

    public Location getSurfaceSpawn(World world) {
        Location site;
        if (world == null && (world = Bukkit.getWorld((String)this.getConfig().getString("world.name", "world"))) == null && !Bukkit.getWorlds().isEmpty()) {
            world = (World)Bukkit.getWorlds().get(0);
        }
        if ((site = this.site("spawn")) != null && site.getWorld() != null) {
            return site;
        }
        if (world == null) {
            throw new IllegalStateException("No loaded world for safe spawn");
        }
        return world.getSpawnLocation();
    }

    boolean isManagedNpc(Entity entity) {
        return this.npcs != null && this.npcs.identify(entity) != null;
    }

    GtmServiceWorkers serviceWorkers() {
        return this.serviceWorkers;
    }

    int serviceWorkerCount() {
        return this.serviceWorkers == null ? 0 : this.serviceWorkers.count();
    }

    boolean hasServiceWorkerCapacity(int existing) {
        return this.npcs != null && this.npcs.canAddServiceWorker(existing);
    }

    boolean hasLoadedGtmPack(Player player) { return loadedPacks.contains(player.getUniqueId()); }

    boolean hasClientHud(Player player) { return clientHud != null && clientHud.active(player); }

    boolean openClientPhone(Player player) { return clientHud != null && clientHud.openPhone(player); }

    boolean isAttackableNpc(Entity entity) { return npcs != null && npcs.isAttackable(entity); }

    String npcDialogueStatus() { return ai == null ? "not-started" : ai.status(); }

    private void offerWeaponUpgrade(Player player) {
        try { GtmWeaponUpgrade.offer(this, player); }
        catch (RuntimeException failure) { getLogger().warning("Native weapon upgrade remains pending for " + player.getUniqueId() + ": " + failure.getClass().getSimpleName()); }
    }

    private void showRepairWelcome(Player player) {
        if (clientHud != null && clientHud.capable(player)) return;
        if (!isAuthenticated(player) || !hasLoadedGtmPack(player) || phoneApps == null || !phoneApps.available(player) || isDowned(player)) return;
        NamespacedKey seen = new NamespacedKey(this, "repair_ui_seen_v1");
        if (player.getPersistentDataContainer().has(seen, PersistentDataType.BYTE)) return;
        Bukkit.getScheduler().runTaskLater(this, () -> {
            if (clientHud != null && clientHud.capable(player)) return;
            if (!isAuthenticated(player) || !hasLoadedGtmPack(player) || !phoneApps.available(player) || isDowned(player)) return;
            if (player.getPersistentDataContainer().has(seen, PersistentDataType.BYTE)) return;
            // Do not interrupt another transaction menu, a vehicle ride or a login flow.
            if (player.isInsideVehicle() || player.getOpenInventory().getTopInventory().getType() != org.bukkit.event.inventory.InventoryType.CRAFTING) return;
            phoneApps.open(player);
            player.getPersistentDataContainer().set(seen, PersistentDataType.BYTE, (byte) 1);
            player.saveData();
        }, 40L);
    }

    public boolean isAuthenticated(Player player) {
        return this.authentication != null && !this.isManagedNpc((Entity)player) && this.authentication.authenticated(player);
    }

    public UUID authenticatedSession(Player player) {
        return this.isAuthenticated(player) ? this.authentication.session(player) : null;
    }

    boolean isDowned(Player player) {
        return player != null && (this.downed.containsKey(player.getUniqueId()) || player.getPersistentDataContainer().has(this.downedKey()));
    }

    private NamespacedKey downedKey() {
        return new NamespacedKey((Plugin)this, "medical_downed_episode");
    }

    private void downedWarning(Player player) {
        if (this.downedWarnings.add(player.getUniqueId())) {
            this.getLogger().warning("Native downed state needs review for " + String.valueOf(player.getUniqueId()) + "; retained without granting recovery");
            player.sendMessage("\u00a7eYour saved downed state needs staff review. It has been retained; no recovery or relocation was granted.");
        }
    }

    private void restoreDownedAfterAuthentication(Player player, long now) {
        if (!player.isOnline() || this.authenticatedSession(player) == null) {
            return;
        }
        PersistentDataContainer data = player.getPersistentDataContainer();
        UUID id = player.getUniqueId();
        if (!data.has(this.downedKey())) {
            if (this.downed.containsKey(id)) {
                this.downedWarning(player);
            }
            return;
        }
        try {
            NativeDownedState saved = NativeDownedState.read((String)data.get(this.downedKey(), PersistentDataType.STRING), now);
            NativeDownedState current = this.downed.putIfAbsent(id, saved);
            if (current != null && !current.equals(saved)) {
                this.downedWarning(player);
                return;
            }
            if (!player.isDead()) {
                player.setInvulnerable(true);
            }
        }
        catch (IllegalArgumentException invalid) {
            this.downedWarning(player);
        }
    }

    private NativeDownedState currentDowned(Player player, long now) {
        if (player == null || !player.isOnline() || this.authenticatedSession(player) == null) {
            return null;
        }
        NativeDownedState current = this.downed.get(player.getUniqueId());
        if (current == null) {
            return null;
        }
        try {
            NativeDownedState saved = NativeDownedState.read((String)player.getPersistentDataContainer().get(this.downedKey(), PersistentDataType.STRING), now);
            if (!current.equals(saved)) {
                this.downedWarning(player);
                return null;
            }
            return current;
        }
        catch (IllegalArgumentException invalid) {
            this.downedWarning(player);
            return null;
        }
    }

    UUID downedEpisode(Player patient) {
        NativeDownedState state = this.currentDowned(patient, System.currentTimeMillis());
        return state == null ? null : state.episode();
    }

    boolean canRevive(Player medic, Player patient, UUID selectedSession, UUID selectedEpisode) {
        long now = System.currentTimeMillis();
        NativeDownedState state = this.currentDowned(patient, now);
        return state != null && Objects.equals(selectedEpisode, state.episode()) && !this.isDowned(medic) && SDCraftCorePlugin.revivalEligible(medic, patient, selectedSession, state.until(), now, this::authenticatedSession, (person, box) -> this.gtmProperties != null && this.gtmProperties.mayEnter((Player)person, person.getWorld(), (BoundingBox)box));
    }

    static boolean revivalEligible(Player medic, Player patient, UUID selectedSession, long until, long now, Function<Player, UUID> sessions, BiPredicate<Player, BoundingBox> accessible) {
        if (medic == null || patient == null || medic.getUniqueId().equals(patient.getUniqueId()) || selectedSession == null || now < 0L || until <= now || !medic.isOnline() || !patient.isOnline() || medic.isDead() || patient.isDead() || !medic.hasPermission("sdcraft.medic") && !medic.hasPermission("sdcraft.admin") || sessions.apply(medic) == null || !selectedSession.equals(sessions.apply(patient)) || !medic.getWorld().equals((Object)patient.getWorld()) || medic.getLocation().distanceSquared(patient.getLocation()) > 36.0) {
            return false;
        }
        BoundingBox corridor = medic.getBoundingBox().clone().union(patient.getBoundingBox());
        World world = medic.getWorld();
        for (int x = (int)Math.floor(corridor.getMinX()) >> 4; x <= (int)Math.floor(Math.nextDown(corridor.getMaxX())) >> 4; ++x) {
            for (int z = (int)Math.floor(corridor.getMinZ()) >> 4; z <= (int)Math.floor(Math.nextDown(corridor.getMaxZ())) >> 4; ++z) {
                if (world.isChunkLoaded(x, z)) continue;
                return false;
            }
        }
        return accessible.test(medic, corridor) && accessible.test(patient, patient.getBoundingBox()) && medic.hasLineOfSight((Entity)patient);
    }

    void reviveNearby(Player medic, UUID target, UUID selectedSession, UUID selectedEpisode) {
        Player patient;
        if (!Bukkit.isPrimaryThread()) {
            throw new IllegalStateException("Native revival requires the server thread");
        }
        Player player = patient = target == null ? null : Bukkit.getPlayer((UUID)target);
        if (!this.canRevive(medic, patient, selectedSession, selectedEpisode)) {
            throw new IllegalStateException("Select a currently authenticated, visible downed patient within six blocks; current medic and property access are required");
        }
        NativeDownedState state = this.downed.get(target);
        this.completeDowned(patient, state);
        patient.sendMessage("\u00a7a[SD Craft] Revived by medic " + medic.getName());
        medic.sendMessage("\u00a7aVerified revival completed.");
    }

    private void completeDowned(Player patient, NativeDownedState state) {
        patient.setHealth(Math.min(patient.getMaxHealth(), 10.0));
        patient.setInvulnerable(state.priorInvulnerable());
        patient.getPersistentDataContainer().remove(this.downedKey());
        this.downed.remove(patient.getUniqueId(), state);
        this.downedWarnings.remove(patient.getUniqueId());
        try {
            patient.saveData();
        }
        catch (RuntimeException failure) {
            this.getLogger().warning("Completed native recovery player save failed for " + String.valueOf(patient.getUniqueId()));
        }
    }

    private void recoverExpiredDowned(long now) {
        for (UUID id : new ArrayList<UUID>(this.downed.keySet())) {
            Player patient = Bukkit.getPlayer((UUID)id);
            NativeDownedState state = this.currentDowned(patient, now);
            if (state == null || !state.recoveryDue(now) || patient.isDead()) continue;
            Location target = this.site("hospital");
            if (target == null) {
                target = patient.getWorld().getSpawnLocation();
            }
            if (!this.medicalRecovery.permittedArrival(patient, target)) continue;
            UUID session = this.authenticatedSession(patient);
            if (!patient.teleport(target.clone()) || session == null || !session.equals(this.authenticatedSession(patient)) || patient.isDead() || !state.equals(this.currentDowned(patient, now)) || !this.medicalRecovery.completedArrival(patient, target)) continue;
            this.completeDowned(patient, state);
            patient.sendMessage("\u00a7e[SD Craft] Transported to hospital fallback after the downed timer.");
        }
    }

    boolean requireAuthenticated(Player player) {
        if (this.isAuthenticated(player)) {
            return true;
        }
        if (this.authentication != null) {
            this.authentication.prompt(player);
        }
        return false;
    }

    private void openCityMap(Player player) {
        if (this.phoneApps != null && this.phoneApps.available(player)) {
            this.phoneApps.openPage(player, "maps");
        } else {
            this.gps.sendMapPrompt(player);
        }
    }

    public void grantStarterKit(Player p, boolean force) {
        boolean hasPhone;
        if (!this.requireAuthenticated(p)) {
            return;
        }
        PlayerInventory inv = p.getInventory();
        boolean hasGun = false;
        for (ItemStack it : inv.getContents()) {
            String dn;
            if (it == null || !it.hasItemMeta()) continue;
            if (it.getItemMeta().getPersistentDataContainer().has(this.guns.getKeyType(), PersistentDataType.STRING)) {
                hasGun = true;
                break;
            }
            String string = dn = it.getItemMeta().hasDisplayName() ? it.getItemMeta().getDisplayName().toLowerCase(Locale.ROOT) : "";
            if (!dn.contains("p30") && !dn.contains("pistol") && !dn.contains("gun") && it.getType() != Material.CROSSBOW) continue;
            hasGun = true;
            break;
        }
        if (!hasGun || force) {
            if (equipment != null && getConfig().getBoolean("equipment.enabled", false)) {
                GtmWeaponUpgrade.offer(this, p);
                inv.addItem(guns.createAmmo("9mm_ammo", 32));
                p.sendMessage("§6[GTM] §fKavach-9 native pistol and 32 matching rounds equipped.");
            } else {
                inv.addItem(new ItemStack[]{this.guns.createGun(GunEngine.GunType.PISTOL)});
                inv.addItem(new ItemStack[]{this.guns.createAmmo("9mm_ammo", 32)});
                p.sendMessage("\u00a7a[SD Craft] \u00a7e9mm Service Pistol & 32 rounds equipped!");
            }
        }
        boolean hasCar = false;
        for (ItemStack it : inv.getContents()) {
            String dName;
            if (it == null || !it.hasItemMeta() || !it.getItemMeta().hasDisplayName() || !(dName = it.getItemMeta().getDisplayName().toLowerCase(Locale.ROOT)).contains("sedan") && !dName.contains("car") && !dName.contains("vehicle") && !dName.contains("voucher")) continue;
            hasCar = true;
            break;
        }
        if (this.vehicles != null && this.vehicles.enabled()) {
            this.grantNativeStarter(p);
            p.sendMessage("\u00a7eOpen \u00a7f/car \u00a7efor your garage and auto-rickshaw controls.");
        } else if (!hasCar || force) {
            if (Bukkit.getPluginManager().isPluginEnabled("MTVehicles")) {
                Bukkit.dispatchCommand((CommandSender)Bukkit.getConsoleSender(), (String)("mtv givecar " + p.getName() + " FFW36Q"));
                p.sendMessage("\u00a7a[SD Craft] \u00a7eKeys to your personal Sedan Black delivered! Right-click road to place & drive.");
            } else {
                p.sendMessage("\u00a7e[Garage] Vehicle delivery is unavailable until a driving runtime is enabled.");
            }
        }
        boolean hasGps = false;
        for (ItemStack it : inv.getContents()) {
            if (it == null || it.getType() != Material.COMPASS || !it.hasItemMeta() || !it.getItemMeta().hasDisplayName() || !it.getItemMeta().getDisplayName().contains("GPS")) continue;
            hasGps = true;
            break;
        }
        if (!hasGps || force) {
            inv.addItem(new ItemStack[]{this.gps.createGpsItem()});
            p.sendMessage("\u00a7a[SD Craft] \u00a7bSD Craft GPS Navigator received! Right-click to open navigation.");
        }
        if (!(hasPhone = Arrays.stream(inv.getContents()).anyMatch(item -> CityItems.is(item, 900002)))) {
            inv.addItem(new ItemStack[]{CityItems.phone()});
        }
        boolean hasFood = false;
        for (ItemStack it : inv.getContents()) {
            if (it == null || it.getType() != Material.COOKED_BEEF && it.getType() != Material.BREAD) continue;
            hasFood = true;
            break;
        }
        if (!hasFood || force) {
            ItemStack burger = new ItemStack(Material.COOKED_BEEF, 16);
            ItemMeta bMeta = burger.getItemMeta();
            if (bMeta != null) {
                bMeta.setDisplayName("\u00a76Street Burger");
                bMeta.setLore(List.of("\u00a77Fresh city burger from local diner", "\u00a78Restores hunger and stamina."));
                burger.setItemMeta(bMeta);
            }
            inv.addItem(new ItemStack[]{burger});
        }
    }

    @EventHandler
    public void onJoin(PlayerJoinEvent e) {
        // Paper sends server.properties packs in the configuration phase,
        // before PlayerResourcePackStatusEvent can exist. Its final status is
        // transferred to Player on join (Paper #12866); seed the UI state here.
        // Subsequent play-phase events still check the configured pack UUID.
        org.bukkit.packs.ResourcePack configured = getServer().getServerResourcePack();
        if (configured != null && !configured.getUrl().isBlank() && e.getPlayer().hasResourcePack()) {
            loadedPacks.add(e.getPlayer().getUniqueId());
        }
        if (this.authentication != null) {
            this.authentication.begin(e.getPlayer());
        }
    }

    private void onAuthenticated(Player p) {
        if (!this.isAuthenticated(p)) {
            return;
        }
        UUID id = p.getUniqueId();
        this.activeAt.put(id, System.currentTimeMillis());
        boolean isFirstJoin = false;
        try {
            isFirstJoin = this.ledger.register(id);
            if (isFirstJoin) {
                p.sendMessage("\u00a7a[GTM] Welcome! ARK 500 in your wallet and ARK 1,000 in your protected bank.");
            }
        }
        catch (Exception ex) {
            this.getLogger().severe("ACCOUNT ERROR " + String.valueOf(id) + " " + ex.getMessage());
            p.kickPlayer("Account persistence is unavailable. Your existing account has not been replaced.");
            return;
        }
        this.restoreDownedAfterAuthentication(p, System.currentTimeMillis());
        if (this.alcohol != null) {
            this.alcohol.afterAuthentication(p);
        }
        if (!this.isDowned(p)) {
            this.medicalRecovery.afterAuthentication(p);
        }
        this.recoverExpiredDowned(System.currentTimeMillis());
        Location cur = p.getLocation();
        if (isFirstJoin) {
            Location surfaceSpawn = this.getSurfaceSpawn(p.getWorld());
            p.teleport(surfaceSpawn);
            p.sendTitle("\u00a76\u00a7lGTM", "\u00a7eWelcome to Indraprastha", 10, 70, 20);
            p.playSound(surfaceSpawn, Sound.UI_TOAST_CHALLENGE_COMPLETE, 0.8f, 1.0f);
            p.sendMessage("\u00a76[GTM] \u00a7aYou are at the city spawn. Open your phone for the map and city services.");
        }
        Bukkit.getScheduler().runTaskLater((Plugin)this, () -> {
            if (p.isOnline() && this.isAuthenticated(p)) {
                if (this.gta.tryClaimStarter(p)) {
                    this.grantStarterKit(p, false);
                }
                this.gta.onJoin(p);
                this.grantNativeStarter(p);
                this.assetShop.retry(p);
                this.vehicleServices.retry(p);
                this.furniture.reconcile(p);
                if (this.wardrobe != null) {
                    this.wardrobe.restore(p);
                }
                this.npcs.tick();
                offerWeaponUpgrade(p);
                showRepairWelcome(p);
                p.sendMessage("§6[GTM] §fYour phone opens city services. /gun opens native equipment; /car opens the garage.");
            }
        }, 15L);
    }

    @EventHandler
    public void onRespawn(PlayerRespawnEvent e) {
        if (!this.isAuthenticated(e.getPlayer())) {
            return;
        }
        if (!e.isBedSpawn() && !e.isAnchorSpawn()) {
            Location surfaceSpawn = this.getSurfaceSpawn(e.getPlayer().getWorld());
            e.setRespawnLocation(surfaceSpawn);
        }
    }

    @EventHandler
    public void onQuit(PlayerQuitEvent e) {
        this.loadedPacks.remove(e.getPlayer().getUniqueId());
        this.onAuthenticationLost(e.getPlayer());
        if (this.authentication != null) {
            this.authentication.end(e.getPlayer());
        }
    }

    private void onAuthenticationLost(Player player) {
        UUID id = player.getUniqueId();
        if (clientHud != null) clientHud.authenticationLost(player);
        if (gtmDialogue != null) gtmDialogue.authenticationLost(player);
        if (ai != null) ai.forget(player.getUniqueId());
        if (this.vehicles != null) {
            this.vehicles.onAuthenticationLost(player);
        }
        if (this.furniture != null) {
            this.furniture.onAuthenticationLost(player);
        }
        if (this.furnitureMenu != null) {
            this.furnitureMenu.onAuthenticationLost(player);
        }
        if (this.gtmFood != null) {
            this.gtmFood.onAuthenticationLost(player);
        }
        if (this.alcohol != null) {
            this.alcohol.authenticationLost(player);
        }
        if (this.equipment != null) {
            this.equipment.onAuthenticationLost(player);
        }
        if (this.nativeFinishes != null) {
            this.nativeFinishes.onAuthenticationLost(player);
        }
        if (this.wardrobe != null) {
            this.wardrobe.onAuthenticationLost(player);
        }
        if (this.phoneApps != null) {
            this.phoneApps.onAuthenticationLost(player);
        }
        if (this.signs != null) {
            this.signs.onAuthenticationLost(player);
        }
        if (this.cityServices != null) {
            this.cityServices.onAuthenticationLost(player);
        }
        if (this.taxi != null) {
            this.taxi.onAuthenticationLost(player);
        }
        if (this.assetShop != null) {
            this.assetShop.quit(player);
        }
        this.clockOut(id, "disconnect");
        if (this.gtmLoans != null) {
            this.gtmLoans.quit(player);
        }
        this.activeAt.remove(id);
        this.guiNpc.remove(id);
        this.pinMode.remove(id);
        this.pinDigits.remove(id);
        this.pending.remove(id);
    }

    @EventHandler
    public void onMove(PlayerMoveEvent e) {
        if (!this.isAuthenticated(e.getPlayer())) {
            return;
        }
        if (e.getTo() == null) {
            return;
        }
        if (e.getFrom().getBlockX() != e.getTo().getBlockX() || e.getFrom().getBlockZ() != e.getTo().getBlockZ() || e.getFrom().getBlockY() != e.getTo().getBlockY()) {
            this.activeAt.put(e.getPlayer().getUniqueId(), System.currentTimeMillis());
        }
    }

    @EventHandler
    public void onInteract(PlayerInteractEntityEvent e) {
        if (!this.isAuthenticated(e.getPlayer())) {
            e.setCancelled(true);
            return;
        }
        String id = this.npcs.identify(e.getRightClicked());
        if (id == null) {
            return;
        }
        e.setCancelled(true);
        if (e.getHand() != org.bukkit.inventory.EquipmentSlot.HAND) return;
        boolean conversation = this.gtmDialogue != null && this.gtmDialogue.select(e.getPlayer(), e.getRightClicked());
        if (this.npcs.isAmbient(id)) {
            if (!conversation) e.getPlayer().sendMessage("\u00a76" + this.npcs.name(id) + " \u00a77(" + this.npcs.role(id) + "): \u00a7f" + this.npcs.greeting(id, this.ledger.language(e.getPlayer().getUniqueId())));
            if (this.npcs.isMerchant(id) && !e.getPlayer().isSneaking()) {
                this.gta.handleNpcAction(e.getPlayer(), "view_catalog");
            }
            return;
        }
        if (!conversation || !e.getPlayer().isSneaking()) this.openNpc(e.getPlayer(), id);
    }

    @EventHandler
    public void onPlayerInteract(PlayerInteractEvent e) {
        if (!this.isAuthenticated(e.getPlayer())) {
            e.setCancelled(true);
            return;
        }
        if (e.getAction() == Action.RIGHT_CLICK_AIR || e.getAction() == Action.RIGHT_CLICK_BLOCK) {
            ItemStack item = e.getItem();
            if (CityItems.is(item, 900002)) {
                e.setCancelled(true);
                try {
                    this.gta.handleCommand(e.getPlayer(), "phone", new String[0]);
                }
                catch (Exception ex) {
                    this.err((CommandSender)e.getPlayer(), "Phone unavailable: " + ex.getMessage());
                }
                return;
            }
            if (item != null && item.getType() == Material.NETHER_STAR && item.hasItemMeta() && item.getItemMeta().hasDisplayName() && item.getItemMeta().getDisplayName().contains("Arsenal")) {
                e.setCancelled(true);
                if (this.arsenal != null && e.getPlayer().hasPermission("sdcraft.admin")) {
                    this.arsenal.openArsenal(e.getPlayer());
                }
                return;
            }
            if (item != null && item.getType() == Material.COMPASS && item.hasItemMeta() && item.getItemMeta().hasDisplayName() && item.getItemMeta().getDisplayName().contains("GPS")) {
                e.setCancelled(true);
                this.gps.openGpsMenu(e.getPlayer());
            }
        }
    }

    @EventHandler
    public void onSwapHands(PlayerSwapHandItemsEvent e) {
        if (!this.isAuthenticated(e.getPlayer())) {
            e.setCancelled(true);
            return;
        }
        ItemStack main = e.getMainHandItem();
        if (main != null && main.getType() == Material.COMPASS && main.hasItemMeta() && main.getItemMeta().hasDisplayName() && main.getItemMeta().getDisplayName().contains("GPS")) {
            e.setCancelled(true);
            Player p = e.getPlayer();
            String dist = this.gps.getDistrict(p.getLocation());
            p.sendActionBar((Component)Component.text((String)("\u00a76[GPS] \u00a7b" + dist + " \u00a77| \u00a7fX: " + p.getLocation().getBlockX() + " Y: " + p.getLocation().getBlockY() + " Z: " + p.getLocation().getBlockZ())));
            p.playSound(p.getLocation(), Sound.UI_BUTTON_CLICK, 0.6f, 1.4f);
        }
    }

    @EventHandler
    public void onInventory(InventoryClickEvent e) {
        HumanEntity clicked;
        Player player;
        HumanEntity humanEntity = e.getWhoClicked();
        if (humanEntity instanceof Player && (!this.isAuthenticated(player = (Player)humanEntity) || e.getView().getTitle().equals("\u00a76\u00a7lSD CRAFT \u00a78- \u00a7eTesting Arsenal") && !player.hasPermission("sdcraft.admin"))) {
            e.setCancelled(true);
            return;
        }
        if (this.arsenal != null && this.arsenal.handleInventory(e)) {
            return;
        }
        if (this.gta.handleInventory(e)) {
            return;
        }
        humanEntity = e.getWhoClicked();
        if (humanEntity instanceof Player) {
            Player gpPlayer = (Player)humanEntity;
            if (e.getView().getTitle().equals("\u00a78[GTA GPS] City Navigation")) {
                e.setCancelled(true);
                this.gps.handleClick(gpPlayer, e.getCurrentItem());
                return;
            }
        }
        if ((humanEntity = e.getWhoClicked()) instanceof Player) {
            Player pinPlayer = (Player)humanEntity;
            if (e.getView().getTitle().equals("SD Craft PIN")) {
                e.setCancelled(true);
                ItemStack pinItem = e.getCurrentItem();
                if (pinItem == null || !pinItem.hasItemMeta() || !pinItem.getItemMeta().hasDisplayName()) {
                    return;
                }
                String val = pinItem.getItemMeta().getDisplayName().replace("\u00a7b", "").replace("\u00a7a", "").replace("\u00a7c", "");
                UUID uid = pinPlayer.getUniqueId();
                StringBuilder digits = this.pinDigits.get(uid);
                String mode = this.pinMode.get(uid);
                if (digits == null || mode == null) {
                    return;
                }
                if (val.matches("[0-9]")) {
                    if (digits.length() < 8) {
                        digits.append(val);
                    }
                    return;
                }
                if (val.equals("CLEAR")) {
                    digits.setLength(0);
                    return;
                }
                if (val.equals("CANCEL")) {
                    this.pinMode.remove(uid);
                    this.pinDigits.remove(uid);
                    pinPlayer.closeInventory();
                    return;
                }
                if (val.equals("CONFIRM")) {
                    String input = digits.toString();
                    digits.setLength(0);
                    this.pinMode.remove(uid);
                    this.pinDigits.remove(uid);
                    pinPlayer.closeInventory();
                    try {
                        if (mode.equals("set")) {
                            this.ledger.pin(uid, input);
                            this.msg((CommandSender)pinPlayer, "Secure PIN saved through private menu.");
                        } else if (this.ledger.verifyPin(uid, input)) {
                            this.executePending(pinPlayer);
                        } else {
                            this.err((CommandSender)pinPlayer, "PIN invalid. No transfer authorized.");
                        }
                    }
                    catch (Exception ex) {
                        this.err((CommandSender)pinPlayer, "PIN operation failed: " + ex.getMessage());
                        this.getLogger().warning(ex.toString());
                    }
                }
                return;
            }
        }
        if (!((clicked = e.getWhoClicked()) instanceof Player)) {
            return;
        }
        Player p = (Player)clicked;
        String id = this.guiNpc.get(p.getUniqueId());
        if (id == null || !e.getView().getTitle().startsWith("SD Craft:")) {
            return;
        }
        e.setCancelled(true);
        ItemStack item = e.getCurrentItem();
        if (item == null || !item.hasItemMeta() || !item.getItemMeta().hasDisplayName() || item.getType() == Material.GRAY_STAINED_GLASS_PANE) {
            return;
        }
        String action = item.getItemMeta().getDisplayName().replace("\u00a7b", "").trim();
        if (action.isEmpty()) {
            return;
        }
        p.closeInventory();
        this.gta.handleNpcAction(p, action);
    }

    @EventHandler(priority=EventPriority.HIGHEST, ignoreCancelled=true)
    public void onDamage(EntityDamageEvent e) {
        Entity entity = e.getEntity();
        if (!(entity instanceof Player)) {
            return;
        }
        Player p = (Player)entity;
        if (this.isManagedNpc((Entity)p)) {
            return;
        }
        if (!this.isAuthenticated(p)) {
            e.setCancelled(true);
            return;
        }
        UUID id = p.getUniqueId();
        if (this.isDowned(p)) {
            e.setCancelled(true);
            return;
        }
        if (!this.getConfig().getBoolean("medical.downed-enabled", true)) {
            return;
        }
        if (e.getFinalDamage() < p.getHealth()) {
            return;
        }
        e.setCancelled(true);
        NativeDownedState state = NativeDownedState.begin(System.currentTimeMillis(), p.isInvulnerable());
        p.getPersistentDataContainer().set(this.downedKey(), PersistentDataType.STRING, state.marker());
        this.downed.put(id, state);
        p.setHealth(Math.max(1.0, Math.min(2.0, p.getMaxHealth())));
        p.setInvulnerable(true);
        try {
            p.saveData();
        }
        catch (RuntimeException failure) {
            this.getLogger().warning("Native downed player save failed for " + String.valueOf(id) + "; active marker retained for retry");
        }
        p.sendMessage("\u00a7c[SD Craft] DOWNED for 90 seconds. A medic can /sdc revive " + p.getName() + ". Hospital fallback is automatic.");
    }

    private void openPin(Player p, String mode) {
        Inventory inv = Bukkit.createInventory(null, (int)27, (String)"SD Craft PIN");
        String[] names = new String[]{"1", "2", "3", "4", "5", "6", "7", "8", "9", "CLEAR", "0", "CONFIRM", "CANCEL"};
        for (int i = 0; i < names.length; ++i) {
            ItemStack item = new ItemStack(Material.PAPER);
            ItemMeta meta = item.getItemMeta();
            if (meta != null) {
                meta.setDisplayName("\u00a7b" + names[i]);
                item.setItemMeta(meta);
            }
            inv.setItem(i, item);
        }
        this.pinDigits.put(p.getUniqueId(), new StringBuilder());
        this.pinMode.put(p.getUniqueId(), mode);
        p.openInventory(inv);
        p.sendMessage("\u00a77[SD Craft] Enter 4\u20138 PIN digits using menu buttons; then CONFIRM. Digits are not sent through chat.");
    }

    private void executePending(Player p) throws IOException {
        if (!this.requireAuthenticated(p)) {
            return;
        }
        UUID id = p.getUniqueId();
        Pending x = this.pending.remove(id);
        if (x == null || x.expires < System.currentTimeMillis()) {
            this.err((CommandSender)p, "No valid pending action");
            return;
        }
        boolean ok = false;
        switch (x.kind) {
            case "deposit": {
                ok = this.ledger.deposit(id, x.cents);
                break;
            }
            case "withdraw": {
                ok = this.ledger.withdraw(id, x.cents);
                break;
            }
            case "transfer": {
                ok = this.ledger.transfer(id, UUID.fromString(x.target), x.cents);
                break;
            }
            case "taxi": 
            case "bus": 
            case "metro": {
                Location dest;
                ok = this.ledger.chargeWallet(id, x.cents, x.kind + " trip");
                if (!ok) break;
                if (x.kind.equals("metro")) {
                    p.getInventory().addItem(new ItemStack[]{CityItems.metroTicket(x.target)});
                }
                if ((dest = this.site(x.target)) == null) break;
                Bukkit.getScheduler().runTaskLater((Plugin)this, () -> {
                    if (p.isOnline() && this.isAuthenticated(p)) {
                        p.teleport(dest);
                    }
                }, 60L);
                break;
            }
            case "medical": {
                ok = this.ledger.chargeWallet(id, x.cents, "medical:" + x.target);
                if (!ok) break;
                Bukkit.getScheduler().runTaskLater((Plugin)this, () -> {
                    if (p.isOnline() && this.isAuthenticated(p)) {
                        p.setHealth(Math.min(p.getMaxHealth(), p.getHealth() + 8.0));
                        p.sendMessage("\u00a7a[SD Craft] Medical care completed.");
                    }
                }, this.getConfig().getLong("medical.procedure-seconds", 30L) * 20L);
            }
        }
        this.msg((CommandSender)p, ok ? "Transaction authorized and saved." : "Transaction declined: insufficient funds or other verification failed.");
    }

    private void openNpc(Player p, String id) {
        String lang = this.ledger.language(p.getUniqueId());
        String npcName = this.npcs.name(id);
        String npcRole = this.npcs.role(id);
        String npcDept = this.npcs.dept(id).toUpperCase(Locale.ROOT);
        String greeting = this.npcs.greeting(id, lang);
        p.sendMessage("\u00a78\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501");
        p.sendMessage("\u00a76\u00a7l\u25b6 \u00a7e\u00a7l" + npcName + " \u00a77(" + npcRole + " \u2022 \u00a76" + npcDept + "\u00a77)");
        p.sendMessage("\u00a7f\"" + greeting + "\"");
        p.sendMessage("\u00a77Select an action in the menu below or type \u00a7f/sdc help\u00a77.");
        p.sendMessage("\u00a78\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501");
        p.playSound(p.getLocation(), Sound.ENTITY_VILLAGER_YES, 0.8f, 1.1f);
        p.sendActionBar((Component)Component.text((String)("\u00a7eSpeaking with \u00a76" + npcName + " \u00a77- \u00a7aChoose an action")));
        List<String> actions = this.npcs.actions(id);
        Inventory inv = Bukkit.createInventory(null, (int)27, (String)("SD Craft: " + npcName));
        ItemStack border = new ItemStack(Material.GRAY_STAINED_GLASS_PANE);
        ItemMeta bMeta = border.getItemMeta();
        if (bMeta != null) {
            bMeta.setDisplayName(" ");
            border.setItemMeta(bMeta);
        }
        for (int i = 0; i < 27; ++i) {
            inv.setItem(i, border);
        }
        int[] actionSlots = new int[]{10, 11, 12, 13, 14, 15, 16, 1, 2, 3, 4, 5, 6, 7};
        for (int i = 0; i < Math.min(actionSlots.length, actions.size()); ++i) {
            String act = actions.get(i);
            Material mat = this.getThematicMaterial(act);
            ItemStack item = new ItemStack(mat);
            ItemMeta meta = item.getItemMeta();
            if (meta != null) {
                meta.setDisplayName("\u00a7b" + act.replace('_', ' '));
                meta.setLore(List.of("\u00a77Official " + npcDept + " Service", "\u00a7a\u25b6 Click to proceed"));
                item.setItemMeta(meta);
            }
            inv.setItem(actionSlots[i], item);
        }
        this.guiNpc.put(p.getUniqueId(), id);
        p.openInventory(inv);
    }

    private Material getThematicMaterial(String action) {
        String act = action.toLowerCase(Locale.ROOT);
        if (act.contains("police") || act.contains("crime") || act.contains("duty") || act.contains("report")) {
            return Material.SHIELD;
        }
        if (act.contains("bank") || act.contains("balance") || act.contains("deposit") || act.contains("withdraw") || act.contains("transfer")) {
            return Material.EMERALD;
        }
        if (act.contains("medic") || act.contains("treatment") || act.contains("hospital") || act.contains("revive") || act.contains("first_aid")) {
            return Material.GOLDEN_APPLE;
        }
        if (act.contains("transit") || act.contains("metro") || act.contains("bus") || act.contains("taxi") || act.contains("ticket")) {
            return Material.COMPASS;
        }
        if (act.contains("car") || act.contains("vehicle") || act.contains("catalog") || act.contains("test_drive") || act.contains("repair")) {
            return Material.MINECART;
        }
        if (act.contains("fire") || act.contains("rescue") || act.contains("extinguisher")) {
            return Material.WATER_BUCKET;
        }
        if (act.contains("register") || act.contains("permit") || act.contains("statement")) {
            return Material.WRITABLE_BOOK;
        }
        return Material.GOLD_INGOT;
    }

    private void second() {
        long now = System.currentTimeMillis();
        boolean retryAssets = ++this.assetRetrySeconds % 5 == 0;
        World world = Bukkit.getWorld((String)this.getConfig().getString("world.name", "world"));
        if (world != null) {
            long tick = world.getTime();
            long boundary = tick < 12000L ? 12000L : 24000L;
            world.setTime((tick + Math.min(boundary - tick, tick < 12000L ? 10L : 20L)) % 24000L);
        }
        for (Player p : Bukkit.getOnlinePlayers()) {
            Duty d;
            if (!this.isAuthenticated(p)) continue;
            if (retryAssets) {
                this.assetShop.retry(p);
                this.vehicleServices.retry(p);
            }
            UUID id = p.getUniqueId();
            if (this.gtmLoans != null) {
                this.gtmLoans.tick(p, !p.isSleeping() && now - this.activeAt.getOrDefault(id, 0L) < 120000L);
            }
            if ((d = this.duties.get(id)) == null) continue;
            int shift = this.shiftOf(world);
            if (d.shift != shift) {
                this.clockOut(id, "shift ended");
                continue;
            }
            boolean awake = !p.isSleeping();
            long active = this.activeAt.getOrDefault(id, 0L);
            if (awake && now - active < 120000L) {
                d.creditedMs += Math.max(0L, now - d.lastTick);
            }
            d.lastTick = now;
        }
        this.recoverExpiredDowned(now);
        this.pending.entrySet().removeIf(e -> ((Pending)e.getValue()).expires < now);
        if (this.restoration != null) {
            this.restoration.tick();
        }
        this.gta.tick();
    }

    private int shiftOf(World w) {
        return w != null && w.getTime() >= 12000L ? 1 : 0;
    }

    private void clockOut(UUID id, String why) {
        Duty d = this.duties.remove(id);
        if (d == null) {
            return;
        }
        try {
            int r = Math.max(1, Math.min(7, this.ledger.rank(id)));
            long[] pay10 = new long[]{12000L, 14500L, 17000L, 19500L, 22000L, 24500L, 27000L};
            long pay = d.creditedMs * pay10[r - 1] / 600000L;
            this.ledger.grantDuty(id, pay, d.creditedMs, 0, "duty " + d.profession + " " + why);
            Player p = Bukkit.getPlayer((UUID)id);
            if (p != null) {
                p.sendMessage("\u00a7a[SD Craft] Duty ended (" + why + "). Earned " + PolicyEngine.money(pay) + " from verified active time.");
            }
        }
        catch (Exception ex) {
            this.getLogger().severe("DUTY SETTLEMENT FAILED " + String.valueOf(id) + " " + ex.getMessage());
        }
    }

    public Location site(String id) {
        String path = "sites." + id;
        World w = Bukkit.getWorld((String)this.data.getString(path + ".world", ""));
        if (w == null || !this.data.contains(path + ".x")) {
            return null;
        }
        return new Location(w, this.data.getDouble(path + ".x"), this.data.getDouble(path + ".y"), this.data.getDouble(path + ".z"));
    }

    GunEngine guns() {
        return this.guns;
    }

    GtmItemDelivery deliveries() {
        return this.itemDelivery;
    }

    GtmLoans loans() {
        return this.gtmLoans;
    }

    GtmProperties properties() {
        return this.gtmProperties;
    }

    GtmFood food() {
        return this.gtmFood;
    }

    GtmAlcohol alcohol() {
        return this.alcohol;
    }

    GtmVehicles vehicles() {
        return this.vehicles;
    }

    GtmAssetShop assetShop() {
        return this.assetShop;
    }

    GtmVehicleServices vehicleServices() {
        return this.vehicleServices;
    }

    GtmFurnitureMenu furnitureMenu() {
        return this.furnitureMenu;
    }

    GtmEquipment equipment() {
        return this.equipment;
    }

    GtmNativeFinishes nativeFinishes() {
        return this.nativeFinishes;
    }

    GtmWardrobe wardrobe() {
        return this.wardrobe;
    }

    GtmPhoneApps phoneApps() {
        return this.phoneApps;
    }

    GtmSigns signs() {
        return this.signs;
    }

    GtmTaxi taxi() {
        return this.taxi;
    }

    GtmFurniture furniture() {
        return this.furniture;
    }

    GtmCivicTerminals civicTerminals() {
        return this.civicTerminals;
    }

    GtmControlCentre festivals() {
        return this.festivals;
    }

    int wantedLevel(Player player) {
        return this.gta.wantedLevel(player.getUniqueId());
    }

    boolean coreAction(Player player, String ... args) {
        return this.onCommand((CommandSender)player, (Command)Objects.requireNonNull(this.getCommand("sdcraft")), "sdcraft", args);
    }

    boolean gameAction(Player player, String action, String ... args) throws Exception {
        if (!this.requireAuthenticated(player)) {
            return false;
        }
        return this.gta.handleCommand(player, action, args);
    }

    void requestBankTransfer(Player player, UUID recipient, long cents) {
        if (!this.requireAuthenticated(player) || recipient.equals(player.getUniqueId()) || !this.ledger.exists(recipient) || cents <= 0L || cents > 100000000000L) {
            throw new IllegalArgumentException("Invalid recipient or payment amount");
        }
        if (!this.ledger.hasPin(player.getUniqueId())) {
            player.sendMessage("\u00a7eSet your private bank PIN, then choose the payment again.");
            this.openPin(player, "set");
            return;
        }
        this.pending.put(player.getUniqueId(), new Pending("transfer", recipient.toString(), cents, System.currentTimeMillis() + 30000L, "ARK Pay"));
        player.sendMessage("\u00a7eAuthorize " + PolicyEngine.money(cents) + " to " + Optional.ofNullable(Bukkit.getPlayer((UUID)recipient)).map(Player::getName).orElse(recipient.toString()) + " with your private PIN.");
        this.openPin(player, "verify");
    }

    String profession(UUID id) {
        return this.data.getString("players." + String.valueOf(id) + ".profession", "");
    }

    private boolean near(Player p, String id, int radius) {
        Location l = this.site(id);
        return l != null && l.getWorld().equals((Object)p.getWorld()) && l.distanceSquared(p.getLocation()) <= (double)(radius * radius);
    }

    private void setSite(String id, Location loc) throws IOException {
        String path = "sites." + id;
        this.data.set(path + ".world", (Object)loc.getWorld().getName());
        this.data.set(path + ".x", (Object)loc.getX());
        this.data.set(path + ".y", (Object)loc.getY());
        this.data.set(path + ".z", (Object)loc.getZ());
        this.runtimeStore.commit();
    }

    private void msg(CommandSender who, String text) {
        who.sendMessage("\u00a76[SD Craft] \u00a7f" + text);
    }

    private void err(CommandSender who, String text) {
        who.sendMessage("\u00a7c[SD Craft] " + text);
    }

    private long dollars(String input) {
        if (!input.matches("[0-9]{1,9}(\\.[0-9]{1,2})?")) {
            throw new IllegalArgumentException("Use positive amount such as 25 or 25.50");
        }
        BigDecimal value = new BigDecimal(input).movePointRight(2);
        long a = value.longValueExact();
        if (a <= 0L || a > 100000000000L) {
            throw new IllegalArgumentException("Invalid amount");
        }
        return a;
    }

    private String commandHelp() {
        return "/sdc map, gps, spawn, car, kit, gun, pack, arsenal, testing, ammo, account, promotion, bank, pin, confirm, cancel, npc, npcs, setnpc, duty, work, fees, taxi, ride, setsite, report, rob, surrender, revive, medical, mission, status, talk, zone, restore";
    }

    public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
        Player player;
        if (sender instanceof Player && !this.requireAuthenticated(player = (Player)sender)) {
            return true;
        }
        String cmdName = cmd.getName().toLowerCase(Locale.ROOT);
        if (Set.of("arsenal", "creativemenu", "testitems", "testing").contains(cmdName) && !sender.hasPermission("sdcraft.admin")) {
            this.err(sender, "Admin only");
            return true;
        }
        if (cmdName.equals("phone")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                try {
                    this.gta.handleCommand(p, "phone", args);
                }
                catch (Exception ex) {
                    this.err((CommandSender)p, ex.getMessage());
                }
            }
            return true;
        }
        if (cmdName.equals("map")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                this.openCityMap(p);
            } else {
                this.msg(sender, "SD Craft 3D Web Map: " + this.getConfig().getString("map.web-url", "http://localhost:8100"));
            }
            return true;
        }
        if (cmdName.equals("gps")) {
            if (args.length >= 2 && args[0].equalsIgnoreCase("give")) {
                if (!sender.hasPermission("sdcraft.admin")) {
                    this.err(sender, "Admin only");
                    return true;
                }
                Player target = Bukkit.getPlayer((String)args[1]);
                if (target == null) {
                    this.err(sender, "Player not found");
                    return true;
                }
                target.getInventory().addItem(new ItemStack[]{this.gps.createGpsItem()});
                this.msg(sender, "Gave SD Craft GPS Navigator to " + target.getName());
                target.sendMessage("\u00a7a[SD Craft] Received SD Craft GPS Navigator");
                return true;
            }
            if (sender instanceof Player) {
                Player p = (Player)sender;
                if (this.phoneApps != null && this.phoneApps.available(p)) {
                    this.phoneApps.openPage(p, "maps");
                } else {
                    this.gps.openGpsMenu(p);
                }
            } else {
                this.msg(sender, "GPS navigation menu is for players in-game.");
            }
            return true;
        }
        if (cmdName.equals("spawn")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                Location surfaceSpawn = this.getSurfaceSpawn(p.getWorld());
                p.teleport(surfaceSpawn);
                p.sendMessage("\u00a7a[SD Craft] \u00a7eTeleported to City Hall Plaza surface.");
                p.playSound(surfaceSpawn, Sound.ENTITY_ENDERMAN_TELEPORT, 0.7f, 1.2f);
            } else {
                this.msg(sender, "Command is for in-game players.");
            }
            return true;
        }
        if (cmdName.equals("car") || cmdName.equals("vehicle") || cmdName.equals("cars")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                try {
                    this.gta.handleStandaloneCar(p, args);
                }
                catch (Exception ex) {
                    this.err((CommandSender)p, ex.getMessage());
                }
            } else {
                this.msg(sender, "Command is for in-game players.");
            }
            return true;
        }
        if (cmdName.equals("kit") || cmdName.equals("starter")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                if (this.gta.tryClaimStarter(p)) {
                    this.grantStarterKit(p, false);
                } else {
                    this.err((CommandSender)p, "The starter kit is one-time only. Use /phone for shops and missions.");
                }
            } else {
                this.msg(sender, "Command is for in-game players.");
            }
            return true;
        }
        if (cmdName.equals("gun") || cmdName.equals("guns")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                try {
                    if (!requireAuthenticated(p)) return true;
                    if (args.length == 0 && equipment != null) {
                        offerWeaponUpgrade(p);
                        equipment.open(p);
                    } else this.gta.handleStandaloneGun(p, args);
                }
                catch (Exception ex) {
                    this.err((CommandSender)p, ex.getMessage());
                }
            } else {
                this.msg(sender, "Command is for in-game players.");
            }
            return true;
        }
        if (cmdName.equals("pack") || cmdName.equals("resourcepack") || cmdName.equals("packs")) {
            org.bukkit.packs.ResourcePack pack = getServer().getServerResourcePack();
            if (pack == null || pack.getUrl().isBlank()) { sender.sendMessage("§cNo server pack is configured. Install the matching GTM repair pack on the server."); return true; }
            if (sender instanceof Player packPlayer) {
                if (!requireAuthenticated(packPlayer)) return true;
                String hash = pack.getHash();
                if (hash == null || !hash.matches("[0-9a-fA-F]{40}")) { sender.sendMessage("§cThe server pack fingerprint is invalid; ask the owner to run the repair installer."); return true; }
                loadedPacks.remove(packPlayer.getUniqueId());
                packPlayer.setResourcePack(pack.getId(), pack.getUrl(), java.util.HexFormat.of().parseHex(hash), Component.text("GTM native128 phone, equipment and vehicles"), pack.isRequired());
                packPlayer.sendMessage("§6[GTM] §fRequested the configured server resource pack. Accept it to load the phone, weapons and vehicles.");
            } else sender.sendMessage("GTM resource pack: " + pack.getUrl() + " SHA-1 " + pack.getHash());
            return true;
        }
        if (cmdName.equals("arsenal") || cmdName.equals("creativemenu") || cmdName.equals("testitems")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                this.arsenal.openArsenal(p);
            } else {
                this.msg(sender, "Creative Testing Arsenal is for players in-game.");
            }
            return true;
        }
        if (cmdName.equals("testing")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                this.arsenal.enableTestingMode(p);
            } else {
                this.msg(sender, "Testing mode is for players in-game.");
            }
            return true;
        }
        try {
            return this.dispatch(sender, args);
        }
        catch (Exception ex) {
            this.err(sender, ex instanceof IllegalArgumentException || ex instanceof IllegalStateException ? ex.getMessage() : "Operation could not finish; review server logs.");
            if (!(ex instanceof IllegalArgumentException)) {
                this.getLogger().warning("Command error: " + ex.toString());
            }
            return true;
        }
    }

    private boolean dispatch(CommandSender sender, String[] a) throws Exception {
        Player target;
        if (a.length == 0 || a[0].equalsIgnoreCase("help")) {
            this.msg(sender, this.commandHelp());
            return true;
        }
        String action = a[0].toLowerCase(Locale.ROOT);
        if (Set.of("arsenal", "creativemenu", "testitems", "testing").contains(action) && !sender.hasPermission("sdcraft.admin")) {
            this.err(sender, "Admin only");
            return true;
        }
        if (action.equals("kit") || action.equals("starter")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                if (this.gta.tryClaimStarter(p)) {
                    this.grantStarterKit(p, false);
                } else {
                    this.err((CommandSender)p, "The starter kit is one-time only.");
                }
            }
            return true;
        }
        if (action.equals("gun") && a.length < 2) {
            return onCommand(sender, Objects.requireNonNull(getCommand("gun")), "gun", new String[0]);
        }
        if (action.equals("gun") && !a[1].equalsIgnoreCase("give")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                this.gta.handleStandaloneGun(p, Arrays.copyOfRange(a, 1, a.length));
            }
            return true;
        }
        if (action.equals("arsenal") || action.equals("creativemenu") || action.equals("testitems")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                this.arsenal.openArsenal(p);
            } else {
                this.msg(sender, "Creative Testing Arsenal is for players in-game.");
            }
            return true;
        }
        if (action.equals("testing")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                this.arsenal.enableTestingMode(p);
            } else {
                this.msg(sender, "Testing mode is for players in-game.");
            }
            return true;
        }
        if (this.gta.handles(action)) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                return this.gta.handleCommand(p, action, a);
            }
            this.err(sender, "This command is for players.");
            return true;
        }
        if (action.equals("status")) {
            this.msg(sender, "Paper core enabled; " + this.npcs.status() + ". Citizens=" + Bukkit.getPluginManager().isPluginEnabled("Citizens"));
            this.msg(sender, "Players " + Bukkit.getOnlinePlayers().size() + ", active duty=" + this.duties.size() + ", downed=" + this.downed.size() + ".");
            this.msg(sender, "NPC dialogue: " + npcDialogueStatus() + ". Autonomous traffic driving is not implemented.");
            return true;
        }
        if (action.equals("promotion")) {
            if (a.length == 3 && a[1].equalsIgnoreCase("approve")) {
                if (!sender.hasPermission("sdcraft.admin")) {
                    this.err(sender, "Admin approval required");
                    return true;
                }
                Player target2 = Bukkit.getPlayerExact((String)a[2]);
                if (target2 == null || !this.ledger.exists(target2.getUniqueId())) {
                    this.err(sender, "Registered player must be online for promotion approval");
                    return true;
                }
                if (!this.ledger.approvePromotion(target2.getUniqueId(), sender.getName())) {
                    this.err(sender, "Promotion requirements not met: use /sdc promotion status " + target2.getName());
                    return true;
                }
                this.msg(sender, "Approved " + target2.getName() + " for rank " + this.ledger.rank(target2.getUniqueId()));
                target2.sendMessage("\u00a7a[SD Craft] Your promotion to rank " + this.ledger.rank(target2.getUniqueId()) + " was approved by " + sender.getName() + ".");
                return true;
            }
            if (a.length == 1 || a.length >= 2 && a[1].equalsIgnoreCase("status")) {
                Player target3;
                if (a.length >= 3) {
                    if (!sender.hasPermission("sdcraft.admin")) {
                        this.err(sender, "Admin only");
                        return true;
                    }
                    target3 = Bukkit.getPlayerExact((String)a[2]);
                } else {
                    Player p;
                    Player player = target3 = sender instanceof Player ? (p = (Player)sender) : null;
                }
                if (target3 == null || !this.ledger.exists(target3.getUniqueId())) {
                    this.err(sender, "Registered player must be online");
                    return true;
                }
                UUID uid = target3.getUniqueId();
                int rank = this.ledger.rank(uid);
                if (rank >= 7) {
                    this.msg(sender, target3.getName() + " is at maximum rank 7.");
                } else {
                    this.msg(sender, target3.getName() + " rank " + rank + " -> " + (rank + 1) + ": " + this.ledger.credits(uid) + "/" + Ledger.requiredCreditsForRank(rank + 1) + " credits, " + this.ledger.dutyMs(uid) / 3600000L + "/" + Ledger.requiredDutyMsForRank(rank + 1) / 3600000L + " verified duty hours; " + (this.ledger.eligibleForPromotion(uid) ? "awaiting admin approval" : "requirements incomplete"));
                }
                return true;
            }
            this.err(sender, "Use /sdc promotion status [online-player] or /sdc promotion approve <online-player>");
            return true;
        }
        if (action.equals("fees")) {
            this.msg(sender, "Stabilization free; diagnosis $25, treatment $50, admission $75; taxi $25+$6/100 blocks; bus $15; metro $10.");
            return true;
        }
        if (action.equals("map")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                this.openCityMap(p);
            } else {
                this.msg(sender, "SD Craft 3D Web Map: " + this.getConfig().getString("map.web-url", "http://localhost:8100"));
            }
            return true;
        }
        if (action.equals("gps")) {
            if (a.length >= 3 && a[1].equalsIgnoreCase("give")) {
                if (!sender.hasPermission("sdcraft.admin")) {
                    this.err(sender, "Admin only");
                    return true;
                }
                Player target4 = Bukkit.getPlayer((String)a[2]);
                if (target4 == null) {
                    this.err(sender, "Player not found");
                    return true;
                }
                target4.getInventory().addItem(new ItemStack[]{this.gps.createGpsItem()});
                this.msg(sender, "Gave SD Craft GPS Navigator to " + target4.getName());
                target4.sendMessage("\u00a7a[SD Craft] Received SD Craft GPS Navigator");
                return true;
            }
            if (sender instanceof Player) {
                Player p = (Player)sender;
                if (this.phoneApps != null && this.phoneApps.available(p)) {
                    this.phoneApps.openPage(p, "maps");
                } else {
                    this.gps.openGpsMenu(p);
                }
            } else {
                this.msg(sender, "GPS navigation menu is for players in-game.");
            }
            return true;
        }
        if (action.equals("spawn")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                Location surfaceSpawn = this.getSurfaceSpawn(p.getWorld());
                p.teleport(surfaceSpawn);
                p.sendMessage("\u00a7a[SD Craft] \u00a7eTeleported to City Hall Plaza surface.");
                p.playSound(surfaceSpawn, Sound.ENTITY_ENDERMAN_TELEPORT, 0.7f, 1.2f);
            } else {
                this.msg(sender, "In-game only");
            }
            return true;
        }
        if (action.equals("car") || action.equals("vehicle")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                this.gta.handleStandaloneCar(p, Arrays.copyOfRange(a, 1, a.length));
            }
            return true;
        }
        if (action.equals("kit") || action.equals("starter")) {
            if (sender instanceof Player) {
                Player p = (Player)sender;
                this.grantStarterKit(p, true);
                p.sendMessage("\u00a7a[SD Craft] \u00a7eStarter GTA roleplay kit claimed!");
                p.playSound(p.getLocation(), Sound.ENTITY_PLAYER_LEVELUP, 1.0f, 1.2f);
            } else {
                this.msg(sender, "In-game only");
            }
            return true;
        }
        if (action.equals("pack") || action.equals("resourcepack")) {
            return onCommand(sender, Objects.requireNonNull(getCommand("pack")), "pack", new String[0]);
        }
        if (action.equals("npcs")) {
            this.msg(sender, "Named NPCs: " + String.join((CharSequence)", ", this.npcs.ids()));
            return true;
        }
        if (action.equals("npc")) {
            if (a.length < 2) {
                this.err(sender, "Use /sdc npc <id>");
                return true;
            }
            if (!this.npcs.known(a[1])) {
                this.err(sender, "NPC ID missing");
                return true;
            }
            if (sender instanceof Player) {
                Player p = (Player)sender;
                this.openNpc(p, a[1]);
            } else {
                this.msg(sender, this.npcs.name(a[1]) + " (" + this.npcs.role(a[1]) + ", skin=" + this.npcs.skin(a[1]) + " [" + this.npcs.model(a[1]) + "]): " + this.npcs.greeting(a[1], "en"));
            }
            return true;
        }
        if (action.equals("setnpc")) {
            if (!sender.hasPermission("sdcraft.admin") || !(sender instanceof Player)) {
                this.err(sender, "Admin player only");
                return true;
            }
            Player p = (Player)sender;
            if (a.length < 2 || !this.npcs.known(a[1])) {
                this.err(sender, "Use /sdc setnpc <validNpcId>");
                return true;
            }
            this.npcs.setAnchor(a[1], p.getLocation());
            this.msg(sender, "NPC anchor saved. Physical NPC activates within 64 blocks of a player.");
            this.npcs.tick();
            return true;
        }
        if (action.equals("setsite")) {
            if (!sender.hasPermission("sdcraft.admin") || !(sender instanceof Player)) {
                this.err(sender, "Admin player only");
                return true;
            }
            Player p = (Player)sender;
            if (a.length < 2 || !a[1].matches("[a-zA-Z0-9_]{2,30}")) {
                this.err(sender, "/sdc setsite <hospital|taxi_stop|metro_stop|bus_stop|bank|<department>>");
                return true;
            }
            this.setSite(a[1], p.getLocation());
            this.msg(sender, "Verified site " + a[1] + " saved at your feet.");
            return true;
        }
        if (!(sender instanceof Player)) {
            this.err(sender, "This command is for players.");
            return true;
        }
        Player p = (Player)sender;
        UUID id = p.getUniqueId();
        if (!this.ledger.exists(id)) {
            this.err(sender, "Account not initialized. Reconnect.");
            return true;
        }
        if (action.equals("account")) {
            this.msg(sender, "Wallet " + PolicyEngine.money(this.ledger.wallet(id)) + " | Bank " + PolicyEngine.money(this.ledger.bank(id)) + " | rank " + this.ledger.rank(id) + " | career credits " + this.ledger.credits(id));
            this.msg(sender, "Use /sdc promotion to see rank requirements and approval status.");
            return true;
        }
        if (action.equals("language")) {
            if (a.length != 2) {
                this.err(sender, "/sdc language en|hi");
                return true;
            }
            this.ledger.language(id, a[1]);
            this.msg(sender, "Language changed to " + a[1]);
            return true;
        }
        if (action.equals("pin")) {
            if (a.length != 2 || !a[1].equalsIgnoreCase("set")) {
                this.err(sender, "/sdc pin set (opens a private clickable keypad; never type the PIN into chat)");
                return true;
            }
            this.openPin(p, "set");
            return true;
        }
        if (action.equals("bank")) {
            if (a.length < 3) {
                this.err(sender, "/sdc bank deposit|withdraw <amount> OR transfer <player> <amount>");
                return true;
            }
            String method = a[1].toLowerCase(Locale.ROOT);
            if (method.equals("deposit")) {
                if (!this.near(p, "bank", 12)) {
                    this.err(sender, "Visit the verified bank location.");
                    return true;
                }
                long v = this.dollars(a[2]);
                this.pending.put(id, new Pending("deposit", "", v, System.currentTimeMillis() + 30000L, ""));
                this.msg(sender, "Deposit " + PolicyEngine.money(v) + "? /sdc confirm");
                return true;
            }
            if (method.equals("withdraw")) {
                if (!this.near(p, "bank", 12)) {
                    this.err(sender, "Visit the verified bank location.");
                    return true;
                }
                long v = this.dollars(a[2]);
                this.pending.put(id, new Pending("withdraw", "", v, System.currentTimeMillis() + 30000L, ""));
                this.msg(sender, "Withdraw " + PolicyEngine.money(v) + "? /sdc confirm <PIN>");
                return true;
            }
            if (method.equals("transfer")) {
                if (a.length != 4) {
                    this.err(sender, "/sdc bank transfer <online-player> <amount>");
                    return true;
                }
                Player target5 = Bukkit.getPlayerExact((String)a[2]);
                if (target5 == null || !this.ledger.exists(target5.getUniqueId())) {
                    this.err(sender, "Recipient must be online with a verified account");
                    return true;
                }
                long v = this.dollars(a[3]);
                this.pending.put(id, new Pending("transfer", target5.getUniqueId().toString(), v, System.currentTimeMillis() + 30000L, target5.getName()));
                this.msg(sender, "Transfer " + PolicyEngine.money(v) + " to " + target5.getName() + "? /sdc confirm <PIN>");
                return true;
            }
            this.err(sender, "/sdc bank deposit|withdraw|transfer");
            return true;
        }
        if (action.equals("cancel")) {
            this.pending.remove(id);
            this.msg(sender, "Pending transaction cancelled.");
            return true;
        }
        if (action.equals("confirm")) {
            Pending x = this.pending.get(id);
            if (x == null || x.expires < System.currentTimeMillis()) {
                this.pending.remove(id);
                this.err(sender, "No valid pending action");
                return true;
            }
            if (x.kind.equals("withdraw") || x.kind.equals("transfer")) {
                if (!this.ledger.hasPin(id)) {
                    this.err(sender, "Set your private PIN using /sdc pin set");
                    return true;
                }
                this.openPin(p, "verify");
                return true;
            }
            this.executePending(p);
            return true;
        }
        if (action.equals("medical")) {
            int dollars;
            if (a.length < 2) {
                this.err(sender, "/sdc medical stabilize|diagnosis|treatment|admission");
                return true;
            }
            String op = a[1].toLowerCase(Locale.ROOT);
            if (!this.near(p, "hospital", 16)) {
                this.err(sender, "Use the verified hospital station.");
                return true;
            }
            if (op.equals("stabilize")) {
                p.setHealth(Math.max(p.getHealth(), 6.0));
                this.msg(sender, "Emergency stabilization is free.");
                return true;
            }
            switch (op) {
                case "diagnosis": {
                    dollars = 25;
                    break;
                }
                case "treatment": {
                    dollars = 50;
                    break;
                }
                case "admission": {
                    dollars = 75;
                    break;
                }
                default: {
                    dollars = -1;
                }
            }
            if (dollars < 0) {
                this.err(sender, "Unknown service");
                return true;
            }
            this.pending.put(id, new Pending("medical", op, (long)dollars * 100L, System.currentTimeMillis() + 30000L, ""));
            this.msg(sender, "Confirm " + op + " for $" + dollars + " using /sdc confirm. Care takes 20\u201360 seconds.");
            return true;
        }
        if (action.equals("revive")) {
            if (a.length < 2) {
                this.err(sender, "/sdc revive <online-player>");
                return true;
            }
            if (!sender.hasPermission("sdcraft.medic") && !sender.hasPermission("sdcraft.admin")) {
                this.err(sender, "Medic authorization required");
                return true;
            }
            Player victim = Bukkit.getPlayerExact((String)a[1]);
            try {
                this.reviveNearby(p, victim == null ? null : victim.getUniqueId(), victim == null ? null : this.authenticatedSession(victim), victim == null ? null : this.downedEpisode(victim));
            }
            catch (IllegalStateException unavailable) {
                this.err(sender, unavailable.getMessage());
            }
            return true;
        }
        if (action.equals("work")) {
            if (a.length < 3 || !a[1].equalsIgnoreCase("join")) {
                this.err(sender, "/sdc work join <taxi|retail|delivery|chef|police|medic|firefighter|metro|maintenance>");
                return true;
            }
            String profession = a[2].toLowerCase(Locale.ROOT);
            if (!List.of("taxi", "retail", "delivery", "chef", "police", "medic", "firefighter", "metro", "maintenance").contains(profession)) {
                this.err(sender, "Unknown profession");
                return true;
            }
            if (List.of("police", "medic", "firefighter").contains(profession) && !sender.hasPermission("sdcraft.profession." + profession)) {
                this.err(sender, "Sensitive profession needs admin permission");
                return true;
            }
            String k = "players." + String.valueOf(id) + ".profession";
            this.data.set(k, (Object)profession);
            this.safeSave();
            this.msg(sender, "Registered role: " + profession + ". Clock in at verified duty station with /sdc duty in.");
            return true;
        }
        if (action.equals("duty")) {
            if (a.length < 2) {
                this.err(sender, "/sdc duty in|out|status");
                return true;
            }
            String op = a[1].toLowerCase(Locale.ROOT);
            if (op.equals("out")) {
                this.clockOut(id, "clock out");
                return true;
            }
            if (op.equals("status")) {
                Duty d = this.duties.get(id);
                this.msg(sender, (String)(d == null ? "Off duty" : "On duty " + d.profession + ", verified " + d.creditedMs / 1000L + " seconds"));
                return true;
            }
            if (op.equals("in")) {
                if (this.duties.containsKey(id)) {
                    this.err(sender, "Already on duty");
                    return true;
                }
                String role = this.data.getString("players." + String.valueOf(id) + ".profession", "");
                if (role.isBlank() || !this.near(p, role, 16)) {
                    this.err(sender, "Register a profession and clock in at its verified department station.");
                    return true;
                }
                long now = System.currentTimeMillis();
                this.duties.put(id, new Duty(role, this.shiftOf(p.getWorld()), now));
                this.msg(sender, "Clocked in as " + role + ". Pay proportionate to verified non-AFK active time.");
                return true;
            }
        }
        if (action.equals("taxi") || action.equals("ride")) {
            String destination;
            String mode;
            mode = action.equals("taxi") ? "taxi" : (a.length > 1 ? a[1].toLowerCase(Locale.ROOT) : "");
            if (mode.equals("taxi") && this.taxi != null && this.taxi.enabled()) {
                this.taxi.open(p);
                return true;
            }
            destination = action.equals("taxi") ? (a.length > 1 ? a[1] : "") : (a.length > 2 ? a[2] : "");
            if (!List.of("taxi", "bus", "metro").contains(mode)) {
                this.err(sender, "/sdc taxi <verified-stop> OR /sdc ride <bus|metro> <verified-stop>");
                return true;
            }
            Location target6 = this.site(destination);
            if (target6 == null || !target6.getWorld().equals((Object)p.getWorld())) {
                this.err(sender, "Unknown verified stop. Admin sets via /sdc setsite <id>");
                return true;
            }
            long cents = mode.equals("taxi") ? PolicyEngine.taxiQuoteCents(Math.round(p.getLocation().distance(target6))) : (mode.equals("bus") ? 1500L : 1000L);
            this.pending.put(id, new Pending(mode, destination, cents, System.currentTimeMillis() + 30000L, ""));
            this.msg(sender, mode + " to " + destination + " fare " + PolicyEngine.money(cents) + ". /sdc confirm. Simulated transport fallback when vehicle bridge unavailable.");
            return true;
        }
        if (action.equals("report")) {
            if (a.length < 3) {
                this.err(sender, "/sdc report <1|2|3> <description>");
                return true;
            }
            int severity = Integer.parseInt(a[1]);
            if (severity < 1 || severity > 3) {
                throw new IllegalArgumentException("Severity 1\u20133 only");
            }
            long now = System.currentTimeMillis();
            if (now - this.lastReport.getOrDefault(id, 0L) < 60000L) {
                this.err(sender, "Report cooldown 60 seconds");
                return true;
            }
            this.lastReport.put(id, now);
            String desc = String.join((CharSequence)" ", Arrays.copyOfRange(a, 2, Math.min(a.length, 15)));
            String incident = UUID.randomUUID().toString().substring(0, 8);
            this.data.set("incidents." + incident + ".reporter", (Object)id.toString());
            this.data.set("incidents." + incident + ".severity", (Object)severity);
            this.data.set("incidents." + incident + ".description", (Object)desc);
            this.data.set("incidents." + incident + ".status", (Object)"reported");
            this.safeSave();
            this.msg(sender, "SDPD incident #" + incident + " reported, level " + severity + "; evidence and investigation required before arrest.");
            for (Player other : Bukkit.getOnlinePlayers()) {
                if (!other.hasPermission("sdcraft.police")) continue;
                other.sendMessage("\u00a7c[SDPD] Level " + severity + " incident #" + incident + " near " + p.getName() + ". " + desc);
            }
            return true;
        }
        if (action.equals("rob")) {
            if (!this.getConfig().getBoolean("crime.robbery-enabled", false)) {
                this.err(sender, "Cash robbery intentionally locked until approved protected zones are configured.");
                return true;
            }
            this.err(sender, "Validated armed robbery requires the crime-zone integration and is not enabled by this build. No unverified money is stolen.");
            return true;
        }
        if (action.equals("surrender")) {
            this.msg(sender, "You offered to surrender. Police arrest still requires a verified incident, evidence and a 15-second surrender opportunity.");
            return true;
        }
        if (action.equals("talk")) {
            if (a.length < 3 || !this.npcs.known(a[1])) {
                this.err(sender, "/sdc talk <npc-id> <message>");
                return true;
            }
            if (this.gtmDialogue != null) this.gtmDialogue.talkById(p, a[1], String.join(" ", Arrays.copyOfRange(a, 2, a.length)));
            return true;
        }
        if (action.equals("mission")) {
            this.msg(sender, "Mission definitions are included in missions.yml. Verified multi-stage objectives require site calibration and an external mission executor; no credits are awarded for an unverified objective.");
            return true;
        }
        if (action.equals("zone")) {
            if (!sender.hasPermission("sdcraft.admin")) {
                this.err(sender, "Admin player only");
                return true;
            }
            if (a.length >= 3 && a[1].equalsIgnoreCase("mark")) {
                int rad = a.length >= 4 ? Integer.parseInt(a[3]) : 50;
                this.restoration.markZone(a[2], p.getLocation(), rad);
                this.msg(sender, "Marked restorable city zone '" + a[2] + "' (radius " + rad + "m). Street damage here restores after 5 minutes.");
                return true;
            }
            if (a.length >= 3 && a[1].equalsIgnoreCase("unmark")) {
                boolean ok = this.restoration.unmarkZone(a[2]);
                this.msg(sender, (String)(ok ? "Removed restorable zone '" + a[2] + "'" : "Zone not found"));
                return true;
            }
            if (a.length >= 2 && a[1].equalsIgnoreCase("list")) {
                Collection<RestorationEngine.RestorableZone> list = this.restoration.getZones();
                this.msg(sender, (String)(list.isEmpty() ? "No custom zones. City default active for Y>=55." : "Restorable zones: " + String.valueOf(list.stream().map(z -> z.name() + "(r=" + z.radius() + ")").toList())));
                return true;
            }
            this.err(sender, "/sdc zone mark <name> [radius] | unmark <name> | list");
            return true;
        }
        if (action.equals("restore")) {
            if (a.length >= 2 && a[1].equalsIgnoreCase("now")) {
                if (!sender.hasPermission("sdcraft.admin")) {
                    this.err(sender, "Admin only");
                    return true;
                }
                int done = this.restoration.forceRestoreAll();
                this.msg(sender, "Force-restored " + done + " street blocks immediately.");
                return true;
            }
            this.msg(sender, "5-Minute Auto-Regeneration: " + this.restoration.getPendingCount() + " street blocks in queue awaiting restoration.");
            return true;
        }
        if (action.equals("gun")) {
            if (!sender.hasPermission("sdcraft.admin")) {
                this.err(sender, "Admin only");
                return true;
            }
            if (a.length < 3 || !a[1].equalsIgnoreCase("give")) {
                this.err(sender, "/sdc gun give <player> <pistol|shotgun|smg|rifle>");
                return true;
            }
            target = Bukkit.getPlayer((String)a[2]);
            if (target == null) {
                this.err(sender, "Player not found");
                return true;
            }
            String gType = a.length >= 4 ? a[3].toUpperCase(Locale.ROOT) : "PISTOL";
            try {
                GunEngine.GunType gt = GunEngine.GunType.valueOf(gType);
                target.getInventory().addItem(new ItemStack[]{this.guns.createGun(gt)});
                this.msg(sender, "Gave " + gt.displayName + " to " + target.getName());
                target.sendMessage("\u00a7a[SD Craft] Received " + gt.displayName);
            }
            catch (Exception ex) {
                this.err(sender, "Unknown gun type. Choose: PISTOL, SHOTGUN, SMG, RIFLE");
            }
            return true;
        }
        if (action.equals("ammo")) {
            String aType;
            if (!sender.hasPermission("sdcraft.admin")) {
                this.err(sender, "Admin only");
                return true;
            }
            if (a.length < 3 || !a[1].equalsIgnoreCase("give")) {
                this.err(sender, "/sdc ammo give <player> <9mm|shotgun|rifle> [count]");
                return true;
            }
            target = Bukkit.getPlayer((String)a[2]);
            if (target == null) {
                this.err(sender, "Player not found");
                return true;
            }
            String fullType = switch (aType = a.length >= 4 ? a[3].toLowerCase(Locale.ROOT) : "9mm") {
                case "9mm" -> "9mm_ammo";
                case "shotgun" -> "shotgun_shells";
                case "rifle" -> "rifle_ammo";
                default -> aType;
            };
            int count = a.length >= 5 ? Integer.parseInt(a[4]) : 32;
            target.getInventory().addItem(new ItemStack[]{this.guns.createAmmo(fullType, count)});
            this.msg(sender, "Gave " + count + "x " + fullType + " to " + target.getName());
            target.sendMessage("\u00a7a[SD Craft] Received " + count + "x service ammunition");
            return true;
        }
        this.err(sender, "Unknown command. " + this.commandHelp());
        return true;
    }

    public List<String> onTabComplete(CommandSender who, Command cmd, String alias, String[] args) {
        if (args.length == 1) {
            return Arrays.asList("map", "gps", "spawn", "car", "kit", "gun", "pack", "help", "status", "account", "promotion", "language", "bank", "pin", "confirm", "cancel", "npcs", "npc", "setnpc", "setsite", "duty", "work", "medical", "revive", "report", "taxi", "ride", "rob", "mission", "talk", "fees", "surrender", "zone", "restore", "gun", "ammo");
        }
        if (args.length == 2 && args[0].equalsIgnoreCase("gps")) {
            return Arrays.asList("give");
        }
        if (args.length == 2 && args[0].equalsIgnoreCase("promotion")) {
            return who.hasPermission("sdcraft.admin") ? Arrays.asList("status", "approve") : Arrays.asList("status");
        }
        if (args.length == 2 && (args[0].equalsIgnoreCase("npc") || args[0].equalsIgnoreCase("setnpc") || args[0].equalsIgnoreCase("talk"))) {
            return new ArrayList<String>(this.npcs.ids());
        }
        if (args.length == 2 && args[0].equalsIgnoreCase("language")) {
            return Arrays.asList("en", "hi");
        }
        if (args.length == 2 && args[0].equalsIgnoreCase("bank")) {
            return Arrays.asList("deposit", "withdraw", "transfer");
        }
        if (args.length == 2 && args[0].equalsIgnoreCase("zone")) {
            return Arrays.asList("mark", "unmark", "list");
        }
        if (args.length == 2 && args[0].equalsIgnoreCase("restore")) {
            return Arrays.asList("status", "now");
        }
        if (args.length == 2 && args[0].equalsIgnoreCase("gun")) {
            return Arrays.asList("give");
        }
        if (args.length == 2 && args[0].equalsIgnoreCase("ammo")) {
            return Arrays.asList("give");
        }
        if (args.length == 4 && args[0].equalsIgnoreCase("gun")) {
            return Arrays.asList("pistol", "shotgun", "smg", "rifle");
        }
        if (args.length == 4 && args[0].equalsIgnoreCase("ammo")) {
            return Arrays.asList("9mm", "shotgun", "rifle");
        }
        return Collections.emptyList();
    }

    private record Pending(String kind, String target, long cents, long expires, String details) {
    }

    private static final class Duty {
        String profession;
        long lastTick;
        long creditedMs;
        long started;
        int shift;

        Duty(String profession, int shift, long now) {
            this.profession = profession;
            this.shift = shift;
            this.lastTick = now;
            this.started = now;
        }
    }
}

