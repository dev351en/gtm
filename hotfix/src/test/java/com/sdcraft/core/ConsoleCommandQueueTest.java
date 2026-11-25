package com.sdcraft.core;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ConsoleCommandQueueTest {
    private static final class HeldScheduler implements ConsoleCommandQueue.Scheduler {
        Runnable pending;
        int cancelled;
        @Override public ConsoleCommandQueue.Cancellation schedule(Runnable task) { pending = task; return () -> cancelled++; }
        void run() { Runnable task = pending; pending = null; task.run(); }
    }

    @Test void auditIntentPrecedesRealDispatchAndCompletionReleasesSlot() {
        var scheduler = new HeldScheduler(); var events = new ArrayList<String>();
        var queue = new ConsoleCommandQueue(scheduler, command -> { events.add("dispatch:" + command); return true; },
                (id, phase, command, outcome) -> events.add(phase));
        var ticket = queue.submit("list");
        assertTrue(queue.busy()); assertFalse(ticket.result().isDone());
        scheduler.run();
        assertEquals(List.of("START", "dispatch:list", "RESULT"), events);
        assertTrue(ticket.result().join().accepted()); assertFalse(queue.busy());
    }

    @Test void failedAuditPreventsActionAndReleasesSlot() {
        var scheduler = new HeldScheduler(); var calls = new AtomicInteger();
        var queue = new ConsoleCommandQueue(scheduler, command -> { calls.incrementAndGet(); return true; },
                (id, phase, command, outcome) -> { throw new IOException("audit unavailable"); });
        var ticket = queue.submit("save-all flush"); scheduler.run();
        assertEquals(0, calls.get()); assertTrue(ticket.result().isCompletedExceptionally()); assertFalse(queue.busy());
    }

    @Test void failureAfterActionIsReportedAsExecutedWithAuditWarning() {
        var scheduler = new HeldScheduler(); var calls = new AtomicInteger();
        var queue = new ConsoleCommandQueue(scheduler, command -> { calls.incrementAndGet(); return true; },
                (id, phase, command, outcome) -> { if (phase.equals("RESULT")) throw new IOException("disk filled"); });
        var ticket = queue.submit("save-all flush"); scheduler.run();
        assertEquals(1, calls.get()); assertTrue(ticket.result().join().accepted());
        assertTrue(ticket.result().join().auditWarning().contains("command ran")); assertFalse(queue.busy());
    }

    @Test void waitingTimeoutCancelsWithoutAuditOrExecution() {
        var scheduler = new HeldScheduler(); var calls = new AtomicInteger();
        var queue = new ConsoleCommandQueue(scheduler, command -> { calls.incrementAndGet(); return true; },
                (id, phase, command, outcome) -> calls.incrementAndGet());
        var ticket = queue.submit("save-all flush");
        assertTrue(ticket.cancelBeforeStart()); assertFalse(ticket.cancelBeforeStart());
        scheduler.run();
        assertEquals(0, calls.get()); assertEquals(1, scheduler.cancelled);
        assertTrue(ticket.result().isCancelled()); assertFalse(queue.busy());
    }

    @Test void runningTimeoutCannotCancelOrAdmitASecondCommand() throws Exception {
        var scheduler = new HeldScheduler(); var running = new CountDownLatch(1); var finish = new CountDownLatch(1);
        var queue = new ConsoleCommandQueue(scheduler, command -> { running.countDown(); if (!finish.await(2, TimeUnit.SECONDS)) throw new AssertionError("test timed out"); return true; },
                (id, phase, command, outcome) -> {});
        var ticket = queue.submit("save-all flush");
        Thread worker = Thread.ofPlatform().start(scheduler::run);
        try {
            assertTrue(running.await(1, TimeUnit.SECONDS));
            assertFalse(ticket.cancelBeforeStart());
            assertTrue(queue.busy());
            assertThrows(ConsoleCommandQueue.Busy.class, () -> queue.submit("save-all flush"));
        } finally { finish.countDown(); worker.join(2000); }
        assertTrue(ticket.result().get(1, TimeUnit.SECONDS).accepted()); assertFalse(queue.busy());
    }

    @Test void schedulerRejectionDoesNotLeaveTheConsoleBusy() {
        var queue = new ConsoleCommandQueue(task -> { throw new IllegalStateException("plugin disabled"); }, command -> true,
                (id, phase, command, outcome) -> {});
        assertThrows(IllegalStateException.class, () -> queue.submit("list"));
        assertFalse(queue.busy());
    }

    @Test void dispatchFailureReleasesTheSlotAndPreservesIntent() {
        var scheduler = new HeldScheduler(); var phases = new ArrayList<String>();
        var queue = new ConsoleCommandQueue(scheduler, command -> { throw new IllegalStateException("unknown adapter failure"); },
                (id, phase, command, outcome) -> phases.add(phase));
        var ticket = queue.submit("list"); scheduler.run();
        assertEquals(List.of("START"), phases); assertTrue(ticket.result().isCompletedExceptionally()); assertFalse(queue.busy());
    }

    @Test void closeCancelsWaitingWorkAndRefusesNewCommands() {
        var scheduler = new HeldScheduler(); var calls = new AtomicInteger();
        var queue = new ConsoleCommandQueue(scheduler, command -> { calls.incrementAndGet(); return true; }, (id, phase, command, outcome) -> {});
        var ticket = queue.submit("list"); queue.close(); queue.close(); scheduler.run();
        assertTrue(ticket.result().isCancelled()); assertEquals(0, calls.get()); assertFalse(queue.busy());
        assertThrows(IllegalStateException.class, () -> queue.submit("list"));
    }

    @Test void lifecycleCommandCanCloseItsOwnConsoleWithoutDeadlocking() {
        var scheduler = new HeldScheduler(); var holder = new ConsoleCommandQueue[1];
        holder[0] = new ConsoleCommandQueue(scheduler, command -> { holder[0].close(); return true; }, (id, phase, command, outcome) -> {});
        var ticket = holder[0].submit("stop"); scheduler.run();
        assertTrue(ticket.result().join().accepted()); assertFalse(holder[0].busy());
        assertThrows(IllegalStateException.class, () -> holder[0].submit("list"));
    }

    @Test void unrecognizedConsoleCommandIsNotReportedAsRecognized() {
        var scheduler = new HeldScheduler();
        var queue = new ConsoleCommandQueue(scheduler, command -> false, (id, phase, command, outcome) -> {});
        var ticket = queue.submit("unknown-command"); scheduler.run();
        assertFalse(ticket.result().join().accepted()); assertEquals("unknown-command", ticket.result().join().command());
        assertEquals(ticket.id(), ticket.result().join().id());
    }
}
