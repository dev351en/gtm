/* Reconstructed from preserved 1.0.3 bytecode; record validation retained. Only menu order changes. */
package com.sdcraft.core.equipment;

import java.io.IOException;
import java.io.InputStream;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Comparator;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;

public final class EquipmentCatalog {
    private final Map<String, Entry> entries;

    private EquipmentCatalog(Map<String, Entry> entries) {
        this.entries = Collections.unmodifiableMap(new LinkedHashMap<String, Entry>(entries));
    }

    public static EquipmentCatalog bundled() throws IOException {
        return EquipmentCatalog.read(EquipmentCatalog.class.getResourceAsStream("/equipment/catalog.tsv"));
    }

    public static EquipmentCatalog read(InputStream stream) throws IOException {
        if (stream == null) throw new IOException("Missing equipment bindings");
        Map<String, Entry> entries = new LinkedHashMap<>();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8))) {
            if (!"# gtm-equipment-catalog\t1\tINDRAPRASTHA_128_V1".equals(reader.readLine()))
                throw new IOException("Unknown equipment format");
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.isBlank() || line.startsWith("#")) continue;
                try {
                    String[] columns = line.split("\t", -1);
                    if (columns.length != 10) throw new IllegalArgumentException("Columns");
                    Entry entry = new Entry(columns[0], columns[1], Action.valueOf(columns[2]), columns[3],
                            Long.parseLong(columns[4]), Integer.parseInt(columns[5]), Double.parseDouble(columns[6]),
                            Double.parseDouble(columns[7]), Integer.parseInt(columns[8]), columns[9]);
                    if (entries.putIfAbsent(entry.id(), entry) != null)
                        throw new IllegalArgumentException("Duplicate equipment");
                } catch (RuntimeException failure) {
                    throw new IOException("Invalid equipment record", failure);
                }
            }
        }
        if (entries.size() != 133) throw new IOException("Expected all 133 equipment/weapon/hero records");
        return new EquipmentCatalog(entries);
    }

    public List<Entry> all() {
        return this.entries.values().stream().sorted(Comparator.comparingInt(EquipmentCatalog::menuPriority)).toList();
    }

    // Stable sorting keeps the authored order within a category. The actual firearms
    // must be visible on page one instead of behind thirty light-tag toys.
    private static int menuPriority(Entry entry) {
        if (entry.ranged()) return 0;
        return switch (entry.action()) {
            case MELEE -> 1;
            case ARMOR, SHIELD -> 2;
            case MEDKIT -> 3;
            case UTILITY, MUSIC, EFFECT -> 4;
            case TAG -> 5;
            case PLACEABLE -> 6;
            default -> 4;
        };
    }

    public Optional<Entry> find(String id) {
        return Optional.ofNullable(this.entries.get(id));
    }

    public record Entry(String id, String title, Action action, String service, long cents, int cooldownTicks, double power, double range, int capacity, String ammo) {
        public Entry {
            Objects.requireNonNull(action);
            if (id == null || !id.matches("gtm:[a-z0-9_]+") || title == null || title.isBlank() || title.length() > 100 || service == null || !service.matches("[a-z_]*") || cents <= 0L || cents > 1000000L || cooldownTicks < 0 || cooldownTicks > 1200 || !Double.isFinite(power) || power < 0.0 || power > 20.0 || !Double.isFinite(range) || range < 0.0 || range > 80.0 || capacity < 0 || capacity > 64 || ammo == null || !Set.of("", "9mm_ammo", "shotgun_shells", "rifle_ammo").contains(ammo)) {
                throw new IllegalArgumentException("Invalid equipment profile");
            }
            if (Entry.ranged(action) && (capacity < 1 || ammo.isBlank() || range <= 0.0 || power <= 0.0 || cooldownTicks < 1)) {
                throw new IllegalArgumentException("Incomplete game weapon");
            }
        }

        public boolean ranged() {
            return Entry.ranged(this.action);
        }

        private static boolean ranged(Action action) {
            return action == Action.RANGED || action == Action.SCATTER || action == Action.PRECISION || action == Action.PULSE;
        }

        public String key() {
            return this.id.substring(4);
        }

        public int pellets() {
            return this.action == Action.SCATTER ? 5 : 1;
        }

        public long reloadMillis() {
            return this.action == Action.SCATTER ? 2200L : (this.action == Action.PRECISION || this.action == Action.PULSE ? 2600L : 1600L);
        }

        public String instruction() {
            return switch (this.action) {
                case RANGED, SCATTER, PRECISION, PULSE -> "Right-click: fire; sneak + right-click: reload";
                case MELEE -> "Left-click a target to strike; attacks have a cooldown";
                case TAG -> "Right-click: play light tag; sneak + right-click: recharge";
                case SHIELD -> "Right-click: raise a short directional guard";
                case ARMOR -> "Right-click: equip protection; remove it in your inventory";
                case MUSIC -> "Right-click: play; sneak + right-click: change pattern";
                case EFFECT -> "Right-click: use one visual effect charge";
                case MEDKIT -> "Right-click: use one kit to restore game health";
                case UTILITY -> "Right-click: open the linked account service";
                case PLACEABLE -> "Buy and place through your owned furnishings collection";
            };
        }
    }

    public static enum Action {
        RANGED,
        SCATTER,
        PRECISION,
        PULSE,
        MELEE,
        TAG,
        SHIELD,
        ARMOR,
        MUSIC,
        EFFECT,
        UTILITY,
        MEDKIT,
        PLACEABLE;

    }
}

