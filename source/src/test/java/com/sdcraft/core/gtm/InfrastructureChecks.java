package com.sdcraft.core.gtm;
import java.util.*;
import java.io.*;
import java.nio.file.*;
import static com.sdcraft.core.gtm.RouteGraph.*;
public final class InfrastructureChecks {
    private static int n;
    private static void check(boolean ok) { n++; if(!ok) throw new AssertionError("Check "+n); }
    @FunctionalInterface interface Action { void run() throws Exception; }
    private static void rejects(Class<? extends Exception> type,Action r) throws Exception { try { r.run(); throw new AssertionError("Expected "+type); } catch(Exception e) { if(!type.isInstance(e)) throw e; n++; } }
    public static void main(String[] args) throws Exception {
        Path root=Files.createTempDirectory("gtm-test");
        try {
            Path file=root.resolve("state.bin"); SnapshotStore s=new SnapshotStore(file,32);
            check(s.read().version()==0); check(s.read().payload().length==0);
            UUID op=UUID.randomUUID(); byte[] data={1,2,3}; var one=s.commit(0,op,data); data[0]=99;
            check(one.version()==1); check(one.payload()[0]==1); one.payload()[0]=88; check(one.payload()[0]==1);
            var reopened=new SnapshotStore(file,32); check(Arrays.equals(reopened.read().payload(),new byte[]{1,2,3}));
            check(reopened.commit(0,op,new byte[]{1,2,3}).version()==1);
            rejects(IllegalStateException.class,()->s.commit(0,op,new byte[]{9}));
            rejects(ConcurrentModificationException.class,()->s.commit(0,UUID.randomUUID(),new byte[]{9}));
            rejects(IllegalArgumentException.class,()->s.commit(1,UUID.randomUUID(),new byte[33]));
            check(s.read().version()==1); var two=s.commit(1,UUID.randomUUID(),new byte[]{4}); check(two.version()==2);
            rejects(ConcurrentModificationException.class,()->s.commit(0,op,new byte[]{1,2,3}));
            byte[] bytes=Files.readAllBytes(file); bytes[bytes.length-1]^=1; Files.write(file,bytes);
            rejects(IOException.class,s::read); rejects(IOException.class,()->s.commit(2,UUID.randomUUID(),new byte[]{1}));
            Files.write(file,new byte[]{1}); rejects(IOException.class,s::read);
        } finally { try(var paths=Files.walk(root)){for(Path p:paths.sorted(Comparator.reverseOrder()).toList())Files.deleteIfExists(p);} }
        var nodes=List.of(new Node("a",0,0,0),new Node("b",1,0,0),new Node("c",2,0,0),new Node("d",3,0,0));
        var links=List.of(new Edge("a","b",Mode.ROAD,2),new Edge("b","c",Mode.ROAD,2),new Edge("a","c",Mode.ROAD,7),new Edge("a","c",Mode.METRO,1),new Edge("c","d",Mode.WALK,1));
        var graph=new RouteGraph(nodes,links); var road=Set.of(Mode.ROAD); var empty=Set.<String>of();
        check(graph.route("a","c",road,empty).orElseThrow().nodes().equals(List.of("a","b","c")));
        check(graph.route("a","c",road,empty).orElseThrow().cost()==4);
        check(graph.route("a","c",road,Set.of("b")).orElseThrow().cost()==7);
        check(graph.route("a","c",Set.of(Mode.METRO),empty).orElseThrow().cost()==1);
        check(graph.route("c","a",road,empty).isEmpty()); check(graph.route("a","d",road,empty).isEmpty());
        check(graph.route("a","d",Set.of(Mode.METRO,Mode.WALK),empty).orElseThrow().cost()==2);
        check(graph.route("a","a",road,empty).orElseThrow().cost()==0);
        check(graph.route("a","c",road,Set.of("c")).isEmpty()); check(graph.route("z","a",road,empty).isEmpty());
        rejects(IllegalArgumentException.class,()->new Edge("a","b",Mode.ROAD,Double.NaN));
        rejects(IllegalArgumentException.class,()->new RouteGraph(nodes,List.of(new Edge("a","z",Mode.ROAD,1))));
        rejects(IllegalArgumentException.class,()->new RouteGraph(List.of(nodes.getFirst(),nodes.getFirst()),links));
        System.out.println("GTM infrastructure: "+n+" checks passed");
    }
}
