#!/usr/bin/env python3
"""Generate a batch of strong self-play games to pick from.

Each game opens with a few random legal plies (variety), then the engine plays
both sides at high think time. Once a forced mate appears, think time drops to a
small value (the line is forced, so deep search there is wasted). Each game is
written to game-<N>.txt as a full ply-by-ply replay; a summary table is printed.

Usage: python3 batch_games.py [movetime_ms] [num_games]
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from transition_test import START_FEN  # noqa: E402
from watch_game import Watcher, hand_str, annotate  # noqa: E402

MATE_MT = 300   # think time once a mate is forced
CAP = 140
WINDOW = 40     # opening: randomize only among moves within this many cp of best


def opening_pick(eng, moves, k, mt, rng):
    """Pick a random opening move from those within WINDOW cp of best (a competitive,
    not blundering, randomization for variety). MultiPV gives per-move evals."""
    eng.send(f"setoption name MultiPV value {k}")
    eng.send(f"position fen {START_FEN}" + (" moves " + " ".join(moves) if moves else ""))
    eng.send(f"go movetime {mt}")
    pv, bm = {}, None
    while True:
        ln = eng.p.stdout.readline()
        if ln.startswith("bestmove"):
            bm = ln.split()[1]
            break
        if ln.startswith("info") and " multipv " in ln and " pv " in ln and " score " in ln:
            p = ln.split()
            si = p.index("score")
            n = int(p[si + 2])
            sc = (100000 - n if n > 0 else -100000 - n) if p[si + 1] == "mate" else n
            pv[int(p[p.index("multipv") + 1])] = (p[p.index("pv") + 1], sc)
    eng.send("setoption name MultiPV value 1")
    if not pv:
        return bm
    best = max(s for _, s in pv.values())
    cand = [mv for mv, s in pv.values() if best - s <= WINDOW]
    return rng.choice(cand) if cand else bm


def board_lines(ref):
    cells, h1, h2, _ = ref.split(";")
    L = [f"        black hand: {hand_str(h2)}"]
    for r in (4, 3, 2, 1):
        L.append(f"     {r}  " + "  ".join(cells[(r - 1) * 4 + c] for c in range(4)))
    L.append(f"        a  b  c  d        white hand: {hand_str(h1)}")
    return L


def play(eng, rng, mt, out):
    moves, n_open, in_mate, result = [], rng.randint(2, 4), False, "draw"
    print(f"=== Shogi4 self-play ({mt}ms/move, {n_open} competitive opening plies, "
          f"eval window {WINDOW}cp) ===\n", file=out)
    start_ref = eng.board([])
    seen = {start_ref: 1}
    for ln in board_lines(start_ref):
        print(ln, file=out)
    for ply in range(CAP):
        prev = eng.board(moves).split(";")[0]
        if ply < n_open:
            mv, score, depth = opening_pick(eng, moves, 6, 900, rng), "(opening)", 0
        else:
            mv, score, depth = eng.go(moves, MATE_MT if in_mate else mt)
            if score.startswith("#"):
                in_mate = True
        if mv in ("(none)", "0000", "none", ""):
            break
        mover = "White" if ply % 2 == 0 else "Black"
        tag = annotate(prev, mv)
        moves.append(mv)
        ref = eng.board(moves)
        print(f"\n--- ply {ply+1:>3}  {mover:5} {mv:7} eval {score:>6} (d{depth})"
              + (f"  [{tag}]" if tag else ""), file=out)
        for ln in board_lines(ref):
            print(ln, file=out)
        wk, bk = ref.split(";")[0].count("K"), ref.split(";")[0].count("k")
        if wk == 0 or bk == 0:
            result = "1-0" if bk == 0 else "0-1"
            print(f"\n=== {'WHITE' if bk==0 else 'BLACK'} WINS — king captured at ply {ply+1} ===", file=out)
            break
        seen[ref] = seen.get(ref, 0) + 1
        if seen[ref] >= 3:
            print(f"\n=== draw by threefold repetition at ply {ply+1} ===", file=out)
            break
    else:
        print("\n=== ply cap ===", file=out)
    return result, len(moves)


def main():
    mt = int(sys.argv[1]) if len(sys.argv) > 1 else 6000
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    eng = Watcher()
    print(f"batch: {n} games @ {mt}ms/move (drops to {MATE_MT}ms once mate is forced)\n")
    for g in range(1, n + 1):
        rng = random.Random(1000 + g)
        fn = os.path.join(HERE, f"game-{g}.txt")
        with open(fn, "w") as out:
            res, plies = play(eng, rng, mt, out)
        winner = {"1-0": "White", "0-1": "Black", "draw": "draw"}[res]
        print(f"  game {g}: {res:4} ({winner:5})  {plies:>3} plies  ->  game-{g}.txt", flush=True)
    eng.close()
    print("\nview one:  less engine/game-<N>.txt   (or: python3 watch_game.py to make a fresh one)")


if __name__ == "__main__":
    main()
