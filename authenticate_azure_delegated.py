#!/usr/bin/env python3
"""Interactive OAuth2 authentication for Microsoft Graph with delegated permissions."""

import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "assistant_hub_gui"))

try:
    from assistant_hub_gui.assistant_hub.integrations.msgraph.auth import GraphCredentials
    from assistant_hub_gui.assistant_hub.integrations.msgraph.oauth_delegated import DelegatedAuth
except ImportError:
    from assistant_hub.integrations.msgraph.auth import GraphCredentials
    from assistant_hub.integrations.msgraph.oauth_delegated import DelegatedAuth


def main():
    """Main function to initiate delegated OAuth flow."""
    print("\n" + "="*70)
    print("Microsoft Graph Delegated Permissions Authentication")
    print("="*70)
    print("\nThis will authenticate using your Microsoft account with delegated permissions.")
    print("This is required for personal Microsoft accounts and /me/ endpoints.\n")
    
    # Load credentials
    try:
        credentials = GraphCredentials.from_env()
        print(f"✓ Loaded credentials:")
        print(f"   Tenant ID: {credentials.tenant_id[:20]}...")
        print(f"   Client ID: {credentials.client_id[:20]}...")
        print()
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        print("\nPlease configure Azure credentials first:")
        print("   python get_azure_credentials.py")
        return 1
    
    # Check if tenant is consumers/common (personal accounts)
    tenant = credentials.tenant_id.strip().lower()
    if tenant in ["consumers", "common"]:
        print("ℹ️  Detected personal Microsoft account (consumers/common)")
        print("   Delegated permissions are recommended for personal accounts.\n")
    else:
        print("ℹ️  Using organizational account")
        print("   Delegated permissions allow access to user-specific data (/me/ endpoints).\n")
    
    # Initiate OAuth flow
    try:
        auth = DelegatedAuth(credentials)
        token = auth.authenticate_interactive()
        
        print("\n" + "="*70)
        print("✅ Authentication Complete!")
        print("="*70)
        print(f"\nAccess token: {token[:50]}...")
        print(f"Token saved to: {auth.token_file}")
        print("\nYou can now use Microsoft Graph APIs with delegated permissions.")
        print("The token will be automatically refreshed when needed.\n")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n❌ Authentication cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

