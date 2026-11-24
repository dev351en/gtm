#!/usr/bin/env python3
"""Add28 original festival art proposals and select the approved100 designs.

The original100 designs are preserved, including Eid and Sankranti. Selection
is art interchange metadata, not a runtime registry or festival activation.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

from PIL import Image

import gtm128_core as core
import studio_3d_engine as s3d

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "creative/generated_128"
APPROVED = {"diwali": 12, "holi": 12, "navratri": 12, "christmas": 16,
            "new_year": 16, "independence_day": 10, "ganesh_chaturthi": 12, "monsoon": 10}
ADDITIONS = {"independence_day": 10, "monsoon": 10, "christmas": 4, "new_year": 4}


class Sculpture:
    def __init__(self):
        self.pb = s3d.PartBuilder()
        self.i = 0

    def box(self, x, y, z, w, h, d, material, name="detail", rot=None):
        self.pb.box(x, y, z, w, h, d, mat=material, name=f"{name}_{self.i}", rot=rot)
        self.i += 1

    def center(self, x, y, z, w, h, d, material, name="detail", rot=None):
        self.box(x - w / 2, y, z - d / 2, w, h, d, material, name, rot)

    def disk(self, x, y, z, rx, rz, height, material, bands=8):
        for i in range(bands):
            z0 = -rz + 2 * rz * i / bands
            half = rx * math.sqrt(max(.03, 1 - ((z0 + rz / bands) / rz) ** 2))
            self.box(x - half, y, z + z0, half * 2, height, rz * 2 / bands, material, "rounded_profile")

    def sphere(self, x, y, z, radius, material, levels=8):
        for i in range(levels):
            y0 = -radius + 2 * radius * i / levels
            r = radius * math.sqrt(max(.02, 1 - ((y0 + radius / levels) / radius) ** 2))
            self.disk(x, y + y0, z, r, r, 2 * radius / levels, material, bands=6)

    def vertical_ring(self, x, y, z, radius, width, depth, material, steps=20):
        length = 2 * math.pi * radius / steps + .2
        for i in range(steps):
            angle = i * 360 / steps
            self.center(x + radius * math.cos(math.radians(angle)), y + radius * math.sin(math.radians(angle)) - width / 2,
                        z, length, width, depth, material, "ring_segment", rot=[0, 0, angle + 90])

    def pedestal(self, width=16, depth=12, height=2, material="sandstone"):
        self.center(0, 0, 0, width, height, depth, material, "plinth")
        self.center(0, height, 0, width - 1, .6, depth - 1, "brass", "plinth_trim")

    def tricolor_flag(self, x, y, z, width=18):
        stripe_h = width / 4.5
        for i, material in enumerate(("paint_emerald", "paint_white", "paint_saffron")):
            self.box(x, y + stripe_h * i, z, width, stripe_h, .55, material, "flag_band")
        cx, cy, radius = x + width / 2, y + stripe_h * 1.5, stripe_h * .36
        for face_z in (z - .05, z + .56):
            self.vertical_ring(cx, cy, face_z, radius, .12, .1, "police_navy", steps=24)
            for i in range(24):
                angle = i * 15
                self.center(cx + radius * .48 * math.cos(math.radians(angle)),
                            cy + radius * .48 * math.sin(math.radians(angle)) - .05,
                            face_z, radius * .95, .10, .11, "police_navy", "chakra_spoke", rot=[0, 0, angle])


def independence_recipes():
    # Flag proportions3:2, the twenty-four-spoke wheel and correct colour order
    # are represented in the original mesh rather than a third-party image.
    s = Sculpture(); s.pedestal(12, 12)
    s.center(0, 2.6, 0, 1.2, 37, 1.2, "stainless", "flagpole")
    s.sphere(0, 40.1, 0, 1.2, "brass", levels=5)
    s.tricolor_flag(.8, 25, -.25, 21)
    yield "national_flag_mast", "National Flag Mast", s.pb

    s = Sculpture()
    for x in (-22, 22):
        s.center(x, 0, 0, 6, 2, 6, "sandstone", "anchor")
        s.center(x, 2, 0, 1.1, 25, 1.1, "brass", "post")
    s.center(0, 26.3, 0, 45, .6, .6, "leather_tan", "bunting_rope")
    for i, x in enumerate(range(-19, 20, 6)):
        material = ("paint_saffron", "paint_white", "paint_emerald")[i % 3]
        for level in range(4):
            s.center(x, 21.1 + level * 1.2, -.2, 1.2 + level * .95, 1.2, .45, material, "pennant")
    yield "unity_bunting", "Tricolour Unity Bunting", s.pb

    s = Sculpture(); s.pedestal(18, 18)
    s.disk(0, 2.6, 0, 7.5, 7.5, 2, "copper")
    s.disk(0, 4.6, 0, 6.5, 6.5, .3, "water_teal")
    for i in range(8):
        angle = i * 45
        s.center(4.5 * math.cos(math.radians(angle)), 5.2, 4.5 * math.sin(math.radians(angle)), 3.5, 1.2, 7,
                 "linen_white", "lotus_petal", rot=[0, -angle, 0])
    s.sphere(0, 7.2, 0, 2.3, "marigold", levels=5)
    yield "lotus_civic_basin", "Lotus Civic Basin", s.pb

    s = Sculpture()
    for x in (-20, 20):
        s.center(x, 0, 0, 8, 3, 10, "sandstone", "gateway_foot")
        s.center(x, 3, 0, 4.5, 31, 5, "sandstone", "gateway_pillar")
        s.center(x, 9, 0, 5.2, 2, 5.7, "brass", "pillar_band")
    for i, material in enumerate(("paint_emerald", "paint_white", "paint_saffron")):
        s.center(0, 30 + i * 2, 0, 46, 2, 8, material, "tricolour_lintel")
    for x in (-10, 0, 10):
        s.center(x, 24, 0, .6, 6, .6, "brass", "pendent_chain")
        s.sphere(x, 23.7, 0, 1.4, "marigold", levels=4)
    yield "civic_gateway", "Independence Civic Gateway", s.pb

    s = Sculpture(); s.pedestal(18, 18, 3)
    for y, width, height in ((3.6, 12, 3), (6.6, 8, 16), (22.6, 6, 5), (27.6, 3, 4)):
        s.center(0, y, 0, width, height, width, "sandstone", "commemorative_column")
    s.center(0, 31.6, 0, 5, 1, 5, "brass", "finial")
    s.center(0, 10, -4.1, 5.5, 7, .4, "graphite", "dedication_plaque")
    for y in (11.2, 13.2, 15.2):
        s.center(0, y, -4.4, 4, .4, .25, "brass", "plaque_rules")
    yield "commemorative_pillar", "Civic Commemorative Pillar", s.pb

    s = Sculpture(); s.pedestal(12, 12)
    s.center(0, 3, 0, 9, 2, 9, "brass", "lantern_base")
    for i, material in enumerate(("paint_emerald", "linen_white", "paint_saffron")):
        s.center(0, 5 + i * 4, 0, 8, 4, 8, material, "lantern_panels")
    for x in (-4.2, 4.2):
        for z in (-4.2, 4.2):
            s.center(x, 4.5, z, .7, 13, .7, "brass", "lantern_frame")
    s.center(0, 17.5, 0, 10, 1.2, 10, "brass", "lantern_roof")
    s.vertical_ring(0, 21, 0, 2.3, .5, .6, "brass", steps=12)
    yield "unity_lantern", "Tricolour Unity Lantern", s.pb

    s = Sculpture(); s.pedestal(19, 14)
    s.center(0, 5, 0, 16, 7, 10, "wood_teak", "parade_drum")
    for x in (-8.2, 8.2):
        s.center(x, 4.5, 0, .7, 8, 11, "linen_white", "drum_skin")
    for x in (-6, -2, 2, 6):
        s.center(x, 4.5, 0, .4, 8.5, 10.5, "brass", "tension_band")
    for i, material in enumerate(("paint_saffron", "paint_white", "paint_emerald")):
        s.center(0, 6 + i * 1.5, -5.3, 14, 1.5, .3, material, "ceremonial_ribbon")
    s.center(-4, 13, 0, .6, .6, 12, "wood_oak", "drumstick", rot=[0, 35, 0])
    yield "parade_drum_stand", "Parade Drum Stand", s.pb

    s = Sculpture(); s.pedestal(22, 16, 3)
    s.center(0, 3.6, 0, 12, 16, 9, "wood_sheesham", "podium_body")
    s.center(0, 19.6, 0, 18, 1.2, 12, "sandstone", "lectern_top", rot=[10, 0, 0])
    for i, material in enumerate(("paint_saffron", "paint_white", "paint_emerald")):
        s.center(0, 12 - i * 2, -4.7, 7.5, 2, .4, material, "ribbon")
    s.center(4.5, 21, -1, .4, 6, .4, "steel_dark", "microphone_stem")
    s.center(3.8, 26.5, -1, 2, .7, .7, "graphite", "microphone")
    yield "heritage_podium", "Heritage Ceremony Podium", s.pb

    s = Sculpture(); s.pedestal(15, 15)
    s.center(0, 2.6, 0, .9, 28, .9, "stainless", "mobile_post")
    s.center(0, 29, 0, 27, .7, .7, "brass", "mobile_arm")
    for x, y, material in ((-10, 21, "paint_saffron"), (0, 16, "linen_white"), (10, 22, "paint_emerald")):
        s.center(x, y + 5, 0, .25, 29 - y - 4.5, .25, "linen_white", "kite_string")
        s.center(x, y, 0, 6, 6, .6, material, "kite", rot=[0, 0, 45])
        for dy in (0, 2, 4):
            s.center(x + (.7 if dy % 4 else -.7), y - 3 - dy, 0, 1.2, 1, .5, "brass", "kite_tail")
    yield "kite_mobile", "Tricolour Kite Mobile", s.pb

    s = Sculpture(); s.pedestal(15, 15)
    for i, material in enumerate(("paint_emerald", "linen_white", "paint_saffron")):
        s.disk(0, 3 + i * 8, 0, 4.2 - i * .4, 4.2 - i * .4, 6, material)
        s.disk(0, 9 + i * 8, 0, 4.6 - i * .4, 4.6 - i * .4, 1, "brass")
    s.sphere(0, 28, 0, 2.1, "glowstone_lamp", levels=6)
    yield "community_light_column", "Community Light Column", s.pb


def monsoon_recipes():
    s = Sculpture(); s.pedestal(15, 15)
    s.center(0, 2.6, 0, 1, 28, 1, "brass", "umbrella_pole")
    for i, radius in enumerate((16, 13, 9, 4)):
        s.disk(0, 24 + i * 2, 0, radius, radius, 1.5, "paint_emerald" if i % 2 == 0 else "fabric_emerald")
    for angle in range(0, 360, 45):
        s.center(8 * math.cos(math.radians(angle)), 25.4, 8 * math.sin(math.radians(angle)), .6, .6, 15, "brass", "umbrella_rib", rot=[0, -angle, 0])
    s.center(0, 32, 0, 1.3, 2, 1.3, "brass", "finial")
    yield "shelter_umbrella", "Monsoon Shelter Umbrella", s.pb

    s = Sculpture()
    s.center(0, 30, 0, 14, 1.4, 8, "wood_teak", "eave_bracket")
    s.center(0, 3, 0, .5, 27, .5, "brass", "rain_chain")
    for y in (6, 12, 18, 24):
        s.disk(0, y, 0, 1.3, 1.3, .9, "copper")
        s.disk(0, y + .9, 0, 2.5, 2.5, 1.4, "copper")
        s.disk(0, y + 2.3, 0, 2.8, 2.8, .4, "brass")
        s.disk(0, y + 2.7, 0, 2.1, 2.1, .15, "water_teal")
    s.disk(0, 0, 0, 7, 7, 2, "sandstone")
    s.disk(0, 2, 0, 6, 6, .2, "water_teal")
    yield "courtyard_rain_chain", "Courtyard Rain Chain", s.pb

    s = Sculpture()
    s.center(0, 0, 0, 23, .5, 17, "water_teal", "water_display_base")
    for i, width in enumerate((10, 15, 20)):
        s.center(0, .7 + i * .8, 0, width, .8, 3 + i * 2.3, "linen_white", "folded_hull")
    for z in (-4, 4):
        s.center(0, 3.1, z, 17, .7, 1.5, "paint_white", "boat_gunwale")
    for i in range(7):
        s.center(0, 3.4 + i * .65, 0, 12 - i * 1.5, .65, .65, "linen_white", "paper_peak")
    yield "paper_boat_display", "Paper Boat Display", s.pb

    s = Sculpture(); s.pedestal(23, 19)
    s.center(0, 2.6, 0, 20, 2, 16, "sandstone", "lily_basin")
    s.center(0, 4.6, 0, 18, .3, 14, "water_teal", "water")
    for x, z, r in ((-5, -3, 3.5), (4, 2, 4), (-3, 3, 2.5)):
        s.disk(x, 5, z, r, r, .25, "leaf_green", bands=7)
    for i in range(6):
        angle = i * 60
        s.center(3.2 + 1.7 * math.cos(math.radians(angle)), 5.4, 1.8 + 1.7 * math.sin(math.radians(angle)), 2.2, .9, 3.1,
                 "linen_white", "lily_petal", rot=[0, -angle, 0])
    s.sphere(3.2, 6.8, 1.8, 1.2, "marigold", levels=4)
    yield "water_lily_planter", "Water Lily Rain Planter", s.pb

    s = Sculpture()
    for x in (-13, 13):
        s.center(x, 0, 3, 3, 25, 3, "wood_teak", "stall_post")
    for i in range(4):
        s.center(0, 24.5 + i * 1.5, 3, 31 - i * 5, 1.5, 21 - i * 3, "fabric_emerald", "shelter_roof")
    s.center(0, 9, 0, 25, 1.2, 10, "wood_oak", "chai_counter")
    for x in (-9, 9):
        s.center(x, 0, 0, 2, 9, 2, "wood_teak", "counter_leg")
    for x in (-5, 0, 5):
        s.disk(x, 10.2, 0, 1.1, 1.1, 2.3, "copper", bands=6)
    yield "chai_rain_shelter", "Monsoon Chai Shelter", s.pb

    s = Sculpture(); s.pedestal(20, 18)
    s.center(-5, 2.6, 4, 3, 24, 3, "copper", "rainwater_downpipe")
    s.center(0, 24, 4, 13, 3, 3, "copper", "spout_arm")
    s.center(5, 21, 4, 3, 4, 3, "copper", "spout_lip")
    for y in (8, 13, 18):
        s.center(5, y, 4, .7, 2.2, .7, "glass_clear", "falling_water")
    s.disk(3, 2.6, 2, 7, 6, 2, "sandstone")
    s.disk(3, 4.6, 2, 5.9, 4.9, .2, "water_teal")
    yield "rainwater_spout_basin", "Rainwater Spout and Basin", s.pb

    s = Sculpture(); s.pedestal(12, 12)
    s.center(0, 2.6, 2, .8, 30, .8, "brass", "lantern_support")
    for x, y, r in ((-6, 24, 4), (0, 27, 5.5), (6, 24, 4)):
        s.sphere(x, y, 0, r, "linen_white", levels=6)
    for x, length in ((-5, 5), (0, 8), (5, 6)):
        s.center(x, 20 - length, 0, .25, length, .25, "stainless", "droplet_wire")
        s.sphere(x, 20 - length - 1, 0, 1.3, "glass_clear", levels=5)
    yield "cloud_droplet_lantern", "Cloud and Droplet Lantern", s.pb

    s = Sculpture()
    s.disk(0, 0, 0, 17, 12, .6, "water_teal")
    for x, z, rx, rz in ((-10, -3, 4.2, 3), (-3, 3, 3.8, 3.2), (4, -2, 4.5, 3.3), (11, 4, 3.3, 2.5)):
        s.disk(x, .7, z, rx, rz, 1.2, "granite", bands=6)
        s.disk(x, 1.9, z, rx - .4, rz - .4, .25, "sandstone", bands=6)
    s.center(-11, 1, 8, .5, 6, .5, "leaf_green", "reed")
    s.center(-9, 1, 8, .5, 8, .5, "leaf_green", "reed")
    yield "puddle_stepping_stones", "Monsoon Stepping Stone Display", s.pb

    s = Sculpture(); s.pedestal(15, 12)
    s.center(0, 2.6, 1, .9, 26, .9, "steel_light", "coat_stand")
    s.center(0, 26, 0, 17, .8, .8, "brass", "hanger")
    s.center(0, 6, 0, 10, 18, 5, "taxi_yellow", "raincoat_body")
    s.center(-6.7, 13, 0, 4, 11, 4, "taxi_yellow", "left_sleeve", rot=[0, 0, -18])
    s.center(6.7, 13, 0, 4, 11, 4, "taxi_yellow", "right_sleeve", rot=[0, 0, 18])
    s.center(0, 24, 0, 8, 5, 6, "taxi_yellow", "hood")
    s.center(0, 25, -3.2, 5.5, 3, .5, "graphite", "hood_opening")
    s.center(0, 7, -2.7, .4, 17, .35, "stainless", "zipper")
    for x in (-2.6, 2.6):
        s.center(x, 10, -2.7, 2.8, 3, .4, "paint_saffron", "pocket")
    yield "raincoat_display", "Monsoon Raincoat Display", s.pb

    s = Sculpture(); s.pedestal(17, 13)
    s.center(0, 2.6, 0, 3, 22, 3, "wood_teak", "weather_post")
    s.center(0, 18, 0, 12, 10, 4, "sandstone", "weather_housing")
    s.center(0, 20, -2.3, 8, 6, .5, "screen_pc", "weather_display")
    s.center(0, 28, 0, 16, 1.2, 8, "paint_emerald", "kiosk_roof")
    s.center(0, 29, 0, .6, 7, .6, "stainless", "windsock_pole")
    for i in range(4):
        s.center(2 + i * 2.2, 34 - i * .35, 0, 2.3, 3 - i * .45, 3 - i * .45,
                 "paint_saffron" if i % 2 == 0 else "linen_white", "windsock_segment")
    yield "coastal_weather_kiosk", "Coastal Weather Kiosk", s.pb


def christmas_recipes():
    s = Sculpture(); s.pedestal(20, 20)
    s.center(0, 2.6, 0, 3, 7, 3, "wood_teak", "tree_trunk")
    for start_y, radius, tiers in ((7, 12, 5), (14, 9, 5), (21, 6, 4)):
        for i in range(tiers):
            r = radius * (1 - i / (tiers + 1))
            s.disk(0, start_y + i * 1.4, 0, r, r, 1.4, "leaf_green", bands=8)
    for x, y, z in ((-7, 11, -6), (6, 10, -7), (0, 18, -8), (-4, 22, -4), (4, 21, -4)):
        s.sphere(x, y, z, 1.1, "brass" if y % 2 else "fire_red", levels=4)
    s.center(0, 28, 0, 1.3, 5, 1.3, "brass", "tree_star")
    s.center(0, 29.8, 0, 5, 1.3, 1.3, "brass", "tree_star")
    yield "fir_tree", "Decorated Christmas Fir Tree", s.pb

    s = Sculpture(); s.pedestal(18, 12)
    s.center(0, 2.6, 2, .7, 15, .7, "brass", "wreath_stand")
    s.vertical_ring(0, 16, 0, 9, 3, 3.5, "leaf_green", steps=16)
    for x, y in ((-6, 11), (6, 11), (-6, 21), (6, 21), (0, 25)):
        s.sphere(x, y, -2, 1.0, "fire_red", levels=4)
    for x, angle in ((-2, 30), (2, -30)):
        s.center(x, 6, -2, 5, 3, 1, "crimson_silk", "ribbon_bow", rot=[0, 0, angle])
    s.center(0, 4, -2, 2, 4, 1, "crimson_silk", "ribbon_tail")
    yield "holly_wreath_stand", "Holly Wreath Stand", s.pb

    s = Sculpture()
    s.center(0, 4, 0, 21, 2, 15, "wood_teak", "gift_cart")
    for x in (-8, 8):
        for z in (-6, 6):
            s.center(x, 0, z, 2, 5, 5, "rubber_tire", "cart_wheel")
    for x, y, z, w, h, d, material in ((-5, 6, 0, 9, 7, 11, "paint_red"), (5, 6, 1, 8, 10, 9, "paint_emerald"), (-4, 13, 0, 6, 5, 7, "paint_gold")):
        s.center(x, y, z, w, h, d, material, "wrapped_gift")
        s.center(x, y, z, 1.3, h + .15, d + .2, "linen_white", "gift_ribbon")
        s.center(x, y + h, z, w + .15, .3, 1.3, "linen_white", "gift_cross_ribbon")
    s.center(0, 6, 10, 16, .8, .8, "brass", "cart_handle")
    for x in (-8, 8):
        s.center(x, 4, 9, .8, 3, .8, "brass", "handle_support")
    yield "gift_cart", "Christmas Gift Cart", s.pb

    s = Sculpture(); s.pedestal(23, 13)
    for x, height in ((-7, 11), (0, 18), (7, 14)):
        s.disk(x, 2.6, 0, 3.3, 3.3, 1, "brass")
        s.disk(x, 3.6, 0, 2.3, 2.3, height, "linen_white")
        s.center(x, 3.6 + height, 0, .2, 1, .2, "graphite", "wick")
        for level, width in enumerate((1.6, 2.1, 1.4, .6)):
            s.center(x, 4.2 + height + level * .6, 0, width, .6, width, "glowstone_lamp", "candle_flame")
    yield "candle_trio", "Christmas Candle Trio", s.pb


def new_year_recipes():
    s = Sculpture(); s.pedestal(20, 14)
    s.center(0, 2.6, 2, 3, 15, 3, "brass", "clock_post")
    s.center(0, 12, 0, 18, 18, 3, "graphite", "clock_housing")
    s.center(0, 13, -1.8, 16, 16, .5, "linen_white", "clock_face")
    s.vertical_ring(0, 21, -2.2, 8.1, .8, .6, "brass", steps=24)
    for i in range(12):
        angle = i * 30
        s.center(6.6 * math.sin(math.radians(angle)), 20.4 + 6.6 * math.cos(math.radians(angle)), -2.4,
                 .55, 1.2, .3, "graphite", "clock_hour", rot=[0, 0, -angle])
    s.center(-.6, 20.8, -2.7, .7, 6.2, .4, "police_navy", "minute_hand", rot=[0, 0, 12])
    s.center(-1.1, 20.8, -2.9, .85, 4.5, .4, "brass", "hour_hand", rot=[0, 0, 28])
    yield "countdown_clock", "Midnight Countdown Clock", s.pb

    s = Sculpture(); s.pedestal(16, 16)
    for x, y, z, material in ((-6, 25, 0, "paint_gold"), (5, 29, 1, "paint_emerald"), (0, 20, -5, "paint_silver")):
        s.center(x, 3, z, .25, y - 6, .25, "linen_white", "balloon_string")
        s.sphere(x, y, z, 5.4, material, levels=9)
        s.center(x, y - 6.3, z, 1.2, 1.2, 1.2, material, "balloon_tie")
    yield "balloon_cluster", "New Year Balloon Cluster", s.pb

    s = Sculpture()
    for x in (-19, 19):
        s.center(x, 0, 0, 8, 3, 9, "graphite", "arch_foot")
        s.center(x, 3, 0, 4, 25, 4, "brass", "arch_upright")
    for x, y in ((-17, 27), (-13, 31), (-7, 34), (0, 35), (7, 34), (13, 31), (17, 27)):
        s.center(x, y, 0, 7, 4, 4, "paint_gold", "arch_crown", rot=[0, 0, -x * 1.4])
    for x in (-13, -6, 0, 6, 13):
        s.center(x, 24, 0, .3, 9, .3, "stainless", "light_drop")
        s.sphere(x, 23, 0, 1.3, "glowstone_lamp", levels=4)
    yield "midnight_light_arch", "Midnight Light Arch", s.pb

    s = Sculpture(); s.pedestal(23, 19, 3, "graphite")
    s.center(0, 3.6, 0, 16, 3, 12, "paint_emerald", "celebration_stage")
    s.center(0, 6.6, 0, 17, .8, 13, "brass", "stage_lip")
    for x, height, z in ((-7, 19, -2), (0, 26, 2), (7, 22, -1)):
        s.center(x, 7.4, z, .45, height, .45, "stainless", "streamer_support")
        for i in range(5):
            material = ("paint_gold", "paint_emerald", "paint_silver")[i % 3]
            s.center(x + (1 if i % 2 else -1), 10 + i * (height / 6), z, 3, 1.3, .5, material, "confetti_pendant", rot=[0, 0, 30 if i % 2 else -30])
        s.sphere(x, 7.4 + height, z, 1.6, "brass", levels=4)
    yield "confetti_podium", "New Year Confetti Podium", s.pb


def build_selection(output, additions):
    legacy = json.loads((output / "manifests/festivals_128.json").read_text())["assets"]
    if len(legacy) != 100:
        raise ValueError("Expected all100 preserved legacy festival assets")
    grouped = {}
    for record in legacy:
        theme = {"ganesh": "ganesh_chaturthi", "new": "new_year"}.get(record["theme"], record["theme"])
        grouped.setdefault(theme, []).append(record)
    selected = []
    for theme, target in APPROVED.items():
        candidates = grouped.get(theme, [])
        add = [record for record in additions if record["theme"] == theme]
        take = target - len(add)
        if take < 0 or len(candidates) < take:
            raise ValueError(f"Insufficient artwork for {theme}: {len(candidates)} legacy +{len(add)} additions")
        # The original order retains the12 shared design families; the extra
        # square beacon remains in the compatibility catalogue for four themes.
        for source, records in (("legacy", candidates[:take]), ("addition", add)):
            for record in records:
                selected.append({"id": record["id"], "title": record["title"], "theme": theme,
                                 "source": source, "source_theme": record["theme"],
                                 "geometry_path": record["geometry_path"], "java_model_path": record["java_model_path"],
                                 "icon_path": record["icon_path"], "editable_source": record["editable_source"],
                                 "activation_mode": "manual_staff_only", "runtime_registration": "not_applied"})
    selected_ids = {record["id"] for record in selected}
    result = {"profile": core.PROFILE, "schema_version": 1, "count": len(selected), "theme_counts": dict(Counter(record["theme"] for record in selected)),
              "legacy_reuse_count": sum(record["source"] == "legacy" for record in selected), "addition_count": len(additions),
              "selections": selected, "retained_legacy_ids": [record["id"] for record in legacy],
              "unselected_legacy_ids": [record["id"] for record in legacy if record["id"] not in selected_ids],
              "binding_status": "art_selection_proposal_only", "activation_mode": "manual_staff_only",
              "world_placement": "not_applied", "runtime_registration": "not_applied",
              "note": "Exactly100 approved-theme selections reuse72 legacy designs and add28 substantive designs. All100 legacy IDs remain available. Eid, Sankranti and four spare square beacons remain preserved; no prior asset, entitlement or activation configuration is replaced."}
    if result["theme_counts"] != APPROVED or len(selected_ids) != 100:
        raise ValueError("Approved festival allocation mismatch")
    core.save_json(output / "manifests/approved_festival_selection_128.json", result)
    core.contact_sheet([(record["title"], output / record["icon_path"]) for record in selected], output / "previews/approved_festival_selection_128.png", cols=10, title="APPROVED FESTIVAL ART / 100 SELECTED DESIGNS")
    return result


def build(output=DEFAULT_OUTPUT):
    output = Path(output).resolve()
    core.configure(output)
    entries = []
    for theme, generator in (("independence_day", independence_recipes), ("monsoon", monsoon_recipes), ("christmas", christmas_recipes), ("new_year", new_year_recipes)):
        for suffix, title, pb in generator():
            asset_id = f"gtm:{theme}_{suffix}"
            record = core.export_model(pb, asset_id, title, "festival_additions", output, metadata={
                "theme": theme, "proposed_id": True, "source_family": "approved_festival_addition",
                "activation_mode": "manual_staff_only", "runtime_registration": "not_applied", "world_placement": "not_applied",
                "preview_yaw_deg": 142, "preview_pitch_deg": 24, "source_recipe": "tools/gtm128_festival_additions.py"})
            entries.append(record)
        print(f"Generated {sum(record['theme'] == theme for record in entries)} {theme} additions", flush=True)
    if dict(Counter(record["theme"] for record in entries)) != ADDITIONS:
        raise ValueError("New festival allocation mismatch")
    manifest = {"profile": core.PROFILE, "count": len(entries), "theme_counts": ADDITIONS, "assets": entries,
                "runtime_registration": "not_applied", "note": "Additive proposed artwork; all100 original festival IDs are preserved."}
    core.save_json(output / "manifests/festival_additions_128.json", manifest)
    core.contact_sheet([(record["title"], output / record["icon_path"]) for record in entries], output / "previews/festival_additions_128.png", cols=7, title="FESTIVAL ADDITIONS / 28 ORIGINAL NATIVE128 DESIGNS")
    selection = build_selection(output, entries)
    errors = []
    fingerprints = set()
    for record in entries:
        image = Image.open(output / record["icon_path"])
        if image.size != (128, 128) or image.mode != "RGBA" or image.getchannel("A").getextrema() != (0, 255):
            errors.append(record["id"] + ": invalid icon")
        java = json.loads((output / record["java_model_path"]).read_text())
        geo = json.loads((output / record["geometry_path"]).read_text())["minecraft:geometry"][0]
        cubes = [cube for bone in geo["bones"] for cube in bone.get("cubes", [])]
        if len(cubes) != len(java["elements"]) or not cubes:
            errors.append(record["id"] + ": invalid mesh parity")
        dimensions = {"size": [cube["size"] for cube in cubes], "origins": [cube["origin"] for cube in cubes], "rotations": [cube.get("rotation") for cube in cubes]}
        fingerprints.add(hashlib.sha256(json.dumps(dimensions, sort_keys=True).encode()).hexdigest())
        for cube in cubes:
            if min(cube["size"]) <= 0:
                errors.append(record["id"] + ": nonpositive cube")
            for face in cube["uv"].values():
                u, v = face["uv"]; w, h = face["uv_size"]
                if min(u, v) < 0 or u + w > geo["description"]["texture_width"] or v + h > geo["description"]["texture_height"]:
                    errors.append(record["id"] + ": UV bounds")
    if len(fingerprints) != 28:
        errors.append("New designs share geometry fingerprints")
    report = {"profile": core.PROFILE, "passed": not errors, "errors": errors, "new_model_pairs": 28, "unique_geometry_fingerprints": len(fingerprints),
              "native128_icons": 28, "approved_selection_count": selection["count"], "approved_theme_counts": selection["theme_counts"],
              "legacy_ids_preserved": 100, "legacy_reused_in_selection": selection["legacy_reuse_count"],
              "world_placement": "not_applied", "runtime_registration": "not_applied", "client_verification": "not_run"}
    core.save_json(output / "reports/festival_additions_checks.json", report)
    if errors:
        raise ValueError("; ".join(errors))
    print(json.dumps(report, indent=2), flush=True)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.output)
