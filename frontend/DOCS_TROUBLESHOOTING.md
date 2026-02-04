# Documentation Route Troubleshooting

## Quick Fixes

### 1. Restart Next.js Dev Server
```bash
cd frontend
# Stop the server (Ctrl+C)
npm run dev
```

### 2. Clear Next.js Cache
```bash
cd frontend
rm -rf .next
npm run dev
```

### 3. Verify Route Structure
```bash
# Check these files exist:
ls -la src/app/docs/page.tsx
ls -la "src/app/docs/[...slug]/page.tsx"
ls -la src/app/docs/layout.tsx
```

### 4. Test Routes
- `/docs` - Should redirect to overview
- `/docs/test` - Simple test page
- `/docs/01-introduction/01-overview` - First doc page

### 5. Check Server Logs
Look for `[Docs]` prefixed logs in the Next.js console:
- `[Docs] Requested path: ...`
- `[Docs] Full file path: ...`
- `[Docs] File exists: ...`

### 6. Verify File Paths
```bash
# From frontend directory:
node -e "const path = require('path'); console.log(path.resolve(process.cwd(), '../docs'));"
# Should output: /opt/obsqra.starknet/docs
```

## Common Issues

### Issue: 404 on all routes
**Solution:** Restart dev server and clear `.next` cache

### Issue: File not found errors
**Check:** 
- Docs directory exists at `/opt/obsqra.starknet/docs`
- File path in logs matches actual file location

### Issue: Route not matching
**Check:**
- Directory name is exactly `[...slug]` (with brackets)
- File is named `page.tsx` (not `page.js`)

### Issue: Import errors
**Check:**
- All components exist in `src/components/docs/`
- All imports use `@/` alias correctly

## Debug Mode

The route includes extensive logging. Check the Next.js server console for:
- Requested paths
- File paths being checked
- Whether files exist
- Directory contents if file not found

## Manual Test

1. Start dev server: `cd frontend && npm run dev`
2. Visit: `http://localhost:3003/docs/test`
3. Should see "Route Test Works!" message
4. If that works, try: `http://localhost:3003/docs/01-introduction/01-overview`
