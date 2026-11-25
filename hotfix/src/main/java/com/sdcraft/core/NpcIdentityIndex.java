package com.sdcraft.core;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** A private ownership index. An entity's public name or NPC metadata is not authority. */
final class NpcIdentityIndex {
    private final Set<String> known;
    private final Map<String, UUID> byIdentity = new HashMap<>();
    private final Map<UUID, String> byEntity = new HashMap<>();

    NpcIdentityIndex(Set<String> known) { this.known = Set.copyOf(known); }

    boolean claim(String id, UUID entity) {
        if (!known.contains(id) || entity == null) return false;
        UUID prior = byIdentity.get(id);
        String owner = byEntity.get(entity);
        if (prior != null && !prior.equals(entity) || owner != null && !owner.equals(id)) return false;
        byIdentity.put(id, entity);
        byEntity.put(entity, id);
        return true;
    }

    String identify(UUID entity) { return byEntity.get(entity); }
    UUID entity(String id) { return byIdentity.get(id); }

    boolean release(String id, UUID entity) {
        if (!byIdentity.remove(id, entity)) return false;
        byEntity.remove(entity, id);
        return true;
    }
}
