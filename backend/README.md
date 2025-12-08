# Obsqra Backend - Verifiable AI Infrastructure

Production-ready Python/FastAPI backend with ML-powered risk prediction and optimization.

## Features

✨ **Authentication & Users**
- Email-based registration (no wallet required initially)
- JWT authentication
- Wallet connection when ready to transact
- User preferences and settings

📊 **Analytics**
- Risk score history tracking
- Allocation snapshots
- Dashboard statistics
- Trend analysis

🧠 **Machine Learning**
- Risk prediction models (scikit-learn)
- Yield forecasting
- Allocation optimization
- Rebalancing suggestions
- Confidence scoring

🔄 **Transaction Tracking**
- All transactions logged
- Status monitoring
- Immutable history

📈 **Real-time Data**
- Historical data access
- Performance metrics
- Live updates

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **ML/Data**: scikit-learn, NumPy, Pandas
- **Auth**: JWT + bcrypt
- **Server**: Uvicorn
- **Containerization**: Docker + Docker Compose

## Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Multi-container setup
│
├── app/
│   ├── config.py          # Settings from env
│   ├── database.py        # SQLAlchemy setup
│   ├── models.py          # Database models
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   ├── users.py           # User profile management
│   │   │   ├── analytics.py       # Historical data
│   │   │   ├── predictions.py     # ML predictions
│   │   │   └── transactions.py    # Transaction tracking
│   │
│   └── ml/
│       ├── models.py      # Risk, Yield, Allocation models
│       └── scheduler.py   # Background job scheduler
```

## Quick Start

### Local Development

1. **Setup Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Setup PostgreSQL**
```bash
# Using Docker
docker run --name obsqra-postgres -e POSTGRES_PASSWORD=obsqra -e POSTGRES_DB=obsqra_db -p 5432:5432 -d postgres:15

# Or use local PostgreSQL
# Update DATABASE_URL in .env
```

4. **Run migrations** (when Alembic is set up)
```bash
alembic upgrade head
```

5. **Start server**
```bash
uvicorn main:app --reload
```

Server will be available at `http://localhost:8000`

### Docker Deployment

```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- FastAPI backend on port 8000

Check health:
```bash
curl http://localhost:8000/health
```

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - Register new user
- `POST /login` - Login with email
- `GET /me` - Get current user
- `POST /connect-wallet` - Link Starknet wallet

### Users (`/api/v1/users`)
- `GET /profile` - Get user profile
- `PUT /preferences` - Update preferences

### Analytics (`/api/v1/analytics`)
- `GET /risk-history` - Risk score history
- `GET /allocation-history` - Allocation snapshots
- `GET /dashboard` - Dashboard statistics

### Predictions (`/api/v1/predictions`)
- `GET /risk-forecast` - Risk predictions
- `GET /yield-forecast` - Yield predictions
- `GET /rebalance-suggestions` - Optimization suggestions
- `POST /run-optimization` - Trigger optimization

### Transactions (`/api/v1/transactions`)
- `POST /` - Log transaction
- `GET /` - List transactions
- `GET /{tx_hash}` - Get transaction details

## ML Models

### Risk Prediction
Predicts risk score (0-100) for each protocol based on:
- Utilization rate
- Volatility
- Liquidity
- Audit score
- Protocol age

```python
from app.ml.models import RiskPredictionModel

model = RiskPredictionModel()
risk, confidence = model.predict_risk("nostra", {
    "utilization": 65,
    "volatility": 35,
    "liquidity": 1,
    "audit_score": 98,
    "age_days": 800,
})
```

### Allocation Optimization
Optimizes allocation across protocols based on:
- Risk predictions
- Yield forecasts
- User risk tolerance
- Protocol constraints

```python
from app.ml.models import AllocationOptimizer

optimizer = AllocationOptimizer()
allocation = optimizer.optimize_allocation(
    protocol_metrics={...},
    apys={"nostra": 8.5, "zklend": 7.2, "ekubo": 12.1},
    user_preferences={"risk_tolerance": "medium"}
)
```

## Configuration

Create `.env` file (see `.env.example`):

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/obsqra_db

# Server
ENVIRONMENT=development
API_PORT=8000

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Starknet
STARKNET_RPC_URL=https://starknet-sepolia.public.blastapi.io
RISK_ENGINE_ADDRESS=0x008c3eff...

# ML
PREDICTION_WINDOW_DAYS=7
BACKTEST_WINDOW_DAYS=90
```

## Database Models

### User
Stores user authentication, profile, and preferences.

### RiskHistory
Historical risk scores for each protocol per user.

### AllocationHistory
Snapshots of user allocations over time.

### Transaction
Immutable transaction log with status tracking.

### Prediction
ML model predictions and optimization suggestions.

## Development

### Testing
```bash
pytest
pytest --cov=app  # With coverage
```

### Code Quality
```bash
black app/        # Format code
flake8 app/       # Lint
mypy app/         # Type checking
```

### Database Migrations (Future)
```bash
alembic init alembic           # Initialize Alembic
alembic revision --autogenerate -m "Add column"
alembic upgrade head
```

## Monitoring

Health check endpoint:
```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "service": "obsqra-backend",
  "version": "1.0.0"
}
```

## Security

- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ CORS configured
- ✅ SQL injection protection (SQLAlchemy)
- ✅ Rate limiting (to be added)
- ✅ Request validation (Pydantic)

## Next Steps

1. **Alembic Setup** - Database migration management
2. **Celery Integration** - Background job queue
3. **Caching Layer** - Redis for performance
4. **Email Service** - Send verification emails
5. **Error Tracking** - Sentry integration
6. **API Documentation** - Auto-generated with Swagger UI
7. **Testing** - Unit and integration tests
8. **Production Deployment** - Gunicorn + Nginx

## Frontend Integration

The backend API is ready to be consumed by the Next.js frontend:

```typescript
// Frontend example
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    Authorization: `Bearer ${token}`
  }
});

// Get dashboard stats
const stats = await api.get('/analytics/dashboard');

// Get predictions
const forecast = await api.get('/predictions/risk-forecast');

// List transactions
const txs = await api.get('/transactions/');
```

## License

Proprietary - Obsqra Inc.

## Support

For issues, check the [main project README](/opt/obsqra.starknet/README.md)

