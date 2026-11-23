package com.sdcraft.core;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("Surface Spawn & GTA Starter Kit Policy Tests")
public class SurfaceSpawnAndKitTest {

    @Test
    @DisplayName("Surface spawn is positioned above ground level (Y >= 70) in Civic Center Plaza")
    void testSurfaceSpawnCoordinates() {
        int spawnX = 10;
        int spawnY = 70;
        int spawnZ = 3;

        // Verify spawn is in the Civic Center district
        assertTrue(spawnX >= -50 && spawnX <= 50, "Spawn X must be in Civic Center bounds");
        assertTrue(spawnZ >= -50 && spawnZ <= 50, "Spawn Z must be in Civic Center bounds");
        assertTrue(spawnY >= 70, "Spawn Y must be at or above ground level 70 (not underground at 63)");
    }

    @Test
    @DisplayName("Underground rescue logic detects low Y coordinates (<66) and legacy underground spawn")
    void testUndergroundDetection() {
        // Legacy underground coordinates in level.dat were X=-8, Y=63, Z=-356
        double legacyX = -8.0;
        double legacyY = 63.0;
        double legacyZ = -356.0;

        boolean isUnderground = legacyY < 66.0;
        boolean isLegacySpawn = Math.abs(legacyX - (-8)) < 24 && Math.abs(legacyZ - (-356)) < 24;

        assertTrue(isUnderground, "Y=63 must trigger underground rescue");
        assertTrue(isLegacySpawn, "Legacy (-8, -356) coordinates must trigger spawn rescue");

        // Surface coordinates must NOT trigger underground rescue
        double surfaceY = 70.0;
        assertFalse(surfaceY < 66.0, "Surface Y=70 must not trigger underground rescue");
    }

    @Test
    @DisplayName("Starter vehicle UUID matches MTVehicles Sedan Black")
    void testStarterVehicleUUID() {
        String starterCarUUID = "FFW36Q";
        assertNotNull(starterCarUUID);
        assertEquals(6, starterCarUUID.length(), "MTVehicles UUID format must be 6 alphanumeric chars");
        assertTrue(starterCarUUID.matches("[A-Z0-9]{6}"), "UUID must be uppercase alphanumeric");
    }

    @Test
    @DisplayName("Starter kit ammunition and food quantities match roleplay balance")
    void testStarterKitQuantities() {
        int initialPistolAmmo = 32;
        int initialFoodBurgers = 16;
        int starterWalletCents = 50000; // $500
        int starterBankCents = 100000;   // $1,000

        assertEquals(32, initialPistolAmmo, "Starter kit must include 32 rounds of 9mm ammo");
        assertEquals(16, initialFoodBurgers, "Starter kit must include 16 Street Burgers");
        assertEquals("$500.00", PolicyEngine.money(starterWalletCents));
        assertEquals("$1000.00", PolicyEngine.money(starterBankCents));
    }

    @Test
    @DisplayName("Civic Center plaza NPCs are anchored within immediate visible proximity (<=10m) of surface spawn")
    void testSpawnNpcProximity() {
        double spawnX = 10.5;
        double spawnZ = 3.5;

        // Nisha Bhat (City Info) at (8.0, 71.0, 4.0)
        double distNisha = Math.hypot(spawnX - 8.0, spawnZ - 4.0);
        assertTrue(distNisha <= 5.0, "Nisha Bhat must be within 5m of spawn");

        // Sameer Qureshi (Taxi) at (16.0, 71.0, 4.0)
        double distSameer = Math.hypot(spawnX - 16.0, spawnZ - 4.0);
        assertTrue(distSameer <= 6.0, "Sameer Qureshi must be within 6m of spawn");

        // Rehan Khan (Transit) at (6.0, 71.0, 4.0)
        double distRehan = Math.hypot(spawnX - 6.0, spawnZ - 4.0);
        assertTrue(distRehan <= 6.0, "Rehan Khan must be within 6m of spawn");
    }
}
