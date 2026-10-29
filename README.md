# The digital twin as a scaffold for a risk-aware RL agent

Simulation package for the paper

> J. Szeles, T. Ruppert, E. Zio, *Residual-Driven Interaction Learning for System-Level
> Risk-Informed Decision Support in Industrial Energy Systems*, ICSRS 2026.

**Developer:** József Szeles, Department of System Engineering and Department of Electrical Engineering,
University of Pannonia

It reproduces every number, table and figure of the paper's case study: a pneumatic production
line whose compressor heats its own room, a digital twin (DT) that misses three couplings, and an
RL agent that asks the twin only when it is unsure about the system-level risk of its decision.

**All plant and twin parameters are hypothetical.** The model is a simplified stand-in for the
FESTO line of the Industry 5.0 Lab at the University of Pannonia. The results show how the method
behaves, not how the real line behaves.

---

## Contents

1. [Quick start](#quick-start)
2. [What is simulated](#what-is-simulated)
3. [Package layout](#package-layout)
4. [Model details](#model-details)
5. [Approaches and scenarios](#approaches-and-scenarios)
6. [Outputs](#outputs)
7. [Reproducing the paper](#reproducing-the-paper)
8. [Configuration](#configuration)
9. [Randomness and paired comparison](#randomness-and-paired-comparison)
10. [Expected results](#expected-results)
11. [Limitations](#limitations)
12. [Citation and acknowledgment](#citation-and-acknowledgment)

---

## Quick start

```bash
pip install -r requirements.txt
python run.py --seeds 10 --out results                    # all seasons (about 45 min on 2 cores)
python paired.py results/runs.json > results/paired.md    # paired differences between approaches
python figures.py results                                 # Fig. 2 of the paper + overview figure
python make_numbers.py results/runs.json numbers.tex      # every number of the paper as a LaTeX macro
```

Requirements: Python 3.10 or newer, `numpy`, `scipy`, `matplotlib`. Nothing else.

A faster smoke test (one season per combination, about 5 min):

```bash
python run.py --seeds 1 --out results_test
```

To re-run only some approaches and keep the other rows of an existing `runs.json`:

```bash
python run.py --seeds 10 --out results --only scaffold,scaffold_retire
```

---

## What is simulated

| Item | Value |
|---|---|
| Season | 120 days, decisions once per hour from 6:00 to 22:00 → 1920 decisions |
| Decision | air request of the line: 200, 220, 240, 250, 260, 265, 270, 275 or 280 Nl/min (no shutdown option) |
| Hard limits | air shortage, lost production (>2 % of requested air missing), cooling shortage, site power above 184 kW, compressor room above 43 °C |
| Admissible system-level risk | ε = 0.01 per hour (probability that at least one hard limit is violated) |
| Couplings missing in the twin | air delivery vs. room temperature, compressor power vs. room temperature, chiller capacity vs. ambient temperature |
| Seasons per combination | 10 (seeds 0–9) |
| Total | 3 scenarios × 6 approaches × 10 seeds + 3 ablations × 2 scenarios × 10 seeds = 240 seasons |

One decision hour runs as follows:

1. The agent proposes a level (ε-greedy over its values for the current room-temperature bin).
2. Its risk critic gives a lower, middle and upper estimate of the system-level risk of that level.
3. Decision rule:
   - **A** – upper bound below ε: act alone;
   - **B** – the range crosses ε: ask the twin;
   - **C** – lower bound above ε: take the highest level below the proposal whose upper bound is below ε; ask the twin only if there is none.
4. A twin request evaluates all nine levels by Monte Carlo (twin + learned residual corrections). The agent learns risk and values from it and executes the highest level, up to its proposal, whose upper bound from the twin is below ε (otherwise the lowest level).
5. The plant runs one hour.
6. The agent learns: values from the real reward; residuals (if the twin was asked) or the calibration test (if it acted alone).

### Risk limit and what happens to a risky proposal

- **The limit.** ε = 0.01 per hour applies to the *system-level* risk: the probability that at least one
  hard limit is violated in the coming hour (union of the five events). It is checked against an
  **upper bound**: the agent's own upper bound (90 % level) when it acts alone, and the twin's upper
  bound (95 % quantile over the epistemic samples) after a request. Over a season, ε corresponds to a
  budget of about 19 violation hours (1920 × 0.01).
- **A proposal whose upper bound exceeds ε is never executed unchanged.** It is replaced by
  - case C: the highest *lower* level whose own upper bound is below ε;
  - case B, or C with no such level: the twin's highest admissible level up to the proposal;
  - if no level is admissible, or the twin is retired and the agent knows no admissible level: the
    **lowest production level** (200 Nl/min).
- **The policy learns from overrides.** The executed level gets the real reward; the overridden proposal
  gets the same reward minus 5, so the policy learns not to propose it again.
- **The fallback is not a guarantee.** There is no shutdown option, and on the hottest days even the
  lowest level breaks the thermal limit of the compressor room ("no safe level" hours, counted
  separately as non-controllable violations).
- **No hard limiter is simulated.** The paper's architecture keeps a local hard limiter below the
  agent; the simulation does not model it, so every hard-limit event is counted as it occurs.

---

## Package layout

| File | Content |
|---|---|
| `scaffold/config.py` | all parameters in one dataclass (`Config`), scenarios, ablation switches |
| `scaffold/plant.py` | the "real" plant: weather, demand, compressor, room heat, chiller, site power, sensors, sensor fault, wear, clogging episodes |
| `scaffold/twin.py` | the digital twin: same physics without the three couplings |
| `scaffold/learner.py` | Bayesian residual learner for one coupling, with the attribution conditions A1, A2, A5, A6 |
| `scaffold/risk.py` | two-level Monte Carlo risk with common random numbers; union, Boole and other aggregations |
| `scaffold/agent.py` | `ScaffoldAgent` (policy, residual learners, decision rule, twin simulation) and `RiskCritic` (risk model, range, forgetting, calibration test) |
| `scaffold/simulate.py` | one season for one approach; fixed-margin rule; ideal reference; "no safe level" diagnostic |
| `run.py` | runs all seasons in parallel, writes `runs.json` and `summary.md` |
| `paired.py` | paired differences over seeds |
| `mc_convergence.py` | Monte Carlo convergence study (n_inner 1000–10 000) |
| `figures.py` | Fig. 2 of the paper (`fig2_base.pdf/.png`) and `overview.png` |
| `make_numbers.py` | writes every number used in the paper as a LaTeX macro |
| `results/` | results of the paper version |
| `results_v2/` | results of the previous paper draft (single A6 drift rule), kept for reference |
| `results_v1/` | results of the earlier package version (clogging from day 0, no attribution gate), kept for reference |

---

## Model details

### Plant (`plant.py`)

- **Weather.** Ambient temperature = 12 °C + 14 °C · sin(π·day/120) + a daily random offset (sd 3 °C) + 5 °C · sin(2π·(hour − 9)/24).
- **Room heat.** Equilibrium = ambient + 7 °C × compressor load; time constant 2 h; a shared random disturbance (sd 3 °C) per hour. All couplings and the thermal limit use the hour-average room temperature.
- **Air delivery.** 300 Nl/min, minus 1.0 Nl/min per °C of room temperature above 20 °C (scenario-dependent), minus wear (0.15 Nl/min per day from day 80), minus 15 Nl/min on clogged days (plant-change scenario only), plus noise (sd 2).
- **Power.** 0.30 kW per Nl/min (line) + 0.12 kW per Nl/min × (1 + 1 % per °C above 20 °C) (compressor) + 1.5 kW per °C of ambient above 22 °C (hall cooling) + 40 kW other loads (sd 6).
- **Cooling.** Load = 0.15 kW per Nl/min + 1.0 kW per °C of ambient above 20 °C; capacity = 70 kW − 1.5 kW per °C of ambient above 25 °C (sd 3).
- **Sensors.** Delivery meter (biased by −15 Nl/min on days 70–74), a pressure-implied delivery estimate (the redundant measurement for A5), power meter, chiller capacity.
- **Energy price and cost** are logged but not used in decisions or rewards.

### Digital twin (`twin.py`)

Constant delivery (300 Nl/min), compressor power at reference efficiency, constant chiller capacity
(70 kW); room-temperature forecast without the disturbance. It knows the noise levels and all limits.

### Residual learners (`learner.py`)

One Bayesian linear model per coupling, residual = measured − twin prediction:

| Coupling | Feature | True slope (base) |
|---|---|---|
| Air delivery | room temperature − 20 °C | −1.00 Nl/min per °C |
| Compressor power | (room temperature − 20 °C) × request / 270 | 0.32 kW per °C |
| Chiller capacity | max(0, ambient − 25 °C) | −1.50 kW per °C |

Learners only receive data in hours in which the twin was asked. Each learner has two parts: the
coupling model (intercept th0 and slope th1, Bayesian) and a separate **drift offset d**, which only A6
changes. The twin is corrected by (th0 + d) + th1·x.

Attribution conditions:

- **A1** – local adequacy: the intercept th0 is near zero (|th0| < 3 sd + 1), i.e. the twin is right
  where the coupling does not act. Because drift is held in d, not in th0, A1 keeps this meaning after
  wear or clogging.
- **A2** – dependence: the slope posterior excludes zero (|mean| > 3 sd).
- **A5** – sensor plausibility: delivery residuals are rejected when the meter and the pressure-implied
  value differ by more than 10 Nl/min (the biased sensor of days 70–74).
- **A6** – time invariance. When the mean one-step error of the last 60 residuals is biased, A6 regresses
  these errors on time and on the coupling feature x:
  - **no dependence on x** (a uniform shift, or a trend in time): **drift**. The bias is moved into the
    drift offset d (and its variance), outside the coupling model. Wear and clogging end up here;
  - **dependence on x** (t-value above 3, with or without time): **model-form misfit**. Nothing is moved
    into d; the coupling's covariance is widened by the size of the misfit. When state and time cannot
    be separated, this is the conservative choice: more uncertainty instead of a wrong offset.

**How A1 and A6 work together.** Residuals mix three things: the missing coupling (depends on the state),
slow wear or clogging (depends on time, the same at every state) and noise. The Bayesian fit averages
the noise out, A2 accepts only a slope clearly different from zero, and A5 removes sensor faults. A6 takes
time-dependent shifts out of the coupling model into d, so the slope is not bent by the wear and A1 still
tests the twin's local model. A6 does not move state-dependent misfit into d, so a coupling of the wrong
shape is not mistaken for drift.

A pattern corrects the twin as an interaction only once A1 and A2 hold (A2 is re-checked afterwards).
Before that, the twin is corrected with zero mean and a widened variance (plus the drift offset). A3 and
A4 are not exercised: the couplings act within the one-hour step and depend on the state only.

`Config(attribution=False)` switches A1, A2, A5 and A6 off (every residual is learned as an interaction);
`Config(interaction_learning=False)` keeps the twin uncorrected (ĝ = 0).

### Risk (`risk.py`)

1000 aleatory samples × K epistemic samples (K = 40 for the twin, 1 for the ideal reference), one fixed
matrix of common random numbers for every call. Aggregations: `joint` (union, default), `boole`,
`independent`, `single`, `joint_with_cost`. The twin's range = 5 % and 95 % quantiles over K.

### Agent (`agent.py`)

- **Policy.** One-step values (γ = 0) per room-temperature bin (limits 22, 26, 30, 34, 38 °C); step size 0.1; ε-greedy from 0.30 down to 0.02 over 60 % of the season. Reward = delivered air (Nm³) − 60 × shortage − 40 × (peak, cooling, thermal); an overridden proposal gets −5.
- **Risk critic.** Logistic model of the system-level risk in 10 features of room temperature, ambient temperature and request; Gaussian posterior; range = σ(μ ± 1.645 ς) with ς² = posterior variance + recent misfit to the twin. Forgetting towards the prior at every decision (0.9993).
- **Calibration test.** After decisions taken alone: if observed violations exceed the 99 % Poisson quantile of the predicted count (window 300, at least 50), the critic's precision is divided by 8 ("surprise").

---

## Approaches and scenarios

| Key in results | Approach |
|---|---|
| `fixed_margin` | RL proposal, capped by fixed safety margins on the twin's predictions (40 Nl/min, 30 kW, 18 kW, 4 °C) |
| `rl_alone` | RL proposal executed without any check |
| `rl_twin_every` | twin asked at every decision |
| `scaffold` | this work |
| `scaffold_retire` | this work, twin retired after day 60 |
| `oracle` | ideal reference: knows the true plant, not the future noise; highest level whose true risk is below ε (= 100 % output) |
| `scaffold_boole` | ablation: Boole bound instead of the union (base, episodes) |
| `scaffold_noattr` | ablation: no attribution conditions (base, episodes) |
| `scaffold_nolearn` | ablation: no interaction learning, the twin is used uncorrected (base, episodes) |

| Key | Scenario |
|---|---|
| `base` | linear coupling, wear from day 80, sensor bias on days 70–74 |
| `episodes` | plant change: as base, plus random clogging episodes from day 60 (daily probability 0.06, 2–5 days, −15 Nl/min) |
| `hinge` | other coupling: no delivery loss up to 30 °C, −2.0 Nl/min per °C above |

The plant also implements a scenario `ambient` that is not used in the paper.

---

## Outputs

### `results/runs.json`

One record per season (scenario × approach × seed):

| Field | Meaning |
|---|---|
| `any_hard`, `any_hard_first30`, `any_hard_last40` | hard-violation hours (season, first 30 days, last 40 days) |
| `no_safe_hours` | hours in which even the lowest level had a true risk ≥ ε |
| `viol_no_safe`, `viol_controllable` | violation hours without / with a safe level available |
| `events`, `events_controllable` | hours per event type (shortage, lost, cooling_short, peak, thermal) |
| `air`, `output_pct`, `lost_pct` | delivered air (Nm³), as % of the ideal reference, and the loss |
| `twin`, `twin_last30`, `alone_share_last30` | twin requests (season, last 30 days), share of decisions taken alone in the last 30 days |
| `n_alone`, `pred_alone`, `obs_alone`, `obs_alone_controllable` | calibration: decisions taken alone, predicted and observed violations |
| `viol_asked` | violation hours in which the twin was asked |
| `surprises` | calibration-test alarms |
| `cpu_total`, `cpu_twin`, `n_sim` | CPU seconds in decisions, of which in twin simulations; candidate levels simulated |
| `daily_q`, `daily_v`, `daily_v_no_safe` | daily twin requests, violation hours, violation hours without a safe level |
| `attribution` | per coupling: learned slope and sd, intercept th0, drift offset d, day identified, A1 at season end, A5 rejection days, A6 drift days and model-form misfit days (this work, its ablations, retired twin, twin on every decision) |

### `results/summary.md`

Three tables: all KPIs (mean ± standard error), hours per event type, attribution statistics.

### `results/paired.md`

Paired differences between approaches on the same seeds (mean ± standard error): this work vs. twin
on every decision, RL alone and fixed margins; retired twin vs. twin on every decision; the three
ablations vs. this work.

### Figures

- `fig2_base.pdf/.png` – Fig. 2 of the paper: cumulative twin requests and cumulative violation hours, base scenario, mean of 10 seasons; the shaded area marks violations without a safe level.
- `overview.png` – weekly twin requests in all three scenarios.

---

## Reproducing the paper

1. Run the four commands of the quick start.
2. `numbers.tex` holds every number of the paper as a macro (e.g. `\BaseScafV` = violations of this work in the base scenario, mean ± standard error). Compare them with the paper, or `\input` the file.
3. Copy `results/fig2_base.pdf` into the paper's `figures/` folder.

CPU seconds depend on the machine; only the ratios between approaches (about 74–79 % saving) are
comparable.

---

## Configuration

All parameters are fields of `Config` in `scaffold/config.py`; override them when creating it,
e.g. `Config(scenario="episodes", aggregation="boole")`.

| Group | Main fields |
|---|---|
| Horizon | `days`, `work_hours` |
| Plant | `q_nom`, `coupling_true`, `drift_start_day`, `drift_per_day`, `heat_gain`, `tau_h`, `room_noise_sd`, weather fields |
| Power and cooling | `p_line_per_nl`, `p_comp_per_nl`, `comp_eff_coef`, `peak_limit`, `chiller_cap`, `chiller_derate`, `t_room_max` |
| Faults | `fault_days`, `fault_bias` |
| Risk | `risk_limit` (ε), `range_q`, `n_inner`, `n_epistemic`, `aggregation` |
| Learners | `attribution`, `interaction_learning`, priors, `forgetting`, `a5_threshold`, `a6_window`, `a6_threshold`, `a6_state_t` |
| Policy | `temp_bins`, `alpha`, `eps_start`, `eps_end`, penalties |
| Baselines | `fixed_margin`, `fixed_power_margin`, `fixed_cool_margin`, `fixed_thermal_margin` |
| Scenarios | `scenario`, `hinge_T`, `hinge_slope`, `episode_start_day`, `episode_rate`, `episode_days`, `episode_drop` |
| Retirement | `extra={"retire_day": 60}` |

---

## Randomness and paired comparison

Each season uses four independent random streams:

| Stream | Seed | Used for |
|---|---|---|
| Plant | seed | weather, demand, all noise |
| Clogging | seed + 777 | episode starts and lengths |
| Agent | seed + 10 000 | exploration, epistemic samples |
| Monte Carlo | fixed (12 345) | the common 1000 × 6 matrix of the risk engine |

The plant draws the same random numbers in the same order whatever the agent decides, so all approaches
with the same seed see the same weather, demand, noise and clogging. Differences between approaches
come only from their decisions, which is why the paper reports paired differences.

---

## Expected results

Base scenario, 10 seasons, mean ± standard error (`results/summary.md`):

| Approach | Violations, h | Controllable, h | Twin requests | Output, % of ideal |
|---|---|---|---|---|
| RL alone | 44.9 ± 4.1 | 22.0 ± 0.9 | 0 | 97.9 ± 0.2 |
| Fixed margins | 10.1 ± 3.3 | 0.4 ± 0.2 | 0 | 90.3 ± 0.1 |
| Twin on every decision | 12.5 ± 3.4 | 2.0 ± 0.5 | 1920 | 97.4 ± 0.0 |
| This work | 11.8 ± 3.3 | 1.6 ± 0.3 | 460 ± 20 | 95.5 ± 0.2 |
| This work, twin retired | 11.0 ± 3.3 | 1.1 ± 0.3 | 336 ± 12 | 95.0 ± 0.3 |
| Ideal reference | 17.9 ± 3.0 | 6.8 ± 0.6 | 0 | 100 |
| Ablation: no interaction learning | 35.7 ± 3.5 | 23.7 ± 1.3 | 174 ± 5 | 98.2 ± 0.2 |

About 86 % of the violation hours of this work fall in hours in which no level was safe (mostly the
thermal limit on the hottest days). The learned slopes converge to −0.97, 0.31 and −1.51 (true:
−1.00, 0.32, −1.50). Without interaction learning the twin stays biased in warm states and the agent
has 22 more controllable violation hours per season: the savings depend on the residual learner.

A1 and A6 together (air delivery): with the twin on every decision, A6 moved the compressor wear into the
drift offset in 10 of 10 seasons (−4.0 Nl/min at season end; true −5.9) while the slope stayed at −0.97
and A1 still held at season end in 9 of 10 seasons. With the twin asked only when unsure, A6 saw the
wear in 5 of 10 seasons (around day 110). With the other coupling shape, A6 flagged model-form misfit in
all 10 seasons (first around day 33) and drift in 8 of 10 (1.1 detections per season).

Previous results (single drift rule, no separate drift offset, no `scaffold_nolearn`) are kept in
`results_v2/`; the first package version in `results_v1/`.

---

## Monte Carlo convergence (`mc_convergence.py`)

Every risk estimate uses `n_inner` aleatory samples (default 1000). At ε = 0.01 one estimate has a standard
error of 0.0031 at n = 1000 and 0.0010 at n = 10 000. `mc_convergence.py` re-runs the base scenario with
n = 1000, 2000, 3000, 5000, 7000 and 10 000 (twin on every decision, this work, ideal reference; 10 seeds)
and writes `results_mc/summary.md` (about 1.5 h on 2 cores; it resumes from `runs_partial.jsonl`).

| n | This work: violations, h | twin requests | output, % | Twin on every decision: violations, h | Ideal reference: violations, h |
|---|---|---|---|---|---|
| 1000 | 11.8 ± 3.3 | 460 ± 20 | 95.5 | 12.5 ± 3.4 | 17.9 ± 3.0 |
| 5000 | 12.4 ± 3.4 | 386 ± 9 | 95.4 | 13.6 ± 3.5 | 21.5 ± 3.0 |
| 10000 | 12.6 ± 3.5 | 378 ± 13 | 95.3 | 13.8 ± 3.4 | 21.9 ± 2.9 |

- The KPIs stop moving from n ≈ 5000: every paired change against n = 10 000 is within about one standard
  error there. At n = 1000 the approaches that evaluate risk at every decision have significantly fewer
  violations (ideal reference −4.0 ± 0.5 h, twin on every decision −1.3 ± 0.3 h): the risk engine uses one
  fixed sample matrix (common random numbers), so its Monte Carlo error is a fixed bias per state, not noise
  that averages out over the season.
- The comparison of this work with the twin on every decision holds at every n: comparable violations
  (−1.2 ± 0.9 h at n = 10 000), 80 % fewer twin requests and 82 % less computation, 2.1 points less output.
- With more samples the agent asks the twin less (460 → 378 requests), because the twin's risk labels are less
  noisy and the agent's risk model fits them better. It still underestimates its risk when acting alone
  (0.42 predicted vs 2.6 observed violations per season at n = 10 000).
- Recommendation for further studies: n = 5000.

---

## Limitations

- Simplified plant, hypothetical parameters, one decision variable without a shutdown option.
- Tabular one-step policy; energy cost logged but not priced.
- Residuals are learned only in hours the twin was asked; after retirement, plant changes are seen only through outcomes.
- A6 sees the slow wear in only half of the seasons when the twin is asked rarely; with a misspecified coupling shape it widens the uncertainty, but still reads part of the misfit as drift, and the linear model cannot represent the hinge (slope −0.37 ± 0.46 over seasons).
- The risk critic underestimates the risk on decisions taken alone (about 3× in the base scenario), although the observed rate stays far below ε.
- No local hard limiter is simulated; the fallback to the lowest level does not guarantee that all hard limits hold.

---

## Citation and acknowledgment

If you use this package, please cite the paper above.

The simulation environment was developed with the assistance of Claude (Claude Opus 5.5, Anthropic);
the authors reviewed it and take responsibility for its content.


## Additional runs for the ICSRS 2026 review (branch `icsrs-revision`)

`main` holds the submitted paper's results and is unchanged. This branch adds:

- `scaffold/datafilter.py`: a data-driven safety filter **without any twin** (Bayesian linear model of each limit's margin, fitted to plant data only; union risk; same rule A/B/C). Two variants: `filter_cautious` (case B treated like case C) and `filter_explore` (case B: the proposal is tried on the plant).
- Fallback logging: hours in which no level was known to be safe and the lowest level was taken, with violations and controllable violations in them.
- `critic_z` in `Config` (agent's range level; default 1.645, results unchanged).
- `review.py`: filters in all scenarios, re-run of this work and DT on every decision (identical to `main`), coupling-strength sweep (kappa = 0, 0.5, 1.5, 2 scales all three missing couplings), and alpha = 0.01 (z = 2.326).
- `review_summary.py results_review` writes `results_review/summary.md`.

```
OMP_NUM_THREADS=1 python review.py --out results_review
python review_summary.py results_review
```

CPU times in `results_review` were measured with single-threaded BLAS and are not comparable with `results/`; the paper's CPU column comes from `results/`.
- `mc_convergence.py` and `results_mc/` (also on branch `mc-convergence`): the Monte Carlo convergence check cited in the revised paper (n_inner = 1000 to 10 000, base scenario; see the section above).
