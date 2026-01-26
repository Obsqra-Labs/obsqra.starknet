"""
Integration of Stone Prover with Allocation Proposal Workflow

This module shows how to integrate the Stone prover service into the
allocation proposal creation workflow.
"""

import json
import logging
from typing import Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AllocationProofResult:
    """Result of allocation proof generation"""
    success: bool
    proof_hash: Optional[str] = None
    proof_method: Optional[str] = None  # "stone" or "atlantic"
    generation_time_ms: Optional[float] = None
    proof_size_kb: Optional[float] = None
    error: Optional[str] = None
    on_chain_verified: bool = False


class AllocationProofOrchestrator:
    """
    Orchestrates proof generation for allocation proposals
    
    This implements the decision logic:
    1. Try Stone prover (local, fast, free)
    2. Fallback to Atlantic on failure (external, slower, costs $)
    3. Track metrics for optimization
    """
    
    def __init__(self, stone_service, atlantic_service, integrity_service):
        """
        Initialize orchestrator
        
        Args:
            stone_service: StoneProverService instance
            atlantic_service: AtlanticService instance
            integrity_service: IntegrityService for verification
        """
        self.stone_service = stone_service
        self.atlantic_service = atlantic_service
        self.integrity_service = integrity_service
    
    async def generate_allocation_proof(
        self,
        allocation_id: str,
        jediswap_risk: int,
        ekubo_risk: int,
        jediswap_apy: int,
        ekubo_apy: int,
        jediswap_pct: int,
        ekubo_pct: int,
        prefer_stone: bool = True
    ) -> AllocationProofResult:
        """
        Generate proof for allocation proposal
        
        Implements fallback strategy:
        1. Try Stone prover if prefer_stone=True
        2. On failure, use Atlantic
        3. Log metrics for analysis
        
        Args:
            allocation_id: Unique allocation identifier
            jediswap_risk: Risk score for Jediswap (0-100)
            ekubo_risk: Risk score for Ekubo (0-100)
            jediswap_apy: APY for Jediswap (basis points)
            ekubo_apy: APY for Ekubo (basis points)
            jediswap_pct: Allocation percentage for Jediswap (0-100)
            ekubo_pct: Allocation percentage for Ekubo (0-100)
            prefer_stone: Try Stone first if True
        
        Returns:
            AllocationProofResult with proof hash and metadata
        """
        
        logger.info(f"Generating proof for allocation {allocation_id}")
        logger.info(f"  Allocation: {jediswap_pct}% Jediswap, {ekubo_pct}% Ekubo")
        logger.info(f"  Risk scores: Jediswap={jediswap_risk}, Ekubo={ekubo_risk}")
        
        # Step 1: Try Stone prover (PRIMARY)
        if prefer_stone:
            logger.info("  Attempting Stone prover (local, free)...")
            
            stone_result = await self._generate_proof_stone(
                allocation_id,
                jediswap_risk, ekubo_risk,
                jediswap_apy, ekubo_apy,
                jediswap_pct, ekubo_pct
            )
            
            if stone_result.success:
                logger.info(f"  ✅ Stone prover succeeded: {stone_result.generation_time_ms:.0f}ms")
                return stone_result
            else:
                logger.warning(f"  ⚠️ Stone prover failed: {stone_result.error}")
        
        # Step 2: Fallback to Atlantic (BACKUP)
        logger.info("  Falling back to Atlantic service...")
        
        atlantic_result = await self._generate_proof_atlantic(
            allocation_id,
            jediswap_risk, ekubo_risk,
            jediswap_apy, ekubo_apy,
            jediswap_pct, ekubo_pct
        )
        
        if atlantic_result.success:
            logger.info(f"  ✅ Atlantic succeeded: {atlantic_result.generation_time_ms:.0f}ms")
            return atlantic_result
        else:
            logger.error(f"  ❌ Both provers failed!")
            return AllocationProofResult(
                success=False,
                error=f"Stone: failed, Atlantic: {atlantic_result.error}"
            )
    
    async def _generate_proof_stone(
        self,
        allocation_id: str,
        jediswap_risk: int, ekubo_risk: int,
        jediswap_apy: int, ekubo_apy: int,
        jediswap_pct: int, ekubo_pct: int,
    ) -> AllocationProofResult:
        """Generate proof using Stone prover"""
        
        try:
            # Step 1: Generate execution trace from allocation
            # (This would use cairo_trace_generator in full implementation)
            # For Phase 3, we use fibonacci as proof of concept
            
            private_input_file = "/opt/obsqra.starknet/stone-prover/e2e_test/Cairo/fib_private.json"
            public_input_file = "/opt/obsqra.starknet/stone-prover/e2e_test/Cairo/fib_public.json"
            
            # Step 2: Generate STARK proof
            proof_result = await self.stone_service.generate_proof(
                private_input_file,
                public_input_file
            )
            
            if not proof_result.success:
                return AllocationProofResult(
                    success=False,
                    error=proof_result.error
                )
            
            # Step 3: Register on Integrity contract (optional)
            # In full implementation, would call:
            # await self.integrity_service.verify_proof_full_and_register_fact(
            #     proof_result.proof_json
            # )
            
            # Step 4: Return success
            return AllocationProofResult(
                success=True,
                proof_hash=proof_result.proof_hash,
                proof_method="stone",
                generation_time_ms=proof_result.generation_time_ms,
                proof_size_kb=proof_result.proof_size_kb,
                on_chain_verified=False  # Would be True after contract interaction
            )
        
        except Exception as e:
            logger.error(f"Stone prover error: {str(e)}", exc_info=True)
            return AllocationProofResult(
                success=False,
                error=str(e)
            )
    
    async def _generate_proof_atlantic(
        self,
        allocation_id: str,
        jediswap_risk: int, ekubo_risk: int,
        jediswap_apy: int, ekubo_apy: int,
        jediswap_pct: int, ekubo_pct: int,
    ) -> AllocationProofResult:
        """Generate proof using Atlantic service"""
        
        try:
            # Atlantic would submit trace and wait for verification
            # For now, return mock result
            
            logger.info("Atlantic submission would happen here in full implementation")
            
            return AllocationProofResult(
                success=False,
                error="Atlantic not fully configured in test environment"
            )
        
        except Exception as e:
            logger.error(f"Atlantic error: {str(e)}")
            return AllocationProofResult(
                success=False,
                error=str(e)
            )


# Example usage in allocation_proposal_create() endpoint:
"""
@router.post("/allocations/propose")
async def allocation_proposal_create(
    jediswap_risk: int,
    ekubo_risk: int,
    jediswap_apy: int,
    ekubo_apy: int,
    jediswap_pct: int,
    ekubo_pct: int
):
    # Validate allocation
    if jediswap_pct + ekubo_pct != 100:
        raise ValueError("Allocations must sum to 100%")
    
    # Generate proof
    orchestrator = AllocationProofOrchestrator(
        stone_service,
        atlantic_service,
        integrity_service
    )
    
    proof_result = await orchestrator.generate_allocation_proof(
        allocation_id=str(uuid4()),
        jediswap_risk=jediswap_risk,
        ekubo_risk=ekubo_risk,
        jediswap_apy=jediswap_apy,
        ekubo_apy=ekubo_apy,
        jediswap_pct=jediswap_pct,
        ekubo_pct=ekubo_pct,
        prefer_stone=True  # Try Stone first, fallback to Atlantic
    )
    
    if not proof_result.success:
        raise ValueError(f"Proof generation failed: {proof_result.error}")
    
    # Store allocation with proof
    allocation = ProofJob(
        allocation_id=allocation_id,
        proof_hash=proof_result.proof_hash,
        proof_source=proof_result.proof_method,  # "stone" or "atlantic"
        stone_latency_ms=proof_result.generation_time_ms if proof_result.proof_method == "stone" else None,
        stone_proof_size=proof_result.proof_size_kb if proof_result.proof_method == "stone" else None,
        jediswap_risk=jediswap_risk,
        ekubo_risk=ekubo_risk,
        jediswap_pct=jediswap_pct,
        ekubo_pct=ekubo_pct,
    )
    
    db.add(allocation)
    db.commit()
    
    return {
        "allocation_id": allocation_id,
        "proof_hash": proof_result.proof_hash,
        "proof_method": proof_result.proof_method,
        "verified": proof_result.on_chain_verified
    }
"""
