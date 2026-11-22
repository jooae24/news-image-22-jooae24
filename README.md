[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# news-image-20261122 — The World in One Page

Entry for the make.fun bounty **news-image-20261122**: "Sum up 22 November's
world news in one image" ($100, top 50). A dense newspaper front page,
1024×1024, summarising Sunday 22 November 2026 in **50 sourced stories**.

See the bounty page: https://make.fun/bounty/news-image-20261122

## What's on the poster

- **Masthead** — "Sunday 22 November 2026", 50 stories, 6 continents.
- **The Day in UTC** — six timeline entries, 00:30–15:00 UTC.
- **4 big stories, each with an original programmatic illustration:**
  1. Iran hits US bases in Bahrain with drones and missiles (radar under attack)
  2. Russian strike on Lviv kills two, injures ten (building hit)
  3. COP31 talks deadlocked into Sunday (globe + stalled clock)
  4. EU and Indonesia sign a landmark trade deal (flags + cargo ship)
- **Grid 5–16** — numbered stories with region/topic tag, headline, summary
  and a source per story (Pant's record century, Hormuz tankers, Trump's
  Iran deal, Estonia's border closure, Mexico cartel arrest, Roundup
  settlement, FBI hack probe, Palisades fire, Denmark's Russia plot claim,
  Hong Kong voting, Japan–India training, UNIFIL/Lebanon).
- **"Where It Happened" world map** — pins numbered 1–16, dots for stories 17–50.
- **"Also on Sunday 22 November, 17–50"** — one line per story (Melania Trump,
  Hegseth, Thanksgiving terror warning, Modi, Cyclone Akvan, Bolsonaro, UFO
  footage, Zverev, Real Madrid, and 25 more).
- **Date Check footer** — the Bahrain strikes happened late Saturday night and
  were first reported across Asia on Sunday; the EU–Indonesia deal was signed
  Saturday 21 Nov and leads here because Sunday's coverage across Asia was
  dominated by it; the Peru earthquake and the Sparta II drone strike are
  left out on purpose because they predate Sunday; the COP31 final deal, the
  ATP Finals champion and the NFL Week 11 results are not yet due.
- **Sources line** — Reuters, AP, AFP, BBC, Al Jazeera, euronews, Fox News,
  Times of India, ANI, Jagran, BVM Sports, FSU Wire, ScoreZaap.
  All drawings are original; no photos.

## Build the poster

```sh
python3 build_poster.py        # renders assets/entry.png (variant A)
python3 build_poster.py b variants/variant-b.png   # alternate layout
python3 build_poster.py c variants/variant-c.png   # alternate layout
```

`build_poster.py` needs Pillow only; fonts are the system DejaVu fonts.
Variant A (classic 4-across front page) was chosen after a self-evaluation
of three variants: B (big stories 2×2) and C (taller big stories, 3-column
grid/list) both pushed the 17–50 list and the Date Check footer off the
1024×1024 page, while A fits all 50 stories, the map, the Date Check and
the sources line inside the frame with no text overflowing its box.

## Run the entry

```sh
python3 main.py        # verifies assets/entry.png is a 1024×1024 PNG
                       # and copies it to /output/entry.png
```

`main.py` uses only the Python standard library, makes no network calls,
and is deterministic: repeated runs copy the same bytes.

## Files

- `main.py` — stdlib-only entry point (copy + verify).
- `build_poster.py` — Pillow renderer for the poster (variants a/b/c).
- `assets/entry.png` — the finished 1024×1024 poster (variant A).
- `variants/` — the two losing layout variants, for reference.
- `LICENSE` — MIT. `README.md` — this file.
