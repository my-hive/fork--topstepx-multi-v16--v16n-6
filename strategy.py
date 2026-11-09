"""Grain USDA report-minute reversal: ZC 11:00 CT event shock continues over subsequent 30 minutes."""
import numpy as np
import pandas as pd

FAMILY = "grain-usda-report-continuation"
PARAMS = {"event_ct": 39600, "hold_minutes": 30, "stop_usd": 290, "risk": 300, "exit_ct": 53400}
SYM, PV = "ZC", 50.0


def entry_risk(panel):
    return {s: np.full(len(d), PARAMS["risk"], dtype=float) for s, d in panel.items()}


def signals(panel):
    out = {s: np.zeros(len(d), dtype=np.int64) for s, d in panel.items()}
    if SYM not in panel:
        return out
    d = panel[SYM]
    o, h, l, c, sec = (d[k].to_numpy() for k in ("open", "high", "low", "close", "ct_sec"))
    pos, stop_pts = np.zeros(len(d), dtype=np.int64), PARAMS["stop_usd"] / PV
    for ix in d.groupby("session", sort=False).indices.values():
        ss = sec[ix]
        event = ix[ss == PARAMS["event_ct"]]
        if len(event) != 1 or pd.Timestamp(d.session.iloc[event[0]]).dayofweek != 4:
            continue
        side = int(np.sign(c[event[0]] - o[event[0]]))
        if not side:
            continue
        entry, stopped = None, False
        for i in ix[(ss > PARAMS["event_ct"]) & (ss < PARAMS["exit_ct"])]:
            if entry is None:
                entry = o[i]
            if (side > 0 and l[i] <= entry - stop_pts) or (side < 0 and h[i] >= entry + stop_pts):
                stopped = True
            if not stopped and sec[i] < PARAMS["event_ct"] + PARAMS["hold_minutes"] * 60:
                pos[i] = side
    out[SYM] = pos
    return out
