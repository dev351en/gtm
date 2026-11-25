package com.sdcraft.clienthud;

/** Measured apertures of the unchanged native128 minimap frame PNGs. */
final class MinimapGeometry {
    private MinimapGeometry(){}
    static final int SOURCE_SIZE=128, DRAW_SIZE=126;
    static boolean textureVisible(boolean circle,int x,int y){
        if(x<0||y<0||x>=SOURCE_SIZE||y>=SOURCE_SIZE)return false;
        if(!circle)return x>=15&&x<113&&y>=30&&y<99;
        // The inner hole has radius45.5; this extra rim is covered by the
        // existing opaque artwork, avoiding seams without bleeding outside it.
        double dx=x-64,dy=y-64;
        return dx*dx+dy*dy<=47*47;
    }
    static double drawOffset(double worldOffset){return worldOffset*DRAW_SIZE/SOURCE_SIZE;}
    static boolean markerVisible(boolean circle,double dx,double dy){
        if(!Double.isFinite(dx)||!Double.isFinite(dy))return false;
        return circle?dx*dx+dy*dy<=39*39:dx>=-42&&dx<=42&&dy>=-27&&dy<=28;
    }
}
