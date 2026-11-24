package com.sdcraft.core;

import com.sdcraft.core.gtm.CityRoster;
import com.sdcraft.core.gtm.RoleplayText;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CityRosterTest {
    @Test void additionsAreBoundedAndPrisonersRotate() throws Exception {
        var roster=new CityRoster(getClass().getResourceAsStream("/gtm-population.tsv"));
        assertEquals(400,roster.citizens().size());
        assertEquals(400,roster.citizens().values().stream().map(CityRoster.Citizen::uuid).distinct().count());
        assertEquals(5,roster.prisoners(0).size());
        assertNotEquals(roster.prisoners(0),roster.prisoners(1));
        assertEquals(roster.prisoners(0),roster.prisoners(19));
        assertFalse(roster.prisoners(0).contains(roster.citizens().get("npc-481").uuid()));
    }
    @Test void hinglishBankRequestGetsLocalBankGuidance() {
        String prompt="Bhai bank kidhar hai?";
        String language=RoleplayText.language(prompt,"en");
        assertEquals("hinglish",language);
        String reply=DialogueEngine.respond("npc-101","Aditi","Banker","bank",language,prompt,"");
        assertTrue(reply.contains("Paise")); assertTrue(reply.contains("/sdc bank deposit"));
    }
}
