"""

Marketplace and Plugin Architecture

Enables third-party developers to create and distribute plugins for the OS Dashboard AI Assistant

"""

import asyncio
import json
import zipfile
import tempfile
import importlib.util
import inspect
from typing import Dict, Any, List, Optional, Type, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import hashlib
import yaml
import semver
from abc import ABC, abstractmethod

from config.logging_config import setup_logger

class PluginType(Enum):
    INTEGRATION = "integration"
    WIDGET = "widget"
    AUTOMATION = "automation"
    ANALYTICS = "analytics"
    NOTIFICATION = "notification"
    SECURITY = "security"
    UTILITY = "utility"

class PluginStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"
    SUSPENDED = "suspended"

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PluginManifest:
    """Plugin manifest definition"""
    id: str
    name: str
    version: str
    description: str
    author: str
    author_email: str
    website: str
    license: str
    type: PluginType
    category: str
    tags: List[str]
    dependencies: List[str]
    permissions: List[str]
    api_version: str
    min_dashboard_version: str
    max_dashboard_version: str = None
    entry_point: str = "main.py"
    config_schema: Dict[str, Any] = None
    screenshots: List[str] = None
    documentation: str = None
    # Monetization fields
    pricing_model: str = "free"  # free, paid, subscription, freemium
    price: float = 0.0
    currency: str = "USD"
    subscription_interval: str = None  # monthly, yearly
    trial_period_days: int = 0
    revenue_share_percentage: float = 70.0  # percentage for plugin developer

@dataclass
class PluginMetadata:
    """Plugin metadata for marketplace"""
    manifest: PluginManifest
    status: PluginStatus
    security_level: SecurityLevel
    download_count: int = 0
    rating: float = 0.0
    review_count: int = 0
    created_at: datetime = None
    updated_at: datetime = None
    file_hash: str = ""
    file_size: int = 0
    verified: bool = False
    # Monetization metadata
    total_revenue: float = 0.0
    active_subscriptions: int = 0
    trial_conversions: int = 0
    refund_count: int = 0

@dataclass
class PluginReview:
    """Plugin review/rating"""
    id: str
    plugin_id: str
    user_id: str
    rating: int  # 1-5
    comment: str
    created_at: datetime
    helpful_votes: int = 0

class BasePlugin(ABC):
    """Base class for all plugins"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = setup_logger(f"Plugin_{self.__class__.__name__}")
        self.enabled = True

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin"""
        pass

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Execute plugin functionality"""
        pass

    @abstractmethod
    async def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        pass

    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration"""
        return True

    async def get_health_status(self) -> Dict[str, Any]:
        """Get plugin health status"""
        return {
            "status": "healthy" if self.enabled else "disabled",
            "timestamp": datetime.now().isoformat()
        }

class IntegrationPlugin(BasePlugin):
    """Base class for integration plugins"""

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to external service"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from external service"""
        pass

    @abstractmethod
    async def sync_data(self, data_type: str) -> Dict[str, Any]:
        """Sync data with external service"""
        pass

class WidgetPlugin(BasePlugin):
    """Base class for widget plugins"""

    @abstractmethod
    async def render(self, context: Dict[str, Any]) -> str:
        """Render widget HTML"""
        pass

    @abstractmethod
    async def get_data(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get widget data"""
        pass

    @abstractmethod
    def get_widget_config(self) -> Dict[str, Any]:
        """Get widget configuration schema"""
        pass

class AutomationPlugin(BasePlugin):
    """Base class for automation plugins"""

    @abstractmethod
    async def create_workflow(self, workflow_def: Dict[str, Any]) -> str:
        """Create automation workflow"""
        pass

    @abstractmethod
    async def execute_workflow(self, workflow_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute automation workflow"""
        pass

    @abstractmethod
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        pass

class PluginMarketplace:
    """Plugin marketplace and management system"""

    def __init__(self, marketplace_dir: str = "marketplace"):
        self.logger = setup_logger("PluginMarketplace")
        self.marketplace_dir = Path(marketplace_dir)
        self.marketplace_dir.mkdir(exist_ok=True, parents=True)

        # Plugin storage
        self.plugins_dir = self.marketplace_dir / "plugins"
        self.plugins_dir.mkdir(exist_ok=True, parents=True)

        self.installed_dir = self.marketplace_dir / "installed"
        self.installed_dir.mkdir(exist_ok=True, parents=True)

        # Plugin registry
        self.available_plugins: Dict[str, PluginMetadata] = {}
        self.installed_plugins: Dict[str, BasePlugin] = {}
        self.plugin_reviews: Dict[str, List[PluginReview]] = {}

        # Security and validation
        self.security_scanner = PluginSecurityScanner()
        self.validator = PluginValidator()


    async def initialize(self):
        """Initialize marketplace"""
        await self._load_available_plugins()
        await self._load_installed_plugins()
        self.logger.info("Plugin Marketplace initialized")


    # Plugin Publishing
    async def submit_plugin(self, plugin_file: Path, author_info: Dict[str, Any]) -> Dict[str, Any]:
        """Submit plugin to marketplace"""
        try:
            # Extract and validate plugin
            plugin_data = await self._extract_plugin(plugin_file)
            manifest = plugin_data["manifest"]

            # Security scan
            security_result = await self.security_scanner.scan_plugin(plugin_data)

            # Create plugin metadata
            metadata = PluginMetadata(
                manifest=manifest,
                status=PluginStatus.PENDING,
                security_level=security_result["level"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                file_hash=self._calculate_file_hash(plugin_file),
                file_size=plugin_file.stat().st_size
            )

            # Store plugin
            plugin_storage_path = self.plugins_dir / f"{manifest.id}_{manifest.version}.zip"
            plugin_file.rename(plugin_storage_path)

            # Add to registry
            self.available_plugins[manifest.id] = metadata

            # Save metadata
            await self._save_plugin_metadata(metadata)

            self.logger.info(f"Plugin submitted: {manifest.name} v{manifest.version}")

            return {
                "status": "submitted",
                "plugin_id": manifest.id,
                "security_level": security_result["level"].value,
                "review_required": security_result["level"] in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]
            }

        except Exception as e:
            self.logger.error(f"Plugin submission failed: {e}")
            return {"status": "error", "message": str(e)}

    async def _extract_plugin(self, plugin_file: Path) -> Dict[str, Any]:
        """Extract and validate plugin package"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Extract ZIP file
                with zipfile.ZipFile(plugin_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)

                # Find and load manifest
                manifest_file = temp_path / "manifest.yaml"
                if not manifest_file.exists():
                    manifest_file = temp_path / "plugin.yaml"

                if not manifest_file.exists():
                    raise Exception("No manifest file found")

                with open(manifest_file, 'r') as f:
                    manifest_data = yaml.safe_load(f)

                # Validate manifest
                manifest = PluginManifest(**manifest_data)

                # Validate plugin structure
                await self.validator.validate_plugin_structure(temp_path, manifest)

                return {
                    "manifest": manifest,
                    "extracted_path": temp_path,
                    "files": list(temp_path.rglob("*"))
                }

        except Exception as e:
            self.logger.error(f"Plugin extraction failed: {e}")
            raise

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    # Plugin Installation
    async def install_plugin(self, plugin_id: str, version: str = None) -> Dict[str, Any]:
        """Install plugin from marketplace"""
        try:
            # Find plugin
            metadata = self.available_plugins.get(plugin_id)
            if not metadata:
                raise Exception(f"Plugin {plugin_id} not found")

            if metadata.status != PluginStatus.APPROVED:
                raise Exception(f"Plugin {plugin_id} is not approved for installation")

            # Check version compatibility
            if version and metadata.manifest.version != version:
                raise Exception(f"Version {version} not available")

            # Check dependencies
            dependency_check = await self._check_dependencies(metadata.manifest.dependencies)
            if not dependency_check["satisfied"]:
                return {
                    "status": "dependency_error",
                    "missing_dependencies": dependency_check["missing"]
                }

            # Plugin is free to install (billing removed)

            # Install plugin
            plugin_file = self.plugins_dir / f"{plugin_id}_{metadata.manifest.version}.zip"
            install_path = self.installed_dir / plugin_id

            # Extract to installation directory
            with zipfile.ZipFile(plugin_file, 'r') as zip_ref:
                zip_ref.extractall(install_path)

            # Load and initialize plugin
            plugin_instance = await self._load_plugin_instance(install_path, metadata.manifest)

            if plugin_instance:
                # Initialize plugin
                if await plugin_instance.initialize():
                    self.installed_plugins[plugin_id] = plugin_instance

                    # Update download/installation count
                    metadata.download_count += 1
                    if metadata.manifest.pricing_model != "free":
                        metadata.active_subscriptions += 1
                    await self._save_plugin_metadata(metadata)

                    self.logger.info(f"Plugin installed: {metadata.manifest.name}")

                    return {
                        "status": "installed",
                        "plugin_id": plugin_id,
                        "version": metadata.manifest.version,
                        "pricing_model": metadata.manifest.pricing_model,
                        "requires_payment": False  # Billing removed - all plugins free
                    }
                else:
                    raise Exception("Plugin initialization failed")
            else:
                raise Exception("Failed to load plugin")

        except Exception as e:
            self.logger.error(f"Plugin installation failed: {e}")
            return {"status": "error", "message": str(e)}


    async def _load_plugin_instance(self, install_path: Path, manifest: PluginManifest) -> Optional[BasePlugin]:
        """Load plugin instance from installation path"""
        try:
            # Find entry point
            entry_file = install_path / manifest.entry_point
            if not entry_file.exists():
                raise Exception(f"Entry point {manifest.entry_point} not found")

            # Load module
            spec = importlib.util.spec_from_file_location(manifest.id, entry_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    issubclass(obj, BasePlugin) and
                    obj != BasePlugin):
                    plugin_class = obj
                    break

            if not plugin_class:
                raise Exception("No plugin class found")

            # Create instance
            plugin_instance = plugin_class(manifest.config_schema)

            return plugin_instance

        except Exception as e:
            self.logger.error(f"Failed to load plugin instance: {e}")
            return None

    async def _check_dependencies(self, dependencies: List[str]) -> Dict[str, Any]:
        """Check if plugin dependencies are satisfied"""
        missing = []

        for dependency in dependencies:
            # Check if dependency is installed
            if dependency not in self.installed_plugins:
                # Check if dependency is available in marketplace
                if dependency not in self.available_plugins:
                    missing.append(dependency)

        return {
            "satisfied": len(missing) == 0,
            "missing": missing
        }

    # Plugin Management
    async def uninstall_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """Uninstall plugin"""
        try:
            if plugin_id not in self.installed_plugins:
                raise Exception(f"Plugin {plugin_id} is not installed")

            plugin = self.installed_plugins[plugin_id]

            # Cleanup plugin
            await plugin.cleanup()

            # Remove from installed plugins
            del self.installed_plugins[plugin_id]

            # Remove installation directory
            install_path = self.installed_dir / plugin_id
            if install_path.exists():
                import shutil
                shutil.rmtree(install_path)

            self.logger.info(f"Plugin uninstalled: {plugin_id}")

            return {"status": "uninstalled", "plugin_id": plugin_id}

        except Exception as e:
            self.logger.error(f"Plugin uninstallation failed: {e}")
            return {"status": "error", "message": str(e)}

    async def enable_plugin(self, plugin_id: str) -> bool:
        """Enable plugin"""
        try:
            if plugin_id in self.installed_plugins:
                self.installed_plugins[plugin_id].enabled = True
                self.logger.info(f"Plugin enabled: {plugin_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to enable plugin {plugin_id}: {e}")
            return False

    async def disable_plugin(self, plugin_id: str) -> bool:
        """Disable plugin"""
        try:
            if plugin_id in self.installed_plugins:
                self.installed_plugins[plugin_id].enabled = False
                self.logger.info(f"Plugin disabled: {plugin_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to disable plugin {plugin_id}: {e}")
            return False

    # Plugin Discovery
    async def search_plugins(self, query: str = None,
                           plugin_type: PluginType = None,
                           category: str = None,
                           tags: List[str] = None) -> List[Dict[str, Any]]:
        """Search plugins in marketplace"""
        try:
            results = []

            for plugin_id, metadata in self.available_plugins.items():
                if metadata.status != PluginStatus.APPROVED:
                    continue

                manifest = metadata.manifest

                # Apply filters
                if plugin_type and manifest.type != plugin_type:
                    continue

                if category and manifest.category != category:
                    continue

                if tags and not any(tag in manifest.tags for tag in tags):
                    continue

                if query:
                    # Simple text search
                    search_text = f"{manifest.name} {manifest.description} {' '.join(manifest.tags)}".lower()
                    if query.lower() not in search_text:
                        continue

                # Add to results
                results.append({
                    "id": plugin_id,
                    "name": manifest.name,
                    "version": manifest.version,
                    "description": manifest.description,
                    "author": manifest.author,
                    "type": manifest.type.value,
                    "category": manifest.category,
                    "tags": manifest.tags,
                    "rating": metadata.rating,
                    "download_count": metadata.download_count,
                    "verified": metadata.verified
                })

            # Sort by rating and download count
            results.sort(key=lambda x: (x["rating"], x["download_count"]), reverse=True)

            return results

        except Exception as e:
            self.logger.error(f"Plugin search failed: {e}")
            return []


    async def get_plugin_revenue_report(self, plugin_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Get revenue report for plugin"""
        try:
            if plugin_id not in self.available_plugins:
                raise Exception(f"Plugin {plugin_id} not found")

            metadata = self.available_plugins[plugin_id]
            manifest = metadata.manifest

            # Calculate revenue metrics
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)

            report = {
                "plugin_id": plugin_id,
                "plugin_name": manifest.name,
                "pricing_model": manifest.pricing_model,
                "price": manifest.price,
                "currency": manifest.currency,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": period_days
                },
                "metrics": {
                    "downloads": metadata.download_count,
                    "active_subscriptions": metadata.active_subscriptions,
                    "total_revenue": metadata.total_revenue,
                    "trial_conversions": metadata.trial_conversions,
                    "refund_count": metadata.refund_count
                },
                "calculated_metrics": {
                    "conversion_rate": (metadata.trial_conversions / max(metadata.download_count, 1)) * 100,
                    "refund_rate": (metadata.refund_count / max(metadata.download_count, 1)) * 100,
                    "average_revenue_per_user": metadata.total_revenue / max(metadata.active_subscriptions, 1)
                }
            }

            return report

        except Exception as e:
            self.logger.error(f"Plugin revenue report generation failed: {e}")
            return {"error": str(e)}

    async def update_plugin_revenue(self, plugin_id: str, amount: float, transaction_type: str):
        """Update plugin revenue metrics"""
        try:
            if plugin_id in self.available_plugins:
                metadata = self.available_plugins[plugin_id]

                if transaction_type == "purchase" or transaction_type == "subscription":
                    metadata.total_revenue += amount
                    if transaction_type == "subscription":
                        metadata.active_subscriptions += 1
                elif transaction_type == "refund":
                    metadata.refund_count += 1
                    metadata.total_revenue -= amount
                elif transaction_type == "trial_conversion":
                    metadata.trial_conversions += 1

                await self._save_plugin_metadata(metadata)

        except Exception as e:
            self.logger.error(f"Plugin revenue update failed: {e}")

    async def get_plugin_details(self, plugin_id: str) -> Dict[str, Any]:
        """Get detailed plugin information"""
        try:
            metadata = self.available_plugins.get(plugin_id)
            if not metadata:
                raise Exception(f"Plugin {plugin_id} not found")

            manifest = metadata.manifest
            reviews = self.plugin_reviews.get(plugin_id, [])

            return {
                "id": plugin_id,
                "manifest": asdict(manifest),
                "metadata": {
                    "status": metadata.status.value,
                    "security_level": metadata.security_level.value,
                    "download_count": metadata.download_count,
                    "rating": metadata.rating,
                    "review_count": metadata.review_count,
                    "verified": metadata.verified,
                    "created_at": metadata.created_at.isoformat() if metadata.created_at else None,
                    "updated_at": metadata.updated_at.isoformat() if metadata.updated_at else None
                },
                "monetization": {
                    "pricing_model": manifest.pricing_model,
                    "price": manifest.price,
                    "currency": manifest.currency,
                    "subscription_interval": manifest.subscription_interval,
                    "trial_period_days": manifest.trial_period_days,
                    "revenue_share_percentage": manifest.revenue_share_percentage,
                    "total_revenue": metadata.total_revenue,
                    "active_subscriptions": metadata.active_subscriptions,
                    "trial_conversions": metadata.trial_conversions
                },
                "reviews": [asdict(review) for review in reviews[-10:]],  # Last 10 reviews
                "installed": plugin_id in self.installed_plugins
            }

        except Exception as e:
            self.logger.error(f"Failed to get plugin details: {e}")
            return {"error": str(e)}

    # Plugin Reviews
    async def add_review(self, review: PluginReview) -> bool:
        """Add plugin review"""
        try:
            if review.plugin_id not in self.available_plugins:
                raise Exception(f"Plugin {review.plugin_id} not found")

            if review.plugin_id not in self.plugin_reviews:
                self.plugin_reviews[review.plugin_id] = []

            self.plugin_reviews[review.plugin_id].append(review)

            # Update plugin rating
            await self._update_plugin_rating(review.plugin_id)

            self.logger.info(f"Review added for plugin {review.plugin_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add review: {e}")
            return False

    async def _update_plugin_rating(self, plugin_id: str):
        """Update plugin average rating"""
        try:
            reviews = self.plugin_reviews.get(plugin_id, [])
            if reviews:
                total_rating = sum(review.rating for review in reviews)
                average_rating = total_rating / len(reviews)

                metadata = self.available_plugins[plugin_id]
                metadata.rating = round(average_rating, 1)
                metadata.review_count = len(reviews)

                await self._save_plugin_metadata(metadata)

        except Exception as e:
            self.logger.error(f"Failed to update plugin rating: {e}")

    # Plugin Execution
    async def execute_plugin(self, plugin_id: str, method: str, *args, **kwargs) -> Any:
        """Execute plugin method"""
        try:
            if plugin_id not in self.installed_plugins:
                raise Exception(f"Plugin {plugin_id} is not installed")

            plugin = self.installed_plugins[plugin_id]

            if not plugin.enabled:
                raise Exception(f"Plugin {plugin_id} is disabled")

            # Check if method exists
            if not hasattr(plugin, method):
                raise Exception(f"Plugin {plugin_id} does not have method {method}")

            # Execute method
            method_func = getattr(plugin, method)
            result = await method_func(*args, **kwargs)

            return result

        except Exception as e:
            self.logger.error(f"Plugin execution failed: {e}")
            raise

    # Data Management
    async def _save_plugin_metadata(self, metadata: PluginMetadata):
        """Save plugin metadata to storage"""
        try:
            metadata_file = self.marketplace_dir / f"{metadata.manifest.id}_metadata.yaml"

            # Convert to dict for serialization
            metadata_dict = asdict(metadata)
            metadata_dict["manifest"] = asdict(metadata.manifest)
            metadata_dict["status"] = metadata.status.value
            metadata_dict["security_level"] = metadata.security_level.value
            metadata_dict["manifest"]["type"] = metadata.manifest.type.value

            # Handle datetime serialization
            if metadata_dict["created_at"]:
                metadata_dict["created_at"] = metadata.created_at.isoformat()
            if metadata_dict["updated_at"]:
                metadata_dict["updated_at"] = metadata.updated_at.isoformat()

            with open(metadata_file, 'w') as f:
                yaml.dump(metadata_dict, f, default_flow_style=False)

        except Exception as e:
            self.logger.error(f"Failed to save plugin metadata: {e}")

    async def _load_available_plugins(self):
        """Load available plugins from storage"""
        try:
            for metadata_file in self.marketplace_dir.glob("*_metadata.yaml"):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata_dict = yaml.safe_load(f)

                    # Convert back from dict
                    manifest_dict = metadata_dict["manifest"]
                    manifest_dict["type"] = PluginType(manifest_dict["type"])
                    manifest = PluginManifest(**manifest_dict)

                    metadata_dict["manifest"] = manifest
                    metadata_dict["status"] = PluginStatus(metadata_dict["status"])
                    metadata_dict["security_level"] = SecurityLevel(metadata_dict["security_level"])

                    # Handle datetime deserialization
                    if metadata_dict["created_at"]:
                        metadata_dict["created_at"] = datetime.fromisoformat(metadata_dict["created_at"])
                    if metadata_dict["updated_at"]:
                        metadata_dict["updated_at"] = datetime.fromisoformat(metadata_dict["updated_at"])

                    metadata = PluginMetadata(**metadata_dict)
                    self.available_plugins[manifest.id] = metadata

                except Exception as e:
                    self.logger.error(f"Failed to load plugin metadata from {metadata_file}: {e}")

        except Exception as e:
            self.logger.error(f"Failed to load available plugins: {e}")

    async def _load_installed_plugins(self):
        """Load installed plugins"""
        try:
            for plugin_dir in self.installed_dir.iterdir():
                if plugin_dir.is_dir():
                    plugin_id = plugin_dir.name

                    # Find manifest
                    manifest_file = plugin_dir / "manifest.yaml"
                    if not manifest_file.exists():
                        manifest_file = plugin_dir / "plugin.yaml"

                    if manifest_file.exists():
                        try:
                            with open(manifest_file, 'r') as f:
                                manifest_data = yaml.safe_load(f)

                            manifest = PluginManifest(**manifest_data)

                            # Load plugin instance
                            plugin_instance = await self._load_plugin_instance(plugin_dir, manifest)

                            if plugin_instance:
                                await plugin_instance.initialize()
                                self.installed_plugins[plugin_id] = plugin_instance

                        except Exception as e:
                            self.logger.error(f"Failed to load installed plugin {plugin_id}: {e}")

        except Exception as e:
            self.logger.error(f"Failed to load installed plugins: {e}")

    async def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        try:
            total_plugins = len(self.available_plugins)
            approved_plugins = sum(1 for m in self.available_plugins.values()
                                 if m.status == PluginStatus.APPROVED)
            installed_plugins = len(self.installed_plugins)

            # Plugin types distribution
            type_distribution = {}
            for metadata in self.available_plugins.values():
                plugin_type = metadata.manifest.type.value
                type_distribution[plugin_type] = type_distribution.get(plugin_type, 0) + 1

            # Top plugins by downloads
            top_plugins = sorted(
                self.available_plugins.values(),
                key=lambda x: x.download_count,
                reverse=True
            )[:10]

            # Revenue statistics
            total_revenue = sum(p.total_revenue for p in self.available_plugins.values())
            paid_plugins = sum(1 for p in self.available_plugins.values()
                             if p.manifest.pricing_model != "free")
            active_subscriptions = sum(p.active_subscriptions for p in self.available_plugins.values())

            # Top revenue plugins
            top_revenue_plugins = sorted(
                self.available_plugins.values(),
                key=lambda x: x.total_revenue,
                reverse=True
            )[:10]

            return {
                "total_plugins": total_plugins,
                "approved_plugins": approved_plugins,
                "installed_plugins": installed_plugins,
                "type_distribution": type_distribution,
                "monetization_stats": {
                    "total_revenue": total_revenue,
                    "paid_plugins": paid_plugins,
                    "active_subscriptions": active_subscriptions,
                    "free_plugins": approved_plugins - paid_plugins
                },
                "top_plugins": [
                    {
                        "id": p.manifest.id,
                        "name": p.manifest.name,
                        "downloads": p.download_count,
                        "rating": p.rating
                    }
                    for p in top_plugins
                ],
                "top_revenue_plugins": [
                    {
                        "id": p.manifest.id,
                        "name": p.manifest.name,
                        "revenue": p.total_revenue,
                        "subscriptions": p.active_subscriptions
                    }
                    for p in top_revenue_plugins
                ]
            }

        except Exception as e:
            self.logger.error(f"Failed to get marketplace stats: {e}")
            return {}

    async def shutdown(self):
        """Shutdown marketplace"""
        # Cleanup all installed plugins
        for plugin in self.installed_plugins.values():
            try:
                await plugin.cleanup()
            except Exception as e:
                self.logger.error(f"Plugin cleanup failed: {e}")

        self.logger.info("Plugin Marketplace shutdown complete")

class PluginSecurityScanner:
    """Security scanner for plugins"""

    def __init__(self):
        self.logger = setup_logger("PluginSecurity")

        # Security patterns to detect
        self.dangerous_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'subprocess\.',
            r'os\.system',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\('
        ]

        self.suspicious_imports = [
            'subprocess',
            'os',
            'sys',
            'socket',
            'urllib',
            'requests',
            'http'
        ]

    async def scan_plugin(self, plugin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Scan plugin for security issues"""
        try:
            security_issues = []
            risk_score = 0

            # Scan files for dangerous patterns
            for file_path in plugin_data["files"]:
                if file_path.suffix == '.py':
                    issues = await self._scan_python_file(file_path)
                    security_issues.extend(issues)
                    risk_score += len(issues)

            # Determine security level
            if risk_score == 0:
                level = SecurityLevel.LOW
            elif risk_score <= 3:
                level = SecurityLevel.MEDIUM
            elif risk_score <= 7:
                level = SecurityLevel.HIGH
            else:
                level = SecurityLevel.CRITICAL

            return {
                "level": level,
                "risk_score": risk_score,
                "issues": security_issues
            }

        except Exception as e:
            self.logger.error(f"Security scan failed: {e}")
            return {
                "level": SecurityLevel.CRITICAL,
                "risk_score": 100,
                "issues": [f"Scan failed: {e}"]
            }

    async def _scan_python_file(self, file_path: Path) -> List[str]:
        """Scan Python file for security issues"""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for dangerous patterns
            import re
            for pattern in self.dangerous_patterns:
                if re.search(pattern, content):
                    issues.append(f"Dangerous pattern found in {file_path.name}: {pattern}")

            # Check for suspicious imports
            for imp in self.suspicious_imports:
                if f"import {imp}" in content or f"from {imp}" in content:
                    issues.append(f"Suspicious import in {file_path.name}: {imp}")

        except Exception as e:
            issues.append(f"Failed to scan {file_path.name}: {e}")

        return issues

class PluginValidator:
    """Plugin structure and manifest validator"""

    def __init__(self):
        self.logger = setup_logger("PluginValidator")

    async def validate_plugin_structure(self, plugin_path: Path, manifest: PluginManifest) -> bool:
        """Validate plugin structure"""
        try:
            # Check required files
            entry_point = plugin_path / manifest.entry_point
            if not entry_point.exists():
                raise Exception(f"Entry point {manifest.entry_point} not found")

            # Check manifest completeness
            required_fields = ['id', 'name', 'version', 'description', 'author', 'type']
            for field in required_fields:
                if not getattr(manifest, field):
                    raise Exception(f"Required field '{field}' is missing or empty")

            # Validate version format
            try:
                semver.VersionInfo.parse(manifest.version)
            except ValueError:
                raise Exception(f"Invalid version format: {manifest.version}")

            # Check file structure
            python_files = list(plugin_path.glob("*.py"))
            if not python_files:
                raise Exception("No Python files found in plugin")

            return True

        except Exception as e:
            self.logger.error(f"Plugin validation failed: {e}")
            raise

# Example plugin implementations
class ExampleIntegrationPlugin(IntegrationPlugin):
    """Example integration plugin"""

    async def initialize(self) -> bool:
        self.logger.info("Example integration plugin initialized")
        return True

    async def execute(self, *args, **kwargs) -> Any:
        return {"message": "Integration plugin executed"}

    async def cleanup(self) -> bool:
        self.logger.info("Example integration plugin cleaned up")
        return True

    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "Example Integration",
            "version": "1.0.0",
            "type": "integration"
        }

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> bool:
        return True

    async def sync_data(self, data_type: str) -> Dict[str, Any]:
        return {"synced": True, "data_type": data_type}
