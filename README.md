# Shogi4: a strong-solution engine for 4×4 drop-shogi

Shogi4 is a public-domain 4×4 drop-shogi by Oca Studios. This repo is a complete, oracle-validated strong-solution engine for it. Its rules, lost when the publisher's app was delisted, were recovered by decompiling that app; the solver was built from scratch, cross-checked three ways against an independent implementation, and run at 2.1 billion positions on rented hardware. The full solve is designed, verified in simulation, and calibrated, but not run: it would take roughly 50 to 100 TB and 130 to 190 core-years, which the result does not justify.

A narrative writeup (*Partially Solving Shogi4*) is on [brianhliou.com](https://brianhliou.com), and the recovered rules are at [mistboard.com/articles/shogi4](https://mistboard.com/articles/shogi4).

The third entry in a small-shogi solving trilogy:

| Repo | Game | Board | Reachable positions | Solve regime |
|---|---|---|---|---|
| [dobutsu-shogi](https://github.com/brianhliou/dobutsu-shogi) | Dōbutsu Shōgi | 3×4 | 246,803,167 | solved, in memory |
| **shogi4** (this) | **Shogi4** | **4×4** | **~3×10¹³** | external-memory, ~50–100 TB, designed not run |
| micro-shogi | Micro Shogi | 4×5 | ~10¹⁵ | open frontier |

## What's here

- **A from-scratch rules engine** (Rust in `solver/`, Python reference oracle in `engine/`), recovered from the decompiled app and cross-validated: perft matches to the digit, a 4,000-position differential test passes with zero mismatches, and three independent solvers agree to the unit.
- **A dense-rank index** (position ↔ integer bijection), the flat-array replacement for a hash map that lets the value table scale past memory. Its full-game domain is N = 410,297,064,507,360, exactly twice the independent arrangement count.
- **A push-based retrograde solver** over the rank index using un-move generation, plus a **sharded BSP distributed design** validated in simulation: confluent across shard counts, with a verification audit at ~55% of solve cost and deterministic crash recovery.
- **A sourced research ledger** in [`research/findings.md`](research/findings.md): every number with its provenance.

## Result

The largest solve is a reduced game, the two kings plus one of each piece type (2,100,849,024 positions), on a 16-core / 64 GB box in 5.3 hours:

| Outcome (side to move) | Share |
|---|---|
| Win | 79.15% |
| Loss | 16.16% |
| Draw | 4.69% |

It also calibrates cost per edge at scale (~697 ns/edge out of cache), which anchors the full-solve projection. This is a reduced game used to push the engine far past the small validation subgames; drops conserve material, so the real game never reaches it.

## Reproduce

```bash
cd solver
cargo test --release
```

Ten tests reproduce every correctness claim: perft, the cross-language oracle diff, all three solvers agreeing, the rank bijection, un-move generation, the left-right symmetry fold, and the verification audit.

## Layout

```
solver/      Rust engine, solver, and the validation suite (the production artifact)
engine/      Python reference oracle (a port of the decompiled app) + golden fixtures
research/    findings.md (sourced ledger), open questions, prior art, run logs
docs/        the research brief and the partial-run runbook
explorer/    interactive board / rules viewer
```

## Source and credits

Shogi4 by Oca Studios, "Four" series, released public domain. Rules recovered from the official app `com.ocastudios.shogi4` and documented at [mistboard.com/articles/shogi4](https://mistboard.com/articles/shogi4).

Built by Brian Liou, sibling to [dobutsu-shogi](https://github.com/brianhliou/dobutsu-shogi). See [`LICENSE`](LICENSE).
