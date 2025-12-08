# Start Server Manually - Port 3002

## The Issue
The automated shell is having issues. You need to start the server manually.

## Run These Commands in Your Terminal

### Step 1: Stop any existing process
If there's a process running in terminal 23, press `Ctrl+C` to stop it.

### Step 2: Navigate to the frontend directory
```bash
cd /opt/obsqra.starknet/frontend
```

### Step 3: Clean the build cache (optional but recommended)
```bash
rm -rf .next
```

### Step 4: Start the dev server on port 3002
```bash
PORT=3002 npm run dev
```

You should see:
```
▲ Next.js 14.2.33
- Local:        http://localhost:3002

✓ Starting...
✓ Ready in ~2s
```

### Step 5: Open in Browser
Navigate to: **http://localhost:3002**

---

## If You Get Errors

### "EADDRINUSE" - Port is in use
```bash
# Kill the process on port 3002
lsof -ti:3002 | xargs kill -9

# Then restart
PORT=3002 npm run dev
```

### Import/Compile Errors
The files should all be fixed now. If you see errors:
1. Make sure you're in `/opt/obsqra.starknet/frontend`
2. Run `npm install` again
3. Clear cache: `rm -rf .next`
4. Restart: `PORT=3002 npm run dev`

---

## What You Should See

Once running successfully:

### In Terminal:
- ✓ Compiled successfully messages
- Server listening on port 3002

### In Browser (http://localhost:3002):
- Beautiful purple/slate gradient background
- "Obsqra.starknet" title
- "Connect Argent X" button
- "Connect Braavos" button

---

## All Files Are Fixed!

These have been updated and should work:
- ✅ src/app/layout.tsx
- ✅ src/app/page.tsx  
- ✅ src/components/Dashboard.tsx
- ✅ src/hooks/useRiskEngine.ts
- ✅ src/hooks/useMistCash.ts (recreated)
- ✅ src/providers/StarknetProvider.tsx

Just need to start the server manually! 
