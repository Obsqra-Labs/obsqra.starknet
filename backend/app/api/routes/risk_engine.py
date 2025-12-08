"""
Risk Engine API endpoints for on-chain risk calculations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging
from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class RiskMetricsRequest(BaseModel):
    """Request to calculate risk score"""
    utilization: int = Field(..., ge=0, le=10000, description="Utilization in basis points")
    volatility: int = Field(..., ge=0, le=10000, description="Volatility in basis points")
    liquidity: int = Field(..., ge=0, le=3, description="Liquidity category (0-3)")
    audit_score: int = Field(..., ge=0, le=100, description="Audit score (0-100)")
    age_days: int = Field(..., ge=0, description="Protocol age in days")


class AllocationRequest(BaseModel):
    """Request to calculate allocation"""
    jediswap_risk: int = Field(..., ge=5, le=95, description="JediSwap risk score")
    ekubo_risk: int = Field(..., ge=5, le=95, description="Ekubo risk score")
    jediswap_apy: int = Field(..., ge=0, description="JediSwap APY in basis points")
    ekubo_apy: int = Field(..., ge=0, description="Ekubo APY in basis points")


class RiskScoreResponse(BaseModel):
    """Risk score response"""
    score: int
    category: str
    description: str


class AllocationResponse(BaseModel):
    """Allocation response"""
    jediswap_pct: int
    ekubo_pct: int


@router.post("/calculate-risk", response_model=RiskScoreResponse, tags=["Risk Engine"])
async def calculate_risk_score(request: RiskMetricsRequest):
    """
    Calculate risk score for a protocol via Risk Engine contract
    
    Returns the calculated risk score (5-95) from on-chain Cairo contract
    """
    try:
        logger.info(f"📊 Calculating risk score via contract: {request.dict()}")
        
        # Initialize RPC client
        rpc_client = FullNodeClient(node_url=settings.STARKNET_RPC_URL)
        
        # Create contract instance (address must be int)
        contract = await Contract.from_address(
            address=int(settings.RISK_ENGINE_ADDRESS, 16),
            provider=rpc_client
        )
        
        # Call calculate_risk_score on the contract
        result = await contract.functions["calculate_risk_score"].call(
            request.utilization,
            request.volatility,
            request.liquidity,
            request.audit_score,
            request.age_days
        )
        
        # Extract risk_score from result (felt252)
        risk_score = int(result[0])
        
        # Determine category
        if risk_score < 30:
            category = "low"
            description = "Low risk protocol - Safe for allocation"
        elif risk_score < 70:
            category = "medium"
            description = "Medium risk - Consider allocation limits"
        else:
            category = "high"
            description = "High risk - Use small allocation only"
        
        logger.info(f"✅ Risk score from contract: {risk_score} ({category})")
        
        return RiskScoreResponse(
            score=risk_score,
            category=category,
            description=description
        )
        
    except Exception as e:
        logger.error(f"❌ Risk calculation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Risk calculation failed: {str(e)}"
        )


@router.post("/calculate-allocation", response_model=AllocationResponse, tags=["Risk Engine"])
async def calculate_allocation(request: AllocationRequest):
    """
    Calculate optimal allocation across JediSwap and Ekubo via Risk Engine contract
    
    Returns allocation percentages in basis points (10000 = 100%) from on-chain Cairo contract
    
    NOTE: This is the legacy endpoint. For full on-chain orchestration, use /orchestrate-allocation
    """
    try:
        logger.info(f"📊 Calculating allocation via contract: {request.dict()}")
        
        # Initialize RPC client
        rpc_client = FullNodeClient(node_url=settings.STARKNET_RPC_URL)
        
        # Create contract instance (address must be int)
        contract = await Contract.from_address(
            address=int(settings.RISK_ENGINE_ADDRESS, 16),
            provider=rpc_client
        )
        
        # Call calculate_allocation on the contract
        # Note: Contract expects 3 protocols (nostra/zklend/ekubo)
        # We map jediswap -> nostra and set zklend to 0 (not used)
        result = await contract.functions["calculate_allocation"].call(
            request.jediswap_risk,  # nostra_risk (mapped from jediswap)
            0,                       # zklend_risk (not used, set to 0)
            request.ekubo_risk,      # ekubo_risk
            request.jediswap_apy,    # nostra_apy (mapped from jediswap)
            0,                       # zklend_apy (not used, set to 0)
            request.ekubo_apy        # ekubo_apy
        )
        
        # Extract allocation percentages from contract result
        # Contract returns ((nostra_pct, zklend_pct, ekubo_pct),) - nested tuple
        # We map nostra_pct -> jediswap_pct and ignore zklend_pct
        allocation_tuple = result[0]  # Get inner tuple
        jediswap_pct = int(allocation_tuple[0])  # nostra_pct maps to jediswap
        ekubo_pct = int(allocation_tuple[2])      # ekubo_pct
        
        logger.info(f"✅ Allocation from contract: JediSwap {jediswap_pct} bps, Ekubo {ekubo_pct} bps")
        
        return AllocationResponse(
            jediswap_pct=jediswap_pct,
            ekubo_pct=ekubo_pct
        )
        
    except Exception as e:
        logger.error(f"❌ Allocation calculation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Allocation calculation failed: {str(e)}"
        )


class OrchestrationRequest(BaseModel):
    """Request for full on-chain orchestration"""
    jediswap_metrics: RiskMetricsRequest = Field(..., description="JediSwap protocol metrics")
    ekubo_metrics: RiskMetricsRequest = Field(..., description="Ekubo protocol metrics")


class OrchestrationResponse(BaseModel):
    """Response from orchestration - read-only decision data"""
    decision_id: int
    block_number: int
    timestamp: int
    jediswap_pct: int
    ekubo_pct: int
    jediswap_risk: int
    ekubo_risk: int
    jediswap_apy: int
    ekubo_apy: int
    rationale_hash: str
    strategy_router_tx: str
    message: str


@router.post("/orchestrate-allocation", response_model=OrchestrationResponse, tags=["Risk Engine"])
async def orchestrate_allocation(request: OrchestrationRequest):
    """
    Backend-driven full on-chain orchestration: RiskEngine calculates, validates, and executes allocation
    
    Uses starknet.py to properly serialize Cairo structs, ensuring 100% auditable flow.
    
    This endpoint triggers the complete on-chain flow:
    1. Calculate risk scores (on-chain)
    2. Query protocol APY (on-chain)  
    3. Calculate allocation (on-chain)
    4. Validate with DAO constraints (on-chain)
    5. Execute on StrategyRouter (on-chain)
    6. Emit audit trail events (on-chain)
    
    NOTE: Since propose_and_execute_allocation is an invoke operation, 
    this endpoint provides a read view of the decision after it's been executed on-chain.
    The actual invoke should be called from the frontend with the user's wallet.
    For MVP, this returns the latest decision from the contract.
    """
    try:
        logger.info(f"🤖 Orchestration request received:")
        logger.info(f"   JediSwap: util={request.jediswap_metrics.utilization}, vol={request.jediswap_metrics.volatility}, "
                   f"liq={request.jediswap_metrics.liquidity}, audit={request.jediswap_metrics.audit_score}, "
                   f"age={request.jediswap_metrics.age_days}")
        logger.info(f"   Ekubo: util={request.ekubo_metrics.utilization}, vol={request.ekubo_metrics.volatility}, "
                   f"liq={request.ekubo_metrics.liquidity}, audit={request.ekubo_metrics.audit_score}, "
                   f"age={request.ekubo_metrics.age_days}")
        
        # Initialize RPC client
        rpc_client = FullNodeClient(node_url=settings.STARKNET_RPC_URL)
        
        # Load Risk Engine contract
        contract = await Contract.from_address(
            address=int(settings.RISK_ENGINE_ADDRESS, 16),
            provider=rpc_client
        )
        
        # ===== FOR MVP =====
        # Since propose_and_execute_allocation is an INVOKE (write operation),
        # it must be called from the frontend with the user's wallet account.
        # This backend endpoint can:
        # 1. Validate the metrics (done above via Pydantic)
        # 2. Call the CONTRACT VIEW to get the latest decision
        # 3. Return that decision to the frontend for display
        
        logger.info("📖 Fetching latest decision from RiskEngine contract (read-only)...")
        
        # Get decision count (read operation)
        decision_count_result = await contract.functions["get_decision_count"].call()
        decision_count = int(decision_count_result[0]) if decision_count_result else 0
        
        logger.info(f"📊 Total decisions on-chain: {decision_count}")
        
        if decision_count > 0:
            # Get the latest decision (read operation)
            latest_decision_result = await contract.functions["get_decision"].call(decision_count)
            decision_data = latest_decision_result[0] if latest_decision_result else None
            
            if decision_data:
                logger.info(f"✅ Retrieved latest decision #{decision_count}:")
                logger.info(f"   JediSwap: {int(decision_data.jediswap_pct)} bps")
                logger.info(f"   Ekubo: {int(decision_data.ekubo_pct)} bps")
                logger.info(f"   Block: {int(decision_data.block_number)}")
                
                return OrchestrationResponse(
                    decision_id=int(decision_data.decision_id),
                    block_number=int(decision_data.block_number),
                    timestamp=int(decision_data.timestamp),
                    jediswap_pct=int(decision_data.jediswap_pct),
                    ekubo_pct=int(decision_data.ekubo_pct),
                    jediswap_risk=int(decision_data.jediswap_risk),
                    ekubo_risk=int(decision_data.ekubo_risk),
                    jediswap_apy=int(decision_data.jediswap_apy),
                    ekubo_apy=int(decision_data.ekubo_apy),
                    rationale_hash=str(decision_data.rationale_hash),
                    strategy_router_tx=str(decision_data.strategy_router_tx),
                    message="Latest decision retrieved from on-chain"
                )
        
        logger.warning("⚠️ No decisions found on-chain yet")
        raise HTTPException(
            status_code=404,
            detail="No orchestration decisions found on-chain. "
                   "Frontend must first call propose_and_execute_allocation via user wallet."
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ Orchestration failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Orchestration failed: {str(e)}"
        )
