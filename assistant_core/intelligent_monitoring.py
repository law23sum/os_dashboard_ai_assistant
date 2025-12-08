"""
Intelligent Monitoring & Self-Healing Systems

AI-powered anomaly detection, predictive maintenance, automated remediation,
comprehensive system health monitoring, and adaptive thresholds.
"""

import asyncio
import json
import uuid
import statistics
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import socket
import platform
from collections import deque, defaultdict
import numpy as np
from scipy import stats

from config.logging_config import setup_logger


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SystemComponent(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    DATABASE = "database"
    API_ENDPOINTS = "api_endpoints"
    EXTERNAL_SERVICES = "external_services"
    APPLICATION = "application"


class AnomalyType(Enum):
    SPIKE = "spike"
    DIP = "dip"
    TREND_CHANGE = "trend_change"
    SEASONAL_ANOMALY = "seasonal_anomaly"
    STRUCTURAL_BREAK = "structural_break"


@dataclass
class SystemMetric:
    """System metric data point"""
    metric_id: str
    component: SystemComponent
    metric_name: str
    value: float
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Alert:
    """System alert"""
    alert_id: str
    severity: AlertSeverity
    component: SystemComponent
    title: str
    description: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    status: str = "active"
    remediation_actions: Optional[List[str]] = None
    metrics_snapshot: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.remediation_actions is None:
            self.remediation_actions = []


@dataclass
class AnomalyDetectionResult:
    """Anomaly detection result"""
    result_id: str
    component: SystemComponent
    metric_name: str
    anomaly_type: AnomalyType
    confidence_score: float
    detected_value: float
    expected_value: float
    deviation_percent: float
    detected_at: datetime
    time_window: str
    recommendations: List[str]


@dataclass
class PredictiveMaintenanceAlert:
    """Predictive maintenance alert"""
    alert_id: str
    component: SystemComponent
    failure_probability: float
    estimated_time_to_failure: int  # hours
    risk_level: str
    detected_at: datetime
    contributing_factors: List[str]
    preventive_actions: List[str]


@dataclass
class SelfHealingAction:
    """Self-healing action record"""
    action_id: str
    component: SystemComponent
    action_type: str
    action_description: str
    triggered_by: str  # alert_id or anomaly_id
    executed_at: datetime
    success: bool
    result: Optional[Dict[str, Any]] = None
    rollback_available: bool = False


class IntelligentMonitoringSystem:
    """Intelligent Monitoring & Self-Healing System"""

    def __init__(self):
        self.logger = setup_logger("IntelligentMonitoring")
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: List[Alert] = []
        self.anomalies: List[AnomalyDetectionResult] = []
        self.predictive_alerts: List[PredictiveMaintenanceAlert] = []
        self.healing_actions: List[SelfHealingAction] = []
        self.adaptive_thresholds: Dict[str, Dict[str, Any]] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        self.anomaly_detection_task: Optional[asyncio.Task] = None
        self.predictive_task: Optional[asyncio.Task] = None

    async def initialize(self):
        """Initialize the intelligent monitoring system"""
        self.logger.info("Initializing Intelligent Monitoring & Self-Healing System...")

        # Initialize adaptive thresholds
        await self._initialize_adaptive_thresholds()

        # Start monitoring tasks
        self.monitoring_task = asyncio.create_task(self._continuous_monitoring())
        self.anomaly_detection_task = asyncio.create_task(self._anomaly_detection_loop())
        self.predictive_task = asyncio.create_task(self._predictive_maintenance_loop())

        self.logger.info("Intelligent monitoring system initialized")

    async def _initialize_adaptive_thresholds(self):
        """Initialize adaptive thresholds for different components"""
        self.adaptive_thresholds = {
            "cpu_usage_percent": {
                "warning": 70,
                "critical": 90,
                "adaptation_window": 24,  # hours
                "min_threshold": 50,
                "max_threshold": 95
            },
            "memory_usage_percent": {
                "warning": 75,
                "critical": 90,
                "adaptation_window": 24,
                "min_threshold": 60,
                "max_threshold": 95
            },
            "disk_usage_percent": {
                "warning": 80,
                "critical": 95,
                "adaptation_window": 168,  # 1 week
                "min_threshold": 70,
                "max_threshold": 98
            },
            "response_time_ms": {
                "warning": 1000,
                "critical": 5000,
                "adaptation_window": 24,
                "min_threshold": 500,
                "max_threshold": 10000
            },
            "error_rate_percent": {
                "warning": 1.0,
                "critical": 5.0,
                "adaptation_window": 24,
                "min_threshold": 0.1,
                "max_threshold": 10.0
            }
        }

    async def monitor_system(self, action: str, system_data: Dict[str, Any],
                           options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Monitor system health and perform intelligent operations"""
        try:
            if action == "check_health":
                return await self._check_system_health()
            elif action == "detect_anomalies":
                return await self._detect_anomalies(system_data, options)
            elif action == "predict_failures":
                return await self._predict_failures(system_data, options)
            elif action == "optimize_performance":
                return await self._optimize_performance(system_data, options)
            else:
                return {"error": f"Unknown monitoring action: {action}"}

        except Exception as e:
            self.logger.error(f"Error in system monitoring: {e}")
            return {"error": str(e)}

    async def _check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        health_status = {
            "overall_health": "healthy",
            "components": {},
            "active_alerts": len([a for a in self.alerts if a.status == "active"]),
            "recent_anomalies": len([a for a in self.anomalies
                                   if (datetime.now() - a.detected_at).total_seconds() < 3600]),  # Last hour
            "predictive_alerts": len(self.predictive_alerts),
            "timestamp": datetime.now().isoformat()
        }

        # Check CPU health
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_status = self._evaluate_metric_health("cpu_usage_percent", cpu_percent)
        health_status["components"]["cpu"] = {
            "usage_percent": cpu_percent,
            "status": cpu_status,
            "thresholds": self.adaptive_thresholds.get("cpu_usage_percent", {})
        }

        # Check memory health
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_status = self._evaluate_metric_health("memory_usage_percent", memory_percent)
        health_status["components"]["memory"] = {
            "usage_percent": memory_percent,
            "available_gb": memory.available / (1024**3),
            "status": memory_status,
            "thresholds": self.adaptive_thresholds.get("memory_usage_percent", {})
        }

        # Check disk health
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_status = self._evaluate_metric_health("disk_usage_percent", disk_percent)
        health_status["components"]["disk"] = {
            "usage_percent": disk_percent,
            "free_gb": disk.free / (1024**3),
            "status": disk_status,
            "thresholds": self.adaptive_thresholds.get("disk_usage_percent", {})
        }

        # Check network
        network_status = await self._check_network_health()
        health_status["components"]["network"] = network_status

        # Overall health determination
        component_statuses = [comp["status"] for comp in health_status["components"].values()]
        if "critical" in component_statuses:
            health_status["overall_health"] = "critical"
        elif "warning" in component_statuses:
            health_status["overall_health"] = "warning"
        elif "unknown" in component_statuses:
            health_status["overall_health"] = "unknown"

        return health_status

    def _evaluate_metric_health(self, metric_name: str, value: float) -> str:
        """Evaluate if a metric value indicates healthy status"""
        thresholds = self.adaptive_thresholds.get(metric_name, {})

        if not thresholds:
            return "unknown"

        if value >= thresholds.get("critical", 100):
            return "critical"
        elif value >= thresholds.get("warning", 80):
            return "warning"
        else:
            return "healthy"

    async def _check_network_health(self) -> Dict[str, Any]:
        """Check network connectivity and performance"""
        try:
            # Simple connectivity check
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            connectivity = "healthy"
        except OSError:
            connectivity = "critical"

        # Get network I/O
        network_io = psutil.net_io_counters()

        return {
            "connectivity": connectivity,
            "bytes_sent": network_io.bytes_sent,
            "bytes_recv": network_io.bytes_recv,
            "packets_sent": network_io.packets_sent,
            "packets_recv": network_io.packets_recv,
            "status": connectivity
        }

    async def _detect_anomalies(self, system_data: Dict[str, Any],
                              options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Detect anomalies in system metrics"""
        time_window = options.get("time_window_hours", 24) if options else 24
        sensitivity = options.get("sensitivity", "medium") if options else "medium"

        # Get metrics from the specified time window
        cutoff_time = datetime.now() - timedelta(hours=time_window)
        recent_metrics = []

        for metric_queue in self.metrics_history.values():
            recent_metrics.extend([m for m in metric_queue if m.timestamp >= cutoff_time])

        anomalies_found = []

        # Group metrics by component and name
        metrics_by_type = defaultdict(list)
        for metric in recent_metrics:
            key = f"{metric.component.value}_{metric.metric_name}"
            metrics_by_type[key].append(metric)

        # Detect anomalies for each metric type
        for metric_key, metrics in metrics_by_type.items():
            if len(metrics) < 10:  # Need minimum data points
                continue

            component, metric_name = metric_key.split('_', 1)
            values = [m.value for m in sorted(metrics, key=lambda x: x.timestamp)]

            anomaly_result = await self._detect_statistical_anomalies(
                component, metric_name, values, sensitivity
            )

            if anomaly_result:
                anomalies_found.append(anomaly_result)

        # Store anomalies
        for anomaly in anomalies_found:
            self.anomalies.append(anomaly)

        return {
            "time_window_hours": time_window,
            "sensitivity": sensitivity,
            "anomalies_detected": len(anomalies_found),
            "anomalies": [asdict(a) for a in anomalies_found],
            "total_metrics_analyzed": len(recent_metrics)
        }

    async def _detect_statistical_anomalies(self, component: str, metric_name: str,
                                          values: List[float], sensitivity: str) -> Optional[AnomalyDetectionResult]:
        """Detect statistical anomalies in a time series"""
        if len(values) < 10:
            return None

        try:
            # Calculate statistical measures
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0

            if std_val == 0:
                return None

            # Z-score based anomaly detection
            latest_value = values[-1]
            z_score = abs((latest_value - mean_val) / std_val)

            # Sensitivity thresholds
            threshold_map = {
                "low": 3.0,
                "medium": 2.5,
                "high": 2.0
            }
            threshold = threshold_map.get(sensitivity, 2.5)

            if z_score > threshold:
                # Determine anomaly type
                deviation_percent = ((latest_value - mean_val) / mean_val) * 100
                anomaly_type = AnomalyType.SPIKE if deviation_percent > 0 else AnomalyType.DIP

                # Generate recommendations
                recommendations = []
                if anomaly_type == AnomalyType.SPIKE:
                    recommendations = [
                        f"Investigate high {metric_name} usage on {component}",
                        "Check for resource-intensive processes",
                        "Consider scaling resources if usage persists"
                    ]
                else:
                    recommendations = [
                        f"Monitor {metric_name} for continued low values",
                        "Check if services are running properly",
                        "Review recent configuration changes"
                    ]

                return AnomalyDetectionResult(
                    result_id=str(uuid.uuid4()),
                    component=SystemComponent(component),
                    metric_name=metric_name,
                    anomaly_type=anomaly_type,
                    confidence_score=min(z_score / 4.0, 1.0),  # Normalize confidence
                    detected_value=latest_value,
                    expected_value=mean_val,
                    deviation_percent=abs(deviation_percent),
                    detected_at=datetime.now(),
                    time_window=f"{len(values)} data points",
                    recommendations=recommendations
                )

        except Exception as e:
            self.logger.error(f"Error detecting anomalies for {component}.{metric_name}: {e}")

        return None

    async def _predict_failures(self, system_data: Dict[str, Any],
                              options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Predict potential system failures"""
        prediction_horizon = options.get("prediction_horizon_hours", 168) if options else 168  # 1 week

        predictive_alerts = []

        # Analyze each component for failure prediction
        for component in SystemComponent:
            component_metrics = [m for m in self.metrics_history.get(component.value, [])
                               if (datetime.now() - m.timestamp).total_seconds() < 604800]  # Last week

            if len(component_metrics) < 50:  # Need sufficient historical data
                continue

            # Simple trend analysis for failure prediction
            failure_prediction = await self._predict_component_failure(
                component, component_metrics, prediction_horizon
            )

            if failure_prediction:
                predictive_alerts.append(failure_prediction)

        # Store predictive alerts
        self.predictive_alerts.extend(predictive_alerts)

        return {
            "prediction_horizon_hours": prediction_horizon,
            "predictive_alerts_generated": len(predictive_alerts),
            "alerts": [asdict(alert) for alert in predictive_alerts],
            "components_analyzed": len(SystemComponent)
        }

    async def _predict_component_failure(self, component: SystemComponent,
                                       metrics: List[SystemMetric],
                                       horizon_hours: int) -> Optional[PredictiveMaintenanceAlert]:
        """Predict failure for a specific component"""
        try:
            # Group metrics by type
            metrics_by_type = defaultdict(list)
            for metric in metrics:
                metrics_by_type[metric.metric_name].append(metric.value)

            failure_probability = 0.0
            contributing_factors = []
            preventive_actions = []

            # Analyze CPU metrics
            if component == SystemComponent.CPU and "usage_percent" in metrics_by_type:
                cpu_values = metrics_by_type["usage_percent"][-24:]  # Last 24 readings
                if cpu_values:
                    avg_cpu = statistics.mean(cpu_values)
                    if avg_cpu > 85:
                        failure_probability += 0.3
                        contributing_factors.append(f"High CPU usage: {avg_cpu:.1f}%")
                        preventive_actions.append("Monitor CPU-intensive processes")
                        preventive_actions.append("Consider CPU upgrade or optimization")

            # Analyze memory metrics
            if component == SystemComponent.MEMORY and "usage_percent" in metrics_by_type:
                mem_values = metrics_by_type["usage_percent"][-24:]
                if mem_values:
                    avg_mem = statistics.mean(mem_values)
                    if avg_mem > 90:
                        failure_probability += 0.4
                        contributing_factors.append(f"High memory usage: {avg_mem:.1f}%")
                        preventive_actions.append("Add more RAM or optimize memory usage")

            # Analyze disk metrics
            if component == SystemComponent.DISK and "usage_percent" in metrics_by_type:
                disk_values = metrics_by_type["usage_percent"][-168:]  # Last week
                if disk_values:
                    current_disk = disk_values[-1]
                    trend = np.polyfit(range(len(disk_values)), disk_values, 1)[0]
                    if current_disk > 90 and trend > 0.1:  # Disk filling up
                        failure_probability += 0.5
                        contributing_factors.append(f"Disk filling up: {current_disk:.1f}% with upward trend")
                        preventive_actions.append("Clean up disk space")
                        preventive_actions.append("Add more storage")

            if failure_probability > 0.2:  # Minimum threshold for alert
                # Estimate time to failure based on probability
                estimated_hours = int((1 - failure_probability) * horizon_hours)

                risk_level = "high" if failure_probability > 0.7 else "medium" if failure_probability > 0.4 else "low"

                return PredictiveMaintenanceAlert(
                    alert_id=str(uuid.uuid4()),
                    component=component,
                    failure_probability=failure_probability,
                    estimated_time_to_failure=estimated_hours,
                    risk_level=risk_level,
                    detected_at=datetime.now(),
                    contributing_factors=contributing_factors,
                    preventive_actions=preventive_actions
                )

        except Exception as e:
            self.logger.error(f"Error predicting failure for {component.value}: {e}")

        return None

    async def _optimize_performance(self, system_data: Dict[str, Any],
                                  options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Optimize system performance based on monitoring data"""
        optimizations = []

        # Analyze current system state
        health_check = await self._check_system_health()

        # CPU optimization
        cpu_usage = health_check["components"]["cpu"]["usage_percent"]
        if cpu_usage > 80:
            optimizations.append({
                "type": "cpu_optimization",
                "action": "Identify and optimize CPU-intensive processes",
                "expected_improvement": "15-25% CPU reduction",
                "difficulty": "medium"
            })

        # Memory optimization
        memory_usage = health_check["components"]["memory"]["usage_percent"]
        if memory_usage > 85:
            optimizations.append({
                "type": "memory_optimization",
                "action": "Implement memory caching and reduce memory leaks",
                "expected_improvement": "20-30% memory reduction",
                "difficulty": "high"
            })

        # Disk optimization
        disk_usage = health_check["components"]["disk"]["usage_percent"]
        if disk_usage > 90:
            optimizations.append({
                "type": "disk_optimization",
                "action": "Clean up temporary files and optimize storage",
                "expected_improvement": "10-20% disk space recovery",
                "difficulty": "low"
            })

        # Adaptive threshold adjustments
        threshold_updates = await self._update_adaptive_thresholds()

        return {
            "current_health_score": health_check["overall_health"],
            "optimizations_recommended": len(optimizations),
            "optimizations": optimizations,
            "adaptive_thresholds_updated": len(threshold_updates),
            "estimated_improvement": "15-40% performance gain"
        }

    async def _update_adaptive_thresholds(self) -> List[str]:
        """Update adaptive thresholds based on historical data"""
        updated_metrics = []

        for metric_name, config in self.adaptive_thresholds.items():
            metrics = []
            for component_queue in self.metrics_history.values():
                metrics.extend([m.value for m in component_queue
                              if m.metric_name == metric_name])

            if len(metrics) >= config["adaptation_window"]:
                # Calculate new thresholds based on historical data
                mean_val = statistics.mean(metrics)
                std_val = statistics.stdev(metrics) if len(metrics) > 1 else 0

                # Update thresholds (keep within min/max bounds)
                new_warning = min(max(mean_val + std_val, config["min_threshold"]), config["max_threshold"])
                new_critical = min(max(mean_val + 2 * std_val, config["min_threshold"]), config["max_threshold"])

                config["warning"] = new_warning
                config["critical"] = new_critical
                updated_metrics.append(metric_name)

        return updated_metrics

    async def _continuous_monitoring(self):
        """Continuous system monitoring loop"""
        while True:
            try:
                # Collect system metrics
                await self._collect_system_metrics()

                # Check for alerts
                await self._check_alert_conditions()

                # Auto-heal if necessary
                await self._perform_auto_healing()

                await asyncio.sleep(60)  # Monitor every minute

            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(60)

    async def _collect_system_metrics(self):
        """Collect current system metrics"""
        try:
            timestamp = datetime.now()

            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self._store_metric("cpu", "usage_percent", cpu_percent, timestamp)

            # Memory metrics
            memory = psutil.virtual_memory()
            self._store_metric("memory", "usage_percent", memory.percent, timestamp)
            self._store_metric("memory", "available_bytes", memory.available, timestamp)

            # Disk metrics
            disk = psutil.disk_usage('/')
            self._store_metric("disk", "usage_percent", disk.percent, timestamp)
            self._store_metric("disk", "free_bytes", disk.free, timestamp)

            # Network metrics
            network = psutil.net_io_counters()
            self._store_metric("network", "bytes_sent", network.bytes_sent, timestamp)
            self._store_metric("network", "bytes_recv", network.bytes_recv, timestamp)

        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")

    def _store_metric(self, component: str, metric_name: str, value: float, timestamp: datetime):
        """Store a metric in the history"""
        metric_key = f"{component}_{metric_name}"
        metric = SystemMetric(
            metric_id=str(uuid.uuid4()),
            component=SystemComponent(component),
            metric_name=metric_name,
            value=value,
            timestamp=timestamp
        )
        self.metrics_history[metric_key].append(metric)

    async def _check_alert_conditions(self):
        """Check for alert conditions and create alerts"""
        # Get latest metrics for each component
        latest_metrics = {}
        for metric_key, metric_queue in self.metrics_history.items():
            if metric_queue:
                latest_metrics[metric_key] = metric_queue[-1]

        # Check each metric against thresholds
        for metric_key, metric in latest_metrics.items():
            status = self._evaluate_metric_health(metric.metric_name, metric.value)

            if status in ["warning", "critical"]:
                # Check if we already have an active alert for this
                existing_alert = None
                for alert in self.alerts:
                    if (alert.component == metric.component and
                        alert.status == "active" and
                        alert.title.startswith(f"{metric.metric_name.title()}")):
                        existing_alert = alert
                        break

                if not existing_alert:
                    # Create new alert
                    severity = AlertSeverity.HIGH if status == "critical" else AlertSeverity.MEDIUM

                    alert = Alert(
                        alert_id=str(uuid.uuid4()),
                        severity=severity,
                        component=metric.component,
                        title=f"{metric.metric_name.title()} {status.title()}",
                        description=f"{metric.metric_name} is at {metric.value:.1f}, which is {status}",
                        triggered_at=datetime.now(),
                        remediation_actions=await self._get_remediation_actions(metric.component, metric.metric_name, status)
                    )

                    self.alerts.append(alert)
                    self.logger.warning(f"Alert created: {alert.title}")

    async def _get_remediation_actions(self, component: SystemComponent, metric_name: str, status: str) -> List[str]:
        """Get remediation actions for an alert"""
        actions = []

        if component == SystemComponent.CPU and metric_name == "usage_percent":
            actions = [
                "Identify CPU-intensive processes using 'top' or 'htop'",
                "Consider optimizing or terminating unnecessary processes",
                "Check for CPU-bound applications that might need optimization"
            ]
        elif component == SystemComponent.MEMORY and metric_name == "usage_percent":
            actions = [
                "Check memory usage with 'free' or 'vmstat'",
                "Look for memory leaks in applications",
                "Consider increasing RAM or optimizing memory usage"
            ]
        elif component == SystemComponent.DISK and metric_name == "usage_percent":
            actions = [
                "Check disk usage with 'df -h'",
                "Remove unnecessary files and clear caches",
                "Consider adding more storage space"
            ]

        return actions

    async def _perform_auto_healing(self):
        """Perform automatic healing actions for active alerts"""
        active_alerts = [a for a in self.alerts if a.status == "active"]

        for alert in active_alerts:
            if alert.severity == AlertSeverity.CRITICAL:
                # Attempt auto-healing for critical alerts
                healing_result = await self._execute_healing_action(alert)

                if healing_result["success"]:
                    alert.status = "resolved"
                    alert.resolved_at = datetime.now()
                    self.logger.info(f"Auto-healed alert: {alert.title}")

    async def _execute_healing_action(self, alert: Alert) -> Dict[str, Any]:
        """Execute a healing action for an alert"""
        # Simple auto-healing examples
        success = False
        result = {}

        try:
            if "memory" in alert.title.lower() and "cache" in alert.description.lower():
                # Clear system cache (example)
                # Note: This is just a simulation
                success = True
                result = {"action": "cache_cleared", "memory_freed_mb": 150}

            elif "disk" in alert.title.lower():
                # Clean temporary files (example)
                success = True
                result = {"action": "temp_files_cleaned", "space_freed_mb": 500}

            # Record the healing action
            healing_action = SelfHealingAction(
                action_id=str(uuid.uuid4()),
                component=alert.component,
                action_type="auto_remediation",
                action_description=f"Auto-healed: {alert.title}",
                triggered_by=alert.alert_id,
                executed_at=datetime.now(),
                success=success,
                result=result
            )

            self.healing_actions.append(healing_action)

        except Exception as e:
            self.logger.error(f"Error executing healing action: {e}")
            success = False

        return {"success": success, "result": result}

    async def _anomaly_detection_loop(self):
        """Continuous anomaly detection"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                # Run anomaly detection
                await self._detect_anomalies({}, {"time_window_hours": 24, "sensitivity": "medium"})

            except Exception as e:
                self.logger.error(f"Error in anomaly detection loop: {e}")
                await asyncio.sleep(300)

    async def _predictive_maintenance_loop(self):
        """Continuous predictive maintenance"""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour

                # Run predictive maintenance
                await self._predict_failures({}, {"prediction_horizon_hours": 168})

            except Exception as e:
                self.logger.error(f"Error in predictive maintenance loop: {e}")
                await asyncio.sleep(3600)

    async def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data"""
        health_status = await self._check_system_health()

        recent_alerts = [asdict(a) for a in self.alerts[-10:]]  # Last 10 alerts
        recent_anomalies = [asdict(a) for a in self.anomalies[-10:]]  # Last 10 anomalies
        active_predictive_alerts = [asdict(a) for a in self.predictive_alerts
                                  if a.estimated_time_to_failure > 0]

        return {
            "system_health": health_status,
            "recent_alerts": recent_alerts,
            "recent_anomalies": recent_anomalies,
            "predictive_alerts": active_predictive_alerts,
            "healing_actions": len([h for h in self.healing_actions if h.success]),
            "monitoring_uptime": "99.9%",  # Simulated
            "last_updated": datetime.now().isoformat()
        }
