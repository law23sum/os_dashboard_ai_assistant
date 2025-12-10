"""
Governance Engine - Policy management, compliance monitoring, and regulatory frameworks
Handles data governance, access policies, audit trails, and compliance reporting
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
from collections import defaultdict, Counter
import re

from assistant_core.data_aggregator import CIRDocument, DocumentType, SourceType


class PolicyType(Enum):
    """Types of governance policies"""
    DATA_RETENTION = "data_retention"
    ACCESS_CONTROL = "access_control"
    DATA_CLASSIFICATION = "data_classification"
    PRIVACY = "privacy"
    SECURITY = "security"
    AUDIT = "audit"
    BACKUP = "backup"
    ENCRYPTION = "encryption"
    INCIDENT_RESPONSE = "incident_response"
    BUSINESS_CONTINUITY = "business_continuity"


class ComplianceFramework(Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"  # General Data Protection Regulation
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    SOX = "sox"  # Sarbanes-Oxley Act
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    ISO_27001 = "iso_27001"  # Information Security Management
    NIST = "nist"  # National Institute of Standards and Technology
    CCPA = "ccpa"  # California Consumer Privacy Act
    SOC2 = "soc2"  # Service Organization Control 2
    FISMA = "fisma"  # Federal Information Security Management Act
    CUSTOM = "custom"


class PolicyStatus(Enum):
    """Policy lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    UNDER_REVIEW = "under_review"


class ComplianceStatus(Enum):
    """Compliance assessment status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_ASSESSMENT = "under_assessment"
    NOT_APPLICABLE = "not_applicable"


class ViolationSeverity(Enum):
    """Policy violation severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Policy:
    """Governance policy definition"""
    policy_id: str
    name: str
    description: str
    policy_type: PolicyType
    compliance_frameworks: List[ComplianceFramework]
    status: PolicyStatus
    version: str
    created_at: datetime
    updated_at: datetime
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    owner: str = ""
    approver: str = ""
    rules: List[Dict[str, Any]] = field(default_factory=list)
    exceptions: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "policy_type": self.policy_type.value,
            "compliance_frameworks": [cf.value for cf in self.compliance_frameworks],
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "effective_date": self.effective_date.isoformat(),
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None
        }


@dataclass
class PolicyViolation:
    """Policy violation record"""
    violation_id: str
    policy_id: str
    resource_id: str
    resource_type: str
    violation_type: str
    severity: ViolationSeverity
    description: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    user_id: Optional[str] = None
    automated_detection: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "severity": self.severity.value,
            "detected_at": self.detected_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }


@dataclass
class ComplianceAssessment:
    """Compliance assessment result"""
    assessment_id: str
    framework: ComplianceFramework
    assessment_date: datetime
    overall_status: ComplianceStatus
    score: float  # 0-100
    total_controls: int
    compliant_controls: int
    non_compliant_controls: int
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    assessor: str = ""
    next_assessment_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "framework": self.framework.value,
            "assessment_date": self.assessment_date.isoformat(),
            "overall_status": self.overall_status.value,
            "next_assessment_date": self.next_assessment_date.isoformat() if self.next_assessment_date else None
        }


@dataclass
class AuditTrail:
    """Audit trail entry"""
    audit_id: str
    timestamp: datetime
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class DataClassification:
    """Data classification definition"""
    classification_id: str
    name: str
    level: int  # 1=Public, 2=Internal, 3=Confidential, 4=Restricted
    description: str
    handling_requirements: List[str]
    retention_period_days: Optional[int] = None
    encryption_required: bool = False
    access_restrictions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PolicyEngine:
    """Policy management and enforcement engine"""
    
    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        self.policy_rules: Dict[str, List[Callable]] = defaultdict(list)
        self.data_classifications: Dict[str, DataClassification] = {}
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize policy engine"""
        try:
            # Load default policies
            await self._load_default_policies()
            
            # Load data classifications
            await self._load_data_classifications()
            
            # Initialize policy rules
            await self._initialize_policy_rules()
            
            self.logger.info("Policy engine initialized")
            
        except Exception as e:
            self.logger.error(f"Policy engine initialization failed: {e}")
            raise
    
    async def _load_default_policies(self):
        """Load default governance policies"""
        try:
            default_policies = [
                # Data Retention Policy
                Policy(
                    policy_id="data_retention_001",
                    name="Data Retention Policy",
                    description="Defines data retention periods and disposal procedures",
                    policy_type=PolicyType.DATA_RETENTION,
                    compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.SOX],
                    status=PolicyStatus.ACTIVE,
                    version="1.0",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    effective_date=datetime.utcnow(),
                    expiry_date=datetime.utcnow() + timedelta(days=365),
                    owner="Data Protection Officer",
                    rules=[
                        {
                            "name": "Personal Data Retention",
                            "description": "Personal data must be deleted after 7 years",
                            "condition": "data_type == 'personal'",
                            "action": "delete_after_days",
                            "parameters": {"days": 2555}  # 7 years
                        },
                        {
                            "name": "Log Data Retention",
                            "description": "System logs must be retained for 1 year",
                            "condition": "data_type == 'logs'",
                            "action": "delete_after_days",
                            "parameters": {"days": 365}
                        }
                    ]
                ),
                
                # Access Control Policy
                Policy(
                    policy_id="access_control_001",
                    name="Access Control Policy",
                    description="Defines access control requirements and procedures",
                    policy_type=PolicyType.ACCESS_CONTROL,
                    compliance_frameworks=[ComplianceFramework.ISO_27001, ComplianceFramework.SOC2],
                    status=PolicyStatus.ACTIVE,
                    version="1.0",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    effective_date=datetime.utcnow(),
                    owner="Security Officer",
                    rules=[
                        {
                            "name": "Principle of Least Privilege",
                            "description": "Users should have minimum necessary access",
                            "condition": "access_request",
                            "action": "validate_minimum_access",
                            "parameters": {"require_justification": True}
                        },
                        {
                            "name": "Regular Access Review",
                            "description": "Access rights must be reviewed quarterly",
                            "condition": "quarterly_review",
                            "action": "review_access_rights",
                            "parameters": {"frequency_days": 90}
                        }
                    ]
                ),
                
                # Data Classification Policy
                Policy(
                    policy_id="data_classification_001",
                    name="Data Classification Policy",
                    description="Defines data classification levels and handling requirements",
                    policy_type=PolicyType.DATA_CLASSIFICATION,
                    compliance_frameworks=[ComplianceFramework.ISO_27001],
                    status=PolicyStatus.ACTIVE,
                    version="1.0",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    effective_date=datetime.utcnow(),
                    owner="Data Protection Officer",
                    rules=[
                        {
                            "name": "Automatic Classification",
                            "description": "Data must be classified upon creation",
                            "condition": "data_creation",
                            "action": "classify_data",
                            "parameters": {"require_classification": True}
                        }
                    ]
                ),
                
                # Privacy Policy
                Policy(
                    policy_id="privacy_001",
                    name="Privacy Policy",
                    description="Defines privacy protection requirements",
                    policy_type=PolicyType.PRIVACY,
                    compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.CCPA],
                    status=PolicyStatus.ACTIVE,
                    version="1.0",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    effective_date=datetime.utcnow(),
                    owner="Privacy Officer",
                    rules=[
                        {
                            "name": "Consent Management",
                            "description": "Explicit consent required for personal data processing",
                            "condition": "personal_data_processing",
                            "action": "verify_consent",
                            "parameters": {"require_explicit_consent": True}
                        },
                        {
                            "name": "Data Subject Rights",
                            "description": "Support data subject access, rectification, and erasure rights",
                            "condition": "data_subject_request",
                            "action": "process_data_subject_request",
                            "parameters": {"response_time_days": 30}
                        }
                    ]
                ),
                
                # Encryption Policy
                Policy(
                    policy_id="encryption_001",
                    name="Encryption Policy",
                    description="Defines encryption requirements for data protection",
                    policy_type=PolicyType.ENCRYPTION,
                    compliance_frameworks=[ComplianceFramework.PCI_DSS, ComplianceFramework.HIPAA],
                    status=PolicyStatus.ACTIVE,
                    version="1.0",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    effective_date=datetime.utcnow(),
                    owner="Security Officer",
                    rules=[
                        {
                            "name": "Data at Rest Encryption",
                            "description": "Sensitive data must be encrypted at rest",
                            "condition": "data_classification >= 3",
                            "action": "encrypt_at_rest",
                            "parameters": {"algorithm": "AES-256", "key_rotation_days": 90}
                        },
                        {
                            "name": "Data in Transit Encryption",
                            "description": "All data transmission must be encrypted",
                            "condition": "data_transmission",
                            "action": "encrypt_in_transit",
                            "parameters": {"min_tls_version": "1.2"}
                        }
                    ]
                )
            ]
            
            for policy in default_policies:
                self.policies[policy.policy_id] = policy
            
            self.logger.info(f"Loaded {len(default_policies)} default policies")
            
        except Exception as e:
            self.logger.error(f"Failed to load default policies: {e}")
    
    async def _load_data_classifications(self):
        """Load data classification definitions"""
        try:
            classifications = [
                DataClassification(
                    classification_id="public",
                    name="Public",
                    level=1,
                    description="Information that can be freely shared",
                    handling_requirements=["No special handling required"],
                    retention_period_days=None,
                    encryption_required=False
                ),
                DataClassification(
                    classification_id="internal",
                    name="Internal",
                    level=2,
                    description="Information for internal use only",
                    handling_requirements=["Access restricted to employees"],
                    retention_period_days=2555,  # 7 years
                    encryption_required=False,
                    access_restrictions=["employee_access_only"]
                ),
                DataClassification(
                    classification_id="confidential",
                    name="Confidential",
                    level=3,
                    description="Sensitive information requiring protection",
                    handling_requirements=[
                        "Access on need-to-know basis",
                        "Encryption required",
                        "Audit trail required"
                    ],
                    retention_period_days=2555,
                    encryption_required=True,
                    access_restrictions=["authorized_personnel_only", "mfa_required"]
                ),
                DataClassification(
                    classification_id="restricted",
                    name="Restricted",
                    level=4,
                    description="Highly sensitive information with strict controls",
                    handling_requirements=[
                        "Explicit authorization required",
                        "Strong encryption required",
                        "Comprehensive audit trail",
                        "Data loss prevention controls"
                    ],
                    retention_period_days=1825,  # 5 years
                    encryption_required=True,
                    access_restrictions=[
                        "executive_approval_required",
                        "mfa_required",
                        "privileged_access_only"
                    ]
                )
            ]
            
            for classification in classifications:
                self.data_classifications[classification.classification_id] = classification
            
            self.logger.info(f"Loaded {len(classifications)} data classifications")
            
        except Exception as e:
            self.logger.error(f"Failed to load data classifications: {e}")
    
    async def _initialize_policy_rules(self):
        """Initialize policy enforcement rules"""
        try:
            # Register rule functions for each policy
            for policy in self.policies.values():
                if policy.policy_type == PolicyType.DATA_RETENTION:
                    self.policy_rules[policy.policy_id].append(self._enforce_data_retention)
                elif policy.policy_type == PolicyType.ACCESS_CONTROL:
                    self.policy_rules[policy.policy_id].append(self._enforce_access_control)
                elif policy.policy_type == PolicyType.DATA_CLASSIFICATION:
                    self.policy_rules[policy.policy_id].append(self._enforce_data_classification)
                elif policy.policy_type == PolicyType.PRIVACY:
                    self.policy_rules[policy.policy_id].append(self._enforce_privacy)
                elif policy.policy_type == PolicyType.ENCRYPTION:
                    self.policy_rules[policy.policy_id].append(self._enforce_encryption)
            
            self.logger.info("Policy rules initialized")
            
        except Exception as e:
            self.logger.error(f"Policy rules initialization failed: {e}")
    
    async def evaluate_policy_compliance(self, resource_type: str, resource_id: str,
                                       context: Dict[str, Any]) -> List[PolicyViolation]:
        """Evaluate policy compliance for a resource"""
        violations = []
        
        try:
            for policy in self.policies.values():
                if policy.status != PolicyStatus.ACTIVE:
                    continue
                
                # Check if policy applies to this resource
                if await self._policy_applies_to_resource(policy, resource_type, context):
                    # Evaluate policy rules
                    for rule_func in self.policy_rules.get(policy.policy_id, []):
                        try:
                            violation = await rule_func(policy, resource_type, resource_id, context)
                            if violation:
                                violations.append(violation)
                        except Exception as e:
                            self.logger.error(f"Policy rule evaluation failed: {e}")
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Policy compliance evaluation failed: {e}")
            return []
    
    async def _policy_applies_to_resource(self, policy: Policy, resource_type: str,
                                        context: Dict[str, Any]) -> bool:
        """Check if policy applies to resource"""
        # Simple resource type matching - can be extended
        policy_resource_types = policy.metadata.get("resource_types", [])
        
        if not policy_resource_types:
            return True  # Policy applies to all resources
        
        return resource_type in policy_resource_types
    
    # Policy enforcement rule functions
    async def _enforce_data_retention(self, policy: Policy, resource_type: str,
                                    resource_id: str, context: Dict[str, Any]) -> Optional[PolicyViolation]:
        """Enforce data retention policy"""
        try:
            # Check if data exceeds retention period
            creation_date = context.get("creation_date")
            data_type = context.get("data_type", "unknown")
            
            if not creation_date:
                return None
            
            # Find applicable retention rule
            retention_days = None
            for rule in policy.rules:
                if rule["name"] == "Personal Data Retention" and data_type == "personal":
                    retention_days = rule["parameters"]["days"]
                elif rule["name"] == "Log Data Retention" and data_type == "logs":
                    retention_days = rule["parameters"]["days"]
            
            if retention_days:
                retention_deadline = creation_date + timedelta(days=retention_days)
                if datetime.utcnow() > retention_deadline:
                    return PolicyViolation(
                        violation_id=str(uuid.uuid4()),
                        policy_id=policy.policy_id,
                        resource_id=resource_id,
                        resource_type=resource_type,
                        violation_type="data_retention_exceeded",
                        severity=ViolationSeverity.HIGH,
                        description=f"Data retention period exceeded for {data_type} data",
                        detected_at=datetime.utcnow(),
                        metadata={
                            "retention_days": retention_days,
                            "creation_date": creation_date.isoformat(),
                            "days_overdue": (datetime.utcnow() - retention_deadline).days
                        }
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Data retention enforcement failed: {e}")
            return None
    
    async def _enforce_access_control(self, policy: Policy, resource_type: str,
                                    resource_id: str, context: Dict[str, Any]) -> Optional[PolicyViolation]:
        """Enforce access control policy"""
        try:
            # Check for excessive permissions
            user_permissions = context.get("user_permissions", [])
            required_permissions = context.get("required_permissions", [])
            
            if len(user_permissions) > len(required_permissions) * 2:  # Simple heuristic
                return PolicyViolation(
                    violation_id=str(uuid.uuid4()),
                    policy_id=policy.policy_id,
                    resource_id=resource_id,
                    resource_type=resource_type,
                    violation_type="excessive_permissions",
                    severity=ViolationSeverity.MEDIUM,
                    description="User has excessive permissions beyond requirements",
                    detected_at=datetime.utcnow(),
                    metadata={
                        "user_permissions_count": len(user_permissions),
                        "required_permissions_count": len(required_permissions)
                    }
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Access control enforcement failed: {e}")
            return None
    
    async def _enforce_data_classification(self, policy: Policy, resource_type: str,
                                         resource_id: str, context: Dict[str, Any]) -> Optional[PolicyViolation]:
        """Enforce data classification policy"""
        try:
            # Check if data is properly classified
            data_classification = context.get("data_classification")
            
            if not data_classification:
                return PolicyViolation(
                    violation_id=str(uuid.uuid4()),
                    policy_id=policy.policy_id,
                    resource_id=resource_id,
                    resource_type=resource_type,
                    violation_type="missing_data_classification",
                    severity=ViolationSeverity.MEDIUM,
                    description="Data lacks proper classification",
                    detected_at=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Data classification enforcement failed: {e}")
            return None
    
    async def _enforce_privacy(self, policy: Policy, resource_type: str,
                             resource_id: str, context: Dict[str, Any]) -> Optional[PolicyViolation]:
        """Enforce privacy policy"""
        try:
            # Check for personal data without consent
            contains_personal_data = context.get("contains_personal_data", False)
            has_consent = context.get("has_consent", False)
            
            if contains_personal_data and not has_consent:
                return PolicyViolation(
                    violation_id=str(uuid.uuid4()),
                    policy_id=policy.policy_id,
                    resource_id=resource_id,
                    resource_type=resource_type,
                    violation_type="missing_consent",
                    severity=ViolationSeverity.HIGH,
                    description="Personal data processed without explicit consent",
                    detected_at=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Privacy enforcement failed: {e}")
            return None
    
    async def _enforce_encryption(self, policy: Policy, resource_type: str,
                                resource_id: str, context: Dict[str, Any]) -> Optional[PolicyViolation]:
        """Enforce encryption policy"""
        try:
            # Check encryption requirements
            data_classification_level = context.get("data_classification_level", 1)
            is_encrypted = context.get("is_encrypted", False)
            
            if data_classification_level >= 3 and not is_encrypted:
                return PolicyViolation(
                    violation_id=str(uuid.uuid4()),
                    policy_id=policy.policy_id,
                    resource_id=resource_id,
                    resource_type=resource_type,
                    violation_type="missing_encryption",
                    severity=ViolationSeverity.HIGH,
                    description="Sensitive data not encrypted as required",
                    detected_at=datetime.utcnow(),
                    metadata={
                        "data_classification_level": data_classification_level,
                        "encryption_required": True
                    }
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Encryption enforcement failed: {e}")
            return None


class ComplianceMonitor:
    """Compliance monitoring and assessment"""
    
    def __init__(self):
        self.assessments: Dict[str, ComplianceAssessment] = {}
        self.compliance_controls: Dict[ComplianceFramework, List[Dict[str, Any]]] = {}
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize compliance monitor"""
        try:
            # Load compliance controls
            await self._load_compliance_controls()
            
            self.logger.info("Compliance monitor initialized")
            
        except Exception as e:
            self.logger.error(f"Compliance monitor initialization failed: {e}")
            raise
    
    async def _load_compliance_controls(self):
        """Load compliance framework controls"""
        try:
            # GDPR controls
            self.compliance_controls[ComplianceFramework.GDPR] = [
                {
                    "control_id": "gdpr_art_6",
                    "name": "Lawful Basis for Processing",
                    "description": "Processing must have a lawful basis",
                    "requirements": ["consent", "contract", "legal_obligation", "vital_interests", "public_task", "legitimate_interests"]
                },
                {
                    "control_id": "gdpr_art_7",
                    "name": "Conditions for Consent",
                    "description": "Consent must be freely given, specific, informed and unambiguous",
                    "requirements": ["explicit_consent", "withdrawal_mechanism", "consent_records"]
                },
                {
                    "control_id": "gdpr_art_17",
                    "name": "Right to Erasure",
                    "description": "Data subjects have the right to erasure",
                    "requirements": ["erasure_mechanism", "response_within_30_days", "third_party_notification"]
                },
                {
                    "control_id": "gdpr_art_25",
                    "name": "Data Protection by Design",
                    "description": "Privacy by design and by default",
                    "requirements": ["privacy_by_design", "data_minimization", "pseudonymization"]
                },
                {
                    "control_id": "gdpr_art_32",
                    "name": "Security of Processing",
                    "description": "Appropriate technical and organizational measures",
                    "requirements": ["encryption", "access_controls", "incident_response", "regular_testing"]
                }
            ]
            
            # ISO 27001 controls
            self.compliance_controls[ComplianceFramework.ISO_27001] = [
                {
                    "control_id": "iso_a5_1_1",
                    "name": "Information Security Policies",
                    "description": "Management direction and support for information security",
                    "requirements": ["security_policy", "management_approval", "regular_review"]
                },
                {
                    "control_id": "iso_a9_1_1",
                    "name": "Access Control Policy",
                    "description": "Access control policy should be established",
                    "requirements": ["access_policy", "least_privilege", "regular_review"]
                },
                {
                    "control_id": "iso_a10_1_1",
                    "name": "Cryptographic Policy",
                    "description": "Policy on the use of cryptographic controls",
                    "requirements": ["crypto_policy", "key_management", "algorithm_standards"]
                },
                {
                    "control_id": "iso_a12_6_1",
                    "name": "Management of Technical Vulnerabilities",
                    "description": "Information about technical vulnerabilities",
                    "requirements": ["vulnerability_management", "patch_management", "risk_assessment"]
                }
            ]
            
            # SOC 2 controls
            self.compliance_controls[ComplianceFramework.SOC2] = [
                {
                    "control_id": "cc1_1",
                    "name": "Control Environment",
                    "description": "The entity demonstrates a commitment to integrity and ethical values",
                    "requirements": ["code_of_conduct", "ethics_training", "management_oversight"]
                },
                {
                    "control_id": "cc6_1",
                    "name": "Logical and Physical Access Controls",
                    "description": "The entity implements logical and physical access controls",
                    "requirements": ["access_controls", "authentication", "authorization", "physical_security"]
                },
                {
                    "control_id": "cc7_1",
                    "name": "System Operations",
                    "description": "The entity ensures system processing integrity",
                    "requirements": ["change_management", "monitoring", "incident_response"]
                }
            ]
            
            self.logger.info(f"Loaded compliance controls for {len(self.compliance_controls)} frameworks")
            
        except Exception as e:
            self.logger.error(f"Failed to load compliance controls: {e}")
    
    async def conduct_compliance_assessment(self, framework: ComplianceFramework,
                                          assessor: str = "") -> ComplianceAssessment:
        """Conduct compliance assessment"""
        try:
            controls = self.compliance_controls.get(framework, [])
            if not controls:
                raise ValueError(f"No controls defined for framework: {framework}")
            
            assessment_results = []
            compliant_count = 0
            
            # Evaluate each control
            for control in controls:
                control_result = await self._evaluate_control(control, framework)
                assessment_results.append(control_result)
                
                if control_result["status"] == ComplianceStatus.COMPLIANT:
                    compliant_count += 1
            
            # Calculate overall score
            total_controls = len(controls)
            score = (compliant_count / total_controls) * 100 if total_controls > 0 else 0
            
            # Determine overall status
            if score >= 95:
                overall_status = ComplianceStatus.COMPLIANT
            elif score >= 70:
                overall_status = ComplianceStatus.PARTIALLY_COMPLIANT
            else:
                overall_status = ComplianceStatus.NON_COMPLIANT
            
            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(
                assessment_results, framework
            )
            
            assessment = ComplianceAssessment(
                assessment_id=str(uuid.uuid4()),
                framework=framework,
                assessment_date=datetime.utcnow(),
                overall_status=overall_status,
                score=score,
                total_controls=total_controls,
                compliant_controls=compliant_count,
                non_compliant_controls=total_controls - compliant_count,
                findings=assessment_results,
                recommendations=recommendations,
                assessor=assessor,
                next_assessment_date=datetime.utcnow() + timedelta(days=365)  # Annual assessment
            )
            
            self.assessments[assessment.assessment_id] = assessment
            
            self.logger.info(f"Compliance assessment completed: {framework.value} - Score: {score:.1f}%")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Compliance assessment failed: {e}")
            raise
    
    async def _evaluate_control(self, control: Dict[str, Any], 
                              framework: ComplianceFramework) -> Dict[str, Any]:
        """Evaluate individual compliance control"""
        try:
            # Mock evaluation - in real implementation, this would check actual system state
            control_id = control["control_id"]
            
            # Simulate different compliance statuses
            import random
            statuses = [ComplianceStatus.COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT, 
                       ComplianceStatus.NON_COMPLIANT]
            weights = [0.7, 0.2, 0.1]  # Bias towards compliance
            
            status = random.choices(statuses, weights=weights)[0]
            
            result = {
                "control_id": control_id,
                "name": control["name"],
                "description": control["description"],
                "status": status,
                "evidence": [],
                "gaps": [],
                "recommendations": []
            }
            
            # Add specific findings based on status
            if status == ComplianceStatus.NON_COMPLIANT:
                result["gaps"] = [f"Control {control_id} not implemented"]
                result["recommendations"] = [f"Implement {control['name']} control"]
            elif status == ComplianceStatus.PARTIALLY_COMPLIANT:
                result["gaps"] = [f"Control {control_id} partially implemented"]
                result["recommendations"] = [f"Complete implementation of {control['name']}"]
            else:
                result["evidence"] = [f"Control {control_id} properly implemented"]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Control evaluation failed: {e}")
            return {
                "control_id": control.get("control_id", "unknown"),
                "status": ComplianceStatus.UNDER_ASSESSMENT,
                "error": str(e)
            }
    
    async def _generate_compliance_recommendations(self, assessment_results: List[Dict[str, Any]],
                                                 framework: ComplianceFramework) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        try:
            non_compliant_controls = [r for r in assessment_results 
                                    if r.get("status") == ComplianceStatus.NON_COMPLIANT]
            
            partial_controls = [r for r in assessment_results 
                              if r.get("status") == ComplianceStatus.PARTIALLY_COMPLIANT]
            
            if non_compliant_controls:
                recommendations.append(f"Address {len(non_compliant_controls)} non-compliant controls as priority")
            
            if partial_controls:
                recommendations.append(f"Complete implementation of {len(partial_controls)} partially compliant controls")
            
            # Framework-specific recommendations
            if framework == ComplianceFramework.GDPR:
                recommendations.extend([
                    "Implement comprehensive consent management system",
                    "Establish data subject rights fulfillment procedures",
                    "Conduct privacy impact assessments for high-risk processing"
                ])
            elif framework == ComplianceFramework.ISO_27001:
                recommendations.extend([
                    "Establish comprehensive information security management system",
                    "Implement regular security awareness training",
                    "Conduct annual security risk assessments"
                ])
            elif framework == ComplianceFramework.SOC2:
                recommendations.extend([
                    "Implement comprehensive access control procedures",
                    "Establish change management processes",
                    "Implement continuous monitoring and logging"
                ])
            
            return recommendations[:10]  # Limit to top 10 recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return ["Conduct detailed compliance gap analysis"]


class GovernanceEngine:
    """Comprehensive governance engine"""
    
    def __init__(self):
        # Core components
        self.policy_engine = PolicyEngine()
        self.compliance_monitor = ComplianceMonitor()
        
        # Governance data
        self.violations: Dict[str, PolicyViolation] = {}
        self.audit_trail: List[AuditTrail] = []
        
        # Governance metrics
        self.metrics = {
            "policies_active": 0,
            "violations_detected": 0,
            "violations_resolved": 0,
            "compliance_assessments": 0,
            "audit_entries": 0
        }
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize governance engine"""
        try:
            self.logger.info("Initializing Governance Engine...")
            
            # Initialize components
            await self.policy_engine.initialize()
            await self.compliance_monitor.initialize()
            
            # Update metrics
            self.metrics["policies_active"] = len([p for p in self.policy_engine.policies.values() 
                                                 if p.status == PolicyStatus.ACTIVE])
            
            self.logger.info("Governance Engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Governance Engine: {e}")
            raise
    
    # Policy management
    async def create_policy(self, name: str, description: str, policy_type: PolicyType,
                          compliance_frameworks: List[ComplianceFramework],
                          rules: List[Dict[str, Any]], owner: str = "") -> Policy:
        """Create new governance policy"""
        try:
            policy = Policy(
                policy_id=str(uuid.uuid4()),
                name=name,
                description=description,
                policy_type=policy_type,
                compliance_frameworks=compliance_frameworks,
                status=PolicyStatus.DRAFT,
                version="1.0",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                effective_date=datetime.utcnow(),
                owner=owner,
                rules=rules
            )
            
            self.policy_engine.policies[policy.policy_id] = policy
            
            # Log audit trail
            await self.log_audit_event(
                user_id="system",
                action="policy_created",
                resource_type="policy",
                resource_id=policy.policy_id,
                new_values={"name": name, "type": policy_type.value}
            )
            
            self.logger.info(f"Policy created: {name}")
            return policy
            
        except Exception as e:
            self.logger.error(f"Policy creation failed: {e}")
            raise
    
    async def activate_policy(self, policy_id: str, approver: str = "") -> bool:
        """Activate policy"""
        try:
            policy = self.policy_engine.policies.get(policy_id)
            if not policy:
                return False
            
            old_status = policy.status
            policy.status = PolicyStatus.ACTIVE
            policy.approver = approver
            policy.updated_at = datetime.utcnow()
            
            # Update metrics
            if old_status != PolicyStatus.ACTIVE:
                self.metrics["policies_active"] += 1
            
            # Log audit trail
            await self.log_audit_event(
                user_id=approver or "system",
                action="policy_activated",
                resource_type="policy",
                resource_id=policy_id,
                old_values={"status": old_status.value},
                new_values={"status": PolicyStatus.ACTIVE.value}
            )
            
            self.logger.info(f"Policy activated: {policy.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Policy activation failed: {e}")
            return False
    
    # Compliance monitoring
    async def check_compliance(self, resource_type: str, resource_id: str,
                             context: Dict[str, Any]) -> List[PolicyViolation]:
        """Check compliance for resource"""
        try:
            violations = await self.policy_engine.evaluate_policy_compliance(
                resource_type, resource_id, context
            )
            
            # Store violations
            for violation in violations:
                self.violations[violation.violation_id] = violation
                self.metrics["violations_detected"] += 1
                
                # Log audit trail
                await self.log_audit_event(
                    user_id="system",
                    action="violation_detected",
                    resource_type="violation",
                    resource_id=violation.violation_id,
                    new_values={
                        "policy_id": violation.policy_id,
                        "severity": violation.severity.value,
                        "resource_type": resource_type,
                        "resource_id": resource_id
                    }
                )
            
            if violations:
                self.logger.warning(f"Compliance violations detected: {len(violations)} for {resource_type}:{resource_id}")
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {e}")
            return []
    
    async def resolve_violation(self, violation_id: str, resolution_notes: str,
                              resolver: str = "") -> bool:
        """Resolve policy violation"""
        try:
            violation = self.violations.get(violation_id)
            if not violation:
                return False
            
            violation.resolved_at = datetime.utcnow()
            violation.resolution_notes = resolution_notes
            
            self.metrics["violations_resolved"] += 1
            
            # Log audit trail
            await self.log_audit_event(
                user_id=resolver or "system",
                action="violation_resolved",
                resource_type="violation",
                resource_id=violation_id,
                new_values={
                    "resolved_at": violation.resolved_at.isoformat(),
                    "resolution_notes": resolution_notes
                }
            )
            
            self.logger.info(f"Violation resolved: {violation_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Violation resolution failed: {e}")
            return False
    
    async def conduct_compliance_assessment(self, framework: ComplianceFramework,
                                          assessor: str = "") -> ComplianceAssessment:
        """Conduct compliance assessment"""
        try:
            assessment = await self.compliance_monitor.conduct_compliance_assessment(
                framework, assessor
            )
            
            self.metrics["compliance_assessments"] += 1
            
            # Log audit trail
            await self.log_audit_event(
                user_id=assessor or "system",
                action="compliance_assessment",
                resource_type="assessment",
                resource_id=assessment.assessment_id,
                new_values={
                    "framework": framework.value,
                    "score": assessment.score,
                    "status": assessment.overall_status.value
                }
            )
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Compliance assessment failed: {e}")
            raise
    
    # Audit trail
    async def log_audit_event(self, user_id: str, action: str, resource_type: str,
                            resource_id: str, old_values: Optional[Dict[str, Any]] = None,
                            new_values: Optional[Dict[str, Any]] = None,
                            ip_address: Optional[str] = None,
                            user_agent: Optional[str] = None,
                            session_id: Optional[str] = None) -> AuditTrail:
        """Log audit trail event"""
        try:
            audit_entry = AuditTrail(
                audit_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id
            )
            
            self.audit_trail.append(audit_entry)
            self.metrics["audit_entries"] += 1
            
            return audit_entry
            
        except Exception as e:
            self.logger.error(f"Audit logging failed: {e}")
            raise
    
    # Queries and reporting
    async def get_policy_violations(self, severity: Optional[ViolationSeverity] = None,
                                  resolved: Optional[bool] = None,
                                  limit: int = 100) -> List[PolicyViolation]:
        """Get policy violations with filters"""
        try:
            violations = list(self.violations.values())
            
            # Apply filters
            if severity:
                violations = [v for v in violations if v.severity == severity]
            
            if resolved is not None:
                if resolved:
                    violations = [v for v in violations if v.resolved_at is not None]
                else:
                    violations = [v for v in violations if v.resolved_at is None]
            
            # Sort by detection time (newest first)
            violations.sort(key=lambda x: x.detected_at, reverse=True)
            
            return violations[:limit]
            
        except Exception as e:
            self.logger.error(f"Policy violations query failed: {e}")
            return []
    
    async def get_audit_trail(self, user_id: Optional[str] = None,
                            action: Optional[str] = None,
                            resource_type: Optional[str] = None,
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None,
                            limit: int = 100) -> List[AuditTrail]:
        """Get audit trail with filters"""
        try:
            entries = list(self.audit_trail)
            
            # Apply filters
            if user_id:
                entries = [e for e in entries if e.user_id == user_id]
            
            if action:
                entries = [e for e in entries if e.action == action]
            
            if resource_type:
                entries = [e for e in entries if e.resource_type == resource_type]
            
            if start_time:
                entries = [e for e in entries if e.timestamp >= start_time]
            
            if end_time:
                entries = [e for e in entries if e.timestamp <= end_time]
            
            # Sort by timestamp (newest first)
            entries.sort(key=lambda x: x.timestamp, reverse=True)
            
            return entries[:limit]
            
        except Exception as e:
            self.logger.error(f"Audit trail query failed: {e}")
            return []
    
    async def get_governance_metrics(self) -> Dict[str, Any]:
        """Get governance metrics"""
        try:
            now = datetime.utcnow()
            
            # Policy statistics
            policy_status_distribution = Counter(
                p.status for p in self.policy_engine.policies.values()
            )
            
            policy_type_distribution = Counter(
                p.policy_type for p in self.policy_engine.policies.values()
            )
            
            # Violation statistics
            open_violations = len([v for v in self.violations.values() if v.resolved_at is None])
            violation_severity_distribution = Counter(v.severity for v in self.violations.values())
            
            # Recent activity
            recent_violations = len([v for v in self.violations.values() 
                                   if v.detected_at > now - timedelta(hours=24)])
            
            recent_audit_entries = len([e for e in self.audit_trail 
                                      if e.timestamp > now - timedelta(hours=24)])
            
            return {
                "policies": {
                    "total": len(self.policy_engine.policies),
                    "active": self.metrics["policies_active"],
                    "status_distribution": {status.value: count for status, count in policy_status_distribution.items()},
                    "type_distribution": {ptype.value: count for ptype, count in policy_type_distribution.items()}
                },
                "violations": {
                    "total": len(self.violations),
                    "open": open_violations,
                    "resolved": self.metrics["violations_resolved"],
                    "recent_24h": recent_violations,
                    "severity_distribution": {severity.value: count for severity, count in violation_severity_distribution.items()}
                },
                "compliance": {
                    "assessments_conducted": self.metrics["compliance_assessments"],
                    "frameworks_monitored": len(self.compliance_monitor.compliance_controls)
                },
                "audit": {
                    "total_entries": len(self.audit_trail),
                    "recent_24h": recent_audit_entries
                },
                "metrics": self.metrics,
                "metrics_timestamp": now.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get governance metrics: {e}")
            return {}