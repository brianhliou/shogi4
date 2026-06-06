#!/usr/bin/env python3
"""Walk the oracle's move tree from the start; report the FIRST position whose
FSF legal-move set differs from the oracle's. Pinpoints the rule mismatch behind
the perft divergence."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shogi4 import start, legal_moves, make, P1  # noqa: E402
from gen_golden import encode_pos, encode_move  # noqa: E402
from diff_test import Engine, ref_to_fsf_fen, fsf_move_to_ref  # noqa: E402

eng = Engine()
seen = set()


def visit(pos, depth, path):
    want = set(encode_move(m) for m in legal_moves(pos))
    enc = encode_pos(pos)
    got = set(fsf_move_to_ref(m) for m in eng.perft1_moves(ref_to_fsf_fen(enc)))
    if want != got:
        print("FIRST DIVERGENCE")
        print("  path:", " ".join(path))
        print("  pos :", enc)
        print("  fen :", ref_to_fsf_fen(enc))
        print("  only-oracle:", sorted(want - got))
        print("  only-FSF   :", sorted(got - want))
        eng.close()
        sys.exit(0)
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
        visit(child, depth - 1, path + [encode_move(m)])


visit(start(), 4, [])
print("no divergence within depth 4")
eng.close()
