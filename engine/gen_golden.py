#!/usr/bin/env python3
"""Generate a golden position->moves file from the Python oracle (shogi4.py).

Random playouts from the start sample varied positions (captures, drops in hand,
promotions, friendly-jumps); each distinct position is written with its sorted
legal-move list. The Rust engine reads this file and asserts identical move sets,
giving cross-language move-gen agreement on arbitrary positions (beyond perft).

Encoding (must match solver/src/lib.rs):
  <16 cells, r=1..4 outer, c=1..4 inner>;<P1 hand carp,tapir,raccoon,fox>;<P2 hand>;<stm 1|2>
  cell: '.' empty, else animal letter (UPPER=P1, lower=P2):
        K king, P carp, T tapir, R raccoon, F fox, O koi, B baku, N tanuki, G kitsune
  move: board "csrc rsrc cdst rdst" as 4 digits (e.g. 1122); drop "<base>@cr" (e.g. P@23)
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shogi4 import P1, BASE, start, legal_moves, make  # noqa: E402

LETTER = {"king": "K", "carp": "P", "tapir": "T", "raccoon": "R", "fox": "F",
          "koi": "O", "baku": "B", "tanuki": "N", "kitsune": "G"}
BASE_LETTER = {"carp": "P", "tapir": "T", "raccoon": "R", "fox": "F"}


def encode_pos(pos):
    cells = []
    for r in (1, 2, 3, 4):
        for c in (1, 2, 3, 4):
            p = pos.board.get((c, r))
            if p is None:
                cells.append(".")
            else:
                o, a = p
                cells.append(LETTER[a] if o == P1 else LETTER[a].lower())

    def hand(o):
        return "".join(str(pos.hands[o].get(t, 0)) for t in BASE)

    return f"{''.join(cells)};{hand(P1)};{hand('player_2')};{1 if pos.stm == P1 else 2}"


def encode_move(mv):
    if mv[0] == "m":
        _, s, d = mv
        return f"{s[0]}{s[1]}{d[0]}{d[1]}"
    _, a, d = mv
    return f"{BASE_LETTER[a]}@{d[0]}{d[1]}"


def main():
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "golden.txt")
    random.seed(12345)
    seen, lines = set(), []
    while len(lines) < target:
        pos = start()
        for _ in range(random.randint(0, 40)):
            mvs = legal_moves(pos)
            if not mvs:
                break
            k = pos.key()
            if k not in seen:
                seen.add(k)
                enc = encode_pos(pos) + " " + ",".join(sorted(encode_move(m) for m in mvs))
                lines.append(enc)
                if len(lines) >= target:
                    break
            pos, king_captured = make(pos, random.choice(mvs))
            if king_captured:
                break
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} golden positions to {out}")


if __name__ == "__main__":
    main()
