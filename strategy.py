"""MES intraday mean reversion when rates/equity 15-minute returns sharply diverge."""
import numpy as np

FAMILY = "equity-rates-divergence-reversion"
PARAMS = {"lookback": 15, "threshold": 0.002, "start_ct": 34200, "end_ct": 51000, "risk": 100}


def entry_risk(panel):
    return {symbol: np.full(len(df), PARAMS["risk"], dtype=float) for symbol, df in panel.items()}


def signals(panel):
    result = {symbol: np.zeros(len(df), dtype=np.int64) for symbol, df in panel.items()}
    if "MES" not in panel or "ZN" not in panel:
        return result
    mes, zn = panel["MES"], panel["ZN"]
    n = PARAMS["lookback"]
    mes_ret = mes.close.pct_change(n)
    zn_ret = zn.close.pct_change(n).reindex(mes.index)
    divergence = mes_ret - zn_ret
    active = (mes.ct_sec >= PARAMS["start_ct"]) & (mes.ct_sec < PARAMS["end_ct"])
    result["MES"] = np.where(active & (divergence.abs() > PARAMS["threshold"]),
                               -np.sign(divergence).fillna(0).astype(np.int64), 0)
    return result
