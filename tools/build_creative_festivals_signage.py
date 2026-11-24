#!/usr/bin/env python3
"""Build 100 festival Blockbench 3D models and 120 bilingual signs for GTM Revision 4 Creative Track."""
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageColor, ImageDraw, ImageFont

import city_festival_art
import food_art

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
FESTIVALS_DIR = CREATIVE / "source" / "models" / "festivals"
SIGNAGE_DIR = CREATIVE / "source" / "signage"
MANIFESTS_DIR = CREATIVE / "manifests"

PALETTE = food_art.PALETTE

def generate_box(name, from_pt, to_pt, uv_origin=(0, 0), uv_size=(16, 16)):
    x, y, z = from_pt
    X, Y, Z = to_pt
    return {
        "origin": [round(8 - X, 3), round(y - 8, 3), round(z - 8, 3)],
        "size": [round(X - x, 3), round(Y - y, 3), round(Z - z, 3)],
        "uv": {
            "north": {"uv": list(uv_origin), "uv_size": list(uv_size)},
            "south": {"uv": list(uv_origin), "uv_size": list(uv_size)},
            "east": {"uv": list(uv_origin), "uv_size": list(uv_size)},
            "west": {"uv": list(uv_origin), "uv_size": list(uv_size)},
            "up": {"uv": list(uv_origin), "uv_size": list(uv_size)},
            "down": {"uv": list(uv_origin), "uv_size": list(uv_size)}
        }
    }

def make_geo(ident, cubes, tex_w=32, tex_h=32):
    return {
        "format_version": "1.12.0",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": f"geometry.gtm.{ident.replace('gtm:', '')}",
                    "texture_width": tex_w,
                    "texture_height": tex_h,
                    "visible_bounds_width": 3.0,
                    "visible_bounds_height": 3.0,
                    "visible_bounds_offset": [0.0, 1.0, 0.0]
                },
                "bones": [
                    {
                        "name": "root",
                        "pivot": [0.0, 0.0, 0.0],
                        "cubes": cubes
                    }
                ]
            }
        ]
    }

def build():
    FESTIVALS_DIR.mkdir(parents=True, exist_ok=True)
    SIGNAGE_DIR.mkdir(parents=True, exist_ok=True)
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Build 100 Festival Models
    raw_festivals = city_festival_art.festival()
    assert len(raw_festivals) == 100, f"Expected 100 festival recipes, got {len(raw_festivals)}"

    festival_manifest_items = []
    # Approved 8 themes mapping proposal
    # Approved target: Diwali 12, Holi 12, Navratri 12, Christmas 16, New Year 16, Independence Day 10, Ganesh Chaturthi 12, Monsoon 10 = 100
    theme_distribution = {
        "diwali": 12,
        "holi": 12,
        "navratri": 12,
        "christmas": 16,
        "new_year": 16,
        "independence_day": 10,
        "ganesh_chaturthi": 12,
        "monsoon": 10
    }

    fest_idx = 0
    approved_slots = []
    for theme_name, count in theme_distribution.items():
        for k in range(1, count + 1):
            approved_slots.append(f"{theme_name}_{k:02d}")
    assert len(approved_slots) == 100

    for key, (category, label, parts) in raw_festivals.items():
        ident = f"gtm:{key}"
        theme_prefix = key.split("_")[0]
        theme_dir = FESTIVALS_DIR / theme_prefix
        theme_dir.mkdir(parents=True, exist_ok=True)

        cubes = []
        for swatch, x, y, z, w, h, d in parts:
            cubes.append(generate_box(f"part_{swatch}", [x, y, z], [x + w, y + h, z + d]))

        geo_data = make_geo(ident, cubes, 64, 64)
        geo_file = theme_dir / f"{key}.geo.json"
        geo_file.write_text(json.dumps(geo_data, indent=2) + "\n", encoding="utf-8")

        # Placement bounds (headroom, clearance)
        min_x = min(p[1] for p in parts)
        max_x = max(p[1] + p[4] for p in parts)
        min_y = min(p[2] for p in parts)
        max_y = max(p[2] + p[5] for p in parts)
        min_z = min(p[3] for p in parts)
        max_z = max(p[3] + p[6] for p in parts)

        target_slot = approved_slots[fest_idx]

        festival_manifest_items.append({
            "id": ident,
            "theme": theme_prefix,
            "title": label,
            "model_path": f"creative/source/models/festivals/{theme_prefix}/{key}.geo.json",
            "cube_count": len(cubes),
            "activation_mode": "manual_staff_only",
            "placement_bounds": {
                "clearance_width": round(max_x - min_x, 2),
                "clearance_height": round(max_y - min_y, 2),
                "clearance_depth": round(max_z - min_z, 2),
                "headroom_required_blocks": math.ceil((max_y - min_y) / 16.0)
            },
            "approved_theme_migration": {
                "target_slot": target_slot,
                "target_theme": target_slot.rsplit("_", 1)[0]
            },
            "sha256": hashlib.sha256(geo_file.read_bytes()).hexdigest()
        })
        fest_idx += 1

    assert len(festival_manifest_items) == 100

    festivals_manifest = MANIFESTS_DIR / "festivals_manifest.json"
    festivals_manifest.write_text(json.dumps({
        "schema_version": "1.0.0",
        "description": "100 festival installations with manual-only activation switchboard and migration to approved 8 themes.",
        "total_models": len(festival_manifest_items),
        "themes_baseline": {
            "diwali": 13, "holi": 13, "ganesh": 13, "navratri": 13,
            "eid": 12, "sankranti": 12, "christmas": 12, "new_year": 12
        },
        "themes_approved_target": theme_distribution,
        "festivals": festival_manifest_items
    }, indent=2) + "\n", encoding="utf-8")
    print(f"SUCCESS: Generated 100 festival Blockbench models and {festivals_manifest.name}")

    # 2. Build 120 Bilingual Signs
    # Categories:
    # 20 transport, 20 road, 15 civic, 25 store, 25 commercial ads, 15 public safety
    sign_definitions = []

    # Transport (20)
    transport_signs = [
        ("marine_drive_station", "Marine Drive Station", "मरीन ड्राईव्ह स्टेशन", "#151B20", "#D6AD59"),
        ("churchgate_terminal", "Churchgate Terminal", "चर्चगेट टर्मिनस", "#151B20", "#D6AD59"),
        ("metro_line_3_cuffe", "Metro Line 3 Cuffe Parade", "मेट्रो ३ कफ परेड", "#236653", "#FFFFFF"),
        ("cst_heritage_junction", "CST Heritage Junction", "सीएसटी हेरिटेज जंक्शन", "#151B20", "#D6AD59"),
        ("bandra_west_pier", "Bandra West Ferry Pier", "वांद्रे पश्चिम जेट्टी", "#1B4F72", "#FFFFFF"),
        ("skylink_gondola_term", "SkyLink Cableway Terminal", "स्कायलिंक केबलवे टर्मिनल", "#AD5637", "#FFFFFF"),
        ("worli_sea_face_bus", "Worli Sea Face Bus Depot", "वरळी सी फेस बस आगार", "#7D6608", "#FFFFFF"),
        ("dadar_central_inter", "Dadar Central Interchange", "दादर मध्यवर्ती जंक्शन", "#151B20", "#D6AD59"),
        ("indrap_international", "Indraprastha Airport T2", "इंद्रप्रस्थ विमानतळ टी२", "#1A5276", "#FFFFFF"),
        ("apollo_bunder_ferry", "Apollo Bunder Ferry Dock", "अपोलो बंदर बोट धक्का", "#1B4F72", "#FFFFFF"),
        ("nariman_point_shuttle", "Nariman Pt Express Shuttle", "नरिमन पॉईंट एक्सप्रेस शटल", "#236653", "#FFFFFF"),
        ("colaba_causeway_tram", "Colaba Tram Stop", "कुलाबा ट्राम थांबा", "#7B241C", "#FFFFFF"),
        ("andheri_metro_link", "Andheri Metro Link Station", "अंधेरी मेट्रो लिंक स्थानक", "#1E8449", "#FFFFFF"),
        ("kurla_freight_yard", "Kurla Logistics Freight Yard", "कुर्ला मालधक्का यार्ड", "#4A235A", "#FFFFFF"),
        ("vikhroli_heliport_hub", "Vikhroli Heliport Hub", "विक्रोळी हेलिपोर्ट हब", "#151B20", "#D6AD59"),
        ("juhu_aerodrome_gate", "Juhu Aerodrome Gate 1", "जुहू विमानतळ प्रवेशद्वार १", "#1A5276", "#FFFFFF"),
        ("malabar_hill_ropeway", "Malabar Hill Ropeway Stn", "मलबार हिल रोपवे स्थानक", "#AD5637", "#FFFFFF"),
        ("sewri_harbour_port", "Sewri Container Port Gate", "शिवडी कंटेनर पोर्ट गेट", "#1B4F72", "#FFFFFF"),
        ("chembur_monorail", "Chembur Monorail Interchange", "चेंबर मोनोरेल स्थानक", "#7D6608", "#FFFFFF"),
        ("santacruz_domestic_t1", "Domestic Terminal T1", "देशांतर्गत टर्मिनल टी१", "#151B20", "#D6AD59")
    ]
    for s in transport_signs:
        sign_definitions.append(("transport", s[0], s[1], s[2], s[3], s[4]))

    # Road (20)
    road_signs = [
        ("sea_link_toll_gate", "Sea Link Toll Plaza 500m", "सी लिंक टोल नाका ५०० मी", "#151B20", "#D6AD59"),
        ("speed_limit_50", "Speed Limit 50 km/h", "कमाल वेग ५० किमी/तास", "#FFFFFF", "#C0392B"),
        ("no_parking_tow_away", "No Parking • Tow-Away Zone", "नो पार्किंग • टोइंग क्षेत्र", "#C0392B", "#FFFFFF"),
        ("one_way_traffic_ahead", "One Way Street Ahead", "एकमुखी रस्ता पुढे", "#2E86C1", "#FFFFFF"),
        ("pedestrian_crossing", "Pedestrian Crossing", "पादचारी क्रॉसिंग", "#2E86C1", "#FFFFFF"),
        ("heavy_vehicles_prohibit", "No Heavy Vehicles Allowed", "जड वाहनांना बंदी", "#C0392B", "#FFFFFF"),
        ("expressway_north_fast", "North Expressway Fast Lane", "उत्तर द्रुतगती मार्ग लेन", "#1E8449", "#FFFFFF"),
        ("u_turn_prohibited", "U-Turn Prohibited", "यु-टर्न मनाई", "#C0392B", "#FFFFFF"),
        ("hospital_quiet_zone", "Hospital Area • Silence Zone", "रुग्णालय क्षेत्र • शांतता झोन", "#2E86C1", "#FFFFFF"),
        ("school_zone_slow_down", "School Zone • Drive Slow", "शाळा क्षेत्र • वाहने हळू चालवा", "#F39C12", "#151B20"),
        ("coastal_road_exit_4", "Coastal Road Exit 4 • Worli", "किनारी रस्ता निकास ४ वरळी", "#1E8449", "#FFFFFF"),
        ("steep_descent_low_gear", "Steep Gradient • Use Low Gear", "तीव्र उतार • कमी गिअर वापरा", "#F39C12", "#151B20"),
        ("road_work_in_progress", "Road Work in Progress", "रस्त्याचे काम सुरू आहे", "#F39C12", "#151B20"),
        ("accident_blackspot_slow", "Accident Prone Area • Slow", "अपघात प्रवण क्षेत्र • सावध", "#C0392B", "#FFFFFF"),
        ("bus_lane_enforced", "Dedicated Bus Lane Only", "फक्त बस मार्गिका", "#8E44AD", "#FFFFFF"),
        ("parking_ark_pay_card", "Municipal Paid Parking", "महानगरपालिका सशुल्क वाहनतळ", "#2E86C1", "#FFFFFF"),
        ("roundabout_give_way", "Roundabout • Give Way", "गोलचक्कर • वाट द्या", "#2E86C1", "#FFFFFF"),
        ("bridge_clearance_4_5m", "Max Clearance Height 4.5m", "कमाल उंची मर्यादा ४.५ मी", "#F39C12", "#151B20"),
        ("stop_security_check", "Stop • Police Check Post", "थांबा • पोलीस तपासणी नाका", "#C0392B", "#FFFFFF"),
        ("free_left_turn_only", "Free Left Turn Only", "फक्त डावे वळण विनामूल्य", "#1E8449", "#FFFFFF")
    ]
    for s in road_signs:
        sign_definitions.append(("road", s[0], s[1], s[2], s[3], s[4]))

    # Civic (15)
    civic_signs = [
        ("city_hall_indrap", "Indraprastha City Hall", "इंद्रप्रस्थ महानगरपालिका", "#151B20", "#D6AD59"),
        ("central_police_hq", "Central Police Commissionerate", "मध्यवर्ती पोलीस मुख्यालय", "#1A252F", "#F1C40F"),
        ("district_court_complex", "District & Sessions Court", "जिल्हा व सत्र न्यायालय", "#2C3E50", "#ECF0F1"),
        ("general_civil_hospital", "Indraprastha General Hospital", "इंद्रप्रस्थ शासकीय रुग्णालय", "#C0392B", "#FFFFFF"),
        ("central_fire_station", "Fire & Rescue Headquarters", "अग्निशामक व बचाव मुख्यालय", "#C0392B", "#FFFFFF"),
        ("central_library_reading", "State Central Library", "राज्य मध्यवर्ती ग्रंथालय", "#1E8449", "#FFFFFF"),
        ("public_works_division", "Public Works Department", "सार्वजनिक बांधकाम विभाग", "#D35400", "#FFFFFF"),
        ("heritage_preservation", "Heritage Conservation Cell", "वारसा संवर्धन विभाग", "#7D6608", "#FFFFFF"),
        ("civil_defense_bunker", "Civic Emergency Operations", "नागरी आपत्कालीन केंद्र", "#922B21", "#FFFFFF"),
        ("tax_revenue_office", "Municipal Revenue & Tax Dept", "महानगरपालिका कर विभाग", "#2E4053", "#FFFFFF"),
        ("water_sanitation_hq", "Hydraulic & Water Works", "पाणी पुरवठा व मलनिस्सारण", "#2980B9", "#FFFFFF"),
        ("sub_registrar_deeds", "Property Registration Office", "नोंदणी व मुद्रांक कार्यालय", "#2C3E50", "#FFFFFF"),
        ("postal_sorting_centre", "General Post Office (GPO)", "मुख्य टपाल कार्यालय", "#C0392B", "#F1C40F"),
        ("citizens_service_center", "Citizen Suvidha Kendra", "नागरिक सुविधा केंद्र", "#27AE60", "#FFFFFF"),
        ("metro_authority_office", "Urban Transport Authority", "नागरी वाहतूक महामंडळ", "#151B20", "#D6AD59")
    ]
    for s in civic_signs:
        sign_definitions.append(("civic", s[0], s[1], s[2], s[3], s[4]))

    # Store (25)
    store_signs = [
        ("irani_cafe_1947", "Cafe Irani & Bakery • Est 1947", "कॅफे इराणी आणि बेकरी", "#5E3225", "#F4E7BF"),
        ("bombay_kirana_mart", "Indraprastha Kirana Stores", "इंद्रप्रस्थ किराणा स्टोअर्स", "#1E8449", "#FFFFFF"),
        ("sahyadri_sweets", "Sahyadri Mithai & Farsan", "सह्याद्री मिठाई व फरसाण", "#C0392B", "#F1C40F"),
        ("marine_jewellers", "Marine Gold & Diamonds", "मरीन ज्वेलर्स • शुद्ध सोने", "#151B20", "#D6AD59"),
        ("royal_tailors_gents", "Royal Master Tailors", "रॉयल टेलर्स • जेंट्स स्पेशालिस्ट", "#2C3E50", "#FFFFFF"),
        ("deccan_pharmacy_247", "Deccan Chemist • 24x7 Open", "डेक्कन मेडिकल व केमिस्ट", "#27AE60", "#FFFFFF"),
        ("apollo_hardware_tools", "Apollo Tools & Hardware", "अपोलो हार्डवेअर आणि टूल्स", "#D35400", "#FFFFFF"),
        ("chetak_auto_spares", "Chetak Genuine Auto Spares", "चेतक ऑटो पार्टस्", "#151B20", "#E74C3C"),
        ("konkan_fresh_fish", "Konkan Fresh Seafood Market", "कोकण ताजे मत्स्य केंद्र", "#2980B9", "#FFFFFF"),
        ("varun_electronics_tv", "Varun Digital Appliances", "वरुण इलेक्ट्रॉनिक्स", "#1F618D", "#FFFFFF"),
        ("national_book_house", "National Bookstore & Stationers", "नॅशनल बुक डेपो", "#7D6608", "#FFFFFF"),
        ("laxmi_textiles_silk", "Laxmi Silk Saree Emporium", "लक्ष्मी सिल्क साडी एम्पोरियम", "#922B21", "#F1C40F"),
        ("sharma_chaat_bhandar", "Sharma Famous Chaat Corner", "शर्मा प्रसिद्ध चाट भंडार", "#D35400", "#FFFFFF"),
        ("metro_footwear_shoes", "Metro Leather Works & Shoes", "मेट्रो फुटवेअर", "#151B20", "#D6AD59"),
        ("bazaar_vegetables", "Fresh Green Vegetable Market", "ताजी भाजीपाला बाजार", "#229954", "#FFFFFF"),
        ("gold_gym_fitness", "Indraprastha Fitness Club", "इंद्रप्रस्थ व्यायामशाळा", "#17202A", "#F39C12"),
        ("deccan_dry_fruits", "Deccan Royal Dry Fruits", "डेक्कन सुकामेवा केंद्र", "#784212", "#F9E79F"),
        ("hind_cycles_repairs", "Hind Cycle Depot & Repairs", "हिंद सायकल डेपो", "#2471A3", "#FFFFFF"),
        ("krishna_dairy_milk", "Krishna Pure Milk & Ghee", "कृष्ण डेअरी • ताजे दूध", "#2E86C1", "#FFFFFF"),
        ("shikari_sports_gear", "Shikari Sports & Armor Goods", "शिकारी स्पोर्ट्स अँड गियर", "#151B20", "#27AE60"),
        ("star_photo_studio", "Star Color Portrait Studio", "स्टार फोटो स्टुडिओ", "#8E44AD", "#FFFFFF"),
        ("lotus_flower_stall", "Lotus Puja Flowers & Garlands", "कमळ फुले व हार केंद्र", "#D98880", "#FFFFFF"),
        ("suruchi_spice_house", "Suruchi Pure Ground Spices", "सुरुची मसाले भांडार", "#BA4A00", "#FFFFFF"),
        ("shree_watch_co", "Shree Time Company & Watches", "श्री घड्याळ कंपनी", "#151B20", "#D6AD59"),
        ("chai_point_tapri", "Amrutulya Masala Chai", "अमृततुल्य कडक चहा", "#6E2C00", "#FAD7A0")
    ]
    for s in store_signs:
        sign_definitions.append(("store", s[0], s[1], s[2], s[3], s[4]))

    # Commercial Advertisements (25)
    ad_signs = [
        ("ark_bank_fixed_deposit", "ARK Bank • 8.5% Fixed Deposits", "एआरके बँक • विश्वासार्ह बचत", "#151B20", "#D6AD59"),
        ("vayu_5g_sim_unlimited", "Vayu Telecom • True 5G Fast", "वायू ५जी • अखंड कनेक्टिव्हिटी", "#0E6251", "#76D7C4"),
        ("chetak_cyclone_suv", "New Chetak Cyclone SUV • Book Now", "नवीन चेतक सायक्लॉन एसयूव्ही", "#78281F", "#FFFFFF"),
        ("deccan_towers_luxury", "Deccan Towers • Sea-Facing Flats", "डेक्कन टॉवर्स • लक्झरी घरे", "#151B20", "#D6AD59"),
        ("star_cola_chilled", "Drink Ice-Cold Star Cola", "थंडगार स्टार कोला प्या", "#C0392B", "#FFFFFF"),
        ("maratha_cement_durable", "Maratha Ultra Strong Cement", "मराठा अल्ट्रा स्ट्रॉंग सिमेंट", "#2C3E50", "#F39C12"),
        ("indrayani_tea_aroma", "Indrayani Gold Tea • Rich Taste", "इंद्रायणी गोल्ड चहा", "#7E5109", "#FAD7A0"),
        ("lotus_fashion_sale", "Black Lotus Fashion Week 50% Off", "ब्लॅक लोटस फॅशन सेल", "#151B20", "#BB8FCE"),
        ("varun_pumps_agri", "Varun Industrial Water Pumps", "वरुण पाणबुडी पंप", "#1B4F72", "#FFFFFF"),
        ("sahyadri_insurance", "Sahyadri Life & Health Cover", "सह्याद्री जीवन विमा", "#196F3D", "#FFFFFF"),
        ("taj_catering_events", "Royal Feast Catering Services", "शाही मेजवानी केटरिंग", "#641E16", "#FAD7A0"),
        ("maharaja_snack_pack", "Maharaja Crunchy Bhujia Sev", "महाराजा भुजिया शेव", "#D35400", "#F9E79F"),
        ("shikari_tyres_grip", "Shikari Heavy Radial Tyres", "शिकारी रेडियल टायर्स", "#17202A", "#F1C40F"),
        ("oceanic_cruises_goa", "Oceanic Ferry Mumbai to Goa", "ओशनिक क्रूझ • मुंबई ते गोवा", "#1A5276", "#FFFFFF"),
        ("hind_paints_weather", "Hind Weatherproof Wall Paints", "हिंद वेदरप्रूफ पेंट्स", "#884EA0", "#FFFFFF"),
        ("mumbai_city_fc_match", "Indraprastha FC • Match This Sun", "इंद्रप्रस्थ फुटबॉल क्लब सामना", "#2E86C1", "#FFFFFF"),
        ("deccan_watches_chron", "Deccan Sapphire Chronograph", "डेक्कन लक्झरी घड्याळे", "#151B20", "#D6AD59"),
        ("speed_petroleum_turbo", "Speed Fuel • Max Power & Mileage", "स्पीड पेट्रोल • अतिरिक्त मायलेज", "#B03A2E", "#F4D03F"),
        ("garuda_airline_fly", "Garuda Express • Daily Flights", "गरुड एक्सप्रेस • थेट उड्डाणे", "#117864", "#FFFFFF"),
        ("arya_security_cctv", "Arya Cyber & Physical Security", "आर्य सुरक्षा यंत्रणा", "#212F3D", "#5DADE2"),
        ("rajput_jewels_wedding", "Rajput Bridal Polki Collection", "राजपूत ब्रायडल दागिने", "#4A235A", "#F1C40F"),
        ("kurukshetra_movie_rel", "Kurukshetra Action Film In Cinema", "कुरुक्षेत्र चित्रपटगृहात", "#78281F", "#F7DC6F"),
        ("sun_solar_roof_ark", "Sun Solar Rooftop Power Systems", "सन सोलर सौर ऊर्जा प्रकल्प", "#D4AC0D", "#151B20"),
        ("deccan_tmt_steel_bars", "Deccan Fe550D TMT Rebars", "डेक्कन टीएमटी स्टील", "#2C3E50", "#E67E22"),
        ("zomatoo_food_express", "Zomatoo • Food Delivered Fast", "झोमॅटू • घरपोच गरमागरम जेवण", "#E74C3C", "#FFFFFF")
    ]
    for s in ad_signs:
        sign_definitions.append(("commercial", s[0], s[1], s[2], s[3], s[4]))

    # Public Safety / Instructions (15)
    safety_signs = [
        ("cctv_24h_surveillance", "24/7 CCTV Video Surveillance", "२४ तास सीसीटीव्ही नजर", "#C0392B", "#FFFFFF"),
        ("emergency_assembly_pt", "Emergency Evacuation Assembly Point", "आपत्कालीन संमेलन जागा", "#1E8449", "#FFFFFF"),
        ("high_voltage_danger", "Danger • High Voltage 11000V", "धोका • उच्च विद्युत दाब", "#F39C12", "#151B20"),
        ("keep_city_clean_green", "Keep Your City Clean & Green", "आपले शहर स्वच्छ ठेवा", "#27AE60", "#FFFFFF"),
        ("no_trespassing_author", "Restricted Area • No Trespassing", "प्रतिबंधित क्षेत्र • प्रवेश मनाई", "#C0392B", "#FFFFFF"),
        ("fire_extinguisher_here", "Fire Extinguisher Station", "अग्निशामक यंत्र येथे आहे", "#C0392B", "#FFFFFF"),
        ("emergency_exit_keep_clr", "Emergency Exit • Keep Clear", "आपत्कालीन निकास मार्ग", "#1E8449", "#FFFFFF"),
        ("no_smoking_fine_500", "No Smoking • Fine ARK 500", "धूम्रपान मनाई • दंड ५००", "#C0392B", "#FFFFFF"),
        ("first_aid_station_aid", "First Aid Emergency Post", "प्रथमोपचार केंद्र", "#2E86C1", "#FFFFFF"),
        ("wear_safety_helmet", "Safety Helmet Mandatory Area", "सुरक्षा हेल्मेट सक्तीचे आहे", "#2471A3", "#FFFFFF"),
        ("do_not_lean_over_rail", "Do Not Lean Over The Railing", "रेलिंगवर टेकू नका", "#E67E22", "#FFFFFF"),
        ("beware_of_pickpockets", "Beware of Pickpockets in Crowd", "खिशाकापूंपासून सावध रहा", "#F39C12", "#151B20"),
        ("safe_drinking_water", "Tested Safe Drinking Water", "पिण्याचे शुद्ध पाणी", "#2980B9", "#FFFFFF"),
        ("wheelchair_accessible", "Wheelchair Accessible Facility", "अपंग व ज्येष्ठ नागरिकांसाठी", "#1A5276", "#FFFFFF"),
        ("sound_horn_prohibited", "No Honking • Silence Zone", "हॉर्न वाजवण्यास मनाई", "#C0392B", "#FFFFFF")
    ]
    for s in safety_signs:
        sign_definitions.append(("public_safety", s[0], s[1], s[2], s[3], s[4]))

    assert len(sign_definitions) == 120, f"Expected 120 sign definitions, got {len(sign_definitions)}"

    sign_manifest_items = []
    # Render 120 signs as crisp 256x128 textures
    W, H = 256, 128
    for cat, slug, en_text, mr_text, bg_hex, fg_hex in sign_definitions:
        cat_dir = SIGNAGE_DIR / cat
        cat_dir.mkdir(parents=True, exist_ok=True)

        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        bg_rgb = ImageColor.getrgb(bg_hex)
        fg_rgb = ImageColor.getrgb(fg_hex)

        # Outer beveled frame
        draw.rounded_rectangle([2, 2, W - 3, H - 3], radius=8, fill=(*bg_rgb, 255), outline=(*ImageColor.getrgb("#151b20"), 255), width=3)
        # Inner contrast border
        draw.rounded_rectangle([6, 6, W - 7, H - 7], radius=6, outline=(*fg_rgb, 120), width=1)

        # Header bar or accent stripe
        draw.rectangle([10, 10, W - 11, 26], fill=(*fg_rgb, 40))

        # Category badge in top corner
        draw.rectangle([12, 12, 80, 24], fill=(*fg_rgb, 220))
        # Label in badge
        draw.text((16, 13), cat.upper()[:9], fill=(*bg_rgb, 255))

        # Main English typography (simulated clean vector sans layout)
        # Draw English text
        draw.text((14, 38), en_text[:30], fill=(*fg_rgb, 255))

        # Divider rule
        draw.line([(14, 66), (W - 14, 66)], fill=(*fg_rgb, 90), width=1)

        # Devanagari / Marathi subtitle
        draw.text((14, 76), mr_text[:36], fill=(*fg_rgb, 220))

        # Corner screw rivets
        for cx, cy in [(8, 8), (W - 9, 8), (8, H - 9), (W - 9, H - 9)]:
            draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(200, 200, 200, 200), outline=(50, 50, 50, 255))

        # Bottom municipal verification mark
        draw.text((14, 106), "MUNICIPAL CORP OF INDRAPRASTHA • APPROVED", fill=(*fg_rgb, 140))

        out_path = cat_dir / f"{slug}.png"
        img.save(out_path, optimize=True)

        sign_manifest_items.append({
            "id": f"gtm:sign_{cat}_{slug}",
            "slug": slug,
            "category": cat,
            "english_text": en_text,
            "marathi_text": mr_text,
            "texture_path": f"creative/source/signage/{cat}/{slug}.png",
            "resolution": [W, H],
            "background_color": bg_hex,
            "text_color": fg_hex,
            "placement_context": f"Indraprastha metropolitan {cat} zone",
            "sha256": hashlib.sha256(out_path.read_bytes()).hexdigest()
        })

    assert len(sign_manifest_items) == 120

    signage_manifest = MANIFESTS_DIR / "signage_manifest.json"
    signage_manifest.write_text(json.dumps({
        "schema_version": "1.0.0",
        "description": "120 bilingual municipal signs (English & Marathi/Devanagari) across 6 civic and commercial categories.",
        "total_signs": len(sign_manifest_items),
        "categories": {
            "transport": 20,
            "road": 20,
            "civic": 15,
            "store": 25,
            "commercial": 25,
            "public_safety": 15
        },
        "signs": sign_manifest_items
    }, indent=2) + "\n", encoding="utf-8")
    print(f"SUCCESS: Generated 120 bilingual signs at {signage_manifest.name}")

if __name__ == "__main__":
    build()
