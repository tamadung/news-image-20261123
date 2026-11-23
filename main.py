#!/usr/bin/env python3
"""news-image-20261123 entrypoint: copy the pre-rendered front page to the
output directory. Deterministic by construction: the same bytes every run.

The image itself is drawn at build time by compose.py (Pillow, no network)
and ships in this repository as entry.png; this program only copies it to
$MAKEFUN_OUTPUT_DIR/entry.png (default: ./out/entry.png).
"""
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "entry.png")
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", os.path.join(BASE, "out"))
DEST = os.path.join(OUT, "entry.png")


def main():
    os.makedirs(OUT, exist_ok=True)
    shutil.copyfile(SRC, DEST)
    print("wrote %s (%d bytes)" % (DEST, os.path.getsize(DEST)))


if __name__ == "__main__":
    main()
