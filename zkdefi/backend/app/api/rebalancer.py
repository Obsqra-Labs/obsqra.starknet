"""
Agent Rebalancer API endpoints.

Endpoints:
- /api/v1/zkdefi/rebalancer/analyze - Analyze portfolio
- /api/v1/zkdefi/rebalancer/propose - Create rebalancing proposal
- /api/v1/zkdefi/rebalancer/check - Run zkML gate checks
- /api/v1/zkdefi/rebalancer/prepare - Prepare execution
- /api/v1/zkdefi/rebalancer/execute - Execute rebalancing
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.agent_rebalancer import get_rebalancer

router = APIRouter()


# ==================== Request Models ====================

class AnalyzeRequest(BaseModel):
    """Request to analyze portfolio."""
    user_address: str
    positions: dict[str, int]  # protocol_id (as string) -> amount


class ProposeRequest(BaseModel):
    """Request to propose rebalancing."""
    user_address: str
    from_protocol: int
    to_protocol: int
    amount: int
    reason: str = "Risk optimization"


class CheckZkmlRequest(BaseModel):
    """Request to check zkML gates."""
    proposal_id: str
    portfolio_features: list[int]
    pool_id: str | None = None


class PrepareRequest(BaseModel):
    """Request to prepare execution."""
    proposal_id: str
    session_id: str


class ExecuteRequest(BaseModel):
    """Request to execute rebalancing."""
    proposal_id: str
    session_id: str


# ==================== Endpoints ====================

@router.post("/analyze")
async def analyze_portfolio(data: AnalyzeRequest):
    """
    Analyze portfolio and determine if rebalancing is needed.
    
    Returns risk assessment and rebalancing recommendation.
    """
    try:
        rebalancer = get_rebalancer()
        # Convert string keys to int
        positions = {int(k): v for k, v in data.positions.items()}
        result = await rebalancer.analyze_portfolio(
            user_address=data.user_address,
            positions=positions
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/propose")
async def propose_rebalance(data: ProposeRequest):
    """
    Create a rebalancing proposal.
    
    The proposal must pass zkML checks before execution.
    """
    try:
        rebalancer = get_rebalancer()
        proposal = await rebalancer.propose_rebalance(
            user_address=data.user_address,
            from_protocol=data.from_protocol,
            to_protocol=data.to_protocol,
            amount=data.amount,
            reason=data.reason
        )
        return proposal.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check")
async def check_zkml_gates(data: CheckZkmlRequest):
    """
    Run zkML models to gate the rebalancing proposal.
    
    Both risk score and anomaly detection must pass.
    """
    try:
        rebalancer = get_rebalancer()
        result = await rebalancer.check_zkml_gates(
            proposal_id=data.proposal_id,
            portfolio_features=data.portfolio_features,
            pool_id=data.pool_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prepare")
async def prepare_execution(data: PrepareRequest):
    """
    Prepare the rebalancing execution.
    
    Validates session key and generates execution proofs.
    """
    try:
        rebalancer = get_rebalancer()
        result = await rebalancer.prepare_execution(
            proposal_id=data.proposal_id,
            session_id=data.session_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
async def execute_rebalance(data: ExecuteRequest):
    """
    Execute the rebalancing.
    
    Requires valid session key and all proofs.
    """
    try:
        rebalancer = get_rebalancer()
        result = await rebalancer.execute_rebalance(
            proposal_id=data.proposal_id,
            session_id=data.session_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposal/{proposal_id}")
async def get_proposal(proposal_id: str):
    """Get proposal by ID."""
    rebalancer = get_rebalancer()
    proposal = rebalancer.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.get("/proposals/{user_address}")
async def get_user_proposals(user_address: str):
    """Get all proposals for a user."""
    rebalancer = get_rebalancer()
    proposals = rebalancer.get_user_proposals(user_address)
    return {
        "user_address": user_address,
        "proposals": proposals,
        "count": len(proposals)
    }
