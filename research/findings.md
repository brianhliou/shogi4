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
- **Solve regime — external-memory, sized to the dense-rank ARRANGEMENT domain (corrected twice).**
  The scalable solver indexes positions by a dense rank (no hashing). That rank necessarily spans
  **all legal arrangements**, not the reachable subset — you can't combinatorially rank
  reachable-only at this scale (an MPHF over ~3×10¹³ keys is itself infeasible; that's why Dōbutsu's
  enumerate-then-MPHF trick doesn't carry up). The **validated** ranker's domain is **N =
  410,297,064,507,360 ≈ 4.1×10¹⁴** (= 2 × the enumerator's arrangement count, to the digit;
  `solver/src/bin/rank_check.rs`). So the flat 2-bit W/L/D array is **~100 TB** (~50 TB after the
  ~2× LR fold; ~5–15 TB peak-resident with stream-and-discard).
  - **This supersedes the earlier "~8 TB" figure**, which was the *reachable-only floor* (~3×10¹³ ×
    2 bit). The solver's real footprint follows the rank domain, ~13× larger. I conflated "reachable
    count" with "solver index size" — building the ranker exposed the gap.
  - Compute is dominated by the *active* (reachable + backward-reachable) subset, still being
    pinned — plausibly ~tens of core-years.
  - Net: **bigger than I first stated — Micro Shogi's storage class, still ~10–19× smaller by the
    arrangement-domain ratio** (Micro upper bound ~3.9×10¹⁵). Rung 4 is a serious NVMe machine or a
    small cluster, *not* "one small box, days." The reachable estimate (~3×10¹³) and its cause (four
    capturable types, all promoting) stand. **[measured N; compute estimate]**
- **Compute — CORRECTED to the rank domain: ~60–190 core-years** (~3.6×10¹⁴ legal slots × ~16
  branching × ~2 passes × 150–500 ns/edge). A push-based retrograde must move-gen *every* slot once
  just to count children (~6×10¹⁵ edge-ops, ~30–90 cy) before any propagation, so reachable-only
  compute (~3×10¹³) is not achievable. The earlier "~5–16 core-years" was reachable-based and is
  superseded.
- **Cost — CORRECTED: ~$5–15k bare-metal (~$15–50k cloud), ~50 TB NVMe, weeks–months.** A serious
  NVMe machine or a small cluster — *not* "one small box, days." This is **Micro-Shogi-cost-class**;
  Shogi4 stays the cheaper rung (~19× smaller arrangement domain than Micro), and since Micro's own
  ~$10–15k figure is likewise reachable-based (optimistic), Micro's true dense-rank cost is
  plausibly $50–200k+ — which is exactly why solving Shogi4 first de-risks it. Levers (tighter rank
  baking in invariants, W/L/D-only, LR-fold, stream-and-discard) shave factors, not orders of
  magnitude. **[estimate]**
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
own carp** via friendly-jump). **The Rust engine (`solver/`) reproduces perft(1..6) to the digit
and passes a 4,000-position golden differential test** against the oracle (random playouts covering
drops, promotions, captures, jumps) with 0 mismatches — cross-language move-gen agreement.
**[measured — engine/validation_output.txt]**

**First Shogi4 game-theoretic results**, via full retrograde over closed small subgames (validates
the W/L/D pipeline incl. drops, promotion, captures, repetition=draw):

| subgame | positions | Win | Loss | Draw |
|---|---|---|---|---|
| 2 kings | 480 | 35.0% | 0% | 65.0% |
| 2 kings + carp | 24,480 | 75.9% | 23.3% | 0.7% |
| 2 kings + fox | 24,480 | 76.7% | 23.3% | 0% |
| 2 kings + raccoon | 24,480 | 76.2% | 23.8% | 0% |
| 2 kings + carp + fox | 1,164,704 | 74.5% | 17.8% | 7.7% |

These are artificial reduced games for pipeline validation, **not** sub-parts of full Shogi4 (drops
conserve material, so the real game doesn't decompose into them). The `{2 kings}` 0-loss result is a
correctness sanity check: with only kings you can always avoid a forced capture. **[measured]**

**Correctness gate passed (Q5):** on every subgame above, **three independent solvers agree to the
unit** — Python reverse-BFS retrograde, Python forward value-iteration, and the **Rust retrograde
solver** (`solver/`, ~20× faster; cross-checked via the committed `engine/subgame_expected.txt`
fixture) — and a **local consistency audit finds 0 violations** (every Win has a move to a Loss;
every Loss has all moves to Wins; every Draw has no move to a Loss and ≥1 to a Draw). Holds at
1.16M positions, e.g. `{2K+carp+fox}` = W 867,856 / L 206,964 / D 89,884. With the move-gen
agreement (perft + golden), the **entire Rust pipeline is now cross-validated**. **[measured]**

**Dense ranking (the scaling bridge) — built & validated.** `solver/` has a `rank`/`unrank`
bijection (position ↔ integer), the component that replaces the in-RAM HashMap with a flat array.
Validated three ways: (a) `rank(unrank(i)) == i` over *every* `i` on the subgames (incl. the count-2
`{2K+2P}`, which exercises the full-game piece shape); (b) the legal positions from `unrank` equal
the enumerator's set; (c) for the full game (too big to iterate) its domain **N =
410,297,064,507,360 = 2 × the state-space enumerator's count, to the digit**. The size of this
domain is what drove the storage correction above. **[measured — solver/src/bin/rank_check.rs]**

**Flat-array solve through the rank — the scalable mechanism, validated in RAM.** `solve_flat`
runs the retrograde over a value array indexed by `rank`, generating child edges on the fly
(`make`+`rank`) with **no stored graph** — the in-RAM miniature of the real external-memory solver.
It reproduces the oracle's W/L/D exactly on the subgames (`{2K}`, `{2K+P/F/R}`). What separates it
from the full solve is now only (a) un-move generation + push (efficiency) and (b) external-memory
backing — not correctness. **[measured — solver/src/bin/flat_check.rs]**

**Un-move generation + push-based retrograde — the full scalable algorithm, validated in RAM.**
`predecessors(q)` reverses each forward-move shape (board move, capture, promotion, drop, jump) and
**verifies every candidate by running `make` forward** — so correctness rides on the validated
engine. It equals the true reverse edges exactly on the subgames (`pred_check`). `solve_push`
(counter-BFS over the rank array via `predecessors` — no stored graph, no pull rescan) reproduces
the oracle's W/L/D to the unit on **all** subgames, including the **1.16M-position `{2K+carp+fox}`**
(W 867,856 / L 206,964 / D 89,884, 7.7 s) that the pull solver could not finish. The complete
external-memory algorithm now runs and is validated in RAM. **Only the external-memory backing
(sharding the flat array onto NVMe) and the rung-4 spend remain — not correctness.**
**[measured — solver/src/bin/push_check.rs]**

**LR-symmetry fold — validated, a clean exact 2×.** `mirror` (columns c↔5−c) + the invariant
`value(pos) == value(mirror(pos))` checked across the solved subgames: **0 mismatches**, and on the
4-wide board **no position is its own mirror**, so the fold factor is exactly **0.500** — a genuine
2× cut to rung-4 storage *and* compute (not the ~1.15× Dōbutsu's solver achieved). `predecessors`
was also optimized (direct single-move legality check instead of full move-gen). **[measured —
solver/src/bin/lr_check.rs]**

**Calibration ladder — the push solver scaled to 51.5M positions in RAM.** Largest in-RAM solve;
all match the oracle's logic (validated at ≤1.16M; the 51.5M is a new result):

| subgame | legal positions | time | ns/edge | W / L / D |
|---|---|---|---|---|
| `{2K+P+F}` | 1,164,704 | 5.5 s | ~396 | 74.5 / 17.8 / 7.7 % |
| `{2K+P+F+R}` | **51,461,568** | 391 s | **~633** | 80.3 / 18.9 / 0.8 % |

These are reduced games (fewer pieces), not the full Shogi4 — for validation + calibration, not the
headline value. **The key signal: `ns/edge` *rises* with working-set size** (396 → 633 as the value
arrays grow past cache), which is exactly the cost model's external-memory risk showing up
empirically. At PB scale on NVMe it climbs further, so **keeping access sequential is the dominant
rung-4 cost driver** — and it places the compute estimate toward the realistic-high end of
~60–190 core-years, partly offset by the exact-2× LR fold. `{2K + one of each type}` (3.5B) is
laptop-infeasible — the in-RAM ceiling is ~50–75M. **[measured — solver/src/bin/scale.rs]**

**Distributed correctness — validated on one machine, for $0.** `sharded_check` simulates the
rung-4 distributed solver: rank-range **shards** (each owning its slots' value+counter), predecessor
updates routed to the owning shard (the **shuffle**), **BSP supersteps** behind a barrier, and
zero-message **convergence**. It reproduces the oracle's W/L/D **for every shard count (1 / 4 / 16 /
64)** on the subgames — proving (a) the distributed decomposition is correct and (b) the result is
**invariant to shard count** (the algorithm is a confluent monotone fixpoint, as argued, so
parallelization can't change the answer). Measured distributed metrics: **supersteps 1 → 54**
(propagation depth ≈ max-DTM; the full game's ~hundreds of plies → ~hundreds of BSP barriers, not a
bottleneck) and **~7 shuffle-messages per position** (`{2K+P+F}`: 8,098,044 msgs / 1,164,704 pos).
That ratio grounds the rung-4 shuffle volume at ~7 × the solve domain ≈ **~15–30 PB** (a throughput
requirement, ~$0 if kept node-local / same-AZ). This converts "distributed correctness" from a
scale-time risk into a passed laptop test. **[measured — solver/src/bin/sharded_check.rs]**

**Verification demonstrated — a certificate for ~½ the solve cost that catches corruption.**
`audit_solution` is a single forward pass checking every value is locally minimax-consistent with
its children; **0 violations certifies the tablebase** (a locally-consistent labeling with correct
terminals is the unique solution — the same theorem our subgame `audit` rests on). On `{2K+P+F}`:
**solve 5.5 s, audit 3.0 s — verification is 55% of the solve**, 0 violations on the clean run.
**Every injected single wrong value is caught** (1–5 violations each: the flipped slot plus its
predecessors), so silent corruption can't pass. At external-memory scale the audit avoids the
solve's iterative shuffle (one forward pass + a sort-merge vs the full fixpoint), so the fraction
*shrinks* further. A computed result is therefore verifiable far more cheaply than re-deriving it.
**[measured — solver/src/bin/audit_demo.rs]**

**Failure-recovery — validated, and it caught a latent nondeterminism.** `failrec_check` injects
crashes at many supersteps (snapshot the checkpoint, run the superstep, discard the work, replay
from the checkpoint), asserting each replay reproduces the superstep **byte-for-byte** and the final
result equals the crash-free run — passed on all subgames (1–18 recoveries each). Building it
surfaced a real bug: `predecessors` collected from a `HashSet` (randomized iteration order), so
replays emitted the same messages in a *different order* — harmless to the confluent result but
breaking bit-exact checkpoints. Fixed by sorting `predecessors`, which makes the whole solver
**deterministic/reproducible**, exactly what idempotent recovery requires. So "a shard = a
checkpoint + a deterministic recompute" is now a demonstrated property, not an assumption.
**[measured — solver/src/bin/failrec_check.rs]**

**Cost calibration:** the 2-piece subgame runs at ~286k edges/s in pure Python (1 core). The full
solve is ~4×10¹⁴ edge-ops (≈3×10¹³ positions × ~13 branching), so Python would take *decades* — but
Rust at ~150 ns/edge (the Dōbutsu solver's measured RAM-speed) puts it at **~2–6 core-years**, i.e.
days–weeks on a many-core NVMe box. Empirical basis for the "external-memory, single high-memory/NVMe
machine" regime, consistent with the ~8 TB table. **[measured + estimate]**

## Sources

- Oca Studios Shogi4 rules page (primary; via Wayback 2024-09-26): <https://ocastudios.com/four/shogi/>
- BoardGameGeek — Shogi4: <https://boardgamegeek.com/boardgame/146291/shogi4>
- Oca Studios (publisher, free-culture / public-domain): <https://boardgamegeek.com/boardgamepublisher/23973/oca-studios>
- Dōbutsu measured numbers: `../dobutsu-shogi/research/findings.md`
- Validated state-space enumerator: `../micro-shogi/research/repro/`
