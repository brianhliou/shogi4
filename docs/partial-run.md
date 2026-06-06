# Partial run — runbook (prepared, not yet executed)

A one-off rented-box solve of the largest meaningful sub-game, to turn the
51.5M laptop ceiling into a **billions-scale** headline number and a real-hardware
ns/edge for the cost model. Single machine, single thread, no distributed moving
parts — the cheapest credible result upgrade. **Status: prepared. Do not run until
you decide to proceed.**

## Target

`{2 kings + carp + fox + raccoon + tapir}` — one of each base type.

- Rank domain **N = 3,523,223,040** (~3.5B), ~3B legal. Fits `u32` (< 4.29B), which
  is why the work queue is `u32` for this run.
- Bin: `partial PTRF` (default arg is `PTRF`).

## Box

Single-threaded, so cores don't matter — pick for **RAM**. Peak memory:

| array        | type       | size for N=3.5B |
|--------------|------------|-----------------|
| `val`        | `Vec<u8>`  | ~3.5 GB         |
| `cnt`        | `Vec<u16>` | ~7.0 GB         |
| `legal`      | `Vec<bool>`| ~3.5 GB         |
| work queue   | `VecDeque<u32>` | up to ~14 GB worst case (realistically less — only the live frontier) |

Fixed arrays ~14 GB; +queue → **~18–28 GB peak**.

- **Safe:** Hetzner Cloud **CCX43** (16 vCPU / **64 GB**, ~€0.32/hr). No OOM risk at
  hour 5.
- **Cheaper gamble:** **CPX51** (16 vCPU / **32 GB**, ~€0.11/hr) — likely fits with
  the `u32` queue, but tight; OOM kills the whole run.

Recommend the 64 GB box for a one-off; the few extra cents buy certainty. *(Verify
current Hetzner instance specs/prices at provisioning — they drift.)*

**Expected:** ~3–8 hours single-threaded; **~$1–3** total. If you want it faster
later, parallelize (deferred — not worth the concurrency risk for one number).

## Commands

On the box (Ubuntu 24.04):

```bash
sudo apt-get update && sudo apt-get install -y build-essential git tmux
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
```

Get the crate. Repo is private, and `partial` needs **only the `solver/` crate**
(no `engine/` fixtures — it solves, it doesn't diff). Simplest is to rsync just
that dir from the laptop:

```bash
# from the laptop:
rsync -av ~/projects/shogi4/solver/ <box>:~/shogi4-solver/
```

Build + run inside `tmux` (so an SSH drop doesn't kill a multi-hour run); progress
streams on stderr, the result is `tee`'d to a file:

```bash
cd ~/shogi4-solver
cargo build --release --bin partial
tmux new -s solve
SHOGI4_PROGRESS=1 ./target/release/partial PTRF | tee ~/shogi4-result.txt
# detach: Ctrl-b then d   ·   reattach: tmux attach -t solve
```

`partial` flushes the result before exit, so the `tee`'d file is complete even
if the pipe is redirected. Live `init N% / propagated …` lines on stderr confirm
it's alive and let you estimate completion.

When it finishes, pull the result back and **destroy the box**:

```bash
# from the laptop:
scp <box>:~/shogi4-result.txt ~/projects/shogi4/research/partial-run-result.txt
```

## What to record

Into `research/findings.md`:

- The sub-game **W/L/D** (the billions-scale headline number).
- The **real-hardware ns/edge** (`partial` prints an estimate at b~13; for the exact
  edge count, cross-check against the `scale` calibration).
- Wall-clock + pos/s — feeds the full-solve core-years / cost estimate with a
  measured constant instead of a laptop-extrapolated one.

## Smoke test first (optional, ~seconds, on the laptop)

`./solver/target/release/partial PF` → must print `W 867856  L 206964  D 89884`
(the known `{2K+carp+fox}` answer). Confirms the binary before you pay for a box.
