package com.sdcraft.core;

import io.papermc.paper.scoreboard.numbers.NumberFormat;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import org.bukkit.Bukkit;
import org.bukkit.ChatColor;
import org.bukkit.entity.Player;
import org.bukkit.scoreboard.Criteria;
import org.bukkit.scoreboard.DisplaySlot;
import org.bukkit.scoreboard.Objective;
import org.bukkit.scoreboard.Scoreboard;
import org.bukkit.scoreboard.ScoreboardManager;
import org.bukkit.scoreboard.Team;

/** Compact right-side status using the supported vanilla scoreboard surface.
 * Never takes over an active external sidebar and restores the prior board. */
final class GtmPhoneStatus implements AutoCloseable {
    private final Map<UUID, Board> boards = new HashMap<>();

    boolean update(Player player, List<Component> lines) {
        ScoreboardManager manager = Bukkit.getScoreboardManager();
        if (manager == null || lines.size() > 6) return false;
        Board board = boards.get(player.getUniqueId());
        if (board != null && player.getScoreboard() != board.own()) {
            // Another plugin has taken ownership; do not fight it each tick.
            boards.remove(player.getUniqueId());
            return false;
        }
        if (board == null) {
            Scoreboard previous = player.getScoreboard();
            // Objectives may own TAB/below-name state even without a sidebar.
            // Leave that board intact instead of cloning stale external scores.
            if (!previous.getObjectives().isEmpty()) return false;
            Scoreboard own = manager.getNewScoreboard();
            for (Team original : previous.getTeams()) {
                Team copy = own.registerNewTeam(original.getName());
                copy.prefix(original.prefix());
                copy.suffix(original.suffix());
                copy.setColor(original.getColor());
                copy.setAllowFriendlyFire(original.allowFriendlyFire());
                copy.setCanSeeFriendlyInvisibles(original.canSeeFriendlyInvisibles());
                for (Team.Option option : Team.Option.values()) copy.setOption(option, original.getOption(option));
                for (String entry : original.getEntries()) copy.addEntry(entry);
            }
            Objective objective = own.registerNewObjective("gtmphone", Criteria.DUMMY,
                    Component.text("GTM · INDRAPRASTHA", NamedTextColor.GOLD));
            objective.numberFormat(NumberFormat.blank());
            objective.setDisplaySlot(DisplaySlot.SIDEBAR);
            for (int index = 0; index < 6; index++) {
                String entry = ChatColor.values()[index].toString() + ChatColor.RESET;
                Team team = own.registerNewTeam("gtmphone" + index);
                team.addEntry(entry);
                objective.getScore(entry).setScore(6 - index);
            }
            board = new Board(previous, own);
            boards.put(player.getUniqueId(), board);
            player.setScoreboard(own);
        }
        for (int index = 0; index < 6; index++) {
            board.own().getTeam("gtmphone" + index).prefix(index < lines.size() ? lines.get(index) : Component.empty());
        }
        return true;
    }

    void remove(Player player) {
        Board board = boards.remove(player.getUniqueId());
        if (board != null && player.getScoreboard() == board.own()) player.setScoreboard(board.previous());
    }

    @Override public void close() {
        for (UUID id : new ArrayList<>(boards.keySet())) {
            Player player = Bukkit.getPlayer(id);
            if (player != null) remove(player);
        }
        boards.clear();
    }

    private record Board(Scoreboard previous, Scoreboard own) {}
}
