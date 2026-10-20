"""Two-level system risk over all risk types of the paper.

Risk types (events in the next hour):
  shortage   air delivery below demand
  lost       more than 2 % of the requested air missing (nested in 'shortage')
  cooling    process cooling load above chiller capacity
  peak       site power above the contracted peak
  thermal    compressor room above its temperature limit
  cost       energy cost per unit of delivered air above budget (a SOFT risk)

Inner level (aleatory): Monte Carlo with common random numbers for the hour's
room temperature, demand, delivery noise, base load, chiller noise and price.
Because all events are evaluated on the same samples, nested events (lost is
part of shortage) and shared causes (temperature; power drives both peak and
cost) are represented exactly.

Outer level (epistemic): samples of the three learned couplings (air delivery,
compressor power, chiller capacity). Quantiles of the aggregated probability
over these samples give the twin's risk RANGE; the twin's mean risk is what the
agent's risk critic learns, and the twin's upper bound selects the executed action
after a request.

Aggregation:
  joint            P(any hard limit violated), from the shared samples (union; paper eq. 5, default)
  boole            min(1, sum of the hard-limit probabilities) (Boole bound; ablation)
  independent      1 - prod(1 - p_k), as if the limits were independent
  single           shortage only (one risk type)
  joint_with_cost  P(any hard limit or cost over budget)
"""
import numpy as np

HARD = ("shortage", "lost", "cooling", "peak", "thermal")
_Z = {}


def _z(n, k=6, seed=12345):
    if (n, k) not in _Z:
        _Z[(n, k)] = np.random.default_rng(seed).standard_normal((n, k))
    return _Z[(n, k)]


def twin_power(request, t_amb, cfg):
    return (cfg.p_line_per_nl + cfg.p_comp_per_nl) * request + cfg.p_hvac_per_deg * max(0.0, t_amb - 22.0) + cfg.p_base_mean


def tariff(hour, cfg):
    return cfg.tariff_peak if 8 <= hour < 20 else cfg.tariff_off


def event_samples(request, t_mean, t_sd, t_amb, hour, th, cfg, n_inner=None, return_served=False):
    """Boolean arrays (n_theta, n_inner) for every risk type.
    th: dict with 'air', 'power', 'chiller' -> arrays (n_theta, 2)."""
    c = cfg
    z = _z(n_inner or c.n_inner)
    a, p, ch = (np.atleast_2d(th[k]) for k in ("air", "power", "chiller"))
    T = (t_mean + t_sd * z[:, 0])[None, :]
    x = T - c.t_ref
    demand = request * (1 + c.demand_cv * z[:, 1])[None, :]
    if "air_offset" in th:  # mixture of hypotheses: callable T -> (n_theta, n_inner)
        q = c.q_nom + th["air_offset"](T[0]) + c.q_noise_sd * z[:, 2][None, :]
        a = np.zeros((q.shape[0], 2))
    elif "air_fn" in th:    # oracle: the true (possibly nonlinear) delivery function
        q = c.q_nom + np.asarray(th["air_fn"](T[0]))[None, :] + c.q_noise_sd * z[:, 2][None, :]
    else:
        q = c.q_nom + a[:, :1] + a[:, 1:2] * x + c.q_noise_sd * z[:, 2][None, :]
    served = np.minimum(q, demand)
    power = twin_power(request, t_amb, c) + p[:, :1] + p[:, 1:2] * x * request / 270.0 + c.p_base_sd * z[:, 3][None, :]
    cap = c.chiller_cap + ch[:, :1] + ch[:, 1:2] * max(0.0, t_amb - 25.0) + c.chiller_noise_sd * z[:, 4][None, :]
    load = c.cool_per_nl * request + c.cool_amb_per_deg * max(0.0, t_amb - 20.0)
    price = tariff(hour, c) * np.exp(c.price_sigma * z[:, 5] - c.price_sigma ** 2 / 2)[None, :]
    cost_unit = price * power / np.maximum(served * 0.06, 1e-6)
    shape = (a.shape[0], len(z))
    ev = {
        "shortage": q < demand,
        "lost": served < (1 - c.lost_tol) * demand,
        "cooling": np.broadcast_to(load > cap, shape),
        "peak": power > c.peak_limit,
        "thermal": np.broadcast_to(T > c.t_room_max, shape),
        "cost": cost_unit > c.cost_budget,
    }
    return (ev, served) if return_served else ev


def aggregate(ev, mode):
    """Per-theta probability of the aggregated event, shape (n_theta,)."""
    if mode == "single":
        return ev["shortage"].mean(1)
    pk = np.stack([ev[k].mean(1) for k in HARD])          # (K, n_theta)
    if mode == "boole":
        return np.minimum(1.0, pk.sum(0))
    if mode == "independent":
        return 1 - np.prod(1 - pk, axis=0)
    if mode == "joint":
        return np.any(np.stack([ev[k] for k in HARD]), axis=0).mean(1)
    if mode == "joint_with_cost":
        return np.any(np.stack([ev[k] for k in HARD + ("cost",)]), axis=0).mean(1)
    raise ValueError(mode)


def risk_range(request, t_mean, t_sd, t_amb, hour, th, cfg, mode=None):
    p = aggregate(event_samples(request, t_mean, t_sd, t_amb, hour, th, cfg), mode or cfg.aggregation)
    lo, hi = np.quantile(p, cfg.range_q)
    return float(lo), float(np.mean(p)), float(hi)


def classify(lo, hi, limit):
    if hi < limit:
        return "A"          # clearly below the limit
    if lo > limit:
        return "C"          # clearly above the limit
    return "B"              # the range crosses the limit
