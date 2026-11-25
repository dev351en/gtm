package com.sdcraft.core.vehicle;

import com.sdcraft.core.gtm.VehicleState;
import java.util.Objects;

/**
 * Deterministic road motion, retaining the public binary API of the preserved
 * 1.0.3 runtime. Units are game blocks, seconds and degrees.
 *
 * <p>Integration accounts for acceleration/braking during a step, rather than
 * moving at the end-of-step velocity for the whole step. Steering is bounded by
 * lateral acceleration at speed; low-speed parking retains the authored lock.
 * Unpowered vehicles can dissipate their existing momentum but cannot accelerate.
 * The Paper adapter remains responsible for swept collision and player access.</p>
 */
public final class RoadPhysics {
    private static final double EPSILON = 1.0e-7;
    private static final double MAX_LATERAL_ACCELERATION = 3.5;

    private RoadPhysics() {}

    public static Proposal propose(Motion motion, Controls controls, RoadVehicleProfile profile, double dt) {
        return propose(motion, controls, profile, dt, VehicleMaintenanceState.Effects.NORMAL);
    }

    public static Proposal propose(Motion motion, Controls controls, RoadVehicleProfile profile, double dt,
                                   VehicleMaintenanceState.Effects maintenance) {
        Objects.requireNonNull(motion, "Road motion");
        Objects.requireNonNull(controls, "Road controls");
        Objects.requireNonNull(profile, "Road profile");
        Objects.requireNonNull(maintenance, "Maintenance effects");
        if (!Double.isFinite(dt) || dt <= 0 || dt > 0.1) throw new IllegalArgumentException("Road step must be bounded");
        // Guided transport reads proposal.speed * dt directly. Preserve its
        // original contract; this repair intentionally changes road handling.
        if (profile.mode() != RoadVehicleProfile.Mode.ROAD) return guidedProposal(motion, controls, profile, dt, maintenance);

        RoadVehicleProfile.Handling handling = profile.handling();
        int throttle = (controls.forward() ? 1 : 0) - (controls.reverse() ? 1 : 0);
        double healthScale = motion.state().health() < 75 ? 0.55 + 0.45 * motion.state().health() / 75 : 1;
        boolean powered = motion.state().canPropel();
        Step step = longitudinal(motion.speed(), throttle, controls.brake(), powered, handling, maintenance, healthScale, dt);
        double rate = handling.energyPerBlock() * maintenance.energyRate();

        // Insufficient fuel must not produce a final un-funded acceleration.
        // Already-moving vehicles coast through this step using their existing
        // momentum. A stationary vehicle can only start within funded distance.
        if (powered && Math.abs(step.distance()) * rate > motion.state().energy()) {
            if (Math.abs(motion.speed()) > EPSILON) {
                step = longitudinal(motion.speed(), 0, controls.brake(), false, handling, maintenance, healthScale, dt);
            } else {
                step = new Step(0, Math.copySign(motion.state().energy() / rate, step.distance()));
            }
        }

        double distance = Math.abs(step.distance());
        double steer = (controls.right() ? 1.0 : 0.0) - (controls.left() ? 1.0 : 0.0);
        double averageSpeed = distance / dt;
        double fullLock = Math.toRadians(handling.steeringDegrees()) * maintenance.steering();
        double speedLock = Math.atan(MAX_LATERAL_ACCELERATION * maintenance.steering() * handling.wheelbase()
                                    / Math.max(0.25, averageSpeed * averageSpeed));
        double wheelAngle = Math.min(fullLock, speedLock) * steer;
        double turn = step.distance() / handling.wheelbase() * Math.tan(wheelAngle);
        double start = Math.toRadians(motion.pose().yaw());
        double dx;
        double dz;
        if (Math.abs(turn) < EPSILON) {
            dx = -Math.sin(start) * step.distance();
            dz = Math.cos(start) * step.distance();
        } else {
            // Exact bicycle-model arc: repeated fixed steps and finer steps
            // agree, and steering reverses naturally when driving backwards.
            double radius = step.distance() / turn;
            dx = radius * (Math.cos(start + turn) - Math.cos(start));
            dz = radius * (Math.sin(start + turn) - Math.sin(start));
        }
        VehicleGeometry.Pose target = new VehicleGeometry.Pose(motion.pose().x() + dx, motion.pose().y(),
                motion.pose().z() + dz, motion.pose().yaw() + Math.toDegrees(turn));
        return new Proposal(target, step.speed(), distance, dt);
    }

    private static Proposal guidedProposal(Motion motion, Controls controls, RoadVehicleProfile profile, double dt,
                                           VehicleMaintenanceState.Effects maintenance) {
        var h = profile.handling();
        double speed = motion.speed();
        int throttle = (controls.forward() ? 1 : 0) - (controls.reverse() ? 1 : 0);
        boolean opposing = throttle != 0 && Math.signum(speed) != throttle && Math.abs(speed) > .05;
        if (controls.brake() || opposing || !motion.state().canPropel()) {
            speed = Math.copySign(Math.max(0, Math.abs(speed) - h.braking() * maintenance.braking() * dt), speed);
        } else if (throttle != 0) speed += throttle * h.acceleration() * maintenance.acceleration() * dt;
        else speed = Math.copySign(Math.max(0, Math.abs(speed) - h.drag() * dt), speed);
        double healthScale = motion.state().health() < 75 ? .55 + .45 * motion.state().health() / 75 : 1;
        speed = Math.max(-h.maxReverse() * healthScale * maintenance.maximumSpeed(),
                Math.min(h.maxForward() * healthScale * maintenance.maximumSpeed(), speed));
        if (Math.abs(speed) < .005) speed = 0;
        double requested = Math.abs(speed) * dt;
        double allowed = motion.state().canPropel()
                ? Math.min(requested, motion.state().energy() / (h.energyPerBlock() * maintenance.energyRate())) : 0;
        if (allowed < requested) speed = allowed / dt * Math.signum(speed);
        double steer = (controls.right() ? 1 : 0) - (controls.left() ? 1 : 0);
        double turn = Math.toDegrees(speed / h.wheelbase() * Math.tan(Math.toRadians(h.steeringDegrees()) * maintenance.steering() * steer) * dt);
        double middle = Math.toRadians(motion.pose().yaw() + turn / 2);
        return new Proposal(new VehicleGeometry.Pose(motion.pose().x() - Math.sin(middle) * speed * dt, motion.pose().y(),
                motion.pose().z() + Math.cos(middle) * speed * dt, motion.pose().yaw() + turn), speed, allowed, dt);
    }

    private static Step longitudinal(double initial, int throttle, boolean brake, boolean powered,
                                     RoadVehicleProfile.Handling h, VehicleMaintenanceState.Effects effects,
                                     double healthScale, double dt) {
        boolean opposing = throttle != 0 && Math.abs(initial) > EPSILON && Math.signum(initial) != throttle;
        if (brake || opposing) return approach(initial, 0, h.braking() * effects.braking(), dt);
        if (!powered || throttle == 0) return approach(initial, 0, h.drag() * (powered ? 1 : 1.25), dt);
        double limit = throttle > 0 ? h.maxForward() : h.maxReverse();
        double target = throttle * limit * healthScale * effects.maximumSpeed();
        // Damage/wear can lower the speed ceiling while already travelling.
        // Brake to that ceiling instead of deleting momentum in a single tick.
        double rate = Math.abs(initial) > Math.abs(target)
                ? h.braking() * effects.braking() : h.acceleration() * effects.acceleration();
        return approach(initial, target, rate, dt);
    }

    private static Step approach(double initial, double target, double rate, double dt) {
        double difference = target - initial;
        if (Math.abs(difference) < EPSILON) return new Step(target, target * dt);
        double time = Math.min(dt, Math.abs(difference) / rate);
        double end = time < dt ? target : initial + Math.copySign(rate * time, difference);
        if (Math.abs(end) < EPSILON) end = 0;
        return new Step(end, (initial + end) * 0.5 * time + end * (dt - time));
    }

    public static Motion accept(Motion before, Proposal proposal, VehicleGeometry.Pose accepted,
                                RoadVehicleProfile profile, boolean physicalImpact) {
        return accept(before, proposal, accepted, profile, physicalImpact, VehicleMaintenanceState.Effects.NORMAL);
    }

    public static Motion accept(Motion before, Proposal proposal, VehicleGeometry.Pose accepted,
                                RoadVehicleProfile profile, boolean physicalImpact,
                                VehicleMaintenanceState.Effects maintenance) {
        Objects.requireNonNull(before, "Previous road motion");
        Objects.requireNonNull(proposal, "Road proposal");
        Objects.requireNonNull(accepted, "Accepted road pose");
        Objects.requireNonNull(profile, "Road profile");
        Objects.requireNonNull(maintenance, "Maintenance effects");
        double chord = Math.hypot(accepted.x() - before.pose().x(), accepted.z() - before.pose().z());
        double proposedChord = Math.hypot(proposal.pose().x() - before.pose().x(), proposal.pose().z() - before.pose().z());
        if (chord > proposedChord + 1.0e-5) throw new IllegalArgumentException("Accepted movement exceeds road proposal");
        double fraction = proposedChord < EPSILON ? 0 : Math.min(1, chord / proposedChord);
        double distance = proposal.distance() * fraction;
        boolean stopped = chord + 1.0e-5 < proposedChord;
        double speed = stopped ? 0 : proposal.speed();
        VehicleState previous = before.state();
        double cost = previous.canPropel() ? distance * profile.handling().energyPerBlock() * maintenance.energyRate() : 0;
        if (previous.canPropel() && (distance > 0 || Math.abs(speed) > 0.05)) {
            cost += profile.handling().idlePerSecond() * proposal.dt() * maintenance.energyRate();
        }
        VehicleState state = new VehicleState(previous.capacity(), Math.max(0, previous.energy() - cost),
                previous.health(), previous.distance() + distance);
        if (physicalImpact && Math.abs(proposal.speed()) > 1.5) {
            state = state.damage(Math.min(35, Math.pow(Math.abs(proposal.speed()) - 1.5, 2) * 0.8)).state();
        }
        return new Motion(accepted, speed, state);
    }

    private record Step(double speed, double distance) {}

    public record Motion(VehicleGeometry.Pose pose, double speed, VehicleState state) {
        public Motion {
            if (pose == null || state == null || !Double.isFinite(speed) || Math.abs(speed) > 16)
                throw new IllegalArgumentException("Invalid road motion");
        }
    }

    public record Controls(boolean forward, boolean reverse, boolean left, boolean right, boolean brake) {
        public static final Controls STOP = new Controls(false, false, false, false, true);
    }

    public record Proposal(VehicleGeometry.Pose pose, double speed, double distance, double dt) {
        public Proposal {
            if (pose == null || !Double.isFinite(speed) || Math.abs(speed) > 16 || !Double.isFinite(distance)
                    || distance < 0 || !Double.isFinite(dt) || dt <= 0 || dt > 0.1)
                throw new IllegalArgumentException("Invalid road proposal");
        }
    }
}
