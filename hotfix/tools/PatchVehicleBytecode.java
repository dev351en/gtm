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

/**
 * Build-only, fail-closed repair of two verified call sites in the preserved
 * owner-supplied core. Every other instruction/class is retained. This does not
 * claim to recover the original missing source and never changes the input JAR.
 */
public final class PatchVehicleBytecode {
    private static final String JAR_SHA256 = "b7c76cd3a664e1bb7e1e56fd2098f7ef0a71e921d47170ed10c4e658974715af";
    private static final String CLASS_SHA256 = "dd621a2d4f8b5962c890f45559d84fe1adaed76957ff6441c66d8c777b24b4c6";
    private static final String ENTRY = "com/sdcraft/core/GtmVehicles.class";
    private static final String HELPER = "com/sdcraft/core/vehicle/VehicleRenderTransform";
    private static final Map<String, String> METHODS = Map.of(
        "setModel", "(Lorg/bukkit/entity/ItemDisplay;Lcom/sdcraft/core/vehicle/RoadVehicleProfile$Render;)V",
        "animate", "(Lcom/sdcraft/core/GtmVehicles$Active;)V"
    );

    public static void main(String[] args) throws Exception {
        if (args.length != 2) throw new IllegalArgumentException("Usage: PatchVehicleBytecode <preserved.jar> <output-directory>");
        Path source = Path.of(args[0]);
        requireHash(Files.readAllBytes(source), JAR_SHA256, "preserved core JAR");
        byte[] original;
        try (JarFile jar = new JarFile(source.toFile())) {
            var entry = jar.getJarEntry(ENTRY);
            if (entry == null) throw new IOException("Missing preserved vehicle adapter");
            original = jar.getInputStream(entry).readAllBytes();
        }
        byte[] patched = patch(original);
        Path destination = Path.of(args[1]).resolve(ENTRY);
        Files.createDirectories(destination.getParent());
        Files.write(destination, patched);
        System.out.println("Vehicle render repair: exactly two verified call sites; input retained; output SHA-256 " + sha256(patched));
    }

    public static byte[] patch(byte[] original) throws Exception {
        requireHash(original, CLASS_SHA256, "GtmVehicles.class");
        ClassReader reader = new ClassReader(original);
        if (!reader.getClassName().equals("com/sdcraft/core/GtmVehicles")) throw new IOException("Wrong class identity");
        // Inserting (Matrix4f)->Matrix4f preserves stack height/types and existing
        // stack-map frames. No ClassLoader or Paper implementation is required.
        ClassWriter writer = new ClassWriter(reader, 0);
        Map<String, Integer> matches = new TreeMap<>();
        reader.accept(new ClassVisitor(Opcodes.ASM9, writer) {
            @Override public MethodVisitor visitMethod(int access, String name, String descriptor, String signature, String[] exceptions) {
                MethodVisitor delegate = super.visitMethod(access, name, descriptor, signature, exceptions);
                if (!METHODS.containsKey(name)) return delegate;
                if (!METHODS.get(name).equals(descriptor)) throw new IllegalStateException("Vehicle method descriptor changed: " + name);
                if (matches.put(name, 0) != null) throw new IllegalStateException("Ambiguous vehicle method: " + name);
                return new MethodVisitor(Opcodes.ASM9, delegate) {
                    @Override public void visitMethodInsn(int opcode, String owner, String method, String desc, boolean isInterface) {
                        if (owner.equals(HELPER)) throw new IllegalStateException("Vehicle render correction is already installed");
                        if (method.equals("setTransformationMatrix")) {
                            if (opcode != Opcodes.INVOKEINTERFACE || !isInterface || !owner.equals("org/bukkit/entity/ItemDisplay") || !desc.equals("(Lorg/joml/Matrix4f;)V")) {
                                throw new IllegalStateException("Unexpected vehicle matrix call in " + name);
                            }
                            matches.compute(name, (key, count) -> count + 1);
                            super.visitMethodInsn(Opcodes.INVOKESTATIC, HELPER, "compensateItemFacing", "(Lorg/joml/Matrix4f;)Lorg/joml/Matrix4f;", false);
                        }
                        super.visitMethodInsn(opcode, owner, method, desc, isInterface);
                    }
                };
            }
        }, 0);
        if (!matches.equals(Map.of("animate", 1, "setModel", 1))) throw new IOException("Expected exactly one matrix call in each vehicle render method, got " + matches);
        return writer.toByteArray();
    }

    private static String sha256(byte[] bytes) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }

    private static void requireHash(byte[] bytes, String expected, String label) throws Exception {
        if (!sha256(bytes).equals(expected)) throw new IOException("Unsupported " + label + "; refusing an unreviewed bytecode repair");
    }
}
