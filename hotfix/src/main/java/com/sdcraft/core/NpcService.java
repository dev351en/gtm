package com.sdcraft.core;

import com.sdcraft.core.GtaEngine;
import com.sdcraft.core.Ledger;
import com.sdcraft.core.PolicyEngine;
import com.sdcraft.core.SDCraftCorePlugin;
import com.sdcraft.core.gtm.CityRoster;
import java.io.File;
import java.io.IOException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Random;
import java.util.Set;
import java.util.UUID;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.GameMode;
import org.bukkit.NamespacedKey;
import org.bukkit.Material;
import org.bukkit.OfflinePlayer;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Entity;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Player;
import org.bukkit.entity.Projectile;
import org.bukkit.entity.Villager;
import org.bukkit.entity.ArmorStand;
import org.bukkit.entity.Mob;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.world.EntitiesLoadEvent;
import org.bukkit.event.world.EntitiesUnloadEvent;
import org.bukkit.metadata.FixedMetadataValue;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.Plugin;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.projectiles.ProjectileSource;
import org.bukkit.util.Vector;

/**
 * Maintained population overlay reconstructed from the preserved 1.0.3 adapter.
 * Identity/roster data stays authoritative; physical actors are bounded and temporary.
 */
final class NpcService implements Listener {
    private static final String[] FIRST_NAMES = new String[]{"Aarav", "Aditi", "Akash", "Anaya", "Arnav", "Diya", "Farhan", "Isha", "Jai", "Kriti", "Manav", "Maya", "Nikhil", "Pooja", "Rahul", "Rhea", "Sahil", "Tara", "Varun", "Zoya"};
    private static final String[] LAST_NAMES = new String[]{"Agarwal", "Bose", "Chandra", "Dutta", "Gill", "Jain", "Khan", "Malik", "Menon", "Mishra", "Nair", "Patel", "Rao", "Roy", "Saxena", "Sharma", "Singh", "Soni", "Verma", "Yadav"};
    private static final String[] CIVILIAN_ROLES = new String[]{"Office worker", "Commuter", "College student", "Courier", "Mechanic", "Tourist", "Construction worker", "Food vendor", "Street photographer", "Taxi passenger", "Warehouse worker", "Shop assistant", "Security guard", "Delivery rider"};
    private static final String[] MERCHANT_ROLES = new String[]{"Street-food merchant", "Clothing merchant", "Electronics merchant", "Book seller", "Market trader", "Souvenir merchant"};
    private final JavaPlugin plugin;
    private final YamlConfiguration identities;
    private final Ledger ledger;
    private final GtaEngine gta;
    private final File anchorsFile;
    private final YamlConfiguration anchors;
    private final Map<String, AmbientProfile> ambient;
    private final CityRoster roster;
    private final NpcIdentityIndex ownership;
    private final NamespacedKey identityKey;
    private final NamespacedKey schemaKey;
    private final Set<String> legacyBlocked = new LinkedHashSet<>();
    private Object citizensRegistry;
    private boolean reconciled;
    private boolean closing;
    private final Map<String, Active> live = new LinkedHashMap<String, Active>();
    private final Map<String, Retaliation> retaliation = new HashMap<String, Retaliation>();
    private final Map<String, ConversationHold> conversationHolds = new HashMap<>();
    private final Map<String, Long> lastMeleeAt = new HashMap<String, Long>();
    private final Map<String, Long> nextWanderAt = new HashMap<String, Long>();
    private final Map<String, Long> respawnAfter = new HashMap<String, Long>();
    private final Map<UUID, Long> crimeNoticeAfter = new HashMap<UUID, Long>();
    private final Set<String> defeated = new HashSet<String>();
    private final Random rng = new Random();
    private long pulseCount;

    NpcService(JavaPlugin plugin, YamlConfiguration identities, Ledger ledger, GtaEngine gta) {
        this.plugin = plugin;
        this.identities = identities;
        this.ledger = ledger;
        this.gta = gta;
        this.anchorsFile = new File(plugin.getDataFolder(), "anchors.yml");
        this.anchors = YamlConfiguration.loadConfiguration((File)this.anchorsFile);
        int target = plugin.getConfig().getInt("population.target-total", 100);
        int named = this.namedIds().size();
        int toughPercent = plugin.getConfig().getInt("population.ambient-tough-percent", 30);
        boolean expanded = plugin.getConfig().getBoolean("gtm.experimental-roster");
        this.ambient = this.createAmbientProfiles(expanded ? 80 : NpcService.generatedAmbientCount(target, named), toughPercent);
        if (expanded) {
            if (named != 20 || target != 100) {
                throw new IllegalStateException("Extended roster expects the original 100 identities");
            }
            try {
                this.roster = new CityRoster(plugin.getResource("gtm-population.tsv"));
            }
            catch (IOException ex) {
                throw new IllegalStateException("Cannot load surveyed GTM roster", ex);
            }
            for (CityRoster.Citizen citizen : this.roster.citizens().values()) {
                String string;
                if (this.known(citizen.id())) {
                    throw new IllegalStateException("NPC identity conflict: " + citizen.id());
                }
                String role = citizen.role();
                boolean merchant = Set.of("shopkeeper", "food_seller", "fashion_seller").contains(role);
                if (merchant) {
                    string = "retail";
                } else {
                    switch (role) {
                        case "healthcare": {
                            string = "medical";
                            break;
                        }
                        case "fire_rescue": {
                            string = "fire";
                            break;
                        }
                        case "police": {
                            string = "police";
                            break;
                        }
                        case "rail_ropeway": 
                        case "road_transport": {
                            string = "transport";
                            break;
                        }
                        default: {
                            string = "civilian";
                        }
                    }
                }
                String department = string;
                this.ambient.put(citizen.id(), new AmbientProfile(citizen.name(), role.replace('_', ' '), department, role.equals("black_lotus") || role.equals("police"), merchant));
            }
        } else {
            this.roster = null;
        }
        this.ownership = new NpcIdentityIndex(new HashSet<>(this.ids()));
        this.identityKey = new NamespacedKey(plugin, "population_identity");
        this.schemaKey = new NamespacedKey(plugin, "population_schema");
        this.ensureDefaultAnchors(null);
    }

    static int generatedAmbientCount(int targetTotal, int namedCount) {
        if (targetTotal < 0 || namedCount < 0) {
            throw new IllegalArgumentException("Population cannot be negative");
        }
        return Math.min(500, Math.max(0, targetTotal - namedCount));
    }

    static boolean deterministicTough(int ordinal, int percent) {
        if (ordinal < 0 || percent < 0 || percent > 100) {
            throw new IllegalArgumentException("Invalid tough policy");
        }
        return Math.floorMod(ordinal * 37 + 11, 100) < percent;
    }

    private Map<String, AmbientProfile> createAmbientProfiles(int count, int toughPercent) {
        LinkedHashMap<String, AmbientProfile> profiles = new LinkedHashMap<String, AmbientProfile>();
        for (int i = 0; i < count; ++i) {
            String department;
            boolean tough;
            String id = String.format(Locale.ROOT, "ambient_%03d", i + 1);
            String person = FIRST_NAMES[i % FIRST_NAMES.length] + " " + LAST_NAMES[Math.floorMod(i * 7 + i / FIRST_NAMES.length, LAST_NAMES.length)];
            boolean patrol = i < 2;
            boolean merchant = !patrol && i % 5 == 0;
            boolean bl = tough = patrol || NpcService.deterministicTough(i, toughPercent);
            department = patrol ? "police" : (merchant ? "retail" : "civilian");
            String role = patrol ? "Patrol officer" : (merchant ? MERCHANT_ROLES[i / 5 % MERCHANT_ROLES.length] : CIVILIAN_ROLES[i % CIVILIAN_ROLES.length]);
            profiles.put(id, new AmbientProfile(person, role, department, tough, merchant));
        }
        return profiles;
    }

    private Collection<String> namedIds() {
        ConfigurationSection section = this.identities.getConfigurationSection("npcs");
        return section == null ? List.of() : new LinkedHashSet(section.getKeys(false));
    }

    Collection<String> ids() {
        ArrayList<String> result = new ArrayList<String>(this.namedIds());
        result.addAll(this.ambient.keySet());
        return result;
    }

    String name(String id) {
        AmbientProfile profile = this.ambient.get(id);
        return profile != null ? profile.name() : this.identities.getString("npcs." + id + ".name", id);
    }

    String role(String id) {
        AmbientProfile profile = this.ambient.get(id);
        return profile != null ? profile.role() : this.identities.getString("npcs." + id + ".role", "Staff");
    }

    String dept(String id) {
        AmbientProfile profile = this.ambient.get(id);
        return profile != null ? profile.department() : this.identities.getString("npcs." + id + ".department", "civilian");
    }

    String greeting(String id, String lang) {
        AmbientProfile profile = this.ambient.get(id);
        if (profile != null) {
            if (profile.merchant()) {
                return "Welcome! I trade everyday city goods. Right-click again to browse the city shop.";
            }
            if (profile.tough()) {
                return "Keep it peaceful. I can handle myself, but I am just going about my day.";
            }
            return "Hello! New Blockston is busy today. I am heading through the city.";
        }
        return this.identities.getString("npcs." + id + ".greeting." + lang, "Hello! Select a service.");
    }

    List<String> actions(String id) {
        AmbientProfile profile = this.ambient.get(id);
        if (profile != null) {
            return profile.merchant() ? List.of("view_catalog") : List.of();
        }
        return this.identities.getStringList("npcs." + id + ".actions");
    }

    String skin(String id) {
        if (this.roster != null && this.roster.citizens().containsKey(id)) {
            return "npc-skins/" + id + ".png";
        }
        return this.isAmbient(id) ? "ambient-generated" : this.identities.getString("npcs." + id + ".skin", "skin_" + id + ".png");
    }

    String model(String id) {
        if (this.roster != null && this.roster.citizens().containsKey(id)) {
            return "classic";
        }
        return this.isAmbient(id) ? (Math.floorMod(id.hashCode(), 2) == 0 ? "classic" : "slim") : this.identities.getString("npcs." + id + ".model", "classic");
    }

    boolean known(String id) {
        return this.namedIds().contains(id) || this.ambient.containsKey(id);
    }

    boolean isAmbient(String id) {
        return this.ambient.containsKey(id);
    }

    boolean isMerchant(String id) {
        AmbientProfile p = this.ambient.get(id);
        return p != null && p.merchant();
    }

    boolean isTough(String id) {
        AmbientProfile p = this.ambient.get(id);
        return p != null && p.tough();
    }

    int configuredPopulation() {
        return this.ids().size();
    }

    int activePolice() {
        int n = 0;
        for (Active a : this.live.values()) {
            if (!a.police()) continue;
            ++n;
        }
        return n;
    }

    int activeOther() {
        int n = 0;
        for (Active a : this.live.values()) {
            if (a.police()) continue;
            ++n;
        }
        return n;
    }

    int activeAmbient() {
        int n = 0;
        for (Active a : this.live.values()) {
            if (!a.ambient()) continue;
            ++n;
        }
        return n;
    }

    int anchors() {
        ConfigurationSection s = this.anchors.getConfigurationSection("anchors");
        return s == null ? 0 : s.getKeys(false).size();
    }

    void setAnchor(String id, Location location) throws IOException {
        if (!this.known(id)) {
            throw new IllegalArgumentException("NPC ID not found");
        }
        String path = "anchors." + id;
        this.anchors.set(path + ".world", (Object)Objects.requireNonNull(location.getWorld()).getName());
        this.anchors.set(path + ".x", (Object)location.getX());
        this.anchors.set(path + ".y", (Object)location.getY());
        this.anchors.set(path + ".z", (Object)location.getZ());
        this.anchors.set(path + ".yaw", (Object)location.getYaw());
        this.anchors.save(this.anchorsFile);
    }

    private Map<String, double[]> namedDefaultAnchors() {
        LinkedHashMap<String, double[]> defaults = new LinkedHashMap<String, double[]>();
        defaults.put("nisha_bhat", new double[]{8.0, 71.0, 4.0, 180.0});
        defaults.put("sameer_qureshi", new double[]{16.0, 71.0, 4.0, 90.0});
        defaults.put("rehan_khan", new double[]{6.0, 71.0, 4.0, 270.0});
        defaults.put("anjali_rao", new double[]{26.0, 68.0, 64.0, 0.0});
        defaults.put("mira_rao", new double[]{120.0, 66.0, -44.0, 180.0});
        defaults.put("arjun_shah", new double[]{114.0, 67.0, -46.0, 90.0});
        defaults.put("kabir_sethi", new double[]{100.0, 68.0, -28.0, 0.0});
        defaults.put("riya_kapoor", new double[]{122.0, 66.0, -48.0, 0.0});
        defaults.put("asha_mehta", new double[]{-62.0, 65.0, 142.0, 180.0});
        defaults.put("rohan_iyer", new double[]{-62.0, 65.0, 138.0, 90.0});
        defaults.put("sana_ali", new double[]{-62.0, 65.0, 140.0, 270.0});
        defaults.put("karan_joshi", new double[]{-62.0, 65.0, 146.0, 0.0});
        defaults.put("priya_desai", new double[]{60.0, 68.0, -116.0, 180.0});
        defaults.put("aditya_verma", new double[]{62.0, 69.0, -116.0, 270.0});
        defaults.put("kavya_nair", new double[]{192.0, 70.0, 82.0, 180.0});
        defaults.put("dev_malhotra", new double[]{182.0, 69.0, 78.0, 90.0});
        defaults.put("imran_sheikh", new double[]{-150.0, 69.0, -80.0, 180.0});
        defaults.put("neha_patel", new double[]{-146.0, 67.0, -82.0, 270.0});
        defaults.put("vikram_singh", new double[]{-206.0, 70.0, 62.0, 180.0});
        defaults.put("meera_kulkarni", new double[]{-206.0, 70.0, 58.0, 90.0});
        return defaults;
    }

    private void ensureDefaultAnchors(World world) {
        String worldName = world != null ? world.getName() : this.plugin.getConfig().getString("world.name", "world");
        Map<String, double[]> defaults = this.namedDefaultAnchors();
        boolean modified = false;
        for (Map.Entry<String, double[]> entry : defaults.entrySet()) {
            String path = "anchors." + entry.getKey();
            if (this.anchors.contains(path + ".x")) continue;
            double[] c = entry.getValue();
            this.anchors.set(path + ".world", (Object)worldName);
            this.anchors.set(path + ".x", (Object)c[0]);
            this.anchors.set(path + ".y", (Object)c[1]);
            this.anchors.set(path + ".z", (Object)c[2]);
            this.anchors.set(path + ".yaw", (Object)c[3]);
            modified = true;
        }
        if (world != null) {
            modified |= this.ensureAmbientAnchors(world, defaults);
        }
        if (modified) {
            this.saveAnchors();
        }
    }

    private boolean ensureAmbientAnchors(World world, Map<String, double[]> defaults) {
        ArrayList<double[]> bases = new ArrayList<double[]>(defaults.values());
        boolean modified = false;
        int i = 0;
        for (String id : this.ambient.keySet()) {
            if (this.roster != null && this.roster.citizens().containsKey(id)) continue;
            String path = "anchors." + id;
            if (this.anchors.contains(path + ".x")) {
                ++i;
                continue;
            }
            double[] base = (double[])bases.get(i % bases.size());
            int ring = i / bases.size();
            double angle = Math.toRadians((double)(i % bases.size()) * 47.0 + (double)ring * 90.0);
            double radius = 4.0 + (double)ring * 2.0;
            Location desired = new Location(world, base[0] + Math.cos(angle) * radius, base[1], base[2] + Math.sin(angle) * radius, (float)Math.toDegrees(angle + Math.PI), 0.0f);
            Location safe = this.findWalkable(desired, 8);
            if (safe == null) {
                ++i;
                continue; // Defer until actual loaded geometry supplies a safe position.
            }
            this.anchors.set(path + ".world", (Object)world.getName());
            this.anchors.set(path + ".x", (Object)safe.getX());
            this.anchors.set(path + ".y", (Object)safe.getY());
            this.anchors.set(path + ".z", (Object)safe.getZ());
            this.anchors.set(path + ".yaw", (Object)safe.getYaw());
            modified = true;
            ++i;
        }
        return modified;
    }

    private void saveAnchors() {
        try {
            this.anchors.save(this.anchorsFile);
        }
        catch (IOException ex) {
            this.plugin.getLogger().warning("Failed to save NPC anchors: " + ex.getMessage());
        }
    }

    private Location location(String id) {
        CityRoster.Citizen citizen;
        String path = "anchors." + id;
        if (!this.anchors.contains(path + ".x") && this.roster != null && (citizen = this.roster.citizens().get(id)) != null) {
            World city = Bukkit.getWorld((String)this.plugin.getConfig().getString("world.name", "world"));
            return city == null ? null : new Location(city, (double)citizen.x() + 0.5, (double)citizen.y(), (double)citizen.z() + 0.5);
        }
        World world = Bukkit.getWorld((String)this.anchors.getString(path + ".world", ""));
        if (world == null || !this.anchors.contains(path + ".x")) {
            return null;
        }
        return new Location(world, this.anchors.getDouble(path + ".x"), this.anchors.getDouble(path + ".y"), this.anchors.getDouble(path + ".z"), (float)this.anchors.getDouble(path + ".yaw"), 0.0f);
    }

    private Location findWalkable(Location desired, int horizontalSearch) {
        World world = desired.getWorld();
        if (world == null) return null;
        int baseX = desired.getBlockX(), baseY = desired.getBlockY(), baseZ = desired.getBlockZ();
        for (int radius = 0; radius <= horizontalSearch; radius++) {
            for (int dx = -radius; dx <= radius; dx++) {
                for (int dz = -radius; dz <= radius; dz++) {
                    if (radius > 0 && Math.abs(dx) != radius && Math.abs(dz) != radius) continue;
                    int x = baseX + dx, z = baseZ + dz;
                    if (!world.isChunkLoaded(x >> 4, z >> 4)) continue;
                    for (int dy : new int[] {0, 1, -1, 2, -2, 3, -3, -4}) {
                        int y = baseY + dy;
                        if (y <= world.getMinHeight() || y >= world.getMaxHeight() - 2) continue;
                        Block floor = world.getBlockAt(x, y - 1, z);
                        Block feet = world.getBlockAt(x, y, z), head = world.getBlockAt(x, y + 1, z);
                        if (!floor.getType().isSolid() || !feet.isPassable() || !head.isPassable()
                                || feet.isLiquid() || head.isLiquid() || hazardous(floor.getType())
                                || hazardous(feet.getType()) || hazardous(head.getType())
                                || !NpcTerrain.supportsStanding(floor.getCollisionShape().getBoundingBoxes())) continue;
                        return new Location(world, x + 0.5, y, z + 0.5, desired.getYaw(), 0);
                    }
                }
            }
        }
        return null;
    }

    private static boolean hazardous(Material material) {
        return material == Material.LAVA || material == Material.FIRE || material == Material.SOUL_FIRE
                || material == Material.MAGMA_BLOCK || material == Material.CACTUS
                || material == Material.POWDER_SNOW || material == Material.CAMPFIRE
                || material == Material.SOUL_CAMPFIRE;
    }

    boolean canAddServiceWorker(int existing) {
        NpcPopulationPolicy.Budget limits = budget(existing);
        return live.size() < limits.total() && activeOther() < limits.other();
    }

    private NpcPopulationPolicy.Budget budget(int workers) {
        return NpcPopulationPolicy.budget(plugin.getConfig().getInt("population.max-physical-total", 100),
                plugin.getConfig().getInt("population.max-physical-police", 6),
                plugin.getConfig().getInt("population.max-physical-nonpolice", 94), workers,
                plugin.getConfig().getInt("population.max-spawns-per-tick", 4));
    }

    private int serviceWorkers() {
        return plugin instanceof SDCraftCorePlugin core ? core.serviceWorkerCount() : 0;
    }

    void tick() {
        if (closing) return;
        World defaultWorld = Bukkit.getWorld(plugin.getConfig().getString("world.name", "world"));
        if (defaultWorld == null && !Bukkit.getWorlds().isEmpty()) defaultWorld = Bukkit.getWorlds().getFirst();
        if (defaultWorld != null) ensureDefaultAnchors(defaultWorld);
        if (!reconciled) {
            reconciled = true;
            for (World world : Bukkit.getWorlds()) reconcile(world.getLivingEntities());
        }
        for (var entry : new ArrayList<>(live.entrySet())) {
            if (activeEntity(entry.getKey()) == null) remove(entry.getKey(), entry.getValue());
        }
        NpcPopulationPolicy.Budget limits = budget(serviceWorkers());
        double activation = plugin.getConfig().getDouble("population.activation-blocks", 56);
        double deactivation = plugin.getConfig().getDouble("population.deactivation-blocks", 80);
        List<Location> players = Bukkit.getOnlinePlayers().stream()
                .filter(p -> !p.hasMetadata("NPC") && identify(p) == null && authenticated(p))
                .map(Player::getLocation).toList();
        Set<UUID> jailed = roster == null || defaultWorld == null ? Set.of()
                : roster.prisoners(Math.floorDiv(defaultWorld.getFullTime(), 24000L));
        Map<String, Double> distances = new HashMap<>();
        for (String id : ids()) {
            Location anchor = location(id);
            Active active = live.get(id);
            CityRoster.Citizen citizen = roster == null ? null : roster.citizens().get(id);
            double nearest = nearestSquared(anchor, players);
            if (active != null) nearest = Math.min(nearest, nearestSquared(active.entity().getLocation(), players));
            distances.put(id, nearest);
            boolean allowed = citizen == null || !jailed.contains(citizen.uuid());
            boolean should = allowed && anchor != null && NpcPopulationPolicy.active(active != null, nearest, activation, deactivation);
            if (!should && active != null) remove(id, active);
        }
        // Preserve nearby staff first. Over-budget physical actors are abstracted, never deleted from the roster.
        List<String> retained = new ArrayList<>(live.keySet());
        retained.sort(Comparator.<String>comparingInt(id -> isAmbient(id) ? 1 : 0)
                .thenComparingDouble(id -> distances.getOrDefault(id, Double.POSITIVE_INFINITY)).thenComparing(id -> id));
        int total = 0, police = 0, other = 0;
        for (String id : retained) {
            Active active = live.get(id);
            if (limits.permits(total, police, other, active.police())) {
                total++; if (active.police()) police++; else other++;
            } else remove(id, active);
        }
        List<String> candidates = new ArrayList<>(ids());
        candidates.sort(Comparator.<String>comparingInt(id -> isAmbient(id) ? 1 : 0)
                .thenComparingDouble(id -> distances.getOrDefault(id, Double.POSITIVE_INFINITY)).thenComparing(id -> id));
        legacyBlocked.clear();
        int admitted = 0;
        long now = System.currentTimeMillis();
        for (String id : candidates) {
            if (live.containsKey(id) || admitted >= limits.admissions() || respawnAfter.getOrDefault(id, 0L) > now) continue;
            Location anchor = location(id);
            CityRoster.Citizen citizen = roster == null ? null : roster.citizens().get(id);
            if (citizen != null && jailed.contains(citizen.uuid())) continue;
            boolean policeNpc = dept(id).equalsIgnoreCase("police");
            if (anchor == null || !NpcPopulationPolicy.active(false, distances.get(id), activation, deactivation)
                    || !limits.permits(live.size(), activePolice(), activeOther(), policeNpc)
                    || !anchor.getWorld().isChunkLoaded(anchor.getBlockX() >> 4, anchor.getBlockZ() >> 4)) continue;
            if (legacyOccupies(id, anchor)) { legacyBlocked.add(id); continue; }
            Location safe = spawnPosition(id, anchor);
            if (safe == null) continue;
            if (spawn(id, safe, policeNpc)) admitted++;
        }
    }

    private static double nearestSquared(Location at, List<Location> players) {
        if (at == null || at.getWorld() == null) return Double.POSITIVE_INFINITY;
        double nearest = Double.POSITIVE_INFINITY;
        for (Location player : players) if (at.getWorld().equals(player.getWorld()))
            nearest = Math.min(nearest, at.distanceSquared(player));
        return nearest;
    }

    /** An explicit conversation briefly stops this actor; combat always takes precedence. */
    void holdConversation(Player player, Entity entity) {
        String id = identify(entity);
        Active active = id == null ? null : live.get(id);
        if (closing || active == null || !active.ambient() || activeEntity(id) != entity
                || !(entity instanceof LivingEntity living) || !(plugin instanceof SDCraftCorePlugin core)) return;
        UUID session = core.authenticatedSession(player);
        long now = System.currentTimeMillis();
        double distance = player.getWorld().equals(entity.getWorld())
                ? player.getLocation().distanceSquared(entity.getLocation()) : Double.POSITIVE_INFINITY;
        if (!NpcPopulationPolicy.mayHoldConversation(authenticated(player), session != null,
                player.isOnline() && !player.isDead() && !core.isDowned(player), player.hasLineOfSight(entity),
                retaliation.containsKey(id), distance, now, now + 30_000)) return;
        ConversationHold previous = conversationHolds.get(id);
        conversationHolds.put(id, new ConversationHold(player.getUniqueId(), session, now + 30_000,
                previous == null ? living.hasAI() : previous.hadAi()));
        NpcNavigation.stop(entity, active.citizensNpc());
        // The villager's own brain must not start another walk while its conversational turn is active.
        // Citizens Player navigation is stopped above; never change a real player's AI or state.
        if (entity instanceof Mob) living.setAI(false);
    }

    private boolean conversationHeld(String id, Active active, Entity entity, long now) {
        ConversationHold hold = conversationHolds.get(id);
        if (hold == null) return false;
        Player player = Bukkit.getPlayer(hold.player());
        SDCraftCorePlugin core = plugin instanceof SDCraftCorePlugin value ? value : null;
        boolean sameWorld = player != null && player.getWorld().equals(entity.getWorld());
        double distance = sameWorld ? player.getLocation().distanceSquared(entity.getLocation()) : Double.POSITIVE_INFINITY;
        boolean allowed = NpcPopulationPolicy.mayHoldConversation(player != null && authenticated(player),
                core != null && player != null && hold.session().equals(core.authenticatedSession(player)),
                core != null && player != null && player.isOnline() && !player.isDead() && !core.isDowned(player),
                sameWorld && player.hasLineOfSight(entity), retaliation.containsKey(id), distance, now, hold.expiresAt());
        if (!allowed) { releaseConversation(id, entity); return false; }
        NpcNavigation.stop(entity, active.citizensNpc());
        if (entity instanceof LivingEntity living) {
            Vector toward = player.getEyeLocation().toVector().subtract(living.getEyeLocation().toVector());
            if (toward.lengthSquared() > .001) {
                Location facing = entity.getLocation().setDirection(toward);
                entity.setRotation(facing.getYaw(), Math.max(-45, Math.min(45, facing.getPitch())));
            }
        }
        return true;
    }

    private void releaseConversation(String id, Entity entity) {
        ConversationHold previous = conversationHolds.remove(id);
        if (previous != null && entity instanceof Mob mob && mob.isValid()) mob.setAI(previous.hadAi());
    }

    private boolean legacyOccupies(String id, Location anchor) {
        String expected = label(id);
        for (Entity entity : anchor.getWorld().getNearbyEntities(anchor, 24, 12, 24)) {
            if (!(entity instanceof LivingEntity) || entity instanceof ArmorStand || identify(entity) != null) continue;
            if (expected.equals(entity.getCustomName())) return true;
        }
        return false;
    }

    private Location spawnPosition(String id, Location anchor) {
        int perChunk = Math.max(1, Math.min(16, plugin.getConfig().getInt("population.max-per-chunk", 6)));
        for (int radius = 0; radius <= 3; radius++) {
            for (int dx = -radius; dx <= radius; dx++) for (int dz = -radius; dz <= radius; dz++) {
                if (radius > 0 && Math.abs(dx) != radius && Math.abs(dz) != radius) continue;
                Location candidate = findWalkable(anchor.clone().add(dx, 0, dz), 0);
                if (candidate == null) continue;
                int occupants = 0;
                boolean crowded = false;
                for (Active active : live.values()) {
                    Entity entity = active.entity();
                    if (!entity.isValid() || !entity.getWorld().equals(candidate.getWorld())) continue;
                    Location occupied = entity.getLocation();
                    if (occupied.getBlockX() >> 4 == candidate.getBlockX() >> 4
                            && occupied.getBlockZ() >> 4 == candidate.getBlockZ() >> 4) occupants++;
                    if (occupied.distanceSquared(candidate) < 2.25) crowded = true;
                }
                if (occupants >= perChunk || crowded) continue;
                if (candidate.getWorld().getNearbyEntities(candidate, .8, 1.8, .8).stream()
                        .anyMatch(e -> e instanceof LivingEntity && !(e instanceof ArmorStand))) continue;
                return candidate;
            }
        }
        return null;
    }

    void pulse() {
        if (closing) return;
        pulseCount++;
        long now = System.currentTimeMillis();
        int wanderRadius = Math.max(2, Math.min(20, plugin.getConfig().getInt("population.ambient-wander-radius-blocks", 12)));
        double configuredDamage = plugin.getConfig().getDouble("population.ambient-melee-damage", 2);
        double meleeDamage = Double.isFinite(configuredDamage) ? Math.max(0, Math.min(6, configuredDamage)) : 2;
        for (var entry : new ArrayList<>(live.entrySet())) {
            String id = entry.getKey();
            Active active = entry.getValue();
            Entity entity = activeEntity(id);
            if (!active.ambient() || entity == null) continue;
            Retaliation fight = retaliation.get(id);
            if (fight != null) {
                releaseConversation(id, entity);
                Player attacker = Bukkit.getPlayer(fight.attacker());
                boolean sameWorld = attacker != null && attacker.getWorld().equals(entity.getWorld());
                double distance = sameWorld ? attacker.getLocation().distanceSquared(entity.getLocation()) : Double.POSITIVE_INFINITY;
                boolean protectedArea = attacker != null && (gta.isSafeZone(attacker.getLocation()) || gta.isSafeZone(entity.getLocation()));
                boolean downed = attacker != null && plugin instanceof SDCraftCorePlugin core && core.isDowned(attacker);
                boolean survival = attacker != null && (attacker.getGameMode() == GameMode.SURVIVAL || attacker.getGameMode() == GameMode.ADVENTURE);
                if (!NpcPopulationPolicy.mayRetaliate(attacker != null && authenticated(attacker),
                        attacker != null && attacker.isOnline() && !attacker.isDead(), survival, sameWorld,
                        protectedArea, downed, distance, now, fight.expiresAt())) {
                    retaliation.remove(id);
                    NpcNavigation.stop(entity, active.citizensNpc());
                } else if (active.tough()) {
                    navigate(active, attacker.getLocation());
                    boolean visible = entity instanceof LivingEntity living && living.hasLineOfSight(attacker);
                    if (NpcPopulationPolicy.mayStrike(distance, visible, now, lastMeleeAt.getOrDefault(id, 0L))
                            && (!(plugin instanceof SDCraftCorePlugin core) || core.properties().mayEnter(attacker, entity.getLocation()))) {
                        lastMeleeAt.put(id, now);
                        if (entity instanceof LivingEntity living) living.swingMainHand();
                        double before = attacker.getHealth() + attacker.getAbsorptionAmount();
                        // Keep the existing custom-damage path: a Citizens Player is not a real player criminal.
                        attacker.damage(meleeDamage);
                        if (attacker.getHealth() + attacker.getAbsorptionAmount() < before) {
                            Vector knockback = attacker.getLocation().toVector().subtract(entity.getLocation().toVector());
                            if (knockback.lengthSquared() > .01) attacker.setVelocity(knockback.normalize().multiply(.35).setY(.18));
                        }
                    }
                    continue;
                } else {
                    if (now >= nextWanderAt.getOrDefault(id, 0L)) {
                        flee(active, attacker, wanderRadius);
                        nextWanderAt.put(id, now + 1500);
                    }
                    continue;
                }
            }
            if (conversationHeld(id, active, entity, now)) continue;
            if (pulseCount % 8 != 0 || now < nextWanderAt.getOrDefault(id, 0L)) continue;
            if (entity.getLocation().distanceSquared(active.home()) > 4.0 * wanderRadius * wanderRadius) {
                navigate(active, active.home());
            } else if (rng.nextDouble() < .55) {
                Location desired = active.home().clone().add(rng.nextInt(wanderRadius * 2 + 1) - wanderRadius,
                        0, rng.nextInt(wanderRadius * 2 + 1) - wanderRadius);
                Location target = findWalkable(desired, 3);
                if (target != null) navigate(active, target);
            }
            nextWanderAt.put(id, now + 3500 + rng.nextInt(4500));
        }
    }

    private void flee(Active active, Player attacker, int radius) {
        Entity entity = active.entity();
        Vector away = entity.getLocation().toVector().subtract(attacker.getLocation().toVector()).setY(0);
        if (away.lengthSquared() < .01) away = new Vector(1, 0, 0);
        Location target = findWalkable(entity.getLocation().clone().add(away.normalize().multiply(Math.min(radius, 8))), 3);
        if (target != null) navigate(active, target);
    }

    private void navigate(Active active, Location target) {
        NpcNavigation.move(active.entity(), active.citizensNpc(), target);
    }

    private boolean spawn(String id, Location where, boolean police) {
        World world = where.getWorld();
        if (world == null || !world.isChunkLoaded(where.getBlockX() >> 4, where.getBlockZ() >> 4)) return false;
        boolean ambientNpc = isAmbient(id);
        String text = label(id);
        Object citizensNpc = null;
        Entity entity = null;
        if (Bukkit.getPluginManager().isPluginEnabled("Citizens")) {
            try {
                Object registry = citizensRegistry();
                citizensNpc = registry.getClass().getMethod("createNPC", EntityType.class, String.class)
                        .invoke(registry, EntityType.PLAYER, text);
                citizensNpc.getClass().getMethod("setProtected", boolean.class).invoke(citizensNpc, !ambientNpc);
                if (!ambientNpc) {
                    try {
                        Class<?> skinClass = Class.forName("net.citizensnpcs.trait.SkinTrait");
                        Object skin = citizensNpc.getClass().getMethod("getOrAddTrait", Class.class).invoke(citizensNpc, skinClass);
                        skin.getClass().getMethod("setSkinName", String.class).invoke(skin, name(id));
                    } catch (ReflectiveOperationException ignored) { }
                }
                try {
                    Class<?> lookClass = Class.forName("net.citizensnpcs.trait.LookClose");
                    Object look = citizensNpc.getClass().getMethod("getOrAddTrait", Class.class).invoke(citizensNpc, lookClass);
                    look.getClass().getMethod("lookClose", boolean.class).invoke(look, true);
                    look.getClass().getMethod("setRange", double.class).invoke(look, 6.0);
                } catch (ReflectiveOperationException ignored) { }
                citizensNpc.getClass().getMethod("spawn", Location.class).invoke(citizensNpc, where);
                Object created = citizensNpc.getClass().getMethod("getEntity").invoke(citizensNpc);
                if (created instanceof Entity spawned && spawned.isValid()) entity = spawned;
            } catch (ReflectiveOperationException | LinkageError failure) {
                plugin.getLogger().warning("Citizens spawn failed for " + id + "; using Paper villager fallback: " + failure.getClass().getSimpleName());
            }
        }
        if (entity == null) {
            destroyCitizens(citizensNpc);
            citizensNpc = null;
            try {
                entity = world.spawn(where, Villager.class, villager -> {
                    villager.setPersistent(false);
                    villager.setAI(ambientNpc);
                    villager.setInvulnerable(!ambientNpc);
                    villager.setSilent(!ambientNpc);
                    villager.setCollidable(false);
                    villager.setRemoveWhenFarAway(false);
                    villager.setAdult();
                    villager.setAgeLock(true);
                    if (!ambientNpc) villager.setGravity(false);
                });
            } catch (RuntimeException failure) {
                plugin.getLogger().warning("NPC fallback failed for " + id + ": " + failure.getClass().getSimpleName());
                return false;
            }
        }
        entity.setCustomName(text);
        entity.setCustomNameVisible(true);
        mark(entity, id);
        if (!ownership.claim(id, entity.getUniqueId())) {
            destroyCitizens(citizensNpc);
            entity.remove();
            return false;
        }
        live.put(id, new Active(entity.getUniqueId(), citizensNpc, police, ambientNpc,
                isTough(id), isMerchant(id), where.clone(), entity));
        nextWanderAt.put(id, System.currentTimeMillis() + 1500 + rng.nextInt(4500));
        return true;
    }

    private String label(String id) {
        String tag = switch (dept(id).toLowerCase(Locale.ROOT)) {
            case "police" -> "§c[SDPD] ";
            case "medical" -> "§a[Hospital] ";
            case "fire" -> "§4[Fire] ";
            case "bank" -> "§e[Bank] ";
            case "transport" -> "§6[Transit] ";
            case "civic" -> "§b[City Info] ";
            case "retail" -> "§d[Shop] ";
            default -> "§7[Citizen] ";
        };
        return tag + "§f" + name(id);
    }

    private Object citizensRegistry() throws ReflectiveOperationException {
        if (citizensRegistry != null) return citizensRegistry;
        Class<?> api = Class.forName("net.citizensnpcs.api.CitizensAPI");
        Class<?> storeType = Class.forName("net.citizensnpcs.api.npc.NPCDataStore");
        Object store = Class.forName("net.citizensnpcs.api.npc.MemoryNPCDataStore").getConstructor().newInstance();
        // This population is runtime materialization, never another persistent Citizens save.
        citizensRegistry = api.getMethod("createAnonymousNPCRegistry", storeType).invoke(null, store);
        return citizensRegistry;
    }

    private void mark(Entity entity, String id) {
        entity.getPersistentDataContainer().set(identityKey, PersistentDataType.STRING, id);
        entity.getPersistentDataContainer().set(schemaKey, PersistentDataType.INTEGER, 1);
        entity.setPersistent(false);
        entity.setMetadata("NPC", new FixedMetadataValue(plugin, true));
    }

    private static void destroyCitizens(Object npc) {
        if (npc == null) return;
        try { npc.getClass().getMethod("destroy").invoke(npc); }
        catch (ReflectiveOperationException ignored) { }
    }

    private void reconcile(Collection<? extends Entity> entities) {
        if (closing) return;
        for (Entity entity : entities) {
            // Real Player PDC and public "NPC" metadata cannot grant ownership or bypass authentication.
            if (!(entity instanceof Villager) || entity instanceof Player) continue;
            String id = entity.getPersistentDataContainer().get(identityKey, PersistentDataType.STRING);
            Integer schema = entity.getPersistentDataContainer().get(schemaKey, PersistentDataType.INTEGER);
            if (id == null || !Integer.valueOf(1).equals(schema) || !known(id)) continue;
            Active existing = live.get(id);
            if (existing != null && existing.uuid().equals(entity.getUniqueId())) continue;
            if (existing != null && activeEntity(id) == null) remove(id, existing);
            NpcPopulationPolicy.Budget limits = budget(serviceWorkers());
            boolean police = dept(id).equalsIgnoreCase("police");
            if (live.containsKey(id) || !limits.permits(live.size(), activePolice(), activeOther(), police)
                    || !ownership.claim(id, entity.getUniqueId())) {
                entity.remove(); // Only an explicitly tagged duplicate physical materialization.
                continue;
            }
            Location home = location(id);
            if (home == null || !home.getWorld().equals(entity.getWorld())) home = entity.getLocation();
            mark(entity, id);
            live.put(id, new Active(entity.getUniqueId(), null, police, isAmbient(id), isTough(id),
                    isMerchant(id), home.clone(), entity));
        }
    }

    @EventHandler
    public void onEntitiesLoad(EntitiesLoadEvent event) { reconcile(event.getEntities()); }

    @EventHandler
    public void onEntitiesUnload(EntitiesUnloadEvent event) {
        for (Entity entity : event.getEntities()) {
            String id = identify(entity);
            if (id != null) remove(id, live.get(id));
        }
    }

    Entity activeEntity(String id) {
        Active active = live.get(id);
        if (active == null || !id.equals(ownership.identify(active.uuid()))) return null;
        Entity entity = active.entity();
        if (!entity.isValid() || entity.isDead()) return null;
        Location at = entity.getLocation();
        if (!at.getWorld().equals(active.home().getWorld())) return null;
        return at.getWorld().isChunkLoaded(at.getBlockX() >> 4, at.getBlockZ() >> 4) ? entity : null;
    }

    boolean isAttackable(Entity entity) {
        String id = identify(entity);
        return id != null && isAmbient(id) && activeEntity(id) == entity;
    }

    String identify(Entity entity) {
        return entity == null ? null : ownership.identify(entity.getUniqueId());
    }

    private Player attackingPlayer(Entity source) {
        Player player;
        Projectile projectile;
        ProjectileSource projectileSource;
        Player player2;
        if (source instanceof Player && this.identify((Entity)(player2 = (Player)source)) == null && this.authenticated(player2)) {
            return player2;
        }
        if (source instanceof Projectile && (projectileSource = (projectile = (Projectile)source).getShooter()) instanceof Player && this.identify((Entity)(player = (Player)projectileSource)) == null && this.authenticated(player)) {
            return player;
        }
        return null;
    }

    private boolean authenticated(Player player) {
        SDCraftCorePlugin core;
        JavaPlugin javaPlugin = this.plugin;
        return javaPlugin instanceof SDCraftCorePlugin && (core = (SDCraftCorePlugin)javaPlugin).isAuthenticated(player);
    }

    @EventHandler(priority=EventPriority.HIGHEST, ignoreCancelled=false)
    public void onNpcDamage(EntityDamageByEntityEvent event) {
        Entity entity;
        String id = this.identify(event.getEntity());
        if (id == null) {
            return;
        }
        if (!this.isAmbient(id)) {
            event.setCancelled(true);
            Player attacker = this.attackingPlayer(event.getDamager());
            if (attacker != null) {
                attacker.sendMessage("\u00a7c[SD Craft] Service NPCs are protected.");
            }
            return;
        }
        if (event.isCancelled() || this.defeated.contains(id)) {
            return;
        }
        Player attacker = this.attackingPlayer(event.getDamager());
        if (attacker == null) {
            event.setCancelled(true);
            return;
        }
        if (gta.isSafeZone(attacker.getLocation()) || gta.isSafeZone(event.getEntity().getLocation())
                || plugin instanceof SDCraftCorePlugin core && !core.properties().mayEnter(attacker, event.getEntity().getLocation())) {
            event.setCancelled(true);
            attacker.sendMessage("§c[Street] Combat is disabled in this protected area.");
            return;
        }
        Active active = this.live.get(id);
        if (active == null || !((entity = event.getEntity()) instanceof LivingEntity)) {
            return;
        }
        LivingEntity victim = (LivingEntity)entity;
        releaseConversation(id, entity);
        long now = System.currentTimeMillis();
        if (now >= this.crimeNoticeAfter.getOrDefault(attacker.getUniqueId(), 0L)) {
            this.gta.recordCrime(attacker, 1, "Assault on pedestrian " + this.name(id));
            this.crimeNoticeAfter.put(attacker.getUniqueId(), now + 10000L);
        }
        if (event.getFinalDamage() >= victim.getHealth()) {
            event.setCancelled(true);
            this.defeat(id, active, victim, attacker);
            return;
        }
        long retaliationSeconds = this.plugin.getConfig().getLong("population.ambient-retaliation-seconds", 20L);
        this.retaliation.put(id, new Retaliation(attacker.getUniqueId(), now + retaliationSeconds * 1000L));
        if (!active.tough()) {
            flee(active, attacker, Math.max(2, Math.min(20, plugin.getConfig().getInt("population.ambient-wander-radius-blocks", 12))));
            nextWanderAt.put(id, now + 1500);
            attacker.sendMessage("§e[Street] " + name(id) + " runs for safety!");
        } else {
            navigate(active, attacker.getLocation());
            attacker.sendMessage("§c[Street] " + name(id) + " fights back!");
        }
    }

    private void defeat(String id, Active active, LivingEntity victim, Player attacker) {
        if (!this.authenticated(attacker)) {
            return;
        }
        if (!this.defeated.add(id)) {
            return;
        }
        victim.setInvulnerable(true);
        long min = Math.max(1L, this.plugin.getConfig().getLong("population.ambient-loot-min-cents", 300L));
        long max = Math.max(min, this.plugin.getConfig().getLong("population.ambient-loot-max-cents", 1500L));
        long cents = min + this.rng.nextLong(max - min + 1L);
        if (active.merchant()) {
            cents += this.plugin.getConfig().getLong("population.ambient-merchant-bonus-cents", 500L);
        }
        if (this.plugin.getConfig().getBoolean("population.ambient-loot-enabled", true) && this.ledger.exists(attacker.getUniqueId())) {
            try {
                this.ledger.creditWallet(attacker.getUniqueId(), cents, "ambient pedestrian loot: " + id);
                attacker.sendMessage("\u00a7a[Street Loot] You picked up " + PolicyEngine.money(cents) + ".");
            }
            catch (IOException ex) {
                this.plugin.getLogger().warning("Failed to credit ambient loot: " + ex.getMessage());
            }
        }
        if (this.rng.nextDouble() < 0.55) {
            Material material = this.rng.nextBoolean() ? Material.BREAD : Material.COOKED_BEEF;
            victim.getWorld().dropItemNaturally(victim.getLocation(), new ItemStack(material, 1 + this.rng.nextInt(2)));
        } else if (this.rng.nextDouble() < 0.25) {
            victim.getWorld().dropItemNaturally(victim.getLocation(), new ItemStack(Material.IRON_NUGGET, 1 + this.rng.nextInt(3)));
        }
        this.gta.recordCrime(attacker, active.merchant() ? 2 : 1, "Street robbery of " + this.name(id));
        long cooldown = this.plugin.getConfig().getLong("population.ambient-respawn-seconds", 180L) * 1000L;
        this.respawnAfter.put(id, System.currentTimeMillis() + cooldown);
        Bukkit.getScheduler().runTask((Plugin)this.plugin, () -> {
            this.remove(id, active);
            this.defeated.remove(id);
        });
    }

    private void remove(String id, Active active) {
        if (active == null || !live.remove(id, active)) return;
        ownership.release(id, active.uuid());
        retaliation.remove(id);
        releaseConversation(id, active.entity());
        lastMeleeAt.remove(id);
        nextWanderAt.remove(id);
        NpcNavigation.stop(active.entity(), active.citizensNpc());
        destroyCitizens(active.citizensNpc());
        active.entity().remove();
    }

    void close() {
        closing = true;
        for (var entry : new ArrayList<>(live.entrySet())) remove(entry.getKey(), entry.getValue());
        citizensRegistry = null;
    }

    String status() {
        NpcPopulationPolicy.Budget limits = budget(serviceWorkers());
        return "configured=" + configuredPopulation() + ", active=" + live.size() + "/" + limits.total()
                + ", police=" + activePolice() + "/" + limits.police() + ", other=" + activeOther() + "/" + limits.other()
                + ", ambient=" + activeAmbient() + ", admission cap=" + limits.admissions()
                + ", legacy anchors awaiting review=" + legacyBlocked.size() + ", anchors=" + anchors();
    }

    Set<String> legacyAnchorsAwaitingReview() { return Set.copyOf(legacyBlocked); }

    private record AmbientProfile(String name, String role, String department, boolean tough, boolean merchant) {
    }

    private record Active(UUID uuid, Object citizensNpc, boolean police, boolean ambient, boolean tough, boolean merchant, Location home, Entity entity) {
    }

    private record Retaliation(UUID attacker, long expiresAt) {
    }

    private record ConversationHold(UUID player, UUID session, long expiresAt, boolean hadAi) {
    }
}

