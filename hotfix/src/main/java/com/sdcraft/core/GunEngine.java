/* Reconstructed from the preserved 1.0.3 runtime with CFR 0.152; changes documented in hotfix/README.md. */
package com.sdcraft.core;

import com.sdcraft.core.GtmEquipment;
import com.sdcraft.core.SDCraftCorePlugin;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.UUID;
import net.kyori.adventure.text.Component;
import org.bukkit.FluidCollisionMode;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.World;
import org.bukkit.entity.Entity;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Player;
import org.bukkit.event.Event;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.event.player.PlayerItemHeldEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import net.kyori.adventure.text.serializer.legacy.LegacyComponentSerializer;
import org.bukkit.inventory.EquipmentSlot;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataContainer;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.Plugin;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.util.RayTraceResult;
import org.bukkit.util.Vector;

public final class GunEngine
implements Listener {
    private final JavaPlugin plugin;
    private final NamespacedKey KEY_TYPE;
    private final NamespacedKey KEY_AMMO;
    private final NamespacedKey KEY_AMMO_ITEM;
    private final NamespacedKey KEY_READY;
    private final Map<UUID, Long> lastShot = new HashMap<UUID, Long>();

    public GunEngine(JavaPlugin plugin) {
        this.plugin = plugin;
        this.KEY_TYPE = new NamespacedKey((Plugin)plugin, "gun_type");
        this.KEY_AMMO = new NamespacedKey((Plugin)plugin, "gun_ammo");
        this.KEY_AMMO_ITEM = new NamespacedKey((Plugin)plugin, "ammo_item");
        this.KEY_READY = new NamespacedKey((Plugin)plugin, "gun_ready_at");
    }

    public NamespacedKey getKeyType() {
        return this.KEY_TYPE;
    }

    public NamespacedKey getKeyAmmo() {
        return this.KEY_AMMO;
    }

    public NamespacedKey getKeyAmmoItem() {
        return this.KEY_AMMO_ITEM;
    }

    public ItemStack createGun(GunType type) {
        ItemStack item = new ItemStack(type.material);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName("\u00a7e" + type.displayName);
            meta.setCustomModelData(Integer.valueOf(type.customModelData));
            meta.setItemModel(new NamespacedKey("gtm", "core_" + type.name().toLowerCase(java.util.Locale.ROOT)));
            meta.setMaxStackSize(1);
            meta.setUnbreakable(true);
            meta.getPersistentDataContainer().set(this.KEY_TYPE, PersistentDataType.STRING, type.name());
            meta.getPersistentDataContainer().set(this.KEY_AMMO, PersistentDataType.INTEGER, type.maxAmmo);
            this.updateLore(meta, type, type.maxAmmo);
            item.setItemMeta(meta);
        }
        return item;
    }

    public ItemStack createAmmo(String ammoType, int count) {
        ammoType = canonicalAmmo(ammoType);
        if (count < 1 || count > 64) throw new IllegalArgumentException("Ammo stack must contain 1 to 64 rounds");
        Material mat = switch (ammoType) {
            case "9mm_ammo" -> Material.COPPER_INGOT;
            case "shotgun_shells" -> Material.RED_DYE;
            case "rifle_ammo" -> Material.IRON_NUGGET;
            default -> Material.PRISMARINE_CRYSTALS;
        };
        String name = switch (ammoType) {
            case "9mm_ammo" -> "\u00a7e9mm Ammunition";
            case "shotgun_shells" -> "\u00a7c12-Gauge Shotgun Shells";
            case "rifle_ammo" -> "\u00a765.56mm Rifle Cartridges";
            default -> "\u00a7fAmmunition Box";
        };
        int cmd = switch (ammoType) {
            case "9mm_ammo" -> 201;
            case "shotgun_shells" -> 202;
            case "rifle_ammo" -> 203;
            default -> 200;
        };
        ItemStack item = new ItemStack(mat, Math.max(1, count));
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName(name);
            meta.setCustomModelData(Integer.valueOf(cmd));
            meta.getPersistentDataContainer().set(this.KEY_AMMO_ITEM, PersistentDataType.STRING, ammoType);
            meta.setLore(List.of("\u00a77Standard issue service ammunition", "\u00a78Can be loaded into SD Craft firearms."));
            item.setItemMeta(meta);
        }
        return item;
    }

    /** Keep old saved/command ammunition aliases compatible with the native reload engine. */
    static String canonicalAmmo(String id) {
        if (id == null) throw new IllegalArgumentException("Missing ammunition type");
        return switch (id.toLowerCase(java.util.Locale.ROOT)) {
            case "9mm", "9mm_ammo", "50cal_ammo" -> "9mm_ammo";
            case "shotgun", "shotgun_ammo", "shotgun_shells" -> "shotgun_shells";
            case "rifle", "rifle_ammo", "556_ammo", "762_ammo", "sniper_ammo", "50bmg_ammo" -> "rifle_ammo";
            default -> throw new IllegalArgumentException("Unknown native ammunition type");
        };
    }

    /** Adds the explicit model only to native legacy guns that do not already have a finish. */
    public void refreshVisuals(Player player) {
        if (this.plugin instanceof SDCraftCorePlugin core && !core.isAuthenticated(player)) return;
        for (ItemStack item : player.getInventory().getContents()) {
            if (item == null || !item.hasItemMeta()) continue;
            ItemMeta meta = item.getItemMeta();
            String ammunition = meta.getPersistentDataContainer().get(this.KEY_AMMO_ITEM, PersistentDataType.STRING);
            if (ammunition != null) {
                try {
                    String canonical = canonicalAmmo(ammunition);
                    if (!canonical.equals(ammunition)) {
                        meta.getPersistentDataContainer().set(this.KEY_AMMO_ITEM, PersistentDataType.STRING, canonical);
                        item.setItemMeta(meta);
                    }
                } catch (IllegalArgumentException ignored) {
                    // Do not interpret foreign ammunition as a native round.
                }
            }
            if (meta.hasItemModel()) continue;
            String id = meta.getPersistentDataContainer().get(this.KEY_TYPE, PersistentDataType.STRING);
            if (id == null) continue;
            try {
                GunType type = GunType.valueOf(id);
                if (item.getType() != type.material || item.getAmount() != 1) continue;
                meta.setItemModel(new NamespacedKey("gtm", "core_" + type.name().toLowerCase(java.util.Locale.ROOT)));
                meta.setMaxStackSize(1);
                meta.setUnbreakable(true);
                item.setItemMeta(meta);
            } catch (IllegalArgumentException ignored) {
                // Foreign or malformed metadata is not migrated.
            }
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onHeld(PlayerItemHeldEvent event) {
        refreshVisuals(event.getPlayer());
    }

    @EventHandler
    public void onQuit(PlayerQuitEvent event) {
        this.lastShot.remove(event.getPlayer().getUniqueId());
    }

    private void updateLore(ItemMeta meta, GunType type, int currentAmmo) {
        ArrayList<String> lore = new ArrayList<>();
        lore.add("\u00a77Damage: \u00a7c" + type.damage + " HP" + (String)(type.pellets > 1 ? " \u00d7 " + type.pellets : ""));
        lore.add("\u00a77Effective Range: \u00a7e" + (int)type.range + "m");
        lore.add("\u00a77Ammunition: \u00a7a[" + currentAmmo + " / " + type.maxAmmo + "]");
        lore.add("");
        lore.add("\u00a78Right-Click: Fire | Sneak + Right-Click: Reload");
        meta.setLore(lore);
    }

    @EventHandler(priority=EventPriority.HIGH)
    public void onInteract(PlayerInteractEvent e) {
        GunType type;
        SDCraftCorePlugin core;
        if (e.getHand() != EquipmentSlot.HAND) {
            return;
        }
        Action a = e.getAction();
        if (a != Action.RIGHT_CLICK_AIR && a != Action.RIGHT_CLICK_BLOCK) {
            return;
        }
        Player p = e.getPlayer();
        JavaPlugin javaPlugin = this.plugin;
        if (javaPlugin instanceof SDCraftCorePlugin && !(core = (SDCraftCorePlugin)javaPlugin).isAuthenticated(p)) {
            e.setCancelled(true);
            return;
        }
        ItemStack item = p.getInventory().getItemInMainHand();
        if (item.getType() == Material.AIR) {
            return;
        }
        ItemMeta meta = item.getItemMeta();
        if (meta == null) {
            return;
        }
        PersistentDataContainer pdc = meta.getPersistentDataContainer();
        if (!pdc.has(this.KEY_TYPE, PersistentDataType.STRING)) {
            return;
        }
        if (e.useItemInHand() == Event.Result.DENY) {
            return;
        }
        e.setCancelled(true);
        String typeStr = (String)pdc.get(this.KEY_TYPE, PersistentDataType.STRING);
        try {
            type = GunType.valueOf(typeStr);
        }
        catch (Exception ex) {
            return;
        }
        if (item.getType() != type.material || item.getAmount() != 1) {
            return;
        }
        UUID pid = p.getUniqueId();
        long now = System.currentTimeMillis();
        long ready = (Long)pdc.getOrDefault(this.KEY_READY, PersistentDataType.LONG, 0L);
        if (ready < 0L || ready > now + 120000L) {
            return;
        }
        if (now < ready) {
            this.sendAction(p, "\u00a7c[ RELOADING... Please wait ]");
            return;
        }
        int currentAmmo = (Integer)pdc.getOrDefault(this.KEY_AMMO, PersistentDataType.INTEGER, 0);
        if (currentAmmo < 0 || currentAmmo > type.maxAmmo) {
            return;
        }
        if (p.isSneaking()) {
            if (currentAmmo >= type.maxAmmo) {
                this.sendAction(p, "\u00a7a[ Magazine already full: " + currentAmmo + " / " + type.maxAmmo + " ]");
                return;
            }
            this.startReload(p, item, meta, type);
            return;
        }
        long last = this.lastShot.getOrDefault(pid, 0L);
        if (now - last < type.fireDelayMs) {
            return;
        }
        if (currentAmmo <= 0) {
            this.sendAction(p, "\u00a7c*CLICK* Empty Magazine! Sneak + Right-Click to Reload.");
            p.playSound(p.getLocation(), Sound.BLOCK_DISPENSER_FAIL, 0.7f, 1.8f);
            return;
        }
        this.lastShot.put(pid, now);
        pdc.set(this.KEY_AMMO, PersistentDataType.INTEGER, (--currentAmmo));
        this.updateLore(meta, type, currentAmmo);
        item.setItemMeta(meta);
        Location eye = p.getEyeLocation();
        try {
            p.getWorld().playSound(eye, Sound.valueOf((String)type.soundName), 1.0f, type.pitch);
        }
        catch (Throwable throwable) {
            // empty catch block
        }
        p.getWorld().playSound(eye, Sound.BLOCK_IRON_TRAPDOOR_CLOSE, 0.5f, 2.0f);
        Random rng = new Random();
        LinkedHashMap<LivingEntity, Double> shotDamage = new LinkedHashMap<LivingEntity, Double>();
        for (int i = 0; i < type.pellets; ++i) {
            Vector dir = eye.getDirection().clone();
            if (type.pellets > 1) {
                dir.add(new Vector((rng.nextDouble() - 0.5) * 0.12, (rng.nextDouble() - 0.5) * 0.12, (rng.nextDouble() - 0.5) * 0.12)).normalize();
            }
            this.fireRaycast(p, eye, dir, type, shotDamage);
        }
        for (Map.Entry<LivingEntity, Double> hit : shotDamage.entrySet()) {
            Player other;
            SDCraftCorePlugin core2;
            JavaPlugin javaPlugin2;
            LivingEntity target = (LivingEntity)hit.getKey();
            if (!target.isValid() || target.isDead() || (javaPlugin2 = this.plugin) instanceof SDCraftCorePlugin && (!(core2 = (SDCraftCorePlugin)javaPlugin2).isAuthenticated(p) || target instanceof Player && !NpcCombatAccess.authenticatedPlayerOrAmbient(core2, other = (Player)target) || !core2.properties().mayEnter(p, target.getLocation()))) continue;
            target.damage(((Double)hit.getValue()).doubleValue(), (Entity)p);
        }
        this.sendAction(p, "\u00a76[" + type.name() + "] \u00a7e" + currentAmmo + " / " + type.maxAmmo + " \u00a77Ammo");
    }

    private void fireRaycast(Player shooter, Location origin, Vector dir, GunType type, Map<LivingEntity, Double> shotDamage) {
        Location point;
        World w = origin.getWorld();
        if (w == null) {
            return;
        }
        double range = GtmEquipment.loadedRange(origin, dir, type.range);
        if (range <= 0.0) {
            return;
        }
        RayTraceResult hit = w.rayTrace(origin, dir, range, FluidCollisionMode.NEVER, true, 0.25, entity -> entity instanceof LivingEntity && !entity.getUniqueId().equals(shooter.getUniqueId()));
        double maxDist = hit != null ? origin.distance(hit.getHitPosition().toLocation(w)) : range;
        for (double d = 1.0; d < maxDist; d += 1.0) {
            point = origin.clone().add(dir.clone().multiply(d));
            w.spawnParticle(Particle.CRIT, point, 1, 0.0, 0.0, 0.0, 0.0);
        }
        if (hit != null) {
            Location hitLoc = hit.getHitPosition().toLocation(w);
            Entity hitEntity = hit.getHitEntity();
            if (hitEntity instanceof LivingEntity target) {
                boolean headshot = Math.abs(hitLoc.getY() - target.getEyeLocation().getY()) <= 0.35;
                double finalDmg = type.damage * (headshot ? 1.5 : 1.0);
                shotDamage.merge(target, finalDmg, Double::sum);
                w.spawnParticle(Particle.DAMAGE_INDICATOR, hitLoc, headshot ? 8 : 4, 0.1, 0.1, 0.1, 0.1);
                if (headshot) {
                    shooter.playSound(shooter.getLocation(), Sound.ENTITY_EXPERIENCE_ORB_PICKUP, 0.6f, 1.9f);
                    this.sendAction(shooter, "\u00a7c\u00a7lHEADSHOT! \u00a7e" + target.getName() + " \u00a77(-" + String.format("%.1f", finalDmg) + " HP)");
                } else {
                    this.sendAction(shooter, "\u00a7aHit \u00a7e" + target.getName() + " \u00a77(-" + String.format("%.1f", finalDmg) + " HP)");
                }
            } else if (hit.getHitBlock() != null) {
                w.spawnParticle(Particle.SMOKE, hitLoc, 4, 0.1, 0.1, 0.1, 0.02);
                w.playSound(hitLoc, Sound.BLOCK_STONE_HIT, 0.5f, 1.4f);
            }
        }
    }

    private void startReload(Player p, ItemStack gun, ItemMeta meta, GunType type) {
        int current = (Integer)meta.getPersistentDataContainer().getOrDefault(this.KEY_AMMO, PersistentDataType.INTEGER, 0);
        int needed = type.maxAmmo - current;
        int available = this.countAmmo(p, type.ammoType);
        if (available <= 0) {
            this.sendAction(p, "\u00a7cNo " + type.ammoType + " found in inventory!");
            p.playSound(p.getLocation(), Sound.BLOCK_DISPENSER_FAIL, 0.6f, 1.0f);
            return;
        }
        int toLoad = Math.min(needed, available);
        this.consumeAmmo(p, type.ammoType, toLoad);
        int finalAmmo = current + toLoad;
        meta.getPersistentDataContainer().set(this.KEY_AMMO, PersistentDataType.INTEGER, finalAmmo);
        meta.getPersistentDataContainer().set(this.KEY_READY, PersistentDataType.LONG, (System.currentTimeMillis() + type.reloadTimeMs));
        this.updateLore(meta, type, finalAmmo);
        gun.setItemMeta(meta);
        p.saveData();
        p.playSound(p.getLocation(), Sound.ITEM_ARMOR_EQUIP_CHAIN, 0.8f, 1.2f);
        this.sendAction(p, "\u00a7eReloading " + type.displayName + "... (+" + toLoad + " rounds)");
    }

    private int countAmmo(Player p, String ammoType) {
        int count = 0;
        for (ItemStack is : p.getInventory().getContents()) {
            String at;
            if (is == null || !is.hasItemMeta() || !ammoType.equalsIgnoreCase(at = (String)is.getItemMeta().getPersistentDataContainer().get(this.KEY_AMMO_ITEM, PersistentDataType.STRING))) continue;
            count += is.getAmount();
        }
        return count;
    }

    private void consumeAmmo(Player p, String ammoType, int amount) {
        int left = amount;
        ItemStack[] contents = p.getInventory().getContents();
        for (int i = 0; i < contents.length; ++i) {
            String at;
            ItemStack is = contents[i];
            if (is == null || !is.hasItemMeta() || !ammoType.equalsIgnoreCase(at = (String)is.getItemMeta().getPersistentDataContainer().get(this.KEY_AMMO_ITEM, PersistentDataType.STRING))) continue;
            int stackAmount = is.getAmount();
            if (stackAmount <= left) {
                left -= stackAmount;
                p.getInventory().setItem(i, null);
            } else {
                is.setAmount(stackAmount - left);
                left = 0;
            }
            if (left <= 0) break;
        }
    }

    private void sendAction(Player p, String msg) {
        p.sendActionBar(LegacyComponentSerializer.legacySection().deserialize(msg));
    }

    public static enum GunType {
        PISTOL("ARK Service Pistol", Material.IRON_HOE, 12, 6.0, 35.0, 280L, 1600L, 1, "9mm_ammo", "ENTITY_GENERIC_EXPLODE", 1.8f, 101),
        SHOTGUN("ARK Patrol Shotgun", Material.GOLDEN_HOE, 6, 2.8, 16.0, 850L, 2400L, 6, "shotgun_shells", "ENTITY_GENERIC_EXPLODE", 0.75f, 102),
        SMG("ARK Compact SMG", Material.DIAMOND_HOE, 30, 4.2, 26.0, 110L, 1900L, 1, "9mm_ammo", "ENTITY_FIREWORK_ROCKET_BLAST", 1.6f, 103),
        RIFLE("ARK Urban Rifle", Material.NETHERITE_HOE, 25, 7.5, 48.0, 180L, 2100L, 1, "rifle_ammo", "ENTITY_GENERIC_EXPLODE", 1.35f, 104);

        public final String displayName;
        public final Material material;
        public final int maxAmmo;
        public final double damage;
        public final double range;
        public final long fireDelayMs;
        public final long reloadTimeMs;
        public final int pellets;
        public final String ammoType;
        public final String soundName;
        public final float pitch;
        public final int customModelData;

        private GunType(String name, Material mat, int mag, double dmg, double rng, long delay, long reload, int pellets, String ammo, String snd, float p, int cmd) {
            this.displayName = name;
            this.material = mat;
            this.maxAmmo = mag;
            this.damage = dmg;
            this.range = rng;
            this.fireDelayMs = delay;
            this.reloadTimeMs = reload;
            this.pellets = pellets;
            this.ammoType = ammo;
            this.soundName = snd;
            this.pitch = p;
            this.customModelData = cmd;
        }
    }
}

