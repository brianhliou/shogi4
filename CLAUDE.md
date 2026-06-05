# CLAUDE.md — shogi4

> Research project: scope and compute the **first complete strong solution** of **Shogi4**
> — Oca Studios' public-domain 4×4 animal drop-shogi. Third rung on the small-shogi ladder
> (Dōbutsu 3×4 → **Shogi4 4×4** → Micro 4×5). Treat it like science, not blogging.

## What this is (and isn't)

- **Is:** a rigorous scoping + solving effort for **Shogi4** — recover its exact rules from the
  primary source, port the Dōbutsu solver to a *different* ruleset and a bigger board, and
  produce the first-ever strong solution (game value, length, full strategy) plus a correct,
  well-cited writeup. The goal is a true strong solution validated without an oracle.
- **Isn't:** a re-derivation of Dōbutsu (done in `../dobutsu-shogi`), the Micro Shogi 4×5 solve
  (`../micro-shogi`), or a general shogi-variant survey. Those appear only as ladder/calibration
  points. It is **not** about inventing a 4×4 — Shogi4 already exists; we are solving *it*.

## Why Shogi4 is the right next rung

- **Never solved.** No academic treatment, no published value, no oracle. The strong solution
  is a genuinely new result, and Shogi4 is **public domain** — free to solve, fork, publish.
- **A real step up from Dōbutsu, not a cluster job.** Bigger board (16 vs 12 squares), one more
  piece type per side, and a **mechanically different ruleset**. Expected to stay RAM-resident
  / single-machine (Dōbutsu regime), *not* the external-memory monster Micro Shogi is.
- **The challenges are exactly:** (1) recovering the exact ruleset from a primary source whose
  PnP PDF is currently unreachable; (2) a different move model — notably the **friendly-jump**
  rule Dōbutsu lacks; (3) **no oracle** for correctness.

## Working method (the "scientist" contract — inherited from dobutsu-shogi / micro-shogi)

1. **Primary source over secondary.** For the *rules*, Oca Studios' own materials are ground
   truth; Wikipedia/blogs/app-store text are leads to verify. **Solving the wrong ruleset is
   worthless**, so the exact rules are the #1 gating open question (`research/open-questions.md`).
2. **Every number carries its source/derivation.** No figure enters `research/findings.md`
   without a pointer (Oca page section, a measured run, or a committed script + output). Mark
   each as *primary* / *secondary* / *measured* / *estimate (bracketed)* / *needs-source*.
3. **No oracle for Shogi4.** Unlike Dōbutsu (Tanaka + clausecker), there is no external
   solution to check against. Correctness must come from: brute-force forward minimax on small
   positions, two independent implementations, and full-table consistency audits. Non-negotiable.
4. **Validate the combinatorics against a known answer.** Any state-space enumerator earns trust
   by reproducing Tanaka's Dōbutsu upper bound (1,567,925,964) exactly before its Shogi4 output
   is believed. (Port the validated enumerator from `../micro-shogi/research/repro/`.)
5. **Estimates are bracketed, not guessed.** Reachable count, RAM footprint, solve time get a
   calibrated range and a note on what pins them.

## Key facts so agents don't re-derive (current best-known — see findings.md)

- **Shogi4 = Oca Studios, "Four" series, public domain, print-and-play ("bronze") + free app.**
  4×4 board, 16 squares. 5 pieces/side: Carp, Tapir, Raccoon-dog, Fox, and a royal (**Crane**
  for one player, **Pheasant** for the other). [primary, via Oca rules page]
- **Confirmed mechanics:** one step per turn in marked directions; Carp = forward only; royal =
  any direction; **a piece may jump over a *friendly* piece** (anti-congestion — Dōbutsu has no
  such rule); **evolve** on reaching the far row (Carp/Tapir/Raccoon-dog/Fox evolve, royals
  never); **drops** (capture = "invite to farm"; "call" = drop), evolved pieces revert on
  capture; **win = capture the opponent's royal — NO "Try"/reach-the-far-side win.** [primary]
- **Ruleset fully recovered** (Q1 closed) by decompiling the official app `com.ocastudios.shogi4`
  v1.0.1 (Kivy/pygame; `logic.py` via uncompyle6 — committed under `research/prior-art-evidence/`).
  Base: Carp=forward; King=8; Fox=Wazir; Raccoon=Ferz; Tapir=N/NE/NW. Evolved: **Koi=Baku=Tanuki=
  Silver, Kitsune=Gold**. Friendly-jump = leap one adjacent ally to the square two beyond. Drops:
  empty squares only, **last-rank ban is the sole restriction** (no nifu/drop-mate). Win = **capture
  the King only** (no checkmate, no check rule, no Try). Repetition has no in-app rule → **our**
  declared convention: infinite play = draw.
- **State-space (estimate): ~10⁹–10¹¹ reachable** (to pin via the ported enumerator) — larger
  than Dōbutsu (2.47×10⁸), far below Micro Shogi (~5×10¹⁴). **Expected RAM-resident / laptop-
  to-workstation solve, ~$0** — Dōbutsu regime, not Micro's cluster regime.
- **Friendly-jump inflates branching** (more legal moves/position) → more edge-operations →
  more compute, but does **not** change the state count.

## Conventions

- **Numbers:** write them exactly. Distinguish **plies** (single moves) from full moves, and
  **state-space complexity** (reachable positions) from **game-tree complexity** (b^d leaves).
- **Pieces (Shogi4):** Carp (pawn — forward 1), Tapir, Raccoon-dog, Fox, royal = Crane/Pheasant.
  Use English names; movements are *marked on the tiles* (Oca's design) and several are not yet
  primary-confirmed — see open-questions.
- **Shogi terms:** 先手 = sente = first player; 後手 = gote = second player. Be explicit about
  which side the strong solution favors (Dōbutsu is a gote win; Shogi4's value is unknown).

## Relationship to the sibling repos

`../dobutsu-shogi` is the methodological anchor (Tanaka reproduction, the from-scratch Rust
solver, the state-space-vs-arrangements disambiguation, the explorer + article format).
`../micro-shogi` holds the validated state-space enumerator and the distributed-solve cost model.
When scaling estimates, cite the *measured* Dōbutsu numbers, not re-derivations. Shogi4 reuses
the Dōbutsu solver/explorer/article pipeline — the new work is the *different ruleset*, the
*bigger board*, and *correctness without an oracle*.

- Drafting publishable prose (article/blog/public README hero) → invoke the `draft-voice` skill
  first. Internal ledgers (`research/*.md`) are technical reference, written directly.

## Primary source

Shogi4 — Oca Studios, "Four" series (public domain). <https://ocastudios.com/four/shogi/>
(Live server down at scaffold time; recovered via the Wayback Machine, 2024-09-26 snapshot.)
BoardGameGeek: <https://boardgamegeek.com/boardgame/146291/shogi4>
