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
    
    def __post_init__(self):
        """Automatically clean credentials when object is created."""
        def clean_credential(value: str) -> str:
            """Thoroughly clean a credential value."""
            if not value:
                return ""
            # Remove all whitespace including newlines, tabs, carriage returns
            cleaned = value.strip()
            # Remove all types of whitespace characters
            cleaned = "".join(cleaned.split())  # This removes all whitespace
            # Also explicitly remove common problematic characters
            cleaned = cleaned.replace("\n", "").replace("\r", "").replace("\t", "")
            cleaned = cleaned.replace("\u200B", "")  # Zero-width space
            cleaned = cleaned.replace("\uFEFF", "")  # BOM
            return cleaned
        
        # Clean all fields
        self.tenant_id = clean_credential(self.tenant_id)
        self.client_id = clean_credential(self.client_id)
        self.client_secret = clean_credential(self.client_secret)

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
                                # Clean value: remove all whitespace, newlines, tabs
                                value = value.strip().replace("\n", "").replace("\r", "").replace("\t", "")
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
        
        # Priority 4: Try loading from Microsoft Graph JSON file (for client_id only)
        if not client_id:
            try:
                # Try to find the JSON file in project root
                current_file = Path(__file__)
                # Navigate up from integrations/msgraph/auth.py to project root
                project_root = current_file.parent.parent.parent.parent
                ms_graph_json = project_root / "os_dashboard_ai_assistant(Microsoft Graph format).json"
                
                if ms_graph_json.exists():
                    import json
                    with open(ms_graph_json, 'r') as f:
                        ms_data = json.load(f)
                    # Extract app_id which is the client_id
                    if ms_data.get("appId"):
                        client_id = ms_data["appId"]
            except Exception:
                # If JSON parsing fails, continue with what we have
                pass
        
        # Clean all credentials to remove any whitespace issues
        def clean_credential(value: str) -> str:
            """Thoroughly clean a credential value."""
            if not value:
                return ""
            # Remove all whitespace including newlines, tabs, carriage returns
            cleaned = value.strip()
            # Remove all types of whitespace characters
            cleaned = "".join(cleaned.split())  # This removes all whitespace
            # Also explicitly remove common problematic characters
            cleaned = cleaned.replace("\n", "").replace("\r", "").replace("\t", "")
            cleaned = cleaned.replace("\u200B", "")  # Zero-width space
            cleaned = cleaned.replace("\uFEFF", "")  # BOM
            return cleaned
        
        tenant_id = clean_credential(tenant_id) if tenant_id else ""
        client_id = clean_credential(client_id) if client_id else ""
        client_secret = clean_credential(client_secret) if client_secret else ""
        
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
        
        # Create instance - __post_init__ will clean the values
        instance = cls(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )
        
        # Additional validation after cleaning
        if not instance.tenant_id:
            raise ValueError("Tenant ID is empty after cleaning")
        if not instance.client_id:
            raise ValueError("Client ID is empty after cleaning")
        if not instance.client_secret:
            raise ValueError("Client Secret is empty after cleaning")
        
        # Warn if client secret looks like a Secret ID (GUID) instead of Secret Value
        if "-" in instance.client_secret and len(instance.client_secret) == 36:
            raise ValueError(
                "Client Secret appears to be a Secret ID (GUID) instead of Secret Value.\n"
                "Please use the SECRET VALUE from Azure Portal (typically 40+ characters),\n"
                "not the Secret ID (which is a GUID)."
            )
        
        return instance


class GraphAuth:
    """Acquire tokens for Microsoft Graph APIs using client credentials."""

    scope: str = "https://graph.microsoft.com/.default"

    def __init__(self, credentials: GraphCredentials):
        self.credentials = credentials

    def get_token(self) -> str:
        """Get access token using client credentials flow."""
        # Use client credentials flow (app-only)
        # Credentials are already cleaned by __post_init__, but validate they're not empty
        if not self.credentials.tenant_id:
            raise AuthenticationError("Tenant ID is empty")
        if not self.credentials.client_id:
            raise AuthenticationError("Client ID is empty")
        if not self.credentials.client_secret:
            raise AuthenticationError("Client Secret is empty")
        
        # Build token URL - credentials are already cleaned
        tenant_lower = self.credentials.tenant_id.lower()
        # Support special tenant values: "consumers" (personal accounts), "common" (both), or specific tenant ID
        if tenant_lower in ["consumers", "common", "organizations"]:
            # Use the special endpoint directly
            token_url = f"https://login.microsoftonline.com/{tenant_lower}/oauth2/v2.0/token"
        else:
            # Use specific tenant ID (already cleaned)
            token_url = f"https://login.microsoftonline.com/{self.credentials.tenant_id}/oauth2/v2.0/token"
        
        # Prepare form data - credentials are already cleaned by __post_init__
        form_data = {
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
            "scope": self.scope,
            "grant_type": "client_credentials",
        }
        
        # Make request with proper headers
        response = requests.post(
            token_url,
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        
        # Handle 400 Bad Request errors
        if response.status_code == 400:
            error_detail = response.text
            try:
                error_json = response.json()
                error_code = error_json.get("error", "unknown")
                error_description = error_json.get("error_description", error_detail)
            except:
                error_code = "bad_request"
                error_description = error_detail
            
            # Check for AADSTS9002346 - App configured for Microsoft Account users only
            if "AADSTS9002346" in error_description and tenant_lower not in ["consumers", "common"]:
                # Automatically retry with consumers endpoint
                print("⚠️  Detected Microsoft Account-only app. Retrying with /consumers endpoint...")
                token_url_retry = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
                response_retry = requests.post(
                    token_url_retry,
                    data=form_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10,
                )
                if response_retry.status_code == 200:
                    print("✓ Successfully authenticated using /consumers endpoint")
                    return response_retry.json()["access_token"]
                else:
                    # Retry also failed, provide guidance
                    raise AuthenticationError(
                        f"❌ Azure Authentication Failed\n\n"
                        f"Your app is configured for Microsoft Account users only (personal accounts).\n"
                        f"Please set your Tenant ID to 'consumers' in your configuration:\n\n"
                        f"1. Go to Settings > Integrations > Configure Microsoft Graph\n"
                        f"2. Set Tenant ID to: consumers\n"
                        f"3. Save and try again\n\n"
                        f"Or update ~/.assistant_hub/azure_config.txt:\n"
                        f"   AZURE_TENANT_ID=consumers\n\n"
                        f"Original error: {error_description}"
                    )
            
            # Provide specific guidance for common 400 errors
            guidance = ""
            if "AADSTS9002346" in error_description:
                guidance = (
                    "\n⚠️  LIKELY CAUSE: App is configured for Microsoft Account users only.\n"
                    "   - Your app registration is set up for personal Microsoft accounts\n"
                    "   - Set Tenant ID to 'consumers' in your configuration\n"
                    "   - Go to Settings > Integrations > Configure Microsoft Graph\n"
                )
            elif "invalid_request" in error_code.lower():
                guidance = (
                    "\n⚠️  LIKELY CAUSE: Malformed request or missing required parameters.\n"
                    "   - Check that all credentials are properly formatted\n"
                    "   - Verify Tenant ID, Client ID, and Client Secret are correct\n"
                    "   - Ensure credentials don't have extra spaces or newlines\n"
                )
            elif "invalid_client" in error_code.lower() or "AADSTS7000215" in error_description:
                guidance = (
                    "\n⚠️  LIKELY CAUSE: Invalid client secret or expired secret.\n"
                    "   - Check Azure Portal > App registrations > Your app > Certificates & secrets\n"
                    "   - Make sure you're using the SECRET VALUE (not the Secret ID)\n"
                    "   - Create a new secret if the current one has expired\n"
                )
            elif "invalid_scope" in error_code.lower():
                guidance = (
                    "\n⚠️  LIKELY CAUSE: Invalid scope or permissions not configured.\n"
                    "   - Check Azure Portal > App registrations > Your app > API permissions\n"
                    "   - Ensure required permissions are granted\n"
                )
            
            raise AuthenticationError(
                f"❌ Azure Authentication Failed (400 Bad Request)\n\n"
                f"Error Code: {error_code}\n"
                f"Error: {error_description}\n"
                f"{guidance}"
                f"\n📋 TROUBLESHOOTING STEPS:\n"
                f"1. Verify credentials in ~/.assistant_hub/azure_config.txt or environment variables\n"
                f"2. Check for extra spaces, newlines, or special characters in credentials\n"
                f"3. Check Azure Portal > App registrations > Your app:\n"
                f"   - Certificates & secrets: Is the secret expired? Use the VALUE, not the ID\n"
                f"   - API permissions: Ensure required permissions are granted:\n"
                f"     • Notes.ReadWrite (for OneNote)\n"
                f"     • Files.ReadWrite.All (for Excel/Word)\n"
                f"     • User.Read\n"
                f"4. If your app is for personal Microsoft accounts, set Tenant ID to 'consumers'\n"
                f"5. Run: python get_azure_credentials.py --test to validate credentials\n"
                f"6. Run: python get_azure_credentials.py --force to reconfigure\n"
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
