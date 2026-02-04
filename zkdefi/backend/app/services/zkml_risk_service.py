"""
zkML Risk Score Service

Privacy-preserving risk score proof generation.
Proves risk_score <= threshold WITHOUT revealing the actual score.

Uses Groth16 (snarkjs) → Garaga-compatible proof format.
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

# Circuit paths - go from services/ -> app/ -> backend/ -> zkdefi (project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CIRCUITS_DIR = PROJECT_ROOT / "circuits" / "build"
RISK_WASM = CIRCUITS_DIR / "RiskScore_js" / "RiskScore.wasm"
RISK_ZKEY = CIRCUITS_DIR / "RiskScore_final.zkey"
RISK_WITNESS_GEN = CIRCUITS_DIR / "RiskScore_js" / "generate_witness.js"


class RiskScoreModel:
    """
    Simple risk scoring model.
    Can be replaced with actual ML model (ONNX, scikit-learn).
    """
    
    # Default model weights (normalized)
    DEFAULT_WEIGHTS = [
        10,   # total_balance weight
        15,   # position_concentration weight
        10,   # protocol_diversity weight (negative = good)
        20,   # volatility_exposure weight
        5,    # liquidity_depth weight (negative = good)
        5,    # time_in_position weight (negative = good)
        25,   # recent_drawdown weight
        10,   # correlation_risk weight
    ]
    
    DEFAULT_BIAS = 0
    SCALE = 100  # Score scaled 0-100
    
    @classmethod
    def compute_risk_score(
        cls,
        portfolio_features: list[int],
        weights: list[int] | None = None,
        bias: int = 0,
        scale: int = 100
    ) -> int:
        """
        Compute risk score from portfolio features.
        Returns score in range [0, scale].
        """
        if weights is None:
            weights = cls.DEFAULT_WEIGHTS
        
        if len(portfolio_features) != len(weights):
            raise ValueError(f"Expected {len(weights)} features, got {len(portfolio_features)}")
        
        weighted_sum = bias
        for i, (feature, weight) in enumerate(zip(portfolio_features, weights)):
            weighted_sum += feature * weight
        
        # Normalize to scale
        max_possible = sum(100 * abs(w) for w in weights) + abs(bias)
        if max_possible > 0:
            score = (weighted_sum * scale) // max_possible
        else:
            score = 0
        
        return max(0, min(scale, score))
    
    @classmethod
    def generate_witness_input(
        cls,
        portfolio_features: list[int],
        threshold: int,
        user_address: str,
        commitment_hash: str,
        weights: list[int] | None = None,
        bias: int = 0,
        scale: int = 100
    ) -> dict[str, Any]:
        """
        Generate witness input for the RiskScore circuit.
        """
        if weights is None:
            weights = cls.DEFAULT_WEIGHTS
        
        actual_score = cls.compute_risk_score(portfolio_features, weights, bias, scale)
        
        return {
            "portfolio_features": [str(f) for f in portfolio_features],
            "model_weights": [str(w) for w in weights],
            "model_bias": str(bias),
            "actual_score": str(actual_score),
            "threshold": str(threshold),
            "scale": str(scale),
            "user_address": user_address,
            "commitment_hash": commitment_hash
        }


class ZkmlRiskService:
    """
    Service for generating privacy-preserving risk score proofs.
    """
    
    def __init__(self):
        self.model = RiskScoreModel()
        self.circuits_ready = self._check_circuits()
    
    def _check_circuits(self) -> bool:
        """Check if circuits are compiled."""
        return RISK_WASM.exists() and RISK_ZKEY.exists()
    
    async def generate_risk_proof(
        self,
        user_address: str,
        portfolio_features: list[int],
        threshold: int,
        commitment_hash: str | None = None
    ) -> dict[str, Any]:
        """
        Generate Groth16 proof that risk_score <= threshold.
        
        Returns Garaga-compatible proof calldata.
        """
        # Generate commitment if not provided
        if commitment_hash is None:
            import hashlib
            commitment_hash = "0x" + hashlib.sha256(
                f"{user_address}{threshold}{portfolio_features}".encode()
            ).hexdigest()[:32]
        
        # Compute actual risk score (private - for witness only)
        actual_score = self.model.compute_risk_score(portfolio_features)
        
        # Check if compliant before generating proof
        is_compliant = actual_score <= threshold
        
        if not self.circuits_ready:
            # Return simulated proof for development
            return self._generate_simulated_proof(
                user_address=user_address,
                threshold=threshold,
                is_compliant=is_compliant,
                commitment_hash=commitment_hash
            )
        
        # Generate witness input
        witness_input = self.model.generate_witness_input(
            portfolio_features=portfolio_features,
            threshold=threshold,
            user_address=user_address,
            commitment_hash=commitment_hash
        )
        
        # Generate proof using snarkjs
        proof_data = await self._generate_groth16_proof(witness_input)
        
        # Format for Garaga
        proof_calldata = self._format_for_garaga(proof_data)
        
        return {
            "proof_type": "risk_score",
            "is_compliant": is_compliant,
            "threshold": threshold,
            "commitment_hash": commitment_hash,
            "proof_calldata": proof_calldata,
            "public_signals": proof_data.get("public_signals", [])
        }
    
    def _generate_simulated_proof(
        self,
        user_address: str,
        threshold: int,
        is_compliant: bool,
        commitment_hash: str
    ) -> dict[str, Any]:
        """
        Generate simulated proof for development/testing.
        """
        import hashlib
        
        # Simulate proof hash
        proof_hash = "0x" + hashlib.sha256(
            f"risk_proof_{user_address}_{threshold}_{is_compliant}".encode()
        ).hexdigest()[:64]
        
        # Simulated Garaga calldata (placeholder)
        simulated_calldata = [
            "0x" + hashlib.sha256(b"proof_a").hexdigest()[:64],
            "0x" + hashlib.sha256(b"proof_b1").hexdigest()[:64],
            "0x" + hashlib.sha256(b"proof_b2").hexdigest()[:64],
            "0x" + hashlib.sha256(b"proof_c").hexdigest()[:64],
            str(1 if is_compliant else 0),  # is_compliant output
            commitment_hash
        ]
        
        return {
            "proof_type": "risk_score",
            "is_compliant": is_compliant,
            "threshold": threshold,
            "commitment_hash": commitment_hash,
            "proof_hash": proof_hash,
            "proof_calldata": simulated_calldata,
            "public_signals": [str(1 if is_compliant else 0), commitment_hash],
            "simulated": True
        }
    
    async def _generate_groth16_proof(self, witness_input: dict) -> dict[str, Any]:
        """
        Generate Groth16 proof using snarkjs.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.json"
            witness_path = Path(tmpdir) / "witness.wtns"
            proof_path = Path(tmpdir) / "proof.json"
            public_path = Path(tmpdir) / "public.json"
            
            # Write input
            with open(input_path, "w") as f:
                json.dump(witness_input, f)
            
            # Generate witness
            witness_gen = RISK_WITNESS_GEN
            subprocess.run([
                "node", str(witness_gen),
                str(RISK_WASM),
                str(input_path),
                str(witness_path)
            ], check=True, capture_output=True)
            
            # Generate proof
            subprocess.run([
                "snarkjs", "groth16", "prove",
                str(RISK_ZKEY),
                str(witness_path),
                str(proof_path),
                str(public_path)
            ], check=True, capture_output=True)
            
            # Read proof
            with open(proof_path) as f:
                proof = json.load(f)
            with open(public_path) as f:
                public_signals = json.load(f)
            
            return {
                "proof": proof,
                "public_signals": public_signals
            }
    
    def _format_for_garaga(self, proof_data: dict) -> list[str]:
        """
        Format Groth16 proof for Garaga verifier.
        Converts proof to felt252 array format.
        """
        proof = proof_data["proof"]
        public_signals = proof_data["public_signals"]
        
        # Garaga expects: [pi_a, pi_b, pi_c, public_inputs...]
        # pi_a: 2 field elements
        # pi_b: 2x2 field elements (flattened)
        # pi_c: 2 field elements
        
        calldata = []
        
        # pi_a (2 elements)
        calldata.extend(proof["pi_a"][:2])
        
        # pi_b (2x2 elements, row-major)
        calldata.extend(proof["pi_b"][0][:2])
        calldata.extend(proof["pi_b"][1][:2])
        
        # pi_c (2 elements)
        calldata.extend(proof["pi_c"][:2])
        
        # Public signals
        calldata.extend(public_signals)
        
        return calldata


# Singleton instance
_risk_service: ZkmlRiskService | None = None


def get_risk_service() -> ZkmlRiskService:
    """Get or create the risk service singleton."""
    global _risk_service
    if _risk_service is None:
        _risk_service = ZkmlRiskService()
    return _risk_service
