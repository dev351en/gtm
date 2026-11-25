package com.sdcraft.core;

import static org.junit.jupiter.api.Assertions.*;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class NpcIdentityIndexTest {
    @Test void repeatedReconciliationAdoptsOnceAndRejectsASecondPhysicalCopy() {
        var index = new NpcIdentityIndex(Set.of("ambient_017"));
        UUID original = UUID.randomUUID(), duplicate = UUID.randomUUID();
        assertTrue(index.claim("ambient_017", original));
        assertTrue(index.claim("ambient_017", original));
        assertFalse(index.claim("ambient_017", duplicate));
        assertEquals(original, index.entity("ambient_017"));
        assertNull(index.identify(duplicate));
    }

    @Test void unloadingReleasesOnlyTheExactOwnerAndAllowsLaterMaterialization() {
        var index = new NpcIdentityIndex(Set.of("ambient_017"));
        UUID original = UUID.randomUUID(), replacement = UUID.randomUUID();
        index.claim("ambient_017", original);
        assertFalse(index.release("ambient_017", replacement));
        assertEquals("ambient_017", index.identify(original));
        assertTrue(index.release("ambient_017", original));
        assertNull(index.identify(original));
        assertTrue(index.claim("ambient_017", replacement));
        assertEquals("ambient_017", index.identify(replacement));
    }

    @Test void anEntityCannotImpersonateAnotherIdentityAndUnknownNamesAreNotAuthority() {
        var index = new NpcIdentityIndex(Set.of("ambient_017", "nisha_bhat"));
        UUID npc = UUID.randomUUID(), stranger = UUID.randomUUID();
        assertTrue(index.claim("ambient_017", npc));
        assertFalse(index.claim("nisha_bhat", npc));
        assertFalse(index.claim("someone_with_NPC_metadata", stranger));
        assertNull(index.identify(stranger));
        assertNull(index.entity("nisha_bhat"));
    }
}
