# Developer: József Szeles, Department of System Engineering and Department of Electrical Engineering, University of Pannonia
"""Data-driven safety filter without any twin (baseline asked for in the ICSRS review).

Each hard limit is described by a margin measured on the plant after every hour
(negative margin = limit violated):

  air       measured delivery - demand              (shortage; 'lost' is nested in it)
  power     contracted peak - measured site power   (peak)
  cooling   measured chiller capacity - cooling load (cooling shortage)
  thermal   room limit - hour-average room temperature

Every margin gets a Bayesian linear model on the decision-time features of the
agent's risk model (room temperature at the start of the hour, ambient
temperature, air request; quadratic basis), fitted to plant data only, with the
same forgetting as the residual learner. Epistemic uncertainty: K samples of the
weights from the posterior. Aleatory uncertainty: Gaussian residuals with the
empirical covariance of the last 500 one-step-ahead residuals, so that the
shared cause (within-hour room disturbance) is kept between the limits. The
system-level risk is the union of the four violations, estimated with common
random numbers exactly as for the twin; the range is the same alpha / 1 - alpha
quantile interval over the K samples.

No physics and no twin are used: the model knows nothing about a level until the
plant has run near it."""
import numpy as np
from scipy.linalg import cho_factor, cho_solve

LIMITS = ("air", "power", "cooling", "thermal")


def phi(t_room, t_amb, req):
    x, a, r = (t_room - 30.0) / 10.0, (t_amb - 20.0) / 10.0, (np.asarray(req, dtype=float) - 250.0) / 30.0
    one = np.ones_like(r)
    return np.stack([one, x * one, a * one, r, x * r, a * r, x * x * one, a * a * one, x * a * one, r * r], axis=-1)


class DataFilter:
    def __init__(self, cfg, lam0=1e-3, forgetting=0.9995, k=40, window=500, min_obs=20, seed=4242):
        self.c, self.f, self.k, self.window, self.min_obs = cfg, forgetting, k, window, min_obs
        d = phi(30.0, 20.0, 250.0).shape[-1]
        self.P0 = lam0 * np.eye(d)
        self.P = self.P0.copy()
        self.B = np.zeros((d, len(LIMITS)))
        self.res = []                                       # one-step-ahead residual vectors
        self.n = 0
        rng = np.random.default_rng(seed)
        self.z_ep = rng.standard_normal((k, d, len(LIMITS)))            # common random numbers (epistemic)
        self.z_al = rng.standard_normal((cfg.n_inner, len(LIMITS)))     # common random numbers (aleatory)
        self.R0 = np.diag(np.array([10.0, 10.0, 5.0, 3.0]) ** 2)

    def margins(self, rec):
        c = self.c
        load = c.cool_per_nl * rec["request"] + c.cool_amb_per_deg * max(0.0, rec["t_amb"] - 20.0)
        return np.array([rec["q_meas"] - rec["demand"], c.peak_limit - rec["power_meas"],
                         rec["cap_meas"] - load, c.t_room_max - rec["t_room"]])

    def _R(self):
        if len(self.res) < 2 * self.min_obs:
            return self.R0
        r = np.array(self.res[-self.window:])
        return np.cov(r.T) + 1e-6 * np.eye(len(LIMITS))

    def bounds(self, t_room, t_amb):
        """(lo, mean, hi) of the union risk for every production level."""
        c = self.c
        F = phi(t_room, t_amb, np.array(c.levels))                      # (L, d)
        if self.n < self.min_obs:
            L = len(c.levels)
            return np.zeros(L), np.full(L, 0.5), np.ones(L)
        cf = cho_factor(self.P)
        W = cho_solve(cf, self.B)                                      # (d, 4) posterior mean
        R = self._R()
        Linv = np.linalg.cholesky(np.linalg.inv(self.P))                # cov of w = s2 * P^-1
        s = np.sqrt(np.diag(R))
        Ws = W[None] + np.einsum("ij,kjl->kil", Linv, self.z_ep) * s[None, None, :]   # (K, d, 4)
        M = np.einsum("ld,kdm->klm", F, Ws)                              # (K, L, 4) mean margins
        E = self.z_al @ np.linalg.cholesky(R).T                          # (n, 4) aleatory residuals
        p = np.any(M[:, :, None, :] + E[None, None, :, :] < 0.0, axis=-1).mean(-1)   # (K, L)
        lo, hi = np.quantile(p, c.range_q, axis=0)
        return lo, p.mean(0), hi

    def learn(self, rec):
        f = phi(rec["t_start"], rec["t_amb"], rec["request"])
        y = self.margins(rec)
        if self.n >= self.min_obs:                                      # residuals only once the model exists
            self.res.append(y - f @ cho_solve(cho_factor(self.P), self.B))
        self.P = self.f * self.P + (1 - self.f) * self.P0 + np.outer(f, f)
        self.B = self.f * self.B + np.outer(f, y)
        self.n += 1
