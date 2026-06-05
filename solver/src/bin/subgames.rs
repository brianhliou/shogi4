//! Cross-check the Rust retrograde subgame solver against the Python oracle.
//! Reads engine/subgame_expected.txt (name|types|W|L|D produced by
//! engine/gen_subgames.py) and asserts the Rust W/L/D counts match to the unit.

use shogi4::*;

fn letter_base(ch: char) -> u8 {
    match ch {
        'P' => CARP, 'T' => TAPIR, 'R' => RACCOON, 'F' => FOX,
        _ => panic!("bad base letter {ch}"),
    }
}

fn main() {
    let path = std::env::args().nth(1).unwrap_or_else(|| "engine/subgame_expected.txt".into());
    let text = std::fs::read_to_string(&path).expect("read expected file");
    println!("=== Rust retrograde subgame solver vs Python oracle ===");
    let mut all_ok = true;
    for line in text.lines() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        let f: Vec<&str> = line.split('|').collect();
        let name = f[0];
        let extra: Vec<u8> = if f[1].is_empty() {
            vec![]
        } else {
            f[1].split(',').map(|s| letter_base(s.chars().next().unwrap())).collect()
        };
        let (ew, el, ed): (u64, u64, u64) =
            (f[2].parse().unwrap(), f[3].parse().unwrap(), f[4].parse().unwrap());
        let (w, l, d) = solve_subgame(&extra);
        let ok = w == ew && l == el && d == ed;
        all_ok &= ok;
        println!(
            "  {name:8} {:>9} pos -> W={w:>7} L={l:>7} D={d:>7}   [python W={ew} L={el} D={ed}: {}]",
            w + l + d,
            if ok { "MATCH" } else { "*** MISMATCH ***" }
        );
    }
    println!("Rust solver == Python oracle on every subgame: {all_ok}");
    if !all_ok {
        std::process::exit(1);
    }
}
