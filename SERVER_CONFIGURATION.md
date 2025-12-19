# Server Configuration Guide

## Port Configuration

The OS Dashboard system can run on different ports depending on how you start it:

### Option 1: Direct API Server (Port 8070)
```bash
# Start the API server directly
python -m assistant_hub_gui.assistant_hub.core.api_server

# The server will run on: http://127.0.0.1:8070
```

### Option 2: Unified Launcher (Port 8000)
```bash
# Use the unified launcher
python start_ui.py --mode web

# The server will run on: http://127.0.0.1:8000
```

## Frontend Configuration

The frontend is now configured to connect to port **8070** by default (matching the direct API server).

If you need to change the API target:

### Method 1: Environment Variable (Recommended)
```bash
# In your terminal before running npm run dev:
export VITE_API_TARGET=http://localhost:8000
npm run dev:web
```

### Method 2: Update .env.development
Edit `frontend/.env.development`:
```env
VITE_API_TARGET=http://localhost:8000
```

### Method 3: Direct Command Line
```bash
VITE_API_TARGET=http://localhost:8000 npm run dev:web
```

## Troubleshooting

### 404 Errors for `/api/runtime/diagnostics`

This endpoint exists and is properly registered. If you see 404 errors:

1. **Check the server is running**: Verify the API server is actually running on the expected port
2. **Verify the port**: Make sure `VITE_API_TARGET` matches your running server
3. **Check the logs**: The server logs should show incoming requests

### Connection Refused (ECONNREFUSED)

This means the frontend cannot connect to the backend:

1. **Server not running**: Start the API server first
2. **Wrong port**: Check that VITE_API_TARGET matches the running server
3. **Firewall**: Ensure localhost connections are not blocked

### SSL/TLS Errors ("packet length too long")

This happens when the proxy tries to use HTTPS with an HTTP server:

1. The vite.config.ts is configured with `secure: false` to prevent this
2. Ensure you're using `http://` (not `https://`) in VITE_API_TARGET
3. If you have SSL certificates in the `certs/` directory, the server may start with HTTPS

## Default Configuration (After This Fix)

- **Frontend dev server**: http://localhost:5173
- **API server (direct)**: http://localhost:8070  ← New default
- **API server (via start_ui.py)**: http://localhost:8000

## Quick Start

### For Development with Direct API Server:
```bash
# Terminal 1: Start API server
python3 -m assistant_hub_gui.assistant_hub.core.api_server

# Terminal 2: Start frontend
cd frontend
npm run dev:web
```

### For Development with Unified Launcher:
```bash
# Single command that starts both
python3 start_ui.py --mode web
```
