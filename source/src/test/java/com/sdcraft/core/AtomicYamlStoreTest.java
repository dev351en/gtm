package com.sdcraft.core;

import java.io.IOException;
import java.nio.file.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import static org.junit.jupiter.api.Assertions.*;

final class AtomicYamlStoreTest {
    @TempDir Path dir;

    @Test void committedStateSurvivesReopen() throws Exception {
        Path file=dir.resolve("gta-state.yml");
        AtomicYamlStore store=new AtomicYamlStore(file);
        store.data().set("player.wanted",3);store.commit();
        assertEquals(3,new AtomicYamlStore(file).data().getInt("player.wanted"));
    }

    @Test void failedSaveRollsBackAndPreservesOriginal() throws Exception {
        Path file=dir.resolve("gta-state.yml"), backup=dir.resolve("original.yml");
        AtomicYamlStore store=new AtomicYamlStore(file);
        store.data().set("starter-claimed",false);store.commit();
        byte[] original=Files.readAllBytes(file);
        Files.move(file,backup);Files.createDirectory(file);
        store.data().set("starter-claimed",true);
        assertThrows(IOException.class,store::commit);
        assertFalse(store.data().getBoolean("starter-claimed"));
        assertArrayEquals(original,Files.readAllBytes(backup));
        Files.delete(file);Files.move(backup,file);
        store.data().set("starter-claimed",true);store.commit();
        assertTrue(new AtomicYamlStore(file).data().getBoolean("starter-claimed"));
    }

    @Test void externalChangesAreNeverOverwritten() throws Exception {
        Path file=dir.resolve("gta-state.yml");Files.writeString(file,"wanted: 1\n");
        AtomicYamlStore store=new AtomicYamlStore(file);
        Files.writeString(file,"wanted: 2\n");store.data().set("wanted",5);
        assertThrows(IOException.class,store::commit);
        assertEquals(1,store.data().getInt("wanted"));
        assertEquals("wanted: 2\n",Files.readString(file));
    }

    @Test void malformedExistingStateIsPreserved() throws Exception {
        Path file=dir.resolve("gta-state.yml");Files.writeString(file,"players: [broken\n");
        assertThrows(IOException.class,()->new AtomicYamlStore(file));
        assertEquals("players: [broken\n",Files.readString(file));
    }
}
