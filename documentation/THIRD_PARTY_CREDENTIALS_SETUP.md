# Third-Party Credentials Setup

This document explains how the two JSON files in the root directory are used to resolve third-party interface authentication issues.

## JSON Files

### 1. `client_secret_788356908604-ro9n0fq4p70q569237314n12u84jnren.apps.googleusercontent.com.json`

**Purpose:** Google OAuth 2.0 client credentials for Gmail and Google Calendar integrations.

**Contents:**
- Client ID
- Client Secret
- OAuth endpoints (auth URI, token URI)
- Redirect URIs

**Usage:**
- Automatically detected by Gmail and Google Calendar integrations
- Copied to `~/.assistant_hub/gmail_credentials.json` and `~/.assistant_hub/google_calendar_credentials.json` when you run `setup_third_party_credentials.py`
- The integrations check the root directory first, then fall back to `~/.assistant_hub/`

**Next Steps:**
1. Run `python setup_third_party_credentials.py` to copy credentials to expected locations
2. Complete OAuth2 flow in the GUI (Tools & Operations tab) or manually
3. Gmail and Calendar integrations will now be able to authenticate

---

### 2. `os_dashboard_ai_assistant(Microsoft Graph format).json`

**Purpose:** Microsoft Graph app registration details for OneNote, Excel, Word, and OneDrive integrations.

**Contents:**
- App ID (Client ID): `c309551b-b97a-4e33-92a6-747532d251bf`
- Object ID: `4c359e0f-21f1-4f0b-bf1f-372c86f28f9e`
- Display Name: `os_dashboard_ai_assistant`
- Publisher Domain: `cswm7876yahoo.onmicrosoft.com`
- Sign-in Audience: `PersonalMicrosoftAccount`
- Required Permissions: Microsoft Graph (User.Read)
- Password Credentials: Information about client secrets (but not the secret value itself)

**Important Notes:**
- ⚠️ The JSON file does NOT contain the client secret VALUE (for security reasons)
- The client secret VALUE must be obtained from Azure Portal
- The JSON file provides the App ID (Client ID) which can be used automatically

**Usage:**
- The Microsoft Graph authentication system automatically extracts the Client ID from this file
- A config template is created at `~/.assistant_hub/azure_config_from_json.txt` with the Client ID pre-filled
- You still need to add:
  - `AZURE_TENANT_ID` (use `consumers` or `common` for personal Microsoft accounts)
  - `AZURE_CLIENT_SECRET` (get the VALUE from Azure Portal)

**Next Steps:**
1. Run `python setup_third_party_credentials.py` to parse the JSON and create config template
2. Get your CLIENT SECRET VALUE from Azure Portal:
   - Go to: Azure Portal > App registrations > os_dashboard_ai_assistant > Certificates & secrets
   - Copy the SECRET VALUE (not the Secret ID!)
3. Edit `~/.assistant_hub/azure_config_from_json.txt` and add:
   - `AZURE_TENANT_ID=consumers` (or your tenant ID)
   - `AZURE_CLIENT_SECRET=<your-secret-value>`
4. Or configure via GUI: Settings > Integrations > Configure Azure
5. Or run: `python get_azure_credentials.py`

---

## Setup Script

### `setup_third_party_credentials.py`

This script automates the setup process:

```bash
python setup_third_party_credentials.py
```

**What it does:**
1. ✅ Copies Google OAuth credentials to expected locations
2. ✅ Parses Microsoft Graph JSON and extracts app registration details
3. ✅ Creates config template with pre-filled Client ID
4. ✅ Provides clear next steps for completing setup

**Output:**
- Google credentials copied to `~/.assistant_hub/`
- Microsoft Graph config template created
- Detailed information about what's configured and what's missing

---

## Integration Updates

### Google Integrations (Gmail & Calendar)

**Updated Files:**
- `assistant_hub/integrations/gmail.py`
- `assistant_hub/integrations/google_calendar.py`

**Changes:**
- Now checks project root directory first for credentials
- Falls back to `~/.assistant_hub/` if not found in root
- Automatically uses the client secret file if present

### Microsoft Graph Integration

**Updated Files:**
- `assistant_hub/integrations/msgraph/auth.py`

**Changes:**
- Added Priority 4: Loads Client ID from JSON file as fallback
- Automatically extracts `appId` from the Microsoft Graph JSON
- Still requires manual configuration of Tenant ID and Client Secret

---

## Troubleshooting

### Google OAuth Issues

**Problem:** "Credentials not configured"
- **Solution:** Run `python setup_third_party_credentials.py` to copy credentials

**Problem:** "Not authenticated"
- **Solution:** Complete OAuth2 flow in GUI or manually authenticate

### Microsoft Graph Issues

**Problem:** "Missing Azure credentials: AZURE_CLIENT_ID"
- **Solution:** The Client ID is now automatically loaded from JSON file. If still missing, check JSON file path.

**Problem:** "Missing Azure credentials: AZURE_TENANT_ID"
- **Solution:** 
  - For personal Microsoft accounts: Use `consumers` or `common`
  - For organizational accounts: Get Tenant ID from Azure Portal
  - Add to `~/.assistant_hub/azure_config.txt` or environment variables

**Problem:** "Missing Azure credentials: AZURE_CLIENT_SECRET"
- **Solution:** 
  - Get the SECRET VALUE from Azure Portal (not the Secret ID!)
  - Azure Portal > App registrations > os_dashboard_ai_assistant > Certificates & secrets
  - Copy the Value column (you can only see it once!)
  - Add to `~/.assistant_hub/azure_config.txt` or environment variables

**Problem:** "401 Unauthorized" or "400 Bad Request"
- **Solution:** 
  - Verify credentials don't have extra spaces or newlines
  - Check that client secret hasn't expired
  - Ensure API permissions are granted in Azure Portal
  - For `/me/` endpoints, ensure proper API permissions are configured in Azure Portal

---

## Summary

✅ **Google OAuth:** Fully automated - just run the setup script and complete OAuth flow
✅ **Microsoft Graph Client ID:** Automatically loaded from JSON file
⚠️ **Microsoft Graph Tenant ID & Secret:** Still require manual configuration (for security)

The JSON files significantly simplify the setup process by:
1. Providing credentials in a standard format
2. Automatically detecting and using them
3. Reducing manual configuration steps
4. Providing clear error messages and next steps

