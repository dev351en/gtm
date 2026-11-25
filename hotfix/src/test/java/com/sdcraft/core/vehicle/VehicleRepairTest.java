package com.sdcraft.core.vehicle;

import com.sdcraft.core.gtm.VehicleState;
import java.util.EnumMap;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class VehicleRepairTest {
    private static final RoadPhysics.Controls FORWARD = new RoadPhysics.Controls(true, false, false, false, false);
    private static final RoadPhysics.Controls REVERSE = new RoadPhysics.Controls(false, true, false, false, false);
    private static final RoadPhysics.Controls COAST = new RoadPhysics.Controls(false, false, false, false, false);
    private static final RoadPhysics.Controls RIGHT = new RoadPhysics.Controls(true, false, false, true, false);
    private static final RoadVehicleProfile PROFILE = profile();

    private static RoadVehicleProfile profile() {
        var renders = new EnumMap<RoadVehicleProfile.ArtState, RoadVehicleProfile.Render>(RoadVehicleProfile.ArtState.class);
        for (var state : RoadVehicleProfile.ArtState.values())
            renders.put(state, new RoadVehicleProfile.Render("gtm:rickshaw_traditional", 1.179, new VehicleGeometry.Point(0, 0.5895, -0.017)));
        return new RoadVehicleProfile("gtm:rickshaw_traditional", "Indra Auto", "rickshaw", RoadVehicleProfile.Energy.CNG, 20,
                new VehicleGeometry.Bounds(-0.65, 0, -1.3, 0.65, 1.7875, 1.3),
                List.of(new RoadVehicleProfile.Seat("driver", new VehicleGeometry.Point(0, 0.60625, 0.208), true)),
                new RoadVehicleProfile.Handling(6.5, 2.6, 2.5, 9, 1.8, 30, 1.612, 0.005, 0.001),
                renders, "a".repeat(64), "preserved profile regression fixture");
    }

    private static RoadPhysics.Motion at(double speed, double energy) {
        return new RoadPhysics.Motion(new VehicleGeometry.Pose(0, 74, 0, 0), speed, new VehicleState(20, energy, 100, 0));
    }

    private static RoadPhysics.Motion tick(RoadPhysics.Motion motion, RoadPhysics.Controls controls, double dt) {
        var proposal = RoadPhysics.propose(motion, controls, PROFILE, dt);
        return RoadPhysics.accept(motion, proposal, proposal.pose(), PROFILE, false);
    }

    private static RoadPhysics.Motion run(RoadPhysics.Motion motion, RoadPhysics.Controls controls, int steps, double dt) {
        for (int i = 0; i < steps; i++) motion = tick(motion, controls, dt);
        return motion;
    }

    @Test void integratesAccelerationInsteadOfTeleportingAtEndVelocity() {
        var after = run(at(0, 20), FORWARD, 20, 0.05);
        assertEquals(2.5, after.speed(), 1e-10);
        assertEquals(1.25, after.pose().z(), 1e-10);
        assertEquals(0, after.pose().x(), 1e-10);
    }

    @Test void straightMotionAgreesAcrossSupportedTimesteps() {
        var coarse = run(at(0, 20), FORWARD, 40, 0.1);
        var normal = run(at(0, 20), FORWARD, 80, 0.05);
        var fine = run(at(0, 20), FORWARD, 160, 0.025);
        assertEquals(coarse.pose().z(), normal.pose().z(), 1e-9);
        assertEquals(coarse.pose().z(), fine.pose().z(), 1e-9);
        assertEquals(6.5, normal.speed(), 1e-10);
    }

    @Test void releasePreservesInertiaThenStopsWithoutOscillation() {
        var before = at(6.5, 20);
        var first = tick(before, COAST, 0.05);
        assertTrue(first.speed() < 6.5 && first.speed() > 6);
        var stopped = run(first, COAST, 100, 0.05);
        assertEquals(0, stopped.speed());
        assertEquals(6.5 * 6.5 / (2 * 1.8), stopped.pose().z(), 1e-8);
    }

    @Test void reverseBrakesBeforeChangingDirection() {
        var before = at(0.2, 20);
        var braking = tick(before, REVERSE, 0.05);
        assertEquals(0, braking.speed());
        assertTrue(braking.pose().z() > 0);
        var reversing = tick(braking, REVERSE, 0.05);
        assertTrue(reversing.speed() < 0);
        assertTrue(reversing.pose().z() < braking.pose().z());
    }

    @Test void reverseSpeedIsBounded() {
        var reverse = run(at(0, 20), REVERSE, 1000, 0.05);
        assertEquals(-2.6, reverse.speed(), 1e-10);
        assertTrue(reverse.state().energy() >= 0);
    }

    @Test void brakeStoppingDistanceIsIndependentOfStepSize() {
        var coarse = run(at(4, 20), RoadPhysics.Controls.STOP, 10, 0.1);
        var normal = run(at(4, 20), RoadPhysics.Controls.STOP, 20, 0.05);
        assertEquals(0, normal.speed());
        assertEquals(16.0 / 18, normal.pose().z(), 1e-10);
        assertEquals(coarse.pose().z(), normal.pose().z(), 1e-10);
    }

    @Test void parkedSteeringDoesNotPivotTheVehicle() {
        var steeringOnly = new RoadPhysics.Controls(false, false, false, true, false);
        var after = run(at(0, 20), steeringOnly, 100, 0.05);
        assertEquals(at(0, 20).pose(), after.pose());
        assertEquals(0, after.state().distance());
    }

    @Test void forwardAndReverseSteeringHaveOppositeYaw() {
        var forward = RoadPhysics.propose(at(2, 20), RIGHT, PROFILE, 0.05);
        var reverseRight = new RoadPhysics.Controls(false, true, false, true, false);
        var reverse = RoadPhysics.propose(at(-2, 20), reverseRight, PROFILE, 0.05);
        assertTrue(forward.pose().yaw() > 0);
        assertTrue(reverse.pose().yaw() < 0);
        assertEquals(-forward.pose().yaw(), reverse.pose().yaw(), 1e-10);
    }

    @Test void highSpeedSteeringHasBoundedLateralAcceleration() {
        var proposal = RoadPhysics.propose(at(6.5, 20), RIGHT, PROFILE, 0.05);
        double yawRate = Math.toRadians(proposal.pose().yaw()) / proposal.dt();
        assertTrue(6.5 * yawRate <= 3.50001);
        assertTrue(proposal.pose().yaw() > 0);
    }

    @Test void fullAcceptedTurnDoesNotTriggerFalseCollisionStop() {
        var before = at(6.5, 20);
        var after = tick(before, RIGHT, 0.05);
        assertEquals(6.5, after.speed(), 1e-10);
        assertEquals(6.5 * 0.05, after.state().distance(), 1e-9);
        assertEquals(100, after.state().health());
    }

    @Test void aFullCircleDoesNotSpiralFromEulerDrift() {
        var fixed = new RoadVehicleProfile(PROFILE.id(), PROFILE.title(), PROFILE.category(), PROFILE.energy(), PROFILE.capacity(),
                PROFILE.bounds(), PROFILE.seats(), new RoadVehicleProfile.Handling(2, 2, 2.5, 9, 1.8, 30, 1.612, .005, .001),
                PROFILE.renders(), PROFILE.geometryHash(), PROFILE.seatSource());
        var motion = at(2, 20);
        double curvature = Math.tan(Math.toRadians(30)) / 1.612;
        double radius = 1 / curvature;
        for (int i = 0; i < 200; i++) {
            var p = RoadPhysics.propose(motion, RIGHT, fixed, 0.05);
            motion = RoadPhysics.accept(motion, p, p.pose(), fixed, false);
            assertEquals(radius, Math.hypot(motion.pose().x() + radius, motion.pose().z()), 1e-8);
        }
    }

    @Test void partiallyAcceptedCollisionConsumesOnlyTravelledDistance() {
        var before = at(4, 20);
        var proposal = RoadPhysics.propose(before, FORWARD, PROFILE, 0.05);
        var halfway = new VehicleGeometry.Pose(0, 74, proposal.pose().z() / 2, 0);
        var after = RoadPhysics.accept(before, proposal, halfway, PROFILE, true);
        assertEquals(0, after.speed());
        assertEquals(proposal.distance() / 2, after.state().distance(), 1e-10);
        assertEquals(20 - proposal.distance() / 2 * .005 - .001 * .05, after.state().energy(), 1e-10);
        assertTrue(after.state().health() < 100);
    }

    @Test void blockedMotionWithoutPhysicalImpactDoesNotDamageVehicle() {
        var before = at(6.5, 20);
        var proposal = RoadPhysics.propose(before, FORWARD, PROFILE, 0.05);
        var after = RoadPhysics.accept(before, proposal, before.pose(), PROFILE, false);
        assertEquals(0, after.speed());
        assertEquals(100, after.state().health());
        assertEquals(20, after.state().energy());
        assertEquals(0, after.state().distance());
    }

    @Test void emptyEngineCannotAccelerateButMomentumCoasts() {
        var first = tick(at(3, 0), FORWARD, 0.05);
        assertTrue(first.speed() > 0 && first.speed() < 3);
        assertTrue(first.pose().z() > 0);
        assertEquals(0, first.state().energy());
        var stopped = run(first, FORWARD, 100, 0.05);
        assertEquals(0, stopped.speed());
        assertEquals(0, tick(at(0, 0), FORWARD, .05).speed());
    }

    @Test void nearlyEmptyTankCannotGrantUnfundedAcceleration() {
        var before = at(3, 0.000001);
        var after = tick(before, FORWARD, .05);
        assertTrue(after.speed() < before.speed());
        assertEquals(0, after.state().energy());
        assertTrue(after.state().distance() > 0);
    }

    @Test void engineFailureCannotCreateMomentum() {
        var before = new RoadPhysics.Motion(at(2, 20).pose(), 2, new VehicleState(20, 20, 25, 0));
        var after = tick(before, FORWARD, .05);
        assertTrue(after.speed() < before.speed());
        assertEquals(20, after.state().energy());
        assertTrue(after.state().distance() > 0);
    }

    @Test void rejectsInvalidTimestepAndMovementBeyondSweptProposal() {
        assertThrows(IllegalArgumentException.class, () -> RoadPhysics.propose(at(0, 20), FORWARD, PROFILE, Double.NaN));
        assertThrows(IllegalArgumentException.class, () -> RoadPhysics.propose(at(0, 20), FORWARD, PROFILE, .2));
        var before = at(3, 20);
        var proposal = RoadPhysics.propose(before, FORWARD, PROFILE, .05);
        assertThrows(IllegalArgumentException.class, () -> RoadPhysics.accept(before, proposal,
                new VehicleGeometry.Pose(0, 74, 10, 0), PROFILE, false));
    }

    @Test void everyBundledRoadProfileRetainsBoundedFiniteMotionAndEnergy() throws Exception {
        var catalog = RoadVehicleCatalog.bundled();
        assertEquals(87, catalog.all().size());
        int roads = 0;
        for (var profile : catalog.all()) {
            if (profile.mode() != RoadVehicleProfile.Mode.ROAD) continue;
            roads++;
            var motion = new RoadPhysics.Motion(new VehicleGeometry.Pose(0, 74, 0, 0), 0,
                    new VehicleState(profile.capacity(), profile.capacity(), 100, 0));
            for (int i = 0; i < 240; i++) {
                var p = RoadPhysics.propose(motion, i < 100 ? FORWARD : i < 180 ? RIGHT : RoadPhysics.Controls.STOP, profile, .05);
                motion = RoadPhysics.accept(motion, p, p.pose(), profile, false);
                assertTrue(Math.abs(motion.speed()) <= profile.handling().maxForward() + 1e-8, profile.id());
                assertTrue(motion.state().energy() >= 0 && motion.state().energy() <= profile.capacity(), profile.id());
            }
            assertEquals(0, motion.speed(), 1e-8, profile.id());
        }
        assertEquals(65, roads);
    }

    @Test void bundledProfileLoadsRaisedTraditionalCanopyWithoutMovingSeats() throws Exception {
        var profile = RoadVehicleCatalog.bundled().all().stream()
                .filter(p -> p.id().equals("gtm:rickshaw_traditional")).findFirst().orElseThrow();
        assertEquals(2.238, profile.bounds().maxY());
        assertEquals(new VehicleGeometry.Point(0, .60625, .208), profile.seats().getFirst().hip());
        assertEquals(new VehicleGeometry.Point(0, .62, .208), profile.seats().getFirst().mount());
        assertEquals(PROFILE.handling(), profile.handling());
        assertEquals("256ff4ca40ae1a310995214a9b261ccfd5e7024a5af73bbdc7d6f31a11c3abf3", profile.geometryHash());
    }

    @Test void guidedModesKeepTheirOriginalSpeedTimesStepFuelContract() throws Exception {
        for (var profile : RoadVehicleCatalog.bundled().all()) {
            if (profile.mode() == RoadVehicleProfile.Mode.ROAD) continue;
            var before = new RoadPhysics.Motion(new VehicleGeometry.Pose(0, 74, 0, 0), 1,
                    new VehicleState(profile.capacity(), .000001, 100, 0));
            var proposal = RoadPhysics.propose(before, FORWARD, profile, .05);
            assertEquals(Math.abs(proposal.speed()) * .05, proposal.distance(), 1e-10);
            assertTrue(proposal.distance() * profile.handling().energyPerBlock() <= before.state().energy() + 1e-10);
            var empty = new RoadPhysics.Motion(before.pose(), 1, new VehicleState(profile.capacity(), 0, 100, 0));
            assertEquals(0, RoadPhysics.propose(empty, FORWARD, profile, .05).speed());
        }
    }

    @Test void preservedFleetControllerCompletesCurvedRouteWithNewRoadPhysics() {
        var points = new ArrayList<VehicleGeometry.Point>();
        for (int i = 0; i <= 10; i++) points.add(new VehicleGeometry.Point(0, 74, i));
        for (int i = 1; i <= 32; i++) {
            double angle = Math.PI / 2 * i / 32;
            points.add(new VehicleGeometry.Point(-10 + 10 * Math.cos(angle), 74, 10 + 10 * Math.sin(angle)));
        }
        for (int i = 11; i <= 30; i++) points.add(new VehicleGeometry.Point(-i, 74, 20));
        var route = new ManagedRoadRoute(new UUID(0, 1), points);
        var motion = at(0, 20);
        double progress = 0;
        boolean arrived = false;
        for (int i = 0; i < 2000; i++) {
            var guidance = route.guide(motion, PROFILE, progress);
            assertFalse(guidance.offRoute(), "Fleet controller left the commissioned route at step " + i);
            if (guidance.arrived()) { arrived = true; break; }
            var previous = motion.pose();
            motion = tick(motion, guidance.controls(), .05);
            double accepted = Math.hypot(motion.pose().x() - previous.x(), motion.pose().z() - previous.z());
            var projected = route.project(motion.pose(), Math.max(0, progress - .15), Math.min(route.length(), progress + accepted + .25));
            progress = Math.max(progress, projected.progress());
        }
        assertTrue(arrived, "Fleet controller did not arrive");
        assertTrue(motion.pose().distance(route.at(route.length())) < .75);
        assertTrue(motion.state().energy() < 20);
    }

    @Test void visualCorrectionPreservesAuthoredSeatAndBodyOrientation() {
        Matrix4f authored = new Matrix4f().translation(0, .5895f, -.017f).scale(1.179f);
        Vector3f model = new Vector3f(.2f, .3f, .8f);
        Vector3f expected = authored.transformPosition(new Vector3f(model));
        Matrix4f runtime = VehicleRenderTransform.compensateItemFacing(new Matrix4f(authored));
        Vector3f actual = runtime.rotateY((float)Math.PI).transformPosition(new Vector3f(model));
        assertVector(expected, actual);
        // Player seat/collision offsets stay in the original authored axes.
        assertTrue(actual.z > 0);
    }

    @Test void frontWheelPivotStaysFixedThroughAFullRevolution() {
        Vector3f pivot = new Vector3f(0, .2f, .962f);
        Vector3f translation = new Vector3f(0, .5895f, -.017f);
        float scale = 1.179f;
        Vector3f normalizedPivot = new Vector3f(pivot).sub(translation).div(scale);
        for (int degrees = 0; degrees <= 360; degrees += 15) {
            Matrix4f authored = new Matrix4f().translation(pivot).rotateX((float)Math.toRadians(degrees))
                    .translate(new Vector3f(pivot).negate()).translate(translation).scale(scale);
            Matrix4f runtime = VehicleRenderTransform.compensateItemFacing(authored).rotateY((float)Math.PI);
            assertVector(pivot, runtime.transformPosition(new Vector3f(normalizedPivot)));
        }
    }

    @Test void uncorrectedWheelReproducesRoofOrbit() {
        Vector3f pivot = new Vector3f(0, .2f, .962f);
        Vector3f translation = new Vector3f(0, .5895f, -.017f);
        float scale = 1.179f;
        Vector3f normalizedPivot = new Vector3f(pivot).sub(translation).div(scale);
        Vector3f wrong = new Matrix4f().translation(pivot).rotateX((float)Math.PI / 2)
                .translate(new Vector3f(pivot).negate()).translate(translation).scale(scale)
                .rotateY((float)Math.PI).transformPosition(normalizedPivot);
        assertTrue(wrong.y > 2, "The previous transform rotates the front wheel above the roof");
    }

    private static void assertVector(Vector3f expected, Vector3f actual) {
        assertEquals(expected.x, actual.x, 1e-5);
        assertEquals(expected.y, actual.y, 1e-5);
        assertEquals(expected.z, actual.z, 1e-5);
    }
}
