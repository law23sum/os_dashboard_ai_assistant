"""
AI Services API - Unified Backend for All AI-Powered Features

This module provides a comprehensive API for all 10 AI-powered features:
1. AI-Powered Predictive Analytics & Forecasting
2. Advanced Natural Language Processing & Conversation AI
3. Intelligent Automation & Workflow Orchestration
4. Computer Vision & Multimodal AI
5. Advanced Security with AI Threat Detection
6. Edge Computing & Distributed AI Processing
7. Advanced Personalization & Recommendation Engines
8. Real-Time Collaboration & Team Intelligence
9. Advanced Data Science & ML Operations (MLOps)
10. Intelligent Monitoring & Self-Healing Systems

Each feature supports user input via parameters and dropdown selections.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import traceback

from assistant_core.spec_registry import get_default_registry
from config.logging_config import setup_logger
from .predictive_analytics import AdvancedPredictiveAnalytics
from .computer_vision_ai import ComputerVisionMultimodalAI
from .conversation_manager import ConversationManager
from .automation_orchestrator import AutomationOrchestrator
from .security_framework import AISecurityFramework
from .edge_computing_ai import EdgeComputingDistributedAI
from .personalization_engine import PersonalizationRecommendationEngine
from .collaboration_intelligence import CollaborationIntelligence
from .mlops_platform import MLOpsPlatform
from .intelligent_monitoring import IntelligentMonitoringSystem


class AIServiceType(Enum):
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    NLP_CONVERSATION = "nlp_conversation"
    AUTOMATION_ORCHESTRATION = "automation_orchestration"
    COMPUTER_VISION = "computer_vision"
    SECURITY_AI = "security_ai"
    EDGE_COMPUTING = "edge_computing"
    PERSONALIZATION = "personalization"
    COLLABORATION = "collaboration"
    MLOPS = "mlops"
    MONITORING = "monitoring"


@dataclass
class AIServiceRequest:
    """Standard request structure for AI services"""

    service_type: AIServiceType
    user_id: str
    parameters: Dict[str, Any]
    input_data: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None

    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())


@dataclass
class AIServiceResponse:
    """Standard response structure for AI services"""

    request_id: str
    service_type: AIServiceType
    success: bool
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()


class AIServicesAPI:
    """Unified API for all AI-powered services"""

    def __init__(self):
        self.logger = setup_logger("AIServicesAPI")
        self.services = {}
        self._initialized = False

    async def initialize(self):
        """Initialize all AI services"""
        if self._initialized:
            return

        try:
            self.logger.info("Initializing AI Services API...")

            # Initialize all AI services
            await self._initialize_predictive_analytics()
            await self._initialize_nlp_conversation()
            await self._initialize_automation_orchestration()
            await self._initialize_computer_vision()
            await self._initialize_security_ai()
            await self._initialize_edge_computing()
            await self._initialize_personalization()
            await self._initialize_collaboration()
            await self._initialize_mlops()
            await self._initialize_monitoring()

            self._initialized = True
            self.logger.info("AI Services API initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize AI Services API: {e}")
            raise

    async def _initialize_predictive_analytics(self):
        """Initialize Predictive Analytics service"""
        try:
            from .predictive_analytics import AdvancedPredictiveAnalytics

            service = AdvancedPredictiveAnalytics()
            await service.initialize()
            self.services[AIServiceType.PREDICTIVE_ANALYTICS] = service
            self.logger.info("Predictive Analytics service initialized")
        except ImportError as e:
            self.logger.warning(f"Missing dependencies for Predictive Analytics: {e}")
            self.services[AIServiceType.PREDICTIVE_ANALYTICS] = None
        except Exception as e:
            self.logger.warning(f"Could not initialize Predictive Analytics: {e}")
            self.services[AIServiceType.PREDICTIVE_ANALYTICS] = None

    async def _initialize_nlp_conversation(self):
        """Initialize NLP Conversation service"""
        try:
            from .conversation_manager import ConversationManager

            service = ConversationManager()
            await service.initialize()
            self.services[AIServiceType.NLP_CONVERSATION] = service
            self.logger.info("NLP Conversation service initialized")
        except ImportError as e:
            self.logger.warning(f"Missing dependencies for NLP Conversation: {e}")
            self.services[AIServiceType.NLP_CONVERSATION] = None
        except Exception as e:
            self.logger.warning(f"Could not initialize NLP Conversation: {e}")
            self.services[AIServiceType.NLP_CONVERSATION] = None

    async def _initialize_automation_orchestration(self):
        """Initialize Automation Orchestration service"""
        try:
            from .automation_orchestrator import AutomationOrchestrator

            service = AutomationOrchestrator()
            await service.initialize()
            self.services[AIServiceType.AUTOMATION_ORCHESTRATION] = service
            self.logger.info("Automation Orchestration service initialized")
        except ImportError as e:
            self.logger.warning(
                f"Missing dependencies for Automation Orchestration: {e}"
            )
            self.services[AIServiceType.AUTOMATION_ORCHESTRATION] = None
        except Exception as e:
            self.logger.warning(f"Could not initialize Automation Orchestration: {e}")
            self.services[AIServiceType.AUTOMATION_ORCHESTRATION] = None

    async def _initialize_computer_vision(self):
        """Initialize Computer Vision service"""
        try:
            from .computer_vision_ai import ComputerVisionMultimodalAI

            service = ComputerVisionMultimodalAI()
            await service.initialize()
            self.services[AIServiceType.COMPUTER_VISION] = service
            self.logger.info("Computer Vision service initialized")
        except ImportError as e:
            self.logger.warning(f"Missing dependencies for Computer Vision: {e}")
            self.services[AIServiceType.COMPUTER_VISION] = None
        except Exception as e:
            self.logger.warning(f"Could not initialize Computer Vision: {e}")
            self.services[AIServiceType.COMPUTER_VISION] = None

    async def _initialize_security_ai(self):
        """Initialize Security AI service"""
        try:
            from .security_framework import AISecurityFramework

            service = AISecurityFramework()
            await service.initialize()
            self.services[AIServiceType.SECURITY_AI] = service
            self.logger.info("Security AI service initialized")
        except ImportError as e:
            self.logger.warning(f"Missing dependencies for Security AI: {e}")
            self.services[AIServiceType.SECURITY_AI] = None
        except Exception as e:
            self.logger.warning(f"Could not initialize Security AI: {e}")
            self.services[AIServiceType.SECURITY_AI] = None

    async def _initialize_edge_computing(self):
        """Initialize Edge Computing service"""
        try:
            from .edge_computing_ai import EdgeComputingDistributedAI

            service = EdgeComputingDistributedAI()
            await service.initialize()
            self.services[AIServiceType.EDGE_COMPUTING] = service
            self.logger.info("Edge Computing service initialized")
        except ImportError as e:
            self.logger.warning(f"Missing dependencies for Edge Computing: {e}")
            self.services[AIServiceType.EDGE_COMPUTING] = None
        except Exception as e:
            self.logger.warning(f"Could not initialize Edge Computing: {e}")
            self.services[AIServiceType.EDGE_COMPUTING] = None

    async def _initialize_personalization(self):
        """Initialize Personalization service"""
        try:
            from .personalization_engine import PersonalizationRecommendationEngine

            service = PersonalizationRecommendationEngine()
            await service.initialize()
            self.services[AIServiceType.PERSONALIZATION] = service
            self.logger.info("Personalization service initialized")
        except ImportError as e:
            self.logger.warning(f"Missing dependencies for Personalization: {e}")
            self.services[AIServiceType.PERSONALIZATION] = None
        except Exception as e:
            self.logger.warning(f"Could not initialize Personalization: {e}")
            self.services[AIServiceType.PERSONALIZATION] = None

    async def _initialize_collaboration(self):
        """Initialize Collaboration service"""
        try:
            from .collaboration_intelligence import CollaborationIntelligence

            service = CollaborationIntelligence()
            await service.initialize()
            self.services[AIServiceType.COLLABORATION] = service
            self.logger.info("Collaboration service initialized")
        except ImportError as e:
            self.logger.warning(f"Missing dependencies for Collaboration: {e}")
            self.services[AIServiceType.COLLABORATION] = None
        except Exception as e:
            self.logger.warning(f"Could not initialize Collaboration: {e}")
            self.services[AIServiceType.COLLABORATION] = None

    async def _initialize_mlops(self):
        """Initialize MLOps service"""
        try:
            from .mlops_platform import MLOpsPlatform

            service = MLOpsPlatform()
            await service.initialize()
            self.services[AIServiceType.MLOPS] = service
            self.logger.info("MLOps service initialized")
        except ImportError as e:
            self.logger.warning(f"Missing dependencies for MLOps: {e}")
            self.services[AIServiceType.MLOPS] = None
        except Exception as e:
            self.logger.warning(f"Could not initialize MLOps: {e}")
            self.services[AIServiceType.MLOPS] = None

    async def _initialize_monitoring(self):
        """Initialize Monitoring service"""
        try:
            from .intelligent_monitoring import IntelligentMonitoringSystem

            service = IntelligentMonitoringSystem()
            await service.initialize()
            self.services[AIServiceType.MONITORING] = service
            self.logger.info("Monitoring service initialized")
        except ImportError as e:
            self.logger.warning(f"Missing dependencies for Monitoring: {e}")
            self.services[AIServiceType.MONITORING] = None
        except Exception as e:
            self.logger.warning(f"Could not initialize Monitoring: {e}")
            self.services[AIServiceType.MONITORING] = None

    async def process_request(self, request: AIServiceRequest) -> AIServiceResponse:
        """Process an AI service request"""
        start_time = datetime.now()

        try:
            self.logger.info(
                f"Processing {request.service_type.value} request {request.request_id}"
            )

            # Check if service is available
            if self.services.get(request.service_type) is None:
                return AIServiceResponse(
                    request_id=request.request_id,
                    service_type=request.service_type,
                    success=False,
                    error_message=f"{request.service_type.value} service is not available",
                    processing_time=(datetime.now() - start_time).total_seconds(),
                )

            # Route to appropriate service
            service = self.services[request.service_type]

            if request.service_type == AIServiceType.PREDICTIVE_ANALYTICS:
                result = await self._handle_predictive_analytics(service, request)
            elif request.service_type == AIServiceType.NLP_CONVERSATION:
                result = await self._handle_nlp_conversation(service, request)
            elif request.service_type == AIServiceType.AUTOMATION_ORCHESTRATION:
                result = await self._handle_automation_orchestration(service, request)
            elif request.service_type == AIServiceType.COMPUTER_VISION:
                result = await self._handle_computer_vision(service, request)
            elif request.service_type == AIServiceType.SECURITY_AI:
                result = await self._handle_security_ai(service, request)
            elif request.service_type == AIServiceType.EDGE_COMPUTING:
                result = await self._handle_edge_computing(service, request)
            elif request.service_type == AIServiceType.PERSONALIZATION:
                result = await self._handle_personalization(service, request)
            elif request.service_type == AIServiceType.COLLABORATION:
                result = await self._handle_collaboration(service, request)
            elif request.service_type == AIServiceType.MLOPS:
                result = await self._handle_mlops(service, request)
            elif request.service_type == AIServiceType.MONITORING:
                result = await self._handle_monitoring(service, request)
            else:
                raise ValueError(f"Unknown service type: {request.service_type}")

            processing_time = (datetime.now() - start_time).total_seconds()

            return AIServiceResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                success=True,
                result=result,
                confidence_score=result.get("confidence_score"),
                processing_time=processing_time,
            )

        except Exception as e:
            self.logger.error(
                f"Error processing {request.service_type.value} request: {e}"
            )
            self.logger.error(traceback.format_exc())

            return AIServiceResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                success=False,
                error_message=str(e),
                processing_time=(datetime.now() - start_time).total_seconds(),
            )

    async def _handle_predictive_analytics(
        self, service, request: AIServiceRequest
    ) -> Dict[str, Any]:
        """Handle predictive analytics requests"""
        if service is None:
            # Return mock response when service is not available
            return {
                "prediction_type": request.parameters.get(
                    "prediction_type", "productivity_score"
                ),
                "predicted_value": 85.5,
                "confidence_score": 0.82,
                "explanation": "Mock prediction - install ML dependencies to enable real predictions",
                "feature_importance": {
                    "historical_performance": 0.4,
                    "time_patterns": 0.3,
                    "workload_balance": 0.3,
                },
                "note": "This is a mock response. Install scikit-learn, pandas, and other ML dependencies to enable real AI predictions.",
            }

        prediction_type = request.parameters.get(
            "prediction_type", "productivity_score"
        )
        time_horizon = request.parameters.get("time_horizon", 7)
        features = request.input_data or {}

        result = await service.generate_prediction(
            user_id=request.user_id,
            prediction_type=prediction_type,
            time_horizon=time_horizon,
            features=features,
            options=request.options,
        )

        return result

    async def _handle_nlp_conversation(
        self, service, request: AIServiceRequest
    ) -> Dict[str, Any]:
        """Handle NLP conversation requests"""
        if service is None:
            action = request.parameters.get("action", "analyze")
            text_input = (
                request.input_data.get("text", "") if request.input_data else ""
            )
            return {
                "action": action,
                "language": request.input_data.get("language", "en")
                if request.input_data
                else "en",
                "processed_text": f"Mock {action} result for: {text_input[:50]}...",
                "confidence_score": 0.75,
                "note": "This is a mock response. Install NLP dependencies (spacy, nltk, transformers) to enable real AI conversation processing.",
            }

        action = request.parameters.get("action", "analyze")
        text_input = request.input_data.get("text", "") if request.input_data else ""

        if action == "analyze":
            result = await service.analyze_text(text_input, options=request.options)
        elif action == "generate":
            result = await service.generate_response(
                text_input, options=request.options
            )
        elif action == "summarize":
            result = await service.summarize_conversation(
                text_input, options=request.options
            )
        else:
            result = {"error": f"Unknown action: {action}"}

        return result

    async def _handle_automation_orchestration(
        self, service, request: AIServiceRequest
    ) -> Dict[str, Any]:
        """Handle automation orchestration requests"""
        if service is None:
            workflow_type = request.parameters.get("workflow_type", "task_automation")
            return {
                "workflow_type": workflow_type,
                "workflow_id": f"mock_workflow_{uuid.uuid4().hex[:8]}",
                "trigger_condition": request.input_data.get(
                    "trigger_condition", "daily"
                ),
                "execution_schedule": request.input_data.get(
                    "execution_schedule", "daily"
                ),
                "status": "created",
                "description": f"Mock {workflow_type} workflow created successfully",
                "note": "This is a mock response. Install automation dependencies to enable real workflow orchestration.",
            }

        workflow_type = request.parameters.get("workflow_type", "task_automation")
        config = request.input_data or {}

        result = await service.create_workflow(
            user_id=request.user_id,
            workflow_type=workflow_type,
            config=config,
            options=request.options,
        )

        return result

    async def _handle_computer_vision(
        self, service, request: AIServiceRequest
    ) -> Dict[str, Any]:
        """Handle computer vision requests"""
        if service is None:
            analysis_type = request.parameters.get("analysis_type", "object_detection")
            return {
                "analysis_type": analysis_type,
                "detections": [
                    {
                        "label": "person",
                        "confidence": 0.89,
                        "bbox": [100, 50, 200, 300],
                    },
                    {
                        "label": "computer",
                        "confidence": 0.76,
                        "bbox": [150, 100, 250, 180],
                    },
                ],
                "processing_time": 1.2,
                "confidence_score": 0.82,
                "note": "This is a mock response. Install computer vision dependencies (torch, torchvision, opencv) to enable real image analysis.",
            }

        analysis_type = request.parameters.get("analysis_type", "object_detection")
        image_data = (
            request.input_data.get("image_data") if request.input_data else None
        )

        result = await service.analyze_image(
            image_data=image_data, analysis_type=analysis_type, options=request.options
        )

        return result

    async def _handle_security_ai(
        self, service, request: AIServiceRequest
    ) -> Dict[str, Any]:
        """Handle security AI requests"""
        if service is None:
            security_action = request.parameters.get("action", "scan")
            return {
                "action": security_action,
                "threats": [
                    {
                        "type": "suspicious_login",
                        "severity": "medium",
                        "confidence": 0.78,
                    },
                    {"type": "unusual_traffic", "severity": "low", "confidence": 0.65},
                ],
                "scan_duration": 2.1,
                "recommendations": [
                    "Review recent login attempts",
                    "Monitor network traffic",
                ],
                "note": "This is a mock response. Install security dependencies to enable real threat detection.",
            }

        security_action = request.parameters.get("action", "scan")
        data = request.input_data or {}

        if security_action == "scan":
            result = await service.scan_for_threats(data, options=request.options)
        elif security_action == "analyze":
            result = await service.analyze_security_event(data, options=request.options)
        else:
            result = {"error": f"Unknown security action: {security_action}"}

        return result

    async def _handle_edge_computing(
        self, service, request: AIServiceRequest
    ) -> Dict[str, Any]:
        """Handle edge computing requests"""
        if service is None:
            operation = request.parameters.get("operation", "deploy")
            return {
                "operation": operation,
                "model_name": request.input_data.get("model_name", "unknown")
                if request.input_data
                else "unknown",
                "target_devices": request.input_data.get("target_devices", [])
                if request.input_data
                else [],
                "status": "completed",
                "deployment_id": f"mock_deployment_{uuid.uuid4().hex[:8]}",
                "details": f"Mock {operation} operation completed successfully",
                "note": "This is a mock response. Install edge computing dependencies to enable real distributed AI.",
            }

        operation = request.parameters.get("operation", "deploy")
        config = request.input_data or {}

        result = await service.manage_edge_deployment(
            operation=operation, config=config, options=request.options
        )

        return result

    async def _handle_personalization(
        self, service, request: AIServiceRequest
    ) -> Dict[str, Any]:
        """Handle personalization requests"""
        if service is None:
            recommendation_type = request.parameters.get(
                "recommendation_type", "content_based"
            )
            return {
                "recommendation_type": recommendation_type,
                "recommendations": [
                    {
                        "item_type": "task",
                        "title": "Daily Review",
                        "score": 0.89,
                        "reason": "Based on your productivity patterns",
                    },
                    {
                        "item_type": "workflow",
                        "title": "Email Automation",
                        "score": 0.76,
                        "reason": "Matches your automation preferences",
                    },
                    {
                        "item_type": "tool",
                        "title": "Time Tracker",
                        "score": 0.82,
                        "reason": "Complements your current tools",
                    },
                ],
                "total_recommendations": 3,
                "note": "This is a mock response. Install personalization dependencies to enable real recommendation engine.",
            }

        recommendation_type = request.parameters.get(
            "recommendation_type", "content_based"
        )
        user_data = request.input_data or {}

        result = await service.generate_recommendations(
            user_id=request.user_id,
            recommendation_type=recommendation_type,
            user_data=user_data,
            options=request.options,
        )

        return result

    async def _handle_collaboration(
        self, service, request: AIServiceRequest
    ) -> Dict[str, Any]:
        """Handle collaboration requests"""
        if service is None:
            collaboration_action = request.parameters.get("action", "analyze_team")
            return {
                "action": collaboration_action,
                "team_size": request.input_data.get("team_size", 5)
                if request.input_data
                else 5,
                "team_health_score": 0.78,
                "communication_score": 0.82,
                "insights": [
                    {
                        "title": "Good Communication Flow",
                        "description": "Team communication is effective",
                        "type": "positive",
                    },
                    {
                        "title": "Meeting Optimization Needed",
                        "description": "Some meetings could be more efficient",
                        "type": "suggestion",
                    },
                ],
                "recommendations": [
                    "Continue current communication practices",
                    "Consider async updates for routine tasks",
                ],
                "note": "This is a mock response. Install collaboration dependencies to enable real team intelligence.",
            }

        collaboration_action = request.parameters.get("action", "analyze_team")
        team_data = request.input_data or {}

        result = await service.analyze_team_collaboration(
            team_data=team_data, options=request.options
        )

        return result

    async def _handle_mlops(self, service, request: AIServiceRequest) -> Dict[str, Any]:
        """Handle MLOps requests"""
        if service is None:
            mlops_action = request.parameters.get("action", "train_model")
            return {
                "action": mlops_action,
                "model_type": request.input_data.get("model_type", "classification")
                if request.input_data
                else "classification",
                "status": "completed",
                "performance_metrics": {
                    "accuracy": 0.87,
                    "precision": 0.85,
                    "recall": 0.88,
                    "f1_score": 0.865,
                },
                "training_duration": 45.2,
                "model_version": "1.0.0",
                "note": "This is a mock response. Install MLOps dependencies (scikit-learn, mlflow, etc.) to enable real ML operations.",
            }

        mlops_action = request.parameters.get("action", "train_model")
        config = request.input_data or {}

        result = await service.manage_ml_pipeline(
            action=mlops_action, config=config, options=request.options
        )

        return result

    async def _handle_monitoring(
        self, service, request: AIServiceRequest
    ) -> Dict[str, Any]:
        """Handle monitoring requests"""
        if service is None:
            monitoring_action = request.parameters.get("action", "check_health")
            return {
                "action": monitoring_action,
                "overall_health": "healthy",
                "active_alerts": 0,
                "recent_anomalies": 1,
                "components": {
                    "cpu": {"usage_percent": 45.2, "status": "healthy"},
                    "memory": {"usage_percent": 62.8, "status": "healthy"},
                    "disk": {"usage_percent": 34.1, "status": "healthy"},
                    "network": {"connectivity": "healthy", "status": "healthy"},
                },
                "anomalies_detected": [
                    {"type": "minor_spike", "component": "cpu", "severity": "low"}
                ],
                "note": "This is a mock response. Install monitoring dependencies (psutil, prometheus, etc.) to enable real system monitoring.",
            }

        monitoring_action = request.parameters.get("action", "check_health")
        system_data = request.input_data or {}

        result = await service.monitor_system(
            action=monitoring_action, system_data=system_data, options=request.options
        )

        return result

    def get_available_services(self) -> Dict[str, bool]:
        """Get availability status of all services"""
        return {
            service_type.value: (service is not None)
            for service_type, service in self.services.items()
        }

    def get_service_config_options(self, service_type: AIServiceType) -> Dict[str, Any]:
        """Get configuration options for a specific service"""
        # Return dropdown options and input field configurations
        configs = {
            AIServiceType.PREDICTIVE_ANALYTICS: {
                "prediction_types": [
                    {"value": "productivity_score", "label": "Productivity Score"},
                    {"value": "task_completion_time", "label": "Task Completion Time"},
                    {"value": "workload_forecast", "label": "Workload Forecast"},
                    {"value": "energy_levels", "label": "Energy Levels"},
                    {
                        "value": "meeting_effectiveness",
                        "label": "Meeting Effectiveness",
                    },
                    {"value": "focus_time_optimal", "label": "Optimal Focus Time"},
                    {"value": "deadline_risk", "label": "Deadline Risk"},
                    {"value": "burnout_risk", "label": "Burnout Risk"},
                    {
                        "value": "collaboration_patterns",
                        "label": "Collaboration Patterns",
                    },
                    {"value": "skill_development", "label": "Skill Development"},
                ],
                "time_horizons": [
                    {"value": 1, "label": "1 Day"},
                    {"value": 7, "label": "1 Week"},
                    {"value": 30, "label": "1 Month"},
                    {"value": 90, "label": "3 Months"},
                ],
                "input_fields": [
                    {
                        "name": "historical_data_points",
                        "type": "number",
                        "label": "Historical Data Points",
                        "default": 30,
                    },
                    {
                        "name": "confidence_level",
                        "type": "float",
                        "label": "Confidence Level (0-1)",
                        "default": 0.95,
                    },
                ],
            },
            AIServiceType.NLP_CONVERSATION: {
                "actions": [
                    {"value": "analyze", "label": "Analyze Text"},
                    {"value": "generate", "label": "Generate Response"},
                    {"value": "summarize", "label": "Summarize Conversation"},
                ],
                "input_fields": [
                    {
                        "name": "text",
                        "type": "textarea",
                        "label": "Input Text",
                        "required": True,
                    },
                    {
                        "name": "language",
                        "type": "text",
                        "label": "Language",
                        "default": "en",
                    },
                    {
                        "name": "max_length",
                        "type": "number",
                        "label": "Max Length",
                        "default": 500,
                    },
                ],
            },
            AIServiceType.AUTOMATION_ORCHESTRATION: {
                "workflow_types": [
                    {"value": "task_automation", "label": "Task Automation"},
                    {"value": "document_processing", "label": "Document Processing"},
                    {"value": "email_management", "label": "Email Management"},
                    {"value": "calendar_scheduling", "label": "Calendar Scheduling"},
                    {"value": "data_sync", "label": "Data Synchronization"},
                ],
                "input_fields": [
                    {
                        "name": "trigger_condition",
                        "type": "text",
                        "label": "Trigger Condition",
                    },
                    {
                        "name": "execution_schedule",
                        "type": "text",
                        "label": "Execution Schedule (cron format)",
                    },
                    {
                        "name": "max_retries",
                        "type": "number",
                        "label": "Max Retries",
                        "default": 3,
                    },
                ],
            },
            AIServiceType.COMPUTER_VISION: {
                "analysis_types": [
                    {"value": "object_detection", "label": "Object Detection"},
                    {"value": "text_extraction", "label": "Text Extraction (OCR)"},
                    {"value": "document_analysis", "label": "Document Analysis"},
                    {"value": "image_captioning", "label": "Image Captioning"},
                    {"value": "visual_qa", "label": "Visual Question Answering"},
                    {"value": "scene_understanding", "label": "Scene Understanding"},
                    {"value": "face_detection", "label": "Face Detection"},
                    {"value": "emotion_recognition", "label": "Emotion Recognition"},
                    {"value": "content_moderation", "label": "Content Moderation"},
                    {"value": "similarity_search", "label": "Similarity Search"},
                ],
                "input_fields": [
                    {"name": "image_url", "type": "url", "label": "Image URL"},
                    {
                        "name": "confidence_threshold",
                        "type": "float",
                        "label": "Confidence Threshold",
                        "default": 0.5,
                    },
                    {
                        "name": "max_results",
                        "type": "number",
                        "label": "Max Results",
                        "default": 10,
                    },
                ],
            },
            AIServiceType.SECURITY_AI: {
                "actions": [
                    {"value": "scan", "label": "Scan for Threats"},
                    {"value": "analyze", "label": "Analyze Security Event"},
                ],
                "input_fields": [
                    {
                        "name": "scan_target",
                        "type": "text",
                        "label": "Scan Target (file, URL, etc.)",
                    },
                    {
                        "name": "threat_types",
                        "type": "multiselect",
                        "label": "Threat Types",
                        "options": [
                            "malware",
                            "phishing",
                            "intrusion",
                            "data_leak",
                            "anomaly",
                        ],
                    },
                    {
                        "name": "severity_level",
                        "type": "select",
                        "label": "Severity Level",
                        "options": ["low", "medium", "high", "critical"],
                    },
                ],
            },
            AIServiceType.EDGE_COMPUTING: {
                "operations": [
                    {"value": "deploy", "label": "Deploy Model"},
                    {"value": "update", "label": "Update Model"},
                    {"value": "monitor", "label": "Monitor Performance"},
                    {"value": "scale", "label": "Scale Resources"},
                ],
                "input_fields": [
                    {"name": "model_name", "type": "text", "label": "Model Name"},
                    {
                        "name": "target_devices",
                        "type": "multiselect",
                        "label": "Target Devices",
                        "options": [
                            "raspberry_pi",
                            "jetson_nano",
                            "coral_tpu",
                            "mobile_device",
                            "edge_server",
                        ],
                    },
                    {
                        "name": "resource_limits",
                        "type": "text",
                        "label": "Resource Limits (CPU, Memory)",
                    },
                ],
            },
            AIServiceType.PERSONALIZATION: {
                "recommendation_types": [
                    {"value": "content_based", "label": "Content-Based"},
                    {"value": "collaborative", "label": "Collaborative Filtering"},
                    {"value": "hybrid", "label": "Hybrid Approach"},
                ],
                "input_fields": [
                    {
                        "name": "user_preferences",
                        "type": "textarea",
                        "label": "User Preferences",
                    },
                    {
                        "name": "context_data",
                        "type": "textarea",
                        "label": "Context Data",
                    },
                    {
                        "name": "max_recommendations",
                        "type": "number",
                        "label": "Max Recommendations",
                        "default": 10,
                    },
                ],
            },
            AIServiceType.COLLABORATION: {
                "actions": [
                    {"value": "analyze_team", "label": "Analyze Team Dynamics"},
                    {"value": "optimize_workflow", "label": "Optimize Workflow"},
                    {"value": "predict_conflicts", "label": "Predict Conflicts"},
                ],
                "input_fields": [
                    {"name": "team_size", "type": "number", "label": "Team Size"},
                    {
                        "name": "communication_patterns",
                        "type": "textarea",
                        "label": "Communication Patterns",
                    },
                    {
                        "name": "project_complexity",
                        "type": "select",
                        "label": "Project Complexity",
                        "options": ["low", "medium", "high"],
                    },
                ],
            },
            AIServiceType.MLOPS: {
                "actions": [
                    {"value": "train_model", "label": "Train Model"},
                    {"value": "deploy_model", "label": "Deploy Model"},
                    {"value": "monitor_performance", "label": "Monitor Performance"},
                    {"value": "retrain_model", "label": "Retrain Model"},
                ],
                "input_fields": [
                    {
                        "name": "model_type",
                        "type": "select",
                        "label": "Model Type",
                        "options": [
                            "classification",
                            "regression",
                            "clustering",
                            "nlp",
                            "computer_vision",
                        ],
                    },
                    {"name": "dataset_path", "type": "text", "label": "Dataset Path"},
                    {
                        "name": "hyperparameters",
                        "type": "textarea",
                        "label": "Hyperparameters (JSON)",
                    },
                ],
            },
            AIServiceType.MONITORING: {
                "actions": [
                    {"value": "check_health", "label": "Check System Health"},
                    {"value": "detect_anomalies", "label": "Detect Anomalies"},
                    {"value": "predict_failures", "label": "Predict Failures"},
                    {"value": "optimize_performance", "label": "Optimize Performance"},
                ],
                "input_fields": [
                    {
                        "name": "system_metrics",
                        "type": "textarea",
                        "label": "System Metrics (JSON)",
                    },
                    {
                        "name": "monitoring_window",
                        "type": "number",
                        "label": "Monitoring Window (hours)",
                        "default": 24,
                    },
                    {
                        "name": "alert_thresholds",
                        "type": "textarea",
                        "label": "Alert Thresholds (JSON)",
                    },
                ],
            },
        }

        return configs.get(service_type, {})


# Global AI Services API instance
ai_services_api = AIServicesAPI()


async def initialize_ai_services():
    """Initialize the global AI services API"""
    await ai_services_api.initialize()


async def process_ai_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process an AI service request from external input"""
    try:
        # Convert request data to AIServiceRequest
        service_type = AIServiceType(request_data["service_type"])
        request = AIServiceRequest(
            service_type=service_type,
            user_id=request_data.get("user_id", "default_user"),
            parameters=request_data.get("parameters", {}),
            input_data=request_data.get("input_data"),
            options=request_data.get("options"),
        )

        # Process the request
        response = await ai_services_api.process_request(request)

        # Convert response to dict
        return {
            "request_id": response.request_id,
            "service_type": response.service_type.value,
            "success": response.success,
            "result": response.result,
            "error_message": response.error_message,
            "confidence_score": response.confidence_score,
            "processing_time": response.processing_time,
            "timestamp": response.timestamp.isoformat() if response.timestamp else None,
        }

    except Exception as e:
        return {
            "success": False,
            "error_message": str(e),
            "timestamp": datetime.now().isoformat(),
        }


def get_service_configurations() -> Dict[str, Any]:
    """Get configuration options for all services"""
    configs = {}
    for service_type in AIServiceType:
        configs[service_type.value] = ai_services_api.get_service_config_options(
            service_type
        )

    return configs


def get_service_availability() -> Dict[str, bool]:
    """Get availability status of all services"""
    return ai_services_api.get_available_services()


_spec_registry = get_default_registry()
_spec_registry.register_feature(
    "assistant_core.ai_services_api",
    sections=["1.7.3", "2.2", "5.6", "8.10", "9.18"],
    metadata={
        "module": __name__,
        "services": [service.value for service in AIServiceType],
    },
)
