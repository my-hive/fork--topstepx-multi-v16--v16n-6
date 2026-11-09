"""ES momentum continuation when intraday rates confirmation (ZN) agrees."""
import numpy as np

FAMILY = "equity-rates-divergence-reversion"
PARAMS = {"lookback": 15, "threshold": 0.0015, "start_ct": 34200, "end_ct": 50400, "risk": 250}


def entry_risk(panel):
    return {symbol: np.full(len(df), PARAMS["risk"], dtype=float) for symbol, df in panel.items()}


def signals(panel):
    result = {symbol: np.zeros(len(df), dtype=np.int64) for symbol, df in panel.items()}
    if "ES" not in panel or "ZN" not in panel:
        return result
    es, zn = panel["ES"], panel["ZN"]
    n = PARAMS["lookback"]
    es_ret = es.close.pct_change(n)
    zn_ret = zn.close.pct_change(n).reindex(es.index)
    divergence = (es_ret - zn_ret).fillna(0.0)
    active = (es.ct_sec >= PARAMS["start_ct"]) & (es.ct_sec < PARAMS["end_ct"])
    result["ES"] = np.where(active & (divergence.abs() > PARAMS["threshold"]),
                            np.sign(divergence).astype(np.int64), 0)
    return result
