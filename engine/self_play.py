#!/usr/bin/env python3
"""Generate a corpus of sampled Shogi4 games via patched-FSF self-play.

Each game opens with a few random legal plies (for variety), then the engine plays
both sides at a fixed think time until a king is captured or a ply cap is hit.
Output: one game per line -> "<result> <ply-count> <space-separated UCI moves>",
result in {1-0, 0-1, draw}. 1-0 = White (Player 1) wins.

Usage: python3 self_play.py [num_games] [out_file] [movetime_ms]
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from transition_test import E2, START_FEN  # noqa: E402

PLY_CAP = 200


class Player(E2):
    def legal(self, moves):
        self.send(f"position fen {START_FEN}" + (" moves " + " ".join(moves) if moves else ""))
        self.send("go perft 1")
        out = []
        while True:
            ln = self.p.stdout.readline()
            if ln.startswith("Nodes searched:"):
                return out
            if ":" in ln and ln[0].isalpha():
                tok = ln.split(":")[0].strip()
                if tok and (tok[0].isalpha()):
                    out.append(tok)

    def bestmove(self, moves, movetime):
        self.send(f"position fen {START_FEN}" + (" moves " + " ".join(moves) if moves else ""))
        self.send(f"go movetime {movetime}")
        while True:
            ln = self.p.stdout.readline()
            if ln.startswith("bestmove"):
                return ln.split()[1]

    def kings(self, moves):
        # `d` prints Fen/Sfen/Key/Checkers/Chased; drain the whole block via an
        # isready handshake so trailing lines don't pollute the next command's parse.
        self.send(f"position fen {START_FEN}" + (" moves " + " ".join(moves) if moves else ""))
        self.send("d")
        self.send("isready")
        fen = ""
        while True:
            ln = self.p.stdout.readline()
            if ln.startswith("Fen:"):
                fen = ln.split("Fen:")[1].strip()
            if ln.startswith("readyok"):
                b = fen.split("[")[0]
                return b.count("K"), b.count("k")


def play_game(eng, rng, movetime):
    moves = []
    n_open = rng.randint(2, 8)
    for ply in range(PLY_CAP):
        if ply < n_open:
            legal = eng.legal(moves)
            if not legal:
                break
            mv = rng.choice(legal)
        else:
            mv = eng.bestmove(moves, movetime)
            if mv in ("(none)", "0000", "none", ""):
                break
        moves.append(mv)
        wk, bk = eng.kings(moves)
        if wk == 0:
            return "0-1", moves
        if bk == 0:
            return "1-0", moves
    return "draw", moves


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "games.txt")
    movetime = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    rng = random.Random(20260605)
    eng = Player()
    res = {"1-0": 0, "0-1": 0, "draw": 0}
    with open(out, "w") as fh:
        for g in range(n):
            r, moves = play_game(eng, rng, movetime)
            res[r] += 1
            fh.write(f"{r} {len(moves)} {' '.join(moves)}\n")
            fh.flush()
            print(f"  game {g+1:>3}: {r:>4}  {len(moves):>3} plies")
    eng.close()
    print(f"\nwrote {n} games to {out}")
    print(f"results: White(P1) {res['1-0']}  Black(P2) {res['0-1']}  draw {res['draw']}")


if __name__ == "__main__":
    main()
