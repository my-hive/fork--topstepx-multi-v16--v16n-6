"""FX-to-equity lead: 6E first-30m move above trailing median -> RTY follows 09:01-14:50, stop."""
import numpy as np

FAMILY = "xasset-6e-rty-lead-follow"
PARAMS = {"norm_win": 250, "quantile": 0.5, "stop_usd": 250, "decl_risk": 300}
LEAD, TGT, PV = "6E", "RTY", 50.0
T0, T1, TEXIT = 30600, 32400, 53400

def entry_risk(panel):
    return {s: np.full(len(d), PARAMS["decl_risk"], dtype=float) for s, d in panel.items()}

def signals(panel):
    out = {s: np.zeros(len(d), dtype=np.int64) for s, d in panel.items()}
    if LEAD not in panel or TGT not in panel:
        return out
    L, B = panel[LEAD], panel[TGT]
    lo, lsec = L.open.to_numpy(), L.ct_sec.to_numpy()
    lsess = L.session.to_numpy()
    move = {}
    for sess, ix in L.groupby("session", sort=False).indices.items():
        a, b = ix[lsec[ix] == T0], ix[lsec[ix] == T1]
        if len(a) and len(b):
            move[str(sess)] = lo[b[0]] / lo[a[0]] - 1
    hist = []
    bo, bh, bl, bsec = (B[k].to_numpy() for k in ("open", "high", "low", "ct_sec"))
    pos = np.zeros(len(B), dtype=np.int64)
    stop_pts = PARAMS["stop_usd"] / PV
    for sess, ix in B.groupby("session", sort=False).indices.items():
        m = move.get(str(sess))
        if m is not None and len(hist) >= PARAMS["norm_win"] // 2:
            h = np.abs(hist[-PARAMS["norm_win"]:])
            if abs(m) > np.quantile(h, PARAMS["quantile"]):
                side, ent, done = int(np.sign(m)), None, False
                for i in ix:
                    t = bsec[i]
                    if t < T1 + 60 or t >= 61200 or done:
                        continue
                    if t >= TEXIT:
                        break
                    if ent is None:
                        ent = bo[i]  # approx next-open entry price (known only after fill; stop uses signal-time open proxy)
                    if (side > 0 and bl[i] <= ent - stop_pts) or (side < 0 and bh[i] >= ent + stop_pts):
                        done = True
                        continue
                    pos[i] = side
        if m is not None:
            hist.append(m)
    out[TGT] = pos
    return out
