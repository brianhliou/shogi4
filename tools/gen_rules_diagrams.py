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
import math
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
DOT = "#15705c"          # reachable-square dot (piece-move grids)
# Move-scene overlays, matched to the explorer / chess-article study layers so
# the rules diagrams read in the same visual language as the playable boards.
MOVE_ARROW = "#e08220"   # move arrow (explorer arrow colour)
HL = "#f6d873"           # from/to square highlight (yellow, drawn at 0.55)
CAP = "#c0392b"          # capture ring + forbidden-square mark (red)
TEAL = "#2b8a8a"         # legal-destination dot
WASH_OK = "rgba(45,100,45,0.10)"    # allowed-rows wash (drop diagram)
WASH_NO = "rgba(192,57,43,0.16)"    # forbidden-row wash (drop diagram)
FARM = "#efe2c4"         # farm (hand) box fill
LABEL = "#9a8c6a"

# Shared sizing so every 3×3-board diagram (move pairs, royal, jump cases)
# renders its tiles at the same on-page pixel size: cell px × TILE_SCALE.
CELL3 = 56
TILE_SCALE = 1.25

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
    for i in (1, 2):  # interior grid lines, inset 1px to stop flush at the inner frame edge
        p.append(f'<line x1="{bx + i * cell}" y1="{by + 1}" x2="{bx + i * cell}" '
                 f'y2="{by + span - 1}" stroke="{GRID}" stroke-width="1"/>')
        p.append(f'<line x1="{bx + 1}" y1="{by + i * cell}" x2="{bx + span - 1}" '
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


def duo(tiles, move_key):
    """Two tiles side by side sharing one move (e.g. the two royals)."""
    cell, m, gap = CELL3, 12, 24
    span = 3 * cell
    W = 2 * m + 2 * span + gap
    H = 2 * m + span
    s = [_open(W, H, int(W * TILE_SCALE))]
    for i, t in enumerate(tiles):
        s += _grid(m + i * (span + gap), m, cell, t, MOVES[move_key])
    s.append("</svg>")
    return "\n".join(s)


ARROW = "#8a7a55"


def pair_diagram(base_key, evolved_tile, evolved_key):
    """Base piece (left) -> evolved form (right), each a 3x3 move grid with an
    arrow between, so a reader sees what evolves into what and how its move
    changes. Koi/Baku/Tanuki are silvers; Kitsune is a gold."""
    cell, m, arrow = CELL3, 12, 46
    span = 3 * cell
    bx2 = m + span + arrow
    W = bx2 + span + m
    H = 2 * m + span
    s = [_open(W, H, int(W * TILE_SCALE))]
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
    for i in (1, 2, 3):  # inset 1px to stop flush at the inner frame edge
        s.append(f'<line x1="{ml + i * cell}" y1="{mt + 1}" x2="{ml + i * cell}" '
                 f'y2="{mt + span - 1}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'<line x1="{ml + 1}" y1="{mt + i * cell}" x2="{ml + span - 1}" '
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


def _jump_panel(bx, by, cell, spec):
    """One 3×3 friendly-jump case (uses the shared scene primitives). spec keys:
    pieces [((c, r), tile, owner)], frm/to (leap squares -> arrow + highlights),
    ring (capture square), ban (illegal square -> red ✕), legal (bool),
    cap (caption lines, coloured by legal)."""
    span = 3 * cell
    out = _board(bx, by, 3, 3, cell)
    if "frm" in spec:
        out.append(_hl(bx, by, cell, *spec["frm"]))
        out.append(_hl(bx, by, cell, *spec["to"]))
    if "ring" in spec:
        out.append(_cap_ring(bx, by, cell, *spec["ring"]))
    for (c, r), tile, owner in spec["pieces"]:
        out.append(_place(bx, by, cell, c, r, tile, owner=owner))
    if "ban" in spec:
        out.append(_ban(bx, by, cell, *spec["ban"]))
    if "frm" in spec:
        fx_, fy_ = _cc(bx, by, cell, *spec["frm"])
        tx_, ty_ = _cc(bx, by, cell, *spec["to"])
        out.append(_arrow(fx_, fy_, tx_, ty_, cell))
    col = "#2e7d32" if spec["legal"] else CAP
    mark = "✓" if spec["legal"] else "✕"
    for li, line in enumerate(spec["cap"]):
        txt = f"{mark} {line}" if li == 0 else line
        out.append(f'<text x="{bx + span / 2:.1f}" '
                   f'y="{by + span + 15 + li * 15:.1f}" text-anchor="middle" '
                   f'fill="{col}" font-family="system-ui,sans-serif" '
                   f'font-size="12">{txt}</text>')
    return out


def jump_cases_diagram():
    """A 2×2 gallery of friendly-jump cases: legal (✓) on top — leaping an ally
    straight or on the diagonal — illegal (✕) below."""
    cell, m, gx, gy, lab = CELL3, 14, 22, 16, 34
    span = 3 * cell
    panels = [
        dict(pieces=[((1, 2), "fox", 1), ((1, 1), "raccoon", 1)],
             frm=(1, 2), to=(1, 0), legal=True, cap=["straight", "leap"]),
        dict(pieces=[((0, 2), "raccoon", 1), ((1, 1), "fox", 1)],
             frm=(0, 2), to=(2, 0), legal=True, cap=["diagonal", "leap"]),
        dict(pieces=[((1, 2), "fox", 1), ((1, 1), "raccoon", 2)],
             ban=(1, 1), legal=False, cap=["not over", "an enemy"]),
        dict(pieces=[((1, 2), "fox", 1), ((1, 1), "raccoon", 1),
                     ((1, 0), "tapir", 1)],
             ban=(1, 0), legal=False, cap=["not onto", "your own"]),
    ]
    W = m + 2 * span + gx + m
    H = m + 2 * span + 2 * lab + gy + m
    s = [_open(W, H, int(W * TILE_SCALE))]
    for i, spec in enumerate(panels):
        bx = m + (i % 2) * (span + gx)
        by = m + (i // 2) * (span + lab + gy)
        s += _jump_panel(bx, by, cell, spec)
    s.append("</svg>")
    return "\n".join(s)


# ---- general board-scene primitives (capture / drop / win diagrams) ---------
# These place arbitrary tiles on an N×M board with move arrows and red
# capture/ban marks. Row 0 is the top; the first player (owner 1) moves up.

def _cc(bx, by, cell, col, row):
    return bx + (col + 0.5) * cell, by + (row + 0.5) * cell


_LAST_BOARD = [(0, 0, 0, 0)]   # (bx, by, w, h) of the most recent board, for _hl clipping
_HL_ID = [0]


def _board(bx, by, cols, rows, cell):
    sx, sy = cols * cell, rows * cell
    _LAST_BOARD[0] = (bx, by, sx, sy)
    p = [f'<rect x="{bx}" y="{by}" width="{sx}" height="{sy}" rx="8" '
         f'fill="{BOARD_FILL}" stroke="{FRAME}" stroke-width="2"/>']
    for i in range(1, cols):                       # inset 1px so lines stop flush at the inner frame edge
        p.append(f'<line x1="{bx + i * cell}" y1="{by + 1}" x2="{bx + i * cell}" '
                 f'y2="{by + sy - 1}" stroke="{GRID}" stroke-width="1"/>')
    for i in range(1, rows):
        p.append(f'<line x1="{bx + 1}" y1="{by + i * cell}" x2="{bx + sx - 1}" '
                 f'y2="{by + i * cell}" stroke="{GRID}" stroke-width="1"/>')
    return p


def _place(bx, by, cell, col, row, tile, owner=1, scale=0.92):
    """A tile on a scene square. Owner 2 is rotated 180° (facing = ownership);
    its base tiles use the dark variant, but the Pheasant royal stays itself."""
    size = cell * scale
    cx, cy = _cc(bx, by, cell, col, row)
    ox, oy = cx - size / 2, cy - size / 2
    if owner == 2:
        name = tile if tile == "pheasant" else f"dark/{tile}"
        return img(name, ox, oy, size, rot_center=(cx, cy))
    return img(tile, ox, oy, size)


def _arrow(x1, y1, x2, y2, cell):
    """Move arrow in the explorer's style: a thick orange shaft starting just
    off the source centre, a polygon head stopping just short of the target."""
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy) or 1.0
    ux, uy = dx / ln, dy / ln
    px, py = -uy, ux
    w, head, hw = cell * 0.1, cell * 0.3, cell * 0.18
    sx, sy = x1 + ux * cell * 0.22, y1 + uy * cell * 0.22
    tipx, tipy = x2 - ux * cell * 0.06, y2 - uy * cell * 0.06
    bxx, byy = tipx - ux * head, tipy - uy * head
    return (f'<g opacity="0.68">'
            f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{bxx:.1f}" y2="{byy:.1f}" '
            f'stroke="{MOVE_ARROW}" stroke-width="{w:.1f}" stroke-linecap="round"/>'
            f'<polygon points="{tipx:.1f},{tipy:.1f} '
            f'{bxx + px * hw:.1f},{byy + py * hw:.1f} '
            f'{bxx - px * hw:.1f},{byy - py * hw:.1f}" fill="{MOVE_ARROW}"/></g>')


def _hl(bx, by, cell, col, row):
    """A from/to square highlight: the full cell flush to the grid, clipped to the
    board's rounded outline so it rounds only at the board corners. Drawn over the
    board, under tiles."""
    bxx, byy, bw, bh = _LAST_BOARD[0]
    cid = f"hlc{_HL_ID[0]}"
    _HL_ID[0] += 1
    # Inset the clip by the board stroke's half-width (1px of the 2px frame) so the
    # highlight stops at the inner edge of the border instead of painting over it.
    return (f'<clipPath id="{cid}"><rect x="{bxx + 1}" y="{byy + 1}" width="{bw - 2}" '
            f'height="{bh - 2}" rx="7"/></clipPath>'
            f'<rect x="{bx + col * cell:.1f}" y="{by + row * cell:.1f}" width="{cell:.1f}" '
            f'height="{cell:.1f}" fill="{HL}" opacity="0.55" clip-path="url(#{cid})"/>')


def _rowwash(bx, by, cell, cols, row, color):
    # Clip to the board's (inset) rounded outline so the far/near rows round at the
    # board corners and stop inside the frame, matching the square highlights.
    bxx, byy, bw, bh = _LAST_BOARD[0]
    cid = f"hlc{_HL_ID[0]}"
    _HL_ID[0] += 1
    return (f'<clipPath id="{cid}"><rect x="{bxx + 1}" y="{byy + 1}" width="{bw - 2}" '
            f'height="{bh - 2}" rx="7"/></clipPath>'
            f'<rect x="{bx}" y="{by + row * cell}" width="{cols * cell}" '
            f'height="{cell}" fill="{color}" clip-path="url(#{cid})"/>')


def _cap_ring(bx, by, cell, col, row):
    cx, cy = _cc(bx, by, cell, col, row)
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{cell * 0.44:.1f}" '
            f'fill="none" stroke="{CAP}" stroke-width="2.5" opacity="0.85"/>')


def _dot(bx, by, cell, col, row):
    cx, cy = _cc(bx, by, cell, col, row)
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{cell * 0.15:.1f}" '
            f'fill="{TEAL}" opacity="0.8"/>')


def _ban(bx, by, cell, col, row):
    cx, cy = _cc(bx, by, cell, col, row)
    d = cell * 0.26
    return (f'<line x1="{cx - d:.1f}" y1="{cy - d:.1f}" x2="{cx + d:.1f}" '
            f'y2="{cy + d:.1f}" stroke="{CAP}" stroke-width="3.5" '
            f'stroke-linecap="round" opacity="0.85"/>'
            f'<line x1="{cx - d:.1f}" y1="{cy + d:.1f}" x2="{cx + d:.1f}" '
            f'y2="{cy - d:.1f}" stroke="{CAP}" stroke-width="3.5" '
            f'stroke-linecap="round" opacity="0.85"/>')


def _ghost(bx, by, cell, col, row, tile, owner=1):
    return f'<g opacity="0.42">{_place(bx, by, cell, col, row, tile, owner)}</g>'


def _farmbox(x, y, w, h, tile, label):
    """A dashed horizontal 'farm' (hand) strip below the board (like the sample-game
    komadai): the held tile sits at the left, the label at the right."""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{FARM}" '
           f'stroke="{FRAME}" stroke-width="1.5" stroke-dasharray="5 4"/>']
    if tile:
        size = h * 0.74
        out.append(img(tile, x + 8, y + (h - size) / 2, size))
    out.append(f'<text x="{x + w - 12:.1f}" y="{y + h / 2 + 4:.1f}" text-anchor="end" '
               f'fill="{LABEL}" font-family="system-ui,sans-serif" font-size="12">{label}</text>')
    return out


def _scenelabel(cx, y, text):
    return (f'<text x="{cx:.1f}" y="{y:.1f}" text-anchor="middle" fill="{LABEL}" '
            f'font-family="system-ui,sans-serif" font-size="12">{text}</text>')


def capture_diagram(max_w=520):
    """Before / after a capture on the 4×4 board, each panel showing the farm as a
    strip below: your Fox takes an enemy Raccoon-dog, which lands in your farm
    (switching sides)."""
    cell, m = 40, 12
    span = 4 * cell
    farm_h, gap_bf, lab = 40, 8, 16
    panel_h = span + gap_bf + farm_h
    mid = 40
    W = m + span + mid + span + m
    H = m + panel_h + lab + m
    s = [_open(W, H, max_w)]

    def panel(ox, after, label):
        bx, by = ox, m
        fy = by + span + gap_bf
        out = _board(bx, by, 4, 4, cell)
        if after:
            out.append(_hl(bx, by, cell, 2, 2))
            out.append(_place(bx, by, cell, 2, 2, "fox", owner=1))
            out += _farmbox(bx, fy, span, farm_h, "raccoon", "farm")
        else:
            out.append(_hl(bx, by, cell, 1, 2))
            out.append(_hl(bx, by, cell, 2, 2))
            out.append(_place(bx, by, cell, 1, 2, "fox", owner=1))
            out.append(_place(bx, by, cell, 2, 2, "raccoon", owner=2))
            out.append(_cap_ring(bx, by, cell, 2, 2))
            fxx, fyy = _cc(bx, by, cell, 1, 2)
            kx, ky = _cc(bx, by, cell, 2, 2)
            out.append(_arrow(fxx, fyy, kx, ky, cell))
            out += _farmbox(bx, fy, span, farm_h, None, "farm")
        out.append(_scenelabel(bx + span / 2, fy + farm_h + 13, label))
        return out

    s += panel(m, False, "before")
    ax, ay = m + span + 9, m + span / 2
    s.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{ax + mid - 24:.1f}" '
             f'y2="{ay:.1f}" stroke="{ARROW}" stroke-width="2.5"/>')
    s.append(f'<path d="M {ax + mid - 26:.1f} {ay - 5:.1f} '
             f'L {ax + mid - 18:.1f} {ay:.1f} L {ax + mid - 26:.1f} {ay + 5:.1f} Z" '
             f'fill="{ARROW}"/>')
    s += panel(m + span + mid, True, "after")
    s.append("</svg>")
    return "\n".join(s)


def drop_diagram(max_w=300):
    """Allowed vs forbidden rows, farm as a strip below: drop from your farm onto
    any empty square in the green rows; the red far row (the opponent's back
    rank) is barred."""
    cell, m, gap, farm_h = 50, 12, 10, 50
    span = 4 * cell
    bx = by = m
    fy = by + span + gap                            # farm strip below the board
    W, H = m + span + m, fy + farm_h + m
    s = [_open(W, H, max_w)]
    s += _board(bx, by, 4, 4, cell)
    for r in (1, 2, 3):                              # allowed rows (faint green)
        s.append(_rowwash(bx, by, cell, 4, r, WASH_OK))
    s.append(_rowwash(bx, by, cell, 4, 0, WASH_NO))  # forbidden far row (red)
    s.append(_place(bx, by, cell, 3, 0, "pheasant", owner=2))  # far-row anchor
    for c in (0, 1, 2):                              # ✗ on the empty far-row cells
        s.append(_ban(bx, by, cell, c, 0))
    s.append(_hl(bx, by, cell, 1, 2))               # the example drop square
    s.append(_ghost(bx, by, cell, 1, 2, "raccoon", owner=1))
    s += _farmbox(bx, fy, span, farm_h, "raccoon", "farm")
    tx, ty = _cc(bx, by, cell, 1, 2)
    fcx, fcy = bx + 8 + farm_h * 0.37, fy + farm_h / 2   # the farm tile, up to the drop square
    s.append(_arrow(fcx, fcy, tx, ty, cell))
    s.append("</svg>")
    return "\n".join(s)


def win_diagram(max_w=340):
    """On the full 4×4 board, your Fox steps into the enemy royal's corner and
    captures it: the only way the game ends."""
    cell, m = 56, 12
    span = 4 * cell
    bx = by = m
    s = [_open(m + span + m, m + span + m, max_w)]
    s += _board(bx, by, 4, 4, cell)
    s.append(_hl(bx, by, cell, 3, 1))            # from
    s.append(_hl(bx, by, cell, 3, 0))            # to
    s.append(_place(bx, by, cell, 0, 3, "crane", owner=1))     # your royal, corner
    s.append(_place(bx, by, cell, 3, 0, "pheasant", owner=2))  # enemy royal, corner
    s.append(_place(bx, by, cell, 3, 1, "fox", owner=1))       # the capturer
    s.append(_cap_ring(bx, by, cell, 3, 0))
    fxx, fyy = _cc(bx, by, cell, 3, 1)
    px, py = _cc(bx, by, cell, 3, 0)
    s.append(_arrow(fxx, fyy, px, py, cell))
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
        "SHOGI4_JUMP_CASES": jump_cases_diagram(),
        "SHOGI4_CAPTURE": capture_diagram(),
        "SHOGI4_DROP": drop_diagram(),
        "SHOGI4_WIN": win_diagram(),
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
