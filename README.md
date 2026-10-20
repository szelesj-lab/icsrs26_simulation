# The digital twin as a scaffold for a risk-aware RL agent

Simulation package for the paper
*Residual-Driven Interaction Learning for System-Level Risk-Informed Decision Support in Industrial Energy Systems*
(J. Szeles, T. Ruppert, E. Zio).

Once per hour, an RL agent chooses the air request of a pneumatic production line with a compressor
room (nine levels, 200–280 Nl/min). Besides its policy it learns

1. what the digital twin gets wrong: residual models of the three missing couplings (air delivery and
   compressor power vs. room temperature, chiller capacity vs. ambient temperature), used as
   interactions only under the attribution conditions,
2. the system-level risk of each action: the probability that at least one hard limit is violated
   (union of the limits),
3. how sure it is about that risk: a range from the posterior of its risk model and its own misfit.

It asks the twin for a simulation only when its risk range crosses the limit, when no safe action is
known, or when real outcomes surprise it. As it learns it asks less, and the twin can be retired.

**All plant and twin parameters are hypothetical.** The model is a simplified stand-in for the FESTO
line of the Industry 5.0 Lab; the numbers show the behaviour of the method, not of the real plant.

## Run

```bash
pip install -r requirements.txt
python run.py --seeds 10 --out results        # 3 scenarios x 6 approaches x 10 seasons + 2 ablations x 2 scenarios
python paired.py results/runs.json > results/paired.md
python figures.py results                     # Fig. 2 of the paper (fig2_base.pdf) and overview.png
python make_numbers.py results/runs.json numbers.tex   # every number of the paper as a LaTeX macro
```

Python 3.10+; only numpy, scipy and matplotlib are needed. The full run takes about 45 min on 2 cores.

## Code

| File | Content |
|---|---|
| `scaffold/config.py` | all parameters and the scenarios |
| `scaffold/plant.py` | the plant: demand, compressor, room heat, chiller, site power, weather, sensor fault, wear, clogging |
| `scaffold/twin.py` | the digital twin; it misses the effect of intake temperature on air delivery and compressor power, and chiller derating |
| `scaffold/learner.py` | Bayesian residual learner for one coupling, with the attribution conditions A1, A2, A5, A6 |
| `scaffold/risk.py` | Monte Carlo risk: aleatory inner samples, epistemic outer samples, union (or Boole bound) of hard-limit events |
| `scaffold/agent.py` | `ScaffoldAgent` (policy, residual models, decision rule A/B/C) and `RiskCritic` (risk model and range) |
| `scaffold/simulate.py` | one season (120 days, 16 decisions per day = 1920 decisions) for one approach; the ideal reference |
| `run.py` | the full study and `results/summary.md` |
| `paired.py` | paired differences over seeds |
| `figures.py`, `make_numbers.py` | paper figure and numbers |

## What the code does (as described in the paper)

- **Decision rule.** Case A (upper bound below the limit): act alone. Case B (range crosses the limit):
  ask the twin. Case C (lower bound above the limit): take the highest level below the proposal whose
  upper bound is below the limit; ask the twin only if there is none. After a request, the executed
  level is the highest one up to the proposal whose upper bound *from the twin* is below the limit.
  Fallback without a safe level (or without twin): the lowest level.
- **Policy.** One-step values per room-temperature bin (gamma = 0); reward = delivered air minus
  penalties for observed violations; an overridden proposal gets a small extra penalty. Energy cost is
  logged but not priced.
- **Attribution.** A1 (residual near zero where no coupling acts) and A2 (slope excludes zero) must
  hold before a residual pattern is used as an interaction; before that, the twin is corrected with
  zero mean and a variance covering the prior and the pattern. A5 rejects delivery residuals when the
  meter and the pressure-implied value disagree (sensor bias on days 70–74). A6 attributes a biased
  one-step error to drift and forgets the old offset (wear from day 80, clogging). A3 and A4 are not
  exercised. `Config(attribution=False)` switches all checks off (ablation).
- **Risk aggregation.** `Config(aggregation="joint")` (union, default) or `"boole"` (ablation).
- **Controllable violations.** A violation hour is controllable if at least one level had a true
  system-level risk below the limit in that state (diagnostic, not timed, not seen by the agent).

## Scenarios and approaches

Scenarios: `base`; `episodes` (plant change: random clogging episodes from day 60, after the learning
phase); `hinge` (the true delivery loss starts only above 30 °C, unlike the linear residual model).
The plant also has a scenario `ambient` that is not used in the paper.

Approaches: fixed safety margins; RL alone (no twin); RL + twin on every decision; this work; this work
with the twin retired after day 60; ideal reference (knows the plant, not the future noise; chooses the
highest level whose true risk is below the limit). Ablations of this work: Boole bound instead of the
union; no attribution checks.

## Results

`results/summary.md` (all KPIs, event types, attribution), `results/paired.md` (paired differences),
`results/fig2_base.pdf` (paper Fig. 2), `results/overview.png` (weekly twin requests, all scenarios).
The results of the earlier version of the package (episodes from day 0, no attribution gate) are in
`results_v1/`.

## Simplifications

Linear-in-features logistic risk model; tabular one-step policy; one decision variable without a
shutdown option; residuals are learned only in hours the twin was asked; after the twin is retired,
changes are seen only through outcomes.
