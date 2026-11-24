package com.sdcraft.core;

import com.sdcraft.core.gtm.RoleplayText;
import com.sdcraft.core.gtm.NearMiss;
import org.bukkit.event.vehicle.VehicleMoveEvent;
import java.util.*;
import org.bukkit.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.player.*;
import org.bukkit.event.world.ChunkUnloadEvent;
import org.bukkit.plugin.java.JavaPlugin;
import net.kyori.adventure.text.Component;

/** Opt-in Paper dialogue adapter. Never invokes a command or alters economic state. */
final class GtmDialogue implements Listener {
    private final JavaPlugin plugin;
    private final NpcService npcs;
    private final Ledger ledger;
    private final Map<UUID, UUID> bubbles = new HashMap<>();
    private final Map<UUID, Long> last = new HashMap<>();
    private final Map<UUID, Long> reactions = new HashMap<>();
    private long nextReactionScan = 0;
    @EventHandler(priority = EventPriority.MONITOR)
    public void onVehicleMove(VehicleMoveEvent event) {
        if (!plugin.getConfig().getBoolean("gtm.experimental-dialogue", false)) return;
        long now = System.currentTimeMillis();
        if (now < nextReactionScan) return;
        Player driver = null;
        for (Entity passenger : event.getVehicle().getPassengers()) {
            if (passenger instanceof Player p && npcs.identify(p) == null && p.hasPermission("gtm.dialogue") && ledger.exists(p.getUniqueId())) {
                driver = p; break;
            }
        }
        if (driver == null) return;
        nextReactionScan = now + 250;
        var velocity = event.getVehicle().getVelocity();
        var at = event.getTo();
        reactions.entrySet().removeIf(e -> e.getValue() < now);
        Entity target = null;
        double best = Double.POSITIVE_INFINITY;
        for (Entity candidate : event.getVehicle().getNearbyEntities(6,2,6)) {
            if (!(candidate instanceof LivingEntity) || !candidate.isValid() || bubbles.containsKey(candidate.getUniqueId()) || reactions.containsKey(candidate.getUniqueId())) continue;
            String id = npcs.identify(candidate);
            if (id == null) continue;
            var d = candidate.getLocation().toVector().subtract(at.toVector());
            if (!NearMiss.approaching(d.getX(),d.getY(),d.getZ(),velocity.getX(),velocity.getZ())) continue;
            if (d.lengthSquared() < best) { target = candidate; best = d.lengthSquared(); }
        }
        if (target == null || reactions.size() >= 128) return;
        reactions.put(target.getUniqueId(),now+10000);
        show(target, RoleplayText.reaction(ledger.language(driver.getUniqueId()),false,(int)(now/1000)));
    }
    GtmDialogue(JavaPlugin plugin, NpcService npcs, Ledger ledger) {
        this.plugin = plugin; this.npcs = npcs; this.ledger = ledger;
    }
    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void onInput(PlayerCommandPreprocessEvent event) {
        if (!plugin.getConfig().getBoolean("gtm.experimental-dialogue", false)) return;
        String raw = event.getMessage();
        if (!RoleplayText.isDialogue(raw)) return;
        Player player = event.getPlayer();
        if (player.hasPermission("worldedit.*") || player.isOp()) {
            if (RoleplayText.reservedEdit(raw)) return;
        }
        event.setCancelled(true);
        if (!player.hasPermission("gtm.dialogue") || !ledger.exists(player.getUniqueId())) return;
        String message = RoleplayText.message(raw);
        if (message.isBlank()) return;
        long now = System.currentTimeMillis();
        if (now - last.getOrDefault(player.getUniqueId(), 0L) < 2000) return;
        last.put(player.getUniqueId(), now);
        show(player, message);
        Entity target = null; String id = null; double best = -Double.MAX_VALUE;
        Location eye = player.getEyeLocation();
        for (Entity nearby : player.getNearbyEntities(7, 4, 7)) {
            if (!(nearby instanceof LivingEntity living) || !living.isValid() || !player.hasLineOfSight(nearby)) continue;
            String candidate = npcs.identify(nearby);
            if (candidate == null) continue;
            var delta = living.getEyeLocation().toVector().subtract(eye.toVector());
            double distance = delta.length();
            if (distance > 7 || distance < 0.01) continue;
            double alignment = delta.clone().normalize().dot(eye.getDirection());
            if (alignment < 0.1) continue;
            double score = alignment * 4 - distance / 7;
            if (score > best) { best = score; target = nearby; id = candidate; }
        }
        if (target == null) return;
        String lang = RoleplayText.language(message, ledger.language(player.getUniqueId()));
        String reply = Jeeva.reply(player, id, npcs.name(id), npcs.role(id), npcs.dept(id),
                lang, message, npcs.greeting(id, lang));
        show(target, reply);
    }
    private void show(Entity speaker, String raw) {
        remove(speaker.getUniqueId());
        String text = RoleplayText.clean(raw);
        if (text.isEmpty()) return;
        TextDisplay display = speaker.getWorld().spawn(speaker.getLocation().add(0, speaker.getHeight() + .35, 0),
                TextDisplay.class, d -> {
                    d.text(Component.text(text));
                    d.setBillboard(Display.Billboard.CENTER);
                    d.setLineWidth(180);
                    d.setSeeThrough(false);
                    d.setShadowed(true);
                    d.setPersistent(false);
                    d.setViewRange(.4f);
                });
        UUID owner = speaker.getUniqueId(), displayId = display.getUniqueId();
        bubbles.put(owner, displayId);
        Bukkit.getScheduler().runTaskTimer(plugin, task -> {
            if (!displayId.equals(bubbles.get(owner))) { display.remove(); task.cancel(); return; }
            if (!speaker.isValid() || !display.isValid()) { remove(owner); task.cancel(); return; }
            display.teleport(speaker.getLocation().add(0, speaker.getHeight() + .35, 0));
        }, 1L, 5L);
        Bukkit.getScheduler().runTaskLater(plugin, () -> {
            if (displayId.equals(bubbles.get(owner))) remove(owner);
        }, 100L);
    }
    private void remove(UUID owner) {
        UUID id = bubbles.remove(owner);
        if (id != null) {
            Entity display = Bukkit.getEntity(id);
            if (display != null) display.remove();
        }
    }
    @EventHandler public void onQuit(PlayerQuitEvent event) {
        UUID id = event.getPlayer().getUniqueId();
        last.remove(id); remove(id);
    }
    @EventHandler public void onChunkUnload(ChunkUnloadEvent event) {
        Set<UUID> unloading = new HashSet<>();
        for (Entity entity : event.getChunk().getEntities()) unloading.add(entity.getUniqueId());
        for (UUID owner : new ArrayList<>(bubbles.keySet()))
            if (unloading.contains(owner) || unloading.contains(bubbles.get(owner))) remove(owner);
    }
    void close() { for (UUID owner : new ArrayList<>(bubbles.keySet())) remove(owner); last.clear(); reactions.clear(); }
}
