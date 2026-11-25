package com.sdcraft.clienthud;

import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.Identifier;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.material.MapColor;

/** Actual loaded surface terrain, with fixed work budget and no chunk requests. */
final class TerrainMinimap {
    static final int SIZE=128, ROWS_PER_TICK=8;
    static final Identifier TEXTURE=GtmHudClient.id("terrain_map");
    private final int[] colours=new int[SIZE*SIZE];
    private final int[] shownColours=new int[SIZE*SIZE];
    private int row,startX,startZ,shownX,shownZ;
    private DynamicTexture texture;
    private ClientLevel level;
    private boolean ready;
    private boolean shownCircle;
    double centerX(){return shownX+SIZE/2.0;} double centerZ(){return shownZ+SIZE/2.0;}
    boolean ready(){return ready;}
    void tick(Minecraft client,boolean circle){
        if(level!=client.level){clear();level=client.level;}
        if(level==null||client.player==null)return;
        if(ready&&shownCircle!=circle)upload(circle);
        if(row==0){startX=(int)Math.floor(client.player.getX())-SIZE/2;startZ=(int)Math.floor(client.player.getZ())-SIZE/2;}
        BlockPos.MutableBlockPos pos=new BlockPos.MutableBlockPos();
        for(int limit=Math.min(SIZE,row+ROWS_PER_TICK);row<limit;row++)for(int x=0;x<SIZE;x++){
            int wx=startX+x,wz=startZ+row;
            LevelChunk chunk=level.getChunkSource().getChunk(wx>>4,wz>>4,false);
            int colour=0xFF253036;
            if(chunk!=null&&!chunk.isEmpty()){
                int y=chunk.getHeight(Heightmap.Types.WORLD_SURFACE,wx&15,wz&15);
                MapColor map=MapColor.NONE;
                for(int skip=0;skip<24&&y>=level.getMinY();skip++,y--){
                    pos.set(wx,y,wz);map=chunk.getBlockState(pos).getMapColor(level,pos);
                    if(map!=MapColor.NONE)break;
                }
                if(map!=MapColor.NONE)colour=map.calculateARGBColor(MapColor.Brightness.NORMAL);
            }
            colours[row*SIZE+x]=colour;
        }
        if(row==SIZE){
            if(texture==null){texture=new DynamicTexture(()->"GTM loaded terrain minimap",SIZE,SIZE,false);client.getTextureManager().register(TEXTURE,texture);}
            System.arraycopy(colours,0,shownColours,0,colours.length);
            upload(circle);shownX=startX;shownZ=startZ;ready=true;row=0;
        }
    }
    private void upload(boolean circle){
        NativeImage pixels=texture.getPixels();
        if(pixels!=null)for(int z=0;z<SIZE;z++)for(int x=0;x<SIZE;x++)
            pixels.setPixel(x,z,MinimapGeometry.textureVisible(circle,x,z)?shownColours[z*SIZE+x]:0);
        texture.upload();shownCircle=circle;
    }
    void clear(){
        if(texture!=null){Minecraft.getInstance().getTextureManager().release(TEXTURE);texture=null;}
        level=null;row=0;ready=false;
        java.util.Arrays.fill(colours,0);
        java.util.Arrays.fill(shownColours,0);
    }
}
