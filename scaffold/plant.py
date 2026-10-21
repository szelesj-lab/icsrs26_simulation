# Developer: József Szeles, Department of System Engineering and Department of Electrical Engineering, University of Pannonia
"""The 'real' plant: stochastic, with a coupling the twin does not know.

Production asks for air. The compressor's waste heat warms its own room; hot
intake air lowers the delivered air (the coupling), which raises the load,
which adds heat (a weak feedback loop)."""
import numpy as np


class Plant:
    def __init__(self, cfg, rng, seed=0):
        self.c, self.rng = cfg, rng
        # clogging episodes (scenario 'episodes'), drawn from their own stream,
        # only after the learning phase (from cfg.episode_start_day)
        er = np.random.default_rng(seed + 777)
        self.clogged = np.zeros(cfg.days + 1, dtype=bool)
        d = cfg.episode_start_day
        while d < cfg.days:
            if er.random() < cfg.episode_rate:
                n = int(er.integers(cfg.episode_days[0], cfg.episode_days[1] + 1))
                self.clogged[d:d + n] = True
                d += n
            d += 1
        self.day, self.hour = 0, 0
        self.day_offset = 0.0
        self.t_room = cfg.season_base + 2.0
        self._new_day()

    # ---------- weather (aleatory) ----------
    def _new_day(self):
        self.day_offset = self.rng.normal(0.0, self.c.day_offset_sd)

    def ambient(self, day=None, hour=None):
        c = self.c
        d = self.day if day is None else day
        h = self.hour if hour is None else hour
        season = c.season_base + c.season_amp * np.sin(np.pi * d / c.days)
        diurnal = c.diurnal_amp * np.sin(2 * np.pi * (h - 9) / 24)
        return season + self.day_offset + diurnal

    # ---------- true physics ----------
    def q_nominal(self, day=None):
        c = self.c
        d = self.day if day is None else day
        return c.q_nom + c.drift_per_day * max(0, d - c.drift_start_day)

    def air_offset(self, t_room, t_amb=None, day=None):
        """True delivery minus nominal, by scenario (vectorised over t_room)."""
        c = self.c
        d = self.day if day is None else day
        t_amb = self.ambient() if t_amb is None else t_amb
        t_room = np.asarray(t_room, dtype=float)
        wear = c.drift_per_day * max(0, d - c.drift_start_day)
        if c.scenario == "hinge":
            coup = c.hinge_slope * np.maximum(0.0, t_room - c.hinge_T)
        elif c.scenario == "ambient":
            coup = c.coupling_true * (t_amb - c.ambient_ref) + 0.0 * t_room
        else:
            coup = c.coupling_true * (t_room - c.t_ref)
        clog = c.episode_drop if (c.scenario == "episodes" and self.clogged[min(d, c.days)]) else 0.0
        return wear + coup + clog

    def delivery_mean(self, t_room, day=None, t_amb=None):
        return self.c.q_nom + self.air_offset(t_room, t_amb, day)

    def hvac(self, t_amb):
        return self.c.p_hvac_per_deg * max(0.0, t_amb - 22.0)

    def power_mean(self, request, t_room, t_amb):
        c = self.c
        comp = c.p_comp_per_nl * request * (1 + c.comp_eff_coef * (t_room - c.t_ref))
        return c.p_line_per_nl * request + comp + self.hvac(t_amb) + c.p_base_mean

    def tariff(self, hour=None):
        h = self.hour if hour is None else hour
        return self.c.tariff_peak if 8 <= h < 20 else self.c.tariff_off

    def cooling_load(self, request, t_amb):
        c = self.c
        return c.cool_per_nl * request + c.cool_amb_per_deg * max(0.0, t_amb - 20.0)

    def chiller_capacity_mean(self, t_amb):
        c = self.c
        return c.chiller_cap + c.chiller_derate * max(0.0, t_amb - 25.0)

    def step(self, request):
        """Run one hour with an air request (Nl/min; 0 = idle). Returns a record.

        The intake temperature that matters is the hour's average. It depends on the
        thermal dynamics and on an unforeseen within-hour disturbance (sun, open doors),
        which is shared by both risk types: a common cause not known at decision time."""
        c, rng = self.c, self.rng
        demand = request * (1 + rng.normal(0, c.demand_cv)) if request > 0 else 0.0
        t_amb = self.ambient()
        t_start = self.t_room
        # thermal step (the loop): equilibrium rises with load, estimated from the start state
        q_start = self.delivery_mean(t_start)
        load = 0.0 if request == 0 else min(1.0, demand / max(q_start, 1.0))
        t_eq = t_amb + c.heat_gain * load
        disturbance = rng.normal(0, c.room_noise_sd)
        t_end = t_start + (t_eq - t_start) / c.tau_h + disturbance
        t_hour = 0.5 * (t_start + t_end)              # average intake temperature of the hour

        q_true = self.delivery_mean(t_hour) + rng.normal(0, c.q_noise_sd)
        served = min(demand, q_true)
        shortage = request > 0 and q_true < demand

        # sensors: delivery meter (can fail) and a pressure-implied estimate
        bias = c.fault_bias if c.fault_days[0] <= self.day < c.fault_days[1] else 0.0
        q_meas = q_true + bias + rng.normal(0, 0.5)
        q_pressure = q_true + rng.normal(0, 3.0)

        e_spec = c.e_spec_ref * (1 + c.e_temp_coef * (t_hour - c.t_ref))
        energy_kwh = e_spec * served * 60 / 1000          # Nl/min over one hour -> Nm3

        if request > 0:
            p_true = self.power_mean(request, t_hour, t_amb) + rng.normal(0, c.p_base_sd)
        else:
            p_true = c.p_base_mean + self.hvac(t_amb) + rng.normal(0, c.p_base_sd)
        p_meas = p_true + rng.normal(0, c.p_meter_sd)
        peak = request > 0 and p_true > c.peak_limit

        # process cooling: the chiller loses capacity in hot weather
        cap_true = self.chiller_capacity_mean(t_amb) + rng.normal(0, c.chiller_noise_sd)
        cap_meas = cap_true + rng.normal(0, 0.5)
        cooling_short = request > 0 and self.cooling_load(request, t_amb) > cap_true

        # energy price and cost per unit of delivered air (all site power)
        price = self.tariff() * np.exp(rng.normal(0, c.price_sigma) - c.price_sigma ** 2 / 2)
        cost_unit = price * p_true / max(served * 0.06, 1e-6) if request > 0 else 0.0

        thermal = request > 0 and t_hour > c.t_room_max
        lost = request > 0 and served < (1 - c.lost_tol) * demand

        rec = dict(cooling_short=bool(cooling_short), cap_meas=cap_meas, price=price, cost_unit=cost_unit,
                   cost_over=bool(request > 0 and cost_unit > c.cost_budget), thermal=bool(thermal), lost=bool(lost),
                   energy_cost=price * p_true,
                   day=self.day, hour=self.hour, request=request, demand=demand,
                   q_true=q_true, q_meas=q_meas, q_pressure=q_pressure, served=served,
                   shortage=bool(shortage), peak=bool(peak), power_true=p_true, power_meas=p_meas,
                   t_room=t_hour, t_start=t_start, t_amb=t_amb,
                   energy_kwh=energy_kwh, air_nm3=served * 60 / 1000)
        self.t_room = t_end

        self.hour += 1
        if self.hour == 24:
            self.hour, self.day = 0, self.day + 1
            self._new_day()
        return rec
