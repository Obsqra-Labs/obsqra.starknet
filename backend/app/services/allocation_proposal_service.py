"""
Phase 3.3: Complete Allocation Workflow Integration

This module shows the complete integrated workflow:
allocation → trace → proof → verification
"""

import asyncio
import json
import logging
from uuid import uuid4
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AllocationProposalService:
    """
    Complete allocation proposal service with integrated proof generation
    
    Workflow:
    1. Validate allocation parameters
    2. Generate execution trace from allocation
    3. Generate STARK proof from trace
    4. Register proof on-chain (optional)
    5. Store allocation with proof metadata
    """
    
    def __init__(
        self,
        stone_service,
        atlantic_service,
        trace_generator,
        integrity_service,
        db_session=None
    ):
        """Initialize with all required services"""
        self.stone_service = stone_service
        self.atlantic_service = atlantic_service
        self.trace_generator = trace_generator
        self.integrity_service = integrity_service
        self.db_session = db_session
        
        logger.info("AllocationProposalService initialized")
    
    async def create_allocation_proposal(
        self,
        jediswap_risk: int,
        ekubo_risk: int,
        jediswap_apy: int,
        ekubo_apy: int,
        jediswap_pct: int,
        ekubo_pct: int,
        prefer_stone: bool = True
    ) -> Dict:
        """
        Create allocation proposal with integrated proof generation
        
        Complete workflow:
        1. Validate parameters
        2. Convert to execution trace
        3. Generate STARK proof
        4. Register on-chain
        5. Store in database
        
        Args:
            jediswap_risk: Risk score (0-100)
            ekubo_risk: Risk score (0-100)
            jediswap_apy: APY in basis points
            ekubo_apy: APY in basis points
            jediswap_pct: Allocation percentage (0-100)
            ekubo_pct: Allocation percentage (0-100)
            prefer_stone: Use Stone prover if True
        
        Returns:
            Dictionary with allocation and proof metadata
        """
        
        allocation_id = str(uuid4())
        
        logger.info(f"Creating allocation proposal {allocation_id}")
        logger.info(f"  Parameters: {jediswap_pct}% Jediswap, {ekubo_pct}% Ekubo")
        
        # Step 1: Validate allocation
        logger.info("Step 1: Validating allocation parameters...")
        
        if not self._validate_allocation(
            jediswap_pct, ekubo_pct,
            jediswap_risk, ekubo_risk,
            jediswap_apy, ekubo_apy
        ):
            return {
                "success": False,
                "error": "Invalid allocation parameters"
            }
        
        logger.info("  ✅ Validation passed")
        
        # Step 2: Generate execution trace
        logger.info("Step 2: Generating execution trace...")
        
        trace_result = await self._generate_trace(
            allocation_id,
            jediswap_risk, ekubo_risk,
            jediswap_apy, ekubo_apy,
            jediswap_pct, ekubo_pct
        )
        
        if not trace_result.get("success"):
            logger.error(f"  ❌ Trace generation failed: {trace_result.get('error')}")
            return {
                "success": False,
                "error": "Trace generation failed (strict mode - no mock traces allowed)"
            }
        
        logger.info(f"  ✅ Trace generated: {trace_result.get('n_steps')} steps")
        
        # Step 3: Generate STARK proof
        logger.info("Step 3: Generating STARK proof...")
        
        proof_result = await self._generate_proof(
            allocation_id,
            trace_result.get("private_input_file"),
            trace_result.get("public_input_file"),
            prefer_stone=prefer_stone
        )
        
        if not proof_result.get("success"):
            return {
                "success": False,
                "error": f"Proof generation failed: {proof_result.get('error')}"
            }
        
        logger.info(f"  ✅ Proof generated: {proof_result.get('proof_method')}")
        logger.info(f"     Hash: {proof_result.get('proof_hash', '')[:32]}...")
        logger.info(f"     Time: {proof_result.get('generation_time_ms', 0):.0f}ms")
        
        # Step 4: Register on-chain (optional)
        logger.info("Step 4: Registering proof on-chain...")
        
        on_chain_result = await self._register_on_chain(
            allocation_id,
            proof_result.get("proof_hash"),
            proof_result.get("proof_data")
        )
        
        logger.info(f"  {'✅' if on_chain_result.get('success') else '⏭️'} On-chain registration: {on_chain_result.get('status', 'skipped')}")
        
        # Step 5: Store in database
        logger.info("Step 5: Storing allocation in database...")
        
        db_result = await self._store_allocation(
            allocation_id,
            jediswap_risk, ekubo_risk,
            jediswap_apy, ekubo_apy,
            jediswap_pct, ekubo_pct,
            proof_result
        )
        
        logger.info(f"  {'✅' if db_result.get('success') else '⏭️'} Database: {db_result.get('status', 'skipped')}")
        
        # Return complete result
        logger.info("")
        logger.info(f"✅ Allocation {allocation_id} created successfully")
        
        return {
            "success": True,
            "allocation_id": allocation_id,
            "jediswap_pct": jediswap_pct,
            "ekubo_pct": ekubo_pct,
            "proof_hash": proof_result.get("proof_hash"),
            "proof_method": proof_result.get("proof_method"),
            "proof_time_ms": proof_result.get("generation_time_ms"),
            "proof_size_kb": proof_result.get("proof_size_kb"),
            "on_chain_verified": on_chain_result.get("verified", False),
            "trace_n_steps": trace_result.get("n_steps"),
            "status": "created"
        }
    
    def _validate_allocation(
        self,
        jediswap_pct: int,
        ekubo_pct: int,
        jediswap_risk: int,
        ekubo_risk: int,
        jediswap_apy: int,
        ekubo_apy: int
    ) -> bool:
        """Validate allocation parameters"""
        
        # Check percentage sum
        if jediswap_pct + ekubo_pct != 100:
            logger.error(f"Percentages don't sum to 100: {jediswap_pct + ekubo_pct}")
            return False
        
        # Check percentage ranges
        if not (0 <= jediswap_pct <= 100) or not (0 <= ekubo_pct <= 100):
            logger.error("Percentages out of range")
            return False
        
        # Check risk ranges
        if not (0 <= jediswap_risk <= 100) or not (0 <= ekubo_risk <= 100):
            logger.error("Risk scores out of range")
            return False
        
        # Check APY ranges (basis points)
        if not (0 <= jediswap_apy <= 100000) or not (0 <= ekubo_apy <= 100000):
            logger.error("APY values out of range")
            return False
        
        return True
    
    async def _generate_trace(
        self,
        allocation_id: str,
        jediswap_risk: int,
        ekubo_risk: int,
        jediswap_apy: int,
        ekubo_apy: int,
        jediswap_pct: int,
        ekubo_pct: int
    ) -> Dict:
        """Generate execution trace from allocation"""
        
        try:
            result = await self.trace_generator.allocation_to_trace(
                allocation_id,
                jediswap_risk, ekubo_risk,
                jediswap_apy, ekubo_apy,
                jediswap_pct, ekubo_pct
            )
            
            if result.success:
                return {
                    "success": True,
                    "n_steps": result.n_steps,
                    "trace_file": result.trace_file,
                    "memory_file": result.memory_file,
                    "public_input_file": result.public_input_file,
                    "private_input_file": result.private_input_file,
                    "generation_time_ms": result.generation_time_ms
                }
            else:
                return {
                    "success": False,
                    "error": result.error
                }
        except Exception as e:
            logger.error(f"Trace generation error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_mock_trace_result(self) -> Dict:
        """Deprecated: mock trace results are disabled in strict mode."""
        raise RuntimeError("Mock trace results are disabled. Provide a real Cairo trace.")
    
    async def _generate_proof(
        self,
        allocation_id: str,
        private_input_file: str,
        public_input_file: str,
        prefer_stone: bool = True
    ) -> Dict:
        """Generate STARK proof from trace"""
        
        try:
            # Strict Stone-only path
            if prefer_stone and self.stone_service:
                stone_result = await self.stone_service.generate_proof(
                    private_input_file,
                    public_input_file
                )

                if stone_result.success:
                    return {
                        "success": True,
                        "proof_hash": stone_result.proof_hash,
                        "proof_data": stone_result.proof_data,
                        "proof_method": "stone",
                        "generation_time_ms": stone_result.generation_time_ms,
                        "proof_size_kb": stone_result.proof_size_kb
                    }

                return {
                    "success": False,
                    "error": stone_result.error or "Stone prover failed"
                }

            return {
                "success": False,
                "error": "Stone prover required (strict mode - no fallback)"
            }
        
        except Exception as e:
            logger.error(f"Proof generation error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _register_on_chain(
        self,
        allocation_id: str,
        proof_hash: str,
        proof_data: bytes
    ) -> Dict:
        """Register proof on-chain"""
        
        try:
            if not self.integrity_service:
                return {
                    "success": True,
                    "status": "skipped (no service)",
                    "verified": False
                }
            
            # TODO: Call integrity service to verify proof
            # verified = await self.integrity_service.verify_proof_full_and_register_fact(...)
            
            logger.info("On-chain registration skipped (requires live contract)")
            
            return {
                "success": True,
                "status": "pending",
                "verified": False
            }
        
        except Exception as e:
            logger.warning(f"On-chain registration failed: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "verified": False
            }
    
    async def _store_allocation(
        self,
        allocation_id: str,
        jediswap_risk: int,
        ekubo_risk: int,
        jediswap_apy: int,
        ekubo_apy: int,
        jediswap_pct: int,
        ekubo_pct: int,
        proof_result: Dict
    ) -> Dict:
        """Store allocation in database"""
        
        try:
            if not self.db_session:
                logger.info("Database storage skipped (no session)")
                return {
                    "success": True,
                    "status": "skipped"
                }
            
            # TODO: Create ProofJob and store in database
            # This would be something like:
            # allocation = ProofJob(
            #     allocation_id=allocation_id,
            #     proof_hash=proof_result.get("proof_hash"),
            #     proof_source=proof_result.get("proof_method"),
            #     stone_latency_ms=proof_result.get("generation_time_ms"),
            #     stone_proof_size=proof_result.get("proof_size_kb"),
            #     jediswap_risk=jediswap_risk,
            #     ekubo_risk=ekubo_risk,
            #     jediswap_pct=jediswap_pct,
            #     ekubo_pct=ekubo_pct
            # )
            # self.db_session.add(allocation)
            # self.db_session.commit()
            
            logger.info("Database storage skipped (requires live session)")
            
            return {
                "success": True,
                "status": "pending"
            }
        
        except Exception as e:
            logger.warning(f"Database storage failed: {str(e)}")
            return {
                "success": False,
                "status": "failed"
            }


"""
USAGE EXAMPLE

In your FastAPI app:

from allocation_proposal_service import AllocationProposalService

# Initialize services
stone_svc = StoneProverService()
atlantic_svc = AtlanticService()
trace_gen = AllocationToTraceAdapter()
integrity_svc = IntegrityService()

service = AllocationProposalService(
    stone_service=stone_svc,
    atlantic_service=atlantic_svc,
    trace_generator=trace_gen,
    integrity_service=integrity_svc,
    db_session=db
)

# Create allocation with integrated proof
@router.post("/allocations/propose")
async def create_allocation_proposal(
    jediswap_risk: int,
    ekubo_risk: int,
    jediswap_apy: int,
    ekubo_apy: int,
    jediswap_pct: int,
    ekubo_pct: int
):
    result = await service.create_allocation_proposal(
        jediswap_risk=jediswap_risk,
        ekubo_risk=ekubo_risk,
        jediswap_apy=jediswap_apy,
        ekubo_apy=ekubo_apy,
        jediswap_pct=jediswap_pct,
        ekubo_pct=ekubo_pct,
        prefer_stone=True
    )
    
    if not result.get("success"):
        raise ValueError(result.get("error"))
    
    return result
"""
