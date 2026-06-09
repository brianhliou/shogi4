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

## Deferred work

### In-browser play on mistboard.com (WASM) — deferred 2026-06-06

The rules article ships a watchable recorded game, which covers "see the engine."
Letting visitors *play* the engine in the browser is a separate, larger phase,
deferred for now. Notes for a clean pickup:

**What it is.** Browsers can't run the native `stockfish` binary, so in-browser play
means compiling the C++ engine to WebAssembly with Emscripten — the same thing
pychess.org does to run Fairy-Stockfish for analysis (the `fairy-stockfish.wasm` /
`fairy-stockfish-nnue.wasm` npm package). The output is a `.wasm` module + a JS
worker that speaks UCI from the page.

**Must be built from this fork.** The friendly-jump lives in the C++
(`shogi4-friendlyjump.patch`), so the upstream npm package can't play Shogi4 — the
WASM has to be compiled from the patched `src/`.

**Build path:**
1. Install Emscripten (`emsdk`, ~1–2 GB) — the one missing prerequisite.
2. Apply the patch to a fresh FSF checkout at pinned `1b5bdd40` (reuse the clone +
   `git apply` from `build-shogi4-engine.sh`).
3. Build to WASM, either:
   - **engine-in-WASM** (to play against): the
     [`fairy-stockfish.wasm`](https://github.com/fairy-stockfish/fairy-stockfish.wasm)
     Emscripten build pointed at the patched `src/` → `.wasm` + JS worker; or
   - **ffish.js** (legal-move gen / board logic, no search): `emcc` build of
     `Fairy-Stockfish/src/ffishjs.cpp` (see `Fairy-Stockfish/tests/js`).
4. Load `shogi4.ini` at runtime: `setoption name VariantPath value <ini>` then
   `setoption name UCI_Variant value shogi4` (or ffish.js `loadVariantConfig`).

**Web integration (`mistboard/apps/web`):** run the engine in a Web Worker, add a
small UCI layer (`position … moves …` / `go movetime …` → `bestmove`) and a play UI.
The `raw-svg-stepper` viewer is the rendering precedent; play needs live input + the
worker.

**Maintenance:** a forked WASM build must be rebuilt on each FSF release. The only
way to drop that burden is upstreaming `friendlyJump` (below) so the official
`fairy-stockfish.wasm` carries it.

### Upstreaming the friendlyJump feature — parked

Goal: get `friendlyJump` into upstream Fairy-Stockfish so Shogi4 runs on the official
engine/WASM via a plain `.ini`, with no fork to maintain.

Read on the maintainer (from the repo's PR history, mid-2026): active, but closed to
new *built-in variants* (he directs people to `variants.ini`). A generic *feature*
like ours is a different bucket — he engages and merges if it's simple, POD,
consistent with existing options, focused, and core-safe (cf. PR #792, a
per-piece-region feature that stalled in review iteration, not on principle).
Realistic failure mode is review-stall, not rejection. He personally maintains the
Dōbutsu family (PR #991) — a real hook, since Shogi4 is its 4×4 sibling.

Plan: open a **discussion, not a PR**, leading with the live rules article + the
validation (perft to depth 6, 4,000-position diff), and ask which shape he'd accept:
the minimal variant flag (our patch) or a betza hurdle-color hopper modifier (more
general, likely his preference; bigger, touches the betza parser). Pre-empt the three
known gaps — it only reaches move generation (`attackers_to` doesn't see jumps; fine
here, no check rule), it's a special case the betza parser doesn't know, and it forces
`fastAttacks` off.

Draft discussion post (Ideas category):

> Wondering if a friendly-hurdle hop is something you'd ever want in the engine, or
> whether it's better left to a fork. No expectations either way.
>
> Context: I've been solving Shogi4, Oca Studios' public-domain 4×4 animal drop-shogi
> (the rung above Dōbutsu). It maps cleanly onto a `variants.ini` config except for
> one rule: a piece may leap an adjacent *friendly* piece to the square two beyond
> (anti-congestion, one friendly hurdle, no chaining). The grasshopper hops over
> either color and there's no friendly-only hurdle modifier (per the betza subset in
> #773), so config can't express it.
>
> I have a small working implementation (a `friendlyJump` variant option, ~36 lines,
> off by default), validated against an independent move generator: perft matches to
> depth 6 and 4,000 sampled positions agree exactly. Happy to share the patch and
> numbers if that's useful.
>
> If it's something you'd consider, I don't have a strong view on the form (a minimal
> variant flag, or a hurdle-color modifier on the betza hopper, whichever fits the
> codebase) and I'm glad to do the work. If it's not a fit upstream, no problem, it
> lives fine as a fork. Mostly wanted to ask before assuming either way.
>
> Variant writeup: https://mistboard.com/rules/shogi4
