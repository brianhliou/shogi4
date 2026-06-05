#!/usr/bin/env python3
"""Local server for the Shogi4 game viewer.

Shogi4 is not solved yet (no tablebase), so unlike the Dōbutsu explorer this
serves *legal moves*, not win/loss verdicts. Move generation is delegated to the
validated Python oracle (engine/shogi4.py) — the viewer writes NO third engine.
The only new logic here is a position/notation codec.

/api?pos=<enc> answers with the position's legal moves; each move carries the
encoded child position (for navigation), its from/to squares, and capture /
promotion / friendly-jump / king-capture flags (everything the SVG board needs).

Wire format (must match engine/gen_golden.py and solver/src/lib.rs):
  <16 cells>;<P1 hand>;<P2 hand>;<stm 1|2>
    cells : index i=0..15, r=i//4+1 (outer), c=i%4+1 (inner). '.'=empty, else a
            letter, UPPER=P1 / lower=P2:
              K king · P carp · T tapir · R raccoon · F fox
              O koi · B baku · N tanuki · G kitsune
    hand  : 4 digits, order carp,tapir,raccoon,fox (hands only hold base types)
  start : KFRTP......ptrfk;0000;0000;1

When the strong solution lands, /api upgrades to also return each move's W/L/D
and distance-to-mate, and the page's status bar becomes a verdict bar — the rest
of the protocol is unchanged.

Run:  python3 explorer/serve.py   ->  http://localhost:41234/
"""
import http.server
import json
import os
import re
import socketserver
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "engine"))
from shogi4 import P1, P2, BASE, legal_moves, make, start, Position  # noqa: E402

PORT = int(os.environ.get("PORT", 41234))  # default for local dev; $PORT if hosted

# ---------------------------------------------------------------- codec
LETTER = {"king": "K", "carp": "P", "tapir": "T", "raccoon": "R", "fox": "F",
          "koi": "O", "baku": "B", "tanuki": "N", "kitsune": "G"}
ANIMAL = {v: k for k, v in LETTER.items()}
BASE_LETTER = {a: LETTER[a] for a in BASE}
FILES = "abcd"

# Exactly the format above — reject anything else before it reaches the engine.
POS_RE = re.compile(r"\A[A-Za-z.]{16};[0-9]{4};[0-9]{4};[12]\Z")
INITIAL = "KFRTP......ptrfk;0000;0000;1"


def encode_pos(pos):
    """Position -> wire string (mirror of engine/gen_golden.py:encode_pos)."""
    cells = []
    for r in (1, 2, 3, 4):
        for c in (1, 2, 3, 4):
            p = pos.board.get((c, r))
            if p is None:
                cells.append(".")
            else:
                o, a = p
                cells.append(LETTER[a] if o == P1 else LETTER[a].lower())

    def hand(o):
        return "".join(str(pos.hands[o].get(t, 0)) for t in BASE)

    return f"{''.join(cells)};{hand(P1)};{hand(P2)};{1 if pos.stm == P1 else 2}"


def decode_pos(enc):
    """Wire string -> Position (the inverse of encode_pos)."""
    cells, h1, h2, stm = enc.split(";")
    board = {}
    for i, ch in enumerate(cells):
        if ch == ".":
            continue
        owner = P1 if ch.isupper() else P2
        board[(i % 4 + 1, i // 4 + 1)] = (owner, ANIMAL[ch.upper()])
    hands = {P1: {BASE[i]: int(h1[i]) for i in range(4)},
             P2: {BASE[i]: int(h2[i]) for i in range(4)}}
    return Position(board, hands, P1 if stm == "1" else P2)


def sq(c, r):
    return f"{FILES[c - 1]}{r}"


def notation(pos, mv):
    """Human-readable move string for the scoresheet.

    Board move: <Piece><from><sep><to>[+]  (sep 'x' if it captures, else '-';
    '+' if it promotes).  Drop: <Base>*<to>.  Side is implied by whose turn it is.
    """
    me = pos.stm
    last_rank = 4 if me == P1 else 1
    if mv[0] == "m":
        _, s, d = mv
        _, animal = pos.board[s]
        occ = pos.board.get(d)
        sep = "x" if (occ is not None and occ[0] != me) else "-"
        promo = animal in BASE and d[1] == last_rank
        return f"{LETTER[animal]}{sq(*s)}{sep}{sq(*d)}{'+' if promo else ''}"
    _, animal, d = mv
    return f"{BASE_LETTER[animal]}*{sq(*d)}"


def describe_move(pos, mv):
    """One legal move -> the JSON the SVG board consumes."""
    me = pos.stm
    last_rank = 4 if me == P1 else 1
    child, king_cap = make(pos, mv)
    out = {"notation": notation(pos, mv), "terminal": king_cap,
           "child": encode_pos(child)}
    if mv[0] == "m":
        _, s, d = mv
        _, animal = pos.board[s]
        occ = pos.board.get(d)
        out.update(kind="m",
                   **{"from": {"c": s[0], "r": s[1]}},
                   to={"c": d[0], "r": d[1]},
                   piece=LETTER[animal],
                   capture=occ is not None and occ[0] != me,
                   promo=animal in BASE and d[1] == last_rank,
                   jump=abs(d[0] - s[0]) == 2 or abs(d[1] - s[1]) == 2)
    else:
        _, animal, d = mv
        out.update(kind="d", **{"from": None}, to={"c": d[0], "r": d[1]},
                   piece=BASE_LETTER[animal], capture=False, promo=False, jump=False)
    return out


def api(enc):
    pos = decode_pos(enc)
    moves = [describe_move(pos, mv) for mv in legal_moves(pos)]
    return {"pos": enc, "stm": 1 if pos.stm == P1 else 2, "moves": moves}


# ---------------------------------------------------------------- server
class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code, ctype, body):
        if not isinstance(body, bytes):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, name, ctype):
        fp = os.path.join(HERE, name)
        if os.path.isfile(fp):
            with open(fp, "rb") as fh:
                self._send(200, ctype, fh.read())
        else:
            self._send(404, "text/plain", b"not found")

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path in ("/", "/index.html"):
            self._file("index.html", "text/html; charset=utf-8")
        elif u.path == "/clips.json":
            self._file("clips.json", "application/json")
        elif u.path == "/api":
            q = urllib.parse.parse_qs(u.query)
            enc = q.get("pos", [INITIAL])[0]
            if not POS_RE.match(enc):
                self._send(400, "application/json", b'{"error":"invalid position"}')
                return
            try:
                self._send(200, "application/json", json.dumps(api(enc)))
            except Exception as exc:  # malformed-but-regex-passing input
                self._send(400, "application/json",
                           json.dumps({"error": str(exc)}))
        else:
            self._send(404, "text/plain", b"not found")

    def log_message(self, *a):
        pass


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    # sanity: the start position must round-trip and match the oracle
    assert encode_pos(start()) == INITIAL, "start encoding drift"
    print(f"shogi4 viewer: http://localhost:{PORT}/   (Ctrl-C to stop)")
    Server(("", PORT), Handler).serve_forever()
