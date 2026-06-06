#!/usr/bin/env python3
"""Generate the Shogi4 rules-article engine-game stepper data.

Reads a recorded engine self-play replay (engine/game-strong.txt — a real
friendly-jump Fairy-Stockfish game) and emits a TS module of per-ply frames.
Each frame is one inline SVG: the 4x4 board (Oca tiles, same style as
gen_rules_diagrams.py) with a komadai (hand) tray above for gote and below for
sente, plus a short narration that is just the move. The mistboard rules article
feeds these to its `raw-svg-stepper` block.

Writes: ../mistboard/apps/web/src/shogi4-sample-game.ts
Regenerate: python3 tools/gen_game_replay.py
"""
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "engine", "game-strong.txt")
OUT = os.path.join(ROOT, "..", "mistboard", "apps", "web", "src", "shogi4-sample-game.ts")

URL = "/shogi4/pieces"
BOARD_FILL, FRAME, GRID, HL, LABEL, FARM = "#f4ead2", "#c9b07f", "#ddcca6", "#f6d873", "#9a8c6a", "#efe2c4"
CELL = 72

TILE = {"K": "crane", "P": "carp", "T": "tapir", "R": "raccoon", "F": "fox",
        "O": "koi", "B": "baku", "N": "tanuki", "G": "kitsune"}
KING2 = "pheasant"                              # gote royal: its own (light) tile, rotated
DARK = {"carp", "tapir", "raccoon", "fox"}      # only the base pieces have dark/ tiles
HAND_BASE = {"P": "carp", "T": "tapir", "R": "raccoon", "F": "fox"}   # hand pieces are always base
HDR = re.compile(r"^--- ply\s+(\d+)\s+(White|Black)\s+(\S+)\s+eval\s+\S+\s+\(d\d+\)(?:\s+\[[^\]]*\])?")


def tile_for(ch):
    owner = 1 if ch.isupper() else 2
    if ch.upper() == "K":
        return owner, ("crane" if owner == 1 else KING2)
    return owner, TILE[ch.upper()]


def piece_img(name, x, y, size, rot_center=None):
    rot = f' transform="rotate(180 {rot_center[0]:.1f} {rot_center[1]:.1f})"' if rot_center else ""
    return (f'<image href="{URL}/{name}.png" x="{x:.1f}" y="{y:.1f}" '
            f'width="{size:.1f}" height="{size:.1f}"{rot}/>')


def parse_hand(h):
    out = []
    if h and h != "-":
        for tok in h.split():
            letter, _, cnt = tok.partition("x")
            out.append((letter.upper(), int(cnt) if cnt else 1))
    return out


def hand_tray(items, ml, tray_w, ty, th, owner):
    """A komadai strip: captured base pieces as small tiles, count-badged."""
    s = [f'<rect x="{ml}" y="{ty}" width="{tray_w}" height="{th}" rx="6" fill="{FARM}" opacity="0.55"/>']
    size = 40
    x, y = ml + 8, ty + (th - size) / 2
    for letter, cnt in items:
        tile = HAND_BASE[letter]
        if owner == 2:
            s.append(piece_img(f"dark/{tile}", x, y, size, (x + size / 2, y + size / 2)))
        else:
            s.append(piece_img(tile, x, y, size))
        if cnt > 1:
            bx, by = x + size - 7, y + size - 7
            s.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="8" fill="#3a352c"/>')
            s.append(f'<text x="{bx:.1f}" y="{by+3.5:.1f}" text-anchor="middle" fill="#fff" '
                     f'font-family="system-ui,sans-serif" font-size="11" font-weight="700">{cnt}</text>')
        x += size + 8
    return s


def render_frame(cells, h1, h2, frm, to, fid):
    ml, mr, pad, th = 24, 14, 8, 48
    span = 4 * CELL
    btop = pad + th + 8                         # board top y
    wtray = btop + span + 22                    # sente (bottom) tray y
    W, H = ml + span + mr, wtray + th + 6
    tray_w = span
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" '
         f'style="max-width:400px;margin:0 auto" role="img" class="shogi4-diagram">']
    s += hand_tray(parse_hand(h2), ml, tray_w, pad, th, 2)        # gote hand, above
    s.append(f'<rect x="{ml}" y="{btop}" width="{span}" height="{span}" rx="9" '
             f'fill="{BOARD_FILL}" stroke="{FRAME}" stroke-width="2"/>')
    # last-move highlight: full-cell squares (flush to the grid), clipped to the
    # board's rounded outline so corners round only where the board frame does.
    # Drawn before the grid lines and pieces, so the tiles sit on top.
    hls = []
    for sq_ in (frm, to):
        if sq_:
            c, r = sq_
            x, y = ml + (c - 1) * CELL, btop + (4 - r) * CELL
            hls.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{HL}" opacity="0.55"/>')
    if hls:
        s.append(f'<clipPath id="s4hl{fid}"><rect x="{ml+1}" y="{btop+1}" width="{span-2}" height="{span-2}" rx="8"/></clipPath>')
        s.append(f'<g clip-path="url(#s4hl{fid})">' + "".join(hls) + "</g>")
    for i in (1, 2, 3):                            # inset 1px so lines stop flush at the inner frame edge
        s.append(f'<line x1="{ml+i*CELL}" y1="{btop+1}" x2="{ml+i*CELL}" y2="{btop+span-1}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'<line x1="{ml+1}" y1="{btop+i*CELL}" x2="{ml+span-1}" y2="{btop+i*CELL}" stroke="{GRID}" stroke-width="1"/>')
    for ci, ch in enumerate(cells):
        if ch == ".":
            continue
        r, c = 4 - ci // 4, ci % 4 + 1
        x, y = ml + (c - 1) * CELL, btop + (4 - r) * CELL
        size = CELL * 0.96
        ox, oy = x + (CELL - size) / 2, y + (CELL - size) / 2
        owner, tile = tile_for(ch)
        if owner == 2:
            name = tile if tile == KING2 or tile not in DARK else f"dark/{tile}"
            s.append(piece_img(name, ox, oy, size, (x + CELL / 2, y + CELL / 2)))
        else:
            s.append(piece_img(tile, ox, oy, size))
    for c in range(4):
        s.append(f'<text x="{ml+c*CELL+CELL/2:.1f}" y="{btop+span+15}" text-anchor="middle" '
                 f'fill="{LABEL}" font-family="system-ui,sans-serif" font-size="12">{"abcd"[c]}</text>')
    for r in range(4):
        s.append(f'<text x="{ml-10}" y="{btop+(3-r)*CELL+CELL/2+4:.1f}" text-anchor="middle" '
                 f'fill="{LABEL}" font-family="system-ui,sans-serif" font-size="12">{r+1}</text>')
    s += hand_tray(parse_hand(h1), ml, tray_w, wtray, th, 1)      # sente hand, below
    s.append("</svg>")
    return "\n".join(s)


def sq(tok):
    return (ord(tok[0]) - ord("a") + 1, int(tok[1]))


def move_label(p):
    if p is None:
        return "Starting position"
    mv = p["move"]
    if "@" in mv:
        letter, dst = mv.split("@")
        return f"{p['ply']}. {letter.upper()}@{dst}"
    promo = "+" if mv.endswith("+") else ""
    a, b = mv[:2], mv.rstrip("+")[2:4]
    return f"{p['ply']}. {a}→{b}{promo}"


def parse_game(path):
    plies, pend, rows, h1, h2, inb = [], None, [], "-", "-", False
    with open(path) as f:
        for line in f:
            s = line.rstrip("\n")
            m = HDR.match(s)
            if m:
                pend = {"ply": int(m[1]), "mover": m[2], "move": m[3]}
                continue
            if "black hand:" in s:
                rows, inb = [], True
                h2 = s.split("black hand:")[1].strip()
                continue
            if inb and re.match(r"\s*[1-4]\s", s):
                rows.append(s.split()[1:5])
                continue
            if "white hand:" in s:
                h1 = s.split("white hand:")[1].strip()
                plies.append(([c for row in rows for c in row], h1, h2, pend))
                pend, inb = None, False
    return plies


def main():
    steps = []
    for fid, (cells, h1, h2, p) in enumerate(parse_game(GAME)):
        if p is None:
            frm = to = None
        elif "@" in p["move"]:
            frm, to = None, sq(p["move"].split("@")[1])
        else:
            mv = p["move"].rstrip("+")
            frm, to = sq(mv[:2]), sq(mv[2:4])
        steps.append((render_frame(cells, h1, h2, frm, to, fid), move_label(p)))

    title = ("Fairy-Stockfish self-play on the friendly-jump engine (this site's patched build). "
             "White wins in 73 plies; the mating move is itself a friendly jump.")
    body = ["// GENERATED by shogi4/tools/gen_game_replay.py — do not edit by hand.",
            "// A real friendly-jump Fairy-Stockfish self-play game (engine/game-strong.txt)",
            "// for the Shogi4 rules article: per-ply Oca-tile board frames (with hand trays).",
            "// Regenerate (from the shogi4 repo): python3 tools/gen_game_replay.py",
            "",
            f"export const SHOGI4_GAME_TITLE = {ts_str(title)};",
            "",
            "export const SHOGI4_GAME_STEPS: { svg: string; narrative: string }[] = ["]
    for svg, narr in steps:
        body += ["  {", f"    svg: {ts_tpl(svg)},", f"    narrative: {ts_str(narr)},", "  },"]
    body.append("];")
    with open(OUT, "w") as f:
        f.write("\n".join(body) + "\n")
    print(f"wrote {OUT} — {len(steps)} frames")

    mb = os.path.join(ROOT, "..", "mistboard")
    try:
        subprocess.run(["npx", "biome", "format", "--write", os.path.relpath(OUT, mb)],
                       cwd=mb, check=True, capture_output=True, text=True)
        print("formatted with biome")
    except Exception as e:  # noqa: BLE001 — best-effort; the file is still valid TS
        print(f"warning: biome format skipped ({e}); run it manually in mistboard")


def ts_str(s):
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def ts_tpl(s):
    return "`" + s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${") + "`"


if __name__ == "__main__":
    main()
