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
- **5 pieces per side**, one of each type: **Carp, Tapir, Raccoon-dog, Fox**, and a **royal** that
  is a **Crane** (one player) or **Pheasant** (the other) — differently themed, both move as a king. **[primary]**
- Total 10 pieces; the 8 non-royals are capturable/droppable, the 2 royals are not (their capture
  ends the game). **[primary + reasoned]**

## Confirmed mechanics

- **Movement: one square per turn**, only in the directions marked on the tile. **[primary]**
  - Carp = forward only (a pawn). **[primary]**
  - Royal (Crane/Pheasant) = any direction, one step (a king). **[primary]**
  - Tapir, Raccoon-dog, Fox = specific marked directions — **exact diagrams not yet primary-confirmed**
    (secondary guesses: Raccoon-dog ≈ one-step diagonal, Fox ≈ one-step orthogonal, Tapir unknown).
    See open-questions Q1. **[needs-source]**
- **Friendly-jump (the signature divergence from Dōbutsu):** "he can jump over another piece that
  belongs to the same player," landing on an empty square or capturing an opponent. An anti-
  congestion mechanic for the cramped board. **[primary]**
- **Evolve (promotion):** on reaching the **far row**, flip the tile to its evolved side. Carp,
  Tapir, Raccoon-dog, Fox all evolve; the royal never does. Evolved pieces move in more
  directions — **the evolved movement diagrams are not yet primary-confirmed** (Q1). **[primary; diagrams needs-source]**
- **Drops:** capture = "invite" the piece to your farm (your hand); "call" = drop a farm piece on
  an empty square. An **evolved piece reverts to its base form when captured** (standard shogi). **[primary]**
- **Drop restriction — WORDING CONFLICT (Q1c):** the rules text says you may not call a piece "on
  the opposing side of the board"; the board graphic caption says "never to the last row." These
  differ (opponent's half vs. just the back rank) and must be resolved from the PDF. **[primary, conflicting]**
- **Win condition: capture ("invite") the opponent's royal.** There is **NO "Try"/reach-the-far-
  side win** (Dōbutsu has one — Shogi4 does not). **[primary]**

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

- **Reachable positions: ~10⁹–10¹¹ (estimate, to be pinned).** Reasoning: Shogi4 = Dōbutsu's
  structure (one of each type per side, drops, flip-promotion) plus **+1 piece type/side and +4
  squares**; Dōbutsu measures 2.47×10⁸ reachable, so 1–3 orders of magnitude up is expected. Pin
  it by porting the validated enumerator from `../micro-shogi/research/repro/` and counting Shogi4. **[estimate]**
- **Solve regime: RAM-resident, single machine, ~$0** — the Dōbutsu regime, *not* Micro Shogi's
  external-memory/cluster regime. A 2-bit W/L/D table is ~0.25–25 GB across the bracket (fits a
  workstation); only the high end (~10¹²) would push toward 128–256 GB RAM or light external
  memory. The enumerator resolves which. **[estimate]**
- **Friendly-jump inflates the average branching factor** (more legal moves per position) → more
  edge-operations in retrograde analysis → more compute — but it does **not** change the position
  count. State-space size is set by arrangements; jump only adds edges. **[reasoned]**
- **Symmetry:** like Dōbutsu, only **left–right mirror** folding applies (shogi pieces have a
  forward direction, so the square board grants no extra rotational symmetry). ~2× fold. **[reasoned]**

## Sources

- Oca Studios Shogi4 rules page (primary; via Wayback 2024-09-26): <https://ocastudios.com/four/shogi/>
- BoardGameGeek — Shogi4: <https://boardgamegeek.com/boardgame/146291/shogi4>
- Oca Studios (publisher, free-culture / public-domain): <https://boardgamegeek.com/boardgamepublisher/23973/oca-studios>
- Dōbutsu measured numbers: `../dobutsu-shogi/research/findings.md`
- Validated state-space enumerator: `../micro-shogi/research/repro/`
