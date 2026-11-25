package com.sdcraft.core;

import com.sdcraft.core.gtm.AuthenticationState;
import com.sdcraft.core.gtm.AuthenticationStore;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.Consumer;
import java.util.function.Predicate;
import org.bukkit.*;
import org.bukkit.command.*;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.block.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.hanging.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.event.vehicle.VehicleEnterEvent;
import org.bukkit.projectiles.ProjectileSource;
import org.bukkit.scheduler.BukkitTask;

/**
 * Built-in offline authentication. Mojang online mode or the installed Floodgate API
 * can verify a connection; an offline name, IP address or permission never does.
 */
final class GtmAuthentication implements Listener, CommandExecutor, TabCompleter, AutoCloseable {
    private enum Action { LOGIN, REGISTER, CHANGE, ENROLL }
    private record Approval(AuthenticationState.Connection connection, long expires) {}
    private final SDCraftCorePlugin plugin;
    private final Predicate<UUID> existingAccount;
    private final Consumer<Player> activated, deactivated;
    private final AuthenticationStore store;
    private final AuthenticationState state = new AuthenticationState();
    private final Map<UUID, AuthenticationState.Connection> connections = new ConcurrentHashMap<>();
    private final Map<UUID, AuthenticationState.Connection> pending = new ConcurrentHashMap<>();
    private final Map<UUID, Approval> approvals = new HashMap<>();
    private final Map<UUID, Long> prompts = new HashMap<>();
    private final ThreadPoolExecutor workers;
    private final BukkitTask timer;
    private final long loginTimeout, sessionTimeout;
    private final Set<String> reservedNames;
    private volatile boolean closing;

    GtmAuthentication(SDCraftCorePlugin plugin, Predicate<UUID> existingAccount,
                      Consumer<Player> activated, Consumer<Player> deactivated) throws IOException {
        this.plugin = plugin; this.existingAccount = existingAccount;
        this.activated = activated; this.deactivated = deactivated;
        for (String provider : List.of("SimpleLogin", "AuthMe", "LoginSecurity")) {
            if (Bukkit.getPluginManager().isPluginEnabled(provider))
                throw new IOException("Existing login provider " + provider + " needs an explicit credential migration");
        }
        store = new AuthenticationStore(plugin.getDataFolder().toPath().resolve("authentication"));
        loginTimeout = bounded("login-timeout-seconds", 120, 30, 600) * 1000L;
        sessionTimeout = bounded("session-timeout-seconds", 43_200, 300, 86_400) * 1000L;
        reservedNames = new HashSet<>();
        for (String name : plugin.getConfig().getStringList("authentication.reserved-names"))
            reservedNames.add(AuthenticationStore.canonicalName(name));
        int threads = bounded("max-concurrent-hashes", 2, 1, 2);
        workers = new ThreadPoolExecutor(threads, threads, 30, TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(bounded("max-pending-hashes", 16, 1, 32)), runnable -> {
                Thread thread = new Thread(runnable, "GTM-authentication");
                thread.setDaemon(true); return thread;
            }, new ThreadPoolExecutor.AbortPolicy());
        workers.allowCoreThreadTimeOut(true);
        timer = Bukkit.getScheduler().runTaskTimer(plugin, this::tick, 20L, 20L);
    }

    private int bounded(String key, int fallback, int min, int max) {
        return Math.max(min, Math.min(max, plugin.getConfig().getInt("authentication." + key, fallback)));
    }
    private boolean npc(Player p) { return p.hasMetadata("NPC") || plugin.isManagedNpc(p); }
    boolean authenticated(Player p) {
        return !closing && state.authenticated(p.getUniqueId(), System.currentTimeMillis());
    }
    UUID session(Player p) {
        var connection = connections.get(p.getUniqueId());
        return connection != null && authenticated(p) ? connection.nonce() : null;
    }
    private boolean blocked(Player p) { return !npc(p) && !authenticated(p); }
    void begin(Player p) {
        if (npc(p) || closing) return;
        end(p);
        var connection = state.begin(p.getUniqueId(), System.currentTimeMillis(), loginTimeout);
        connections.put(p.getUniqueId(), connection);
        p.closeInventory();
        p.leaveVehicle();
        if (!store.nameAvailable(p.getUniqueId(), p.getName())) {
            p.kickPlayer("This name is bound to another account identity. Ask the server owner to review migration.");
            return;
        }
        if (verifiedIdentity(p)) authenticate(p, connection);
        else prompt(p);
    }
    void end(Player p) {
        UUID id = p.getUniqueId();
        var connection = connections.remove(id);
        if (connection != null) pending.remove(id, connection);
        approvals.remove(id); prompts.remove(id); state.end(id);
    }
    private boolean verifiedIdentity(Player p) {
        if (Bukkit.getOnlineMode()) return true;
        if (!plugin.getConfig().getBoolean("authentication.trust-floodgate", true)
                || !Bukkit.getPluginManager().isPluginEnabled("floodgate")) return false;
        try {
            Class<?> api = Class.forName("org.geysermc.floodgate.api.FloodgateApi");
            Object instance = api.getMethod("getInstance").invoke(null);
            return Boolean.TRUE.equals(api.getMethod("isFloodgatePlayer", UUID.class).invoke(instance, p.getUniqueId()))
                && api.getMethod("getPlayer", UUID.class).invoke(instance, p.getUniqueId()) != null;
        } catch (ReflectiveOperationException | LinkageError ex) {
            return false; // Missing/broken bridge requires a password; never trusts a name prefix.
        }
    }
    private boolean protectedEnrollment(Player p) {
        if (existingAccount.test(p.getUniqueId()) || p.isOp() || p.hasPermission("sdcraft.admin")) return true;
        String name = AuthenticationStore.canonicalName(p.getName());
        if (reservedNames.contains(name)) return true;
        return Bukkit.getOperators().stream().map(OfflinePlayer::getName).filter(Objects::nonNull)
            .anyMatch(operator -> AuthenticationStore.canonicalName(operator).equals(name));
    }
    private boolean approved(Player p, AuthenticationState.Connection connection) {
        Approval approval = approvals.get(p.getUniqueId());
        return approval != null && approval.connection().equals(connection)
            && approval.expires() > System.currentTimeMillis();
    }
    void prompt(Player p) {
        if (npc(p) || authenticated(p)) return;
        long now = System.currentTimeMillis();
        if (now - prompts.getOrDefault(p.getUniqueId(), 0L) < 3000) return;
        prompts.put(p.getUniqueId(), now);
        var connection = connections.get(p.getUniqueId());
        if (connection != null && approved(p, connection))
            p.sendMessage("§e[GTM] Console enrollment approved for this connection. Use /register <passphrase> <repeat>.");
        else if (store.registered(p.getUniqueId()))
            p.sendMessage("§e[GTM] Log in with /login <passphrase> before playing.");
        else if (protectedEnrollment(p))
            p.sendMessage("§e[GTM] Existing or protected account: the owner must enroll this connection from the local console.");
        else
            p.sendMessage("§e[GTM] Create your account with /register <passphrase> <repeat>. Use 15–128 characters; quote passphrases containing spaces.");
    }
    private void authenticate(Player p, AuthenticationState.Connection connection) {
        if (!p.isOnline() || !state.authenticate(connection, System.currentTimeMillis(), sessionTimeout)) return;
        state.authenticatedAttempt(p.getUniqueId());
        approvals.remove(p.getUniqueId()); prompts.remove(p.getUniqueId());
        p.sendMessage("§a[GTM] Account authenticated.");
        activated.accept(p);
    }
    private void lock(Player p) {
        lock(p, loginTimeout);
    }
    private void lock(Player p, long timeout) {
        deactivated.accept(p);
        end(p);
        var connection = state.begin(p.getUniqueId(), System.currentTimeMillis(), timeout);
        connections.put(p.getUniqueId(), connection);
        p.closeInventory(); p.leaveVehicle();
        prompt(p);
    }
    private void tick() {
        if (closing) return;
        long now = System.currentTimeMillis();
        for (Player p : Bukkit.getOnlinePlayers()) {
            if (npc(p)) continue;
            if (!state.expired(p.getUniqueId(), now)) continue;
            deactivated.accept(p);
            end(p);
            p.kickPlayer("Authentication session expired. Reconnect and authenticate again.");
        }
        approvals.entrySet().removeIf(e -> e.getValue().expires() <= now);
    }

    /** Cancels and redacts credential commands before Bukkit dispatch. Disable server command logging too. */
    @EventHandler(priority = EventPriority.LOWEST)
    public void command(PlayerCommandPreprocessEvent event) {
        Player player = event.getPlayer();
        if (npc(player)) return;
        String message = event.getMessage();
        int separator = message.indexOf(' ');
        String label = (separator < 0 ? message.substring(1) : message.substring(1, separator)).toLowerCase(Locale.ROOT);
        if (label.startsWith("sdcraftcore:")) label = label.substring("sdcraftcore:".length());
        String canonical = switch (label) {
            case "register", "reg" -> "register";
            case "login", "l" -> "login";
            case "logout" -> "logout";
            case "changepassword", "changepass" -> "changepassword";
            default -> "";
        };
        if (!canonical.isEmpty()) {
            event.setCancelled(true);
            event.setMessage("/" + canonical + " <redacted>");
            try { playerCommand(player, canonical, AuthenticationState.arguments(separator < 0 ? "" : message.substring(separator + 1))); }
            catch (IllegalArgumentException ex) { player.sendMessage("§c[GTM] " + ex.getMessage()); }
        } else if (blocked(player)) { event.setCancelled(true); prompt(player); }
        // Authenticated // and WorldEdit commands pass through unchanged.
    }

    @Override public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (command.getName().equalsIgnoreCase("gtmauth")) { console(sender, args); return true; }
        if (sender instanceof Player player) {
            try { playerCommand(player, command.getName().toLowerCase(Locale.ROOT), List.of(args)); }
            catch (IllegalArgumentException ex) { player.sendMessage("§c[GTM] " + ex.getMessage()); }
        } else sender.sendMessage("Players enter credentials in their own authenticated connection; use gtmauth for console enrollment.");
        return true;
    }

    private void console(CommandSender sender, String[] args) {
        if (!(sender instanceof ConsoleCommandSender)) {
            sender.sendMessage("Authentication enrollment is restricted to the local server console.");
            return;
        }
        if (args.length == 1 && args[0].equalsIgnoreCase("status")) {
            sender.sendMessage("GTM authentication: " + store.size() + " enrolled identities; "
                + connections.size() + " connected sessions; " + pending.size() + " pending checks.");
            return;
        }
        if (args.length != 2 || !args[0].equalsIgnoreCase("enroll")) {
            sender.sendMessage("gtmauth status | gtmauth enroll <online-player>");
            return;
        }
        Player player = Bukkit.getPlayerExact(args[1]);
        if (player == null || npc(player)) { sender.sendMessage("The player must be connected; verify their identity out of band first."); return; }
        if (verifiedIdentity(player)) { sender.sendMessage("This connection already has a verified platform identity; local password enrollment is unnecessary."); return; }
        lock(player, 600_000);
        var connection = connections.get(player.getUniqueId());
        approvals.put(player.getUniqueId(), new Approval(connection, System.currentTimeMillis() + 600_000));
        prompts.remove(player.getUniqueId());
        prompt(player);
        plugin.getLogger().info("Local console approved credential enrollment for UUID " + player.getUniqueId());
        sender.sendMessage("Enrollment authorized for that connected session for ten minutes. No UUID, balance or inventory was changed.");
    }

    private void playerCommand(Player p, String command, List<String> args) {
        if (closing || npc(p)) return;
        var connection = connections.get(p.getUniqueId());
        if (connection == null || !state.current(connection)) { p.kickPlayer("Reconnect to initialize a protected session."); return; }
        if (command.equals("logout")) {
            if (!args.isEmpty()) throw new IllegalArgumentException("Use /logout");
            lock(p);
            if (verifiedIdentity(p)) p.kickPlayer("Logged out. Reconnect to verify your platform identity.");
            return;
        }
        if (pending.containsKey(p.getUniqueId())) { p.sendMessage("§e[GTM] A credential check is already running."); return; }
        Action action;
        if (command.equals("login")) {
            if (args.size() != 1) throw new IllegalArgumentException("Use /login <passphrase>; quote spaces");
            if (authenticated(p)) { p.sendMessage("§a[GTM] This session is already authenticated."); return; }
            if (approved(p, connection)) { prompt(p); return; }
            action = Action.LOGIN;
        } else if (command.equals("register")) {
            if (args.size() != 2 || !args.get(0).equals(args.get(1)))
                throw new IllegalArgumentException("Use /register <passphrase> <repeat> with matching values; quote spaces");
            if (authenticated(p)) { p.sendMessage("§e[GTM] Use /changepassword for an enrolled offline account."); return; }
            if (approved(p, connection)) action = Action.ENROLL;
            else {
                if (store.registered(p.getUniqueId())) { prompt(p); return; }
                if (protectedEnrollment(p)) { prompt(p); return; }
                action = Action.REGISTER;
            }
        } else if (command.equals("changepassword")) {
            if (!authenticated(p)) { prompt(p); return; }
            if (!store.registered(p.getUniqueId())) { p.sendMessage("§e[GTM] This identity uses platform authentication and has no local password."); return; }
            if (args.size() != 3 || !args.get(1).equals(args.get(2)))
                throw new IllegalArgumentException("Use /changepassword <old> <new> <repeat>; quote spaces");
            action = Action.CHANGE;
        } else return;
        String address = p.getAddress() == null || p.getAddress().getAddress() == null
            ? "unknown" : p.getAddress().getAddress().getHostAddress();
        if (!state.acquireAttempt(p.getUniqueId(), address, System.currentTimeMillis())) {
            p.sendMessage("§c[GTM] Too many authentication attempts. Wait five minutes before retrying."); return;
        }
        char[] first = args.get(0).toCharArray();
        char[] second = action == Action.CHANGE ? args.get(1).toCharArray() : new char[0];
        HashJob job = new HashJob(p, connection, action, first, second);
        pending.put(p.getUniqueId(), connection);
        try { workers.execute(job); }
        catch (RejectedExecutionException ex) {
            pending.remove(p.getUniqueId(), connection); job.clear();
            p.sendMessage("§e[GTM] Authentication is busy. Try again shortly.");
        }
    }

    private final class HashJob implements Runnable {
        private final Player player;
        private final UUID id;
        private final String name;
        private final AuthenticationState.Connection connection;
        private final Action action;
        private final char[] first, second;
        HashJob(Player player, AuthenticationState.Connection connection, Action action, char[] first, char[] second) {
            this.player = player; this.id = player.getUniqueId(); this.name = player.getName();
            this.connection = connection; this.action = action; this.first = first; this.second = second;
        }
        void clear() { Arrays.fill(first, '\0'); Arrays.fill(second, '\0'); }
        @Override public void run() {
            AuthenticationStore.Proof result = null;
            String failure = null;
            try {
                result = switch (action) {
                    case LOGIN -> store.verify(id, first);
                    case REGISTER -> store.register(id, name, first);
                    case CHANGE -> store.changePassword(id, first, second);
                    case ENROLL -> store.enrollAfterConsoleApproval(id, name, first);
                };
            } catch (IllegalArgumentException ex) { failure = ex.getMessage(); }
            catch (IOException | RuntimeException ex) {
                failure = "Credential operation could not be committed. Contact the server owner.";
                plugin.getLogger().warning("Authentication operation failed for UUID " + id + ": " + ex.getClass().getSimpleName());
            } finally { clear(); }
            AuthenticationStore.Proof proof = result;
            String message = failure;
            if (closing) return;
            try {
                Bukkit.getScheduler().runTask(plugin, () -> {
                    pending.remove(id, connection);
                    if (closing || !player.isOnline() || !state.current(connection)) return;
                    if (message != null) { player.sendMessage("§c[GTM] " + message); return; }
                    if (proof == null || !store.current(proof)) {
                        player.sendMessage("§c[GTM] Credentials were not accepted."); return;
                    }
                    if (action == Action.CHANGE) {
                        state.authenticatedAttempt(id);
                        player.sendMessage("§a[GTM] Password changed and saved.");
                    } else authenticate(player, connection);
                });
            } catch (org.bukkit.plugin.IllegalPluginAccessException ignored) {
                // Plugin shutdown invalidates every connection; no late activation is allowed.
            }
        }
    }

    @Override public List<String> onTabComplete(CommandSender sender, Command command, String label, String[] args) {
        return List.of(); // Never suggest, echo or retain credential arguments.
    }

    @EventHandler(priority = EventPriority.LOWEST)
    public void chat(AsyncPlayerChatEvent e) {
        // This event is asynchronous: read only the concurrent session map, not NPC/Bukkit collections.
        if (!authenticated(e.getPlayer())) e.setCancelled(true);
    }
    @EventHandler(priority = EventPriority.LOWEST)
    public void move(PlayerMoveEvent e) {
        if (!blocked(e.getPlayer()) || e.getTo() == null) return;
        Location stay = e.getFrom().clone(); stay.setYaw(e.getTo().getYaw()); stay.setPitch(e.getTo().getPitch());
        e.setTo(stay);
    }
    @EventHandler(priority = EventPriority.LOWEST)
    public void teleport(PlayerTeleportEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void portal(PlayerPortalEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void interact(PlayerInteractEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void entityInteract(PlayerInteractEntityEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void preciseEntityInteract(PlayerInteractAtEntityEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void armorStand(PlayerArmorStandManipulateEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void swap(PlayerSwapHandItemsEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void held(PlayerItemHeldEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void drop(PlayerDropItemEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void pickup(EntityPickupItemEvent e) { if (e.getEntity() instanceof Player p && blocked(p)) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void arrow(PlayerPickupArrowEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void inventory(InventoryClickEvent e) { if (e.getWhoClicked() instanceof Player p && blocked(p)) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void drag(InventoryDragEvent e) { if (e.getWhoClicked() instanceof Player p && blocked(p)) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void open(InventoryOpenEvent e) { if (e.getPlayer() instanceof Player p && blocked(p)) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void place(BlockPlaceEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void breakBlock(BlockBreakEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void bucketEmpty(PlayerBucketEmptyEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void bucketFill(PlayerBucketFillEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void consume(PlayerItemConsumeEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void editBook(PlayerEditBookEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void sign(SignChangeEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void fish(PlayerFishEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void bed(PlayerBedEnterEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void vehicle(VehicleEnterEvent e) { if (e.getEntered() instanceof Player p && blocked(p)) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void mount(EntityMountEvent e) { if (e.getEntity() instanceof Player p && blocked(p)) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void shear(PlayerShearEntityEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void leash(PlayerLeashEntityEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void unleash(PlayerUnleashEntityEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void hangingPlace(HangingPlaceEvent e) { if (e.getPlayer() != null && blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void hangingBreak(HangingBreakByEntityEvent e) { if (e.getRemover() instanceof Player p && blocked(p)) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void mend(PlayerItemMendEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void flight(PlayerToggleFlightEvent e) { if (blocked(e.getPlayer())) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void commands(PlayerCommandSendEvent e) {
        if (blocked(e.getPlayer())) e.getCommands().removeIf(c ->
            !Set.of("register", "reg", "login", "l", "logout", "changepassword", "changepass").contains(c));
    }
    @EventHandler(priority = EventPriority.LOWEST)
    public void damage(EntityDamageEvent e) {
        if (e.getEntity() instanceof Player p && blocked(p)) { e.setCancelled(true); return; }
        if (e instanceof EntityDamageByEntityEvent hit) {
            Entity source = hit.getDamager();
            if (source instanceof Player p && blocked(p)) e.setCancelled(true);
            if (source instanceof Projectile projectile && projectile.getShooter() instanceof Player p && blocked(p)) e.setCancelled(true);
        }
    }
    @EventHandler(priority = EventPriority.LOWEST)
    public void shoot(EntityShootBowEvent e) { if (e.getEntity() instanceof Player p && blocked(p)) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void projectile(ProjectileLaunchEvent e) {
        ProjectileSource source = e.getEntity().getShooter();
        if (source instanceof Player p && blocked(p)) e.setCancelled(true);
    }
    @EventHandler(priority = EventPriority.LOWEST)
    public void hunger(FoodLevelChangeEvent e) { if (e.getEntity() instanceof Player p && blocked(p)) e.setCancelled(true); }
    @EventHandler(priority = EventPriority.LOWEST)
    public void target(EntityTargetLivingEntityEvent e) { if (e.getTarget() instanceof Player p && blocked(p)) e.setCancelled(true); }

    @Override public void close() {
        closing = true; timer.cancel();
        for (Runnable task : workers.shutdownNow()) if (task instanceof HashJob job) job.clear();
        try {
            if (!workers.awaitTermination(5, TimeUnit.SECONDS))
                plugin.getLogger().warning("Authentication workers are still terminating; no late session activation is allowed.");
        } catch (InterruptedException ex) { Thread.currentThread().interrupt(); }
        state.clear(); connections.clear(); pending.clear(); approvals.clear(); prompts.clear();
    }
}
