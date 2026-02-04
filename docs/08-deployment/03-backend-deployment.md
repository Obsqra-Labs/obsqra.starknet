# Backend Deployment Guide

Complete guide for deploying the FastAPI backend service, including environment setup, database configuration, and service management.

## Prerequisites

### Server Requirements

**Minimum:**
- Ubuntu 20.04+ or similar Linux
- 2 CPU cores
- 4 GB RAM
- 20 GB storage

**Recommended:**
- 4+ CPU cores
- 8+ GB RAM
- 50+ GB storage
- SSD storage

### Software Requirements

**1. Python 3.11+**
```bash
python3 --version  # Should be 3.11+
```

**2. PostgreSQL 12+**
```bash
psql --version  # Should be 12+
```

**3. System Dependencies**
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib
```

## Backend Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/Obsqra-Labs/obsqra.starknet.git
cd obsqra.starknet/backend
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Database Setup

**Create Database:**
```bash
sudo -u postgres createdb obsqra_db
sudo -u postgres createuser obsqra_user
sudo -u postgres psql -c "ALTER USER obsqra_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE obsqra_db TO obsqra_user;"
```

**Run Migrations:**
```bash
# If using Alembic
alembic upgrade head

# Or manually
psql obsqra_db < migrations/001_initial.sql
```

### Step 5: Environment Configuration

**Create .env file:**
```bash
cat > .env << EOF
# Environment
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://obsqra_user:secure_password@localhost/obsqra_db

# Starknet
STARKNET_RPC_URL=https://starknet-sepolia-rpc.publicnode.com
STARKNET_NETWORK=sepolia
RISK_ENGINE_ADDRESS=0x000ee68bae3346502c97a79ac575b7c5c5839c1bb79a18cbd2717ea0126a09d4
STRATEGY_ROUTER_ADDRESS=0x0221284a7b77041f9f963c0f0b65b901604792533f0f937aa4591bd43d08ee2b
MODEL_REGISTRY_ADDRESS=0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc

# Backend Wallet
BACKEND_WALLET_ADDRESS=<your_wallet_address>
BACKEND_WALLET_PRIVATE_KEY=<your_private_key>

# Integrity Service (Optional)
ATLANTIC_API_KEY=<api_key>

# Server
API_HOST=0.0.0.0
API_PORT=8001
EOF
```

**Secure .env:**
```bash
chmod 600 .env
```

## Service Management

### Option 1: systemd Service

**Create service file:**
```bash
sudo cat > /etc/systemd/system/obsqra-backend.service << EOF
[Unit]
Description=Obsqra Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=obsqra
WorkingDirectory=/opt/obsqra.starknet/backend
Environment="PATH=/opt/obsqra.starknet/backend/venv/bin"
ExecStart=/opt/obsqra.starknet/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

**Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable obsqra-backend
sudo systemctl start obsqra-backend
sudo systemctl status obsqra-backend
```

### Option 2: Manual Start

```bash
cd /opt/obsqra.starknet/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Option 3: Docker (Future)

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## Verification

### Health Check

```bash
curl http://localhost:8001/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### API Test

```bash
curl http://localhost:8001/api/v1/risk-engine/decisions
```

## Monitoring

### Logs

**systemd:**
```bash
sudo journalctl -u obsqra-backend -f
```

**Manual:**
```bash
tail -f /opt/obsqra.starknet/backend/logs/app.log
```

### Metrics

**Endpoints:**
- `/health`: Health check
- `/metrics`: Prometheus metrics (if enabled)

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
sudo journalctl -u obsqra-backend -n 50
```

**Common issues:**
- Database connection failed
- Missing environment variables
- Port already in use
- Python dependencies missing

### Database Connection

**Test connection:**
```bash
psql -h localhost -U obsqra_user -d obsqra_db
```

**Check credentials:**
- Verify DATABASE_URL
- Check user permissions
- Confirm database exists

## Next Steps

- **[Fact Registry Deployment](04-fact-registry.md)** - Custom FactRegistry
- **[Contract Deployment](02-contract-deployment.md)** - Contract deployment
- **[Deployment Overview](01-overview.md)** - Architecture

---

**Backend Deployment Summary:** Complete backend deployment with systemd service management, database setup, and monitoring.
