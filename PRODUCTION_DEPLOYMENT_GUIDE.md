# Production Deployment Guide

## Current Status

✅ **Frontend built and ready to deploy**
- Build output: `/opt/obsqra.starknet/frontend/.next/`
- Domain: `starknet.obsqra.fi` (resolves to `5.181.218.40`)
- Port: Ready for port 3003 or any port on production server

---

## Deployment Options

### Option 1: Simple SSH + pm2 (Recommended for Speed)

```bash
# 1. SSH to production server
ssh root@5.181.218.40

# 2. Navigate to project
cd /opt/obsqra.starknet/frontend

# 3. Pull latest code
git pull origin main

# 4. Install dependencies
npm install

# 5. Build
npm run build

# 6. Start with pm2
pm2 start npm --name "obsqra-frontend" -- start -- -p 3003

# 7. Make it restart on reboot
pm2 startup
pm2 save
```

### Option 2: Docker (More Reliable)

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3003

CMD ["npm", "start", "--", "-p", "3003"]
```

Deploy:
```bash
docker build -t obsqra-frontend .
docker run -d -p 3003:3003 --name obsqra-frontend obsqra-frontend
```

### Option 3: Nginx Reverse Proxy (Production Standard)

```nginx
# /etc/nginx/sites-available/obsqra
server {
    listen 80;
    server_name starknet.obsqra.fi;

    location / {
        proxy_pass http://localhost:3003;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/obsqra /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## What I Can Do

I can help with:
1. ✅ Building the frontend (DONE)
2. ✅ Creating deployment scripts
3. ✅ Creating Docker configuration
4. ✅ Creating Nginx configuration
5. ⏳ Uploading to your server (need SSH credentials or specific instructions)

---

## What You Need to Do

1. **Provide access** - Either:
   - SSH credentials to `5.181.218.40`
   - OR existing deployment method/instructions
   - OR deployment key/script

2. **Choose deployment method**:
   - Simple (pm2): Fast, good for dev/test
   - Docker: Most reliable
   - Nginx: Production standard

3. **Verify domain DNS** - Make sure `starknet.obsqra.fi` points to correct IP

---

## Quick Deployment (pm2)

If you give me SSH access, I can deploy immediately:

```bash
# 1. SSH to server
# 2. Copy latest code
# 3. Install dependencies
# 4. Build
# 5. Start with pm2
# Total time: ~5 minutes
```

---

## How to Give Me Access

**Option A: SSH Key**
```
Send me your SSH key and I can SSH directly
```

**Option B: Deployment Script**
```
If you have an existing script or method, send the details
```

**Option C: Manual Steps**
```
Tell me what command to run and where, I'll create the exact steps
```

---

## Frontend is Ready

The built frontend is in:
```
/opt/obsqra.starknet/frontend/.next/
/opt/obsqra.starknet/frontend/node_modules/
```

Can be:
- Copied to production server
- Deployed as Docker image
- Run with `npm start`

---

## Next Step

**Tell me your preferred deployment method and how to access the production server**, and I'll get it live on `starknet.obsqra.fi` immediately!

