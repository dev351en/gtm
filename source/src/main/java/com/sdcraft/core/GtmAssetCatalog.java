package com.sdcraft.core;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.regex.Pattern;

/** Validated client item bindings. Art availability never grants an entitlement. */
public final class GtmAssetCatalog {
    public static final String PROFILE = "INDRAPRASTHA_128_V1";
    private static final String HEADER = "# gtm-asset-catalog\t1\t" + PROFILE;
    private static final Pattern ID = Pattern.compile("gtm:[a-z0-9_]+");
    private static final Pattern CATEGORY = Pattern.compile("[a-z0-9_]+");
    private static final Pattern BASE = Pattern.compile("minecraft:[a-z0-9_]+");

    public enum Source { NATIVE_128, ALIAS_128, LEGACY_COMPATIBILITY }

    public record Entry(String id, String category, String title, String baseItem,
                        Source source, String canonicalId, String kind) {
        public String key() { return id.substring("gtm:".length()); }
        public boolean legacyCompatibility() { return source == Source.LEGACY_COMPATIBILITY; }
    }

    private final Map<String, Entry> entries;

    private GtmAssetCatalog(Map<String, Entry> entries) {
        this.entries = Collections.unmodifiableMap(new LinkedHashMap<>(entries));
    }

    public static GtmAssetCatalog bundled() throws IOException {
        InputStream stream = GtmAssetCatalog.class.getResourceAsStream("/gtm-assets.tsv");
        if (stream == null) throw new IOException("Missing GTM asset catalogue");
        return read(stream);
    }

    /** Reads and closes the supplied stream, rejecting partial or ambiguous bindings. */
    public static GtmAssetCatalog read(InputStream stream) throws IOException {
        if (stream == null) throw new IOException("Missing GTM asset catalogue");
        Map<String, Entry> entries = new LinkedHashMap<>();
        try (var reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8))) {
            if (!HEADER.equals(reader.readLine())) throw new IOException("Unsupported GTM asset catalogue format");
            int lineNumber = 1;
            for (String line; (line = reader.readLine()) != null;) {
                lineNumber++;
                String[] fields = line.split("\t", -1);
                if (fields.length != 7 || !ID.matcher(fields[0]).matches()
                        || !CATEGORY.matcher(fields[1]).matches() || fields[2].isBlank()
                        || fields[2].codePoints().anyMatch(Character::isISOControl)
                        || !BASE.matcher(fields[3]).matches() || !ID.matcher(fields[5]).matches()
                        || !CATEGORY.matcher(fields[6]).matches()) {
                    throw new IOException("Invalid GTM asset catalogue row " + lineNumber);
                }
                Source source;
                try { source = Source.valueOf(fields[4]); }
                catch (IllegalArgumentException ex) {
                    throw new IOException("Invalid GTM asset provenance at row " + lineNumber, ex);
                }
                var entry = new Entry(fields[0], fields[1], fields[2], fields[3], source, fields[5], fields[6]);
                if (entries.putIfAbsent(entry.id(), entry) != null)
                    throw new IOException("Duplicate GTM asset identifier: " + entry.id());
            }
        }
        if (entries.isEmpty()) throw new IOException("Empty GTM asset catalogue");
        for (Entry entry : entries.values()) {
            Entry canonical = entries.get(entry.canonicalId());
            if (canonical == null) throw new IOException("Missing GTM canonical model: " + entry.id());
            if (entry.source() == Source.ALIAS_128) {
                if (entry.id().equals(canonical.id()) || canonical.source() != Source.NATIVE_128
                        || !entry.baseItem().equals(canonical.baseItem()))
                    throw new IOException("Invalid GTM semantic alias: " + entry.id());
            } else if (!entry.id().equals(entry.canonicalId())) {
                throw new IOException("Unexpected GTM asset reassignment: " + entry.id());
            }
        }
        return new GtmAssetCatalog(entries);
    }

    public int size() { return entries.size(); }
    public List<Entry> entries() { return List.copyOf(entries.values()); }
    public Optional<Entry> find(String id) {
        if (id == null) return Optional.empty();
        return Optional.ofNullable(entries.get(id.indexOf(':') < 0 ? "gtm:" + id : id));
    }

    /** The staff browser issues city decorations, never food, finishes, weapons or damage-state previews. */
    public List<Entry> paperModels() {
        return entries.values().stream().filter(e -> e.kind().equals("city") && e.baseItem().equals("minecraft:paper")).toList();
    }
}
