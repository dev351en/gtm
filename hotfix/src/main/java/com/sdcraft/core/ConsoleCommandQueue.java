package com.sdcraft.core;

import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicReference;

/** One real console action at a time, including after its HTTP caller times out. */
final class ConsoleCommandQueue implements AutoCloseable {
    interface Cancellation { void cancel(); }
    interface Scheduler { Cancellation schedule(Runnable task); }
    interface Dispatcher { boolean dispatch(String command) throws Exception; }
    interface Audit { void record(UUID id, String phase, String command, String outcome) throws Exception; }
    record Result(UUID id, String command, boolean accepted, String auditWarning) {}
    enum State { WAITING, RUNNING, FINISHED, CANCELLED }

    private final Scheduler scheduler;
    private final Dispatcher dispatcher;
    private final Audit audit;
    private Ticket active;
    private boolean closed;

    ConsoleCommandQueue(Scheduler scheduler, Dispatcher dispatcher, Audit audit) {
        this.scheduler = scheduler; this.dispatcher = dispatcher; this.audit = audit;
    }

    synchronized Ticket submit(String command) {
        if (closed) throw new IllegalStateException("The server console is closing.");
        if (active != null) throw new Busy();
        Ticket ticket = new Ticket(command);
        active = ticket;
        try {
            ticket.scheduled = scheduler.schedule(ticket::run);
            // Close/cancellation can win while the scheduler was accepting work.
            if (ticket.state.get() == State.CANCELLED) ticket.scheduled.cancel();
            return ticket;
        } catch (RuntimeException rejected) {
            ticket.state.set(State.CANCELLED);
            release(ticket);
            ticket.result.completeExceptionally(rejected);
            throw rejected;
        }
    }

    synchronized boolean busy() { return active != null; }

    private synchronized void release(Ticket ticket) {
        if (active == ticket) active = null;
    }

    @Override public synchronized void close() {
        closed = true;
        if (active != null) active.cancelBeforeStart();
        // A running command can itself stop/reload the server. Do not block the
        // main thread or promise cancellation once its action has begun.
    }

    final class Ticket {
        private final UUID id = UUID.randomUUID();
        private final String command;
        private final AtomicReference<State> state = new AtomicReference<>(State.WAITING);
        private final CompletableFuture<Result> result = new CompletableFuture<>();
        private volatile Cancellation scheduled;

        private Ticket(String command) { this.command = command; }
        UUID id() { return id; }
        CompletableFuture<Result> result() { return result; }

        boolean cancelBeforeStart() {
            if (!state.compareAndSet(State.WAITING, State.CANCELLED)) return false;
            Cancellation task = scheduled;
            try { if (task != null) task.cancel(); }
            catch (RuntimeException ignored) { /* State gate still prevents a queued callback from executing. */ }
            finally { release(this); result.cancel(false); }
            return true;
        }

        private void run() {
            if (!state.compareAndSet(State.WAITING, State.RUNNING)) return;
            try {
                // Failure to record the intent means the action never executes.
                audit.record(id, "START", command, "pending");
                boolean accepted = dispatcher.dispatch(command);
                String warning = "";
                try { audit.record(id, "RESULT", command, Boolean.toString(accepted)); }
                catch (Exception unavailable) { warning = "The command ran, but its final audit entry could not be written. Its START entry was recorded; check the server log before retrying."; }
                result.complete(new Result(id, command, accepted, warning));
            } catch (Exception failure) {
                result.completeExceptionally(failure);
            } finally {
                state.set(State.FINISHED);
                release(this);
            }
        }
    }

    static final class Busy extends IllegalStateException {
        Busy() { super("A command is already running. Wait for its result in the server log."); }
    }
}
