package com.sdcraft.core;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

public class MapAndGpsTest {

    @Test
    public void testDirectionCalculation() {
        // Mock simple coordinate vectors
        assertEquals("North", calculateDirection(0, 0, 0, -50));
        assertEquals("South", calculateDirection(0, 0, 0, 50));
        assertEquals("East", calculateDirection(0, 0, 50, 0));
        assertEquals("West", calculateDirection(0, 0, -50, 0));
        assertEquals("North-East", calculateDirection(0, 0, 50, -50));
        assertEquals("South-West", calculateDirection(0, 0, -50, 50));
    }

    private String calculateDirection(double fromX, double fromZ, double toX, double toZ) {
        double dx = toX - fromX;
        double dz = toZ - fromZ;
        double angle = Math.toDegrees(Math.atan2(dx, -dz));
        if (angle < 0) angle += 360.0;

        if (angle >= 337.5 || angle < 22.5) return "North";
        if (angle >= 22.5 && angle < 67.5) return "North-East";
        if (angle >= 67.5 && angle < 112.5) return "East";
        if (angle >= 112.5 && angle < 157.5) return "South-East";
        if (angle >= 157.5 && angle < 202.5) return "South";
        if (angle >= 202.5 && angle < 247.5) return "South-West";
        if (angle >= 247.5 && angle < 292.5) return "West";
        return "North-West";
    }

    @Test
    public void testDistrictBoundaries() {
        assertEquals("Downtown City Center", getDistrictForCoords(100, 0));
        assertEquals("Civic Center", getDistrictForCoords(0, 0));
        assertEquals("Financial District", getDistrictForCoords(60, -120));
        assertEquals("Motor Mile & Industrial", getDistrictForCoords(-150, 0));
        assertEquals("Airport International Zone", getDistrictForCoords(-300, -250));
        assertEquals("New Blockston Metro", getDistrictForCoords(1000, 1000));
    }

    private String getDistrictForCoords(int x, int z) {
        if (x >= 50 && x <= 200 && z >= -100 && z <= 50) return "Downtown City Center";
        if (x >= -50 && x < 50 && z >= -50 && z <= 50) return "Civic Center";
        if (x >= 30 && x <= 150 && z < -100 && z >= -250) return "Financial District";
        if (x >= -250 && x < -100 && z >= -100 && z <= 50) return "Motor Mile & Industrial";
        if (x >= -200 && x < -50 && z > 50 && z <= 250) return "Westside Residential";
        if (x >= 150 && x <= 350 && z > 50 && z <= 250) return "Midtown District";
        if (x <= -250 && z <= -150) return "Airport International Zone";
        if (x < -180 && z >= 50 && z <= 300) return "East Commercial Boulevard";
        return "New Blockston Metro";
    }
}
