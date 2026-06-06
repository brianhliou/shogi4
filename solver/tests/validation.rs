//! Permanent validation suite — `cargo test` reproduces every correctness claim
//! the project rests on. Runs on small subgames (fast) plus the committed oracle
//! fixtures; the larger-scale solves and the distributed-design checks live in
//! `src/bin/` (see docs). Green here == the engine, all three solvers, the dense
//! rank, un-move generation, the symmetry fold, and the verification audit are all
//! consistent with the Python oracle and with each other.

use shogi4::*;
use std::collections::HashSet;

fn fixture(name: &str) -> String {
    let p = format!("{}/../engine/{}", env!("CARGO_MANIFEST_DIR"), name);
    std::fs::read_to_string(&p).unwrap_or_else(|e| panic!("missing fixture {p}: {e}"))
}

fn parse_base(s: &str) -> u8 {
    match s {
        "P" => CARP, "T" => TAPIR, "R" => RACCOON, "F" => FOX,
        _ => panic!("bad base letter {s}"),
    }
}

// subgames small enough for the heavy per-position checks
const SMALL: [&[u8]; 4] = [&[], &[CARP], &[FOX], &[RACCOON]];

// -------- move generation --------

#[test]
fn perft_from_start_matches_known() {
    let s = start();
    for (d, e) in [(1u32, 8u64), (2, 64), (3, 626), (4, 6304), (5, 68723), (6, 769014)] {
        assert_eq!(perft(&s, d), e, "perft({d})");
    }
}

#[test]
fn move_gen_matches_oracle_golden() {
    // every Python-oracle position's sorted legal moves equal ours (cross-language)
    let text = fixture("golden.txt");
    let (mut n, mut bad) = (0u32, 0u32);
    for line in text.lines() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        let (penc, want) = line.split_once(' ').expect("golden line");
        let mut got: Vec<String> = legal_moves(&parse_pos(penc)).into_iter().map(encode_move).collect();
        got.sort();
        if got.join(",") != want {
            bad += 1;
        }
        n += 1;
    }
    assert!(n >= 1000, "golden fixture too small ({n})");
    assert_eq!(bad, 0, "{bad}/{n} golden move-gen mismatches");
}

// -------- solvers vs the Python oracle, and vs each other --------

#[test]
fn subgame_solve_matches_python_oracle() {
    for line in fixture("subgame_expected.txt").lines() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        let f: Vec<&str> = line.split('|').collect();
        let extra: Vec<u8> = if f[1].is_empty() {
            vec![]
        } else {
            f[1].split(',').map(parse_base).collect()
        };
        let exp = (f[2].parse().unwrap(), f[3].parse().unwrap(), f[4].parse().unwrap());
        assert_eq!(solve_subgame(&extra), exp, "{} (HashMap retrograde)", f[0]);
    }
}

#[test]
fn three_solvers_agree() {
    // HashMap retrograde == push == flat, on small subgames
    for &extra in &SMALL {
        let counts = vec![1u8; extra.len()];
        let oracle = solve_subgame(extra);
        assert_eq!(solve_push(extra, &counts), oracle, "push vs oracle");
        assert_eq!(solve_flat(extra, &counts), oracle, "flat vs oracle");
    }
    // push also matches on the larger {2K+carp+fox}
    assert_eq!(solve_push(&[CARP, FOX], &[1, 1]), solve_subgame(&[CARP, FOX]));
}

// -------- dense rank --------

#[test]
fn rank_is_a_bijection_and_covers_enumeration() {
    for &extra in &SMALL {
        let counts = vec![1u8; extra.len()];
        let rk = Ranker::new(extra, &counts);
        let n = rk.size();
        for i in 0..n {
            assert_eq!(rk.rank(&rk.unrank(i)), i, "rank(unrank({i}))");
        }
        let from_rank: HashSet<Pos> = (0..n).map(|i| rk.unrank(i)).filter(is_legal).collect();
        let enumerated: HashSet<Pos> = enumerate_subgame(extra).into_iter().collect();
        assert!(from_rank == enumerated, "legal slots != enumeration");
    }
}

#[test]
fn full_game_rank_domain_equals_twice_enumerator() {
    let rk = Ranker::new(&[CARP, TAPIR, RACCOON, FOX], &[2, 2, 2, 2]);
    assert_eq!(rk.size(), 2 * 205_148_532_253_680);
}

// -------- un-move generation --------

#[test]
fn predecessors_equal_true_reverse_edges() {
    use std::collections::HashMap;
    for &extra in &[&[][..], &[CARP][..], &[FOX][..]] {
        let legal: Vec<Pos> = {
            let mut seen = HashSet::new();
            enumerate_subgame(extra).into_iter().filter(|p| seen.insert(*p)).collect()
        };
        let mut truth: HashMap<Pos, HashSet<Pos>> = HashMap::new();
        for p in &legal {
            for mv in legal_moves(p) {
                let (c, kc) = make(p, mv);
                if !kc {
                    truth.entry(c).or_default().insert(*p);
                }
            }
        }
        for q in &legal {
            let got: HashSet<Pos> = predecessors(q).into_iter().collect();
            let want = truth.get(q).cloned().unwrap_or_default();
            assert!(got == want, "predecessors != reverse edges");
        }
    }
}

#[test]
fn predecessors_is_deterministic() {
    // the determinism that makes checkpoint replay exact
    let p = solve_and_pick_a_position();
    assert_eq!(predecessors(&p), predecessors(&p));
}

fn solve_and_pick_a_position() -> Pos {
    let rk = Ranker::new(&[CARP], &[1]);
    (0..rk.size()).map(|i| rk.unrank(i)).find(|p| is_legal(p) && !predecessors(p).is_empty()).unwrap()
}

// -------- symmetry fold --------

#[test]
fn lr_symmetry_holds_on_solved_values() {
    let (rk, val, legal) = solve_push_array(&[CARP, FOX], &[1, 1]);
    let n = rk.size() as usize;
    for i in 0..n {
        if legal[i] {
            let m = mirror(&rk.unrank(i as u64));
            assert_eq!(val[i], val[rk.rank(&m) as usize], "value(pos) != value(mirror)");
        }
    }
}

// -------- verification audit --------

#[test]
fn audit_certifies_clean_and_catches_corruption() {
    let (rk, mut val, legal) = solve_push_array(&[CARP, FOX], &[1, 1]);
    assert_eq!(audit_solution(&rk, &val, &legal), 0, "clean solve failed its audit");
    // flip the first decided value to a wrong one — the audit must catch it
    let i = (0..val.len()).find(|&i| legal[i] && (val[i] == V_WIN || val[i] == V_LOSS)).unwrap();
    val[i] = if val[i] == V_WIN { V_LOSS } else { V_WIN };
    assert!(audit_solution(&rk, &val, &legal) > 0, "corruption not caught");
}
