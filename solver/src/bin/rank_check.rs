//! Validate the dense ranking function:
//!  1. bijection: rank(unrank(i)) == i for every i in [0, N)   (subgames)
//!  2. the legal positions produced by unrank == enumerate_subgame's set
//!  3. full game: N == 2 x the independently-validated state-space count

use shogi4::*;
use std::collections::HashSet;

fn check_subgame(name: &str, types: &[u8], counts: &[u8], extra: &[u8]) {
    let rk = Ranker::new(types, counts);
    let n = rk.size();
    for i in 0..n {
        let p = rk.unrank(i);
        let r = rk.rank(&p);
        assert_eq!(r, i, "{name}: rank(unrank({i})) = {r}");
    }
    let from_rank: HashSet<Pos> = (0..n).map(|i| rk.unrank(i)).filter(is_legal).collect();
    let enumerated: HashSet<Pos> = enumerate_subgame(extra).into_iter().collect();
    assert!(from_rank == enumerated, "{name}: legal set != enumerate set");
    println!("  {name:8} N={n:>9}  legal={:>9}  [bijection OK, set==enumerate OK]", from_rank.len());
}

fn main() {
    println!("=== ranking: bijection + set-equality on subgames ===");
    check_subgame("2K", &[], &[], &[]);
    check_subgame("2K+P", &[CARP], &[1], &[CARP]);
    check_subgame("2K+F", &[FOX], &[1], &[FOX]);
    check_subgame("2K+R", &[RACCOON], &[1], &[RACCOON]);
    check_subgame("2K+P+F", &[CARP, FOX], &[1, 1], &[CARP, FOX]);
    check_subgame("2K+2P", &[CARP], &[2], &[CARP, CARP]); // count-2 (full-game shape)

    println!("\n=== full game: N cross-check vs the state-space enumerator ===");
    let full = Ranker::new(&[CARP, TAPIR, RACCOON, FOX], &[2, 2, 2, 2]);
    let n = full.size();
    let expected = 2u64 * 205_148_532_253_680; // 2 x upper bound (turn x arrangements)
    println!("  Ranker N        = {n}");
    println!("  2 x enumerator  = {expected}");
    assert_eq!(n, expected, "full-game N mismatch");
    println!("  match: true");
    println!("\nALL RANKING CHECKS PASSED");
}
