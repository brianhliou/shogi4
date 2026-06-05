#!/usr/bin/env python3
"""Guard the viewer's codec against the validated oracle.

engine/golden.txt holds 4,000 positions, each with its sorted legal-move list,
generated straight from the oracle (engine/gen_golden.py). For every line we:

  1. round-trip the position: encode_pos(decode_pos(enc)) == enc, and
  2. re-derive the legal moves through serve.decode_pos -> oracle.legal_moves and
     check the set equals the golden list.

If both hold over all 4,000 positions, the codec and /api wiring faithfully
reflect the oracle — no divergent third engine has crept into the viewer.

Run:  python3 explorer/test_codec.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "engine"))

from serve import decode_pos, encode_pos, BASE_LETTER  # noqa: E402
from shogi4 import legal_moves  # noqa: E402

GOLDEN = os.path.join(os.path.dirname(HERE), "engine", "golden.txt")


def golden_move(mv):
    """Oracle move -> golden.txt encoding (board '1122', drop 'P@23')."""
    if mv[0] == "m":
        _, s, d = mv
        return f"{s[0]}{s[1]}{d[0]}{d[1]}"
    _, animal, d = mv
    return f"{BASE_LETTER[animal]}@{d[0]}{d[1]}"


def main():
    with open(GOLDEN) as fh:
        lines = [ln.strip() for ln in fh if ln.strip()]

    rt_fail = mv_fail = 0
    for ln in lines:
        enc, want = ln.split(" ")
        # 1. round-trip
        if encode_pos(decode_pos(enc)) != enc:
            rt_fail += 1
            if rt_fail <= 3:
                print(f"  round-trip drift: {enc} -> {encode_pos(decode_pos(enc))}")
        # 2. move set matches the oracle's recorded set
        got = ",".join(sorted(golden_move(m) for m in legal_moves(decode_pos(enc))))
        if got != want:
            mv_fail += 1
            if mv_fail <= 3:
                print(f"  move-set drift @ {enc}\n    want {want}\n    got  {got}")

    n = len(lines)
    print(f"checked {n} golden positions: "
          f"round-trip {n - rt_fail}/{n} ok, move-set {n - mv_fail}/{n} ok")
    if rt_fail or mv_fail:
        print("FAIL")
        sys.exit(1)
    print("OK — codec agrees with the oracle on every golden position")


if __name__ == "__main__":
    main()
