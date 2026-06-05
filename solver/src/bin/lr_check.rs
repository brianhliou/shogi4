//! Validate the left–right symmetry fold: in a solved subgame, every position
//! must have the same value as its mirror — value(pos) == value(mirror(pos)).
//! That proves the ~2× storage/compute fold is sound, and reports the real fold
//! factor (canonical orbits / positions).

use shogi4::*;

fn check(name: &str, types: &[u8], counts: &[u8]) {
    let (rk, val, legal) = solve_push_array(types, counts);
    let n = rk.size() as usize;
    let (mut total, mut self_sym, mut bad) = (0u64, 0u64, 0u64);
    for i in 0..n {
        if !legal[i] {
            continue;
        }
        total += 1;
        let pos = rk.unrank(i as u64);
        let m = mirror(&pos);
        if val[i] != val[rk.rank(&m) as usize] {
            bad += 1;
        }
        if m == pos {
            self_sym += 1;
        }
    }
    let canonical = (total + self_sym) / 2; // # LR orbits
    println!(
        "  {name:8} {total:>9} positions  mismatches={bad}  self-sym={self_sym}  \
         -> {canonical} canonical reps (fold {:.3})",
        canonical as f64 / total as f64
    );
    assert_eq!(bad, 0, "{name}: LR symmetry violated");
}

fn main() {
    println!("=== LR-symmetry validation: value(pos) == value(mirror(pos)) ===");
    check("2K", &[], &[]);
    check("2K+P", &[CARP], &[1]);
    check("2K+F", &[FOX], &[1]);
    check("2K+P+F", &[CARP, FOX], &[1, 1]);
    println!("LR fold is sound — the ~2× storage/compute lever is confirmed.");
}
