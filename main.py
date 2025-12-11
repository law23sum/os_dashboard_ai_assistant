#!/usr/bin/env python3
"""Main entry point for OS Dashboard AI Assistant."""

import sys
import os

# Add current directory to path for proper imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

async def main_async():
    """Initialize the OS Dashboard AI Assistant asynchronously."""
    try:
        from assistant_core.ai import AIAssistant
        from assistant_core.core.state import ApplicationState
        from config.logging_config import configure_logging

        # Configure logging
        configure_logging()

        # Initialize application state
        app_state = ApplicationState()

        # Initialize AI assistant
        ai_assistant = AIAssistant(app_state)

        print("✅ OS Dashboard AI Assistant initialized successfully!")
        print(f"Active persona: {app_state.get_active_persona()}")

        # Try to initialize plugin marketplace and security framework (optional)
        try:
            from assistant_core.dashboard_engine import DashboardEngine
            dashboard_engine = DashboardEngine()
            await dashboard_engine.initialize_plugin_marketplace()
            await dashboard_engine.initialize_security_framework()
            print("Plugin Marketplace: Ready for plugin management")
            print("Security Framework: Enterprise-grade security and compliance monitoring active")
        except ImportError as e:
            print(f"Advanced systems not available: {e}")
            print("Core functionality will work without plugins and security framework")

        # Try to initialize partner management system (optional)
        try:
            from assistant_core.partner_management import initialize_partner_system
            partner_system = await initialize_partner_system()
            if partner_system:
                print("Partner Management System: Enterprise partner lifecycle management active")
                # Analytics system is initialized within partner management system
            else:
                print("Partner Management System: Dependencies not available")
        except ImportError as e:
            print(f"Partner Management System: Not available ({e})")

        # Try to initialize developer portal system (optional)
        try:
            from assistant_core.developer_portal import DeveloperPortalSystem
            developer_portal = DeveloperPortalSystem()
            await developer_portal.initialize()
            print("Developer Portal System: Documentation and API reference portal active")
        except ImportError as e:
            print(f"Developer Portal System: Not available ({e})")

        # Try to initialize AI services API (unified backend for all AI features)
        try:
            from assistant_core.ai_services_api import initialize_ai_services
            await initialize_ai_services()
            print("AI Services API: Unified backend for all 10 AI-powered features active")
        except ImportError as e:
            print(f"AI Services API: Not available ({e})")

        # Try to initialize predictive analytics system (optional)
        try:
            from assistant_core.predictive_analytics import AdvancedPredictiveAnalytics
            predictive_analytics = AdvancedPredictiveAnalytics()
            await predictive_analytics.initialize()
            print("Predictive Analytics System: AI-powered productivity insights and forecasting active")
        except ImportError as e:
            print(f"Predictive Analytics System: Not available ({e})")

        # Try to initialize computer vision AI system (optional)
        try:
            from assistant_core.computer_vision_ai import ComputerVisionMultimodalAI
            computer_vision_ai = ComputerVisionMultimodalAI()
            await computer_vision_ai.initialize()
            print("Computer Vision AI System: Advanced image processing and multimodal understanding active")
        except ImportError as e:
            print(f"Computer Vision AI System: Not available ({e})")

        # Try to initialize conversation manager (optional)
        try:
            from assistant_core.conversation_manager import ConversationManager
            conversation_manager = ConversationManager()
            await conversation_manager.initialize()
            print("Conversation Manager: Advanced NLP and conversation AI active")
        except ImportError as e:
            print(f"Conversation Manager: Not available ({e})")

        # Try to initialize automation orchestrator (optional)
        try:
            from assistant_core.automation_orchestrator import AutomationOrchestrator
            automation_orchestrator = AutomationOrchestrator()
            await automation_orchestrator.initialize()
            print("Automation Orchestrator: Intelligent workflow automation active")
        except ImportError as e:
            print(f"Automation Orchestrator: Not available ({e})")

        # Try to initialize AI security framework (optional)
        try:
            from assistant_core.security_framework import AISecurityFramework
            ai_security = AISecurityFramework()
            await ai_security.initialize()
            print("AI Security Framework: Advanced threat detection and response active")
        except ImportError as e:
            print(f"AI Security Framework: Not available ({e})")

        # Try to initialize edge computing AI (optional)
        try:
            from assistant_core.edge_computing_ai import EdgeComputingDistributedAI
            edge_computing = EdgeComputingDistributedAI()
            await edge_computing.initialize()
            print("Edge Computing AI: Distributed AI processing and federated learning active")
        except ImportError as e:
            print(f"Edge Computing AI: Not available ({e})")

        # Try to initialize personalization engine (optional)
        try:
            from assistant_core.personalization_engine import PersonalizationRecommendationEngine
            personalization = PersonalizationRecommendationEngine()
            await personalization.initialize()
            print("Personalization Engine: Advanced recommendation systems active")
        except ImportError as e:
            print(f"Personalization Engine: Not available ({e})")

        # Try to initialize collaboration intelligence (optional)
        try:
            from assistant_core.collaboration_intelligence import CollaborationIntelligence
            collaboration = CollaborationIntelligence()
            await collaboration.initialize()
            print("Collaboration Intelligence: Real-time team intelligence active")
        except ImportError as e:
            print(f"Collaboration Intelligence: Not available ({e})")

        # Try to initialize MLOps platform (optional)
        try:
            from assistant_core.mlops_platform import MLOpsPlatform
            mlops = MLOpsPlatform()
            await mlops.initialize()
            print("MLOps Platform: Advanced ML operations and deployment active")
        except ImportError as e:
            print(f"MLOps Platform: Not available ({e})")

        # Try to initialize intelligent monitoring (optional)
        try:
            from assistant_core.intelligent_monitoring import IntelligentMonitoringSystem
            monitoring = IntelligentMonitoringSystem()
            await monitoring.initialize()
            print("Intelligent Monitoring: AI-powered system monitoring and self-healing active")
        except ImportError as e:
            print(f"Intelligent Monitoring: Not available ({e})")

        # Try to initialize API integration gateway (optional)
        try:
            from api_connectors import IntegrationAPIGateway
            api_gateway = IntegrationAPIGateway(db_connection=None, scheduler=None)
            print("API Integration Gateway: Third-party service integrations ready")
        except ImportError as e:
            print(f"API Integration Gateway: Not available ({e})")

        print("\nFor the full GUI experience, run the assistant_hub_gui application.")
        print("AI assistant is ready for use by other components.")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Could not load the application. Please check your installation.")
        sys.exit(1)

def main():
    """Main entry point - runs async initialization."""
    import asyncio
    asyncio.run(main_async())

if __name__ == "__main__":
    main()