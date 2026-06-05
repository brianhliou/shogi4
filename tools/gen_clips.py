#!/usr/bin/env python3
"""Generate explorer/clips.json — short, oracle-verified replay lines.

The viewer's "play through a recorded game" feature reads these. Two kinds of
clip are authored here:

  * scripted — an explicit list of move tokens (golden encoding: board "1314",
    drop "T@22"). Each token is matched against the oracle's legal moves, so an
    illegal script fails loudly with the legal options rather than silently
    producing a wrong board.
  * auto — a seeded oracle playout (deterministic), used for a sample game that
    runs to a natural end (a king capture).

Every step is rendered with serve.describe_move, so clips and live play share one
shape. Because the oracle drives both the legality check and the rendering, the
clips are correct by construction — they double as the canonical sequences the
mistboard rules article can cite.

Run:  python3 tools/gen_clips.py
"""
import json
import os
import random
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "explorer"))
sys.path.insert(0, os.path.join(ROOT, "engine"))

from serve import describe_move, encode_pos, decode_pos, INITIAL, ANIMAL  # noqa: E402
from shogi4 import start, legal_moves, make  # noqa: E402

OUT = os.path.join(ROOT, "explorer", "clips.json")

BOARD_TOK = re.compile(r"\A[1-4]{4}\Z")
DROP_TOK = re.compile(r"\A([PTRFG])@([1-4])([1-4])\Z")  # base letters P/T/R/F (G unused)


def match_move(pos, token):
    """Authored token -> the matching oracle Move (or raise with the options)."""
    moves = legal_moves(pos)
    if BOARD_TOK.match(token):
        src = (int(token[0]), int(token[1]))
        dst = (int(token[2]), int(token[3]))
        for mv in moves:
            if mv[0] == "m" and mv[1] == src and mv[2] == dst:
                return mv
    else:
        m = DROP_TOK.match(token)
        if m:
            animal = ANIMAL[m.group(1)]
            dst = (int(m.group(2)), int(m.group(3)))
            for mv in moves:
                if mv[0] == "d" and mv[1] == animal and mv[2] == dst:
                    return mv
    def tok(mv):
        if mv[0] == "m":
            _, s, d = mv
            return f"{s[0]}{s[1]}{d[0]}{d[1]}"
        from serve import BASE_LETTER
        _, a, d = mv
        return f"{BASE_LETTER[a]}@{d[0]}{d[1]}"
    opts = ", ".join(sorted(tok(mv) for mv in moves))
    raise SystemExit(f"illegal scripted move {token!r} at {encode_pos(pos)}\n  legal: {opts}")


def steps_from_tokens(tokens, start_enc=INITIAL):
    pos = decode_pos(start_enc)
    steps = []
    for tok in tokens:
        mv = match_move(pos, tok)
        steps.append(describe_move(pos, mv))
        pos, _ = make(pos, mv)
    return steps


def steps_auto(seed, max_plies=40):
    """Deterministic playout; takes a king capture as soon as one is available."""
    rng = random.Random(seed)
    pos = start()
    steps = []
    for _ in range(max_plies):
        moves = legal_moves(pos)
        if not moves:
            break
        winning = [m for m in moves if make(pos, m)[1]]
        mv = winning[0] if winning else rng.choice(moves)
        steps.append(describe_move(pos, mv))
        pos, kc = make(pos, mv)
        if kc:
            break
    return steps


# ---- authored clips ---------------------------------------------------------
# Tokens use the golden move encoding: board src+dst digits, drop "<base>@cr".
SCRIPTED = [
    {"id": "friendly-jump", "title": "Friendly jump",
     "desc": "A piece may leap one adjacent ally to the empty square two beyond — "
             "Shogi4's anti-congestion rule, which Dōbutsu has nothing like. Here "
             "each King jumps its own Carp.",
     "tokens": ["1113", "4442"]},
    {"id": "promotion", "title": "Far-rank promotion",
     "desc": "Carp, Tapir, Raccoon-dog and Fox evolve the instant they reach the "
             "opponent's last rank (royals never do). The Carp marches up and "
             "captures onto the back rank, evolving to a Koi.",
     "tokens": ["1213", "4342", "1314"]},
    {"id": "drops", "title": "Drops (last-rank ban)",
     "desc": "A captured piece flips side, reverts to its base form, and can be "
             "dropped back onto any empty square — except the opponent's last rank. "
             "After winning a Tapir to hand, it is dropped into the centre.",
     "tokens": ["1213", "4342", "1314", "4443", "T@22"]},
]
# ---- auto clip --------------------------------------------------------------
AUTO = {"id": "sample-game", "title": "Sample game",
        "desc": "A complete random-legal game played to its end — the only way to "
                "win is to capture the opposing royal (no checkmate, no Try).",
        "seed": 3, "max_plies": 60}


def main():
    clips = []
    for c in SCRIPTED:
        steps = steps_from_tokens(c["tokens"])
        clips.append({"id": c["id"], "title": c["title"], "desc": c["desc"],
                      "start": INITIAL, "steps": steps})
        print(f"  {c['id']:14} {len(steps)} plies")

    steps = steps_auto(AUTO["seed"], AUTO["max_plies"])
    ended = steps and steps[-1]["terminal"]
    clips.append({"id": AUTO["id"], "title": AUTO["title"], "desc": AUTO["desc"],
                  "start": INITIAL, "steps": steps})
    print(f"  {AUTO['id']:14} {len(steps)} plies "
          f"({'ends in king capture' if ended else 'unfinished'})")

    with open(OUT, "w") as fh:
        json.dump({"clips": clips}, fh, indent=1)
    print(f"wrote {len(clips)} clips -> {OUT}")


if __name__ == "__main__":
    main()
