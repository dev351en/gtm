import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.jar.JarFile;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.Opcodes;

/** Fail-closed provenance plus exact instruction conservation checks. */
public final class PatchNpcCombatBytecodeChecks {
    public static void main(String[] args) throws Exception {
        byte[] original;
        try (JarFile jar = new JarFile(Path.of(args[0]).toFile())) {
            original = jar.getInputStream(jar.getJarEntry("com/sdcraft/core/GtmEquipment.class")).readAllBytes();
        }
        byte[] patched = PatchNpcCombatBytecode.patch(original);
        require(Arrays.equals(patched, PatchNpcCombatBytecode.patch(original)), "Deterministic output");
        Map<String, List<String>> before = methodCalls(original), after = methodCalls(patched);
        int changed = 0;
        for (String key : before.keySet()) {
            List<String> a = before.get(key), b = after.get(key);
            require(a.size() == b.size(), "Same invocation count in " + key);
            for (int i = 0; i < a.size(); i++) if (!a.get(i).equals(b.get(i))) {
                changed++;
                require(key.startsWith("shoot(") || key.startsWith("trace("), "Only combat target methods changed");
                require(a.get(i).equals("182 com/sdcraft/core/SDCraftCorePlugin.isAuthenticated(Lorg/bukkit/entity/Player;)Z false"), "Original auth target");
                require(b.get(i).equals("184 com/sdcraft/core/NpcCombatAccess.authenticatedPlayerOrAmbient(Lcom/sdcraft/core/SDCraftCorePlugin;Lorg/bukkit/entity/Player;)Z false"), "Exact stack-compatible hook");
            }
        }
        require(changed == 2, "Exactly two calls replaced");
        String trace = before.keySet().stream().filter(k -> k.startsWith("trace(")).findFirst().orElseThrow();
        require(after.get(trace).stream().filter(s -> s.contains("SDCraftCorePlugin.isAuthenticated")).count() == 1,
                "Real-player tag game authentication retained");
        byte[] corrupt = original.clone(); corrupt[corrupt.length - 1] ^= 1;
        rejects(corrupt); rejects(patched); rejects(new byte[] {1,2,3});
        System.out.println("NPC combat bytecode checks passed: deterministic; exact2 target replacements; other calls and tag auth preserved; corrupt/already-patched/non-class inputs rejected.");
    }

    private static Map<String, List<String>> methodCalls(byte[] bytes) {
        Map<String, List<String>> calls = new LinkedHashMap<>();
        new ClassReader(bytes).accept(new ClassVisitor(Opcodes.ASM9) {
            @Override public MethodVisitor visitMethod(int access, String name, String descriptor, String signature, String[] exceptions) {
                List<String> list = new ArrayList<>(); calls.put(name + descriptor, list);
                return new MethodVisitor(Opcodes.ASM9) {
                    @Override public void visitMethodInsn(int opcode, String owner, String method, String desc, boolean itf) {
                        list.add(opcode + " " + owner + "." + method + desc + " " + itf);
                    }
                };
            }
        }, 0);
        return calls;
    }
    private static void rejects(byte[] bytes) throws Exception {
        try { PatchNpcCombatBytecode.patch(bytes); }
        catch (java.io.IOException expected) { return; }
        throw new AssertionError("Unsupported bytes were accepted");
    }
    private static void require(boolean value, String message) { if (!value) throw new AssertionError(message); }
}
