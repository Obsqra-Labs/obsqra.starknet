"""RPC helpers with retry + failover."""

from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable, Iterable, List, Optional, Sequence, Tuple, TypeVar

from starknet_py.net.full_node_client import FullNodeClient

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

T = TypeVar("T")


def _split_urls(raw: str) -> List[str]:
    return [url.strip() for url in raw.split(",") if url.strip()]


def get_rpc_urls() -> List[str]:
    """Return ordered, de-duplicated list of RPC URLs."""
    urls: List[str] = []
    if settings.STARKNET_RPC_URLS:
        urls.extend(_split_urls(settings.STARKNET_RPC_URLS))

    # Always include the primary RPC as a fallback.
    if settings.STARKNET_RPC_URL:
        urls.append(settings.STARKNET_RPC_URL)

    # De-duplicate while preserving order.
    seen = set()
    deduped: List[str] = []
    for url in urls:
        if url not in seen:
            deduped.append(url)
            seen.add(url)
    return deduped


def is_retryable_rpc_error(exc: Exception) -> bool:
    """Best-effort detection of transient RPC errors."""
    status_code = getattr(exc, "status_code", None)
    if isinstance(status_code, int) and status_code in {502, 503, 504, 429}:
        return True

    message = str(exc).lower()
    if "blast api is no longer available" in message and "403" in message:
        return True
    retry_signals = [
        "502",
        "503",
        "504",
        "429",
        "bad gateway",
        "service unavailable",
        "gateway timeout",
        "temporarily unavailable",
        "timeout",
        "timed out",
        "connection reset",
        "connection error",
        "client connector error",
        "cannot connect",
    ]
    return any(signal in message for signal in retry_signals)


def _default_retries() -> int:
    return max(1, int(settings.STARKNET_RPC_RETRY_ATTEMPTS))


def _default_backoff() -> float:
    return max(0.1, float(settings.STARKNET_RPC_RETRY_BACKOFF_SEC))


async def with_rpc_fallback(
    action: Callable[[FullNodeClient, str], Awaitable[T]],
    *,
    urls: Optional[Sequence[str]] = None,
    retries: Optional[int] = None,
    backoff_sec: Optional[float] = None,
) -> Tuple[T, str]:
    """
    Execute an async action against RPC endpoints with retry + failover.

    Returns (result, rpc_url_used).
    """
    rpc_urls = list(urls or get_rpc_urls())
    if not rpc_urls:
        raise RuntimeError("No Starknet RPC URLs configured")

    attempts = retries if retries is not None else _default_retries()
    backoff = backoff_sec if backoff_sec is not None else _default_backoff()

    last_exc: Optional[Exception] = None
    for attempt in range(attempts):
        for rpc_url in rpc_urls:
            client = FullNodeClient(node_url=rpc_url)
            try:
                result = await action(client, rpc_url)
                return result, rpc_url
            except Exception as exc:  # noqa: BLE001 - bubble after retry checks
                last_exc = exc
                if not is_retryable_rpc_error(exc):
                    raise
                logger.warning(
                    "RPC error on %s (attempt %s/%s): %s",
                    rpc_url,
                    attempt + 1,
                    attempts,
                    exc,
                )

        if attempt < attempts - 1:
            await asyncio.sleep(backoff * (2 ** attempt))

    if last_exc:
        raise last_exc
    raise RuntimeError("RPC failover failed without an exception")
