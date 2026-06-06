#!/usr/bin/env python3
"""Replay the oracle's move sequences in FSF and compare the RESULTING position.
Move sets already match everywhere (find_divergence), so any perft gap must be a
do_move/make discrepancy: FSF applies some move to a different result. This finds
the first such move."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shogi4 import start, legal_moves, make, P1, BASE  # noqa: E402
from gen_golden import encode_pos  # noqa: E402
from diff_test import Engine, PROMO2FSF  # noqa: E402

START_FEN = "trfk/3p/P3/KFRT[-] w 0 1"
FSF2PROMO = {v: k for k, v in PROMO2FSF.items()}  # "+P"->"O", etc.


def oracle_move_to_fsf(pos, mv):
    if mv[0] == "d":
        _, animal, d = mv
        letter = {"carp": "P", "tapir": "T", "raccoon": "R", "fox": "F"}[animal]
        return f"{letter}@{chr(96 + d[0])}{d[1]}"  # UCI drops use the uppercase piece letter
    _, s, d = mv
    promo = ""
    owner, animal = pos.board[s]
    last = 4 if owner == P1 else 1
    if animal in BASE and d[1] == last:
        promo = "+"
    return f"{chr(96 + s[0])}{s[1]}{chr(96 + d[0])}{d[1]}{promo}"


def fsf_fen_to_ref(fen):
    """FSF 'board[hand] stm ...' -> oracle '16cells;h1;h2;stm'."""
    board, rest = fen.split("[", 1)
    hand, after = rest.split("]", 1)
    stm = after.split()[0]
    # board: ranks 4..1 -> oracle cells r=1..4 outer, c=1..4 inner
    rows = board.split("/")  # rows[0]=rank4 ... rows[3]=rank1
    cells = [["."] * 4 for _ in range(4)]  # cells[r-1][c-1]
    for ri, row in enumerate(rows):
        r = 4 - ri
        c = 1
        i = 0
        while i < len(row):
            ch = row[i]
            if ch.isdigit():
                c += int(ch); i += 1; continue
            if ch == "+":
                tok = FSF2PROMO[row[i:i + 2]]; i += 2
            else:
                tok = ch; i += 1
            cells[r - 1][c - 1] = tok
            c += 1
    flat = "".join(cells[r][c] for r in range(4) for c in range(4))
    order = ["P", "T", "R", "F"]
    h1 = "".join(str(hand.count(x)) for x in order)
    h2 = "".join(str(hand.count(x.lower())) for x in order)
    s = "1" if stm == "w" else "2"
    return f"{flat};{h1};{h2};{s}"


class E2(Engine):
    def fen_after(self, moves):
        self.send(f"position fen {START_FEN}" + (" moves " + " ".join(moves) if moves else ""))
        self.send("d")
        while True:
            ln = self.p.stdout.readline()
            if ln.startswith("Fen:"):
                return ln.split("Fen:")[1].strip()


seen = set()


def visit(pos, fsf_moves, depth):
    want = encode_pos(pos)
    got = fsf_fen_to_ref(eng.fen_after(fsf_moves))
    if want != got:
        print("FIRST TRANSITION DIVERGENCE")
        print("  fsf moves :", " ".join(fsf_moves))
        print("  oracle pos:", want)
        print("  FSF    pos:", got)
        eng.close(); sys.exit(0)
    if depth == 0:
        return
    for m in legal_moves(pos):
        child, kc = make(pos, m)
        if kc:
            continue
        k = child.key()
        if k in seen:
            continue
        seen.add(k)
        visit(child, fsf_moves + [oracle_move_to_fsf(pos, m)], depth - 1)


if __name__ == "__main__":
    eng = E2()
    visit(start(), [], 4)
    print("no transition divergence within depth 4")
    eng.close()
