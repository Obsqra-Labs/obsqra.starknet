"""
Deterministic risk model used for zkML scoring.

This mirrors the Cairo implementation so off-chain displays match on-chain logic.
"""
from __future__ import annotations

from typing import Dict, Tuple


def calculate_risk_score(metrics: Dict[str, int]) -> Tuple[int, Dict[str, int]]:
    """
    Calculate risk score using the reference linear model.

    Mirrors Cairo math:
    - utilization_risk = utilization * 25 / 10000
    - volatility_risk = volatility * 40 / 10000
    - liquidity_risk = 0/5/15/30 by category (0..3)
    - audit_risk = (100 - audit_score) * 3 / 10
    - age_risk = max(0, (730 - age_days) * 10 / 730)
    - total = clamp(sum, 5, 95)
    """
    util = metrics["utilization"]
    vol = metrics["volatility"]
    liq = metrics["liquidity"]
    audit = metrics["audit_score"]
    age = metrics["age_days"]

    util_component = int((util * 25) / 10000)
    vol_component = int((vol * 40) / 10000)

    if liq == 0:
        liq_component = 0
    elif liq == 1:
        liq_component = 5
    elif liq == 2:
        liq_component = 15
    else:
        liq_component = 30

    audit_component = int(((100 - audit) * 3) / 10)

    if age >= 730:
        age_penalty = 0
    else:
        age_penalty = int(((730 - age) * 10) / 730)

    total = util_component + vol_component + liq_component + audit_component + age_penalty
    total_clamped = max(5, min(95, total))

    components = {
        "util_component": util_component,
        "vol_component": vol_component,
        "liq_component": liq_component,
        "audit_component": audit_component,
        "age_penalty": age_penalty,
        "total_unclamped": total,
        "total_clamped": total_clamped,
    }

    return total_clamped, components
