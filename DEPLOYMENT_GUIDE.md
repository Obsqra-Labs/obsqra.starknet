# Production Deployment Guide

**Domain:** https://starknet.obsqra.fi  
**Status:** Ready for deployment

---

## Quick Start

### For Immediate Testing (Localhost)
```bash
# Terminal 1: Backend
cd /opt/obsqra.starknet/backend
API_PORT=8001 python3 main.py

# Terminal 2: Frontend
cd /opt/obsqra.starknet/frontend
PORT=3003 npm start

# Access: http://localhost:3003
```

### For Production Deployment

#### Step 1: Build Production Assets
```bash
cd /opt/obsqra.starknet
bash deploy-to-production.sh
```

This will:
- ✅ Build Next.js frontend for production
- ✅ Verify backend is ready
- ✅ Display deployment instructions

#### Step 2: Deploy to Server

**Option A: Manual Deployment (Recommended)**

1. **SSH into your production server:**
```bash
ssh root@<your-server-ip>
```

2. **Create deployment directory:**
```bash
sudo mkdir -p /var/www/obsqra
sudo chown -R $USER:$USER /var/www/obsqra
```

3. **Upload files (from your local machine):**
```bash
# Upload frontend build
rsync -avz /opt/obsqra.starknet/frontend/.next root@<server>:/var/www/obsqra/frontend/.next
rsync -avz /opt/obsqra.starknet/frontend/public root@<server>:/var/www/obsqra/frontend/public
rsync -avz /opt/obsqra.starknet/frontend/package.json root@<server>:/var/www/obsqra/frontend/

# Upload entire backend
rsync -avz /opt/obsqra.starknet/backend root@<server>:/var/www/obsqra/backend
```

4. **Install dependencies (on server):**
```bash
# Frontend
cd /var/www/obsqra/frontend
npm install --production

# Backend
cd /var/www/obsqra/backend
pip install -r requirements.txt
```

5. **Set up Node.js processes (on server):**
```bash
# Install PM2 for process management
npm install -g pm2

# Start frontend
cd /var/www/obsqra/frontend
pm2 start "npm start" --name obsqra-frontend

# Start backend
cd /var/www/obsqra/backend
pm2 start "python3 main.py" --name obsqra-backend

# Save PM2 configuration
pm2 save
pm2 startup

# Check status
pm2 status
```

6. **Configure Nginx (on server):**
```bash
# Copy Nginx config
sudo cp /path/to/nginx-obsqra.conf /etc/nginx/sites-available/starknet.obsqra.fi

# Enable site
sudo ln -s /etc/nginx/sites-available/starknet.obsqra.fi /etc/nginx/sites-enabled/

# Test Nginx config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

7. **Set up SSL Certificate (on server):**
```bash
# Install certbot if needed
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot certonly --nginx -d starknet.obsqra.fi

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

8. **Verify Deployment:**
```bash
# Check backend health
curl https://starknet.obsqra.fi/health

# Should return:
# {"status": "healthy", "service": "obsqra-backend", "version": "1.0.0"}

# Check frontend loads
curl -I https://starknet.obsqra.fi/
# Should return 200 OK
```

---

## Architecture

```
Browser (User)
     ↓
Nginx (Reverse Proxy) - starknet.obsqra.fi
     ↓
Frontend (Next.js) - localhost:3003
Backend (FastAPI) - localhost:8001
     ↓
Starknet (Sepolia)
```

---

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_BACKEND_URL=https://starknet.obsqra.fi/api
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia.public.blastapi.io
NEXT_PUBLIC_RISK_ENGINE_ADDRESS=0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80
NEXT_PUBLIC_MIST_CHAMBER_ADDRESS=0x...
```

### Backend (.env)
```
API_HOST=0.0.0.0
API_PORT=8001
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost:5432/obsqra
```

---

## Monitoring

### Check Service Status
```bash
# Using PM2
pm2 status

# Using systemctl (if using systemd services)
sudo systemctl status obsqra-frontend
sudo systemctl status obsqra-backend
```

### View Logs
```bash
# PM2 logs
pm2 logs obsqra-frontend
pm2 logs obsqra-backend

# Nginx logs
tail -f /var/log/nginx/obsqra-access.log
tail -f /var/log/nginx/obsqra-error.log

# System logs
journalctl -u obsqra-frontend -f
journalctl -u obsqra-backend -f
```

### Performance Monitoring
```bash
# Monitor resources
pm2 monit

# Check Nginx connections
netstat -an | grep :443

# Check API response time
curl -w "Response time: %{time_total}s\n" https://starknet.obsqra.fi/health
```

---

## Troubleshooting

### Issue: 502 Bad Gateway
**Cause:** Backend not running or not responding

**Solution:**
```bash
# Check if backend is running
ps aux | grep "python3 main.py"

# Restart backend
pm2 restart obsqra-backend

# Check backend logs
pm2 logs obsqra-backend
```

### Issue: MIME Type Errors (text/html instead of application/javascript)
**Cause:** Static assets not being served correctly

**Solution:**
```bash
# Clear Nginx cache
rm -rf /var/cache/nginx/*

# Ensure Next.js build completed
ls -la /var/www/obsqra/frontend/.next/static/

# Reload Nginx
sudo systemctl reload nginx
```

### Issue: Connection Refused
**Cause:** Ports blocked or services not listening

**Solution:**
```bash
# Check if ports are open
sudo netstat -tlnp | grep -E "3003|8001"

# Check firewall
sudo ufw status

# Open ports if needed
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Issue: SSL Certificate Issues
**Cause:** Certificate expired or misconfigured

**Solution:**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

---

## Backup & Recovery

### Backup Database
```bash
# PostgreSQL backup (when database is configured)
pg_dump obsqra_db > /backups/obsqra_db_$(date +%Y%m%d).sql
```

### Backup Configuration
```bash
# Backup Nginx config
sudo tar -czf /backups/nginx-backup.tar.gz /etc/nginx/

# Backup application
tar -czf /backups/obsqra-app-$(date +%Y%m%d).tar.gz /var/www/obsqra/
```

### Restore from Backup
```bash
# Stop services
pm2 stop all

# Restore files
tar -xzf /backups/obsqra-app-DATE.tar.gz -C /

# Restart services
pm2 start all
```

---

## Scaling

### Load Balancing
When you need to handle more traffic:

1. **Multiple Frontend Instances:**
```bash
pm2 start "npm start" --name obsqra-frontend-1
pm2 start "npm start" --name obsqra-frontend-2
```

2. **Nginx Load Balancing:**
```nginx
upstream frontend_backend {
    least_conn;
    server localhost:3003;
    server localhost:3004;
    server localhost:3005;
}

location / {
    proxy_pass http://frontend_backend;
}
```

### Database Scaling
```bash
# When volume exceeds in-memory limits, configure PostgreSQL
# Update backend/.env with real DATABASE_URL
DATABASE_URL=postgresql://user:pass@db-server:5432/obsqra
```

---

## Security Checklist

- [ ] SSL certificate installed and auto-renewing
- [ ] Environment variables set securely (not in code)
- [ ] Database credentials in .env (not visible)
- [ ] Firewall configured (only ports 80, 443 open)
- [ ] SSH key authentication (no passwords)
- [ ] Regular backups enabled
- [ ] Monitoring and alerting set up
- [ ] Rate limiting on API endpoints
- [ ] CORS properly configured
- [ ] Security headers added to Nginx

---

## Post-Deployment Testing

### 1. Test Authentication
```bash
curl -X POST https://starknet.obsqra.fi/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@obsqra.io","password":"TestPassword123"}'
```

### 2. Test Proof Generation
```bash
curl -X POST https://starknet.obsqra.fi/api/v1/proofs/risk-score \
  -H "Content-Type: application/json" \
  -d '{
    "utilization": 6500,
    "volatility": 3500,
    "liquidity": 1,
    "audit_score": 98,
    "age_days": 800
  }'
```

### 3. Test Frontend
- Visit https://starknet.obsqra.fi
- Create account
- Connect wallet
- Generate proofs
- Update allocation

---

## Support

For issues or questions:
1. Check logs: `pm2 logs`
2. Check Nginx config: `sudo nginx -t`
3. Test API: `curl https://starknet.obsqra.fi/health`
4. Check processes: `pm2 status`

---

**Deployment Status:** ✅ Ready for Production

All files are prepared and tested. Follow the steps above to deploy to your production server.

