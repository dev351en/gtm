package com.sdcraft.core;

import java.util.Objects;
import java.util.UUID;

/** Connection capability is separate from the authenticated account session. */
final class HudSession {
    static final long CAPABILITY_MILLIS = 15_000;
    private long helloAt;
    private UUID login;
    private long sequence;
    private long actionAt = Long.MIN_VALUE;
    private long revision;

    HudSession(long now) { helloAt = now; }
    void hello(long now) { helloAt = now; }
    boolean fresh(long now) { return now >= helloAt && now - helloAt <= CAPABILITY_MILLIS; }
    void authenticate(UUID current) {
        if (!Objects.equals(login, current)) {
            login = current;
            sequence = 0;
            actionAt = Long.MIN_VALUE;
        }
    }
    boolean accept(UUID current, String nonce, long next, long now) {
        if (!fresh(now) || current == null || !current.equals(login)
                || !current.toString().equals(nonce) || next <= sequence
                || next > 9_007_199_254_740_991L || next - sequence > 1_000_000
                || (actionAt != Long.MIN_VALUE && now - actionAt < 200)) return false;
        sequence = next;
        actionAt = now;
        return true;
    }
    long revision() { return ++revision; }
}
