# Prior art — the 4×4 shogi landscape

Why this matters: Shogi4 is an *existing* game, so we are the **solver/explainer**, not the
originator (the same relationship `../dobutsu-shogi` has to Tanaka). This file is the honest
record of what already exists at 4×4 — both so we credit correctly and so a future "design our
own variant" effort (open-questions Q7) has a clean baseline.

## The subject: Shogi4 (Oca Studios, public domain)

The recovered ruleset lives in `findings.md` (with confidence tags and the three open gaps in
`open-questions.md` Q1). In one line: a **Dōbutsu-lineage 4×4 animal drop-shogi** — flip-tiles,
ownership by orientation, drops ("farm"), flip-promotion — that **diverges from Dōbutsu** via a
**friendly-jump** rule, promotion for four of five piece types, a drop restriction, and **no
"Try" win** (king-capture only).

Distribution: free **print-and-play ("bronze")** PDF + a free **electronic/app** version, all
public domain. Part of Oca's **"Four" series** of kids' remixes of classic games. Never solved;
no academic treatment.

Primary-source evidence committed: `prior-art-evidence/oca-shogi4-board-strip.png` (Oca's own
instructional graphic, public domain).

## The other 4×4 attempt: "Shogi 4×4" (TatApp, Android)

A **different game**, not a variant spelling of Shogi4 — it diverges on all three axes that
define a shogi variant:

- **Pieces:** traditional shogi (King/Gold/Silver/…), not animals.
- **Starting position:** **randomized every game** ("the placement of pieces is different each
  time") — so it has no fixed opening at all.
- **Intent:** a **blitz/puzzle app** (10-second and 3-minute modes), not a fixed competitive game.

Consequence for solving: a randomized-setup game can't be "solved as a game" — only as a full
all-positions tablebase. Shogi4, with its fixed setup, is the one existing 4×4 that *can* be
strongly solved as a single game. (Google Play: `com.TatApp.JPChess44`.)

## Red herrings (a "4" in the name, but not 4×4)

- **Micro Shogi = 4×5**, not 4×4 — the canonical small variant and the subject of
  `../micro-shogi`. Some search engines mislabel it 4×4; it is not.
- **Sigma 4 Shogi = 7×7** — the "4" is stones-per-piece, not the board.

## Why there's no *canonical* 4×4, and none on Wikipedia

- **No canonical ruleset exists** because the two real attempts went opposite directions (Oca's
  designed children's board game vs. TatApp's randomized blitz app) and neither built a fixed
  competitive ruleset with a community. 4×4 never got its "Kitao moment" the way Dōbutsu did.
- **Not on Wikipedia** is a *notability gate, not an oversight.* Wikipedia's
  [General Notability Guideline](https://en.wikipedia.org/wiki/Wikipedia:Notability) requires
  *significant coverage in reliable secondary sources independent of the subject.* The listed
  small variants (Dōbutsu 3×4, Micro 4×5, Mini/Kyoto 5×5, 9-grid 3×3) each have that —
  historical documentation, notable designers, commercial publication, and in Dōbutsu's case an
  academic solve (Tanaka 2009) plus news coverage. The 4×4 games are documented only on hobbyist
  wikis and app stores, which Wikipedia treats as self-published/primary. Same reason Bushi
  (1×2), Gufuu (2×3), and Nana (3×3) are absent despite existing.
- **Implication for us:** the honest path to recognition isn't "claim the 4×4 board" — it's the
  *Dōbutsu route*: produce a result (the first strong solution of a specific 4×4 ruleset) strong
  enough to draw independent coverage. Coverage follows the result, not the artifact.

## Sources

- Oca Shogi4 (primary, via Wayback 2024-09-26): <https://ocastudios.com/four/shogi/>
- BGG — Shogi4: <https://boardgamegeek.com/boardgame/146291/shogi4>
- TatApp Shogi 4×4: <https://play.google.com/store/apps/details?id=com.TatApp.JPChess44>
- Sigma 4 Shogi (7×7): <https://www.chessvariants.com/rules/sigma-4-shogi>
- Wikipedia Shogi variant list: <https://en.wikipedia.org/wiki/Shogi_variant>
- Wikipedia notability: <https://en.wikipedia.org/wiki/Wikipedia:Notability>
