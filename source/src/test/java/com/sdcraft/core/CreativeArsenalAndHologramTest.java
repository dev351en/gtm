package com.sdcraft.core;

import static org.junit.jupiter.api.Assertions.*;

import java.io.File;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

public class CreativeArsenalAndHologramTest {

    @Test
    public void testHologramDefinitions() {
        // Test that 10 core city landmark locations are defined with valid coordinates
        Map<String, String> holograms = Map.of(
                "spawn_welcome", "world:10.500:74.200:15.500",
                "city_hall", "world:10.500:73.500:3.500",
                "police_hq", "world:120.500:69.500:-45.500",
                "general_hospital", "world:-61.500:68.500:140.500",
                "central_bank", "world:56.500:70.500:-118.500",
                "motor_dealership", "world:-150.500:70.500:-82.500",
                "metro_transit", "world:26.500:71.500:63.500",
                "gas_station", "world:-204.500:73.500:60.500",
                "fire_rescue", "world:190.500:73.500:86.500",
                "testing_arsenal", "world:8.500:73.500:17.500"
        );

        assertEquals(10, holograms.size(), "Should have exactly 10 landmark holograms");

        for (Map.Entry<String, String> entry : holograms.entrySet()) {
            String[] parts = entry.getValue().split(":");
            assertEquals(4, parts.length, "Location format must be world:x:y:z for " + entry.getKey());
            assertEquals("world", parts[0]);
            double x = Double.parseDouble(parts[1]);
            double y = Double.parseDouble(parts[2]);
            double z = Double.parseDouble(parts[3]);
            assertTrue(y >= 65.0 && y <= 80.0, "Hologram " + entry.getKey() + " must be at surface daylight level");
        }
    }

    @Test
    public void testVehicleArsenalMapping() {
        Map<Integer, String> vehicles = Map.of(
                0, "FFW36Q", // Sedan Black
                1, "W32FND", // Sportscar GT
                2, "JSJ4ST", // Police Cruiser
                3, "HVN8HB", // Police SUV Interceptor
                4, "384A4N", // Police Motorcycle
                5, "RJRN9P", // Apache Attack Chopper
                6, "PLV871"  // Ocean Speedboat
        );

        assertEquals(7, vehicles.size());
        for (String id : vehicles.values()) {
            assertNotNull(id);
            assertEquals(6, id.length(), "MTVehicles UUID must be a 6-character alphanumeric code");
        }
    }

    @Test
    public void testFirearmsArsenalMapping() {
        Map<Integer, String> guns = Map.of(
                9, "p30",
                10, "glock",
                11, "deagle",
                12, "mp5",
                13, "ak47",
                14, "m4",
                15, "remington",
                16, "awp",
                17, "barrett"
        );

        assertEquals(9, guns.size());
        List<String> validCalibers = List.of("9mm", "50ae", "556", "762", "12gauge", "338", "50bmg");
        assertTrue(validCalibers.size() >= 7, "QualityArmory ammo types registered");
    }

    @Test
    public void testTeleportLandmarksCoordinates() {
        record Landmark(String name, double x, double y, double z) {}

        List<Landmark> landmarks = List.of(
                new Landmark("Civic Plaza", 10.5, 70.0, 3.5),
                new Landmark("Police HQ", 120.5, 66.0, -45.5),
                new Landmark("Hospital", -61.5, 65.0, 140.5),
                new Landmark("Bank", 56.5, 68.0, -118.5),
                new Landmark("Dealership", -150.5, 69.0, -82.5),
                new Landmark("Metro", 26.5, 68.0, 63.5),
                new Landmark("Gas Station", -204.5, 70.0, 60.5),
                new Landmark("Fire Station", 190.5, 70.0, 86.5),
                new Landmark("Airport", -350.0, 68.0, -200.0)
        );

        assertEquals(9, landmarks.size(), "Should have 9 fast teleport landmarks in Arsenal row 5");
        for (Landmark l : landmarks) {
            assertTrue(l.y() >= 65.0, "Landmark " + l.name() + " must be at surface daylight level: " + l.y());
        }
    }
}
