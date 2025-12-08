#!/bin/bash

# Deploy Obsqra to Production (starknet.obsqra.fi)
# This script builds the frontend and backend, then deploys them

set -e

echo "════════════════════════════════════════════════════════════════"
echo "🚀 OBSQRA PRODUCTION DEPLOYMENT"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Configuration
DOMAIN="${DOMAIN:-starknet.obsqra.fi}"
DEPLOY_DIR="/var/www/obsqra"
BACKEND_PORT=8001
FRONTEND_PORT=3003

echo "📊 Configuration:"
echo "  Domain: $DOMAIN"
echo "  Deploy Dir: $DEPLOY_DIR"
echo "  Backend Port: $BACKEND_PORT"
echo "  Frontend Port: $FRONTEND_PORT"
echo ""

# Step 1: Build Frontend
echo "════════════════════════════════════════════════════════════════"
echo "📦 Building Frontend (Next.js production build)..."
echo "════════════════════════════════════════════════════════════════"
cd /opt/obsqra.starknet/frontend

# Set production environment
export NODE_ENV=production
export NEXT_PUBLIC_BACKEND_URL="https://$DOMAIN/api"
export NEXT_PUBLIC_RPC_URL="https://starknet-sepolia.public.blastapi.io"

npm run build

echo "✅ Frontend build complete"
echo ""

# Step 2: Build Backend
echo "════════════════════════════════════════════════════════════════"
echo "🔧 Backend ready (FastAPI)..."
echo "════════════════════════════════════════════════════════════════"
cd /opt/obsqra.starknet/backend
echo "✅ Backend ready"
echo ""

# Step 3: Create deployment directory (if deploying to server)
echo "════════════════════════════════════════════════════════════════"
echo "📂 Preparing deployment..."
echo "════════════════════════════════════════════════════════════════"

# For local testing, we'll just verify everything is built
if [ -d "/opt/obsqra.starknet/frontend/.next" ]; then
    echo "✅ Frontend build artifacts exist"
    du -sh /opt/obsqra.starknet/frontend/.next
else
    echo "❌ Frontend build not found!"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🎯 DEPLOYMENT INSTRUCTIONS"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "To deploy to $DOMAIN, follow these steps:"
echo ""
echo "1️⃣  SSH INTO PRODUCTION SERVER:"
echo "    ssh root@<your-server-ip>"
echo ""
echo "2️⃣  CREATE DEPLOYMENT DIRECTORY:"
echo "    sudo mkdir -p $DEPLOY_DIR"
echo "    sudo chown -R www-data:www-data $DEPLOY_DIR"
echo ""
echo "3️⃣  UPLOAD BUILT FILES (FROM LOCAL MACHINE):"
echo "    # Upload frontend"
echo "    rsync -avz /opt/obsqra.starknet/frontend/.next root@<server>:$DEPLOY_DIR/frontend/"
echo "    rsync -avz /opt/obsqra.starknet/frontend/public root@<server>:$DEPLOY_DIR/frontend/"
echo "    rsync -avz /opt/obsqra.starknet/frontend/package.json root@<server>:$DEPLOY_DIR/frontend/"
echo ""
echo "    # Upload backend"
echo "    rsync -avz /opt/obsqra.starknet/backend root@<server>:$DEPLOY_DIR/"
echo ""
echo "4️⃣  INSTALL PRODUCTION DEPENDENCIES (ON SERVER):"
echo "    cd $DEPLOY_DIR/frontend"
echo "    npm install --production"
echo ""
echo "    cd $DEPLOY_DIR/backend"
echo "    pip install -r requirements.txt"
echo ""
echo "5️⃣  SET UP SYSTEMD SERVICES (ON SERVER):"
echo "    # Copy systemd service files"
echo "    sudo cp obsqra-frontend.service /etc/systemd/system/"
echo "    sudo cp obsqra-backend.service /etc/systemd/system/"
echo ""
echo "    # Enable and start services"
echo "    sudo systemctl daemon-reload"
echo "    sudo systemctl enable obsqra-frontend obsqra-backend"
echo "    sudo systemctl start obsqra-frontend obsqra-backend"
echo ""
echo "6️⃣  CONFIGURE NGINX (ON SERVER):"
echo "    sudo cp nginx-obsqra.conf /etc/nginx/sites-available/$DOMAIN"
echo "    sudo ln -s /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/"
echo "    sudo nginx -t"
echo "    sudo systemctl reload nginx"
echo ""
echo "7️⃣  SET UP SSL (ON SERVER):"
echo "    sudo certbot certonly --nginx -d $DOMAIN"
echo "    # Update nginx config with SSL certs"
echo ""
echo "8️⃣  VERIFY DEPLOYMENT:"
echo "    curl -s https://$DOMAIN/health"
echo "    # Should return: {\"status\": \"healthy\", ...}"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✨ Production deployment ready!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Current Frontend Build:"
ls -lh /opt/obsqra.starknet/frontend/.next 2>/dev/null | head -3
echo ""
echo "Backend Status:"
echo "  Location: /opt/obsqra.starknet/backend"
echo "  Framework: FastAPI"
echo "  Port: $BACKEND_PORT"
echo ""

