package com.sdcraft.core;

import com.sdcraft.core.gtm.RoleplayText;
import com.sdcraft.core.gtm.NearMiss;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.event.ClickEvent;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.Color;
import org.bukkit.entity.Display;
import org.bukkit.entity.Entity;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Player;
import org.bukkit.entity.TextDisplay;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerCommandPreprocessEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.event.world.ChunkUnloadEvent;
import org.bukkit.event.vehicle.VehicleMoveEvent;
import org.bukkit.scheduler.BukkitTask;
import org.bukkit.util.Transformation;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/** Reachable, session-bound NPC conversations; one bounded bubble maintenance task. */
final class GtmDialogue implements Listener, AutoCloseable {
    private static final double BUBBLE_RISE = .75;
    private record Selection(UUID session, String npc, UUID entity, long until) {}
    private record Bubble(UUID speaker, TextDisplay display, long until, boolean ambient) {}
    private record Greeting(UUID player, String npc) {}
    private final SDCraftCorePlugin core;
    private final NpcService npcs;
    private final Ledger ledger;
    private final AiService ai;
    private final Map<UUID, Selection> selections = new HashMap<>();
    private final Map<UUID, Long> last = new HashMap<>();
    private final LinkedHashMap<UUID, Bubble> bubbles = new LinkedHashMap<>();
    private final LinkedHashMap<Greeting, Long> greeted = new LinkedHashMap<>();
    private final Map<UUID, Long> speakerCooldown = new HashMap<>();
    private final Map<UUID, Long> playerGreetingCooldown = new HashMap<>();
    private final Map<UUID, Location> vehiclePositions = new HashMap<>();
    private long nextReaction;
    private BukkitTask task;
    private int ticks;
    private boolean closed;

    GtmDialogue(SDCraftCorePlugin core, NpcService npcs, Ledger ledger, AiService ai) {
        this.core = core; this.npcs = npcs; this.ledger = ledger; this.ai = ai;
    }
    void start() { if (task == null) task = Bukkit.getScheduler().runTaskTimer(core, this::pulse, 5L, 5L); }
    private boolean enabled() { return !closed && core.getConfig().getBoolean("dialogue.enabled", true); }
    private boolean eligible(Player player) {
        return enabled() && core.isAuthenticated(player) && core.authenticatedSession(player) != null
                && !core.isDowned(player) && player.hasPermission("gtm.dialogue") && ledger.exists(player.getUniqueId());
    }
    private boolean reachable(Player player, Entity entity) {
        return entity instanceof LivingEntity && entity.isValid() && !entity.isDead()
                && entity.getWorld().equals(player.getWorld()) && entity.getLocation().distanceSquared(player.getLocation()) <= 49
                && player.hasLineOfSight(entity) && npcs.identify(entity) != null;
    }

    boolean select(Player player, Entity entity) {
        if (!eligible(player) || !reachable(player, entity)) return false;
        String id = npcs.identify(entity);
        npcs.holdConversation(player, entity);
        long now = System.currentTimeMillis();
        Selection previous = selections.put(player.getUniqueId(), new Selection(core.authenticatedSession(player), id, entity.getUniqueId(), now + 180_000));
        if (previous != null && previous.entity().equals(entity.getUniqueId()) && now - last.getOrDefault(player.getUniqueId(), 0L) < 1500) return true;
        String greeting = Jeeva.reply(player, id, npcs.name(id), npcs.role(id), npcs.dept(id),
                ledger.language(player.getUniqueId()), "hello", npcs.greeting(id, ledger.language(player.getUniqueId())));
        show(entity, greeting);
        player.sendMessage("§6" + npcs.name(id) + ": §f" + greeting);
        player.sendMessage(Component.text("[Talk] Type // followed by your message, or click here.", net.kyori.adventure.text.format.NamedTextColor.GRAY)
                .clickEvent(ClickEvent.suggestCommand("// ")));
        last.put(player.getUniqueId(), now);
        greeted.put(new Greeting(player.getUniqueId(), id), now + 120_000);
        speakerCooldown.put(entity.getUniqueId(), now + 30_000);
        playerGreetingCooldown.put(player.getUniqueId(), now + 12_000);
        return true;
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = true)
    public void input(PlayerCommandPreprocessEvent event) {
        String raw = event.getMessage();
        if (!RoleplayText.isDialogue(raw)) return;
        Player player = event.getPlayer();
        if ((player.isOp() || player.hasPermission("worldedit.*")) && RoleplayText.reservedEdit(raw)) return;
        event.setCancelled(true);
        if (!core.isAuthenticated(player)) return;
        if (!eligible(player)) {
            player.sendMessage("§eNPC conversation is disabled or unavailable for this account."); return;
        }
        Entity target = selected(player);
        if (target == null) target = lookingAt(player);
        if (target == null) {
            player.sendMessage("§eTap an NPC nearby, or look at one within seven blocks before speaking."); return;
        }
        talk(player, target, RoleplayText.message(raw));
    }

    void talkById(Player player, String id, String message) {
        if (!eligible(player)) { player.sendMessage("§eNPC conversation is disabled or unavailable for this account."); return; }
        Entity entity = npcs.activeEntity(id);
        if (!reachable(player, entity)) { player.sendMessage("§eMove near that NPC and make sure you can see them first."); return; }
        talk(player, entity, RoleplayText.clean(message));
    }

    private void talk(Player player, Entity target, String message) {
        if (message.isBlank()) return;
        long now = System.currentTimeMillis();
        if (now - last.getOrDefault(player.getUniqueId(), 0L) < 1000) return;
        last.put(player.getUniqueId(), now);
        String id = npcs.identify(target);
        npcs.holdConversation(player, target);
        Selection choice = new Selection(core.authenticatedSession(player), id, target.getUniqueId(), now + 180_000);
        selections.put(player.getUniqueId(), choice);
        show(player, message);
        ai.reply(player, id, npcs.name(id), npcs.role(id), npcs.dept(id), ledger.language(player.getUniqueId()),
                message, npcs.greeting(id, ledger.language(player.getUniqueId())), answer -> {
                    if (!eligible(player) || !choice.equals(selections.get(player.getUniqueId()))
                            || !Objects.equals(choice.session(), core.authenticatedSession(player)) || !reachable(player, target)
                            || !id.equals(npcs.identify(target))) return;
                    remove(player.getUniqueId());
                    show(target, answer);
                    player.sendMessage("§6" + npcs.name(id) + ": §f" + answer);
                });
    }

    private Entity selected(Player player) {
        Selection selection = selections.get(player.getUniqueId());
        if (selection == null || selection.until() < System.currentTimeMillis()
                || !Objects.equals(selection.session(), core.authenticatedSession(player))) return null;
        Entity entity = npcs.activeEntity(selection.npc());
        return entity != null && entity.getUniqueId().equals(selection.entity()) && reachable(player, entity) ? entity : null;
    }
    private Entity lookingAt(Player player) {
        Location eye = player.getEyeLocation();
        var hit = player.getWorld().rayTraceEntities(eye, eye.getDirection(), 7, .35,
                entity -> reachable(player, entity));
        return hit == null ? null : hit.getHitEntity();
    }

    private void pulse() {
        if (closed) return;
        long now = System.currentTimeMillis();
        for (Player player : Bukkit.getOnlinePlayers()) {
            if (!eligible(player) || !player.isInsideVehicle()) { vehiclePositions.remove(player.getUniqueId()); continue; }
            Location at = player.getLocation(); Location previous = vehiclePositions.put(player.getUniqueId(), at.clone());
            if (previous != null && previous.getWorld().equals(at.getWorld()))
                react(player, at, at.toVector().subtract(previous.toVector()).multiply(.2));
        }
        for (Bubble bubble : new ArrayList<>(bubbles.values())) {
            Entity speaker = Bukkit.getEntity(bubble.speaker());
            if (!enabled() || bubble.until() <= now || speaker == null || !speaker.isValid() || !bubble.display().isValid()) {
                remove(bubble.speaker()); continue;
            }
            bubble.display().teleport(speaker.getLocation().add(0, speaker.getHeight() + BUBBLE_RISE, 0));
        }
        selections.entrySet().removeIf(entry -> {
            Player player = Bukkit.getPlayer(entry.getKey());
            return player == null || !eligible(player) || entry.getValue().until() <= now
                    || !Objects.equals(entry.getValue().session(), core.authenticatedSession(player));
        });
        if (++ticks % 4 != 0 || !enabled() || !core.getConfig().getBoolean("dialogue.proximity-greetings", true)) return;
        greeted.entrySet().removeIf(entry -> entry.getValue() <= now);
        speakerCooldown.entrySet().removeIf(entry -> entry.getValue() <= now);
        playerGreetingCooldown.entrySet().removeIf(entry -> entry.getValue() <= now);
        int budget = 2;
        for (Player player : Bukkit.getOnlinePlayers()) {
            if (budget <= 0) break;
            if (!eligible(player) || selected(player) != null || playerGreetingCooldown.getOrDefault(player.getUniqueId(), 0L) > now) continue;
            for (Entity entity : player.getNearbyEntities(3, 2, 3)) {
                if (!reachable(player, entity) || speakerCooldown.containsKey(entity.getUniqueId())) continue;
                String id = npcs.identify(entity); Greeting key = new Greeting(player.getUniqueId(), id);
                if (greeted.containsKey(key)) continue;
                if (!show(entity, npcs.greeting(id, ledger.language(player.getUniqueId())), true)) continue;
                greeted.put(key, now + 120_000); speakerCooldown.put(entity.getUniqueId(), now + 30_000);
                playerGreetingCooldown.put(player.getUniqueId(), now + 12_000);
                while (greeted.size() > 512) greeted.remove(greeted.keySet().iterator().next());
                budget--; break;
            }
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void vehicleMoved(VehicleMoveEvent event) {
        for (Entity passenger : event.getVehicle().getPassengers()) {
            if (passenger instanceof Player player && eligible(player)) {
                react(player, event.getTo(), event.getVehicle().getVelocity()); break;
            }
        }
    }

    private void react(Player player, Location at, org.bukkit.util.Vector velocity) {
        long now = System.currentTimeMillis();
        if (now < nextReaction) return;
        for (Entity entity : player.getNearbyEntities(6, 2, 6)) {
            if (!entity.isValid() || npcs.identify(entity) == null || bubbles.containsKey(entity.getUniqueId())
                    || speakerCooldown.getOrDefault(entity.getUniqueId(), 0L) > now || !player.hasLineOfSight(entity)) continue;
            var distance = entity.getLocation().toVector().subtract(at.toVector());
            if (!NearMiss.approaching(distance.getX(), distance.getY(), distance.getZ(), velocity.getX(), velocity.getZ())) continue;
            nextReaction = now + 250;
            speakerCooldown.put(entity.getUniqueId(), now + 10_000);
            show(entity, RoleplayText.reaction(ledger.language(player.getUniqueId()), npcs.isAttackable(entity), (int)(now / 1000)), true);
            break;
        }
    }

    private void show(Entity speaker, String raw) {
        show(speaker, raw, false);
    }
    private boolean show(Entity speaker, String raw, boolean ambient) {
        remove(speaker.getUniqueId());
        String text = RoleplayText.clean(raw); if (text.isBlank() || !speaker.isValid()) return false;
        for (Bubble existing : new ArrayList<>(bubbles.values())) {
            if (!existing.display().isValid() || !existing.display().getWorld().equals(speaker.getWorld())
                    || existing.display().getLocation().distanceSquared(speaker.getLocation()) > 64) continue;
            if (ambient) return false;
            if (existing.ambient()) remove(existing.speaker());
        }
        while (bubbles.size() >= 64) remove(bubbles.keySet().iterator().next());
        TextDisplay display = speaker.getWorld().spawn(speaker.getLocation().add(0, speaker.getHeight() + BUBBLE_RISE, 0), TextDisplay.class, value -> {
            value.text(Component.text(text)); value.setBillboard(Display.Billboard.CENTER); value.setLineWidth(190);
            value.setSeeThrough(false); value.setShadowed(true); value.setPersistent(false); value.setViewRange(.4f);
            value.setBackgroundColor(Color.fromARGB(190, 12, 16, 20));
            value.setTransformation(new Transformation(new Vector3f(), new Quaternionf(), new Vector3f(.65f), new Quaternionf()));
        });
        bubbles.put(speaker.getUniqueId(), new Bubble(speaker.getUniqueId(), display, System.currentTimeMillis() + 7000, ambient));
        return true;
    }
    private void remove(UUID speaker) {
        Bubble previous = bubbles.remove(speaker); if (previous != null) previous.display().remove();
    }
    void authenticationLost(Player player) {
        UUID id = player.getUniqueId(); selections.remove(id); last.remove(id); vehiclePositions.remove(id); playerGreetingCooldown.remove(id); remove(id);
        greeted.keySet().removeIf(key -> key.player().equals(id));
    }
    @EventHandler public void quit(PlayerQuitEvent event) { authenticationLost(event.getPlayer()); }
    @EventHandler public void unload(ChunkUnloadEvent event) {
        for (Entity entity : event.getChunk().getEntities()) remove(entity.getUniqueId());
    }
    @Override public void close() {
        if (closed) return; closed = true;
        if (task != null) task.cancel();
        for (UUID id : new ArrayList<>(bubbles.keySet())) remove(id);
        selections.clear(); last.clear(); greeted.clear(); speakerCooldown.clear(); playerGreetingCooldown.clear(); vehiclePositions.clear();
    }
}
