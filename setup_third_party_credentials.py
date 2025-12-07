#!/usr/bin/env python3
"""Setup third-party credentials from JSON files in the root directory.

This script:
1. Parses the Microsoft Graph JSON file to extract app registration details
2. Copies/sets up Google OAuth client secret for Gmail/Calendar integrations
3. Updates the credential storage (database, config files, etc.)
"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

# Get project root directory
PROJECT_ROOT = Path(__file__).parent
MS_GRAPH_JSON = PROJECT_ROOT / "os_dashboard_ai_assistant(Microsoft Graph format).json"
GOOGLE_CLIENT_SECRET = PROJECT_ROOT / "client_secret_788356908604-ro9n0fq4p70q569237314n12u84jnren.apps.googleusercontent.com.json"
ASSISTANT_HUB_DIR = Path.home() / ".assistant_hub"


def ensure_assistant_hub_dir():
    """Ensure ~/.assistant_hub directory exists."""
    ASSISTANT_HUB_DIR.mkdir(parents=True, exist_ok=True)
    return ASSISTANT_HUB_DIR


def setup_google_credentials():
    """Set up Google OAuth credentials for Gmail and Calendar integrations."""
    if not GOOGLE_CLIENT_SECRET.exists():
        print(f"⚠️  Google client secret not found: {GOOGLE_CLIENT_SECRET}")
        return False
    
    try:
        # Read the Google client secret
        with open(GOOGLE_CLIENT_SECRET, 'r') as f:
            google_creds = json.load(f)
        
        # The file has structure: {"installed": {...}}
        if "installed" not in google_creds:
            print("⚠️  Google client secret file doesn't have expected 'installed' structure")
            return False
        
        creds_data = google_creds["installed"]
        
        # Copy to expected locations for Gmail and Calendar
        gmail_path = ASSISTANT_HUB_DIR / "gmail_credentials.json"
        calendar_path = ASSISTANT_HUB_DIR / "google_calendar_credentials.json"
        
        # Write credentials to both locations
        with open(gmail_path, 'w') as f:
            json.dump(google_creds, f, indent=2)
        print(f"✅ Google credentials copied to: {gmail_path}")
        
        with open(calendar_path, 'w') as f:
            json.dump(google_creds, f, indent=2)
        print(f"✅ Google credentials copied to: {calendar_path}")
        
        # Print summary
        print(f"\n📋 Google OAuth Configuration:")
        print(f"   Client ID: {creds_data.get('client_id', 'N/A')}")
        print(f"   Project ID: {creds_data.get('project_id', 'N/A')}")
        print(f"   Auth URI: {creds_data.get('auth_uri', 'N/A')}")
        print(f"   Token URI: {creds_data.get('token_uri', 'N/A')}")
        print(f"   Redirect URIs: {creds_data.get('redirect_uris', [])}")
        
        return True
    except Exception as e:
        print(f"❌ Error setting up Google credentials: {e}")
        return False


def parse_microsoft_graph_json() -> Optional[Dict[str, Any]]:
    """Parse Microsoft Graph app registration JSON and extract useful information."""
    if not MS_GRAPH_JSON.exists():
        print(f"⚠️  Microsoft Graph JSON not found: {MS_GRAPH_JSON}")
        return None
    
    try:
        with open(MS_GRAPH_JSON, 'r') as f:
            data = json.load(f)
        
        # Extract key information
        result = {
            "app_id": data.get("appId", ""),
            "object_id": data.get("id", ""),
            "display_name": data.get("displayName", ""),
            "publisher_domain": data.get("publisherDomain", ""),
            "sign_in_audience": data.get("signInAudience", ""),
            "required_resource_access": data.get("requiredResourceAccess", []),
            "password_credentials": data.get("passwordCredentials", []),
            "web": data.get("web", {}),
            "public_client": data.get("publicClient", {}),
        }
        
        return result
    except Exception as e:
        print(f"❌ Error parsing Microsoft Graph JSON: {e}")
        return None


def setup_microsoft_graph_credentials():
    """Set up Microsoft Graph credentials from the JSON file."""
    ms_data = parse_microsoft_graph_json()
    if not ms_data:
        return False
    
    print(f"\n📋 Microsoft Graph App Registration:")
    print(f"   Display Name: {ms_data.get('display_name', 'N/A')}")
    print(f"   App ID (Client ID): {ms_data.get('app_id', 'N/A')}")
    print(f"   Object ID: {ms_data.get('object_id', 'N/A')}")
    print(f"   Publisher Domain: {ms_data.get('publisher_domain', 'N/A')}")
    print(f"   Sign-in Audience: {ms_data.get('sign_in_audience', 'N/A')}")
    
    # Check for password credentials (client secrets)
    password_creds = ms_data.get("password_credentials", [])
    if password_creds:
        print(f"\n   Password Credentials Found:")
        for cred in password_creds:
            print(f"     - Display Name: {cred.get('displayName', 'N/A')}")
            print(f"       Key ID: {cred.get('keyId', 'N/A')}")
            print(f"       Hint: {cred.get('hint', 'N/A')}")
            print(f"       End Date: {cred.get('endDateTime', 'N/A')}")
            print(f"       ⚠️  Note: Secret value is not stored in JSON (for security)")
            print(f"       You need to get the secret VALUE from Azure Portal:")
            print(f"       Azure Portal > App registrations > {ms_data.get('display_name')} > Certificates & secrets")
    
    # Check required resource access
    required_access = ms_data.get("required_resource_access", [])
    if required_access:
        print(f"\n   Required Resource Access:")
        for resource in required_access:
            resource_app_id = resource.get("resourceAppId", "")
            if resource_app_id == "00000003-0000-0000-c000-000000000000":
                print(f"     - Microsoft Graph (ID: {resource_app_id})")
                scopes = resource.get("resourceAccess", [])
                for scope in scopes:
                    scope_id = scope.get("id", "")
                    scope_type = scope.get("type", "")
                    # Common scope IDs
                    scope_map = {
                        "e1fe6dd8-ba31-4d61-89e7-88639da4683d": "User.Read",
                        "64a6cdd6-aab1-4aaf-94b8-3cc8405e90d0": "email",
                        "14dad69e-099b-42c9-810b-d002981feec1": "profile",
                        "37f7f235-527c-4136-accd-4a02d197296e": "offline_access",
                    }
                    scope_name = scope_map.get(scope_id, f"Scope {scope_id}")
                    print(f"       - {scope_name} ({scope_type})")
    
    # Check redirect URIs
    web_redirects = ms_data.get("web", {}).get("redirectUris", [])
    public_redirects = ms_data.get("public_client", {}).get("redirectUris", [])
    
    if web_redirects or public_redirects:
        print(f"\n   Redirect URIs:")
        if web_redirects:
            for uri in web_redirects:
                print(f"     - Web: {uri}")
        if public_redirects:
            for uri in public_redirects:
                print(f"     - Public Client: {uri}")
    else:
        print(f"\n   ⚠️  No redirect URIs configured")
        print(f"      You may need to add redirect URIs for OAuth flows")
    
    # Create a helpful config file template
    config_file = ASSISTANT_HUB_DIR / "azure_config_from_json.txt"
    try:
        with open(config_file, 'w') as f:
            f.write("# Microsoft Graph Credentials (from JSON file)\n")
            f.write("# NOTE: You still need to get the CLIENT SECRET VALUE from Azure Portal\n")
            f.write("# Azure Portal > App registrations > os_dashboard_ai_assistant > Certificates & secrets\n")
            f.write("# Copy the SECRET VALUE (not the Secret ID) and add it below\n\n")
            f.write(f"# App Registration Details:\n")
            f.write(f"# Display Name: {ms_data.get('display_name', 'N/A')}\n")
            f.write(f"# App ID (Client ID): {ms_data.get('app_id', 'N/A')}\n")
            f.write(f"# Object ID: {ms_data.get('object_id', 'N/A')}\n")
            f.write(f"# Publisher Domain: {ms_data.get('publisher_domain', 'N/A')}\n")
            f.write(f"# Sign-in Audience: {ms_data.get('sign_in_audience', 'N/A')}\n\n")
            f.write(f"# Extract tenant ID from publisher domain or Azure Portal\n")
            f.write(f"# For personal Microsoft accounts, use 'consumers' or 'common'\n")
            f.write(f"AZURE_TENANT_ID=\n")
            f.write(f"AZURE_CLIENT_ID={ms_data.get('app_id', '')}\n")
            f.write(f"AZURE_CLIENT_SECRET=\n")
        
        print(f"\n✅ Created config template: {config_file}")
        print(f"   Edit this file and add your TENANT_ID and CLIENT_SECRET")
    except Exception as e:
        print(f"⚠️  Could not create config template: {e}")
    
    return True


def main():
    """Main setup function."""
    print("=" * 70)
    print("Third-Party Credentials Setup")
    print("=" * 70)
    
    ensure_assistant_hub_dir()
    
    # Setup Google credentials
    print("\n" + "=" * 70)
    print("Setting up Google OAuth credentials...")
    print("=" * 70)
    google_success = setup_google_credentials()
    
    # Setup Microsoft Graph credentials
    print("\n" + "=" * 70)
    print("Setting up Microsoft Graph credentials...")
    print("=" * 70)
    ms_success = setup_microsoft_graph_credentials()
    
    # Summary
    print("\n" + "=" * 70)
    print("Setup Summary")
    print("=" * 70)
    print(f"Google OAuth: {'✅ Success' if google_success else '❌ Failed'}")
    print(f"Microsoft Graph: {'✅ Success' if ms_success else '❌ Failed'}")
    
    if google_success:
        print("\n📧 Next steps for Google integrations:")
        print("   1. Gmail and Calendar integrations will now find credentials")
        print("   2. Complete OAuth2 flow in the GUI (Tools & Operations tab)")
        print("   3. Or use the Google OAuth2 flow manually")
    
    if ms_success:
        print("\n📧 Next steps for Microsoft Graph integrations:")
        print("   1. Get your TENANT_ID from Azure Portal or use 'consumers'/'common' for personal accounts")
        print("   2. Get your CLIENT_SECRET VALUE from Azure Portal:")
        print("      Azure Portal > App registrations > os_dashboard_ai_assistant > Certificates & secrets")
        print("   3. Edit ~/.assistant_hub/azure_config_from_json.txt and add TENANT_ID and CLIENT_SECRET")
        print("   4. Or run: python get_azure_credentials.py")
        print("   5. Or configure in GUI: Settings > Integrations > Configure Azure")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()



