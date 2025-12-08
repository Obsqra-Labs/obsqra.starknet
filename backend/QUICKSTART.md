# 🚀 Backend Quick Start Guide

Get the Obsqra backend running in 5 minutes.

## Option 1: Docker (Recommended)

```bash
# Start both PostgreSQL and FastAPI
docker-compose up -d

# Check if running
curl http://localhost:8000/health
# Response: {"status": "healthy", "service": "obsqra-backend", "version": "1.0.0"}

# View logs
docker-compose logs -f backend

# Stop everything
docker-compose down
```

**Access Points:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs (Swagger UI)
- Database: localhost:5432 (credentials in docker-compose.yml)

---

## Option 2: Local Development

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- pip

### Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup PostgreSQL
# Option A: Use Docker just for database
docker run --name obsqra-db \
  -e POSTGRES_PASSWORD=obsqra \
  -e POSTGRES_DB=obsqra_db \
  -p 5432:5432 -d postgres:15

# Option B: Use local PostgreSQL (update DATABASE_URL in .env)

# 4. Configure environment
cp .env.example .env
# Edit .env with your database URL

# 5. Run server
uvicorn main:app --reload
```

**Server will be available at:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## First API Calls

### 1. Register User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure-password",
    "full_name": "John Doe"
  }'

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer",
#   "expires_in": 1800
# }
```

**Save the token for subsequent requests!**

### 2. Get Current User

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Response:
# {
#   "id": 1,
#   "email": "user@example.com",
#   "full_name": "John Doe",
#   "wallet_address": null,
#   "is_verified": false
# }
```

### 3. Get Dashboard Stats

```bash
curl http://localhost:8000/api/v1/analytics/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Response: Empty initially (no data yet)
# {
#   "latest_allocation": null,
#   "risk_scores": [],
#   "period_days": 7
# }
```

### 4. Connect Wallet

```bash
curl -X POST http://localhost:8000/api/v1/auth/connect-wallet \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "0x1234567890abcdef..."
  }'

# Response:
# {"message": "Wallet connected successfully"}
```

### 5. Update Preferences

```bash
curl -X PUT http://localhost:8000/api/v1/users/preferences \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "risk_tolerance": "medium",
    "auto_rebalance_enabled": true,
    "rebalance_threshold": 5.0
  }'

# Response:
# {"message": "Preferences updated"}
```

---

## Testing ML Models

### Test Risk Prediction

```python
from app.ml.models import RiskPredictionModel

model = RiskPredictionModel()

# Predict risk for Nostra protocol
metrics = {
    "utilization": 65,
    "volatility": 35,
    "liquidity": 1,
    "audit_score": 98,
    "age_days": 800,
}

risk_score, confidence = model.predict_risk("nostra", metrics)
print(f"Risk: {risk_score:.1f}, Confidence: {confidence:.2f}")
# Output: Risk: 45.2, Confidence: 0.87
```

### Test Allocation Optimization

```python
from app.ml.models import AllocationOptimizer

optimizer = AllocationOptimizer()

metrics = {
    "nostra": {
        "utilization": 65,
        "volatility": 35,
        "liquidity": 1,
        "audit_score": 98,
        "age_days": 800,
    },
    "zklend": {
        "utilization": 72,
        "volatility": 42,
        "liquidity": 1,
        "audit_score": 96,
        "age_days": 650,
    },
    "ekubo": {
        "utilization": 58,
        "volatility": 48,
        "liquidity": 2,
        "audit_score": 92,
        "age_days": 400,
    }
}

apys = {"nostra": 8.5, "zklend": 7.2, "ekubo": 12.1}

allocation = optimizer.optimize_allocation(metrics, apys)
print(allocation)
# Output: {'nostra': 45.2, 'zklend': 32.8, 'ekubo': 22.0}
```

---

## Useful Commands

### View API Documentation

```
http://localhost:8000/docs
```

Interactive Swagger UI with all endpoints.

### Check Database

```bash
# Connect to PostgreSQL
psql postgresql://obsqra:obsqra@localhost:5432/obsqra_db

# List tables
\dt

# Check users
SELECT * FROM users;

# Check risk history
SELECT * FROM risk_history;
```

### Run Tests

```bash
pytest
pytest -v           # Verbose
pytest --cov=app    # With coverage
```

### Format Code

```bash
black app/
```

### Lint Code

```bash
flake8 app/
mypy app/
```

---

## Troubleshooting

### PostgreSQL Connection Error

```
Error: could not connect to server
```

**Solution**: Make sure PostgreSQL is running
```bash
# Docker
docker ps  # Check if obsqra-postgres is running

# Local PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql   # Mac
```

### Port Already in Use

```
Address already in use
```

**Solution**: Change port in command
```bash
uvicorn main:app --reload --port 8001
```

### Import Errors

```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

---

## Next Steps

1. **Connect Frontend** - Point Next.js to http://localhost:8000
2. **Create Schema** - Run Alembic migrations (when set up)
3. **Load Test Data** - Create sample users and data
4. **Test Integration** - Call backend from frontend
5. **Deploy** - Use docker-compose on production server

---

## File Locations

| File | Purpose |
|------|---------|
| `main.py` | FastAPI entry point |
| `app/config.py` | Settings management |
| `app/models.py` | Database models |
| `app/database.py` | SQLAlchemy setup |
| `app/api/routes/` | API endpoints |
| `app/ml/models.py` | ML models |
| `docker-compose.yml` | Container setup |
| `requirements.txt` | Dependencies |

---

## Useful Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org
- **scikit-learn**: https://scikit-learn.org
- **PostgreSQL**: https://www.postgresql.org/docs

---

## Support

Check `README.md` for full documentation or the main project README for system-wide help.

**You're all set! 🚀**


