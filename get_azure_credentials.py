#!/usr/bin/env python3
"""Helper script to guide users through getting Azure credentials."""

import os
import webbrowser
import sys
import re
from pathlib import Path
from typing import Tuple

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
    print("     • For organizational accounts: Use your Tenant ID (GUID)")
    print("     • For personal Microsoft accounts: Use 'consumers'")
    print("     • For both types: Use 'common'")
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
    print("\n17. Go to 'Authentication' in the left menu")
    print("18. Under 'Platform configurations', click 'Add a platform' > 'Web'")
    print("19. Add redirect URI: http://localhost:8080 (or your preferred redirect URI)")
    print("20. Click 'Configure'")
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

def is_guid(value: str) -> bool:
    """Check if a string looks like a GUID (Secret ID format)."""
    guid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    return bool(re.match(guid_pattern, value.strip()))


def validate_client_secret(secret: str) -> Tuple[bool, str]:
    """Validate that the client secret looks like a Secret Value, not a Secret ID."""
    secret = secret.strip()
    
    if not secret:
        return False, "Client secret cannot be empty"
    
    # Secret IDs are GUIDs (36 characters with dashes)
    if is_guid(secret):
        return False, (
            "⚠️  WARNING: This looks like a Secret ID (GUID), not a Secret Value!\n"
            "   Secret IDs look like: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'\n"
            "   Secret Values are longer strings with special characters like: 'abc~DEF123...'\n"
            "   Please go to Azure Portal > App registrations > Your app > Certificates & secrets\n"
            "   and copy the VALUE column (not the Secret ID column).\n"
            "   If the secret has expired, create a new one."
        )
    
    # Secret Values are typically 40+ characters and may contain special chars
    if len(secret) < 20:
        return False, "Client secret seems too short. Secret Values are typically 40+ characters."
    
    return True, "✓ Client secret format looks valid"


def test_credentials(tenant_id: str, client_id: str, client_secret: str) -> Tuple[bool, str]:
    """Test Azure credentials by attempting to get an access token."""
    try:
        # Try importing the auth module
        sys.path.insert(0, str(Path(__file__).parent))
        sys.path.insert(0, str(Path(__file__).parent / "assistant_hub_gui"))
        
        try:
            from assistant_hub.integrations.msgraph.auth import GraphAuth, GraphCredentials
        except ImportError:
            from assistant_hub_gui.assistant_hub.integrations.msgraph.auth import GraphAuth, GraphCredentials
        
        credentials = GraphCredentials(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        print("\n🔄 Testing credentials...")
        auth = GraphAuth(credentials)
        token = auth.get_token()
        
        if token:
            return True, "✅ Credentials are valid! Access token retrieved successfully."
        else:
            return False, "❌ Failed to get access token (no error details)"
            
    except Exception as e:
        error_msg = str(e)
        if "400" in error_msg or "Bad Request" in error_msg:
            return False, (
                "❌ Bad Request (400) - Invalid request format!\n"
                "   Common causes:\n"
                "   1. Credentials have extra spaces, newlines, or special characters\n"
                "   2. Tenant ID, Client ID, or Client Secret is malformed\n"
                "   3. Missing or incorrect credentials\n"
                "   Please:\n"
                "   1. Check your credentials for extra spaces or newlines\n"
                "   2. Re-enter credentials carefully\n"
                "   3. Run: python get_azure_credentials.py --force to reconfigure"
            )
        elif "AADSTS7000215" in error_msg or "invalid_client" in error_msg.lower():
            return False, (
                "❌ Invalid client secret!\n"
                "   The secret you provided is incorrect or has expired.\n"
                "   Please:\n"
                "   1. Go to Azure Portal > App registrations > Your app > Certificates & secrets\n"
                "   2. Check if your secret has expired\n"
                "   3. Create a new secret if needed\n"
                "   4. Copy the SECRET VALUE (not the Secret ID)\n"
                "   5. Make sure you're copying the entire value"
            )
        elif "AADSTS700016" in error_msg or "unauthorized_client" in error_msg.lower():
            return False, (
                "❌ App registration not found!\n"
                "   Please verify:\n"
                "   1. The Tenant ID is correct\n"
                "   2. The Client ID is correct\n"
                "   3. The app registration exists in Azure Portal"
            )
        else:
            return False, f"❌ Authentication failed: {error_msg}"


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

def clean_credential(value: str) -> str:
    """Clean credential value by stripping whitespace and newlines."""
    if not value:
        return ""
    # Strip all whitespace including newlines, tabs, etc.
    cleaned = value.strip().replace("\n", "").replace("\r", "").replace("\t", "")
    return cleaned


def test_existing_credentials():
    """Test existing credentials from config file or environment."""
    print("\n" + "="*70)
    print("TESTING EXISTING AZURE CREDENTIALS")
    print("="*70)
    
    # Load credentials
    config_file = Path.home() / ".assistant_hub" / "azure_config.txt"
    tenant_id = clean_credential(os.environ.get("AZURE_TENANT_ID", ""))
    client_id = clean_credential(os.environ.get("AZURE_CLIENT_ID", ""))
    client_secret = clean_credential(os.environ.get("AZURE_CLIENT_SECRET", ""))
    
    # Load from config file if not in environment
    if not all([tenant_id, client_id, client_secret]) and config_file.exists():
        try:
            with open(config_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = clean_credential(value)
                        if key == "AZURE_TENANT_ID" and not tenant_id:
                            tenant_id = value
                        elif key == "AZURE_CLIENT_ID" and not client_id:
                            client_id = value
                        elif key == "AZURE_CLIENT_SECRET" and not client_secret:
                            client_secret = value
        except Exception as e:
            print(f"Error reading config file: {e}")
            return 1
    
    if not all([tenant_id, client_id, client_secret]):
        print("\n❌ Credentials not found!")
        print("   Please configure credentials first using:")
        print("   python get_azure_credentials.py")
        return 1
    
    print(f"\n✓ Found credentials:")
    print(f"   Tenant ID: {tenant_id[:8]}... (length: {len(tenant_id)})")
    print(f"   Client ID: {client_id[:8]}... (length: {len(client_id)})")
    print(f"   Client Secret: {'*' * min(len(client_secret), 20)}... (length: {len(client_secret)})")
    
    # Check for potential issues
    if "\n" in tenant_id or "\n" in client_id or "\n" in client_secret:
        print("\n⚠️  WARNING: Credentials contain newlines - this may cause 400 errors!")
        print("   Cleaning credentials...")
        tenant_id = clean_credential(tenant_id)
        client_id = clean_credential(client_id)
        client_secret = clean_credential(client_secret)
    
    # Validate format
    is_valid, validation_msg = validate_client_secret(client_secret)
    print(f"\n{validation_msg}")
    
    # Test credentials
    test_success, test_msg = test_credentials(tenant_id, client_id, client_secret)
    print(f"\n{test_msg}\n")
    
    return 0 if test_success else 1


def main():
    """Main function."""
    print("\nAzure Credentials Helper")
    print("-" * 70)
    
    # Check for --test flag
    if "--test" in sys.argv:
        return test_existing_credentials()
    
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
            tenant_id = clean_credential(input("Enter Tenant ID: "))
            client_id = clean_credential(input("Enter Client ID: "))
            client_secret = clean_credential(input("Enter Client Secret: "))
            
            if all([tenant_id, client_id, client_secret]):
                # Validate client secret format
                is_valid, validation_msg = validate_client_secret(client_secret)
                print(f"\n{validation_msg}")
                
                if not is_valid:
                    if input("\nDo you want to continue anyway? (y/n): ").lower() != 'y':
                        print("\nConfiguration cancelled. Please check your credentials and try again.\n")
                        return
                
                # Test credentials if user wants
                test_creds = input("\nTest credentials before saving? (recommended) (y/n): ").lower() == 'y'
                if test_creds:
                    test_success, test_msg = test_credentials(tenant_id, client_id, client_secret)
                    print(f"\n{test_msg}\n")
                    
                    if not test_success:
                        if input("Do you want to save anyway? (y/n): ").lower() != 'y':
                            print("\nConfiguration cancelled. Please fix your credentials and try again.\n")
                            return
                
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
                    
                    # If we didn't test before, offer to test now
                    if not test_creds:
                        if input("Test credentials now? (y/n): ").lower() == 'y':
                            test_success, test_msg = test_credentials(tenant_id, client_id, client_secret)
                            print(f"\n{test_msg}\n")
                            
                except Exception as e:
                    print(f"\n✗ Error saving credentials: {e}\n")
            else:
                print("\n⚠ All fields are required. Please try again.\n")
    else:
        print("\nYour credentials are already configured!")
        print("To reconfigure, run this script with --force flag.")
        print("To test existing credentials, run: python get_azure_credentials.py --test\n")

if __name__ == "__main__":
    main()

