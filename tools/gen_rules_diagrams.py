#!/usr/bin/env python3
"""Generate the SVG diagrams for the Shogi4 rules page in ../mistboard.

The mistboard article system can't use its board renderer for Shogi4 (that
renderer is hardcoded to 8x8 chess / 9x10 xiangqi), so the rules page embeds
hand-built inline SVG via `raw-svg` blocks. This script emits those SVGs and
copies the authentic public-domain Oca tiles they reference.

Each move diagram is a small board with the piece's tile in the centre and a dot
on every square it can step to (forward = up). The starting-position diagram and
the friendly-jump diagram reuse the same tiles. The dots come from the same move
directions the engine uses, so the diagrams can't drift from the rules.

Outputs (all under ../mistboard):
  apps/web/public/shogi4/pieces/*.png        copied tiles (light + dark variants)
  apps/web/src/shogi4-rules-diagrams.ts       exported SVG-string constants

Run:  python3 tools/gen_rules_diagrams.py
"""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PIECES = os.path.join(ROOT, "explorer", "pieces")
MB = os.path.normpath(os.path.join(ROOT, "..", "mistboard"))
DST_PIECES = os.path.join(MB, "apps", "web", "public", "shogi4", "pieces")
DST_TS = os.path.join(MB, "apps", "web", "src", "shogi4-rules-diagrams.ts")

# URL the SVGs reference at runtime (served from apps/web/public/).
URL = "/shogi4/pieces"

# ---- palette (matches the explorer's warm board, reads on any article theme)
BOARD_FILL = "#f4ead2"
FRAME = "#c9b07f"
GRID = "#ddcca6"
DOT = "#15705c"          # reachable-square dot
LABEL = "#9a8c6a"

# ---- move directions in SCREEN coords: dy = -1 is forward (up). -------------
# Mirrors engine/shogi4.py DIRS, re-expressed with forward = up.
MOVES = {
    "carp":    [(0, -1)],
    "fox":     [(0, -1), (0, 1), (-1, 0), (1, 0)],
    "raccoon": [(-1, -1), (1, -1), (-1, 1), (1, 1)],
    "tapir":   [(0, -1), (-1, -1), (1, -1)],
    "crane":   [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)],
    # evolved
    "silver":  [(0, -1), (-1, -1), (1, -1), (-1, 1), (1, 1)],
    "gold":    [(0, -1), (-1, -1), (1, -1), (-1, 0), (1, 0), (0, 1)],
}
# Which tile sits in the centre of each move diagram.
MOVE_TILE = {
    "carp": "carp", "fox": "fox", "raccoon": "raccoon", "tapir": "tapir",
    "crane": "crane", "silver": "koi", "gold": "kitsune",
}


def img(name, x, y, size, rot_center=None):
    href = f"{URL}/{name}.png"
    el = (f'<image href="{href}" x="{x:.1f}" y="{y:.1f}" '
          f'width="{size:.1f}" height="{size:.1f}"')
    if rot_center is not None:
        cx, cy = rot_center
        el += f' transform="rotate(180 {cx:.1f} {cy:.1f})"'
    return el + "/>"


def _open(W, H, max_w):
    style = f' style="max-width:{max_w}px"' if max_w else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="100%"{style} role="img" class="shogi4-diagram">')


def _grid(bx, by, cell, tile, moves):
    """SVG fragment: a 3x3 board with `tile` centred and a dot on each move,
    its top-left board corner at (bx, by)."""
    span = 3 * cell
    p = [f'<rect x="{bx}" y="{by}" width="{span}" height="{span}" rx="8" '
         f'fill="{BOARD_FILL}" stroke="{FRAME}" stroke-width="2"/>']
    for i in (1, 2):  # interior grid lines
        p.append(f'<line x1="{bx + i * cell}" y1="{by}" x2="{bx + i * cell}" '
                 f'y2="{by + span}" stroke="{GRID}" stroke-width="1"/>')
        p.append(f'<line x1="{bx}" y1="{by + i * cell}" x2="{bx + span}" '
                 f'y2="{by + i * cell}" stroke="{GRID}" stroke-width="1"/>')

    def cxx(col):
        return bx + col * cell + cell / 2

    def cyy(row):
        return by + row * cell + cell / 2

    for dx, dy in moves:
        col, row = 1 + dx, 1 + dy
        p.append(f'<circle cx="{cxx(col):.1f}" cy="{cyy(row):.1f}" '
                 f'r="{cell * 0.12:.1f}" fill="{DOT}"/>')
    size = cell * 0.92
    p.append(img(tile, cxx(1) - size / 2, cyy(1) - size / 2, size))
    return p


def move_grid(piece, max_w=300):
    """One 3x3 board: the piece's tile in the middle, a dot on each target."""
    cell, m = 56, 12
    W = H = 3 * cell + 2 * m
    s = [_open(W, H, max_w)]
    s += _grid(m, m, cell, MOVE_TILE[piece], MOVES[piece])
    s.append("</svg>")
    return "\n".join(s)


def duo(tiles, move_key, max_w=540):
    """Two tiles side by side sharing one move (e.g. the two royals)."""
    cell, m, gap = 56, 12, 24
    span = 3 * cell
    W = 2 * m + 2 * span + gap
    H = 2 * m + span
    s = [_open(W, H, max_w)]
    for i, t in enumerate(tiles):
        s += _grid(m + i * (span + gap), m, cell, t, MOVES[move_key])
    s.append("</svg>")
    return "\n".join(s)


ARROW = "#8a7a55"


def pair_diagram(base_key, evolved_tile, evolved_key, max_w=600):
    """Base piece (left) -> evolved form (right), each a 3x3 move grid with an
    arrow between, so a reader sees what evolves into what and how its move
    changes. Koi/Baku/Tanuki are silvers; Kitsune is a gold."""
    cell, m, arrow = 52, 12, 46
    span = 3 * cell
    bx2 = m + span + arrow
    W = bx2 + span + m
    H = 2 * m + span
    s = [_open(W, H, max_w)]
    s += _grid(m, m, cell, MOVE_TILE[base_key], MOVES[base_key])
    s += _grid(bx2, m, cell, evolved_tile, MOVES[evolved_key])
    y = m + span / 2
    x1, x2 = m + span + 8, bx2 - 8
    s.append(f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2 - 6:.1f}" y2="{y:.1f}" '
             f'stroke="{ARROW}" stroke-width="2.5"/>')
    s.append(f'<path d="M {x2 - 8:.1f} {y - 5:.1f} L {x2:.1f} {y:.1f} '
             f'L {x2 - 8:.1f} {y + 5:.1f} Z" fill="{ARROW}"/>')
    s.append("</svg>")
    return "\n".join(s)


# starting position: (col 1..4, rank 1..4) -> (tile, owner) ; owner 1 = sente
START = {
    (1, 1): ("crane", 1), (2, 1): ("fox", 1), (3, 1): ("raccoon", 1),
    (4, 1): ("tapir", 1), (1, 2): ("carp", 1),
    (4, 3): ("carp", 2), (1, 4): ("tapir", 2), (2, 4): ("raccoon", 2),
    (3, 4): ("fox", 2), (4, 4): ("pheasant", 2),
}


def start_board(labels=True, max_w=None):
    cell = 60
    ml = 22 if labels else 10        # left gutter for rank labels
    mt = 12
    mr = 12
    mb = 22 if labels else 10        # bottom gutter for file labels
    span = 4 * cell
    W = ml + span + mr
    H = mt + span + mb
    s = [_open(W, H, max_w)]
    s.append(f'<rect x="{ml}" y="{mt}" width="{span}" height="{span}" rx="9" '
             f'fill="{BOARD_FILL}" stroke="{FRAME}" stroke-width="2"/>')
    for i in (1, 2, 3):
        s.append(f'<line x1="{ml + i * cell}" y1="{mt}" x2="{ml + i * cell}" '
                 f'y2="{mt + span}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'<line x1="{ml}" y1="{mt + i * cell}" x2="{ml + span}" '
                 f'y2="{mt + i * cell}" stroke="{GRID}" stroke-width="1"/>')
    for (c, r), (tile, owner) in START.items():
        x = ml + (c - 1) * cell
        y = mt + (4 - r) * cell      # rank 4 at the top
        size = cell * 0.96
        ox, oy = x + (cell - size) / 2, y + (cell - size) / 2
        if owner == 2:
            name = tile if tile == "pheasant" else f"dark/{tile}"
            s.append(img(name, ox, oy, size, rot_center=(x + cell / 2, y + cell / 2)))
        else:
            s.append(img(tile, ox, oy, size))
    if labels:
        for c in range(1, 5):
            s.append(f'<text x="{ml + (c - 1) * cell + cell / 2:.1f}" '
                     f'y="{mt + span + 15}" text-anchor="middle" fill="{LABEL}" '
                     f'font-family="system-ui,sans-serif" font-size="13">'
                     f'{"abcd"[c - 1]}</text>')
        for r in range(1, 5):
            s.append(f'<text x="{ml - 9}" '
                     f'y="{mt + (4 - r) * cell + cell / 2 + 4:.1f}" '
                     f'text-anchor="middle" fill="{LABEL}" '
                     f'font-family="system-ui,sans-serif" font-size="13">{r}</text>')
    s.append("</svg>")
    return "\n".join(s)


def jump_diagram(max_w=180):
    """A 1x3 column: mover (bottom) leaps an adjacent ally to the empty square
    two ahead (top), with a curved leap arrow."""
    cell = 60
    ml, mt, mb = 12, 12, 12
    arrow_pad = 34
    W = ml + cell + arrow_pad
    H = mt + 3 * cell + mb
    cxc = ml + cell / 2
    s = [_open(W, H, max_w),
         '<defs><marker id="s4arrow" markerWidth="8" markerHeight="8" '
         'refX="6" refY="3" orient="auto">'
         f'<path d="M0,0 L6,3 L0,6 Z" fill="{DOT}"/></marker></defs>']
    s.append(f'<rect x="{ml}" y="{mt}" width="{cell}" height="{3 * cell}" rx="8" '
             f'fill="{BOARD_FILL}" stroke="{FRAME}" stroke-width="2"/>')
    for i in (1, 2):
        s.append(f'<line x1="{ml}" y1="{mt + i * cell}" x2="{ml + cell}" '
                 f'y2="{mt + i * cell}" stroke="{GRID}" stroke-width="1"/>')
    # row 0 top = landing (target ring), row 1 = ally, row 2 bottom = mover
    top_c = mt + 0 * cell + cell / 2
    mid_c = mt + 1 * cell + cell / 2
    bot_c = mt + 2 * cell + cell / 2
    s.append(f'<circle cx="{cxc:.1f}" cy="{top_c:.1f}" r="{cell * 0.30:.1f}" '
             f'fill="none" stroke="{DOT}" stroke-width="2" '
             f'stroke-dasharray="4 4"/>')
    size = cell * 0.92
    s.append(img("raccoon", cxc - size / 2, mid_c - size / 2, size))  # ally
    s.append(img("carp", cxc - size / 2, bot_c - size / 2, size))   # mover
    # curved leap arrow from mover up to landing, bulging right around the ally
    bx = ml + cell + arrow_pad - 10
    s.append(f'<path d="M {ml + cell - 6:.1f} {bot_c - 6:.1f} '
             f'Q {bx:.1f} {mid_c:.1f} {ml + cell - 6:.1f} {top_c + 6:.1f}" '
             f'fill="none" stroke="{DOT}" stroke-width="2.5" '
             f'marker-end="url(#s4arrow)"/>')
    s.append("</svg>")
    return "\n".join(s)


def copy_tiles():
    os.makedirs(os.path.join(DST_PIECES, "dark"), exist_ok=True)
    light = ["crane", "pheasant", "carp", "tapir", "raccoon", "fox",
             "koi", "baku", "tanuki", "kitsune"]
    dark = ["carp", "tapir", "raccoon", "fox"]
    for n in light:
        shutil.copy(os.path.join(SRC_PIECES, f"{n}.png"),
                    os.path.join(DST_PIECES, f"{n}.png"))
    for n in dark:
        shutil.copy(os.path.join(SRC_PIECES, "dark", f"{n}.png"),
                    os.path.join(DST_PIECES, "dark", f"{n}.png"))
    print(f"  tiles -> {os.path.relpath(DST_PIECES, MB)} "
          f"({len(light)} light + {len(dark)} dark)")


def emit_ts():
    consts = {
        "SHOGI4_START_BOARD": start_board(labels=True, max_w=480),
        "SHOGI4_RULES_THUMBNAIL": start_board(labels=False),
        "SHOGI4_PAIR_CARP": pair_diagram("carp", "koi", "silver"),
        "SHOGI4_PAIR_TAPIR": pair_diagram("tapir", "baku", "silver"),
        "SHOGI4_PAIR_RACCOON": pair_diagram("raccoon", "tanuki", "silver"),
        "SHOGI4_PAIR_FOX": pair_diagram("fox", "kitsune", "gold"),
        "SHOGI4_MOVE_ROYAL": duo(["crane", "pheasant"], "crane"),
        "SHOGI4_JUMP": jump_diagram(),
    }
    head = (
        "// GENERATED by shogi4/tools/gen_rules_diagrams.py — do not edit by hand.\n"
        "// Inline SVG diagrams for the Shogi4 rules article. They reference the\n"
        "// public-domain Oca tiles copied to apps/web/public/shogi4/pieces/.\n"
        "// Regenerate (from the shogi4 repo): python3 tools/gen_rules_diagrams.py\n\n"
    )
    body = "\n".join(f"export const {k} = `{v}`;\n" for k, v in consts.items())
    with open(DST_TS, "w") as fh:
        fh.write(head + body)
    print(f"  diagrams -> {os.path.relpath(DST_TS, MB)} ({len(consts)} consts)")


def main():
    if not os.path.isdir(MB):
        raise SystemExit(f"mistboard not found at {MB}")
    copy_tiles()
    emit_ts()


if __name__ == "__main__":
    main()
