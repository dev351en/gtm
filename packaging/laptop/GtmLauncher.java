package com.sdcraft.launcher;

import com.sun.net.httpserver.HttpServer;
import java.io.*;
import java.net.*;
import java.nio.channels.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.*;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.zip.*;

/** Local-only launcher. It never accesses Daytona, installs plugins or changes player data. */
public final class GtmLauncher {
    private final Path root;
    private final Properties config = new Properties();
    private final Properties server = new Properties();
    private final BufferedReader consoleInput = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
    private Process paper;
    private HttpServer packServer;
    private ExecutorService packWorkers;

    GtmLauncher(Path root) throws IOException {
        this.root = root.toRealPath();
        read(config, this.root.resolve("launcher/launcher.properties"));
        read(server, this.root.resolve("server.properties"));
    }

    private static void read(Properties props, Path path) throws IOException {
        try (Reader reader = Files.newBufferedReader(path, StandardCharsets.UTF_8)) { props.load(reader); }
    }

    private Path local(String key) throws IOException {
        String value = config.getProperty(key);
        if (value == null || value.isBlank()) throw new IOException("Missing launcher setting: " + key);
        Path path = root.resolve(value).normalize();
        if (!path.startsWith(root) || !Files.isRegularFile(path) || Files.isSymbolicLink(path))
            throw new IOException("Missing or unsafe bundle file: " + key);
        if (!path.toRealPath().startsWith(root)) throw new IOException("Bundle path escaped through a symlink");
        return path;
    }

    private static String sha256(Path file) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        try (InputStream in = Files.newInputStream(file)) {
            byte[] buffer = new byte[1024 * 1024];
            int n; while ((n = in.read(buffer)) >= 0) md.update(buffer, 0, n);
        }
        return HexFormat.of().formatHex(md.digest());
    }

    private static void rejectPointer(Path path) throws IOException {
        try (InputStream in = Files.newInputStream(path)) {
            String prefix = new String(in.readNBytes(80), StandardCharsets.US_ASCII);
            if (prefix.startsWith("version https://git-lfs.github.com/spec/v1"))
                throw new IOException("Unresolved Git LFS pointer: " + path.getFileName());
        }
    }

    private void verifyIntegrity() throws Exception {
        Set<String> recorded = new HashSet<>();
        for (String line : Files.readAllLines(root.resolve("launcher/integrity.sha256"), StandardCharsets.UTF_8)) {
            if (line.isBlank() || line.startsWith("#")) continue;
            if (!line.matches("[0-9a-f]{64}  .+")) throw new IOException("Malformed bundle integrity manifest");
            String name = line.substring(66);
            Path path = root.resolve(name).normalize();
            if (!path.startsWith(root) || !Files.isRegularFile(path) || Files.isSymbolicLink(path)
                    || !path.toRealPath().startsWith(root)) throw new IOException("Unsafe integrity path");
            rejectPointer(path);
            if (!sha256(path).equals(line.substring(0, 64))) throw new IOException("Bundle checksum mismatch: " + name);
            recorded.add(name.replace('\\', '/'));
        }
        try (var files = Files.list(root.resolve("plugins"))) {
            for (Path p : files.filter(p -> p.getFileName().toString().endsWith(".jar")).toList()) {
                if (!recorded.contains("plugins/" + p.getFileName()))
                    throw new IOException("Unrecorded plugin JAR; rebuild the verified bundle: " + p.getFileName());
            }
        }
        if (!recorded.contains(config.getProperty("paper.jar")) || !recorded.contains(config.getProperty("resource.pack")))
            throw new IOException("Paper and resource pack must be in the integrity manifest");
    }

    private static int port(String text) throws IOException {
        try { int value = Integer.parseInt(text); if (value > 0 && value <= 65535) return value; }
        catch (NumberFormatException ignored) { }
        throw new IOException("Invalid TCP port");
    }

    private static void checkPort(String host, int port) throws IOException {
        try (ServerSocket socket = new ServerSocket()) {
            socket.setReuseAddress(false);
            socket.bind(new InetSocketAddress(host.isBlank() ? "0.0.0.0" : host, port));
        } catch (IOException ex) { throw new IOException("Port " + port + " is already in use or cannot bind; stop the other instance."); }
    }

    private static String yamlScalar(Path path, String section, String key) throws IOException {
        boolean active = false;
        for (String line : Files.readAllLines(path, StandardCharsets.UTF_8)) {
            if (line.isBlank() || line.stripLeading().startsWith("#")) continue;
            if (!Character.isWhitespace(line.charAt(0))) { active = line.strip().equals(section + ":"); continue; }
            String prefix = "  " + key + ":";
            if (active && line.startsWith(prefix)) {
                String value = line.substring(prefix.length()).split("#", 2)[0].strip();
                if (value.length() >= 2 && ((value.startsWith("\"") && value.endsWith("\"")) || (value.startsWith("'") && value.endsWith("'")))) value = value.substring(1, value.length() - 1);
                return value;
            }
        }
        return null;
    }

    private static long heapBytes(String heap) throws IOException {
        if (!heap.matches("[1-9][0-9]*[MG]")) throw new IOException("max.heap must be a positive number with M or G suffix");
        return Math.multiplyExact(Long.parseLong(heap.substring(0, heap.length() - 1)), heap.endsWith("G") ? 1073741824L : 1048576L);
    }

    private void preflight() throws Exception {
        if (Runtime.version().feature() != 25) throw new IOException("This verified profile requires Java 25. Use the bundled runtime or JAVA_HOME.");
        verifyIntegrity();
        Path paperJar = local("paper.jar"), pack = local("resource.pack");
        try (ZipFile z = new ZipFile(paperJar.toFile())) {
            if (z.getEntry("META-INF/MANIFEST.MF") == null) throw new IOException("Paper JAR has no manifest");
        }
        try (ZipFile z = new ZipFile(pack.toFile())) {
            if (z.getEntry("pack.mcmeta") == null) throw new IOException("Client pack lacks pack.mcmeta");
        }
        String worldName = server.getProperty("level-name", "world");
        Path world = root.resolve(worldName).normalize();
        if (!world.startsWith(root) || !Files.isRegularFile(world.resolve("level.dat")) || Files.isSymbolicLink(world)
                || Files.isSymbolicLink(world.resolve("level.dat")) || !world.toRealPath().startsWith(root))
            throw new IOException("Expected city world is missing; refusing to generate a replacement world");
        rejectPointer(world.resolve("level.dat"));
        boolean hasRegions = false;
        for (Path folder : List.of(world.resolve("region"), world.resolve("dimensions/minecraft/overworld/region"))) {
            if (!Files.isDirectory(folder)) continue;
            if (Files.isSymbolicLink(folder) || !folder.toRealPath().startsWith(root)) throw new IOException("World region path escaped the local bundle");
            try (var regions = Files.list(folder)) {
                hasRegions |= regions.anyMatch(p -> p.getFileName().toString().endsWith(".mca") && p.toFile().length() >= 8192);
            }
        }
        if (!hasRegions) throw new IOException("City world contains no valid-size region files");
        Path worldLock = world.resolve("session.lock");
        if (Files.isRegularFile(worldLock)) {
            try (FileChannel channel = FileChannel.open(worldLock, StandardOpenOption.WRITE)) {
                FileLock lock = channel.tryLock();
                if (lock == null) throw new IOException("City world is locked by a running Minecraft process");
                lock.release();
            }
        }
        String expectedMode = config.getProperty("expected.online.mode");
        if (!Objects.equals(expectedMode, server.getProperty("online-mode", "true")))
            throw new IOException("Authentication mode changed. Review UUID/account migration before rebuilding this bundle.");
        if (!server.getProperty("enable-rcon", "false").equals("false"))
            throw new IOException("RCON is disabled in this local profile; review network exposure separately");
        String host = server.getProperty("server-ip", "127.0.0.1");
        if (!host.equals("127.0.0.1") && !config.getProperty("allow.network", "false").equals("true"))
            throw new IOException("This profile is local-only. Network exposure requires an explicit reviewed profile.");
        int mcPort = port(server.getProperty("server-port", "25565"));
        int packPort = port(config.getProperty("pack.port", "25566"));
        if (mcPort == packPort) throw new IOException("Minecraft and pack HTTP server need different ports");
        checkPort(host, mcPort);
        checkPort(config.getProperty("pack.bind", "127.0.0.1"), packPort);
        if (config.getProperty("bedrock.enabled", "false").equals("true")) {
            Path geyser = local("bedrock.config");
            int bedrock = port(config.getProperty("bedrock.port", "19132"));
            if (!"127.0.0.1".equals(yamlScalar(geyser, "bedrock", "address")) || !String.valueOf(bedrock).equals(yamlScalar(geyser, "bedrock", "port")))
                throw new IOException("Geyser bind/port changed from the reviewed local profile");
            if (bedrock == mcPort || bedrock == packPort) throw new IOException("Bedrock requires its own TCP/UDP port");
            checkPort("127.0.0.1", bedrock);
            try (DatagramSocket socket = new DatagramSocket(null)) {
                socket.setReuseAddress(false); socket.bind(new InetSocketAddress("127.0.0.1", bedrock));
            } catch (IOException ex) { throw new IOException("Bedrock UDP port is in use or unavailable"); }
        }
        String expectedUrl = "http://" + config.getProperty("pack.client.host", "127.0.0.1") + ":" + packPort + "/gtm-pack.zip";
        if (!server.getProperty("resource-pack", "").equals(expectedUrl)) throw new IOException("Resource-pack URL differs from the bundled local pack server");
        if (!server.getProperty("resource-pack-sha1", "").equals(config.getProperty("pack.sha1"))) throw new IOException("Resource-pack SHA-1 mismatch in server.properties");
        long minimumFree = Long.parseLong(config.getProperty("minimum.free.bytes", "2147483648"));
        if (Files.getFileStore(root).getUsableSpace() < minimumFree) throw new IOException("Insufficient free disk space for server saves and first-boot libraries");
        long heap = heapBytes(config.getProperty("max.heap", "3G"));
        if (java.lang.management.ManagementFactory.getOperatingSystemMXBean() instanceof com.sun.management.OperatingSystemMXBean os) {
            if (os.getTotalMemorySize() < heap + 2L * 1024 * 1024 * 1024)
                throw new IOException("Heap leaves less than 2 GiB for the OS/client. Reduce max.heap in launcher.properties.");
        }
        System.out.println("Preflight passed: Java 25, pinned files, city world, authentication policy, disk and ports.");
        System.out.println("Profile: " + config.getProperty("profile.name") + ". External AI remains optional/off.");
    }

    private boolean eula(boolean accept, boolean checkOnly) throws IOException {
        Properties eula = new Properties();
        Path path = root.resolve("eula.txt");
        if (Files.isRegularFile(path)) read(eula, path);
        if ("true".equalsIgnoreCase(eula.getProperty("eula"))) return true;
        System.out.println("Minecraft EULA: https://www.minecraft.net/en-us/eula");
        if (checkOnly) { System.out.println("First-start owner EULA acceptance is still required."); return false; }
        if (!accept) {
            System.out.println("Read the EULA. To accept for this local installation, type I ACCEPT; anything else cancels.");
            String line = consoleInput.readLine();
            accept = "I ACCEPT".equals(line);
        }
        if (accept) Files.writeString(path, "# Accepted explicitly by this installation's operator on " + Instant.now() + "\neula=true\n", StandardCharsets.UTF_8);
        return accept;
    }

    private void rotatePreviousLog() throws IOException {
        Path current = root.resolve("logs/latest.log");
        if (!Files.isRegularFile(current)) return;
        Path history = root.resolve("launcher/log-history");
        Files.createDirectories(history);
        String date = DateTimeFormatter.ofPattern("uuuuMMdd-HHmmss-SSS").withZone(ZoneOffset.UTC).format(Instant.now());
        Files.copy(current, history.resolve("previous-" + date + ".log"));
        try (var files = Files.list(history)) {
            var own = files.filter(p -> p.getFileName().toString().matches("previous-[0-9-]+\\.log"))
                    .sorted(Comparator.comparing(p -> p.getFileName().toString(), Comparator.reverseOrder())).toList();
            for (int i = 10; i < own.size(); i++) Files.delete(own.get(i));
        }
    }

    private void startPackServer() throws IOException {
        Path pack = local("resource.pack");
        packServer = HttpServer.create(new InetSocketAddress(config.getProperty("pack.bind", "127.0.0.1"), port(config.getProperty("pack.port"))), 8);
        packWorkers = Executors.newFixedThreadPool(2, r -> { Thread t = new Thread(r, "gtm-pack-download"); t.setDaemon(true); return t; });
        packServer.setExecutor(packWorkers);
        packServer.createContext("/", exchange -> {
            try {
                String method = exchange.getRequestMethod();
                if (!exchange.getRequestURI().getPath().equals("/gtm-pack.zip")) { exchange.sendResponseHeaders(404, -1); return; }
                if (!method.equals("GET") && !method.equals("HEAD")) { exchange.sendResponseHeaders(405, -1); return; }
                exchange.getResponseHeaders().set("Content-Type", "application/zip");
                exchange.getResponseHeaders().set("Cache-Control", "private, max-age=3600");
                exchange.getResponseHeaders().set("Content-Length", String.valueOf(Files.size(pack)));
                exchange.sendResponseHeaders(200, method.equals("HEAD") ? -1 : Files.size(pack));
                if (method.equals("GET")) try (OutputStream out = exchange.getResponseBody()) { Files.copy(pack, out); }
            } finally { exchange.close(); }
        });
        packServer.start();
    }

    private synchronized void command(String line) throws IOException {
        if (paper != null && paper.isAlive()) {
            paper.getOutputStream().write((line + "\n").getBytes(StandardCharsets.UTF_8));
            paper.getOutputStream().flush();
        }
    }

    private void stop() {
        if (paper != null && paper.isAlive()) {
            System.out.println("Requesting a clean Minecraft save and stop...");
            try { command("stop"); if (!paper.waitFor(30, TimeUnit.SECONDS)) System.err.println("Server is still saving; do not delete its world or kill it while writes continue."); }
            catch (IOException | InterruptedException ex) { System.err.println("Could not confirm graceful server shutdown."); }
        }
        if (packServer != null) packServer.stop(0);
        if (packWorkers != null) packWorkers.shutdownNow();
    }

    private int run(boolean checkOnly, boolean acceptEula) throws Exception {
        Files.createDirectories(root.resolve("launcher"));
        try (FileChannel channel = FileChannel.open(root.resolve("launcher/.running.lock"), StandardOpenOption.CREATE, StandardOpenOption.WRITE)) {
            FileLock lock = channel.tryLock();
            if (lock == null) throw new IOException("Another GTM launcher owns this folder");
            try (lock) {
                preflight();
                if (!eula(acceptEula, checkOnly)) return 2;
                if (checkOnly) { System.out.println("Check complete. No server started."); return 0; }
                rotatePreviousLog();
                startPackServer();
                String java = Path.of(System.getProperty("java.home"), "bin", System.getProperty("os.name").startsWith("Windows") ? "java.exe" : "java").toString();
                paper = new ProcessBuilder(java, "-Xms256M", "-Xmx" + config.getProperty("max.heap", "3G"), "-jar", local("paper.jar").toString(), "--nogui")
                        .directory(root.toFile()).redirectErrorStream(true).start();
                Thread hook = new Thread(this::stop, "gtm-clean-stop");
                Runtime.getRuntime().addShutdownHook(hook);
                Thread input = new Thread(() -> {
                    try {
                        String line; while ((line = consoleInput.readLine()) != null) command(line);
                    } catch (IOException ignored) { }
                }, "gtm-console-input");
                input.setDaemon(true); input.start();
                System.out.println("Starting local Paper. Wait for the actual Done message; use stop for a clean shutdown.");
                boolean ready = false;
                try (BufferedReader output = paper.inputReader(StandardCharsets.UTF_8)) {
                    String line;
                    while ((line = output.readLine()) != null) {
                        System.out.println(line);
                        if (!ready && line.contains("Done (") && line.contains("For help")) {
                            ready = true;
                            System.out.println("Paper startup completed. Java client address: 127.0.0.1:" + server.getProperty("server-port", "25565"));
                            System.out.println("A successful boot is not a certification of all gameplay or Bedrock features.");
                        }
                    }
                }
                int exit = paper.waitFor();
                Runtime.getRuntime().removeShutdownHook(hook);
                stop();
                if (!ready) System.err.println("Paper exited before its ready message. Read logs/latest.log; no readiness claim was made.");
                return exit == 0 && !ready ? 3 : exit;
            }
        } finally { stop(); }
    }

    public static void main(String[] args) {
        try {
            Set<String> options = Set.of(args);
            if (!Set.of("--check", "--accept-eula").containsAll(options)) throw new IOException("Usage: Start-GTM [--check] [--accept-eula]");
            int exit = new GtmLauncher(Path.of(".")).run(options.contains("--check"), options.contains("--accept-eula"));
            System.exit(exit);
        } catch (Exception ex) {
            System.err.println("GTM startup stopped: " + ex.getMessage());
            System.err.println("No replacement world or authentication migration was performed.");
            System.exit(1);
        }
    }
}
