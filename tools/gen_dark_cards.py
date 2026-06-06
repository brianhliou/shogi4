#!/usr/bin/env python3
"""Make a slightly-darker-card variant of each piece for one side.

Goal: darken only the tile's CARD background — the main card AND the bottom "floor"
strip — leaving the animal and the paw move-marks at full colour. Colour alone
can't do it (the card and the animals' white parts overlap, and base vs evolved
tiles use inverted schemes: cream card + tan paws vs pink card + white paws), so
we separate by REGION and adapt to each tile's own palette:

  1. read the background palette from the tile border (the 1-2 colours that make
     up most of the perimeter = the card and the floor strip);
  2. flood-fill inward from the border through pixels close to that palette,
     darkening as we go. The paws (a contrasting colour) and the animal (its
     outline + saturated body) are walls, so the fill wraps around the paws and
     never enters the animal.

Writes explorer/pieces/dark/<name>.png — the second player uses these; the first
player keeps the originals. Run:  python3 tools/gen_dark_cards.py
"""
import os
from collections import deque, Counter
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "explorer", "pieces")
DST = os.path.join(SRC, "dark")
FACTOR = 0.88        # "slightly darker"
TOL = 42             # how close to a background colour a pixel must be to count
NAMES = ["crane", "pheasant", "carp", "tapir", "raccoon", "fox",
         "koi", "baku", "tanuki", "kitsune"]


def process(name):
    im = Image.open(os.path.join(SRC, f"{name}.png")).convert("RGBA")
    px = im.load()
    w, h = im.size

    # 1. background palette = colours that dominate the border perimeter
    border = []
    for x in range(w):
        border += [px[x, 0], px[x, h - 1]]
    for y in range(h):
        border += [px[0, y], px[w - 1, y]]
    cnt = Counter((r // 8 * 8, g // 8 * 8, b // 8 * 8) for r, g, b, a in border if a > 8)
    thresh = 0.06 * sum(cnt.values())
    bg = [c for c, n in cnt.items() if n >= thresh]

    def is_bg(p):
        r, g, b, a = p
        if a < 8:
            return False
        return any(abs(r - c[0]) + abs(g - c[1]) + abs(b - c[2]) < TOL for c in bg)

    # 2. flood-fill from the border, darkening card/floor, walling off paws+animal
    seen = bytearray(w * h)
    dq = deque()

    def seed(x, y):
        i = y * w + x
        if not seen[i] and is_bg(px[x, y]):
            seen[i] = 1
            dq.append((x, y))

    for x in range(w):
        seed(x, 0); seed(x, h - 1)
    for y in range(h):
        seed(0, y); seed(w - 1, y)

    n = 0
    while dq:
        x, y = dq.popleft()
        r, g, b, a = px[x, y]
        px[x, y] = (round(r * FACTOR), round(g * FACTOR), round(b * FACTOR), a)
        n += 1
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h:
                i = ny * w + nx
                if not seen[i] and is_bg(px[nx, ny]):
                    seen[i] = 1
                    dq.append((nx, ny))

    os.makedirs(DST, exist_ok=True)
    im.save(os.path.join(DST, f"{name}.png"))
    print(f"  {name:9} bg palette {bg}  -> darkened {n} px")


def main():
    for name in NAMES:
        process(name)


if __name__ == "__main__":
    main()
