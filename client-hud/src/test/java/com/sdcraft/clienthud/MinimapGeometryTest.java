package com.sdcraft.clienthud;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class MinimapGeometryTest {
    @Test void rectangleMatchesTheExistingFrameAperture(){
        int count=0;
        for(int y=0;y<128;y++)for(int x=0;x<128;x++)
            if(MinimapGeometry.textureVisible(false,x,y))count++;
        assertEquals(6762,count); // 98 by69 transparent pixels in the source art.
        assertTrue(MinimapGeometry.textureVisible(false,15,30));
        assertTrue(MinimapGeometry.textureVisible(false,112,98));
        assertFalse(MinimapGeometry.textureVisible(false,14,64));
        assertFalse(MinimapGeometry.textureVisible(false,64,99));
    }
    @Test void circleCannotLeakThroughTheOutsideOfTheFrame(){
        assertTrue(MinimapGeometry.textureVisible(true,64,64));
        assertTrue(MinimapGeometry.textureVisible(true,19,64));
        assertFalse(MinimapGeometry.textureVisible(true,10,64));
        assertFalse(MinimapGeometry.textureVisible(true,64,10));
        assertFalse(MinimapGeometry.textureVisible(true,20,20));
        assertFalse(MinimapGeometry.textureVisible(true,-1,64));
    }
    @Test void markerClippingKeepsWholeIconsInsideEitherAperture(){
        assertTrue(MinimapGeometry.markerVisible(false,42,28));
        assertFalse(MinimapGeometry.markerVisible(false,43,0));
        assertFalse(MinimapGeometry.markerVisible(false,0,-28));
        assertTrue(MinimapGeometry.markerVisible(true,39,0));
        assertFalse(MinimapGeometry.markerVisible(true,39,39));
        assertFalse(MinimapGeometry.markerVisible(true,Double.NaN,0));
    }
    @Test void TerrainAndMarkersShareAnUndistortedWorldScale(){
        assertEquals(63,MinimapGeometry.drawOffset(64));
        assertEquals(-31.5,MinimapGeometry.drawOffset(-32));
        assertEquals(0,MinimapGeometry.drawOffset(0));
    }
}
