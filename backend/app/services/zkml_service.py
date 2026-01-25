"""
Tiny zkML demo model (Cairo-aligned linear classifier).

This intentionally uses a small, deterministic model so proofs remain fast.
Weights and threshold must match the Cairo implementation in contracts/src/zkml_oracle.cairo.
"""
from dataclasses import dataclass
from typing import Dict


# Model weights (must match Cairo)
UTIL_WEIGHT = 2
VOL_WEIGHT = 3
LIQ_WEIGHT = 500
AUDIT_WEIGHT = 200
AGE_WEIGHT = 5
THRESHOLD = 22000  # score threshold for decision


@dataclass
class ZkmlInference:
    score: int
    decision: int
    threshold: int
    components: Dict[str, int]


class ZkmlService:
    """Simple linear classifier for zkML demo."""

    def infer_protocol(self, metrics: Dict[str, int]) -> ZkmlInference:
        util = int(metrics["utilization"])
        vol = int(metrics["volatility"])
        liq = int(metrics["liquidity"])
        audit = int(metrics["audit_score"])
        age = int(metrics["age_days"])

        audit_risk = max(0, 100 - audit)
        age_risk = max(0, 730 - age)

        components = {
            "util": util * UTIL_WEIGHT,
            "vol": vol * VOL_WEIGHT,
            "liq": liq * LIQ_WEIGHT,
            "audit": audit_risk * AUDIT_WEIGHT,
            "age": age_risk * AGE_WEIGHT,
        }

        score = (
            components["util"]
            + components["vol"]
            + components["liq"]
            + components["audit"]
            + components["age"]
        )

        decision = 1 if score >= THRESHOLD else 0
        return ZkmlInference(
            score=score,
            decision=decision,
            threshold=THRESHOLD,
            components=components,
        )


_zkml_service: ZkmlService | None = None


def get_zkml_service() -> ZkmlService:
    global _zkml_service
    if _zkml_service is None:
        _zkml_service = ZkmlService()
    return _zkml_service
