#!/usr/bin/env python3
"""
Render all 120 bilingual Indraprastha signs (512x256 RGBA PNG) using headless Microsoft Edge (DirectWrite/HarfBuzz)
for 100% genuine Devanagari (Marathi/Hindi) typography, SVG pictograms, and embedded 3D brand emblems.
"""
import base64
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
SIGNAGE_DIR = CREATIVE / "source" / "signage"
BRANDING_DIR = CREATIVE / "source" / "branding"
MANIFESTS = CREATIVE / "manifests"
PREVIEWS = CREATIVE / "previews"
ARTIFACT_DIR = Path(r"C:\Users\brode\.gemini\antigravity\brain\ceee3c26-6ae4-4f1c-b357-09eb59f51997")
MSEDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

SVGS = {
    "metro": '<svg viewBox="0 0 64 64" width="54" height="54"><circle cx="32" cy="32" r="28" fill="#1D4ED8" stroke="#FFFFFF" stroke-width="4"/><path d="M18 46 V18 L32 34 L46 18 V46" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "rail": '<svg viewBox="0 0 64 64" width="54" height="54"><rect x="14" y="10" width="36" height="38" rx="8" fill="#D6AD59"/><rect x="20" y="16" width="24" height="14" rx="2" fill="#151B20"/><circle cx="22" cy="39" r="3" fill="#151B20"/><circle cx="42" cy="39" r="3" fill="#151B20"/><line x1="12" y1="54" x2="52" y2="54" stroke="#D6AD59" stroke-width="4"/></svg>',
    "ferry": '<svg viewBox="0 0 64 64" width="54" height="54"><polygon points="10,36 54,36 46,48 18,48" fill="#38BDF8"/><polygon points="20,20 42,20 46,36 16,36" fill="#FFFFFF"/><path d="M8 54 Q20 48 32 54 Q44 60 56 54" fill="none" stroke="#7DD3FC" stroke-width="4"/></svg>',
    "ropeway": '<svg viewBox="0 0 64 64" width="54" height="54"><line x1="6" y1="14" x2="58" y2="20" stroke="#F8FAFC" stroke-width="4"/><line x1="32" y1="17" x2="32" y2="28" stroke="#D6AD59" stroke-width="4"/><rect x="14" y="28" width="36" height="24" rx="6" fill="#F59E0B" stroke="#FFFFFF" stroke-width="2"/><rect x="20" y="33" width="10" height="10" fill="#0F172A"/><rect x="34" y="33" width="10" height="10" fill="#0F172A"/></svg>',
    "airport": '<svg viewBox="0 0 64 64" width="54" height="54"><path d="M32 8 L38 26 L56 34 V40 L38 35 V48 L44 54 V58 L32 54 L20 58 V54 L26 48 V35 L8 40 V34 L26 26 Z" fill="#F8FAFC"/></svg>',
    "bus": '<svg viewBox="0 0 64 64" width="54" height="54"><rect x="14" y="10" width="36" height="40" rx="6" fill="#EF4444" stroke="#FFFFFF" stroke-width="2.5"/><rect x="19" y="16" width="26" height="14" fill="#E0F2FE"/><circle cx="22" cy="41" r="3" fill="#FEF08A"/><circle cx="42" cy="41" r="3" fill="#FEF08A"/></svg>',
    "speed50": '<svg viewBox="0 0 64 64" width="56" height="56"><circle cx="32" cy="32" r="28" fill="#FFFFFF" stroke="#DC2626" stroke-width="7"/><text x="32" y="42" font-family="Segoe UI,sans-serif" font-size="28" font-weight="900" fill="#111827" text-anchor="middle">50</text></svg>',
    "prohibit": '<svg viewBox="0 0 64 64" width="56" height="56"><circle cx="32" cy="32" r="27" fill="#FFFFFF" stroke="#DC2626" stroke-width="7"/><line x1="14" y1="14" x2="50" y2="50" stroke="#DC2626" stroke-width="7"/></svg>',
    "warning": '<svg viewBox="0 0 64 64" width="56" height="56"><polygon points="32,6 58,54 6,54" fill="#FBBF24" stroke="#111827" stroke-width="4" stroke-linejoin="round"/><rect x="30" y="24" width="4" height="16" fill="#111827"/><circle cx="32" cy="46" r="2.8" fill="#111827"/></svg>',
    "arrow_blue": '<svg viewBox="0 0 64 64" width="56" height="56"><circle cx="32" cy="32" r="27" fill="#1D4ED8" stroke="#FFFFFF" stroke-width="3"/><path d="M32 14 V48 M32 14 L20 26 M32 14 L44 26" fill="none" stroke="#FFFFFF" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "stop": '<svg viewBox="0 0 64 64" width="56" height="56"><polygon points="22,6 42,6 58,22 58,42 42,58 22,58 6,42 6,22" fill="#DC2626" stroke="#FFFFFF" stroke-width="3.5"/><text x="32" y="38" font-family="Segoe UI,sans-serif" font-size="16" font-weight="900" fill="#FFFFFF" text-anchor="middle">STOP</text></svg>',
    "civic": '<svg viewBox="0 0 64 64" width="54" height="54"><polygon points="32,8 54,20 10,20" fill="#D6AD59"/><rect x="14" y="23" width="6" height="24" fill="#D6AD59"/><rect x="29" y="23" width="6" height="24" fill="#D6AD59"/><rect x="44" y="23" width="6" height="24" fill="#D6AD59"/><rect x="8" y="49" width="48" height="6" fill="#D6AD59"/></svg>',
    "police": '<svg viewBox="0 0 64 64" width="54" height="54"><path d="M32 6 L54 16 V34 C54 48 32 58 32 58 C32 58 10 48 10 34 V16 Z" fill="#1E3A8A" stroke="#D6AD59" stroke-width="3.5"/><polygon points="32,18 36,28 46,28 38,34 41,44 32,38 23,44 26,34 18,28 28,28" fill="#D6AD59"/></svg>',
    "hospital": '<svg viewBox="0 0 64 64" width="54" height="54"><rect x="8" y="8" width="48" height="48" rx="10" fill="#FFFFFF" stroke="#DC2626" stroke-width="3"/><rect x="27" y="16" width="10" height="32" fill="#DC2626"/><rect x="16" y="27" width="32" height="10" fill="#DC2626"/></svg>',
    "store": '<svg viewBox="0 0 64 64" width="54" height="54"><path d="M10 24 L16 10 H48 L54 24 Z" fill="#D6AD59"/><rect x="14" y="24" width="36" height="28" fill="#FFFFFF" fill-opacity="0.9"/><rect x="25" y="34" width="14" height="18" fill="#151B20"/></svg>',
    "cctv": '<svg viewBox="0 0 64 64" width="54" height="54"><circle cx="32" cy="32" r="26" fill="#FFFFFF" stroke="#DC2626" stroke-width="4"/><polygon points="16,24 44,18 48,32 22,38" fill="#111827"/><circle cx="48" cy="25" r="4" fill="#DC2626"/></svg>',
    "bolt": '<svg viewBox="0 0 64 64" width="54" height="54"><polygon points="32,6 58,54 6,54" fill="#FACC15" stroke="#111827" stroke-width="4" stroke-linejoin="round"/><polygon points="35,19 23,36 32,36 28,49 41,31 32,31" fill="#111827"/></svg>',
    "safe_exit": '<svg viewBox="0 0 64 64" width="54" height="54"><rect x="8" y="8" width="48" height="48" rx="8" fill="#15803D" stroke="#FFFFFF" stroke-width="3"/><polygon points="22,32 34,20 34,27 48,27 48,37 34,37 34,44" fill="#FFFFFF"/></svg>',
    "accessibility": '<svg viewBox="0 0 64 64" width="54" height="54"><rect x="8" y="8" width="48" height="48" rx="10" fill="#1D4ED8" stroke="#FFFFFF" stroke-width="3"/><circle cx="32" cy="18" r="5" fill="#FFFFFF"/><path d="M30 25 V38 H42 V48 M26 32 C20 34 18 42 22 47 C26 52 34 52 38 46" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/></svg>',
}


def load_brand_data_uri(brand_id: str) -> str:
    p = BRANDING_DIR / f"{brand_id}.png"
    if not p.exists():
        return ""
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def get_sign_definitions():
    # Exact 120 signs: 20 transport, 20 road, 15 civic, 25 store, 25 commercial ads, 15 public safety
    signs = []
    # 1. Transport (20)
    t = [
        ("marine_drive_station", "Marine Drive Station", "मरीन ड्राईव्ह स्टेशन", "#0F172A", "#D6AD59", "metro", "M3"),
        ("churchgate_terminal", "Churchgate Terminal", "चर्चगेट टर्मिनल", "#1E1B18", "#D6AD59", "rail", "WR"),
        ("metro_line_3_cuffe", "Metro Line 3 Cuffe Parade", "मेट्रो ३ कफ परेड", "#064E3B", "#6EE7B7", "metro", "M3"),
        ("cst_heritage_junction", "CST Heritage Junction", "सीएसटी हेरिटेज जंक्शन", "#151B20", "#D6AD59", "rail", "CR"),
        ("bandra_west_pier", "Bandra West Ferry Pier", "वांद्रे पश्चिम जेट्टी", "#0C4A6E", "#7DD3FC", "ferry", "P-1"),
        ("skylink_gondola_term", "SkyLink Cableway Terminal", "स्कायलिंक केबलवे टर्मिनल", "#7C2D12", "#FDBA74", "ropeway", "SL1"),
        ("worli_sea_face_bus", "Worli Sea Face Bus Depot", "वरळी सी फेस बस आगार", "#450A0A", "#FCA5A5", "bus", "BEST"),
        ("dadar_central_inter", "Dadar Central Interchange", "दादर मध्यवर्ती जंक्शन", "#151B20", "#D6AD59", "rail", "HUB"),
        ("indrap_international", "Indraprastha Airport T2", "इंद्रप्रस्थ विमानतळ टी२", "#172554", "#93C5FD", "airport", "T2"),
        ("apollo_bunder_ferry", "Apollo Bunder Ferry Dock", "अपोलो बंदर बोट धक्का", "#0C4A6E", "#FFFFFF", "ferry", "D-2"),
        ("nariman_point_shuttle", "Nariman Pt Express Shuttle", "नरिमन पॉईंट एक्सप्रेस शटल", "#064E3B", "#FFFFFF", "bus", "EXP"),
        ("colaba_causeway_tram", "Colaba Heritage Tram Stop", "कुलाबा ट्राम थांबा", "#7F1D1D", "#FDE047", "rail", "TRM"),
        ("andheri_metro_link", "Andheri Metro Link Station", "अंधेरी मेट्रो लिंक स्थानक", "#14532D", "#FFFFFF", "metro", "M1"),
        ("kurla_freight_yard", "Kurla Logistics Freight Yard", "कुर्ला मालधक्का यार्ड", "#3B0764", "#E9D5FF", "rail", "FRT"),
        ("vikhroli_heliport_hub", "Vikhroli Heliport Hub", "विक्रोळी हेलिपोर्ट हब", "#151B20", "#D6AD59", "airport", "H-1"),
        ("juhu_aerodrome_gate", "Juhu Aerodrome Gate 1", "जुहू विमानतळ प्रवेशद्वार १", "#1E3A8A", "#FFFFFF", "airport", "GA1"),
        ("malabar_hill_ropeway", "Malabar Hill Ropeway Stn", "मलबार हिल रोपवे स्थानक", "#7C2D12", "#FDE047", "ropeway", "SL2"),
        ("sewri_harbour_port", "Sewri Container Port Gate", "शिवडी कंटेनर पोर्ट गेट", "#0F172A", "#38BDF8", "ferry", "CPT"),
        ("chembur_monorail", "Chembur Monorail Station", "चेंबूर मोनोरेल स्थानक", "#422006", "#FACC15", "metro", "MONO"),
        ("santacruz_domestic_t1", "Domestic Airport Term T1", "देशांतर्गत विमानतळ टी१", "#151B20", "#D6AD59", "airport", "T1")
    ]
    for slug, en, mr, bg, acc, ico, code in t:
        signs.append(("transport", slug, en, mr, bg, acc, ico, code, ""))

    # 2. Road (20)
    rd = [
        ("sea_link_toll_gate", "Sea Link Toll Plaza 500m", "सी लिंक टोल नाका ५०० मी", "#151B20", "#D6AD59", "arrow_blue", "NH-4"),
        ("speed_limit_50", "Speed Limit 50 km/h", "कमाल वेग ५० किमी/तास", "#1E293B", "#EF4444", "speed50", "MAX"),
        ("no_parking_tow_away", "No Parking • Tow-Away Zone", "नो पार्किंग • टोइंग क्षेत्र", "#7F1D1D", "#FCA5A5", "prohibit", "NO-P"),
        ("one_way_traffic_ahead", "One Way Street Ahead", "एकमुखी रस्ता पुढे", "#1E3A8A", "#93C5FD", "arrow_blue", "1-WAY"),
        ("pedestrian_crossing", "Pedestrian Crossing", "पादचारी क्रॉसिंग", "#1E3A8A", "#FFFFFF", "arrow_blue", "XING"),
        ("heavy_vehicles_prohibit", "No Heavy Vehicles Allowed", "जड वाहनांना बंदी", "#7F1D1D", "#FFFFFF", "prohibit", "BAN"),
        ("expressway_north_fast", "North Expressway Fast Lane", "उत्तर द्रुतगती मार्ग लेन", "#14532D", "#86EFAC", "arrow_blue", "EXP-N"),
        ("u_turn_prohibited", "U-Turn Prohibited Ahead", "यु-टर्न मनाई पुढे", "#7F1D1D", "#FCA5A5", "prohibit", "NO-U"),
        ("hospital_quiet_zone", "Hospital Area • Silence Zone", "रुग्णालय क्षेत्र • शांतता झोन", "#1E3A8A", "#93C5FD", "hospital", "SIL"),
        ("school_zone_slow_down", "School Zone • Drive Slow", "शाळा क्षेत्र • वाहने हळू चालवा", "#422006", "#FBBF24", "warning", "SCH"),
        ("coastal_road_exit_4", "Coastal Road Exit 4 • Worli", "किनारी रस्ता निकास ४ वरळी", "#064E3B", "#6EE7B7", "arrow_blue", "EX-4"),
        ("steep_descent_low_gear", "Steep Gradient • Low Gear", "तीव्र उतार • कमी गिअर वापरा", "#422006", "#FBBF24", "warning", "SLOPE"),
        ("road_work_in_progress", "Road Work in Progress", "रस्त्याचे काम सुरू आहे", "#422006", "#FBBF24", "warning", "WORK"),
        ("accident_blackspot_slow", "Accident Prone Area • Slow", "अपघात प्रवण क्षेत्र • सावध", "#7F1D1D", "#FBBF24", "warning", "ALERT"),
        ("bus_lane_enforced", "Dedicated Bus Lane Only", "फक्त बस मार्गिका", "#3B0764", "#E9D5FF", "bus", "BUS"),
        ("parking_ark_pay_card", "Municipal ARK Pay Parking", "महानगरपालिका सशुल्क वाहनतळ", "#1E3A8A", "#D6AD59", "arrow_blue", "P"),
        ("roundabout_give_way", "Roundabout • Give Way", "गोलचक्कर • वाट द्या", "#1E3A8A", "#FFFFFF", "warning", "YIELD"),
        ("bridge_clearance_4_5m", "Max Clearance Height 4.5m", "कमाल उंची मर्यादा ४.५ मी", "#422006", "#FBBF24", "warning", "4.5m"),
        ("stop_security_check", "Stop • Police Check Post", "थांबा • पोलीस तपासणी नाका", "#7F1D1D", "#FFFFFF", "stop", "CHK"),
        ("free_left_turn_only", "Free Left Turn Permitted", "फक्त डावे वळण विनामूल्य", "#14532D", "#86EFAC", "arrow_blue", "LEFT")
    ]
    for slug, en, mr, bg, acc, ico, code in rd:
        signs.append(("road", slug, en, mr, bg, acc, ico, code, ""))

    # 3. Civic (15)
    civ = [
        ("city_hall_indrap", "Indraprastha City Hall", "इंद्रप्रस्थ महानगरपालिका", "#151B20", "#D6AD59", "civic", "MCI"),
        ("central_police_hq", "Police Commissionerate HQ", "मध्यवर्ती पोलीस मुख्यालय", "#0F172A", "#D6AD59", "police", "SDPD"),
        ("district_court_complex", "District & Sessions Court", "जिल्हा व सत्र न्यायालय", "#1E293B", "#D6AD59", "civic", "COURT"),
        ("general_civil_hospital", "Indraprastha Civil Hospital", "इंद्रप्रस्थ शासकीय रुग्णालय", "#7F1D1D", "#FFFFFF", "hospital", "EMS"),
        ("central_fire_station", "Fire & Rescue Headquarters", "अग्निशामक व बचाव मुख्यालय", "#7F1D1D", "#FBBF24", "warning", "FIRE"),
        ("central_library_reading", "State Central Library", "राज्य मध्यवर्ती ग्रंथालय", "#064E3B", "#D6AD59", "civic", "LIB"),
        ("public_works_division", "Public Works Department", "सार्वजनिक बांधकाम विभाग", "#431407", "#FDBA74", "civic", "PWD"),
        ("heritage_preservation", "Heritage Conservation Cell", "वारसा संवर्धन विभाग", "#422006", "#D6AD59", "civic", "HER"),
        ("civil_defense_bunker", "Civic Emergency Operations", "नागरी आपत्कालीन केंद्र", "#450A0A", "#FCA5A5", "bolt", "OPS"),
        ("tax_revenue_office", "Municipal Revenue Dept", "महानगरपालिका कर विभाग", "#1E293B", "#93C5FD", "civic", "TAX"),
        ("water_sanitation_hq", "Hydraulic & Water Works", "पाणी पुरवठा विभाग", "#0C4A6E", "#7DD3FC", "civic", "H2O"),
        ("sub_registrar_deeds", "Property Registry Office", "नोंदणी व मुद्रांक कार्यालय", "#151B20", "#D6AD59", "civic", "REG"),
        ("postal_sorting_centre", "General Post Office (GPO)", "मुख्य टपाल कार्यालय", "#7F1D1D", "#FDE047", "civic", "POST"),
        ("citizens_service_center", "Citizen Suvidha Kendra", "नागरिक सुविधा केंद्र", "#064E3B", "#6EE7B7", "civic", "SEVA"),
        ("metro_authority_office", "Urban Transport Authority", "नागरी वाहतूक महामंडळ", "#151B20", "#D6AD59", "metro", "UTA")
    ]
    for slug, en, mr, bg, acc, ico, code in civ:
        signs.append(("civic", slug, en, mr, bg, acc, ico, code, ""))

    # 4. Storefronts (25)
    st = [
        ("irani_cafe_1947", "Cafe Irani & Bakery • 1947", "कॅफे इराणी आणि बेकरी", "#451A03", "#FDE68A", "store", "CAFE"),
        ("bombay_kirana_mart", "Indraprastha Kirana Mart", "इंद्रप्रस्थ किराणा स्टोअर्स", "#064E3B", "#6EE7B7", "store", "MART"),
        ("sahyadri_sweets", "Sahyadri Mithai & Farsan", "सह्याद्री मिठाई व फरसाण", "#7C2D12", "#FDE047", "store", "SWEETS"),
        ("marine_jewellers", "Marine Gold & Diamonds", "मरीन ज्वेलर्स • शुद्ध सोने", "#151B20", "#D6AD59", "store", "GOLD"),
        ("royal_tailors_gents", "Royal Bespoke Tailors", "रॉयल टेलर्स • जेंट्स स्पेशालिस्ट", "#1E293B", "#E2E8F0", "store", "SUITS"),
        ("deccan_pharmacy_247", "Deccan Chemist • 24x7 Open", "डेक्कन मेडिकल व केमिस्ट", "#065F46", "#34D399", "hospital", "24x7"),
        ("apollo_hardware_tools", "Apollo Tools & Hardware", "अपोलो हार्डवेअर आणि टूल्स", "#7C2D12", "#FB923C", "store", "TOOLS"),
        ("chetak_auto_spares", "Chetak Genuine Auto Spares", "चेतक ऑटो पार्टस्", "#151B20", "#EF4444", "store", "AUTO"),
        ("konkan_fresh_fish", "Konkan Seafood Market", "कोकण ताजे मत्स्य केंद्र", "#0C4A6E", "#7DD3FC", "ferry", "FISH"),
        ("varun_electronics_tv", "Varun Digital Appliances", "वरुण इलेक्ट्रॉनिक्स", "#172554", "#60A5FA", "store", "TECH"),
        ("national_book_house", "National Book Depot", "नॅशनल बुक डेपो", "#422006", "#FDE047", "store", "BOOKS"),
        ("laxmi_textiles_silk", "Laxmi Silk Saree Emporium", "लक्ष्मी सिल्क साडी एम्पोरियम", "#7F1D1D", "#FACC15", "store", "SILK"),
        ("sharma_chaat_bhandar", "Sharma Chaat Bhandar", "शर्मा प्रसिद्ध चाट भंडार", "#9A3412", "#FDBA74", "store", "CHAAT"),
        ("metro_footwear_shoes", "Metro Footwear Works", "मेट्रो फुटवेअर", "#151B20", "#D6AD59", "store", "SHOES"),
        ("bazaar_vegetables", "Fresh Green Sabzi Mandi", "ताजी भाजीपाला बाजार", "#14532D", "#86EFAC", "store", "FRESH"),
        ("gold_gym_fitness", "Royal Iron Fitness Club", "रॉयल आयर्न व्यायामशाळा", "#111827", "#D6AD59", "store", "GYM"),
        ("deccan_dry_fruits", "Deccan Royal Dry Fruits", "डेक्कन सुकामेवा केंद्र", "#451A03", "#FCD34D", "store", "NUTS"),
        ("hind_cycles_repairs", "Hind Cycle & EV Works", "हिंद सायकल डेपो", "#1E3A8A", "#93C5FD", "store", "CYCLE"),
        ("krishna_dairy_milk", "Krishna Pure Dairy & Ghee", "कृष्ण डेअरी • ताजे दूध", "#0369A1", "#FFFFFF", "store", "MILK"),
        ("shikari_sports_gear", "Shikari Sports & Gear", "शिकारी स्पोर्ट्स अँड गियर", "#151B20", "#34D399", "store", "GEAR"),
        ("star_photo_studio", "CineVista Portrait Studio", "सिनेव्हिस्टा फोटो स्टुडिओ", "#3B0764", "#D8B4FE", "store", "PHOTO"),
        ("lotus_flower_stall", "Lotus Puja Flowers & Toran", "कमळ फुले व हार केंद्र", "#831843", "#F9A8D4", "store", "PUJA"),
        ("suruchi_spice_house", "Suruchi Ground Spices", "सुरुची मसाले भांडार", "#7C2D12", "#FDBA74", "store", "SPICE"),
        ("shree_watch_co", "Shree Time Watch Makers", "श्री घड्याळ कंपनी", "#151B20", "#D6AD59", "store", "WATCH"),
        ("chai_point_tapri", "Amrutulya Masala Chai", "अमृततुल्य कडक चहा", "#451A03", "#FBBF24", "store", "CHAI")
    ]
    for slug, en, mr, bg, acc, ico, code in st:
        signs.append(("store", slug, en, mr, bg, acc, ico, code, ""))

    # 5. Commercial Ads (25) — LINKED TO ACTUAL EXTRACTED BRAND LOGOS!
    ads = [
        ("ark_bank_fixed_deposit", "ARK Bank • 8.5% Returns", "इंद्रप्रस्थ बँक • विश्वासार्ह बचत", "#0D1115", "#D6AD59", "indra_bank"),
        ("vayu_5g_sim_unlimited", "AirWave True 5G UltraFast", "एअरवेव्ह ५जी • अखंड नेटवर्क", "#0F172A", "#38BDF8", "airwave"),
        ("chetak_cyclone_suv", "Wahindra SUV • Book Today", "महिंद्रा एसयूव्ही • आजच बुक करा", "#431407", "#FB923C", "wahindra"),
        ("deccan_towers_luxury", "Maya Sea-Facing Condos", "माया रेसिडेन्सी • लक्झरी घरे", "#151B20", "#D6AD59", "maya_residences"),
        ("star_cola_chilled", "Royal Iron Pre-Workout", "रॉयल आयर्न फिटनेस एनर्जी", "#1E1B18", "#D6AD59", "royal_iron"),
        ("maratha_cement_durable", "Tavara Heavy EV Fleets", "तवरा हेवी इलेक्ट्रिक ट्रक्स", "#0F172A", "#38BDF8", "tavara"),
        ("indrayani_tea_aroma", "Amora Royal Handloom Silks", "अमोरा शुद्ध रेशमी वस्त्रे", "#431407", "#D6AD59", "amora"),
        ("lotus_fashion_sale", "Black Lotus VIP Club Night", "ब्लॅक लोटस • व्हीआयपी क्लब", "#110915", "#F43F5E", "black_lotus"),
        ("varun_pumps_agri", "Maruva Hybrid City Hatch", "मारुवा हायब्रीड सिटी कार", "#064E3B", "#6EE7B7", "maruva"),
        ("sahyadri_insurance", "Toyora Crown Exec Fleet", "टोयोरा क्राऊन लक्झरी सिडान", "#151B20", "#D6AD59", "toyora"),
        ("taj_catering_events", "Rang Bharat Festival Wear", "रंग भारत उत्सवी कलेक्शन", "#064E3B", "#FACC15", "rang_bharat"),
        ("maharaja_snack_pack", "D-Bazaar Super Wholesale", "डी-बझार महाबचत स्टोअर", "#14532D", "#86EFAC", "d_bazaar"),
        ("shikari_tyres_grip", "Veero 200cc Street Track", "वीरो २००सीसी स्पोर्ट्स बाईक", "#450A0A", "#EF4444", "veero"),
        ("oceanic_cruises_goa", "Vayu Bharat Coastal Flights", "वायू भारत कोस्टल विमानसेवा", "#0C4A6E", "#7DD3FC", "vayu_bharat"),
        ("hind_paints_weather", "Hondo Silent E-Scooter", "होंडो ई-स्कूटर आजच घ्या", "#172554", "#60A5FA", "hondo"),
        ("mumbai_city_fc_match", "SD Motorsport Hypercars", "एसडी मोटरस्पोर्ट सुपरकार्स", "#0D1115", "#D6AD59", "sd_motors"),
        ("deccan_watches_chron", "Jyon Urban Drops Today", "ज्यॉन स्ट्रीटवेअर फॅशन", "#1E293B", "#E8C87E", "jyon"),
        ("speed_petroleum_turbo", "Indra Fuel High Octane", "इंद्रप्रस्थ शुद्ध पेट्रोलियम", "#0F172A", "#2DD4BF", "indra_fuel"),
        ("garuda_airline_fly", "SkyIndra Ropeway Skyway", "स्कायइंद्र रोपवे प्रवास", "#064E3B", "#D2B997", "skyindra"),
        ("arya_security_cctv", "Quoggle City GPS Navigation", "क्वागल सिटी स्मार्ट नेव्हिगेशन", "#0F172A", "#60A5FA", "quoggle"),
        ("rajput_jewels_wedding", "Flippit Mega Flash Sale", "फ्लिपिट महासेल ८०% सूट", "#1E3A8A", "#FACC15", "flippit"),
        ("kurukshetra_movie_rel", "CineVista IMAX Premiere", "सिनेव्हिस्टा ब्लॉकबस्टर शो", "#450A0A", "#D6AD59", "cinevista"),
        ("sun_solar_roof_ark", "Amazzo 1-Day City Hub", "अमेज़ो जलद घरपोच सेवा", "#151B20", "#D6AD59", "amazzo"),
        ("deccan_tmt_steel_bars", "ARK Pay Instant Tap UPI", "आर्क पे झटपट डिजिटल पेमेंट", "#064E3B", "#D6AD59", "arkpay"),
        ("zomatoo_food_express", "Zomatoo • Hot Meals Fast", "झोमॅटू • गरमागरम जेवण घरपोच", "#7F1D1D", "#FCA5A5", "zomatoo")
    ]
    for slug, en, mr, bg, acc, brand_id in ads:
        signs.append(("commercial", slug, en, mr, bg, acc, "", "PROMO", brand_id))

    # 6. Public Safety (15)
    saf = [
        ("cctv_24h_surveillance", "24/7 CCTV Video Surveillance", "२४ तास सीसीटीव्ही नजर", "#7F1D1D", "#FCA5A5", "cctv", "CAM"),
        ("emergency_assembly_pt", "Emergency Assembly Point", "आपत्कालीन संमेलन स्थळ", "#14532D", "#86EFAC", "safe_exit", "SAFE"),
        ("high_voltage_danger", "Danger • High Voltage 11kV", "धोका • उच्च विद्युत दाब", "#422006", "#FACC15", "bolt", "11kV"),
        ("keep_city_clean_green", "Keep Indraprastha Clean", "आपले शहर स्वच्छ व सुंदर ठेवा", "#065F46", "#6EE7B7", "safe_exit", "ECO"),
        ("no_trespassing_author", "Restricted • No Trespassing", "प्रतिबंधित क्षेत्र • प्रवेश मनाई", "#7F1D1D", "#FFFFFF", "prohibit", "AUTH"),
        ("fire_extinguisher_here", "Fire Extinguisher Station", "अग्निशामक यंत्र येथे आहे", "#7F1D1D", "#FDE047", "warning", "FIRE"),
        ("emergency_exit_keep_clr", "Emergency Exit • Keep Clear", "आपत्कालीन निकास मार्ग", "#15803D", "#FFFFFF", "safe_exit", "EXIT"),
        ("no_smoking_fine_500", "No Smoking • Fine ARK 500", "धूम्रपान मनाई • दंड ५००", "#7F1D1D", "#FFFFFF", "prohibit", "FINE"),
        ("first_aid_station_aid", "First Aid Emergency Post", "प्रथमोपचार केंद्र", "#1E3A8A", "#FFFFFF", "hospital", "AID"),
        ("wear_safety_helmet", "Safety Helmet Mandatory", "सुरक्षा हेल्मेट सक्तीचे आहे", "#1E3A8A", "#93C5FD", "warning", "PPE"),
        ("do_not_lean_over_rail", "Do Not Lean Over Railing", "रेलिंगवर वाकून पाहू नका", "#7C2D12", "#FDBA74", "warning", "WARN"),
        ("beware_of_pickpockets", "Beware of Pickpockets", "खिशाकापूंपासून सावध राहा", "#422006", "#FBBF24", "warning", "INFO"),
        ("safe_drinking_water", "Safe Pure Drinking Water", "पिण्याचे शुद्ध व सुरक्षित पाणी", "#0369A1", "#FFFFFF", "safe_exit", "H2O"),
        ("wheelchair_accessible", "Step-Free Universal Access", "सर्वसमावेशक सुलभ प्रवेश", "#1E3A8A", "#FFFFFF", "accessibility", "ADA"),
        ("sound_horn_prohibited", "No Honking • Silence Zone", "हॉर्न वाजवण्यास मनाई", "#7F1D1D", "#FCA5A5", "prohibit", "QUIET")
    ]
    for slug, en, mr, bg, acc, ico, code in saf:
        signs.append(("public_safety", slug, en, mr, bg, acc, ico, code, ""))

    assert len(signs) == 120
    return signs


def render_sign_html_card(cat, slug, en, mr, bg, acc, ico, code, brand_id):
    if brand_id:
        uri = load_brand_data_uri(brand_id)
        icon_html = f'<img src="{uri}" style="width:68px;height:68px;object-fit:contain;filter:drop-shadow(0 2px 6px rgba(0,0,0,0.6));">'
    else:
        icon_html = SVGS.get(ico, SVGS["civic"])

    return f'''
    <div class="card" style="background:linear-gradient(145deg, {bg}, #0B0F14); border-color:{acc};">
      <div class="rivet tl"></div><div class="rivet tr"></div><div class="rivet bl"></div><div class="rivet br"></div>
      <div class="top">
        <span class="badge" style="background:{acc}; color:#0B0F14;">{cat.replace("_"," ").upper()}</span>
        <span class="code" style="color:{acc};">{code}</span>
      </div>
      <div class="mid">
        <div class="ico">{icon_html}</div>
        <div class="txt">
          <div class="en">{en}</div>
          <div class="mr" style="color:{acc};">{mr}</div>
        </div>
      </div>
      <div class="foot">MUNICIPAL CORPORATION OF INDRAPRASTHA &bull; APPROVED SIGNAGE</div>
    </div>'''


def build():
    SIGNAGE_DIR.mkdir(parents=True, exist_ok=True)
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    tmp_dir = ARTIFACT_DIR / "scratch" / "signage_batches"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    signs = get_sign_definitions()
    css = '''
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { width: 2048px; height: 1536px; background: #000; font-family: "Segoe UI", "Nirmala UI", sans-serif; display: grid; grid-template-columns: repeat(4, 512px); grid-template-rows: repeat(6, 256px); overflow: hidden; }
    .card { width: 512px; height: 256px; position: relative; border: 5px solid #D6AD59; padding: 14px 20px; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden; box-shadow: inset 0 0 28px rgba(0,0,0,0.55); }
    .rivet { width: 6px; height: 6px; border-radius: 50%; background: #CBD5E1; border: 1px solid #1E293B; position: absolute; opacity: 0.75; }
    .tl { top: 6px; left: 6px; } .tr { top: 6px; right: 6px; } .bl { bottom: 6px; left: 6px; } .br { bottom: 6px; right: 6px; }
    .top { display: flex; justify-content: space-between; align-items: center; padding: 0 4px; }
    .badge { font-size: 12px; font-weight: 900; padding: 3px 10px; border-radius: 5px; letter-spacing: 1.2px; }
    .code { font-size: 16px; font-weight: 900; letter-spacing: 1px; }
    .mid { display: flex; align-items: center; gap: 16px; padding: 4px; }
    .ico { width: 70px; height: 70px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
    .txt { flex: 1; min-width: 0; }
    .en { font-size: 23px; font-weight: 800; color: #FFFFFF; line-height: 1.18; letter-spacing: 0.2px; text-shadow: 0 2px 4px rgba(0,0,0,0.6); }
    .mr { font-size: 21px; font-weight: 700; font-family: "Nirmala UI", sans-serif; margin-top: 6px; line-height: 1.2; text-shadow: 0 2px 4px rgba(0,0,0,0.6); }
    .foot { font-size: 10px; color: #94A3B8; letter-spacing: 1.6px; border-top: 1px solid rgba(255,255,255,0.16); padding-top: 6px; text-align: center; }
    '''

    manifest_items = []
    # 5 sheets x 24 signs = 120 signs
    for batch_idx in range(5):
        chunk = signs[batch_idx * 24:(batch_idx + 1) * 24]
        cards_html = "\n".join(render_sign_html_card(*item) for item in chunk)
        html_file = tmp_dir / f"signs_batch_{batch_idx}.html"
        shot_file = tmp_dir / f"signs_batch_{batch_idx}.png"
        html_file.write_text(f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{cards_html}</body></html>', encoding="utf-8")

        subprocess.run([
            MSEDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--window-size=2048,1536", "--force-device-scale-factor=1",
            f"--screenshot={shot_file}", f"file:///{html_file.as_posix()}"
        ], check=True, capture_output=True)

        sheet = Image.open(shot_file).convert("RGBA")
        for i, (cat, slug, en, mr, bg, acc, ico, code, brand_id) in enumerate(chunk):
            r, c = i // 4, i % 4
            tile = sheet.crop((c * 512, r * 256, (c + 1) * 512, (r + 1) * 256))
            cat_dir = SIGNAGE_DIR / cat
            cat_dir.mkdir(parents=True, exist_ok=True)
            out_png = cat_dir / f"{slug}.png"
            tile.save(out_png, format="PNG", optimize=True)

            manifest_items.append({
                "id": f"gtm:sign_{cat}_{slug}",
                "slug": slug,
                "category": cat,
                "english_text": en,
                "marathi_text": mr,
                "texture_path": f"creative/source/signage/{cat}/{slug}.png",
                "resolution": [512, 256],
                "background_color": bg,
                "text_color": acc,
                "embedded_brand": brand_id or None,
                "placement_context": f"Indraprastha metropolitan {cat} zone",
                "sha256": hashlib.sha256(out_png.read_bytes()).hexdigest()
            })

    (MANIFESTS / "signage_manifest.json").write_text(json.dumps({
        "schema_version": "2.0.0",
        "description": "120 vector-grade bilingual municipal signs (512x256, genuine DirectWrite Devanagari + SVG icons + embedded 3D brand emblems).",
        "total_signs": len(manifest_items),
        "categories": {"transport": 20, "road": 20, "civic": 15, "store": 25, "commercial": 25, "public_safety": 15},
        "signs": manifest_items
    }, indent=2) + "\n", encoding="utf-8")
    print(f"SUCCESS: Rendered all 120 crisp 512x256 bilingual signs via DirectWrite Chromium!")


if __name__ == "__main__":
    build()
