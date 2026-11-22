#!/usr/bin/env python3
"""Sunday 22 November 2026 front page — a dense newspaper poster.

Renders one 1024x1024 PNG: a masthead with the date, a UTC timeline,
four big stories with original programmatic illustrations, a numbered
grid of twelve, a pinned world map, a numbered list to fifty stories,
a DATE CHECK footer and a sources line. Everything is drawn by this
file; no photos, no network, no fonts beyond the system DejaVu set.

Usage: python3 build_poster.py [classic|wide] [output-path]

Layout note: the classic layout (four lead stories across, four-column
grid and list) fits all fifty stories, the map, the DATE CHECK and the
sources line inside 1024x1024; the wide layout (2x2 lead stories) runs
out of room and cuts the 17-50 list and the footer off the page.
"""
import math
import sys
from PIL import Image, ImageDraw, ImageFont

CANVAS = 1024
MARGIN = 22
BG = (253, 248, 232)
FG = (18, 18, 18)
ACCENT = (178, 34, 28)
NAVY = (24, 64, 128)
SEA = (14, 110, 110)
OCHRE = (176, 132, 20)
MUTED = (90, 88, 80)
FAINT = (180, 170, 140)
EDGE = (60, 55, 45)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def _load(name, size):
    return ImageFont.truetype("%s/%s" % (FONT_DIR, name), size)


def serif(size, bold=False):
    return _load("DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf", size)


def sans(size, bold=False):
    return _load("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)


def _split_words(draw, text, font, width):
    """Greedy wrap: returns the lines of text that fit in width pixels."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split()
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            if draw.textlength(trial, font=font) <= width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        lines.append(current if current else "")
    return lines


class FrontPage:
    """One poster, drawn section by section onto a 1024x1024 canvas."""

    def __init__(self, layout="classic"):
        self.layout = layout
        self.img = Image.new("RGB", (CANVAS, CANVAS), BG)
        self.d = ImageDraw.Draw(self.img)

    # -- tiny drawing helpers -------------------------------------------
    def text(self, x, y, s, font, fill):
        self.d.text((x, y), s, font=font, fill=fill)

    def rule(self, x0, x1, y, width=2, fill=FG):
        self.d.line([(x0, y), (x1, y)], fill=fill, width=width)

    def block(self, x, y, text, font, fill, width, leading, limit=None):
        """Draw wrapped text; returns the y after the last line."""
        lines = _split_words(self.d, text, font, width)
        shown = lines if limit is None else lines[:limit]
        if limit is not None and len(lines) > limit and shown:
            tail = shown[-1]
            while tail and self.d.textlength(tail + "...", font=font) > width:
                tail = tail[:-1].rstrip()
            shown[-1] = tail + "..."
        for line in shown:
            self.text(x, y, line, font, fill)
            y += leading
        return y

    # -- sections --------------------------------------------------------
    def masthead(self):
        d = self.d
        d.rectangle([0, 0, CANVAS, 86], fill=FG)
        self.text(MARGIN, 6, "THE WORLD IN ONE PAGE", serif(30, True),
                  (255, 255, 255))
        self.text(MARGIN, 44, "Sunday 22 November 2026", serif(22, True),
                  (255, 214, 90))
        rx = CANVAS - MARGIN - 330
        self.text(rx, 12, "50 STORIES · 6 CONTINENTS", sans(15, True),
                  (255, 255, 255))
        self.text(rx, 36, "SUNDAY EDITION · ALL TIMES UTC", sans(12),
                  (200, 200, 200))
        self.text(rx, 56, "Every story happened or was first", sans(10),
                  (200, 200, 200))
        self.text(rx, 70, "reported on Sunday 22 Nov 2026*", sans(10),
                  (200, 200, 200))

    def timeline(self, top):
        self.text(MARGIN, top, "THE DAY IN UTC", sans(11, True), ACCENT)
        self.rule(MARGIN, CANVAS - MARGIN, top + 16, 1, ACCENT)
        cols = 3 if self.layout == "wide" else 6
        colw = (CANVAS - 2 * MARGIN) // cols
        for i, (when, what) in enumerate(TIMELINE):
            cx = MARGIN + (i % cols) * colw
            cy = top + 20 + (i // cols) * 34
            self.text(cx, cy, when, sans(10, True), ACCENT)
            self.block(cx, cy + 11, what, sans(9), FG, colw - 8, 10, limit=2)
        return top + 20 + (68 if self.layout == "wide" else 36)

    def big_stories(self, top):
        self.rule(MARGIN, CANVAS - MARGIN, top - 4, 2)
        if self.layout == "wide":
            box_h, pic_h = 152, 62
            box_w = (CANVAS - 2 * MARGIN - 10) // 2
            positions = [(MARGIN + (i % 2) * (box_w + 10),
                          top + (i // 2) * (box_h + 8)) for i in range(4)]
        else:
            box_h, pic_h = 166, 62
            box_w = (CANVAS - 2 * MARGIN - 30) // 4
            positions = [(MARGIN + i * (box_w + 10), top) for i in range(4)]
        for (num, tag, head, summ, src, kind), (bx, by) in zip(BIG, positions):
            self.d.rectangle([bx, by, bx + box_w, by + box_h], outline=EDGE)
            self.text(bx + 5, by + 3, num, serif(14, True), ACCENT)
            self.text(bx + 22, by + 5, tag, sans(8, True), ACCENT)
            getattr(self, "pic_" + kind)(bx + 5, by + 22, box_w - 10, pic_h)
            yy = self.block(bx + 5, by + 22 + pic_h + 4, head,
                            serif(11, True), FG, box_w - 10, 13, limit=2)
            self.block(bx + 5, yy + 1, summ, sans(9), FG, box_w - 10, 11,
                       limit=4)
            self.text(bx + 5, by + box_h - 12, "Source: " + src, sans(7),
                      MUTED)
        rows = 2 if self.layout == "wide" else 1
        return top + rows * box_h + (rows - 1) * 8 + 12

    def grid(self, top):
        self.text(MARGIN, top, "THE DAY'S NEWS  ·  5-16", sans(11, True),
                  ACCENT)
        self.rule(MARGIN, CANVAS - MARGIN, top + 15, 1, ACCENT)
        if self.layout == "wide":
            ncols, nrows, cell_h = 3, 4, 70
        else:
            ncols, nrows, cell_h = 4, 3, 80
        cell_w = (CANVAS - 2 * MARGIN - (ncols - 1) * 8) // ncols
        gy = top + 19
        for i, (num, tag, head, summ, src) in enumerate(GRID):
            gx = MARGIN + (i % ncols) * (cell_w + 8)
            gr = gy + (i // ncols) * (cell_h + 4)
            self.d.rectangle([gx, gr, gx + cell_w, gr + cell_h], outline=FAINT)
            self.text(gx + 4, gr + 2, num + "  " + tag, sans(8, True), ACCENT)
            yy = self.block(gx + 4, gr + 14, head, sans(10, True), FG,
                            cell_w - 8, 12, limit=2)
            self.block(gx + 4, yy, summ, sans(9), FG, cell_w - 8, 11, limit=2)
            self.text(gx + 4, gr + cell_h - 11, "Source: " + src, sans(7),
                      MUTED)
        return gy + nrows * (cell_h + 4) + 6

    def world_map(self, top, height):
        d = self.d
        d.rectangle([MARGIN, top, CANVAS - MARGIN, top + height],
                    fill=(222, 236, 242), outline=NAVY)
        self.text(MARGIN + 6, top + 3,
                  "WHERE IT HAPPENED — pins 1-16 numbered; dots = stories 17-50",
                  sans(10, True), NAVY)
        mx, my = MARGIN + 8, top + 20
        mw, mh = CANVAS - 2 * MARGIN - 16, height - 26

        def px(lon):
            return mx + (lon + 170) / 360 * mw

        def py(lat):
            return my + (75 - lat) / 130 * mh

        for shape in CONTINENTS:
            d.polygon([(px(lo), py(la)) for lo, la in shape],
                      fill=(196, 214, 176), outline=(90, 120, 70))
        for lon, lat in DOTS:
            d.ellipse([px(lon) - 2, py(lat) - 2, px(lon) + 2, py(lat) + 2],
                      fill=MUTED)
        for num, (lon, lat) in sorted(PINS.items()):
            cx, cy = px(lon), py(lat)
            d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=ACCENT,
                      outline=(255, 255, 255))
            self.text(cx - 3 if num < 10 else cx - 6, cy - 6, str(num),
                      sans(9, True), (255, 255, 255))
        return top + height

    def also_list(self, top):
        self.text(MARGIN, top, "ALSO ON SUNDAY 22 NOVEMBER  ·  17-50",
                  sans(11, True), ACCENT)
        self.rule(MARGIN, CANVAS - MARGIN, top + 15, 1, ACCENT)
        ncols = 3 if self.layout == "wide" else 4
        per = (len(ALSO) + ncols - 1) // ncols
        colw = (CANVAS - 2 * MARGIN - (ncols - 1) * 10) // ncols
        bottom = top + 19
        for c in range(ncols):
            lx = MARGIN + c * (colw + 10)
            yy = top + 19
            for num, txt in ALSO[c * per:(c + 1) * per]:
                for line in _split_words(self.d, "%d. %s" % (num, txt),
                                         sans(9), colw):
                    self.text(lx, yy, line, sans(9), FG)
                    yy += 10
            bottom = max(bottom, yy)
        return bottom

    def footer(self, top):
        self.rule(MARGIN, CANVAS - MARGIN, top, 2)
        fy = top + 5
        self.text(MARGIN, fy, "DATE CHECK", sans(10, True), ACCENT)
        fy = self.block(MARGIN + 78, fy, DATE_CHECK, sans(8), FG,
                        CANVAS - 2 * MARGIN - 78, 10)
        self.text(MARGIN, fy + 2, SOURCES_LINE, sans(8), MUTED)
        return fy + 2

    # -- illustrations (original drawings) --------------------------------
    def _burst(self, cx, cy, r, color):
        for k in range(8):
            ang = math.radians(k * 45)
            ex = cx + r * math.cos(ang)
            ey = cy + r * math.sin(ang)
            self.d.line([(cx, cy), (ex, ey)], fill=color, width=2)

    def pic_bahrain(self, x, y, w, h):
        d = self.d
        d.rectangle([x, y, x + w, y + h], fill=(226, 232, 240), outline=ACCENT)
        cx, cy = x + int(w * 0.30), y + h - 18
        d.arc([cx - 26, cy - 34, cx + 26, cy + 18], 180, 360, fill=FG, width=3)
        d.line([(cx, cy), (cx, cy - 30)], fill=FG, width=3)
        d.line([(cx, cy - 30), (cx + 16, cy - 40)], fill=FG, width=2)
        for dx, dy in [(x + w * 0.62, y + 16), (x + w * 0.80, y + 30)]:
            d.polygon([(dx, dy - 7), (dx - 8, dy + 5), (dx + 8, dy + 5)],
                      fill=ACCENT)
        self._burst(x + int(w * 0.55), y + h - 34, 10, (255, 170, 0))
        self.text(x + 6, y + 3, "BAHRAIN · AL-RIFFA", sans(9, True), ACCENT)
        self.text(x + w - 96, y + h - 16, "2 radars claimed", sans(8), FG)

    def pic_lviv(self, x, y, w, h):
        d = self.d
        d.rectangle([x, y, x + w, y + h], fill=(240, 232, 222), outline=FG)
        bx = x + int(w * 0.30)
        d.rectangle([bx, y + 22, bx + 58, y + h - 6], fill=(90, 88, 84))
        for r in range(3):
            for c in range(3):
                wx = bx + 8 + c * 17
                wy = y + 30 + r * 14
                d.rectangle([wx, wy, wx + 10, wy + 8], fill=(255, 220, 120))
        d.line([(bx + 58, y + 22), (bx + 78, y + 8)], fill=ACCENT, width=3)
        self._burst(bx + 82, y + 10, 9, (255, 140, 0))
        self.text(x + 6, y + 3, "LVIV · 2 KILLED, 10 HURT", sans(9, True),
                  ACCENT)
        self.text(x + w - 64, y + h - 16, "CRIMEA: 'fair'", sans(8), FG)

    def pic_cop(self, x, y, w, h):
        d = self.d
        d.rectangle([x, y, x + w, y + h], fill=(220, 236, 228), outline=SEA)
        cx, cy = x + int(w * 0.32), y + h // 2 + 6
        d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], outline=SEA, width=3)
        d.arc([cx - 24, cy - 24, cx + 24, cy + 24], 300, 60, fill=SEA, width=2)
        d.line([(cx - 24, cy), (cx + 24, cy)], fill=SEA, width=1)
        d.ellipse([cx - 12, cy - 24, cx + 12, cy + 24], outline=SEA, width=1)
        kx, ky = x + int(w * 0.72), y + h // 2 + 6
        d.ellipse([kx - 16, ky - 16, kx + 16, ky + 16], outline=FG, width=2)
        d.line([(kx, ky), (kx, ky - 11)], fill=FG, width=2)
        d.line([(kx, ky), (kx + 8, ky + 3)], fill=FG, width=2)
        self.text(x + 6, y + 3, "ANTALYA · COP31", sans(9, True), SEA)
        self.text(x + w - 62, y + h - 16, "NO DEAL YET", sans(8, True),
                  ACCENT)

    def pic_trade(self, x, y, w, h):
        d = self.d
        d.rectangle([x, y, x + w, y + h], fill=(228, 234, 246), outline=NAVY)
        fx, fy = x + 10, y + 14
        d.rectangle([fx, fy, fx + 52, fy + 30], fill=NAVY)
        for k in range(8):
            ang = math.radians(k * 45)
            px = fx + 26 + 10 * math.cos(ang)
            py = fy + 15 + 8 * math.sin(ang)
            d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5],
                      fill=(255, 220, 0))
        ix = x + w - 62
        d.rectangle([ix, fy, ix + 52, fy + 15], fill=(200, 30, 30))
        d.rectangle([ix, fy + 15, ix + 52, fy + 30], fill=(255, 255, 255),
                    outline=(180, 180, 180))
        sx, sy = x + w // 2 - 34, y + h - 22
        d.polygon([(sx, sy), (sx + 68, sy), (sx + 58, sy + 12),
                   (sx + 10, sy + 12)], fill=(60, 60, 66))
        d.rectangle([sx + 14, sy - 12, sx + 30, sy], fill=(200, 30, 30))
        d.rectangle([sx + 34, sy - 12, sx + 50, sy], fill=NAVY)
        d.line([(x + 6, y + h - 6), (x + w - 6, y + h - 6)], fill=NAVY,
               width=2)
        self.text(x + 6, y + 3, "BRUSSELS · CEPA", sans(9, True), NAVY)
        self.text(x + 6, y + h - 16, "98.5% tariffs cut", sans(8), FG)

    # -- assembly ----------------------------------------------------------
    def render(self):
        self.masthead()
        after_timeline = self.timeline(92)
        after_big = self.big_stories(after_timeline)
        after_grid = self.grid(after_big)
        map_h = 148 if self.layout == "wide" else 104
        after_map = self.world_map(after_grid, map_h)
        after_list = self.also_list(after_map + 8)
        self.footer(after_list + 6)
        return self.img


# ----------------------------------------------------------------------
# The day's stories. Every entry: number, region/topic tag, headline,
# two-sentence summary, source. Researched the morning of 22 Nov 2026.
# ----------------------------------------------------------------------
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

DATE_CHECK = ("* The Bahrain strikes happened late Saturday night and were FIRST REPORTED across Asia on "
              "Sunday; the EU-Indonesia deal was SIGNED in Brussels on Saturday 21 Nov and leads here because "
              "Sunday's coverage across Asia was dominated by it; Estonia's border closure and Denmark's "
              "expulsion were announced Saturday and carried into Sunday. LEFT OUT ON PURPOSE: the magnitude 6.9 "
              "Peru earthquake (Friday 20 Nov local time) and the drone strike on the Russian cargo ship Sparta II "
              "in the Gulf of Finland (Saturday) — both predate Sunday. NOT YET: the COP31 final deal, the ATP "
              "Finals champion and the NFL Week 11 results are all due after this page was drawn.")

SOURCES_LINE = ("Sources: Reuters, AP, AFP, BBC, Al Jazeera, euronews, Fox News, Times of India, "
                "ANI, Jagran, BVM Sports, FSU Wire, ScoreZaap. Original drawings.")

# Pin positions for stories 1-16, as (longitude, latitude).
PINS = {1: (50.5, 26.2), 2: (24.0, 49.8), 3: (30.7, 36.9), 4: (4.4, 50.8),
        5: (174.8, -41.3), 6: (56.5, 26.5), 7: (-77.0, 38.9), 8: (24.7, 59.4),
        9: (-107.0, 24.8), 10: (-90.0, 38.6), 11: (-122.0, 37.0),
        12: (-118.0, 34.0), 13: (12.6, 55.7), 14: (114.2, 22.3),
        15: (77.2, 28.6), 16: (35.5, 33.3)}

# Dots for stories 17-50, as (longitude, latitude).
DOTS = [(-100, 13), (-62, -10), (30, 15), (-70, 10), (-95, 38), (-100, 35),
        (10, 59), (-2, 54), (-120, 35), (-74, 41), (12, 42), (-7, 34),
        (-122, 37), (-100, 20), (100, 5), (78, 21), (67, 30), (90, 24),
        (77, 28), (139, 35), (35, -1), (32, 15), (44, 33), (47, 32),
        (100, 13), (103, 1), (-43, -23), (151, -33), (18, 59), (-0, 51),
        (-55, -10), (120, -25), (55, 25), (-45, 60)]

# Simplified continent outlines, as lists of (longitude, latitude).
CONTINENTS = [
    [(-168, 66), (-135, 70), (-110, 71), (-90, 69), (-75, 60), (-60, 52),
     (-55, 46), (-68, 44), (-76, 36), (-81, 26), (-90, 21), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-145, 60)],
    [(-78, 8), (-62, 8), (-52, 4), (-44, -4), (-36, -10), (-40, -22),
     (-48, -28), (-58, -34), (-66, -40), (-70, -30), (-72, -18), (-78, -4)],
    [(-10, 36), (-2, 37), (3, 42), (8, 44), (12, 45), (20, 44), (28, 41),
     (30, 36), (23, 36), (15, 38), (8, 39), (0, 39), (-6, 36)],
    [(-6, 35), (10, 37), (20, 32), (32, 31), (35, 28), (43, 12), (51, 11),
     (48, 2), (40, -10), (35, -20), (28, -30), (20, -35), (15, -28),
     (12, -18), (9, 4), (0, 6), (-8, 5), (-16, 12)],
    [(60, 70), (75, 72), (95, 73), (115, 73), (135, 72), (155, 70),
     (170, 66), (162, 60), (158, 52), (142, 50), (135, 43), (127, 40),
     (122, 32), (115, 23), (108, 18), (100, 8), (97, 16), (90, 22),
     (85, 20), (80, 13), (76, 8), (72, 20), (66, 25), (60, 25), (55, 26)],
    [(113, -22), (122, -14), (132, -12), (142, -11), (146, -19), (150, -23),
     (153, -27), (150, -37), (140, -38), (130, -32), (120, -34), (114, -30)],
]


def render_poster(layout="classic", out="assets/entry.png"):
    page = FrontPage(layout)
    img = page.render()
    img.save(out, optimize=True)
    print(out, img.size)


if __name__ == "__main__":
    chosen = sys.argv[1] if len(sys.argv) > 1 else "classic"
    target = sys.argv[2] if len(sys.argv) > 2 else "assets/entry.png"
    render_poster(chosen, target)
