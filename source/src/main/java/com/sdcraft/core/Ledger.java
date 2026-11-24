package com.sdcraft.core;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import com.sdcraft.core.gtm.CivicRules.Loan;
import org.bukkit.configuration.InvalidConfigurationException;
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
    private YamlConfiguration db;
    private String committed;
    Ledger(File folder) {
        file = new File(folder,"accounts.yml"); log = new File(folder,"transactions.csv");
        db = new YamlConfiguration();
        try {
            if (file.exists()) db.load(file);
            committed = db.saveToString();
        } catch (IOException | InvalidConfigurationException e) {
            throw new IllegalStateException("Cannot load accounts.yml; refusing to replace player records", e);
        }
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
        String hash=Base64.getEncoder().encodeToString(derive(pass,salt));
        db.set(key(id)+".pinSalt",Base64.getEncoder().encodeToString(salt));
        db.set(key(id)+".pinHash",hash);
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
        long nextBank=Math.addExact(bank(id),cents);
        db.set(key(id)+".wallet",wallet(id)-cents);db.set(key(id)+".bank",nextBank);
        save();append("DEPOSIT",id,null,cents,"");return true;
    }
    synchronized boolean withdraw(UUID id,long cents) throws IOException {
        require(id);checkAmount(cents); if(bank(id)<cents)return false;
        long nextWallet=Math.addExact(wallet(id),cents);
        db.set(key(id)+".bank",bank(id)-cents);db.set(key(id)+".wallet",nextWallet);
        save();append("WITHDRAW",id,null,cents,"");return true;
    }
    synchronized boolean transfer(UUID from,UUID to,long cents) throws IOException {
        require(from);require(to);checkAmount(cents);
        if(from.equals(to)||bank(from)<cents)return false;
        long nextBank=Math.addExact(bank(to),cents);
        db.set(key(from)+".bank",bank(from)-cents);
        db.set(key(to)+".bank",nextBank);
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
        long nextBank=Math.addExact(bank(id),cents);
        int total=Math.addExact(credits(id),addCredits);
        db.set(key(id)+".bank",nextBank);
        db.set(key(id)+".credits",total);
        save();append("MISSION",id,null,cents,reason+" credits="+addCredits);
    }
    synchronized void grantDuty(UUID id,long cents,long ms,int addCredits,String reason) throws IOException {
        require(id);
        if(cents<0||ms<0||addCredits<0||addCredits>3)throw new IllegalArgumentException("Invalid duty grant");
        long nextBank=Math.addExact(bank(id),cents), nextDuty=Math.addExact(dutyMs(id),ms);
        int nextCredits=Math.addExact(credits(id),addCredits);
        db.set(key(id)+".bank",nextBank);
        db.set(key(id)+".dutyMs",nextDuty);
        db.set(key(id)+".credits",nextCredits);
        save();append("DUTY",id,null,cents,reason+" credit="+addCredits);
    }
    synchronized boolean rob(UUID robber,UUID victim,long cents) throws IOException {
        require(robber);require(victim);checkAmount(cents);
        if(robber.equals(victim)||cents>PolicyEngine.robberyMaximumCents(wallet(victim)))return false;
        long nextWallet=Math.addExact(wallet(robber),cents);
        db.set(key(victim)+".wallet",wallet(victim)-cents);
        db.set(key(robber)+".wallet",nextWallet);
        save();append("ROBBERY",robber,victim,cents,"validated");return true;
    }
    /** One current loan per account; account balance and debt are in the same committed file. */
    record LoanAccount(UUID id, Loan terms, int activeSeconds) {
        LoanAccount {
            Objects.requireNonNull(id); Objects.requireNonNull(terms);
            if(activeSeconds<0||activeSeconds>=1800) throw new IllegalArgumentException("Invalid loan clock");
        }
    }
    synchronized Optional<LoanAccount> loan(UUID id) {
        require(id); String p=key(id)+".gtm-loan";
        if(!db.contains(p)) return Optional.empty();
        for(String field:List.of("id","principal","total","days","grace","elapsed","paid","active-seconds"))
            if(!db.contains(p+"."+field)) throw new IllegalStateException("Incomplete loan record");
        return Optional.of(new LoanAccount(UUID.fromString(db.getString(p+".id","")),
            new Loan(db.getLong(p+".principal"),db.getLong(p+".total"),db.getInt(p+".days"),db.getInt(p+".grace"),db.getInt(p+".elapsed"),db.getLong(p+".paid")),db.getInt(p+".active-seconds")));
    }
    private void writeLoan(UUID id, LoanAccount account) {
        String p=key(id)+".gtm-loan"; Loan t=account.terms();
        db.set(p+".id",account.id().toString()); db.set(p+".principal",t.principal()); db.set(p+".total",t.total());
        db.set(p+".days",t.days()); db.set(p+".grace",t.grace()); db.set(p+".elapsed",t.elapsed());
        db.set(p+".paid",t.paid()); db.set(p+".active-seconds",account.activeSeconds());
    }
    synchronized boolean issueLoan(UUID id, UUID loanId, long principal, int basisPoints, int days, int grace) throws IOException {
        require(id); Objects.requireNonNull(loanId);
        var existing=loan(id);
        if(existing.isPresent()&&(existing.get().id().equals(loanId)||existing.get().terms().outstanding()>0)) return false;
        var account=new LoanAccount(loanId,Loan.issue(principal,basisPoints,days,grace),0);
        long nextBank=Math.addExact(bank(id),principal);
        db.set(key(id)+".bank",nextBank); writeLoan(id,account);
        save(); append("LOAN_ISSUE",id,null,principal,"loan="+loanId); return true;
    }
    synchronized boolean repayLoan(UUID id, UUID loanId,long expectedPaid,long amount) throws IOException {
        require(id); checkAmount(amount); var a=loan(id).orElseThrow();
        if(!a.id().equals(loanId)||a.terms().paid()!=expectedPaid||bank(id)<amount||amount>a.terms().outstanding()) return false;
        Loan next=a.terms().repay(amount);
        db.set(key(id)+".bank",bank(id)-amount); writeLoan(id,new LoanAccount(a.id(),next,a.activeSeconds()));
        save(); append("LOAN_REPAY",id,null,amount,"loan="+loanId); return true;
    }
    /** Count only verified active play; no debt accrual while the player is offline. */
    synchronized boolean advanceLoanClock(UUID id,int seconds) throws IOException {
        if(seconds<1||seconds>60) throw new IllegalArgumentException("Invalid activity interval");
        var a=loan(id).orElse(null);
        if(a==null||a.terms().outstanding()==0||a.terms().elapsed()>=a.terms().days()+a.terms().grace()) return false;
        int total=a.activeSeconds()+seconds; Loan next=a.terms();
        if(total>=1800) { next=next.advanceActiveDay(); total-=1800; }
        writeLoan(id,new LoanAccount(a.id(),next,total)); save();
        return !a.terms().overdue()&&next.overdue();
    }
    private void save() throws IOException {
        Path target=file.toPath().toAbsolutePath(); Path temp=null;
        try {
            String candidate=db.saveToString();
            Files.createDirectories(target.getParent());
            temp=Files.createTempFile(target.getParent(),"account-",".tmp");
            try(var out=FileChannel.open(temp,StandardOpenOption.WRITE,StandardOpenOption.TRUNCATE_EXISTING)) {
                ByteBuffer bytes=StandardCharsets.UTF_8.encode(candidate);
                while(bytes.hasRemaining()) out.write(bytes);
                out.force(true);
            }
            // Do not use a non-atomic fallback for player funds.
            Files.move(temp,target,StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);
            committed=candidate;
        } catch(IOException|RuntimeException ex) {
            YamlConfiguration restored=new YamlConfiguration();
            try { restored.loadFromString(committed); }
            catch(InvalidConfigurationException impossible) { throw new IllegalStateException("Cannot restore committed accounts",impossible); }
            db=restored; throw ex;
        } finally {
            if(temp!=null) try { Files.deleteIfExists(temp); } catch(IOException ignored) {}
        }
    }
    private void append(String type,UUID from,UUID to,long cents,String extra) {
        // The account snapshot is authoritative. A diagnostic CSV failure must not invite a duplicate payment retry.
        String safe=Objects.toString(extra,"").replace(',',' ').replace('\n',' ').replace('\r',' ');
        String line=Instant.now()+","+UUID.randomUUID()+","+type+","+from+","+(to==null?"":to)+","+cents+","+safe+"\n";
        try { Files.writeString(log.toPath(),line,StandardCharsets.UTF_8,StandardOpenOption.CREATE,StandardOpenOption.APPEND); }
        catch(IOException|RuntimeException e) { java.util.logging.Logger.getLogger("SDCraftCore").severe("Committed account transaction; audit CSV append failed: "+type+" "+from+" "+e.getClass().getSimpleName()); }
    }
}
