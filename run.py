# Developer: József Szeles, Department of System Engineering and Department of Electrical Engineering, University of Pannonia
"""Twin-as-scaffold study.

    python run.py --seeds 10 --out results      # main study + ablations
    python paired.py results/runs.json          # paired differences
    python figures.py results                   # Fig. 2 of the paper and an overview figure
"""
import argparse, json, os
from multiprocessing import Pool

import numpy as np

from scaffold.config import Config
from scaffold.simulate import simulate, APPROACHES

SCEN = ["base", "episodes", "hinge"]
# ablations of "this work": (approach used, config overrides, scenarios)
ABLATIONS = {"scaffold_boole": ("scaffold", dict(aggregation="boole"), ["base", "episodes"]),
             "scaffold_noattr": ("scaffold", dict(attribution=False), ["base", "episodes"]),
             "scaffold_nolearn": ("scaffold", dict(interaction_learning=False), ["base", "episodes"])}
LABEL = {"fixed_margin": "Fixed safety margins", "rl_alone": "RL alone (no twin)", "rl_twin_every": "RL + twin on every decision",
         "scaffold": "This work: RL asks the twin when unsure", "scaffold_retire": "This work, twin retired after day 60",
         "oracle": "Ideal reference (knows the plant)",
         "scaffold_boole": "Ablation: Boole bound instead of union", "scaffold_noattr": "Ablation: no attribution checks",
         "scaffold_nolearn": "Ablation: no interaction learning (twin uncorrected)",
         "filter_cautious": "Data-driven filter, no twin (cautious)", "filter_explore": "Data-driven filter, no twin (explores)"}
EVENTS = ("shortage", "lost", "cooling_short", "peak", "thermal")


def job(a):
    sc, name, seed = a[:3]
    app, over, _ = ABLATIONS.get(name, (name, {}, None))
    cfg = Config(scenario=sc, **over, **{k: v for k, v in (a[3] if len(a) > 3 else {}).items() if not k.startswith("_")})
    log, ag = simulate(app, cfg, seed)
    days = cfg.days
    dq, dv, dvn = np.zeros(days), np.zeros(days), np.zeros(days)
    for r in log:
        dq[r["day"]] += r["twin_request"]; dv[r["day"]] += r["any_hard"]; dvn[r["day"]] += r["any_hard"] and r["no_safe"]
    alone = [r for r in log if not np.isnan(r["alone_p"])]
    asked = [r for r in log if r["twin_request"]]
    row = dict(scenario=sc, approach=name, seed=seed,
               any_hard=int(sum(r["any_hard"] for r in log)),
               any_hard_first30=int(sum(r["any_hard"] for r in log if r["day"] < 30)),
               any_hard_last40=int(sum(r["any_hard"] for r in log if r["day"] >= 80)),
               no_safe_hours=int(sum(r["no_safe"] for r in log)),
               viol_no_safe=int(sum(r["any_hard"] and r["no_safe"] for r in log)),
               events={k: int(sum(r[k] for r in log)) for k in EVENTS},
               events_controllable={k: int(sum(r[k] and not r["no_safe"] for r in log)) for k in EVENTS},
               air=float(sum(r["air_nm3"] for r in log)),
               twin=int(len(asked)),
               twin_last30=int(sum(r["twin_request"] for r in log if r["day"] >= days - 30)),
               alone_share_last30=float(np.mean([not r["twin_request"] for r in log if r["day"] >= days - 30])),
               n_alone=len(alone), pred_alone=float(sum(r["alone_p"] for r in alone)),
               obs_alone=int(sum(r["any_hard"] for r in alone)),
               obs_alone_controllable=int(sum(r["any_hard"] and not r["no_safe"] for r in alone)),
               viol_asked=int(sum(r["any_hard"] for r in asked)),
               fallback_hours=int(sum(r["fallback"] for r in log)),
               fallback_viol=int(sum(r["fallback"] and r["any_hard"] for r in log)),
               fallback_no_safe=int(sum(r["fallback"] and r["no_safe"] for r in log)),
               fallback_viol_controllable=int(sum(r["fallback"] and r["any_hard"] and not r["no_safe"] for r in log)),
               surprises=len(ag.critic.surprises) if app != "oracle" else 0,
               cpu_total=float(ag.cpu["decide"]), cpu_twin=float(ag.cpu_twin), n_sim=int(ag.n_sim),
               daily_q=dq.tolist(), daily_v=dv.tolist(), daily_v_no_safe=dvn.tolist())
    row["viol_controllable"] = row["any_hard"] - row["viol_no_safe"]
    if app in ("scaffold", "rl_twin_every", "scaffold_retire"):
        row["attribution"] = ag.attribution_summary()
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10); ap.add_argument("--out", default="results")
    ap.add_argument("--procs", type=int, default=None)
    ap.add_argument("--only", default="", help="comma-separated approaches to re-run; other rows are kept from runs.json")
    args = ap.parse_args(); os.makedirs(args.out, exist_ok=True)
    jobs = [(sc, a, s) for s in range(args.seeds) for sc in SCEN for a in APPROACHES]
    jobs += [(sc, a, s) for s in range(args.seeds) for a, (_, _, scs) in ABLATIONS.items() for sc in scs]
    keep = []
    if args.only:
        only = set(args.only.split(","))
        jobs = [j for j in jobs if j[1] in only]
        keep = [r for r in json.load(open(os.path.join(args.out, "runs.json"))) if r["approach"] not in only]
    jobs.sort(key=lambda j: j[1] != "rl_twin_every")          # long jobs first
    rows = list(keep)
    with Pool(args.procs) as p:
        for i, r in enumerate(p.imap_unordered(job, jobs)):
            rows.append(r); print(f"{i + 1}/{len(jobs)} {r['scenario']} {r['approach']} {r['seed']}", flush=True)
    orc = {(r["scenario"], r["seed"]): r["air"] for r in rows if r["approach"] == "oracle"}
    for r in rows:
        r["lost_pct"] = 100 * (1 - r["air"] / orc[(r["scenario"], r["seed"])])
        r["output_pct"] = 100 - r["lost_pct"]
    rows.sort(key=lambda r: (r["scenario"], r["approach"], r["seed"]))
    json.dump(rows, open(os.path.join(args.out, "runs.json"), "w"))
    write_summary(rows, args.out)


def _m(rs, k):
    v = np.array([r[k] for r in rs], dtype=float)
    return v.mean(), v.std(ddof=1) / np.sqrt(len(v))


def write_summary(rows, out):
    names = APPROACHES + list(ABLATIONS)
    L = ["Mean ± standard error over seeds (seasons).", "",
         "| Scenario | Approach | Hard violations, h | of which no safe level, h | controllable, h | Twin requests | "
         "Decisions without twin, last 30 days | CPU per season, s | of which twin, s | Output, % of ideal | "
         "Alone: predicted / observed violations | Surprises |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for sc in SCEN:
        for a in names:
            rs = [r for r in rows if r["scenario"] == sc and r["approach"] == a]
            if not rs:
                continue
            f = lambda k, d=1: "{:.{d}f} ± {:.{d}f}".format(*_m(rs, k), d=d)
            cal = (f"{_m(rs, 'pred_alone')[0]:.2f} / {_m(rs, 'obs_alone')[0]:.1f}" if a.startswith("scaffold") else "–")
            L.append(f"| {sc} | {LABEL[a]} | {f('any_hard')} | {f('viol_no_safe')} | {f('viol_controllable')} | {f('twin', 0)} | "
                     f"{100 * _m(rs, 'alone_share_last30')[0]:.0f} % | {f('cpu_total')} | {_m(rs, 'cpu_twin')[0]:.1f} | "
                     f"{f('output_pct')} | {cal} | {_m(rs, 'surprises')[0]:.1f} |")
    L += ["", "Hours with hard-limit events, mean per season (controllable hours in brackets):", "",
          "| Scenario | Approach | " + " | ".join(EVENTS) + " | hours without a safe level |", "|---|---|" + "---|" * (len(EVENTS) + 1)]
    for sc in SCEN:
        for a in names:
            rs = [r for r in rows if r["scenario"] == sc and r["approach"] == a]
            if not rs:
                continue
            cells = [f"{np.mean([r['events'][k] for r in rs]):.1f} ({np.mean([r['events_controllable'][k] for r in rs]):.1f})" for k in EVENTS]
            L.append(f"| {sc} | {LABEL[a]} | " + " | ".join(cells) + f" | {_m(rs, 'no_safe_hours')[0]:.1f} |")
    L += ["", "Attribution (this work, mean over seeds): learned slope ± sd at season end (true value), "
          "first day identified, residuals rejected by A5 (of which on fault days 70–74), A6 drift detections and first day, "
          "A6 model-form detections, drift offset at season end, A1 at season end:", "",
          "| Scenario | Approach | Coupling | Slope (true) | Identified on day | A5 rejections (fault days) | A6 drift detections | first drift day | A6 misfit detections | drift offset | A1 at end |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    true = {"air": {"base": -1.0, "episodes": -1.0, "hinge": "hinge"}, "power": 0.12 * 270 * 0.01, "chiller": -1.5}
    for sc in SCEN:
        for a in ["scaffold", "scaffold_noattr", "scaffold_nolearn", "rl_twin_every"]:
            rs = [r for r in rows if r["scenario"] == sc and r["approach"] == a and "attribution" in r]
            if not rs:
                continue
            for k in ("air", "power", "chiller"):
                A = [r["attribution"][k] for r in rs]
                tv = true[k][sc] if isinstance(true[k], dict) else true[k]
                tv = f"{tv:.2f}" if not isinstance(tv, str) else tv
                idd = [x["identified_day"] for x in A if x["identified_day"] is not None]
                rej = [len(x["rejected_a5_days"]) for x in A]
                rej_f = [sum(70 <= d < 75 for d in x["rejected_a5_days"]) for x in A]
                dr = [len(x["drift_days"]) for x in A]
                d1 = [x["drift_days"][0] for x in A if x["drift_days"]]
                L.append(f"| {sc} | {LABEL[a]} | {k} | {np.mean([x['slope'] for x in A]):.2f} ± {np.mean([x['slope_sd'] for x in A]):.2f} ({tv}) | "
                         f"{(np.mean(idd) if idd else float('nan')):.1f} ({len(idd)}/{len(A)}) | {np.mean(rej):.1f} ({np.mean(rej_f):.1f}) | "
                         f"{np.mean(dr):.1f} | {(np.mean(d1) if d1 else float('nan')):.0f} | "
                         f"{np.mean([len(x.get('misfit_days', [])) for x in A]):.1f} | {np.mean([x.get('drift', 0.0) for x in A]):.1f} | "
                         f"{sum(x.get('a1_end', False) for x in A)}/{len(A)} |")
    open(os.path.join(out, "summary.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
