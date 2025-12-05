# Move Starknet Frontend to Port 3001

## Problem
Port 3001 is currently occupied by another process (likely the obsqra.fi frontend managed by PM2).

## Solution: Run These Commands

### Option 1: Quick Method (Try this first)
```bash
# Stop PM2 managed frontend
pm2 stop obsqra-frontend

# Kill anything else on port 3001  
lsof -ti:3001 | xargs kill -9

# Wait a moment
sleep 2

# Start the Starknet frontend on port 3001
cd /opt/obsqra.starknet/frontend
PORT=3001 npm run dev
```

### Option 2: Nuclear Option (if Option 1 doesn't work)
```bash
# Stop all PM2 processes
pm2 stop all

# Kill all node processes
killall -9 node

# Wait a moment
sleep 3

# Start the Starknet frontend on port 3001
cd /opt/obsqra.starknet/frontend
PORT=3001 npm run dev
```

### Option 3: Keep Both Running (Recommended)
If you want to keep the obsqra.fi frontend running:

```bash
# Just use the already-working port 3002
cd /opt/obsqra.starknet/frontend
PORT=3002 npm run dev
```

Access at: **http://localhost:3002**

## Verify It's Working
After starting the server, you should see:
```
▲ Next.js 14.2.33
- Local:        http://localhost:3001

✓ Starting...
✓ Ready in 1321ms
```

Then open http://localhost:3001 in your browser.

## If You Get "EADDRINUSE" Error
The port is still in use. Try these diagnostic commands:

```bash
# Find what's using port 3001
lsof -i :3001

# Or using ss
ss -tlnp | grep :3001

# Get the PID and kill it manually
kill -9 <PID>
```

## Status
- ✅ Package dependencies updated and installed
- ✅ StarknetProvider.tsx fixed
- ✅ Server works on port 3002
- ⏳ Waiting to move to port 3001

## Alternative: Update PM2 Config
If you want the obsqra.fi frontend on a different port:

Edit `/opt/obsqra.fi/ecosystem.config.js`:
```javascript
env: {
  NODE_ENV: 'development',
  NODE_OPTIONS: '--max-old-space-size=3072',
  PORT: 3000  // Change this to 3003 or another port
}
```

Then:
```bash
pm2 restart obsqra-frontend
```
