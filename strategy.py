"""ES morning exposure follows completed FX overnight risk signal."""
import numpy as np

FAMILY = "equity-fx-risk-barometer"
PARAMS = {"entry_ct": 30660, "exit_ct": 36000, "risk": 250}


def entry_risk(panel):
    return {s: np.full(len(d), PARAMS["risk"], dtype=float) for s, d in panel.items()}


def signals(panel):
    out = {s: np.zeros(len(d), dtype=np.int64) for s, d in panel.items()}
    if "ES" not in panel or "6E" not in panel:
        return out
    es, fx = panel["ES"], panel["6E"]
    fx_open = fx.open.where(fx.ct_sec == 17 * 3600).groupby(fx.session).transform("first")
    fx_sig = -np.sign((fx.close / fx_open - 1).reindex(es.index).ffill()).fillna(0).astype(np.int64)
    active = (es.ct_sec >= PARAMS["entry_ct"]) & (es.ct_sec < PARAMS["exit_ct"])
    out["ES"] = np.where(active, fx_sig, 0)
    return out
