"""ML Models for Risk Prediction and Optimization"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import json


class RiskPredictionModel:
    """Risk score prediction model using historical data."""
    
    def __init__(self, model_version: str = "v1"):
        self.model_version = model_version
        self.models = {}  # protocol -> model
        self.scalers = {}  # protocol -> scaler
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize or load pre-trained models."""
        for protocol in ["nostra", "zklend", "ekubo"]:
            self.models[protocol] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1,
            )
            self.scalers[protocol] = StandardScaler()
    
    def predict_risk(self, protocol: str, metrics: dict) -> tuple[float, float]:
        """
        Predict risk score for a protocol.
        
        Returns: (predicted_risk, confidence_score)
        """
        if protocol not in self.models:
            # Fallback to simple calculation
            return self._fallback_risk_calc(metrics), 0.6
        
        # Extract features from metrics
        features = np.array([[
            metrics.get("utilization", 0),
            metrics.get("volatility", 0),
            metrics.get("liquidity", 0),
            metrics.get("audit_score", 0),
            metrics.get("age_days", 0),
        ]])
        
        # Scale features
        features_scaled = self.scalers[protocol].transform(features)
        
        # Predict
        prediction = self.models[protocol].predict(features_scaled)[0]
        
        # Calculate confidence (simplified - real model would return actual confidence)
        confidence = min(max(0.5 + (abs(metrics.get("audit_score", 0)) / 100) * 0.4, 0.5), 0.95)
        
        return float(np.clip(prediction, 0, 100)), float(confidence)
    
    def _fallback_risk_calc(self, metrics: dict) -> float:
        """Fallback calculation when model unavailable."""
        utilization = metrics.get("utilization", 0) / 100
        volatility = metrics.get("volatility", 0) / 100
        audit_score = metrics.get("audit_score", 100) / 100
        
        risk = (utilization * 30) + (volatility * 40) - (audit_score * 30)
        return float(np.clip(risk, 0, 100))


class YieldForecastModel:
    """Yield prediction model for protocols."""
    
    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42,
        )
        self.scaler = StandardScaler()
    
    def predict_yield(self, protocol: str, current_apy: float, market_data: dict) -> tuple[float, float]:
        """
        Predict future yield for protocol.
        
        Returns: (predicted_yield, confidence_score)
        """
        # Simple trend-based prediction
        features = np.array([[
            current_apy,
            market_data.get("tvl", 0) / 1e9,  # normalize TVL
            market_data.get("volatility", 0),
        ]])
        
        features_scaled = self.scaler.transform(features)
        prediction = self.model.predict(features_scaled)[0]
        
        confidence = 0.7  # Yield prediction is inherently uncertain
        
        return float(np.clip(prediction, 0, 100)), confidence


class AllocationOptimizer:
    """Optimize allocation across protocols using ML."""
    
    def __init__(self):
        self.risk_model = RiskPredictionModel()
        self.yield_model = YieldForecastModel()
    
    def optimize_allocation(
        self,
        protocol_metrics: dict,
        apys: dict,
        user_preferences: dict = None
    ) -> dict:
        """
        Optimize allocation across protocols.
        
        Args:
            protocol_metrics: {protocol: {utilization, volatility, ...}}
            apys: {protocol: current_apy}
            user_preferences: {risk_tolerance, preferred_protocols, ...}
        
        Returns:
            {protocol: allocation_percentage}
        """
        if not user_preferences:
            user_preferences = {"risk_tolerance": "medium"}
        
        # Get risk predictions
        risk_scores = {}
        for protocol, metrics in protocol_metrics.items():
            risk, confidence = self.risk_model.predict_risk(protocol, metrics)
            risk_scores[protocol] = risk
        
        # Get yield forecasts
        yield_forecasts = {}
        for protocol, apy in apys.items():
            market_data = protocol_metrics.get(protocol, {})
            forecast, _ = self.yield_model.predict_yield(protocol, apy, market_data)
            yield_forecasts[protocol] = forecast
        
        # Calculate scores (higher is better)
        scores = {}
        for protocol in protocol_metrics.keys():
            risk = risk_scores.get(protocol, 50)
            yield_forecast = yield_forecasts.get(protocol, apys.get(protocol, 0))
            
            # Risk-adjusted score
            risk_factor = 1.0 - (risk / 100)  # Lower risk = higher factor
            score = yield_forecast * risk_factor
            scores[protocol] = max(score, 0.1)  # Prevent zero scores
        
        # Normalize to percentages
        total_score = sum(scores.values())
        allocations = {
            protocol: (score / total_score) * 100
            for protocol, score in scores.items()
        }
        
        # Apply risk tolerance constraints
        risk_tolerance = user_preferences.get("risk_tolerance", "medium")
        allocations = self._apply_risk_constraints(allocations, risk_tolerance)
        
        return allocations
    
    def _apply_risk_constraints(self, allocations: dict, risk_tolerance: str) -> dict:
        """Apply risk tolerance constraints to allocation."""
        if risk_tolerance == "low":
            # Favor safer protocols (higher audit scores)
            allocations["nostra"] = min(allocations.get("nostra", 0) * 1.2, 60)
            allocations["zklend"] = min(allocations.get("zklend", 0) * 1.1, 50)
            allocations["ekubo"] = allocations.get("ekubo", 0) * 0.7
        elif risk_tolerance == "high":
            # Allow higher allocation to higher-yield protocols
            allocations["ekubo"] = min(allocations.get("ekubo", 0) * 1.3, 60)
        
        # Normalize to sum to 100
        total = sum(allocations.values())
        if total > 0:
            allocations = {k: (v / total) * 100 for k, v in allocations.items()}
        
        return allocations

