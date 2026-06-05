//! Validate the push-based retrograde solver (solve_push) against the oracle's
//! expected counts (engine/subgame_expected.txt) — including the 1.16M-position
//! subgame the pull-based solver couldn't finish. This is the full scalable
//! algorithm: rank-indexed flat array + un-move-gen, no stored graph.

use shogi4::*;

fn letter_base(ch: char) -> u8 {
    match ch {
        'P' => CARP, 'T' => TAPIR, 'R' => RACCOON, 'F' => FOX,
        _ => panic!("bad base letter {ch}"),
    }
}

fn main() {
    let text = std::fs::read_to_string("engine/subgame_expected.txt").expect("read expected");
    println!("=== push-based retrograde (un-move-gen) vs oracle ===");
    let mut all_ok = true;
    for line in text.lines() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        let f: Vec<&str> = line.split('|').collect();
        let name = f[0];
        let types: Vec<u8> = if f[1].is_empty() {
            vec![]
        } else {
            f[1].split(',').map(|s| letter_base(s.chars().next().unwrap())).collect()
        };
        let counts: Vec<u8> = types.iter().map(|_| 1u8).collect();
        let (ew, el, ed): (u64, u64, u64) =
            (f[2].parse().unwrap(), f[3].parse().unwrap(), f[4].parse().unwrap());
        let t0 = std::time::Instant::now();
        let (w, l, d) = solve_push(&types, &counts);
        let dt = t0.elapsed().as_secs_f64();
        let ok = w == ew && l == el && d == ed;
        all_ok &= ok;
        println!(
            "  {name:8} W={w:>7} L={l:>7} D={d:>7}  [oracle {ew}/{el}/{ed}: {}]  {dt:.1}s",
            if ok { "MATCH" } else { "*** MISMATCH ***" }
        );
    }
    println!("push-based solver == oracle: {all_ok}");
    if !all_ok {
        std::process::exit(1);
    }
}
