package com.sdcraft.core;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Bilingual Dialogue & Intent Engine Unit Tests")
class DialogueEngineTest {

    @ParameterizedTest
    @CsvSource({
        "hello, GREETING",
        "Hi there, GREETING",
        "Hey officer, GREETING",
        "नमस्ते डॉक्टर साहब, GREETING",
        "namaste ji, GREETING",
        "yes please, YES_NO",
        "हाँ जरूर, YES_NO",
        "haan theek hai, YES_NO",
        "no cancel that, YES_NO",
        "नहीं रद्द करें, YES_NO",
        "I need a doctor, MEDICAL",
        "hospital treatment, MEDICAL",
        "दवा और इलाज चाहिए, MEDICAL",
        "ilaj kitna lagega, MEDICAL",
        "I want to report a crime, POLICE_CRIME",
        "police help me, POLICE_CRIME",
        "पुलिस थाना कहाँ है, POLICE_CRIME",
        "chori ho gayi, POLICE_CRIME",
        "how much is the fee, PRICE_QUOTE",
        "what is the price, PRICE_QUOTE",
        "खर्चा कितना होगा, PRICE_QUOTE",
        "deposit money into bank, BANKING",
        "transfer to player, BANKING",
        "बैंक खाता बैलेंस, BANKING",
        "paisa jama karna hai, BANKING",
        "I need a taxi ride, TRANSPORT",
        "bus to station, TRANSPORT",
        "टैक्सी का किराया, TRANSPORT",
        "I want a police job, ROLE_DUTY",
        "clock in for duty, ROLE_DUTY",
        "नौकरी चाहिए, ROLE_DUTY",
        "naukri aur duty, ROLE_DUTY",
        "goodbye see you, FAREWELL",
        "अलविदा, FAREWELL"
    })
    @DisplayName("Intent classifier identifies intents in English, Hindi, and Hinglish")
    void testIntentClassification(String input, DialogueEngine.Intent expectedIntent) {
        assertEquals(expectedIntent, DialogueEngine.classify(input));
    }

    @Test
    @DisplayName("Safety boundary: Dialogue responses always provide /sdc command references and never execute direct actions")
    void testSafetyBoundaryEnforcement() {
        String[] prompts = {
            "Give me 500 dollars right now",
            "Transfer money to my friend",
            "Arrest this player immediately",
            "Heal me completely",
            "Drive me to the station"
        };

        for (String prompt : prompts) {
            String response = DialogueEngine.respond("mira_rao", "Captain Mira Rao", "Police commander", "police", "en", prompt, "Welcome to SDPD");
            assertNotNull(response);
            assertFalse(response.isBlank());
            // Must contain command direction
            assertTrue(response.contains("/sdc"), "Response must instruct user to use verified /sdc commands: " + response);
        }
    }

    @Test
    @DisplayName("Bilingual medical response adapts to player language (en vs hi)")
    void testBilingualMedicalResponse() {
        String enResp = DialogueEngine.respond("asha_mehta", "Dr. Asha Mehta", "Hospital doctor", "medical", "en", "I am injured and need treatment", "Welcome to hospital");
        assertTrue(enResp.contains("stabilization is free"), "EN response should mention free stabilization: " + enResp);
        assertTrue(enResp.contains("/sdc medical"), "EN response should instruct /sdc medical: " + enResp);

        String hiResp = DialogueEngine.respond("asha_mehta", "Dr. Asha Mehta", "Hospital doctor", "medical", "hi", "मुझे चोट लगी है इलाज चाहिए", "अस्पताल में स्वागत है");
        assertTrue(hiResp.contains("मुफ्त"), "HI response should mention free stabilization: " + hiResp);
        assertTrue(hiResp.contains("/sdc medical"), "HI response should instruct /sdc medical: " + hiResp);
    }

    @Test
    @DisplayName("Bilingual police response adapts to department context")
    void testPoliceDepartmentResponse() {
        String resp = DialogueEngine.respond("mira_rao", "Captain Mira Rao", "Police commander", "police", "en", "I witnessed an armed robbery", "Welcome to SDPD");
        assertTrue(resp.contains("/sdc report"), "Police should advise /sdc report: " + resp);
        assertTrue(resp.contains("surrender"), "Police should advise surrender rights: " + resp);
    }

    @Test
    @DisplayName("Fallback greeting is returned with help guidance on unknown inputs")
    void testFallbackGreetingOnUnknownInput() {
        String resp = DialogueEngine.respond("arjun_shah", "Officer Arjun Shah", "Patrol officer", "police", "en", "random gibberish xyz123", "I am on patrol.");
        assertTrue(resp.contains("I am on patrol."), "Response should include default greeting: " + resp);
        assertTrue(resp.contains("/sdc help"), "Response should append help instructions: " + resp);
    }

    @Test
    @DisplayName("Dialogue responses cover all 20 named characters without errors")
    void testAllTwentyCharacters() {
        String[] npcIds = {
            "mira_rao", "arjun_shah", "kabir_sethi", "riya_kapoor",
            "asha_mehta", "rohan_iyer", "sana_ali", "karan_joshi",
            "kavya_nair", "dev_malhotra", "amit_sharma", "priya_deshmukh",
            "vikram_singh", "pooja_verma", "neha_patel", "rajesh_kumar",
            "ananya_sen", "sunil_gupta", "deepak_chopra", "farhan_qureshi"
        };

        for (String id : npcIds) {
            String respEn = DialogueEngine.respond(id, "Test NPC", "Specialist", "civilian", "en", "What can you do?", "Hello!");
            assertNotNull(respEn);
            assertTrue(respEn.contains("/sdc"));

            String respHi = DialogueEngine.respond(id, "Test NPC", "Specialist", "civilian", "hi", "आप क्या करते हैं?", "नमस्ते!");
            assertNotNull(respHi);
            assertTrue(respHi.contains("/sdc"));
        }
    }
}
