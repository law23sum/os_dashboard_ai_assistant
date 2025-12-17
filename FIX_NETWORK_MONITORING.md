# Fix Network Monitoring Error

## Issues Found

1. **Missing `psutil` dependency** - Required for network monitoring script
2. **Wrong backend server** - Port 8000 is running Django instead of FastAPI with network router

## Quick Fix

### Option 1: Install psutil (Recommended)

If you have a virtual environment:

```bash
cd /Users/chrisdixon/Projects/os_dashboard_ai_assistant
source venv/bin/activate  # or: . venv/bin/activate
pip install psutil
```

Or if using system Python with --user:
```bash
python3 -m pip install --user --break-system-packages psutil
```

### Option 2: Use the Correct Backend Server

The network monitoring router was added to `backend_api/main.py`. You need to run:

```bash
cd backend_api
python main.py
```

Or with uvicorn:
```bash
uvicorn backend_api.main:app --reload --host 127.0.0.1 --port 8000
```

**Note**: Make sure port 8000 is free (stop the Django server first if it's running there).

## Complete Setup Steps

1. **Stop any existing servers on port 8000**:
   ```bash
   lsof -ti:8000 | xargs kill
   ```

2. **Install psutil** (choose one):
   ```bash
   # If using venv:
   source venv/bin/activate
   pip install psutil
   
   # Or with --user:
   python3 -m pip install --user --break-system-packages psutil
   ```

3. **Start the correct backend**:
   ```bash
   cd backend_api
   python main.py
   ```
   
   You should see it start on port 8000.

4. **Generate network data**:
   ```bash
   cd /Users/chrisdixon/Projects/os_dashboard_ai_assistant
   python3 ops_root_assets/scripts/network_watch.py
   ```

5. **Test the API**:
   ```bash
   curl http://localhost:8000/api/network/status
   ```

6. **Refresh the frontend page**:
   - Go to: `http://localhost:5173/systems/network`
   - Click "Refresh" button

## Alternative: Use Backend on Different Port

If port 8000 must stay on Django, you can:

1. Run FastAPI backend on a different port (e.g., 8002):
   ```bash
   cd backend_api
   uvicorn backend_api.main:app --reload --host 127.0.0.1 --port 8002
   ```

2. Update frontend vite.config.ts proxy:
   Change line 21 from:
   ```typescript
   target: "http://localhost:8000",
   ```
   To:
   ```typescript
   target: "http://localhost:8002",
   ```

3. Restart frontend dev server

## Verify It's Working

After setup, test:

```bash
# 1. Check backend is running
curl http://localhost:8000/api/network/status

# 2. Check network data file exists
ls -la ~/OS_Dashboard_AI_Assistant/logs/network_watch.json

# 3. Frontend should show data
# Open: http://localhost:5173/systems/network
```

## Expected Response

The API should return JSON like:
```json
{
  "generated_at": "2025-12-16T...",
  "auth": {...},
  "devices": [...],
  "suspicious_devices": [...],
  ...
}
```

If you see "Not Found" or HTML error page, the router isn't registered correctly.





