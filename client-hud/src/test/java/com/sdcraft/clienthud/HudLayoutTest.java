package com.sdcraft.clienthud;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class HudLayoutTest {
    @Test void fourCornersRemainSeparateAtSmallLargeAndUltrawideGuiScales(){
        for(int[] size:new int[][]{{320,180},{480,300},{640,360},{960,540},{1720,720},{240,150}}){
            HudLayout l=HudLayout.of(size[0],size[1]);
            assertTrue(l.hotbar().x()<l.width()/2);assertTrue(l.status().x()>l.width()/2);
            assertTrue(l.map().y()>l.height()/2-10);assertTrue(l.phone().right()<=l.width());
            assertFalse(l.hotbar().overlaps(l.status()));assertFalse(l.map().overlaps(l.phone()));assertFalse(l.status().overlaps(l.phone()));
            assertTrue(l.phone().bottom()<=l.height());assertTrue(l.map().bottom()<=l.height());
        }
    }
    @Test void allNineActualSlotsHaveDistinctHitTargetsAndScaleRoundTrips(){
        for(int[] size:new int[][]{{320,180},{480,300},{1280,720}}){
            HudLayout l=HudLayout.of(size[0],size[1]);
            for(int i=0;i<9;i++){
                HudLayout.Box b=l.slot(i);double px=(b.x()+12)*l.scale(),py=(b.y()+12)*l.scale();
                assertTrue(b.contains(px/l.scale(),py/l.scale()));
                for(int j=0;j<9;j++)if(i!=j)assertFalse(b.overlaps(l.slot(j)));
            }
            assertThrows(IllegalArgumentException.class,()->l.slot(-1));assertThrows(IllegalArgumentException.class,()->l.slot(9));
        }
    }
    @Test void all24AppTargetsFitAboveHomeAndAssistantControls(){
        HudLayout l=HudLayout.of(480,300);
        for(int i=0;i<24;i++){
            HudLayout.Box b=l.app(i);assertTrue(b.x()>l.phone().x());assertTrue(b.right()<l.phone().right());
            assertTrue(b.bottom()<l.homeButton().y());
            for(int j=i+1;j<24;j++)assertFalse(b.overlaps(l.app(j)));
        }
    }
}
