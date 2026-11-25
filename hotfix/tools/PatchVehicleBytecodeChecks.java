import java.nio.file.Path;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.jar.JarFile;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.Opcodes;

/** Build-only regression checks; requires the original verified core JAR. */
public final class PatchVehicleBytecodeChecks {
    public static void main(String[] args) throws Exception {
        if (args.length != 1) throw new IllegalArgumentException("Usage: PatchVehicleBytecodeChecks <preserved.jar>");
        byte[] original;
        try (JarFile jar = new JarFile(Path.of(args[0]).toFile())) {
            original = jar.getInputStream(jar.getJarEntry("com/sdcraft/core/GtmVehicles.class")).readAllBytes();
        }
        byte[] patched = PatchVehicleBytecode.patch(original);
        require(Arrays.equals(patched, PatchVehicleBytecode.patch(original)), "Deterministic patch output");
        Map<String, Integer> calls = new LinkedHashMap<>();
        new ClassReader(patched).accept(new ClassVisitor(Opcodes.ASM9) {
            @Override public MethodVisitor visitMethod(int access, String name, String descriptor, String signature, String[] exceptions) {
                return new MethodVisitor(Opcodes.ASM9) {
                    @Override public void visitMethodInsn(int opcode, String owner, String method, String desc, boolean itf) {
                        if (owner.equals("com/sdcraft/core/vehicle/VehicleRenderTransform")) {
                            require(opcode == Opcodes.INVOKESTATIC && !itf && method.equals("compensateItemFacing")
                                    && desc.equals("(Lorg/joml/Matrix4f;)Lorg/joml/Matrix4f;"), "Exact stack-neutral hook");
                            calls.merge(name, 1, Integer::sum);
                        }
                    }
                };
            }
        }, 0);
        require(calls.equals(Map.of("setModel", 1, "animate", 1)), "Only the intended two vehicle methods");
        byte[] damaged = original.clone();
        damaged[damaged.length - 1] ^= 1;
        rejects(damaged, "Corrupt/unknown class");
        rejects(patched, "Already patched class");
        rejects(new byte[]{0, 1, 2}, "Non-class input");
        System.out.println("Vehicle bytecode checks: deterministic, exactly two hooks, corrupt/unknown/already-patched input rejected (5 checks).");
    }

    private static void rejects(byte[] bytes, String label) throws Exception {
        try { PatchVehicleBytecode.patch(bytes); }
        catch (java.io.IOException expected) { return; }
        throw new AssertionError(label + " was accepted");
    }

    private static void require(boolean value, String label) {
        if (!value) throw new AssertionError(label);
    }
}
