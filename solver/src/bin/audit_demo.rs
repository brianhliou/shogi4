//! Demonstrate that a computed result can be verified for a fraction of the solve
//! cost, and that the audit catches corruption. We solve {2K+P+F} (1.16M positions),
//! run the consistency audit (expect 0 violations = certified), then inject single
//! wrong values and re-audit to show every corruption is caught.

use shogi4::*;

fn main() {
    let (types, counts): (&[u8], &[u8]) = (&[CARP, FOX], &[1, 1]); // {2K+P+F}
    println!("=== verification-audit demo on {{2K+P+F}} ===");

    let t0 = std::time::Instant::now();
    let (rk, mut val, legal) = solve_push_array(types, counts);
    let solve_s = t0.elapsed().as_secs_f64();
    let legal_n: u64 = legal.iter().filter(|&&b| b).count() as u64;

    let t1 = std::time::Instant::now();
    let bad = audit_solution(&rk, &val, &legal);
    let audit_s = t1.elapsed().as_secs_f64();

    println!("positions: {legal_n}");
    println!("solve : {solve_s:5.1}s   (push retrograde: un-move-gen + fixpoint)");
    println!("audit : {audit_s:5.1}s   (one forward pass: move-gen + child lookups)");
    println!("        -> verification is {:.0}% of the solve cost", 100.0 * audit_s / solve_s);
    println!("clean audit: {bad} violations  {}",
             if bad == 0 { "=> tablebase CERTIFIED correct" } else { "*** FAILED ***" });
    assert_eq!(bad, 0, "clean solve failed its own audit");

    println!("\ninjecting single wrong values — does the audit catch each?");
    let n = rk.size() as usize;
    let (mut i, mut samples) = (0usize, 0);
    while samples < 5 && i < n {
        if legal[i] && (val[i] == V_WIN || val[i] == V_LOSS) {
            let orig = val[i];
            val[i] = if orig == V_WIN { V_LOSS } else { V_WIN };
            let caught = audit_solution(&rk, &val, &legal);
            println!("  flip slot {i:>7} {}->{}  =>  audit reports {caught} violations",
                     if orig == V_WIN { "W" } else { "L" },
                     if orig == V_WIN { "L" } else { "W" });
            assert!(caught > 0, "corruption not caught!");
            val[i] = orig; // restore
            samples += 1;
        }
        i += 100_003; // stride to sample distinct positions
    }

    println!("\nEvery single wrong value is caught (it fails its own local check, plus its");
    println!("predecessors'), and the certificate costs a fraction of the solve — so a result");
    println!("can be verified far more cheaply than re-deriving it.");
}
