# Starting Network Monitoring GUI

## Quick Start Instructions

### Step 1: Start Backend (if not already running)
Backend appears to be running on port 8000. If not, start it:

```bash
cd backend_api
python main.py
```

### Step 2: Start Frontend Dev Server

Open a **new terminal window** and run:

```bash
cd frontend
npm run dev:web
```

This will start Vite dev server on `http://localhost:5173`

Wait for it to show:
```
  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 3: Open Browser

Open your browser and go to:

**Option 1 - Direct URL:**
```
http://localhost:5173/systems/network
```

**Option 2 - Via Navigation:**
1. Go to: `http://localhost:5173`
2. Click "Systems" in the sidebar
3. Click "Network Monitoring"

### Step 4: Generate Network Data (First Time)

If you see "No devices detected" or an error:

1. **Option A - Use the Refresh Button:**
   - Click the "Refresh" button in the GUI
   - This will automatically run the network scan

2. **Option B - Run Script Manually:**
   ```bash
   python3 ops_root_assets/scripts/network_watch.py
   ```

## Troubleshooting

### Frontend won't start
```bash
cd frontend
npm install  # Make sure dependencies are installed
npm run dev:web
```

### Port 5173 already in use
```bash
# Find what's using the port
lsof -ti:5173

# Kill it if needed, or use a different port
npm run dev:web -- --port 5174
```

### Page shows "Failed to load network data"
- Make sure backend is running on port 8000
- Check backend logs for errors
- Run the network watch script once manually
- Check browser console (F12) for errors

### "Cannot GET /systems/network"
- Make sure frontend dev server is running
- Check that you're using `npm run dev:web` (not a production build)
- Verify the route exists in `frontend/src/App.tsx`

### Blank page or React errors
- Open browser DevTools (F12)
- Check Console tab for errors
- Check Network tab to see if API calls are failing

## What You Should See

When working correctly, you'll see:

1. **Header** with "Network Device Monitor" title
2. **Summary Cards** showing:
   - Total Devices
   - Suspicious Devices  
   - Auth Failures
   - Listening Ports
3. **Network Devices Table** (if devices are found)
4. **Refresh and Auto buttons** in the header

## Quick Test Command

Run this to start everything at once (requires multiple terminals):

```bash
# Terminal 1: Backend
cd backend_api && python main.py

# Terminal 2: Frontend  
cd frontend && npm run dev:web

# Terminal 3: Generate initial data
python3 ops_root_assets/scripts/network_watch.py
```

Then open: `http://localhost:5173/systems/network`





