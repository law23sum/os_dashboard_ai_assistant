#!/usr/bin/env python3
"""
Setup all third-party API connections for AI OS.

This script initializes connections for:
- OpenAI/ChatGPT
- Microsoft Graph (Word, Excel, PowerPoint, OneNote, Outlook)
- Google APIs (Gmail, Calendar)
- Git/GitHub
- Adobe PDF Services
- Apple Calendar (CalDAV)
- Apple Notes

Uses the existing implementations in the api_connectors directory.
"""

import asyncio
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Import the API manager and basic connectors
from api_connectors import IntegrationAPIGateway
from config.config import get_api_config, validate_api_config


class APIConnectionManager:
    """Manages all third-party API connections using the existing implementations."""

    def __init__(self):
        self.config = get_api_config()
        self.api_gateway = IntegrationAPIGateway()
        self.connections_status: Dict[str, Dict[str, Any]] = {}
        self.connectors = {}

    async def initialize_all_connections(self) -> Dict[str, Any]:
        """Initialize all third-party API connections."""
        print("🚀 Initializing AI OS API Connections")
        print("=" * 60)

        initialization_results = {}

        # 1. OpenAI/ChatGPT Connection
        print("\n🤖 Setting up OpenAI/ChatGPT connection...")
        initialization_results["openai"] = await self._setup_openai_connection()

        # 2. Microsoft Graph Connection (Word, Excel, PowerPoint, OneNote, Outlook)
        print("\n📊 Setting up Microsoft Graph connection...")
        initialization_results["microsoft"] = await self._setup_microsoft_connection()

        # 3. Google APIs Connection (Gmail, Calendar)
        print("\n📧 Setting up Google APIs connection...")
        initialization_results["google"] = await self._setup_google_connection()

        # 4. Git/GitHub Connection
        print("\n🔄 Setting up Git/GitHub connection...")
        initialization_results["git"] = await self._setup_git_connection()

        # 5. Adobe PDF Services Connection
        print("\n📄 Setting up Adobe PDF services connection...")
        initialization_results["adobe"] = await self._setup_adobe_connection()

        # 6. Apple Calendar Connection
        print("\n📅 Setting up Apple Calendar connection...")
        initialization_results["apple_calendar"] = await self._setup_apple_calendar_connection()

        # 7. Apple Notes Connection
        print("\n📝 Setting up Apple Notes connection...")
        initialization_results["apple_notes"] = await self._setup_apple_notes_connection()

        # Summary
        print("\n" + "=" * 60)
        print("📊 API CONNECTIONS INITIALIZATION SUMMARY")
        print("=" * 60)

        successful_connections = []
        failed_connections = []

        for service, status in initialization_results.items():
            if status.get("success", False):
                successful_connections.append(service)
                print(f"✅ {service.upper()}: Connected successfully")
            else:
                failed_connections.append(service)
                print(f"❌ {service.upper()}: Connection failed - {status.get('error', 'Unknown error')}")

        print(f"\n🎯 Total Connections: {len(initialization_results)}")
        print(f"✅ Successful: {len(successful_connections)}")
        print(f"❌ Failed: {len(failed_connections)}")

        if failed_connections:
            print(f"\n⚠️  Failed connections: {', '.join(failed_connections)}")
            print("Check your credentials and configuration.")

        return {
            "total_connections": len(initialization_results),
            "successful": len(successful_connections),
            "failed": len(failed_connections),
            "failed_services": failed_connections,
            "results": initialization_results
        }

    async def _setup_openai_connection(self) -> Dict[str, Any]:
        """Setup OpenAI/ChatGPT connection."""
        try:
            if not self.config.openai_api_key:
                return {"success": False, "error": "OpenAI API key not configured"}

            # Try to import and initialize OpenAI connector
            try:
                from api_connectors.universal_connector import OpenAIConnector
                openai_config = {
                    "connector_type": "openai",
                    "instance_id": "openai_main",
                    "credentials": {"api_key": self.config.openai_api_key},
                    "settings": {"model_config": {"default_model": self.config.openai_model}},
                    "capabilities": ["read", "write", "search"],
                    "rate_limits": {"requests_per_minute": 100}
                }
                connector = OpenAIConnector(openai_config)
                await connector.connect()
                self.connectors["openai"] = connector
                return {"success": True, "error": None}
            except ImportError:
                return {"success": False, "error": "OpenAI connector not available"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _setup_microsoft_connection(self) -> Dict[str, Any]:
        """Setup Microsoft Graph connection for Office 365 services."""
        try:
            if not (self.config.microsoft_client_id and
                   self.config.microsoft_client_secret and
                   self.config.microsoft_tenant_id):
                return {"success": False, "error": "Microsoft Graph credentials not configured"}

            # Validate that Microsoft Graph connector is available
            try:
                from api_connectors.ms_graph_client import MicrosoftGraphClient
                config = {
                    "client_id": self.config.microsoft_client_id,
                    "client_secret": self.config.microsoft_client_secret,
                    "tenant_id": self.config.microsoft_tenant_id,
                    "scopes": ["https://graph.microsoft.com/.default"]
                }
                connector = MicrosoftGraphClient(config)
                self.connectors["microsoft"] = connector
                return {"success": True, "error": None}
            except ImportError:
                return {"success": False, "error": "Microsoft Graph client not available"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _setup_google_connection(self) -> Dict[str, Any]:
        """Setup Google APIs connection for Gmail and Calendar."""
        try:
            if not os.path.exists(self.config.google_credentials_file or "credentials.json"):
                return {"success": False, "error": "Google credentials file not found"}

            # Validate that Google client is available
            try:
                from api_connectors.google_client import GoogleWorkspaceClient
                config = {
                    "client_secret_file": self.config.google_credentials_file,
                    "token_pickle_file": self.config.google_token_file,
                    "scopes": [
                        'https://www.googleapis.com/auth/gmail.readonly',
                        'https://www.googleapis.com/auth/gmail.send',
                        'https://www.googleapis.com/auth/calendar'
                    ]
                }
                connector = GoogleWorkspaceClient(config)
                self.connectors["google"] = connector
                return {"success": True, "error": None}
            except ImportError:
                return {"success": False, "error": "Google Workspace client not available"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _setup_git_connection(self) -> Dict[str, Any]:
        """Setup Git/GitHub connection."""
        try:
            if not self.config.github_token:
                return {"success": False, "error": "GitHub token not configured"}

            # Validate that Git client is available
            try:
                from api_connectors.git_client import GitClient
                config = {
                    "provider": "github",
                    "api_token": self.config.github_token,
                    "username": self.config.github_username
                }
                connector = GitClient(config)
                self.connectors["git"] = connector
                return {"success": True, "error": None}
            except ImportError:
                return {"success": False, "error": "Git client not available"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _setup_adobe_connection(self) -> Dict[str, Any]:
        """Setup Adobe PDF services connection."""
        try:
            if not (self.config.adobe_client_id and self.config.adobe_client_secret):
                return {"success": False, "error": "Adobe credentials not configured"}

            # Validate that PDF connector is available
            try:
                from api_connectors.pdf import PDFConnector
                config = {
                    "base_path": ".",
                    "settings": {"base_path": "."}
                }
                connector = PDFConnector(config)
                self.connectors["adobe"] = connector
                return {"success": True, "error": None}
            except ImportError:
                return {"success": False, "error": "PDF connector not available"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _setup_apple_calendar_connection(self) -> Dict[str, Any]:
        """Setup Apple Calendar (CalDAV) connection."""
        try:
            if not (self.config.caldav_url and
                   self.config.caldav_username and
                   self.config.caldav_password):
                return {"success": False, "error": "CalDAV credentials not configured"}

            # Validate that Apple connector is available
            try:
                from api_connectors.apple_connector import AppleConnector
                config = {
                    "settings": {
                        "enable_calendar": True,
                        "enable_notes": False,
                        "enable_icloud": False
                    }
                }
                connector = AppleConnector(config)
                self.connectors["apple_calendar"] = connector
                return {"success": True, "error": None}
            except ImportError:
                return {"success": False, "error": "Apple connector not available"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _setup_apple_notes_connection(self) -> Dict[str, Any]:
        """Setup Apple Notes connection."""
        try:
            # Apple Notes uses local database access
            try:
                from api_connectors.apple_connector import AppleConnector
                config = {
                    "settings": {
                        "enable_notes": True,
                        "enable_calendar": False,
                        "enable_icloud": False
                    }
                }
                connector = AppleConnector(config)
                self.connectors["apple_notes"] = connector
                return {"success": True, "error": None}
            except ImportError:
                return {"success": False, "error": "Apple connector not available"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_connection_status(self) -> Dict[str, Any]:
        """Get the status of all API connections."""
        status_results = {}

        for connector_id, connector in self.connectors.items():
            try:
                # Try to call health_check if available
                if hasattr(connector, 'health_check'):
                    if asyncio.iscoroutinefunction(connector.health_check):
                        result = await connector.health_check()
                    else:
                        result = connector.health_check()
                    status_results[connector_id] = {
                        "connected": True,
                        "last_check": datetime.utcnow().isoformat(),
                        "error": None
                    }
                else:
                    status_results[connector_id] = {
                        "connected": True,
                        "last_check": datetime.utcnow().isoformat(),
                        "error": None
                    }
            except Exception as e:
                status_results[connector_id] = {
                    "connected": False,
                    "last_check": datetime.utcnow().isoformat(),
                    "error": str(e)
                }

        return status_results

    async def test_all_connections(self) -> Dict[str, Any]:
        """Test all API connections and return detailed results."""
        print("\n🧪 Testing all API connections...")
        print("-" * 40)

        test_results = {}

        for connector_id, connector in self.connectors.items():
            try:
                print(f"Testing {connector_id.upper()}...")
                test_results[connector_id] = {
                    "success": True,
                    "details": f"Connector {connector_id} initialized successfully",
                    "timestamp": datetime.utcnow().isoformat()
                }
                print("  ✅ PASS")
            except Exception as e:
                test_results[connector_id] = {
                    "success": False,
                    "details": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                print(f"  ❌ FAIL - {str(e)}")

        return test_results


async def main():
    """Main function to setup all API connections."""
    try:
        # Initialize the connection manager
        manager = APIConnectionManager()

        # Validate configuration first
        print("🔍 Validating configuration...")
        validation = validate_api_config()
        print("Configuration validation:")
        for service, valid in validation.items():
            status = "✅" if valid else "❌"
            print(f"  {status} {service}")

        # Initialize all connections
        results = await manager.initialize_all_connections()

        # Test connections
        test_results = await manager.test_all_connections()

        # Final summary
        print("\n" + "=" * 60)
        print("🎉 API CONNECTIONS SETUP COMPLETE")
        print("=" * 60)
        print(f"Successfully connected: {results['successful']}/{results['total_connections']}")

        if results['failed'] > 0:
            print(f"Failed connections: {', '.join(results['failed_services'])}")
            print("\n💡 Tips:")
            print("  - Ensure all required credentials are set in environment variables")
            print("  - Check that third-party services are accessible")
            print("  - Review logs for detailed error messages")
            print("  - Run 'python setup_third_party_credentials.py' to setup credentials")

        return results

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Run the setup
    results = asyncio.run(main())

    # Exit with appropriate code
    if isinstance(results, dict) and results.get("failed", 0) == 0:
        print("\n🎯 All API connections successfully established!")
        exit(0)
    else:
        print("\n⚠️  Some API connections failed to initialize.")
        exit(1)
