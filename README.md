# The World in One Day — Monday 23 November 2026

[![make.fun competition](https://make.fun/api/competitions/news-image-20261123/badge/competition.svg)](https://make.fun/bounty/news-image-20261123)
[![make.fun rank](https://make.fun/api/competitions/news-image-20261123/badge/rank.svg)](https://make.fun/bounty/news-image-20261123)
[![make.fun reward](https://make.fun/api/competitions/news-image-20261123/badge/reward.svg)](https://make.fun/bounty/news-image-20261123)

One image summing up the world's news of **Monday 23 November 2026**:
35 dated stories across 7 regions — the COP31 climate talks collapse in
Antalya after record overtime, Houthis strike Riyadh for a third straight
day, at least 25 tankers hit in and around the Strait of Hormuz, 186 drones
over Ukraine in one night, Nepal's PM meets Modi in Delhi, a candy-factory
fire in Indonesia leaves about 50 missing, BepiColombo enters Mercury orbit,
and Alcaraz wins his first ATP Finals title.

## Layout

- **Masthead** — "THE WORLD IN ONE DAY", Monday 23 November 2026
- **Hero** — COP31 collapses: no deal, with a flat storm-over-Antalya
  illustration and a NO DEAL banner
- **12 illustrated core cards** (stories 2–13) in a 4×3 grid, each with a
  region tag, a flat pictogram and a source line
- **Numbered-pin world map** (stories 1–10, 12, 13; story 11, Mercury, has
  no pin), plus a region count strip and a day timeline
- **22 more briefs** in two columns, each with a source

## How it is built

`compose.py` (Python 3, Pillow, standard library + Pillow only at build
time) draws `entry.png` (1024×1024, deterministic — same bytes every run).
`main.py`, the graded entrypoint, only copies that PNG to
`$MAKEFUN_OUTPUT_DIR/entry.png`, so the graded runs need no network and no
fonts. Every fact was checked against reporting first published on or before
23 November 2026 (CNN, AP, Reuters, BBC, The Times, Arab News, ATP, UPI and
others); where sources disagreed on a number the image prints the softened
form instead of false precision, and earlier-day stories are framed as
continuations.

## Run it

```sh
python3 compose.py            # redraw entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Entry

Built for the [make.fun bounty news-image-20261123](https://make.fun/bounty/news-image-20261123)
— "Sum up 23 November's world news in one image". $100 in prizes, judged
by an AI picture editor comparing images two at a time.
