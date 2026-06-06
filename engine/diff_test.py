#!/usr/bin/env python3
"""Differential move-gen test: patched Fairy-Stockfish vs the Python oracle.

Drives the friendlyJump-patched engine (engine/Fairy-Stockfish/src/stockfish) over
every position in golden.txt and asserts its legal-move set is IDENTICAL to the
oracle's (shogi4.py, a faithful port of the decompiled app). Also cross-checks
perft(1..N) from the start against shogi4.py at shallow depths (no king captures
occur shallow, so the oracle's "king-capture = leaf" semantics and FSF's pure
enumeration agree there).

Encoding bridge (reference -> Fairy-Stockfish):
  - board: oracle cells are r=1..4 outer, c=1..4 inner; FSF FEN lists rank4..rank1,
    files a..d. Promoted pieces O/B/N/G  <->  FSF +P/+T/+R/+F.
  - hands: 4 digits = carp,tapir,raccoon,fox -> letters P,T,R,F (White) / p,t,r,f (Black).
  - moves: oracle "csrc rsrc cdst rdst" / "<BASE>@cr"  <->  FSF "a1b2" / "P@b3" (+promo).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "Fairy-Stockfish", "src", "stockfish")
INI = os.path.join(HERE, "shogi4.ini")
GOLDEN = os.path.join(HERE, "golden.txt")

PROMO2FSF = {"O": "+P", "B": "+T", "N": "+R", "G": "+F",
             "o": "+p", "b": "+t", "n": "+r", "g": "+f"}
HAND_LETTER = ["P", "T", "R", "F"]  # carp, tapir, raccoon, fox (BASE order in shogi4.py)


def ref_to_fsf_fen(line_pos):
    cells, h1, h2, stm = line_pos.split(";")
    # board: emit rank 4 down to rank 1, files a..d
    ranks = []
    for r in (4, 3, 2, 1):
        run, out = 0, []
        for c in (1, 2, 3, 4):
            ch = cells[(r - 1) * 4 + (c - 1)]
            if ch == ".":
                run += 1
                continue
            if run:
                out.append(str(run)); run = 0
            out.append(PROMO2FSF.get(ch, ch))
        if run:
            out.append(str(run))
        ranks.append("".join(out))
    board = "/".join(ranks)
    hand = "".join(HAND_LETTER[i] * int(h1[i]) for i in range(4)) \
         + "".join(HAND_LETTER[i].lower() * int(h2[i]) for i in range(4))
    hand = hand or "-"
    side = "w" if stm == "1" else "b"
    return f"{board}[{hand}] {side} 0 1"


def fsf_move_to_ref(m):
    m = m.rstrip("+")  # strip mandatory-promotion suffix
    if "@" in m:
        letter, sq = m.split("@")
        c = ord(sq[0]) - ord("a") + 1
        return f"{letter.upper()}@{c}{sq[1]}"
    c1 = ord(m[0]) - ord("a") + 1
    c2 = ord(m[2]) - ord("a") + 1
    return f"{c1}{m[1]}{c2}{m[3]}"


class Engine:
    def __init__(self):
        self.p = subprocess.Popen([ENGINE], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  text=True, bufsize=1)
        self._cmd("uci", "uciok")
        self.send(f"setoption name VariantPath value {INI}")
        self.send("setoption name UCI_Variant value shogi4")
        self._cmd("isready", "readyok")

    def send(self, s):
        self.p.stdin.write(s + "\n"); self.p.stdin.flush()

    def _cmd(self, cmd, until):
        self.send(cmd)
        while True:
            if self.p.stdout.readline().startswith(until):
                return

    def perft1_moves(self, fen):
        self.send(f"position fen {fen}")
        self.send("go perft 1")
        moves = []
        while True:
            ln = self.p.stdout.readline()
            if ln.startswith("Nodes searched:"):
                return moves
            if ":" in ln and not ln.startswith("info"):
                tok = ln.split(":")[0].strip()
                if tok and tok[0].isalpha():
                    moves.append(tok)

    def perft(self, fen, depth):
        self.send(f"position fen {fen}")
        self.send(f"go perft {depth}")
        while True:
            ln = self.p.stdout.readline()
            if ln.startswith("Nodes searched:"):
                return int(ln.split(":")[1])

    def close(self):
        self.send("quit"); self.p.wait()


def main():
    eng = Engine()

    # 1) perft(1..6) from start vs the oracle.
    # Align terminal semantics: a king-capture move ends the game (the oracle's own
    # perft counts it as a leaf at any depth; FSF treats the post-capture position as
    # terminal with no children). With that convention the two enumerators agree to
    # the node -- the earlier raw-perft gap was only this definitional difference.
    sys.path.insert(0, HERE)
    from shogi4 import start, legal_moves, make  # noqa: E402

    def ref_perft(pos, depth):
        if depth == 0:
            return 1
        n = 0
        for mv in legal_moves(pos):
            child, kc = make(pos, mv)
            n += (1 if depth == 1 else 0) if kc else ref_perft(child, depth - 1)
        return n

    start_fen = "trfk/3p/P3/KFRT[-] w 0 1"
    print("=== perft from start: FSF vs oracle (aligned terminal semantics) ===")
    ok = True
    for d in range(1, 7):
        f, r = eng.perft(start_fen, d), ref_perft(start(), d)
        flag = "OK" if f == r else "*** MISMATCH ***"
        ok &= f == r
        print(f"  perft({d}): FSF={f:>9,}  oracle={r:>9,}  {flag}")

    # 2) move-set diff over every golden position
    print("\n=== move-set diff over golden.txt ===")
    n, bad = 0, 0
    with open(GOLDEN) as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            pos, moves = raw.split(" ", 1)
            want = set(moves.split(","))
            fen = ref_to_fsf_fen(pos)
            got = set(fsf_move_to_ref(m) for m in eng.perft1_moves(fen))
            n += 1
            if got != want:
                bad += 1
                if bad <= 8:
                    print(f"  MISMATCH @ {pos}\n    fen={fen}\n"
                          f"    only-oracle: {sorted(want - got)}\n"
                          f"    only-FSF:    {sorted(got - want)}")
    print(f"\n  checked {n:,} positions, {bad} mismatches")
    eng.close()
    sys.exit(0 if ok and bad == 0 else 1)


if __name__ == "__main__":
    main()
