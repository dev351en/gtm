package com.sdcraft.core;

import java.io.File;
import java.io.IOException;
import java.util.*;
import org.bukkit.*;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.*;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.player.PlayerMoveEvent;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.scoreboard.*;

/**
 * Persistent GTA gameplay layer: wanted heat, arrests, jail, missions, stores,
 * owned starter rewards and the in-game phone/HUD. All state changes stay on
 * the server thread and are persisted in gta-state.yml.
 */
final class GtaEngine implements Listener {
    static final String PHONE_TITLE = "§8[ §6iFruit OS 26.3 §8] §fCity Apps";
    static final String SHOP_TITLE = "§8[SD SHOP] Ammu-Nation";
    static final String MISSIONS_TITLE = "§8[SD JOBS] Mission Board";

    private record MissionDefinition(String id, String title, String profession,
            String difficulty, long rewardCents, int credits, List<String> route,
            boolean criminal, int cooldownSeconds) {}

    private record ActiveMission(String id, int stage, long startedAt) {}

    private final SDCraftCorePlugin plugin;
    private final Ledger ledger;
    private final GpsManager gps;
    private final File stateFile;
    private final YamlConfiguration state;
    private final Map<String, MissionDefinition> definitions = new LinkedHashMap<>();
    private final Map<UUID, ActiveMission> activeMissions = new HashMap<>();
    private final Map<UUID, Long> lastJailWarning = new HashMap<>();
    private final NamespacedKey actionKey;
    private long ticks;

    GtaEngine(SDCraftCorePlugin plugin, Ledger ledger, GpsManager gps) {
        this.plugin = plugin;
        this.ledger = ledger;
        this.gps = gps;
        this.stateFile = new File(plugin.getDataFolder(), "gta-state.yml");
        this.state = YamlConfiguration.loadConfiguration(stateFile);
        this.actionKey = new NamespacedKey(plugin, "gta_action");
        loadMissionDefinitions();
    }

    void close() {
        save();
    }

    void onJoin(Player player) {
        String path = "missions.active." + player.getUniqueId();
        String id = state.getString(path + ".id", "");
        if (definitions.containsKey(id)) {
            activeMissions.put(player.getUniqueId(), new ActiveMission(id,
                    state.getInt(path + ".stage", 0), state.getLong(path + ".started-at", System.currentTimeMillis())));
        }
        long jailUntil = jailUntil(player.getUniqueId());
        if (jailUntil > System.currentTimeMillis()) {
            Location jail = plugin.site("jail");
            if (jail != null) player.teleport(jail);
            player.sendMessage("§c[SDPD] You are still jailed for " + seconds(jailUntil - System.currentTimeMillis()) + ".");
        }
        updateHud(player);
    }

    boolean tryClaimStarter(Player player) {
        String base = playerPath(player.getUniqueId());
        if (state.getBoolean(base + ".starter-claimed", false)) return false;
        state.set(base + ".starter-claimed", true);
        state.set(base + ".vehicles-owned", Math.max(1, state.getInt(base + ".vehicles-owned", 0)));
        state.set(base + ".vehicles-issued", Math.max(1, state.getInt(base + ".vehicles-issued", 0)));
        save();
        return true;
    }

    boolean starterClaimed(UUID id) {
        return state.getBoolean(playerPath(id) + ".starter-claimed", false);
    }

    int wantedLevel(UUID id) {
        return Math.max(0, Math.min(5, state.getInt(playerPath(id) + ".wanted", 0)));
    }

    void recordCrime(Player player, int stars, String reason) {
        if (player == null || stars <= 0 || player.hasPermission("sdcraft.admin")) return;
        int before = wantedLevel(player.getUniqueId());
        int after = Math.min(5, Math.max(before, before + stars));
        String base = playerPath(player.getUniqueId());
        state.set(base + ".wanted", after);
        state.set(base + ".last-crime", System.currentTimeMillis());
        state.set(base + ".last-crime-reason", reason);
        save();
        player.sendTitle(stars(after), "§cWANTED: " + reason, 5, 35, 10);
        player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_BIT, 1.0f, 0.65f);
        for (Player officer : Bukkit.getOnlinePlayers()) {
            if (officer.hasPermission("sdcraft.police")) {
                officer.sendMessage("§c[SDPD] " + player.getName() + " is wanted " + after + "★ near "
                        + gps.getDistrict(player.getLocation()) + ": " + reason);
            }
        }
    }

    void clearWanted(Player player) {
        if (player == null) return;
        String base = playerPath(player.getUniqueId());
        state.set(base + ".wanted", 0);
        state.set(base + ".last-crime", 0L);
        save();
        updateHud(player);
    }

    boolean handles(String action) {
        return Set.of("phone", "shop", "garage", "wanted", "surrender", "arrest", "jail",
                "mission", "missions", "rob").contains(action);
    }

    boolean handleCommand(Player player, String action, String[] args) throws Exception {
        return switch (action) {
            case "phone" -> { openPhone(player); yield true; }
            case "shop" -> { openShop(player); yield true; }
            case "garage" -> { showGarage(player); yield true; }
            case "wanted" -> { showWanted(player); yield true; }
            case "surrender" -> { surrender(player); yield true; }
            case "arrest" -> { arrest(player, args); yield true; }
            case "jail" -> { showJail(player); yield true; }
            case "missions", "mission" -> { missionCommand(player, args); yield true; }
            case "rob" -> { startMission(player, "bank_heist"); yield true; }
            default -> false;
        };
    }

    boolean handleStandaloneCar(Player player, String[] args) throws IOException {
        if (args.length == 0) {
            showGarage(player);
            return true;
        }
        String sub = args[0].toLowerCase(Locale.ROOT);
        if (!sub.equals("buy")) {
            player.sendMessage("§e[Garage] Use §f/car buy §eto purchase a Sedan Black, or open §f/phone§e.");
            return true;
        }
        long price = plugin.getConfig().getLong("gta.shop.vehicle-sedan-cents", 150000L);
        if (!ledger.chargeBank(player.getUniqueId(), price, "vehicle:sedan_black")) {
            player.sendMessage("§c[Garage] You need " + PolicyEngine.money(price) + " in your bank.");
            return true;
        }
        String base = playerPath(player.getUniqueId());
        state.set(base + ".vehicles-owned", state.getInt(base + ".vehicles-owned", 0) + 1);
        state.set(base + ".vehicles-issued", state.getInt(base + ".vehicles-issued", 0) + 1);
        save();
        issueSedan(player);
        player.sendMessage("§a[Garage] Sedan Black purchased for " + PolicyEngine.money(price) + ".");
        return true;
    }

    boolean handleStandaloneGun(Player player, String[] args) throws IOException {
        String type = args.length == 0 ? "p30" : args[0].toLowerCase(Locale.ROOT);
        return buyGun(player, type);
    }

    boolean handleInventory(InventoryClickEvent event) {
        if (!(event.getWhoClicked() instanceof Player player)) return false;
        String title = event.getView().getTitle();
        if (!title.equals(PHONE_TITLE) && !title.equals(SHOP_TITLE) && !title.equals(MISSIONS_TITLE)) return false;
        event.setCancelled(true);
        ItemStack clicked = event.getCurrentItem();
        if (clicked == null || !clicked.hasItemMeta()) return true;
        String action = clicked.getItemMeta().getPersistentDataContainer().get(actionKey, PersistentDataType.STRING);
        if (action == null) return true;
        player.closeInventory();
        try {
            if (action.equals("gps")) gps.openGpsMenu(player);
            else if (action.equals("shop")) openShop(player);
            else if (action.equals("missions")) openMissions(player);
            else if (action.equals("garage")) showGarage(player);
            else if (action.equals("wanted")) showWanted(player);
            else if (action.equals("account")) player.performCommand("sdc account");
            else if (action.equals("loans") && plugin.loans()!=null) Bukkit.getScheduler().runTask(plugin,()->plugin.loans().open(player));
            else if (action.startsWith("buy:")) buyShopItem(player, action.substring(4));
            else if (action.startsWith("mission:")) startMission(player, action.substring(8));
        } catch (Exception ex) {
            player.sendMessage("§c[SD Craft] " + ex.getMessage());
        }
        return true;
    }

    void handleNpcAction(Player player, String rawAction) {
        String action = rawAction.toLowerCase(Locale.ROOT).replace(' ', '_');
        if (action.contains("catalog") || action.contains("buy_item") || action.contains("sale") || action.contains("negotiate")) {
            openShop(player);
        } else if (action.contains("taxi") || action.contains("metro") || action.contains("bus") || action.contains("ride")) {
            gps.openGpsMenu(player);
        } else if (action.contains("task") || action.contains("job") || action.contains("duty") || action.contains("response")
                || action.contains("delivery") || action.contains("repair")) {
            openMissions(player);
        } else if (action.contains("report") || action.contains("statement") || action.contains("case")) {
            player.sendMessage("§e[SDPD] File a verified incident with §f/sdc report <1|2|3> <description>§e.");
        } else if (action.contains("treatment") || action.contains("diagnosis") || action.contains("medical") || action.contains("revive")) {
            player.sendMessage("§a[Hospital] Use §f/sdc medical stabilize|diagnosis|treatment|admission§a.");
        } else {
            openPhone(player);
        }
    }

    void tick() {
        ticks++;
        long now = System.currentTimeMillis();
        for (Player player : Bukkit.getOnlinePlayers()) {
            UUID id = player.getUniqueId();
            long jail = jailUntil(id);
            if (jail > 0 && jail <= now) release(player);
            int wanted = wantedLevel(id);
            long lastCrime = state.getLong(playerPath(id) + ".last-crime", 0L);
            long decayMs = plugin.getConfig().getLong("gta.wanted.decay-seconds", 120L) * 1000L;
            if (wanted > 0 && jail <= now && now - lastCrime >= decayMs) {
                state.set(playerPath(id) + ".wanted", wanted - 1);
                state.set(playerPath(id) + ".last-crime", now);
                save();
                player.sendMessage("§7[SDPD] You evaded police. Wanted level reduced to " + (wanted - 1) + "★.");
            }
            if (ticks % 5 == 0) updateHud(player);
            checkMissionProgress(player);
        }
    }

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    public void onPlayerDamage(EntityDamageByEntityEvent event) {
        if (!(event.getEntity() instanceof Player victim)) return;
        if (plugin.isManagedNpc(victim)) return; // Ambient NPC combat is owned by NpcService.
        Player attacker = attacker(event.getDamager());
        if (attacker == null || attacker.equals(victim)) return;
        if (isSafeZone(victim.getLocation()) || isSafeZone(attacker.getLocation())) {
            event.setCancelled(true);
            attacker.sendMessage("§c[SDPD] Weapons are disabled in this protected civic zone.");
            return;
        }
        if (attacker.hasPermission("sdcraft.police") && wantedLevel(victim.getUniqueId()) > 0) return;
        recordCrime(attacker, event.getFinalDamage() >= victim.getHealth() ? 3 : 2, "Assault on " + victim.getName());
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onProtectedBlockBreak(BlockBreakEvent event) {
        Player player = event.getPlayer();
        if (player.getGameMode() == GameMode.CREATIVE || player.hasPermission("sdcraft.admin")) return;
        if (isSafeZone(event.getBlock().getLocation())) recordCrime(player, 1, "Civic property damage");
    }

    @EventHandler(priority = EventPriority.HIGH, ignoreCancelled = true)
    public void onMove(PlayerMoveEvent event) {
        if (event.getTo() == null) return;
        Player player = event.getPlayer();
        long jail = jailUntil(player.getUniqueId());
        if (jail > System.currentTimeMillis()) {
            Location center = plugin.site("jail");
            if (center != null && center.getWorld().equals(player.getWorld()) && center.distanceSquared(event.getTo()) > 144.0) {
                event.setTo(center);
                long now = System.currentTimeMillis();
                if (now - lastJailWarning.getOrDefault(player.getUniqueId(), 0L) > 3000L) {
                    lastJailWarning.put(player.getUniqueId(), now);
                    player.sendMessage("§c[SDPD] Sentence remaining: " + seconds(jail - now) + ".");
                }
            }
        }
    }

    private void loadMissionDefinitions() {
        File file = new File(plugin.getDataFolder(), "missions.yml");
        YamlConfiguration yaml = YamlConfiguration.loadConfiguration(file);
        ConfigurationSection section = yaml.getConfigurationSection("missions");
        if (section == null) return;
        for (String id : section.getKeys(false)) {
            String p = "missions." + id;
            List<String> route = yaml.getStringList(p + ".route");
            if (route.isEmpty()) route = fallbackRoute(id);
            definitions.put(id, new MissionDefinition(id,
                    yaml.getString(p + ".title", id.replace('_', ' ')),
                    yaml.getString(p + ".profession", "any"), yaml.getString(p + ".difficulty", "easy"),
                    yaml.getLong(p + ".reward-cents", rewardFor(yaml.getString(p + ".difficulty", "easy"))),
                    yaml.getInt(p + ".credits", creditsFor(yaml.getString(p + ".difficulty", "easy"))),
                    List.copyOf(route), yaml.getBoolean(p + ".criminal", false),
                    yaml.getInt(p + ".cooldown-seconds", 300)));
        }
    }

    private List<String> fallbackRoute(String id) {
        return switch (id) {
            case "police_report" -> List.of("police", "city_hall", "police");
            case "police_pursuit" -> List.of("police", "airport", "jail");
            case "medical_triage" -> List.of("hospital", "city_hall", "hospital");
            case "medical_emergency" -> List.of("hospital", "airport", "hospital");
            case "fire_response" -> List.of("fire", "gas_station", "fire");
            case "taxi_trip" -> List.of("city_hall", "airport");
            case "maintenance_repair" -> List.of("gas_station", "city_hall", "gas_station");
            case "delivery_job" -> List.of("dealership", "bank", "city_hall");
            case "chef_job", "retail_sale" -> List.of("dealership", "city_hall");
            case "vehicle_recovery" -> List.of("dealership", "airport", "police");
            case "street_race" -> List.of("dealership", "gas_station", "airport", "dealership");
            case "bank_heist" -> List.of("bank", "airport", "gas_station");
            default -> List.of("city_hall");
        };
    }

    private long rewardFor(String difficulty) {
        return switch (difficulty.toLowerCase(Locale.ROOT)) {
            case "hard" -> 12000L;
            case "medium" -> 8500L;
            default -> 5000L;
        };
    }

    private int creditsFor(String difficulty) {
        return switch (difficulty.toLowerCase(Locale.ROOT)) {
            case "hard" -> 3;
            case "medium" -> 2;
            default -> 1;
        };
    }

    private void missionCommand(Player player, String[] args) throws Exception {
        if (args.length < 2 || args[1].equalsIgnoreCase("list")) {
            openMissions(player);
            return;
        }
        String sub = args[1].toLowerCase(Locale.ROOT);
        if (sub.equals("status")) {
            ActiveMission active = activeMissions.get(player.getUniqueId());
            if (active == null) player.sendMessage("§7[Mission] No active mission.");
            else sendMissionStatus(player, active);
            return;
        }
        if (sub.equals("cancel")) {
            cancelMission(player);
            return;
        }
        if (sub.equals("start") && args.length >= 3) {
            startMission(player, args[2].toLowerCase(Locale.ROOT));
            return;
        }
        player.sendMessage("§e[Mission] /sdc mission list|start <id>|status|cancel");
    }

    private void startMission(Player player, String id) throws Exception {
        MissionDefinition def = definitions.get(id);
        if (def == null) throw new IllegalArgumentException("Unknown mission: " + id);
        if (activeMissions.containsKey(player.getUniqueId())) throw new IllegalStateException("Finish or cancel your active mission first.");
        if (def.criminal && !plugin.getConfig().getBoolean("crime.robbery-enabled", false)) {
            throw new IllegalStateException("Criminal missions are disabled until protected zones are enabled.");
        }
        String profession = plugin.profession(player.getUniqueId());
        if (!def.profession.equalsIgnoreCase("any") && !def.profession.equalsIgnoreCase(profession)) {
            throw new IllegalStateException("Join the " + def.profession + " profession before starting this mission.");
        }
        long completedAt = state.getLong("missions.cooldowns." + player.getUniqueId() + "." + id, 0L);
        long remaining = completedAt + def.cooldownSeconds * 1000L - System.currentTimeMillis();
        if (remaining > 0) throw new IllegalStateException("Mission cooldown: " + seconds(remaining) + ".");
        Location start = plugin.site(def.route.get(0));
        if (start == null || !start.getWorld().equals(player.getWorld()) || start.distanceSquared(player.getLocation()) > 625.0) {
            if (start != null) player.setCompassTarget(start);
            throw new IllegalStateException("Go to " + def.route.get(0) + " to start; GPS target set.");
        }
        ActiveMission active = new ActiveMission(id, Math.min(1, def.route.size()), System.currentTimeMillis());
        activeMissions.put(player.getUniqueId(), active);
        persistMission(player.getUniqueId(), active);
        if (def.criminal) recordCrime(player, 3, "Armed bank alarm");
        player.sendTitle("§6MISSION STARTED", "§f" + def.title, 5, 45, 10);
        player.sendMessage("§e[Mission] " + def.title + " started. Reward: " + PolicyEngine.money(def.rewardCents) + ".");
        if (active.stage >= def.route.size()) completeMission(player, active, def);
        else setMissionTarget(player, def, active.stage);
    }

    private void checkMissionProgress(Player player) {
        ActiveMission active = activeMissions.get(player.getUniqueId());
        if (active == null) return;
        MissionDefinition def = definitions.get(active.id);
        if (def == null || active.stage >= def.route.size()) return;
        Location target = plugin.site(def.route.get(active.stage));
        if (target == null || !target.getWorld().equals(player.getWorld()) || target.distanceSquared(player.getLocation()) > 144.0) return;
        ActiveMission next = new ActiveMission(active.id, active.stage + 1, active.startedAt);
        activeMissions.put(player.getUniqueId(), next);
        persistMission(player.getUniqueId(), next);
        player.playSound(player.getLocation(), Sound.UI_TOAST_IN, 0.8f, 1.3f);
        if (next.stage >= def.route.size()) {
            try { completeMission(player, next, def); }
            catch (Exception ex) { plugin.getLogger().severe("Mission reward failed: " + ex.getMessage()); }
        } else {
            player.sendMessage("§a[Mission] Checkpoint complete (" + next.stage + "/" + def.route.size() + ").");
            setMissionTarget(player, def, next.stage);
        }
    }

    private void completeMission(Player player, ActiveMission active, MissionDefinition def) throws Exception {
        ledger.rewardCareer(player.getUniqueId(), def.rewardCents, def.credits, "mission:" + def.id);
        activeMissions.remove(player.getUniqueId());
        state.set("missions.active." + player.getUniqueId(), null);
        state.set("missions.cooldowns." + player.getUniqueId() + "." + def.id, System.currentTimeMillis());
        save();
        player.sendTitle("§aMISSION PASSED", "§e+" + PolicyEngine.money(def.rewardCents) + "  §b+" + def.credits + " RP", 10, 60, 15);
        player.playSound(player.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 1.0f, 1.0f);
    }

    private void cancelMission(Player player) {
        if (activeMissions.remove(player.getUniqueId()) == null) {
            player.sendMessage("§7[Mission] No active mission.");
            return;
        }
        state.set("missions.active." + player.getUniqueId(), null);
        save();
        player.sendMessage("§c[Mission] Mission cancelled; no reward awarded.");
    }

    private void setMissionTarget(Player player, MissionDefinition def, int stage) {
        String site = def.route.get(stage);
        Location location = plugin.site(site);
        if (location != null) player.setCompassTarget(location);
        player.sendMessage("§e[Mission] Next objective: reach §f" + site.replace('_', ' ') + "§e (checkpoint "
                + (stage + 1) + "/" + def.route.size() + ").");
    }

    private void sendMissionStatus(Player player, ActiveMission active) {
        MissionDefinition def = definitions.get(active.id);
        if (def == null) return;
        player.sendMessage("§6[Mission] §f" + def.title + " §7checkpoint " + Math.min(active.stage + 1, def.route.size())
                + "/" + def.route.size() + " §eReward " + PolicyEngine.money(def.rewardCents));
        if (active.stage < def.route.size()) setMissionTarget(player, def, active.stage);
    }

    private void persistMission(UUID id, ActiveMission active) {
        String path = "missions.active." + id;
        state.set(path + ".id", active.id);
        state.set(path + ".stage", active.stage);
        state.set(path + ".started-at", active.startedAt);
        save();
    }

    private void surrender(Player player) {
        if (wantedLevel(player.getUniqueId()) == 0) {
            player.sendMessage("§7[SDPD] You are not currently wanted.");
            return;
        }
        state.set(playerPath(player.getUniqueId()) + ".surrender-until", System.currentTimeMillis() + 15000L);
        save();
        player.sendMessage("§e[SDPD] Hands raised for 15 seconds. Remain still while an officer uses /sdc arrest " + player.getName() + ".");
        player.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.SLOWNESS, 300, 5, false, false));
    }

    private void arrest(Player officer, String[] args) throws IOException {
        if (!officer.hasPermission("sdcraft.police") && !officer.hasPermission("sdcraft.admin")) {
            throw new IllegalStateException("Police authorization required.");
        }
        if (args.length < 2) throw new IllegalArgumentException("/sdc arrest <player>");
        Player suspect = Bukkit.getPlayerExact(args[1]);
        if (suspect == null || !suspect.getWorld().equals(officer.getWorld())
                || suspect.getLocation().distanceSquared(officer.getLocation()) > 64.0) {
            throw new IllegalStateException("Wanted player must be online and within 8 blocks.");
        }
        int level = wantedLevel(suspect.getUniqueId());
        if (level == 0) throw new IllegalStateException("That player is not wanted.");
        long surrender = state.getLong(playerPath(suspect.getUniqueId()) + ".surrender-until", 0L);
        if (level < 3 && surrender < System.currentTimeMillis()) {
            throw new IllegalStateException("Low-level suspect must use /sdc surrender before arrest.");
        }
        int[] jailMinutes = {5, 10, 20};
        int tier = level <= 1 ? 0 : level <= 3 ? 1 : 2;
        long until = System.currentTimeMillis() + jailMinutes[tier] * 60000L;
        String base = playerPath(suspect.getUniqueId());
        state.set(base + ".jail-until", until);
        state.set(base + ".wanted", 0);
        state.set(base + ".surrender-until", 0);
        save();
        long[] fines = {5000L, 15000L, 30000L};
        boolean paid = ledger.chargeWallet(suspect.getUniqueId(), fines[tier], "conviction:level_" + level);
        if (!paid) paid = ledger.chargeBank(suspect.getUniqueId(), fines[tier], "conviction:level_" + level);
        Location jail = plugin.site("jail");
        if (jail != null) suspect.teleport(jail);
        suspect.sendTitle("§cBUSTED", "§fJailed " + jailMinutes[tier] + " min • Fine " + (paid ? PolicyEngine.money(fines[tier]) : "unpaid"), 10, 60, 15);
        officer.sendMessage("§a[SDPD] " + suspect.getName() + " arrested at wanted level " + level + ".");
    }

    private void release(Player player) {
        state.set(playerPath(player.getUniqueId()) + ".jail-until", 0L);
        save();
        player.teleport(plugin.getSurfaceSpawn(player.getWorld()));
        player.sendMessage("§a[SDPD] Sentence completed. You have been released at City Hall.");
    }

    private void showJail(Player player) {
        long remaining = jailUntil(player.getUniqueId()) - System.currentTimeMillis();
        player.sendMessage(remaining > 0 ? "§c[SDPD] Sentence remaining: " + seconds(remaining) + "." : "§7[SDPD] You are not jailed.");
    }

    private long jailUntil(UUID id) {
        return state.getLong(playerPath(id) + ".jail-until", 0L);
    }

    private void showWanted(Player player) {
        int level = wantedLevel(player.getUniqueId());
        String reason = state.getString(playerPath(player.getUniqueId()) + ".last-crime-reason", "none");
        player.sendMessage("§c[SDPD] Wanted: " + stars(level) + " §7Last incident: §f" + reason);
    }

    private void showGarage(Player player) {
        String base = playerPath(player.getUniqueId());
        int owned = state.getInt(base + ".vehicles-owned", 0);
        int issued = state.getInt(base + ".vehicles-issued", 0);
        long price = plugin.getConfig().getLong("gta.shop.vehicle-sedan-cents", 150000L);
        player.sendMessage("§b[Garage] Sedans owned: §f" + owned + " §7| delivered keys: " + issued);
        player.sendMessage("§e[Garage] Buy another Sedan Black for " + PolicyEngine.money(price) + " with §f/car buy§e.");
    }

    private void issueSedan(Player player) {
        if (Bukkit.getPluginManager().isPluginEnabled("MTVehicles")) {
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "mtv givecar " + player.getName() + " FFW36Q");
        } else player.sendMessage("§c[Garage] MTVehicles is unavailable; purchase recorded for later delivery.");
    }

    private boolean buyGun(Player player, String type) throws IOException {
        Map<String, Long> prices = Map.of("p30", 25000L, "deagle", 65000L, "uzi", 70000L,
                "remington", 85000L, "ak47", 120000L, "m4", 135000L, "awp", 180000L, "fnp90", 110000L);
        String normalized = switch (type) {
            case "ak", "ak47" -> "ak47";
            case "m4", "m4a1" -> "m4";
            case "shotgun", "remington" -> "remington";
            case "sniper", "awp" -> "awp";
            case "smg", "uzi" -> "uzi";
            case "p90", "fnp90" -> "fnp90";
            case "deagle" -> "deagle";
            default -> "p30";
        };
        long price = prices.get(normalized);
        if (!ledger.chargeBank(player.getUniqueId(), price, "weapon:" + normalized)) {
            player.sendMessage("§c[Ammu-Nation] You need " + PolicyEngine.money(price) + " in your bank.");
            return true;
        }
        if (Bukkit.getPluginManager().isPluginEnabled("QualityArmory")) {
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "qa give " + normalized + " " + player.getName());
        } else {
            player.getInventory().addItem(plugin.guns().createGun(GunEngine.GunType.PISTOL));
        }
        player.sendMessage("§a[Ammu-Nation] Purchased " + normalized.toUpperCase(Locale.ROOT) + " for " + PolicyEngine.money(price) + ". Ammunition sold separately.");
        return true;
    }

    private void buyShopItem(Player player, String id) throws IOException {
        if (id.startsWith("gun:")) { buyGun(player, id.substring(4)); return; }
        record Product(long cents, String qaId, int amount) {}
        Map<String, Product> products = Map.of(
                "9mm", new Product(2500L, "9mm", 32), "556", new Product(4500L, "556", 32),
                "762", new Product(5000L, "762", 32), "shells", new Product(3500L, "12gauge", 16));
        Product product = products.get(id);
        if (product == null) throw new IllegalArgumentException("Unknown shop product.");
        if (!ledger.chargeWallet(player.getUniqueId(), product.cents, "ammo:" + id)) {
            throw new IllegalStateException("Insufficient wallet cash: " + PolicyEngine.money(product.cents) + " required.");
        }
        if (Bukkit.getPluginManager().isPluginEnabled("QualityArmory")) {
            Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "qa give " + product.qaId + " " + player.getName() + " " + product.amount);
        } else {
            String nativeId = id.equals("shells") ? "shotgun_shells" : id.equals("556") || id.equals("762") ? "rifle_ammo" : "9mm_ammo";
            player.getInventory().addItem(plugin.guns().createAmmo(nativeId, product.amount));
        }
        player.sendMessage("§a[Ammu-Nation] Purchased " + product.amount + "x " + id + " for " + PolicyEngine.money(product.cents) + ".");
    }

    private void openPhone(Player player) {
        boolean lending=plugin.loans()!=null && plugin.loans().available(player);
        if (!lending && Bukkit.getPluginManager().isPluginEnabled("CommandPanels")
                && Bukkit.dispatchCommand(player, "cityphone")) return;
        Inventory inventory = Bukkit.createInventory(null, 27, PHONE_TITLE);
        fill(inventory);
        inventory.setItem(10, menuApp(CityItems.APP_GPS, "§b§lSnapmatic GPS", "gps", "§7Tap to set live city waypoint"));
        inventory.setItem(11, menuApp(CityItems.APP_JOBS, "§6§lMission Board", "missions", "§7Jobs, races and emergency calls"));
        inventory.setItem(12, menuApp(CityItems.APP_GEAR, "§c§lAmmu-Nation", "shop", "§7Browse weapons and ammunition"));
        inventory.setItem(14, menuApp(CityItems.APP_GARAGE, "§a§lMotorsport Garage", "garage", "§7Owned vehicles and dealership"));
        inventory.setItem(15, menuApp(CityItems.APP_BANK, "§2§lMaze Bank Mobile", "account", "§7Wallet, bank and career rank"));
        if(lending) inventory.setItem(13,menu(Material.BOOK,"§6ARK Bank Loans","loans","§7Borrow and repay ARK"));
        inventory.setItem(16, menuApp(CityItems.APP_SAFETY, "§4§lLSPD Wanted & Bail", "wanted", "§7Heat, surrender and jail status"));
        player.openInventory(inventory);
    }

    private ItemStack menuApp(int customModel, String name, String action, String... lore) {
        ItemStack item = new ItemStack(Material.PAPER);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(name);
            meta.setCustomModelData(customModel);
            meta.setLore(List.of(lore));
            meta.getPersistentDataContainer().set(actionKey, PersistentDataType.STRING, action);
            item.setItemMeta(meta);
        }
        return item;
    }

    private void openShop(Player player) {
        Inventory inventory = Bukkit.createInventory(null, 27, SHOP_TITLE);
        fill(inventory);
        inventory.setItem(9, menu(Material.CROSSBOW, "§fP30 Pistol §7- §e$250", "buy:gun:p30", "§7Entry-level sidearm"));
        inventory.setItem(10, menu(Material.CROSSBOW, "§fUzi SMG §7- §e$700", "buy:gun:uzi", "§7Compact automatic weapon"));
        inventory.setItem(11, menu(Material.CROSSBOW, "§fAK-47 §7- §e$1,200", "buy:gun:ak47", "§7High-powered rifle"));
        inventory.setItem(12, menu(Material.CROSSBOW, "§fAWP §7- §e$1,800", "buy:gun:awp", "§7Long-range precision rifle"));
        inventory.setItem(14, menu(Material.IRON_NUGGET, "§f32x 9mm §7- §e$25", "buy:9mm", "§7Pistol and SMG ammunition"));
        inventory.setItem(15, menu(Material.IRON_NUGGET, "§f32x 5.56 §7- §e$45", "buy:556", "§7Rifle ammunition"));
        inventory.setItem(16, menu(Material.IRON_NUGGET, "§f32x 7.62 §7- §e$50", "buy:762", "§7Heavy rifle ammunition"));
        inventory.setItem(17, menu(Material.FIREWORK_STAR, "§f16x Shells §7- §e$35", "buy:shells", "§7Shotgun ammunition"));
        player.openInventory(inventory);
    }

    private void openMissions(Player player) {
        Inventory inventory = Bukkit.createInventory(null, 27, MISSIONS_TITLE);
        fill(inventory);
        int slot = 9;
        for (MissionDefinition def : definitions.values()) {
            if (slot >= 18) break;
            Material icon = def.criminal ? Material.TNT : def.profession.equals("police") ? Material.IRON_BARS
                    : def.profession.equals("medic") ? Material.GLISTERING_MELON_SLICE
                    : def.id.contains("race") || def.id.contains("vehicle") ? Material.MINECART : Material.MAP;
            inventory.setItem(slot++, menu(icon, "§e" + def.title, "mission:" + def.id,
                    "§7" + def.difficulty + " • " + def.profession, "§aReward " + PolicyEngine.money(def.rewardCents) + " + " + def.credits + " RP"));
        }
        player.openInventory(inventory);
    }

    private ItemStack menu(Material material, String name, String action, String... lore) {
        ItemStack item = new ItemStack(material);
        ItemMeta meta = item.getItemMeta();
        meta.setDisplayName(name);
        meta.setLore(List.of(lore));
        if (action.equals("account")) meta.setCustomModelData(CityItems.CASH);
        meta.getPersistentDataContainer().set(actionKey, PersistentDataType.STRING, action);
        item.setItemMeta(meta);
        return item;
    }

    private void fill(Inventory inventory) {
        ItemStack filler = menu(Material.GRAY_STAINED_GLASS_PANE, " ", "noop");
        for (int i = 0; i < inventory.getSize(); i++) inventory.setItem(i, filler);
    }

    private void updateHud(Player player) {
        if (!plugin.getConfig().getBoolean("gta.hud.enabled", true) || !ledger.exists(player.getUniqueId())) return;
        ScoreboardManager manager = Bukkit.getScoreboardManager();
        if (manager == null) return;
        Scoreboard board = manager.getNewScoreboard();
        Objective objective = board.registerNewObjective("sdgta", Criteria.DUMMY, "§6§lSD CRAFT");
        objective.setDisplaySlot(DisplaySlot.SIDEBAR);
        objective.getScore("§7" + gps.getDistrict(player.getLocation())).setScore(6);
        objective.getScore("§eWallet §f" + PolicyEngine.money(ledger.wallet(player.getUniqueId()))).setScore(5);
        objective.getScore("§6Bank §f" + PolicyEngine.money(ledger.bank(player.getUniqueId()))).setScore(4);
        objective.getScore("§cWanted §f" + stars(wantedLevel(player.getUniqueId()))).setScore(3);
        ActiveMission mission = activeMissions.get(player.getUniqueId());
        objective.getScore(mission == null ? "§7No active mission" : "§aMission §f" + definitions.get(mission.id).title).setScore(2);
        objective.getScore(jailUntil(player.getUniqueId()) > System.currentTimeMillis() ? "§cJAILED" : "§b/phone").setScore(1);
        player.setScoreboard(board);
    }

    private boolean isSafeZone(Location location) {
        int radius = plugin.getConfig().getInt("gta.safe-zone-radius", 18);
        for (String site : List.of("spawn", "city_hall", "hospital", "bank", "police")) {
            Location center = plugin.site(site);
            if (center != null && center.getWorld().equals(location.getWorld()) && center.distanceSquared(location) <= radius * radius) return true;
        }
        return false;
    }

    private Player attacker(Entity entity) {
        if (entity instanceof Player player) return player;
        if (entity instanceof Projectile projectile && projectile.getShooter() instanceof Player player) return player;
        return null;
    }

    private String playerPath(UUID id) {
        return "players." + id;
    }

    private String stars(int wanted) {
        return "§c" + "★".repeat(Math.max(0, wanted)) + "§8" + "☆".repeat(Math.max(0, 5 - wanted));
    }

    private String seconds(long millis) {
        long total = Math.max(0L, (millis + 999L) / 1000L);
        return (total / 60L) + "m " + (total % 60L) + "s";
    }

    private void save() {
        try {
            state.save(stateFile);
        } catch (IOException ex) {
            plugin.getLogger().severe("GTA STATE SAVE FAILED: " + ex.getMessage());
        }
    }
}
