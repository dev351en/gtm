package com.sdcraft.core;

import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.Damageable;
import org.bukkit.entity.Entity;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.inventory.EquipmentSlot;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataContainer;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.util.RayTraceResult;
import org.bukkit.util.Vector;

/**
 * Lightweight, high-precision native firearms engine for SD Craft.
 * Raycast ballistic hitscan with particle trails, headshots, recoil, and reload mechanics.
 * Fits within the 3.5 GB RAM envelope with 0 external dependencies.
 */
public final class GunEngine implements Listener {

    public enum GunType {
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

        GunType(String name, Material mat, int mag, double dmg, double rng, long delay, long reload, int pellets, String ammo, String snd, float p, int cmd) {
            this.displayName = name; this.material = mat; this.maxAmmo = mag; this.damage = dmg;
            this.range = rng; this.fireDelayMs = delay; this.reloadTimeMs = reload; this.pellets = pellets;
            this.ammoType = ammo; this.soundName = snd; this.pitch = p; this.customModelData = cmd;
        }
    }

    private final JavaPlugin plugin;
    private final NamespacedKey KEY_TYPE;
    private final NamespacedKey KEY_AMMO;
    private final NamespacedKey KEY_AMMO_ITEM;

    private final Map<UUID, Long> lastShot = new HashMap<>();
    private final Map<UUID, Long> reloadUntil = new HashMap<>();

    public GunEngine(JavaPlugin plugin) {
        this.plugin = plugin;
        this.KEY_TYPE = new NamespacedKey(plugin, "gun_type");
        this.KEY_AMMO = new NamespacedKey(plugin, "gun_ammo");
        this.KEY_AMMO_ITEM = new NamespacedKey(plugin, "ammo_item");
    }

    public NamespacedKey getKeyType() {
        return KEY_TYPE;
    }

    public NamespacedKey getKeyAmmo() {
        return KEY_AMMO;
    }

    public NamespacedKey getKeyAmmoItem() {
        return KEY_AMMO_ITEM;
    }

    public ItemStack createGun(GunType type) {
        ItemStack item = new ItemStack(type.material);
        ItemMeta meta = item.getItemMeta();
        if (meta != null) {
            meta.setDisplayName("§e" + type.displayName);
            meta.setCustomModelData(type.customModelData);
            meta.getPersistentDataContainer().set(KEY_TYPE, PersistentDataType.STRING, type.name());
            meta.getPersistentDataContainer().set(KEY_AMMO, PersistentDataType.INTEGER, type.maxAmmo);
            updateLore(meta, type, type.maxAmmo);
            item.setItemMeta(meta);
        }
        return item;
    }

    public ItemStack createAmmo(String ammoType, int count) {
        Material mat = switch (ammoType) {
            case "9mm_ammo" -> Material.COPPER_INGOT;
            case "shotgun_shells" -> Material.RED_DYE;
            case "rifle_ammo" -> Material.IRON_NUGGET;
            default -> Material.PRISMARINE_CRYSTALS;
        };
        String name = switch (ammoType) {
            case "9mm_ammo" -> "§e9mm Ammunition";
            case "shotgun_shells" -> "§c12-Gauge Shotgun Shells";
            case "rifle_ammo" -> "§65.56mm Rifle Cartridges";
            default -> "§fAmmunition Box";
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
            meta.setCustomModelData(cmd);
            meta.getPersistentDataContainer().set(KEY_AMMO_ITEM, PersistentDataType.STRING, ammoType);
            meta.setLore(List.of("§7Standard issue service ammunition", "§8Can be loaded into SD Craft firearms."));
            item.setItemMeta(meta);
        }
        return item;
    }

    private void updateLore(ItemMeta meta, GunType type, int currentAmmo) {
        List<String> lore = new ArrayList<>();
        lore.add("§7Damage: §c" + type.damage + " HP" + (type.pellets > 1 ? " × " + type.pellets : ""));
        lore.add("§7Effective Range: §e" + (int)type.range + "m");
        lore.add("§7Ammunition: §a[" + currentAmmo + " / " + type.maxAmmo + "]");
        lore.add("");
        lore.add("§8Right-Click: Fire | Sneak + Right-Click: Reload");
        meta.setLore(lore);
    }

    @EventHandler(priority = EventPriority.HIGH)
    public void onInteract(PlayerInteractEvent e) {
        if (e.getHand() != EquipmentSlot.HAND) return;
        Action a = e.getAction();
        if (a != Action.RIGHT_CLICK_AIR && a != Action.RIGHT_CLICK_BLOCK) return;

        Player p = e.getPlayer();
        if (plugin instanceof SDCraftCorePlugin core && !core.isAuthenticated(p)) {
            e.setCancelled(true);
            return;
        }
        ItemStack item = p.getInventory().getItemInMainHand();
        if (item.getType() == Material.AIR) return;

        ItemMeta meta = item.getItemMeta();
        if (meta == null) return;

        PersistentDataContainer pdc = meta.getPersistentDataContainer();
        if (!pdc.has(KEY_TYPE, PersistentDataType.STRING)) return;

        e.setCancelled(true); // Prevent block interaction while holding gun

        String typeStr = pdc.get(KEY_TYPE, PersistentDataType.STRING);
        GunType type;
        try {
            type = GunType.valueOf(typeStr);
        } catch (Exception ex) {
            return;
        }

        UUID pid = p.getUniqueId();
        long now = System.currentTimeMillis();

        // Check if currently reloading
        if (reloadUntil.containsKey(pid)) {
            if (now < reloadUntil.get(pid)) {
                sendAction(p, "§c[ RELOADING... Please wait ]");
                return;
            } else {
                reloadUntil.remove(pid);
            }
        }

        int currentAmmo = pdc.getOrDefault(KEY_AMMO, PersistentDataType.INTEGER, 0);

        // Sneak + Right Click = Manual Reload
        if (p.isSneaking()) {
            if (currentAmmo >= type.maxAmmo) {
                sendAction(p, "§a[ Magazine already full: " + currentAmmo + " / " + type.maxAmmo + " ]");
                return;
            }
            startReload(p, item, meta, type);
            return;
        }

        // Fire Rate Check
        long last = lastShot.getOrDefault(pid, 0L);
        if (now - last < type.fireDelayMs) {
            return;
        }

        // Check ammo
        if (currentAmmo <= 0) {
            sendAction(p, "§c*CLICK* Empty Magazine! Sneak + Right-Click to Reload.");
            p.playSound(p.getLocation(), Sound.BLOCK_DISPENSER_FAIL, 0.7f, 1.8f);
            return;
        }

        // FIRE WEAPON
        lastShot.put(pid, now);
        currentAmmo--;
        pdc.set(KEY_AMMO, PersistentDataType.INTEGER, currentAmmo);
        updateLore(meta, type, currentAmmo);
        item.setItemMeta(meta);

        // Sound & recoil
        Location eye = p.getEyeLocation();
        try {
            p.getWorld().playSound(eye, Sound.valueOf(type.soundName), 1.0f, type.pitch);
        } catch (Throwable ignored) {}
        p.getWorld().playSound(eye, Sound.BLOCK_IRON_TRAPDOOR_CLOSE, 0.5f, 2.0f);

        // Fire bullets/pellets
        Random rng = new Random();
        for (int i = 0; i < type.pellets; i++) {
            Vector dir = eye.getDirection().clone();
            if (type.pellets > 1) {
                // Pellet spread for shotgun
                dir.add(new Vector((rng.nextDouble() - 0.5) * 0.12, (rng.nextDouble() - 0.5) * 0.12, (rng.nextDouble() - 0.5) * 0.12)).normalize();
            }
            fireRaycast(p, eye, dir, type);
        }

        sendAction(p, "§6[" + type.name() + "] §e" + currentAmmo + " / " + type.maxAmmo + " §7Ammo");
    }

    private void fireRaycast(Player shooter, Location origin, Vector dir, GunType type) {
        World w = origin.getWorld();
        if (w == null) return;

        // Perform raytrace against blocks and living entities
        RayTraceResult hit = w.rayTrace(origin, dir, type.range, FluidCollisionMode.NEVER, true, 0.25,
            entity -> entity instanceof LivingEntity && !entity.getUniqueId().equals(shooter.getUniqueId()));

        double maxDist = hit != null ? origin.distance(hit.getHitPosition().toLocation(w)) : type.range;

        // Render bullet trace particles
        for (double d = 1.0; d < maxDist; d += 1.0) {
            Location point = origin.clone().add(dir.clone().multiply(d));
            w.spawnParticle(Particle.CRIT, point, 1, 0, 0, 0, 0.0);
        }

        if (hit != null) {
            Location hitLoc = hit.getHitPosition().toLocation(w);

            if (hit.getHitEntity() instanceof LivingEntity target) {
                // Check headshot (hit within 0.35m of eye level)
                boolean headshot = Math.abs(hitLoc.getY() - target.getEyeLocation().getY()) <= 0.35;
                double finalDmg = type.damage * (headshot ? 1.5 : 1.0);

                target.damage(finalDmg, shooter);
                w.spawnParticle(Particle.DAMAGE_INDICATOR, hitLoc, headshot ? 8 : 4, 0.1, 0.1, 0.1, 0.1);

                if (headshot) {
                    shooter.playSound(shooter.getLocation(), Sound.ENTITY_EXPERIENCE_ORB_PICKUP, 0.6f, 1.9f);
                    sendAction(shooter, "§c§lHEADSHOT! §e" + target.getName() + " §7(-" + String.format("%.1f", finalDmg) + " HP)");
                } else {
                    sendAction(shooter, "§aHit §e" + target.getName() + " §7(-" + String.format("%.1f", finalDmg) + " HP)");
                }
            } else if (hit.getHitBlock() != null) {
                w.spawnParticle(Particle.SMOKE, hitLoc, 4, 0.1, 0.1, 0.1, 0.02);
                w.playSound(hitLoc, Sound.BLOCK_STONE_HIT, 0.5f, 1.4f);
            }
        }
    }

    private void startReload(Player p, ItemStack gun, ItemMeta meta, GunType type) {
        int current = meta.getPersistentDataContainer().getOrDefault(KEY_AMMO, PersistentDataType.INTEGER, 0);
        int needed = type.maxAmmo - current;
        int available = countAmmo(p, type.ammoType);

        if (available <= 0) {
            sendAction(p, "§cNo " + type.ammoType + " found in inventory!");
            p.playSound(p.getLocation(), Sound.BLOCK_DISPENSER_FAIL, 0.6f, 1.0f);
            return;
        }

        int toLoad = Math.min(needed, available);
        consumeAmmo(p, type.ammoType, toLoad);
        int finalAmmo = current + toLoad;

        UUID pid = p.getUniqueId();
        reloadUntil.put(pid, System.currentTimeMillis() + type.reloadTimeMs);

        p.playSound(p.getLocation(), Sound.ITEM_ARMOR_EQUIP_CHAIN, 0.8f, 1.2f);
        sendAction(p, "§eReloading " + type.displayName + "... (+" + toLoad + " rounds)");

        Bukkit.getScheduler().runTaskLater(plugin, () -> {
            if (!p.isOnline()) return;
            ItemStack currentHand = p.getInventory().getItemInMainHand();
            ItemMeta curMeta = currentHand.getItemMeta();
            if (curMeta != null && curMeta.getPersistentDataContainer().has(KEY_TYPE, PersistentDataType.STRING)) {
                curMeta.getPersistentDataContainer().set(KEY_AMMO, PersistentDataType.INTEGER, finalAmmo);
                updateLore(curMeta, type, finalAmmo);
                currentHand.setItemMeta(curMeta);
                p.playSound(p.getLocation(), Sound.BLOCK_IRON_TRAPDOOR_OPEN, 0.7f, 1.6f);
                sendAction(p, "§a[" + type.name() + " RELOADED] §e" + finalAmmo + " / " + type.maxAmmo);
            }
            reloadUntil.remove(pid);
        }, type.reloadTimeMs / 50L);
    }

    private int countAmmo(Player p, String ammoType) {
        int count = 0;
        for (ItemStack is : p.getInventory().getContents()) {
            if (is != null && is.hasItemMeta()) {
                String at = is.getItemMeta().getPersistentDataContainer().get(KEY_AMMO_ITEM, PersistentDataType.STRING);
                if (ammoType.equalsIgnoreCase(at)) {
                    count += is.getAmount();
                }
            }
        }
        return count;
    }

    private void consumeAmmo(Player p, String ammoType, int amount) {
        int left = amount;
        ItemStack[] contents = p.getInventory().getContents();
        for (int i = 0; i < contents.length; i++) {
            ItemStack is = contents[i];
            if (is != null && is.hasItemMeta()) {
                String at = is.getItemMeta().getPersistentDataContainer().get(KEY_AMMO_ITEM, PersistentDataType.STRING);
                if (ammoType.equalsIgnoreCase(at)) {
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
        }
    }

    private void sendAction(Player p, String msg) {
        p.sendActionBar(net.kyori.adventure.text.Component.text(msg));
    }
}
