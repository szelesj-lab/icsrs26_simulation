"""One season for one approach."""
import time

import numpy as np

from .agent import ScaffoldAgent
from .plant import Plant
from .risk import risk_range, twin_power
from .twin import Twin

HARD_RECORD = ("shortage", "lost", "cooling_short", "peak", "thermal")
APPROACHES = ["fixed_margin", "rl_alone", "rl_twin_every", "scaffold", "scaffold_retire", "oracle"]


def _true_risk(cfg, plant, twin, t_room, t_amb, hour, i):
    """True system-level risk (union of hard limits) of level i at the current state:
    the plant's own couplings, only the future noise unknown."""
    th = {"air": np.zeros((1, 2)), "power": np.array([[0.0, cfg.p_comp_per_nl * 270.0 * cfg.comp_eff_coef]]),
          "chiller": np.array([[0.0, cfg.chiller_derate]]), "air_fn": lambda T: plant.air_offset(T, t_amb)}
    t_next = twin.predict_room(t_room, t_amb, cfg.levels[i], plant.delivery_mean(t_room))
    return risk_range(cfg.levels[i], 0.5 * (t_room + t_next), cfg.sd_state_twin, t_amb, hour, th, cfg, "joint")[1]


def _oracle(cfg, plant, twin, t_room, t_amb, hour):
    for i in range(len(cfg.levels) - 1, -1, -1):
        if _true_risk(cfg, plant, twin, t_room, t_amb, hour, i) < cfg.risk_limit:
            return i
    return 0


def simulate(approach, cfg, seed):
    plant = Plant(cfg, np.random.default_rng(seed), seed)
    rng = np.random.default_rng(seed + 10_000)
    twin = Twin(cfg)
    mode = {"rl_alone": "alone", "fixed_margin": "alone", "rl_twin_every": "every"}.get(approach, "scaffold")
    agent = ScaffoldAgent(cfg, rng, twin, mode)
    retire_day = cfg.extra.get("retire_day", 60) if approach == "scaffold_retire" else 10 ** 9
    h0, h1 = cfg.work_hours
    total = cfg.days * (h1 - h0)
    log = []
    cpu = {"decide": 0.0, "oracle_sims": 0}
    for _ in range(cfg.days * 24):
        if not (h0 <= plant.hour < h1):
            plant.step(0.0)
            continue
        t_room, t_amb, hour, day = plant.t_room, plant.ambient(), plant.hour, plant.day
        t0 = time.process_time()
        if approach == "oracle":
            prop = idx = _oracle(cfg, plant, twin, t_room, t_amb, hour); asked, p_alone = None, None
        else:
            prop, idx, asked, p_alone = agent.decide(t_room, t_amb, hour, day, total, twin_available=day < retire_day)
            if approach == "fixed_margin":
                def ok(i):
                    r = cfg.levels[i]
                    t_next = twin.predict_room(t_room, t_amb, r, cfg.q_nom)
                    return (r <= cfg.q_nom - cfg.fixed_margin
                            and twin_power(r, t_amb, cfg) + cfg.fixed_power_margin <= cfg.peak_limit
                            and plant.cooling_load(r, t_amb) + cfg.fixed_cool_margin <= twin.predict_chiller(t_amb)
                            and 0.5 * (t_room + t_next) + cfg.fixed_thermal_margin <= cfg.t_room_max)
                allowed = [i for i in range(len(cfg.levels)) if ok(i)]
                idx = min(prop, max(allowed) if allowed else 0)
        cpu["decide"] += time.process_time() - t0
        # diagnostics (not timed): is there any level whose true risk is below the limit here?
        no_safe = _true_risk(cfg, plant, twin, t_room, t_amb, hour, 0) >= cfg.risk_limit
        rec = plant.step(cfg.levels[idx])
        t0 = time.process_time()
        if approach != "oracle":
            agent.learn(rec, t_room, prop, idx, asked, p_alone)
        cpu["decide"] += time.process_time() - t0
        rec.update(approach=approach, seed=seed, executed=cfg.levels[idx], asked=asked or "",
                   twin_request=bool(asked), alone_p=p_alone if p_alone is not None else np.nan,
                   any_hard=any(rec[k] for k in HARD_RECORD), no_safe=bool(no_safe))
        log.append(rec)
    agent.cpu = cpu
    return log, agent
