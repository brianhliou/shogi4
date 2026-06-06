# Partial run — runbook

A one-off rented-box solve of the largest meaningful sub-game, to turn the
51.5M laptop ceiling into a **billions-scale** headline number and a real-hardware
ns/edge for the cost model. Single machine, single thread, no distributed moving
parts — the cheapest credible result upgrade.

**Status: DONE — first run executed 2026-06-06**, Hetzner CCX43 (Ubuntu 26.04, 16 vCPU /
64 GB), single-threaded baseline (zero concurrency risk). **2,100,849,024 legal positions;
W 79.15 / L 16.16 / D 4.69 %; 5.29 hr wall; ~697 ns/edge at scale; peak RSS ~15 GB** (`u32`
queue). EXIT=0, W+L+D reconciles to the unit. Numbers folded into `findings.md`; raw output in
`research/partial-run-{result.txt,progress.log}`.

## Before the next run — parallelize first

The single-threaded run used **1 of 16 cores** (the box was sized for the 64 GB,
not the cores — they came bundled). That's the right call for a *one-off* you want
correct on the first try, but **any next run gets parallelized first** — don't start
another multi-hour solve on one core.

- **Init pass — embarrassingly parallel, do it.** Every position is independent
  (unrank → is_legal → count children → seed terminals). `rayon` over the rank
  range is near-linear: ~39 min → ~4–5 min. Low risk; the per-position work is pure.
- **Propagation — use the validated sharded BSP solver, not the sequential one.**
  The design is already built and de-risked (`sharded_check` confluence,
  `failrec_check` crash-replay). Wire *that* into the production runner instead of
  the single-`VecDeque` loop in `solve_push_array`.
- **Don't expect 16×.** Propagation is **memory-latency bound** — each pop is a
  random `rank()`/array touch into a multi-GB working set, so you saturate memory
  bandwidth well before core count. Realistic overall speedup ~4–8×. The bigger
  full-solve wins are footprint/locality (2-bit packing, compression, mmap — the
  rung-4 optimizations from `../micro-shogi`), not just more threads.
- **Baseline to beat:** this run's single-threaded wall-clock + ns/edge is the
  reference the parallel version's speedup gets measured against.

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
