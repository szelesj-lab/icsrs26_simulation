# Developer: József Szeles, Department of System Engineering and Department of Electrical Engineering, University of Pannonia
"""Write every number used in the paper as a LaTeX macro (numbers.tex), straight from runs.json.

    python make_numbers.py results/runs.json ../paper/numbers.tex
"""
import json, sys
import numpy as np

R = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
S = {"Base": "base", "Epi": "episodes", "Hin": "hinge"}
A = {"Fixed": "fixed_margin", "Alone": "rl_alone", "Every": "rl_twin_every", "Scaf": "scaffold", "Ret": "scaffold_retire",
     "Ideal": "oracle", "Boole": "scaffold_boole", "Noattr": "scaffold_noattr", "Nolearn": "scaffold_nolearn"}
seeds = sorted({r["seed"] for r in R})
g = {(r["scenario"], r["approach"], r["seed"]): r for r in R}
M = {}


def vals(sc, a, k):
    return np.array([g[(sc, a, s)][k] for s in seeds], dtype=float)


def ms(v):
    return v.mean(), v.std(ddof=1) / np.sqrt(len(v))


def pm(m, s, d=1, sign=False):
    f = f"{{:{'+' if sign else ''}.{d}f}}"
    a = f.format(m).replace("-", "$-$").replace("+", "$+$")
    return f"{a}$\\pm${s:.{d}f}"


def has(sc, a):
    return (sc, a, seeds[0]) in g


KEYS = {"V": ("any_hard", 1), "C": ("viol_controllable", 1), "R": ("twin", 0), "U": ("cpu_total", 1), "O": ("output_pct", 1)}
for sn, sc in S.items():
    for an, a in A.items():
        if not has(sc, a):
            continue
        for kn, (k, d) in KEYS.items():
            m, s = ms(vals(sc, a, k))
            M[f"{sn}{an}{kn}"] = pm(m, s, d)
            M[f"{sn}{an}{kn}m"] = f"{m:.{d}f}"
        M[f"{sn}{an}N"] = f"{vals(sc, a, 'viol_no_safe').mean():.1f}"
        M[f"{sn}{an}Surp"] = f"{vals(sc, a, 'surprises').mean():.1f}"
    # paired differences
    for an, ref in [("Scaf", "rl_twin_every"), ("Ret", "rl_twin_every"), ("Boole", "scaffold"), ("Noattr", "scaffold"),
                    ("Nolearn", "scaffold")]:
        a = A[an]
        if not has(sc, a):
            continue
        for kn, (k, d) in KEYS.items():
            dv = vals(sc, a, k) - vals(sc, ref, k)
            m, s = ms(dv)
            M[f"{sn}D{an}{kn}"] = pm(m, s, d, sign=True)
            M[f"{sn}D{an}{kn}m"] = f"{m:.{d}f}"
    dv = vals(sc, "scaffold", "any_hard") - vals(sc, "fixed_margin", "any_hard")
    M[f"{sn}DScafFixedV"] = pm(*ms(dv), 1, sign=True)

# reductions vs DT on every decision
red_r, red_u, alone_last, ret_save, out_loss = {}, {}, {}, {}, {}
for sn, sc in S.items():
    red_r[sn] = 100 * (1 - vals(sc, "scaffold", "twin").mean() / vals(sc, "rl_twin_every", "twin").mean())
    red_u[sn] = 100 * (1 - vals(sc, "scaffold", "cpu_total").mean() / vals(sc, "rl_twin_every", "cpu_total").mean())
    alone_last[sn] = 100 * vals(sc, "scaffold", "alone_share_last30").mean()
    ret_save[sn] = vals(sc, "scaffold", "cpu_total").mean() - vals(sc, "scaffold_retire", "cpu_total").mean()
    out_loss[sn] = vals(sc, "rl_twin_every", "output_pct").mean() - vals(sc, "scaffold", "output_pct").mean()
M["BaseReqRed"] = f"{red_r['Base']:.0f}"; M["BaseCpuRed"] = f"{red_u['Base']:.0f}"
M["ReqRedMin"] = f"{min(red_r.values()):.0f}"; M["ReqRedMax"] = f"{max(red_r.values()):.0f}"
M["CpuRedMin"] = f"{min(red_u.values()):.0f}"; M["CpuRedMax"] = f"{max(red_u.values()):.0f}"
M["BaseAloneLast"] = f"{alone_last['Base']:.0f}"
M["AloneLastMin"] = f"{min(alone_last.values()):.0f}"; M["AloneLastMax"] = f"{max(alone_last.values()):.0f}"
M["RetSaveMin"] = f"{min(ret_save.values()):.1f}"; M["RetSaveMax"] = f"{max(ret_save.values()):.1f}"
M["OutLossMin"] = f"{min(out_loss.values()):.1f}"; M["OutLossMax"] = f"{max(out_loss.values()):.1f}"
M["BaseDScafOabs"] = f"{out_loss['Base']:.1f}"
M["BaseAloneRatio"] = f"{vals('base', 'rl_alone', 'any_hard').mean() / vals('base', 'scaffold', 'any_hard').mean():.1f}"
M["BaseScafNoSafeShare"] = f"{100 * vals('base', 'scaffold', 'viol_no_safe').sum() / vals('base', 'scaffold', 'any_hard').sum():.0f}"

# calibration
for sn, sc in S.items():
    M[f"{sn}CalPred"] = f"{vals(sc, 'scaffold', 'pred_alone').mean():.2f}"
    M[f"{sn}CalObs"] = f"{vals(sc, 'scaffold', 'obs_alone').mean():.1f}"
    M[f"{sn}CalObsCtrl"] = f"{vals(sc, 'scaffold', 'obs_alone_controllable').mean():.1f}"
    M[f"{sn}Nalone"] = f"{vals(sc, 'scaffold', 'n_alone').mean():.0f}"
M["BaseCalRatio"] = f"{vals('base', 'scaffold', 'obs_alone').mean() / vals('base', 'scaffold', 'pred_alone').mean():.0f}"

# attribution (this work, base)
att = [g[("base", "scaffold", s)]["attribution"] for s in seeds]
for key, name in [("air", "Air"), ("power", "Pow"), ("chiller", "Chil")]:
    sl = np.array([a[key]["slope"] for a in att])
    M[f"{name}Slope"] = f"${sl.mean():.2f}\\pm{sl.std(ddof=1):.2f}$".replace("$-", "$-")
    idd = [a[key]["identified_day"] for a in att if a[key]["identified_day"] is not None]
    M[f"{name}IdDay"] = f"{np.mean(idd):.0f}" if idd else "--"
    M[f"{name}IdN"] = str(len(idd))
iddays = [a[k]["identified_day"] for a in att for k in ("air", "power", "chiller") if a[k]["identified_day"] is not None]
M["IdDayRange"] = f"{min(iddays)}--{max(iddays)}"
rej = np.array([len(a["air"]["rejected_a5_days"]) for a in att], dtype=float)
rej_f = np.array([sum(70 <= d < 75 for d in a["air"]["rejected_a5_days"]) for a in att], dtype=float)
M["AfiveRej"] = f"{rej.mean():.1f}"
M["AfiveShare"] = f"{100 * rej_f.sum() / max(rej.sum(), 1):.0f}"
first = [min([d for d in a["air"]["drift_days"] if d >= 80], default=None) for a in att]
first = [d for d in first if d is not None]
M["AsixDay"] = f"{np.mean(first):.0f}" if first else "--"
M["AsixN"] = str(len(first))
early = [d for a in att for d in a["air"]["drift_days"] if d < 80]
M["AsixEarly"] = str(len(early))
for sn, sc in S.items():
    if has(sc, "scaffold_boole"):
        M[f"{sn}BooleReqPct"] = f"{100 * (vals(sc, 'scaffold_boole', 'twin').mean() / vals(sc, 'scaffold', 'twin').mean() - 1):.0f}"
    if has(sc, "scaffold_noattr"):
        M[f"{sn}NoattrCalObs"] = f"{vals(sc, 'scaffold_noattr', 'obs_alone').mean():.1f}"
    if has(sc, "scaffold_nolearn"):
        M[f"{sn}NolearnReqPct"] = f"{100 * (vals(sc, 'scaffold_nolearn', 'twin').mean() / vals(sc, 'scaffold', 'twin').mean() - 1):.0f}"
        M[f"{sn}NolearnCalObs"] = f"{vals(sc, 'scaffold_nolearn', 'obs_alone').mean():.1f}"
hatt = [g[("hinge", "scaffold", s)]["attribution"]["air"] for s in seeds]
hd = [a["drift_days"][0] for a in hatt if a["drift_days"]]
M["HinAsixDay"] = f"{np.mean(hd):.0f}" if hd else "--"
M["HinAsixN"] = str(len(hd))
M["HinAsixCount"] = f"{np.mean([len(a['drift_days']) for a in hatt]):.1f}"
M["HinMisfitCount"] = f"{np.mean([len(a.get('misfit_days', [])) for a in hatt]):.1f}"
hm = [a["misfit_days"][0] for a in hatt if a.get("misfit_days")]
M["HinMisfitDay"] = f"{np.mean(hm):.0f}" if hm else "--"
M["HinMisfitN"] = str(len(hm))
hs = np.array([a["slope"] for a in hatt])
M["HinAirSlope"] = f"${hs.mean():.2f}\\pm{hs.std(ddof=1):.2f}$"
# A1 and A6 together (base, this work and DT on every decision): drift offset at season end, A1 still holding
for an, a in [("Scaf", "scaffold"), ("Every", "rl_twin_every")]:
    at = [g[("base", a, s)]["attribution"]["air"] for s in seeds]
    M[f"Base{an}AirDrift"] = f"{np.mean([x['drift'] for x in at]):.1f}"
    M[f"Base{an}AirAoneEnd"] = str(sum(x["a1_end"] for x in at))
    M[f"Base{an}AirMisfit"] = f"{np.mean([len(x['misfit_days']) for x in at]):.1f}"
    M[f"Base{an}AirDriftN"] = str(sum(1 for x in at if any(d >= 80 for d in x["drift_days"])))
M["WearTrue"] = f"{-0.15 * 39:.1f}"

with open(OUT, "w") as f:
    f.write("% generated by make_numbers.py from runs.json -- do not edit by hand\n")
    for k, v in sorted(M.items()):
        f.write(f"\\providecommand{{\\{k}}}{{{v}}}\n")
print(f"{len(M)} macros -> {OUT}")
