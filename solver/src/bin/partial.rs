//! One focused partial solve, for the rented-box run. Solves exactly the requested
//! sub-game {2 kings + inventory} and prints + FLUSHES the result (so a long run's
//! output survives redirection — block-buffered stdout has eaten results before).
//!
//! Usage:  partial [PTRF]      (default PTRF = one of each type, ~3.5B positions)
//!         partial PPFF        (2 carp + 2 fox), etc.
//! Set SHOGI4_PROGRESS=1 for live progress on stderr.

use shogi4::*;
use std::collections::BTreeMap;
use std::io::Write;

fn parse_inventory(s: &str) -> (Vec<u8>, Vec<u8>) {
    let mut order: Vec<u8> = Vec::new();
    let mut counts: BTreeMap<u8, u8> = BTreeMap::new();
    for ch in s.chars() {
        let t = match ch {
            'P' => CARP, 'T' => TAPIR, 'R' => RACCOON, 'F' => FOX,
            _ => panic!("bad piece '{ch}' — use P (carp) / T (tapir) / R (raccoon) / F (fox)"),
        };
        if !order.contains(&t) {
            order.push(t);
        }
        *counts.entry(t).or_insert(0) += 1;
    }
    let c = order.iter().map(|t| counts[t]).collect();
    (order, c)
}

fn main() {
    let arg = std::env::args().nth(1).unwrap_or_else(|| "PTRF".into());
    let (types, counts) = parse_inventory(&arg);
    let n = Ranker::new(&types, &counts).size();
    let mut out = std::io::stdout();

    writeln!(out, "=== partial solve: {{2 kings + {arg}}}  (rank domain N = {n}) ===").unwrap();
    writeln!(out, "(set SHOGI4_PROGRESS=1 for live progress on stderr)").unwrap();
    out.flush().unwrap();

    let t0 = std::time::Instant::now();
    let (w, l, d) = solve_push(&types, &counts);
    let dt = t0.elapsed().as_secs_f64();
    let tot = w + l + d;
    let edges = tot as f64 * 13.0; // ~avg branching (estimate, from perft + drops)

    writeln!(out, "legal positions : {tot}").unwrap();
    writeln!(out, "time            : {dt:.0} s").unwrap();
    writeln!(out, "throughput      : {:.0}k pos/s   (~{:.0} ns/edge, est @ b~13)",
             tot as f64 / dt / 1e3, dt * 1e9 / edges).unwrap();
    writeln!(out, "result          : W {:.2}%  L {:.2}%  D {:.2}%",
             100.0 * w as f64 / tot as f64, 100.0 * l as f64 / tot as f64, 100.0 * d as f64 / tot as f64).unwrap();
    writeln!(out, "                  (W {w}  L {l}  D {d})").unwrap();
    out.flush().unwrap();
}
