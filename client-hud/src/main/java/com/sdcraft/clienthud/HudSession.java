package com.sdcraft.clienthud;

/** Clears private state on revocation, disconnect or expiry; rejects stale snapshots. */
public final class HudSession {
    private HudState state;
    private long receivedAt;
    private long actionSequence;
    private String openedSession="";
    private long openedRevision=-1;
    public static final long EXPIRES_MILLIS = 10_000;

    public boolean accept(HudState next,long now) {
        if (next==null) { clear(); return true; }
        if (state!=null&&state.session().equals(next.session())&&next.revision()<state.revision()) return false;
        if (state==null||!state.session().equals(next.session())) actionSequence=0;
        state=next; receivedAt=now; return true;
    }
    public HudState current(long now) {
        if (state!=null&&(now<receivedAt||now-receivedAt>EXPIRES_MILLIS)) clear();
        return state;
    }
    public long nextSequence() { return ++actionSequence; }
    public boolean consumeOpenPhone(long now) {
        HudState s=current(now);
        if(s==null||!s.openPhone()||(s.session().equals(openedSession)&&s.revision()<=openedRevision))return false;
        openedSession=s.session();openedRevision=s.revision();return true;
    }
    public void clear() { state=null;receivedAt=0;actionSequence=0;openedSession="";openedRevision=-1; }
}
