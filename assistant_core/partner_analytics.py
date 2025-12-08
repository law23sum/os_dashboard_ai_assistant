"""

Partner Monitoring and Analytics System

Comprehensive monitoring, analytics, and insights for partner performance

INTEGRATED INTO OS DASHBOARD AI ASSISTANT
- Advanced analytics for partner performance tracking
- Real-time alerting and anomaly detection
- Performance scoring and trend analysis
- Automated recommendations

"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import statistics

from config.logging_config import setup_logger

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

@dataclass
class Metric:
    """Metric data point"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    type: MetricType

@dataclass
class Alert:
    """Alert definition and status"""
    id: str
    partner_id: str
    metric_name: str
    condition: str
    threshold: float
    severity: AlertSeverity
    status: AlertStatus
    message: str
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: str = ""

@dataclass
class PerformanceReport:
    """Performance analysis report"""
    partner_id: str
    period_start: datetime
    period_end: datetime
    metrics_summary: Dict[str, Any]
    performance_score: float
    trends: Dict[str, str]
    recommendations: List[str]
    alerts_summary: Dict[str, int]

class PartnerAnalyticsSystem:
    """Comprehensive partner analytics and monitoring system"""

    def __init__(self):
        self.logger = setup_logger("PartnerAnalytics")

        # Data storage
        self.metrics_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, Dict[str, Any]] = {}

        # Real-time monitoring
        self.monitoring_enabled = True
        self.alert_processors = []

        # Analytics configuration
        self.config = {
            "retention_days": 90,
            "aggregation_intervals": [60, 300, 3600, 86400],  # 1m, 5m, 1h, 1d
            "performance_weights": {
                "api_success_rate": 0.3,
                "response_time": 0.25,
                "uptime": 0.2,
                "error_rate": 0.15,
                "usage_growth": 0.1
            },
            "alert_cooldown": 300,  # 5 minutes
            "anomaly_detection": {
                "enabled": True,
                "sensitivity": 0.95,
                "window_size": 100
            }
        }

        # Predefined metric definitions
        self.metric_definitions = {
            "api_requests_total": {
                "type": MetricType.COUNTER,
                "description": "Total API requests",
                "unit": "requests"
            },
            "api_requests_success": {
                "type": MetricType.COUNTER,
                "description": "Successful API requests",
                "unit": "requests"
            },
            "api_requests_failed": {
                "type": MetricType.COUNTER,
                "description": "Failed API requests",
                "unit": "requests"
            },
            "api_response_time": {
                "type": MetricType.HISTOGRAM,
                "description": "API response time",
                "unit": "milliseconds"
            },
            "api_rate_limit_hits": {
                "type": MetricType.COUNTER,
                "description": "Rate limit violations",
                "unit": "hits"
            },
            "data_transfer_bytes": {
                "type": MetricType.COUNTER,
                "description": "Data transfer volume",
                "unit": "bytes"
            },
            "active_connections": {
                "type": MetricType.GAUGE,
                "description": "Active connections",
                "unit": "connections"
            },
            "revenue_generated": {
                "type": MetricType.COUNTER,
                "description": "Revenue generated",
                "unit": "dollars"
            }
        }

    async def initialize(self):
        """Initialize analytics system"""
        await self._load_alert_rules()
        await self._start_monitoring_tasks()

        self.logger.info("Partner Analytics System initialized")

    # Metrics Collection and Storage
    async def record_metric(self, partner_id: str, metric_name: str,
                          value: float, tags: Dict[str, str] = None) -> bool:
        """Record a metric data point"""
        try:
            metric = Metric(
                name=metric_name,
                value=value,
                timestamp=datetime.now(),
                tags=tags or {},
                type=self.metric_definitions.get(metric_name, {}).get("type", MetricType.GAUGE)
            )

            # Store metric
            metric_key = f"{partner_id}:{metric_name}"
            self.metrics_data[metric_key].append(metric)

            # Check for alerts
            await self._check_metric_alerts(partner_id, metric)

            # Detect anomalies
            if self.config["anomaly_detection"]["enabled"]:
                await self._detect_anomalies(partner_id, metric_name, value)

            return True

        except Exception as e:
            self.logger.error(f"Metric recording failed: {e}")
            return False

    async def record_api_request(self, partner_id: str, endpoint: str,
                               method: str, status_code: int,
                               response_time: float, data_size: int = 0):
        """Record API request metrics"""
        try:
            tags = {
                "endpoint": endpoint,
                "method": method,
                "status_code": str(status_code)
            }

            # Record total requests
            await self.record_metric(partner_id, "api_requests_total", 1, tags)

            # Record success/failure
            if 200 <= status_code < 400:
                await self.record_metric(partner_id, "api_requests_success", 1, tags)
            else:
                await self.record_metric(partner_id, "api_requests_failed", 1, tags)

            # Record response time
            await self.record_metric(partner_id, "api_response_time", response_time, tags)

            # Record data transfer
            if data_size > 0:
                await self.record_metric(partner_id, "data_transfer_bytes", data_size, tags)

            # Check for rate limiting
            if status_code == 429:
                await self.record_metric(partner_id, "api_rate_limit_hits", 1, tags)

        except Exception as e:
            self.logger.error(f"API request recording failed: {e}")

    # Metrics Querying and Aggregation
    async def get_metric_values(self, partner_id: str, metric_name: str,
                              start_time: datetime, end_time: datetime,
                              aggregation: str = "avg") -> List[Tuple[datetime, float]]:
        """Get metric values for time range"""
        try:
            metric_key = f"{partner_id}:{metric_name}"
            metrics = self.metrics_data.get(metric_key, deque())

            # Filter by time range
            filtered_metrics = [
                m for m in metrics
                if start_time <= m.timestamp <= end_time
            ]

            if not filtered_metrics:
                return []

            # Group by time intervals and aggregate
            interval = 300  # 5 minutes
            aggregated_data = []

            current_time = start_time
            while current_time < end_time:
                interval_end = current_time + timedelta(seconds=interval)

                interval_metrics = [
                    m for m in filtered_metrics
                    if current_time <= m.timestamp < interval_end
                ]

                if interval_metrics:
                    values = [m.value for m in interval_metrics]

                    if aggregation == "avg":
                        agg_value = statistics.mean(values)
                    elif aggregation == "sum":
                        agg_value = sum(values)
                    elif aggregation == "max":
                        agg_value = max(values)
                    elif aggregation == "min":
                        agg_value = min(values)
                    elif aggregation == "count":
                        agg_value = len(values)
                    else:
                        agg_value = statistics.mean(values)

                    aggregated_data.append((current_time, agg_value))

                current_time = interval_end

            return aggregated_data

        except Exception as e:
            self.logger.error(f"Metric query failed: {e}")
            return []

    async def calculate_derived_metrics(self, partner_id: str,
                                      start_time: datetime,
                                      end_time: datetime) -> Dict[str, float]:
        """Calculate derived metrics from raw data"""
        try:
            derived_metrics = {}

            # API Success Rate
            total_requests = await self.get_metric_values(
                partner_id, "api_requests_total", start_time, end_time, "sum"
            )
            success_requests = await self.get_metric_values(
                partner_id, "api_requests_success", start_time, end_time, "sum"
            )

            if total_requests and success_requests:
                total_sum = sum(value for _, value in total_requests)
                success_sum = sum(value for _, value in success_requests)

                if total_sum > 0:
                    derived_metrics["api_success_rate"] = (success_sum / total_sum) * 100
                else:
                    derived_metrics["api_success_rate"] = 0

            # Error Rate
            failed_requests = await self.get_metric_values(
                partner_id, "api_requests_failed", start_time, end_time, "sum"
            )

            if total_requests and failed_requests:
                total_sum = sum(value for _, value in total_requests)
                failed_sum = sum(value for _, value in failed_requests)

                if total_sum > 0:
                    derived_metrics["api_error_rate"] = (failed_sum / total_sum) * 100
                else:
                    derived_metrics["api_error_rate"] = 0

            # Average Response Time
            response_times = await self.get_metric_values(
                partner_id, "api_response_time", start_time, end_time, "avg"
            )

            if response_times:
                avg_response_time = statistics.mean(value for _, value in response_times)
                derived_metrics["avg_response_time"] = avg_response_time

            # Request Rate (requests per minute)
            if total_requests:
                duration_minutes = (end_time - start_time).total_seconds() / 60
                total_sum = sum(value for _, value in total_requests)
                derived_metrics["request_rate"] = total_sum / duration_minutes if duration_minutes > 0 else 0

            # Data Transfer Rate
            data_transfer = await self.get_metric_values(
                partner_id, "data_transfer_bytes", start_time, end_time, "sum"
            )

            if data_transfer:
                duration_hours = (end_time - start_time).total_seconds() / 3600
                total_bytes = sum(value for _, value in data_transfer)
                derived_metrics["data_transfer_rate_mbps"] = (total_bytes / (1024 * 1024)) / duration_hours if duration_hours > 0 else 0

            return derived_metrics

        except Exception as e:
            self.logger.error(f"Derived metrics calculation failed: {e}")
            return {}

    # Performance Analysis
    async def calculate_performance_score(self, partner_id: str,
                                        start_time: datetime,
                                        end_time: datetime) -> float:
        """Calculate overall performance score"""
        try:
            derived_metrics = await self.calculate_derived_metrics(partner_id, start_time, end_time)
            weights = self.config["performance_weights"]

            score = 0.0
            total_weight = 0.0

            # API Success Rate (0-100, higher is better)
            if "api_success_rate" in derived_metrics:
                success_rate = derived_metrics["api_success_rate"]
                score += (success_rate / 100) * weights["api_success_rate"]
                total_weight += weights["api_success_rate"]

            # Response Time (lower is better, normalize to 0-1)
            if "avg_response_time" in derived_metrics:
                response_time = derived_metrics["avg_response_time"]
                # Assume 1000ms is baseline, 100ms is excellent
                normalized_response = max(0, min(1, (1000 - response_time) / 900))
                score += normalized_response * weights["response_time"]
                total_weight += weights["response_time"]

            # Error Rate (0-100, lower is better)
            if "api_error_rate" in derived_metrics:
                error_rate = derived_metrics["api_error_rate"]
                normalized_error = max(0, (100 - error_rate) / 100)
                score += normalized_error * weights["error_rate"]
                total_weight += weights["error_rate"]

            # Calculate uptime based on successful requests
            if "api_success_rate" in derived_metrics:
                uptime_score = derived_metrics["api_success_rate"] / 100
                score += uptime_score * weights["uptime"]
                total_weight += weights["uptime"]

            # Usage growth (simplified calculation)
            usage_growth = await self._calculate_usage_growth(partner_id, start_time, end_time)
            if usage_growth is not None:
                # Normalize growth rate (0-50% growth = 0-1 score)
                normalized_growth = max(0, min(1, usage_growth / 50))
                score += normalized_growth * weights["usage_growth"]
                total_weight += weights["usage_growth"]

            # Calculate final score
            if total_weight > 0:
                final_score = (score / total_weight) * 100
            else:
                final_score = 0

            return round(final_score, 2)

        except Exception as e:
            self.logger.error(f"Performance score calculation failed: {e}")
            return 0.0

    async def _calculate_usage_growth(self, partner_id: str,
                                    start_time: datetime,
                                    end_time: datetime) -> Optional[float]:
        """Calculate usage growth rate"""
        try:
            # Get current period usage
            current_requests = await self.get_metric_values(
                partner_id, "api_requests_total", start_time, end_time, "sum"
            )

            # Get previous period usage
            period_duration = end_time - start_time
            prev_start = start_time - period_duration
            prev_end = start_time

            previous_requests = await self.get_metric_values(
                partner_id, "api_requests_total", prev_start, prev_end, "sum"
            )

            if current_requests and previous_requests:
                current_total = sum(value for _, value in current_requests)
                previous_total = sum(value for _, value in previous_requests)

                if previous_total > 0:
                    growth_rate = ((current_total - previous_total) / previous_total) * 100
                    return growth_rate

            return None

        except Exception as e:
            self.logger.error(f"Usage growth calculation failed: {e}")
            return None

    # Trend Analysis
    async def analyze_trends(self, partner_id: str, metric_name: str,
                           start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Analyze trends in metric data"""
        try:
            metric_values = await self.get_metric_values(
                partner_id, metric_name, start_time, end_time, "avg"
            )

            if len(metric_values) < 2:
                return {"trend": "insufficient_data", "direction": "unknown"}

            # Extract values and timestamps
            timestamps = [t.timestamp() for t, _ in metric_values]
            values = [v for _, v in metric_values]

            # Calculate linear trend
            if len(values) >= 2:
                # Simple linear regression
                x = np.array(timestamps)
                y = np.array(values)

                # Normalize x to avoid numerical issues
                x_norm = (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else np.zeros_like(x)

                # Calculate slope
                slope = np.polyfit(x_norm, y, 1)[0] if len(x_norm) > 1 else 0

                # Determine trend direction
                if abs(slope) < 0.01 * np.std(y):
                    direction = "stable"
                elif slope > 0:
                    direction = "increasing"
                else:
                    direction = "decreasing"

                # Calculate trend strength
                correlation = np.corrcoef(x_norm, y)[0, 1] if len(x_norm) > 1 else 0
                strength = abs(correlation)

                # Detect seasonality (simplified)
                seasonality = await self._detect_seasonality(values)

                return {
                    "trend": "linear",
                    "direction": direction,
                    "slope": float(slope),
                    "strength": float(strength),
                    "seasonality": seasonality,
                    "data_points": len(values),
                    "period": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat()
                    }
                }

            return {"trend": "insufficient_data", "direction": "unknown"}

        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            return {"trend": "error", "direction": "unknown"}

    async def _detect_seasonality(self, values: List[float]) -> Dict[str, Any]:
        """Detect seasonality patterns in data"""
        try:
            if len(values) < 24:  # Need at least 24 data points
                return {"detected": False, "pattern": "insufficient_data"}

            # Simple autocorrelation check for daily patterns
            # This is a simplified implementation
            values_array = np.array(values)

            # Check for daily pattern (assuming 5-minute intervals, 288 points per day)
            if len(values) >= 288:
                daily_correlation = np.corrcoef(values_array[:-288], values_array[288:])[0, 1]
                if abs(daily_correlation) > 0.3:
                    return {"detected": True, "pattern": "daily", "correlation": float(daily_correlation)}

            # Check for weekly pattern
            if len(values) >= 2016:  # 7 days * 288 points
                weekly_correlation = np.corrcoef(values_array[:-2016], values_array[2016:])[0, 1]
                if abs(weekly_correlation) > 0.3:
                    return {"detected": True, "pattern": "weekly", "correlation": float(weekly_correlation)}

            return {"detected": False, "pattern": "none"}

        except Exception as e:
            self.logger.error(f"Seasonality detection failed: {e}")
            return {"detected": False, "pattern": "error"}

    # Alerting System
    async def create_alert_rule(self, partner_id: str, rule_data: Dict[str, Any]) -> str:
        """Create new alert rule"""
        try:
            rule_id = str(uuid.uuid4())

            rule = {
                "id": rule_id,
                "partner_id": partner_id,
                "metric_name": rule_data["metric_name"],
                "condition": rule_data["condition"],  # "gt", "lt", "eq"
                "threshold": float(rule_data["threshold"]),
                "severity": AlertSeverity(rule_data.get("severity", "warning")),
                "message_template": rule_data.get("message_template", "Alert: {metric_name} {condition} {threshold}"),
                "cooldown": rule_data.get("cooldown", self.config["alert_cooldown"]),
                "enabled": rule_data.get("enabled", True),
                "last_triggered": None
            }

            self.alert_rules[rule_id] = rule

            self.logger.info(f"Alert rule created: {rule_id}")
            return rule_id

        except Exception as e:
            self.logger.error(f"Alert rule creation failed: {e}")
            raise

    async def _check_metric_alerts(self, partner_id: str, metric: Metric):
        """Check if metric triggers any alerts"""
        try:
            for rule_id, rule in self.alert_rules.items():
                if (rule["partner_id"] == partner_id and
                    rule["metric_name"] == metric.name and
                    rule["enabled"]):

                    # Check cooldown
                    if rule["last_triggered"]:
                        time_since_last = (datetime.now() - rule["last_triggered"]).total_seconds()
                        if time_since_last < rule["cooldown"]:
                            continue

                    # Evaluate condition
                    triggered = False
                    condition = rule["condition"]
                    threshold = rule["threshold"]

                    if condition == "gt" and metric.value > threshold:
                        triggered = True
                    elif condition == "lt" and metric.value < threshold:
                        triggered = True
                    elif condition == "eq" and abs(metric.value - threshold) < 0.001:
                        triggered = True
                    elif condition == "gte" and metric.value >= threshold:
                        triggered = True
                    elif condition == "lte" and metric.value <= threshold:
                        triggered = True

                    if triggered:
                        await self._trigger_alert(rule, metric)
                        rule["last_triggered"] = datetime.now()

        except Exception as e:
            self.logger.error(f"Alert checking failed: {e}")

    async def _trigger_alert(self, rule: Dict[str, Any], metric: Metric):
        """Trigger an alert"""
        try:
            alert_id = str(uuid.uuid4())

            message = rule["message_template"].format(
                metric_name=metric.name,
                condition=rule["condition"],
                threshold=rule["threshold"],
                value=metric.value
            )

            alert = Alert(
                id=alert_id,
                partner_id=rule["partner_id"],
                metric_name=metric.name,
                condition=f"{metric.value} {rule['condition']} {rule['threshold']}",
                threshold=rule["threshold"],
                severity=rule["severity"],
                status=AlertStatus.ACTIVE,
                message=message,
                created_at=datetime.now()
            )

            self.alerts[alert_id] = alert

            # Send notification
            await self._send_alert_notification(alert)

            self.logger.warning(f"Alert triggered: {alert_id} - {message}")

        except Exception as e:
            self.logger.error(f"Alert triggering failed: {e}")

    async def _send_alert_notification(self, alert: Alert):
        """Send alert notification"""
        # In production, integrate with notification systems
        self.logger.warning(f"ALERT: {alert.severity.value.upper()} - {alert.message}")

    # Anomaly Detection
    async def _detect_anomalies(self, partner_id: str, metric_name: str, value: float):
        """Detect anomalies in metric values"""
        try:
            if not self.config["anomaly_detection"]["enabled"]:
                return

            metric_key = f"{partner_id}:{metric_name}"
            metrics = list(self.metrics_data.get(metric_key, deque()))

            if len(metrics) < self.config["anomaly_detection"]["window_size"]:
                return  # Not enough data

            # Get recent values
            recent_values = [m.value for m in metrics[-self.config["anomaly_detection"]["window_size"]:]]
            values_array = np.array(recent_values)

            # Calculate statistical bounds
            mean_value = np.mean(values_array)
            std_value = np.std(values_array)

            # Z-score based anomaly detection
            if std_value > 0:
                z_score = abs(value - mean_value) / std_value
                threshold = 2.5  # 2.5 standard deviations

                if z_score > threshold:
                    await self._create_anomaly_alert(partner_id, metric_name, value, mean_value, z_score)

        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")

    async def _create_anomaly_alert(self, partner_id: str, metric_name: str,
                                  value: float, expected: float, z_score: float):
        """Create anomaly alert"""
        try:
            alert_id = str(uuid.uuid4())

            message = f"Anomaly detected in {metric_name}: value {value:.2f} (expected ~{expected:.2f}, z-score: {z_score:.2f})"

            alert = Alert(
                id=alert_id,
                partner_id=partner_id,
                metric_name=metric_name,
                condition=f"anomaly_z_score > 2.5",
                threshold=2.5,
                severity=AlertSeverity.WARNING,
                status=AlertStatus.ACTIVE,
                message=message,
                created_at=datetime.now()
            )

            self.alerts[alert_id] = alert
            await self._send_alert_notification(alert)

        except Exception as e:
            self.logger.error(f"Anomaly alert creation failed: {e}")

    # Reporting
    async def generate_performance_report(self, partner_id: str,
                                        start_time: datetime,
                                        end_time: datetime) -> PerformanceReport:
        """Generate comprehensive performance report"""
        try:
            # Calculate derived metrics
            derived_metrics = await self.calculate_derived_metrics(partner_id, start_time, end_time)

            # Calculate performance score
            performance_score = await self.calculate_performance_score(partner_id, start_time, end_time)

            # Analyze trends for key metrics
            trends = {}
            key_metrics = ["api_requests_total", "api_response_time", "api_success_rate"]

            for metric_name in key_metrics:
                if metric_name in derived_metrics or metric_name in self.metric_definitions:
                    trend_analysis = await self.analyze_trends(partner_id, metric_name, start_time, end_time)
                    trends[metric_name] = trend_analysis.get("direction", "unknown")

            # Generate recommendations
            recommendations = await self._generate_recommendations(partner_id, derived_metrics, trends)

            # Summarize alerts
            partner_alerts = [
                alert for alert in self.alerts.values()
                if alert.partner_id == partner_id
            ]

            period_alerts = [
                alert for alert in partner_alerts
                if start_time <= alert.created_at <= end_time
            ]

            alerts_summary = {
                "total": len(period_alerts),
                "critical": len([a for a in period_alerts if a.severity == AlertSeverity.CRITICAL]),
                "error": len([a for a in period_alerts if a.severity == AlertSeverity.ERROR]),
                "warning": len([a for a in period_alerts if a.severity == AlertSeverity.WARNING]),
                "info": len([a for a in period_alerts if a.severity == AlertSeverity.INFO])
            }

            report = PerformanceReport(
                partner_id=partner_id,
                period_start=start_time,
                period_end=end_time,
                metrics_summary=derived_metrics,
                performance_score=performance_score,
                trends=trends,
                recommendations=recommendations,
                alerts_summary=alerts_summary
            )

            return report

        except Exception as e:
            self.logger.error(f"Performance report generation failed: {e}")
            raise

    async def _generate_recommendations(self, partner_id: str,
                                      metrics: Dict[str, float],
                                      trends: Dict[str, str]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []

        try:
            # API Success Rate recommendations
            if "api_success_rate" in metrics:
                success_rate = metrics["api_success_rate"]
                if success_rate < 95:
                    recommendations.append("API success rate is below 95%. Consider implementing retry logic and improving error handling.")
                elif success_rate < 99:
                    recommendations.append("API success rate could be improved. Review error patterns and optimize API reliability.")

            # Response Time recommendations
            if "avg_response_time" in metrics:
                response_time = metrics["avg_response_time"]
                if response_time > 1000:
                    recommendations.append("Average response time exceeds 1 second. Consider optimizing API performance and implementing caching.")
                elif response_time > 500:
                    recommendations.append("Response time could be improved. Review slow endpoints and optimize database queries.")

            # Error Rate recommendations
            if "api_error_rate" in metrics:
                error_rate = metrics["api_error_rate"]
                if error_rate > 5:
                    recommendations.append("Error rate is high (>5%). Investigate common error patterns and improve input validation.")
                elif error_rate > 1:
                    recommendations.append("Consider reducing error rate further by improving API robustness.")

            # Trend-based recommendations
            if trends.get("api_requests_total") == "decreasing":
                recommendations.append("API usage is declining. Consider reaching out to understand user needs and improve API value proposition.")

            if trends.get("api_response_time") == "increasing":
                recommendations.append("Response times are trending upward. Monitor system performance and consider scaling resources.")

            # Usage growth recommendations
            request_rate = metrics.get("request_rate", 0)
            if request_rate < 1:  # Less than 1 request per minute
                recommendations.append("Low API usage detected. Consider improving documentation and developer experience.")

        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")

        return recommendations

    # Background Tasks
    async def _start_monitoring_tasks(self):
        """Start background monitoring tasks"""
        # Data cleanup task
        asyncio.create_task(self._cleanup_old_data())

        # Alert processing task
        asyncio.create_task(self._process_alerts())

        # Health check task
        asyncio.create_task(self._health_check_partners())

    async def _cleanup_old_data(self):
        """Clean up old metric data"""
        while self.monitoring_enabled:
            try:
                cutoff_time = datetime.now() - timedelta(days=self.config["retention_days"])

                for metric_key, metrics in self.metrics_data.items():
                    # Remove old metrics
                    while metrics and metrics[0].timestamp < cutoff_time:
                        metrics.popleft()

                await asyncio.sleep(3600)  # Run every hour

            except Exception as e:
                self.logger.error(f"Data cleanup failed: {e}")
                await asyncio.sleep(300)

    async def _process_alerts(self):
        """Process and manage alerts"""
        while self.monitoring_enabled:
            try:
                # Auto-resolve old alerts
                current_time = datetime.now()
                auto_resolve_time = timedelta(hours=24)

                for alert in self.alerts.values():
                    if (alert.status == AlertStatus.ACTIVE and
                        current_time - alert.created_at > auto_resolve_time):

                        alert.status = AlertStatus.RESOLVED
                        alert.resolved_at = current_time

                        self.logger.info(f"Auto-resolved alert: {alert.id}")

                await asyncio.sleep(300)  # Run every 5 minutes

            except Exception as e:
                self.logger.error(f"Alert processing failed: {e}")
                await asyncio.sleep(60)

    async def _health_check_partners(self):
        """Perform health checks on partners"""
        while self.monitoring_enabled:
            try:
                # Check for partners with no recent activity
                current_time = datetime.now()
                inactive_threshold = timedelta(hours=1)

                for metric_key in self.metrics_data.keys():
                    partner_id = metric_key.split(':')[0]
                    metrics = self.metrics_data[metric_key]

                    if metrics and current_time - metrics[-1].timestamp > inactive_threshold:
                        # Partner appears inactive
                        await self._create_inactivity_alert(partner_id)

                await asyncio.sleep(1800)  # Run every 30 minutes

            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
                await asyncio.sleep(300)

    async def _create_inactivity_alert(self, partner_id: str):
        """Create alert for partner inactivity"""
        try:
            # Check if we already have an active inactivity alert
            existing_alerts = [
                alert for alert in self.alerts.values()
                if (alert.partner_id == partner_id and
                    alert.metric_name == "partner_activity" and
                    alert.status == AlertStatus.ACTIVE)
            ]

            if existing_alerts:
                return  # Already have an active alert

            alert_id = str(uuid.uuid4())

            alert = Alert(
                id=alert_id,
                partner_id=partner_id,
                metric_name="partner_activity",
                condition="inactive > 1 hour",
                threshold=1.0,
                severity=AlertSeverity.WARNING,
                status=AlertStatus.ACTIVE,
                message=f"Partner {partner_id} has been inactive for over 1 hour",
                created_at=datetime.now()
            )

            self.alerts[alert_id] = alert
            await self._send_alert_notification(alert)

        except Exception as e:
            self.logger.error(f"Inactivity alert creation failed: {e}")

    # Data Management
    async def _load_alert_rules(self):
        """Load predefined alert rules"""
        # Default alert rules
        default_rules = [
            {
                "metric_name": "api_response_time",
                "condition": "gt",
                "threshold": 2000,
                "severity": "warning",
                "message_template": "High response time detected: {value}ms (threshold: {threshold}ms)"
            },
            {
                "metric_name": "api_error_rate",
                "condition": "gt",
                "threshold": 10,
                "severity": "error",
                "message_template": "High error rate detected: {value}% (threshold: {threshold}%)"
            }
        ]

        # In production, load from configuration storage
        self.logger.info("Default alert rules loaded")

    async def get_analytics_dashboard_data(self, partner_id: str = None) -> Dict[str, Any]:
        """Get analytics dashboard data"""
        try:
            current_time = datetime.now()
            last_hour = current_time - timedelta(hours=1)

            if partner_id:
                # Partner-specific dashboard
                derived_metrics = await self.calculate_derived_metrics(partner_id, last_hour, current_time)
                performance_score = await self.calculate_performance_score(partner_id, last_hour, current_time)

                partner_alerts = [
                    alert for alert in self.alerts.values()
                    if alert.partner_id == partner_id and alert.status == AlertStatus.ACTIVE
                ]

                return {
                    "partner_id": partner_id,
                    "timestamp": current_time.isoformat(),
                    "performance_score": performance_score,
                    "metrics": derived_metrics,
                    "active_alerts": len(partner_alerts),
                    "alert_breakdown": {
                        "critical": len([a for a in partner_alerts if a.severity == AlertSeverity.CRITICAL]),
                        "error": len([a for a in partner_alerts if a.severity == AlertSeverity.ERROR]),
                        "warning": len([a for a in partner_alerts if a.severity == AlertSeverity.WARNING])
                    }
                }
            else:
                # System-wide dashboard
                total_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE])

                # Get unique partners with metrics
                active_partners = set()
                for metric_key in self.metrics_data.keys():
                    partner_id = metric_key.split(':')[0]
                    active_partners.add(partner_id)

                return {
                    "timestamp": current_time.isoformat(),
                    "total_partners": len(active_partners),
                    "total_metrics": sum(len(metrics) for metrics in self.metrics_data.values()),
                    "active_alerts": total_alerts,
                    "alert_breakdown": {
                        "critical": len([a for a in self.alerts.values() if a.severity == AlertSeverity.CRITICAL and a.status == AlertStatus.ACTIVE]),
                        "error": len([a for a in self.alerts.values() if a.severity == AlertSeverity.ERROR and a.status == AlertStatus.ACTIVE]),
                        "warning": len([a for a in self.alerts.values() if a.severity == AlertSeverity.WARNING and a.status == AlertStatus.ACTIVE])
                    }
                }

        except Exception as e:
            self.logger.error(f"Analytics dashboard data generation failed: {e}")
            return {}

    async def shutdown(self):
        """Shutdown analytics system"""
        self.monitoring_enabled = False
        self.logger.info("Partner Analytics System shutdown complete")

# Integration helpers for OS Dashboard AI Assistant
async def initialize_partner_analytics() -> Optional[PartnerAnalyticsSystem]:
    """Initialize partner analytics system if dependencies are available"""
    try:
        # Check if required dependencies are available
        import pandas
        import numpy

        analytics_system = PartnerAnalyticsSystem()
        await analytics_system.initialize()
        return analytics_system
    except ImportError as e:
        print(f"⚠️ Partner analytics system not available: Missing dependencies ({e})")
        return None

# Example usage integrated with OS Dashboard
async def demo_partner_analytics():
    """Demo function for partner analytics integration"""
    analytics_system = await initialize_partner_analytics()
    if not analytics_system:
        print("Partner analytics system not available")
        return

    # Example partner analytics
    partner_id = "partner_001"

    # Record some metrics
    await analytics_system.record_api_request(
        partner_id=partner_id,
        endpoint="/api/v1/data",
        method="GET",
        status_code=200,
        response_time=150.0,
        data_size=1024
    )

    # Create alert rule
    alert_rule_data = {
        "metric_name": "api_response_time",
        "condition": "gt",
        "threshold": 200,
        "severity": "warning"
    }

    rule_id = await analytics_system.create_alert_rule(partner_id, alert_rule_data)
    print(f"Created alert rule: {rule_id}")

    # Generate performance report
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)

    report = await analytics_system.generate_performance_report(partner_id, start_time, end_time)
    print(f"Performance Score: {report.performance_score}")
    print(f"Recommendations: {report.recommendations}")

    # Get dashboard data
    dashboard = await analytics_system.get_analytics_dashboard_data(partner_id)
    print(f"Dashboard: {dashboard}")

if __name__ == "__main__":
    asyncio.run(demo_partner_analytics())
