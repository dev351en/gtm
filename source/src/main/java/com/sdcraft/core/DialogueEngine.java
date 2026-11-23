package com.sdcraft.core;

import java.util.*;

/**
 * Deterministic bilingual (English / Hindi) NPC dialogue & intent resolution engine.
 * Fully offline: requires no external API keys, consumes zero dollars, runs inside server memory.
 * 
 * HARD SECURITY BOUNDARY:
 * This engine NEVER executes commands, transfers money, alters player data,
 * promotes ranks, or triggers arrests. It produces informational conversational text
 * and instructs players on the verified server commands (/sdc ...) to execute actions.
 */
public final class DialogueEngine {

    public enum Intent {
        GREETING,
        YES_NO,
        SERVICE_ENQUIRY,
        ROLE_DUTY,
        PRICE_QUOTE,
        BANKING,
        MEDICAL,
        POLICE_CRIME,
        TRANSPORT,
        FAREWELL,
        UNKNOWN
    }

    private static final Set<String> KW_FAREWELL = Set.of(
        "bye", "goodbye", "alvida", "अलविदा", "tata"
    );

    private static final Set<String> KW_GREETING = Set.of(
        "hello", "hi", "hey", "howdy", "namaste", "namaskar", "pranam", "kaisa", "kaise",
        "नमस्ते", "नमस्कार", "प्रणाम", "halo"
    );

    private static final Set<String> KW_DUTY = Set.of(
        "job", "work", "duty", "shift", "salary", "pay", "join", "career",
        "naukri", "vetan", "kam", "kaam", "नौकरी", "ड्यूटी", "काम", "वेतन"
    );

    private static final Set<String> KW_BANKING = Set.of(
        "bank", "money", "cash", "deposit", "withdraw", "transfer", "balance", "wallet",
        "pin", "account", "paisa", "paise", "khata", "rupaye", "पैसे", "बैंक", "जमा", "निकासी", "खाता"
    );

    private static final Set<String> KW_MEDICAL = Set.of(
        "doctor", "hospital", "medic", "heal", "health", "injured", "injury", "hurt",
        "sick", "revive", "treatment", "diagnosis", "admission", "stabilize", "ilaj", "dawa",
        "aspatal", "chot", "bimar", "इलाज", "अस्पताल", "दवा", "चोट", "बीमार", "डॉक्टर"
    );

    private static final Set<String> KW_POLICE = Set.of(
        "police", "cop", "officer", "report", "crime", "rob", "robbery", "thief", "arrest",
        "jail", "surrender", "fine", "law", "sdpd", "thana", "chori", "chor",
        "सुरक्षा", "पुलिस", "अपराध", "चोरी", "रिपोर्ट", "गिरफ्तार", "थाना"
    );

    private static final Set<String> KW_TRANSPORT = Set.of(
        "taxi", "cab", "bus", "metro", "ride", "transport", "station", "stop",
        "gaadi", "sawaari", "kiraya", "टैक्सी", "बस", "मेट्रो", "किराया", "सवारी", "गाड़ी"
    );

    private static final Set<String> KW_PRICE = Set.of(
        "price", "cost", "fee", "charge", "quote", "rate", "kitna", "kharcha", "bhav",
        "फीस", "कीमत", "खर्चा", "कितना"
    );

    private static final Set<String> KW_YES = Set.of(
        "yes", "yeah", "yep", "sure", "ok", "okay", "agreed", "accept", "confirm",
        "haan", "theek", "bilkul", "हाँ", "हां", "हाँजी", "जरूर", "बिल्कुल"
    );

    private static final Set<String> KW_NO = Set.of(
        "no", "nope", "cancel", "decline", "never", "nahi", "nahin", "na", "radd",
        "नहीं", "ना", "रद्द"
    );

    private static final Set<String> KW_SERVICE = Set.of(
        "help", "service", "options", "assist", "madad", "seva", "मदद", "सेवा"
    );

    private DialogueEngine() {}

    /**
     * Identifies the primary intent from player text.
     */
    public static Intent classify(String text) {
        if (text == null || text.isBlank()) return Intent.UNKNOWN;
        String raw = text.trim();
        String lower = raw.toLowerCase(Locale.ROOT);

        // Unicode-aware word tokenization: keeps letters, marks, digits
        String clean = lower.replaceAll("[^\\p{L}\\p{M}\\p{N}\\s]", " ").trim();
        if (clean.isEmpty()) return Intent.UNKNOWN;

        String[] tokenArray = clean.split("\\s+");
        Set<String> tokens = new HashSet<>(Arrays.asList(tokenArray));

        // 1. Farewells
        if (containsAny(tokens, KW_FAREWELL) || lower.contains("फिर मिलेंगे")) {
            return Intent.FAREWELL;
        }

        // 2. Greetings (if short query or starts with greeting)
        if (containsAny(tokens, KW_GREETING) || lower.startsWith("ram ram") || lower.contains("राम राम")) {
            if (tokenArray.length <= 4 || (!containsAny(tokens, KW_DUTY) && !containsAny(tokens, KW_BANKING) && !containsAny(tokens, KW_POLICE) && !containsAny(tokens, KW_MEDICAL))) {
                return Intent.GREETING;
            }
        }

        // 3. Job / Duty (highest priority for phrases like "police job", "hospital work")
        if (containsAny(tokens, KW_DUTY)) {
            return Intent.ROLE_DUTY;
        }

        // 4. Banking
        if (containsAny(tokens, KW_BANKING)) {
            return Intent.BANKING;
        }

        // 5. Medical
        if (containsAny(tokens, KW_MEDICAL)) {
            return Intent.MEDICAL;
        }

        // 6. Police & Crime
        if (containsAny(tokens, KW_POLICE)) {
            return Intent.POLICE_CRIME;
        }

        // 7. Transport
        if (containsAny(tokens, KW_TRANSPORT)) {
            return Intent.TRANSPORT;
        }

        // 8. Price / Quote
        if (containsAny(tokens, KW_PRICE) || lower.contains("how much")) {
            return Intent.PRICE_QUOTE;
        }

        // 9. Yes / No
        if (containsAny(tokens, KW_YES) || containsAny(tokens, KW_NO)) {
            return Intent.YES_NO;
        }

        // 10. Service Enquiry
        if (containsAny(tokens, KW_SERVICE) || lower.contains("what do you do") || lower.contains("काम क्या")) {
            return Intent.SERVICE_ENQUIRY;
        }

        // 11. Greeting fallback if any greeting token was present
        if (containsAny(tokens, KW_GREETING)) {
            return Intent.GREETING;
        }

        return Intent.UNKNOWN;
    }

    private static boolean containsAny(Set<String> tokens, Set<String> keywords) {
        for (String kw : keywords) {
            if (tokens.contains(kw)) return true;
        }
        return false;
    }

    /**
     * Generates a context-aware bilingual response for the given NPC identity and user prompt.
     * Enforces the rule that AI dialogue cannot execute transactions directly.
     */
    public static String respond(String npcId, String npcName, String role, String dept, String lang, String prompt, String defaultGreeting) {
        boolean hi = "hi".equalsIgnoreCase(lang);
        Intent intent = classify(prompt);
        String department = dept == null ? "civilian" : dept.toLowerCase(Locale.ROOT);

        switch (intent) {
            case GREETING:
                if (hi) {
                    return "नमस्ते! मैं " + npcName + " (" + role + ") हूँ। मैं आपकी क्या सेवा कर सकता हूँ? आधिकारिक विकल्पों के लिए /sdc help देखें।";
                } else {
                    return "Hello! I am " + npcName + " (" + role + "). How can I assist you today? Check /sdc help for official options.";
                }

            case YES_NO:
                String clean = prompt.toLowerCase(Locale.ROOT).replaceAll("[^\\p{L}\\p{M}\\p{N}\\s]", " ");
                Set<String> tokens = new HashSet<>(Arrays.asList(clean.trim().split("\\s+")));
                if (containsAny(tokens, KW_NO)) {
                    return hi ? "ठीक है, कार्रवाई रद्द कर दी गई है। किसी भी लंबित प्रक्रिया को हटाने के लिए /sdc cancel टाइप करें।"
                              : "Understood, action cancelled. Type /sdc cancel to clear any pending action.";
                } else {
                    return hi ? "सहमति दर्ज की गई। किसी भी वित्तीय या सेवा लेनदेन को पूरा करने के लिए /sdc confirm कमांड का उपयोग करें।"
                              : "Acknowledged. To finalize any financial or service transaction, please use /sdc confirm.";
                }

            case BANKING:
                if (hi) {
                    return "बैंक सेवाएँ केवल अधिकृत बैंक स्टेशन पर उपलब्ध हैं। जमा के लिए /sdc bank deposit <रकम>, निकासी के लिए /sdc bank withdraw <रकम> और ट्रांसफर के लिए /sdc bank transfer <खिलाड़ी> <रकम> उपयोग करें। पिन सेट करने के लिए /sdc pin set दबाएँ।";
                } else {
                    return "Banking services are strictly handled at the verified bank station. Use /sdc bank deposit <amt>, /sdc bank withdraw <amt>, or /sdc bank transfer <player> <amt>. Set your secure PIN with /sdc pin set.";
                }

            case MEDICAL:
                if (department.equals("medical")) {
                    if (hi) {
                        return "अस्पताल में आपातकालीन स्थिरीकरण मुफ्त है। जाँच ($25), इलाज ($50) या भर्ती ($75) के लिए अस्पताल स्टेशन पर /sdc medical <सेवा> दर्ज करें और /sdc confirm से पुष्टि करें।";
                    } else {
                        return "At the hospital, emergency stabilization is free. For diagnosis ($25), treatment ($50), or admission ($75), visit the station and enter /sdc medical <service>, followed by /sdc confirm.";
                    }
                } else {
                    return hi ? "चिकित्सा सहायता के लिए सिटी अस्पताल जाएँ या किसी अधिकृत डॉक्टर से संपर्क करें। आपात स्थिति में स्थिरीकरण मुफ्त है (/sdc medical stabilize)।"
                              : "For medical care, please visit City Hospital or call an on-duty medic. Emergency stabilization is free (/sdc medical stabilize).";
                }

            case POLICE_CRIME:
                if (department.equals("police")) {
                    if (hi) {
                        return "एसडीपीडी में अपराध दर्ज करने के लिए /sdc report <1|2|3> <विवरण> दर्ज करें। आत्मसमर्पण के लिए /sdc surrender का उपयोग करें। किसी भी गिरफ्तारी से पहले 15 सेकंड का आत्मसमर्पण अवसर दिया जाता है।";
                    } else {
                        return "To file an official SDPD crime report, use /sdc report <1|2|3> <description>. To yield peacefully, use /sdc surrender. A 15-second surrender opportunity is guaranteed before arrest.";
                    }
                } else {
                    return hi ? "अपराध या संदिग्ध गतिविधि की सूचना पुलिस को देने के लिए /sdc report <1|2|3> <विवरण> का उपयोग करें।"
                              : "To report crimes or suspicious activity, contact SDPD or use /sdc report <1|2|3> <description>.";
                }

            case TRANSPORT:
                if (hi) {
                    return "परिवहन दरें: टैक्सी बेस $25 + $6 प्रति 100 ब्लॉक; बस $15; मेट्रो $10। यात्रा बुक करने के लिए /sdc taxi <स्टॉप> या /sdc ride <bus|metro> <स्टॉप> उपयोग करें।";
                } else {
                    return "Transit fares: Taxi $25 base + $6 per 100 blocks; Bus $15; Metro $10. Book a trip using /sdc taxi <stop> or /sdc ride <bus|metro> <stop>.";
                }

            case PRICE_QUOTE:
                if (hi) {
                    return "अधिकृत शहर दरें: मेडिकल जाँच $25, इलाज $50, भर्ती $75। टैक्सी $25+$6/100 ब्लॉक, बस $15, मेट्रो $10। अपराध जुर्माना: स्तर 1=$50, स्तर 2=$150, स्तर 3=$300।";
                } else {
                    return "Official city rates: Medical diagnosis $25, treatment $50, admission $75. Taxi $25+$6/100 blocks, Bus $15, Metro $10. Conviction fines: L1=$50, L2=$150, L3=$300.";
                }

            case ROLE_DUTY:
                if (hi) {
                    return "नौकरी में शामिल होने के लिए /sdc work join <रोल> दर्ज करें। अपनी ड्यूटी शुरू करने के लिए विभाग के स्टेशन पर जाकर /sdc duty in करें। वेतन आपकी सक्रिय गतिविधि के आधार पर मिलेगा।";
                } else {
                    return "To register a profession, use /sdc work join <role>. Clock in at your department's verified station with /sdc duty in. Pay is prorated by verified active duty time.";
                }

            case SERVICE_ENQUIRY:
                if (hi) {
                    return "मैं " + role + " के रूप में सहायता कर सकता हूँ। सभी सेवाएँ सुरक्षित मेनू और कमांड के माध्यम से उपलब्ध हैं। विकल्प देखने के लिए मुझ पर राइट-क्लिक करें या /sdc help का उपयोग करें।";
                } else {
                    return "I provide assistance as " + role + ". All actions are executed safely through verified menus and commands. Right-click me or use /sdc help for available services.";
                }

            case FAREWELL:
                return hi ? "धन्यवाद, सुरक्षित रहें! जब भी ज़रूरत हो, बेझिझक वापस आएं।"
                          : "Thank you, stay safe! Feel free to return whenever you need assistance.";

            case UNKNOWN:
            default:
                if (defaultGreeting != null && !defaultGreeting.isBlank()) {
                    return defaultGreeting + (hi ? " (कमांड जानकारी के लिए /sdc help देखें)" : " (Type /sdc help for verified services)");
                }
                return hi ? "क्षमा करें, मैं यह नहीं समझ सका। आधिकारिक शहर सेवाओं के लिए /sdc help देखें।"
                          : "I could not fully understand your request. Please check /sdc help for verified city services.";
        }
    }
}
