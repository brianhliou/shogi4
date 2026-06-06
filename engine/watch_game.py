#!/usr/bin/env python3
"""Watch the patched engine play itself, rendered ply-by-ply (board + move + eval).

Best-vs-best from the start by default; pass an opening-randomization count for
variety. Eval is shown from the mover's perspective (+ = the side that just moved
is better); cp/100 as pawns, or #N for mate-in-N.

Usage: python3 watch_game.py [movetime_ms] [random_open_plies] [ply_cap]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from transition_test import E2, START_FEN, fsf_fen_to_ref  # noqa: E402

HAND = ["P", "T", "R", "F"]  # carp, tapir, raccoon, fox


class Watcher(E2):
    def go(self, moves, movetime):
        self.send(f"position fen {START_FEN}" + (" moves " + " ".join(moves) if moves else ""))
        self.send(f"go movetime {movetime}")
        score, depth = "?", 0
        while True:
            ln = self.p.stdout.readline()
            if ln.startswith("info") and " score " in ln and " pv " in ln:
                p = ln.split()
                depth = int(p[p.index("depth") + 1])
                i = p.index("score")
                score = (f"{int(p[i+2])/100:+.2f}" if p[i+1] == "cp"
                         else f"#{int(p[i+2]):+d}".replace("+", "+").replace("#+", "#"))
            if ln.startswith("bestmove"):
                return ln.split()[1], score, depth

    def board(self, moves):
        self.send(f"position fen {START_FEN}" + (" moves " + " ".join(moves) if moves else ""))
        self.send("d"); self.send("isready")
        fen = ""
        while True:
            ln = self.p.stdout.readline()
            if ln.startswith("Fen:"):
                fen = ln.split("Fen:")[1].strip()
            if ln.startswith("readyok"):
                return fsf_fen_to_ref(fen)


def hand_str(h):
    parts = [f"{HAND[i]}x{h[i]}" for i in range(4) if int(h[i]) > 0]
    return " ".join(parts) if parts else "-"


def show(ref, last_dst=None):
    cells, h1, h2, _ = ref.split(";")
    print(f"        black hand: {hand_str(h2)}")
    for r in (4, 3, 2, 1):
        row = "  ".join(cells[(r - 1) * 4 + c] for c in range(4))
        print(f"     {r}  {row}")
    print(f"        a  b  c  d        white hand: {hand_str(h1)}")


def annotate(prev_cells, mv):
    if "@" in mv:
        return "drop"
    tags = []
    if mv.endswith("+"):
        tags.append("promo")
    dst = mv.rstrip("+")[2:4]
    c = ord(dst[0]) - ord("a") + 1
    r = int(dst[1])
    if prev_cells[(r - 1) * 4 + (c - 1)] != ".":
        tags.append("CAPTURE")
    return " ".join(tags) if tags else ""


def main():
    movetime = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    rnd = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 120

    eng = Watcher()
    import random
    rng = random.Random(7)
    moves = []
    print(f"=== Shogi4 self-play  (movetime {movetime}ms/move)  UPPER=White/P1 ===\n")
    show(eng.board([]))
    for ply in range(cap):
        prev = eng.board(moves).split(";")[0]
        if ply < rnd:
            self_legal = eng.legal_moves_at(moves) if hasattr(eng, "legal_moves_at") else None
            # simple random opening via perft list
            eng.send(f"position fen {START_FEN}" + (" moves " + " ".join(moves) if moves else ""))
            eng.send("go perft 1")
            lm = []
            while True:
                ln = eng.p.stdout.readline()
                if ln.startswith("Nodes searched:"):
                    break
                if ":" in ln and ln[0].isalpha():
                    lm.append(ln.split(":")[0].strip())
            mv, score, depth = rng.choice(lm), "(book)", 0
        else:
            mv, score, depth = eng.go(moves, movetime)
        if mv in ("(none)", "0000", "none", ""):
            print("\n(no legal move)"); break
        mover = "White" if ply % 2 == 0 else "Black"
        tag = annotate(prev, mv)
        moves.append(mv)
        ref = eng.board(moves)
        print(f"\n--- ply {ply+1:>3}  {mover:5} {mv:7} eval {score:>6} (d{depth})"
              + (f"  [{tag}]" if tag else ""))
        show(ref)
        wk, bk = ref.split(";")[0].count("K"), ref.split(";")[0].count("k")
        if wk == 0 or bk == 0:
            print(f"\n=== {'BLACK' if wk==0 else 'WHITE'} WINS — king captured at ply {ply+1} ===")
            break
    else:
        print("\n=== reached ply cap (likely a draw by repetition under best play) ===")
    eng.close()


if __name__ == "__main__":
    main()
