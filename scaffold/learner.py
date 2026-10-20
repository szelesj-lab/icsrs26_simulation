"""Residual learner: what does the twin miss?

Residual r = measured value - twin prediction. A Bayesian linear model
r = th0 + th1 * x + noise is learned online, with x the coupling feature
(air: T_room - T_ref; power: (T_room - T_ref) * request / 270; chiller:
max(0, T_amb - 25)). Its Gaussian posterior is the EPISTEMIC uncertainty; the
twin samples it (K samples) when it simulates.

Attribution conditions (paper, Sec. II-B), as implemented in this case study:
  A1 local adequacy   - the local model fits where the coupling does not act:
                        the residual at x = 0 (the intercept) is near zero
  A2 dependence       - the slope posterior excludes zero (|mean| > 3 sd)
  A5 sensor plausible - the delivery meter agrees with the pressure-implied
                        value; implausible residuals are rejected (air only:
                        power and chiller have no redundant measurement here)
  A6 time invariance  - if the one-step-ahead errors of the last window are
                        biased, the change is attributed to drift: old evidence
                        about the offset is forgotten instead of being read as
                        a coupling
A pattern is used as an interaction only once A1 and A2 hold (A2 is re-checked
afterwards). Until then the learned residual is kept as extra epistemic
uncertainty: the twin is corrected with zero mean and a variance that covers
both the prior and the size of the residual pattern.
A3 (interventional support) and A4 (timing) are not exercised: the couplings
of the case study act within the one-hour step and are purely state-dependent.
cfg.attribution = False switches all checks off (ablation: every residual is
learned as an interaction)."""
import numpy as np


class ResidualLearner:
    def __init__(self, cfg, kind="air"):
        c = self.c = cfg
        self.kind = kind
        if kind == "air":
            self.prior_sd = (c.prior_sd_intercept, c.prior_sd_slope)
            self.noise_var = c.q_noise_sd ** 2 + 1.0
        elif kind == "chiller":
            self.prior_sd = (3.0, c.prior_sd_slope_chiller)
            self.noise_var = c.chiller_noise_sd ** 2 + 0.25
        else:
            self.prior_sd = (3.0, c.prior_sd_slope_power)
            self.noise_var = c.p_base_sd ** 2 + c.p_meter_sd ** 2
        self.prior_P = np.diag([1 / s ** 2 for s in self.prior_sd])
        self.P = self.prior_P.copy()         # precision
        self.b = np.zeros(2)
        self.data = []                       # accepted residuals: (day, x, r)
        self.rejected_a5 = []                # days of residuals rejected by A5
        self.drift_events = []               # (day, index) of A6 drift detections
        self.identified_day = None           # first day A1 and A2 held
        self.history = []                    # (day, slope mean, slope sd, intercept mean, identified)
        self.pred_errors = []                # one-step-ahead errors, used by A6

    def feature(self, t, request=270.0):
        """air: t = room temp; power: t = room temp, scaled by request; chiller: t = ambient."""
        if self.kind == "chiller":
            return np.maximum(0.0, np.asarray(t, dtype=float) - 25.0)
        x = np.asarray(t, dtype=float) - self.c.t_ref
        return x if self.kind == "air" else x * request / 270.0

    def _phi(self, t, request=270.0):
        return np.array([1.0, float(self.feature(t, request))])

    @property
    def mean(self):
        return np.linalg.solve(self.P, self.b)

    @property
    def cov(self):
        return np.linalg.inv(self.P)

    # ---------- attribution ----------
    def a1(self):
        m, C = self.mean, self.cov
        return len(self.data) >= 5 and abs(m[0]) < 3 * np.sqrt(C[0, 0]) + 1.0

    def a2(self):
        m, s = self.mean[1], np.sqrt(self.cov[1, 1])
        return abs(m) > 3 * s

    def coupling_identified(self):
        if not self.c.attribution:
            return True
        if self.identified_day is None:
            return False
        return self.a2()

    def sample(self, n, rng):
        """Epistemic samples of (th0, th1) for the twin correction."""
        m, C = self.mean, self.cov
        if self.coupling_identified():
            return rng.multivariate_normal(m, C, size=n)
        # not (yet) an interaction: zero mean, the pattern is kept as uncertainty
        C_u = C + np.diag([s ** 2 for s in self.prior_sd]) + np.diag(m ** 2)
        return rng.multivariate_normal(np.zeros(2), C_u, size=n)

    # ---------- update ----------
    def observe(self, day, t, meas, check, pred, request=270.0):
        """meas: measured value, check: an independent plausibility value (or None), pred: twin."""
        c = self.c
        if c.attribution and check is not None and abs(meas - check) > c.a5_threshold:   # A5
            self.rejected_a5.append(day)
            return False
        phi = self._phi(t, request)
        x = phi[1]
        r = meas - pred
        self.pred_errors.append(r - phi @ self.mean)      # one-step-ahead error, before learning from r
        # exponential forgetting towards the prior keeps the model able to follow drift
        self.P = c.forgetting * self.P + (1 - c.forgetting) * self.prior_P
        self.b = c.forgetting * self.b
        self.P = self.P + np.outer(phi, phi) / self.noise_var
        self.b = self.b + phi * r / self.noise_var
        self.data.append((day, x, r))
        if c.attribution:
            self._a6(day)
            if self.identified_day is None and self.a1() and self.a2():
                self.identified_day = day
        m, C = self.mean, self.cov
        self.history.append((day, float(m[1]), float(np.sqrt(C[1, 1])), float(m[0]), bool(self.coupling_identified())))
        return True

    def _a6(self, day):
        """Drift check (A6): if the model's one-step-ahead errors on the last window are
        biased, the plant has changed over time. Old evidence about the offset is then
        forgotten, so the drift is not misread as a coupling."""
        c, w = self.c, self.c.a6_window
        since = len(self.pred_errors) - (self.drift_events[-1][1] if self.drift_events else 0)
        if since < w:
            return
        bias = float(np.mean(self.pred_errors[-w:]))
        if abs(bias) > c.a6_threshold * np.sqrt(self.noise_var / w) + 0.5:
            C, m = self.cov, self.mean
            m = m + np.array([bias, 0.0])
            C[0, 0] += (2 * bias) ** 2
            self.P = np.linalg.inv(C)
            self.b = self.P @ m
            self.drift_events.append((day, len(self.pred_errors)))

    def summary(self):
        """Attribution statistics for the results files."""
        m, C = self.mean, self.cov
        return dict(slope=float(m[1]), slope_sd=float(np.sqrt(C[1, 1])), intercept=float(m[0]),
                    identified_day=self.identified_day, identified_end=bool(self.coupling_identified()),
                    n_accepted=len(self.data), rejected_a5_days=list(self.rejected_a5),
                    drift_days=[d for d, _ in self.drift_events])
