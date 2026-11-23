package com.sdcraft.core;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Collection;
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
import org.bukkit.Material;
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
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.util.Vector;

/**
 * Proximity-managed city population.
 *
 * The 20 named service NPCs remain protected at audited anchors. The remaining
 * population is generated as lightweight ambient pedestrians. Only NPCs near a
 * real player are physical, so a 100-person city policy does not mean 100
 * permanently ticking entities on the 3.5 GB host.
 */
final class NpcService implements Listener {
    private static final String[] FIRST_NAMES = {
            "Aarav", "Aditi", "Akash", "Anaya", "Arnav", "Diya", "Farhan", "Isha", "Jai", "Kriti",
            "Manav", "Maya", "Nikhil", "Pooja", "Rahul", "Rhea", "Sahil", "Tara", "Varun", "Zoya"
    };
    private static final String[] LAST_NAMES = {
            "Agarwal", "Bose", "Chandra", "Dutta", "Gill", "Jain", "Khan", "Malik", "Menon", "Mishra",
            "Nair", "Patel", "Rao", "Roy", "Saxena", "Sharma", "Singh", "Soni", "Verma", "Yadav"
    };
    private static final String[] CIVILIAN_ROLES = {
            "Office worker", "Commuter", "College student", "Courier", "Mechanic", "Tourist",
            "Construction worker", "Food vendor", "Street photographer", "Taxi passenger",
            "Warehouse worker", "Shop assistant", "Security guard", "Delivery rider"
    };
    private static final String[] MERCHANT_ROLES = {
            "Street-food merchant", "Clothing merchant", "Electronics merchant", "Book seller",
            "Market trader", "Souvenir merchant"
    };

    private record AmbientProfile(String name, String role, String department, boolean tough, boolean merchant) {}
    private record Active(UUID uuid, Object citizensNpc, boolean police, boolean ambient, boolean tough,
                          boolean merchant, Location home) {}
    private record Retaliation(UUID attacker, long expiresAt) {}

    private final JavaPlugin plugin;
    private final YamlConfiguration identities;
    private final Ledger ledger;
    private final GtaEngine gta;
    private final File anchorsFile;
    private final YamlConfiguration anchors;
    private final Map<String, AmbientProfile> ambient;
    private final Map<String, Active> live = new LinkedHashMap<>();
    private final Map<String, Retaliation> retaliation = new HashMap<>();
    private final Map<String, Long> lastMeleeAt = new HashMap<>();
    private final Map<String, Long> nextWanderAt = new HashMap<>();
    private final Map<String, Long> respawnAfter = new HashMap<>();
    private final Map<UUID, Long> crimeNoticeAfter = new HashMap<>();
    private final Set<String> defeated = new HashSet<>();
    private final Random rng = new Random();
    private long pulseCount;

    NpcService(JavaPlugin plugin, YamlConfiguration identities, Ledger ledger, GtaEngine gta) {
        this.plugin = plugin;
        this.identities = identities;
        this.ledger = ledger;
        this.gta = gta;
        anchorsFile = new File(plugin.getDataFolder(), "anchors.yml");
        anchors = YamlConfiguration.loadConfiguration(anchorsFile);
        int target = plugin.getConfig().getInt("population.target-total", 100);
        int named = namedIds().size();
        int toughPercent = plugin.getConfig().getInt("population.ambient-tough-percent", 30);
        ambient = createAmbientProfiles(generatedAmbientCount(target, named), toughPercent);
        ensureDefaultAnchors(null);
    }

    static int generatedAmbientCount(int targetTotal, int namedCount) {
        if (targetTotal < 0 || namedCount < 0) throw new IllegalArgumentException("Population cannot be negative");
        return Math.min(500, Math.max(0, targetTotal - namedCount));
    }

    static boolean deterministicTough(int ordinal, int percent) {
        if (ordinal < 0 || percent < 0 || percent > 100) throw new IllegalArgumentException("Invalid tough policy");
        return Math.floorMod(ordinal * 37 + 11, 100) < percent;
    }

    private Map<String, AmbientProfile> createAmbientProfiles(int count, int toughPercent) {
        Map<String, AmbientProfile> profiles = new LinkedHashMap<>();
        for (int i = 0; i < count; i++) {
            String id = String.format(Locale.ROOT, "ambient_%03d", i + 1);
            String person = FIRST_NAMES[i % FIRST_NAMES.length] + " "
                    + LAST_NAMES[Math.floorMod(i * 7 + i / FIRST_NAMES.length, LAST_NAMES.length)];
            boolean patrol = i < 2;
            boolean merchant = !patrol && i % 5 == 0;
            boolean tough = patrol || deterministicTough(i, toughPercent);
            String department = patrol ? "police" : merchant ? "retail" : "civilian";
            String role = patrol ? "Patrol officer"
                    : merchant ? MERCHANT_ROLES[(i / 5) % MERCHANT_ROLES.length]
                    : CIVILIAN_ROLES[i % CIVILIAN_ROLES.length];
            profiles.put(id, new AmbientProfile(person, role, department, tough, merchant));
        }
        return profiles;
    }

    private Collection<String> namedIds() {
        ConfigurationSection section = identities.getConfigurationSection("npcs");
        return section == null ? List.of() : new LinkedHashSet<>(section.getKeys(false));
    }

    Collection<String> ids() {
        List<String> result = new ArrayList<>(namedIds());
        result.addAll(ambient.keySet());
        return result;
    }

    String name(String id) {
        AmbientProfile profile = ambient.get(id);
        return profile != null ? profile.name() : identities.getString("npcs." + id + ".name", id);
    }

    String role(String id) {
        AmbientProfile profile = ambient.get(id);
        return profile != null ? profile.role() : identities.getString("npcs." + id + ".role", "Staff");
    }

    String dept(String id) {
        AmbientProfile profile = ambient.get(id);
        return profile != null ? profile.department()
                : identities.getString("npcs." + id + ".department", "civilian");
    }

    String greeting(String id, String lang) {
        AmbientProfile profile = ambient.get(id);
        if (profile != null) {
            if (profile.merchant()) return "Welcome! I trade everyday city goods. Right-click again to browse the city shop.";
            if (profile.tough()) return "Keep it peaceful. I can handle myself, but I am just going about my day.";
            return "Hello! New Blockston is busy today. I am heading through the city.";
        }
        return identities.getString("npcs." + id + ".greeting." + lang, "Hello! Select a service.");
    }

    List<String> actions(String id) {
        AmbientProfile profile = ambient.get(id);
        if (profile != null) return profile.merchant() ? List.of("view_catalog") : List.of();
        return identities.getStringList("npcs." + id + ".actions");
    }

    String skin(String id) {
        return isAmbient(id) ? "ambient-generated" : identities.getString("npcs." + id + ".skin", "skin_" + id + ".png");
    }

    String model(String id) {
        return isAmbient(id) ? (Math.floorMod(id.hashCode(), 2) == 0 ? "classic" : "slim")
                : identities.getString("npcs." + id + ".model", "classic");
    }

    boolean known(String id) { return namedIds().contains(id) || ambient.containsKey(id); }
    boolean isAmbient(String id) { return ambient.containsKey(id); }
    boolean isMerchant(String id) { AmbientProfile p = ambient.get(id); return p != null && p.merchant(); }
    boolean isTough(String id) { AmbientProfile p = ambient.get(id); return p != null && p.tough(); }
    int configuredPopulation() { return ids().size(); }
    int activePolice() { int n = 0; for (Active a : live.values()) if (a.police()) n++; return n; }
    int activeOther() { int n = 0; for (Active a : live.values()) if (!a.police()) n++; return n; }
    int activeAmbient() { int n = 0; for (Active a : live.values()) if (a.ambient()) n++; return n; }
    int anchors() { ConfigurationSection s = anchors.getConfigurationSection("anchors"); return s == null ? 0 : s.getKeys(false).size(); }

    void setAnchor(String id, Location location) throws IOException {
        if (!known(id)) throw new IllegalArgumentException("NPC ID not found");
        String path = "anchors." + id;
        anchors.set(path + ".world", Objects.requireNonNull(location.getWorld()).getName());
        anchors.set(path + ".x", location.getX());
        anchors.set(path + ".y", location.getY());
        anchors.set(path + ".z", location.getZ());
        anchors.set(path + ".yaw", (double) location.getYaw());
        anchors.save(anchorsFile);
    }

    private Map<String, double[]> namedDefaultAnchors() {
        Map<String, double[]> defaults = new LinkedHashMap<>();
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
        String worldName = world != null ? world.getName() : plugin.getConfig().getString("world.name", "world");
        Map<String, double[]> defaults = namedDefaultAnchors();
        boolean modified = false;
        for (Map.Entry<String, double[]> entry : defaults.entrySet()) {
            String path = "anchors." + entry.getKey();
            if (!anchors.contains(path + ".x")) {
                double[] c = entry.getValue();
                anchors.set(path + ".world", worldName);
                anchors.set(path + ".x", c[0]);
                anchors.set(path + ".y", c[1]);
                anchors.set(path + ".z", c[2]);
                anchors.set(path + ".yaw", c[3]);
                modified = true;
            }
        }
        if (world != null) modified |= ensureAmbientAnchors(world, defaults);
        if (modified) saveAnchors();
    }

    private boolean ensureAmbientAnchors(World world, Map<String, double[]> defaults) {
        List<double[]> bases = new ArrayList<>(defaults.values());
        boolean modified = false;
        int i = 0;
        for (String id : ambient.keySet()) {
            String path = "anchors." + id;
            if (anchors.contains(path + ".x")) { i++; continue; }
            double[] base = bases.get(i % bases.size());
            int ring = i / bases.size();
            double angle = Math.toRadians((i % bases.size()) * 47.0 + ring * 90.0);
            double radius = 4.0 + ring * 2.0;
            Location desired = new Location(world, base[0] + Math.cos(angle) * radius, base[1],
                    base[2] + Math.sin(angle) * radius, (float) Math.toDegrees(angle + Math.PI), 0.0f);
            Location safe = findWalkable(desired, 8);
            if (safe == null) safe = new Location(world, base[0], base[1], base[2]);
            anchors.set(path + ".world", world.getName());
            anchors.set(path + ".x", safe.getX());
            anchors.set(path + ".y", safe.getY());
            anchors.set(path + ".z", safe.getZ());
            anchors.set(path + ".yaw", (double) safe.getYaw());
            modified = true;
            i++;
        }
        return modified;
    }

    private void saveAnchors() {
        try { anchors.save(anchorsFile); }
        catch (IOException ex) { plugin.getLogger().warning("Failed to save NPC anchors: " + ex.getMessage()); }
    }

    private Location location(String id) {
        String path = "anchors." + id;
        World world = Bukkit.getWorld(anchors.getString(path + ".world", ""));
        if (world == null || !anchors.contains(path + ".x")) return null;
        return new Location(world, anchors.getDouble(path + ".x"), anchors.getDouble(path + ".y"),
                anchors.getDouble(path + ".z"), (float) anchors.getDouble(path + ".yaw"), 0.0f);
    }

    private Location findWalkable(Location desired, int horizontalSearch) {
        World world = desired.getWorld();
        if (world == null) return null;
        int baseX = desired.getBlockX();
        int baseY = desired.getBlockY();
        int baseZ = desired.getBlockZ();
        for (int radius = 0; radius <= horizontalSearch; radius++) {
            for (int dx = -radius; dx <= radius; dx++) {
                for (int dz = -radius; dz <= radius; dz++) {
                    if (radius > 0 && Math.abs(dx) != radius && Math.abs(dz) != radius) continue;
                    for (int dy = 3; dy >= -4; dy--) {
                        int y = baseY + dy;
                        if (y <= world.getMinHeight() || y >= world.getMaxHeight() - 2) continue;
                        Block floor = world.getBlockAt(baseX + dx, y - 1, baseZ + dz);
                        Block feet = world.getBlockAt(baseX + dx, y, baseZ + dz);
                        Block head = world.getBlockAt(baseX + dx, y + 1, baseZ + dz);
                        if (floor.getType().isSolid() && feet.isPassable() && head.isPassable()
                                && !feet.isLiquid() && !head.isLiquid()) {
                            return new Location(world, baseX + dx + 0.5, y, baseZ + dz + 0.5,
                                    desired.getYaw(), 0.0f);
                        }
                    }
                }
            }
        }
        return null;
    }

    /** Reconciles the physical population every ten seconds. */
    void tick() {
        World defaultWorld = Bukkit.getWorld(plugin.getConfig().getString("world.name", "world"));
        if (defaultWorld == null && !Bukkit.getWorlds().isEmpty()) defaultWorld = Bukkit.getWorlds().get(0);
        if (defaultWorld != null) ensureDefaultAnchors(defaultWorld);

        int policeLimit = plugin.getConfig().getInt("population.max-physical-police", 6);
        int otherLimit = plugin.getConfig().getInt("population.max-physical-nonpolice", 94);
        int totalLimit = plugin.getConfig().getInt("population.max-physical-total", 100);
        double activation = plugin.getConfig().getDouble("population.activation-blocks", 56.0);
        double deactivation = plugin.getConfig().getDouble("population.deactivation-blocks", 80.0);
        long now = System.currentTimeMillis();

        for (String id : ids()) {
            Location anchor = location(id);
            if (anchor == null) continue;
            Active active = live.get(id);
            boolean police = dept(id).equalsIgnoreCase("police");
            double nearest = Double.POSITIVE_INFINITY;
            for (Player player : Bukkit.getOnlinePlayers()) {
                if (identify(player) != null || !player.getWorld().equals(anchor.getWorld())) continue;
                nearest = Math.min(nearest, player.getLocation().distance(anchor));
            }
            boolean should = PolicyEngine.shouldBeActive(active != null, nearest, activation, deactivation);
            if (!should && active != null) {
                remove(id, active);
                continue;
            }
            if (should && active == null) {
                if (respawnAfter.getOrDefault(id, 0L) > now || live.size() >= totalLimit) continue;
                if (police ? activePolice() >= policeLimit : activeOther() >= otherLimit) continue;
                spawn(id, anchor, police);
            }
        }
    }

    /** Lightweight half-second movement and retaliation pulse. */
    void pulse() {
        pulseCount++;
        long now = System.currentTimeMillis();
        int wanderRadius = plugin.getConfig().getInt("population.ambient-wander-radius-blocks", 12);
        double meleeDamage = plugin.getConfig().getDouble("population.ambient-melee-damage", 2.0);
        long retaliationMs = plugin.getConfig().getLong("population.ambient-retaliation-seconds", 20L) * 1000L;
        for (Map.Entry<String, Active> entry : new ArrayList<>(live.entrySet())) {
            String id = entry.getKey();
            Active active = entry.getValue();
            if (!active.ambient()) continue;
            Entity entity = Bukkit.getEntity(active.uuid());
            if (entity == null || !entity.isValid()) continue;

            Retaliation fight = retaliation.get(id);
            if (fight != null && active.tough()) {
                Player attacker = Bukkit.getPlayer(fight.attacker());
                if (attacker == null || !attacker.isOnline() || now > fight.expiresAt()
                        || !attacker.getWorld().equals(entity.getWorld())
                        || attacker.getLocation().distanceSquared(entity.getLocation()) > 24.0 * 24.0) {
                    retaliation.remove(id);
                } else {
                    navigate(active, attacker.getLocation());
                    if (attacker.getLocation().distanceSquared(entity.getLocation()) <= 2.8 * 2.8
                            && now - lastMeleeAt.getOrDefault(id, 0L) >= 1100L) {
                        lastMeleeAt.put(id, now);
                        attacker.damage(meleeDamage);
                        Vector knockback = attacker.getLocation().toVector().subtract(entity.getLocation().toVector());
                        if (knockback.lengthSquared() > 0.01) attacker.setVelocity(knockback.normalize().multiply(0.35).setY(0.18));
                    }
                    continue;
                }
            }

            if (pulseCount % 8 != 0 || now < nextWanderAt.getOrDefault(id, 0L)) continue;
            if (entity.getLocation().distanceSquared(active.home()) > (wanderRadius * 2.0) * (wanderRadius * 2.0)) {
                navigate(active, active.home());
            } else if (rng.nextDouble() < 0.55) {
                Location desired = active.home().clone().add(rng.nextInt(wanderRadius * 2 + 1) - wanderRadius, 0,
                        rng.nextInt(wanderRadius * 2 + 1) - wanderRadius);
                Location target = findWalkable(desired, 4);
                if (target != null) navigate(active, target);
            }
            nextWanderAt.put(id, now + 3500L + rng.nextInt(4500));
            if (fight != null && now > fight.expiresAt() + retaliationMs) retaliation.remove(id);
        }
    }

    private void navigate(Active active, Location target) {
        if (active.citizensNpc() == null) return; // Villager fallback has its own AI wandering.
        try {
            Object navigator = active.citizensNpc().getClass().getMethod("getNavigator").invoke(active.citizensNpc());
            navigator.getClass().getMethod("setTarget", Location.class).invoke(navigator, target);
        } catch (ReflectiveOperationException ignored) {
            // Citizens API differences should not disable the rest of the population.
        }
    }

    private void spawn(String id, Location where, boolean police) {
        if (where.getWorld() == null) return;
        boolean ambientNpc = isAmbient(id);
        String tag = switch (dept(id).toLowerCase(Locale.ROOT)) {
            case "police" -> "\u00A7c[SDPD] ";
            case "medical" -> "\u00A7a[Hospital] ";
            case "fire" -> "\u00A74[Fire] ";
            case "bank" -> "\u00A7e[Bank] ";
            case "transport" -> "\u00A76[Transit] ";
            case "civic" -> "\u00A7b[City Info] ";
            case "retail" -> "\u00A7d[Shop] ";
            default -> "\u00A77[Citizen] ";
        };
        String text = tag + "\u00A7f" + name(id);
        World world = where.getWorld();
        if (!world.isChunkLoaded(where.getBlockX() >> 4, where.getBlockZ() >> 4))
            world.loadChunk(where.getBlockX() >> 4, where.getBlockZ() >> 4);

        Object citizensNpc = null;
        Entity entity = null;
        if (Bukkit.getPluginManager().isPluginEnabled("Citizens")) {
            try {
                Class<?> api = Class.forName("net.citizensnpcs.api.CitizensAPI");
                Object registry = api.getMethod("getNPCRegistry").invoke(null);
                Method create = registry.getClass().getMethod("createNPC", EntityType.class, String.class);
                citizensNpc = create.invoke(registry, EntityType.PLAYER, text);
                try { citizensNpc.getClass().getMethod("setProtected", boolean.class).invoke(citizensNpc, !ambientNpc); }
                catch (ReflectiveOperationException ignored) {}
                if (!ambientNpc) {
                    try {
                        Class<?> traitClass = Class.forName("net.citizensnpcs.trait.SkinTrait");
                        Object trait = citizensNpc.getClass().getMethod("getOrAddTrait", Class.class)
                                .invoke(citizensNpc, traitClass);
                        trait.getClass().getMethod("setSkinName", String.class).invoke(trait, name(id));
                    } catch (Throwable ignored) {}
                }
                citizensNpc.getClass().getMethod("spawn", Location.class).invoke(citizensNpc, where);
                Object result = citizensNpc.getClass().getMethod("getEntity").invoke(citizensNpc);
                if (result instanceof Entity spawned) entity = spawned;
            } catch (Exception ex) {
                plugin.getLogger().warning("Citizens NPC spawn failed for " + id + "; using villager fallback: " + ex.getMessage());
                citizensNpc = null;
            }
        }
        if (entity == null) {
            if (citizensNpc != null) {
                try { citizensNpc.getClass().getMethod("destroy").invoke(citizensNpc); }
                catch (Exception ignored) {}
                citizensNpc = null;
            }
            try {
                Villager villager = world.spawn(where, Villager.class);
                villager.setCustomName(text);
                villager.setCustomNameVisible(true);
                villager.setAI(ambientNpc);
                villager.setInvulnerable(!ambientNpc);
                villager.setSilent(!ambientNpc);
                villager.setRemoveWhenFarAway(false);
                entity = villager;
            } catch (Exception ex) {
                plugin.getLogger().warning("NPC fallback failed " + id + ": " + ex.getMessage());
                return;
            }
        }
        entity.setCustomName(text);
        entity.setCustomNameVisible(true);
        live.put(id, new Active(entity.getUniqueId(), citizensNpc, police, ambientNpc, isTough(id),
                isMerchant(id), where.clone()));
        nextWanderAt.put(id, System.currentTimeMillis() + 1500L + rng.nextInt(4500));
    }

    String identify(Entity entity) {
        for (Map.Entry<String, Active> entry : live.entrySet())
            if (entry.getValue().uuid().equals(entity.getUniqueId())) return entry.getKey();
        return null;
    }

    private Player attackingPlayer(Entity source) {
        if (source instanceof Player player && identify(player) == null) return player;
        if (source instanceof Projectile projectile && projectile.getShooter() instanceof Player player
                && identify(player) == null) return player;
        return null;
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void onNpcDamage(EntityDamageByEntityEvent event) {
        String id = identify(event.getEntity());
        if (id == null) return;
        if (!isAmbient(id)) {
            event.setCancelled(true);
            Player attacker = attackingPlayer(event.getDamager());
            if (attacker != null) attacker.sendMessage("\u00A7c[SD Craft] Service NPCs are protected.");
            return;
        }
        if (event.isCancelled() || defeated.contains(id)) return;
        Player attacker = attackingPlayer(event.getDamager());
        if (attacker == null) {
            event.setCancelled(true); // Keep ambient population from dying to fire/falls/mobs.
            return;
        }
        Active active = live.get(id);
        if (active == null || !(event.getEntity() instanceof LivingEntity victim)) return;
        long now = System.currentTimeMillis();
        if (now >= crimeNoticeAfter.getOrDefault(attacker.getUniqueId(), 0L)) {
            gta.recordCrime(attacker, 1, "Assault on pedestrian " + name(id));
            crimeNoticeAfter.put(attacker.getUniqueId(), now + 10_000L);
        }
        if (event.getFinalDamage() >= victim.getHealth()) {
            event.setCancelled(true);
            defeat(id, active, victim, attacker);
            return;
        }
        long retaliationSeconds = plugin.getConfig().getLong("population.ambient-retaliation-seconds", 20L);
        retaliation.put(id, new Retaliation(attacker.getUniqueId(), now + retaliationSeconds * 1000L));
        if (!active.tough()) {
            Vector away = victim.getLocation().toVector().subtract(attacker.getLocation().toVector());
            if (away.lengthSquared() > 0.01) {
                Location flee = active.home().clone().add(away.normalize().multiply(
                        plugin.getConfig().getInt("population.ambient-wander-radius-blocks", 12)));
                Location safe = findWalkable(flee, 5);
                if (safe != null) navigate(active, safe);
            }
        } else {
            attacker.sendMessage("\u00A7c[Street] " + name(id) + " fights back!");
        }
    }

    private void defeat(String id, Active active, LivingEntity victim, Player attacker) {
        if (!defeated.add(id)) return;
        victim.setInvulnerable(true);
        long min = Math.max(1L, plugin.getConfig().getLong("population.ambient-loot-min-cents", 300L));
        long max = Math.max(min, plugin.getConfig().getLong("population.ambient-loot-max-cents", 1500L));
        long cents = min + rng.nextLong(max - min + 1L);
        if (active.merchant()) cents += plugin.getConfig().getLong("population.ambient-merchant-bonus-cents", 500L);
        if (plugin.getConfig().getBoolean("population.ambient-loot-enabled", true) && ledger.exists(attacker.getUniqueId())) {
            try {
                ledger.creditWallet(attacker.getUniqueId(), cents, "ambient pedestrian loot: " + id);
                attacker.sendMessage("\u00A7a[Street Loot] You picked up " + PolicyEngine.money(cents) + ".");
            } catch (IOException ex) {
                plugin.getLogger().warning("Failed to credit ambient loot: " + ex.getMessage());
            }
        }
        if (rng.nextDouble() < 0.55) {
            Material material = rng.nextBoolean() ? Material.BREAD : Material.COOKED_BEEF;
            victim.getWorld().dropItemNaturally(victim.getLocation(), new ItemStack(material, 1 + rng.nextInt(2)));
        } else if (rng.nextDouble() < 0.25) {
            victim.getWorld().dropItemNaturally(victim.getLocation(), new ItemStack(Material.IRON_NUGGET, 1 + rng.nextInt(3)));
        }
        gta.recordCrime(attacker, active.merchant() ? 2 : 1, "Street robbery of " + name(id));
        long cooldown = plugin.getConfig().getLong("population.ambient-respawn-seconds", 180L) * 1000L;
        respawnAfter.put(id, System.currentTimeMillis() + cooldown);
        Bukkit.getScheduler().runTask(plugin, () -> {
            remove(id, active);
            defeated.remove(id);
        });
    }

    private void remove(String id, Active active) {
        if (!live.remove(id, active)) return;
        retaliation.remove(id);
        lastMeleeAt.remove(id);
        nextWanderAt.remove(id);
        if (active.citizensNpc() != null) {
            try { active.citizensNpc().getClass().getMethod("destroy").invoke(active.citizensNpc()); }
            catch (Exception ignored) {}
        }
        Entity entity = Bukkit.getEntity(active.uuid());
        if (entity != null) entity.remove();
    }

    void close() {
        for (String id : new ArrayList<>(live.keySet())) remove(id, live.get(id));
    }

    String status() {
        int policeLimit = plugin.getConfig().getInt("population.max-physical-police", 6);
        int otherLimit = plugin.getConfig().getInt("population.max-physical-nonpolice", 94);
        return "configured=" + configuredPopulation() + ", active police=" + activePolice() + "/" + policeLimit
                + ", other=" + activeOther() + "/" + otherLimit + ", ambient=" + activeAmbient()
                + ", confirmed NPC anchors=" + anchors();
    }
}
