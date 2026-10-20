"""Paired differences between approaches (same seed = same weather and demand).
python paired.py results/runs.json > results/paired.md"""
import json, sys
import numpy as np

R = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "results/runs.json"))
g = {(r["scenario"], r["approach"], r["seed"]): r for r in R}
seeds = sorted({r["seed"] for r in R})
PAIRS = [("scaffold", "rl_twin_every"), ("scaffold", "rl_alone"), ("scaffold", "fixed_margin"),
         ("scaffold_retire", "rl_twin_every"), ("scaffold_boole", "scaffold"), ("scaffold_noattr", "scaffold")]
KEYS = [("any_hard", "Δ hard violations, h"), ("viol_controllable", "Δ controllable violations, h"),
        ("twin", "Δ twin requests"), ("output_pct", "Δ output, pp of ideal"), ("cpu_total", "Δ CPU per season, s")]
print("| Scenario | Comparison | " + " | ".join(n for _, n in KEYS) + " |")
print("|---|---|" + "---|" * len(KEYS))
for sc in ["base", "episodes", "hinge"]:
    for a, b in PAIRS:
        if (sc, a, seeds[0]) not in g:
            continue
        cells = []
        for k, _ in KEYS:
            d = np.array([g[(sc, a, s)][k] - g[(sc, b, s)][k] for s in seeds], dtype=float)
            cells.append(f"{d.mean():+.1f} ± {d.std(ddof=1) / np.sqrt(len(d)):.1f}")
        print(f"| {sc} | {a} − {b} | " + " | ".join(cells) + " |")
print("\nMean ± standard error of the paired difference over seeds. Controllable: hours in which at least one "
      "production level had a true system-level risk below the limit.")
