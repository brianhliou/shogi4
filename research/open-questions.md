# Open questions — Shogi4

The backlog. Resolve with primary sources or our own reproducible experiments — never paper over
in prose. Q1 is **gating**: nothing downstream is trustworthy until the exact rules are pinned.

---

## Q1 — Exact ruleset (GATING) 🔴

Most of Shogi4's rules are recovered (see `findings.md`), but **three solve-critical specifics
are still missing**, all locked in Oca's print-and-play PDF + per-piece tile images:

- **Q1a — Starting setup.** Which animal sits on which of the 16 squares for each player. The
  recovered board graphic is an *instructional strip*, not the setup diagram. **[blocking]**
- **Q1b — Movement diagrams.** Exact directions for **Tapir, Raccoon-dog, Fox** (regular) and the
  **four evolved forms**. Carp (forward) and the royal (any direction) are confirmed; the rest are
  only secondary-guessed. A solver cannot generate moves without these. **[blocking]**
- **Q1c — Drop restriction.** Rules text says "not on the opposing side of the board"; the board
  graphic says "never to the last row." Resolve which (opponent's half vs. back rank). **[blocking]**

**Why blocked now:** Oca's live server is down (connection refused at scaffold time) and the PnP
PDF (`.../releases/version 0-1-0/Four-Shogi4-0-1-0-EN.pdf`) was **never captured** by the Wayback
Machine (CDX confirms only board1.png, the two royal images, and logo were archived).

**Routes already attempted and RULED OUT (don't re-walk these):**
- ❌ Live Oca server (page + EN/US PDF) — connection refused (HTTP 000); earlier Cloudflare 52x.
- ❌ Wayback PnP PDF — not archived under either host (`ocastudios.com` / `www.ocastudios.com`),
  any timestamp (broad CDX prefix sweep, empty).
- ❌ Archived web-app `ocastudios.com/four/shogi/app/` (2020-11-30) — only the landing HTML was
  captured (links to Play Store + screenshots); no JS/JSON rule data, screenshots not archived.
- ❌ Official Oca app `com.ocastudios.shogi4` on Google Play — listing returns empty (**delisted**).

**Remaining routes (need external availability or human action):**
1. **Retry the live Oca server later** — outage looked transient; the PDF + app live there.
   Cheapest *if* it recovers. Worth a periodic re-poll.
2. **Email Oca Studios** — small free-culture studio; likely to share the PnP PDF directly. (Draft
   ready on request.)
3. **BGG file section** for Shogi4 — community-uploaded PnP PDFs sometimes live there (BGG blocks
   automated fetch; needs a manual/logged-in pull).
4. **Buy/inspect the live TatApp app** is **not** a route — that's the *other*, randomized-setup
   4×4 game, not Shogi4 (see `prior-art.md`).

Until Q1 is closed, the engine is built against a **clearly-flagged provisional ruleset** and
re-validated the moment the primary source lands.

---

## Q2 — Exact reachable count

Port the validated enumerator from `../micro-shogi/research/repro/`, **reproduce Tanaka's Dōbutsu
upper bound (1,567,925,964) to the digit**, then count Shogi4's arrangements and reachable
positions. Pins the ~10⁹–10¹¹ estimate and the RAM footprint (→ workstation vs. needs-big-RAM).
Depends on Q1b (promotion/movement affect which arrangements are legal/reachable).

## Q3 — The game value

Is Shogi4 a **first-player win, second-player win, or draw**, and in how many plies (DTM)? The
headline result. Unknown — no prior solve exists. Depends on Q1 + a correct solver.

## Q4 — Is it degenerate?

Tiny drop-shogi can collapse into a trivial fast win or a dead draw. Does Shogi4's specific combo
(friendly-jump + 4-of-5 promotion + drop limit + **no Try rule**) yield a balanced game or a short
forced result? A short forced win is still a clean, publishable finding — not a failure.

## Q5 — Correctness without an oracle

There is no external Shogi4 solution to check against. Define the correctness regime before the
full solve: (a) brute-force forward minimax agreeing with the retrograde table on all small
positions; (b) two independent move-gen/solver implementations agreeing; (c) full-table
consistency audits (every win has a winning move; every loss has all moves losing; parity/DTM
monotonicity). Inherited contract from `../micro-shogi`.

## Q6 — Does friendly-jump change the retrograde unmove generation?

Forward moves include jumps over friendlies; **retrograde analysis must invert them correctly**
(the un-jump predecessor set differs from sliding/stepping pieces). Verify the unmove generator
against the forward generator on random positions before trusting any backward pass.

## Q7 — Relationship of Shogi4 to a possible *original* variant

Out of scope for the solve, but noted: once Shogi4 is solved, designing and solving an *original*
fixed-setup 4×4 (where we are the originator, not the solver/explainer) is a natural follow-on,
with Shogi4 as the prior-art baseline. Tracked, not pursued here yet.
