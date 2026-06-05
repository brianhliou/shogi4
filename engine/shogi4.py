#!/usr/bin/env python3
"""Shogi4 reference engine + perft + tiny-subgame retrograde solver.

This is the ORACLE-side implementation. The move generation is a faithful port of
the decompiled official app (see research/prior-art-evidence/oca-shogi4-logic-
decompiled.py: get_possible_squares / can_take_square / fake_take_square / capture).
The Rust engine (next milestone) will be differential-tested against this; perft
numbers here are the spec it must reproduce to the digit.

Rules (research/findings.md):
- 4x4 board, code = (col, row), col,row in 1..4. "Forward" = +row for player_1,
  -row for player_2.
- Pieces: king (Crane/Pheasant) + capturable carp/tapir/raccoon/fox, each promoting
  to koi/baku/tanuki/kitsune on reaching the opponent's last rank.
- Every piece moves ONE step in marked directions. Per-piece direction sets
  (consolidated from the decompiled blocks; "forward" sense, dcol is column-symmetric):
    king    : all 8
    fox     : 4 orthogonal               (Wazir)
    raccoon : 4 diagonal                 (Ferz)
    carp    : forward                    (pawn)
    tapir   : forward + 2 forward-diag    {N,NE,NW}
    koi/baku/tanuki : forward + 4 diag    (Silver)  {N,NE,NW,SE,SW}
    kitsune : forward + 2 fwd-diag + L,R + back  (Gold) {N,NE,NW,E,W,S}
- FRIENDLY-JUMP: for any move direction, if an allied piece sits on the adjacent
  square, you may instead land two squares out in that same direction (one ally,
  no enemy-jumps; landing must be empty or an enemy).
- Drops: to any empty square except the opponent's last rank. Captured pieces flip
  side and demote to base.
- Win: capture the King (no checkmate / no check rule; moving into check is legal).
- Repetition: our convention -> draw (handled by the retrograde fixpoint:
  anything not provably Win or Loss is a Draw).
"""
from collections import deque

P1, P2 = "player_1", "player_2"
BASE = ("carp", "tapir", "raccoon", "fox")
PROMO = {"carp": "koi", "tapir": "baku", "raccoon": "tanuki", "fox": "kitsune"}
DEMOTE = {v: k for k, v in PROMO.items()}

# direction sets in (dcol, drow_forward); drow_forward is the player's forward sense
DIRS = {
    "king":    [(-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (1, 1), (-1, -1), (1, -1)],
    "fox":     [(-1, 0), (1, 0), (0, 1), (0, -1)],
    "raccoon": [(-1, 1), (1, 1), (-1, -1), (1, -1)],
    "carp":    [(0, 1)],
    "tapir":   [(0, 1), (-1, 1), (1, 1)],
    "koi":     [(0, 1), (-1, 1), (1, 1), (-1, -1), (1, -1)],
    "baku":    [(0, 1), (-1, 1), (1, 1), (-1, -1), (1, -1)],
    "tanuki":  [(0, 1), (-1, 1), (1, 1), (-1, -1), (1, -1)],
    "kitsune": [(0, 1), (-1, 1), (1, 1), (-1, 0), (1, 0), (0, -1)],
}
SQUARES = [(c, r) for c in (1, 2, 3, 4) for r in (1, 2, 3, 4)]


def opp(p):
    return P2 if p == P1 else P1


def on_board(c):
    return 1 <= c[0] <= 4 and 1 <= c[1] <= 4


class Position:
    __slots__ = ("board", "hands", "stm")

    def __init__(self, board, hands, stm):
        self.board = board          # {(col,row): (owner, animal)}
        self.hands = hands          # {P1: {animal: n}, P2: {...}}; hand pieces are base
        self.stm = stm

    def key(self):
        b = tuple(sorted((c, r, o, a) for (c, r), (o, a) in self.board.items()))
        h = (tuple(sorted((k, v) for k, v in self.hands[P1].items() if v > 0)),
             tuple(sorted((k, v) for k, v in self.hands[P2].items() if v > 0)))
        return (b, h, self.stm)


def dests(board, sq, owner, animal):
    """Faithful port of get_possible_squares for one on-board piece."""
    col, row = sq
    fwd = 1 if owner == P1 else -1
    out = []
    for dc, drf in DIRS[animal]:
        dr = drf * fwd
        step = (col + dc, row + dr)
        if not on_board(step):
            continue
        out.append(step)                       # base step (legality filtered by caller)
        occ = board.get(step)
        if occ is not None and occ[0] == owner:  # allied -> may leap it
            jump = (col + 2 * dc, row + 2 * dr)
            if on_board(jump):
                out.append(jump)
    return out


def legal_moves(pos):
    me, board = pos.stm, pos.board
    moves = []
    for sq, (owner, animal) in board.items():
        if owner != me:
            continue
        for d in dests(board, sq, owner, animal):
            occ = board.get(d)
            if occ is not None and occ[0] == me:
                continue                        # cannot land on an allied piece
            moves.append(("m", sq, d))
    last_rank = 4 if me == P1 else 1
    for animal, cnt in pos.hands[me].items():
        if cnt <= 0:
            continue
        for d in SQUARES:
            if d[1] == last_rank or d in board:
                continue                        # drops: empty, not the opp last rank
            moves.append(("d", animal, d))
    return moves


def make(pos, mv):
    """Returns (child, king_captured). If king_captured, child is terminal."""
    board = dict(pos.board)
    hands = {P1: dict(pos.hands[P1]), P2: dict(pos.hands[P2])}
    me = pos.stm
    king_captured = False
    if mv[0] == "m":
        _, src, dst = mv
        owner, animal = board.pop(src)
        occ = board.get(dst)
        if occ is not None:
            if occ[1] == "king":
                king_captured = True
            else:
                base = DEMOTE.get(occ[1], occ[1])
                hands[me][base] = hands[me].get(base, 0) + 1
        last_rank = 4 if me == P1 else 1
        if animal in BASE and dst[1] == last_rank:   # mandatory promotion
            animal = PROMO[animal]
        board[dst] = (owner, animal)
    else:
        _, animal, dst = mv
        hands[me][animal] -= 1
        board[dst] = (me, animal)
    return Position(board, hands, opp(me)), king_captured


def perft(pos, depth):
    """Leaf count to `depth`. A king-capture ends the game -> counted as a leaf there."""
    if depth == 0:
        return 1
    n = 0
    for mv in legal_moves(pos):
        child, kc = make(pos, mv)
        n += 1 if kc else perft(child, depth - 1)
    return n


def start():
    b = {
        (1, 1): (P1, "king"), (2, 1): (P1, "fox"), (3, 1): (P1, "raccoon"),
        (4, 1): (P1, "tapir"), (1, 2): (P1, "carp"),
        (4, 4): (P2, "king"), (3, 4): (P2, "fox"), (2, 4): (P2, "raccoon"),
        (1, 4): (P2, "tapir"), (4, 3): (P2, "carp"),
    }
    return Position(b, {P1: {}, P2: {}}, P1)


# ----------------------------- tiny-subgame solver -----------------------------

def _place(types, board, hands):
    """Yield all distributions of the remaining capturable `types`."""
    if not types:
        for stm in (P1, P2):
            yield Position(dict(board), {P1: dict(hands[P1]), P2: dict(hands[P2])}, stm)
        return
    t, rest = types[0], types[1:]
    for owner in (P1, P2):                       # option: in a hand (base)
        h = {P1: dict(hands[P1]), P2: dict(hands[P2])}
        h[owner][t] = h[owner].get(t, 0) + 1
        yield from _place(rest, board, h)
    for sq in SQUARES:                           # option: on the board
        if sq in board:
            continue
        for owner in (P1, P2):
            for face in (t, PROMO[t]):
                if face == t and sq[1] == (4 if owner == P1 else 1):
                    continue                     # a base piece can't sit on its promo rank
                b = dict(board); b[sq] = (owner, face)
                yield from _place(rest, b, hands)


def enumerate_positions(extra_types):
    for kc1 in SQUARES:
        for kc2 in SQUARES:
            if kc1 == kc2:
                continue
            base = {kc1: (P1, "king"), kc2: (P2, "king")}
            yield from _place(list(extra_types), base, {P1: {}, P2: {}})


def build_graph(extra_types):
    """Enumerate the closed subgame {2 kings + extra_types} and build its move graph."""
    index, nodes = {}, []
    for p in enumerate_positions(extra_types):
        k = p.key()
        if k not in index:
            index[k] = len(nodes); nodes.append(p)
    n = len(nodes)
    children = [[] for _ in range(n)]
    imm_win = [False] * n
    has_move = [False] * n
    edges = 0
    for i, p in enumerate(nodes):
        for mv in legal_moves(p):
            has_move[i] = True; edges += 1
            child, kc = make(p, mv)
            if kc:
                imm_win[i] = True                # king-capture: terminal win for stm
            else:
                children[i].append(index[child.key()])   # closed: child is in the set
    return {"n": n, "children": children, "imm_win": imm_win,
            "has_move": has_move, "edges": edges}


def label_retro(g):
    """W/L/D by reverse-BFS retrograde from terminals (our production algorithm)."""
    n, children, imm_win, has_move = g["n"], g["children"], g["imm_win"], g["has_move"]
    parents = [[] for _ in range(n)]
    for i in range(n):
        for j in children[i]:
            parents[j].append(i)
    label = [None] * n
    win_children = [0] * n
    q = deque()
    for i in range(n):
        if imm_win[i]:
            label[i] = "W"; q.append(i)
        elif not has_move[i]:
            label[i] = "L"; q.append(i)
    while q:
        i = q.popleft()
        for p in parents[i]:
            if label[p] is not None:
                continue
            if label[i] == "L":                  # a child is a Loss -> parent Wins
                label[p] = "W"; q.append(p)
            else:                                # child is a Win
                win_children[p] += 1
                if win_children[p] == len(children[p]) and not imm_win[p]:
                    label[p] = "L"; q.append(p)  # all children Win -> parent Loses
    return ["D" if x is None else x for x in label]


def label_valueiter(g):
    """INDEPENDENT solver: forward value-iteration to the same least fixpoint."""
    n, children, imm_win, has_move = g["n"], g["children"], g["imm_win"], g["has_move"]
    label = [None] * n
    for i in range(n):
        if imm_win[i]:
            label[i] = "W"
        elif not has_move[i]:
            label[i] = "L"
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if label[i] is not None:
                continue
            ch = children[i]
            if any(label[j] == "L" for j in ch):
                label[i] = "W"; changed = True
            elif ch and all(label[j] == "W" for j in ch):
                label[i] = "L"; changed = True
    return ["D" if x is None else x for x in label]


def audit(g, label):
    """Local consistency: every label must satisfy the W/L/D recurrence (0 = clean)."""
    children, imm_win, has_move = g["children"], g["imm_win"], g["has_move"]
    bad = 0
    for i in range(g["n"]):
        ch, L = children[i], label[i]
        if imm_win[i]:
            ok = L == "W"
        elif not has_move[i]:
            ok = L == "L"
        elif L == "W":
            ok = any(label[j] == "L" for j in ch)
        elif L == "L":
            ok = bool(ch) and all(label[j] == "W" for j in ch)
        else:
            ok = (not any(label[j] == "L" for j in ch)) and any(label[j] == "D" for j in ch)
        bad += not ok
    return bad


def counts_of(label):
    c = {"W": 0, "L": 0, "D": 0}
    for x in label:
        c[x] += 1
    return c


def main():
    import time
    print("=== perft from the start position ===")
    s = start()
    for d in range(1, 7):
        print(f"  perft({d}) = {perft(s, d):,}")

    print("\n=== cross-checked subgame solves (retrograde vs value-iteration + audit) ===")
    for extra in ([], ["carp"], ["fox"], ["raccoon"]):
        name = "2 kings" + ("" if not extra else " + " + " + ".join(extra))
        g = build_graph(extra)
        L1, L2 = label_retro(g), label_valueiter(g)
        bad = audit(g, L1)
        c, tot = counts_of(L1), g["n"]
        print(f"  {{{name}}}: {tot:,} pos, {g['edges']:,} edges -> "
              f"W {c['W']/tot:5.1%}  L {c['L']/tot:5.1%}  D {c['D']/tot:5.1%}   "
              f"[retro==valueiter: {L1 == L2}; audit: {bad}]")
        assert L1 == L2 and bad == 0, "*** CORRECTNESS CHECK FAILED ***"

    print("\n=== scaling: 2-piece subgame (cost calibration) ===")
    for extra in (["carp", "fox"],):
        name = "2 kings + " + " + ".join(extra)
        t0 = time.time()
        g = build_graph(extra)
        L = label_retro(g)
        bad = audit(g, L)
        dt = time.time() - t0
        c, tot = counts_of(L), g["n"]
        print(f"  {{{name}}}: {tot:,} pos, {g['edges']:,} edges, {dt:.1f}s "
              f"(~{g['edges']/dt/1e3:.0f}k edges/s, pure Python) -> "
              f"W {c['W']/tot:.1%}  L {c['L']/tot:.1%}  D {c['D']/tot:.1%}  [audit {bad}]")
    print("\n  growth: 480 (0 pieces) -> 24,480 (1) -> ~1.5M (2): ~50-60x per added piece")
    print("  (board saturates, so this does NOT extrapolate to the full ~3e13; the")
    print("   enumerator gives the true size. This run calibrates per-edge time only.)")


if __name__ == "__main__":
    main()
