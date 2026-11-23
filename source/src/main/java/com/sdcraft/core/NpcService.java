package com.sdcraft.core;

import java.io.*;
import java.lang.reflect.Method;
import java.util.*;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Entity;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.Player;
import org.bukkit.entity.Villager;
import org.bukkit.plugin.java.JavaPlugin;

/** Physical NPCs spawn only at operator-verified anchors. Citizens optional, villager fallback. */
final class NpcService {
    private final JavaPlugin plugin;
    private final YamlConfiguration identities;
    private final File anchorsFile;
    private final YamlConfiguration anchors;
    private final Map<String, Active> live = new HashMap<>();
    private final Random rng=new Random();
    private record Active(UUID uuid, Object citizensNpc, boolean police, Location location){}
    NpcService(JavaPlugin plugin, YamlConfiguration identities) {
        this.plugin=plugin; this.identities=identities;
        anchorsFile=new File(plugin.getDataFolder(),"anchors.yml");
        anchors=YamlConfiguration.loadConfiguration(anchorsFile);
        ensureDefaultAnchors(null);
    }

    private void ensureDefaultAnchors(World w) {
        String wName = (w != null) ? w.getName() : plugin.getConfig().getString("world.name", "world");
        Map<String, double[]> defaults = new LinkedHashMap<>();
        // Civic Plaza & Spawn (10, 71, 15)
        defaults.put("nisha_bhat", new double[]{8.0, 71.0, 4.0, 180.0});
        defaults.put("sameer_qureshi", new double[]{16.0, 71.0, 4.0, 90.0});
        defaults.put("rehan_khan", new double[]{6.0, 71.0, 4.0, 270.0});
        defaults.put("anjali_rao", new double[]{26.0, 68.0, 64.0, 0.0});

        // Police Headquarters (120, 68, -45)
        defaults.put("mira_rao", new double[]{120.0, 66.0, -44.0, 180.0});
        defaults.put("arjun_shah", new double[]{114.0, 67.0, -46.0, 90.0});
        defaults.put("kabir_sethi", new double[]{100.0, 68.0, -28.0, 0.0});
        defaults.put("riya_kapoor", new double[]{122.0, 66.0, -48.0, 0.0});

        // City General Hospital (-85, 68, 140)
        defaults.put("asha_mehta", new double[]{-62.0, 65.0, 142.0, 180.0});
        defaults.put("rohan_iyer", new double[]{-62.0, 65.0, 138.0, 90.0});
        defaults.put("sana_ali", new double[]{-62.0, 65.0, 140.0, 270.0});
        defaults.put("karan_joshi", new double[]{-62.0, 65.0, 146.0, 0.0});

        // Central Bank & ATMs (60, 69, -110)
        defaults.put("priya_desai", new double[]{60.0, 68.0, -116.0, 180.0});
        defaults.put("aditya_verma", new double[]{62.0, 69.0, -116.0, 270.0});

        // Central Fire Station (190, 68, 80)
        defaults.put("kavya_nair", new double[]{192.0, 70.0, 82.0, 180.0});
        defaults.put("dev_malhotra", new double[]{182.0, 69.0, 78.0, 90.0});

        // Motor Mile Dealership & Retail (-150, 68, -80)
        defaults.put("imran_sheikh", new double[]{-150.0, 69.0, -80.0, 180.0});
        defaults.put("neha_patel", new double[]{-146.0, 67.0, -82.0, 270.0});

        // East Boulevard Workshop / Gas Station (-220, 68, 60)
        defaults.put("vikram_singh", new double[]{-206.0, 70.0, 62.0, 180.0});
        defaults.put("meera_kulkarni", new double[]{-206.0, 70.0, 58.0, 90.0});

        boolean modified = false;
        for (var entry : defaults.entrySet()) {
            String id = entry.getKey();
            String p = "anchors." + id;
            if (!anchors.contains(p + ".x")) {
                double[] c = entry.getValue();
                anchors.set(p + ".world", wName);
                anchors.set(p + ".x", c[0]);
                anchors.set(p + ".y", c[1]);
                anchors.set(p + ".z", c[2]);
                anchors.set(p + ".yaw", c[3]);
                modified = true;
            }
        }
        if (modified) {
            try {
                anchors.save(anchorsFile);
            } catch (IOException ex) {
                plugin.getLogger().warning("Failed to save default anchors: " + ex.getMessage());
            }
        }
    }
    Collection<String> ids() {
        ConfigurationSection s=identities.getConfigurationSection("npcs");
        return s==null?List.of():s.getKeys(false);
    }
    String name(String id) {return identities.getString("npcs."+id+".name", id);}
    String role(String id) {return identities.getString("npcs."+id+".role","Staff");}
    String dept(String id) {return identities.getString("npcs."+id+".department","civilian");}
    String greeting(String id, String lang) {return identities.getString("npcs."+id+".greeting."+lang,"Hello! Select a service.");}
    List<String> actions(String id) {return identities.getStringList("npcs."+id+".actions");}
    String skin(String id) {return identities.getString("npcs."+id+".skin", "skin_"+id+".png");}
    String model(String id) {return identities.getString("npcs."+id+".model", "classic");}
    boolean known(String id) {return ids().contains(id);}
    int activePolice() {int n=0;for(Active a:live.values()) if(a.police)n++;return n;}
    int activeOther() {int n=0;for(Active a:live.values()) if(!a.police)n++;return n;}
    int anchors() {ConfigurationSection s=anchors.getConfigurationSection("anchors");return s==null?0:s.getKeys(false).size();}
    void setAnchor(String id, Location l) throws IOException {
        if(!known(id))throw new IllegalArgumentException("NPC ID not found");
        String p="anchors."+id;
        anchors.set(p+".world",l.getWorld().getName());
        anchors.set(p+".x",l.getX());anchors.set(p+".y",l.getY());anchors.set(p+".z",l.getZ());
        anchors.set(p+".yaw",(double)l.getYaw());
        anchors.save(anchorsFile);
    }
    private Location location(String id) {
        String p="anchors."+id;
        World w=Bukkit.getWorld(anchors.getString(p+".world",""));
        if(w==null||!anchors.contains(p+".x"))return null;
        return new Location(w,anchors.getDouble(p+".x"),anchors.getDouble(p+".y"),anchors.getDouble(p+".z"),
           (float)anchors.getDouble(p+".yaw"),0);
    }
    /** Controlled active population: spawn <=64 blocks; keep until >96 blocks. */
    public void tick() {
        World defaultWorld = Bukkit.getWorld(plugin.getConfig().getString("world.name", "world"));
        if (defaultWorld == null && !Bukkit.getWorlds().isEmpty()) defaultWorld = Bukkit.getWorlds().get(0);
        if (defaultWorld != null) ensureDefaultAnchors(defaultWorld);

        for (String id : ids()) {
            Location anchor = location(id);
            if (anchor == null) continue;
            Active a = live.get(id);
            boolean isPolice = dept(id).equalsIgnoreCase("police");
            double min = Double.POSITIVE_INFINITY;
            for (Player p : Bukkit.getOnlinePlayers()) {
                if (p.getWorld().equals(anchor.getWorld()))
                    min = Math.min(min, p.getLocation().distance(anchor));
            }
            boolean should = PolicyEngine.shouldBeActive(a != null, min);
            if (!should && a != null) {
                remove(id, a);
                continue;
            }
            if (should && a == null) {
                int lim = isPolice
                        ? Math.min(plugin.getConfig().getInt("population.max-physical-police", 6),
                                plugin.getConfig().getInt("population.idle-police-patrol", 2))
                        : plugin.getConfig().getInt("population.max-physical-nonpolice", 20);
                if ((isPolice ? activePolice() : activeOther()) >= lim) continue;
                spawn(id, anchor, isPolice);
            }
        }
    }

    private void spawn(String id, Location where, boolean police) {
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
        String text = tag + "§f" + name(id);

        if (where.getWorld() != null && !where.getWorld().isChunkLoaded(where.getBlockX() >> 4, where.getBlockZ() >> 4)) {
            where.getWorld().loadChunk(where.getBlockX() >> 4, where.getBlockZ() >> 4);
        }

        Object cit = null;
        Entity entity = null;
        if (Bukkit.getPluginManager().isPluginEnabled("Citizens")) {
            try {
                Class<?> api = Class.forName("net.citizensnpcs.api.CitizensAPI");
                Object registry = api.getMethod("getNPCRegistry").invoke(null);
                Method create = registry.getClass().getMethod("createNPC", EntityType.class, String.class);
                cit = create.invoke(registry, EntityType.PLAYER, text);
                try {
                    Class<?> traitClass = Class.forName("net.citizensnpcs.trait.SkinTrait");
                    Object trait = cit.getClass().getMethod("getOrAddTrait", Class.class).invoke(cit, traitClass);
                    trait.getClass().getMethod("setSkinName", String.class).invoke(trait, name(id));
                } catch (Throwable ignore) {}
                cit.getClass().getMethod("spawn", Location.class).invoke(cit, where);
                Object result = cit.getClass().getMethod("getEntity").invoke(cit);
                if (result instanceof Entity) entity = (Entity) result;
            } catch (Exception ex) {
                plugin.getLogger().warning("Citizens NPC spawn failed for " + id + "; using villager fallback: " + ex.getMessage());
                cit = null;
            }
        }
        if (entity == null) {
            if (cit != null) {
                try { cit.getClass().getMethod("destroy").invoke(cit); } catch (Exception ignore) {}
                cit = null;
            }
            try {
                Villager v = where.getWorld().spawn(where, Villager.class);
                v.setCustomName(text);
                v.setCustomNameVisible(true);
                v.setAI(false);
                v.setInvulnerable(true);
                v.setSilent(true);
                entity = v;
            } catch (Exception ex) {
                plugin.getLogger().warning("NPC fallback failed " + id + ": " + ex.getMessage());
                return;
            }
        }
        if (entity != null) {
            entity.setCustomName(text);
            entity.setCustomNameVisible(true);
        }
        live.put(id, new Active(entity.getUniqueId(), cit, police, where.clone()));
    }
    String identify(Entity e){for(var ent:live.entrySet())if(ent.getValue().uuid.equals(e.getUniqueId()))return ent.getKey();return null;}
    private void remove(String id,Active a){
        live.remove(id);
        if(a.citizensNpc!=null){
            try {a.citizensNpc.getClass().getMethod("destroy").invoke(a.citizensNpc);}catch(Exception ignore){}
        }
        Entity e=Bukkit.getEntity(a.uuid);
        if(e!=null)e.remove();
    }
    void close(){for(String id:new ArrayList<>(live.keySet()))remove(id,live.get(id));}
    String status(){return "active police="+activePolice()+"/6, other="+activeOther()+"/20, confirmed NPC anchors="+anchors();}
}
