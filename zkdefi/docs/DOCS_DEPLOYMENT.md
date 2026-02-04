# Docs Deployment to docs.zkde.fi

## Current Status
- Docs built at: `docs-site/docs/.vitepress/dist`
- Archive created: `/tmp/docs_zkde_fi_*.tar.gz`

## Deployment Steps

### Option 1: Create Subdomain in Hostinger
1. Log into Hostinger hPanel
2. Go to Domains → Subdomains
3. Create subdomain: `docs.zkde.fi`
4. Point it to a directory (e.g., `public_html/docs` or create new directory)
5. Use Hostinger MCP tool to deploy:
   ```bash
   # Archive is ready at: /tmp/docs_zkde_fi_*.tar.gz
   ```

### Option 2: Deploy to Main Domain Subdirectory
If subdomain isn't available, deploy to `zkde.fi/docs/`:
1. Extract archive to a `docs` subdirectory
2. Access at: `https://zkde.fi/docs/`

## Archive Location
Latest archive: `/tmp/docs_zkde_fi_*.tar.gz` (737KB)

## Build Command
```bash
cd docs-site
npm install
npm run build
# Output: docs/.vitepress/dist
```

