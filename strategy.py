"""Market-neutral ES/NQ relative-return dislocation reversion."""
import numpy as np
import pandas as pd

FAMILY = "equity-index-pair-dispersion"
PARAMS = {"lookback": 60, "threshold": 0.004, "start_ct": 34200, "end_ct": 50400, "risk": 250}


def entry_risk(panel):
    return {s: np.full(len(d), PARAMS["risk"], dtype=float) for s, d in panel.items()}


def signals(panel):
    out = {s: np.zeros(len(d), dtype=np.int64) for s, d in panel.items()}
    if "ES" not in panel or "NQ" not in panel:
        return out
    es, nq = panel["ES"], panel["NQ"]
    spread = es.close.pct_change(PARAMS["lookback"]) - nq.close.pct_change(PARAMS["lookback"]).reindex(es.index)
    side = np.sign(spread.fillna(0)).astype(np.int64)
    active = pd.Series((es.ct_sec >= PARAMS["start_ct"]) & (es.ct_sec < PARAMS["end_ct"]) & (spread.abs() > PARAMS["threshold"]), index=es.index)
    out["ES"] = np.where(active, -side, 0)
    a = active.reindex(nq.index, fill_value=False).to_numpy()
    sd = pd.Series(side, index=es.index).reindex(nq.index).fillna(0).astype(np.int64).to_numpy()
    out["NQ"] = np.where(a, sd, 0)
    return out
