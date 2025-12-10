"""
Edge Computing & Distributed AI Processing System

Advanced AI capabilities for distributed model deployment, federated learning,
edge orchestration, and intelligent resource management.
"""

import asyncio
import json
import uuid
import platform
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - fallback when psutil missing
    from utils.psutil_stub import psutil  # type: ignore
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import pickle
import base64

from config.logging_config import setup_logger


class EdgeDeviceType(Enum):
    RASPBERRY_PI = "raspberry_pi"
    JETSON_NANO = "jetson_nano"
    CORAL_TPU = "coral_tpu"
    MOBILE_DEVICE = "mobile_device"
    EDGE_SERVER = "edge_server"
    IOT_DEVICE = "iot_device"


class DeploymentStatus(Enum):
    PENDING = "pending"
    DEPLOYING = "deploying"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"
    UPDATING = "updating"


class ModelFormat(Enum):
    TENSORFLOW_LITE = "tflite"
    ONNX = "onnx"
    PYTORCH_MOBILE = "pytorch_mobile"
    COREML = "coreml"
    OPENVINO = "openvino"


@dataclass
class EdgeDevice:
    """Edge device information"""
    device_id: str
    device_type: EdgeDeviceType
    hostname: str
    ip_address: str
    capabilities: Dict[str, Any]
    status: str = "online"
    last_seen: Optional[datetime] = None
    models_deployed: List[str] = None

    def __post_init__(self):
        if self.models_deployed is None:
            self.models_deployed = []
        if not self.last_seen:
            self.last_seen = datetime.now()


@dataclass
class ModelDeployment:
    """Model deployment configuration"""
    deployment_id: str
    model_name: str
    model_version: str
    target_devices: List[EdgeDeviceType]
    model_format: ModelFormat
    model_data: bytes
    config: Dict[str, Any]
    status: DeploymentStatus = DeploymentStatus.PENDING
    created_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None
    performance_metrics: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()
        if self.performance_metrics is None:
            self.performance_metrics = {}


@dataclass
class FederatedLearningConfig:
    """Federated learning configuration"""
    rounds: int
    clients_per_round: int
    learning_rate: float
    aggregation_method: str = "fedavg"
    privacy_budget: Optional[float] = None
    differential_privacy: bool = False


class EdgeComputingDistributedAI:
    """Edge Computing & Distributed AI Processing System"""

    def __init__(self):
        self.logger = setup_logger("EdgeComputingAI")
        self.devices: Dict[str, EdgeDevice] = {}
        self.deployments: Dict[str, ModelDeployment] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None

    async def initialize(self):
        """Initialize the edge computing system"""
        self.logger.info("Initializing Edge Computing & Distributed AI System...")

        # Register local device
        await self._register_local_device()

        # Start monitoring
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_devices())

        self.logger.info("Edge Computing system initialized")

    async def _register_local_device(self):
        """Register the local device"""
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)

            # Detect device type based on platform
            device_type = self._detect_device_type()

            # Get device capabilities
            capabilities = await self._get_device_capabilities()

            device = EdgeDevice(
                device_id=str(uuid.uuid4()),
                device_type=device_type,
                hostname=hostname,
                ip_address=ip_address,
                capabilities=capabilities
            )

            self.devices[device.device_id] = device
            self.logger.info(f"Registered local device: {device.hostname} ({device.device_type.value})")

        except Exception as e:
            self.logger.error(f"Failed to register local device: {e}")

    def _detect_device_type(self) -> EdgeDeviceType:
        """Detect the type of edge device"""
        system = platform.system().lower()
        machine = platform.machine().lower()

        if "raspberry" in platform.platform().lower():
            return EdgeDeviceType.RASPBERRY_PI
        elif "jetson" in platform.platform().lower():
            return EdgeDeviceType.JETSON_NANO
        elif "darwin" in system:  # macOS
            return EdgeDeviceType.MOBILE_DEVICE
        elif "linux" in system and ("arm" in machine or "aarch64" in machine):
            return EdgeDeviceType.EDGE_SERVER  # Could be various ARM devices
        else:
            return EdgeDeviceType.EDGE_SERVER

    async def _get_device_capabilities(self) -> Dict[str, Any]:
        """Get device hardware and software capabilities"""
        capabilities = {
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq().max if psutil.cpu_freq() else None,
            "memory_total": psutil.virtual_memory().total,
            "gpu_available": False,
            "supported_formats": [ModelFormat.TENSORFLOW_LITE.value, ModelFormat.ONNX.value],
            "platform": platform.platform(),
            "python_version": platform.python_version()
        }

        # Check for GPU
        try:
            import torch
            capabilities["gpu_available"] = torch.cuda.is_available()
            if capabilities["gpu_available"]:
                capabilities["gpu_count"] = torch.cuda.device_count()
                capabilities["gpu_name"] = torch.cuda.get_device_name(0)
        except ImportError:
            pass

        # Check for specialized hardware
        try:
            import tflite_runtime.interpreter as tflite
            capabilities["tpu_available"] = True
            capabilities["supported_formats"].append(ModelFormat.TENSORFLOW_LITE.value)
        except ImportError:
            capabilities["tpu_available"] = False

        return capabilities

    async def _monitor_devices(self):
        """Monitor device health and status"""
        while self._running:
            try:
                # Update device last_seen times
                current_time = datetime.now()
                for device in self.devices.values():
                    if device.status == "online":
                        device.last_seen = current_time

                # Check for offline devices
                offline_threshold = timedelta(minutes=5)
                for device in self.devices.values():
                    if device.last_seen and (current_time - device.last_seen) > offline_threshold:
                        device.status = "offline"
                        self.logger.warning(f"Device {device.hostname} marked as offline")

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error in device monitoring: {e}")
                await asyncio.sleep(60)

    async def manage_edge_deployment(self, operation: str, config: Dict[str, Any],
                                   options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manage edge deployments"""
        try:
            if operation == "deploy":
                return await self._deploy_model(config, options)
            elif operation == "update":
                return await self._update_model(config, options)
            elif operation == "monitor":
                return await self._monitor_deployment(config, options)
            elif operation == "scale":
                return await self._scale_deployment(config, options)
            else:
                return {"error": f"Unknown operation: {operation}"}

        except Exception as e:
            self.logger.error(f"Error in edge deployment management: {e}")
            return {"error": str(e)}

    async def _deploy_model(self, config: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Deploy a model to edge devices"""
        model_name = config.get("model_name")
        target_devices = config.get("target_devices", [])
        model_format = config.get("model_format", ModelFormat.TENSORFLOW_LITE.value)

        if not model_name:
            return {"error": "Model name is required"}

        # Convert string device types to enum
        device_types = [EdgeDeviceType(dt) if isinstance(dt, str) else dt for dt in target_devices]

        # Find suitable devices
        suitable_devices = []
        for device in self.devices.values():
            if device.status == "online" and device.device_type in device_types:
                suitable_devices.append(device)

        if not suitable_devices:
            return {"error": "No suitable edge devices found"}

        # Create deployment
        deployment_id = str(uuid.uuid4())
        deployment = ModelDeployment(
            deployment_id=deployment_id,
            model_name=model_name,
            model_version=config.get("model_version", "1.0.0"),
            target_devices=device_types,
            model_format=ModelFormat(model_format),
            model_data=b"",  # Would be loaded from storage
            config=config
        )

        self.deployments[deployment_id] = deployment

        # Start deployment process
        asyncio.create_task(self._execute_deployment(deployment, suitable_devices))

        return {
            "deployment_id": deployment_id,
            "status": "deployment_started",
            "target_devices_count": len(suitable_devices),
            "estimated_completion": "5-10 minutes"
        }

    async def _execute_deployment(self, deployment: ModelDeployment, devices: List[EdgeDevice]):
        """Execute the actual deployment"""
        try:
            deployment.status = DeploymentStatus.DEPLOYING

            # Simulate deployment process
            for device in devices:
                self.logger.info(f"Deploying {deployment.model_name} to {device.hostname}")

                # In real implementation, this would:
                # 1. Transfer model files to device
                # 2. Configure device runtime
                # 3. Start model inference service
                # 4. Validate deployment

                await asyncio.sleep(2)  # Simulate deployment time

                device.models_deployed.append(deployment.model_name)

            deployment.status = DeploymentStatus.RUNNING
            deployment.deployed_at = datetime.now()

            self.logger.info(f"Successfully deployed {deployment.model_name} to {len(devices)} devices")

        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            deployment.status = DeploymentStatus.FAILED

    async def _update_model(self, config: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update an existing model deployment"""
        deployment_id = config.get("deployment_id")
        new_version = config.get("new_version")

        if not deployment_id or deployment_id not in self.deployments:
            return {"error": "Deployment not found"}

        deployment = self.deployments[deployment_id]
        deployment.status = DeploymentStatus.UPDATING

        # Simulate update process
        await asyncio.sleep(3)

        deployment.model_version = new_version or f"{float(deployment.model_version) + 0.1:.1f}"
        deployment.status = DeploymentStatus.RUNNING

        return {
            "deployment_id": deployment_id,
            "status": "updated",
            "new_version": deployment.model_version
        }

    async def _monitor_deployment(self, config: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Monitor deployment performance"""
        deployment_id = config.get("deployment_id")

        if not deployment_id or deployment_id not in self.deployments:
            return {"error": "Deployment not found"}

        deployment = self.deployments[deployment_id]

        # Generate mock performance metrics
        metrics = {
            "inference_latency_ms": 45.2,
            "throughput_req_per_sec": 23.8,
            "cpu_usage_percent": 68.5,
            "memory_usage_mb": 234.1,
            "error_rate_percent": 0.02,
            "uptime_hours": 24.5
        }

        deployment.performance_metrics.update(metrics)

        return {
            "deployment_id": deployment_id,
            "status": deployment.status.value,
            "performance_metrics": metrics,
            "device_health": self._get_device_health_summary()
        }

    async def _scale_deployment(self, config: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Scale deployment resources"""
        deployment_id = config.get("deployment_id")
        scale_action = config.get("scale_action", "up")  # up or down
        target_instances = config.get("target_instances", 1)

        if not deployment_id or deployment_id not in self.deployments:
            return {"error": "Deployment not found"}

        deployment = self.deployments[deployment_id]

        # Find additional devices if scaling up
        if scale_action == "up":
            current_device_count = len([d for d in self.devices.values()
                                      if deployment.model_name in d.models_deployed])

            if target_instances > current_device_count:
                available_devices = [d for d in self.devices.values()
                                   if d.status == "online" and deployment.model_name not in d.models_deployed
                                   and d.device_type in deployment.target_devices]

                devices_to_add = available_devices[:target_instances - current_device_count]

                if devices_to_add:
                    await self._execute_deployment(deployment, devices_to_add)

        return {
            "deployment_id": deployment_id,
            "scale_action": scale_action,
            "target_instances": target_instances,
            "current_instances": len([d for d in self.devices.values()
                                    if deployment.model_name in d.models_deployed])
        }

    def _get_device_health_summary(self) -> Dict[str, Any]:
        """Get summary of device health"""
        total_devices = len(self.devices)
        online_devices = len([d for d in self.devices.values() if d.status == "online"])
        offline_devices = total_devices - online_devices

        return {
            "total_devices": total_devices,
            "online_devices": online_devices,
            "offline_devices": offline_devices,
            "health_percentage": (online_devices / total_devices * 100) if total_devices > 0 else 0
        }

    async def start_federated_learning(self, config: FederatedLearningConfig,
                                     model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Start a federated learning process"""
        try:
            # This would coordinate federated learning across edge devices
            # For now, return a placeholder implementation

            return {
                "federated_learning_id": str(uuid.uuid4()),
                "status": "started",
                "config": asdict(config),
                "participants": len([d for d in self.devices.values() if d.status == "online"]),
                "estimated_completion": f"{config.rounds * 10} minutes"
            }

        except Exception as e:
            self.logger.error(f"Error starting federated learning: {e}")
            return {"error": str(e)}

    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "total_devices": len(self.devices),
            "online_devices": len([d for d in self.devices.values() if d.status == "online"]),
            "active_deployments": len([d for d in self.deployments.values() if d.status == DeploymentStatus.RUNNING]),
            "total_deployments": len(self.deployments),
            "system_health": "healthy" if any(d.status == "online" for d in self.devices.values()) else "degraded"
        }

    async def shutdown(self):
        """Shutdown the edge computing system"""
        self.logger.info("Shutting down Edge Computing system...")

        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()

        self.executor.shutdown(wait=True)
        self.logger.info("Edge Computing system shutdown complete")
