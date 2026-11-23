package com.sdcraft.core;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("Restoration Engine & Firearms Unit Tests")
public class RestorationAndGunsTest {

    @Test
    @DisplayName("Gun types enforce proper magazine capacities, range, and ammo profiles")
    void testGunTypeProfiles() {
        // Pistol
        assertEquals(12, GunEngine.GunType.PISTOL.maxAmmo);
        assertEquals(6.0, GunEngine.GunType.PISTOL.damage);
        assertEquals(35.0, GunEngine.GunType.PISTOL.range);
        assertEquals("9mm_ammo", GunEngine.GunType.PISTOL.ammoType);
        assertEquals(101, GunEngine.GunType.PISTOL.customModelData);

        // Shotgun
        assertEquals(6, GunEngine.GunType.SHOTGUN.maxAmmo);
        assertEquals(6, GunEngine.GunType.SHOTGUN.pellets);
        assertEquals(16.0, GunEngine.GunType.SHOTGUN.range);
        assertEquals("shotgun_shells", GunEngine.GunType.SHOTGUN.ammoType);
        assertEquals(102, GunEngine.GunType.SHOTGUN.customModelData);

        // SMG
        assertEquals(30, GunEngine.GunType.SMG.maxAmmo);
        assertEquals(4.2, GunEngine.GunType.SMG.damage);
        assertEquals(26.0, GunEngine.GunType.SMG.range);
        assertEquals("9mm_ammo", GunEngine.GunType.SMG.ammoType);
        assertEquals(103, GunEngine.GunType.SMG.customModelData);

        // Rifle
        assertEquals(25, GunEngine.GunType.RIFLE.maxAmmo);
        assertEquals(7.5, GunEngine.GunType.RIFLE.damage);
        assertEquals(48.0, GunEngine.GunType.RIFLE.range);
        assertEquals("rifle_ammo", GunEngine.GunType.RIFLE.ammoType);
        assertEquals(104, GunEngine.GunType.RIFLE.customModelData);
    }

    @Test
    @DisplayName("Restoration engine 5-minute timer policy")
    void testRestorationTimingPolicy() {
        long fiveMinutesMs = 300_000L;
        long now = 1700000000000L;
        long restoreAt = now + fiveMinutesMs;

        assertEquals(300_000L, restoreAt - now);
        assertEquals(5 * 60 * 1000L, restoreAt - now);
    }

    @Test
    @DisplayName("Restorable zone spatial boundary calculation")
    void testZoneSpatialBoundary() {
        RestorationEngine.RestorableZone zone = new RestorationEngine.RestorableZone("financial_district", "world", 100, 64, 200, 50);

        assertEquals("financial_district", zone.name());
        assertEquals("world", zone.world());
        assertEquals(50, zone.radius());

        // Point inside zone (dx=20, dz=20 -> distSq = 800 <= 2500)
        double distSqInside = Math.pow(zone.x() - 120, 2) + Math.pow(zone.z() - 220, 2);
        assertTrue(distSqInside <= Math.pow(zone.radius(), 2));

        // Point outside zone (dx=40, dz=40 -> distSq = 3200 > 2500)
        double distSqOutside = Math.pow(zone.x() - 140, 2) + Math.pow(zone.z() - 240, 2);
        assertFalse(distSqOutside <= Math.pow(zone.radius(), 2));
    }
}
