"""Large ES overnight gap continuation: rebalance/risk flow persists through RTH."""
import numpy as np

FAMILY = "equity-overnight-gap-continuation"
PARAMS = {"gap": 0.008, "entry_ct": 30660, "exit_ct": 54000, "risk": 300}


def entry_risk(panel):
    return {s: np.full(len(d), PARAMS["risk"], dtype=float) for s, d in panel.items()}


def signals(panel):
    out = {s: np.zeros(len(d), dtype=np.int64) for s, d in panel.items()}
    if "ES" not in panel:
        return out
    d = panel["ES"]
    pos = np.zeros(len(d), dtype=np.int64)
    previous_close = np.nan
    for ix in d.groupby("session", sort=False).indices.values():
        opens, closes, sec = d.open.to_numpy()[ix], d.close.to_numpy()[ix], d.ct_sec.to_numpy()[ix]
        rth = np.flatnonzero(sec >= 34200)
        if len(rth) and np.isfinite(previous_close):
            j = rth[0]
            side = int(np.sign(opens[j] / previous_close - 1))
            if abs(opens[j] / previous_close - 1) >= PARAMS["gap"]:
                active = (sec >= PARAMS["entry_ct"]) & (sec < PARAMS["exit_ct"])
                pos[ix[active]] = side
        previous_close = closes[-1]
    out["ES"] = pos
    return out
