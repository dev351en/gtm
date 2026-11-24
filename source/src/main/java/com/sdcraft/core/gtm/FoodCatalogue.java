package com.sdcraft.core.gtm;

import java.util.*;

/** Original fictional food catalogue. Prices are ARK cents, not real currency. */
public final class FoodCatalogue {
    private FoodCatalogue() {}
    public record Meal(String id,String name,long cents,int portions) {
        public Meal {
            if(id==null||!id.matches("[a-z_]{1,32}")||name==null||name.isBlank()||cents<=0||portions<1||portions>4)
                throw new IllegalArgumentException("Invalid meal");
        }
    }
    public static final List<Meal> ITEMS=List.of(
        new Meal("chai","Chai",1000,1),new Meal("vada_pav","Vada pav",2000,1),
        new Meal("samosa","Samosa",2000,1),new Meal("dabeli","Dabeli",2500,1),
        new Meal("pav_bhaji","Pav bhaji",6000,2),new Meal("dosa","Dosa",5500,2),
        new Meal("idli","Idli",3500,2),new Meal("thali","Gujarati thali",8500,3),
        new Meal("biryani","Biryani",9000,3),new Meal("lassi","Lassi",3000,1),
        new Meal("dhokla", "Khaman dhokla", 3000, 1),
        new Meal("khandvi", "Khandvi", 3500, 1),
        new Meal("poha", "Kanda poha", 3000, 1),
        new Meal("misal", "Misal", 6500, 1),
        new Meal("upma", "Upma", 3500, 1),
        new Meal("puran_poli", "Puran poli", 4500, 1),
        new Meal("bhakri", "Bhakri", 2500, 1),
        new Meal("thepla", "Methi thepla", 3000, 1),
        new Meal("modak", "Ukadiche modak", 2500, 1),
        new Meal("jalebi", "Jalebi", 3000, 1),
        new Meal("kulfi", "Pista kulfi", 3500, 1),
        new Meal("falooda", "Rose falooda", 6500, 1),
        new Meal("nimbu_pani", "Nimbu pani", 2000, 1),
        new Meal("filter_coffee", "Filter coffee", 2500, 1),
        new Meal("kathi_roll", "Kathi roll", 5500, 1),
        new Meal("pani_puri", "Pani puri", 3000, 1),
        new Meal("sev_puri", "Sev puri", 3500, 1),
        new Meal("ragda", "Ragda pattice", 5000, 1),
        new Meal("sandesh", "Sandesh", 3000, 1),
        new Meal("sheera", "Rava sheera", 3500, 1));
    public static Meal get(String id){return ITEMS.stream().filter(m->m.id().equals(id)).findFirst().orElseThrow(()->new IllegalArgumentException("Unknown meal"));}
    public static boolean validBrand(String s){return "zomatoo".equals(s)||"swiffy".equals(s);}
    public record Ticket(UUID id,String brand,String meal,long price,String vendor,UUID customer,long readyAt,Phase phase) {
        public Ticket {
            Objects.requireNonNull(id);Objects.requireNonNull(customer);Objects.requireNonNull(phase);
            if(!validBrand(brand)||!get(meal).id().equals(meal)||price<=0||price>100000000L||vendor==null||!vendor.matches("[a-z0-9_-]{1,40}")||readyAt<0)
                throw new IllegalArgumentException("Invalid order");
        }
        public boolean open(){return phase==Phase.ORDERED;}
        public boolean ready(long now){return open()&&now>=readyAt;}
        public Ticket close(Phase next,long now){
            if(!open()||next==Phase.ORDERED||(next==Phase.COLLECTED&&!ready(now)))throw new IllegalStateException("Invalid food order transition");
            return new Ticket(id,brand,meal,price,vendor,customer,readyAt,next);
        }
    }
    public enum Phase {ORDERED,COLLECTED,REFUNDED}
}
