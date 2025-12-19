# HTTPS Setup Guide

This application now supports HTTPS for secure connections. When SSL certificates are present, the application will automatically use HTTPS instead of HTTP.

## Quick Setup

1. **Generate SSL Certificates** (if not already present):
   ```bash
   python3 scripts/generate_ssl_certs.py
   ```

2. **Start the Application**:
   ```bash
   python start_ui.py
   ```

The application will automatically detect the certificates and use HTTPS.

## How It Works

### Automatic Detection

- **Backend Server**: The `start_ui.py` script checks for certificates in `certs/cert.pem` and `certs/key.pem`
- **Frontend Dev Server**: The Vite configuration automatically detects certificates and enables HTTPS
- **API Proxy**: All API requests are automatically routed through HTTPS when certificates are present

### Certificate Location

Certificates are stored in:
```
certs/
  ├── cert.pem    # SSL certificate
  └── key.pem     # Private key
```

These files are automatically excluded from git (see `.gitignore`).

## Browser Security Warning

Since these are self-signed certificates for local development, your browser will show a security warning. This is expected and safe for local development.

### To Proceed:

1. Click **"Advanced"** or **"Show Details"**
2. Click **"Proceed to localhost"** or **"Accept the Risk"**

The warning will only appear once per browser session.

## Manual Configuration

### Force HTTPS

Set the environment variable:
```bash
export VITE_USE_HTTPS=true
python start_ui.py
```

### Force HTTP

Set the environment variable:
```bash
export VITE_USE_HTTPS=false
python start_ui.py
```

### Custom API Target

Set a custom API target:
```bash
export VITE_API_TARGET=https://your-server:8000
python start_ui.py
```

## URLs

When HTTPS is enabled:
- **Backend API**: `https://localhost:8000` or `https://0.0.0.0:8000`
- **Frontend Dev Server**: `https://localhost:5173`
- **API Documentation**: `https://localhost:8000/swagger`

## Regenerating Certificates

To regenerate certificates (e.g., if they expire):
```bash
rm -rf certs/
python3 scripts/generate_ssl_certs.py
```

Certificates are valid for 365 days by default.

## Production Deployment

For production, you should:
1. Use certificates from a trusted Certificate Authority (CA)
2. Configure your reverse proxy (nginx, Apache) with proper SSL certificates
3. Use Let's Encrypt or similar services for free SSL certificates

## Troubleshooting

### Certificates Not Detected

1. Verify certificates exist:
   ```bash
   ls -la certs/
   ```

2. Check file permissions:
   ```bash
   chmod 600 certs/key.pem
   chmod 644 certs/cert.pem
   ```

### Browser Still Shows HTTP Warning

1. Clear browser cache
2. Ensure you're accessing `https://` not `http://`
3. Check browser console for mixed content warnings

### Connection Refused

1. Verify the backend is running with HTTPS:
   ```bash
   # Check the startup logs for:
   # "🔒 SSL certificates found. Starting with HTTPS..."
   ```

2. Verify port 8000 is accessible:
   ```bash
   curl -k https://localhost:8000/api/health
   ```

The `-k` flag allows self-signed certificates for testing.
