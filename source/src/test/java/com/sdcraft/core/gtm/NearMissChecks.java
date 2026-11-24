package com.sdcraft.core.gtm;
public final class NearMissChecks {
    private static int n;
    private static void check(boolean ok){n++;if(!ok)throw new AssertionError("Check "+n);}
    public static void main(String[] args){
        check(NearMiss.approaching(3,0,0,.5,0));
        check(NearMiss.approaching(3,1,1,.5,0));
        check(!NearMiss.approaching(3,0,2,.5,0));
        check(!NearMiss.approaching(-3,0,0,.5,0));
        check(!NearMiss.approaching(3,0,0,0,0));
        check(!NearMiss.approaching(3,3,0,.5,0));
        check(!NearMiss.approaching(3,0,0,.2,0));
        check(!NearMiss.approaching(3,0,0,5,0));
        check(!NearMiss.approaching(Double.NaN,0,0,.5,0));
        check(!NearMiss.approaching(0,0,0,.5,0));
        check(NearMiss.approaching(0,0,-3,0,-.5));
        check(!NearMiss.approaching(7,0,0,1,0));
        System.out.println("GTM near-miss: "+n+" checks passed");
    }
}
