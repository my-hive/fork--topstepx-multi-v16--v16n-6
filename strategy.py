"""Index overnight gap-down buy: long RTH after unusually large overnight drop (forced-liquidation/overreaction reverts); no short side."""
import numpy as np

FAMILY = "index-gapdown-buy-rth"
PARAMS = {"norm_win": 250, "quantile": 0.8, "stop_usd": 290, "exit_ct": 53400}
SYMS = {"ES": 50.0, "NQ": 20.0, "YM": 5.0}
SIG_CT = 30600  # 08:30 CT bar close known at 08:31 fill

def entry_risk(panel):
    return {s: np.full(len(d), PARAMS["stop_usd"], dtype=float) for s, d in panel.items()}

def signals(panel):
    out = {s: np.zeros(len(d), dtype=np.int64) for s, d in panel.items()}
    for s, pv in SYMS.items():
        if s not in panel:
            continue
        d = panel[s]
        o, h, l, c, sec = (d[k].to_numpy() for k in ("open", "high", "low", "close", "ct_sec"))
        pos = np.zeros(len(d), dtype=np.int64)
        hist = []
        stop_pts = PARAMS["stop_usd"] / pv
        for ix in d.groupby("session", sort=False).indices.values():
            ss = sec[ix]
            ev = ix[ss >= 61200]
            sig = ix[ss == SIG_CT]
            if len(ev) and len(sig):
                ov = c[sig[0]] / o[ev[0]] - 1
                if len(hist) >= PARAMS["norm_win"] // 2 and ov < 0 and -ov > np.quantile(np.abs(hist[-PARAMS["norm_win"]:]), PARAMS["quantile"]):
                    ent, done = None, False
                    for i in ix[(ss > SIG_CT) & (ss < PARAMS["exit_ct"])]:
                        if done:
                            break
                        if ent is None:
                            ent = o[i]
                        if l[i] <= ent - stop_pts:
                            done = True
                            continue
                        pos[i] = 1
                hist.append(ov)
        out[s] = pos
    return out
