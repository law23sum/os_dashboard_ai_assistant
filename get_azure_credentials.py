#!/usr/bin/env python3
"""Helper script to guide users through getting Azure credentials."""

import os
import webbrowser
import sys
from pathlib import Path

def print_instructions():
    """Print detailed instructions for getting Azure credentials."""
    print("\n" + "="*70)
    print("AZURE CREDENTIALS SETUP GUIDE")
    print("="*70)
    print("\nTo get your Azure Client ID and Client Secret, follow these steps:\n")
    print("1. Go to Azure Portal: https://portal.azure.com")
    print("2. Navigate to: Azure Active Directory > App registrations")
    print("3. Click 'New registration' (or select an existing app)")
    print("4. Fill in the app details:")
    print("   - Name: e.g., 'OS Dashboard Assistant'")
    print("   - Supported account types: Your choice")
    print("   - Redirect URI: Leave blank for now")
    print("5. Click 'Register'")
    print("\n6. On the Overview page, copy these values:")
    print("   - Tenant ID (Directory ID)")
    print("   - Application (client) ID")
    print("\n7. Go to 'Certificates & secrets' in the left menu")
    print("8. Click 'New client secret'")
    print("9. Add a description and choose expiration")
    print("10. Click 'Add'")
    print("11. ⚠️  IMPORTANT: Copy the SECRET VALUE (not the Secret ID!)")
    print("    - The Value column shows the actual secret (e.g., 'abc~DEF123...')")
    print("    - The Secret ID is a GUID - DO NOT use this")
    print("    - You can only see the Value once, so copy it immediately!")
    print("\n12. Go to 'API permissions' in the left menu")
    print("13. Click 'Add a permission' > 'Microsoft Graph' > 'Delegated permissions'")
    print("14. Add these permissions:")
    print("    - Notes.ReadWrite (for OneNote)")
    print("    - Files.ReadWrite.All (for Excel/Word)")
    print("    - User.Read (for basic user info)")
    print("15. Click 'Add permissions'")
    print("16. Click 'Grant admin consent' (if you have admin rights)")
    print("\n" + "="*70)
    print("\nOnce you have the credentials, you can:")
    print("1. Set them as environment variables:")
    print("   export AZURE_TENANT_ID='your-tenant-id'")
    print("   export AZURE_CLIENT_ID='your-client-id'")
    print("   export AZURE_CLIENT_SECRET='your-client-secret'")
    print("\n2. Or configure them in the GUI:")
    print("   - Open the OS Dashboard Assistant GUI")
    print("   - Go to Tools & Operations tab")
    print("   - Click 'Configure Microsoft Graph'")
    print("   - Enter your credentials")
    print("\n3. Or save them to a config file:")
    print("   ~/.assistant_hub/azure_config.txt")
    print("\n" + "="*70 + "\n")

def open_azure_portal():
    """Open Azure Portal in the default browser."""
    url = "https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps"
    print(f"Opening Azure Portal: {url}")
    webbrowser.open(url)
    print("Azure Portal should now be open in your browser.\n")

def check_existing_credentials():
    """Check if credentials are already configured."""
    config_file = Path.home() / ".assistant_hub" / "azure_config.txt"
    env_vars = {
        "AZURE_TENANT_ID": os.environ.get("AZURE_TENANT_ID"),
        "AZURE_CLIENT_ID": os.environ.get("AZURE_CLIENT_ID"),
        "AZURE_CLIENT_SECRET": os.environ.get("AZURE_CLIENT_SECRET"),
    }
    
    has_env = all(env_vars.values())
    
    has_file = False
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                content = f.read()
                has_file = "AZURE_TENANT_ID" in content and "AZURE_CLIENT_ID" in content
        except Exception:
            pass
    
    if has_env or has_file:
        print("\n✓ Azure credentials appear to be configured!")
        if has_env:
            print("  Found in environment variables")
        if has_file:
            print(f"  Found in config file: {config_file}")
        print("\nTo update them, use the GUI or edit the config file.\n")
        return True
    else:
        print("\n⚠ Azure credentials not found.")
        print("  Please follow the instructions below to set them up.\n")
        return False

def main():
    """Main function."""
    print("\nAzure Credentials Helper")
    print("-" * 70)
    
    # Check for existing credentials
    has_creds = check_existing_credentials()
    
    if not has_creds or "--force" in sys.argv:
        # Ask if user wants to open Azure Portal
        if "--open" in sys.argv or input("\nOpen Azure Portal in browser? (y/n): ").lower() == 'y':
            open_azure_portal()
        
        # Print instructions
        print_instructions()
        
        # Offer to save credentials interactively
        if input("\nDo you have your credentials ready to configure? (y/n): ").lower() == 'y':
            tenant_id = input("Enter Tenant ID: ").strip()
            client_id = input("Enter Client ID: ").strip()
            client_secret = input("Enter Client Secret: ").strip()
            
            if all([tenant_id, client_id, client_secret]):
                # Save to config file
                config_dir = Path.home() / ".assistant_hub"
                config_dir.mkdir(exist_ok=True)
                config_file = config_dir / "azure_config.txt"
                
                try:
                    with open(config_file, "w") as f:
                        f.write(f"AZURE_TENANT_ID={tenant_id}\n")
                        f.write(f"AZURE_CLIENT_ID={client_id}\n")
                        f.write(f"AZURE_CLIENT_SECRET={client_secret}\n")
                    print(f"\n✓ Credentials saved to: {config_file}")
                    print("  They will be loaded automatically when you run the application.\n")
                except Exception as e:
                    print(f"\n✗ Error saving credentials: {e}\n")
            else:
                print("\n⚠ All fields are required. Please try again.\n")
    else:
        print("\nYour credentials are already configured!")
        print("To reconfigure, run this script with --force flag.\n")

if __name__ == "__main__":
    main()

