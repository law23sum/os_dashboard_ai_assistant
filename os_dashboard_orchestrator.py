"""

Main Application Orchestrator

Central coordination hub for the OS Dashboard AI Assistant

"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import signal
import sys
import uuid

from assistant_core.cir.schema import CIRDocument, SourceSystem
from api_connectors import (
    BaseConnector,
    ConnectorConfig,
    MicrosoftGraphConnector,
    PDFConnector,
    GitConnector,
    OpenAIConnector,
    AppleNotesConnector
)
from api_connectors.universal_connector import SystemDaemonConnector
from assistant_core.search_engine import UnifiedSearchEngine, SearchQuery
# from assistant_core.daemon.workflow_orchestration import WorkflowEngine
# from assistant_core.audit_system import AuditStorage, AuditEventType, AuditLevel, AuditEvent


class OSDashboardConfig:
    """Configuration management for OS Dashboard"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed to load config: {e}")

        # Return default configuration
        return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "connectors": {
                "microsoft_graph": {
                    "enabled": False,
                    "settings": {
                        "client_id": "",
                        "client_secret": "",
                        "tenant_id": ""
                    }
                },
                "pdf": {
                    "enabled": True,
                    "settings": {
                        "base_path": "./documents"
                    }
                },
                "git": {
                    "enabled": True,
                    "settings": {
                        "repo_path": "."
                    }
                },
                "openai": {
                    "enabled": False,
                    "settings": {
                        "api_key": "",
                        "default_model": "gpt-4"
                    }
                },
                "apple": {
                    "enabled": False,
                    "settings": {
                        "enable_notes": True,
                        "enable_calendar": True,
                        "enable_icloud": True
                    }
                },
                "daemon": {
                    "enabled": True,
                    "settings": {
                        "enable_system_daemons": True,
                        "enable_user_daemons": True,
                        "enable_process_monitoring": True
                    }
                }
            },
            "search": {
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "cache_size": 10000,
                "enable_semantic_search": True
            },
            "workflows": {
                "config_path": "workflows",
                "enable_scheduler": True,
                "enable_event_processing": True
            },
            "audit": {
                "storage_path": "audit_data",
                "git_repo_path": "audit_repository",
                "enable_git_integration": True,
                "enable_compliance_monitoring": True
            },
            "logging": {
                "level": "INFO",
                "file": "os_dashboard.log",
                "max_size_mb": 100,
                "backup_count": 5
            }
        }

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def get_connector_config(self, connector_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific connector"""
        return self.config.get("connectors", {}).get(connector_name)

    def is_connector_enabled(self, connector_name: str) -> bool:
        """Check if connector is enabled"""
        connector_config = self.get_connector_config(connector_name)
        return connector_config.get("enabled", False) if connector_config else False


class OSDashboard:
    """Main OS Dashboard AI Assistant application"""

    def __init__(self, config_path: str = "config.json"):
        self.config = OSDashboardConfig(config_path)
        self.connectors: Dict[str, BaseConnector] = {}
        self.search_engine = UnifiedSearchEngine()
        # self.workflow_engine = WorkflowEngine(self.config.config.get("workflows", {}).get("config_path", "workflows"))
        # self.audit_system = AuditStorage(
        #     Path(self.config.config.get("audit", {}).get("storage_path", "audit_data")),
        #     Path(self.config.config.get("audit", {}).get("git_repo_path", "audit_repository"))
        # )
        self.workflow_engine = None  # Placeholder
        self.audit_system = None  # Placeholder

        self.is_running = False
        self.logger = self._setup_logging()

        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        log_config = self.config.config.get("logging", {})

        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_config.get("level", "INFO")),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get("file", "os_dashboard.log")),
                logging.StreamHandler(sys.stdout)
            ]
        )

        return logging.getLogger(__name__)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        asyncio.create_task(self.shutdown())

    async def initialize(self):
        """Initialize all components"""
        self.logger.info("Initializing OS Dashboard AI Assistant...")

        try:
            # Initialize audit system first
            # await self._initialize_audit_system()

            # Initialize connectors
            await self._initialize_connectors()

            # Initialize search engine
            await self._initialize_search_engine()

            # Initialize workflow engine
            # await self._initialize_workflow_engine()

            # Log initialization
            # await self.audit_system.log_event(
            #     AuditEvent(
            #         event_type=AuditEventType.SYSTEM_CONFIG,
            #         description="system_initialization",
            #         details={
            #             "connectors_initialized": len(self.connectors),
            #             "search_enabled": True,
            #             "workflows_enabled": True,
            #             "audit_enabled": True
            #         }
            #     )
            # )

            self.logger.info("OS Dashboard AI Assistant initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize OS Dashboard: {e}")
            raise

    # async def _initialize_audit_system(self):
    #     """Initialize audit and governance system"""
    #     self.logger.info("Initializing audit system...")
    #
    #     # Initialize git connector for audit if enabled
    #     git_connector = None
    #     if self.config.config.get("audit", {}).get("enable_git_integration", True):
    #         git_config = self.config.get_connector_config("git")
    #         if git_config and git_config.get("enabled", False):
    #             git_connector = GitConnector(ConnectorConfig(
    #                 connector_id="audit_git",
    #                 connector_type="git",
    #                 settings=git_config.get("settings", {})
    #             ))
    #
    #     await self.audit_system.initialize(
    #         enable_git=git_connector is not None,
    #         git_connector=git_connector
    #     )

    async def _initialize_connectors(self):
        """Initialize all enabled connectors"""
        self.logger.info("Initializing connectors...")

        connector_classes = {
            "microsoft_graph": MicrosoftGraphConnector,
            "pdf": PDFConnector,
            "git": GitConnector,
            "openai": OpenAIConnector,
            "apple": AppleNotesConnector,
            "daemon": SystemDaemonConnector
        }

        for connector_name, connector_class in connector_classes.items():
            if self.config.is_connector_enabled(connector_name):
                try:
                    connector_config = self.config.get_connector_config(connector_name)

                    config = ConnectorConfig(
                        instance_id=connector_name,
                        connector_type=connector_name,
                        settings=connector_config.get("settings", {})
                    )

                    connector = connector_class(config)

                    # Connect to the service
                    result = await connector.connect()
                    if result.success:
                        self.connectors[connector_name] = connector

                        # Register with other systems
                        self.search_engine.register_connector(connector_name, connector)
                        # self.workflow_engine.register_connector(connector_name, connector)
                        # self.audit_system.register_connector(connector_name, connector)

                        self.logger.info(f"Connector '{connector_name}' initialized successfully")
                    else:
                        self.logger.warning(f"Failed to connect '{connector_name}': {result.error}")

                except Exception as e:
                    self.logger.error(f"Failed to initialize connector '{connector_name}': {e}")

    async def _initialize_search_engine(self):
        """Initialize unified search engine"""
        self.logger.info("Initializing search engine...")

        await self.search_engine.initialize()

        # Index existing resources if configured
        search_config = self.config.config.get("search", {})
        if search_config.get("auto_index_on_startup", False):
            self.logger.info("Starting initial indexing...")
            total_indexed = await self.search_engine.reindex_all()
            self.logger.info(f"Indexed {total_indexed} resources")

    # async def _initialize_workflow_engine(self):
    #     """Initialize workflow orchestration engine"""
    #     self.logger.info("Initializing workflow engine...")
    #
    #     await self.workflow_engine.start()

    async def start(self):
        """Start the OS Dashboard application"""
        if self.is_running:
            return

        await self.initialize()
        self.is_running = True

        self.logger.info("OS Dashboard AI Assistant is now running")

        # Start background tasks
        await self._start_background_tasks()

        # Keep the application running
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await self.shutdown()

    async def _start_background_tasks(self):
        """Start background maintenance tasks"""
        # Daily audit commit task
        # if self.config.config.get("audit", {}).get("enable_git_integration", True):
        #     asyncio.create_task(self._daily_audit_commit_task())

        # Search index cleanup task
        asyncio.create_task(self._search_cleanup_task())

        # Health check task
        asyncio.create_task(self._health_check_task())

    # async def _daily_audit_commit_task(self):
    #     """Daily task to commit audit data to git"""
    #     while self.is_running:
    #         try:
    #             # Wait until midnight
    #             now = datetime.now()
    #             next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    #             if next_midnight <= now:
    #                 next_midnight = next_midnight.replace(day=next_midnight.day + 1)
    #
    #             wait_seconds = (next_midnight - now).total_seconds()
    #             await asyncio.sleep(wait_seconds)
    #
    #             # Commit previous day's audit data
    #             if self.is_running:
    #                 await self.audit_system.daily_audit_commit()
    #
    #         except Exception as e:
    #             self.logger.error(f"Daily audit commit task failed: {e}")
    #             await asyncio.sleep(3600)  # Wait 1 hour before retry

    async def _search_cleanup_task(self):
        """Periodic search index cleanup"""
        while self.is_running:
            try:
                # Run cleanup every 6 hours
                await asyncio.sleep(6 * 3600)

                if self.is_running:
                    cleaned = await self.search_engine.cleanup_index()
                    if cleaned > 0:
                        self.logger.info(f"Cleaned up {cleaned} stale search index entries")

            except Exception as e:
                self.logger.error(f"Search cleanup task failed: {e}")

    async def _health_check_task(self):
        """Periodic health check of all components"""
        while self.is_running:
            try:
                # Run health check every 5 minutes
                await asyncio.sleep(5 * 60)

                if self.is_running:
                    await self._perform_health_check()

            except Exception as e:
                self.logger.error(f"Health check task failed: {e}")

    async def _perform_health_check(self):
        """Perform comprehensive health check"""
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "components": {}
        }

        # Check connectors
        for name, connector in self.connectors.items():
            try:
                result = await connector.health_check()
                health_status["components"][f"connector_{name}"] = {
                    "status": "healthy" if result.success else "unhealthy",
                    "details": result.data if result.success else result.error
                }

                if not result.success:
                    health_status["overall_status"] = "degraded"

            except Exception as e:
                health_status["components"][f"connector_{name}"] = {
                    "status": "error",
                    "error": str(e)
                }
                health_status["overall_status"] = "degraded"

        # Check search engine
        try:
            search_stats = await self.search_engine.get_search_statistics()
            health_status["components"]["search_engine"] = {
                "status": "healthy",
                "statistics": search_stats
            }
        except Exception as e:
            health_status["components"]["search_engine"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"

        # Check workflow engine
        # try:
        #     workflow_stats = await self.workflow_engine.get_workflow_statistics()
        #     health_status["components"]["workflow_engine"] = {
        #         "status": "healthy",
        #         "statistics": workflow_stats
        #     }
        # except Exception as e:
        #     health_status["components"]["workflow_engine"] = {
        #         "status": "error",
        #         "error": str(e)
        #     }
        #     health_status["overall_status"] = "degraded"
        health_status["components"]["workflow_engine"] = {
            "status": "disabled",
            "note": "Workflow engine not implemented"
        }

        # Check audit system
        # try:
        #     audit_stats = await self.audit_system.get_system_statistics()
        #     health_status["components"]["audit_system"] = {
        #         "status": "healthy",
        #         "statistics": audit_stats
        #     }
        # except Exception as e:
        #     health_status["components"]["audit_system"] = {
        #         "status": "error",
        #         "error": str(e)
        #     }
        #     health_status["overall_status"] = "degraded"
        health_status["components"]["audit_system"] = {
            "status": "disabled",
            "note": "Audit system not implemented"
        }

        # Log health status if there are issues
        if health_status["overall_status"] != "healthy":
            self.logger.warning(f"System health check: {health_status['overall_status']}")

            # Log to audit system
            # await self.audit_system.log_event(
            #     AuditEvent(
            #         event_type=AuditEventType.SYSTEM_EVENT,
            #         description="health_check_warning",
            #         level=AuditLevel.WARNING,
            #         details=health_status
            #     )
            # )

    async def shutdown(self):
        """Gracefully shutdown the application"""
        if not self.is_running:
            return

        self.logger.info("Shutting down OS Dashboard AI Assistant...")
        self.is_running = False

        try:
            # Log shutdown event
            # await self.audit_system.log_event(
            #     AuditEvent(
            #         event_type=AuditEventType.SYSTEM_EVENT,
            #         description="system_shutdown",
            #         details={"shutdown_time": datetime.utcnow().isoformat()}
            #     )
            # )

            # Stop workflow engine
            # await self.workflow_engine.stop()

            # Disconnect connectors
            for name, connector in self.connectors.items():
                try:
                    await connector.disconnect()
                    self.logger.info(f"Disconnected connector: {name}")
                except Exception as e:
                    self.logger.error(f"Error disconnecting connector {name}: {e}")

            # Save search engine cache
            self.search_engine.embedding_engine._save_cache()

            self.logger.info("OS Dashboard AI Assistant shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    # Public API methods

    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Perform unified search across all connectors"""
        search_query = SearchQuery(text=query, **kwargs)

        # Log search event
        # await self.audit_system.log_event(
        #     AuditEvent(
        #         event_type=AuditEventType.SEARCH_QUERY,
        #         description="unified_search",
        #         details={
        #             "query": query,
        #             "filters": search_query.filters,
        #             "connectors": search_query.connectors,
        #             "search_types": search_query.search_types
        #         }
        #     )
        # )

        results = await self.search_engine.search(search_query)

        # Convert to serializable format
        return [
            {
                "resource_id": result.resource_ref.id,
                "name": result.resource_ref.name,
                "connector": result.connector_name,
                "relevance_score": result.relevance_score,
                "search_type": result.search_type,
                "snippet": result.snippet,
                "highlights": result.highlights,
                "metadata": result.resource_ref.metadata
            }
            for result in results
        ]

    async def get_resource(self, connector_name: str, resource_id: str) -> Optional[CIRDocument]:
        """Get resource from specific connector"""
        if connector_name not in self.connectors:
            raise ValueError(f"Connector {connector_name} not available")

        connector = self.connectors[connector_name]

        # Log access event
        # await self.audit_system.log_event(
        #     AuditEvent(
        #         event_type=AuditEventType.RESOURCE_READ,
        #         description="get_resource",
        #         connector_name=connector_name,
        #         resource_id=resource_id
        #     )
        # )

        result = await connector.read_resource(resource_id)
        return result.data if result.success else None

    async def create_workflow(self, workflow_definition: Dict[str, Any]) -> str:
        """Create new workflow"""
        # Convert dict to WorkflowDefinition
        # This would need proper validation and conversion
        workflow_id = str(uuid.uuid4())

        # Log workflow creation
        # await self.audit_system.log_event(
        #     AuditEvent(
        #         event_type=AuditEventType.WORKFLOW_EXECUTE,
        #         description="create_workflow",
        #         details={"workflow_id": workflow_id, "workflow_name": workflow_definition.get("name")}
        #     )
        # )

        # Save workflow (simplified)
        # In practice, this would use proper WorkflowDefinition objects
        return workflow_id

    async def trigger_workflow(self, workflow_id: str, event: Dict[str, Any] = None) -> str:
        """Trigger workflow execution"""
        # Log workflow trigger
        # await self.audit_system.log_event(
        #     AuditEvent(
        #         event_type=AuditEventType.WORKFLOW_EXECUTE,
        #         description="trigger_workflow",
        #         details={"workflow_id": workflow_id, "trigger_event": event}
        #     )
        # )

        # return await self.workflow_engine.trigger_workflow(workflow_id, event)
        return f"Workflow {workflow_id} triggered (placeholder)"

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "is_running": self.is_running,
            "connectors": {},
            "search_engine": {},
            "workflow_engine": {},
            "audit_system": {}
        }

        # Connector status
        for name, connector in self.connectors.items():
            try:
                health_result = await connector.health_check()
                status["connectors"][name] = {
                    "connected": connector.is_connected,
                    "healthy": health_result.success,
                    "last_check": health_result.data.get("last_check") if health_result.success else None
                }
            except Exception as e:
                status["connectors"][name] = {
                    "connected": False,
                    "healthy": False,
                    "error": str(e)
                }

        # Search engine status
        try:
            status["search_engine"] = await self.search_engine.get_search_statistics()
        except Exception as e:
            status["search_engine"] = {"error": str(e)}

        # Workflow engine status
        # try:
        #     status["workflow_engine"] = await self.workflow_engine.get_workflow_statistics()
        # except Exception as e:
        #     status["workflow_engine"] = {"error": str(e)}
        status["workflow_engine"] = {"status": "disabled", "note": "Workflow engine not implemented"}

        # Audit system status
        # try:
        #     status["audit_system"] = await self.audit_system.get_system_statistics()
        # except Exception as e:
        #     status["audit_system"] = {"error": str(e)}
        status["audit_system"] = {"status": "disabled", "note": "Audit system not implemented"}

        return status


async def main():
    """Main entry point"""
    dashboard = OSDashboard()

    try:
        await dashboard.start()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error: {e}")
    finally:
        await dashboard.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
