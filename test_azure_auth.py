#!/usr/bin/env python3
"""Test Azure authentication and retrieve access token."""

import os
import sys
from pathlib import Path

# Add the assistant_hub directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from assistant_hub.integrations.msgraph.auth import GraphAuth, GraphCredentials
except ImportError:
    # Try alternative path
    sys.path.insert(0, str(Path(__file__).parent / "assistant_hub_gui"))
    from assistant_hub.integrations.msgraph.auth import GraphAuth, GraphCredentials


def load_credentials_from_config() -> GraphCredentials:
    """Load credentials from config file if it exists."""
    config_file = Path.home() / ".assistant_hub" / "azure_config.txt"
    
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    
    return GraphCredentials.from_env()


def main():
    """Main function to test authentication and get token."""
    print("=" * 70)
    print("Azure Authentication Test")
    print("=" * 70)
    print()
    
    # Load credentials
    print("Loading Azure credentials...")
    try:
        credentials = load_credentials_from_config()
        
        # Check if credentials are set
        if not credentials.tenant_id:
            print("❌ ERROR: AZURE_TENANT_ID is not configured")
            print("\nPlease configure your Azure credentials:")
            print("  1. Run: python get_azure_credentials.py")
            print("  2. Or set environment variables:")
            print("     export AZURE_TENANT_ID='your-tenant-id'")
            print("     export AZURE_CLIENT_ID='your-client-id'")
            print("     export AZURE_CLIENT_SECRET='your-client-secret'")
            print("  3. Or configure via GUI: Tools & Operations > Configure Microsoft Graph")
            sys.exit(1)
        
        if not credentials.client_id:
            print("❌ ERROR: AZURE_CLIENT_ID is not configured")
            sys.exit(1)
        
        if not credentials.client_secret:
            print("❌ ERROR: AZURE_CLIENT_SECRET is not configured")
            sys.exit(1)
        
        print(f"✓ Tenant ID: {credentials.tenant_id[:8]}...")
        print(f"✓ Client ID: {credentials.client_id[:8]}...")
        print(f"✓ Client Secret: {'*' * len(credentials.client_secret)}")
        print()
        
        # Attempt to get token
        print("Requesting access token from Azure AD...")
        try:
            auth = GraphAuth(credentials)
            token = auth.get_token()
            
            print("✅ SUCCESS! Access token retrieved.")
            print()
            print("Token details:")
            print(f"  Length: {len(token)} characters")
            print(f"  Preview: {token[:50]}...")
            print()
            
            # Optionally show full token (for debugging)
            if "--show-token" in sys.argv:
                print("Full access token:")
                print("-" * 70)
                print(token)
                print("-" * 70)
            else:
                print("(Use --show-token flag to display full token)")
            
            # Test the token by making a simple API call
            if "--test-api" in sys.argv:
                print()
                print("Testing token with Microsoft Graph API...")
                try:
                    import requests
                    headers = {"Authorization": f"Bearer {token}"}
                    response = requests.get(
                        "https://graph.microsoft.com/v1.0/me",
                        headers=headers,
                        timeout=10
                    )
                    if response.status_code == 200:
                        user_info = response.json()
                        print("✅ Token is valid!")
                        print(f"  User: {user_info.get('displayName', 'N/A')}")
                        print(f"  Email: {user_info.get('mail', user_info.get('userPrincipalName', 'N/A'))}")
                    else:
                        print(f"⚠️  API call returned status {response.status_code}")
                        print(f"  Response: {response.text[:200]}")
                except Exception as e:
                    print(f"⚠️  Could not test API: {e}")
            
            return 0
            
        except Exception as e:
            print(f"❌ ERROR: Failed to get access token")
            print(f"   {type(e).__name__}: {e}")
            print()
            print("Possible issues:")
            print("  1. Invalid credentials (check Tenant ID, Client ID, Client Secret)")
            print("  2. Client secret may have expired")
            print("  3. App registration may not have correct permissions")
            print("  4. Network connectivity issues")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())

