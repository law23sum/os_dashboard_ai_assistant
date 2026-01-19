#!/usr/bin/env python3
"""Plugin Manager CLI for AI OS."""

import asyncio
import sys
import os
from pathlib import Path
import argparse

# Add current directory to path for proper imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from assistant_core.dashboard_engine import DashboardEngine
from config.logging_config import configure_logging

class PluginManager:
    """Command-line interface for plugin management."""

    def __init__(self):
        self.dashboard_engine = None

    async def initialize(self):
        """Initialize the plugin manager."""
        configure_logging()
        self.dashboard_engine = DashboardEngine()
        await self.dashboard_engine.initialize_plugin_marketplace()
        print("🔌 Plugin Manager initialized")

    async def list_plugins(self, args):
        """List available plugins."""
        try:
            plugins = await self.dashboard_engine.search_plugins(
                query=getattr(args, 'query', None),
                plugin_type=getattr(args, 'type', None)
            )

            if not plugins:
                print("No plugins found matching criteria.")
                return

            print(f"\n📦 Found {len(plugins)} plugins:")
            print("-" * 80)

            for plugin in plugins:
                status = "✅ Installed" if plugin.get('installed', False) else "📦 Available"
                verified = "🔒 Verified" if plugin.get('verified', False) else ""
                rating = f"⭐ {plugin['rating']}" if plugin['rating'] > 0 else ""

                print(f"🔌 {plugin['name']} (v{plugin['version']})")
                print(f"   {plugin['description']}")
                print(f"   Type: {plugin['type']} | Author: {plugin['author']}")
                print(f"   Downloads: {plugin['download_count']} {rating} {verified} | {status}")
                print()

        except Exception as e:
            print(f"❌ Error listing plugins: {e}")

    async def show_plugin(self, args):
        """Show detailed plugin information."""
        try:
            details = await self.dashboard_engine.get_plugin_details(args.plugin_id)

            if 'error' in details:
                print(f"❌ Error: {details['error']}")
                return

            manifest = details['manifest']
            metadata = details['metadata']

            print(f"\n🔌 Plugin: {manifest['name']} (v{manifest['version']})")
            print("=" * 80)
            print(f"ID: {details['id']}")
            print(f"Description: {manifest['description']}")
            print(f"Author: {manifest['author']} ({manifest['author_email']})")
            print(f"Type: {manifest['type']} | Category: {manifest['category']}")
            print(f"License: {manifest['license']} | Website: {manifest['website']}")
            print(f"Tags: {', '.join(manifest['tags'])}")
            print()
            print(f"Status: {metadata['status']} | Security: {metadata['security_level']}")
            print(f"Downloads: {metadata['download_count']} | Rating: {metadata['rating']}/5.0")
            print(f"Reviews: {metadata['review_count']} | Verified: {'Yes' if metadata['verified'] else 'No'}")
            print(f"Created: {metadata['created_at'] or 'Unknown'}")
            print(f"Installed: {'Yes' if details['installed'] else 'No'}")

        except Exception as e:
            print(f"❌ Error showing plugin details: {e}")

    async def install_plugin(self, args):
        """Install a plugin."""
        try:
            print(f"📦 Installing plugin: {args.plugin_id}...")
            result = await self.dashboard_engine.install_plugin(args.plugin_id, args.version)

            if result['status'] == 'installed':
                print(f"✅ Plugin {args.plugin_id} v{result['version']} installed successfully!")
            elif result['status'] == 'dependency_error':
                print(f"❌ Dependency error: {', '.join(result['missing_dependencies'])}")
            else:
                print(f"❌ Installation failed: {result.get('message', 'Unknown error')}")

        except Exception as e:
            print(f"❌ Error installing plugin: {e}")

    async def uninstall_plugin(self, args):
        """Uninstall a plugin."""
        try:
            print(f"🗑️ Uninstalling plugin: {args.plugin_id}...")
            result = await self.dashboard_engine.uninstall_plugin(args.plugin_id)

            if result['status'] == 'uninstalled':
                print(f"✅ Plugin {args.plugin_id} uninstalled successfully!")
            else:
                print(f"❌ Uninstallation failed: {result.get('message', 'Unknown error')}")

        except Exception as e:
            print(f"❌ Error uninstalling plugin: {e}")

    async def marketplace_stats(self, args):
        """Show marketplace statistics."""
        try:
            stats = await self.dashboard_engine.get_plugin_marketplace_stats()

            print("\n📊 Plugin Marketplace Statistics")
            print("=" * 40)
            print(f"Total Plugins: {stats['total_plugins']}")
            print(f"Approved Plugins: {stats['approved_plugins']}")
            print(f"Installed Plugins: {stats['installed_plugins']}")
            print()

            if stats['type_distribution']:
                print("Plugin Types:")
                for plugin_type, count in stats['type_distribution'].items():
                    print(f"  {plugin_type}: {count}")

            if stats['top_plugins']:
                print("\n🏆 Top Plugins by Downloads:")
                for i, plugin in enumerate(stats['top_plugins'][:5], 1):
                    print(f"  {i}. {plugin['name']} - {plugin['downloads']} downloads")

        except Exception as e:
            print(f"❌ Error getting marketplace stats: {e}")

def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Plugin Manager for AI OS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python plugin_manager.py list
  python plugin_manager.py list --query "integration" --type integration
  python plugin_manager.py show my-plugin-id
  python plugin_manager.py install my-plugin-id
  python plugin_manager.py install my-plugin-id --version 1.2.0
  python plugin_manager.py uninstall my-plugin-id
  python plugin_manager.py stats
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List plugins
    list_parser = subparsers.add_parser('list', help='List available plugins')
    list_parser.add_argument('--query', help='Search query')
    list_parser.add_argument('--type', choices=['integration', 'widget', 'automation', 'analytics', 'notification', 'security', 'utility'],
                           help='Filter by plugin type')
    list_parser.set_defaults(func='list_plugins')

    # Show plugin details
    show_parser = subparsers.add_parser('show', help='Show plugin details')
    show_parser.add_argument('plugin_id', help='Plugin ID to show')
    show_parser.set_defaults(func='show_plugin')

    # Install plugin
    install_parser = subparsers.add_parser('install', help='Install a plugin')
    install_parser.add_argument('plugin_id', help='Plugin ID to install')
    install_parser.add_argument('--version', help='Specific version to install')
    install_parser.set_defaults(func='install_plugin')

    # Uninstall plugin
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a plugin')
    uninstall_parser.add_argument('plugin_id', help='Plugin ID to uninstall')
    uninstall_parser.set_defaults(func='uninstall_plugin')

    # Marketplace stats
    stats_parser = subparsers.add_parser('stats', help='Show marketplace statistics')
    stats_parser.set_defaults(func='marketplace_stats')

    return parser

async def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        return

    manager = PluginManager()
    await manager.initialize()

    # Call the appropriate method
    func_name = args.func
    if hasattr(manager, func_name):
        await getattr(manager, func_name)(args)
    else:
        print(f"❌ Unknown command: {func_name}")

if __name__ == "__main__":
    asyncio.run(main())
