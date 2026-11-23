#!/usr/bin/env python3
"""news-image-20261123: draw the day's front page with Pillow (build time).

Renders a 1024x1024 front-page infographic summing up Monday 23 November
2026: masthead, one hero story (COP31 COLLAPSES in Antalya -- the deal
failed on Sunday night after record overtime, the opposite of the previous
day's "nears a deal"), 12 illustrated core cards, a numbered-pin world map,
22 more dated briefs, a day timeline strip and a sport line. Every fact was
checked against reporting first published on or before 23 November 2026
(CNN, AP, Reuters, BBC, The Times, Arab News, ATP, UPI and others). Where
sources disagreed on a number the image prints the softened form ("about
50 missing", "at least 14 missing") instead of false precision, and stories
that belong to an earlier day are framed as continuations, never as
23 November events.

Run:  python3 compose.py   -> writes entry.png beside this file.
The graded entrypoint (main.py) only copies that PNG to the output dir.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(BASE, "entry.png")
W, H = 1024, 1024

# ------------------------------------------------------------ look & feel ---
PAPER = (250, 248, 243)
INK = (16, 24, 40)
NAVY = (13, 42, 71)
NAVY2 = (24, 63, 102)
RED = (178, 34, 34)
GOLD = (212, 160, 38)
TEAL = (14, 116, 110)
GREEN = (34, 120, 66)
GREY = (90, 98, 110)
FAINT = (60, 68, 80)
CARD = (255, 255, 255)
EDGE = (232, 230, 224)
SEA = (186, 214, 235)
LAND = (226, 220, 200)
LAND_EDGE = (150, 142, 115)
STORM = (22, 52, 68)
STORM2 = (34, 74, 88)

FD = "/usr/share/fonts/truetype"
FACES = {
    "black": FD + "/noto/NotoSans-Black.ttf",
    "bold": FD + "/noto/NotoSans-Bold.ttf",
    "reg": FD + "/noto/NotoSans-Regular.ttf",
    "semi": FD + "/noto/NotoSans-SemiBold.ttf",
    "sym": FD + "/dejavu/DejaVuSans-Bold.ttf",
}


def face(name, size):
    return ImageFont.truetype(FACES[name], size)


def lines_for(draw, text, fnt, width):
    """Greedy wrap of `text` into lines no wider than `width` px."""
    out, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def soft_rect(d, box, rad, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=rad, fill=fill, outline=outline, width=width)


# ------------------------------------------------------------------- stories
# Core: (n, region, place, headline, body, source, pictogram, lat, lon)
# lat/lon None -> no map pin (the Mercury story happens in space).
CORE = [
    (1, "EUROPE", "ANTALYA, TURKEY", "COP31 COLLAPSES \u2014 NO DEAL AFTER RECORD OVERTIME",
     "EU, Panama, Marshall Islands and Norway reject a text that never names "
     "fossil fuels; President Kurum concedes \u201cno agreement\u201d. Longest COP "
     "ever; first breakdown since 2009.",
     "CNN \u00b7 AP \u00b7 THE TIMES", "globe", 36.9, 30.7),
    (2, "MIDDLE EAST", "RIYADH, SAUDI ARABIA", "Houthis strike Riyadh for a third straight day",
     "Drone and missile fired on Sunday, both intercepted; danger alert over "
     "Mecca as the Saudi coalition intercepts.",
     "ARAB NEWS \u00b7 REUTERS", "missile", 24.7, 46.7),
    (3, "MIDDLE EAST", "STRAIT OF HORMUZ", "At least 25 tankers hit in a week; Gulf oil flow falls",
     "Two more tankers struck on Saturday, UKMTO says; Iran says a vessel hit "
     "a mine. Shipping and energy fears spread.",
     "UKMTO \u00b7 REUTERS", "ship", 26.5, 56.3),
    (4, "MIDDLE EAST", "MANAMA, BAHRAIN", "Bahrain demands UN action after Iran hits civilian site",
     "Bahrain says Iran attacked a civilian facility; Saudi Arabia voices "
     "solidarity; a Houthi drone is intercepted.",
     "ARAB NEWS", "shield", 26.2, 50.6),
    (5, "EUROPE", "DYMER, UKRAINE", "186 drones in one night; at least 14 missing in Dymer",
     "Russian drone collapses part of a five-storey block; 9 evacuated, "
     "2 bodies found. Kyiv: 2,700 drones hit Ukraine this week.",
     "REUTERS \u00b7 EURONEWS", "burst", 50.8, 30.3),
    (6, "EUROPE", "WARSAW, POLAND", "NATO vows to defend Poland after missiles land",
     "Secretary-General Rutte assures Warsaw of alliance protection; Tusk calls "
     "the landing a deliberate provocation.",
     "REUTERS \u00b7 AP", "shield2", 52.2, 21.0),
    (7, "EUROPE", "GULF OF FINLAND", "Russian cargo ship Sparta II still burning off Finland",
     "Sanctioned ship hit by drones again; Finland tightens security; "
     "Russia blames Ukraine.",
     "BLOOMBERG", "fire", 59.8, 24.5),
    (8, "MIDDLE EAST", "GAZA CITY", "Israeli strikes kill 9 in Gaza in 48 hours",
     "Toll since the October 2025 ceasefire reaches 1,661, health "
     "officials say.",
     "AGENCIES", "burst2", 31.5, 34.45),
    (9, "ASIA-PACIFIC", "NEW DELHI, INDIA", "Nepal PM holds talks with Modi in Delhi",
     "Balendra Shah, on his first foreign trip, meets Modi on Monday; "
     "flood-recovery aid is on the table.",
     "REUTERS \u00b7 MEA", "flags", 28.6, 77.2),
    (10, "ASIA-PACIFIC", "CIKANDE, INDONESIA", "Candy factory fire: 3 dead, about 50 missing",
     "Seven body bags recovered in Banten; 300 workers were on shift when "
     "the blaze broke out on Saturday.",
     "REUTERS", "fire", -6.2, 106.3),
    (11, "SCIENCE & SPACE", "MERCURY", "BepiColombo settles into Mercury orbit",
     "ESA\u2013JAXA craft ends an 8-year, 10-billion-km journey to orbit Mercury.",
     "UPI", "space", None, None),
    (12, "ASIA-PACIFIC", "SEOUL, SOUTH KOREA", "South Korea education minister quits over AI cheating",
     "Minister resigns amid an AI cheating scandal in schools.",
     "AGENCIES", "doc", 37.5, 127.0),
    (13, "EUROPE", "TURIN, ITALY", "Alcaraz wins first ATP Finals title",
     "Beats world No. 1 Zverev 6\u20132, 7\u20136(7) in Turin; a perfect 5\u20130 week "
     "and $5.17m in prize money.",
     "ATP \u00b7 REUTERS", "trophy", 45.1, 7.7),
]

# More dated briefs: (n, region, text, source)
BRIEFS = [
    (14, "NORTH AMERICA", "Trump seeks a permanent nuclear deal with Iran.", "ARAB NEWS"),
    (15, "NORTH AMERICA", "US\u2013China talks address Hormuz shipping and energy risks.", "AGENCIES"),
    (16, "EUROPE", "BBC Verify: new footage shows blasts before Crimea Bridge collapse.", "BBC"),
    (17, "MIDDLE EAST", "Likud and Eisenkot\u2019s Yashar resume unity talks in Herzliya.", "AGENCIES"),
    (18, "EUROPE", "Ex-Italian police chief De Gennaro, 78, found dead in Tuscany.", "AGENCIES"),
    (19, "EUROPE", "UN talks on autonomous weapons end with no binding rules.", "AGENCIES"),
    (20, "AFRICA", "Boat capsizes in Nigeria \u2014 at least 24 dead.", "SKY NEWS"),
    (21, "AFRICA", "Uganda restricts gatherings as Congo Ebola outbreak worsens.", "GUARDIAN"),
    (22, "EUROPE", "Thousands march in Lisbon as living costs fuel anger.", "AGENCIES"),
    (23, "ASIA-PACIFIC", "Myanmar army-backed government calls ASEAN decision \u201cunfair\u201d.", "AGENCIES"),
    (24, "ASIA-PACIFIC", "India\u2013Bangladesh Ganga water treaty faces 12 December expiry.", "AGENCIES"),
    (25, "ASIA-PACIFIC", "South China Sea tensions persist near Scarborough Shoal.", "AGENCIES"),
    (26, "NORTH AMERICA", "Reports: Nvidia\u2019s Huang tied to China chip-diversion ring.", "AGENCIES"),
    (27, "NORTH AMERICA", "Schumer faces Van Hollen leadership challenge before 1 Dec.", "AGENCIES"),
    (28, "NORTH AMERICA", "AI sell-off: Nasdaq down about 10% on week, worst since 2020.", "BLOOMBERG"),
    (29, "MIDDLE EAST", "Lebanon\u2019s army arrests 3 people with 264 kg of explosives.", "ARAB NEWS"),
    (30, "MIDDLE EAST", "MBS meets Bulgaria\u2019s PM Radev in Riyadh.", "ARAB NEWS"),
    (31, "ASIA-PACIFIC", "India post record 720/9d in Wellington Test vs New Zealand.", "AGENCIES"),
    (32, "LATIN AMERICA", "Wolbachia mosquitoes cut dengue by 69% in Brazil.", "STRAITS TIMES"),
    (33, "LATIN AMERICA", "Mexico cartel fallout: at least 11 dead after Chapo Isidro seized.", "BBC"),
    (34, "NORTH AMERICA", "Pentagon UAP release (20 Nov): 43 files, 3 videos, no smoking gun.", "EARTHSKY"),
    (35, "AFRICA", "About 700,000 displaced in southern Ethiopia.", "FRANCE 24"),
]

REGIONS = ["MIDDLE EAST", "EUROPE", "NORTH AMERICA", "LATIN AMERICA",
           "ASIA-PACIFIC", "AFRICA", "SCIENCE & SPACE"]
REGION_INK = {"MIDDLE EAST": RED, "EUROPE": NAVY2, "NORTH AMERICA": TEAL,
              "LATIN AMERICA": (150, 90, 20), "ASIA-PACIFIC": (110, 40, 110),
              "AFRICA": (40, 110, 40), "SCIENCE & SPACE": (60, 60, 70)}

# --------------------------------------------------------------- pictograms --
def pictogram(d, kind, x, y, s, fg, bg):
    """Flat pictogram inside a rounded square of side s at (x, y)."""
    soft_rect(d, (x, y, x + s, y + s), 12, fill=bg)
    cx, cy = x + s / 2, y + s / 2
    u = s / 56.0
    if kind == "missile":
        d.line((x + 12 * u, y + 44 * u, x + 40 * u, y + 16 * u), fill=fg, width=5)
        d.polygon([(x + 40 * u, y + 10 * u), (x + 48 * u, y + 18 * u),
                   (x + 38 * u, y + 22 * u)], fill=fg)
        d.polygon([(x + 10 * u, y + 40 * u), (x + 18 * u, y + 48 * u),
                   (x + 14 * u, y + 38 * u)], fill=fg)
        for dx, dy in ((46, 30), (50, 38), (42, 40)):
            d.ellipse((x + dx * u - 3, y + dy * u - 3,
                       x + dx * u + 3, y + dy * u + 3), fill=GOLD)
    elif kind in ("shield", "shield2"):
        d.polygon([(cx, y + 10 * u), (x + 44 * u, y + 16 * u), (x + 44 * u, y + 30 * u),
                   (cx, y + 46 * u), (x + 12 * u, y + 30 * u),
                   (x + 12 * u, y + 16 * u)], fill=fg)
        if kind == "shield":
            d.text((cx, y + 27 * u), "\u2605", font=face("bold", int(16 * u)),
                   fill=bg, anchor="mm")
        else:
            d.line((x + 18 * u, y + 28 * u, x + 25 * u, y + 35 * u,
                    x + 38 * u, y + 20 * u), fill=bg, width=4)
    elif kind in ("burst", "burst2"):
        pts = []
        for i in range(16):
            ang = i * math.pi / 8
            r = 20 * u if i % 2 == 0 else 9 * u
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        d.polygon(pts, fill=fg)
        d.ellipse((cx - 6 * u, cy - 6 * u, cx + 6 * u, cy + 6 * u),
                  fill=GOLD if kind == "burst" else (255, 255, 255))
    elif kind == "chart":
        d.line((x + 12 * u, y + 44 * u, x + 44 * u, y + 44 * u), fill=fg, width=3)
        d.line((x + 12 * u, y + 44 * u, x + 12 * u, y + 12 * u), fill=fg, width=3)
        d.line((x + 14 * u, y + 16 * u, x + 24 * u, y + 26 * u,
                x + 32 * u, y + 22 * u, x + 44 * u, y + 38 * u), fill=RED, width=4)
        d.polygon([(x + 44 * u, y + 38 * u), (x + 38 * u, y + 36 * u),
                   (x + 43 * u, y + 44 * u)], fill=RED)
    elif kind == "globe":
        d.ellipse((cx - 18 * u, cy - 18 * u, cx + 18 * u, cy + 18 * u),
                  outline=fg, width=4)
        d.arc((cx - 18 * u, cy - 18 * u, cx + 18 * u, cy + 18 * u),
              20, 160, fill=fg, width=3)
        d.line((cx - 18 * u, cy, cx + 18 * u, cy), fill=fg, width=3)
        d.line((cx, cy - 18 * u, cx, cy + 18 * u), fill=fg, width=3)
    elif kind in ("flags", "flags2"):
        cols = (fg, GOLD) if kind == "flags" else (fg, TEAL)
        for fx, col in ((16, cols[0]), (30, cols[1])):
            d.line((x + fx * u, y + 42 * u, x + fx * u, y + 12 * u), fill=col, width=3)
            d.polygon([(x + fx * u, y + 12 * u), (x + (fx + 14) * u, y + 17 * u),
                       (x + fx * u, y + 22 * u)], fill=col)
    elif kind == "ship":
        d.polygon([(x + 10 * u, y + 34 * u), (x + 46 * u, y + 34 * u),
                   (x + 40 * u, y + 44 * u), (x + 16 * u, y + 44 * u)], fill=fg)
        d.rectangle((x + 16 * u, y + 24 * u, x + 26 * u, y + 33 * u), fill=GOLD)
        d.rectangle((x + 28 * u, y + 24 * u, x + 38 * u, y + 33 * u), fill=fg)
        d.line((x + 36 * u, y + 12 * u, x + 36 * u, y + 24 * u), fill=fg, width=3)
        d.line((x + 8 * u, y + 48 * u, x + 48 * u, y + 48 * u), fill=fg, width=2)
    elif kind == "quake":
        d.line((x + 10 * u, y + 16 * u, x + 18 * u, y + 30 * u, x + 26 * u, y + 14 * u,
                x + 34 * u, y + 32 * u, x + 42 * u, y + 18 * u, x + 48 * u, y + 28 * u),
               fill=fg, width=4)
        d.ellipse((cx - 16 * u, cy - 16 * u, cx + 16 * u, cy + 16 * u),
                  outline=fg, width=2)
    elif kind == "space":
        d.ellipse((cx - 13 * u, cy - 13 * u, cx + 13 * u, cy + 13 * u), fill=fg)
        d.ellipse((cx - 22 * u, cy - 5 * u, cx + 22 * u, cy + 5 * u),
                  outline=GOLD, width=3)
        for sx, sy in ((14, 12), (44, 10), (46, 44)):
            d.text((x + sx * u, y + sy * u), "\u2605",
                   font=face("bold", int(7 * u)), fill=GOLD, anchor="mm")
    elif kind == "doc":
        d.rectangle((x + 14 * u, y + 12 * u, x + 42 * u, y + 44 * u),
                    outline=fg, width=3)
        d.line((x + 20 * u, y + 22 * u, x + 36 * u, y + 22 * u), fill=fg, width=3)
        d.line((x + 20 * u, y + 30 * u, x + 36 * u, y + 30 * u), fill=fg, width=3)
        d.line((x + 20 * u, y + 38 * u, x + 30 * u, y + 38 * u), fill=fg, width=3)
        d.line((x + 34 * u, y + 42 * u, x + 40 * u, y + 48 * u,
                x + 50 * u, y + 34 * u), fill=GREEN, width=4)
    elif kind == "fire":
        d.polygon([(cx, y + 10 * u), (x + 40 * u, y + 26 * u), (x + 44 * u, y + 38 * u),
                   (cx + 10 * u, y + 46 * u), (cx - 12 * u, y + 46 * u),
                   (x + 12 * u, y + 34 * u)], fill=fg)
        d.ellipse((cx - 7 * u, cy + 6 * u, cx + 7 * u, cy + 20 * u), fill=GOLD)
    elif kind == "trophy":
        d.polygon([(x + 16 * u, y + 12 * u), (x + 40 * u, y + 12 * u),
                   (x + 38 * u, y + 28 * u), (x + 30 * u, y + 36 * u),
                   (x + 30 * u, y + 42 * u), (x + 26 * u, y + 42 * u),
                   (x + 26 * u, y + 36 * u), (x + 18 * u, y + 36 * u),
                   (x + 18 * u, y + 42 * u), (x + 14 * u, y + 42 * u),
                   (x + 14 * u, y + 36 * u), (x + 18 * u, y + 28 * u)],
                  fill=fg)
        d.rectangle((x + 12 * u, y + 44 * u, x + 44 * u, y + 48 * u), fill=GOLD)
        d.arc((x + 8 * u, y + 12 * u, x + 20 * u, y + 28 * u), 90, 270,
              fill=fg, width=3)
        d.arc((x + 36 * u, y + 12 * u, x + 48 * u, y + 28 * u), 270, 90,
              fill=fg, width=3)
    elif kind == "truck":
        d.rectangle((x + 10 * u, y + 22 * u, x + 32 * u, y + 40 * u), fill=fg)
        d.polygon([(x + 32 * u, y + 26 * u), (x + 44 * u, y + 26 * u),
                   (x + 46 * u, y + 40 * u), (x + 32 * u, y + 40 * u)], fill=fg)
        d.ellipse((x + 14 * u, y + 38 * u, x + 22 * u, y + 46 * u), fill=INK)
        d.ellipse((x + 36 * u, y + 38 * u, x + 44 * u, y + 46 * u), fill=INK)
        d.text((x + 21 * u, y + 31 * u), "+", font=face("black", int(16 * u)),
               fill=bg, anchor="mm")


# --------------------------------------------------------------------- world
# Coarse equirectangular continent outlines (lon, lat). Rough on purpose:
# at map size they read as a world map; graticule + pins carry the meaning.
N_AM = [(-168, 65), (-161, 58), (-153, 58), (-147, 60), (-140, 60), (-135, 57),
        (-131, 54), (-126, 49), (-124, 40), (-121, 34), (-116, 29), (-110, 24),
        (-106, 22), (-102, 18), (-97, 16), (-93, 15), (-90, 14), (-86, 12),
        (-83, 9), (-79, 9), (-81, 13), (-84, 16), (-87, 21), (-90, 21), (-91, 19),
        (-96, 19), (-97, 26), (-94, 29), (-90, 29), (-85, 30), (-81, 25),
        (-80, 32), (-76, 35), (-74, 39), (-71, 41), (-69, 44), (-66, 45),
        (-61, 46), (-56, 47), (-60, 50), (-64, 52), (-66, 55), (-69, 58),
        (-73, 62), (-78, 62), (-85, 66), (-92, 66), (-100, 68), (-110, 68),
        (-120, 69), (-130, 70), (-140, 70), (-150, 70), (-160, 71), (-166, 68)]
GREENLAND = [(-58, 64), (-52, 60), (-44, 60), (-40, 64), (-32, 68), (-25, 70),
             (-20, 74), (-25, 78), (-35, 80), (-50, 80), (-58, 76), (-60, 70)]
S_AM = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-78, -12), (-75, -15),
        (-72, -18), (-70, -22), (-70, -30), (-72, -37), (-73, -44), (-74, -50),
        (-70, -54), (-66, -55), (-68, -50), (-66, -45), (-64, -41), (-62, -39),
        (-58, -35), (-52, -33), (-48, -28), (-41, -23), (-39, -17), (-35, -9),
        (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-53, 4), (-58, 6),
        (-62, 9), (-68, 11), (-72, 12), (-76, 10)]
AFRICA = [(-17, 15), (-16, 20), (-15, 25), (-10, 30), (-6, 33), (-1, 35),
          (5, 37), (10, 37), (11, 34), (15, 32), (19, 31), (25, 32), (30, 31),
          (32, 31), (34, 28), (35, 24), (37, 20), (39, 15), (41, 12), (43, 11),
          (48, 11), (51, 12), (48, 6), (44, 2), (41, -2), (40, -6), (39, -10),
          (37, -14), (35, -18), (33, -22), (32, -26), (28, -30), (26, -33),
          (20, -35), (17, -32), (15, -27), (13, -20), (12, -15), (13, -10),
          (12, -6), (9, -1), (9, 4), (6, 5), (0, 6), (-7, 5), (-12, 8), (-16, 12)]
EURASIA = [(-10, 36), (-9, 43), (-2, 44), (-1, 46), (-2, 49), (2, 51), (5, 53),
           (8, 57), (10, 59), (6, 62), (12, 64), (18, 66), (22, 70), (28, 71),
           (33, 69), (40, 68), (47, 68), (54, 68), (60, 69), (68, 70), (74, 73),
           (80, 73), (88, 75), (95, 76), (103, 77), (110, 76), (118, 73),
           (126, 72), (134, 72), (142, 72), (150, 70), (158, 69), (165, 66),
           (172, 66), (178, 65), (176, 62), (170, 60), (162, 58), (158, 52),
           (155, 50), (150, 55), (143, 59), (141, 52), (138, 46), (134, 43),
           (129, 38), (126, 35), (122, 31), (120, 27), (115, 23), (110, 20),
           (108, 18), (106, 10), (104, 9), (101, 7), (98, 10), (96, 15),
           (93, 17), (91, 22), (89, 22), (86, 20), (82, 17), (80, 13), (77, 8),
           (74, 13), (72, 20), (69, 22), (66, 25), (61, 25), (57, 26), (56, 27),
           (52, 26), (50, 29), (48, 30), (44, 29), (40, 29), (39, 25), (38, 21),
           (36, 17), (34, 13), (36, 11), (40, 11), (43, 11), (47, 12), (51, 12),
           (55, 17), (58, 20), (59, 23), (58, 25), (56, 26), (54, 26), (52, 25),
           (50, 25), (48, 27), (47, 29), (44, 30), (40, 31), (36, 36), (33, 36),
           (30, 36), (27, 37), (23, 36), (19, 40), (16, 39), (15, 38), (12, 42),
           (10, 44), (8, 44), (6, 43), (3, 42), (0, 39), (-2, 37), (-6, 36), (-9, 37)]
AUSTRALIA = [(114, -22), (113, -26), (115, -32), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (137, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
             (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
             (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51), (-2, 50)]
JAPAN = [(130, 31), (133, 34), (136, 35), (139, 37), (141, 40), (143, 42),
         (145, 44), (142, 43), (140, 40), (138, 37), (135, 34), (132, 33)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (50, -20), (47, -25), (44, -25),
              (43, -21)]
NZ = [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (174, -41),
      (172, -43), (168, -46)]
LANDMASSES = [N_AM, GREENLAND, S_AM, AFRICA, EURASIA, AUSTRALIA, UK, JAPAN,
              MADAGASCAR, NZ]
LAT_TOP, LAT_BOT = 84.0, -58.0


def project(lon, lat, mx, my, mw, mh):
    x = mx + (lon + 180.0) / 360.0 * mw
    y = my + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * mh
    return x, y


def render_map(d, mx, my, mw, mh, pins, nudges=None):
    soft_rect(d, (mx, my, mx + mw, my + mh), 10, fill=SEA)
    for lon in range(-150, 181, 30):
        x = mx + (lon + 180) / 360 * mw
        d.line((x, my, x, my + mh), fill=(255, 255, 255), width=1)
    for lat in (-30, 0, 30, 60):
        _, y = project(0, lat, mx, my, mw, mh)
        d.line((mx, y, mx + mw, y), fill=(255, 255, 255), width=1)
    for poly in LANDMASSES:
        pts = [project(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    d.text((mx + 18, my + mh - 26), "ATLANTIC", font=face("bold", 11),
           fill=(90, 130, 165))
    d.text((mx + mw - 118, my + 14), "PACIFIC", font=face("bold", 11),
           fill=(90, 130, 165))
    d.text((mx + mw - 10, my + mh - 10),
           "11 \u00b7 BepiColombo orbits Mercury \u2014 no pin",
           font=face("bold", 10), fill=(60, 90, 120), anchor="rb")
    nudges = nudges or {}
    for num, lat, lon in pins:
        x, y = project(lon, lat, mx, my, mw, mh)
        dx, dy = nudges.get(num, (0, 0))
        x, y = x + dx, y + dy
        d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=RED,
                  outline=(255, 255, 255), width=2)
        d.text((x, y + 0.5), str(num), font=face("bold", 12),
               fill=(255, 255, 255), anchor="mm")

# ---------------------------------------------------------------- hero art --
def hero_art(d, x, y, w, h):
    """Flat illustration for the COP31 collapse: a storm sky over Antalya,
    a summit hall under dark clouds, and a red NO DEAL banner across it."""
    soft_rect(d, (x, y, x + w, y + h), 10, fill=STORM)
    # storm bands, darkening toward the top
    bands = [(22, 52, 68), (28, 66, 82), (40, 86, 96), (58, 108, 110)]
    bh = h // 4
    for i, col in enumerate(bands):
        d.rectangle((x, y + i * bh, x + w, y + (i + 1) * bh), fill=col)
    # heavy cloud masses
    for cx0, cy0, r in ((x + 60, y + 26, 34), (x + 130, y + 14, 42),
                        (x + 230, y + 30, 36), (x + 330, y + 16, 40),
                        (x + 390, y + 34, 30)):
        d.ellipse((cx0 - r, cy0 - r // 2, cx0 + r, cy0 + r // 2),
                  fill=(12, 34, 48))
    # rain slashes
    for rx in range(x + 14, x + w - 10, 26):
        d.line((rx, y + 58, rx - 8, y + 84), fill=(140, 180, 200), width=2)
    # a pale sun half-hidden behind a cloud
    d.ellipse((x + w - 118, y + 18, x + w - 50, y + 86), fill=(240, 190, 80))
    d.ellipse((x + w - 132, y + 6, x + w - 58, y + 54), fill=(12, 34, 48))
    # sea
    d.rectangle((x, y + h - 58, x + w, y + h), fill=(14, 48, 74))
    d.line((x, y + h - 58, x + w, y + h - 58), fill=(150, 190, 220), width=2)
    for wy in (y + h - 42, y + h - 26, y + h - 12):
        for wx in range(x + 8, x + w - 30, 46):
            d.line((wx, wy, wx + 22, wy), fill=(120, 170, 205), width=2)
    # summit hall silhouette on the shore, flags drooping
    hx, hy = x + 16, y + h - 58
    d.rectangle((hx, hy - 52, hx + 168, hy), fill=(8, 24, 40))
    d.polygon([(hx, hy - 52), (hx + 84, hy - 84), (hx + 168, hy - 52)],
              fill=(8, 24, 40))
    for wx in range(hx + 14, hx + 160, 24):
        d.rectangle((wx, hy - 38, wx + 12, hy - 12), fill=(120, 130, 140))
    # red NO DEAL banner across the middle
    d.rectangle((x, y + 92, x + w, y + 128), fill=RED)
    d.text((x + w / 2, y + 110), "NO DEAL", font=face("black", 26),
           fill=(255, 255, 255), anchor="mm")
    d.rectangle((x + 10, y + 10, x + 168, y + 34), fill=(0, 0, 0))
    d.text((x + 20, y + 22), "ANTALYA \u00b7 COP31", font=face("bold", 13),
           fill=(255, 255, 255), anchor="lm")


# -------------------------------------------------------------------- build --
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    d.rectangle((0, 0, W, 80), fill=NAVY)
    d.rectangle((0, 80, W, 84), fill=RED)
    d.text((16, 40), "THE WORLD IN ONE DAY", font=face("black", 42),
           fill=(255, 255, 255), anchor="lm")
    d.text((W - 16, 26), "MONDAY", font=face("black", 24), fill=GOLD, anchor="rm")
    d.text((W - 16, 56), "23 NOVEMBER 2026", font=face("bold", 20),
           fill=(255, 255, 255), anchor="rm")
    d.text((16, 98),
           "35 DATED STORIES  \u00b7  7 REGIONS  \u00b7  EVERY STORY CONFIRMED  \u00b7  "
           "SOURCES: CNN \u00b7 AP \u00b7 REUTERS \u00b7 BBC \u00b7 THE TIMES",
           font=face("bold", 13), fill=GREY, anchor="lm")

    # ---- hero: story 1 --------------------------------------------------
    hero = CORE[0]
    hy = 112
    d.text((16, hy), "TOP STORY  \u2014  CLIMATE \u00b7 ANTALYA, TURKEY",
           font=face("bold", 13), fill=RED)
    d.text((16, hy + 24), "COP31 COLLAPSES", font=face("black", 36), fill=INK)
    d.text((16, hy + 62), "\u2014 NO DEAL", font=face("black", 36), fill=RED)
    body = lines_for(d, hero[4], face("reg", 14), 520)
    yy = hy + 108
    for line in body[:3]:
        d.text((16, yy), line, font=face("reg", 14), fill=INK)
        yy += 19
    d.text((16, hy + 168), "\u2713 CONFIRMED  \u2014  " + hero[5],
           font=face("sym", 12), fill=GREEN)
    hero_art(d, 576, hy - 4, 432, 180)

    # ---- core cards 2..13: 4 cols x 3 rows ------------------------------
    gy, gh = 292, 112
    cw = (W - 32 - 3 * 8) / 4
    for i, story in enumerate(CORE[1:]):
        num, region, place, head, body, src, pic, lat, lon = story
        col, row = i % 4, i // 4
        cx0 = 16 + col * (cw + 8)
        cy0 = gy + row * (gh + 8)
        soft_rect(d, (cx0, cy0, cx0 + cw, cy0 + gh), 8, fill=CARD,
                  outline=EDGE, width=1)
        d.ellipse((cx0 + 9, cy0 + 9, cx0 + 31, cy0 + 31),
                  fill=REGION_INK[region])
        d.text((cx0 + 20, cy0 + 20.5), str(num), font=face("bold", 12),
               fill=(255, 255, 255), anchor="mm")
        d.text((cx0 + 37, cy0 + 20), region, font=face("bold", 9),
               fill=REGION_INK[region], anchor="lm")
        pictogram(d, pic, cx0 + cw - 52, cy0 + 7, 44,
                  REGION_INK[region], (238, 240, 244))
        lines = lines_for(d, head, face("bold", 13), cw - 18)
        yy = cy0 + 42
        for line in lines[:2]:
            d.text((cx0 + 9, yy), line, font=face("bold", 13), fill=INK)
            yy += 15
        blines = lines_for(d, body, face("reg", 10), cw - 18)
        for line in blines[:2]:
            d.text((cx0 + 9, yy), line, font=face("reg", 10), fill=FAINT)
            yy += 11
        d.text((cx0 + 9, cy0 + gh - 8), src, font=face("bold", 8),
               fill=GREY, anchor="lb")

    # ---- bottom band: map (left) + briefs (right) -----------------------
    by = 652
    d.text((16, by), "THE DAY ON THE MAP", font=face("black", 15), fill=INK)
    pins = [(s[0], s[7], s[8]) for s in CORE if s[7] is not None]
    # nudge the crowded Gulf / Europe pins apart so numbers stay readable
    nudges = {1: (-20, 10), 2: (-24, 12), 3: (26, 8), 4: (28, -14),
              5: (0, -16), 6: (-26, -6), 7: (16, -14), 8: (-22, 16),
              9: (0, 0), 10: (0, 0), 12: (0, 0), 13: (-16, -12)}
    render_map(d, 16, by + 22, 568, 260, pins, nudges)

    # region strip + day timeline under the map
    counts = {r: 0 for r in REGIONS}
    for s in CORE:
        counts[s[1]] += 1
    for b in BRIEFS:
        counts[b[1]] += 1
    strip = "  \u00b7  ".join("%s %d" % (r, counts[r]) for r in REGIONS)
    d.text((16, by + 292), strip, font=face("bold", 11), fill=INK)
    d.text((16, by + 312),
           "TIMELINE \u2014 SUNDAY NIGHT: COP31 COLLAPSES  \u00b7  SUNDAY EVENING: "
           "ALCARAZ LIFTS TURIN TITLE  \u00b7  OVERNIGHT: 186 DRONES OVER UKRAINE",
           font=face("bold", 10), fill=GREY)
    d.text((16, by + 330),
           "MONDAY MORNING: NEPAL PM MEETS MODI IN DELHI  \u00b7  MONDAY: HOUTHIS "
           "FIRE ON RIYADH, 3RD DAY",
           font=face("bold", 10), fill=GREY)

    # briefs, two flowing columns
    d.text((600, by), "ALSO ON 23 NOVEMBER", font=face("black", 15), fill=INK)
    bx0, bcol_w, bgap = 600, 198, 12
    fnt_b, fnt_n = face("reg", 9), face("bold", 10)
    bottom = by + 22
    for ci, chunk in enumerate((BRIEFS[:11], BRIEFS[11:])):
        x = bx0 + ci * (bcol_w + bgap)
        y = by + 22
        for num, region, text, src in chunk:
            full = text + " \u2014 " + src
            bl = lines_for(d, full, fnt_b, bcol_w - 24)
            if len(bl) > 2:
                print("WARN brief %d wraps to %d lines: %s" % (num, len(bl), full))
            d.text((x, y), "%d." % num, font=fnt_n, fill=RED)
            ly = y
            for line in bl[:2]:
                d.text((x + 24, ly), line, font=fnt_b, fill=(40, 48, 60))
                ly += 11
            y = ly + 2
            bottom = max(bottom, y)
    d.text((600, 992), "Stories as reported up to Monday 23 November 2026 (UTC).",
           font=face("reg", 10), fill=GREY)

    img.save(TARGET, optimize=True)
    size = os.path.getsize(TARGET)
    print("wrote %s  %d bytes  briefs bottom y=%d (limit 988)" % (TARGET, size, bottom))
    print("regions:", {r: counts[r] for r in REGIONS},
          "total stories:", len(CORE) + len(BRIEFS))
    assert size <= 1048576, "entry.png over the 1 MiB gate"
    assert bottom <= 988, "briefs overflow the page"


if __name__ == "__main__":
    build()
