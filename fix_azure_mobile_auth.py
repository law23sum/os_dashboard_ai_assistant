#!/usr/bin/env python3
"""
Fix Azure authentication for personal Microsoft accounts.

The error AADSTS70002 indicates that the app needs to be marked as 'mobile'
in Azure AD to use device code flow with personal Microsoft accounts.
"""

import os
from pathlib import Path

def fix_azure_config():
    """Update Azure configuration to use consumers endpoint for personal accounts."""

    config_file = Path.home() / ".assistant_hub" / "azure_config.txt"

    print("🔧 Fixing Azure Authentication Configuration")
    print("=" * 60)

    # Read current config
    current_config = {}
    if config_file.exists():
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    current_config[key.strip()] = value.strip()

    print("Current configuration:")
    for key, value in current_config.items():
        if "SECRET" in key:
            print(f"  {key}=[HIDDEN]")
        else:
            print(f"  {key}={value}")

    print("\n⚠️  ISSUE: Your Azure app is configured for personal Microsoft accounts")
    print("   but not marked as a 'mobile' application in Azure AD.")
    print("   The device code flow requires mobile app designation.")

    print("\n🔧 SOLUTION: Updating configuration to use /consumers endpoint...")

    # Update tenant to consumers
    current_config["AZURE_TENANT_ID"] = "consumers"

    # Write updated config
    os.makedirs(config_file.parent, exist_ok=True)
    with open(config_file, 'w') as f:
        f.write("# Azure Authentication Configuration\n")
        f.write("# Updated for personal Microsoft accounts (consumers endpoint)\n")
        f.write("\n")
        for key, value in current_config.items():
            f.write(f"{key}={value}\n")

    print("✅ Configuration updated!")
    print(f"   Tenant ID changed to: consumers")
    print(f"   Config saved to: {config_file}")

    print("\n🔄 Testing the fix...")
    print("   Run: python test_azure_auth.py")
    print("   Or: python assistant_hub_gui/manage_integrations.py")

    print("\n📋 If authentication still fails, you have two options:")
    print("\n   OPTION 1 - Fix in Azure Portal (Recommended):")
    print("   1. Go to https://portal.azure.com")
    print("   2. Navigate to Azure Active Directory > App registrations")
    print("   3. Find your app (Client ID starts with c309551b...)")
    print("   4. Go to Authentication > Platform configurations")
    print("   5. Add a platform > Mobile and desktop applications")
    print("   6. Add these redirect URIs:")
    print("      - https://login.microsoftonline.com/common/oauth2/nativeclient")
    print("      - https://login.microsoftonline.com/consumers/oauth2/nativeclient")
    print("   7. Save the changes")

    print("\n   OPTION 2 - Use different authentication flow:")
    print("   1. Use authorization code flow instead of device code")
    print("   2. Or configure the app for organizational accounts")

    print("\n🔐 Your app supports personal Microsoft accounts only.")
    print("   Make sure you're signing in with a personal Microsoft account (hotmail.com, outlook.com, etc.)")

if __name__ == "__main__":
    fix_azure_config()
