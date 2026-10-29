# Developer: József Szeles, Department of System Engineering and Department of Electrical Engineering, University of Pannonia
"""The digital twin as a scaffold.

One RL agent learns three things:
  1. what the twin gets wrong        -> residual models (air delivery, compressor power, chiller)
  2. the risk of each action         -> a Bayesian risk critic
  3. how sure it is about that risk  -> the critic's posterior + its own misfit

It asks the twin for a simulation only when its own risk estimate is uncertain or
close to the limit. Every simulation teaches it (risk critic and policy), every
executed hour after a simulation teaches the residual models, and every real outcome
calibrates the critic. As the RL learns, it asks less; the twin can finally be retired.
"""
import time

import numpy as np
from scipy.stats import poisson

from .learner import ResidualLearner
from .risk import event_samples, aggregate
from .datafilter import DataFilter

LOGIT_CLIP = 1e-5


def _logit(p):
    p = np.clip(p, LOGIT_CLIP, 1 - LOGIT_CLIP)
    return np.log(p / (1 - p))


def _sigmoid(x):
    return 1 / (1 + np.exp(-x))


class RiskCritic:
    """logit P(hard violation | room temp, ambient, request) = w . phi, Bayesian in w.

    Uncertainty = posterior variance (shrinks where the twin has been asked, grows
    elsewhere and slowly over time) + the critic's own misfit to the twin (model-form
    error of the critic). A real-outcome calibration test re-opens it on surprise."""

    def __init__(self, cfg, prior_sd=4.0, forgetting=0.9993, z=1.645):
        self.c, self.forgetting, self.z = cfg, forgetting, z
        k = len(self.phi(30.0, 20.0, 250.0))
        self.prior_P = np.eye(k) / prior_sd ** 2
        self.prior_P[0, 0] = 1 / 2.0 ** 2
        m0 = np.zeros(k); m0[0] = _logit(cfg.risk_limit)     # before learning: right at the limit, unsure
        self.prior_b = self.prior_P @ m0
        self.P, self.b = self.prior_P.copy(), self.prior_b.copy()
        self.fit_err = []
        self.alone = []
        self.surprises = []

    @staticmethod
    def phi(t_room, t_amb, req):
        x, a, r = (t_room - 30.0) / 10.0, (t_amb - 20.0) / 10.0, (req - 250.0) / 30.0
        return np.array([1.0, x, a, r, x * r, a * r, x * x, a * a, x * a, r * r])

    @property
    def mean(self):
        return np.linalg.solve(self.P, self.b)

    def bounds(self, t_room, t_amb, req):
        f = self.phi(t_room, t_amb, req)
        m = float(f @ self.mean)
        v = float(f @ np.linalg.solve(self.P, f))
        misfit = np.mean(self.fit_err[-300:]) if len(self.fit_err) > 30 else 4.0
        s = np.sqrt(v + misfit)
        return _sigmoid(m - self.z * s), _sigmoid(m), _sigmoid(m + self.z * s)

    def forget(self):
        self.P = self.forgetting * self.P + (1 - self.forgetting) * self.prior_P
        self.b = self.forgetting * self.b + (1 - self.forgetting) * self.prior_b

    def learn(self, t_room, t_amb, reqs, p_twin, noise_var=0.5):
        for req, p in zip(reqs, p_twin):
            f = self.phi(t_room, t_amb, req)
            y = float(_logit(p))
            self.fit_err.append((y - f @ self.mean) ** 2)
            self.P = self.P + np.outer(f, f) / noise_var
            self.b = self.b + f * y / noise_var

    def calibrate(self, p_pred, violated, day):
        """Real outcomes of decisions taken without the twin: Poisson test for surprise."""
        self.alone.append((p_pred, bool(violated)))
        w = self.alone[-300:]
        if violated and len(w) >= 50:
            exp = sum(p for p, _ in w)
            obs = sum(v for _, v in w)
            if obs > poisson.ppf(0.99, max(exp, 1e-3)):
                self.P, self.b = self.P / 8.0, self.b / 8.0     # re-open: same estimate, much less sure
                self.surprises.append(day)
                self.alone = []


class ScaffoldAgent:
    def attribution_summary(self):
        return {k: L.summary() for k, L in self.res.items()}

    def __init__(self, cfg, rng, twin, mode="scaffold"):
        self.c, self.rng, self.twin, self.mode = cfg, rng, twin, mode
        self.Q = np.full((len(cfg.temp_bins) + 1, len(cfg.levels)), 20.0)
        self.n = 0
        self.res = {k: ResidualLearner(cfg, k) for k in ("air", "power", "chiller")}
        self.critic = RiskCritic(cfg, z=cfg.critic_z)
        self.asks = []                       # (day, reason)
        self.cpu_twin = 0.0                  # CPU seconds spent in twin simulations
        self.n_sim = 0                       # candidate actions simulated by the twin
        self.fallback = False                # last decision: no level known to be safe -> lowest level
        self.dfilter = DataFilter(cfg) if mode.startswith("filter") else None

    # ---------- policy ----------
    def _s(self, t_room):
        return int(np.searchsorted(self.c.temp_bins, t_room))

    def propose(self, t_room, total):
        c = self.c
        eps = c.eps_end + (c.eps_start - c.eps_end) * max(0.0, 1 - self.n / (0.6 * total))
        if self.rng.random() < eps:
            return int(self.rng.integers(len(c.levels)))
        return int(np.argmax(self.Q[self._s(t_room)]))

    def _q(self, t_room, i, r):
        s = self._s(t_room)
        self.Q[s, i] += self.c.alpha * (r - self.Q[s, i])

    # ---------- the twin, corrected by the learned residuals ----------
    def simulate(self, t_room, t_amb, hour):
        """One twin request: all candidate actions at this state. Returns (lo, mean, hi, reward) per action."""
        c = self.c
        t0 = time.process_time()
        th = {k: L.sample(c.n_epistemic, self.rng) for k, L in self.res.items()}
        out = []
        for req in c.levels:
            t_next = self.twin.predict_room(t_room, t_amb, req, c.q_nom)
            ev, served = event_samples(req, 0.5 * (t_room + t_next), c.sd_state_twin, t_amb, hour, th, c, return_served=True)
            p = aggregate(ev, c.aggregation)          # per epistemic sample; default: union of hard limits
            lo, hi = np.quantile(p, c.range_q)
            rew = (c.reward_per_nm3 * float(served.mean()) * 0.06 - c.shortage_penalty * float(ev["shortage"].mean())
                   - c.peak_penalty * float(ev["peak"].mean()) - c.cool_penalty * float(ev["cooling"].mean())
                   - c.thermal_penalty * float(ev["thermal"].mean()))
            out.append((float(lo), float(p.mean()), float(hi), rew))
        self.cpu_twin += time.process_time() - t0
        self.n_sim += len(c.levels)
        return out

    # ---------- decision ----------
    def decide(self, t_room, t_amb, hour, day, total, twin_available=True):
        """Rule A/B/C (paper, Sec. III-A). Levels are ordered by output, so 'the best action it is
        sure about' is the highest level below the proposal whose upper risk bound is below the limit.
        Fallback when no level is known to be safe: the lowest production level."""
        c = self.c
        prop = self.propose(t_room, total)
        self.fallback = False
        if self.mode.startswith("filter"):
            return self._decide_filter(prop, t_room, t_amb)
        self.critic.forget()
        lim = c.risk_limit
        lo, mid, hi = self.critic.bounds(t_room, t_amb, c.levels[prop])

        if self.mode == "alone":
            return prop, prop, None, None
        if self.mode == "every":
            ask = "every"
        elif hi < lim:
            return prop, prop, None, mid                      # sure it is safe: act alone
        elif lo > lim:                                         # sure it is too risky: a safer action it is sure about?
            sure = [i for i in range(prop) if self.critic.bounds(t_room, t_amb, c.levels[i])[2] < lim]
            if sure:
                i = max(sure)
                return prop, i, None, self.critic.bounds(t_room, t_amb, c.levels[i])[1]
            ask = "alternative"
        else:
            ask = "unsure"

        if not twin_available:                                 # twin retired: be cautious with what it knows
            sure = [i for i in range(prop + 1) if self.critic.bounds(t_room, t_amb, c.levels[i])[2] < lim]
            i = max(sure) if sure else 0
            self.fallback = not sure
            return prop, i, None, self.critic.bounds(t_room, t_amb, c.levels[i])[1]

        sim = self.simulate(t_room, t_amb, hour)
        self.asks.append((day, ask))
        self.critic.learn(t_room, t_amb, c.levels, [m for _, m, _, _ in sim])   # learn the risk from the twin
        for i, (_, _, _, r) in enumerate(sim):                                   # learn the policy from the twin
            self._q(t_room, i, r)
        ok = [i for i in range(prop + 1) if sim[i][2] < lim]
        self.fallback = not ok
        return prop, (max(ok) if ok else 0), ask, None

    def _decide_filter(self, prop, t_room, t_amb):
        """Baseline without twin: the same rule A/B/C on a risk range learned from plant data only.
        Case B cannot ask a twin. 'filter_cautious' treats B like C: the highest level below the
        proposal whose upper bound is below the limit, else the lowest level. 'filter_explore' tries
        the proposal on the plant instead (the plant is its only source of information)."""
        lim = self.c.risk_limit
        lo, mid, hi = self.dfilter.bounds(t_room, t_amb)
        if hi[prop] < lim:
            return prop, prop, None, None                          # A
        if lo[prop] <= lim and self.mode == "filter_explore":
            return prop, prop, None, None                          # B, explore on the plant
        ok = [i for i in range(prop) if hi[i] < lim]               # C (and B for the cautious filter)
        self.fallback = not ok
        return prop, (max(ok) if ok else 0), None, None

    # ---------- learning from the plant ----------
    def learn(self, rec, t_room, prop, idx, asked, p_alone):
        c = self.c
        violated = any(rec[k] for k in ("shortage", "lost", "cooling_short", "peak", "thermal"))
        reward = (c.reward_per_nm3 * rec["air_nm3"] - c.shortage_penalty * rec["shortage"] - c.peak_penalty * rec["peak"]
                  - c.cool_penalty * rec["cooling_short"] - c.thermal_penalty * rec["thermal"])
        self._q(t_room, idx, reward); self.n += 1
        if self.dfilter is not None:
            self.dfilter.learn(rec)
        if idx != prop:
            self._q(t_room, prop, reward - 5.0)
        if asked:   # the twin predicted this hour -> residuals
            self.res["air"].observe(rec["day"], rec["t_room"], rec["q_meas"], rec["q_pressure"], self.twin.predict_delivery(rec["t_room"]))
            self.res["power"].observe(rec["day"], rec["t_room"], rec["power_meas"], None,
                                      (c.p_line_per_nl + c.p_comp_per_nl) * rec["request"]
                                      + c.p_hvac_per_deg * max(0.0, rec["t_amb"] - 22.0) + c.p_base_mean, rec["request"])
            self.res["chiller"].observe(rec["day"], rec["t_amb"], rec["cap_meas"], None, self.twin.predict_chiller(rec["t_amb"]))
        elif p_alone is not None:
            self.critic.calibrate(p_alone, violated, rec["day"])
        return violated
