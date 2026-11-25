/* Reconstructed from the preserved 1.0.3 binary with CFR 0.152; repaired and patched.
 * This is maintainable hotfix source, not recovery of the lost original checkout. */
package com.sdcraft.core;

import com.sdcraft.core.GtmPhoneApps;
import com.sdcraft.core.SDCraftCorePlugin;
import com.sdcraft.core.gtm.SnapshotStore;
import com.sdcraft.core.phone.MapProjection;
import com.sdcraft.core.phone.PhoneStore;
import com.sdcraft.core.phone.UiCatalog;
import com.sdcraft.core.phone.VehicleDashboard;
import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics2D;
import java.awt.Image;
import java.awt.Rectangle;
import java.awt.RenderingHints;
import java.awt.Shape;
import java.awt.geom.AffineTransform;
import java.awt.geom.Area;
import java.awt.geom.Ellipse2D;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import javax.imageio.ImageIO;
import net.kyori.adventure.key.Key;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import net.kyori.adventure.text.format.TextColor;
import net.kyori.adventure.title.Title;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.HeightMap;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.World;
import org.bukkit.attribute.Attribute;
import org.bukkit.attribute.AttributeInstance;
import org.bukkit.entity.Display;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.entity.TextDisplay;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.inventory.meta.MapMeta;
import org.bukkit.map.MapCanvas;
import org.bukkit.map.MapRenderer;
import org.bukkit.map.MapView;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.Plugin;

final class GtmPhoneHud
implements AutoCloseable {
    private final SDCraftCorePlugin plugin;
    private final GtmPhoneApps phone;
    private final UiCatalog art;
    private final GtmPhoneStatus status = new GtmPhoneStatus();
    private final Map<String, BufferedImage> images = new HashMap<String, BufferedImage>();
    private final Map<UUID, Integer> mapIds = new LinkedHashMap<UUID, Integer>();
    private final Map<UUID, MapView> maps = new HashMap<UUID, MapView>();
    private final Map<Cell, Sample> terrain = new LinkedHashMap<Cell, Sample>(128, 0.75f, true);
    private final Map<UUID, MapFrame> frames = new HashMap<UUID, MapFrame>();
    private final Map<UUID, Integer> sampleOffsets = new HashMap<UUID, Integer>();
    private final Map<UUID, Boolean> city = new HashMap<UUID, Boolean>();
    private final Map<UUID, Long> mutedUntil = new HashMap<UUID, Long>();
    private final Map<UUID, Bubble> bubbles = new HashMap<UUID, Bubble>();
    private final SnapshotStore mapStore;
    private long mapRevision;
    private long ticks;
    private long nextWarning;
    private int budget = 128;
    private final NamespacedKey mapKey;

    GtmPhoneHud(SDCraftCorePlugin plugin, GtmPhoneApps phone, UiCatalog art) throws IOException {
        this.plugin = plugin;
        this.phone = phone;
        this.art = art;
        this.mapKey = new NamespacedKey((Plugin)plugin, "phone_map");
        for (UiCatalog.Asset a : art.family("hud")) {
            InputStream input = plugin.getResource(a.resource());
            try {
                if (input == null) {
                    throw new IOException("Missing native HUD image");
                }
                BufferedImage image = ImageIO.read(input);
                if (image == null || image.getWidth() != 128 || image.getHeight() != 128) {
                    throw new IOException("Invalid native HUD image");
                }
                this.images.put(a.id(), image);
            }
            finally {
                if (input == null) continue;
                input.close();
            }
        }
        this.mapStore = new SnapshotStore(plugin.getDataFolder().toPath().resolve("phone-maps.snapshot"), 4096);
        SnapshotStore.Snapshot saved = this.mapStore.read();
        this.mapRevision = saved.version();
        if (saved.payload().length > 0) {
            try (DataInputStream in = new DataInputStream(new ByteArrayInputStream(saved.payload()));){
                if (in.readInt() != 1296126001) {
                    throw new IOException("Unsupported phone map store");
                }
                int size = in.readInt();
                if (size < 0 || size > 16) {
                    throw new IOException("Invalid phone map count");
                }
                for (int i = 0; i < size; ++i) {
                    UUID world = new UUID(in.readLong(), in.readLong());
                    int id = in.readInt();
                    if (id >= 0 && this.mapIds.putIfAbsent(world, id) == null) continue;
                    throw new IOException("Invalid map identity");
                }
                if (in.read() != -1) {
                    throw new IOException("Trailing phone map data");
                }
            }
        }
    }

    void giveMap(Player p) throws IOException {
        this.giveDisplay(p, false);
    }

    void giveDashboard(Player p) throws IOException {
        this.giveDisplay(p, true);
    }

    private void giveDisplay(Player p, boolean dashboard) throws IOException {
        if (!this.phone.available(p)) {
            throw new IllegalStateException("Authenticate before opening your map");
        }
        MapView view = this.map(p.getWorld());
        byte kind = (byte)(dashboard ? 2 : 1);
        for (int slot = 0; slot < p.getInventory().getSize(); ++slot) {
            ItemStack item = p.getInventory().getItem(slot);
            if (item == null || item.getType() != Material.FILLED_MAP || !item.hasItemMeta() || !Objects.equals(item.getItemMeta().getPersistentDataContainer().get(this.mapKey, PersistentDataType.BYTE), kind)) continue;
            MapMeta meta = (MapMeta)item.getItemMeta();
            meta.setMapView(view);
            item.setItemMeta((ItemMeta)meta);
            p.getInventory().setItem(slot, item);
            this.frames.remove(p.getUniqueId());
            p.sendMap(view);
            p.sendMessage(dashboard ? "\u00a7aYour live dashboard is refreshed. Hold it while using your vehicle; instrument style is in phone Settings." : "\u00a7aYour terrain map is refreshed. Hold it to view; map settings are in your phone.");
            return;
        }
        if (p.getInventory().firstEmpty() < 0) {
            throw new IllegalStateException("Make one inventory slot available for your reusable terrain map");
        }
        ItemStack item = new ItemStack(Material.FILLED_MAP);
        MapMeta meta = (MapMeta)item.getItemMeta();
        meta.setMapView(view);
        meta.setDisplayName(dashboard ? "\u00a76GTM Live Vehicle Dashboard" : "\u00a76GTM Live City Map");
        meta.setLore(dashboard ? List.of("\u00a77Actual vehicle speed, energy and condition", "\u00a77Phone Settings: analog, digital or compact") : List.of("\u00a77Loaded terrain \u2022 personal map settings", "\u00a77Phone: Maps, Settings and registered destinations"));
        meta.getPersistentDataContainer().set(this.mapKey, PersistentDataType.BYTE, kind);
        item.setItemMeta((ItemMeta)meta);
        if (!p.getInventory().addItem(new ItemStack[]{item}).isEmpty()) {
            throw new IllegalStateException("Inventory changed; reopen the map after making room");
        }
        this.frames.remove(p.getUniqueId());
        p.sendMap(view);
        p.sendMessage(dashboard ? "\u00a7aHold your GTM dashboard while using a vehicle. Its readings follow actual accepted movement." : "\u00a7aHold your GTM map. Use the phone to select its layout, rotation, zoom and destination.");
    }

    private MapView map(World world) throws IOException {
        MapView view;
        if (this.maps.containsKey(world.getUID())) {
            return this.maps.get(world.getUID());
        }
        Integer id = this.mapIds.get(world.getUID());
        MapView mapView = view = id == null ? null : Bukkit.getMap((int)id);
        if (!(view == null || view.getWorld() != null && view.getWorld().getUID().equals(world.getUID()))) {
            throw new IOException("Stored map belongs to a different world; review the consistent world/map backup");
        }
        if (view == null) {
            if (!this.mapIds.containsKey(world.getUID()) && this.mapIds.size() >= 16) {
                throw new IllegalStateException("Phone map world capacity reached");
            }
            view = Bukkit.createMap((World)world);
            LinkedHashMap<UUID, Integer> next = new LinkedHashMap<UUID, Integer>(this.mapIds);
            next.put(world.getUID(), view.getId());
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            try (DataOutputStream out = new DataOutputStream(bytes);){
                out.writeInt(1296126001);
                out.writeInt(next.size());
                for (Map.Entry e : next.entrySet()) {
                    out.writeLong(((UUID)e.getKey()).getMostSignificantBits());
                    out.writeLong(((UUID)e.getKey()).getLeastSignificantBits());
                    out.writeInt((Integer)e.getValue());
                }
            }
            SnapshotStore.Snapshot saved = this.mapStore.commit(this.mapRevision, UUID.randomUUID(), bytes.toByteArray());
            this.mapRevision = saved.version();
            this.mapIds.clear();
            this.mapIds.putAll(next);
        }
        for (MapRenderer renderer : new ArrayList<>(view.getRenderers())) {
            view.removeRenderer(renderer);
        }
        view.setTrackingPosition(false);
        view.setUnlimitedTracking(false);
        view.addRenderer(new MapRenderer(true) {
            public void render(MapView map, MapCanvas canvas, Player viewer) {
                if (!GtmPhoneHud.this.phone.available(viewer)) {
                    canvas.drawImage(0, 0, (Image)GtmPhoneHud.blank());
                    return;
                }
                long now = System.nanoTime();
                boolean dashboard = GtmPhoneHud.this.heldDashboard(viewer);
                PhoneStore.Preferences preferences = GtmPhoneHud.this.phone.preferences(viewer.getUniqueId());
                MapFrame existing = GtmPhoneHud.this.frames.get(viewer.getUniqueId());
                if (existing != null && now < existing.next() && existing.world().equals(viewer.getWorld().getUID()) && existing.dashboard() == dashboard && existing.preferences().equals(preferences)) {
                    canvas.drawImage(0, 0, (Image)existing.image());
                    return;
                }
                try {
                    BufferedImage image = dashboard ? GtmPhoneHud.this.renderDashboard(viewer) : GtmPhoneHud.this.renderMap(viewer, now);
                    GtmPhoneHud.this.frames.put(viewer.getUniqueId(), new MapFrame(now + 250000000L, viewer.getWorld().getUID(), dashboard, preferences, image));
                    canvas.drawImage(0, 0, (Image)image);
                }
                catch (RuntimeException unavailable) {
                    GtmPhoneHud.this.warn(unavailable);
                    canvas.drawImage(0, 0, (Image)GtmPhoneHud.blank());
                }
            }
        });
        this.maps.put(world.getUID(), view);
        return view;
    }

    private boolean heldDashboard(Player p) {
        for (ItemStack item : List.of(p.getInventory().getItemInMainHand(), p.getInventory().getItemInOffHand())) {
            Byte kind;
            if (item.getType() != Material.FILLED_MAP || !item.hasItemMeta() || (kind = (Byte)item.getItemMeta().getPersistentDataContainer().get(this.mapKey, PersistentDataType.BYTE)) == null) continue;
            return kind == 2;
        }
        return false;
    }

    private BufferedImage renderDashboard(Player p) {
        PhoneStore.SpeedStyle style = this.phone.preferences(p.getUniqueId()).speedStyle();
        Optional<GtmPhoneApps.DriveData> d = this.phone.services().driving(p);
        VehicleDashboard.Reading reading = d.map(v -> new VehicleDashboard.Reading(v.title(), v.mode(), v.blocksPerSecond(), v.energyKind(), v.energyPercent(), v.health())).orElse(null);
        return VehicleDashboard.render(style, this.images.get("speedometer_" + style.name().toLowerCase(Locale.ROOT)), reading);
    }

    private static BufferedImage blank() {
        BufferedImage image = new BufferedImage(128, 128, 1);
        Graphics2D g = image.createGraphics();
        g.setColor(new Color(1383200));
        g.fillRect(0, 0, 128, 128);
        g.dispose();
        return image;
    }

    private BufferedImage renderMap(Player p, long now) {
        int start;
        BufferedImage image = GtmPhoneHud.blank();
        Graphics2D g = image.createGraphics();
        PhoneStore.Preferences prefs = this.phone.preferences(p.getUniqueId());
        Location loc = p.getLocation();
        MapProjection projection = new MapProjection(loc.getX(), loc.getZ(), loc.getYaw(), prefs.rotate(), prefs.zoom(), prefs.layout());
        g.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_NEAREST_NEIGHBOR);
        int next = start = this.sampleOffsets.getOrDefault(p.getUniqueId(), 0).intValue();
        int allowance = Math.min(64, Math.max(1, 128 / Math.max(1, Bukkit.getOnlinePlayers().size())));
        int spent = 0;
        for (int offset = 0; offset < 784; ++offset) {
            int index = (start + offset) % 784;
            int px = 8 + 4 * (index % 28);
            int py = 8 + 4 * (index / 28);
            if (!projection.inside(px + 2, py + 2)) continue;
            MapProjection.Point point = projection.world(px + 2, py + 2);
            int x = (int)Math.floor(point.x());
            int n = (int)Math.floor(point.z());
            int before = this.budget;
            g.setColor(this.sample(p.getWorld(), x, n, now, spent < allowance));
            g.fillRect(px, py, 4, 4);
            if (this.budget >= before) continue;
            ++spent;
            next = (index + 1) % 784;
        }
        this.sampleOffsets.put(p.getUniqueId(), next);
        if (prefs.layout() == PhoneStore.Layout.CIRCLE) {
            Area outside = new Area(new Rectangle(0, 0, 128, 128));
            outside.subtract(new Area(new Ellipse2D.Double(8.0, 8.0, 112.0, 112.0)));
            g.setColor(new Color(1383200));
            g.fill(outside);
        }
        Shape clip = g.getClip();
        g.setClip(prefs.layout() == PhoneStore.Layout.CIRCLE ? new Ellipse2D.Double(9.0, 9.0, 110.0, 110.0) : new Rectangle(9, 9, 110, 110));
        Optional<GtmPhoneApps.Destination> target = this.phone.navigation(p.getUniqueId());
        boolean bearing = false;
        if (target.isPresent() && target.get().location().getWorld().equals((Object)p.getWorld())) {
            List<Location> route = this.phone.services().route(p, target.get());
            if (route.size() > 4096) {
                route = List.of();
            }
            g.setColor(new Color(14069081));
            g.setStroke(new BasicStroke(2.0f));
            if (route.size() > 1) {
                Location last = null;
                for (Location location : route) {
                    if (location == null || location.getWorld() != p.getWorld() || !Double.isFinite(location.getX()) || !Double.isFinite(location.getZ())) {
                        last = null;
                        continue;
                    }
                    if (last != null) {
                        MapProjection.Point a = projection.pixel(last.getX(), last.getZ());
                        MapProjection.Point b = projection.pixel(location.getX(), location.getZ());
                        g.drawLine((int)a.x(), (int)a.z(), (int)b.x(), (int)b.z());
                    }
                    last = location;
                }
            } else {
                bearing = true;
                g.setStroke(new BasicStroke(1.0f, 0, 0, 10.0f, new float[]{3.0f, 3.0f}, 0.0f));
                Location dest = target.get().location();
                MapProjection.Point end = projection.pixel(dest.getX(), dest.getZ());
                g.drawLine(64, 64, (int)end.x(), (int)end.z());
            }
        }
        int markers = 0;
        for (GtmPhoneApps.Destination d : this.phone.destinations(p)) {
            MapProjection.Point point;
            if (!d.location().getWorld().equals((Object)p.getWorld()) || !projection.inside((point = projection.pixel(d.location().getX(), d.location().getZ())).x(), point.z()) || markers++ >= 64) continue;
            this.draw(g, GtmPhoneApps.marker(d.category()), (int)point.x() - 5, (int)point.z() - 5, 10, 10);
        }
        AffineTransform before = g.getTransform();
        g.rotate(prefs.rotate() ? 0.0 : Math.toRadians(loc.getYaw() + 180.0f), 64.0, 64.0);
        this.draw(g, "player_arrow", 58, 58, 12, 12);
        g.setTransform(before);
        g.setClip(clip);
        this.draw(g, prefs.layout() == PhoneStore.Layout.CIRCLE ? "minimap_circle" : "minimap_rectangle", 0, 0, 128, 128);
        g.setFont(new Font("SansSerif", 1, 7));
        g.setColor(new Color(13810071));
        String district = ChatColor.stripColor((String)this.phone.services().district(p));
        g.drawString(district.substring(0, Math.min(24, district.length())), 4, 7);
        g.setFont(new Font("SansSerif", 0, 7));
        g.drawString(prefs.zoom() + "b " + (bearing ? "Bearing" : "Map") + " | " + (prefs.rotate() ? "Heading" : "North"), 4, 125);
        this.draw(g, "health", 4, 111, 9, 9);
        g.setColor(new Color(11359799));
        g.fillRect(14, 113, (int)Math.max(0.0, Math.min(34.0, p.getHealth() / GtmPhoneHud.maxHealth(p) * 34.0)), 3);
        this.draw(g, "armour", 51, 111, 9, 9);
        g.setColor(new Color(8166312));
        g.fillRect(61, 113, (int)Math.max(0.0, Math.min(28.0, GtmPhoneHud.armour(p) / 20.0 * 28.0)), 3);
        g.dispose();
        return image;
    }

    private Color sample(World world, int x, int z, long now, boolean allowQuery) {
        x = Math.floorDiv(x, 4) * 4;
        z = Math.floorDiv(z, 4) * 4;
        Cell key = new Cell(world.getUID(), x, z);
        Sample saved = this.terrain.get(key);
        if (saved != null && saved.expires() > now) {
            return saved.color();
        }
        if (!allowQuery || this.budget <= 0 || !world.isChunkLoaded(x >> 4, z >> 4)) {
            return saved == null ? new Color(0x273237) : saved.color();
        }
        --this.budget;
        int y = world.getHighestBlockYAt(x, z, HeightMap.MOTION_BLOCKING_NO_LEAVES);
        Material type = world.getBlockAt(x, y, z).getType();
        Color color = GtmPhoneHud.color(type);
        this.terrain.put(key, new Sample(color, now + 30000000000L));
        while (this.terrain.size() > 8192) {
            this.terrain.remove(this.terrain.keySet().iterator().next());
        }
        return color;
    }

    private static Color color(Material type) {
        String s = type.name();
        int rgb = s.contains("WATER") ? 3497593 : (s.contains("LEAVES") || s.contains("GRASS") || s.contains("MOSS") ? 4025934 : (s.contains("SAND") ? 13810071 : (s.contains("TERRACOTTA") || s.contains("BRICK") ? 11359799 : (s.contains("CONCRETE") || s.contains("ASPHALT") ? 5265244 : (s.contains("SNOW") || s.contains("QUARTZ") ? 14673117 : (s.contains("WOOD") || s.contains("LOG") || s.contains("PLANK") ? 9794904 : (s.contains("LAVA") ? 12346427 : 8750202)))))));
        return new Color(rgb);
    }

    private void draw(Graphics2D g, String id, int x, int y, int w, int h) {
        g.drawImage(this.images.get(id), x, y, w, h, null);
    }

    private static double maxHealth(Player p) {
        AttributeInstance value = p.getAttribute(Attribute.MAX_HEALTH);
        return value == null ? 20.0 : Math.max(1.0, value.getValue());
    }

    private static double armour(Player p) {
        AttributeInstance value = p.getAttribute(Attribute.ARMOR);
        return value == null ? 0.0 : value.getValue();
    }

    private Component glyph(Player p, String id, String fallback, boolean large) {
        return this.phone.services().glyphsAvailable(p) ? Component.text((String)this.art.require(id).glyph()).font(Key.key((String)"gtm", (String)(large ? "ui_large" : "ui"))) : Component.text((String)fallback);
    }

    void tick() {
        this.ticks += 5L;
        this.budget = 128;
        for (Map.Entry<UUID, Bubble> e : new ArrayList<Map.Entry<UUID, Bubble>>(this.bubbles.entrySet())) {
            Player p = Bukkit.getPlayer((UUID)e.getKey());
            Bubble b = e.getValue();
            if (p != null && this.phone.available(p) && Objects.equals(this.plugin.authenticatedSession(p), b.session()) && this.ticks < b.expires()) continue;
            b.display().remove();
            this.bubbles.remove(e.getKey());
        }
        if (this.ticks % 10L != 0L) {
            return;
        }
        for (Player p : Bukkit.getOnlinePlayers()) {
            try {
                if (!this.phone.available(p)) {
                    this.forget(p);
                    continue;
                }
                boolean inside = this.phone.services().inCity(p);
                Boolean prior = this.city.put(p.getUniqueId(), inside);
                if (prior != null && prior != inside) {
                    this.cinematic(p, inside ? "city_enter" : "city_exit", this.phone.services().district(p));
                }
                if (!this.phone.preferences(p.getUniqueId()).hud()) {
                    this.status.remove(p);
                    continue;
                }
                Component stars = Component.empty();
                int wanted = Math.max(0, Math.min(5, this.phone.services().wanted(p)));
                for (int star = 0; star < 5; star++) {
                    stars = stars.append(this.glyph(p, star < wanted ? "wanted_star_filled" : "wanted_star_empty",
                            star < wanted ? "★" : "☆", false));
                }
                String district = Objects.toString(ChatColor.stripColor(this.phone.services().district(p)), "Indraprastha");
                if (district.length() > 24) district = district.substring(0, 23) + "…";
                this.status.update(p, List.of(
                        Component.text(district, NamedTextColor.GRAY),
                        stars,
                        Component.text("ARK ", NamedTextColor.GOLD).append(Component.text(
                                String.format(Locale.ROOT, "%,.2f", this.phone.services().wallet(p) / 100.0), NamedTextColor.WHITE)),
                        Component.text("Bank ", NamedTextColor.GRAY).append(Component.text(
                                String.format(Locale.ROOT, "%,.2f", this.phone.services().bank(p) / 100.0), NamedTextColor.WHITE)),
                        Component.text(String.format(Locale.ROOT, "HP %.0f  ·  Armour %.0f", p.getHealth(), GtmPhoneHud.armour(p)), NamedTextColor.GRAY),
                        Component.text("/phone  ·  City services", NamedTextColor.AQUA)));
                // Do not compete with weapon/ammo messages on foot. Driving
                // gets one short telemetry strip instead of the old full-width
                // health + armour + stars + money + controls sentence.
                if (this.mutedUntil.getOrDefault(p.getUniqueId(), 0L) > this.ticks
                        || p.getOpenInventory().getTopInventory().getSize() > 5) continue;
                Optional<GtmPhoneApps.DriveData> drive = this.phone.services().driving(p);
                if (drive.isPresent()) {
                    GtmPhoneApps.DriveData d = drive.get();
                    String energy = d.energyKind().toLowerCase(Locale.ROOT).contains("electric") ? "Battery" : "Fuel";
                    String text = String.format(Locale.ROOT, "%s%.0f km/h  ·  %s %.0f%%  ·  Body %.0f%%",
                            d.blocksPerSecond() < -0.05 ? "R " : "", Math.abs(d.blocksPerSecond()) * 3.6,
                            energy, d.energyPercent(), d.health());
                    p.sendActionBar(Component.text(text, d.energyPercent() < 15 || d.health() < 25
                            ? NamedTextColor.YELLOW : NamedTextColor.WHITE));
                }
            }
            catch (RuntimeException unavailable) {
                this.warn(unavailable);
            }
        }
    }

    private void warn(RuntimeException failure) {
        if (this.ticks >= this.nextWarning) {
            this.nextWarning = this.ticks + 1200L;
            this.plugin.getLogger().warning("Phone HUD source temporarily unavailable: " + failure.getClass().getSimpleName());
        }
    }

    void notification(Player p, String detail) {
        this.mutedUntil.put(p.getUniqueId(), this.ticks + 60L);
        p.sendActionBar(this.glyph(p, "notification_frame", "Notice: ", false).append((Component)Component.text((String)detail)));
    }

    void cinematic(Player p, String id, String detail) {
        if (!Set.of("wasted_title", "busted_title", "city_enter", "city_exit").contains(id)) {
            throw new IllegalArgumentException("Unknown cinematic state");
        }
        String label = switch (id) {
            case "wasted_title" -> "WASTED";
            case "busted_title" -> "BUSTED";
            case "city_enter" -> "INDRAPRASTHA";
            default -> "WILDERNESS";
        };
        if (this.phone.preferences(p.getUniqueId()).reducedEffects()) {
            this.notification(p, label + " \u00b7 " + detail);
            return;
        }
        p.showTitle(Title.title((Component)this.glyph(p, id, label, true), (Component)Component.text((String)detail), (Title.Times)Title.Times.times((Duration)Duration.ofMillis(150L), (Duration)Duration.ofSeconds(2L), (Duration)Duration.ofMillis(300L))));
    }

    void dialogue(Player p, Entity speaker, String detail) {
        if (!Bukkit.isPrimaryThread()) {
            throw new IllegalStateException("Dialogue presentation runs on the server thread");
        }
        if (!speaker.getWorld().equals((Object)p.getWorld()) || speaker.getLocation().distanceSquared(p.getLocation()) > 144.0) {
            return;
        }
        Bubble old = this.bubbles.remove(p.getUniqueId());
        if (old != null) {
            old.display().remove();
        }
        if (!this.phone.services().glyphsAvailable(p) || this.phone.preferences(p.getUniqueId()).reducedEffects()) {
            p.sendMessage(Component.text((String)(speaker.getName() + ": ")).append((Component)Component.text((String)detail)));
            return;
        }
        if (this.bubbles.size() >= 32) {
            return;
        }
        TextDisplay display = (TextDisplay)speaker.getWorld().spawn(speaker.getLocation().add(0.0, speaker.getHeight() + 0.45, 0.0), TextDisplay.class);
        try {
            display.setPersistent(false);
            display.setGravity(false);
            display.setInvulnerable(true);
            display.setVisibleByDefault(false);
            display.setBillboard(Display.Billboard.CENTER);
            display.setLineWidth(220);
            display.text(this.glyph(p, "dialogue_bubble", "", false).append((Component)Component.text((String)detail)));
            p.showEntity((Plugin)this.plugin, (Entity)display);
            this.bubbles.put(p.getUniqueId(), new Bubble(display, this.ticks + 80L, this.plugin.authenticatedSession(p)));
        }
        catch (RuntimeException ex) {
            display.remove();
            throw ex;
        }
    }

    void forget(Player p) {
        this.status.remove(p);
        this.frames.remove(p.getUniqueId());
        this.sampleOffsets.remove(p.getUniqueId());
        this.city.remove(p.getUniqueId());
        this.mutedUntil.remove(p.getUniqueId());
        Bubble b = this.bubbles.remove(p.getUniqueId());
        if (b != null) {
            b.display().remove();
        }
    }

    @Override
    public void close() {
        this.status.close();
        for (Bubble b : this.bubbles.values()) {
            b.display().remove();
        }
        this.bubbles.clear();
        this.frames.clear();
        this.sampleOffsets.clear();
        this.terrain.clear();
        this.city.clear();
        this.mutedUntil.clear();
        for (MapView map : this.maps.values()) {
            for (MapRenderer r : new ArrayList<>(map.getRenderers())) {
                map.removeRenderer(r);
            }
        }
        this.maps.clear();
    }

    private record Cell(UUID world, int x, int z) {
    }

    private record Sample(Color color, long expires) {
    }

    private record Bubble(TextDisplay display, long expires, UUID session) {
    }

    private record MapFrame(long next, UUID world, boolean dashboard, PhoneStore.Preferences preferences, BufferedImage image) {
    }
}

