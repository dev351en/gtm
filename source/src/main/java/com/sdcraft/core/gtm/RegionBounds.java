package com.sdcraft.core.gtm;

import java.util.Objects;

/** Inclusive integer block bounds; continuous positions use half-open edges. */
public record RegionBounds(String world,int minX,int minY,int minZ,int maxX,int maxY,int maxZ) {
    public RegionBounds {
        Objects.requireNonNull(world);
        if(world.isBlank()||minX>maxX||minY>maxY||minZ>maxZ||Math.abs((long)minX)>30000000||Math.abs((long)maxX)>30000000
            ||Math.abs((long)minZ)>30000000||Math.abs((long)maxZ)>30000000||minY < -2048||maxY>2048)throw new IllegalArgumentException("Invalid surveyed bounds");
    }
    public boolean contains(String w,double x,double y,double z) {
        return world.equals(w)&&x>=minX&&x<(double)maxX+1&&y>=minY&&y<(double)maxY+1&&z>=minZ&&z<(double)maxZ+1;
    }
    public boolean overlaps(RegionBounds b) {
        return world.equals(b.world)&&minX<=b.maxX&&maxX>=b.minX&&minY<=b.maxY&&maxY>=b.minY&&minZ<=b.maxZ&&maxZ>=b.minZ;
    }
}
