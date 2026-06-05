//! perft + golden differential-test driver for the Shogi4 engine.
//! Usage: shogi4-perft [golden_file]

use shogi4::*;

fn main() {
    let s = start();
    println!("=== Rust perft from the start position ===");
    let expected = [(1u32, 8u64), (2, 64), (3, 626), (4, 6304), (5, 68723), (6, 769014)];
    let mut perft_ok = true;
    for d in 1..=6u32 {
        let got = perft(&s, d);
        let exp = expected[(d - 1) as usize].1;
        let mark = if got == exp { "ok" } else { perft_ok = false; "MISMATCH" };
        println!("  perft({d}) = {got:>9}   (python {exp:>9})  [{mark}]");
    }
    println!("perft matches the Python oracle to the digit: {perft_ok}");

    if let Some(path) = std::env::args().nth(1) {
        println!("\n=== golden differential test ({path}) ===");
        match verify_golden(&path) {
            Ok((n, bad)) => {
                println!("checked {n} positions, {bad} mismatches -> {}",
                         if bad == 0 { "PASS" } else { "FAIL" });
                if !perft_ok || bad != 0 {
                    std::process::exit(1);
                }
            }
            Err(e) => {
                println!("golden error: {e}");
                std::process::exit(1);
            }
        }
    } else if !perft_ok {
        std::process::exit(1);
    }
}
