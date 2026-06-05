#!/usr/bin/env python3
"""Exact 'all-arrangements' upper bound on positions for Shogi4 (4x4 drop-shogi),
computed Tanaka-2009 Table-1 style.

We FIRST reproduce Dobutsu's published upper bound 1,567,925,964 -- and its full
by-pieces-in-hand breakdown -- to validate the combinatorial model (copied
verbatim from ../micro-shogi/research/repro, where it is validated against
Tanaka), THEN apply the identical model to Shogi4.

Shogi4 piece model (from the decompiled official app; see research/findings.md and
research/prior-art-evidence/oca-shogi4-logic-decompiled.py):
- Kings (Crane / Pheasant): exactly one per player, always on the board, never in
  hand -- capturing a king ends the game. Treated identically to Dobutsu's lions.
- Four capturable types, two copies each, ALL promote (Carp<->Koi, Tapir<->Baku,
  Raccoon<->Tanuki, Fox<->Kitsune). Captured pieces revert to base in hand.

This counts arrangements ignoring legality/reachability -> a strict upper bound.
Reachable is bracketed via ratios calibrated on Dobutsu (0.157) and Minishogi
(0.077); the closest analog is Dobutsu -- same one-step animal drop-shogi family.
The exact reachable count needs a forward search with the real rules engine (the
next milestone), not this combinatorial bound.

Model (verified to reproduce Tanaka's Dobutsu sub-counts exactly):
- On-board occupied square = owner (2) x face (2 if the type promotes, else 1).
- In-hand pieces revert to base; identical in-hand copies of a type collapse to
  counts, giving (h+1) owner-splits for h copies in hand.
- Sum over every split of each type's 2 copies into (on_board, in_hand).
"""
from math import comb
from itertools import product


def upper_bound(squares, capturable):
    """capturable: list of (name, promotes: bool). Returns (total, by_in_hand)."""
    by_hand = {}
    total = 0
    for js in product(range(3), repeat=len(capturable)):  # on-board count per type
        on_board = 2 + sum(js)  # +2 kings
        if on_board > squares:
            continue
        ways = 1
        rem = squares
        # kings: choose 2 squares, assign P1/P2 (exactly one each) -> x2
        ways *= comb(rem, 2) * 2
        rem -= 2
        for (_, promotes), j in zip(capturable, js):
            ways *= comb(rem, j) * (2 * (2 if promotes else 1)) ** j
            rem -= j
        hand = 1
        for j in js:
            hand *= (2 - j) + 1  # owner-splits for the (2-j) copies in hand
        cnt = ways * hand
        tih = sum(2 - j for j in js)
        by_hand[tih] = by_hand.get(tih, 0) + cnt
        total += cnt
    return total, by_hand


DOBUTSU_CAP = [("giraffe", False), ("elephant", False), ("chick", True)]
SHOGI4_CAP = [("carp", True), ("tapir", True), ("raccoon", True), ("fox", True)]

DOBUTSU_PUBLISHED = 1_567_925_964
DOBUTSU_BREAKDOWN = {0: 638_668_800, 1: 638_668_800, 2: 242_161_920,
                     3: 44_098_560, 4: 4_134_240, 5: 190_080, 6: 3_564}
DOBUTSU_REACHABLE = 246_803_167      # Tanaka, reachable from start
DOBUTSU_CANONICAL = 213_993_386      # our Dobutsu solver, turn+LR folded


def main():
    # ---- validate the model on Dobutsu (correctness gate) ----
    d, dbh = upper_bound(12, DOBUTSU_CAP)
    print("=== validation vs Tanaka 2009 (Dobutsu 3x4) ===")
    print(f"computed upper bound  {d:,}")
    print(f"published (Tanaka)    {DOBUTSU_PUBLISHED:,}")
    breakdown_ok = all(dbh.get(k) == v for k, v in DOBUTSU_BREAKDOWN.items())
    ok = (d == DOBUTSU_PUBLISHED) and breakdown_ok
    print(f"total match: {d == DOBUTSU_PUBLISHED}   breakdown match: {breakdown_ok}")
    assert ok, "model failed Dobutsu validation -- aborting before trusting Shogi4"
    print("MODEL VALIDATED.")

    r_reach = DOBUTSU_REACHABLE / DOBUTSU_PUBLISHED   # 0.1574
    r_canon = DOBUTSU_CANONICAL / DOBUTSU_REACHABLE   # 0.8671

    # ---- Shogi4 (4x4) exact upper bound ----
    s, sbh = upper_bound(16, SHOGI4_CAP)
    print("\n=== Shogi4 (4x4) : 16 squares, 4 capturable types (all promote) ===")
    print(f"all-arrangements upper bound (EXACT) = {s:,}")
    print("by pieces-in-hand:")
    for k in sorted(sbh):
        print(f"  {k} in hand: {sbh[k]:,}")

    # ---- reachable / storage projection ----
    print("\n=== reachable + storage projection ===")
    print(f"upper bound (exact)              {s:,}   (~{s:.3e})")
    lo, hi = 0.077, r_reach     # minishogi ratio .. dobutsu ratio
    print(f"reachable bracket    ~{s*lo:.3e} .. {s*hi:.3e}")
    reach = s * r_reach
    print(f"reachable (Dobutsu ratio {r_reach:.3f}, closest analog)  ~{reach:.3e}")
    print(f"  -> ~{reach/DOBUTSU_REACHABLE:.0f}x larger than Dobutsu's 2.47e8 reachable")
    canon = reach * r_canon
    print(f"canonical (Dobutsu fold {r_canon:.3f})                    ~{canon:.3e}")
    print("  note: Shogi4's rules are left-right symmetric, so a full LR fold")
    print("  (~2x) is available; Dobutsu's measured fold was milder (0.867).")

    print("\nstorage for a complete tablebase over the reachable set:")
    for bits, label in [(2, "W/L/D (2-bit)"), (8, "DTM (1-byte)"), (16, "DTM+slack (2-byte)")]:
        gb = reach * bits / 8 / 1e9
        print(f"  {label:20s} {gb:7.2f} GB")
    print("\nregime: RAM-resident on a single workstation (Dobutsu regime), not a")
    print("cluster. The exact reachable count comes from the rules engine + forward")
    print("search (next milestone); this bound + ratio just sizes the solve.")


if __name__ == "__main__":
    main()
