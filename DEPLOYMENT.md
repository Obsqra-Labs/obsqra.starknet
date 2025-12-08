# Deployment Guide

## Contract Addresses

### Starknet Sepolia Testnet

| Contract | Address | Status |
|----------|---------|--------|
| RiskEngine v2 | `0x0751c85290c660d738236a12bb362bf64c0a8ef4b1a9cc05dc7000d14fd44d31` | Active |
| StrategyRouterV2 | `0x0539d5611c6158a4234f7c4e8e7fe50af7b9502314ca95409f5106ee2f6741d6` | Active |
| DAOConstraintManager | `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856` | Active |

### Protocol Integration Addresses

| Protocol | Address |
|----------|---------|
| JediSwap Router | `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21` |
| Ekubo Core | `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384` |
| STRK Token | `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1` |

## Backend Deployment

### Environment Configuration

Create `/opt/obsqra.starknet/backend/.env`:

```env
# Starknet Configuration
STARKNET_RPC_URL=https://starknet-sepolia-rpc.publicnode.com
RISK_ENGINE_ADDRESS=0x0751c85290c660d738236a12bb362bf64c0a8ef4b1a9cc05dc7000d14fd44d31
STRATEGY_ROUTER_ADDRESS=0x0539d5611c6158a4234f7c4e8e7fe50af7b9502314ca95409f5106ee2f6741d6

# Backend Orchestrator Account
BACKEND_WALLET_ADDRESS=<YOUR_WALLET_ADDRESS>
BACKEND_WALLET_PRIVATE_KEY=<YOUR_PRIVATE_KEY>

# Server Configuration
API_PORT=8001
ENVIRONMENT=production
```

### Service Management

```bash
# Start backend service
cd /opt/obsqra.starknet/backend
python3 main.py

# Or use systemd
sudo systemctl start obsqra-backend
sudo systemctl enable obsqra-backend
```

## Frontend Deployment

### Environment Configuration

Create `/opt/obsqra.starknet/frontend/.env.local`:

```env
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia-rpc.publicnode.com
NEXT_PUBLIC_BACKEND_URL=
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x0539d5611c6158a4234f7c4e8e7fe50af7b9502314ca95409f5106ee2f6741d6
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=0x0751c85290c660d738236a12bb362bf64c0a8ef4b1a9cc05dc7000d14fd44d31
NEXT_PUBLIC_NETWORK=sepolia
```

### Build and Deploy

```bash
cd /opt/obsqra.starknet/frontend
npm install
npm run build
npm start -- -p 3003
```

## Nginx Configuration

### Reverse Proxy Setup

File: `/etc/nginx/conf.d/starknet-obsqra.conf`

```nginx
server {
    listen 443 ssl http2;
    server_name starknet.obsqra.fi;

    ssl_certificate /etc/letsencrypt/live/starknet.obsqra.fi/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/starknet.obsqra.fi/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:3003;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Apply Configuration

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Contract Deployment

### Prerequisites

- Starknet Foundry installed
- Funded deployer account
- RPC endpoint configured

### Build Contracts

```bash
cd /opt/obsqra.starknet/contracts
snforge build
```

### Deploy to Testnet

```bash
# Deploy RiskEngine
sncast --profile deployer deploy \
  --class-hash <RISK_ENGINE_CLASS_HASH> \
  --constructor-calldata <OWNER> <ROUTER> <DAO_MANAGER>

# Deploy StrategyRouterV2
sncast --profile deployer deploy \
  --class-hash <ROUTER_CLASS_HASH> \
  --constructor-calldata <OWNER> <JEDISWAP> <EKUBO> <RISK_ENGINE> <DAO> <STRK_TOKEN>
```

## Verification

### Backend Health Check

```bash
curl https://starknet.obsqra.fi/api/health
```

### Frontend Access

Navigate to: `https://starknet.obsqra.fi`

### Contract Verification

View contracts on Starkscan:
- https://sepolia.starkscan.co/contract/<CONTRACT_ADDRESS>

## Monitoring

### Service Status

```bash
# Backend
ps aux | grep "python.*main.py"

# Frontend  
ps aux | grep "node.*next"

# Nginx
sudo systemctl status nginx
```

### Logs

```bash
# Backend logs
tail -f /tmp/backend.log

# Frontend logs
tail -f /tmp/frontend.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

## Troubleshooting

### Backend Not Starting

1. Check environment variables in `.env`
2. Verify Python dependencies: `pip install -r requirements.txt`
3. Check port availability: `netstat -tlnp | grep 8001`

### Frontend Build Failures

1. Clear Next.js cache: `rm -rf .next`
2. Reinstall dependencies: `rm -rf node_modules && npm install`
3. Check Node version: `node --version` (requires 18+)

### Transaction Failures

1. Verify backend wallet has sufficient ETH for gas
2. Check RPC endpoint is responding
3. Verify contract addresses in configuration
4. Review DAO constraints configuration

## Security Notes

- Keep `.env` files secure (never commit to git)
- Rotate backend wallet private key regularly
- Use HTTPS for all production endpoints
- Monitor contract events for unauthorized access attempts
- Implement rate limiting on API endpoints

