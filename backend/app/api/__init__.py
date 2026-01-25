"""API Routes"""

from fastapi import APIRouter
from app.api.routes import auth, users, analytics, predictions, transactions, proofs, market, zkml, mist

try:
    from app.api.routes import risk_engine
    HAS_RISK_ENGINE = True
except ImportError as e:
    print(f"⚠️ Risk Engine module not available: {e}")
    HAS_RISK_ENGINE = False

router = APIRouter()

# Include route modules
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
router.include_router(proofs.router, prefix="/proofs", tags=["Proofs"])
router.include_router(market.router, prefix="/market", tags=["Market"])
router.include_router(zkml.router, prefix="/zkml", tags=["zkML"])
router.include_router(mist.router, prefix="/mist", tags=["MIST"])

if HAS_RISK_ENGINE:
    router.include_router(risk_engine.router, prefix="/risk-engine", tags=["Risk Engine"])
