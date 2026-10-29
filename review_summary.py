# Developer: József Szeles, Department of System Engineering and Department of Electrical Engineering, University of Pannonia
"""Summary of the review runs:  python review_summary.py results_review"""
import json, os, sys

import numpy as np

out = sys.argv[1] if len(sys.argv) > 1 else "results_review"
rows = [json.loads(l) for l in open(os.path.join(out, "runs.jsonl"))]
for r in rows:
    r["kappa"] = str(r["kappa"]).replace("-0.0", "0.0")
orc = {(r["scenario"], r["kappa"], r["seed"]): r["air"] for r in rows if r["approach"] == "oracle"}
for r in rows:
    k = r["kappa"] if not r["kappa"].startswith("alpha") else "1.0"
    o = orc.get((r["scenario"], k, r["seed"])); r["output_pct"] = 100 * r["air"] / o if o else float("nan")


def ms(v):
    v = np.asarray(v, float)
    return v.mean(), (v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0.0)


def fmt(v, d=1):
    m, s = ms(v)
    return f"{m:.{d}f} ± {s:.{d}f}"


def sel(sc, a, k):
    return sorted([r for r in rows if r["scenario"] == sc and r["approach"] == a and r["kappa"] == k], key=lambda r: r["seed"])


KEYS = [("any_hard", "Violations h"), ("viol_controllable", "Controllable h"), ("any_hard_first30", "Viol. days 0-29"),
        ("twin", "Twin requests"), ("cpu_total", "CPU s"), ("output_pct", "Output %"),
        ("fallback_hours", "Fallback h"), ("fallback_viol", "Fallback viol h"),
        ("fallback_viol_controllable", "Fallback controllable viol h"), ("no_safe_hours", "No-safe-level h")]
L = ["# Review runs (branch icsrs-revision)", "", "Mean ± SE over seeds. Paired differences against 'scaffold' (this work) of the same scenario, kappa and seed.", ""]
groups = sorted({(r["scenario"], r["kappa"]) for r in rows})
for sc, k in groups:
    L += [f"## scenario={sc}, kappa={k}", "", "| Approach | " + " | ".join(n for _, n in KEYS) + " |", "|---|" + "---|" * len(KEYS)]
    for a in ("rl_alone", "fixed_margin", "filter_cautious", "filter_explore", "rl_twin_every", "scaffold", "oracle"):
        rs = sel(sc, a, k)
        if rs:
            L.append(f"| {a} (n={len(rs)}) | " + " | ".join(fmt([r[key] for r in rs], 0 if key == 'twin' else 1) for key, _ in KEYS) + " |")
    base = {r["seed"]: r for r in sel(sc, "scaffold", k)}
    for a in ("fixed_margin", "filter_cautious", "filter_explore", "rl_twin_every"):
        rs = [r for r in sel(sc, a, k) if r["seed"] in base]
        if rs:
            L.append(f"| {a} − scaffold | " + " | ".join(fmt([r[key] - base[r['seed']][key] for r in rs], 0 if key == 'twin' else 1) for key, _ in KEYS) + " |")
    sc_rs, ev_rs = sel(sc, "scaffold", k), sel(sc, "rl_twin_every", k)
    if sc_rs and ev_rs:
        rq = 100 * (1 - np.mean([r["twin"] for r in sc_rs]) / np.mean([r["twin"] for r in ev_rs]))
        cp = 100 * (1 - np.mean([r["cpu_total"] for r in sc_rs]) / np.mean([r["cpu_total"] for r in ev_rs]))
        L.append(f"\nThis work vs DT on every decision: {rq:.0f} % fewer requests, {cp:.0f} % less CPU.")
    L.append("")
open(os.path.join(out, "summary.md"), "w").write("\n".join(L))
print("\n".join(L))
