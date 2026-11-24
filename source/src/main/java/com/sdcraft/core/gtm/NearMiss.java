package com.sdcraft.core.gtm;

/** Proximity reaction predicate, not collision physics. All units are Minecraft blocks. */
public final class NearMiss {
    private NearMiss() {}
    public static boolean approaching(double dx,double dy,double dz,double vx,double vz) {
        if (!Double.isFinite(dx)||!Double.isFinite(dy)||!Double.isFinite(dz)||!Double.isFinite(vx)||!Double.isFinite(vz)) return false;
        double speed=Math.hypot(vx,vz), distance=Math.hypot(dx,dz);
        if (Math.abs(dy)>2 || speed<.15 || speed>3 || distance<.1 || distance>6) return false;
        double along=(dx*vx+dz*vz)/speed;
        double lateral=Math.abs(dx*vz-dz*vx)/speed;
        return along>0 && along/speed<=12 && lateral<=1.6;
    }
}
