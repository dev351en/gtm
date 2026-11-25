package com.sdcraft.core;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class GtmAssetCatalogTest {
    private static final String HEADER = "# gtm-asset-catalog\t1\tINDRAPRASTHA_128_V1\n";

    private GtmAssetCatalog parse(String rows) throws IOException {
        return GtmAssetCatalog.read(new ByteArrayInputStream((HEADER + rows).getBytes(StandardCharsets.UTF_8)));
    }

    @Test
    void everyLegacyCityIdentifierRetainsItsSemanticNameAndCategory() throws Exception {
        GtmAssetCatalog catalog = GtmAssetCatalog.bundled();
        try (var stream = getClass().getResourceAsStream("/gtm-city-models.tsv")) {
            assertNotNull(stream);
            String[] lines = new String(stream.readAllBytes(), StandardCharsets.UTF_8).split("\\R");
            assertEquals(479, lines.length);
            for (String line : lines) {
                String[] old = line.split("\t", -1);
                var item = catalog.find(old[0]).orElseThrow();
                assertEquals("gtm:" + old[0], item.id());
                assertEquals(old[1], item.category(), old[0]);
                assertEquals(old[2], item.title(), old[0]);
                assertEquals("minecraft:paper", item.baseItem());
                assertEquals(item.id(), item.canonicalId());
            }
        }
        assertEquals(GtmAssetCatalog.Source.LEGACY_COMPATIBILITY,
                catalog.find("bar_stool_irani").orElseThrow().source());
        assertEquals(GtmAssetCatalog.Source.NATIVE_128,
                catalog.find("sedan_city").orElseThrow().source());
        assertNotEquals(catalog.find("bar_stool_irani").orElseThrow().id(),
                catalog.find("coffee_table_teak").orElseThrow().id());
    }

    @Test
    void foodAliasesAreExactAndAllActualFinishEntitlementsStayOneBased() throws Exception {
        GtmAssetCatalog catalog = GtmAssetCatalog.bundled();
        var chai = catalog.find("chai").orElseThrow();
        assertEquals("gtm:food_chai", chai.canonicalId());
        assertEquals(GtmAssetCatalog.Source.ALIAS_128, chai.source());
        assertEquals("minecraft:bread", chai.baseItem());
        for (String family : new String[] {"pistol", "shotgun", "smg", "rifle"}) {
            assertTrue(catalog.find(family + "_00").isEmpty());
            for (int number = 1; number <= 75; number++) {
                String id = String.format(java.util.Locale.ROOT, "%s_%02d", family, number);
                var entry = catalog.find(id).orElseThrow();
                assertEquals("gtm:" + id, entry.canonicalId());
                assertEquals(GtmAssetCatalog.Source.LEGACY_COMPATIBILITY, entry.source());
                assertEquals("finish", entry.kind());
            }
        }
        assertTrue(catalog.find("kavach_9_gold_leaf").isPresent());
        assertEquals(30, catalog.entries().stream().filter(e -> e.source() == GtmAssetCatalog.Source.ALIAS_128).count());
    }

    @Test
    void staffPaperCatalogueNeverIssuesOwnedFoodOrRuntimeWeaponFinishes() throws Exception {
        GtmAssetCatalog catalog = GtmAssetCatalog.bundled();
        assertEquals(1683, catalog.size());
        assertEquals(787, catalog.paperModels().size());
        assertTrue(catalog.paperModels().stream().allMatch(e -> e.baseItem().equals("minecraft:paper")));
        assertTrue(catalog.paperModels().stream().allMatch(e -> e.kind().equals("city")));
        assertThrows(UnsupportedOperationException.class, () -> catalog.entries().clear());
        assertTrue(catalog.find(null).isEmpty());
        assertTrue(catalog.find("../missing").isEmpty());
    }

    @Test
    void duplicateAndReassignedIdentifiersAreRejected() {
        String valid = "gtm:a\tfurniture\tChair\tminecraft:paper\tNATIVE_128\tgtm:a\tcity\n";
        assertThrows(IOException.class, () -> parse(valid + valid));
        assertThrows(IOException.class, () -> parse(valid +
                "gtm:b\tfurniture\tTable\tminecraft:paper\tNATIVE_128\tgtm:a\tcity\n"));
    }

    @Test
    void brokenAliasesCannotFallBackToAnUnrelatedItem() {
        String target = "gtm:food_a\tfood\tMeal\tminecraft:bread\tNATIVE_128\tgtm:food_a\tfood\n";
        assertThrows(IOException.class, () -> parse(
                "gtm:a\tfood\tMeal\tminecraft:bread\tALIAS_128\tgtm:missing\tfood\n"));
        assertThrows(IOException.class, () -> parse(target +
                "gtm:a\tfood\tMeal\tminecraft:paper\tALIAS_128\tgtm:food_a\tfood\n"));
        assertThrows(IOException.class, () -> parse(
                "gtm:a\tfood\tMeal\tminecraft:bread\tALIAS_128\tgtm:a\tfood\n"));
    }

    @Test
    void corruptOrUnsupportedCataloguesFailClosed() {
        assertThrows(IOException.class, () -> GtmAssetCatalog.read(null));
        assertThrows(IOException.class, () -> GtmAssetCatalog.read(new ByteArrayInputStream("other".getBytes(StandardCharsets.UTF_8))));
        assertThrows(IOException.class, () -> parse(""));
        assertThrows(IOException.class, () -> parse("gtm:a\tfurniture\tChair\tminecraft:paper\tUNKNOWN\tgtm:a\tcity\n"));
        assertThrows(IOException.class, () -> parse("gtm:../a\tfurniture\tChair\tminecraft:paper\tNATIVE_128\tgtm:a\tcity\n"));
    }
}
