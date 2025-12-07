"""
Advanced AI Security and Threat Detection System

Intelligent security monitoring with ML-powered threat detection, behavioral analysis, and automated response

"""

import asyncio

import json

import uuid

import hashlib

import hmac

from typing import Dict, Any, List, Optional, Tuple, Set

from datetime import datetime, timedelta

from dataclasses import dataclass, asdict

from enum import Enum

import numpy as np

from collections import defaultdict, deque

import ipaddress

import re

import base64

# ML Libraries

from sklearn.ensemble import IsolationForest, RandomForestClassifier

from sklearn.preprocessing import StandardScaler

from sklearn.cluster import DBSCAN

import joblib

from config.logging_config import setup_logger

class ThreatLevel(Enum):

    LOW = 1

    MEDIUM = 2

    HIGH = 3

    CRITICAL = 4

    EMERGENCY = 5

class ThreatType(Enum):

    MALWARE = "malware"

    PHISHING = "phishing"

    BRUTE_FORCE = "brute_force"

    DDoS = "ddos"

    SQL_INJECTION = "sql_injection"

    XSS = "xss"

    UNAUTHORIZED_ACCESS = "unauthorized_access"

    DATA_EXFILTRATION = "data_exfiltration"

    INSIDER_THREAT = "insider_threat"

    ANOMALOUS_BEHAVIOR = "anomalous_behavior"

    PRIVILEGE_ESCALATION = "privilege_escalation"

    LATERAL_MOVEMENT = "lateral_movement"

class SecurityEventType(Enum):

    LOGIN_ATTEMPT = "login_attempt"

    FILE_ACCESS = "file_access"

    NETWORK_CONNECTION = "network_connection"

    API_REQUEST = "api_request"

    SYSTEM_COMMAND = "system_command"

    DATA_TRANSFER = "data_transfer"

    CONFIGURATION_CHANGE = "configuration_change"

    USER_BEHAVIOR = "user_behavior"

class ResponseAction(Enum):

    ALERT = "alert"

    BLOCK_IP = "block_ip"

    DISABLE_USER = "disable_user"

    QUARANTINE_FILE = "quarantine_file"

    ISOLATE_SYSTEM = "isolate_system"

    FORCE_LOGOUT = "force_logout"

    REQUIRE_MFA = "require_mfa"

    MONITOR_ENHANCED = "monitor_enhanced"

@dataclass

class SecurityEvent:

    """Security event data structure"""

    event_id: str

    event_type: SecurityEventType

    timestamp: datetime

    source_ip: str

    user_id: Optional[str]

    resource: str

    action: str

    details: Dict[str, Any]

    risk_score: float = 0.0

    threat_indicators: List[str] = None

@dataclass

class ThreatDetection:

    """Threat detection result"""

    detection_id: str

    threat_type: ThreatType

    threat_level: ThreatLevel

    confidence_score: float

    affected_resources: List[str]

    indicators: List[str]

    evidence: Dict[str, Any]

    recommended_actions: List[ResponseAction]

    created_at: datetime

    source_events: List[str]

@dataclass

class UserBehaviorProfile:

    """User behavior profile for anomaly detection"""

    user_id: str

    login_patterns: Dict[str, Any]

    access_patterns: Dict[str, Any]

    activity_patterns: Dict[str, Any]

    risk_score: float

    last_updated: datetime

    anomaly_threshold: float = 0.7

@dataclass

class SecurityIncident:

    """Security incident tracking"""

    incident_id: str

    title: str

    description: str

    threat_level: ThreatLevel

    status: str

    assigned_to: str

    detections: List[str]

    timeline: List[Dict[str, Any]]

    impact_assessment: Dict[str, Any]

    response_actions: List[Dict[str, Any]]

    created_at: datetime

    updated_at: datetime

class AISecurityThreatDetection:

    """Advanced AI-powered security and threat detection system"""



    def __init__(self):

        self.logger = setup_logger("AISecurityThreatDetection")



        # Core storage

        self.security_events: deque = deque(maxlen=100000)

        self.threat_detections: Dict[str, ThreatDetection] = {}

        self.security_incidents: Dict[str, SecurityIncident] = {}

        self.user_profiles: Dict[str, UserBehaviorProfile] = {}



        # ML Models

        self.anomaly_detector = None

        self.threat_classifier = None

        self.behavior_analyzer = None

        self.scaler = StandardScaler()



        # Threat intelligence

        self.threat_indicators: Dict[str, Set[str]] = {

            "malicious_ips": set(),

            "malicious_domains": set(),

            "malware_hashes": set(),

            "suspicious_patterns": set()

        }



        # Security rules

        self.security_rules: Dict[str, Dict[str, Any]] = {}

        self.whitelist: Dict[str, Set[str]] = defaultdict(set)

        self.blacklist: Dict[str, Set[str]] = defaultdict(set)



        # Configuration

        self.config = {

            "anomaly_threshold": 0.7,

            "threat_confidence_threshold": 0.8,

            "max_failed_logins": 5,

            "suspicious_login_window": 300,  # 5 minutes

            "data_transfer_threshold": 1000000,  # 1MB

            "api_rate_limit": 1000,  # per hour

            "auto_response_enabled": True,

            "ml_model_retrain_interval": 86400,  # 24 hours

            "incident_auto_creation": True

        }



        # Real-time monitoring

        self.active_sessions: Dict[str, Dict[str, Any]] = {}

        self.rate_limiters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))



        # Response system

        self.response_handlers: Dict[ResponseAction, callable] = {}

        self.blocked_ips: Set[str] = set()

        self.disabled_users: Set[str] = set()



    async def initialize(self):

        """Initialize AI security system"""

        await self._load_threat_intelligence()

        await self._load_security_rules()

        await self._initialize_ml_models()

        await self._setup_response_handlers()



        # Start background tasks

        asyncio.create_task(self._real_time_monitoring())

        asyncio.create_task(self._behavioral_analysis_loop())

        asyncio.create_task(self._threat_intelligence_update())

        asyncio.create_task(self._model_retraining_loop())

        asyncio.create_task(self._incident_management_loop())



        self.logger.info("AI Security and Threat Detection System initialized")



    # Event Processing

    async def process_security_event(self, event_data: Dict[str, Any]) -> SecurityEvent:

        """Process incoming security event"""

        try:

            # Create security event

            event = SecurityEvent(

                event_id=str(uuid.uuid4()),

                event_type=SecurityEventType(event_data['event_type']),

                timestamp=datetime.fromisoformat(event_data.get('timestamp', datetime.now().isoformat())),

                source_ip=event_data.get('source_ip', ''),

                user_id=event_data.get('user_id'),

                resource=event_data.get('resource', ''),

                action=event_data.get('action', ''),

                details=event_data.get('details', {}),

                threat_indicators=[]

            )



            # Calculate initial risk score

            event.risk_score = await self._calculate_event_risk_score(event)



            # Add threat indicators

            event.threat_indicators = await self._identify_threat_indicators(event)



            # Store event

            self.security_events.append(event)



            # Real-time threat detection

            await self._real_time_threat_detection(event)



            # Update user behavior profile

            if event.user_id:

                await self._update_user_behavior_profile(event)



            # Check for immediate response actions

            if event.risk_score > 0.8:

                await self._trigger_immediate_response(event)



            self.logger.debug(f"Security event processed: {event.event_id} (risk: {event.risk_score:.2f})")

            return event



        except Exception as e:

            self.logger.error(f"Security event processing failed: {e}")

            raise



    async def _calculate_event_risk_score(self, event: SecurityEvent) -> float:

        """Calculate risk score for security event"""

        try:

            risk_score = 0.0



            # Base risk by event type

            event_type_risks = {

                SecurityEventType.LOGIN_ATTEMPT: 0.3,

                SecurityEventType.FILE_ACCESS: 0.2,

                SecurityEventType.NETWORK_CONNECTION: 0.4,

                SecurityEventType.API_REQUEST: 0.2,

                SecurityEventType.SYSTEM_COMMAND: 0.6,

                SecurityEventType.DATA_TRANSFER: 0.5,

                SecurityEventType.CONFIGURATION_CHANGE: 0.7,

                SecurityEventType.USER_BEHAVIOR: 0.3

            }



            risk_score += event_type_risks.get(event.event_type, 0.3)



            # IP-based risk

            if event.source_ip:

                if event.source_ip in self.blacklist["ips"]:

                    risk_score += 0.5

                elif event.source_ip in self.threat_indicators["malicious_ips"]:

                    risk_score += 0.4

                elif self._is_suspicious_ip(event.source_ip):

                    risk_score += 0.2



            # User-based risk

            if event.user_id:

                if event.user_id in self.disabled_users:

                    risk_score += 0.6



                # Check user behavior profile

                profile = self.user_profiles.get(event.user_id)

                if profile and profile.risk_score > 0.7:

                    risk_score += 0.3



            # Time-based risk (off-hours access)

            current_hour = event.timestamp.hour

            if current_hour < 6 or current_hour > 22:  # Outside business hours

                risk_score += 0.1



            # Action-based risk

            high_risk_actions = ["delete", "modify", "admin", "root", "sudo"]

            if any(action in event.action.lower() for action in high_risk_actions):

                risk_score += 0.2



            # Resource-based risk

            sensitive_resources = ["database", "config", "admin", "user_data", "financial"]

            if any(resource in event.resource.lower() for resource in sensitive_resources):

                risk_score += 0.2



            # Details-based risk

            details = event.details

            if details.get("failed_attempts", 0) > 3:

                risk_score += 0.3

            if details.get("data_size", 0) > self.config["data_transfer_threshold"]:

                risk_score += 0.2



            return min(1.0, risk_score)



        except Exception as e:

            self.logger.error(f"Risk score calculation failed: {e}")

            return 0.5



    async def _identify_threat_indicators(self, event: SecurityEvent) -> List[str]:

        """Identify threat indicators in event"""

        try:

            indicators = []



            # IP-based indicators

            if event.source_ip in self.threat_indicators["malicious_ips"]:

                indicators.append(f"malicious_ip:{event.source_ip}")



            # Pattern-based indicators

            for pattern in self.threat_indicators["suspicious_patterns"]:

                if re.search(pattern, str(event.details), re.IGNORECASE):

                    indicators.append(f"suspicious_pattern:{pattern}")



            # Behavioral indicators

            if event.event_type == SecurityEventType.LOGIN_ATTEMPT:

                # Multiple failed logins

                recent_failures = self._count_recent_failed_logins(event.source_ip, event.user_id)

                if recent_failures > self.config["max_failed_logins"]:

                    indicators.append("brute_force_attempt")



            # SQL injection patterns

            sql_patterns = [

                r"union\s+select", r"drop\s+table", r"insert\s+into",

                r"delete\s+from", r"update\s+.*set", r"exec\s*\("

            ]



            for pattern in sql_patterns:

                if re.search(pattern, str(event.details), re.IGNORECASE):

                    indicators.append("sql_injection_attempt")

                    break



            # XSS patterns

            xss_patterns = [

                r"<script", r"javascript:", r"onerror=", r"onload=",

                r"eval\s*\(", r"document\.cookie"

            ]



            for pattern in xss_patterns:

                if re.search(pattern, str(event.details), re.IGNORECASE):

                    indicators.append("xss_attempt")

                    break



            # Data exfiltration indicators

            if event.event_type == SecurityEventType.DATA_TRANSFER:

                data_size = event.details.get("data_size", 0)

                if data_size > self.config["data_transfer_threshold"]:

                    indicators.append("large_data_transfer")



            return indicators



        except Exception as e:

            self.logger.error(f"Threat indicator identification failed: {e}")

            return []



    # Real-time Threat Detection

    async def _real_time_threat_detection(self, event: SecurityEvent):

        """Perform real-time threat detection"""

        try:

            # Rule-based detection

            rule_detections = await self._apply_security_rules(event)



            # ML-based anomaly detection

            ml_detections = await self._ml_anomaly_detection(event)



            # Behavioral analysis

            behavioral_detections = await self._behavioral_threat_detection(event)



            # Combine detections

            all_detections = rule_detections + ml_detections + behavioral_detections



            # Process detections

            for detection in all_detections:

                await self._process_threat_detection(detection)



        except Exception as e:

            self.logger.error(f"Real-time threat detection failed: {e}")



    async def _apply_security_rules(self, event: SecurityEvent) -> List[ThreatDetection]:

        """Apply security rules to detect threats"""

        try:

            detections = []



            for rule_id, rule in self.security_rules.items():

                if self._event_matches_rule(event, rule):

                    detection = ThreatDetection(

                        detection_id=str(uuid.uuid4()),

                        threat_type=ThreatType(rule["threat_type"]),

                        threat_level=ThreatLevel(rule["threat_level"]),

                        confidence_score=rule.get("confidence", 0.8),

                        affected_resources=[event.resource],

                        indicators=event.threat_indicators,

                        evidence={"rule_id": rule_id, "event": asdict(event)},

                        recommended_actions=[ResponseAction(action) for action in rule.get("actions", [])],

                        created_at=datetime.now(),

                        source_events=[event.event_id]

                    )

                    detections.append(detection)



            return detections



        except Exception as e:

            self.logger.error(f"Security rules application failed: {e}")

            return []



    def _event_matches_rule(self, event: SecurityEvent, rule: Dict[str, Any]) -> bool:

        """Check if event matches security rule"""

        try:

            conditions = rule.get("conditions", {})



            # Event type condition

            if "event_type" in conditions:

                if event.event_type.value not in conditions["event_type"]:

                    return False



            # Source IP condition

            if "source_ip" in conditions:

                ip_conditions = conditions["source_ip"]

                if "blacklist" in ip_conditions and event.source_ip in ip_conditions["blacklist"]:

                    return True

                if "pattern" in ip_conditions:

                    if not re.match(ip_conditions["pattern"], event.source_ip):

                        return False



            # User condition

            if "user_id" in conditions:

                user_conditions = conditions["user_id"]

                if "blacklist" in user_conditions and event.user_id in user_conditions["blacklist"]:

                    return True

                if "pattern" in user_conditions and event.user_id:

                    if not re.match(user_conditions["pattern"], event.user_id):

                        return False



            # Action condition

            if "action" in conditions:

                action_pattern = conditions["action"]

                if not re.search(action_pattern, event.action, re.IGNORECASE):

                    return False



            # Risk score condition

            if "min_risk_score" in conditions:

                if event.risk_score < conditions["min_risk_score"]:

                    return False



            # Time-based conditions

            if "time_window" in conditions:

                time_window = conditions["time_window"]

                current_hour = event.timestamp.hour

                if current_hour < time_window.get("start", 0) or current_hour > time_window.get("end", 23):

                    return False



            return True



        except Exception as e:

            self.logger.error(f"Rule matching failed: {e}")

            return False



    async def _ml_anomaly_detection(self, event: SecurityEvent) -> List[ThreatDetection]:

        """ML-based anomaly detection"""

        try:

            detections = []



            if not self.anomaly_detector:

                return detections



            # Extract features for ML model

            features = self._extract_event_features(event)



            if features is not None:

                # Scale features

                features_scaled = self.scaler.transform([features])



                # Predict anomaly

                anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]

                is_anomaly = self.anomaly_detector.predict(features_scaled)[0] == -1



                if is_anomaly and abs(anomaly_score) > self.config["anomaly_threshold"]:

                    detection = ThreatDetection(

                        detection_id=str(uuid.uuid4()),

                        threat_type=ThreatType.ANOMALOUS_BEHAVIOR,

                        threat_level=ThreatLevel.MEDIUM if abs(anomaly_score) < 1.0 else ThreatLevel.HIGH,

                        confidence_score=min(1.0, abs(anomaly_score)),

                        affected_resources=[event.resource],

                        indicators=["ml_anomaly_detected"],

                        evidence={

                            "anomaly_score": anomaly_score,

                            "features": features,

                            "model_type": "isolation_forest"

                        },

                        recommended_actions=[ResponseAction.MONITOR_ENHANCED],

                        created_at=datetime.now(),

                        source_events=[event.event_id]

                    )

                    detections.append(detection)



            return detections



        except Exception as e:

            self.logger.error(f"ML anomaly detection failed: {e}")

            return []



    def _extract_event_features(self, event: SecurityEvent) -> Optional[List[float]]:

        """Extract numerical features from security event"""

        try:

            features = []



            # Event type (one-hot encoded)

            event_types = list(SecurityEventType)

            for et in event_types:

                features.append(1.0 if event.event_type == et else 0.0)



            # Time features

            features.append(event.timestamp.hour)

            features.append(event.timestamp.weekday())



            # IP features

            if event.source_ip:

                try:

                    ip = ipaddress.ip_address(event.source_ip)

                    if ip.is_private:

                        features.append(1.0)

                    else:

                        features.append(0.0)



                    # IP octets (for IPv4)

                    if isinstance(ip, ipaddress.IPv4Address):

                        octets = str(ip).split('.')

                        features.extend([float(octet) / 255.0 for octet in octets])

                    else:

                        features.extend([0.0, 0.0, 0.0, 0.0])

                except:

                    features.extend([0.0, 0.0, 0.0, 0.0, 0.0])

            else:

                features.extend([0.0, 0.0, 0.0, 0.0, 0.0])



            # Risk score

            features.append(event.risk_score)



            # Details features

            details = event.details

            features.append(details.get("failed_attempts", 0))

            features.append(min(1.0, details.get("data_size", 0) / 1000000))  # Normalized data size

            features.append(len(event.threat_indicators))



            return features



        except Exception as e:

            self.logger.error(f"Feature extraction failed: {e}")

            return None



    async def _behavioral_threat_detection(self, event: SecurityEvent) -> List[ThreatDetection]:

        """Behavioral analysis for threat detection"""

        try:

            detections = []



            if not event.user_id:

                return detections



            # Get user behavior profile

            profile = self.user_profiles.get(event.user_id)

            if not profile:

                return detections



            # Analyze login patterns

            if event.event_type == SecurityEventType.LOGIN_ATTEMPT:

                login_anomaly = self._analyze_login_behavior(event, profile)

                if login_anomaly:

                    detections.append(login_anomaly)



            # Analyze access patterns

            if event.event_type == SecurityEventType.FILE_ACCESS:

                access_anomaly = self._analyze_access_behavior(event, profile)

                if access_anomaly:

                    detections.append(access_anomaly)



            # Analyze activity patterns

            activity_anomaly = self._analyze_activity_behavior(event, profile)

            if activity_anomaly:

                detections.append(activity_anomaly)



            return detections



        except Exception as e:

            self.logger.error(f"Behavioral threat detection failed: {e}")

            return []



    def _analyze_login_behavior(self, event: SecurityEvent, profile: UserBehaviorProfile) -> Optional[ThreatDetection]:

        """Analyze login behavior for anomalies"""

        try:

            login_patterns = profile.login_patterns



            # Check login time anomaly

            current_hour = event.timestamp.hour

            typical_hours = login_patterns.get("typical_hours", [])



            if typical_hours and current_hour not in typical_hours:

                # Check if this is significantly outside normal hours

                hour_distances = [min(abs(current_hour - h), 24 - abs(current_hour - h)) for h in typical_hours]

                min_distance = min(hour_distances) if hour_distances else 12



                if min_distance > 4:  # More than 4 hours from typical

                    return ThreatDetection(

                        detection_id=str(uuid.uuid4()),

                        threat_type=ThreatType.ANOMALOUS_BEHAVIOR,

                        threat_level=ThreatLevel.MEDIUM,

                        confidence_score=0.7,

                        affected_resources=[event.resource],

                        indicators=["unusual_login_time"],

                        evidence={

                            "current_hour": current_hour,

                            "typical_hours": typical_hours,

                            "hour_distance": min_distance

                        },

                        recommended_actions=[ResponseAction.REQUIRE_MFA],

                        created_at=datetime.now(),

                        source_events=[event.event_id]

                    )



            # Check login location anomaly (IP-based)

            typical_ips = login_patterns.get("typical_ips", set())

            if event.source_ip not in typical_ips and len(typical_ips) > 0:

                return ThreatDetection(

                    detection_id=str(uuid.uuid4()),

                    threat_type=ThreatType.ANOMALOUS_BEHAVIOR,

                    threat_level=ThreatLevel.MEDIUM,

                    confidence_score=0.6,

                    affected_resources=[event.resource],

                    indicators=["unusual_login_location"],

                    evidence={

                        "source_ip": event.source_ip,

                        "typical_ips": list(typical_ips)

                    },

                    recommended_actions=[ResponseAction.REQUIRE_MFA],

                    created_at=datetime.now(),

                    source_events=[event.event_id]

                )



            return None



        except Exception as e:

            self.logger.error(f"Login behavior analysis failed: {e}")

            return None



    def _analyze_access_behavior(self, event: SecurityEvent, profile: UserBehaviorProfile) -> Optional[ThreatDetection]:

        """Analyze file access behavior for anomalies"""

        try:

            access_patterns = profile.access_patterns



            # Check if accessing unusual resources

            typical_resources = access_patterns.get("typical_resources", set())



            if event.resource not in typical_resources and len(typical_resources) > 0:

                # Check if this is a sensitive resource

                sensitive_keywords = ["admin", "config", "database", "user_data", "financial"]

                is_sensitive = any(keyword in event.resource.lower() for keyword in sensitive_keywords)



                if is_sensitive:

                    return ThreatDetection(

                        detection_id=str(uuid.uuid4()),

                        threat_type=ThreatType.UNAUTHORIZED_ACCESS,

                        threat_level=ThreatLevel.HIGH,

                        confidence_score=0.8,

                        affected_resources=[event.resource],

                        indicators=["unusual_sensitive_access"],

                        evidence={

                            "resource": event.resource,

                            "typical_resources": list(typical_resources),

                            "is_sensitive": is_sensitive

                        },

                        recommended_actions=[ResponseAction.MONITOR_ENHANCED, ResponseAction.ALERT],

                        created_at=datetime.now(),

                        source_events=[event.event_id]

                    )



            return None



        except Exception as e:

            self.logger.error(f"Access behavior analysis failed: {e}")

            return None



    def _analyze_activity_behavior(self, event: SecurityEvent, profile: UserBehaviorProfile) -> Optional[ThreatDetection]:

        """Analyze general activity behavior for anomalies"""

        try:

            activity_patterns = profile.activity_patterns



            # Check activity volume

            current_hour = event.timestamp.hour

            typical_activity = activity_patterns.get("hourly_activity", {}).get(str(current_hour), 0)



            # Count recent activity for this user

            recent_events = [

                e for e in list(self.security_events)[-1000:]  # Last 1000 events

                if e.user_id == event.user_id and

                (event.timestamp - e.timestamp).total_seconds() < 3600  # Last hour

            ]



            current_activity = len(recent_events)



            # Check if activity is significantly higher than typical

            if typical_activity > 0 and current_activity > typical_activity * 3:

                return ThreatDetection(

                    detection_id=str(uuid.uuid4()),

                    threat_type=ThreatType.ANOMALOUS_BEHAVIOR,

                    threat_level=ThreatLevel.MEDIUM,

                    confidence_score=0.6,

                    affected_resources=[event.resource],

                    indicators=["unusual_activity_volume"],

                    evidence={

                        "current_activity": current_activity,

                        "typical_activity": typical_activity,

                        "activity_ratio": current_activity / typical_activity

                    },

                    recommended_actions=[ResponseAction.MONITOR_ENHANCED],

                    created_at=datetime.now(),

                    source_events=[event.event_id]

                )



            return None



        except Exception as e:

            self.logger.error(f"Activity behavior analysis failed: {e}")

            return None



    # User Behavior Profiling

    async def _update_user_behavior_profile(self, event: SecurityEvent):

        """Update user behavior profile"""

        try:

            if not event.user_id:

                return



            # Get or create profile

            if event.user_id not in self.user_profiles:

                self.user_profiles[event.user_id] = UserBehaviorProfile(

                    user_id=event.user_id,

                    login_patterns={

                        "typical_hours": [],

                        "typical_ips": set(),

                        "login_frequency": {}

                    },

                    access_patterns={

                        "typical_resources": set(),

                        "access_frequency": {}

                    },

                    activity_patterns={

                        "hourly_activity": {},

                        "daily_activity": {},

                        "action_patterns": {}

                    },

                    risk_score=0.0,

                    last_updated=datetime.now()

                )



            profile = self.user_profiles[event.user_id]



            # Update login patterns

            if event.event_type == SecurityEventType.LOGIN_ATTEMPT:

                hour = event.timestamp.hour

                if hour not in profile.login_patterns["typical_hours"]:

                    profile.login_patterns["typical_hours"].append(hour)



                profile.login_patterns["typical_ips"].add(event.source_ip)



                # Keep only recent IPs (last 30 days worth)

                if len(profile.login_patterns["typical_ips"]) > 10:

                    # In production, implement proper time-based cleanup

                    profile.login_patterns["typical_ips"] = set(

                        list(profile.login_patterns["typical_ips"])[-10:]

                    )



            # Update access patterns

            if event.event_type == SecurityEventType.FILE_ACCESS:

                profile.access_patterns["typical_resources"].add(event.resource)



                # Keep only recent resources

                if len(profile.access_patterns["typical_resources"]) > 50:

                    profile.access_patterns["typical_resources"] = set(

                        list(profile.access_patterns["typical_resources"])[-50:]

                    )



            # Update activity patterns

            hour_key = str(event.timestamp.hour)

            if hour_key not in profile.activity_patterns["hourly_activity"]:

                profile.activity_patterns["hourly_activity"][hour_key] = 0

            profile.activity_patterns["hourly_activity"][hour_key] += 1



            # Update action patterns

            if event.action not in profile.activity_patterns["action_patterns"]:

                profile.activity_patterns["action_patterns"][event.action] = 0

            profile.activity_patterns["action_patterns"][event.action] += 1



            # Update risk score based on recent events

            profile.risk_score = await self._calculate_user_risk_score(event.user_id)

            profile.last_updated = datetime.now()



        except Exception as e:

            self.logger.error(f"User behavior profile update failed: {e}")



    async def _calculate_user_risk_score(self, user_id: str) -> float:

        """Calculate user risk score"""

        try:

            # Get recent events for user

            recent_events = [

                e for e in list(self.security_events)[-5000:]  # Last 5000 events

                if e.user_id == user_id and

                (datetime.now() - e.timestamp).total_seconds() < 86400 * 7  # Last 7 days

            ]



            if not recent_events:

                return 0.0



            # Calculate average risk score

            avg_risk = np.mean([e.risk_score for e in recent_events])



            # Factor in threat indicators

            total_indicators = sum(len(e.threat_indicators) for e in recent_events)

            indicator_factor = min(0.3, total_indicators * 0.01)



            # Factor in failed attempts

            failed_attempts = sum(

                e.details.get("failed_attempts", 0) for e in recent_events

                if e.event_type == SecurityEventType.LOGIN_ATTEMPT

            )

            failure_factor = min(0.2, failed_attempts * 0.02)



            # Factor in off-hours activity

            off_hours_events = [

                e for e in recent_events

                if e.timestamp.hour < 6 or e.timestamp.hour > 22

            ]

            off_hours_factor = min(0.1, len(off_hours_events) / len(recent_events))



            total_risk = avg_risk + indicator_factor + failure_factor + off_hours_factor

            return min(1.0, total_risk)



        except Exception as e:

            self.logger.error(f"User risk score calculation failed: {e}")

            return 0.5



    # Threat Detection Processing

    async def _process_threat_detection(self, detection: ThreatDetection):

        """Process threat detection"""

        try:

            # Store detection

            self.threat_detections[detection.detection_id] = detection



            # Log detection

            self.logger.warning(

                f"Threat detected: {detection.threat_type.value} "

                f"(Level: {detection.threat_level.value}, "

                f"Confidence: {detection.confidence_score:.2f})"

            )



            # Execute recommended actions

            if self.config["auto_response_enabled"]:

                for action in detection.recommended_actions:

                    await self._execute_response_action(action, detection)



            # Create incident if necessary

            if (detection.threat_level.value >= ThreatLevel.HIGH.value and

                self.config["incident_auto_creation"]):

                await self._create_security_incident(detection)



            # Send alerts

            await self._send_security_alert(detection)



        except Exception as e:

            self.logger.error(f"Threat detection processing failed: {e}")



    # Response Actions

    async def _setup_response_handlers(self):

        """Setup response action handlers"""

        self.response_handlers = {

            ResponseAction.ALERT: self._handle_alert,

            ResponseAction.BLOCK_IP: self._handle_block_ip,

            ResponseAction.DISABLE_USER: self._handle_disable_user,

            ResponseAction.QUARANTINE_FILE: self._handle_quarantine_file,

            ResponseAction.ISOLATE_SYSTEM: self._handle_isolate_system,

            ResponseAction.FORCE_LOGOUT: self._handle_force_logout,

            ResponseAction.REQUIRE_MFA: self._handle_require_mfa,

            ResponseAction.MONITOR_ENHANCED: self._handle_monitor_enhanced

        }



    async def _execute_response_action(self, action: ResponseAction, detection: ThreatDetection):

        """Execute response action"""

        try:

            handler = self.response_handlers.get(action)

            if handler:

                await handler(detection)

                self.logger.info(f"Response action executed: {action.value} for {detection.detection_id}")

            else:

                self.logger.warning(f"No handler for response action: {action.value}")



        except Exception as e:

            self.logger.error(f"Response action execution failed: {e}")



    async def _handle_alert(self, detection: ThreatDetection):

        """Handle alert action"""

        # Send alert to security team

        alert_data = {

            "detection_id": detection.detection_id,

            "threat_type": detection.threat_type.value,

            "threat_level": detection.threat_level.value,

            "confidence": detection.confidence_score,

            "timestamp": detection.created_at.isoformat()

        }



        # In production, integrate with alerting system

        self.logger.info(f"Security alert sent: {alert_data}")



    async def _handle_block_ip(self, detection: ThreatDetection):

        """Handle IP blocking action"""

        # Extract IP from detection evidence

        source_events = detection.source_events

        for event_id in source_events:

            # Find the event

            for event in self.security_events:

                if event.event_id == event_id and event.source_ip:

                    self.blocked_ips.add(event.source_ip)

                    self.logger.info(f"IP blocked: {event.source_ip}")

                    break



    async def _handle_disable_user(self, detection: ThreatDetection):

        """Handle user disabling action"""

        # Extract user from detection evidence

        source_events = detection.source_events

        for event_id in source_events:

            for event in self.security_events:

                if event.event_id == event_id and event.user_id:

                    self.disabled_users.add(event.user_id)

                    self.logger.info(f"User disabled: {event.user_id}")

                    break



    async def _handle_quarantine_file(self, detection: ThreatDetection):

        """Handle file quarantine action"""

        # In production, implement file quarantine

        self.logger.info(f"File quarantine requested for detection: {detection.detection_id}")



    async def _handle_isolate_system(self, detection: ThreatDetection):

        """Handle system isolation action"""

        # In production, implement system isolation

        self.logger.info(f"System isolation requested for detection: {detection.detection_id}")



    async def _handle_force_logout(self, detection: ThreatDetection):

        """Handle force logout action"""

        # In production, implement force logout

        self.logger.info(f"Force logout requested for detection: {detection.detection_id}")



    async def _handle_require_mfa(self, detection: ThreatDetection):

        """Handle MFA requirement action"""

        # In production, implement MFA requirement

        self.logger.info(f"MFA requirement set for detection: {detection.detection_id}")



    async def _handle_monitor_enhanced(self, detection: ThreatDetection):

        """Handle enhanced monitoring action"""

        # In production, implement enhanced monitoring

        self.logger.info(f"Enhanced monitoring enabled for detection: {detection.detection_id}")



    # Incident Management

    async def _create_security_incident(self, detection: ThreatDetection):

        """Create security incident"""

        try:

            incident_id = str(uuid.uuid4())



            incident = SecurityIncident(

                incident_id=incident_id,

                title=f"{detection.threat_type.value.title()} - {detection.threat_level.value.title()} Threat",

                description=f"Threat detected: {detection.threat_type.value} with confidence {detection.confidence_score:.2f}",

                threat_level=detection.threat_level,

                status="open",

                assigned_to="security_team",

                detections=[detection.detection_id],

                timeline=[{

                    "timestamp": datetime.now().isoformat(),

                    "event": "incident_created",

                    "details": {"detection_id": detection.detection_id}

                }],

                impact_assessment={

                    "affected_resources": detection.affected_resources,

                    "potential_impact": "under_investigation"

                },

                response_actions=[],

                created_at=datetime.now(),

                updated_at=datetime.now()

            )



            self.security_incidents[incident_id] = incident



            self.logger.info(f"Security incident created: {incident_id}")

            return incident_id



        except Exception as e:

            self.logger.error(f"Security incident creation failed: {e}")

            return None



    async def _send_security_alert(self, detection: ThreatDetection):

        """Send security alert"""

        try:

            alert = {

                "alert_id": str(uuid.uuid4()),

                "detection_id": detection.detection_id,

                "threat_type": detection.threat_type.value,

                "threat_level": detection.threat_level.value,

                "confidence_score": detection.confidence_score,

                "affected_resources": detection.affected_resources,

                "indicators": detection.indicators,

                "recommended_actions": [action.value for action in detection.recommended_actions],

                "timestamp": detection.created_at.isoformat()

            }



            # In production, send to alerting system (email, Slack, etc.)

            self.logger.info(f"Security alert: {alert}")



        except Exception as e:

            self.logger.error(f"Security alert sending failed: {e}")



    # Utility Methods

    def _is_suspicious_ip(self, ip: str) -> bool:

        """Check if IP is suspicious"""

        try:

            ip_obj = ipaddress.ip_address(ip)



            # Check if IP is in suspicious ranges

            suspicious_ranges = [

                ipaddress.ip_network("10.0.0.0/8"),  # Example suspicious range

                ipaddress.ip_network("192.168.0.0/16")  # Example suspicious range

            ]



            for network in suspicious_ranges:

                if ip_obj in network:

                    return True



            return False



        except Exception:

            return False



    def _count_recent_failed_logins(self, source_ip: str, user_id: str) -> int:

        """Count recent failed login attempts"""

        try:

            cutoff_time = datetime.now() - timedelta(seconds=self.config["suspicious_login_window"])



            failed_count = 0

            for event in self.security_events:

                if (event.event_type == SecurityEventType.LOGIN_ATTEMPT and

                    event.timestamp > cutoff_time and

                    (event.source_ip == source_ip or event.user_id == user_id) and

                    event.details.get("success", True) == False):

                    failed_count += 1



            return failed_count



        except Exception as e:

            self.logger.error(f"Failed login counting failed: {e}")

            return 0



    async def _trigger_immediate_response(self, event: SecurityEvent):

        """Trigger immediate response for high-risk events"""

        try:

            if event.risk_score > 0.9:

                # Critical risk - immediate action

                if event.source_ip:

                    self.blocked_ips.add(event.source_ip)

                    self.logger.warning(f"IP immediately blocked due to critical risk: {event.source_ip}")



                if event.user_id:

                    # In production, force logout or require MFA

                    self.logger.warning(f"User flagged for immediate review: {event.user_id}")



        except Exception as e:

            self.logger.error(f"Immediate response trigger failed: {e}")



    # Background Tasks

    async def _real_time_monitoring(self):

        """Real-time security monitoring"""

        while True:

            try:

                # Monitor active sessions

                current_time = datetime.now()



                # Check for session anomalies

                for session_id, session_data in self.active_sessions.items():

                    session_duration = (current_time - session_data["start_time"]).total_seconds()



                    # Check for unusually long sessions

                    if session_duration > 28800:  # 8 hours

                        self.logger.warning(f"Long session detected: {session_id}")



                # Check rate limits

                for identifier, requests in self.rate_limiters.items():

                    # Remove old requests

                    cutoff_time = current_time - timedelta(hours=1)

                    while requests and requests[0] < cutoff_time:

                        requests.popleft()



                    # Check if rate limit exceeded

                    if len(requests) > self.config["api_rate_limit"]:

                        self.logger.warning(f"Rate limit exceeded: {identifier}")



                await asyncio.sleep(10)  # Check every 10 seconds



            except Exception as e:

                self.logger.error(f"Real-time monitoring failed: {e}")

                await asyncio.sleep(30)



    async def _behavioral_analysis_loop(self):

        """Periodic behavioral analysis"""

        while True:

            try:

                # Analyze user behavior patterns

                for user_id, profile in self.user_profiles.items():

                    # Update risk score

                    profile.risk_score = await self._calculate_user_risk_score(user_id)



                    # Check for behavioral anomalies

                    if profile.risk_score > profile.anomaly_threshold:

                        self.logger.warning(f"User behavioral anomaly detected: {user_id} (risk: {profile.risk_score:.2f})")



                await asyncio.sleep(300)  # Run every 5 minutes



            except Exception as e:

                self.logger.error(f"Behavioral analysis loop failed: {e}")

                await asyncio.sleep(60)



    async def _threat_intelligence_update(self):

        """Update threat intelligence data"""

        while True:

            try:

                # In production, fetch from threat intelligence feeds

                # For now, simulate updates



                # Add some sample malicious IPs

                sample_malicious_ips = ["192.168.1.100", "10.0.0.50"]

                self.threat_indicators["malicious_ips"].update(sample_malicious_ips)



                # Add suspicious patterns

                sample_patterns = [

                    r"admin.*password",

                    r"select.*from.*users",

                    r"<script.*>.*</script>"

                ]

                self.threat_indicators["suspicious_patterns"].update(sample_patterns)



                self.logger.debug("Threat intelligence updated")



                await asyncio.sleep(3600)  # Update every hour



            except Exception as e:

                self.logger.error(f"Threat intelligence update failed: {e}")

                await asyncio.sleep(1800)



    async def _model_retraining_loop(self):

        """Retrain ML models periodically"""

        while True:

            try:

                await asyncio.sleep(self.config["ml_model_retrain_interval"])



                # Retrain anomaly detection model

                await self._retrain_anomaly_detector()



                self.logger.info("ML models retrained")



            except Exception as e:

                self.logger.error(f"Model retraining failed: {e}")

                await asyncio.sleep(3600)



    async def _incident_management_loop(self):

        """Manage security incidents"""

        while True:

            try:

                current_time = datetime.now()



                # Check for incidents that need attention

                for incident in self.security_incidents.values():

                    if incident.status == "open":

                        # Check if incident is old and needs escalation

                        age = (current_time - incident.created_at).total_seconds()



                        if age > 3600:  # 1 hour

                            self.logger.warning(f"Incident requires attention: {incident.incident_id}")



                await asyncio.sleep(600)  # Check every 10 minutes



            except Exception as e:

                self.logger.error(f"Incident management loop failed: {e}")

                await asyncio.sleep(300)



    # ML Model Management

    async def _initialize_ml_models(self):

        """Initialize ML models"""

        try:

            # Initialize anomaly detector

            self.anomaly_detector = IsolationForest(

                contamination=0.1,

                random_state=42,

                n_estimators=100

            )



            # Initialize threat classifier

            self.threat_classifier = RandomForestClassifier(

                n_estimators=100,

                random_state=42

            )



            # Train with sample data if available

            await self._train_initial_models()



            self.logger.info("ML models initialized")



        except Exception as e:

            self.logger.error(f"ML model initialization failed: {e}")



    async def _train_initial_models(self):

        """Train models with initial data"""

        try:

            # Generate sample training data

            sample_features = []

            sample_labels = []



            # Create normal behavior samples

            for _ in range(1000):

                features = self._generate_sample_features(is_anomaly=False)

                sample_features.append(features)

                sample_labels.append(1)  # Normal



            # Create anomalous behavior samples

            for _ in range(100):

                features = self._generate_sample_features(is_anomaly=True)

                sample_features.append(features)

                sample_labels.append(-1)  # Anomaly



            # Train anomaly detector

            self.scaler.fit(sample_features)

            features_scaled = self.scaler.transform(sample_features)

            self.anomaly_detector.fit(features_scaled)



            self.logger.info("Initial model training completed")



        except Exception as e:

            self.logger.error(f"Initial model training failed: {e}")



    def _generate_sample_features(self, is_anomaly: bool = False) -> List[float]:

        """Generate sample features for training"""

        # Event type features (one-hot encoded)

        event_type_features = [0.0] * len(SecurityEventType)

        event_type_features[np.random.randint(0, len(SecurityEventType))] = 1.0



        # Time features

        if is_anomaly:

            hour = np.random.choice([2, 3, 4, 23, 0, 1])  # Unusual hours

            weekday = np.random.randint(0, 7)

        else:

            hour = np.random.choice([9, 10, 11, 14, 15, 16])  # Business hours

            weekday = np.random.randint(0, 5)  # Weekdays



        # IP features

        ip_features = [

            1.0 if not is_anomaly else 0.0,  # is_private

            np.random.uniform(0, 1),  # octet1

            np.random.uniform(0, 1),  # octet2

            np.random.uniform(0, 1),  # octet3

            np.random.uniform(0, 1)   # octet4

        ]



        # Risk score

        risk_score = np.random.uniform(0.8, 1.0) if is_anomaly else np.random.uniform(0.0, 0.3)



        # Details features

        failed_attempts = np.random.randint(5, 20) if is_anomaly else np.random.randint(0, 2)

        data_size = np.random.uniform(0.8, 1.0) if is_anomaly else np.random.uniform(0.0, 0.2)

        threat_indicators = np.random.randint(3, 10) if is_anomaly else np.random.randint(0, 1)



        return (event_type_features + [hour, weekday] + ip_features +

                [risk_score, failed_attempts, data_size, threat_indicators])



    async def _retrain_anomaly_detector(self):

        """Retrain anomaly detection model"""

        try:

            # Extract features from recent events

            recent_events = list(self.security_events)[-10000:]  # Last 10k events



            if len(recent_events) < 100:

                return



            features = []

            for event in recent_events:

                event_features = self._extract_event_features(event)

                if event_features:

                    features.append(event_features)



            if len(features) < 100:

                return



            # Retrain scaler and model

            self.scaler.fit(features)

            features_scaled = self.scaler.transform(features)

            self.anomaly_detector.fit(features_scaled)



            self.logger.info(f"Anomaly detector retrained with {len(features)} samples")



        except Exception as e:

            self.logger.error(f"Anomaly detector retraining failed: {e}")



    # Data Management

    async def _load_threat_intelligence(self):

        """Load threat intelligence data"""

        try:

            # In production, load from threat intelligence feeds

            # For now, initialize with sample data



            self.threat_indicators["malicious_ips"] = {

                "192.168.1.100", "10.0.0.50", "172.16.0.100"

            }



            self.threat_indicators["malicious_domains"] = {

                "malicious-site.com", "phishing-example.org"

            }



            self.threat_indicators["suspicious_patterns"] = {

                r"union\s+select", r"<script.*>", r"admin.*password"

            }



            self.logger.info("Threat intelligence loaded")



        except Exception as e:

            self.logger.error(f"Threat intelligence loading failed: {e}")



    async def _load_security_rules(self):

        """Load security rules"""

        try:

            # Sample security rules

            self.security_rules = {

                "brute_force_detection": {

                    "threat_type": "brute_force",

                    "threat_level": 3,

                    "conditions": {

                        "event_type": ["login_attempt"],

                        "min_risk_score": 0.6

                    },

                    "actions": ["block_ip", "alert"],

                    "confidence": 0.9

                },

                "sql_injection_detection": {

                    "threat_type": "sql_injection",

                    "threat_level": 4,

                    "conditions": {

                        "event_type": ["api_request"],

                        "action": r".*select.*from.*"

                    },

                    "actions": ["block_ip", "alert", "monitor_enhanced"],

                    "confidence": 0.95

                },

                "off_hours_access": {

                    "threat_type": "anomalous_behavior",

                    "threat_level": 2,

                    "conditions": {

                        "time_window": {"start": 22, "end": 6}

                    },

                    "actions": ["require_mfa", "monitor_enhanced"],

                    "confidence": 0.7

                }

            }



            self.logger.info("Security rules loaded")



        except Exception as e:

            self.logger.error(f"Security rules loading failed: {e}")



    # API Methods

    async def get_security_dashboard(self) -> Dict[str, Any]:

        """Get security dashboard data"""

        try:

            current_time = datetime.now()



            # Recent threats (last 24 hours)

            recent_detections = [

                d for d in self.threat_detections.values()

                if (current_time - d.created_at).total_seconds() < 86400

            ]



            # Threat level distribution

            threat_levels = defaultdict(int)

            for detection in recent_detections:

                threat_levels[detection.threat_level.value] += 1



            # Top threat types

            threat_types = defaultdict(int)

            for detection in recent_detections:

                threat_types[detection.threat_type.value] += 1



            # Security metrics

            total_events = len(self.security_events)

            high_risk_events = len([e for e in self.security_events if e.risk_score > 0.7])



            return {

                "timestamp": current_time.isoformat(),

                "threats": {

                    "total_detections": len(self.threat_detections),

                    "recent_24h": len(recent_detections),

                    "threat_levels": dict(threat_levels),

                    "threat_types": dict(threat_types)

                },

                "events": {

                    "total_events": total_events,

                    "high_risk_events": high_risk_events,

                    "risk_percentage": (high_risk_events / total_events * 100) if total_events > 0 else 0

                },

                "incidents": {

                    "total_incidents": len(self.security_incidents),

                    "open_incidents": len([i for i in self.security_incidents.values() if i.status == "open"])

                },

                "security_status": {

                    "blocked_ips": len(self.blocked_ips),

                    "disabled_users": len(self.disabled_users),

                    "active_sessions": len(self.active_sessions)

                },

                "ml_models": {

                    "anomaly_detector_trained": self.anomaly_detector is not None,

                    "threat_classifier_trained": self.threat_classifier is not None

                }

            }



        except Exception as e:

            self.logger.error(f"Security dashboard generation failed: {e}")

            return {"error": str(e)}



    async def get_threat_analysis(self, time_range_hours: int = 24) -> Dict[str, Any]:

        """Get detailed threat analysis"""

        try:

            cutoff_time = datetime.now() - timedelta(hours=time_range_hours)



            # Get recent detections

            recent_detections = [

                d for d in self.threat_detections.values()

                if d.created_at > cutoff_time

            ]



            # Analyze patterns

            analysis = {

                "time_range_hours": time_range_hours,

                "total_detections": len(recent_detections),

                "threat_trends": self._analyze_threat_trends(recent_detections),

                "top_indicators": self._analyze_top_indicators(recent_detections),

                "affected_resources": self._analyze_affected_resources(recent_detections),

                "response_effectiveness": self._analyze_response_effectiveness(recent_detections),

                "recommendations": self._generate_security_recommendations(recent_detections)

            }



            return analysis



        except Exception as e:

            self.logger.error(f"Threat analysis failed: {e}")

            return {"error": str(e)}



    def _analyze_threat_trends(self, detections: List[ThreatDetection]) -> Dict[str, Any]:

        """Analyze threat trends"""

        try:

            # Group by hour

            hourly_counts = defaultdict(int)

            for detection in detections:

                hour_key = detection.created_at.strftime("%Y-%m-%d %H:00")

                hourly_counts[hour_key] += 1



            # Calculate trend

            hours = sorted(hourly_counts.keys())

            counts = [hourly_counts[hour] for hour in hours]



            if len(counts) > 1:

                trend = "increasing" if counts[-1] > counts[0] else "decreasing" if counts[-1] < counts[0] else "stable"

            else:

                trend = "insufficient_data"



            return {

                "hourly_distribution": dict(hourly_counts),

                "trend": trend,

                "peak_hour": max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else None

            }



        except Exception as e:

            self.logger.error(f"Threat trend analysis failed: {e}")

            return {}



    def _analyze_top_indicators(self, detections: List[ThreatDetection]) -> List[Dict[str, Any]]:

        """Analyze top threat indicators"""

        try:

            indicator_counts = defaultdict(int)



            for detection in detections:

                for indicator in detection.indicators:

                    indicator_counts[indicator] += 1



            # Get top 10 indicators

            top_indicators = sorted(

                indicator_counts.items(),

                key=lambda x: x[1],

                reverse=True

            )[:10]



            return [

                {"indicator": indicator, "count": count}

                for indicator, count in top_indicators

            ]



        except Exception as e:

            self.logger.error(f"Top indicators analysis failed: {e}")

            return []



    def _analyze_affected_resources(self, detections: List[ThreatDetection]) -> Dict[str, Any]:

        """Analyze affected resources"""

        try:

            resource_counts = defaultdict(int)



            for detection in detections:

                for resource in detection.affected_resources:

                    resource_counts[resource] += 1



            # Get top 10 resources

            top_resources = sorted(

                resource_counts.items(),

                key=lambda x: x[1],

                reverse=True

            )[:10]



            return {

                "total_unique_resources": len(resource_counts),

                "top_targeted_resources": [

                    {"resource": resource, "threat_count": count}

                    for resource, count in top_resources

                ]

            }



        except Exception as e:

            self.logger.error(f"Affected resources analysis failed: {e}")

            return {}



    def _analyze_response_effectiveness(self, detections: List[ThreatDetection]) -> Dict[str, Any]:

        """Analyze response effectiveness"""

        try:

            action_counts = defaultdict(int)



            for detection in detections:

                for action in detection.recommended_actions:

                    action_counts[action.value] += 1



            return {

                "total_actions_recommended": sum(action_counts.values()),

                "action_distribution": dict(action_counts),

                "most_common_action": max(action_counts.items(), key=lambda x: x[1])[0] if action_counts else None

            }



        except Exception as e:

            self.logger.error(f"Response effectiveness analysis failed: {e}")

            return {}



    def _generate_security_recommendations(self, detections: List[ThreatDetection]) -> List[str]:

        """Generate security recommendations"""

        try:

            recommendations = []



            # Analyze threat patterns

            threat_types = defaultdict(int)

            for detection in detections:

                threat_types[detection.threat_type.value] += 1



            # Generate recommendations based on patterns

            if threat_types.get("brute_force", 0) > 5:

                recommendations.append("Consider implementing stronger password policies and account lockout mechanisms")



            if threat_types.get("sql_injection", 0) > 2:

                recommendations.append("Review and strengthen input validation and parameterized queries")



            if threat_types.get("anomalous_behavior", 0) > 10:

                recommendations.append("Consider implementing user behavior analytics and adaptive authentication")



            # High-level recommendations

            high_confidence_detections = [d for d in detections if d.confidence_score > 0.9]

            if len(high_confidence_detections) > len(detections) * 0.3:

                recommendations.append("High confidence threat detection rate suggests need for immediate security review")



            return recommendations



        except Exception as e:

            self.logger.error(f"Security recommendations generation failed: {e}")

            return []



    async def shutdown(self):

        """Shutdown AI security system"""

        # Save models

        if self.anomaly_detector:

            try:

                joblib.dump(self.anomaly_detector, "anomaly_detector.pkl")

                joblib.dump(self.scaler, "feature_scaler.pkl")

            except Exception as e:

                self.logger.error(f"Model saving failed: {e}")



        self.logger.info("AI Security and Threat Detection System shutdown complete")

# Example usage

async def main():

    """Example usage of AI security system"""

    security_ai = AISecurityThreatDetection()

    await security_ai.initialize()



    # Process sample security events

    sample_events = [

        {

            "event_type": "login_attempt",

            "source_ip": "192.168.1.100",

            "user_id": "user123",

            "resource": "admin_panel",

            "action": "login",

            "details": {"success": False, "failed_attempts": 5}

        },

        {

            "event_type": "api_request",

            "source_ip": "10.0.0.50",

            "user_id": "user456",

            "resource": "database",

            "action": "SELECT * FROM users WHERE id=1 OR 1=1",

            "details": {"method": "POST", "response_code": 200}

        }

    ]



    for event_data in sample_events:

        event = await security_ai.process_security_event(event_data)

        print(f"Event processed: {event.event_id} (risk: {event.risk_score:.2f})")



    # Get security dashboard

    dashboard = await security_ai.get_security_dashboard()

    print(f"Security Dashboard: {dashboard}")



    # Get threat analysis

    analysis = await security_ai.get_threat_analysis(24)

    print(f"Threat Analysis: {analysis}")

if __name__ == "__main__":

    asyncio.run(main())
