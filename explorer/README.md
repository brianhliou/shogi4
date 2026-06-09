# Shogi4 explorer

A static browser-based board for **Shogi4** — play through games move by move.
Friendly-jumps, far-rank promotion, drops, and king-capture wins are generated
in the page from the same rules as the project's validated oracle.

Shogi4 is **not solved yet** (no tablebase), so this is a *rules viewer*: it shows
**legal moves only**, with no win/loss verdicts. When the strong solution is
computed, the move list can gain each move's result + distance-to-mate and the
status bar can become a verdict bar — the rest is unchanged.

## Run

```bash
python3 explorer/serve.py        # -> http://localhost:41234/
```

No dependencies (Python stdlib only). The server is only a local static file
server for browser testing; deployed hosting can serve `explorer/` directly.

## Deploy

Deploy `explorer/` as the Vercel project root for `shogi4.brianhliou.com`. There
is no build step, no database, and no Railway service.

## Use

- **Play:** drag a piece, or click a piece then a destination, or click a row in
  the move list. Friendly-jumps appear as legal 2-square moves (tagged `jump`).
- **Step:** `◀ ▶` (or arrow keys) walk the played line; click any move in
  "Moves played" to jump there; `↺` resets.
- **Import / export** (`⇄`): a space-separated move list in this viewer's
  notation (`Ka1-a3 Kd4-d2 …`), optionally prefixed `FROM:<position>`.

## Pieces

The tiles are the **official Shogi4 artwork**, extracted from Oca's public-domain
app (see `pieces/CREDITS.txt`). Each tile carries its own movement marks (paw
prints, in the piece's forward sense); base pieces sit on a cream card, evolved
pieces on a pink one. The **second player's** non-royal tiles use a slightly darker
card (`pieces/dark/`, regenerate via `tools/gen_dark_cards.py`) and are rotated
180°, so their painted marks point forward for that side. The letters below are the
move notation (e.g. `Pa2-a3`), not what's printed on the tile.

| | base | evolves to (on the far rank) | moves as |
|---|---|---|---|
| K | King (Crane / Pheasant) | — (royal, never) | all 8 directions |
| P | Carp | O Koi | pawn (forward 1) → silver |
| T | Tapir | B Baku | forward + 2 fwd-diag → silver |
| R | Raccoon-dog | N Tanuki | the 4 diagonals → silver |
| F | Fox | G Kitsune | the 4 orthogonals → gold |

Win = capture the opposing King. No check, no checkmate, no Try.

## Wire format

The page's internal position encoding matches
`engine/gen_golden.py` and `solver/src/lib.rs`:

```
<16 cells>;<P1 hand>;<P2 hand>;<stm 1|2>
  cells : index i=0..15, r=i//4+1 (outer), c=i%4+1 (inner). '.'=empty,
          else a letter, UPPER=P1 / lower=P2 (K P T R F O B N G).
  hand  : 4 digits, order carp,tapir,raccoon,fox.
start : KFRTP......ptrfk;0000;0000;1
```

Each generated move carries its child position (for navigation), `from`/`to`
squares, readable `notation`, and `capture` / `promo` / `jump` / `terminal`
flags.

## Pieces of this directory

| file | what |
|---|---|
| `index.html` | the single-file SVG viewer and vanilla JS rules engine |
| `serve.py` | stdlib local static server; also keeps an oracle-backed `/api?pos=` endpoint for compatibility/testing |
| `og.png` / `og.svg` | social preview image and its editable SVG source |
| `pieces/` | official Shogi4 piece art (public domain) + `CREDITS.txt`; `dark/` = darker-card variants |
| `test_codec.py` | codec/move-set agreement vs `engine/golden.txt` (4,000 positions) |
| `test_static_engine.mjs` | browser rules-engine agreement vs `engine/golden.txt` (4,000 positions) |

## Trust

The canonical correctness check still rests on the oracle. `python3
explorer/test_codec.py` re-derives the legal moves for all 4,000 golden positions
through the shared codec and asserts they match the oracle's recorded sets (and
that positions round-trip). `node explorer/test_static_engine.mjs` runs the same
golden corpus against the static page's JavaScript move generator.
