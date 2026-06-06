# Shogi4 on Fairy-Stockfish

A playable, **validated** Shogi4 engine built by patching
[Fairy-Stockfish](https://github.com/fairy-stockfish/Fairy-Stockfish) to add the one
rule its variant config can't express — the **friendly-jump** — plus a `shogi4.ini`
variant definition. Gives us a second, independent move generator (a partial oracle
the project otherwise lacks), engine-vs-engine sampled games, and a path to in-browser
play on mistboard.com.

## Why a patch was needed

Everything else in Shogi4 maps onto stock Fairy-Stockfish: the 4×4 board, the piece
moves, drops + capture-to-hand, mandatory promotion on the far rank, and **win by
capturing the king** (modeled as `extinctionValue=loss` on a *non-royal* king, so
there is no check rule — moving your king into capture range is legal, exactly as in
Shogi4). The single exception is the friendly-jump: *in any direction a piece already
steps, if an adjacent square holds a **friendly** piece, it may leap to the square two
steps out* (capture allowed on landing; no enemy hops; no chaining). FSF's grasshopper
hops over a piece of **either** colour and has no friendly-only modifier, so the rule
is genuinely inexpressible in config alone.

## The patch (`Fairy-Stockfish/` fork, 5 edits, 4 files)

A new variant rule `friendlyJump`:

- `src/variant.h` — `bool friendlyJump` field.
- `src/parser.cpp` — parse `friendlyJump` from the `.ini`.
- `src/variant.cpp` — force the slow attack path (`fastAttacks=false`) when it's on.
- `src/position.h` — `friendly_jumps()` helper + calls in `attacks_from` / `moves_from`.

`friendly_jumps()` takes the piece's base step bitboard, finds the step squares that
hold a friendly piece (the "screens"), and for each adds the landing square obtained by
**reflecting the origin through the screen** (`target = 2·screen − origin`). That keeps
the jump in the piece's own directions, lands it exactly two steps out, and — because
it reflects through the *current* move bitboard — automatically follows a promoted
piece's (silver/gold) movement. The existing capture/quiet split in `generate_moves`
then routes a jump-onto-enemy to a capture and a jump-onto-empty to a quiet for free.
Sound only for single-step leapers, which is all Shogi4 has.

## `shogi4.ini`

Pieces: king = non-royal `commoner`; `carp fW`, `tapir fWfF`, `raccoon F`, `fox W` as
custom pieces; promoted movers `silver FfW` / `gold WfF`. `promotedPieceType` maps each
base to its promoted mover; FSF stores a promoted piece *as* the mover type while
remembering its base, so three bases can all promote to silver yet revert correctly on
capture. Promoted pieces print as `+P/+T/+R/+F` (= koi/baku/tanuki/kitsune). Drops are
banned on the opponent's last rank via `dropRegion*` (the sole drop restriction).

## Build (native)

The durable source of truth for the engine change is **`shogi4-friendlyjump.patch`**
(36 lines) against upstream Fairy-Stockfish at pinned commit
`1b5bdd40499bd5c7417bdc532d52fef8847bdf3f`. The `Fairy-Stockfish/` directory is just a
working checkout reproducible from that patch — to rebuild from scratch:

```bash
./build-shogi4-engine.sh /tmp/fsf       # clone pinned SHA, apply patch, build
```

Or, in an existing checkout:

```bash
cd Fairy-Stockfish/src
make -j build ARCH=apple-silicon        # or your arch; see `make help`
```

Load it:

```
setoption name VariantPath value <abs path>/shogi4.ini
setoption name UCI_Variant value shogi4
position startpos
go movetime 1000
```

## Validation — move-equivalent to the oracle

The oracle is `../engine/shogi4.py`, a faithful port of the decompiled official app
(`../research/prior-art-evidence/oca-shogi4-logic-decompiled.py`). Run:

```bash
python3 diff_test.py          # perft(1..6) + 4000-position move-set diff
```

Results (both green):

- **perft(1..6) from the start = 8 / 64 / 624 / 6,283 / 68,398 / 765,249**, identical to
  the oracle once terminal semantics are aligned (a king-capture ends the line; the
  oracle counts it as a leaf, FSF as a terminal node — a *definition* difference, not a
  move-gen one).
- **0 mismatches** across all 4,000 golden positions (captures, drops, promotions,
  friendly-jumps, hands).
- `find_divergence.py` / `transition_test.py` further confirm identical move **sets**
  and identical move **application** at every position/transition through depth 4.

## Sampled games

```bash
python3 self_play.py [num_games] [out_file] [movetime_ms]   # -> games.txt
```

One game per line: `<result> <ply-count> <UCI moves>` (`1-0` = White / Player 1 wins).

## In-browser play on mistboard.com (WASM) — next step

Needs the **emscripten** toolchain (`emsdk`), not yet installed. Two options:

1. **Engine-in-WASM** (to *play* against): build our patched `src/` with the
   [`fairy-stockfish.wasm`](https://github.com/fairy-stockfish/fairy-stockfish.wasm)
   setup → a `.wasm` + JS loader that speaks UCI in the browser (as pychess.org does).
   Ship `shogi4.ini` and load it at runtime via `setoption VariantPath` / the JS
   `loadVariantConfig`.
2. **ffish.js** (board logic / legal moves / SVG, no search): build `src/ffishjs.cpp`
   with emscripten (see `Fairy-Stockfish/tests/js`). Good for the move UI; pair with
   option 1 for an opponent.

The friendly-jump patch is in the C++, so **either WASM artifact must be built from
this fork**, not from upstream/npm.
