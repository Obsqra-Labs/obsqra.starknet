"""Read-only market data endpoints (mainnet-friendly)."""
from fastapi import APIRouter, Query

from app.config import get_settings
from app.services.market_data_service import get_market_data_service

router = APIRouter()
settings = get_settings()


@router.get("/snapshot", tags=["Market"])
async def get_market_snapshot(
    force_refresh: bool = Query(False, description="Bypass APY cache"),
):
    """
    Fetch a read-only market snapshot (APYs + block metadata).
    Uses DATA_RPC_URL if set; otherwise falls back to STARKNET_RPC_URL.
    """
    rpc_url = settings.DATA_RPC_URL or settings.STARKNET_RPC_URL
    network = settings.DATA_NETWORK or settings.STARKNET_NETWORK
    service = get_market_data_service(rpc_url=rpc_url, network=network)

    snapshot = await service.get_snapshot(force_refresh=force_refresh)

    return {
        "block_number": snapshot.block_number,
        "block_hash": snapshot.block_hash,
        "timestamp": snapshot.timestamp,
        "apys": snapshot.apys,
        "apy_source": snapshot.apy_source,
        "network": snapshot.network,
        "rpc_url": snapshot.rpc_url,
    }
