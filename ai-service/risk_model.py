"""
Risk Model for Obsqra.starknet

Multi-factor risk scoring algorithm (reference implementation for Cairo port).
"""

from typing import Dict, Tuple
import numpy as np


class RiskModel:
    """Risk scoring model"""
    
    def __init__(self):
        self.protocol_data = {}
    
    def get_risk_score(self, protocol_name: str) -> Tuple[int, str, Dict]:
        """
        Calculate risk score for a protocol.
        
        Returns:
            (risk_score, risk_level, factors)
        """
        # TODO: Implement risk scoring logic
        # This is a reference for the Cairo port
        
        data = self.protocol_data.get(protocol_name.lower(), {})
        
        # Multi-factor risk calculation
        utilization_risk = data.get("utilization", 0) * 25
        volatility_risk = data.get("volatility", 0) * 40
        
        # Liquidity risk (categorical)
        liquidity_map = {"Very High": 0, "High": 5, "Medium": 15, "Low": 30}
        liquidity_risk = liquidity_map.get(data.get("liquidity", "Medium"), 10)
        
        # Audit risk (inverse - lower score = higher risk)
        audit_risk = (100 - data.get("audit_score", 50)) * 0.3
        
        # Age risk (newer protocols = slightly riskier)
        age_risk = max(0, (730 - data.get("age_days", 365)) / 730 * 10)
        
        # Combined score
        total_score = int(utilization_risk + volatility_risk + liquidity_risk + audit_risk + age_risk)
        
        # Clip to 5-95 range
        total_score = np.clip(total_score, 5, 95)
        
        # Determine risk level
        if total_score < 30:
            level = "Low"
        elif total_score < 60:
            level = "Medium"
        else:
            level = "High"
        
        factors = {
            "utilization_risk": utilization_risk,
            "volatility_risk": volatility_risk,
            "liquidity_risk": liquidity_risk,
            "audit_risk": audit_risk,
            "age_risk": age_risk,
        }
        
        return total_score, level, factors

