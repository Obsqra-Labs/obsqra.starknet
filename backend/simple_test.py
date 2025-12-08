"""
Minimal test server - no external dependencies
"""

from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Obsqra Backend Test")

# Test data
TEST_DATA = {
    "dashboard": {
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
    },
    "risk_forecast": [
        {"protocol": "nostra", "predicted_risk": 42.5, "confidence": 0.87},
        {"protocol": "zklend", "predicted_risk": 51.3, "confidence": 0.82},
        {"protocol": "ekubo", "predicted_risk": 36.8, "confidence": 0.75},
    ],
    "yield_forecast": [
        {"protocol": "nostra", "predicted_yield": 8.2, "confidence": 0.70},
        {"protocol": "zklend", "predicted_yield": 7.5, "confidence": 0.68},
        {"protocol": "ekubo", "predicted_yield": 13.2, "confidence": 0.65},
    ],
    "allocation": {
        "nostra": 45.2,
        "zklend": 32.8,
        "ekubo": 22.0,
    },
}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    return {
        "message": "Obsqra Backend (Test Mode)",
        "endpoints": [
            "GET /health",
            "GET /dashboard",
            "GET /risk-forecast",
            "GET /yield-forecast",
            "POST /optimize",
            "GET /transactions",
            "GET /docs",
        ]
    }

@app.get("/dashboard")
async def dashboard():
    return TEST_DATA["dashboard"]

@app.get("/risk-forecast")
async def risk_forecast():
    return TEST_DATA["risk_forecast"]

@app.get("/yield-forecast")
async def yield_forecast():
    return TEST_DATA["yield_forecast"]

@app.post("/optimize")
async def optimize():
    return {
        "message": "Optimization scheduled",
        "allocation": TEST_DATA["allocation"]
    }

@app.get("/transactions")
async def transactions():
    return [{
        "id": 1,
        "tx_hash": "0x123456",
        "status": "confirmed",
        "amount": 100.0,
    }]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

