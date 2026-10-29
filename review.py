# Developer: József Szeles, Department of System Engineering and Department of Electrical Engineering, University of Pannonia
"""Additional runs for the ICSRS 2026 review (branch icsrs-revision; main is unchanged).

    python review.py --out results_review

1. Data-driven safety filters without a twin (cautious / explores), all scenarios.
2. Fallback statistics of this work: re-run of 'scaffold' and 'rl_twin_every' with the
   fallback logged (same seeds, so the results equal results/runs.json).
3. Coupling-strength sweep: all three missing couplings scaled by kappa, base scenario.
Rows carry 'kappa' (1.0 = paper). Output % uses the ideal reference of the same
scenario, seed and kappa."""
import argparse, json, os
from multiprocessing import Pool

from run import job, SCEN

KAPPAS = (0.0, 0.5, 1.5, 2.0)


def kappa_over(k):
    return dict(coupling_true=-1.0 * k, comp_eff_coef=0.01 * k, chiller_derate=-1.5 * k)




def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10); ap.add_argument("--out", default="results_review")
    ap.add_argument("--procs", type=int, default=None)
    args = ap.parse_args(); os.makedirs(args.out, exist_ok=True)
    jobs = [(sc, a, s) for s in range(args.seeds) for sc in SCEN
            for a in ("filter_cautious", "filter_explore", "scaffold", "rl_twin_every", "oracle")]
    for k in KAPPAS:
        jobs += [("base", a, s, kappa_over(k)) for s in range(args.seeds)
                 for a in ("scaffold", "rl_twin_every", "oracle", "fixed_margin", "filter_explore")]
    # sensitivity of the credible level: alpha = 0.01 (z = 2.326) instead of 0.05 (z = 1.645)
    jobs += [("base", a, s, dict(range_q=(0.01, 0.99), critic_z=2.326, _alpha=0.01)) for s in range(args.seeds)
             for a in ("scaffold", "rl_twin_every")]
    jobs.sort(key=lambda j: j[1] != "rl_twin_every")
    path = os.path.join(args.out, "runs.jsonl")
    done = set()
    if os.path.exists(path):
        for line in open(path):
            r = json.loads(line); done.add((r["scenario"], r["approach"], r["seed"], r["kappa"]))
    def kap(j):
        if len(j) < 4: return 1.0
        return -j[3]["coupling_true"] if "coupling_true" in j[3] else "alpha" + str(j[3]["_alpha"])
    jobs = [j for j in jobs if (j[0], j[1], j[2], kap(j)) not in done]
    jobs = [j if len(j) < 4 else (*j[:3], {**j[3]}) for j in jobs]
    with Pool(args.procs) as p, open(path, "a") as f:
        for i, r in enumerate(p.imap_unordered(job_k, jobs)):
            f.write(json.dumps(r) + "\n"); f.flush()
            print(f"{i + 1}/{len(jobs)} {r['scenario']} {r['approach']} {r['seed']} k={r['kappa']}", flush=True)


def job_k(j):
    r = job(j)
    r["kappa"] = 1.0 if len(j) < 4 else (-j[3]["coupling_true"] if "coupling_true" in j[3] else "alpha" + str(j[3]["_alpha"]))
    return r


if __name__ == "__main__":
    main()
