//! Failure-recovery simulation (belt-and-suspenders for rung 4).
//!
//! A BSP superstep is a deterministic function of (checkpoint state + inbox). We
//! inject crashes at many supersteps: snapshot the state (the checkpoint), run the
//! superstep, then "crash" (discard the work, roll back to the checkpoint) and
//! REPLAY the superstep. We assert the replay reproduces the superstep byte-for-byte
//! (idempotent recovery), and that the final result is identical to the crash-free
//! run. This is the basis of "a shard = a checkpoint + a deterministic recompute".

use shogi4::*;

/// One BSP superstep: apply the inbox (mutating val/cnt) and emit the next shuffle.
/// Pure in (val,cnt,inbox) -> (val',cnt',next), so replaying from a checkpoint is exact.
fn superstep(
    val: &mut [u8],
    cnt: &mut [u16],
    inbox: &[Vec<(u64, u8)>],
    k: usize,
    shard_size: usize,
    rk: &Ranker,
) -> Vec<Vec<(u64, u8)>> {
    let shard_of = |i: usize| (i / shard_size).min(k - 1);
    let mut newly: Vec<usize> = Vec::new();
    for s in 0..k {
        for &(p, cv) in &inbox[s] {
            let pi = p as usize;
            if val[pi] != V_UNK {
                continue;
            }
            if cv == V_LOSS {
                val[pi] = V_WIN;
                newly.push(pi);
            } else {
                cnt[pi] = cnt[pi].saturating_sub(1);
                if cnt[pi] == 0 {
                    val[pi] = V_LOSS;
                    newly.push(pi);
                }
            }
        }
    }
    let mut next: Vec<Vec<(u64, u8)>> = vec![Vec::new(); k];
    for &r in &newly {
        let vr = val[r];
        for pp in predecessors(&rk.unrank(r as u64)) {
            let pr = rk.rank(&pp);
            next[shard_of(pr as usize)].push((pr, vr));
        }
    }
    next
}

/// Returns (W, L, D, crashes_recovered).
fn solve_with_recovery(types: &[u8], counts: &[u8], k: usize, crash_at: &[u64]) -> (u64, u64, u64, u64) {
    let rk = Ranker::new(types, counts);
    let n = rk.size() as usize;
    let shard_size = n.div_ceil(k);
    let shard_of = |i: usize| (i / shard_size).min(k - 1);
    let mut val = vec![V_UNK; n];
    let mut cnt = vec![0u16; n];
    let mut legal = vec![false; n];
    let mut resolved: Vec<usize> = Vec::new();

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

    let mut inbox: Vec<Vec<(u64, u8)>> = vec![Vec::new(); k];
    for &r in &resolved {
        let vr = val[r];
        for pp in predecessors(&rk.unrank(r as u64)) {
            let pr = rk.rank(&pp);
            inbox[shard_of(pr as usize)].push((pr, vr));
        }
    }

    let (mut step, mut recovered) = (0u64, 0u64);
    loop {
        if inbox.iter().all(|v| v.is_empty()) {
            break;
        }
        step += 1;
        if crash_at.contains(&step) {
            let (val_ckpt, cnt_ckpt) = (val.clone(), cnt.clone()); // durable checkpoint
            let next1 = superstep(&mut val, &mut cnt, &inbox, k, shard_size, &rk);
            let after1 = (val.clone(), cnt.clone(), next1);
            // CRASH: lose all of this superstep's work, restore the checkpoint
            val = val_ckpt;
            cnt = cnt_ckpt;
            // RECOVER: deterministic replay from the checkpoint + the same inbox
            let next2 = superstep(&mut val, &mut cnt, &inbox, k, shard_size, &rk);
            let after2 = (val.clone(), cnt.clone(), next2);
            assert!(after1 == after2, "recovery NOT idempotent at superstep {step}");
            recovered += 1;
            inbox = after2.2;
        } else {
            inbox = superstep(&mut val, &mut cnt, &inbox, k, shard_size, &rk);
        }
    }

    let (mut w, mut l, mut d) = (0u64, 0u64, 0u64);
    for i in 0..n {
        if legal[i] {
            match val[i] {
                V_WIN => w += 1,
                V_LOSS => l += 1,
                _ => d += 1,
            }
        }
    }
    (w, l, d, recovered)
}

fn main() {
    println!("=== failure-recovery simulation (crash + deterministic replay) ===");
    let cases: &[(&str, &[u8], &[u8])] = &[
        ("2K", &[], &[]),
        ("2K+P", &[CARP], &[1]),
        ("2K+F", &[FOX], &[1]),
        ("2K+P+F", &[CARP, FOX], &[1, 1]),
    ];
    let crashes: Vec<u64> = (1..=80).step_by(3).collect(); // crash at supersteps 1,4,7,...
    for (name, types, counts) in cases {
        let clean = solve_push(types, counts);
        let (w, l, d, rec) = solve_with_recovery(types, counts, 16, &crashes);
        let ok = (w, l, d) == clean;
        println!(
            "  {name:8} clean W{}/L{}/D{}  | {rec} crash-recoveries (every replay idempotent) -> {}",
            clean.0, clean.1, clean.2,
            if ok { "result IDENTICAL" } else { "*** RESULT DIFFERS ***" }
        );
        assert!(ok, "{name}: crashes changed the result!");
    }
    println!("\nCrashes injected at many supersteps: each deterministic replay reproduced the");
    println!("superstep byte-for-byte, and every final result is identical to the crash-free run.");
    println!("Recovery is exact and idempotent — a shard = a checkpoint + a deterministic recompute.");
}
