"""
Agent Orchestrator API Routes
Endpoints for intent management, agent reputation, and policy marketplace
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

from app.services.agent_orchestrator_service import (
    get_agent_orchestrator_service,
    IntentType,
    IntentStatus,
)

router = APIRouter(prefix="/agent-orchestrator", tags=["Agent Orchestrator"])


# ============================================================================
# Response Models
# ============================================================================

class ContractInfoResponse(BaseModel):
    """Contract information response"""
    contract_address: str
    version: str
    contract_version: int
    owner: str
    network: str = "sepolia"


class OrchestratorStatsResponse(BaseModel):
    """Orchestrator statistics response"""
    contract_address: str
    intent_count: int
    agent_count: int
    policy_count: int
    execution_count: int
    status: str


class AgentReputationResponse(BaseModel):
    """Agent reputation response"""
    agent: str
    is_registered: bool
    total_executions: Optional[int] = None
    successful_executions: Optional[int] = None
    failed_executions: Optional[int] = None
    reputation_score: Optional[int] = None
    is_active: Optional[bool] = None


class PolicyResponse(BaseModel):
    """Policy response"""
    policy_hash: str
    is_approved: bool
    name: Optional[str] = None
    creator: Optional[str] = None


class IntentTypeEnum(str, Enum):
    """Intent types for API"""
    maximize_yield = "maximize_yield"
    minimize_risk = "minimize_risk"
    balanced_growth = "balanced_growth"
    custom_policy = "custom_policy"


class ConstraintSetRequest(BaseModel):
    """Constraint set for intent submission"""
    max_risk_score: int = Field(ge=0, le=100, default=50)
    min_confidence: int = Field(ge=0, le=100, default=80)
    max_drawdown_bps: int = Field(ge=0, le=10000, default=500)  # 5%
    allowed_protocols: int = Field(ge=0, default=0xFFFF)  # All
    max_single_position_bps: int = Field(ge=0, le=10000, default=2000)  # 20%
    require_proof: bool = True


class IntentSubmissionRequest(BaseModel):
    """Request to submit a new intent"""
    goal: IntentTypeEnum
    constraints: ConstraintSetRequest
    policy_hash: str = "0x0"  # No specific policy
    expires_in_seconds: int = Field(ge=3600, le=2592000, default=604800)  # 1 week default


class IntentResponse(BaseModel):
    """Intent response"""
    intent_id: str
    owner: str
    goal: str
    status: str
    constraints: Dict[str, Any]
    policy_hash: str
    created_at: int
    expires_at: int
    execution_count: int


# ============================================================================
# Contract Info Endpoints
# ============================================================================

@router.get("/info", response_model=ContractInfoResponse)
async def get_contract_info():
    """Get AgentOrchestrator contract information"""
    try:
        service = await get_agent_orchestrator_service()
        version = await service.get_version()
        contract_version = await service.get_contract_version()
        owner = await service.get_owner()
        
        return ContractInfoResponse(
            contract_address=service.contract_address,
            version=version,
            contract_version=contract_version,
            owner=owner
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get contract info: {str(e)}")


@router.get("/stats", response_model=OrchestratorStatsResponse)
async def get_stats():
    """Get overall orchestrator statistics"""
    try:
        service = await get_agent_orchestrator_service()
        stats = await service.get_stats()
        
        if stats.get("status") == "error":
            raise HTTPException(status_code=500, detail=stats.get("error"))
        
        return OrchestratorStatsResponse(**stats)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for the orchestrator service"""
    try:
        service = await get_agent_orchestrator_service()
        version = await service.get_version()
        return {
            "status": "healthy",
            "contract_address": service.contract_address,
            "version": version
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# ============================================================================
# Agent Endpoints
# ============================================================================

@router.get("/agents/{agent_address}", response_model=AgentReputationResponse)
async def get_agent_reputation(agent_address: str):
    """Get reputation for a specific agent"""
    try:
        service = await get_agent_orchestrator_service()
        reputation = await service.get_agent_reputation(agent_address)
        
        if reputation is None:
            raise HTTPException(status_code=404, detail="Agent not registered")
        
        return AgentReputationResponse(**reputation)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent reputation: {str(e)}")


@router.get("/agents/{agent_address}/check")
async def check_agent_registration(agent_address: str):
    """Check if an address is a registered agent"""
    try:
        service = await get_agent_orchestrator_service()
        is_registered = await service.is_registered_agent(agent_address)
        
        return {
            "agent": agent_address,
            "is_registered": is_registered
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check agent: {str(e)}")


# ============================================================================
# Policy Endpoints
# ============================================================================

@router.get("/policies/{policy_hash}", response_model=PolicyResponse)
async def get_policy(policy_hash: str):
    """Get policy details"""
    try:
        service = await get_agent_orchestrator_service()
        policy = await service.get_policy(policy_hash)
        
        return PolicyResponse(**policy)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get policy: {str(e)}")


@router.get("/policies/{policy_hash}/check")
async def check_policy_approval(policy_hash: str):
    """Check if a policy is approved"""
    try:
        service = await get_agent_orchestrator_service()
        is_approved = await service.is_policy_approved(policy_hash)
        
        return {
            "policy_hash": policy_hash,
            "is_approved": is_approved
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check policy: {str(e)}")


# ============================================================================
# Intent Endpoints (placeholder for write operations)
# ============================================================================

@router.get("/intents/user/{user_address}")
async def get_user_intents(
    user_address: str,
    limit: int = Query(default=10, ge=1, le=100)
):
    """Get intents for a user"""
    try:
        service = await get_agent_orchestrator_service()
        intents = await service.get_user_intents(user_address, limit)
        
        return {
            "user": user_address,
            "intents": intents,
            "count": len(intents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user intents: {str(e)}")


@router.post("/intents/preview")
async def preview_intent_submission(request: IntentSubmissionRequest):
    """
    Preview intent submission (validation only, no on-chain transaction)
    
    Actual submission requires wallet signature via frontend
    """
    try:
        # Validate constraints
        constraints = request.constraints
        
        # Calculate constraint hash for preview
        import hashlib
        constraint_str = f"{constraints.max_risk_score}:{constraints.min_confidence}:{constraints.max_drawdown_bps}"
        constraint_hash = hashlib.sha256(constraint_str.encode()).hexdigest()[:16]
        
        return {
            "valid": True,
            "preview": {
                "goal": request.goal.value,
                "policy_hash": request.policy_hash,
                "expires_in_seconds": request.expires_in_seconds,
                "constraints": constraints.dict(),
                "constraint_preview_hash": f"0x{constraint_hash}"
            },
            "message": "Intent is valid. Submit via wallet to create on-chain."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid intent: {str(e)}")


# ============================================================================
# Available Policies (curated list)
# ============================================================================

@router.get("/policies/available/list")
async def list_available_policies():
    """
    Get list of pre-built, audited policies available for use
    
    These are curated policies that users can select for their intents
    """
    # Hardcoded for now - in production, these would come from the contract
    policies = [
        {
            "name": "Conservative DeFi",
            "policy_hash": "0x0",  # No policy = default conservative
            "description": "Low-risk yield farming with strict position limits",
            "risk_level": "low",
            "features": ["max 20% single position", "stablecoin focus", "audited protocols only"]
        },
        {
            "name": "Balanced Growth",
            "policy_hash": "0x1",
            "description": "Balanced risk/reward with diversified exposure",
            "risk_level": "medium",
            "features": ["50/50 stable/volatile", "auto-rebalancing", "proof-gated"]
        },
        {
            "name": "Aggressive Yield",
            "policy_hash": "0x2",
            "description": "Higher risk strategies for maximum returns",
            "risk_level": "high",
            "features": ["leverage enabled", "volatile assets", "requires proof verification"]
        }
    ]
    
    return {
        "policies": policies,
        "count": len(policies),
        "note": "Custom policies require approval from contract owner"
    }
