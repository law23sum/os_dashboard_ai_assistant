"""
Security Monitor - Real-time security monitoring and threat detection
Handles security events, anomaly detection, and incident response
"""

import asyncio
from typing import Dict, List, Any, Optional, Union, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import json
import logging
from pathlib import Path
import uuid
import hashlib
from collections import defaultdict, Counter, deque
import re
import ipaddress

from assistant_core.data_aggregator import CIRDocument, DocumentType, SourceType


class ThreatLevel(Enum):
    """Security threat levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecurityEventType(Enum):
    """Types of security events"""
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_LOCKED = "account_locked"
    
    # Authorization events
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    
    # Data access events
    DATA_ACCESS = "data_access"
    DATA_EXPORT = "data_export"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    
    # System events
    SYSTEM_ACCESS = "system_access"
    CONFIGURATION_CHANGE = "configuration_change"
    SERVICE_START = "service_start"
    SERVICE_STOP = "service_stop"
    
    # Network events
    SUSPICIOUS_IP = "suspicious_ip"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNUSUAL_TRAFFIC = "unusual_traffic"
    
    # Malicious activity
    BRUTE_FORCE_ATTACK = "brute_force_attack"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    MALWARE_DETECTED = "malware_detected"
    
    # Anomalies
    UNUSUAL_BEHAVIOR = "unusual_behavior"
    ANOMALOUS_ACCESS_PATTERN = "anomalous_access_pattern"
    SUSPICIOUS_FILE_ACCESS = "suspicious_file_access"


class IncidentStatus(Enum):
    """Security incident status"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    timestamp: datetime
    source_ip: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    geolocation: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "event_type": self.event_type.value,
            "threat_level": self.threat_level.value,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class SecurityIncident:
    """Security incident record"""
    incident_id: str
    title: str
    description: str
    threat_level: ThreatLevel
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str] = None
    events: List[str] = field(default_factory=list)  # Event IDs
    indicators: List[str] = field(default_factory=list)
    mitigation_steps: List[str] = field(default_factory=list)
    resolution_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "threat_level": self.threat_level.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class ThreatIndicator:
    """Threat indicator for detection"""
    indicator_id: str
    indicator_type: str  # ip, domain, hash, pattern
    value: str
    threat_level: ThreatLevel
    description: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    source: str = "internal"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "threat_level": self.threat_level.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }


@dataclass
class AnomalyPattern:
    """Anomaly detection pattern"""
    pattern_id: str
    name: str
    description: str
    pattern_type: str  # behavioral, statistical, rule-based
    threshold: float
    time_window_minutes: int
    conditions: Dict[str, Any]
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ThreatDetector:
    """Threat detection engine"""
    
    def __init__(self):
        self.threat_indicators: Dict[str, ThreatIndicator] = {}
        self.anomaly_patterns: Dict[str, AnomalyPattern] = {}
        self.detection_rules: List[Callable] = []
        
        # Known malicious patterns
        self.malicious_patterns = {
            "sql_injection": [
                r"(\bunion\b.*\bselect\b)",
                r"(\bselect\b.*\bfrom\b.*\bwhere\b.*['\"].*['\"])",
                r"(\bdrop\b.*\btable\b)",
                r"(\binsert\b.*\binto\b.*\bvalues\b)"
            ],
            "xss": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>.*?</iframe>"
            ],
            "path_traversal": [
                r"\.\./",
                r"\.\.\\",
                r"%2e%2e%2f",
                r"%2e%2e%5c"
            ]
        }
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize threat detector"""
        try:
            # Load default threat indicators
            await self._load_default_indicators()
            
            # Load anomaly patterns
            await self._load_anomaly_patterns()
            
            # Initialize detection rules
            await self._initialize_detection_rules()
            
            self.logger.info("Threat detector initialized")
            
        except Exception as e:
            self.logger.error(f"Threat detector initialization failed: {e}")
            raise
    
    async def _load_default_indicators(self):
        """Load default threat indicators"""
        try:
            # Known malicious IPs (example)
            malicious_ips = [
                "192.168.1.100",  # Example malicious IP
                "10.0.0.50"       # Example suspicious IP
            ]
            
            for ip in malicious_ips:
                indicator = ThreatIndicator(
                    indicator_id=str(uuid.uuid4()),
                    indicator_type="ip",
                    value=ip,
                    threat_level=ThreatLevel.HIGH,
                    description=f"Known malicious IP: {ip}",
                    created_at=datetime.utcnow(),
                    source="threat_intelligence"
                )
                self.threat_indicators[indicator.indicator_id] = indicator
            
            self.logger.info(f"Loaded {len(malicious_ips)} threat indicators")
            
        except Exception as e:
            self.logger.error(f"Failed to load threat indicators: {e}")
    
    async def _load_anomaly_patterns(self):
        """Load anomaly detection patterns"""
        try:
            patterns = [
                AnomalyPattern(
                    pattern_id="failed_login_burst",
                    name="Failed Login Burst",
                    description="Multiple failed login attempts in short time",
                    pattern_type="behavioral",
                    threshold=5.0,
                    time_window_minutes=5,
                    conditions={
                        "event_type": "login_failure",
                        "min_count": 5,
                        "same_ip": True
                    }
                ),
                AnomalyPattern(
                    pattern_id="unusual_access_time",
                    name="Unusual Access Time",
                    description="Access outside normal business hours",
                    pattern_type="behavioral",
                    threshold=0.8,
                    time_window_minutes=60,
                    conditions={
                        "business_hours": {"start": 8, "end": 18},
                        "weekdays_only": True
                    }
                ),
                AnomalyPattern(
                    pattern_id="privilege_escalation",
                    name="Privilege Escalation",
                    description="User accessing resources above their role",
                    pattern_type="rule-based",
                    threshold=1.0,
                    time_window_minutes=10,
                    conditions={
                        "check_permissions": True,
                        "alert_on_violation": True
                    }
                ),
                AnomalyPattern(
                    pattern_id="data_exfiltration",
                    name="Data Exfiltration",
                    description="Large volume of data export",
                    pattern_type="statistical",
                    threshold=100.0,  # MB
                    time_window_minutes=30,
                    conditions={
                        "event_type": "data_export",
                        "volume_threshold_mb": 100
                    }
                )
            ]
            
            for pattern in patterns:
                self.anomaly_patterns[pattern.pattern_id] = pattern
            
            self.logger.info(f"Loaded {len(patterns)} anomaly patterns")
            
        except Exception as e:
            self.logger.error(f"Failed to load anomaly patterns: {e}")
    
    async def _initialize_detection_rules(self):
        """Initialize detection rules"""
        try:
            # Add detection rule functions
            self.detection_rules = [
                self._detect_brute_force,
                self._detect_malicious_patterns,
                self._detect_suspicious_ips,
                self._detect_anomalous_behavior
            ]
            
            self.logger.info(f"Initialized {len(self.detection_rules)} detection rules")
            
        except Exception as e:
            self.logger.error(f"Detection rules initialization failed: {e}")
    
    async def analyze_event(self, event: SecurityEvent) -> List[SecurityEvent]:
        """Analyze event for threats and anomalies"""
        try:
            additional_events = []
            
            # Run detection rules
            for rule in self.detection_rules:
                try:
                    detected_events = await rule(event)
                    if detected_events:
                        additional_events.extend(detected_events)
                except Exception as e:
                    self.logger.error(f"Detection rule failed: {e}")
            
            return additional_events
            
        except Exception as e:
            self.logger.error(f"Event analysis failed: {e}")
            return []
    
    async def _detect_brute_force(self, event: SecurityEvent) -> List[SecurityEvent]:
        """Detect brute force attacks"""
        if event.event_type != SecurityEventType.LOGIN_FAILURE:
            return []
        
        # This would check recent failed attempts from same IP
        # For now, return empty list
        return []
    
    async def _detect_malicious_patterns(self, event: SecurityEvent) -> List[SecurityEvent]:
        """Detect malicious patterns in requests"""
        additional_events = []
        
        try:
            # Check for SQL injection patterns
            if "request_data" in event.details:
                request_data = str(event.details["request_data"]).lower()
                
                for pattern in self.malicious_patterns["sql_injection"]:
                    if re.search(pattern, request_data, re.IGNORECASE):
                        sql_event = SecurityEvent(
                            event_id=str(uuid.uuid4()),
                            event_type=SecurityEventType.SQL_INJECTION_ATTEMPT,
                            threat_level=ThreatLevel.HIGH,
                            timestamp=datetime.utcnow(),
                            source_ip=event.source_ip,
                            user_id=event.user_id,
                            username=event.username,
                            details={
                                "original_event_id": event.event_id,
                                "pattern_matched": pattern,
                                "request_data": request_data[:500]  # Truncate for storage
                            }
                        )
                        additional_events.append(sql_event)
                        break
                
                # Check for XSS patterns
                for pattern in self.malicious_patterns["xss"]:
                    if re.search(pattern, request_data, re.IGNORECASE):
                        xss_event = SecurityEvent(
                            event_id=str(uuid.uuid4()),
                            event_type=SecurityEventType.XSS_ATTEMPT,
                            threat_level=ThreatLevel.MEDIUM,
                            timestamp=datetime.utcnow(),
                            source_ip=event.source_ip,
                            user_id=event.user_id,
                            username=event.username,
                            details={
                                "original_event_id": event.event_id,
                                "pattern_matched": pattern,
                                "request_data": request_data[:500]
                            }
                        )
                        additional_events.append(xss_event)
                        break
            
        except Exception as e:
            self.logger.error(f"Malicious pattern detection failed: {e}")
        
        return additional_events
    
    async def _detect_suspicious_ips(self, event: SecurityEvent) -> List[SecurityEvent]:
        """Detect suspicious IP addresses"""
        additional_events = []
        
        try:
            # Check against threat indicators
            for indicator in self.threat_indicators.values():
                if (indicator.indicator_type == "ip" and 
                    indicator.value == event.source_ip and
                    (not indicator.expires_at or indicator.expires_at > datetime.utcnow())):
                    
                    suspicious_event = SecurityEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=SecurityEventType.SUSPICIOUS_IP,
                        threat_level=indicator.threat_level,
                        timestamp=datetime.utcnow(),
                        source_ip=event.source_ip,
                        user_id=event.user_id,
                        username=event.username,
                        details={
                            "original_event_id": event.event_id,
                            "indicator_id": indicator.indicator_id,
                            "indicator_description": indicator.description
                        }
                    )
                    additional_events.append(suspicious_event)
                    break
            
        except Exception as e:
            self.logger.error(f"Suspicious IP detection failed: {e}")
        
        return additional_events
    
    async def _detect_anomalous_behavior(self, event: SecurityEvent) -> List[SecurityEvent]:
        """Detect anomalous behavior patterns"""
        additional_events = []
        
        try:
            # Check unusual access time
            current_hour = event.timestamp.hour
            is_weekend = event.timestamp.weekday() >= 5
            
            if (current_hour < 8 or current_hour > 18) or is_weekend:
                if event.event_type == SecurityEventType.LOGIN_SUCCESS:
                    anomaly_event = SecurityEvent(
                        event_id=str(uuid.uuid4()),
                        event_type=SecurityEventType.UNUSUAL_BEHAVIOR,
                        threat_level=ThreatLevel.LOW,
                        timestamp=datetime.utcnow(),
                        source_ip=event.source_ip,
                        user_id=event.user_id,
                        username=event.username,
                        details={
                            "original_event_id": event.event_id,
                            "anomaly_type": "unusual_access_time",
                            "access_hour": current_hour,
                            "is_weekend": is_weekend
                        }
                    )
                    additional_events.append(anomaly_event)
            
        except Exception as e:
            self.logger.error(f"Anomalous behavior detection failed: {e}")
        
        return additional_events


class SecurityMonitor:
    """Security monitoring and incident management system"""
    
    def __init__(self):
        # Event storage
        self.security_events: Dict[str, SecurityEvent] = {}
        self.security_incidents: Dict[str, SecurityIncident] = {}
        
        # Threat detection
        self.threat_detector = ThreatDetector()
        
        # Event processing
        self.event_queue: deque = deque()
        self.processing_active = False
        
        # Rate limiting
        self.rate_limits: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "requests": deque(),
            "limit": 100,
            "window_minutes": 15
        })
        
        # Alerting
        self.alert_handlers: List[Callable] = []
        
        # Metrics
        self.security_metrics = {
            "events_processed": 0,
            "incidents_created": 0,
            "threats_detected": 0,
            "false_positives": 0
        }
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize security monitor"""
        try:
            self.logger.info("Initializing Security Monitor...")
            
            # Initialize threat detector
            await self.threat_detector.initialize()
            
            # Start event processing
            await self._start_event_processing()
            
            self.logger.info("Security Monitor initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Security Monitor: {e}")
            raise
    
    async def _start_event_processing(self):
        """Start background event processing"""
        try:
            if not self.processing_active:
                self.processing_active = True
                asyncio.create_task(self._process_events())
                self.logger.info("Event processing started")
            
        except Exception as e:
            self.logger.error(f"Failed to start event processing: {e}")
    
    async def _process_events(self):
        """Process security events from queue"""
        while self.processing_active:
            try:
                if self.event_queue:
                    event = self.event_queue.popleft()
                    await self._process_single_event(event)
                else:
                    await asyncio.sleep(1)  # Wait for events
                    
            except Exception as e:
                self.logger.error(f"Event processing error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_single_event(self, event: SecurityEvent):
        """Process a single security event"""
        try:
            # Store event
            self.security_events[event.event_id] = event
            
            # Analyze for threats
            additional_events = await self.threat_detector.analyze_event(event)
            
            # Process additional events
            for additional_event in additional_events:
                self.security_events[additional_event.event_id] = additional_event
                
                # Check if incident should be created
                if additional_event.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
                    await self._create_incident_if_needed(additional_event)
            
            # Update metrics
            self.security_metrics["events_processed"] += 1
            if additional_events:
                self.security_metrics["threats_detected"] += len(additional_events)
            
            # Send alerts for high-priority events
            if event.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
                await self._send_alert(event)
            
        except Exception as e:
            self.logger.error(f"Single event processing failed: {e}")
    
    # Event logging
    async def log_security_event(self, event_type: SecurityEventType, 
                                source_ip: str, threat_level: ThreatLevel = ThreatLevel.INFO,
                                user_id: Optional[str] = None, username: Optional[str] = None,
                                resource: Optional[str] = None, action: Optional[str] = None,
                                details: Optional[Dict[str, Any]] = None,
                                user_agent: Optional[str] = None,
                                session_id: Optional[str] = None) -> SecurityEvent:
        """Log security event"""
        try:
            event = SecurityEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                threat_level=threat_level,
                timestamp=datetime.utcnow(),
                source_ip=source_ip,
                user_id=user_id,
                username=username,
                resource=resource,
                action=action,
                details=details or {},
                user_agent=user_agent,
                session_id=session_id
            )
            
            # Add to processing queue
            self.event_queue.append(event)
            
            return event
            
        except Exception as e:
            self.logger.error(f"Security event logging failed: {e}")
            raise
    
    # Rate limiting
    async def check_rate_limit(self, identifier: str, limit: Optional[int] = None,
                             window_minutes: Optional[int] = None) -> bool:
        """Check if identifier exceeds rate limit"""
        try:
            rate_data = self.rate_limits[identifier]
            
            # Update limits if provided
            if limit is not None:
                rate_data["limit"] = limit
            if window_minutes is not None:
                rate_data["window_minutes"] = window_minutes
            
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=rate_data["window_minutes"])
            
            # Clean old requests
            while rate_data["requests"] and rate_data["requests"][0] < window_start:
                rate_data["requests"].popleft()
            
            # Check limit
            if len(rate_data["requests"]) >= rate_data["limit"]:
                # Log rate limit exceeded event
                await self.log_security_event(
                    event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
                    source_ip=identifier,
                    threat_level=ThreatLevel.MEDIUM,
                    details={
                        "requests_count": len(rate_data["requests"]),
                        "limit": rate_data["limit"],
                        "window_minutes": rate_data["window_minutes"]
                    }
                )
                return False
            
            # Add current request
            rate_data["requests"].append(now)
            return True
            
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {e}")
            return True  # Allow on error
    
    # Incident management
    async def _create_incident_if_needed(self, event: SecurityEvent):
        """Create security incident if needed"""
        try:
            # Check if similar incident already exists
            existing_incident = await self._find_similar_incident(event)
            
            if existing_incident:
                # Add event to existing incident
                existing_incident.events.append(event.event_id)
                existing_incident.updated_at = datetime.utcnow()
            else:
                # Create new incident
                incident = SecurityIncident(
                    incident_id=str(uuid.uuid4()),
                    title=f"{event.event_type.value.replace('_', ' ').title()} - {event.source_ip}",
                    description=f"Security incident detected: {event.event_type.value}",
                    threat_level=event.threat_level,
                    status=IncidentStatus.OPEN,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    events=[event.event_id]
                )
                
                self.security_incidents[incident.incident_id] = incident
                self.security_metrics["incidents_created"] += 1
                
                self.logger.warning(f"Security incident created: {incident.title}")
            
        except Exception as e:
            self.logger.error(f"Incident creation failed: {e}")
    
    async def _find_similar_incident(self, event: SecurityEvent) -> Optional[SecurityIncident]:
        """Find similar open incident"""
        try:
            for incident in self.security_incidents.values():
                if (incident.status in [IncidentStatus.OPEN, IncidentStatus.INVESTIGATING] and
                    incident.threat_level == event.threat_level):
                    
                    # Check if incident involves same IP or user
                    incident_events = [self.security_events.get(eid) for eid in incident.events]
                    incident_events = [e for e in incident_events if e]
                    
                    for inc_event in incident_events:
                        if (inc_event.source_ip == event.source_ip or
                            (inc_event.user_id and inc_event.user_id == event.user_id)):
                            return incident
            
            return None
            
        except Exception as e:
            self.logger.error(f"Similar incident search failed: {e}")
            return None
    
    async def update_incident_status(self, incident_id: str, 
                                   status: IncidentStatus,
                                   resolution_notes: Optional[str] = None) -> bool:
        """Update incident status"""
        try:
            incident = self.security_incidents.get(incident_id)
            if not incident:
                return False
            
            incident.status = status
            incident.updated_at = datetime.utcnow()
            
            if resolution_notes:
                incident.resolution_notes = resolution_notes
            
            self.logger.info(f"Incident status updated: {incident_id} -> {status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Incident status update failed: {e}")
            return False
    
    # Alerting
    async def _send_alert(self, event: SecurityEvent):
        """Send security alert"""
        try:
            alert_data = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "threat_level": event.threat_level.value,
                "timestamp": event.timestamp.isoformat(),
                "source_ip": event.source_ip,
                "username": event.username,
                "details": event.details
            }
            
            # Call alert handlers
            for handler in self.alert_handlers:
                try:
                    await handler(alert_data)
                except Exception as e:
                    self.logger.error(f"Alert handler failed: {e}")
            
            self.logger.info(f"Security alert sent: {event.event_type.value}")
            
        except Exception as e:
            self.logger.error(f"Alert sending failed: {e}")
    
    def add_alert_handler(self, handler: Callable):
        """Add alert handler function"""
        self.alert_handlers.append(handler)
    
    # Queries and reporting
    async def get_security_events(self, limit: int = 100, 
                                threat_level: Optional[ThreatLevel] = None,
                                event_type: Optional[SecurityEventType] = None,
                                start_time: Optional[datetime] = None,
                                end_time: Optional[datetime] = None) -> List[SecurityEvent]:
        """Get security events with filters"""
        try:
            events = list(self.security_events.values())
            
            # Apply filters
            if threat_level:
                events = [e for e in events if e.threat_level == threat_level]
            
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            if start_time:
                events = [e for e in events if e.timestamp >= start_time]
            
            if end_time:
                events = [e for e in events if e.timestamp <= end_time]
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x.timestamp, reverse=True)
            
            return events[:limit]
            
        except Exception as e:
            self.logger.error(f"Security events query failed: {e}")
            return []
    
    async def get_security_incidents(self, status: Optional[IncidentStatus] = None) -> List[SecurityIncident]:
        """Get security incidents"""
        try:
            incidents = list(self.security_incidents.values())
            
            if status:
                incidents = [i for i in incidents if i.status == status]
            
            # Sort by created date (newest first)
            incidents.sort(key=lambda x: x.created_at, reverse=True)
            
            return incidents
            
        except Exception as e:
            self.logger.error(f"Security incidents query failed: {e}")
            return []
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get security monitoring metrics"""
        try:
            now = datetime.utcnow()
            
            # Event statistics
            recent_events = [e for e in self.security_events.values() 
                           if e.timestamp > now - timedelta(hours=24)]
            
            threat_distribution = Counter(e.threat_level for e in recent_events)
            event_type_distribution = Counter(e.event_type for e in recent_events)
            
            # Incident statistics
            open_incidents = len([i for i in self.security_incidents.values() 
                                if i.status in [IncidentStatus.OPEN, IncidentStatus.INVESTIGATING]])
            
            return {
                "events": {
                    "total": len(self.security_events),
                    "recent_24h": len(recent_events),
                    "threat_distribution": {level.value: count for level, count in threat_distribution.items()},
                    "type_distribution": {etype.value: count for etype, count in event_type_distribution.items()}
                },
                "incidents": {
                    "total": len(self.security_incidents),
                    "open": open_incidents,
                    "status_distribution": Counter(i.status for i in self.security_incidents.values())
                },
                "processing": {
                    "queue_size": len(self.event_queue),
                    "processing_active": self.processing_active
                },
                "metrics": self.security_metrics,
                "metrics_timestamp": now.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get security metrics: {e}")
            return {}
    
    async def stop(self):
        """Stop security monitoring"""
        try:
            self.processing_active = False
            self.logger.info("Security Monitor stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop Security Monitor: {e}")