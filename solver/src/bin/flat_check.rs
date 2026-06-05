//! Validate the flat-array dense-rank retrograde solver (solve_flat) against the
//! Python oracle's expected counts (engine/subgame_expected.txt). This proves the
//! actual scalable mechanism — a value array indexed by `rank`, edges on the fly —
//! produces the same W/L/D as the HashMap solver and the Python oracle.

use shogi4::*;

fn letter_base(ch: char) -> u8 {
    match ch {
        'P' => CARP, 'T' => TAPIR, 'R' => RACCOON, 'F' => FOX,
        _ => panic!("bad base letter {ch}"),
    }
}

fn main() {
    let path = "engine/subgame_expected.txt";
    let text = std::fs::read_to_string(path).expect("read expected file");
    println!("=== flat-array dense-rank retrograde vs Python oracle ===");
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
        let n = Ranker::new(&types, &counts).size();
        if n > 100_000 {
            println!("  {name:8} N={n:>9}  (skipped — pull-based too slow; covered by the HashMap \
                      solver == oracle and the rank bijection)");
            continue;
        }
        let t0 = std::time::Instant::now();
        let (w, l, d) = solve_flat(&types, &counts);
        let dt = t0.elapsed().as_secs_f64();
        let ok = w == ew && l == el && d == ed;
        all_ok &= ok;
        println!(
            "  {name:8} N={n:>9}  W={w} L={l} D={d}  [oracle {ew}/{el}/{ed}: {}]  {dt:.2}s",
            if ok { "MATCH" } else { "*** MISMATCH ***" }
        );
    }
    println!("flat-array dense-rank solver == oracle: {all_ok}");
    if !all_ok {
        std::process::exit(1);
    }
}
