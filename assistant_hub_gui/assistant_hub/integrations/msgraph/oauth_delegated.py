"""OAuth2 delegated permissions flow for Microsoft Graph (user sign-in)."""

from __future__ import annotations

import json
import os
import socket
import webbrowser
from pathlib import Path
from typing import Optional, Dict
from urllib.parse import urlencode, parse_qs, urlparse
import http.server
import socketserver
import threading
import time

import requests

from .auth import GraphCredentials, AuthenticationError


def find_free_port(start_port: int = 8080, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise OSError(f"Could not find an available port starting from {start_port}")


class DelegatedAuth:
    """OAuth2 authorization code flow for delegated permissions (user sign-in)."""
    
    def __init__(self, credentials: GraphCredentials, redirect_port: int = 8080):
        self.credentials = credentials
        # Default to 8080 (must match Azure redirect URI configuration)
        # We'll handle port conflicts when starting the server
        self.redirect_port = redirect_port
        self.redirect_uri = f"http://localhost:{self.redirect_port}"
        self.token_file = Path.home() / ".assistant_hub" / "azure_delegated_token.json"
        
    def get_authorization_url(self, scopes: list[str] = None) -> str:
        """Generate the authorization URL for user sign-in."""
        if scopes is None:
            scopes = [
                "https://graph.microsoft.com/Notes.ReadWrite",
                "https://graph.microsoft.com/Files.ReadWrite.All",
                "https://graph.microsoft.com/User.Read",
                "offline_access"  # Required for refresh token
            ]
        
        # Support special tenant values
        tenant = self.credentials.tenant_id.strip().lower()
        if tenant in ["consumers", "common", "organizations"]:
            auth_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
        else:
            auth_url = f"https://login.microsoftonline.com/{self.credentials.tenant_id}/oauth2/v2.0/authorize"
        
        params = {
            "client_id": self.credentials.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "response_mode": "query",
            "scope": " ".join(scopes),
            "state": "assistant_hub_auth"  # Simple state for validation
        }
        
        return f"{auth_url}?{urlencode(params)}"
    
    def start_callback_server(self) -> tuple[list, list, threading.Thread, int]:
        """Start a local HTTP server to receive the OAuth callback.
        
        Returns:
            Tuple of (auth_code list, error list, server thread, actual_port used)
        """
        auth_code = [None]
        error = [None]
        
        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)
                
                if "code" in params:
                    auth_code[0] = params["code"][0]
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"""
                    <html>
                    <head><title>Authentication Successful</title></head>
                    <body>
                        <h1>Authentication Successful!</h1>
                        <p>You can close this window and return to the application.</p>
                    </body>
                    </html>
                    """)
                elif "error" in params:
                    error[0] = params.get("error_description", [params["error"][0]])[0]
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(f"""
                    <html>
                    <head><title>Authentication Failed</title></head>
                    <body>
                        <h1>Authentication Failed</h1>
                        <p>Error: {error[0]}</p>
                    </body>
                    </html>
                    """.encode())
                else:
                    self.send_response(400)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass  # Suppress server logs
        
        # Use allow_reuse_address to avoid "Address already in use" errors
        # This allows reusing the port if it was recently used
        socketserver.TCPServer.allow_reuse_address = True
        
        # Try to find a free port, starting with the preferred port
        actual_port = None
        server = None
        
        try:
            # First try the preferred port
            server = socketserver.TCPServer(("", self.redirect_port), CallbackHandler)
            server.timeout = 1
            actual_port = self.redirect_port
        except OSError as e:
            if "Address already in use" in str(e) or e.errno == 48:
                # Port is in use, try to find a free port
                print(f"⚠️  Port {self.redirect_port} is in use, searching for available port...")
                try:
                    actual_port = find_free_port(start_port=self.redirect_port, max_attempts=10)
                    server = socketserver.TCPServer(("", actual_port), CallbackHandler)
                    server.timeout = 1
                    # Update redirect URI to use the found port
                    self.redirect_uri = f"http://localhost:{actual_port}"
                    print(f"✓ Using port {actual_port} instead")
                    
                    # Warn user if port doesn't match Azure configuration
                    if actual_port != self.redirect_port:
                        print(f"\n⚠️  WARNING: Using port {actual_port} instead of {self.redirect_port}")
                        print(f"   Make sure this redirect URI is configured in Azure Portal:")
                        print(f"   http://localhost:{actual_port}")
                        print(f"   Azure Portal > App registrations > Your app > Authentication")
                        print(f"   Add this as a redirect URI if not already configured.\n")
                except OSError as e2:
                    # Couldn't find any free port
                    import subprocess
                    port_info = ""
                    try:
                        result = subprocess.run(
                            ["lsof", "-i", f":{self.redirect_port}"],
                            capture_output=True,
                            text=True,
                            timeout=2
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            lines = result.stdout.strip().split('\n')
                            if len(lines) > 1:
                                # Skip header, show first process
                                process_info = lines[1].split()
                                if len(process_info) >= 2:
                                    cmd = process_info[0]
                                    pid = process_info[1]
                                    port_info = f"\n   Found: {cmd} (PID {pid}) is using port {self.redirect_port}\n"
                                    port_info += f"   To stop it: kill {pid}\n"
                    except Exception:
                        pass
                    
                    raise AuthenticationError(
                        f"❌ Could not find an available port starting from {self.redirect_port}.{port_info}\n"
                        f"\nPlease either:\n"
                        f"1. Stop processes using ports {self.redirect_port}-{self.redirect_port + 9}, or\n"
                        f"2. Configure multiple redirect URIs in Azure Portal:\n"
                        f"   - Azure Portal > App registrations > Your app > Authentication\n"
                        f"   - Add redirect URIs: http://localhost:8080 through http://localhost:8089\n"
                        f"\nTo find what's using the ports:\n"
                        f"   lsof -i :{self.redirect_port}"
                    )
            else:
                raise
        
        def run_server():
            while auth_code[0] is None and error[0] is None:
                server.handle_request()
            server.server_close()
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        
        return auth_code, error, thread, actual_port
    
    def exchange_code_for_token(self, auth_code: str) -> Dict:
        """Exchange authorization code for access token."""
        # Support special tenant values
        tenant = self.credentials.tenant_id.strip().lower()
        if tenant in ["consumers", "common", "organizations"]:
            token_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
        else:
            token_url = f"https://login.microsoftonline.com/{self.credentials.tenant_id}/oauth2/v2.0/token"
        
        data = {
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
            "code": auth_code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        
        response = requests.post(
            token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        
        if response.status_code != 200:
            error_detail = response.text
            try:
                error_json = response.json()
                error_description = error_json.get("error_description", error_detail)
            except:
                error_description = error_detail
            raise AuthenticationError(f"Failed to exchange code for token: {error_description}")
        
        return response.json()
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """Refresh an access token using a refresh token."""
        # Support special tenant values
        tenant = self.credentials.tenant_id.strip().lower()
        if tenant in ["consumers", "common", "organizations"]:
            token_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
        else:
            token_url = f"https://login.microsoftonline.com/{self.credentials.tenant_id}/oauth2/v2.0/token"
        
        data = {
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "scope": "https://graph.microsoft.com/.default",
        }
        
        response = requests.post(
            token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        
        if response.status_code != 200:
            error_detail = response.text
            try:
                error_json = response.json()
                error_description = error_json.get("error_description", error_detail)
            except:
                error_description = error_detail
            raise AuthenticationError(f"Failed to refresh token: {error_description}")
        
        return response.json()
    
    def authenticate_interactive(self) -> str:
        """Perform interactive OAuth flow and return access token."""
        print("\n" + "="*70)
        print("Microsoft Graph OAuth2 Authentication (Delegated Permissions)")
        print("="*70)
        print("\nThis will open your browser for Microsoft sign-in.")
        print("After signing in, you'll be redirected back to this application.\n")
        
        # Start callback server first (this may change redirect_uri if port is in use)
        auth_code, error, server_thread, actual_port = self.start_callback_server()
        time.sleep(1)  # Give server time to start
        
        # Generate authorization URL (using the actual redirect_uri, which may have changed)
        auth_url = self.get_authorization_url()
        print(f"Opening browser: {auth_url}\n")
        print(f"ℹ️  Listening on: {self.redirect_uri}\n")
        
        # Open browser
        try:
            webbrowser.open(auth_url)
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print(f"\nPlease open this URL in your browser:\n{auth_url}\n")
        
        # Wait for callback (with timeout)
        print("Waiting for authentication...")
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while auth_code[0] is None and error[0] is None:
            if time.time() - start_time > timeout:
                raise AuthenticationError("Authentication timeout. Please try again.")
            time.sleep(0.5)
        
        if error[0]:
            raise AuthenticationError(f"Authentication error: {error[0]}")
        
        if not auth_code[0]:
            raise AuthenticationError("No authorization code received.")
        
        print("✓ Authorization code received. Exchanging for token...")
        
        # Exchange code for token
        token_data = self.exchange_code_for_token(auth_code[0])
        
        # Save token data
        self.save_token(token_data)
        
        print("✅ Authentication successful!")
        print(f"   Access token expires in: {token_data.get('expires_in', 'unknown')} seconds")
        
        return token_data["access_token"]
    
    def save_token(self, token_data: Dict):
        """Save token data to file."""
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.token_file, "w") as f:
            json.dump(token_data, f, indent=2)
    
    def load_token(self) -> Optional[Dict]:
        """Load token data from file."""
        if not self.token_file.exists():
            return None
        
        try:
            with open(self.token_file, "r") as f:
                return json.load(f)
        except Exception:
            return None
    
    def get_valid_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        token_data = self.load_token()
        
        if not token_data:
            # No token stored, need interactive auth
            return self.authenticate_interactive()
        
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 3600)
        
        # Check if token is expired (with 5 minute buffer)
        if "expires_at" in token_data:
            expires_at = float(token_data["expires_at"])
            if time.time() < expires_at - 300:  # 5 minute buffer
                return access_token
        
        # Token expired or will expire soon, try to refresh
        if refresh_token:
            try:
                print("🔄 Refreshing access token...")
                new_token_data = self.refresh_token(refresh_token)
                new_token_data["refresh_token"] = refresh_token  # Keep the refresh token
                self.save_token(new_token_data)
                return new_token_data["access_token"]
            except Exception as e:
                print(f"⚠️  Token refresh failed: {e}")
                print("Starting new authentication flow...")
                return self.authenticate_interactive()
        
        # No refresh token, need new auth
        return self.authenticate_interactive()

