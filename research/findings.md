# Findings — Shogi4 (verified facts ledger)

Every entry carries a source and a confidence tag:
**[primary]** Oca Studios' own materials · **[secondary]** third-party (BGG/blogs/app stores) ·
**[measured]** a committed run · **[estimate]** bracketed derivation · **[needs-source]** unverified.

Primary source recovered via the Wayback Machine snapshot of <https://ocastudios.com/four/shogi/>
(2024-09-26) + the Oca board graphic (`prior-art-evidence/oca-shogi4-board-strip.png`); the live
server was down at scaffold time and the PnP PDF was never archived.

## Game identity

- **Shogi4** is by **Oca Studios** (Brazilian free-culture studio), part of its **"Four" series**
  ("classic games remixed for children"). The "4" is the series brand; the board is also 4×4. **[primary]**
- Released **public domain**, as a free **print-and-play ("bronze") PDF** (version 0.1.0) plus a
  free **electronic/app** version. No commercial boxed product. **[primary]**
- Pieces are **flip-tiles**: laid down animal-up, ownership shown by **orientation** (not color),
  movement printed on the tile, **flip to promote** — the Dōbutsu physical idiom. **[primary]**

## Board & pieces

- **Board: 4×4, 16 squares.** **[primary — board graphic]**
- **Starting setup** (BGG board photo, image 1830896): each side's back row, reading from the
  royal's corner, is **Royal · Fox · Raccoon-dog · Tapir**, with the **Carp one square ahead of
  the royal**. Mirrored for the opponent (royal = Pheasant). The royal starts in a corner and the
  Carp shields it. The two **farm/hand zones flank the 4×4 grid** (left and right), outside the
  playing board. **[primary]**
- **5 pieces per side**, one of each type: **Carp, Tapir, Raccoon-dog, Fox**, and a **royal** that
  is a **Crane** (one player) or **Pheasant** (the other) — differently themed, both move as a king. **[primary]**
- Total 10 pieces; the 8 non-royals are capturable/droppable, the 2 royals are not (their capture
  ends the game). **[primary + reasoned]**

## Confirmed mechanics

- **Movement: every piece moves exactly one square per turn**, in the directions marked on the
  tile — the rules text confirms this for all pieces ("each animal only moves one space at a
  time"). The rook/bishop analogies are **direction-only, not sliding range.** Base movements
  transcribed from the BGG board photo (image 1830896):
  - **Carp** = forward only (N) — a pawn. **[primary]**
  - **Royal (Crane/Pheasant)** = all 8 directions — a king. **[primary]**
  - **Fox** = the 4 orthogonals (N, E, S, W) — a Wazir (Dōbutsu's Giraffe). **[primary]**
  - **Raccoon-dog** = the 4 diagonals (NE, NW, SE, SW) — a Ferz (Dōbutsu's Elephant). **[primary]**
  - **Tapir** = the 3 forward squares (N, NE, NW). **[primary]**
- **Friendly-jump (the signature divergence from Dōbutsu) — precise semantics from app source:**
  for any direction a piece may move, if an **allied** piece sits on the *adjacent* square, the
  piece may instead land on the square **exactly two steps away in that same direction** (the ally
  is leapt). One ally, one square beyond — **no multi-jumps, and you cannot jump an enemy**; the
  landing square must be empty or hold an enemy (enforced in `can_take_square`). An anti-congestion
  mechanic for the cramped board. **[primary — app source: the sq_F* logic in get_possible_squares]**
- **Evolve (promotion): mandatory** — every non-royal piece evolves *on reaching the last row*
  (BGG: "All pieces, save the kings, will evolve upon reaching the last row … adding more movement
  options"); royals never evolve. Flip the tile to its evolved side. Promotion is **themed and
  monotonic** (each evolved form *adds* directions to its base, never removes):
  - **Carp → Koi · Tapir → Baku · Raccoon-dog → Tanuki · Fox → Kitsune** (each base animal's
    folklore/yokai form, in that order). **[primary — BGG, "respectively"]**
  - **All four evolved movements confirmed from the official app's source** (`logic.py` →
    `get_possible_squares`): **Koi = Baku = Tanuki = Silver** (N, NE, NW, SE, SW) and
    **Kitsune = Gold** (N, NE, NW, E, W, S). So the three minor pieces all promote to **Silver**
    and only the Fox promotes to **Gold** — not a uniform rule, and the earlier "Koi = Gold (tokin)"
    guess was wrong. Each is still monotonic over its base (Koi=Carp+4 diagonals; Baku=Tapir+back
    diagonals; Tanuki=Raccoon+forward; Kitsune=Fox+forward diagonals). **[primary — app source]**
  - Mandatory promotion also means a forward-only Carp can never strand itself immobile on the
    last row. **[reasoned]**
- **Drops:** capture = "invite" the piece to your farm (your hand); "call" = drop a farm piece on
  an empty square. An **evolved piece reverts to its base form when captured** (standard shogi). **[primary]**
- **Drop restriction — RESOLVED from app source** (`can_take_square`): the *only* drop ban is the
  **opponent's last rank** (row 4 for player 1, row 1 for player 2); drops are otherwise legal on
  any empty square, your half or theirs. The earlier "opposing side" wording was wrong; it's
  "never the last row." There is **no nifu, no drop-mate, and no immobile-drop rule** — the
  last-rank ban is the entire restriction. **[primary — app source]**
- **Win condition: capture the King — and *only* that** (`capture()` sets game-over iff the captured
  piece is the King). There is **no checkmate and no check restriction**: `can_take_square` never
  filters moves that leave your own king attacked, so **moving into check is legal** and you win by
  *actually taking* the king (pure Dōbutsu-style). **No "Try"/reach-the-far-side win.** **[primary — app source]**

## Divergences from Dōbutsu (the engineering delta)

| | Dōbutsu (3×4) | Shogi4 (4×4) |
|---|---|---|
| Board | 12 squares | 16 squares |
| Piece types/side | 4 (Lion, Giraffe, Elephant, Chick) | 5 (royal, Carp, Tapir, Raccoon-dog, Fox) |
| Jump over own pieces | no | **yes (friendly-jump)** |
| Promotion | Chick→Hen only | **4 of 5 types evolve** |
| Drop restriction | none (any empty square) | **yes (exact form = Q1c)** |
| Win by king march ("Try") | yes | **no — king-capture only** |

These are why the Dōbutsu solver must be re-derived, not re-pointed.

## State-space & solve regime

- **All-arrangements upper bound: 205,148,532,253,680 (≈ 2.05×10¹⁴) — EXACT.** Computed by
  `repro/statespace_upperbound.py`, which reproduces Dōbutsu's published 1,567,925,964 **and its
  full by-pieces-in-hand breakdown to the digit** as its correctness gate. **[measured — repro/upper_bound.txt]**
- **Reachable positions: ~3×10¹³** (bracket ~1.6–3.2×10¹³), via the Dōbutsu-calibrated
  reachable/upper ratio (0.157; Dōbutsu is the closest one-step animal drop-shogi analog). Exact
  count needs the rules engine + forward search. **[estimate, bracketed]**
- **Solve regime — CORRECTED: this is an external-memory solve, not a laptop one.** A 2-bit W/L/D
  table over the reachable set is **~8 TB** (~4 TB after the ~2× LR fold) — it does **not** fit in
  RAM. Shogi4 lives in **Micro Shogi's external-memory regime, just ~15–20× smaller** (Micro
  reachable ~5×10¹⁴). The earlier scaffolding guess ("~10⁹–10¹¹, RAM-resident, Dōbutsu regime,
  ~$0") was **wrong by 3–4 orders of magnitude**: Shogi4 has **four** capturable types and **all
  promote** (4 owner×face states each), against Dōbutsu's 8 pieces with only the chick promoting —
  that multiplies out far faster than "+1 type, +4 squares" suggested. **[measured]**
- **Compute: ~5–16 core-years** (~3×10¹³ pos × ~15 branching × ~2 passes × 150–500 ns/edge) —
  buyable in days–weeks. Either external-memory on an ~8 TB NVMe box, or **in-RAM on a 4–6 TB
  high-memory node** (which the LR-folded table would fit). Low-hundreds to low-thousands of $,
  not $0. The Micro Shogi cost levers (W/L/D-only, stream-and-discard, bare-metal, symmetry) all
  apply, scaled down ~15×. **[estimate]**
- **Friendly-jump inflates the average branching factor** (more legal moves per position) → more
  edge-operations in retrograde analysis → more compute — but it does **not** change the position
  count. State-space size is set by arrangements; jump only adds edges. **[reasoned]**
- **Symmetry:** like Dōbutsu, only **left–right mirror** folding applies (shogi pieces have a
  forward direction, so the square board grants no extra rotational symmetry). ~2× fold. **[reasoned]**

## Engine & perft (reference implementation)

`engine/shogi4.py` is a faithful Python port of the decompiled app's rules — the **oracle** for
differential-testing the Rust engine. **perft from the start position** (a king-capture ends the
game, counted as a leaf at its depth):

| depth | perft |
|---|---|
| 1 | 8 |
| 2 | 64 |
| 3 | 626 |
| 4 | 6,304 |
| 5 | 68,723 |
| 6 | 769,014 |

perft(1)=8 is hand-verified (king/fox/raccoon/tapir/carp moves, including the king **leaping its
own carp** via friendly-jump). These are the numbers the Rust port must reproduce to the digit.
**[measured — engine/validation_output.txt]**

**First Shogi4 game-theoretic results**, via full retrograde over closed small subgames (validates
the W/L/D pipeline incl. drops, promotion, captures, repetition=draw):

| subgame | positions | Win | Loss | Draw |
|---|---|---|---|---|
| 2 kings | 480 | 35.0% | 0% | 65.0% |
| 2 kings + carp | 24,480 | 75.9% | 23.3% | 0.7% |
| 2 kings + fox | 24,480 | 76.7% | 23.3% | 0% |
| 2 kings + raccoon | 24,480 | 76.2% | 23.8% | 0% |

These are artificial reduced games for pipeline validation, **not** sub-parts of full Shogi4 (drops
conserve material, so the real game doesn't decompose into them). The `{2 kings}` 0-loss result is a
correctness sanity check: with only kings you can always avoid a forced capture. **[measured]**

## Sources

- Oca Studios Shogi4 rules page (primary; via Wayback 2024-09-26): <https://ocastudios.com/four/shogi/>
- BoardGameGeek — Shogi4: <https://boardgamegeek.com/boardgame/146291/shogi4>
- Oca Studios (publisher, free-culture / public-domain): <https://boardgamegeek.com/boardgamepublisher/23973/oca-studios>
- Dōbutsu measured numbers: `../dobutsu-shogi/research/findings.md`
- Validated state-space enumerator: `../micro-shogi/research/repro/`
