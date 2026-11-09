"""CL Wednesday EIA-release impulse continuation (post-release window)."""
import numpy as np
import pandas as pd

FAMILY = "energy-eia-inventory-drift"
PARAMS = {"rel_ct": 30600, "sig_end_ct": 31500, "exit_ct": 39600, "min_impulse": 0.0, "risk": 300}


def entry_risk(panel):
    return {s: np.full(len(d), PARAMS["risk"], dtype=float) for s, d in panel.items()}


def signals(panel):
    out = {s: np.zeros(len(d), dtype=np.int64) for s, d in panel.items()}
    if "CL" not in panel:
        return out
    cl = panel["CL"]
    pos = np.zeros(len(cl), dtype=np.int64)
    opens, closes, sec = cl.open.to_numpy(), cl.close.to_numpy(), cl.ct_sec.to_numpy()
    for ix in cl.groupby("session", sort=False).indices.values():
        s = sec[ix]
        if pd.Timestamp(cl.session.iloc[ix[0]]).day_of_week != 2:
            continue
        start = np.flatnonzero(s == PARAMS["rel_ct"])
        end = np.flatnonzero(s == PARAMS["sig_end_ct"])
        if not len(start) or not len(end):
            continue
        impulse = closes[ix[end[0] - 1]] / opens[ix[start[0]]] - 1
        if abs(impulse) < PARAMS["min_impulse"]:
            continue
        active = (s >= PARAMS["sig_end_ct"]) & (s < PARAMS["exit_ct"])
        pos[ix[active]] = -int(np.sign(impulse))
    out["CL"] = pos
    return out
