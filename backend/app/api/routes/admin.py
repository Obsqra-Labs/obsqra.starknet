"""Admin endpoints for contract management"""

from fastapi import APIRouter, HTTPException
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call

from app.config import settings
from app.utils.rpc import with_rpc_fallback
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

DEFAULT_RESOURCE_BOUNDS = {
    "l1_gas": {"max_amount": 10000, "max_price_per_unit": 200000000000000},
    "l2_gas": {"max_amount": 1000000, "max_price_per_unit": 1000000000},
    "l1_data_gas": {"max_amount": 5000, "max_price_per_unit": 150000000000000},
}


@router.post("/update-strategy-router-risk-engine")
async def update_strategy_router_risk_engine():
    """
    Update StrategyRouter's risk_engine to point to current RISK_ENGINE_ADDRESS.
    
    This fixes the issue where StrategyRouter is wired to an old RiskEngine,
    causing allocation execution to fail.
    """
    if not settings.BACKEND_WALLET_PRIVATE_KEY or not settings.BACKEND_WALLET_ADDRESS:
        raise HTTPException(
            status_code=500,
            detail="Backend wallet not configured. Set BACKEND_WALLET_PRIVATE_KEY in backend/.env"
        )
    
    strategy_router = int(settings.STRATEGY_ROUTER_ADDRESS, 16)
    new_risk_engine = int(settings.RISK_ENGINE_ADDRESS, 16)
    
    logger.info(f"🔧 Updating StrategyRouter's risk_engine...")
    logger.info(f"   StrategyRouter: {hex(strategy_router)}")
    logger.info(f"   New RiskEngine: {hex(new_risk_engine)}")
    
    key_pair = KeyPair.from_private_key(int(settings.BACKEND_WALLET_PRIVATE_KEY, 16))
    network_chain = (
        StarknetChainId.SEPOLIA
        if settings.STARKNET_NETWORK.lower() == "sepolia"
        else StarknetChainId.MAINNET
    )
    
    async def _execute(client: FullNodeClient, _rpc_url: str):
        # Create account
        account = Account(
            address=int(settings.BACKEND_WALLET_ADDRESS, 16),
            client=client,
            key_pair=key_pair,
            chain=network_chain
        )
        
        # Get nonce manually to avoid RPC version issues
        nonce_response = await client._client.call(
            method_name="starknet_getNonce",
            params={"block_id": "latest", "contract_address": settings.BACKEND_WALLET_ADDRESS}
        )
        nonce = int(nonce_response, 16)
        logger.info(f"   Nonce: {nonce}")
        
        # Build call
        call = Call(
            to_addr=strategy_router,
            selector=get_selector_from_name("set_risk_engine"),
            calldata=[new_risk_engine]
        )
        
        # Sign invoke manually to avoid cairo version check issues
        from starknet_py.transaction_errors import TransactionRejectedError
        from starknet_py.net.client_models import ResourceBounds
        
        # Build signed invoke
        prepared_call = await account.sign_invoke_v3(
            calls=[call],
            nonce=nonce,
            l1_resource_bounds=ResourceBounds(
                max_amount=DEFAULT_RESOURCE_BOUNDS["l1_gas"]["max_amount"],
                max_price_per_unit=DEFAULT_RESOURCE_BOUNDS["l1_gas"]["max_price_per_unit"]
            ),
        )
        
        # Send transaction
        result = await client.send_transaction(prepared_call)
        return result
    
    try:
        result, rpc_used = await with_rpc_fallback(_execute)
        tx_hash = hex(result.transaction_hash)
        
        logger.info(f"✅ Transaction sent: {tx_hash}")
        logger.info(f"   RPC used: {rpc_used}")
        
        # Wait for confirmation
        async def _wait(client: FullNodeClient, _rpc_url: str):
            await client.wait_for_tx(result.transaction_hash)
            return True
        
        await with_rpc_fallback(_wait, urls=[rpc_used])
        
        logger.info(f"✅ StrategyRouter's risk_engine updated to {hex(new_risk_engine)}!")
        
        return {
            "success": True,
            "tx_hash": tx_hash,
            "strategy_router": hex(strategy_router),
            "new_risk_engine": hex(new_risk_engine),
            "message": "StrategyRouter's risk_engine updated successfully. Allocation execution is now unblocked."
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to update StrategyRouter: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update StrategyRouter: {str(e)}")
