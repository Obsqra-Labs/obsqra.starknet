# 🚀 Local Setup Guide - No Docker Needed!

## ✅ Current Status

Your system is **already fully running locally** with all services operational!

```
✅ Frontend (Next.js 14)      - Running on port 3003
✅ Backend (FastAPI)           - Running on port 8000
✅ Database (PostgreSQL)       - Running on port 5432
```

---

## 📊 Services Running

### Frontend - Next.js 14
- **Port**: 3003
- **URL**: http://localhost:3003
- **Status**: ✅ RUNNING
- **Technology**: React 18, TypeScript, Tailwind CSS

### Backend - FastAPI
- **Port**: 8000
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Status**: ✅ RUNNING
- **Technology**: Python 3.12, FastAPI, async/await

### Database - PostgreSQL
- **Port**: 5432
- **Connection**: postgresql://obsqra:obsqra@localhost:5432/obsqra_db
- **Status**: ✅ RUNNING
- **Technology**: PostgreSQL 15 (local installation)

---

## 🎯 What's Already Set Up

### Frontend
```bash
Location: /opt/obsqra.starknet/frontend
Process: next-server (v1) on port 3003
Started: Before this session
Status: ✅ LIVE
```

**What you can do:**
- Visit http://localhost:3003
- See the dashboard
- View risk analytics
- See proof display
- Test MIST integration
- Monitor transactions

### Backend
```bash
Location: /opt/obsqra.starknet/backend
Process: python main.py
Port: 8000
Status: ✅ RUNNING
```

**Available endpoints:**
- Health check: `GET /health`
- API docs: `GET /docs`
- 16 API endpoints ready
- ML models loaded
- Database connected

### Database
```bash
Location: Local PostgreSQL installation
Port: 5432
Database: obsqra_db
User: obsqra
Status: ✅ RUNNING
```

**6 tables created:**
- users
- risk_history
- allocation_history
- transactions
- predictions
- analytics_cache

---

## 🔧 How It's All Set Up Locally

### 1. Frontend Setup
```bash
# Already installed and running
/opt/obsqra.starknet/frontend
├── node_modules/ (all dependencies installed)
├── src/ (React components)
├── public/ (static assets)
├── .env.local (configured with contract addresses)
└── package.json (dependencies locked)

# Started with:
npm run dev  # Running on port 3003
```

### 2. Backend Setup
```bash
# Python environment
/opt/obsqra.starknet/backend
├── main.py (FastAPI entry point)
├── app/ (application code)
├── requirements.txt (24 dependencies)
└── .env (configured)

# Running with:
python3 main.py  # Or uvicorn main:app
# Listening on port 8000
```

### 3. Database Setup
```bash
# PostgreSQL local installation
# Connection: postgresql://obsqra:obsqra@localhost:5432/obsqra_db

# Tables created via SQLAlchemy models
# Migrations ready (Alembic)
```

---

## 🌐 Access Points

### Visit the Application
```
Frontend:     http://localhost:3003
Backend API:  http://localhost:8000
API Docs:     http://localhost:8000/docs
```

### Test the System

**1. Check Frontend**
```bash
curl http://localhost:3003
# Returns: HTML of Next.js app
```

**2. Check Backend**
```bash
curl http://localhost:8000/health
# Response: {"status":"healthy","model_loaded":true,"timestamp":"..."}
```

**3. View API Documentation**
```
http://localhost:8000/docs
# Interactive Swagger UI with all endpoints
```

---

## 🛠️ Managing Local Services

### Check What's Running
```bash
ss -tlnp | grep -E "3003|8000|5432"
# Shows all three services with PIDs
```

### Stop Frontend (if needed)
```bash
pkill -f "next-server"
# Or: kill <PID>
```

### Stop Backend (if needed)
```bash
pkill -f "python.*main.py"
# Or: kill <PID>
```

### Stop Database (if needed)
```bash
sudo systemctl stop postgresql
# Or on Mac: brew services stop postgresql
```

### Restart Frontend
```bash
cd /opt/obsqra.starknet/frontend
npm run dev
```

### Restart Backend
```bash
cd /opt/obsqra.starknet/backend
python3 main.py
# Or: uvicorn main:app --reload
```

### Restart Database
```bash
sudo systemctl start postgresql
# Or on Mac: brew services start postgresql
```

---

## 📝 Complete Local Setup From Scratch

If you ever need to set up everything fresh locally:

### Step 1: Install Prerequisites
```bash
# macOS
brew install postgresql node python@3.12

# Linux (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib nodejs python3.12 python3.12-venv

# Windows
# Download and install:
# - PostgreSQL: https://www.postgresql.org/download/windows/
# - Node.js: https://nodejs.org/
# - Python: https://www.python.org/downloads/
```

### Step 2: Start PostgreSQL
```bash
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Windows
# Should start automatically with installation
```

### Step 3: Create Database
```bash
createdb obsqra_db
psql obsqra_db -c "CREATE USER obsqra WITH PASSWORD 'obsqra';"
psql obsqra_db -c "GRANT ALL PRIVILEGES ON DATABASE obsqra_db TO obsqra;"
```

### Step 4: Setup Frontend
```bash
cd /opt/obsqra.starknet/frontend
npm install  # If not already done
npm run dev
# Running on port 3003
```

### Step 5: Setup Backend
```bash
cd /opt/obsqra.starknet/backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 main.py
# Running on port 8000
```

---

## 🎯 Testing Everything Works

### Test 1: Frontend Is Running
```bash
curl -s http://localhost:3003 | head -c 50
# Should return HTML
```

### Test 2: Backend Is Running
```bash
curl http://localhost:8000/health
# Should return JSON with status: healthy
```

### Test 3: Database Is Connected
```bash
psql postgresql://obsqra:obsqra@localhost:5432/obsqra_db -c "SELECT * FROM users;"
# Should return empty table or users
```

### Test 4: API Endpoints Work
```bash
# List users
curl http://localhost:8000/api/v1/users/

# Get dashboard
curl http://localhost:8000/api/v1/analytics/dashboard

# Get predictions
curl http://localhost:8000/api/v1/predictions/
```

---

## 📊 Local System Architecture

```
Your Computer
│
├── Frontend Server (Next.js)
│   ├── Process: node next-server
│   ├── Port: 3003
│   ├── Path: /opt/obsqra.starknet/frontend
│   └── Status: ✅ RUNNING
│
├── Backend Server (FastAPI)
│   ├── Process: python main.py
│   ├── Port: 8000
│   ├── Path: /opt/obsqra.starknet/backend
│   └── Status: ✅ RUNNING
│
└── Database (PostgreSQL)
    ├── Process: postgres
    ├── Port: 5432
    ├── Database: obsqra_db
    └── Status: ✅ RUNNING

All communicating via localhost
```

---

## 🚀 Development Workflow (Local)

### 1. Make Frontend Changes
```bash
# Edit files in: /opt/obsqra.starknet/frontend/src
# Changes automatically reload (HMR)
# Visit http://localhost:3003 to see
```

### 2. Make Backend Changes
```bash
# Edit files in: /opt/obsqra.starknet/backend/app
# Run with reload:
cd backend
uvicorn main:app --reload
# Visit http://localhost:8000/docs
```

### 3. Check Database
```bash
# Connect to PostgreSQL
psql postgresql://obsqra:obsqra@localhost:5432/obsqra_db

# Useful queries
\dt                    # List tables
SELECT * FROM users;   # See users
SELECT * FROM risk_history LIMIT 5;  # See risk data
\q                     # Quit
```

---

## 🔍 Common Operations

### View Backend Logs
```bash
# If running in terminal:
# Logs appear directly

# Or check system logs:
journalctl -u postgresql  # PostgreSQL logs
```

### Reset Database
```bash
# Drop and recreate
dropdb obsqra_db
createdb obsqra_db
psql obsqra_db < schema.sql  # If you have schema file

# Or let SQLAlchemy recreate tables
# by restarting backend
```

### Clear Frontend Cache
```bash
cd /opt/obsqra.starknet/frontend
rm -rf .next
npm run dev  # Rebuilds
```

### Update Dependencies
```bash
# Frontend
cd frontend
npm update

# Backend
cd backend
pip install --upgrade -r requirements.txt
```

---

## ⚙️ Configuration Files

### Frontend Configuration
```
Location: /opt/obsqra.starknet/frontend/.env.local
Contains: 
  - NEXT_PUBLIC_RPC_URL
  - Contract addresses
  - API endpoint
```

### Backend Configuration
```
Location: /opt/obsqra.starknet/backend/.env
Contains:
  - DATABASE_URL
  - SECRET_KEY
  - STARKNET settings
  - ML settings
```

### Database Connection
```
URL: postgresql://obsqra:obsqra@localhost:5432/obsqra_db
User: obsqra
Password: obsqra
Database: obsqra_db
```

---

## 📱 Testing the Full System

### User Registration Flow
```bash
# 1. Frontend shows signup at http://localhost:3003
# 2. User submits email + password
# 3. Backend receives at POST /api/v1/auth/register
# 4. Stores in PostgreSQL users table
# 5. Returns JWT token
# 6. Frontend stores token and redirects
```

### View Analytics
```bash
# 1. User logs in
# 2. Frontend calls GET /api/v1/analytics/dashboard
# 3. Backend queries risk_history, allocation_history
# 4. Returns aggregated data
# 5. Frontend displays charts and metrics
```

### Run Optimization
```bash
# 1. User clicks "Calculate Risk"
# 2. Frontend calls POST /api/v1/predictions/run-optimization
# 3. Backend loads ML models
# 4. Calculates allocation
# 5. Stores result in predictions table
# 6. Returns to frontend
```

---

## 🎓 Useful Commands

### Monitor Ports
```bash
# See what's using ports 3003, 8000, 5432
lsof -i :3003
lsof -i :8000
lsof -i :5432
```

### Check Processes
```bash
ps aux | grep -E "node|python|postgres"
```

### Test Connectivity
```bash
# Frontend to Backend
curl http://localhost:8000/health

# Backend to Database
psql postgresql://obsqra:obsqra@localhost:5432/obsqra_db -c "SELECT 1;"

# Database to Frontend
# (No direct connection - frontend uses backend as proxy)
```

### View Network Activity
```bash
# Linux/Mac
sudo tcpdump -i lo -n 'tcp port 3003 or tcp port 8000 or tcp port 5432'
```

---

## 📚 Documentation for Local Development

### See Also
- `backend/README.md` - Backend guide
- `backend/QUICKSTART.md` - Quick reference
- `frontend/package.json` - Frontend dependencies
- `SPRINT_SUMMARY.md` - Project overview

---

## 🎉 Summary

**You have a fully functional local development environment!**

✅ Frontend running and accessible  
✅ Backend running with all endpoints  
✅ Database connected and ready  
✅ All systems communicating  
✅ Ready for development  

### Next Steps:
1. **Visit**: http://localhost:3003
2. **Test**: Signup and explore
3. **Develop**: Make changes as needed
4. **Deploy**: Use Docker when ready for production

### No Docker needed for local development!

All three services are running natively on your machine and ready to use. 🚀


