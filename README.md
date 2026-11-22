[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# Sunday 22 November 2026 in one page

My entry for make.fun's **news-image-20261122** bounty ("Sum up 22
November's world news in one image", $100 shared by the top 50). One
dense newspaper front page, 1024×1024, with **50 sourced stories**
from Sunday 22 November 2026.

Bounty page: https://make.fun/bounty/news-image-20261122

## Inside the poster

- Masthead: "Sunday 22 November 2026", 50 stories, 6 continents.
- A UTC timeline of the day, 00:30–15:00.
- Four lead stories with original drawings: Iran's strikes on US
  bases in Bahrain, the Russian strike on Lviv, the COP31 deadlock in
  Antalya, and the EU–Indonesia trade deal signed in Brussels.
- Stories 5–16 in a numbered grid, each with a region/topic tag, a
  headline, a summary and its source.
- A world map with numbered pins for stories 1–16 and dots for 17–50.
- Stories 17–50 as a numbered list, one line each.
- A DATE CHECK box: which Saturday developments lead the page and why,
  what was left out on purpose (the Peru quake, the Sparta II strike),
  and what was not yet due (COP31 deal, ATP Finals, NFL Week 11).
- Sources: Reuters, AP, AFP, BBC, Al Jazeera, euronews, Fox News,
  Times of India, ANI, Jagran, BVM Sports, FSU Wire, ScoreZaap.
  Every picture is drawn by the program; there are no photos.

## Rebuilding it

```sh
python3 build_poster.py            # classic layout -> assets/entry.png
python3 build_poster.py wide variants/variant-wide.png
python3 main.py                    # copy assets/entry.png to /output/entry.png
```

`build_poster.py` needs Pillow and the system DejaVu fonts. The
classic layout was picked after comparing two layouts: the wide one
(2×2 lead stories) pushes the 17–50 list and the DATE CHECK off the
page, while the classic one fits everything inside 1024×1024.

`main.py` is standard-library only, makes no network calls, and writes
the same bytes on every run.

## Files

- `main.py` — entry point: checks the bundled PNG and copies it out.
- `build_poster.py` — the Pillow renderer (classic and wide layouts).
- `assets/entry.png` — the finished 1024×1024 poster (classic layout).
- `variants/` — the losing wide layout, for reference.
- `LICENSE` — MIT.
