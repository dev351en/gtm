package com.sdcraft.core.gtm;

import java.util.*;

/** Shared directed transport graph; surveyed edges only. Costs are positive game travel units. */
public final class RouteGraph {
    public enum Mode { ROAD, LOCAL, METRO, ROPEWAY, WATER, AIR, WALK }
    public record Node(String id, double x, double y, double z) {
        public Node { if (id==null || id.isBlank() || !Double.isFinite(x) || !Double.isFinite(y) || !Double.isFinite(z)) throw new IllegalArgumentException("Invalid node"); }
    }
    public record Edge(String from,String to,Mode mode,double cost) {
        public Edge { Objects.requireNonNull(from); Objects.requireNonNull(to); Objects.requireNonNull(mode); if(from.equals(to)||!Double.isFinite(cost)||cost<=0) throw new IllegalArgumentException("Invalid edge"); }
    }
    public record Route(List<String> nodes,double cost) { public Route { nodes=List.copyOf(nodes); } }
    private record Step(String id,double cost) {}
    private final Map<String,Node> nodes;
    private final Map<String,List<Edge>> edges;
    public RouteGraph(Collection<Node> points,Collection<Edge> links) {
        if(points.size()>100000 || links.size()>500000) throw new IllegalArgumentException("Graph too large");
        Map<String,Node> n=new HashMap<>(); Map<String,List<Edge>> e=new HashMap<>();
        for(Node p:points) if(n.putIfAbsent(p.id(),p)!=null) throw new IllegalArgumentException("Duplicate node");
        for(Edge link:links) {
            if(!n.containsKey(link.from())||!n.containsKey(link.to())) throw new IllegalArgumentException("Unknown endpoint");
            e.computeIfAbsent(link.from(),k->new ArrayList<>()).add(link);
        }
        e.replaceAll((id,list)->list.stream().sorted(Comparator.comparing(Edge::to).thenComparing(Edge::mode).thenComparingDouble(Edge::cost)).toList());
        nodes=Map.copyOf(n); edges=Map.copyOf(e);
    }
    public Optional<Route> route(String from,String to,Set<Mode> modes,Set<String> closedNodes) {
        if(!nodes.containsKey(from)||!nodes.containsKey(to)||modes.isEmpty()||closedNodes.contains(from)||closedNodes.contains(to)) return Optional.empty();
        Map<String,Double> dist=new HashMap<>(); Map<String,String> prev=new HashMap<>();
        var q=new PriorityQueue<Step>(Comparator.comparingDouble(Step::cost).thenComparing(Step::id));
        dist.put(from,0d); q.add(new Step(from,0));
        while(!q.isEmpty()) {
            Step s=q.remove(); if(s.cost()!=dist.get(s.id())) continue;
            if(s.id().equals(to)) {
                List<String> path=new ArrayList<>(); for(String p=to;p!=null;p=prev.get(p)) path.add(p);
                Collections.reverse(path); return Optional.of(new Route(path,s.cost()));
            }
            for(Edge edge:edges.getOrDefault(s.id(),List.of())) {
                if(!modes.contains(edge.mode())||closedNodes.contains(edge.to())) continue;
                double next=s.cost()+edge.cost();
                if(Double.isFinite(next)&&next<dist.getOrDefault(edge.to(),Double.POSITIVE_INFINITY)) { dist.put(edge.to(),next); prev.put(edge.to(),s.id()); q.add(new Step(edge.to(),next)); }
            }
        }
        return Optional.empty();
    }
}
