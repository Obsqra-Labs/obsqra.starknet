# Deploy zkde.fi to Hostinger

## Prerequisites

- zkde.fi domain configured on Hostinger
- Hostinger hosting account with Node.js support
- Backend API running somewhere accessible (or deploy separately)

## Deployment options

### Option 1: Deploy as Node.js application (recommended)

The zkdefi frontend is a Next.js app that can be deployed as a full Node.js application to Hostinger.

**Steps:**

1. **Create deployment archive** (from zkdefi/frontend directory):
   ```bash
   cd /opt/obsqra.starknet/zkdefi/frontend
   
   # Create archive with source files (NOT build output)
   # Exclude node_modules, .next, .git
   tar --exclude='node_modules' \
       --exclude='.next' \
       --exclude='.git' \
       --exclude='.env.local' \
       -czf zkdefi-frontend-$(date +%Y%m%d_%H%M%S).tar.gz \
       .
   ```

2. **Deploy via Hostinger MCP** (when ready):
   ```python
   # Use hosting_deployJsApplication
   # Domain: zkde.fi
   # Archive: path to zkdefi-frontend-*.tar.gz
   # Build will run automatically on Hostinger
   ```

3. **Environment variables** (set on Hostinger after deployment):
   - `NEXT_PUBLIC_API_URL` - Backend API URL (e.g., https://api.zkde.fi or https://starknet.obsqra.fi/api/v1/zkdefi)
   - `NEXT_PUBLIC_PROOF_GATED_AGENT_ADDRESS` - Contract address
   - `NEXT_PUBLIC_SELECTIVE_DISCLOSURE_ADDRESS` - Contract address
   - `NEXT_PUBLIC_CONFIDENTIAL_TRANSFER_ADDRESS` - Contract address
   - `NEXT_PUBLIC_STARKNET_CHAIN_ID` - 0x534e5f5345504f4c4941 (Sepolia)

### Option 2: Deploy as static website

If you prefer static export (faster, no Node.js runtime needed):

1. **Build static export**:
   ```bash
   cd /opt/obsqra.starknet/zkdefi/frontend
   
   # Update next.config.js to add:
   # output: 'export',
   
   npm run build
   # This creates 'out/' directory with static files
   
   # Create archive
   cd out
   tar -czf zkdefi-static-$(date +%Y%m%d_%H%M%S).tar.gz *
   ```

2. **Deploy via Hostinger MCP**:
   ```python
   # Use hosting_deployStaticWebsite
   # Domain: zkde.fi
   # Archive: path to zkdefi-static-*.tar.gz
   ```

**Note:** Static export may not work if you're using server-side features (API routes, middleware, etc.). For zkdefi, Option 1 (Node.js) is recommended.

## Backend deployment

The FastAPI backend needs to run separately. Options:

1. **Same Hostinger account** (if you have VPS or appropriate plan)
   - Deploy Python app alongside frontend
   - Use subdomain like `api.zkde.fi`

2. **Current server** (starknet.obsqra.fi)
   - Keep backend at `starknet.obsqra.fi/api/v1/zkdefi`
   - Set `NEXT_PUBLIC_API_URL=https://starknet.obsqra.fi`

3. **Separate service** (Render, Railway, etc.)
   - Deploy backend independently
   - Point frontend to that URL

## DNS Configuration

After deployment, ensure zkde.fi DNS points to Hostinger:

- **If Hostinger manages DNS**: Should auto-configure
- **If external DNS**: Point A record to Hostinger server IP
- **SSL**: Hostinger should auto-provision Let's Encrypt certificate

## Quick deployment script

When ready to deploy, run:

```bash
cd /opt/obsqra.starknet/zkdefi
./deploy_zkdefi_to_hostinger.sh
```

(Script to be created - will archive frontend and use Hostinger MCP to deploy)

## Post-deployment checklist

- [ ] Frontend live at https://zkde.fi
- [ ] Landing page loads with agent narrative
- [ ] Connect wallet works (Argent/Braavos on Sepolia)
- [ ] Backend API accessible (check /api/v1/zkdefi/health)
- [ ] Contracts deployed on Sepolia
- [ ] Environment variables set correctly
- [ ] SSL certificate active (HTTPS)

## Rollback

If deployment fails, Hostinger keeps previous deployments. Use Hostinger panel to rollback or redeploy.
