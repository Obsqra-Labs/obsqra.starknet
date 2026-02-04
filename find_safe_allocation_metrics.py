#!/usr/bin/env python3
"""
Helper: Find metrics that produce allocations within DAO constraints.

DAO Constraints:
- max_single: 6000 (60%)
- min per protocol: 1000 (10%)

This script tests various metric combinations and shows which allocations
they produce WITHOUT generating proofs (read-only preview).
"""

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.selector import get_selector_from_name
import asyncio
import requests

RISK_ENGINE = 0x00967a28878b85bbb56ac1810152f71668a5f4e3020aed21a5afd1df6129e9ab
RPC_URL = "https://starknet-sepolia-rpc.publicnode.com"

# On-chain APYs
JEDISWAP_APY = 850  # 8.5%
EKUBO_APY = 1210    # 12.1%


def calculate_risk_score(util, vol, liq, audit, age):
    """Calculate risk score using the same formula as contract."""
    # Utilization component (0-40 points, higher util = higher risk)
    util_component = (util * 40) // 10000
    
    # Volatility component (0-40 points)
    vol_component = (vol * 40) // 10000
    
    # Liquidity component (0-15 points, INVERTED: higher liq category = lower risk)
    # liq is 0-3; liq=3 → lowest risk (0 points), liq=0 → highest risk (15 points)
    liq_component = 15 - (liq * 15) // 3
    
    # Audit score component (0-15 points, INVERTED: higher audit = lower risk)
    # audit is 0-100; audit=100 → 0 points, audit=0 → 15 points
    audit_component = 15 - (audit * 15) // 100
    
    # Age component (0-10 points, INVERTED with cap: older = lower risk)
    # age_days < 30: 10 points; >= 365: 0 points; linear in between
    if age < 30:
        age_component = 10
    elif age >= 365:
        age_component = 0
    else:
        age_component = 10 - ((age - 30) * 10) // 335
    
    # Total risk = sum, clamped to [5, 95]
    total = util_component + vol_component + liq_component + audit_component + age_component
    
    if total < 5:
        return 5
    elif total > 95:
        return 95
    return total


def calculate_allocation(jedi_risk, ekubo_risk, jedi_apy, ekubo_apy):
    """Calculate allocation using same formula as contract."""
    # Risk-adjusted score = (APY * 10000) / (Risk + 1)
    jedi_score = (jedi_apy * 10000) // (jedi_risk + 1)
    ekubo_score = (ekubo_apy * 10000) // (ekubo_risk + 1)
    total_score = jedi_score + ekubo_score
    
    # JediSwap percentage
    jedi_pct = (jedi_score * 10000) // total_score
    ekubo_pct = 10000 - jedi_pct
    
    return jedi_pct, ekubo_pct


def test_metrics(desc, jedi_metrics, ekubo_metrics):
    """Test a set of metrics and show the resulting allocation."""
    jedi_risk = calculate_risk_score(**jedi_metrics)
    ekubo_risk = calculate_risk_score(**ekubo_metrics)
    
    jedi_pct, ekubo_pct = calculate_allocation(jedi_risk, ekubo_risk, JEDISWAP_APY, EKUBO_APY)
    
    passes_dao = jedi_pct <= 6000 and ekubo_pct <= 6000 and jedi_pct >= 1000 and ekubo_pct >= 1000
    status = "✅ PASS" if passes_dao else "❌ FAIL"
    
    print(f"\n{desc}")
    print(f"  Jedi metrics: {jedi_metrics}")
    print(f"  Ekubo metrics: {ekubo_metrics}")
    print(f"  → Jedi risk: {jedi_risk}, Ekubo risk: {ekubo_risk}")
    print(f"  → Allocation: Jedi {jedi_pct} ({jedi_pct/100:.1f}%), Ekubo {ekubo_pct} ({ekubo_pct/100:.1f}%)")
    print(f"  {status} DAO constraints")
    
    return passes_dao, jedi_pct, ekubo_pct


if __name__ == "__main__":
    print("=" * 70)
    print("Finding Metrics That Produce Safe Allocations")
    print("=" * 70)
    print(f"\nOn-chain APYs: JediSwap {JEDISWAP_APY}bp, Ekubo {EKUBO_APY}bp")
    print("DAO Constraints: max_single=6000 (60%), min=1000 (10%) per protocol")
    print("\n" + "=" * 70)
    
    # Test various combinations
    test_metrics(
        "1. Equal Metrics (baseline)",
        {"util": 500, "vol": 2000, "liq": 2, "audit": 85, "age": 365},
        {"util": 500, "vol": 2000, "liq": 2, "audit": 85, "age": 365}
    )
    
    test_metrics(
        "2. Jedi Slightly Higher Volatility",
        {"util": 500, "vol": 2500, "liq": 2, "audit": 85, "age": 365},
        {"util": 500, "vol": 2000, "liq": 2, "audit": 85, "age": 365}
    )
    
    test_metrics(
        "3. Jedi Much Higher Volatility",
        {"util": 500, "vol": 3500, "liq": 1, "audit": 80, "age": 300},
        {"util": 500, "vol": 1500, "liq": 3, "audit": 90, "age": 400}
    )
    
    test_metrics(
        "4. Jedi Extreme Risk (expect 70%+ to Ekubo - FAIL)",
        {"util": 700, "vol": 4500, "liq": 0, "audit": 75, "age": 200},
        {"util": 300, "vol": 800, "liq": 3, "audit": 95, "age": 500}
    )
    
    test_metrics(
        "5. Jedi Ultra Extreme Risk (expect 80%+ to Ekubo - FAIL)",
        {"util": 900, "vol": 6000, "liq": 0, "audit": 65, "age": 100},
        {"util": 200, "vol": 500, "liq": 3, "audit": 98, "age": 600}
    )
    
    print("\n" + "=" * 70)
    print("Finding PASS cases: need Jedi lower risk to balance APY difference")
    print("=" * 70)
    
    test_metrics(
        "6. Jedi Lower Volatility (trying to get Jedi > 40%)",
        {"util": 500, "vol": 1500, "liq": 3, "audit": 90, "age": 400},
        {"util": 500, "vol": 2500, "liq": 1, "audit": 80, "age": 300}
    )
    
    test_metrics(
        "7. Jedi Much Lower Volatility",
        {"util": 400, "vol": 1000, "liq": 3, "audit": 95, "age": 500},
        {"util": 600, "vol": 3000, "liq": 1, "audit": 75, "age": 250}
    )
    
    test_metrics(
        "8. Jedi Extreme Low Risk (trying 50/50)",
        {"util": 300, "vol": 800, "liq": 3, "audit": 95, "age": 500},
        {"util": 700, "vol": 4000, "liq": 0, "audit": 75, "age": 200}
    )
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
