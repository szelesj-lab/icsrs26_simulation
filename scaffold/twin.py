"""The digital twin (simulation platform).

It models demand, the compressor and room heat, but assumes constant air
delivery: the coupling 'hot intake air -> less air' is missing. Consulting it
gives a sharper forecast of next-hour room temperature than the cheap
surrogate, and a logged prediction that is later compared with reality."""
import numpy as np


class Twin:
    def __init__(self, cfg):
        self.c = cfg
        self.queries = 0

    def predict_delivery(self, t_room):
        return self.c.q_nom                      # constant: the missing coupling

    def predict_power(self, request, t_room, t_amb):
        """Line + compressor at reference efficiency + hall cooling + mean base load.
        Missing: compressor power rising with intake temperature."""
        c = self.c
        return (c.p_line_per_nl + c.p_comp_per_nl) * request + c.p_hvac_per_deg * max(0.0, t_amb - 22.0) + c.p_base_mean

    def predict_chiller(self, t_amb):
        return self.c.chiller_cap                 # missing: derating in hot weather

    def predict_room(self, t_room, t_amb, request, q_assumed):
        """One-hour room temperature forecast from the twin's thermal model."""
        c = self.c
        load = 0.0 if request == 0 else min(1.0, request / max(q_assumed, 1.0))
        t_eq = t_amb + c.heat_gain * load
        return t_room + (t_eq - t_room) / c.tau_h

    def consult(self, t_room, t_amb, request):
        self.queries += 1
        q = self.predict_delivery(t_room)
        return dict(t_room_next=self.predict_room(t_room, t_amb, request, q), q_pred=q)
