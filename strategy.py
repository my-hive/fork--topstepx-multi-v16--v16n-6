"""RBOB daily momentum: trade RTH only when prior 20-session move is unusually large."""
import numpy as np

FAMILY = "energy-rb-daily-momentum-filter"
PARAMS = {"lookback": 20, "norm_win": 250, "quantile": 0.5, "entry_ct": 30660, "exit_ct": 53400, "risk": 300}
SYMS = ("RB",)

def entry_risk(panel):
    return {s: np.full(len(d), PARAMS["risk"], dtype=float) for s, d in panel.items()}

def signals(panel):
    out = {s: np.zeros(len(d), dtype=np.int64) for s, d in panel.items()}
    for s in SYMS:
        if s not in panel:
            continue
        d = panel[s]
        c, sec = d.close.to_numpy(), d.ct_sec.to_numpy()
        pos = np.zeros(len(d), dtype=np.int64)
        closes = []
        for ix in d.groupby("session", sort=False).indices.values():
            ss = sec[ix]
            rth = ix[(ss >= 30600) & (ss < 54000)]
            if len(closes) >= PARAMS["norm_win"] + PARAMS["lookback"]:
                hist = np.asarray(closes)
                mom = hist[-1] / hist[-1 - PARAMS["lookback"]] - 1
                moves = np.abs(hist[PARAMS["lookback"]:] / hist[:-PARAMS["lookback"]] - 1)
                threshold = np.quantile(moves[-PARAMS["norm_win"]:], PARAMS["quantile"])
                if abs(mom) > threshold:
                    pos[ix[(ss >= PARAMS["entry_ct"]) & (ss < PARAMS["exit_ct"])]] = int(np.sign(mom))
            if len(rth):
                closes.append(c[rth[-1]])
        out[s] = pos
    return out
