# Developer: József Szeles, Department of System Engineering and Department of Electrical Engineering, University of Pannonia
"""Monte Carlo convergence study: are the results stable in the number of aleatory samples?

Every risk evaluation (twin request, ideal reference, attribution of a violation hour) estimates
probabilities from n_inner aleatory samples. At the risk limit eps = 0.01, the standard error of one
estimate is sqrt(eps (1 - eps) / n): 0.0031 at n = 1000 (31 % of eps), 0.0010 at n = 10000 (10 %).
This script re-runs the base scenario with n_inner = 1000, 2000, 3000, 5000, 7000 and 10000 for the
approaches that evaluate risk, on the same seeds, and checks how the KPIs move with n.

    python mc_convergence.py --seeds 10 --out results_mc
"""
import argparse, json, os
from multiprocessing import Pool

import numpy as np

from scaffold.config import Config
from scaffold.simulate import simulate
from scaffold import risk as riskmod

NS = [1000, 2000, 3000, 5000, 7000, 10000]
APPS = ["rl_twin_every", "scaffold", "oracle"]


def job(a):
    n, app, seed = a
    cfg = Config(scenario="base", n_inner=n)
    log, ag = simulate(app, cfg, seed)
    alone = [r for r in log if not np.isnan(r["alone_p"])]
    return dict(n_inner=n, approach=app, seed=seed,
                any_hard=int(sum(r["any_hard"] for r in log)),
                viol_controllable=int(sum(r["any_hard"] and not r["no_safe"] for r in log)),
                no_safe_hours=int(sum(r["no_safe"] for r in log)),
                air=float(sum(r["air_nm3"] for r in log)),
                twin=int(sum(r["twin_request"] for r in log)),
                pred_alone=float(sum(r["alone_p"] for r in alone)), obs_alone=int(sum(r["any_hard"] for r in alone)),
                cpu_total=float(ag.cpu["decide"]))


def mc_error_check(out):
    """Direct accuracy of one risk estimate: the union risk of the twin at fixed states, estimated with
    n samples, against a reference with 200000 samples (independent sample matrices)."""
    cfg = Config(scenario="base")
    zero = {"air": np.zeros((1, 2)), "power": np.zeros((1, 2)), "chiller": np.zeros((1, 2))}
    states = [(t_room, t_amb, req) for t_room in (30.0, 36.0, 40.0) for t_amb in (20.0, 28.0) for req in (240.0, 270.0, 280.0)]
    def p_of(n, seed):
        riskmod._Z.clear()
        z = np.random.default_rng(seed).standard_normal((n, 6))
        riskmod._Z[(n, 6)] = z
        return np.array([riskmod.aggregate(riskmod.event_samples(q, tr, cfg.sd_state_twin, ta, 14, zero, cfg, n_inner=n), "joint")[0]
                         for tr, ta, q in states])
    ref = p_of(200000, 1)
    rows = []
    for n in NS:
        est = np.array([p_of(n, 100 + k) for k in range(20)])          # 20 independent repetitions
        err = est - ref
        near = (ref > 0.002) & (ref < 0.05)                              # states near the limit
        rows.append(dict(n=n, rmse_all=float(np.sqrt((err ** 2).mean())),
                         rmse_near=float(np.sqrt((err[:, near] ** 2).mean())) if near.any() else float("nan"),
                         se_at_eps=float(np.sqrt(0.01 * 0.99 / n))))
    riskmod._Z.clear()
    return rows, int(((ref > 0.002) & (ref < 0.05)).sum()), len(states)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--out", default="results_mc"); ap.add_argument("--procs", type=int, default=None)
    args = ap.parse_args(); os.makedirs(args.out, exist_ok=True)
    jobs = [(n, a, s) for n in sorted(NS, reverse=True) for a in APPS for s in range(args.seeds)]
    jobs.sort(key=lambda j: (-j[0] * (4 if j[1] == "rl_twin_every" else 1)))     # long jobs first
    part = os.path.join(args.out, "runs_partial.jsonl")          # checkpoint: a re-run skips finished seasons
    rows = [json.loads(x) for x in open(part)] if os.path.exists(part) else []
    done = {(r["n_inner"], r["approach"], r["seed"]) for r in rows}
    jobs = [j for j in jobs if j not in done]
    with Pool(args.procs) as p, open(part, "a") as fh:
        for i, r in enumerate(p.imap_unordered(job, jobs)):
            rows.append(r); fh.write(json.dumps(r) + "\n"); fh.flush()
            print(f"{i + 1}/{len(jobs)} n={r['n_inner']} {r['approach']} {r['seed']}", flush=True)
    ideal = {(r["n_inner"], r["seed"]): r["air"] for r in rows if r["approach"] == "oracle"}
    for r in rows:
        r["output_pct"] = 100 * r["air"] / ideal[(r["n_inner"], r["seed"])]
    json.dump(rows, open(os.path.join(args.out, "runs.json"), "w"))
    mc, n_near, n_states = mc_error_check(args.out)

    def ms(v):
        v = np.asarray(v, float); return v.mean(), v.std(ddof=1) / np.sqrt(len(v))
    g = {(r["n_inner"], r["approach"], r["seed"]): r for r in rows}
    seeds = sorted({r["seed"] for r in rows})
    L = ["# Monte Carlo convergence (base scenario, mean ± standard error over seeds)", "",
         "## Accuracy of one risk estimate", "",
         f"Union risk of the twin at {n_states} fixed states ({n_near} near the limit, 0.2–5 %), 20 repetitions per n, "
         "against a reference with 200 000 samples.", "",
         "| n | RMSE, all states | RMSE, near the limit | binomial SE at ε = 0.01 |", "|---|---|---|---|"]
    for m in mc:
        L.append(f"| {m['n']} | {m['rmse_all']:.4f} | {m['rmse_near']:.4f} | {m['se_at_eps']:.4f} |")
    L += ["", "## KPIs against n", "",
          "| n | Approach | Violations, h | Controllable, h | Twin requests | Output, % of ideal | CPU per season, s | Alone: predicted / observed |",
          "|---|---|---|---|---|---|---|---|"]
    for n in NS:
        for a in APPS:
            rs = [g[(n, a, s)] for s in seeds]
            f = lambda k, d=1: "{:.{d}f} ± {:.{d}f}".format(*ms([r[k] for r in rs]), d=d)
            cal = f"{np.mean([r['pred_alone'] for r in rs]):.2f} / {np.mean([r['obs_alone'] for r in rs]):.1f}" if a == "scaffold" else "–"
            L.append(f"| {n} | {a} | {f('any_hard')} | {f('viol_controllable')} | {f('twin', 0)} | {f('output_pct')} | {f('cpu_total')} | {cal} |")
    L += ["", "## Paired change against n = 10000 (same seeds)", "",
          "| n | Approach | Δ violations, h | Δ controllable, h | Δ twin requests | Δ output, pp |", "|---|---|---|---|---|---|"]
    for n in NS[:-1]:
        for a in APPS:
            cells = []
            for k, d in (("any_hard", 1), ("viol_controllable", 1), ("twin", 0), ("output_pct", 2)):
                dv = [g[(n, a, s)][k] - g[(10000, a, s)][k] for s in seeds]
                cells.append("{:+.{d}f} ± {:.{d}f}".format(*ms(dv), d=d))
            L.append(f"| {n} | {a} | " + " | ".join(cells) + " |")
    open(os.path.join(args.out, "summary.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
