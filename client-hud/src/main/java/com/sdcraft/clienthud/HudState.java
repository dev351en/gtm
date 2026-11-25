package com.sdcraft.clienthud;

import com.google.gson.*;
import java.util.*;

/** Bounded display data from the authenticated server; never inventory authority. */
public record HudState(String session, long revision, String city, String district,
                       int wanted, String wallet, String bank, List<App> apps,
                       Vehicle vehicle, List<Marker> markers, boolean openPhone) {
    public static final int MAX_BYTES = 16_384;
    public record App(String id, String title, boolean enabled) {}
    public record Vehicle(double speed, double fuel, double body, String energyKind, int seats, int occupiedSeats) {}
    public record Marker(String id, String kind, String label, double x, double z) {}
    public static final Set<String> APP_IDS = Set.of("app_quoggle", "app_amazzo", "app_flippit", "app_arkpay",
            "app_zomatoo", "app_swiffy", "app_fashion", "app_property", "app_car_app", "app_maps",
            "app_garage", "app_bank", "app_loans", "app_taxi", "app_transport", "app_news", "app_police",
            "app_medical", "app_events", "app_missions", "app_careers", "app_contacts", "app_keys", "app_settings");

    public static HudState decode(String json) {
        if (json.getBytes(java.nio.charset.StandardCharsets.UTF_8).length > MAX_BYTES) throw new IllegalArgumentException("HUD packet too large");
        JsonObject root = JsonParser.parseString(json).getAsJsonObject();
        if (root.get("v").getAsInt() != 1) throw new IllegalArgumentException("Unsupported HUD schema");
        if (!root.has("active") || !root.get("active").getAsBoolean()) return null;
        String session = text(root, "session", 64, "");
        if (session.isBlank()) throw new IllegalArgumentException("Missing session");
        long revision = root.get("revision").getAsLong();
        if (revision < 0) throw new IllegalArgumentException("Negative revision");
        List<App> apps = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        if (root.has("apps")) for (JsonElement el : root.getAsJsonArray("apps")) {
            if (apps.size() >= 24) throw new IllegalArgumentException("Too many apps");
            JsonObject item = el.getAsJsonObject();
            String id = text(item, "id", 40, "");
            if (!APP_IDS.contains(id) || !seen.add(id)) throw new IllegalArgumentException("Unknown or duplicate app");
            apps.add(new App(id, text(item, "title", 48, id), item.has("enabled") && item.get("enabled").getAsBoolean()));
        }
        Vehicle vehicle = null;
        if (root.has("vehicle") && root.get("vehicle").isJsonObject()) {
            JsonObject v = root.getAsJsonObject("vehicle");
            vehicle = new Vehicle(number(v,"speed",-400,400,0), number(v,"fuel",0,100,0),
                    number(v,"body",0,100,0),text(v,"energyKind",16,"fuel"),
                    (int)number(v,"seats",0,100,0),(int)number(v,"occupiedSeats",0,100,0));
        }
        List<Marker> markers = new ArrayList<>();
        if (root.has("markers")) for (JsonElement el : root.getAsJsonArray("markers")) {
            if (markers.size() >= 64) throw new IllegalArgumentException("Too many markers");
            JsonObject m=el.getAsJsonObject();
            markers.add(new Marker(text(m,"id",64,""),text(m,"kind",32,"shop"),text(m,"label",64,""),
                    number(m,"x",-30_000_000,30_000_000,0),number(m,"z",-30_000_000,30_000_000,0)));
        }
        return new HudState(session, revision, text(root,"city",48,"Indraprastha"),text(root,"district",64,"City"),
                (int)number(root,"wanted",0,5,0),text(root,"wallet",32,"—"),text(root,"bank",32,"—"),
                List.copyOf(apps),vehicle,List.copyOf(markers),root.has("openPhone")&&root.get("openPhone").getAsBoolean());
    }
    static String text(JsonObject obj, String key, int maximum, String fallback) {
        if (!obj.has(key) || obj.get(key).isJsonNull()) return fallback;
        String value=obj.get(key).getAsString();
        if (value.length()>maximum || value.codePoints().anyMatch(c->Character.isISOControl(c)||c==0xA7))
            throw new IllegalArgumentException("Invalid display text: "+key);
        return value;
    }
    static double number(JsonObject obj,String key,double min,double max,double fallback) {
        double n=obj.has(key)?obj.get(key).getAsDouble():fallback;
        if (!Double.isFinite(n)||n<min||n>max) throw new IllegalArgumentException("Invalid number: "+key);
        return n;
    }
}
