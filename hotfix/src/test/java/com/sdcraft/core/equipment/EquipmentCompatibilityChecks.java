package com.sdcraft.core.equipment;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.net.URLClassLoader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.jar.JarFile;

/** Compare the reconstructed parser/model rules with the exact preserved runtime. */
public final class EquipmentCompatibilityChecks {
    private static int checks;

    public static void main(String[] args) throws Exception {
        if (args.length != 1) throw new IllegalArgumentException("Pass preserved 1.0.3 JAR path");
        Path originalJar = Path.of(args[0]);
        byte[] catalogue;
        try (JarFile jar = new JarFile(originalJar.toFile())) {
            catalogue = jar.getInputStream(jar.getJarEntry("equipment/catalog.tsv")).readAllBytes();
        }
        try (URLClassLoader loader = new URLClassLoader(new java.net.URL[]{originalJar.toUri().toURL()}, ClassLoader.getPlatformClassLoader())) {
            Class<?> originalType = loader.loadClass("com.sdcraft.core.equipment.EquipmentCatalog");
            Object original = originalType.getMethod("read", java.io.InputStream.class).invoke(null, new ByteArrayInputStream(catalogue));
            List<?> originalEntries = (List<?>) originalType.getMethod("all").invoke(original);
            EquipmentCatalog repaired = EquipmentCatalog.read(new ByteArrayInputStream(catalogue));
            Map<String, String> expected = new LinkedHashMap<>();
            for (Object entry : originalEntries) {
                String id = (String) entry.getClass().getMethod("id").invoke(entry);
                expected.put(id, entry.toString());
                var current = repaired.find(id).orElseThrow();
                check(current.toString().equals(entry.toString()), "Record changed: " + id);
                for (String method : List.of("ranged", "pellets", "reloadMillis", "instruction", "key")) {
                    Object before = entry.getClass().getMethod(method).invoke(entry);
                    Object after = current.getClass().getMethod(method).invoke(current);
                    check(before.equals(after), "Behavior changed: " + id + "." + method);
                }
            }
            check(expected.size() == 133 && repaired.all().size() == 133, "All 133 identities retained");
            long guns = repaired.all().stream().filter(EquipmentCatalog.Entry::ranged).count();
            check(guns > 0 && guns <= 45, "Functional firearms fit first equipment page");
            check(repaired.all().subList(0, (int) guns).stream().allMatch(EquipmentCatalog.Entry::ranged), "Actual firearms shown before light tag and furnishings");
            check(repaired.all().getFirst().id().equals("gtm:kavach_9"), "Native service pistol discoverable first");
            check(repaired.find("gtm:nonexistent").isEmpty(), "Unknown IDs remain absent");
            String text = new String(catalogue, StandardCharsets.UTF_8);
            String first = text.lines().filter(s -> !s.isBlank() && !s.startsWith("#")).findFirst().orElseThrow();
            for (String bad : List.of(
                    text.replace("INDRAPRASTHA_128_V1", "unrecognized"),
                    text + first + "\n",
                    text.replace(first + "\n", ""),
                    text.replace(first, first.replace("\tTAG\t", "\tINVALID\t")),
                    text.replace(first, first + "\textra"),
                    text.replace("\tRANGED\t\t25000\t6\t4.0\t30\t12\t9mm_ammo", "\tRANGED\t\t25000\t6\tNaN\t30\t12\t9mm_ammo"),
                    text.replace("\tRANGED\t\t25000\t6\t4.0\t30\t12\t9mm_ammo", "\tRANGED\t\t25000\t6\t4.0\t30\t0\t9mm_ammo")
            )) {
                check(!bad.equals(text), "Invalid fixture really changes the catalogue");
                byte[] bytes = bad.getBytes(StandardCharsets.UTF_8);
                check(rejected(originalType, bytes), "Original parser rejects malformed catalogue");
                try {
                    EquipmentCatalog.read(new ByteArrayInputStream(bytes));
                    throw new AssertionError("Repaired parser accepted malformed catalogue");
                } catch (IOException expectedFailure) { checks++; }
            }
            check(rejected(originalType, null), "Original rejects missing stream");
            try {
                EquipmentCatalog.read(null);
                throw new AssertionError("Repaired accepted missing stream");
            } catch (IOException expectedFailure) { checks++; }
        }
        System.out.println("Equipment compatibility: " + checks + " checks passed against preserved runtime");
    }

    private static boolean rejected(Class<?> type, byte[] bytes) throws Exception {
        try {
            type.getMethod("read", java.io.InputStream.class).invoke(null,
                    bytes == null ? null : new ByteArrayInputStream(bytes));
            return false;
        } catch (InvocationTargetException ex) {
            return ex.getCause() instanceof IOException;
        }
    }

    private static void check(boolean result, String message) {
        if (!result) throw new AssertionError(message);
        checks++;
    }
}
