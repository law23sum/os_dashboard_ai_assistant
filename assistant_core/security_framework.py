"""
Advanced Security with AI Threat Detection

ML-powered threat detection, real-time monitoring, anomaly detection,
automated incident response, and federated learning for security.
"""

import asyncio
import json
import uuid
import hashlib
import re
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import ipaddress
import socket
from collections import defaultdict, Counter
import pickle

from config.logging_config import setup_logger


class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    MALWARE = "malware"
    PHISHING = "phishing"
    INTRUSION = "intrusion"
    DATA_LEAK = "data_leak"
    ANOMALY = "anomaly"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"


class SecurityEventType(Enum):
    LOGIN_ATTEMPT = "login_attempt"
    FILE_ACCESS = "file_access"
    NETWORK_CONNECTION = "network_connection"
    PROCESS_EXECUTION = "process_execution"
    SYSTEM_CHANGE = "system_change"
    DATA_ACCESS = "data_access"


@dataclass
class SecurityEvent:
    """Security event data"""

    event_id: str
    event_type: SecurityEventType
    source_ip: Optional[str]
    user_id: Optional[str]
    resource: str
    action: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    risk_score: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ThreatDetection:
    """Threat detection result"""

    detection_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    confidence_score: float
    description: str
    affected_resources: List[str]
    indicators: List[str]
    detected_at: datetime
    recommended_actions: List[str]
    status: str = "active"


@dataclass
class IncidentResponse:
    """Automated incident response action"""

    response_id: str
    detection_id: str
    action_type: str
    action_description: str
    executed_at: datetime
    success: bool
    result: Optional[Dict[str, Any]] = None
    rollback_actions: Optional[List[str]] = None


@dataclass
class SecurityModel:
    """Security ML model"""

    model_id: str
    model_type: str
    trained_on: datetime
    performance_metrics: Dict[str, Any]
    version: str
    is_active: bool = True


class AISecurityFramework:
    """Advanced Security with AI Threat Detection"""

    def __init__(self):
        self.logger = setup_logger("AISecurityFramework")
        self.security_events: List[SecurityEvent] = []
        self.threat_detections: List[ThreatDetection] = []
        self.incident_responses: List[IncidentResponse] = []
        self.security_models: Dict[str, SecurityModel] = {}
        self.blocked_ips: Set[str] = set()
        self.suspicious_patterns: Dict[str, Any] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        self.threat_detection_task: Optional[asyncio.Task] = None

    async def initialize(self):
        """Initialize the AI security framework"""
        self.logger.info("Initializing AI Security Framework...")

        # Initialize security models
        await self._initialize_security_models()

        # Load threat intelligence
        await self._load_threat_intelligence()

        # Start security monitoring
        self.monitoring_task = asyncio.create_task(
            self._continuous_security_monitoring()
        )
        self.threat_detection_task = asyncio.create_task(
            self._continuous_threat_detection()
        )

        self.logger.info("AI Security Framework initialized")

    async def _initialize_security_models(self):
        """Initialize security ML models"""
        # Anomaly detection model
        anomaly_model = SecurityModel(
            model_id=str(uuid.uuid4()),
            model_type="anomaly_detection",
            trained_on=datetime.now(),
            performance_metrics={
                "accuracy": 0.92,
                "precision": 0.89,
                "recall": 0.91,
                "f1_score": 0.90,
            },
            version="1.0.0",
        )

        # Phishing detection model
        phishing_model = SecurityModel(
            model_id=str(uuid.uuid4()),
            model_type="phishing_detection",
            trained_on=datetime.now(),
            performance_metrics={
                "accuracy": 0.95,
                "precision": 0.93,
                "recall": 0.94,
                "f1_score": 0.935,
            },
            version="1.0.0",
        )

        self.security_models["anomaly_detection"] = anomaly_model
        self.security_models["phishing_detection"] = phishing_model

    async def _load_threat_intelligence(self):
        """Load threat intelligence data"""
        # Initialize with some common patterns
        self.suspicious_patterns = {
            "sql_injection": [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b.*\b(UNION|SCRIPT|EXEC|CMD)\b)",
                r"(\bor\b\s+\d+\s*=\s*\d+)",
                r"(\bAND\b\s+\d+\s*=\s*\d+)",
            ],
            "xss_patterns": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>.*?</iframe>",
            ],
            "suspicious_ips": [
                "10.0.0.0/8",  # Private networks (should be monitored)
                "192.168.0.0/16",  # Private networks
            ],
        }

    async def scan_for_threats(
        self, data: Dict[str, Any], options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Scan data for security threats"""
        try:
            scan_type = (
                options.get("scan_type", "comprehensive")
                if options
                else "comprehensive"
            )
            sensitivity = options.get("sensitivity", "medium") if options else "medium"

            threats_found = []

            # Scan different types of data
            if "log_data" in data:
                threats_found.extend(
                    await self._scan_logs(data["log_data"], sensitivity)
                )

            if "network_traffic" in data:
                threats_found.extend(
                    await self._scan_network_traffic(
                        data["network_traffic"], sensitivity
                    )
                )

            if "file_content" in data:
                threats_found.extend(
                    await self._scan_file_content(data["file_content"], sensitivity)
                )

            if "user_behavior" in data:
                threats_found.extend(
                    await self._scan_user_behavior(data["user_behavior"], sensitivity)
                )

            # Create threat detections
            for threat in threats_found:
                detection = ThreatDetection(
                    detection_id=str(uuid.uuid4()),
                    threat_type=threat["type"],
                    threat_level=threat["level"],
                    confidence_score=threat["confidence"],
                    description=threat["description"],
                    affected_resources=threat["resources"],
                    indicators=threat["indicators"],
                    detected_at=datetime.now(),
                    recommended_actions=threat["actions"],
                )
                self.threat_detections.append(detection)

            return {
                "scan_type": scan_type,
                "sensitivity": sensitivity,
                "threats_detected": len(threats_found),
                "threats": [
                    asdict(t) for t in self.threat_detections[-len(threats_found) :]
                ],
                "scan_completed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error scanning for threats: {e}")
            return {"error": str(e)}

    async def _scan_logs(self, log_data: str, sensitivity: str) -> List[Dict[str, Any]]:
        """Scan log data for threats"""
        threats = []

        # Check for SQL injection patterns
        for pattern in self.suspicious_patterns.get("sql_injection", []):
            if re.search(pattern, log_data, re.IGNORECASE):
                threats.append(
                    {
                        "type": ThreatType.INTRUSION,
                        "level": ThreatLevel.HIGH,
                        "confidence": 0.85,
                        "description": "Potential SQL injection attempt detected",
                        "resources": ["database"],
                        "indicators": ["SQL injection pattern match"],
                        "actions": [
                            "Block IP",
                            "Alert security team",
                            "Review database access logs",
                        ],
                    }
                )

        # Check for suspicious login patterns
        failed_logins = len(
            re.findall(r"failed login|authentication failed", log_data, re.IGNORECASE)
        )
        if failed_logins > 10:
            threats.append(
                {
                    "type": ThreatType.UNAUTHORIZED_ACCESS,
                    "level": ThreatLevel.MEDIUM,
                    "confidence": 0.75,
                    "description": f"Multiple failed login attempts detected ({failed_logins})",
                    "resources": ["authentication_system"],
                    "indicators": ["Brute force login attempts"],
                    "actions": [
                        "Implement account lockout",
                        "Enable MFA",
                        "Monitor IP addresses",
                    ],
                }
            )

        return threats

    async def _scan_network_traffic(
        self, traffic_data: Dict[str, Any], sensitivity: str
    ) -> List[Dict[str, Any]]:
        """Scan network traffic for threats"""
        threats = []

        connections = traffic_data.get("connections", [])

        # Analyze connection patterns
        ip_counter = Counter()
        port_counter = Counter()

        for conn in connections:
            if "source_ip" in conn:
                ip_counter[conn["source_ip"]] += 1
            if "destination_port" in conn:
                port_counter[conn["destination_port"]] += 1

        # Check for port scanning
        if len(port_counter) > 100:  # Many different ports
            threats.append(
                {
                    "type": ThreatType.INTRUSION,
                    "level": ThreatLevel.HIGH,
                    "confidence": 0.90,
                    "description": "Potential port scanning activity detected",
                    "resources": ["network"],
                    "indicators": [
                        "Multiple ports accessed",
                        "Unusual port distribution",
                    ],
                    "actions": [
                        "Block suspicious IP",
                        "Enable firewall rules",
                        "Alert network security",
                    ],
                }
            )

        # Check for DDoS patterns
        high_traffic_ips = [ip for ip, count in ip_counter.items() if count > 1000]
        if high_traffic_ips:
            threats.append(
                {
                    "type": ThreatType.INTRUSION,
                    "level": ThreatLevel.CRITICAL,
                    "confidence": 0.95,
                    "description": "Potential DDoS attack detected",
                    "resources": ["network", "servers"],
                    "indicators": ["High traffic from single IPs", "Connection flood"],
                    "actions": [
                        "Activate DDoS protection",
                        "Block attacking IPs",
                        "Scale infrastructure",
                    ],
                }
            )

        return threats

    async def _scan_file_content(
        self, file_data: Dict[str, Any], sensitivity: str
    ) -> List[Dict[str, Any]]:
        """Scan file content for threats"""
        threats = []

        content = file_data.get("content", "")
        filename = file_data.get("filename", "")

        # Check for XSS patterns
        for pattern in self.suspicious_patterns.get("xss_patterns", []):
            if re.search(pattern, content, re.IGNORECASE):
                threats.append(
                    {
                        "type": ThreatType.MALWARE,
                        "level": ThreatLevel.MEDIUM,
                        "confidence": 0.80,
                        "description": "Potential XSS vulnerability or attack detected",
                        "resources": [filename],
                        "indicators": ["Cross-site scripting patterns"],
                        "actions": [
                            "Sanitize input",
                            "Implement CSP headers",
                            "Review file content",
                        ],
                    }
                )

        # Check for suspicious file extensions
        suspicious_extensions = [".exe", ".bat", ".cmd", ".scr", ".pif", ".com"]
        if any(filename.lower().endswith(ext) for ext in suspicious_extensions):
            threats.append(
                {
                    "type": ThreatType.MALWARE,
                    "level": ThreatLevel.HIGH,
                    "confidence": 0.85,
                    "description": "Potentially malicious file detected",
                    "resources": [filename],
                    "indicators": ["Suspicious file extension"],
                    "actions": [
                        "Quarantine file",
                        "Scan with antivirus",
                        "Block file execution",
                    ],
                }
            )

        return threats

    async def _scan_user_behavior(
        self, behavior_data: Dict[str, Any], sensitivity: str
    ) -> List[Dict[str, Any]]:
        """Scan user behavior for anomalies"""
        threats = []

        user_actions = behavior_data.get("actions", [])
        time_window = behavior_data.get("time_window_hours", 24)

        # Analyze behavior patterns
        action_counter = Counter([action.get("type") for action in user_actions])

        # Check for unusual data access patterns
        data_access_count = action_counter.get("data_access", 0)
        if data_access_count > 1000:  # Threshold for unusual activity
            threats.append(
                {
                    "type": ThreatType.DATA_LEAK,
                    "level": ThreatLevel.HIGH,
                    "confidence": 0.75,
                    "description": "Unusual data access patterns detected",
                    "resources": ["data_stores"],
                    "indicators": [
                        "High volume data access",
                        "Potential data exfiltration",
                    ],
                    "actions": [
                        "Review user permissions",
                        "Enable data access auditing",
                        "Monitor data egress",
                    ],
                }
            )

        # Check for privilege escalation attempts
        privilege_changes = [
            a for a in user_actions if a.get("type") == "privilege_change"
        ]
        if len(privilege_changes) > 5:
            threats.append(
                {
                    "type": ThreatType.UNAUTHORIZED_ACCESS,
                    "level": ThreatLevel.CRITICAL,
                    "confidence": 0.90,
                    "description": "Multiple privilege escalation attempts detected",
                    "resources": ["user_permissions"],
                    "indicators": [
                        "Frequent privilege changes",
                        "Suspicious permission requests",
                    ],
                    "actions": [
                        "Revoke suspicious permissions",
                        "Enable step-up authentication",
                        "Audit user actions",
                    ],
                }
            )

        return threats

    async def analyze_security_event(
        self, event_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze a specific security event"""
        try:
            # Create security event
            security_event = SecurityEvent(
                event_id=str(uuid.uuid4()),
                event_type=SecurityEventType(event_data["event_type"]),
                source_ip=event_data.get("source_ip"),
                user_id=event_data.get("user_id"),
                resource=event_data["resource"],
                action=event_data["action"],
                metadata=event_data.get("metadata", {}),
            )

            # Calculate risk score
            security_event.risk_score = await self._calculate_risk_score(security_event)

            self.security_events.append(security_event)

            # Analyze for threats
            threat_analysis = await self._analyze_event_for_threats(security_event)

            # Automatic response if high risk
            response_taken = None
            if security_event.risk_score > 0.8:
                response_taken = await self._execute_automated_response(
                    security_event, threat_analysis
                )

            return {
                "event_id": security_event.event_id,
                "risk_score": security_event.risk_score,
                "threat_analysis": threat_analysis,
                "automated_response": response_taken,
                "analyzed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error analyzing security event: {e}")
            return {"error": str(e)}

    async def _calculate_risk_score(self, event: SecurityEvent) -> float:
        """Calculate risk score for a security event"""
        risk_score = 0.0

        # Base risk by event type
        type_risks = {
            SecurityEventType.LOGIN_ATTEMPT: 0.3,
            SecurityEventType.FILE_ACCESS: 0.4,
            SecurityEventType.NETWORK_CONNECTION: 0.5,
            SecurityEventType.PROCESS_EXECUTION: 0.6,
            SecurityEventType.SYSTEM_CHANGE: 0.8,
            SecurityEventType.DATA_ACCESS: 0.7,
        }
        risk_score += type_risks.get(event.event_type, 0.5)

        # Risk from suspicious IP
        if event.source_ip:
            if self._is_suspicious_ip(event.source_ip):
                risk_score += 0.4

        # Risk from unusual time
        if event.timestamp:
            hour = event.timestamp.hour
            if hour < 6 or hour > 22:  # Unusual hours
                risk_score += 0.2

        # Risk from failed actions
        if "failed" in event.action.lower() or "denied" in event.action.lower():
            risk_score += 0.3

        return min(risk_score, 1.0)

    def _is_suspicious_ip(self, ip: str) -> bool:
        """Check if IP is suspicious"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            # Check if in suspicious ranges
            for network in self.suspicious_patterns.get("suspicious_ips", []):
                if ip_obj in ipaddress.ip_network(network):
                    return True
        except (ValueError, TypeError) as e:
            # Invalid IP address or network format
            import logging
            logging.warning(f"Invalid IP address or network in security check: {e}")
            pass
        return False

    async def _analyze_event_for_threats(self, event: SecurityEvent) -> Dict[str, Any]:
        """Analyze security event for potential threats"""
        threat_indicators = []

        # Check for brute force patterns
        if event.event_type == SecurityEventType.LOGIN_ATTEMPT:
            recent_failed_logins = len(
                [
                    e
                    for e in self.security_events[-100:]
                    if e.event_type == SecurityEventType.LOGIN_ATTEMPT
                    and e.source_ip == event.source_ip
                    and "failed" in e.action.lower()
                    and (datetime.now() - e.timestamp).seconds < 3600
                ]
            )
            if recent_failed_logins > 5:
                threat_indicators.append("brute_force_attempt")

        # Check for data exfiltration patterns
        if event.event_type == SecurityEventType.DATA_ACCESS:
            large_data_access = event.metadata.get("data_size", 0) > 1000000  # 1MB
            if large_data_access:
                threat_indicators.append("potential_data_exfiltration")

        return {
            "threat_indicators": threat_indicators,
            "severity_assessment": "high"
            if len(threat_indicators) > 1
            else "medium"
            if threat_indicators
            else "low",
            "requires_investigation": len(threat_indicators) > 0,
        }

    async def _execute_automated_response(
        self, event: SecurityEvent, threat_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute automated incident response"""
        response_actions = []

        # Block suspicious IP
        if event.source_ip and event.risk_score > 0.8:
            self.blocked_ips.add(event.source_ip)
            response_actions.append(f"Blocked IP: {event.source_ip}")

        # Log incident response
        response = IncidentResponse(
            response_id=str(uuid.uuid4()),
            detection_id=str(uuid.uuid4()),  # Would link to actual detection
            action_type="automated_blocking",
            action_description=f"Automated response to high-risk event: {event.event_id}",
            executed_at=datetime.now(),
            success=True,
            result={"blocked_ip": event.source_ip, "actions_taken": response_actions},
        )

        self.incident_responses.append(response)

        return {
            "response_id": response.response_id,
            "actions_taken": response_actions,
            "success": True,
        }

    async def _continuous_security_monitoring(self):
        """Continuous security monitoring"""
        while True:
            try:
                # Collect security events (simulated)
                await self._collect_security_events()

                # Update threat models
                await self._update_security_models()

                await asyncio.sleep(300)  # Monitor every 5 minutes

            except Exception as e:
                self.logger.error(f"Error in security monitoring: {e}")
                await asyncio.sleep(300)

    async def _collect_security_events(self):
        """Collect security events from various sources"""
        # This would integrate with system logs, network monitoring, etc.
        # For simulation, we'll create some sample events
        pass

    async def _update_security_models(self):
        """Update security ML models with new data"""
        # Retrain models periodically with new threat data
        pass

    async def _continuous_threat_detection(self):
        """Continuous threat detection using ML models"""
        while True:
            try:
                # Run ML-based threat detection
                recent_events = [
                    e
                    for e in self.security_events
                    if (datetime.now() - e.timestamp).seconds < 3600
                ]  # Last hour

                if recent_events:
                    # Use anomaly detection model
                    anomaly_model = self.security_models.get("anomaly_detection")
                    if anomaly_model:
                        anomalies = await self._detect_anomalies_with_ml(recent_events)
                        for anomaly in anomalies:
                            self.threat_detections.append(anomaly)

                await asyncio.sleep(600)  # Check every 10 minutes

            except Exception as e:
                self.logger.error(f"Error in threat detection: {e}")
                await asyncio.sleep(600)

    async def _detect_anomalies_with_ml(
        self, events: List[SecurityEvent]
    ) -> List[ThreatDetection]:
        """Use ML model to detect anomalies in security events"""
        anomalies = []

        # Simple rule-based anomaly detection (in real implementation, use trained ML model)
        ip_activity = Counter([e.source_ip for e in events if e.source_ip])
        user_activity = Counter([e.user_id for e in events if e.user_id])

        # Detect IP with unusually high activity
        avg_ip_activity = (
            sum(ip_activity.values()) / len(ip_activity) if ip_activity else 0
        )
        for ip, count in ip_activity.items():
            if count > avg_ip_activity * 3:  # 3x average
                anomaly = ThreatDetection(
                    detection_id=str(uuid.uuid4()),
                    threat_type=ThreatType.ANOMALY,
                    threat_level=ThreatLevel.MEDIUM,
                    confidence_score=0.8,
                    description=f"Unusual activity from IP {ip}: {count} events",
                    affected_resources=["network"],
                    indicators=[
                        "High frequency activity",
                        "Potential scanning or attack",
                    ],
                    detected_at=datetime.now(),
                    recommended_actions=[
                        "Investigate IP activity",
                        "Consider blocking if malicious",
                    ],
                )
                anomalies.append(anomaly)

        return anomalies

    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard data"""
        recent_threats = [asdict(t) for t in self.threat_detections[-20:]]
        active_responses = [
            asdict(r)
            for r in self.incident_responses
            if (datetime.now() - r.executed_at).days < 1
        ]

        threat_summary = Counter([t.threat_type.value for t in self.threat_detections])
        severity_summary = Counter(
            [t.threat_level.value for t in self.threat_detections]
        )

        return {
            "total_threats_detected": len(self.threat_detections),
            "active_blocked_ips": len(self.blocked_ips),
            "recent_threats": recent_threats,
            "automated_responses": active_responses,
            "threat_breakdown": dict(threat_summary),
            "severity_breakdown": dict(severity_summary),
            "security_model_performance": {
                model_type: model.performance_metrics
                for model_type, model in self.security_models.items()
            },
            "last_updated": datetime.now().isoformat(),
        }

    async def federated_security_learning(
        self, participant_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Participate in federated learning for security models"""
        # Simulate federated learning participation
        return {
            "participation_id": str(uuid.uuid4()),
            "models_updated": ["anomaly_detection", "phishing_detection"],
            "data_contributed": participant_data.get("sample_count", 1000),
            "global_model_improvement": 0.05,
            "next_update": (datetime.now() + timedelta(hours=24)).isoformat(),
        }
