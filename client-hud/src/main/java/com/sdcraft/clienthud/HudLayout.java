package com.sdcraft.clienthud;

/** One layout drives painting and hit tests at every Minecraft GUI scale. */
public record HudLayout(float scale,int width,int height,Box hotbar,Box status,Box map,Box phone,Box phoneShortcut) {
    public record Box(int x,int y,int width,int height) {
        public int right(){return x+width;} public int bottom(){return y+height;}
        public boolean contains(double x,double y){return x>=this.x&&y>=this.y&&x<right()&&y<bottom();}
        public boolean overlaps(Box b){return x<b.right()&&right()>b.x&&y<b.bottom()&&bottom()>b.y;}
    }
    public static HudLayout of(int physicalWidth,int physicalHeight) {
        float scale=Math.min(1f,Math.min(physicalWidth/480f,physicalHeight/300f));
        scale=Math.max(.1f,scale);
        int width=Math.round(physicalWidth/scale),height=Math.round(physicalHeight/scale);
        return new HudLayout(scale,width,height,new Box(10,10,216,24),new Box(width-164,10,154,60),
                new Box(10,height-146,126,136),new Box(width-176,height-218,166,208),
                new Box(width-64,height-58,54,48));
    }
    public Box slot(int index) { if(index<0||index>8)throw new IllegalArgumentException();return new Box(hotbar.x()+index*24,hotbar.y(),24,24); }
    public Box app(int index) { return new Box(phone.x()+9+(index%4)*37,phone.y()+28+(index/4)*25,34,23); }
    public Box homeButton(){return new Box(phone.x()+9,phone.bottom()-21,70,14);}
    public Box guideButton(){return new Box(phone.x()+86,phone.bottom()-21,70,14);}
}
