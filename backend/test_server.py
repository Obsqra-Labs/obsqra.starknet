"""
Simple test server to verify FastAPI setup works
Doesn't require database, just tests the basic structure
"""

import sys
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

# Create test app
app = FastAPI(
    title="Obsqra Backend (Test Mode)",
    description="Testing core functionality without database",
    version="1.0.0",
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3003", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test models
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

# Test routes
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "obsqra-backend-test",
        "version": "1.0.0",
        "mode": "test (no database)",
    }

@app.post("/api/v1/auth/register", response_model=TokenResponse)
async def register(request: UserRegisterRequest):
    """Test registration endpoint."""
    # Mock response
    return {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzAxOTAwMDAwfQ.test_token",
        "token_type": "bearer",
        "expires_in": 1800
    }

@app.get("/api/v1/auth/me")
async def get_me():
    """Test current user endpoint."""
    return {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "wallet_address": None,
        "is_verified": False,
    }

@app.get("/dashboard")
@app.get("/api/v1/analytics/dashboard")
async def get_dashboard():
    """Test dashboard endpoint."""
    return {
        "latest_allocation": {
            "nostra_pct": 45.2,
            "zklend_pct": 32.8,
            "ekubo_pct": 22.0,
        },
        "risk_scores": [
            {"protocol": "nostra", "score": 45.2},
            {"protocol": "zklend", "score": 52.1},
            {"protocol": "ekubo", "score": 38.9},
        ],
        "period_days": 7,
    }

@app.get("/risk-forecast")
@app.get("/api/v1/predictions/risk-forecast")
async def get_risk_forecast():
    """Test risk forecast endpoint."""
    return [
        {"protocol": "nostra", "predicted_risk": 42.5, "confidence": 0.87},
        {"protocol": "zklend", "predicted_risk": 51.3, "confidence": 0.82},
        {"protocol": "ekubo", "predicted_risk": 36.8, "confidence": 0.75},
    ]

@app.get("/yield-forecast")
@app.get("/api/v1/predictions/yield-forecast")
async def get_yield_forecast():
    """Test yield forecast endpoint."""
    return [
        {"protocol": "nostra", "predicted_yield": 8.2, "confidence": 0.70},
        {"protocol": "zklend", "predicted_yield": 7.5, "confidence": 0.68},
        {"protocol": "ekubo", "predicted_yield": 13.2, "confidence": 0.65},
    ]

@app.post("/optimize")
@app.post("/api/v1/predictions/run-optimization")
async def run_optimization():
    """Test optimization endpoint."""
    return {
        "message": "Optimization scheduled",
        "status": "queued",
        "allocation": {
            "nostra": 45.2,
            "zklend": 32.8,
            "ekubo": 22.0,
        }
    }

@app.get("/transactions")
@app.get("/api/v1/transactions/")
async def list_transactions():
    """Test transactions endpoint."""
    return [
        {
            "id": 1,
            "tx_hash": "0x123456789abcdef",
            "tx_type": "deposit",
            "amount": 100.0,
            "status": "confirmed",
            "created_at": "2025-12-06T10:00:00",
        }
    ]

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 Starting Obsqra Backend Test Server")
    print("="*70)
    print("\n📍 Access points:")
    print("   • API:  http://localhost:8000")
    print("   • Docs: http://localhost:8000/docs")
    print("   • Health: http://localhost:8000/health")
    print("\n📝 Test endpoints:")
    print("   • POST /api/v1/auth/register")
    print("   • GET  /api/v1/auth/me")
    print("   • GET  /api/v1/analytics/dashboard")
    print("   • GET  /api/v1/predictions/risk-forecast")
    print("   • GET  /api/v1/predictions/yield-forecast")
    print("   • POST /api/v1/predictions/run-optimization")
    print("   • GET  /api/v1/transactions/")
    print("\n⚠️  Mode: TEST (no database connection)")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

