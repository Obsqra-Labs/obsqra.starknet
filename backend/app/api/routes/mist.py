"""MIST.cash privacy integration endpoints (commit/reveal)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging

from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models import StarknetChainId

from app.config import get_settings
from app.utils.rpc import get_rpc_urls, with_rpc_fallback

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class MistCommitRequest(BaseModel):
    commitment_hash: str = Field(..., description="Poseidon hash of secret")
    expected_amount: int = Field(..., ge=1, description="Expected amount (u256)")


class MistRevealRequest(BaseModel):
    secret: str = Field(..., description="Secret used in commitment")


class MistChamberRequest(BaseModel):
    chamber_address: str = Field(..., description="MIST chamber contract address")


def _build_backend_account(client: FullNodeClient) -> Account:
    if not settings.BACKEND_WALLET_PRIVATE_KEY or not settings.BACKEND_WALLET_ADDRESS:
        raise HTTPException(status_code=500, detail="Backend wallet not configured")

    key_pair = KeyPair.from_private_key(int(settings.BACKEND_WALLET_PRIVATE_KEY, 16))
    network_chain = (
        StarknetChainId.SEPOLIA
        if settings.STARKNET_NETWORK.lower() == "sepolia"
        else StarknetChainId.MAINNET
    )
    return Account(
        address=int(settings.BACKEND_WALLET_ADDRESS, 16),
        client=client,
        key_pair=key_pair,
        chain=network_chain,
    )


async def _get_router_contract(account: Account) -> Contract:
    if not settings.STRATEGY_ROUTER_ADDRESS:
        raise HTTPException(status_code=500, detail="STRATEGY_ROUTER_ADDRESS not configured")
    return await Contract.from_address(
        address=int(settings.STRATEGY_ROUTER_ADDRESS, 16),
        provider=account,
    )


@router.post("/commit", tags=["MIST"])
async def commit_mist_deposit(request: MistCommitRequest):
    """Commit a MIST deposit hash to the strategy router."""
    commitment = int(request.commitment_hash, 16)

    try:
        async def _call(client: FullNodeClient, _rpc_url: str):
            account = _build_backend_account(client)
            contract = await _get_router_contract(account)
            return await contract.functions["commit_mist_deposit"].invoke(
                commitment,
                request.expected_amount,
                auto_estimate=True,
            )

        invoke, _ = await with_rpc_fallback(_call, urls=get_rpc_urls())
        tx_hash = hex(invoke.transaction_hash)
        logger.info(f"MIST commit submitted: {tx_hash}")
        return {"tx_hash": tx_hash, "commitment_hash": request.commitment_hash}
    except Exception as e:
        logger.error(f"MIST commit failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reveal", tags=["MIST"])
async def reveal_mist_deposit(request: MistRevealRequest):
    """Reveal a MIST deposit secret and claim from the chamber."""
    secret = int(request.secret, 16)
    try:
        async def _call(client: FullNodeClient, _rpc_url: str):
            account = _build_backend_account(client)
            contract = await _get_router_contract(account)
            return await contract.functions["reveal_and_claim_mist_deposit"].invoke(
                secret,
                auto_estimate=True,
            )

        invoke, _ = await with_rpc_fallback(_call, urls=get_rpc_urls())
        tx_hash = hex(invoke.transaction_hash)
        logger.info(f"MIST reveal submitted: {tx_hash}")
        return {"tx_hash": tx_hash}
    except Exception as e:
        logger.error(f"MIST reveal failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/commitments/{commitment_hash}", tags=["MIST"])
async def get_mist_commitment(commitment_hash: str):
    """Get commitment info (user, amount, revealed)."""
    commitment = int(commitment_hash, 16)
    try:
        async def _call(client: FullNodeClient, _rpc_url: str):
            contract = await Contract.from_address(
                address=int(settings.STRATEGY_ROUTER_ADDRESS, 16),
                provider=client,
            )
            return await contract.functions["get_mist_commitment"].call(commitment)

        result, _ = await with_rpc_fallback(_call, urls=get_rpc_urls())
        user, amount, revealed = result
        return {
            "commitment_hash": commitment_hash,
            "user": hex(user) if hasattr(user, "__int__") else user,
            "amount": int(amount),
            "revealed": bool(revealed),
        }
    except Exception as e:
        logger.error(f"Failed to read commitment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chamber", tags=["MIST"])
async def set_mist_chamber(request: MistChamberRequest):
    """Set the MIST chamber address on the router (owner only)."""
    chamber = int(request.chamber_address, 16)
    try:
        async def _call(client: FullNodeClient, _rpc_url: str):
            account = _build_backend_account(client)
            contract = await _get_router_contract(account)
            return await contract.functions["set_mist_chamber"].invoke(
                chamber,
                auto_estimate=True,
            )

        invoke, _ = await with_rpc_fallback(_call, urls=get_rpc_urls())
        tx_hash = hex(invoke.transaction_hash)
        logger.info(f"MIST chamber set: {tx_hash}")
        return {"tx_hash": tx_hash, "chamber_address": request.chamber_address}
    except Exception as e:
        logger.error(f"Failed to set chamber: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
