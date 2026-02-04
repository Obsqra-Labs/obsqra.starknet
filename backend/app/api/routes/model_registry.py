"""Model Registry API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from app.config import get_settings
from app.services.model_registry_service import get_model_registry_service
from app.services.model_service import get_model_service

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class ModelRegistryEntry(BaseModel):
    registry_address: str
    version_felt: str
    version: str
    model_hash_felt: str
    model_hash: str
    deployed_at: int
    description: str
    is_active: bool


class ModelHistoryResponse(BaseModel):
    registry_address: str
    versions: List[ModelRegistryEntry]


class RegisterModelRequest(BaseModel):
    version: Optional[str] = Field(None, description="Version felt (0x..) or semantic version (e.g. 1.0.0)")
    model_hash: Optional[str] = Field(None, description="Model hash felt (0x..) or hex string")
    description: Optional[str] = Field("Initial risk scoring model", description="Human-readable description")


class RegisterModelResponse(BaseModel):
    transaction_hash: str
    model: ModelRegistryEntry


def _decode_version_felt(version_felt: int) -> str:
    if version_felt <= 0:
        return "0.0.0"
    major = (version_felt >> 16) & 0xFF
    minor = (version_felt >> 8) & 0xFF
    patch = version_felt & 0xFF
    return f"{major}.{minor}.{patch}"


def _parse_version(value: Optional[str], fallback_felt: int) -> int:
    if value is None or value == "":
        return fallback_felt
    if isinstance(value, str) and value.startswith("0x"):
        return int(value, 16)
    # Semver string
    if isinstance(value, str) and "." in value:
        parts = value.split(".")
        try:
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            return (major << 16) + (minor << 8) + patch
        except ValueError:
            return fallback_felt
    try:
        return int(value)
    except Exception:
        return fallback_felt


def _parse_model_hash(value: Optional[str], fallback_felt: int) -> int:
    if value is None or value == "":
        return fallback_felt
    if isinstance(value, str) and value.startswith("0x"):
        return int(value, 16)
    try:
        return int(value, 16)
    except Exception:
        return fallback_felt


def _format_entry(raw: dict, registry_address: str) -> ModelRegistryEntry:
    version_felt = int(raw.get("version", 0))
    model_hash_felt = int(raw.get("model_hash", 0))
    return ModelRegistryEntry(
        registry_address=registry_address,
        version_felt=hex(version_felt),
        version=_decode_version_felt(version_felt),
        model_hash_felt=hex(model_hash_felt),
        model_hash=hex(model_hash_felt),
        deployed_at=int(raw.get("deployed_at", 0)),
        description=raw.get("description", ""),
        is_active=bool(raw.get("is_active", False)),
    )


def _authorize_admin(admin_key: Optional[str]):
    if settings.MODEL_REGISTRY_ADMIN_KEY:
        if admin_key != settings.MODEL_REGISTRY_ADMIN_KEY:
            raise HTTPException(status_code=403, detail="Invalid admin key")
    else:
        # Allow in non-production without key
        if settings.ENVIRONMENT.lower() == "production":
            raise HTTPException(status_code=403, detail="Admin key required")


@router.get("/current", response_model=ModelRegistryEntry)
async def get_current_model():
    service = get_model_registry_service()
    registry = await service.get_current_model()
    if not registry:
        raise HTTPException(status_code=404, detail="No model registered")
    return _format_entry(registry, registry_address=settings.MODEL_REGISTRY_ADDRESS)


@router.get("/history", response_model=ModelHistoryResponse)
async def get_model_history():
    service = get_model_registry_service()
    versions = await service.get_model_history()
    entries: List[ModelRegistryEntry] = []
    for version in versions:
        entry_raw = await service.get_model_version(int(version))
        if entry_raw:
            entries.append(_format_entry(entry_raw, registry_address=settings.MODEL_REGISTRY_ADDRESS))
    return ModelHistoryResponse(
        registry_address=settings.MODEL_REGISTRY_ADDRESS,
        versions=entries,
    )


@router.get("/version/{version}", response_model=ModelRegistryEntry)
async def get_model_version(version: str):
    service = get_model_registry_service()
    fallback = service.get_local_model_info().get("version_felt", 0)
    version_felt = _parse_version(version, fallback)
    entry = await service.get_model_version(version_felt)
    if not entry:
        raise HTTPException(status_code=404, detail="Model version not found")
    return _format_entry(entry, registry_address=settings.MODEL_REGISTRY_ADDRESS)


@router.post("/register", response_model=RegisterModelResponse)
async def register_model_version(
    request: RegisterModelRequest,
    admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
):
    _authorize_admin(admin_key)
    service = get_model_registry_service()
    model_service = get_model_service()
    local_info = model_service.get_current_model_version()

    version_felt = _parse_version(request.version, local_info.get("version_felt", 0))
    model_hash_felt = _parse_model_hash(request.model_hash, local_info.get("model_hash_felt", 0))
    description = request.description or local_info.get("description", "")

    tx_hash = await service.register_model_version(
        version_felt=version_felt,
        model_hash_felt=model_hash_felt,
        description=description,
    )

    # Fetch latest model after registration
    current = await service.get_current_model()
    if not current:
        raise HTTPException(status_code=500, detail="Failed to read model registry after registration")

    return RegisterModelResponse(
        transaction_hash=hex(tx_hash),
        model=_format_entry(current, registry_address=settings.MODEL_REGISTRY_ADDRESS),
    )
