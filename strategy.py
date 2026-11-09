"""HG 11:30-12:00 CT positive intraday seasonal liquidity window."""
import numpy as np

FAMILY = "tod-seasonality-allasset"
PARAMS = {"entry_ct": 41400, "exit_ct": 43200, "risk": 300}


def entry_risk(panel):
    return {s: np.full(len(d), PARAMS["risk"], dtype=float) for s, d in panel.items()}


def signals(panel):
    out = {s: np.zeros(len(d), dtype=np.int64) for s, d in panel.items()}
    if "HG" in panel:
        d = panel["HG"]
        out["HG"] = ((d.ct_sec >= PARAMS["entry_ct"]) & (d.ct_sec < PARAMS["exit_ct"])).astype(np.int64)
    return out
