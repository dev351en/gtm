package com.sdcraft.core.gtm;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Extra citizens of the surveyed public city. Legacy identities retain their original keys. */
public final class CityRoster {
    public record Citizen(String id, UUID uuid, String name, String role, int x, int y, int z) {}
    private final Map<String,Citizen> citizens;
    private final List<UUID> gang;
    private final UUID boss;

    public CityRoster(InputStream source) throws IOException {
        Objects.requireNonNull(source);
        var data = new LinkedHashMap<String,Citizen>();
        var gangIds = new ArrayList<UUID>();
        var unique = new HashSet<UUID>();
        try (var reader = new BufferedReader(new InputStreamReader(source,StandardCharsets.UTF_8))) {
            String line;
            while ((line=reader.readLine())!=null) {
                var cells=line.split("\t",-1);
                if (cells.length!=7 || !cells[0].matches("npc-[0-9]{3}") || cells[2].isBlank() || cells[3].isBlank())
                    throw new IOException("Invalid surveyed roster row");
                var entry=new Citizen(cells[0],UUID.fromString(cells[1]),cells[2],cells[3],
                    Integer.parseInt(cells[4]),Integer.parseInt(cells[5]),Integer.parseInt(cells[6]));
                if (data.putIfAbsent(entry.id(),entry)!=null || !unique.add(entry.uuid()))
                    throw new IOException("Duplicate citizen");
                if (entry.role().equals("black_lotus")) gangIds.add(entry.uuid());
            }
        }
        if (data.size()!=400 || gangIds.size()!=20 || !data.containsKey("npc-481") ||
            !gangIds.contains(data.get("npc-481").uuid())) throw new IOException("Incomplete extended roster");
        citizens=Collections.unmodifiableMap(data);
        gang=List.copyOf(gangIds);
        boss=data.get("npc-481").uuid();
    }
    public Map<String,Citizen> citizens() { return citizens; }
    public Set<UUID> prisoners(long day) { return CivicRules.prisonRotation(gang,boss,day); }
}
