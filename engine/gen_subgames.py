#!/usr/bin/env python3
"""Write exact subgame W/L/D counts from the Python oracle, as the cross-check
fixture the Rust solver (solver/src/bin/subgames.rs) verifies against.

Line format:  <name>|<base-letter types, comma-sep>|<W>|<L>|<D>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shogi4 import build_graph, label_retro, counts_of  # noqa: E402

LET = {"carp": "P", "tapir": "T", "raccoon": "R", "fox": "F"}
SUBGAMES = [
    ("2K", []),
    ("2K+P", ["carp"]),
    ("2K+F", ["fox"]),
    ("2K+R", ["raccoon"]),
    ("2K+P+F", ["carp", "fox"]),
]


def main():
    out = os.path.join(os.path.dirname(__file__), "subgame_expected.txt")
    lines = []
    for name, extra in SUBGAMES:
        c = counts_of(label_retro(build_graph(extra)))
        enc = ",".join(LET[e] for e in extra)
        lines.append(f"{name}|{enc}|{c['W']}|{c['L']}|{c['D']}")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
