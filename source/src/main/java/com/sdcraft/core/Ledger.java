package com.sdcraft.core;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.*;
import java.time.Instant;
import java.util.*;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import org.bukkit.configuration.file.YamlConfiguration;

/** Main-thread-only, atomic-on-disk small server wallet/bank ledger. Vault exposes this wallet. */
final class Ledger {
    private static final int[] PROMOTION_CREDITS = {0, 10, 25, 45, 70, 100, 140};
    private static final long[] PROMOTION_DUTY_MS = {0, 3_600_000L, 10_800_000L, 21_600_000L,
            36_000_000L, 54_000_000L, 79_200_000L};
    private final File file, log;
    private final YamlConfiguration db;
    Ledger(File folder) {
        file = new File(folder,"accounts.yml"); log = new File(folder,"transactions.csv");
        db = YamlConfiguration.loadConfiguration(file);
    }
    private String key(UUID id) { return "accounts."+id.toString(); }
    synchronized boolean register(UUID id) throws IOException {
        String k=key(id);
        if (db.getBoolean(k+".created",false)) return false;
        if (db.contains(k)) throw new IOException("Ambiguous player record: "+id);
        db.set(k+".wallet",50000L); db.set(k+".bank",100000L);
        db.set(k+".created",true); db.set(k+".language","en"); db.set(k+".credits",0); db.set(k+".rank",1);
        save(); append("WELCOME",id,null,150000L,"initial 500 wallet 1000 bank");
        return true;
    }
    synchronized boolean exists(UUID id) { return db.getBoolean(key(id)+".created",false); }
    synchronized long wallet(UUID id) { return db.getLong(key(id)+".wallet",0); }
    synchronized long bank(UUID id) { return db.getLong(key(id)+".bank",0); }
    synchronized String language(UUID id) { return db.getString(key(id)+".language","en"); }
    synchronized int rank(UUID id) { return db.getInt(key(id)+".rank",1); }
    synchronized int credits(UUID id) { return db.getInt(key(id)+".credits",0); }
    synchronized long dutyMs(UUID id) { return db.getLong(key(id)+".dutyMs",0); }
    static int requiredCreditsForRank(int targetRank) {
        if (targetRank < 1 || targetRank > 7) throw new IllegalArgumentException("Invalid rank");
        return PROMOTION_CREDITS[targetRank - 1];
    }
    static long requiredDutyMsForRank(int targetRank) {
        if (targetRank < 1 || targetRank > 7) throw new IllegalArgumentException("Invalid rank");
        return PROMOTION_DUTY_MS[targetRank - 1];
    }
    synchronized boolean eligibleForPromotion(UUID id) {
        require(id);
        int next = rank(id) + 1;
        return next <= 7 && credits(id) >= requiredCreditsForRank(next)
                && dutyMs(id) >= requiredDutyMsForRank(next);
    }
    synchronized boolean approvePromotion(UUID id, String approver) throws IOException {
        require(id);
        if (approver == null || approver.isBlank()) throw new IllegalArgumentException("Approver required");
        if (!eligibleForPromotion(id)) return false;
        int next = rank(id) + 1;
        db.set(key(id)+".rank",next);
        save();append("PROMOTION",id,null,0L,"rank="+next+" approved-by="+approver);
        return true;
    }
    synchronized void language(UUID id,String lang) throws IOException {
        if (!lang.equals("hi")&&!lang.equals("en")) throw new IllegalArgumentException("Unknown language");
        require(id); db.set(key(id)+".language",lang); save();
    }
    synchronized void pin(UUID id,String pass) throws Exception {
        require(id); if (!pass.matches("[0-9]{4,8}")) throw new IllegalArgumentException("PIN must be 4–8 digits");
        byte[] salt=new byte[16]; new SecureRandom().nextBytes(salt);
        db.set(key(id)+".pinSalt",Base64.getEncoder().encodeToString(salt));
        db.set(key(id)+".pinHash",Base64.getEncoder().encodeToString(derive(pass,salt)));
        save();
    }
    synchronized boolean hasPin(UUID id) {return db.contains(key(id)+".pinHash");}
    synchronized boolean verifyPin(UUID id,String pass) {
        try {
            String salt=db.getString(key(id)+".pinSalt","");
            String hash=db.getString(key(id)+".pinHash","");
            return !hash.isBlank()&&MessageDigest.isEqual(Base64.getDecoder().decode(hash),derive(pass,Base64.getDecoder().decode(salt)));
        } catch(Exception e) {return false;}
    }
    private byte[] derive(String pass, byte[] salt) throws Exception {
        PBEKeySpec spec=new PBEKeySpec(pass.toCharArray(),salt,160000,256);
        try {return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).getEncoded();}
        finally{spec.clearPassword();}
    }
    private void require(UUID id) {if(!exists(id)) throw new IllegalStateException("No account: "+id);}
    private void checkAmount(long a) {if(a<=0||a>100000000000L)throw new IllegalArgumentException("Invalid amount");}
    synchronized boolean deposit(UUID id,long cents) throws IOException {
        require(id);checkAmount(cents); if(wallet(id)<cents)return false;
        db.set(key(id)+".wallet",wallet(id)-cents);db.set(key(id)+".bank",Math.addExact(bank(id),cents));
        save();append("DEPOSIT",id,null,cents,"");return true;
    }
    synchronized boolean withdraw(UUID id,long cents) throws IOException {
        require(id);checkAmount(cents); if(bank(id)<cents)return false;
        db.set(key(id)+".bank",bank(id)-cents);db.set(key(id)+".wallet",Math.addExact(wallet(id),cents));
        save();append("WITHDRAW",id,null,cents,"");return true;
    }
    synchronized boolean transfer(UUID from,UUID to,long cents) throws IOException {
        require(from);require(to);checkAmount(cents);
        if(from.equals(to)||bank(from)<cents)return false;
        db.set(key(from)+".bank",bank(from)-cents);
        db.set(key(to)+".bank",Math.addExact(bank(to),cents));
        save();append("TRANSFER",from,to,cents,"");return true;
    }
    synchronized boolean chargeWallet(UUID id,long cents,String reason) throws IOException {
        require(id); checkAmount(cents);if(wallet(id)<cents)return false;
        db.set(key(id)+".wallet",wallet(id)-cents);save();append("SPEND",id,null,cents,reason);return true;
    }
    synchronized void creditWallet(UUID id,long cents,String reason) throws IOException {
        require(id);checkAmount(cents);
        db.set(key(id)+".wallet",Math.addExact(wallet(id),cents));
        save();append("WALLET_CREDIT",id,null,cents,reason);
    }
    synchronized boolean chargeBank(UUID id,long cents,String reason) throws IOException {
        require(id); checkAmount(cents);if(bank(id)<cents)return false;
        db.set(key(id)+".bank",bank(id)-cents);save();append("BANK_SPEND",id,null,cents,reason);return true;
    }
    synchronized void reward(UUID id,long cents,String reason) throws IOException {
        require(id);checkAmount(cents);db.set(key(id)+".bank",Math.addExact(bank(id),cents));
        save();append("EARN",id,null,cents,reason);
    }
    synchronized void rewardCareer(UUID id,long cents,int addCredits,String reason) throws IOException {
        require(id);checkAmount(cents);
        if(addCredits<0||addCredits>3)throw new IllegalArgumentException("Invalid career credits");
        db.set(key(id)+".bank",Math.addExact(bank(id),cents));
        int total=Math.addExact(credits(id),addCredits);
        db.set(key(id)+".credits",total);
        save();append("MISSION",id,null,cents,reason+" credits="+addCredits);
    }
    synchronized void grantDuty(UUID id,long cents,long ms,int addCredits,String reason) throws IOException {
        require(id);
        if(cents<0||ms<0||addCredits<0||addCredits>3)throw new IllegalArgumentException("Invalid duty grant");
        db.set(key(id)+".bank",Math.addExact(bank(id),cents));
        db.set(key(id)+".dutyMs",Math.addExact(dutyMs(id),ms));
        db.set(key(id)+".credits",Math.addExact(credits(id),addCredits));
        save();append("DUTY",id,null,cents,reason+" credit="+addCredits);
    }
    synchronized boolean rob(UUID robber,UUID victim,long cents) throws IOException {
        require(robber);require(victim);checkAmount(cents);
        if(robber.equals(victim)||cents>PolicyEngine.robberyMaximumCents(wallet(victim)))return false;
        db.set(key(victim)+".wallet",wallet(victim)-cents);
        db.set(key(robber)+".wallet",Math.addExact(wallet(robber),cents));
        save();append("ROBBERY",robber,victim,cents,"validated");return true;
    }
    private void save() throws IOException {
        Path target=file.toPath(); Files.createDirectories(target.getParent());
        Path temp=Files.createTempFile(target.getParent(),"account-",".tmp");
        try {Files.writeString(temp,db.saveToString(),StandardCharsets.UTF_8);
            try {Files.move(temp,target,StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}
            catch(AtomicMoveNotSupportedException e){Files.move(temp,target,StandardCopyOption.REPLACE_EXISTING);}
        } finally {Files.deleteIfExists(temp);}
    }
    private void append(String type,UUID from,UUID to,long cents,String extra) throws IOException {
        String safe=extra.replace(',',' ').replace('\n',' ').replace('\r',' ');
        String line=Instant.now()+","+UUID.randomUUID()+","+type+","+from+","+(to==null?"":to)+","+cents+","+safe+"\n";
        Files.writeString(log.toPath(),line,StandardCharsets.UTF_8,StandardOpenOption.CREATE,StandardOpenOption.APPEND);
    }
}
