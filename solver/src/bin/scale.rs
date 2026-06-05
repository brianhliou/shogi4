//! See how far the in-RAM push solver goes — solve progressively larger subgames,
//! reporting the rank-domain size, the W/L/D split (a real partial Shogi4 result),
//! and throughput (a rough ns/edge calibration for the rung-4 budget).

use shogi4::*;

fn run(name: &str, types: &[u8], counts: &[u8], cap: u64) {
    let n = Ranker::new(types, counts).size();
    print!("  {name:12} N(rank domain)={n:>13}  ");
    if n > cap {
        println!("[skipped — over the {cap} cap for laptop/time]");
        return;
    }
    let t0 = std::time::Instant::now();
    let (w, l, d) = solve_push(types, counts);
    let dt = t0.elapsed().as_secs_f64();
    let tot = w + l + d;
    let edges = tot as f64 * 12.0; // ~avg branching (rough)
    println!(
        "legal={tot} in {dt:.1}s  ({:.0}k pos/s, ~{:.0} ns/edge)  ->  W {:.1}%  L {:.1}%  D {:.1}%",
        tot as f64 / dt / 1e3,
        dt * 1e9 / edges,
        100.0 * w as f64 / tot as f64,
        100.0 * l as f64 / tot as f64,
        100.0 * d as f64 / tot as f64,
    );
}

fn main() {
    let cap: u64 = std::env::args().nth(1).and_then(|s| s.parse().ok()).unwrap_or(120_000_000);
    println!("=== scaling the in-RAM push solver (cap N={cap}) ===");
    run("2K+P+F", &[CARP, FOX], &[1, 1], cap);
    run("2K+P+F+R", &[CARP, FOX, RACCOON], &[1, 1, 1], cap);
    run("2K+P+F+R+T", &[CARP, FOX, RACCOON, TAPIR], &[1, 1, 1, 1], cap);
}
