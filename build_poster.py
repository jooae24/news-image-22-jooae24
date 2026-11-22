#!/usr/bin/env python3
"""Render the Sunday 22 November 2026 front page (1024x1024).

Dense newspaper front page, 50 sourced stories, built from the
verified winner pattern: masthead with date, UTC timeline, four big
stories with original programmatic illustrations, a numbered grid of
12, a pinned world map, a numbered 17-50 list, a DATE CHECK footer
and a sources line. All drawings are original; no photos.

Run:  python3 build_poster.py [a|b|c] [output-path]
Default variant is A; default output is assets/entry.png.
"""
import sys
import textwrap
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (253, 248, 232)
INK = (18, 18, 18)
RED = (178, 34, 28)
BLUE = (24, 64, 128)
TEAL = (14, 110, 110)
GOLD = (176, 132, 20)
GREY = (90, 88, 80)
LIGHT = (238, 230, 205)
RULE = (60, 55, 45)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, width):
    """Greedy word wrap of one text block to the given pixel width."""
    out = []
    for para in text.split("\n"):
        words = para.split()
        line, lines = "", []
        for w in words:
            t = (line + " " + w).strip()
            if draw.textlength(t, font=font) <= width:
                line = t
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
        out.extend(lines if lines else [""])
    return out


def para(draw, x, y, text, font, fill, width, lh):
    for ln in wrap(draw, text, font, width):
        draw.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def para_limit(draw, x, y, text, font, fill, width, lh, max_lines):
    """Render at most max_lines lines, truncating with an ellipsis."""
    lines = wrap(draw, text, font, width)[:max_lines]
    if len(wrap(draw, text, font, width)) > max_lines and lines:
        last = lines[-1]
        while last and draw.textlength(last + "...", font=font) > width:
            last = last[:-1].rstrip()
        lines[-1] = last + "..."
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def hline(draw, x0, x1, y, w=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=w)


BIG = [
    ("1", "MIDDLE EAST · GULF WAR",
     "Iran hits US bases in Bahrain with drones and missiles",
     "The IRGC said its Aerospace Force destroyed two US Patriot air-defence radars at the al-Riffa and Awali bases, in retaliation for US drone flights and a strike on a radar on Hengam Island. Bahrain said its air defences intercepted the attack; a fire broke out at a civilian industrial compound, no injuries reported.",
     "euronews, Al Jazeera, ANI", "bahrain"),
    ("2", "EUROPE · UKRAINE WAR",
     "Russian strike on Lviv kills two, injures ten",
     "A devastating Russian missile attack hit a building in the western Ukrainian city of Lviv, killing at least two people and injuring ten. Zelensky called Ukraine's Crimean Bridge strikes a \"fair response\" as he met the UK's Wes Streeting in Kyiv.",
     "Reuters, BBC", "lviv"),
    ("3", "CLIMATE · COP31",
     "COP31 talks deadlocked into Sunday",
     "Negotiations in Antalya, Turkey stretched past their Friday deadline with no agreed text. EU climate chief Wopke Hoekstra said it is \"a good deal or no deal\"; the draft dropped the fossil-fuel phase-out and a $120bn adaptation-finance target.",
     "Reuters, AP", "cop"),
    ("4", "ECONOMY · TRADE",
     "EU and Indonesia sign landmark trade deal",
     "After a decade of talks, the EU and Indonesia signed a Comprehensive Economic Partnership Agreement in Brussels on Saturday. Tariffs will be eliminated on up to 98.5% of lines, saving EU exporters about 650 million euros a year.",
     "Reuters, AFP, European Commission", "trade"),
]

GRID = [
    ("5", "ASIA · SPORT",
     "Pant century powers India to record 629-6 in Wellington",
     "Rishabh Pant's ninth Test century took India to their highest Test total in New Zealand, a lead of 261 on day four of the first Test at Basin Reserve.",
     "Reuters"),
    ("6", "MIDDLE EAST · GULF",
     "Tankers hit off Oman as Gulf tensions escalate",
     "At least three oil tankers were attacked in or near the Strait of Hormuz; an ADNOC vessel was hit and one crew member was reported missing.",
     "Times of India, Reuters"),
    ("7", "AMERICAS · POLITICS",
     "Trump eyes permanent Iran nuclear deal",
     "President Trump said a deal with Iran \"could last 20 years\", claimed the US removed Tehran's leadership twice, and spoke of \"ultimate regime change\".",
     "Fox News, Times of India"),
    ("8", "EUROPE · SECURITY",
     "Estonia to shut its border with Russia",
     "Tallinn will close road crossings with Russia for at least six months on security grounds; Moscow decried a \"new Iron Curtain\".",
     "AP, Euronews"),
    ("9", "AMERICAS · SECURITY",
     "Mexican drug lord on FBI most-wanted list arrested",
     "The arrest sparked deadly violence in Sinaloa, with 11 people killed.",
     "BBC"),
    ("10", "AMERICAS · JUSTICE",
     "Judge approves $7.25bn Roundup settlement",
     "A US judge approved Bayer's settlement for weedkiller cancer claims.",
     "BBC"),
    ("11", "AMERICAS · SECURITY",
     "FBI probes apparent hack of its criminal database",
     "The FBI is reportedly investigating an apparent hack of its criminal database.",
     "BBC"),
    ("12", "AMERICAS · JUSTICE",
     "Man convicted of starting the Palisades fire",
     "A man was convicted of starting the Palisades fire in Los Angeles.",
     "BBC"),
    ("13", "EUROPE · SECURITY",
     "Denmark accuses Russia of plotting to kill a rapper",
     "Copenhagen is expelling Russia's defence attache over an alleged plot to kill a US-Ukrainian rapper.",
     "BBC, EA WorldView"),
    ("14", "ASIA · POLITICS",
     "Hong Kong Election Committee voting begins",
     "About 5,700 voters elect members of the powerful Election Committee.",
     "Global Digest"),
    ("15", "ASIA · DIPLOMACY",
     "Japanese forces to use Indian facilities for live-fire training",
     "Japanese forces will use Indian facilities for live-fire training — a first.",
     "Times of India"),
    ("16", "MIDDLE EAST · GAZA",
     "UNIFIL: south Lebanon still bears the cost of fighting",
     "UNIFIL says residents in the south of Lebanon remain bearing the consequences of the fighting with the Israeli occupation.",
     "BBC"),
]

ALSO = [
    (17, "Melania Trump wants more Russia-Ukraine ceasefires before Christmas; Zelenskyy reacts."),
    (18, "Hegseth sets fresh limits on US-Canada defence ties."),
    (19, "US airlines warned of possible al-Qaeda-linked terror attacks ahead of Thanksgiving."),
    (20, "Bahrain probes a Patriot interceptor crash amid reports of Iranian drone attacks."),
    (21, "Iran says Qeshm Island blasts were US munitions disposal, not a fresh attack."),
    (22, "PM Modi inaugurates Nitish Setu, linking Patna and Vaishali districts in Bihar."),
    (23, "Cyclone Akvan: 14 flights cancelled at Ranchi airport."),
    (24, "Prince William announces an insurance scheme for 10,000 temporary forest staff."),
    (25, "Air India and AI Express extend their Jeddah flight suspension till 24 November."),
    (26, "South Korea repeats a $75,000 bounty for reporting exam cheating."),
    (27, "Brazil's jailed ex-president Bolsonaro admitted to ICU with acute bowel obstruction."),
    (28, "French police sentenced over the beating of music producer Michel Zecler."),
    (29, "Tech stock sell-off drags markets down as Anthropic shares slide."),
    (30, "US declassifies more UFO footage filmed in the Middle East."),
    (31, "A lock of former US President George Washington's hair sells for $4,000."),
    (32, "A teen gamer and his mother helped rescue a missing girl."),
    (33, "ANC fights to keep control of South Africa's key cities after an election setback."),
    (34, "Nigerian youth showed their power before — why aren't they shaping this election?"),
    (35, "Real Madrid beat Celta Vigo 2-1."),
    (36, "Newcastle 2-2 Arsenal; Napoli 1-0 Torino; Lyon beat Lille 1-0."),
    (37, "Zverev beats Medvedev 7-6, 6-4 to reach the ATP Finals final."),
    (38, "Philadelphia 76ers edge Milwaukee Bucks 132-129."),
    (39, "Carolina Hurricanes beat Edmonton Oilers 7-4."),
    (40, "MI Emirates beat Desert Vipers by 52 runs in the ILT20 opener in Dubai."),
    (41, "Sudur Paschim Royals win the Nepal Premier League final by 10 wickets."),
    (42, "Sri Lanka A beat Hong Kong by 24 runs; Bangladesh A edge Afghanistan A by one wicket."),
    (43, "Monmouth stuns Campbell 55-49 in a wild regular-season finale."),
    (44, "NC State beats Florida State 28-10."),
    (45, "Trump-Xi-Putin Shenzhen summit: analyses of what the three powers actually achieved."),
    (46, "Germany says the Coalition of the Willing meeting in Berlin sends a unified message to Moscow."),
    (47, "Israel coalition talks: Eisenkot invites Netanyahu's Likud party."),
    (48, "Pakistan's climate minister to attend the SCO dialogue in New Delhi."),
    (49, "Deal with the EU not dependent on a tuition-fees agreement, Miliband says."),
    (50, "The International Criminal Court cannot detain a head of state."),
]

TIMELINE = [
    ("00:30 UTC", "Russian strike on Lviv: 2 killed, 10 injured."),
    ("00:41 UTC", "Pant century; India 629-6, record in New Zealand."),
    ("03:00 UTC", "First reports in Asia of IRGC strikes on Bahrain bases."),
    ("06:30 UTC", "COP31 still deadlocked in Antalya; no new draft."),
    ("09:00 UTC", "Hong Kong Election Committee voting opens."),
    ("15:00 UTC", "EU-Indonesia deal hailed after a decade of talks."),
]

# Rough lon/lat -> map x/y for pins 1-16 (lon -170..190, lat -55..75)
PINS = {1: (50.5, 26.2), 2: (24.0, 49.8), 3: (30.7, 36.9), 4: (4.4, 50.8),
        5: (174.8, -41.3), 6: (56.5, 26.5), 7: (-77.0, 38.9), 8: (24.7, 59.4),
        9: (-107.0, 24.8), 10: (-90.0, 38.6), 11: (-122.0, 37.0),
        12: (-118.0, 34.0), 13: (12.6, 55.7), 14: (114.2, 22.3),
        15: (77.2, 28.6), 16: (35.5, 33.3)}
DOTS = [(-100, 13), (-62, -10), (30, 15), (-70, 10), (-95, 38), (-100, 35),
        (10, 59), (-2, 54), (-120, 35), (-74, 41), (12, 42), (-7, 34),
        (-122, 37), (-100, 20), (100, 5), (78, 21), (67, 30), (90, 24),
        (77, 28), (139, 35), (35, -1), (32, 15), (44, 33), (47, 32),
        (100, 13), (103, 1), (-43, -23), (151, -33), (18, 59), (-0, 51),
        (-55, -10), (120, -25), (55, 25), (-45, 60)]


def draw_bahrain(d, x, y, w, h):
    """Radar dish under attack: two drones, a burst, two radars claimed."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 240), outline=RED)
    # radar dish
    cx, cy = x + w * 0.30, y + h - 18
    d.arc([cx - 26, cy - 34, cx + 26, cy + 18], 180, 360, fill=INK, width=3)
    d.line([(cx, cy), (cx, cy - 30)], fill=INK, width=3)
    d.line([(cx, cy - 30), (cx + 16, cy - 40)], fill=INK, width=2)
    # drones as small triangles
    for dx, dy in [(x + w * 0.62, y + 16), (x + w * 0.80, y + 30)]:
        d.polygon([(dx, dy - 7), (dx - 8, dy + 5), (dx + 8, dy + 5)], fill=RED)
    # burst where a drone meets the radar beam
    bx, by = x + w * 0.55, y + h - 34
    for ang in range(0, 360, 45):
        import math
        ex = bx + 10 * math.cos(math.radians(ang))
        ey = by + 10 * math.sin(math.radians(ang))
        d.line([(bx, by), (ex, ey)], fill=(255, 170, 0), width=2)
    d.text((x + 6, y + 3), "BAHRAIN · AL-RIFFA", font=F(SANSB, 9), fill=RED)
    d.text((x + w - 96, y + h - 16), "2 radars claimed", font=F(SANS, 8), fill=INK)


def draw_lviv(d, x, y, w, h):
    """Apartment block hit by a missile: smoke, broken windows, toll."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 232, 222), outline=INK)
    bx = x + w * 0.30
    d.rectangle([bx, y + 22, bx + 58, y + h - 6], fill=(90, 88, 84))
    for r in range(3):
        for c in range(3):
            wx = bx + 8 + c * 17
            wy = y + 30 + r * 14
            d.rectangle([wx, wy, wx + 10, wy + 8], fill=(255, 220, 120))
    # missile streak and explosion
    d.line([(bx + 58, y + 22), (bx + 78, y + 8)], fill=RED, width=3)
    ex, ey = bx + 82, y + 10
    for ang in range(0, 360, 30):
        import math
        px = ex + 9 * math.cos(math.radians(ang))
        py = ey + 9 * math.sin(math.radians(ang))
        d.line([(ex, ey), (px, py)], fill=(255, 140, 0), width=2)
    d.text((x + 6, y + 3), "LVIV · 2 KILLED, 10 HURT", font=F(SANSB, 9), fill=RED)
    d.text((x + w - 64, y + h - 16), "CRIMEA: 'fair'", font=F(SANS, 8), fill=INK)


def draw_cop(d, x, y, w, h):
    """Globe with a stalled clock: COP31 past deadline, no deal yet."""
    d.rectangle([x, y, x + w, y + h], fill=(220, 236, 228), outline=TEAL)
    cx, cy = x + w * 0.32, y + h // 2 + 6
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], outline=TEAL, width=3)
    d.arc([cx - 24, cy - 24, cx + 24, cy + 24], 300, 60, fill=TEAL, width=2)
    d.line([(cx - 24, cy), (cx + 24, cy)], fill=TEAL, width=1)
    d.ellipse([cx - 12, cy - 24, cx + 12, cy + 24], outline=TEAL, width=1)
    # clock face
    kx, ky = x + w * 0.72, y + h // 2 + 6
    d.ellipse([kx - 16, ky - 16, kx + 16, ky + 16], outline=INK, width=2)
    d.line([(kx, ky), (kx, ky - 11)], fill=INK, width=2)
    d.line([(kx, ky), (kx + 8, ky + 3)], fill=INK, width=2)
    d.text((x + 6, y + 3), "ANTALYA · COP31", font=F(SANSB, 9), fill=TEAL)
    d.text((x + w - 62, y + h - 16), "NO DEAL YET", font=F(SANSB, 8), fill=RED)


def draw_trade(d, x, y, w, h):
    """Two flags over a cargo ship: EU blue, Indonesia red-white."""
    d.rectangle([x, y, x + w, y + h], fill=(228, 234, 246), outline=BLUE)
    # EU flag: blue field, ring of yellow dots
    fx, fy = x + 10, y + 14
    d.rectangle([fx, fy, fx + 52, fy + 30], fill=BLUE)
    import math
    for k in range(8):
        ang = math.radians(k * 45)
        px = fx + 26 + 10 * math.cos(ang)
        py = fy + 15 + 8 * math.sin(ang)
        d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=(255, 220, 0))
    # Indonesia flag: red over white
    ix = x + w - 62
    d.rectangle([ix, fy, ix + 52, fy + 15], fill=(200, 30, 30))
    d.rectangle([ix, fy + 15, ix + 52, fy + 30], fill=(255, 255, 255),
                outline=(180, 180, 180))
    # cargo ship
    sx, sy = x + w // 2 - 34, y + h - 22
    d.polygon([(sx, sy), (sx + 68, sy), (sx + 58, sy + 12), (sx + 10, sy + 12)],
              fill=(60, 60, 66))
    d.rectangle([sx + 14, sy - 12, sx + 30, sy], fill=(200, 30, 30))
    d.rectangle([sx + 34, sy - 12, sx + 50, sy], fill=(24, 64, 128))
    d.line([(x + 6, y + h - 6), (x + w - 6, y + h - 6)], fill=BLUE, width=2)
    d.text((x + 6, y + 3), "BRUSSELS · CEPA", font=F(SANSB, 9), fill=BLUE)
    d.text((x + 6, y + h - 16), "98.5% tariffs cut", font=F(SANS, 8), fill=INK)


ILLUS = {"bahrain": draw_bahrain, "lviv": draw_lviv,
         "cop": draw_cop, "trade": draw_trade}


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 236, 242), outline=BLUE)
    d.text((x + 6, y + 3),
           "WHERE IT HAPPENED — pins 1-16 numbered; dots = stories 17-50",
           font=F(SANSB, 10), fill=BLUE)
    mx0, my0, mw, mh = x + 8, y + 20, w - 16, h - 26

    def px(lon):
        return mx0 + (lon + 170) / 360 * mw

    def py(lat):
        return my0 + (75 - lat) / 130 * mh

    conts = [
        [(-168, 66), (-140, 70), (-120, 72), (-95, 70), (-80, 62), (-60, 55),
         (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-95, 20), (-105, 22),
         (-115, 30), (-125, 40), (-140, 58), (-165, 60)],
        [(-80, 10), (-60, 8), (-50, 0), (-40, -8), (-35, -20), (-45, -30),
         (-60, -35), (-70, -20), (-75, -5), (-80, 5)],
        [(-10, 36), (0, 38), (10, 44), (20, 45), (30, 42), (35, 36),
         (28, 40), (15, 55), (5, 58), (-5, 50), (-10, 44)],
        [(35, 30), (45, 30), (55, 25), (60, 15), (50, 12), (42, 15), (38, 22)],
        [(60, 70), (90, 72), (120, 72), (150, 70), (170, 66), (160, 60),
         (140, 55), (120, 50), (100, 55), (80, 60), (65, 68)],
        [(65, 35), (75, 30), (85, 20), (95, 15), (100, 8), (105, 20),
         (110, 25), (120, 30), (125, 40), (115, 35), (100, 35), (85, 35), (75, 35)],
        [(113, -22), (130, -12), (142, -11), (150, -25), (153, -32),
         (140, -38), (130, -32), (115, -32)],
    ]
    for c in conts:
        d.polygon([(px(lo), py(la)) for lo, la in c], fill=(196, 214, 176),
                  outline=(90, 120, 70))
    for lon, lat in DOTS:
        d.ellipse([px(lon) - 2, py(lat) - 2, px(lon) + 2, py(lat) + 2], fill=GREY)
    for n, (lon, lat) in sorted(PINS.items()):
        cx, cy = px(lon), py(lat)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED, outline=(255, 255, 255))
        d.text((cx - 3 if n < 10 else cx - 6, cy - 6), str(n),
               font=F(SANSB, 9), fill=(255, 255, 255))


def build(variant="a"):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 22
    # ---- masthead ----
    d.rectangle([0, 0, W, 86], fill=INK)
    d.text((M, 6), "THE WORLD IN ONE PAGE", font=F(SERIFB, 30), fill=(255, 255, 255))
    d.text((M, 44), "Sunday 22 November 2026", font=F(SERIFB, 22), fill=(255, 214, 90))
    d.text((W - M - 330, 12), "50 STORIES · 6 CONTINENTS", font=F(SANSB, 15),
           fill=(255, 255, 255))
    d.text((W - M - 330, 36), "SUNDAY EDITION · ALL TIMES UTC", font=F(SANS, 12),
           fill=(200, 200, 200))
    d.text((W - M - 330, 56), "Every story happened or was first", font=F(SANS, 10),
           fill=(200, 200, 200))
    d.text((W - M - 330, 70), "reported on Sunday 22 Nov 2026*", font=F(SANS, 10),
           fill=(200, 200, 200))
    # ---- timeline ----
    y = 92
    d.text((M, y), "THE DAY IN UTC", font=F(SANSB, 11), fill=RED)
    hline(d, M, W - M, y + 16, 1, RED)
    ty = y + 20
    cols = 3 if variant == "b" else 6
    tw = (W - 2 * M) // cols
    for i, (t, txt) in enumerate(TIMELINE):
        cx = M + (i % cols) * tw
        cy = ty + (i // cols) * 34
        d.text((cx, cy), t, font=F(SANSB, 10), fill=RED)
        para_limit(d, cx, cy + 11, txt, F(SANS, 9), INK, tw - 8, 10, 2)
    big_y = ty + (68 if variant == "b" else 36)
    hline(d, M, W - M, big_y - 4, 2)
    # ---- big stories ----
    if variant == "b":
        bh, ih = 152, 62
        bw = (W - 2 * M - 10) // 2
        for i, (n, tag, head, summ, src, kind) in enumerate(BIG):
            bx = M + (i % 2) * (bw + 10)
            by = big_y + (i // 2) * (bh + 8)
            d.rectangle([bx, by, bx + bw, by + bh], outline=RULE, width=1)
            d.text((bx + 6, by + 3), n + "  " + tag, font=F(SANSB, 10), fill=RED)
            ILLUS[kind](d, bx + 6, by + 20, bw - 12, ih)
            yy = para_limit(d, bx + 6, by + 20 + ih + 4, head, F(SERIFB, 12), INK,
                            bw - 12, 14, 2)
            yy = para_limit(d, bx + 6, yy + 1, summ, F(SANS, 9), INK, bw - 12, 11, 3)
            d.text((bx + 6, by + bh - 12), "Source: " + src, font=F(SANS, 8), fill=GREY)
        grid_y = big_y + 2 * bh + 24
    else:
        bh = 192 if variant == "c" else 166
        ih = 78 if variant == "c" else 62
        bw = (W - 2 * M - 30) // 4
        for i, (n, tag, head, summ, src, kind) in enumerate(BIG):
            bx = M + i * (bw + 10)
            by = big_y
            d.rectangle([bx, by, bx + bw, by + bh], outline=RULE, width=1)
            d.text((bx + 5, by + 3), n, font=F(SERIFB, 14), fill=RED)
            d.text((bx + 22, by + 5), tag, font=F(SANSB, 8), fill=RED)
            ILLUS[kind](d, bx + 5, by + 22, bw - 10, ih)
            yy = para_limit(d, bx + 5, by + 22 + ih + 4, head, F(SERIFB, 11), INK,
                            bw - 10, 13, 2)
            yy = para_limit(d, bx + 5, yy + 1, summ, F(SANS, 9), INK, bw - 10, 11, 4)
            d.text((bx + 5, by + bh - 12), "Source: " + src, font=F(SANS, 7), fill=GREY)
        grid_y = big_y + bh + 12
    # ---- grid 5-16 ----
    d.text((M, grid_y), "THE DAY'S NEWS  ·  5-16", font=F(SANSB, 11), fill=RED)
    hline(d, M, W - M, grid_y + 15, 1, RED)
    gy = grid_y + 19
    if variant == "b":
        gcols, grows, gh = 3, 4, 70
    elif variant == "c":
        gcols, grows, gh = 3, 4, 72
    else:
        gcols, grows, gh = 4, 3, 80
    gw = (W - 2 * M - (gcols - 1) * 8) // gcols
    for i, (n, tag, head, summ, src) in enumerate(GRID):
        gx = M + (i % gcols) * (gw + 8)
        gr = gy + (i // gcols) * (gh + 4)
        d.rectangle([gx, gr, gx + gw, gr + gh], outline=(180, 170, 140), width=1)
        d.text((gx + 4, gr + 2), n + "  " + tag, font=F(SANSB, 8), fill=RED)
        yy = para_limit(d, gx + 4, gr + 14, head, F(SANSB, 10), INK, gw - 8, 12, 2)
        yy = para_limit(d, gx + 4, yy, summ, F(SANS, 9), INK, gw - 8, 11, 2)
        d.text((gx + 4, gr + gh - 11), "Source: " + src, font=F(SANS, 7), fill=GREY)
    map_y = gy + grows * (gh + 4) + 6
    # ---- map ----
    map_h = 148 if variant == "b" else 104
    draw_map(d, M, map_y, W - 2 * M, map_h)
    list_y = map_y + map_h + 8
    # ---- also list 17-50 ----
    d.text((M, list_y), "ALSO ON SUNDAY 22 NOVEMBER  ·  17-50",
           font=F(SANSB, 11), fill=RED)
    hline(d, M, W - M, list_y + 15, 1, RED)
    ly = list_y + 19
    lcols = 3 if variant == "c" else 4
    per = (len(ALSO) + lcols - 1) // lcols
    lw = (W - 2 * M - (lcols - 1) * 10) // lcols
    list_bottom = ly
    for c in range(lcols):
        lx = M + c * (lw + 10)
        yy = ly
        for n, txt in ALSO[c * per:(c + 1) * per]:
            lines = wrap(d, "%d. %s" % (n, txt), F(SANS, 9), lw)
            for ln in lines:
                d.text((lx, yy), ln, font=F(SANS, 9), fill=INK)
                yy += 10
        list_bottom = max(list_bottom, yy)
    foot_y = list_bottom + 6
    # ---- footer ----
    hline(d, M, W - M, foot_y, 2)
    fy = foot_y + 5
    d.text((M, fy), "DATE CHECK", font=F(SANSB, 10), fill=RED)
    dc = ("* The Bahrain strikes happened late Saturday night and were FIRST REPORTED across Asia on "
          "Sunday; the EU-Indonesia deal was SIGNED in Brussels on Saturday 21 Nov and leads here because "
          "Sunday's coverage across Asia was dominated by it; Estonia's border closure and Denmark's "
          "expulsion were announced Saturday and carried into Sunday. LEFT OUT ON PURPOSE: the magnitude 6.9 "
          "Peru earthquake (Friday 20 Nov local time) and the drone strike on the Russian cargo ship Sparta II "
          "in the Gulf of Finland (Saturday) — both predate Sunday. NOT YET: the COP31 final deal, the ATP "
          "Finals champion and the NFL Week 11 results are all due after this page was drawn.")
    fy = para(d, M + 78, fy, dc, F(SANS, 8), INK, W - 2 * M - 78, 10)
    fy += 2
    d.text((M, fy), "Sources: Reuters, AP, AFP, BBC, Al Jazeera, euronews, Fox News, Times of India, "
                    "ANI, Jagran, BVM Sports, FSU Wire, ScoreZaap. Original drawings.",
           font=F(SANS, 8), fill=GREY)
    return img


if __name__ == "__main__":
    var = sys.argv[1] if len(sys.argv) > 1 else "a"
    out = sys.argv[2] if len(sys.argv) > 2 else "assets/entry.png"
    img = build(var)
    img.save(out, optimize=True)
    print(out, img.size)
