package com.sdcraft.core.gtm;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
final class RegionBoundsTest {
    @Test void halfOpenAndWorldSpecific() {
        var a=new RegionBounds("city",10,60,-3,12,64,-1);
        assertTrue(a.contains("city",10,60,-3));
        assertTrue(a.contains("city",12.99,64.99,-.01));
        assertFalse(a.contains("city",13,64,-1));
        assertFalse(a.contains("city",10,65,-1));
        assertFalse(a.contains("city",10,64,0));
        assertFalse(a.contains("other",10,60,-3));
        assertFalse(a.contains("city",Double.NaN,60,-3));
    }
    @Test void rejectsOverlapButAllowsAdjacentFloors() {
        var a=new RegionBounds("city",0,60,0,5,64,5);
        assertTrue(a.overlaps(new RegionBounds("city",5,64,5,9,70,9)));
        assertFalse(a.overlaps(new RegionBounds("city",0,65,0,5,69,5)));
        assertFalse(a.overlaps(new RegionBounds("other",0,60,0,5,64,5)));
        assertThrows(IllegalArgumentException.class,()->new RegionBounds("city",5,60,0,0,64,5));
        assertThrows(IllegalArgumentException.class,()->new RegionBounds("city",0,60,0,Integer.MAX_VALUE,64,5));
    }
}
