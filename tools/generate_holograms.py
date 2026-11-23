import os

holograms = {
    'spawn_welcome': {
        'location': 'world:10.500:74.200:15.500',
        'lines': [
            '&6&l★ &e&lSDCRAFT &6&l- &f&lGTA ROLEPLAY &6&l★',
            '&7Welcome to the San Andreas City experience!',
            '&bType &f/testing &bto enter instant testing mode',
            '&aType &f/arsenal &afor Vehicles, Guns & Testing Gear',
            '&eInteract with NPCs around the city to take jobs & services',
            '&dPress &fM &dto view the live City Map & GPS'
        ]
    },
    'city_hall': {
        'location': 'world:10.500:73.500:3.500',
        'lines': [
            '&6&l🏛 &e&lCITY HALL &6&l🏛',
            '&fCivilian Registrations & City Administration',
            '&7Speak to &eMayor Sterling &7or &eClerk Davis',
            '&aGet Citizen IDs, Property Permits, City Directives'
        ]
    },
    'police_hq': {
        'location': 'world:120.500:69.500:-45.500',
        'lines': [
            '&9&l🛡 &b&lMETRO POLICE DEPARTMENT &9&l🛡',
            '&fPrecinct 1 - San Andreas Law Enforcement',
            '&7Speak to &bCaptain Miller &7for duty enlistment',
            '&cWanted level reports & armory check-in'
        ]
    },
    'general_hospital': {
        'location': 'world:-61.500:68.500:140.500',
        'lines': [
            '&c&l✚ &f&lMOUNT ZONAH GENERAL HOSPITAL &c&l✚',
            '&fEmergency Medical Services & Trauma Center',
            '&7Speak to &aChief Hayes &7for medical care & revive kits',
            '&eHealthcare subsidies & medkit dispensary'
        ]
    },
    'central_bank': {
        'location': 'world:56.500:70.500:-118.500',
        'lines': [
            '&2&l$ &a&lFIRST NATIONAL CITY BANK &2&l$',
            '&fSan Andreas Financial Reserve & Vault',
            '&7Speak to &aBanker Jenkins &7to access accounts & balance',
            '&eDeposit, withdraw, transfer & safety deposit vaults'
        ]
    },
    'motor_dealership': {
        'location': 'world:-150.500:70.500:-82.500',
        'lines': [
            '&e&l🏎 &6&lPREMIUM MOTORSPORTS DEALERSHIP &e&l🏎',
            '&fAuthorized MTVehicles Dealership & Showroom',
            '&7Speak to &eDealer Marcus &7or Mechanic Axel',
            '&bSedans, Supercars, Cruisers, Bikes & Helicopters',
            '&aTest drive vehicles instantly via &f/arsenal'
        ]
    },
    'metro_transit': {
        'location': 'world:26.500:71.500:63.500',
        'lines': [
            '&3&l🚆 &b&lSAN ANDREAS METRO & TRANSIT &3&l🚆',
            '&fTrainCarts High-Speed Rail Network',
            '&7Speak to &bConductor Vance &7for route maps',
            '&eAutomated trains arriving every 60 seconds'
        ]
    },
    'gas_station': {
        'location': 'world:-204.500:73.500:60.500',
        'lines': [
            '&6&l⛽ &e&lCITY CENTRAL GAS & REPAIR &6&l⛽',
            '&fVehicle Refuel, Maintenance & Roadside Assist',
            '&7Speak to &eAttendant Otis &7for Jerry Cans & Tuning',
            '&aKeep your vehicle fueled & tires inflated'
        ]
    },
    'fire_rescue': {
        'location': 'world:190.500:73.500:86.500',
        'lines': [
            '&4&l🚒 &c&lSAN ANDREAS FIRE & RESCUE &4&l🚒',
            '&fStation 4 - Hazardous Incident Response',
            '&7Speak to &cChief Sullivan &7for emergency calls',
            '&eFire extinguishers, heavy extraction & hazard gear'
        ]
    },
    'testing_arsenal': {
        'location': 'world:8.500:73.500:17.500',
        'lines': [
            '&d&l⚔ &5&lDEVELOPER & TESTING ARSENAL &d&l⚔',
            '&eInstant Creative & Roleplay Testing Suite',
            '&fClick or run &a/arsenal &f/ &a/testing',
            '&bAll Vehicles • QualityArmory Guns • Ammo • Godmode'
        ]
    }
}

target_dirs = [
    'd:/Games/SDCRAFT/sdcraft_isolated/plugins/DecentHolograms/holograms',
    'd:/Games/SDCRAFT/github_gtm_repo/plugins/DecentHolograms/holograms'
]

for base_dir in target_dirs:
    os.makedirs(base_dir, exist_ok=True)
    for name, data in holograms.items():
        filepath = os.path.join(base_dir, f'{name}.yml')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"location: {data['location']}\n")
            f.write("enabled: true\n")
            f.write("display-range: 48\n")
            f.write("update-range: 48\n")
            f.write("update-interval: 20\n")
            f.write("down-origin: false\n")
            f.write("pages:\n")
            f.write("  - lines:\n")
            for line in data['lines']:
                f.write(f"      - content: '{line}'\n")
                f.write("        height: 0.3\n")
        print(f"Wrote {filepath}")

print("All 10 holograms generated successfully in both isolated and repo staging.")
