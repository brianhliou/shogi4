//! Validate un-move generation: for every position q in a subgame,
//! predecessors(q) must EXACTLY equal the set of p that have a legal move p -> q
//! (computed by inverting all forward edges). Covers drops, captures, promotions,
//! and friendly-jumps (a one-piece subgame exercises every reverse-move shape).

use shogi4::*;
use std::collections::{HashMap, HashSet};

fn check(name: &str, extra: &[u8]) {
    let mut legal: Vec<Pos> = Vec::new();
    let mut seen: HashSet<Pos> = HashSet::new();
    for p in enumerate_subgame(extra) {
        if seen.insert(p) {
            legal.push(p);
        }
    }
    // ground truth: invert every forward (non-king-capture) edge
    let mut truth: HashMap<Pos, HashSet<Pos>> = HashMap::new();
    for p in &legal {
        for mv in legal_moves(p) {
            let (c, kc) = make(p, mv);
            if !kc {
                truth.entry(c).or_default().insert(*p);
            }
        }
    }
    let mut ok = true;
    for q in &legal {
        let got: HashSet<Pos> = predecessors(q).into_iter().collect();
        let want = truth.get(q).cloned().unwrap_or_default();
        if got != want {
            ok = false;
            eprintln!("  {name}: mismatch — got {} preds, want {}", got.len(), want.len());
            break;
        }
    }
    println!("  {name:8} {:>7} positions  predecessors == true reverse edges: {ok}", legal.len());
    assert!(ok, "{name} FAILED");
}

fn main() {
    println!("=== un-move generation vs true reverse edges ===");
    check("2K", &[]);
    check("2K+P", &[CARP]);
    check("2K+F", &[FOX]);
    check("2K+R", &[RACCOON]);
    println!("predecessors() validated — covers drops, captures, promotions, jumps.");
}
