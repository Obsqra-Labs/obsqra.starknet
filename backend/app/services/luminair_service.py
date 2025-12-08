"""
LuminAIR proof generation service

Calls Rust binary to generate real STARK proofs using LuminAIR framework
"""
import asyncio
import json
import logging
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


@dataclass
class ProofResult:
    """Result of proof generation"""
    proof_hash: str
    output_score_jediswap: int
    output_score_ekubo: int
    output_components_jediswap: Dict[str, int]
    output_components_ekubo: Dict[str, int]
    proof_data: bytes  # Binary proof (mock for now)
    status: str


class LuminAIRService:
    """
    Service for generating STARK proofs of risk model execution
    
    Calls Rust binary with LuminAIR operator to generate real STARK proofs
    """
    
    def __init__(self):
        # Path to Rust binary (relative to backend directory)
        backend_dir = Path(__file__).parent.parent.parent
        self.binary_path = backend_dir / ".." / "operators" / "risk-scoring" / "target" / "release" / "risk_scoring_operator"
        self.binary_path = self.binary_path.resolve()
        
        if not self.binary_path.exists():
            logger.warning(f"LuminAIR binary not found at {self.binary_path}, falling back to mock mode")
            self.use_mock = True
        else:
            logger.info(f"LuminAIR Service initialized with binary: {self.binary_path}")
            self.use_mock = False
    
    async def generate_proof(
        self,
        jediswap_metrics: Dict[str, int],
        ekubo_metrics: Dict[str, int]
    ) -> ProofResult:
        """
        Generate STARK proof for risk scoring computation
        
        Args:
            jediswap_metrics: Protocol metrics for Jediswap
            ekubo_metrics: Protocol metrics for Ekubo
        
        Returns:
            ProofResult with proof hash and computed scores
        """
        logger.info("Generating STARK proof for risk scoring...")
        
        if self.use_mock:
            # Fallback to mock if binary not available
            return await self._generate_mock_proof(jediswap_metrics, ekubo_metrics)
        
        # Prepare input JSON
        input_data = {
            "jediswap_metrics": jediswap_metrics,
            "ekubo_metrics": ekubo_metrics
        }
        input_json = json.dumps(input_data)
        
        try:
            # Call Rust binary
            logger.info(f"Calling LuminAIR binary: {self.binary_path}")
            result = subprocess.run(
                [str(self.binary_path)],
                input=input_json.encode(),
                capture_output=True,
                timeout=300,  # 5 minute timeout
                check=True
            )
            
            # Parse output (JSON is at the end after log messages)
            output_lines = result.stdout.decode().strip().split('\n')
            # Find JSON output (last line or line containing '{')
            json_output = None
            for line in reversed(output_lines):
                if line.strip().startswith('{'):
                    json_output = line.strip()
                    break
            
            if not json_output:
                raise ValueError("No JSON output found in binary response")
            
            output_data = json.loads(json_output)
            
            # Read proof data from file
            proof_data_path = output_data["proof_data_path"]
            with open(proof_data_path, "rb") as f:
                proof_data = f.read()
            
            logger.info(f"Proof generated: {output_data['proof_hash'][:16]}...")
            logger.info(f"Jediswap risk: {output_data['jediswap_risk']}, Ekubo risk: {output_data['ekubo_risk']}")
            
            # Calculate components for compatibility (we can enhance this later)
            jediswap_components = self._calculate_risk_components(jediswap_metrics)
            ekubo_components = self._calculate_risk_components(ekubo_metrics)
            
            return ProofResult(
                proof_hash=output_data["proof_hash"],
                output_score_jediswap=output_data["jediswap_risk"],
                output_score_ekubo=output_data["ekubo_risk"],
                output_components_jediswap=jediswap_components,
                output_components_ekubo=ekubo_components,
                proof_data=proof_data,
                status="generated"
            )
            
        except subprocess.TimeoutExpired:
            logger.error("LuminAIR binary timed out after 5 minutes")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"LuminAIR binary failed: {e.stderr.decode() if e.stderr else 'Unknown error'}")
            # Fallback to mock
            logger.warning("Falling back to mock proof generation")
            return await self._generate_mock_proof(jediswap_metrics, ekubo_metrics)
        except Exception as e:
            logger.error(f"Error calling LuminAIR binary: {e}")
            # Fallback to mock
            logger.warning("Falling back to mock proof generation")
            return await self._generate_mock_proof(jediswap_metrics, ekubo_metrics)
    
    async def _generate_mock_proof(
        self,
        jediswap_metrics: Dict[str, int],
        ekubo_metrics: Dict[str, int]
    ) -> ProofResult:
        """Fallback mock proof generation"""
        import hashlib
        await asyncio.sleep(1)  # Simulate work
        
        jediswap_score, jediswap_components = self._calculate_risk_score(jediswap_metrics)
        ekubo_score, ekubo_components = self._calculate_risk_score(ekubo_metrics)
        
        proof_structure = {
            "version": "1.0.0-mock",
            "operator": "risk_scoring",
            "inputs": {"jediswap": jediswap_metrics, "ekubo": ekubo_metrics},
            "outputs": {
                "jediswap_score": jediswap_score,
                "ekubo_score": ekubo_score,
            }
        }
        proof_json = json.dumps(proof_structure, sort_keys=True)
        proof_hash = hashlib.sha256(proof_json.encode()).hexdigest()
        
        return ProofResult(
            proof_hash=f"0x{proof_hash}",
            output_score_jediswap=jediswap_score,
            output_score_ekubo=ekubo_score,
            output_components_jediswap=jediswap_components,
            output_components_ekubo=ekubo_components,
            proof_data=proof_json.encode(),
            status="generated-mock"
        )
    
    def _calculate_risk_score(
        self,
        metrics: Dict[str, int]
    ) -> tuple[int, Dict[str, int]]:
        """
        Calculate risk score using our Python reference model
        
        This matches our Cairo implementation:
        - util_component = (utilization / 10000) * 35
        - vol_component = (volatility / 10000) * 30
        - liq_component = (3 - liquidity) * 5
        - audit_component = (100 - audit_score) / 5
        - age_penalty = max(0, 10 - age_days / 100)
        - total = clamp(sum, 5, 95)
        """
        util = metrics["utilization"]
        vol = metrics["volatility"]
        liq = metrics["liquidity"]
        audit = metrics["audit_score"]
        age = metrics["age_days"]
        
        # Calculate components
        util_component = int((util / 10000) * 35)
        vol_component = int((vol / 10000) * 30)
        liq_component = (3 - liq) * 5
        audit_component = (100 - audit) // 5
        age_penalty = max(0, 10 - (age // 100))
        
        # Sum and clamp
        total = util_component + vol_component + liq_component + audit_component + age_penalty
        total_clamped = max(5, min(95, total))
        
        components = {
            "util_component": util_component,
            "vol_component": vol_component,
            "liq_component": liq_component,
            "audit_component": audit_component,
            "age_penalty": age_penalty,
            "total_unclamped": total,
            "total_clamped": total_clamped
        }
        
        return total_clamped, components
    
    def _calculate_risk_components(
        self,
        metrics: Dict[str, int]
    ) -> Dict[str, int]:
        """Calculate risk components for display (helper method)"""
        _, components = self._calculate_risk_score(metrics)
        return components
    
    async def verify_proof(
        self,
        proof_data: bytes
    ) -> bool:
        """
        Verify STARK proof locally
        
        Current: Basic validation
        Future: Call LuminAIR verifier
        """
        try:
            # Parse proof structure
            proof_json = json.loads(proof_data.decode())
            
            # Verify structure
            required_fields = ["version", "operator", "inputs", "outputs"]
            if not all(field in proof_json for field in required_fields):
                return False
            
            # Verify operator
            if proof_json["operator"] != "risk_scoring":
                return False
            
            # Recalculate and verify scores match
            for protocol in ["jediswap", "ekubo"]:
                metrics = proof_json["inputs"][protocol]
                expected_score = proof_json["outputs"][f"{protocol}_score"]
                
                actual_score, _ = self._calculate_risk_score(metrics)
                
                if actual_score != expected_score:
                    logger.error(f"Score mismatch for {protocol}: {actual_score} != {expected_score}")
                    return False
            
            logger.info("Proof verification successful")
            return True
            
        except Exception as e:
            logger.error(f"Proof verification failed: {e}")
            return False


# Singleton instance
_luminair_service_instance = None


def get_luminair_service() -> LuminAIRService:
    """Get singleton LuminAIR service instance"""
    global _luminair_service_instance
    if _luminair_service_instance is None:
        _luminair_service_instance = LuminAIRService()
    return _luminair_service_instance

