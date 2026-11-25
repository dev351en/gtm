package com.sdcraft.core.vehicle;

import static org.junit.jupiter.api.Assertions.*;
import com.sdcraft.core.gtm.VehicleState;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.joml.Matrix4f;
import org.joml.Vector3f;

class VehicleBoardingTest {
    private static RoadVehicleCatalog CATALOG;
    private static final UUID OWNER = UUID.fromString("10000000-0000-0000-0000-000000000001");
    private static final UUID GUEST = UUID.fromString("20000000-0000-0000-0000-000000000001");

    @BeforeAll static void loadCatalogue() throws Exception { CATALOG = RoadVehicleCatalog.bundled(); }

    private static OwnedRoadVehicle record(String model, boolean locked, Set<UUID> keys) {
        return new OwnedRoadVehicle(UUID.fromString("30000000-0000-0000-0000-000000000001"), OWNER, model,
                UUID.fromString("40000000-0000-0000-0000-000000000001"), new VehicleGeometry.Pose(0, 74, 0, 0),
                new VehicleState(20, 20, 100, 0), locked, keys);
    }

    @Test void garageChoosesTheExistingAutomaticAdmissionCommandWithExactIdentity() {
        var vehicle = record("gtm:rickshaw_traditional", true, Set.of());
        assertArrayEquals(new String[] {"enter", vehicle.id().toString()}, VehicleBoarding.automaticCommand(vehicle.id()));
        assertThrows(NullPointerException.class, () -> VehicleBoarding.automaticCommand(null));
    }

    @Test void capacityTextComesFromEveryLoadedProfileIncludingUnpoweredCarriages() {
        for (var profile : CATALOG.all()) {
            var original = List.of("Original identity", "Energy/condition", "Parked location");
            var lore = VehicleBoarding.garageLore(original, profile, record(profile.id(), false, Set.of()));
            int drivers = (int) profile.seats().stream().filter(RoadVehicleProfile.Seat::driver).count();
            assertEquals(original, lore.subList(0, original.size()));
            assertEquals("Seats: " + profile.seats().size() + " total (" + drivers + " driver + "
                    + (profile.seats().size() - drivers) + " passengers)", lore.get(3), profile.id());
            assertThrows(UnsupportedOperationException.class, () -> lore.add("changed"));
        }
    }

    @Test void guestGuidancePreservesOwnerLocksAndDoesNotGrantDrivingKeys() {
        var profile = CATALOG.require("gtm:rickshaw_traditional");
        var locked = record(profile.id(), true, Set.of());
        var unlocked = locked.lock(OWNER, false);
        assertTrue(locked.canDrive(OWNER));
        assertFalse(locked.canRide(GUEST));
        assertTrue(unlocked.canRide(GUEST));
        assertFalse(unlocked.canDrive(GUEST));
        assertTrue(VehicleBoarding.garageLore(List.of(), profile, locked).stream().anyMatch(s -> s.startsWith("Guests locked out.")));
        assertTrue(VehicleBoarding.garageLore(List.of(), profile, unlocked).stream().anyMatch(s -> s.startsWith("Guests may right-click")));
        var keyed = locked.key(OWNER, GUEST, true);
        assertTrue(keyed.canDrive(GUEST));
        assertTrue(keyed.canRide(GUEST));
        assertFalse(keyed.key(OWNER, GUEST, false).canRide(GUEST));
    }

    @Test void oneSeatAndSupportModelsDoNotAdvertiseNonexistentPassengers() {
        for (String id : List.of("gtm:rickshaw_cargo", "gtm:bus_single_deck", "gtm:moto_splendor")) {
            var lore = VehicleBoarding.garageLore(List.of(), CATALOG.require(id), record(id, false, Set.of()));
            assertTrue(lore.stream().anyMatch(s -> s.equals("This model currently has no authored passenger seat.")), id);
            assertFalse(lore.stream().anyMatch(s -> s.startsWith("Passenger only:")), id);
        }
        var support = "gtm:skylink_grip";
        var lore = VehicleBoarding.garageLore(List.of(), CATALOG.require(support), record(support, false, Set.of()));
        assertTrue(lore.stream().anyMatch(s -> s.startsWith("This is a transport support")));
    }

    @Test void fourDistinctAdultMountsRotateTogetherInsideTheWidenedBody() {
        var auto = CATALOG.require("gtm:rickshaw_traditional");
        assertEquals(List.of("driver", "rear_left", "rear_right", "rear_center"),
                auto.seats().stream().map(RoadVehicleProfile.Seat::name).toList());
        for (int yaw = -180; yaw <= 180; yaw += 15) {
            var pose = new VehicleGeometry.Pose(120, 74, -40, yaw);
            for (int i = 0; i < auto.seats().size(); i++) {
                var hip = auto.seats().get(i).hip();
                assertTrue(hip.x() - .3 >= auto.bounds().minX());
                assertTrue(hip.x() + .3 <= auto.bounds().maxX());
                var point = pose.transform(auto.seats().get(i).mount());
                for (int j = i + 1; j < auto.seats().size(); j++) {
                    var other = pose.transform(auto.seats().get(j).mount());
                    assertTrue(Math.hypot(point.x() - other.x(), point.z() - other.z()) >= .6 - 1e-10);
                }
            }
        }
    }

    @Test void actualRearWheelAnimationPivotsRemainCentredThroughoutRotation() throws Exception {
        var animations = TransportAnimations.bundled();
        for (var state : RoadVehicleProfile.ArtState.values()) {
            var parts = animations.parts("gtm:rickshaw_traditional", state);
            for (var part : parts) {
                if (!Set.of("wheel_rl", "wheel_rr").contains(part.name())) continue;
                assertEquals(.966, Math.abs(part.pivot().x()), 1e-10);
                assertEquals(.2, part.pivot().y());
                assertEquals(-.78, part.pivot().z());
                assertEquals(.2, part.radius());
                var pivot = new Vector3f((float) part.pivot().x(), .2f, -.78f);
                var t = part.render().translation();
                var translation = new Vector3f((float)t.x(), (float)t.y(), (float)t.z());
                var localPivot = new Vector3f(pivot).sub(translation).div((float)part.render().scale());
                for (int angle = 0; angle <= 360; angle += 30) {
                    var matrix = new Matrix4f().translation(pivot).rotateX((float)Math.toRadians(angle))
                            .translate(new Vector3f(pivot).negate()).translate(translation).scale((float)part.render().scale());
                    var actual = VehicleRenderTransform.compensateItemFacing(matrix).rotateY((float)Math.PI)
                            .transformPosition(new Vector3f(localPivot));
                    assertEquals(pivot.x, actual.x, 1e-5);
                    assertEquals(pivot.y, actual.y, 1e-5);
                    assertEquals(pivot.z, actual.z, 1e-5);
                }
            }
        }
    }

    @Test void bothExistingEmergencyCarFrontCushionsAreReachableProfileSeats() {
        for (String id : List.of("gtm:emerg_police_suv", "gtm:emerg_patrol_sedan")) {
            var profile = CATALOG.require(id);
            assertEquals(2, profile.seats().size(), id);
            var driver = profile.seats().get(0);
            var passenger = profile.seats().get(1);
            assertTrue(driver.driver());
            assertFalse(passenger.driver());
            assertEquals("front_passenger", passenger.name());
            assertEquals(-driver.hip().x(), passenger.hip().x());
            assertEquals(driver.hip().y(), passenger.hip().y());
            assertEquals(driver.hip().z(), passenger.hip().z());
        }
    }
}
