import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.Map;
import java.util.TreeMap;
import java.util.jar.JarFile;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.Opcodes;

/** Exact target-only repair: never changes shooter login, tag-game login or permissions. */
public final class PatchNpcCombatBytecode {
    private static final String JAR_SHA256 = "b7c76cd3a664e1bb7e1e56fd2098f7ef0a71e921d47170ed10c4e658974715af";
    private static final String CLASS_SHA256 = "3fbb26074b5f1fd1cd6fe2936836a232f8f08347ddd80d3c83632133f3e93145";
    private static final String ENTRY = "com/sdcraft/core/GtmEquipment.class";
    private static final String CORE = "com/sdcraft/core/SDCraftCorePlugin";
    private static final String HELPER = "com/sdcraft/core/NpcCombatAccess";
    private static final Map<String, String> METHODS = Map.of(
            "shoot", "(Lorg/bukkit/entity/Player;Lorg/bukkit/inventory/ItemStack;Lcom/sdcraft/core/equipment/EquipmentCatalog$Entry;)V",
            "trace", "(Lorg/bukkit/entity/Player;Lcom/sdcraft/core/equipment/EquipmentCatalog$Entry;Lorg/bukkit/Location;Lorg/bukkit/util/Vector;JLjava/util/Map;Ljava/util/Map;)V");

    public static void main(String[] args) throws Exception {
        if (args.length != 2) throw new IllegalArgumentException("Usage: PatchNpcCombatBytecode <preserved.jar> <output-directory>");
        Path source = Path.of(args[0]);
        requireHash(Files.readAllBytes(source), JAR_SHA256, "preserved core JAR");
        byte[] original;
        try (JarFile jar = new JarFile(source.toFile())) {
            original = jar.getInputStream(jar.getJarEntry(ENTRY)).readAllBytes();
        }
        byte[] result = patch(original);
        Path destination = Path.of(args[1]).resolve(ENTRY);
        Files.createDirectories(destination.getParent());
        Files.write(destination, result);
        System.out.println("NPC combat repair: exactly two target-auth calls; SHA-256 " + sha256(result));
    }

    public static byte[] patch(byte[] original) throws Exception {
        requireHash(original, CLASS_SHA256, "GtmEquipment.class");
        ClassReader reader = new ClassReader(original);
        if (!reader.getClassName().equals("com/sdcraft/core/GtmEquipment")) throw new IOException("Wrong class identity");
        ClassWriter writer = new ClassWriter(reader, 0);
        Map<String, Integer> calls = new TreeMap<>();
        Map<String, Integer> replacements = new TreeMap<>();
        reader.accept(new ClassVisitor(Opcodes.ASM9, writer) {
            @Override public MethodVisitor visitMethod(int access, String name, String descriptor, String signature, String[] exceptions) {
                MethodVisitor delegate = super.visitMethod(access, name, descriptor, signature, exceptions);
                if (!METHODS.containsKey(name)) return delegate;
                if (!METHODS.get(name).equals(descriptor) || calls.put(name, 0) != null)
                    throw new IllegalStateException("Unexpected combat method: " + name);
                return new MethodVisitor(Opcodes.ASM9, delegate) {
                    @Override public void visitMethodInsn(int opcode, String owner, String method, String desc, boolean itf) {
                        if (owner.equals(HELPER)) throw new IllegalStateException("NPC combat correction already installed");
                        if (owner.equals(CORE) && method.equals("isAuthenticated")) {
                            if (opcode != Opcodes.INVOKEVIRTUAL || itf || !desc.equals("(Lorg/bukkit/entity/Player;)Z"))
                                throw new IllegalStateException("Unexpected auth signature");
                            int ordinal = calls.compute(name, (key, count) -> count + 1);
                            // trace's FIRST auth call is the real-player tag minigame. Preserve it.
                            if (name.equals("shoot") && ordinal == 1 || name.equals("trace") && ordinal == 2) {
                                replacements.merge(name, 1, Integer::sum);
                                super.visitMethodInsn(Opcodes.INVOKESTATIC, HELPER, "authenticatedPlayerOrAmbient",
                                        "(Lcom/sdcraft/core/SDCraftCorePlugin;Lorg/bukkit/entity/Player;)Z", false);
                                return;
                            }
                        }
                        super.visitMethodInsn(opcode, owner, method, desc, itf);
                    }
                };
            }
        }, 0);
        if (!calls.equals(Map.of("shoot", 1, "trace", 2)) || !replacements.equals(Map.of("shoot", 1, "trace", 1)))
            throw new IOException("Unexpected target auth calls: " + calls + "; replacements=" + replacements);
        // Both old and new instructions consume (core, player) and leave a boolean.
        // Existing stack-map frames and every non-target instruction remain intact.
        return writer.toByteArray();
    }

    private static String sha256(byte[] bytes) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }
    private static void requireHash(byte[] bytes, String expected, String label) throws Exception {
        if (!sha256(bytes).equals(expected)) throw new IOException("Unsupported " + label + "; refusing an unreviewed NPC combat repair");
    }
}
