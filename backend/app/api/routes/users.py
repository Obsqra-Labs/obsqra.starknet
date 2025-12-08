"""User management endpoints"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models import User
from app.api.routes.auth import get_current_user

router = APIRouter()


class PreferencesUpdate(BaseModel):
    """User preferences update."""
    risk_tolerance: str = None
    auto_rebalance_enabled: bool = None
    rebalance_threshold: float = None
    email_alerts_enabled: bool = None


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get user profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "wallet_address": current_user.wallet_address,
        "is_verified": current_user.is_verified,
        "preferences": current_user.preferences,
    }


@router.put("/preferences")
async def update_preferences(
    preferences: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences."""
    for key, value in preferences.dict(exclude_unset=True).items():
        if value is not None:
            current_user.preferences[key] = value
    
    await db.commit()
    return {"message": "Preferences updated"}

