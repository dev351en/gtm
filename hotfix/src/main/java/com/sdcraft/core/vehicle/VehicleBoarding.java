package com.sdcraft.core.vehicle;

import com.sdcraft.core.GtmVehicles;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.UUID;
import org.bukkit.entity.Player;

/** Maintained garage adapter; all admission decisions remain in the vehicle engine. */
public final class VehicleBoarding {
    private VehicleBoarding() {}

    /**
     * The preserved garage always asked for the driver's seat, even when another
     * key holder was driving. Use the same authenticated, proximity-checked
     * automatic seat selection as a world click or /car enter. In particular,
     * this does not unlock vehicles or bypass a managed-service reservation.
     * The last argument preserves the original call site's operand stack.
     */
    public static boolean enterFromGarage(GtmVehicles vehicles, Player player, UUID vehicle,
                                          boolean ignoredDriverPreference) {
        return Objects.requireNonNull(vehicles).command(Objects.requireNonNull(player), automaticCommand(vehicle));
    }

    static String[] automaticCommand(UUID vehicle) {
        return new String[] {"enter", Objects.requireNonNull(vehicle).toString()};
    }

    /** Report loaded seat definitions, never a capacity guessed from the model name. */
    public static List<String> garageLore(List<String> original, RoadVehicleProfile profile,
                                          OwnedRoadVehicle vehicle) {
        Objects.requireNonNull(original);
        Objects.requireNonNull(profile);
        Objects.requireNonNull(vehicle);
        var result = new ArrayList<>(original);
        int drivers = (int) profile.seats().stream().filter(RoadVehicleProfile.Seat::driver).count();
        int passengers = profile.seats().size() - drivers;
        result.add("Seats: " + profile.seats().size() + " total (" + drivers + " driver + " + passengers + " passengers)");
        if (profile.seats().isEmpty()) {
            result.add("This is a transport support, not a passenger vehicle.");
        } else {
            result.add("Click: driver if free; otherwise a free passenger seat.");
            if (passengers > 0) {
                result.add("Passenger only: /car passenger " + vehicle.id());
                result.add(vehicle.locked() ? "Guests locked out. Owner: /car lock " + vehicle.id()
                                           : "Guests may right-click the stopped vehicle to board.");
            } else {
                result.add("This model currently has no authored passenger seat.");
            }
        }
        return List.copyOf(result);
    }
}
