# shogi4

> Research project: scope and compute the **first complete strong solution** of **Shogi4** —
> Oca Studios' public-domain 4×4 animal drop-shogi. Treat it like science: every number carries
> its source, estimates are bracketed, and the exact ruleset is nailed before anything is solved.

This is the third entry in a small-shogi solving trilogy:

| Repo | Game | Board | State-space (reachable) | Solve regime |
|---|---|---|---|---|
| [`dobutsu-shogi`](../dobutsu-shogi) | Dōbutsu Shōgi | 3×4 (12 sq) | 246,803,167 *(measured)* | laptop, ~75 min |
| **`shogi4`** *(this repo)* | **Shogi4** | **4×4 (16 sq)** | **~3×10¹³ *(upper 2.05×10¹⁴ exact)*** | **external-memory, ~8 TB** |
| [`micro-shogi`](../micro-shogi) | Micro Shogi | 4×5 (20 sq) | ~5×10¹⁴ *(bracketed)* | ~16-node cluster, ~$10–15k |

Shogi4 sits between them — and the enumerator shows it's a genuine **external-memory** solve
(~8 TB W/L/D), only ~15–20× smaller than Micro Shogi: finishable on one high-memory or NVMe
machine rather than a cluster, but well past the laptop regime. (An earlier scaffolding guess of
"~10⁹–10¹¹, RAM-resident" was wrong by 3–4 orders of magnitude — the enumerator corrected it.)

## Why Shogi4 is worth solving

- **It has never been solved.** No academic paper, no published game value, no oracle. The
  strong solution — is it a first- or second-player win, or a draw, and in how many plies — is
  a genuinely new result. Nobody knows the answer yet.
- **It's public domain.** Oca Studios released the whole "Four" series under public domain, so
  we're free to solve it, fork it, and publish the result, crediting Oca.
- **It's a different game, not "wider Dōbutsu."** Shogi4 has a **friendly-jump** rule (pieces
  leap over their own pieces — Dōbutsu has nothing like it), promotion for four of five piece
  types, a drop restriction, and **no "Try"/king-march win** (Dōbutsu has one). The move model
  is meaningfully different, which is most of the engineering.

## The challenge (what makes this non-trivial)

1. **Recovering the exact ruleset from the primary source.** Solving the wrong rules is
   worthless. Oca's print-and-play PDF and per-piece movement diagrams are the ground truth —
   and at scaffold time the live server is down and the PDF was never archived. Three specifics
   are still open (see [`research/open-questions.md`](research/open-questions.md)).
2. **A bigger board with a different move model.** 16 squares, one extra piece type per side,
   friendly-jump move generation — the Dōbutsu solver has to be re-derived, not just re-pointed.
3. **No oracle.** Unlike Dōbutsu (checkable against Tanaka and clausecker), correctness here has
   to be *manufactured*: brute-force forward minimax on small positions, two independent
   implementations, and full-table consistency audits.

## Status

**Scoping.** No solver yet. The cheap, high-leverage milestones come first:

1. **Recover the exact ruleset** from Oca's primary source — starting setup, every piece's
   movement (regular + evolved), and the drop restriction. **This gates everything.**
   *(✅ done — decompiled from the official Oca app `com.ocastudios.shogi4`; see `research/`)*
2. **Rules engine + validation.** Python reference (`engine/`, the oracle — a port of the
   decompiled app), Rust engine (`solver/`), perft, and a two-solver + audit correctness gate.
   *(✅ done — Rust perft matches the oracle to the digit + a 4,000-position golden diff passes;
   retrograde == value-iteration + clean audit on subgames up to 1.16M positions.)*
3. **State-space enumerator** — reproduce Tanaka's Dōbutsu upper bound to the digit, then count
   Shogi4. *(✅ done — upper bound 2.05×10¹⁴ exact; reachable ~3×10¹³; ~8 TB W/L/D. Exact reachable
   awaits the full solve. See `research/repro/`.)*
4. **Full strong solve** (W/L/D + DTM) — external-memory retrograde on one high-memory/NVMe machine
   (~2–6 core-years, ~8 TB), reusing the Dōbutsu pipeline. *(open — the first real compute spend)*
5. **Explorer + article**, reusing the Dōbutsu formats. *(open)*

## Layout

```
engine/                — Python reference engine (the oracle): move-gen, perft,
  shogi4.py              retrograde + value-iteration subgame solvers, audit
  gen_golden.py          golden position->moves generator for cross-language testing
  golden.txt             4,000 oracle positions+moves (the Rust diff fixture)
solver/                — Rust engine (validated to the digit); grows into the solver
  src/lib.rs             rules engine + perft + golden verifier
  src/main.rs            perft + golden differential-test driver
research/
  findings.md          — verified facts ledger (numbers + sources, confidence-tagged)
  open-questions.md    — the backlog (Q1 ruleset resolved; solve-correctness contract in Q5)
  prior-art.md         — the 4×4 landscape: Shogi4's recovered rules, other 4×4 attempts, why
                         there's no canonical 4×4 and none on Wikipedia
  prior-art-evidence/  — committed primary-source artifacts (Oca board graphic, decompiled logic)
```

## Primary source

Shogi4 — Oca Studios, "Four" series (public domain) · <https://ocastudios.com/four/shogi/>
· BGG <https://boardgamegeek.com/boardgame/146291/shogi4>

---

Built by Brian Liou with Claude (Anthropic) — sibling to `dobutsu-shogi` and `micro-shogi`.

> Note: this README is a working scoping doc. The polished public hero gets drafted via the
> `draft-voice` skill when the project nears distribution.
