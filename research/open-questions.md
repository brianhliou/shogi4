# Open questions — Shogi4

The backlog. Resolve with primary sources or our own reproducible experiments — never paper over
in prose. Q1 is **gating**: nothing downstream is trustworthy until the exact rules are pinned.

---

## Q1 — Exact ruleset ✅ RESOLVED

**Fully recovered by decompiling the official Oca app** (`com.ocastudios.shogi4` v1.0.1), whose
`logic.py` is the authoritative ruleset. Recovery route: APK → `assets/private.mp3` (a gzipped tar
of the Kivy/pygame payload) → `logic.pyo` (Python 2.7 bytecode) → `uncompyle6`. The decompiled
source is committed at `prior-art-evidence/oca-shogi4-logic-decompiled.py`; the derived rules are
in `findings.md`. Oca's PnP PDF / dormant server are no longer on the critical path.

- **Q1a — Starting setup.** ✅ Back row **Royal · Fox · Raccoon · Tapir** from the royal's corner,
  Carp one square ahead of the royal (BGG photo 1830896).
- **Q1b — All movements.** ✅ From `get_possible_squares`: Carp=N; Royal=king; Fox=Wazir;
  Raccoon=Ferz; Tapir=N/NE/NW. Evolved: **Koi=Baku=Tanuki=Silver**, **Kitsune=Gold**. Friendly-jump
  = leap one adjacent ally to the square two beyond, same direction (no multi-jump, no enemy-jump).
- **Q1c — Drop restriction.** ✅ Only ban is the **opponent's last rank**; drops otherwise legal on
  any empty square (`can_take_square`). It was "never the last row," not "opposing side."
- **Q1d — Other drop legality.** ✅ **None** — no nifu, no drop-mate, no immobile-drop rule.
- **Q1e — Repetition / draw convention.** The app has **no** repetition/draw rule (grep confirms),
  so this stays **our declared convention**: *repeated/infinite play = draw, no perpetual-check
  exception*. Operationally (competitive play + the public rules article) this is enforced as
  **threefold repetition = automatic draw**, which realizes infinite-play-as-draw in finite play
  and leaves the solved game value unchanged. The only rule that is ours, not Oca's — flag it as
  such in any writeup. **[our decision]**
- **Win condition.** ✅ Capture the King (and only that); no checkmate, no check restriction
  (moving into check is legal); no Try rule. Promotion is mandatory on the last rank.

The ruleset is complete and unambiguous. The solve is unblocked.

---

## Q2 — Exact reachable count

◐ **Upper bound DONE** (`repro/`): all-arrangements **205,148,532,253,680 (≈2.05×10¹⁴), exact**,
enumerator validated against Tanaka's Dōbutsu number + breakdown. Reachable **bracketed ~3×10¹³**
(Dōbutsu ratio). **Still open: the EXACT reachable count**, which needs the rules engine + a forward
BFS from the start position (it falls out of the solve). The headline consequence is already clear:
~8 TB W/L/D → external-memory regime (see findings.md "Solve regime — CORRECTED").

## Q3 — The game value

Is Shogi4 a **first-player win, second-player win, or draw**, and in how many plies (DTM)? The
headline result. Unknown — no prior solve exists. Depends on Q1 + a correct solver.

## Q4 — Is it degenerate?

Tiny drop-shogi can collapse into a trivial fast win or a dead draw. Does Shogi4's specific combo
(friendly-jump + 4-of-5 promotion + drop limit + **no Try rule**) yield a balanced game or a short
forced result? A short forced win is still a clean, publishable finding — not a failure.

## Q5 — Correctness (the engine HAS an oracle; the values do not)

Two layers, validated differently — and unlike `../micro-shogi`, we have a runnable reference:

- **Engine (move-gen, promotion, drops, win) HAS a runnable oracle:** the decompiled official app
  `prior-art-evidence/oca-shogi4-logic-decompiled.py`. Strip its pure rule functions
  (`get_possible_squares`, `can_take_square`, `fake_take_square`, `capture`) into a standalone
  Python harness, then **differential-test** the Rust engine against it on millions of random
  positions, plus **perft** (move-path counts) matching to the digit at each depth. Caveat: this
  validates against the *app's behaviour as ground truth*; the **repetition rule is ours** (the app
  has none), so that one is validated by internal consistency, not the app.
- **Solve values (W/L/D/DTM) have NO external oracle:** (a) brute-force forward minimax agreeing
  with the retrograde table on small sub-games; (b) two independent solver implementations agreeing;
  (c) full-table consistency audits (every Win → a move to opp-Loss; every Loss → all moves to
  opp-Win; DTM monotonicity). Inherited from `../micro-shogi`.

## Q6 — Does friendly-jump change the retrograde unmove generation?

Forward moves include jumps over friendlies; **retrograde analysis must invert them correctly**
(the un-jump predecessor set differs from sliding/stepping pieces). Verify the unmove generator
against the forward generator on random positions before trusting any backward pass.

## Q7 — Relationship of Shogi4 to a possible *original* variant

Out of scope for the solve, but noted: once Shogi4 is solved, designing and solving an *original*
fixed-setup 4×4 (where we are the originator, not the solver/explainer) is a natural follow-on,
with Shogi4 as the prior-art baseline. Tracked, not pursued here yet.
