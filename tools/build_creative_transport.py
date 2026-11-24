#!/usr/bin/env python3
"""Generate Transport Art specifications, 3D Blockbench geometries, seating anchors, pivots, and migration mappings."""
import os, sys, json, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CREATIVE = ROOT / "creative"
SOURCE = CREATIVE / "source"
MODELS_DIR = SOURCE / "models" / "transport"
MANIFESTS = CREATIVE / "manifests"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
MANIFESTS.mkdir(parents=True, exist_ok=True)

ROAD_TARGETS = [
    # 7 Hatchbacks
    ("hatchback_swift", "Maruva Swift 1.2", "maruva", "hatchback", [1.6, 1.45, 3.8], ["normal", "damaged", "critical", "wreck"]),
    ("hatchback_baleno", "Maruva Baleno Premium", "maruva", "hatchback", [1.7, 1.45, 3.9], ["normal", "damaged", "critical", "wreck"]),
    ("hatchback_wagonr", "Maruva Wagon Tallboy", "maruva", "hatchback", [1.5, 1.65, 3.6], ["normal", "damaged", "critical", "wreck"]),
    ("hatchback_alto", "Maruva Alto City", "maruva", "hatchback", [1.45, 1.45, 3.4], ["normal", "damaged", "critical", "wreck"]),
    ("hatchback_i10", "Hondo CityGrand 1.2", "hondo", "hatchback", [1.65, 1.5, 3.8], ["normal", "damaged", "critical", "wreck"]),
    ("hatchback_tiago", "Tavara Tiago Compact", "tavara", "hatchback", [1.65, 1.5, 3.75], ["normal", "damaged", "critical", "wreck"]),
    ("hatchback_i20", "Hondo AeroSport 1.0T", "hondo", "hatchback", [1.75, 1.45, 4.0], ["normal", "damaged", "critical", "wreck"]),
    # 6 Sedans
    ("sedan_dzire", "Maruva Swift Sedan", "maruva", "sedan", [1.7, 1.5, 4.0], ["normal", "damaged", "critical", "wreck"]),
    ("sedan_aura", "Hondo Compact Sedan", "hondo", "sedan", [1.68, 1.5, 3.99], ["normal", "damaged", "critical", "wreck"]),
    ("sedan_amaze", "Hondo Accord Classic", "hondo", "sedan", [1.7, 1.5, 4.0], ["normal", "damaged", "critical", "wreck"]),
    ("sedan_verna", "Hondo Verna Executive", "hondo", "sedan", [1.75, 1.48, 4.4], ["normal", "damaged", "critical", "wreck"]),
    ("sedan_city", "Toyora City Cruiser", "toyora", "sedan", [1.74, 1.48, 4.5], ["normal", "damaged", "critical", "wreck"]),
    ("sedan_slavia", "Toyora Regal Sedan", "toyora", "sedan", [1.75, 1.5, 4.54], ["normal", "damaged", "critical", "wreck"]),
    # 12 SUVs
    ("suv_thar", "Wahindra Thar 4x4 Offroader", "wahindra", "suv", [1.85, 1.9, 4.0], ["normal", "damaged", "critical", "wreck"]),
    ("suv_scorpio", "Wahindra Scorpio-N Patrol", "wahindra", "suv", [1.9, 1.85, 4.66], ["normal", "damaged", "critical", "wreck"]),
    ("suv_bolero", "Wahindra Bolero Rugged", "wahindra", "suv", [1.75, 1.88, 4.1], ["normal", "damaged", "critical", "wreck"]),
    ("suv_xuv700", "Wahindra XUV Sovereign", "wahindra", "suv", [1.9, 1.75, 4.7], ["normal", "damaged", "critical", "wreck"]),
    ("suv_fortuner", "Toyora Fortuner 4WD", "toyora", "suv", [1.85, 1.83, 4.8], ["normal", "damaged", "critical", "wreck"]),
    ("suv_safari", "Tavara Safari Flagship", "tavara", "suv", [1.9, 1.78, 4.67], ["normal", "damaged", "critical", "wreck"]),
    ("suv_harrier", "Tavara Harrier Monocoque", "tavara", "suv", [1.89, 1.7, 4.6], ["normal", "damaged", "critical", "wreck"]),
    ("suv_nexon", "Tavara Nexon EV", "tavara", "suv", [1.8, 1.6, 3.99], ["normal", "damaged", "critical", "wreck"]),
    ("suv_punch", "Tavara Punch Micro-SUV", "tavara", "suv", [1.74, 1.6, 3.82], ["normal", "damaged", "critical", "wreck"]),
    ("suv_creta", "Hondo Urban Cross", "hondo", "suv", [1.79, 1.63, 4.3], ["normal", "damaged", "critical", "wreck"]),
    ("suv_seltos", "Hondo Trail Master", "hondo", "suv", [1.8, 1.64, 4.36], ["normal", "damaged", "critical", "wreck"]),
    ("suv_jimny", "Maruva Jimny 5-Door", "maruva", "suv", [1.64, 1.72, 3.98], ["normal", "damaged", "critical", "wreck"]),
    # 5 Luxury
    ("luxury_series3", "SD Executive 3-Series", "sd_motors", "luxury", [1.82, 1.44, 4.7], ["normal", "damaged", "critical", "wreck"]),
    ("luxury_eclass", "SD Prestige E-Chassis", "sd_motors", "luxury", [1.85, 1.47, 4.9], ["normal", "damaged", "critical", "wreck"]),
    ("luxury_q7", "SD Quattro Seven SUV", "sd_motors", "luxury", [1.97, 1.74, 5.06], ["normal", "damaged", "critical", "wreck"]),
    ("luxury_x5", "SD Bavaria X-Drive", "sd_motors", "luxury", [2.0, 1.75, 4.92], ["normal", "damaged", "critical", "wreck"]),
    ("luxury_rangerover", "SD Sovereign Imperial", "sd_motors", "luxury", [2.05, 1.87, 5.05], ["normal", "damaged", "critical", "wreck"]),
    # 8 Motorcycles
    ("moto_splendor", "Veero Splendor 100", "veero", "motorcycle", [0.75, 1.05, 2.0], ["normal", "damaged", "wreck"]),
    ("moto_classic350", "Royal Iron Classic 350", "royal_iron", "motorcycle", [0.8, 1.1, 2.15], ["normal", "damaged", "wreck"]),
    ("moto_bullet350", "Royal Iron Bullet 350", "royal_iron", "motorcycle", [0.8, 1.12, 2.15], ["normal", "damaged", "wreck"]),
    ("moto_pulsar", "Wahindra Pulsar 220F", "wahindra", "motorcycle", [0.78, 1.15, 2.05], ["normal", "damaged", "wreck"]),
    ("moto_apache", "Tavara Apache RTR", "tavara", "motorcycle", [0.79, 1.1, 2.08], ["normal", "damaged", "wreck"]),
    ("moto_duke", "SD Duke 390 Naked", "sd_motors", "motorcycle", [0.82, 1.1, 2.05], ["normal", "damaged", "wreck"]),
    ("moto_himalayan", "Royal Iron Himalayan Explorer", "royal_iron", "motorcycle", [0.85, 1.35, 2.2], ["normal", "damaged", "wreck"]),
    ("moto_r15", "Hondo Supersport 150", "hondo", "motorcycle", [0.72, 1.13, 1.99], ["normal", "damaged", "wreck"]),
    # 4 Scooters
    ("scooter_activa", "Hondo Activa 6G Commuter", "hondo", "scooter", [0.7, 1.15, 1.83], ["normal", "damaged", "wreck"]),
    ("scooter_jupiter", "Tavara Jupiter Metal", "tavara", "scooter", [0.68, 1.15, 1.83], ["normal", "damaged", "wreck"]),
    ("scooter_access", "Maruva Access 125", "maruva", "scooter", [0.69, 1.16, 1.87], ["normal", "damaged", "wreck"]),
    ("scooter_ather", "Tavara Ather 450X EV", "tavara", "scooter", [0.73, 1.25, 1.81], ["normal", "damaged", "wreck"]),
    # 3 Rickshaws
    ("rickshaw_traditional", "Indra Auto CNG Passenger", "wahindra", "rickshaw", [1.3, 1.75, 2.6], ["normal", "damaged", "wreck"]),
    ("rickshaw_electric", "Indra Mayuri E-Rickshaw", "tavara", "rickshaw", [1.0, 1.8, 2.75], ["normal", "damaged", "wreck"]),
    ("rickshaw_cargo", "Indra Loader Cargo 3-Wheeler", "wahindra", "rickshaw", [1.4, 1.75, 3.1], ["normal", "damaged", "wreck"]),
    # 4 Buses
    ("bus_single_deck", "Tavara Starbus City Transit", "tavara", "bus", [2.5, 3.2, 11.5], ["normal", "damaged", "wreck"]),
    ("bus_double_deck", "BEST Coastal Double-Decker", "tavara", "bus", [2.5, 4.4, 10.5], ["normal", "damaged", "wreck"]),
    ("bus_minibus", "Wahindra Metro Minibus", "wahindra", "bus", [2.1, 2.8, 6.8], ["normal", "damaged", "wreck"]),
    ("bus_intercity_coach", "Tavara Garuda Air-Suspension", "tavara", "bus", [2.6, 3.6, 13.5], ["normal", "damaged", "wreck"]),
    # 7 Commercial Trucks & Vans
    ("comm_mini_cargo", "Tavara Ace Mini Truck (Chhota Hathi)", "tavara", "commercial", [1.5, 1.85, 3.8], ["normal", "damaged", "wreck"]),
    ("comm_pickup", "Wahindra Bolero Maxi Truck", "wahindra", "commercial", [1.7, 1.9, 4.9], ["normal", "damaged", "wreck"]),
    ("comm_light_truck", "Tavara 407 Light Hauler", "tavara", "commercial", [2.1, 2.6, 5.5], ["normal", "damaged", "wreck"]),
    ("comm_medium_truck", "Tavara 1613 Medium Goods", "tavara", "commercial", [2.4, 3.1, 8.2], ["normal", "damaged", "wreck"]),
    ("comm_tipper", "Wahindra Blazo Heavy Tipper", "wahindra", "commercial", [2.5, 3.5, 7.8], ["normal", "damaged", "wreck"]),
    ("comm_container", "Tavara Signa 4825 Multi-Axle", "tavara", "commercial", [2.55, 3.9, 14.0], ["normal", "damaged", "wreck"]),
    ("comm_delivery_van", "Wahindra Supro Delivery Van", "wahindra", "commercial", [1.6, 1.95, 3.9], ["normal", "damaged", "wreck"]),
    # 6 Emergency Vehicles
    ("emerg_police_suv", "SDPD Tactical Interceptor Scorpio", "wahindra", "emergency", [1.9, 1.95, 4.7], ["normal", "damaged", "critical", "wreck"]),
    ("emerg_patrol_sedan", "SDPD Highway Patrol Dzire", "maruva", "emergency", [1.7, 1.55, 4.0], ["normal", "damaged", "critical", "wreck"]),
    ("emerg_ambulance", "Mount Zonah Advanced Life Support Van", "tavara", "emergency", [1.95, 2.45, 5.2], ["normal", "damaged", "wreck"]),
    ("emerg_fire_engine", "Indra Fire & Rescue Water Bowzer", "tavara", "emergency", [2.5, 3.4, 9.2], ["normal", "damaged", "wreck"]),
    ("emerg_recovery_truck", "Highway Heavy Tow Crane", "wahindra", "emergency", [2.4, 3.0, 7.5], ["normal", "damaged", "wreck"]),
    ("emerg_rescue_van", "Disaster Response Mobile Command", "tavara", "emergency", [2.1, 2.7, 6.2], ["normal", "damaged", "wreck"]),
    # 3 Agricultural
    ("agri_compact_tractor", "Wahindra Oja Compact Tractor", "wahindra", "agricultural", [1.4, 2.1, 2.8], ["normal", "damaged", "wreck"]),
    ("agri_heavy_tractor", "Wahindra Arjun Novo Heavy Tractor", "wahindra", "agricultural", [1.8, 2.5, 3.6], ["normal", "damaged", "wreck"]),
    ("agri_harvester", "Wahindra Coastal Combine Harvester", "wahindra", "agricultural", [3.2, 3.8, 6.8], ["normal", "damaged", "wreck"])
]

RAIL_ROPEWAY_TARGETS = [
    ("local_driving_cab", "Mumbai Suburban Driving Motor Coach (Cab)", "indra_suburban", "rail", [3.2, 3.8, 20.5], "Transverse 3x3 wooden benches, ceiling fans, open sliding doorways, baggage lofts"),
    ("local_motor", "Mumbai Suburban Motor Coach", "indra_suburban", "rail", [3.2, 3.8, 20.5], "High-capacity commuter layout, overhead pantograph, standing grab poles"),
    ("local_trailer", "Mumbai Suburban Trailer Coach", "indra_suburban", "rail", [3.2, 3.8, 20.5], "Second-class general coach with partition grills and ceiling ventilation"),
    ("metro_lead", "Indra Metro Lead Motor Car", "indra_metro", "rail", [2.9, 3.6, 21.0], "Modern aerodynamically shaped cab, digital route displays, longitudinal seating"),
    ("metro_middle", "Indra Metro Intermediate Car", "indra_metro", "rail", [2.9, 3.6, 21.0], "Continuous vestibule walkway, stainless steel stanchions, LED route maps"),
    ("metro_accessible", "Indra Metro Universal Access Car", "indra_metro", "rail", [2.9, 3.6, 21.0], "Dedicated wheelchair securement bays, priority seating, tactile boarding strip"),
    ("skylink_cabin", "SkyLink 10-Passenger Aerial Gondola", "skylink", "ropeway", [2.2, 2.4, 2.8], "Suspended cabin with panoramic acrylic windows, dual perimeter benches"),
    ("skylink_accessible", "SkyLink Universal Barrier-Free Cabin", "skylink", "ropeway", [2.4, 2.4, 3.2], "Level roll-on boarding, folding jump seats, safety anchor straps"),
    ("skylink_grip", "SkyLink Detachable Cable Grip Assembly", "skylink", "ropeway", [0.6, 1.2, 0.8], "Spring-loaded dual clamp grip mechanism with guide rollers"),
    ("skylink_terminal_machinery", "SkyLink Terminal Drive Bullwheel & Bullgear", "skylink", "ropeway", [4.5, 3.2, 4.5], "Tension hydraulic piston, main drive bullwheel and decelerator rails")
]

HELI_MARINE_TARGETS = [
    # 4 Helicopters
    ("heli_police", "SDPD Air Support Patrol Helicopter", "police", "helicopter", [2.4, 3.4, 11.2], ["main_rotor", "tail_rotor", "searchlight", "skid_left", "skid_right"]),
    ("heli_media", "Indra 24 SkyCam Broadcast Helicopter", "media", "helicopter", [2.2, 3.2, 10.5], ["main_rotor", "tail_rotor", "gimbal_camera", "skid_left", "skid_right"]),
    ("heli_rescue", "Coast Guard SAR Twin-Turbine Rescue Chopper", "rescue", "helicopter", [2.8, 4.0, 13.5], ["main_rotor", "tail_rotor", "winch_hoist", "wheel_gear"]),
    ("heli_civilian", "Executive VIP Luxury Corporate Helicopter", "civilian", "helicopter", [2.5, 3.5, 12.0], ["main_rotor", "tail_rotor", "cabin_door_left", "cabin_door_right"]),
    # 8 Marine
    ("marine_ferry", "Indra Gateway Double-Deck Passenger Ferry", "transit", "marine", [6.5, 4.8, 24.0], ["rudder", "starboard_prop", "port_prop", "loading_ramp"]),
    ("marine_speedboat", "Marine Police Interceptor Speedboat", "police", "marine", [2.4, 1.8, 7.5], ["outboard_motor_1", "outboard_motor_2", "windshield"]),
    ("marine_police_launch", "SDPD Harbour Patrol Steel Launch", "police", "marine", [3.8, 3.2, 14.5], ["mast_radar", "twin_screws", "deck_gun_mount"]),
    ("marine_rescue", "Coastal Lifeboat All-Weather Rescue Craft", "rescue", "marine", [3.6, 2.9, 11.8], ["survivor_scaffold", "radar_dome", "jet_drives"]),
    ("marine_fishing", "Sassoon Docks Wooden Fishing Trawler", "commercial", "marine", [4.2, 4.5, 16.0], ["trawl_winch", "fish_hold_hatch", "mast_rigging"]),
    ("marine_yacht", "Maya Harbour Luxury Motor Yacht", "luxury", "marine", [5.0, 4.2, 18.5], ["flybridge_helm", "sunpad_stern", "swim_platform"]),
    ("marine_cargo", "Coastal Container & Bulk Freight Barge", "commercial", "marine", [8.5, 5.0, 38.0], ["deck_crane", "cargo_hold_hatches", "stern_wheelhouse"]),
    ("marine_water_taxi", "Express Harbour Catamaran Water Taxi", "transit", "marine", [3.2, 2.2, 9.8], ["twin_catamaran_hulls", "passenger_cabin_door"])
]

def generate_transport():
    transport_manifest = []

    # 1. Road Vehicles
    for vid, name, mfg, cat, dims, variants in ROAD_TARGETS:
        w, h, l = dims
        geo_id = f"geometry.gtm.{vid}"
        geo_data = {
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {
                    "identifier": geo_id,
                    "texture_width": 128,
                    "texture_height": 128,
                    "visible_bounds_width": round(w + 1.0, 2),
                    "visible_bounds_height": round(h + 0.8, 2),
                    "visible_bounds_offset": [0, round(h / 2, 2), 0]
                },
                "bones": [
                    {"name": "root", "pivot": [0, 0, 0]},
                    {"name": "chassis", "parent": "root", "pivot": [0, 0.4, 0],
                     "cubes": [{"origin": [-round(w*8, 1), 6, -round(l*8, 1)], "size": [round(w*16, 1), round(h*12, 1), round(l*16, 1)], "uv": [0, 0]}]},
                    {"name": "wheel_fl", "parent": "root", "pivot": [-round(w*7, 1), 6, round(l*5, 1)]},
                    {"name": "wheel_fr", "parent": "root", "pivot": [round(w*7, 1), 6, round(l*5, 1)]},
                    {"name": "wheel_rl", "parent": "root", "pivot": [-round(w*7, 1), 6, -round(l*5, 1)]},
                    {"name": "wheel_rr", "parent": "root", "pivot": [round(w*7, 1), 6, -round(l*5, 1)]},
                    {"name": "steering_wheel", "parent": "chassis", "pivot": [-round(w*3, 1), round(h*7, 1), round(l*2, 1)]}
                ]
            }]
        }
        geo_path = MODELS_DIR / f"{vid}.geo.json"
        geo_path.write_text(json.dumps(geo_data, indent=2), encoding="utf-8")

        # Anchors and collision proxy
        anchors = [
            {"id": "driver_seat", "position": [-round(w * 0.25, 2), round(h * 0.35, 2), round(l * 0.05, 2)], "yaw": 0},
            {"id": "passenger_front", "position": [round(w * 0.25, 2), round(h * 0.35, 2), round(l * 0.05, 2)], "yaw": 0}
        ]
        if cat in ("suv", "sedan", "luxury", "emergency"):
            anchors.append({"id": "rear_seat_left", "position": [-round(w * 0.25, 2), round(h * 0.35, 2), -round(l * 0.25, 2)], "yaw": 0})
            anchors.append({"id": "rear_seat_right", "position": [round(w * 0.25, 2), round(h * 0.35, 2), -round(l * 0.25, 2)], "yaw": 0})

        collision_boxes = [{
            "min": [-round(w / 2, 2), 0.0, -round(l / 2, 2)],
            "max": [round(w / 2, 2), round(h, 2), round(l / 2, 2)]
        }]

        transport_manifest.append({
            "id": f"gtm:{vid}",
            "title": name,
            "manufacturer": mfg,
            "category": "road",
            "subcategory": cat,
            "dimensions_blocks": dims,
            "geometry": geo_id,
            "variants": variants,
            "anchors": anchors,
            "collision_boxes": collision_boxes,
            "delivery_livery": "zomatoo_swiffy_ready" if cat == "scooter" else None,
            "json_path": str(geo_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(geo_path.read_bytes()).hexdigest()
        })

    # 2. Rail & Ropeway
    for rid, name, mfg, cat, dims, interior in RAIL_ROPEWAY_TARGETS:
        w, h, l = dims
        geo_id = f"geometry.gtm.{rid}"
        geo_data = {
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {"identifier": geo_id, "texture_width": 256, "texture_height": 256, "visible_bounds_width": w + 2.0, "visible_bounds_height": h + 1.0, "visible_bounds_offset": [0, h/2, 0]},
                "bones": [
                    {"name": "root", "pivot": [0, 0, 0]},
                    {"name": "body", "parent": "root", "pivot": [0, 1.0, 0],
                     "cubes": [{"origin": [-round(w*8, 1), 4, -round(l*8, 1)], "size": [round(w*16, 1), round(h*16, 1), round(l*16, 1)], "uv": [0, 0]}]},
                    {"name": "doors_left", "parent": "body", "pivot": [-round(w*8, 1), 4, 0]},
                    {"name": "doors_right", "parent": "body", "pivot": [round(w*8, 1), 4, 0]},
                    {"name": "interior_fittings", "parent": "body", "pivot": [0, 4, 0]}
                ]
            }]
        }
        geo_path = MODELS_DIR / f"{rid}.geo.json"
        geo_path.write_text(json.dumps(geo_data, indent=2), encoding="utf-8")

        transport_manifest.append({
            "id": f"gtm:{rid}",
            "title": name,
            "operator": mfg,
            "category": cat,
            "dimensions_blocks": dims,
            "interior_description": interior,
            "geometry": geo_id,
            "variants": ["normal", "maintenance"],
            "json_path": str(geo_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(geo_path.read_bytes()).hexdigest()
        })

    # 3. Helicopters & Marine
    for hid, name, subcat, cat, dims, pivots in HELI_MARINE_TARGETS:
        w, h, l = dims
        geo_id = f"geometry.gtm.{hid}"
        bones = [{"name": "root", "pivot": [0, 0, 0]}, {"name": "hull", "parent": "root", "pivot": [0, 0.5, 0]}]
        for p in pivots:
            bones.append({"name": p, "parent": "hull", "pivot": [0, 1.0, 0]})
        geo_data = {
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {"identifier": geo_id, "texture_width": 256, "texture_height": 256, "visible_bounds_width": w + 2.0, "visible_bounds_height": h + 1.0, "visible_bounds_offset": [0, h/2, 0]},
                "bones": bones
            }]
        }
        geo_path = MODELS_DIR / f"{hid}.geo.json"
        geo_path.write_text(json.dumps(geo_data, indent=2), encoding="utf-8")

        transport_manifest.append({
            "id": f"gtm:{hid}",
            "title": name,
            "category": cat,
            "dimensions_blocks": dims,
            "pivots": pivots,
            "geometry": geo_id,
            "variants": ["normal", "emergency_service"],
            "json_path": str(geo_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(geo_path.read_bytes()).hexdigest()
        })

    # Save full transport manifest
    (MANIFESTS / "transport_art_manifest.json").write_text(json.dumps(transport_manifest, indent=2), encoding="utf-8")

    # Compatibility Mapping: Connect current 13x5 procedural road vehicles to approved 65 distinct models
    proc_vehicles = ["sedan", "sportscar", "suv", "cruiser", "interceptor", "motorcycle", "scooter", "rickshaw", "bus", "van", "truck", "ambulance", "fire_truck"]
    proc_variants = ["city", "courier", "rescue", "touring", "utility"]
    mapping_table = {}
    idx = 0
    for pv in proc_vehicles:
        for pvar in proc_variants:
            legacy_id = f"gtm:{pv}_{pvar}"
            if idx < len(ROAD_TARGETS):
                new_item = ROAD_TARGETS[idx]
                mapping_table[legacy_id] = {
                    "approved_id": f"gtm:{new_item[0]}",
                    "approved_title": new_item[1],
                    "manufacturer": new_item[2],
                    "category": new_item[3],
                    "migration_action": "bind_geometry_and_physics_anchor"
                }
            idx += 1

    (MANIFESTS / "transport_catalog_mapping.json").write_text(json.dumps(mapping_table, indent=2), encoding="utf-8")
    print(f"Generated {len(transport_manifest)} transport specifications (65 road, 10 rail/ropeway, 4 helis, 8 marine).")
    print(f"Generated legacy-to-approved migration table for all {len(mapping_table)} existing procedural models.")
    return transport_manifest

if __name__ == "__main__":
    generate_transport()
    print("SUCCESS: Transport art & vehicle mappings complete!")
