"""Authentication helpers for Microsoft Graph integrations."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import requests


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


@dataclass
class GraphCredentials:
    tenant_id: str
    client_id: str
    client_secret: str

    @classmethod
    def from_env(cls, conn=None) -> "GraphCredentials":
        """Load credentials from database, environment variables, or config file (in that order)."""
        tenant_id = ""
        client_id = ""
        client_secret = ""
        
        # Priority 1: Try loading from database if connection provided
        if conn is not None:
            try:
                from ...db import load_azure_credentials
                db_creds = load_azure_credentials(conn)
                if db_creds:
                    tenant_id = db_creds.get("tenant_id", "")
                    client_id = db_creds.get("client_id", "")
                    client_secret = db_creds.get("client_secret", "")
            except Exception:
                # If database load fails, continue to other sources
                pass
        
        # Priority 2: Check environment variables (only if not already loaded from DB)
        if not all([tenant_id, client_id, client_secret]):
            tenant_id = tenant_id or os.environ.get("AZURE_TENANT_ID", "")
            client_id = client_id or os.environ.get("AZURE_CLIENT_ID", "")
            client_secret = client_secret or os.environ.get("AZURE_CLIENT_SECRET", "")
        
        # Priority 3: Try loading from config file (only if not already loaded)
        if not all([tenant_id, client_id, client_secret]):
            config_file = Path.home() / ".assistant_hub" / "azure_config.txt"
            if config_file.exists():
                try:
                    with open(config_file, "r") as f:
                        for line in f:
                            line = line.strip()
                            if "=" in line and not line.startswith("#"):
                                key, value = line.split("=", 1)
                                key = key.strip()
                                value = value.strip()
                                # Only set if not already loaded
                                if key == "AZURE_TENANT_ID" and not tenant_id:
                                    tenant_id = value
                                elif key == "AZURE_CLIENT_ID" and not client_id:
                                    client_id = value
                                elif key == "AZURE_CLIENT_SECRET" and not client_secret:
                                    client_secret = value
                except Exception:
                    # If file read fails, continue with what we have
                    pass
        
        # Validate that we have all credentials
        if not tenant_id or not client_id or not client_secret:
            missing = []
            if not tenant_id:
                missing.append("AZURE_TENANT_ID")
            if not client_id:
                missing.append("AZURE_CLIENT_ID")
            if not client_secret:
                missing.append("AZURE_CLIENT_SECRET")
            raise ValueError(
                f"Missing Azure credentials: {', '.join(missing)}\n"
                f"Please configure them in:\n"
                f"1. Database (Settings > Integrations > Configure)\n"
                f"2. Environment variables (AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)\n"
                f"3. Config file (~/.assistant_hub/azure_config.txt)\n"
                f"Run: python get_azure_credentials.py to configure."
            )
        
        return cls(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )


class GraphAuth:
    """Acquire tokens for Microsoft Graph APIs using client credentials."""

    scope: str = "https://graph.microsoft.com/.default"

    def __init__(self, credentials: GraphCredentials):
        self.credentials = credentials

    def get_token(self) -> str:
        token_url = f"https://login.microsoftonline.com/{self.credentials.tenant_id}/oauth2/v2.0/token"
        response = requests.post(
            token_url,
            data={
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "scope": self.scope,
                "grant_type": "client_credentials",
            },
            timeout=10,
        )
        if response.status_code == 401:
            error_detail = response.text
            try:
                error_json = response.json()
                error_code = error_json.get("error", "unknown")
                error_description = error_json.get("error_description", error_detail)
            except:
                error_code = "unknown"
                error_description = error_detail
            
            # Provide specific guidance based on common error patterns
            guidance = ""
            if "AADSTS7000215" in error_description or "invalid_client" in error_code.lower():
                guidance = (
                    "\n⚠️  LIKELY CAUSE: Invalid client secret or expired secret.\n"
                    "   - Check Azure Portal > App registrations > Your app > Certificates & secrets\n"
                    "   - Make sure you're using the SECRET VALUE (not the Secret ID)\n"
                    "   - Create a new secret if the current one has expired\n"
                )
            elif "AADSTS700016" in error_description or "unauthorized_client" in error_code.lower():
                guidance = (
                    "\n⚠️  LIKELY CAUSE: App registration not found or misconfigured.\n"
                    "   - Verify the Client ID and Tenant ID are correct\n"
                    "   - Check that the app registration exists in Azure Portal\n"
                )
            
            raise AuthenticationError(
                f"❌ Azure Authentication Failed (401 Unauthorized)\n\n"
                f"Error Code: {error_code}\n"
                f"Error: {error_description}\n"
                f"{guidance}"
                f"\n📋 TROUBLESHOOTING STEPS:\n"
                f"1. Verify credentials in ~/.assistant_hub/azure_config.txt or environment variables\n"
                f"2. Check Azure Portal > App registrations > Your app:\n"
                f"   - Certificates & secrets: Is the secret expired? Use the VALUE, not the ID\n"
                f"   - API permissions: Ensure delegated permissions are granted:\n"
                f"     • Notes.ReadWrite (for OneNote)\n"
                f"     • Files.ReadWrite.All (for Excel/Word)\n"
                f"     • User.Read\n"
                f"3. Run: python get_azure_credentials.py to reconfigure\n"
                f"4. NOTE: /me/ endpoints require DELEGATED permissions with user sign-in.\n"
                f"   Client credentials (app-only) may not work for user data access.\n"
            )
        response.raise_for_status()
        return response.json()["access_token"]


# Backwards compatibility functions
def load_credentials_from_env() -> GraphCredentials:
    """Load Graph credentials from environment variables (backwards compatibility)."""
    return GraphCredentials.from_env()


def request_access_token(credentials: GraphCredentials) -> str:
    """Request a bearer token using the client credentials flow (backwards compatibility)."""
    auth = GraphAuth(credentials)
    return auth.get_token()
