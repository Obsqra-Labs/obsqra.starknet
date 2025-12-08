"""
Risk Engine API endpoints for on-chain risk calculations
"""
import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import logging
from sqlalchemy.orm import Session
from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models import StarknetChainId
from app.config import get_settings
from app.db.session import get_db
from app.models import ProofJob, ProofStatus
from app.services.luminair_service import get_luminair_service
from app.workers.sharp_worker import submit_proof_to_sharp

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
    # Proof information
    proof_job_id: str = None
    proof_hash: str = None
    proof_status: str = None


@router.post("/orchestrate-allocation", response_model=OrchestrationResponse, tags=["Risk Engine"])
async def orchestrate_allocation(
    request: OrchestrationRequest,
    db: Session = Depends(get_db)
):
    """
    🤖 AI-Driven Orchestration: Backend executes verified allocation decision
    
    This is the CORE of verifiable AI:
    1. AI proposes allocation based on protocol metrics
    2. Generates STARK proof that decision respects constraints
    3. Backend EXECUTES the transaction on-chain
    4. Returns decision + proof for audit trail
    
    The backend signs and submits the transaction using its authorized account.
    This enables fully automated AI execution without user wallet interaction.
    """
    try:
        logger.info(f"🤖 AI Orchestration Starting...")
        logger.info(f"📊 JediSwap metrics: util={request.jediswap_metrics.utilization}, "
                   f"vol={request.jediswap_metrics.volatility}, liq={request.jediswap_metrics.liquidity}, "
                   f"audit={request.jediswap_metrics.audit_score}, age={request.jediswap_metrics.age_days}")
        logger.info(f"📊 Ekubo metrics: util={request.ekubo_metrics.utilization}, "
                   f"vol={request.ekubo_metrics.volatility}, liq={request.ekubo_metrics.liquidity}, "
                   f"audit={request.ekubo_metrics.audit_score}, age={request.ekubo_metrics.age_days}")
        
        # STEP 1: Generate STARK Proof
        logger.info(f"🔐 Generating STARK proof...")
        luminair = get_luminair_service()
        proof = await luminair.generate_proof(
            request.jediswap_metrics.dict(),
            request.ekubo_metrics.dict()
        )
        logger.info(f"✅ Proof generated: {proof.proof_hash[:32]}...")
        logger.info(f"   Jediswap risk: {proof.output_score_jediswap}")
        logger.info(f"   Ekubo risk: {proof.output_score_ekubo}")
        
        # STEP 2: Store proof in database
        proof_job = ProofJob(
            proof_hash=proof.proof_hash,
            status=ProofStatus.GENERATED,
            metrics={
                "jediswap": request.jediswap_metrics.dict(),
                "ekubo": request.ekubo_metrics.dict(),
                "jediswap_risk": proof.output_score_jediswap,
                "ekubo_risk": proof.output_score_ekubo
            },
            proof_data=proof.proof_data
        )
        db.add(proof_job)
        db.commit()
        db.refresh(proof_job)
        logger.info(f"💾 Proof stored in database (ID: {proof_job.id})")
        
        # Validate backend wallet is configured
        if not settings.BACKEND_WALLET_PRIVATE_KEY or not settings.BACKEND_WALLET_ADDRESS:
            raise HTTPException(
                status_code=500,
                detail="Backend wallet not configured. Set BACKEND_WALLET_PRIVATE_KEY in .env"
            )
        
        # Initialize RPC client
        rpc_client = FullNodeClient(node_url=settings.STARKNET_RPC_URL)
        
        # Create backend account (AI orchestrator account)
        key_pair = KeyPair.from_private_key(int(settings.BACKEND_WALLET_PRIVATE_KEY, 16))
        account = Account(
            address=int(settings.BACKEND_WALLET_ADDRESS, 16),
            client=rpc_client,
            key_pair=key_pair,
            chain=StarknetChainId.SEPOLIA
        )
        
        logger.info(f"✅ Backend account initialized: {settings.BACKEND_WALLET_ADDRESS}")
        
        # Load Risk Engine contract with the account (for invoke operations)
        contract = await Contract.from_address(
            address=int(settings.RISK_ENGINE_ADDRESS, 16),
            provider=account
        )
        
        # Prepare protocol metrics as Python dicts (starknet.py maps to Cairo structs)
        jediswap_metrics = {
            'utilization': request.jediswap_metrics.utilization,
            'volatility': request.jediswap_metrics.volatility,
            'liquidity': request.jediswap_metrics.liquidity,
            'audit_score': request.jediswap_metrics.audit_score,
            'age_days': request.jediswap_metrics.age_days,
        }
        
        ekubo_metrics = {
            'utilization': request.ekubo_metrics.utilization,
            'volatility': request.ekubo_metrics.volatility,
            'liquidity': request.ekubo_metrics.liquidity,
            'audit_score': request.ekubo_metrics.audit_score,
            'age_days': request.ekubo_metrics.age_days,
        }
        
        logger.info(f"🚀 EXECUTING propose_and_execute_allocation on-chain...")
        logger.info(f"   Contract: {settings.RISK_ENGINE_ADDRESS}")
        logger.info(f"   Caller: {settings.BACKEND_WALLET_ADDRESS}")
        
        # Get function selector
        from starknet_py.hash.selector import get_selector_from_name
        from starknet_py.cairo.felt import encode_shortstring
        
        selector = get_selector_from_name("propose_and_execute_allocation")
        
        # Serialize structs to calldata manually
        # ProtocolMetrics struct: (utilization, volatility, liquidity, audit_score, age_days)
        calldata = [
            # jediswap_metrics struct
            jediswap_metrics['utilization'],
            jediswap_metrics['volatility'],
            jediswap_metrics['liquidity'],
            jediswap_metrics['audit_score'],
            jediswap_metrics['age_days'],
            # ekubo_metrics struct
            ekubo_metrics['utilization'],
            ekubo_metrics['volatility'],
            ekubo_metrics['liquidity'],
            ekubo_metrics['audit_score'],
            ekubo_metrics['age_days'],
        ]
        
        logger.info(f"📝 Calldata: {calldata}")
        
        # Execute via account
        from starknet_py.net.client_models import Call
        
        call = Call(
            to_addr=int(settings.RISK_ENGINE_ADDRESS, 16),
            selector=selector,
            calldata=calldata
        )
        
        invoke_result = await account.execute_v3(
            calls=[call],
            auto_estimate=True
        )
        
        tx_hash = hex(invoke_result.transaction_hash)
        logger.info(f"📤 Transaction submitted: {tx_hash}")
        
        # Update proof job with transaction hash
        proof_job.tx_hash = tx_hash
        proof_job.status = ProofStatus.SUBMITTED
        db.commit()
        db.refresh(proof_job)
        
        logger.info(f"⏳ Waiting for acceptance...")
        
        # Wait for transaction to be accepted
        await invoke_result.wait_for_acceptance()
        
        logger.info(f"✅ Transaction accepted on-chain!")
        
        # Update proof status to executed
        proof_job.status = ProofStatus.SUBMITTED
        proof_job.submitted_at = datetime.utcnow()
        db.commit()
        db.refresh(proof_job)
        
        # Trigger background SHARP submission
        logger.info(f"📡 Triggering SHARP submission...")
        asyncio.create_task(submit_proof_to_sharp(
            db=db,
            proof_job_id=proof_job.id,
            proof_data=proof.proof_data,
            proof_hash=proof.proof_hash
        ))
        
        # Now fetch the decision that was just created
        decision_count_result = await contract.functions["get_decision_count"].call()
        decision_count = int(decision_count_result[0]) if decision_count_result else 0
        
        if decision_count > 0:
            latest_decision_result = await contract.functions["get_decision"].call(decision_count)
            decision_data = latest_decision_result[0] if latest_decision_result else None
            
            if decision_data:
                logger.info(f"✅ AI Decision #{decision_count} executed:")
                logger.info(f"   JediSwap: {int(decision_data.jediswap_pct)/100}%")
                logger.info(f"   Ekubo: {int(decision_data.ekubo_pct)/100}%")
                
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
                    message=f"✅ AI executed decision #{decision_count} on-chain (tx: {tx_hash})",
                    # Proof information
                    proof_job_id=str(proof_job.id),
                    proof_hash=proof.proof_hash,
                    proof_status=proof_job.status.value if hasattr(proof_job.status, 'value') else str(proof_job.status)
                )
        
        raise HTTPException(
            status_code=500,
            detail="Transaction succeeded but failed to retrieve decision"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ AI Orchestration failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"AI execution failed: {str(e)}"
        )
