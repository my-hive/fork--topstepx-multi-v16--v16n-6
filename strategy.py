"""Opening-range breakout on 30-minute RTH range, stop at opposite range side."""
import numpy as np
import pandas as pd

FAMILY = "opening-range-breakout"
PARAMS = {"or_end_ct": 36000, "entry_cutoff_ct": 52200, "max_width": 6.0, "min_width": 2.0, "risk": 300}


def entry_risk(panel):
    out = {}
    for s, d in panel.items():
        risk = np.zeros(len(d))
        hi = d.high.where((d.ct_sec >= 34200) & (d.ct_sec < PARAMS["or_end_ct"]))
        lo = d.low.where((d.ct_sec >= 34200) & (d.ct_sec < PARAMS["or_end_ct"]))
        w = (hi.groupby(d.session).transform("max") - lo.groupby(d.session).transform("min")) * 50.0
        risk[:] = np.clip(w.fillna(0).to_numpy(), 0, PARAMS["risk"])
        out[s] = risk
    return out


def signals(panel):
    out = {s: np.zeros(len(d), dtype=np.int64) for s, d in panel.items()}
    if "ES" not in panel:
        return out
    es = panel["ES"]
    hi = es.high.where((es.ct_sec >= 34200) & (es.ct_sec < PARAMS["or_end_ct"]))
    lo = es.low.where((es.ct_sec >= 34200) & (es.ct_sec < PARAMS["or_end_ct"]))
    orh = hi.groupby(es.session).transform("max")
    orl = lo.groupby(es.session).transform("min")
    width = orh - orl
    tradable = (width >= PARAMS["min_width"]) & (width <= PARAMS["max_width"])
    c = es.close
    up = ((c > orh) & (c.shift(1) <= orh)).fillna(False)
    dn = ((c < orl) & (c.shift(1) >= orl)).fillna(False)
    ev = (up.astype(np.int64) - dn.astype(np.int64)).groupby(es.session).cumsum().clip(-1, 1)
    active = (es.ct_sec >= PARAMS["or_end_ct"]) & (es.ct_sec < PARAMS["entry_cutoff_ct"])
    pos = np.where(active & tradable, ev, 0)
    pos = pd.Series(pos, index=es.index).groupby(es.session).ffill().fillna(0).astype(np.int64)
    out["ES"] = pos.to_numpy()
    return out
