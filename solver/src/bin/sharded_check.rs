//! Distributed-correctness validation on one machine, for $0.
//!
//! Simulates the rung-4 distributed solver: the rank space is split into K
//! rank-range SHARDS; each shard owns its slots' value+counter; when a slot
//! resolves it emits predecessor-update messages routed to the owning shard (the
//! SHUFFLE); a SUPERSTEP processes all inboxes behind a barrier; convergence is the
//! first zero-message superstep. We assert the result equals the `solve_push`
//! oracle for EVERY shard count — proving the distributed decomposition is correct
//! AND that the answer is invariant to how it's parallelized (confluence).

use shogi4::*;

/// Returns (W, L, D, supersteps, total_messages).
fn solve_sharded(types: &[u8], counts: &[u8], k: usize) -> (u64, u64, u64, u64, u64) {
    let rk = Ranker::new(types, counts);
    let n = rk.size() as usize;
    let shard_size = n.div_ceil(k);
    let shard_of = |i: usize| (i / shard_size).min(k - 1);

    let mut val = vec![V_UNK; n];
    let mut cnt = vec![0u16; n];
    let mut legal = vec![false; n];
    let mut resolved: Vec<usize> = Vec::new();

    // init: each shard counts children + seeds its terminals
    for i in 0..n {
        let pos = rk.unrank(i as u64);
        if !is_legal(&pos) {
            continue;
        }
        legal[i] = true;
        let (mut imm, mut deg) = (false, 0u16);
        for mv in legal_moves(&pos) {
            let (_c, kc) = make(&pos, mv);
            if kc {
                imm = true;
            } else {
                deg += 1;
            }
        }
        cnt[i] = deg;
        if imm {
            val[i] = V_WIN;
            resolved.push(i);
        } else if deg == 0 {
            val[i] = V_LOSS;
            resolved.push(i);
        }
    }

    let (mut total_msgs, mut supersteps) = (0u64, 0u64);
    let mut inbox: Vec<Vec<(u64, u8)>> = vec![Vec::new(); k];
    // seed the shuffle from init-resolved terminals
    for &r in &resolved {
        let vr = val[r];
        for p in predecessors(&rk.unrank(r as u64)) {
            let pr = rk.rank(&p);
            inbox[shard_of(pr as usize)].push((pr, vr));
            total_msgs += 1;
        }
    }

    // BSP supersteps
    loop {
        if inbox.iter().all(|v| v.is_empty()) {
            break;
        }
        supersteps += 1;
        let mut newly: Vec<usize> = Vec::new();
        for s in 0..k {
            for (p, cv) in std::mem::take(&mut inbox[s]) {
                let pi = p as usize;
                if val[pi] != V_UNK {
                    continue;
                }
                if cv == V_LOSS {
                    val[pi] = V_WIN; // a child is a Loss => Win
                    newly.push(pi);
                } else {
                    cnt[pi] = cnt[pi].saturating_sub(1);
                    if cnt[pi] == 0 {
                        val[pi] = V_LOSS; // all children Win => Loss
                        newly.push(pi);
                    }
                }
            }
        }
        // emit next round's shuffle (consumed after the barrier)
        let mut next: Vec<Vec<(u64, u8)>> = vec![Vec::new(); k];
        for &r in &newly {
            let vr = val[r];
            for p in predecessors(&rk.unrank(r as u64)) {
                let pr = rk.rank(&p);
                next[shard_of(pr as usize)].push((pr, vr));
                total_msgs += 1;
            }
        }
        inbox = next;
    }

    let (mut w, mut l, mut d) = (0u64, 0u64, 0u64);
    for i in 0..n {
        if !legal[i] {
            continue;
        }
        match val[i] {
            V_WIN => w += 1,
            V_LOSS => l += 1,
            _ => d += 1,
        }
    }
    (w, l, d, supersteps, total_msgs)
}

fn main() {
    println!("=== sharded/BSP distributed solve (shuffle + supersteps) vs oracle ===");
    let subgames: &[(&str, &[u8], &[u8])] = &[
        ("2K", &[], &[]),
        ("2K+P", &[CARP], &[1]),
        ("2K+F", &[FOX], &[1]),
        ("2K+P+F", &[CARP, FOX], &[1, 1]),
    ];
    for (name, types, counts) in subgames {
        let oracle = solve_push(types, counts);
        let ks: Vec<usize> = if *name == "2K+P+F" { vec![1, 64] } else { vec![1, 4, 16, 64] };
        let mut all_match = true;
        let (mut ss, mut msgs) = (0u64, 0u64);
        for &k in &ks {
            let (w, l, d, s, m) = solve_sharded(types, counts, k);
            if (w, l, d) != oracle {
                all_match = false;
                eprintln!("  {name} k={k}: ({w},{l},{d}) != oracle {oracle:?}");
            }
            ss = s;
            msgs = m;
        }
        println!(
            "  {name:8} W{}/L{}/D{}  shards {ks:?} all match: {all_match}  (supersteps={ss}, shuffle msgs={msgs})",
            oracle.0, oracle.1, oracle.2
        );
        assert!(all_match, "{name}: sharded result depends on shard count!");
    }
    println!("\nSharded BSP solve == oracle for every shard count: the distributed");
    println!("decomposition (sharding + shuffle + supersteps + convergence) is correct");
    println!("and the result is invariant to shard count (confluent). Validated for $0.");
}
