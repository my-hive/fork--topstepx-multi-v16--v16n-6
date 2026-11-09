"""Adopted from v16n-5 (index-prior-day-reversal), re-tested on ES/YM: fade prior RTH return after high-range day."""
import numpy as np

FAMILY = "index-prior-day-reversal-esym"
PARAMS = {"med_win": 20, "entry_ct": 30660, "exit_ct": 49800, "risk": 250}
SYMS = ("ES", "YM")


def entry_risk(panel):
    return {s: np.full(len(d), PARAMS["risk"], dtype=float) for s, d in panel.items()}


def signals(panel):
    out = {s: np.zeros(len(d), dtype=np.int64) for s, d in panel.items()}
    for s in SYMS:
        if s not in panel:
            continue
        d = panel[s]
        o, h, l, c, sec = (d[k].to_numpy() for k in ("open", "high", "low", "close", "ct_sec"))
        pos = np.zeros(len(d), dtype=np.int64)
        ranges, prev_ret, prev_rng = [], np.nan, np.nan
        for ix in d.groupby("session", sort=False).indices.values():
            ss = sec[ix]
            rth = ix[(ss >= 30600) & (ss < 54000)]
            if np.isfinite(prev_ret) and len(ranges) >= PARAMS["med_win"]:
                if prev_rng > np.median(ranges[-PARAMS["med_win"]:]):
                    m = (ss >= PARAMS["entry_ct"]) & (ss < PARAMS["exit_ct"])
                    pos[ix[m]] = -int(np.sign(prev_ret))
            if len(rth) > 30:
                prev_ret = c[rth[-1]] / o[rth[0]] - 1
                prev_rng = (h[rth].max() - l[rth].min()) / o[rth[0]]
                ranges.append(prev_rng)
        out[s] = pos
    return out
