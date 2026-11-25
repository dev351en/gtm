package com.sdcraft.core;

import com.sdcraft.core.gtm.RegionBounds;
import java.io.IOException;
import java.util.*;
import org.bukkit.*;
import org.bukkit.block.*;
import org.bukkit.block.data.BlockData;
import org.bukkit.block.data.Bisected;
import org.bukkit.block.sign.Side;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.block.*;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.plugin.java.JavaPlugin;

/** Durable public-infrastructure restoration. No configured city zone means no automatic edits. */
public final class RestorationEngine implements Listener {
    public record RestorableZone(String name,String world,int x,int y,int z,int radius) {}
    private record Position(UUID world,int x,int y,int z) {
        String key(){return world+"_"+x+"_"+y+"_"+z;}
        static Position of(Block b){return new Position(b.getWorld().getUID(),b.getX(),b.getY(),b.getZ());}
    }
    private record Record(Position position,String block,long due,List<String> front,List<String> back,
                          String frontColor,String backColor,boolean frontGlow,boolean backGlow,boolean waxed) {}
    private record Scheduled(long at,String key) implements Comparable<Scheduled> {
        public int compareTo(Scheduled other){int time=Long.compare(at,other.at);return time!=0?time:key.compareTo(other.key);}
    }
    private static final int MAX_PENDING=8192,MAX_PLACED=32768;
    private final JavaPlugin plugin;
    private final AtomicYamlStore zonesStore,stateStore;
    private final YamlConfiguration zonesConfig,state;
    private final Map<String,RestorableZone> zones=new LinkedHashMap<>();
    private final Map<String,Record> pending=new LinkedHashMap<>();
    private final Set<String> placed=new HashSet<>();
    private final PriorityQueue<Scheduled> due=new PriorityQueue<>();
    private final List<RegionBounds> properties=new ArrayList<>();
    private final int batch,minY;
    private final long delay;

    public RestorationEngine(JavaPlugin plugin) {
        this.plugin=plugin;
        batch=Math.max(1,Math.min(256,plugin.getConfig().getInt("restoration.batch-per-second",64)));
        minY=plugin.getConfig().getInt("restoration.min-y",55);
        delay=Math.max(120000L,Math.min(600000L,plugin.getConfig().getLong("restoration.delay-ms",300000L)));
        try{
            zonesStore=new AtomicYamlStore(plugin.getDataFolder().toPath().resolve("restorable_zones.yml"));
            stateStore=new AtomicYamlStore(plugin.getDataFolder().toPath().resolve("restoration-state.yml"));
            zonesConfig=zonesStore.data();state=stateStore.data();
            ConfigurationSection section=zonesConfig.getConfigurationSection("zones");
            if(section!=null)for(String name:section.getKeys(false)){
                String p="zones."+name;
                RestorableZone z=new RestorableZone(name,zonesConfig.getString(p+".world","world"),zonesConfig.getInt(p+".x"),zonesConfig.getInt(p+".y"),zonesConfig.getInt(p+".z"),zonesConfig.getInt(p+".radius",50));
                validate(z);zones.put(name,z);
            }
            placed.addAll(state.getStringList("player-placed"));
            if(placed.size()>MAX_PLACED)throw new IOException("Player placement limit exceeded");
            ConfigurationSection records=state.getConfigurationSection("pending");
            if(records!=null)for(String key:records.getKeys(false)){
                String p="pending."+key;
                Position position=new Position(UUID.fromString(state.getString(p+".world","")),state.getInt(p+".x"),state.getInt(p+".y"),state.getInt(p+".z"));
                if(!position.key().equals(key))throw new IOException("Restoration location mismatch");
                String block=state.getString(p+".block","");Bukkit.createBlockData(block);
                Record r=new Record(position,block,state.getLong(p+".due"),state.getStringList(p+".front"),state.getStringList(p+".back"),state.getString(p+".front-color","BLACK"),state.getString(p+".back-color","BLACK"),state.getBoolean(p+".front-glow"),state.getBoolean(p+".back-glow"),state.getBoolean(p+".waxed"));
                DyeColor.valueOf(r.frontColor);DyeColor.valueOf(r.backColor);
                if((!r.front.isEmpty()&&r.front.size()!=4)||(!r.back.isEmpty()&&r.back.size()!=4))throw new IOException("Invalid sign record");
                pending.put(key,r);due.add(new Scheduled(r.due,key));
                if(pending.size()>MAX_PENDING)throw new IOException("Restoration queue limit exceeded");
            }
            for(Map<?,?> row:plugin.getConfig().getMapList("gtm.property-regions"))
                properties.add(new RegionBounds(String.valueOf(row.get("world")),number(row,"min-x"),number(row,"min-y"),number(row,"min-z"),number(row,"max-x"),number(row,"max-y"),number(row,"max-z")));
        }catch(IOException|RuntimeException ex){throw new IllegalStateException("Restoration records invalid; refusing world edits",ex);}
        if(zones.isEmpty())plugin.getLogger().info("Restoration waits for surveyed public-city zones; wilderness remains permanent.");
    }
    private static int number(Map<?,?> row,String key){Object v=row.get(key);if(!(v instanceof Number n))throw new IllegalArgumentException("Invalid property coordinate");return Math.toIntExact(n.longValue());}
    private static void validate(RestorableZone z){
        if(!z.name.matches("[A-Za-z0-9_-]{1,64}")||z.world.isBlank()||z.radius<1||z.radius>512)throw new IllegalArgumentException("Zone needs a name and a radius of 1–512 blocks");
    }
    public void saveZones(){
        zonesConfig.set("zones",null);
        for(var z:zones.values()){
            String p="zones."+z.name;zonesConfig.set(p+".world",z.world);zonesConfig.set(p+".x",z.x);zonesConfig.set(p+".y",z.y);zonesConfig.set(p+".z",z.z);zonesConfig.set(p+".radius",z.radius);
        }
        try{zonesStore.commit();}catch(IOException ex){throw new IllegalStateException("Zone save failed",ex);}
    }
    public boolean markZone(String name,Location location,int radius){
        if(location.getWorld()==null)throw new IllegalArgumentException("Loaded world required");
        RestorableZone next=new RestorableZone(name,location.getWorld().getName(),location.getBlockX(),location.getBlockY(),location.getBlockZ(),radius);validate(next);
        RestorableZone previous=zones.put(name,next);
        try{saveZones();return true;}catch(RuntimeException ex){if(previous==null)zones.remove(name);else zones.put(name,previous);throw ex;}
    }
    public boolean unmarkZone(String name){
        RestorableZone previous=zones.remove(name);if(previous==null)return false;
        try{saveZones();return true;}catch(RuntimeException ex){zones.put(name,previous);throw ex;}
    }
    public Collection<RestorableZone> getZones(){return List.copyOf(zones.values());}
    public int getPendingCount(){return pending.size();}
    private boolean inCity(Block block){
        if(block.getY()<minY)return false;
        for(var z:zones.values())if(z.world.equals(block.getWorld().getName())){
            double x=(double)block.getX()-z.x,d=(double)block.getZ()-z.z;
            if(x*x+d*d<=(double)z.radius*z.radius)return true;
        }return false;
    }
    private boolean privateProperty(Block block){return properties.stream().anyMatch(p->p.contains(block.getWorld().getName(),block.getX(),block.getY(),block.getZ()));}
    private boolean sensitive(Block block){
        var state=block.getState();
        return state instanceof TileState tile && (!(state instanceof Sign)||!tile.getPersistentDataContainer().getKeys().isEmpty());
    }
    public boolean isRestorable(Block block){
        if(!inCity(block)||privateProperty(block)||placed.contains(Position.of(block).key())||sensitive(block))return false;
        Material m=block.getType();
        return !m.isAir()&&m!=Material.FARMLAND&&m!=Material.WHEAT&&m!=Material.CARROTS&&m!=Material.POTATOES&&m!=Material.BEETROOTS&&m!=Material.PUMPKIN_STEM&&m!=Material.MELON_STEM&&m!=Material.SUGAR_CANE;
    }
    private Record capture(Block block){
        Sign sign=block.getState() instanceof Sign s?s:null;
        return new Record(Position.of(block),block.getBlockData().getAsString(),System.currentTimeMillis()+delay,
            sign==null?List.of():List.of(sign.getSide(Side.FRONT).getLines()),sign==null?List.of():List.of(sign.getSide(Side.BACK).getLines()),
            sign==null?"BLACK":sign.getSide(Side.FRONT).getColor().name(),sign==null?"BLACK":sign.getSide(Side.BACK).getColor().name(),
            sign!=null&&sign.getSide(Side.FRONT).isGlowingText(),sign!=null&&sign.getSide(Side.BACK).isGlowingText(),sign!=null&&sign.isWaxed());
    }
    private void write(Record r){
        String p="pending."+r.position.key();state.set(p+".world",r.position.world.toString());state.set(p+".x",r.position.x);state.set(p+".y",r.position.y);state.set(p+".z",r.position.z);state.set(p+".block",r.block);state.set(p+".due",r.due);
        state.set(p+".front",r.front);state.set(p+".back",r.back);state.set(p+".front-color",r.frontColor);state.set(p+".back-color",r.backColor);state.set(p+".front-glow",r.frontGlow);state.set(p+".back-glow",r.backGlow);state.set(p+".waxed",r.waxed);
    }
    private boolean enqueue(Collection<Block> blocks){
        Map<String,Record> additions=new LinkedHashMap<>();
        for(Block b:blocks)if(isRestorable(b)&&!pending.containsKey(Position.of(b).key())){
            Record r=capture(b);additions.put(r.position.key(),r);
        }
        if(additions.isEmpty())return true;
        if(pending.size()+additions.size()>MAX_PENDING)return false;
        additions.values().forEach(this::write);
        try{stateStore.commit();}catch(IOException|RuntimeException ex){plugin.getLogger().warning("Damage prevented because restoration could not be journaled");return false;}
        pending.putAll(additions);additions.forEach((key,r)->due.add(new Scheduled(r.due,key)));return true;
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void onBlockPlace(BlockPlaceEvent event){
        Block b=event.getBlockPlaced();if(!inCity(b))return;
        String key=Position.of(b).key();
        if(pending.containsKey(key)){event.setCancelled(true);event.getPlayer().sendMessage("§ePublic infrastructure is waiting for repair.");return;}
        if(placed.contains(key))return;
        if(placed.size()>=MAX_PLACED){event.setCancelled(true);return;}
        Set<String> next=new HashSet<>(placed);next.add(key);state.set("player-placed",new ArrayList<>(next));
        try{stateStore.commit();placed.add(key);}catch(IOException|RuntimeException ex){event.setCancelled(true);}
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void onBlockBreak(BlockBreakEvent event){
        Player player=event.getPlayer();Block block=event.getBlock();String key=Position.of(block).key();
        if(player.hasPermission("sdcraft.admin")&&player.getGameMode()==GameMode.CREATIVE){
            if(pending.containsKey(key)){state.set("pending."+key,null);try{stateStore.commit();pending.remove(key);}catch(IOException|RuntimeException ex){event.setCancelled(true);}}return;
        }
        if(inCity(block)&&sensitive(block)&&!privateProperty(block)&&!placed.contains(key)){event.setCancelled(true);return;}
        if(!isRestorable(block))return;
        List<Block> group=new ArrayList<>();group.add(block);
        if(block.getBlockData() instanceof Bisected half){
            Block partner=block.getRelative(0,half.getHalf()==Bisected.Half.BOTTOM?1:-1,0);
            if(partner.getType()==block.getType()&&isRestorable(partner))group.add(partner);
        }
        if(!enqueue(group)){event.setCancelled(true);return;}
        event.setDropItems(false);event.setExpToDrop(0);
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void onEntityExplode(EntityExplodeEvent event){explosion(event.blockList(),event);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void onSignEdit(SignChangeEvent event){
        if(pending.containsKey(Position.of(event.getBlock()).key()))event.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void onBlockExplode(BlockExplodeEvent event){explosion(event.blockList(),event);}
    private void explosion(List<Block> blocks,Cancellable event){
        List<Block> controlled=new ArrayList<>();
        for(Iterator<Block> iterator=blocks.iterator();iterator.hasNext();){Block b=iterator.next();
            if(privateProperty(b)||(inCity(b)&&sensitive(b))){iterator.remove();continue;}
            if(isRestorable(b)){controlled.add(b);iterator.remove();}
        }
        // The original yield still applies to untouched wilderness/player-built blocks.
        if(controlled.isEmpty()||!enqueue(controlled))return;
        Bukkit.getScheduler().runTask(plugin,()->{
            if(event.isCancelled())return;
            for(Block b:controlled){Record r=pending.get(Position.of(b).key());
                if(r!=null&&r.block.equals(b.getBlockData().getAsString())&&!privateProperty(b)&&!placed.contains(r.position.key()))b.setType(Material.AIR,false);
            }
        });
    }
    public void tick(){
        long now=System.currentTimeMillis();int examined=0,changed=0;List<String> completed=new ArrayList<>();List<Scheduled> retry=new ArrayList<>();
        while(!due.isEmpty()&&due.peek().at<=now&&examined++<batch*4&&changed<batch){
            Scheduled scheduled=due.poll();Record r=pending.get(scheduled.key);if(r==null)continue;
            World world=Bukkit.getWorld(r.position.world);
            if(world==null||!world.isChunkLoaded(r.position.x>>4,r.position.z>>4)){retry.add(new Scheduled(now+5000,scheduled.key));continue;}
            Block b=world.getBlockAt(r.position.x,r.position.y,r.position.z);
            if(privateProperty(b)||placed.contains(r.position.key())||!inCity(b)||sensitive(b)){completed.add(scheduled.key);continue;}
            if(!b.getType().isAir()){
                if(b.getBlockData().getAsString().equals(r.block)){
                    // Recover the sign-text phase after a crash between block placement and
                    // its tile update. A replacement sign with different text is left intact.
                    if(b.getState() instanceof Sign sign&&r.front.size()==4&&r.back.size()==4){
                        boolean empty=Arrays.stream(sign.getSide(Side.FRONT).getLines()).allMatch(String::isEmpty)
                                &&Arrays.stream(sign.getSide(Side.BACK).getLines()).allMatch(String::isEmpty)
                                &&sign.getSide(Side.FRONT).getColor()==DyeColor.BLACK&&sign.getSide(Side.BACK).getColor()==DyeColor.BLACK
                                &&!sign.getSide(Side.FRONT).isGlowingText()&&!sign.getSide(Side.BACK).isGlowingText()&&!sign.isWaxed();
                        if(empty&&!restoreSign(sign,r)){retry.add(new Scheduled(now+5000,scheduled.key));continue;}
                    }
                    completed.add(scheduled.key);
                }
                else retry.add(new Scheduled(now+30000,scheduled.key));
                continue; // Never overwrite a replacement block or its contents.
            }
            b.setBlockData(Bukkit.createBlockData(r.block),false);
            if(b.getState() instanceof Sign sign&&r.front.size()==4&&r.back.size()==4){
                if(!restoreSign(sign,r)){retry.add(new Scheduled(now+5000,scheduled.key));continue;}
            }
            completed.add(scheduled.key);changed++;
        }
        due.addAll(retry);if(completed.isEmpty())return;
        completed.forEach(key->state.set("pending."+key,null));
        try{stateStore.commit();completed.forEach(pending::remove);}
        catch(IOException|RuntimeException ex){completed.forEach(key->due.add(new Scheduled(now+5000,key)));plugin.getLogger().warning("Restoration checkpoint pending; replay will not overwrite replacement blocks");}
    }
    /** Make repairs eligible now, then execute only one configured batch. */
    public int forceRestoreAll(){
        due.clear();pending.keySet().forEach(key->due.add(new Scheduled(0,key)));int before=pending.size();tick();return before-pending.size();
    }
    private static boolean restoreSign(Sign sign,Record r){
        for(int i=0;i<4;i++){sign.getSide(Side.FRONT).setLine(i,r.front.get(i));sign.getSide(Side.BACK).setLine(i,r.back.get(i));}
        sign.getSide(Side.FRONT).setColor(DyeColor.valueOf(r.frontColor));sign.getSide(Side.BACK).setColor(DyeColor.valueOf(r.backColor));
        sign.getSide(Side.FRONT).setGlowingText(r.frontGlow);sign.getSide(Side.BACK).setGlowingText(r.backGlow);sign.setWaxed(r.waxed);return sign.update(true,false);
    }
}
