package com.sdcraft.core;

import static org.junit.jupiter.api.Assertions.*;
import com.sdcraft.core.equipment.EquipmentCatalog;
import org.junit.jupiter.api.Test;
import java.util.List;

class WeaponMenuCompatibilityTest {
    @Test void allArsenalShortcutsResolveToDistinctFunctionalModelsWithMatchingNativeAmmo() throws Exception {
        var catalog = EquipmentCatalog.bundled();
        var legacy = List.of("p30", "glock", "deagle", "mp5", "ak47", "m4", "remington", "awp", "barrett");
        var nativeIds = legacy.stream().map(CreativeArsenalManager::nativeWeaponId).toList();
        assertEquals(9, nativeIds.stream().distinct().count());
        for (String id : nativeIds) {
            var entry = catalog.find(id).orElseThrow();
            assertTrue(entry.ranged(), id);
            assertTrue(entry.capacity() > 0, id);
            assertEquals(entry.ammo(), GunEngine.canonicalAmmo(entry.ammo()), id);
        }
    }

    @Test void oldArsenalAmmoLabelsResolveToTheActualNativeReloadGroups() {
        assertEquals("shotgun_shells", GunEngine.canonicalAmmo("shotgun_ammo"));
        assertEquals("rifle_ammo", GunEngine.canonicalAmmo("556_ammo"));
        assertEquals("rifle_ammo", GunEngine.canonicalAmmo("762_ammo"));
        assertEquals("rifle_ammo", GunEngine.canonicalAmmo("sniper_ammo"));
        assertEquals("rifle_ammo", GunEngine.canonicalAmmo("50bmg_ammo"));
        assertEquals("9mm_ammo", GunEngine.canonicalAmmo("50cal_ammo"));
        assertThrows(IllegalArgumentException.class, () -> GunEngine.canonicalAmmo("invalid"));
        assertThrows(IllegalArgumentException.class, () -> GunEngine.canonicalAmmo(null));
    }
}
