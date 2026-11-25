/* Reconstructed from the preserved 1.0.3 binary with CFR 0.152; repaired and patched.
 * This is maintainable hotfix source, not recovery of the lost original checkout. */
package com.sdcraft.core;

import com.sdcraft.core.CityItems;
import com.sdcraft.core.GtmPhoneHud;
import com.sdcraft.core.SDCraftCorePlugin;
import com.sdcraft.core.phone.PhoneStore;
import com.sdcraft.core.phone.UiCatalog;
import java.io.IOException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.Sound;
import org.bukkit.SoundCategory;
import org.bukkit.entity.Entity;
import org.bukkit.entity.HumanEntity;
import org.bukkit.entity.Player;
import org.bukkit.event.Event;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.inventory.ClickType;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.inventory.InventoryDragEvent;
import org.bukkit.event.player.AsyncPlayerChatEvent;
import org.bukkit.event.player.PlayerItemHeldEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.event.player.PlayerSwapHandItemsEvent;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.InventoryHolder;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.Plugin;
import org.bukkit.scheduler.BukkitTask;

public final class GtmPhoneApps
implements Listener,
AutoCloseable {
    private static final List<App> APPS = List.of(new App("app_quoggle", "Quoggle", null, "directory", "Search commissioned city services and destinations"), new App("app_amazzo", "Amazzo", null, "amazzo", "Equipment and home catalogues with real purchases"), new App("app_flippit", "Flippit", null, "flippit", "Owned furnishings, local signs and home shopping"), new App("app_arkpay", "ARK Pay", Action.PAYMENTS, "", "Account-to-account payments"), new App("app_zomatoo", "Zomatoo", Action.FOOD_ZOMATOO, "", "Order and collect real Zomatoo food"), new App("app_swiffy", "Swiffy", Action.FOOD_SWIFFY, "", "Order and collect real Swiffy food"), new App("app_fashion", "Vogue Indra", Action.FASHION, "", "Purchase and wear owned clothing"), new App("app_property", "Properties", Action.PROPERTY, "", "Owned properties, purchases and access"), new App("app_car_app", "Motor Mile", null, "car", "Music, navigation and live vehicle diagnostics"), new App("app_maps", "City GPS", null, "maps", "Live terrain map and commissioned destinations"), new App("app_garage", "My Garage", Action.GARAGE, "", "Owned vehicles and their actual controls"), new App("app_bank", "Indra Bank", Action.BANK, "", "Your bank, cash and secured account actions"), new App("app_loans", "Municipal Loans", Action.LOANS, "", "Borrowing, due balances and repayments"), new App("app_taxi", "City Cabs", Action.TAXI, "", "Registered taxi destinations and fares"), new App("app_transport", "Metro & Rail", Action.TRANSPORT, "", "Commissioned transport routes and tickets"), new App("app_news", "Indra 24", null, "news", "Verified game events; no invented headlines"), new App("app_police", "SDPD Law", Action.POLICE, "", "Your wanted status and lawful surrender options"), new App("app_medical", "Trauma Bay", Action.MEDICAL, "", "Actual medical services and hospital navigation"), new App("app_events", "Festivals", Action.FESTIVALS, "", "The live city calendar and authorized events"), new App("app_missions", "Contracts", Action.MISSIONS, "", "Accept and track actual missions"), new App("app_careers", "City Jobs", Action.JOBS, "", "Registered jobs and duty workflows"), new App("app_contacts", "Contacts", null, "contacts", "Private UUID contacts selected from authenticated players"), new App("app_keys", "Key Fob", Action.KEYS, "", "Manage actual owned property and vehicle access"), new App("app_settings", "Settings", null, "settings", "Save map, instruments, effects and audio preferences"));
    private final SDCraftCorePlugin plugin;
    private final Services services;
    private final PhoneStore store;
    private final UiCatalog art;
    private final Map<UUID, Search> searches = new ConcurrentHashMap<UUID, Search>();
    private final Map<UUID, Playing> playing = new HashMap<UUID, Playing>();
    private final Map<UUID, Destination> navigation = new HashMap<UUID, Destination>();
    private final GtmPhoneHud hud;
    private BukkitTask task;
    private boolean closed;

    public GtmPhoneApps(SDCraftCorePlugin plugin, Services services) throws IOException {
        this.plugin = Objects.requireNonNull(plugin);
        this.services = Objects.requireNonNull(services);
        this.store = new PhoneStore(plugin.getDataFolder().toPath().resolve("phone.snapshot"));
        this.art = UiCatalog.bundled();
        for (App app : APPS) {
            this.art.require(app.id());
        }
        this.hud = new GtmPhoneHud(plugin, this, this.art);
    }

    public void start() {
        if (this.task == null && !this.closed) {
            this.task = Bukkit.getScheduler().runTaskTimer((Plugin)this.plugin, this::tick, 5L, 5L);
        }
    }

    public boolean available(Player p) {
        return !this.closed && this.plugin.getConfig().getBoolean("phone.enabled", true) && p.isOnline() && this.plugin.isAuthenticated(p) && p.hasPermission("gtm.phone") && this.plugin.authenticatedSession(p) != null;
    }

    private boolean current(Player p, UUID nonce) {
        return nonce != null && this.available(p) && nonce.equals(this.plugin.authenticatedSession(p));
    }

    public Services services() {
        return this.services;
    }

    public record ClientApp(String id, String title, boolean enabled, String detail) {}

    /** The optional client renders the same stable app registry and server gates. */
    public List<ClientApp> clientApps(Player player) {
        if (!available(player)) return List.of();
        return APPS.stream().map(app -> {
            Gate state = app.action() == null ? Gate.ready() : gate(player, app.action());
            return new ClientApp(app.id(), app.title(), state.available(), state.detail());
        }).toList();
    }

    public boolean clientAppAvailable(Player player, String id) {
        return available(player) && APPS.stream().filter(app -> app.id().equals(id))
                .anyMatch(app -> app.action() == null || gate(player, app.action()).available());
    }

    public void openClientApp(Player player, String id) throws Exception {
        if (!available(player)) return;
        App app = APPS.stream().filter(value -> value.id().equals(id)).findFirst()
                .orElseThrow(() -> new IllegalArgumentException("Unknown phone app"));
        searches.remove(player.getUniqueId());
        if (app.action() != null) openAction(player, app.action());
        else view(player, app.view(), 0);
    }

    public PhoneStore.Preferences preferences(UUID player) {
        return this.store.state(player).preferences();
    }

    public Optional<Destination> navigation(UUID player) {
        return Optional.ofNullable(this.navigation.get(player));
    }

    public List<Destination> destinations(Player p) {
        if (!this.available(p)) {
            return List.of();
        }
        List<Destination> rows = List.copyOf(this.services.destinations(p));
        if (rows.size() > 256) {
            throw new IllegalStateException("Destination registry exceeds its bound");
        }
        if (rows.stream().map(Destination::id).distinct().count() != (long)rows.size()) {
            throw new IllegalStateException("Ambiguous destination registry");
        }
        return rows;
    }

    public void navigate(Player p, String id) {
        if (!this.available(p)) {
            return;
        }
        Destination d = this.destinations(p).stream().filter(v -> v.id().equals(id)).findFirst().orElseThrow(() -> new IllegalArgumentException("This destination is no longer commissioned"));
        if (!d.location().getWorld().equals((Object)p.getWorld())) {
            throw new IllegalStateException("Travel to the destination world before starting this route");
        }
        p.setCompassTarget(d.location());
        this.navigation.put(p.getUniqueId(), d);
        p.sendMessage("\u00a7aGPS target: " + d.title() + ". The map shows direction; it does not certify a walkable road route.");
    }

    public Gate gate(Player p, Action action) {
        return this.available(p) ? Objects.requireNonNull(this.services.gate(p, action)) : Gate.blocked("Authenticate and obtain phone access first.");
    }

    public void openAction(Player p, Action action) throws Exception {
        Gate gate = this.gate(p, action);
        if (!gate.available()) {
            throw new IllegalStateException(gate.detail());
        }
        this.services.open(p, action);
    }

    public void publish(UUID audience, UUID receipt, String category, String title, String detail) throws IOException {
        this.store.publish(new PhoneStore.Notice(receipt, audience, System.currentTimeMillis(), category, title, detail));
    }

    public List<Bulletin> publicNews() {
        return this.store.news(null).stream().map(n -> new Bulletin(n.id(), n.timeMillis(), n.title(), n.detail())).limit(32L).toList();
    }

    public void cinematic(Player p, String id, String detail) {
        if (this.available(p)) {
            this.hud.cinematic(p, id, detail);
        }
    }

    public void notification(Player p, String detail) {
        if (this.available(p)) {
            this.hud.notification(p, detail);
        }
    }

    public void dialogue(Player p, Entity speaker, String detail) {
        if (this.available(p)) {
            this.hud.dialogue(p, speaker, detail);
        }
    }

    public void open(Player p) {
        if (!this.available(p)) {
            p.sendMessage("\u00a7eThe phone needs an authenticated permitted account.");
            return;
        }
        this.searches.remove(p.getUniqueId());
        if (this.plugin.openClientPhone(p)) return;
        this.home(p);
    }

    public void openPage(Player p, String page) {
        if (!this.available(p)) {
            this.open(p);
            return;
        }
        this.searches.remove(p.getUniqueId());
        if (Set.of("maps", "news", "contacts", "directory", "assistant").contains(page)) {
            this.view(p, page, 0);
        } else {
            this.home(p);
        }
    }

    private Menu menu(Player p, String title, int size) {
        return new Menu(p, this.plugin.authenticatedSession(p), title, size,
                this.services.glyphsAvailable(p) && this.plugin.getConfig().getBoolean("phone.custom-gui", true));
    }

    private void show(Player p, Menu m) {
        p.openInventory(m.inventory);
    }

    private void home(Player p) {
        Menu m = this.menu(p, "\u00a78GTM Phone | Indraprastha", 54);
        for (int i = 0; i < APPS.size(); ++i) {
            App a = APPS.get(i);
            Gate gate = a.action() == null ? Gate.ready() : this.gate(p, a.action());
            GtmPhoneApps.put(m, 10 + i / 6 * 9 + i % 6, this.icon(a.id(), "\u00a7f" + a.title(), a.description(), (gate.available() ? "\u00a7a" : "\u00a7e") + gate.detail()), new Button(Kind.APP, a.id(), 0));
        }
        GtmPhoneApps.put(m, 17, this.icon("app_contacts", "§bJEEVA · City assistant",
                "Open the offline guide, ask a question, or choose a real service."), new Button(Kind.VIEW, "assistant", 0));
        this.service(m, p, 26, Action.EQUIPMENT, "app_amazzo", "§eWeapons & equipment");
        GtmPhoneApps.put(m, 35, this.icon("app_car_app", "§aVehicle controls",
                "Open live driving instruments and controls."), new Button(Kind.VIEW, "car", 0));
        GtmPhoneApps.put(m, 44, this.icon("app_settings", "§fDisplay settings",
                "Change your HUD, map, instruments and effects."), new Button(Kind.VIEW, "settings", 0));
        GtmPhoneApps.put(m, 45, this.icon("hotbar_frame", "\u00a7eYour hotbar", "Inspect and select any of your actual nine hotbar slots."), new Button(Kind.VIEW, "help", 0));
        GtmPhoneApps.put(m, 49, this.icon("app_maps", "\u00a7aLive map", "Give or refresh your personal terrain map"), new Button(Kind.MAP, "", 0));
        GtmPhoneApps.put(m, 53, GtmPhoneApps.item(Material.BARRIER, "\u00a7cClose", new String[0]), new Button(Kind.CLOSE, "", 0));
        this.show(p, m);
    }

    private void view(Player p, String name, int page) {
        switch (name) {
            case "home": {
                this.home(p);
                break;
            }
            case "directory": 
            case "maps": {
                this.directory(p, "", page, name.equals("maps"));
                break;
            }
            case "news": {
                this.news(p, page);
                break;
            }
            case "contacts": {
                this.contacts(p, false, page);
                break;
            }
            case "add_contacts": {
                this.contacts(p, true, page);
                break;
            }
            case "settings": {
                this.settings(p);
                break;
            }
            case "assistant": {
                this.assistant(p, "");
                break;
            }
            case "car": {
                this.car(p);
                break;
            }
            case "music": {
                this.music(p);
                break;
            }
            case "traffic": {
                this.traffic(p);
                break;
            }
            case "amazzo": 
            case "flippit": {
                Menu m = this.menu(p, name.equals("amazzo") ? "\u00a78Amazzo | Real catalogues" : "\u00a78Flippit | Your home", 27);
                this.service(m, p, 10, Action.EQUIPMENT, "app_amazzo", "Equipment catalogue");
                this.service(m, p, 12, Action.FURNITURE, "app_flippit", "Furniture catalogue and owned pieces");
                this.service(m, p, 14, Action.SIGNS, "notification_frame", "Owned signs and managed displays");
                this.service(m, p, 16, Action.FASHION, "app_fashion", "Wearable clothing");
                this.back(m, 22);
                this.show(p, m);
                break;
            }
            case "help": {
                this.hotbar(p);
                break;
            }
            default: {
                throw new IllegalArgumentException("Unknown phone view");
            }
        }
    }

    /** A real menu for the existing offline guide. It never claims a remote
     * model is connected and never interprets a prompt as a server command. */
    private void assistant(Player p, String prompt) {
        Menu m = this.menu(p, "§8JEEVA | City assistant", 27);
        String answer = GtmPhoneAssistant.answer(p, this, prompt);
        m.inventory.setItem(4, this.icon("app_contacts", "§bJEEVA · Offline city guide",
                answer, "Choose a topic below, or select Ask a question.",
                "Replies use game rules and live state; no external AI service is connected."));
        String[] topics = {"Getting started", "Driving", "Weapons", "Banking", "Jobs", "Talking to NPCs"};
        String[] prompts = {"help", "driving", "weapons", "bank", "jobs", "npc"};
        String[] icons = {"phone_shortcut", "app_car_app", "app_amazzo", "app_bank", "app_careers", "app_contacts"};
        for (int i = 0; i < topics.length; ++i) {
            GtmPhoneApps.put(m, 10 + i, this.icon(icons[i], "§f" + topics[i], "Read JEEVA's game help."),
                    new Button(Kind.ASSISTANT, prompts[i], 0));
        }
        GtmPhoneApps.put(m, 16, GtmPhoneApps.item(Material.WRITABLE_BOOK, "§bAsk a question",
                "Enter a private question in chat. Cancel returns to the phone."), new Button(Kind.SEARCH, "assistant", 0));
        GtmPhoneApps.put(m, 18, this.icon("app_maps", "§aOpen city map", "Choose an actual commissioned destination."), new Button(Kind.VIEW, "maps", 0));
        this.service(m, p, 20, Action.EQUIPMENT, "app_amazzo", "Open equipment shop");
        this.back(m, 22);
        this.service(m, p, 24, Action.GARAGE, "app_garage", "Open your garage");
        this.service(m, p, 26, Action.MISSIONS, "app_missions", "Open real missions");
        if (!prompt.isBlank()) p.sendMessage("§b[JEEVA] §f" + answer);
        this.show(p, m);
    }

    private void hotbar(Player p) {
        Menu m = this.menu(p, "\u00a78Phone | Your live hotbar", 36);
        int selected = p.getInventory().getHeldItemSlot();
        GtmPhoneApps.put(m, 4, this.icon("hotbar_frame", "\u00a7fRefresh your nine slots", "These are views of your current items.", "Select a slot below to hold its actual item."), new Button(Kind.VIEW, "help", 0));
        GtmPhoneApps.put(m, 10, this.icon("hotbar_selected", "\u00a7eSelected slot " + (selected + 1), "Select to advance to the next hotbar slot.", "No item is moved, copied or consumed."), new Button(Kind.HOTBAR, Integer.toString((selected + 1) % 9), 0));
        for (int slot = 0; slot < 9; ++slot) {
            String name;
            ItemStack actual = p.getInventory().getItem(slot);
            String string = name = actual == null || actual.getType().isAir() ? "Empty" : actual.getType().name().toLowerCase(Locale.ROOT).replace('_', ' ');
            if (actual != null && actual.hasItemMeta() && actual.getItemMeta().hasDisplayName()) {
                name = GtmPhoneApps.plain(actual.getItemMeta().getDisplayName(), 80);
            }
            ItemStack preview = actual == null || actual.getType().isAir() ? this.icon(slot == selected ? "hotbar_selected" : "hotbar_frame", "\u00a77Empty slot", new String[0]) : actual.clone();
            int number = slot + 1;
            String label = name;
            boolean active = slot == selected;
            preview.editMeta(meta -> {
                meta.setDisplayName((active ? "\u00a7e" : "\u00a7f") + number + " \u00b7 " + label);
                meta.setLore(List.of(active ? "\u00a7aCurrently held" : "\u00a77Select to hold this real slot", "\u00a77The original inventory item stays intact."));
            });
            GtmPhoneApps.put(m, 18 + slot, preview, new Button(Kind.HOTBAR, Integer.toString(slot), 0));
        }
        this.back(m, 31);
        this.show(p, m);
    }

    private void selectHotbar(Player p, int slot) {
        if (slot < 0 || slot > 8 || p.isDead()) {
            throw new IllegalStateException("This hotbar slot is unavailable");
        }
        UUID session = this.plugin.authenticatedSession(p);
        int before = p.getInventory().getHeldItemSlot();
        if (before != slot) {
            PlayerItemHeldEvent event = new PlayerItemHeldEvent(p, before, slot);
            Bukkit.getPluginManager().callEvent((Event)event);
            if (event.isCancelled() || !this.current(p, session) || p.isDead() || p.getInventory().getHeldItemSlot() != before) {
                throw new IllegalStateException("Your current item action prevents changing this slot");
            }
            p.getInventory().setHeldItemSlot(slot);
        }
        p.closeInventory();
        p.sendMessage("\u00a7aHotbar slot " + (slot + 1) + " selected. Use your normal item controls.");
    }

    private void directory(Player p, String query, int page, boolean maps) {
        int start;
        List<Destination> list = this.destinations(p).stream().filter(d -> (d.title() + " " + d.category() + " " + d.id()).toLowerCase(Locale.ROOT).contains(query.toLowerCase(Locale.ROOT))).sorted(Comparator.comparing(Destination::title)).toList();
        Menu m = this.menu(p, (String)(maps ? "\u00a78City GPS | Registered destinations" : "\u00a78Quoggle | " + (query.isBlank() ? "Service search" : query.substring(0, Math.min(18, query.length())))), 54);
        int number = Math.max(0, Math.min(page, Math.max(0, (list.size() - 1) / 36)));
        for (int i = start = number * 36; i < Math.min(list.size(), start + 36); ++i) {
            Destination d2 = list.get(i);
            boolean same = d2.location().getWorld().equals((Object)p.getWorld());
            String distance = same ? Math.round(d2.location().distance(p.getLocation())) + " blocks away" : "In " + d2.location().getWorld().getName();
            GtmPhoneApps.put(m, i - start, this.icon(GtmPhoneApps.marker(d2.category()), "\u00a7f" + d2.title(), d2.category(), distance, "\u00a7eSet this real destination as your GPS target"), new Button(Kind.DESTINATION, d2.id(), 0));
        }
        if (list.isEmpty()) {
            m.inventory.setItem(13, GtmPhoneApps.item(Material.PAPER, "\u00a77No registered destinations match", "Only commissioned locations are shown; no guessed coordinates."));
        }
        GtmPhoneApps.put(m, 40, GtmPhoneApps.item(Material.NAME_TAG, "\u00a7eSearch registered services", "Type the service name in chat after selecting."), new Button(Kind.SEARCH, maps ? "maps" : "directory", 0));
        GtmPhoneApps.put(m, 42, this.icon("app_maps", "\u00a7aOpen live terrain map", new String[0]), new Button(Kind.MAP, "", 0));
        if (number > 0) {
            GtmPhoneApps.put(m, 45, GtmPhoneApps.item(Material.ARROW, "\u00a7ePrevious", new String[0]), new Button(maps ? Kind.MAP_DIRECTORY : Kind.DIRECTORY, query, number - 1));
        }
        if (start + 36 < list.size()) {
            GtmPhoneApps.put(m, 53, GtmPhoneApps.item(Material.ARROW, "\u00a7eNext", new String[0]), new Button(maps ? Kind.MAP_DIRECTORY : Kind.DIRECTORY, query, number + 1));
        }
        this.back(m, 49);
        this.show(p, m);
    }

    static String marker(String category) {
        return switch (category) {
            case "police" -> "map_police";
            case "medical", "hospital" -> "map_hospital";
            case "fuel", "repair" -> "map_fuel";
            case "property" -> "map_property";
            case "station", "transport", "airport", "dock" -> "map_station";
            case "mission", "job" -> "map_mission";
            default -> "map_shop";
        };
    }

    private void car(Player p) {
        Menu m = this.menu(p, "\u00a78Motor Mile | Vehicle and media", 54);
        Optional<DriveData> driving = this.services.driving(p);
        if (driving.isPresent()) {
            DriveData d = driving.get();
            String speed = String.format(Locale.ROOT, "%.1f km/h", Math.abs(d.blocksPerSecond()) * 3.6);
            m.inventory.setItem(10, this.icon("speedometer_" + this.preferences(p.getUniqueId()).speedStyle().name().toLowerCase(Locale.ROOT), "\u00a7f" + d.title(), speed, "Mode: " + d.mode(), "Seats: " + d.occupiedSeats() + " / " + d.seats()));
            m.inventory.setItem(11, this.icon(d.energyKind().toLowerCase(Locale.ROOT).contains("electric") ? "battery" : "fuel", "\u00a7f" + d.energyKind(), String.format(Locale.ROOT, "%.0f%% remaining \u2022 estimate %.0f blocks", d.energyPercent(), d.estimatedRange())));
            m.inventory.setItem(12, this.icon("engine_condition", "\u00a7fVehicle condition", String.format(Locale.ROOT, "%.0f%%", d.health())));
            if (d.energyPercent() < 15.0) {
                m.inventory.setItem(13, this.icon("low_fuel", "\u00a7eLow energy", "Navigate to a commissioned fuel/service site."));
            }
            if (d.health() < 25.0) {
                m.inventory.setItem(14, this.icon("critical_damage", "\u00a7cCritical condition", "Stop safely and use an available repair service."));
            }
        } else {
            m.inventory.setItem(10, this.icon("engine_condition", "\u00a77No active vehicle session", "Enter an owned permitted vehicle for live diagnostics."));
        }
        GtmPhoneApps.put(m, 19, this.icon("app_maps", "\u00a7aNavigation", new String[0]), new Button(Kind.VIEW, "maps", 0));
        GtmPhoneApps.put(m, 20, GtmPhoneApps.item(Material.NOTE_BLOCK, "\u00a7aOriginal music and playlists", "Local game audio; no streaming or external account"), new Button(Kind.VIEW, "music", 0));
        GtmPhoneApps.put(m, 21, this.icon("app_news", "\u00a7aVerified game news", new String[0]), new Button(Kind.VIEW, "news", 0));
        GtmPhoneApps.put(m, 22, this.icon("gps_route", "\u00a7aTraffic telemetry", new String[0]), new Button(Kind.VIEW, "traffic", 0));
        this.service(m, p, 23, Action.VEHICLE_SERVICE, "map_fuel", "Refuel and repair");
        this.service(m, p, 24, Action.ROADSIDE_ASSISTANCE, "app_medical", "Roadside assistance");
        this.service(m, p, 28, Action.GARAGE, "app_garage", "Owned garage");
        this.service(m, p, 29, Action.VEHICLE_SHOP, "app_car_app", "Vehicle shop");
        GtmPhoneApps.put(m, 31, this.icon("speedometer_" + this.preferences(p.getUniqueId()).speedStyle().name().toLowerCase(Locale.ROOT), "\u00a7aLive vehicle dashboard", "Hold its 128\u00d7128 map to see current speed, energy and condition.", "The analog needle follows accepted vehicle movement."), new Button(Kind.DASHBOARD, "", 0));
        String[] controls = new String[]{"horn", "lights", "left", "right", "hazards", "cargo", "doors", "hover", "rescue"};
        for (int i = 0; i < controls.length; ++i) {
            String control = controls[i];
            Gate g = this.services.vehicleControlGate(p, control);
            GtmPhoneApps.put(m, 36 + i, GtmPhoneApps.item(g.available() ? Material.LEVER : Material.GRAY_DYE, "\u00a7f" + control, g.detail()), new Button(Kind.CONTROL, control, 0));
        }
        this.back(m, 49);
        this.show(p, m);
    }

    private void traffic(Player p) {
        Menu m = this.menu(p, "\u00a78Motor Mile | Live traffic data", 27);
        List<String> lines = this.services.traffic(p);
        for (int i = 0; i < Math.min(18, lines.size()); ++i) {
            m.inventory.setItem(i, GtmPhoneApps.item(Material.PAPER, "\u00a7f" + GtmPhoneApps.plain(lines.get(i), 90), new String[0]));
        }
        this.back(m, 22);
        this.show(p, m);
    }

    private void news(Player p, int page) {
        int start;
        LinkedHashMap<UUID, Bulletin> unique = new LinkedHashMap<UUID, Bulletin>();
        for (Bulletin b : this.services.news(p)) {
            if (unique.size() >= 256) break;
            unique.put(b.id(), b);
        }
        for (PhoneStore.Notice n : this.store.news(p.getUniqueId())) {
            unique.putIfAbsent(n.id(), new Bulletin(n.id(), n.timeMillis(), n.title(), n.detail()));
        }
        List<Bulletin> list = unique.values().stream().sorted(Comparator.comparingLong(Bulletin::timeMillis).reversed()).limit(256L).toList();
        Menu m = this.menu(p, "\u00a78Indra 24 | Verified game events", 54);
        int number = Math.max(0, Math.min(page, Math.max(0, (list.size() - 1) / 45)));
        for (int i = start = number * 45; i < Math.min(list.size(), start + 45); ++i) {
            Bulletin b = list.get(i);
            m.inventory.setItem(i - start, this.icon("notification_frame", "\u00a7f" + GtmPhoneApps.plain(b.title(), 80), GtmPhoneApps.plain(b.detail(), 320), Instant.ofEpochMilli(b.timeMillis()).toString()));
        }
        if (list.isEmpty()) {
            m.inventory.setItem(13, GtmPhoneApps.item(Material.PAPER, "\u00a77No verified city reports yet", "This feed displays recorded game events only."));
        }
        if (number > 0) {
            GtmPhoneApps.put(m, 45, GtmPhoneApps.item(Material.ARROW, "\u00a7ePrevious", new String[0]), new Button(Kind.VIEW, "news", number - 1));
        }
        if (start + 45 < list.size()) {
            GtmPhoneApps.put(m, 53, GtmPhoneApps.item(Material.ARROW, "\u00a7eNext", new String[0]), new Button(Kind.VIEW, "news", number + 1));
        }
        this.back(m, 49);
        this.show(p, m);
    }

    private void contacts(Player p, boolean add, int page) {
        int start;
        Menu m = this.menu(p, add ? "\u00a78Contacts | Authenticated players" : "\u00a78Your private contacts", 54);
        List<PhoneStore.Contact> list = add ? Bukkit.getOnlinePlayers().stream().filter(other -> !other.equals((Object)p) && this.plugin.isAuthenticated((Player)other) && !other.hasMetadata("NPC")).map(other -> new PhoneStore.Contact(other.getUniqueId(), GtmPhoneApps.plain(other.getName(), 48))).sorted(Comparator.comparing(PhoneStore.Contact::lastKnownName)).limit(256L).toList() : this.store.state(p.getUniqueId()).contacts();
        int number = Math.max(0, Math.min(page, Math.max(0, (list.size() - 1) / 45)));
        for (int i = start = number * 45; i < Math.min(list.size(), start + 45); ++i) {
            PhoneStore.Contact c = list.get(i);
            Player other2 = Bukkit.getPlayer((UUID)c.id());
            boolean online = other2 != null && this.plugin.isAuthenticated(other2);
            GtmPhoneApps.put(m, i - start, GtmPhoneApps.item(Material.PLAYER_HEAD, "\u00a7f" + c.lastKnownName(), online ? "Authenticated online" : "Offline", add ? "\u00a7aSave this UUID contact" : "\u00a7eRemove from your private contacts"), new Button(add ? Kind.ADD_CONTACT : Kind.REMOVE_CONTACT, c.id().toString(), 0));
        }
        if (!add) {
            GtmPhoneApps.put(m, 48, GtmPhoneApps.item(Material.EMERALD, "\u00a7aAdd an authenticated player", new String[0]), new Button(Kind.VIEW, "add_contacts", 0));
        }
        if (number > 0) {
            GtmPhoneApps.put(m, 45, GtmPhoneApps.item(Material.ARROW, "\u00a7ePrevious", new String[0]), new Button(Kind.VIEW, add ? "add_contacts" : "contacts", number - 1));
        }
        if (start + 45 < list.size()) {
            GtmPhoneApps.put(m, 53, GtmPhoneApps.item(Material.ARROW, "\u00a7eNext", new String[0]), new Button(Kind.VIEW, add ? "add_contacts" : "contacts", number + 1));
        }
        this.back(m, 49);
        this.show(p, m);
    }

    private void settings(Player p) {
        PhoneStore.Preferences s = this.preferences(p.getUniqueId());
        Menu m = this.menu(p, "\u00a78Phone | Saved settings", 27);
        this.setting(m, 10, "hud", "notification_frame", "Status HUD", s.hud() ? "On" : "Off");
        this.setting(m, 11, "layout", s.layout() == PhoneStore.Layout.CIRCLE ? "minimap_circle" : "minimap_rectangle", "Map layout", s.layout().name());
        this.setting(m, 12, "rotate", "player_arrow", "Map rotation", s.rotate() ? "Follow player heading" : "North up");
        this.setting(m, 13, "zoom", "gps_route", "Map width", s.zoom() + " blocks");
        this.setting(m, 14, "speed", "speedometer_" + s.speedStyle().name().toLowerCase(Locale.ROOT), "Instruments", s.speedStyle().name());
        this.setting(m, 15, "effects", "wasted_title", "Reduced effects", s.reducedEffects() ? "On" : "Off");
        this.setting(m, 16, "volume", "app_settings", "Original music volume", s.musicVolume() + "%");
        this.back(m, 22);
        this.show(p, m);
    }

    private void setting(Menu m, int slot, String key, String art, String label, String value) {
        GtmPhoneApps.put(m, slot, this.icon(art, "\u00a7f" + label, value, "\u00a7eSelect to change and save"), new Button(Kind.SETTING, key, 0));
    }

    private void changeSetting(Player p, String key) throws IOException {
        PhoneStore.Preferences s = this.preferences(p.getUniqueId());
        PhoneStore.Preferences next = switch (key) {
            case "hud" -> new PhoneStore.Preferences(!s.hud(), s.layout(), s.rotate(), s.zoom(), s.speedStyle(), s.reducedEffects(), s.musicVolume());
            case "layout" -> new PhoneStore.Preferences(s.hud(), s.layout() == PhoneStore.Layout.CIRCLE ? PhoneStore.Layout.RECTANGLE : PhoneStore.Layout.CIRCLE, s.rotate(), s.zoom(), s.speedStyle(), s.reducedEffects(), s.musicVolume());
            case "rotate" -> new PhoneStore.Preferences(s.hud(), s.layout(), !s.rotate(), s.zoom(), s.speedStyle(), s.reducedEffects(), s.musicVolume());
            case "zoom" -> new PhoneStore.Preferences(s.hud(), s.layout(), s.rotate(), s.zoom() == 256 ? 64 : s.zoom() * 2, s.speedStyle(), s.reducedEffects(), s.musicVolume());
            case "speed" -> new PhoneStore.Preferences(s.hud(), s.layout(), s.rotate(), s.zoom(), PhoneStore.SpeedStyle.values()[(s.speedStyle().ordinal() + 1) % 3], s.reducedEffects(), s.musicVolume());
            case "effects" -> new PhoneStore.Preferences(s.hud(), s.layout(), s.rotate(), s.zoom(), s.speedStyle(), !s.reducedEffects(), s.musicVolume());
            case "volume" -> new PhoneStore.Preferences(s.hud(), s.layout(), s.rotate(), s.zoom(), s.speedStyle(), s.reducedEffects(), (s.musicVolume() + 25) % 125);
            default -> throw new IllegalArgumentException("Unknown preference");
        };
        this.store.preferences(p.getUniqueId(), next);
        this.settings(p);
    }

    private void music(Player p) {
        this.music(p, "");
    }

    private void music(Player p, String query) {
        Menu m = this.menu(p, "\u00a78Motor Mile | Original local music", 27);
        int i = 0;
        List<String> saved = this.store.state(p.getUniqueId()).playlist();
        for (String id : List.of("sea_link_evening", "monsoon_steps", "market_morning")) {
            if (!GtmPhoneApps.trackTitle(id).toLowerCase(Locale.ROOT).contains(query.toLowerCase(Locale.ROOT))) continue;
            GtmPhoneApps.put(m, 10 + i, GtmPhoneApps.item(Material.NOTE_BLOCK, "\u00a7f" + GtmPhoneApps.trackTitle(id), "Original SD Craft note-block composition", "\u00a7aPlay this track locally"), new Button(Kind.MUSIC, id, 0));
            GtmPhoneApps.put(m, 14 + i, GtmPhoneApps.item(saved.contains(id) ? Material.LIME_DYE : Material.GRAY_DYE, "\u00a7f" + (saved.contains(id) ? "Remove from" : "Add to") + " playlist", GtmPhoneApps.trackTitle(id)), new Button(Kind.PLAYLIST, id, 0));
            ++i;
        }
        if (i == 0) {
            m.inventory.setItem(11, GtmPhoneApps.item(Material.PAPER, "\u00a77No local tracks match", "The authorized local catalogue has three original compositions."));
        }
        GtmPhoneApps.put(m, 4, GtmPhoneApps.item(Material.NAME_TAG, "\u00a7eSearch authorized local music", "Search these original track names in chat.", "An external music-provider integration is not configured."), new Button(Kind.SEARCH, "music", 0));
        GtmPhoneApps.put(m, 19, GtmPhoneApps.item(Material.JUKEBOX, "\u00a7aPlay your saved playlist", saved.size() + " authorized original tracks"), new Button(Kind.MUSIC, "playlist", 0));
        GtmPhoneApps.put(m, 25, GtmPhoneApps.item(Material.BARRIER, "\u00a7cStop music", new String[0]), new Button(Kind.STOP, "", 0));
        this.back(m, 22);
        this.show(p, m);
    }

    private static String trackTitle(String id) {
        return switch (id) {
            case "sea_link_evening" -> "Sea Link Evening";
            case "monsoon_steps" -> "Monsoon Steps";
            case "market_morning" -> "Market Morning";
            default -> throw new IllegalArgumentException("Unknown original track");
        };
    }

    private static int[] notes(String id) {
        int[] nArray;
        switch (id) {
            case "sea_link_evening": {
                int[] nArray2 = new int[32];
                nArray2[0] = 0;
                nArray2[1] = 7;
                nArray2[2] = 12;
                nArray2[3] = 7;
                nArray2[4] = 4;
                nArray2[5] = 7;
                nArray2[6] = 11;
                nArray2[7] = 7;
                nArray2[8] = 2;
                nArray2[9] = 9;
                nArray2[10] = 14;
                nArray2[11] = 9;
                nArray2[12] = 5;
                nArray2[13] = 9;
                nArray2[14] = 12;
                nArray2[15] = -1;
                nArray2[16] = 0;
                nArray2[17] = 4;
                nArray2[18] = 7;
                nArray2[19] = 12;
                nArray2[20] = 11;
                nArray2[21] = 7;
                nArray2[22] = 4;
                nArray2[23] = 0;
                nArray2[24] = 2;
                nArray2[25] = 5;
                nArray2[26] = 9;
                nArray2[27] = 12;
                nArray2[28] = 7;
                nArray2[29] = 4;
                nArray2[30] = 0;
                nArray = nArray2;
                nArray2[31] = -1;
                break;
            }
            case "monsoon_steps": {
                int[] nArray3 = new int[32];
                nArray3[0] = 2;
                nArray3[1] = 5;
                nArray3[2] = 9;
                nArray3[3] = 14;
                nArray3[4] = 9;
                nArray3[5] = 5;
                nArray3[6] = 2;
                nArray3[7] = -1;
                nArray3[8] = 4;
                nArray3[9] = 7;
                nArray3[10] = 11;
                nArray3[11] = 16;
                nArray3[12] = 11;
                nArray3[13] = 7;
                nArray3[14] = 4;
                nArray3[15] = -1;
                nArray3[16] = 5;
                nArray3[17] = 9;
                nArray3[18] = 12;
                nArray3[19] = 17;
                nArray3[20] = 12;
                nArray3[21] = 9;
                nArray3[22] = 5;
                nArray3[23] = -1;
                nArray3[24] = 2;
                nArray3[25] = 7;
                nArray3[26] = 9;
                nArray3[27] = 14;
                nArray3[28] = 9;
                nArray3[29] = 7;
                nArray3[30] = 2;
                nArray = nArray3;
                nArray3[31] = -1;
                break;
            }
            case "market_morning": {
                int[] nArray4 = new int[32];
                nArray4[0] = 0;
                nArray4[1] = 4;
                nArray4[2] = 7;
                nArray4[3] = 12;
                nArray4[4] = 7;
                nArray4[5] = 4;
                nArray4[6] = 2;
                nArray4[7] = 7;
                nArray4[8] = 2;
                nArray4[9] = 5;
                nArray4[10] = 9;
                nArray4[11] = 14;
                nArray4[12] = 9;
                nArray4[13] = 5;
                nArray4[14] = 4;
                nArray4[15] = 9;
                nArray4[16] = 4;
                nArray4[17] = 7;
                nArray4[18] = 11;
                nArray4[19] = 16;
                nArray4[20] = 11;
                nArray4[21] = 7;
                nArray4[22] = 5;
                nArray4[23] = 12;
                nArray4[24] = 0;
                nArray4[25] = 7;
                nArray4[26] = 12;
                nArray4[27] = 19;
                nArray4[28] = 12;
                nArray4[29] = 7;
                nArray4[30] = 4;
                nArray = nArray4;
                nArray4[31] = 0;
                break;
            }
            default: {
                throw new IllegalArgumentException("Unknown original track");
            }
        }
        return nArray;
    }

    private void tick() {
        for (UUID id : new ArrayList<UUID>(this.playing.keySet())) {
            Player p = Bukkit.getPlayer((UUID)id);
            Playing play = this.playing.get(id);
            if (p == null || !this.current(p, play.session)) {
                this.playing.remove(id);
                continue;
            }
            int[] notes = GtmPhoneApps.notes(play.tracks.get(play.track));
            int note = notes[play.step++];
            if (note >= 0) {
                p.playSound(p.getLocation(), Sound.BLOCK_NOTE_BLOCK_HARP, SoundCategory.RECORDS, (float)this.preferences(id).musicVolume() / 100.0f, (float)(0.5 * Math.pow(2.0, (double)note / 12.0)));
            }
            if (play.step < notes.length) continue;
            play.step = 0;
            if (++play.track < play.tracks.size()) continue;
            this.playing.remove(id);
        }
        this.hud.tick();
    }

    private void service(Menu m, Player p, int slot, Action action, String art, String title) {
        Gate gate = this.gate(p, action);
        GtmPhoneApps.put(m, slot, this.icon(art, "\u00a7f" + title, (gate.available() ? "\u00a7a" : "\u00a7e") + gate.detail()), new Button(Kind.SERVICE, action.name(), 0));
    }

    private void back(Menu m, int slot) {
        GtmPhoneApps.put(m, slot, this.icon("phone_shortcut", "\u00a7ePhone home", new String[0]), new Button(Kind.VIEW, "home", 0));
    }

    private static void put(Menu m, int slot, ItemStack item, Button button) {
        m.inventory.setItem(slot, item);
        m.buttons.put(slot, button);
    }

    private ItemStack icon(String id, String title, String ... lore) {
        ItemStack i = GtmPhoneApps.item(Material.PAPER, title, lore);
        i.editMeta(meta -> meta.setItemModel(Objects.requireNonNull(NamespacedKey.fromString((String)this.art.require(id).model()))));
        return i;
    }

    private static ItemStack item(Material type, String title, String ... lines) {
        ItemStack item = new ItemStack(type);
        item.editMeta(m -> {
            m.setDisplayName(title);
            ArrayList<String> lore = new ArrayList<String>();
            for (String line : lines) {
                for (String part : GtmPhoneApps.wrap(line, 46)) {
                    lore.add("\u00a77" + part);
                }
            }
            m.setLore(lore);
        });
        return item;
    }

    private static List<String> wrap(String text, int width) {
        ArrayList<String> result = new ArrayList<String>();
        StringBuilder line = new StringBuilder();
        for (String word : text.split("\\s+")) {
            if (line.length() > 0 && line.length() + word.length() + 1 > width) {
                result.add(line.toString());
                line.setLength(0);
            }
            if (!line.isEmpty()) {
                line.append(' ');
            }
            line.append(word);
        }
        if (!line.isEmpty()) {
            result.add(line.toString());
        }
        return result;
    }

    private static String plain(String text, int max) {
        String clean = Objects.toString(ChatColor.stripColor((String)text), "").replaceAll("[\\p{Cntrl}]", "").strip();
        return clean.substring(0, Math.min(max, clean.length()));
    }

    @EventHandler(priority=EventPriority.HIGHEST)
    public void click(InventoryClickEvent e) {
        Player p;
        Menu m;
        block6: {
            block5: {
                InventoryHolder inventoryHolder = e.getView().getTopInventory().getHolder();
                if (!(inventoryHolder instanceof Menu)) {
                    return;
                }
                m = (Menu)inventoryHolder;
                e.setCancelled(true);
                HumanEntity humanEntity = e.getWhoClicked();
                if (!(humanEntity instanceof Player)) break block5;
                p = (Player)humanEntity;
                if (!m.consumed && m.viewer.equals(p.getUniqueId()) && (e.getClick() == ClickType.LEFT || e.getClick() == ClickType.RIGHT)) break block6;
            }
            return;
        }
        Button button = m.buttons.get(e.getRawSlot());
        if (button == null) {
            return;
        }
        m.consumed = true;
        Bukkit.getScheduler().runTask((Plugin)this.plugin, () -> {
            if (p.getOpenInventory().getTopInventory().getHolder() != m) {
                return;
            }
            if (!this.current(p, m.session)) {
                p.closeInventory();
                return;
            }
            try {
                this.activate(p, button);
            }
            catch (Exception failed) {
                p.closeInventory();
                p.sendMessage("\u00a7e" + (failed instanceof IllegalArgumentException || failed instanceof IllegalStateException ? Objects.toString(failed.getMessage(), "Action unavailable") : "This action could not be completed or saved."));
                this.plugin.getLogger().fine("Phone action ended: " + failed.getClass().getSimpleName());
            }
        });
    }

    private void activate(Player p, Button b) throws Exception {
        switch (b.kind().ordinal()) {
            case 0: {
                App a = APPS.stream().filter(v -> v.id().equals(b.value())).findFirst().orElseThrow();
                if (a.action() != null) {
                    p.closeInventory();
                    this.openAction(p, a.action());
                    break;
                }
                this.view(p, a.view(), 0);
                break;
            }
            case 1: {
                this.view(p, b.value(), b.page());
                break;
            }
            case 2: 
            case 3: {
                this.directory(p, b.value(), b.page(), b.kind() == Kind.MAP_DIRECTORY);
                break;
            }
            case 4: {
                p.closeInventory();
                this.openAction(p, Action.valueOf(b.value()));
                break;
            }
            case 5: {
                p.closeInventory();
                this.navigate(p, b.value());
                this.hud.giveMap(p);
                break;
            }
            case 6: {
                Search search = new Search(this.plugin.authenticatedSession(p), System.nanoTime() + 30000000000L, b.value());
                this.searches.put(p.getUniqueId(), search);
                p.closeInventory();
                p.sendMessage(b.value().equals("assistant") ? "§b[JEEVA] §fType your private game question in chat, or cancel. Expires in 30 seconds."
                        : b.value().equals("music") ? "\u00a7eType an original track name in chat, or cancel. Search expires in 30 seconds." : "\u00a7eType a local service name in chat, or cancel. Search expires in 30 seconds.");
                Bukkit.getScheduler().runTaskLater((Plugin)this.plugin, () -> this.searches.remove(p.getUniqueId(), search), 600L);
                break;
            }
            case 9: {
                this.changeSetting(p, b.value());
                break;
            }
            case 8: {
                Player other = Bukkit.getPlayer((UUID)UUID.fromString(b.value()));
                if (other == null || !this.plugin.isAuthenticated(other) || other.hasMetadata("NPC")) {
                    throw new IllegalStateException("That player is no longer authenticated online");
                }
                this.store.contact(p.getUniqueId(), new PhoneStore.Contact(other.getUniqueId(), GtmPhoneApps.plain(other.getName(), 48)), true);
                this.contacts(p, false, 0);
                break;
            }
            case 7: {
                UUID id = UUID.fromString(b.value());
                PhoneStore.Contact c = this.store.state(p.getUniqueId()).contacts().stream().filter(v -> v.id().equals(id)).findFirst().orElseThrow();
                this.store.contact(p.getUniqueId(), c, false);
                this.contacts(p, false, 0);
                break;
            }
            case 10: {
                List<String> tracks;
                List<String> list = tracks = b.value().equals("playlist") ? this.store.state(p.getUniqueId()).playlist() : List.of(b.value());
                if (tracks.isEmpty()) {
                    throw new IllegalStateException("Add an original track to your playlist first");
                }
                if (!PhoneStore.TRACKS.containsAll(tracks)) {
                    throw new IllegalArgumentException("Unknown authorized track");
                }
                this.playing.put(p.getUniqueId(), new Playing(this.plugin.authenticatedSession(p), tracks));
                p.sendMessage("\u00a7aPlaying original local game audio. Use Stop music to end playback.");
                this.music(p);
                break;
            }
            case 11: {
                this.store.track(p.getUniqueId(), b.value(), !this.store.state(p.getUniqueId()).playlist().contains(b.value()));
                this.music(p);
                break;
            }
            case 12: {
                this.playing.remove(p.getUniqueId());
                p.stopSound(Sound.BLOCK_NOTE_BLOCK_HARP, SoundCategory.RECORDS);
                this.music(p);
                break;
            }
            case 13: {
                Gate g = this.services.vehicleControlGate(p, b.value());
                if (!g.available()) {
                    throw new IllegalStateException(g.detail());
                }
                p.closeInventory();
                this.services.vehicleControl(p, b.value());
                break;
            }
            case 14: {
                p.closeInventory();
                this.hud.giveMap(p);
                break;
            }
            case 15: {
                p.closeInventory();
                this.hud.giveDashboard(p);
                break;
            }
            case 16: {
                this.selectHotbar(p, Integer.parseInt(b.value()));
                break;
            }
            case 17: {
                p.closeInventory();
                break;
            }
            case 18: {
                this.assistant(p, b.value());
                break;
            }
        }
    }

    @EventHandler(priority=EventPriority.HIGHEST)
    public void drag(InventoryDragEvent e) {
        if (e.getView().getTopInventory().getHolder() instanceof Menu) {
            e.setCancelled(true);
        }
    }

    @EventHandler(priority=EventPriority.LOWEST, ignoreCancelled=true)
    public void search(AsyncPlayerChatEvent e) {
        Search s = this.searches.remove(e.getPlayer().getUniqueId());
        if (s == null || System.nanoTime() > s.expires()) {
            return;
        }
        e.setCancelled(true);
        String query = e.getMessage();
        Bukkit.getScheduler().runTask((Plugin)this.plugin, () -> {
            Player p = e.getPlayer();
            if (!this.current(p, s.session()) || System.nanoTime() > s.expires()) {
                return;
            }
            if (query.equalsIgnoreCase("cancel")) {
                this.home(p);
                return;
            }
            String clean = GtmPhoneApps.plain(query, s.scope().equals("assistant") ? 240 : 64);
            if (s.scope().equals("assistant")) {
                this.assistant(p, clean);
            } else if (s.scope().equals("music")) {
                this.music(p, clean);
            } else {
                this.directory(p, clean, 0, s.scope().equals("maps"));
            }
        });
    }

    @EventHandler(priority=EventPriority.HIGHEST)
    public void shortcut(PlayerSwapHandItemsEvent e) {
        if (CityItems.is(e.getMainHandItem(), 900002) || CityItems.is(e.getOffHandItem(), 900002)) {
            e.setCancelled(true);
            this.open(e.getPlayer());
        }
    }

    @EventHandler
    public void quit(PlayerQuitEvent e) {
        this.onAuthenticationLost(e.getPlayer());
    }

    public void onAuthenticationLost(Player p) {
        this.searches.remove(p.getUniqueId());
        this.playing.remove(p.getUniqueId());
        this.navigation.remove(p.getUniqueId());
        this.hud.forget(p);
        if (p.getOpenInventory().getTopInventory().getHolder() instanceof Menu) {
            p.closeInventory();
        }
    }

    @Override
    public void close() {
        this.closed = true;
        if (this.task != null) {
            this.task.cancel();
        }
        this.playing.clear();
        this.searches.clear();
        this.navigation.clear();
        this.hud.close();
    }

    public static interface Services {
        public Gate gate(Player var1, Action var2);

        public void open(Player var1, Action var2) throws Exception;

        public List<Destination> destinations(Player var1);

        default public String district(Player player) {
            return player.getWorld().getName();
        }

        default public boolean inCity(Player player) {
            return false;
        }

        default public int wanted(Player player) {
            return 0;
        }

        default public long wallet(Player player) {
            return 0L;
        }

        default public long bank(Player player) {
            return 0L;
        }

        default public List<Bulletin> news(Player player) {
            return List.of();
        }

        default public Optional<DriveData> driving(Player player) {
            return Optional.empty();
        }

        default public List<String> traffic(Player player) {
            return List.of("No commissioned traffic telemetry source is available.");
        }

        default public List<Location> route(Player player, Destination destination) {
            return List.of();
        }

        default public Gate vehicleControlGate(Player player, String control) {
            return Gate.blocked("This vehicle control is not commissioned for your current vehicle.");
        }

        default public void vehicleControl(Player player, String control) throws Exception {
            throw new IllegalStateException("Vehicle control unavailable");
        }

        default public boolean glyphsAvailable(Player player) {
            return false;
        }
    }

    private record App(String id, String title, Action action, String view, String description) {
    }

    public record Destination(String id, String title, String category, Location location) {

        public Destination {
            if (!(id != null && id.matches("[a-z0-9_:-]{1,96}") && title != null && !title.isBlank() && title.length() <= 100 && category != null && category.matches("[a-z_]{1,32}") && location != null && location.getWorld() != null && Double.isFinite(location.getX()) && Double.isFinite(location.getY()) && Double.isFinite(location.getZ()))) {
                throw new IllegalArgumentException("Invalid commissioned destination");
            }
            title = ChatColor.stripColor((String)title);
            location = location.clone();
        }

        public Location location() {
            return this.location.clone();
        }
    }

    public static enum Action {
        EQUIPMENT,
        FURNITURE,
        SIGNS,
        FOOD_ZOMATOO,
        FOOD_SWIFFY,
        FASHION,
        PROPERTY,
        VEHICLE_SHOP,
        GARAGE,
        VEHICLE_SERVICE,
        BANK,
        PAYMENTS,
        LOANS,
        TAXI,
        TRANSPORT,
        MISSIONS,
        JOBS,
        POLICE,
        MEDICAL,
        FESTIVALS,
        KEYS,
        ROADSIDE_ASSISTANCE;

    }

    public record Gate(boolean available, String detail) {
        public Gate {
            if (detail == null || detail.isBlank() || detail.length() > 320) {
                throw new IllegalArgumentException("A precise service status is required");
            }
        }

        public static Gate ready() {
            return new Gate(true, "Open the live game service");
        }

        public static Gate blocked(String reason) {
            return new Gate(false, reason);
        }
    }

    private static final class Menu
    implements InventoryHolder {
        final UUID viewer;
        final UUID session;
        final Map<Integer, Button> buttons = new HashMap<Integer, Button>();
        final Inventory inventory;
        boolean consumed;

        Menu(Player p, UUID nonce, String title, int size, boolean customGui) {
            this.viewer = p.getUniqueId();
            this.session = nonce;
            this.inventory = customGui
                    ? Bukkit.createInventory(this, size, GtmPhoneScreen.title(title, size, title.contains("GTM Phone")))
                    : Bukkit.createInventory(this, size, title);
        }

        public Inventory getInventory() {
            return this.inventory;
        }
    }

    private record Button(Kind kind, String value, int page) {
    }

    private static enum Kind {
        APP,
        VIEW,
        DIRECTORY,
        MAP_DIRECTORY,
        SERVICE,
        DESTINATION,
        SEARCH,
        REMOVE_CONTACT,
        ADD_CONTACT,
        SETTING,
        MUSIC,
        PLAYLIST,
        STOP,
        CONTROL,
        MAP,
        DASHBOARD,
        HOTBAR,
        CLOSE,
        ASSISTANT;

    }

    public record DriveData(String title, String mode, double blocksPerSecond, String energyKind, double energyPercent, double health, double estimatedRange, int occupiedSeats, int seats) {
        public DriveData {
            Objects.requireNonNull(title);
            Objects.requireNonNull(mode);
            Objects.requireNonNull(energyKind);
            if (!Double.isFinite(blocksPerSecond) || !Double.isFinite(energyPercent) || !Double.isFinite(health) || !Double.isFinite(estimatedRange) || energyPercent < 0.0 || energyPercent > 100.0 || health < 0.0 || health > 100.0 || estimatedRange < 0.0 || occupiedSeats < 0 || seats < 1 || occupiedSeats > seats) {
                throw new IllegalArgumentException("Invalid vehicle telemetry");
            }
        }
    }

    public record Bulletin(UUID id, long timeMillis, String title, String detail) {
        public Bulletin {
            Objects.requireNonNull(id);
            if (timeMillis < 0L || title == null || title.isBlank() || title.length() > 80 || detail == null || detail.length() > 320) {
                throw new IllegalArgumentException("Invalid verified bulletin");
            }
        }
    }

    private static final class Playing {
        final UUID session;
        final List<String> tracks;
        int track;
        int step;

        Playing(UUID session, List<String> tracks) {
            this.session = session;
            this.tracks = List.copyOf(tracks);
        }
    }

    private record Search(UUID session, long expires, String scope) {
    }
}

