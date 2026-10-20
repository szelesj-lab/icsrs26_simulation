"""All parameters in one place. Every number here is hypothetical, chosen to
reproduce the qualitative story of the paper's use case, not measured on the
FESTO line."""
from dataclasses import dataclass, field


@dataclass
class Config:
    # --- horizon ---
    days: int = 120
    work_hours: tuple = (6, 22)          # decisions are made in these hours

    # --- compressor (true plant) ---
    q_nom: float = 300.0                  # nominal air delivery, Nl/min
    t_ref: float = 20.0                   # reference intake (room) temperature, degC
    coupling_true: float = -1.0           # Nl/min per degC above t_ref  (missing in the twin)
    q_noise_sd: float = 2.0               # delivery noise, Nl/min
    drift_start_day: int = 80             # wear: nominal delivery drops after this day
    drift_per_day: float = -0.15          # Nl/min per day

    # --- room heat (thermal loop) ---
    heat_gain: float = 7.0                # degC rise of equilibrium at full compressor load
    tau_h: float = 2.0                    # room time constant, hours
    room_noise_sd: float = 3.0            # degC unforeseen within-hour disturbance (shared cause)

    # --- ambient weather (stochastic) ---
    season_base: float = 12.0             # degC at season start/end
    season_amp: float = 14.0              # degC added in mid-season
    day_offset_sd: float = 3.0            # day-to-day weather variation
    diurnal_amp: float = 5.0              # degC, peak at 15:00

    # --- production / demand ---
    levels: tuple = (200.0, 220.0, 240.0, 250.0, 260.0, 265.0, 270.0, 275.0, 280.0)  # air request, Nl/min
    demand_cv: float = 0.025              # demand noise as fraction of request

    # --- sensor fault (to exercise attribution condition A5) ---
    fault_days: tuple = (70, 75)          # delivery sensor biased in these days
    fault_bias: float = -15.0             # Nl/min

    # --- electrical power and contracted peak (second risk type) ---
    p_line_per_nl: float = 0.30           # kW of production-line power per Nl/min of air request
    p_comp_per_nl: float = 0.12           # kW compressor power per Nl/min at t_ref
    comp_eff_coef: float = 0.01           # +1 % compressor power per degC intake (missing in the twin)
    p_hvac_per_deg: float = 1.5           # kW hall cooling per degC ambient above 22 degC
    p_base_mean: float = 40.0             # kW other consumers (random)
    p_base_sd: float = 6.0
    p_meter_sd: float = 1.0
    peak_limit: float = 184.0             # kW contracted power (hourly mean)

    # --- process cooling (risk: cooling shortage) ---
    cool_per_nl: float = 0.15             # kW process heat to remove per Nl/min of request
    cool_amb_per_deg: float = 1.0         # kW extra cooling load per degC ambient above 20
    chiller_cap: float = 70.0             # kW nominal chiller capacity (what the twin assumes)
    chiller_derate: float = -1.5          # kW per degC ambient above 25 (missing in the twin)
    chiller_noise_sd: float = 3.0

    # --- thermal limit (risk: compressor room too hot) ---
    t_room_max: float = 43.0              # degC hour-average intake temperature

    # --- lost production (risk: output below plan) ---
    lost_tol: float = 0.02                # more than 2 % of the requested air missing

    # --- energy cost per unit (soft risk; logged, not used in decisions or reward) ---
    tariff_peak: float = 0.25             # EUR/kWh 8:00-20:00
    tariff_off: float = 0.15
    price_sigma: float = 0.25             # lognormal price variation (spot exposure)
    cost_budget: float = 3.6              # EUR per Nm3 of delivered air, hourly (all site power)

    # --- energy ---
    e_spec_ref: float = 0.11              # kWh per Nm3 at t_ref
    e_temp_coef: float = 0.005            # +0.5 % per degC intake temperature

    # --- risk model and shield ---
    risk_limit: float = 0.01              # admissible system-level risk per hour (P of any hard limit violated)
    range_q: tuple = (0.05, 0.95)         # epistemic quantiles that define the range
    sd_state_twin: float = 1.5            # degC: hour-average room temp from the twin (= half the disturbance)

    # --- risk aggregation across the hard limits (used by the twin simulation) ---
    aggregation: str = "joint"            # joint (union, default) | boole | independent | single | joint_with_cost
    n_inner: int = 1000                   # aleatory samples (common random numbers)
    n_epistemic: int = 40                 # outer samples of the coupling posteriors

    # --- residual learner ---
    attribution: bool = True              # False: ablation, every residual is learned (no A1/A2 gate, no A5, no A6)
    prior_sd_intercept: float = 3.0
    prior_sd_slope: float = 0.7
    forgetting: float = 0.9995            # per accepted residual
    a5_threshold: float = 10.0            # Nl/min disagreement measured vs pressure-implied
    a6_window: int = 60                   # residuals per window for the drift check
    a6_threshold: float = 3.0             # z-score of the mean one-step error that counts as drift

    prior_sd_slope_power: float = 0.4     # kW per degC at full request
    prior_sd_slope_chiller: float = 1.5   # kW per degC ambient
    # --- fixed-margin baseline ---
    fixed_margin: float = 40.0            # Nl/min kept free on every hour
    fixed_power_margin: float = 30.0      # kW kept free below the contracted peak
    fixed_cool_margin: float = 18.0       # kW chiller capacity kept free
    fixed_thermal_margin: float = 4.0     # degC kept below the thermal limit

    # --- supervisor (tabular, one-step values per room-temperature bin, i.e. gamma = 0) ---
    temp_bins: tuple = (22.0, 26.0, 30.0, 34.0, 38.0)
    alpha: float = 0.1
    eps_start: float = 0.3
    eps_end: float = 0.02
    reward_per_nm3: float = 1.0
    shortage_penalty: float = 60.0
    peak_penalty: float = 40.0
    cool_penalty: float = 40.0
    thermal_penalty: float = 40.0

    # --- misspecification scenarios for the air-delivery coupling ---
    scenario: str = "base"                # base | episodes | hinge   (ambient: extra, not in the paper)
    hinge_T: float = 30.0                 # hinge: no effect below this room temperature ...
    hinge_slope: float = -2.0             # ... and this slope above it (Nl/min per degC)
    ambient_ref: float = 13.0             # ambient: delivery follows OUTSIDE temperature, not the room
    episode_start_day: int = 60           # episodes: the plant changes only after the learning phase
    episode_rate: float = 0.06            # episodes: chance per day that a clogging episode starts
    episode_days: tuple = (2, 5)          # episode length range, days
    episode_drop: float = -15.0           # Nl/min while clogged (unexplained by any input)

    seed: int = 0
    extra: dict = field(default_factory=dict)
