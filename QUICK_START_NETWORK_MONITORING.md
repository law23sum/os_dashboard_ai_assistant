# Quick Start: Network Monitoring GUI

## Issue Fixed ✅

The network monitoring router was imported but not registered. This has been fixed.

## How to Access the Network Monitoring GUI

### Step 1: Start the Backend Server

Make sure the FastAPI backend is running:

```bash
cd backend_api
python main.py
```

Or use uvicorn directly:
```bash
uvicorn backend_api.main:app --reload --host 127.0.0.1 --port 8000
```

The backend should start on `http://localhost:8000`

### Step 2: Start the Frontend

In a **new terminal**, start the frontend dev server:

```bash
cd frontend
npm run dev:web
```

This will start Vite dev server on `http://localhost:5173`

### Step 3: Access the Network Monitoring Page

You have **two ways** to access it:

1. **Via Navigation Menu**:
   - Open `http://localhost:5173` in your browser
   - Click on **"Systems"** in the sidebar
   - Click on **"Network Monitoring"** (with Network icon)

2. **Direct URL**:
   - Navigate directly to: `http://localhost:5173/systems/network`
   - Or: `http://localhost:5173/network`

### Step 4: Generate Network Data (First Time)

The first time you access the page, you may need to generate network monitoring data:

```bash
python3 ops_root_assets/scripts/network_watch.py
```

This creates the JSON file at: `~/OS_Dashboard_AI_Assistant/logs/network_watch.json`

Or click the **"Refresh"** button in the GUI - it will automatically run the script.

## What You Should See

1. **Header**: "Network Device Monitor" with refresh controls
2. **Summary Cards**: Total devices, suspicious devices, auth failures, listening ports
3. **Suspicious Device Alerts** (if any): Highlighted warnings at the top
4. **Network Devices Table**: All devices with IP, MAC, hostname, status
5. **Network Interfaces**: Interface statistics (if available)
6. **WiFi Status**: Current WiFi connection info (if available)

## Troubleshooting

### "Failed to load network data"
- Make sure the backend is running on port 8000
- Run the network watch script once: `python3 ops_root_assets/scripts/network_watch.py`
- Check that the file exists: `~/OS_Dashboard_AI_Assistant/logs/network_watch.json`

### Page doesn't load / 404 error
- Make sure frontend dev server is running
- Check browser console for errors (F12)
- Verify route is registered: check `frontend/src/App.tsx` for `/systems/network`

### No devices showing
- This is normal if no devices are on your network
- Try clicking "Refresh" to run a fresh scan
- Check the backend logs for errors

### Backend import errors
- Make sure you're in a virtual environment with dependencies installed:
  ```bash
  pip install -r requirements.txt
  ```

## API Endpoints

Once running, these endpoints are available:

- `GET http://localhost:8000/api/network/status` - Get network status
- `POST http://localhost:8000/api/network/refresh` - Refresh network data
- `GET http://localhost:8000/api/network/devices` - Get device list
- `GET http://localhost:8000/api/network/interfaces` - Get interface stats

You can test these directly in your browser or with curl:

```bash
curl http://localhost:8000/api/network/status
```

## Quick Test

1. Start backend: `cd backend_api && python main.py`
2. Start frontend: `cd frontend && npm run dev:web` (new terminal)
3. Generate data: `python3 ops_root_assets/scripts/network_watch.py` (optional)
4. Open browser: `http://localhost:5173/systems/network`
5. Click "Refresh" button in the GUI

The page should now display network monitoring data! 🎉





