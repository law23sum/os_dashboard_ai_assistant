"""
Authentication and Authorization Manager
Handles user authentication, role-based access control, and session management
"""

import asyncio
from typing import Dict, List, Any, Optional, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import json
import logging
import hashlib
import secrets
import jwt
from pathlib import Path
import uuid
import bcrypt
from collections import defaultdict

try:
    from api_connectors.universal_connector import CIRDocument, DocumentType, SourceType
except ImportError:
    # Fallback definitions if import fails
    from dataclasses import dataclass
    from enum import Enum
    class DocumentType(Enum):
        DOCUMENT = "document"
        REPORT = "report"
    class SourceType(Enum):
        LOCAL = "local"
        REMOTE = "remote"
    @dataclass
    class CIRDocument:
        id: str = ""
        content: str = ""
        doc_type: DocumentType = DocumentType.DOCUMENT
        source: SourceType = SourceType.LOCAL


class AuthProvider(Enum):
    """Authentication providers"""

    LOCAL = "local"
    OAUTH2 = "oauth2"
    SAML = "saml"
    LDAP = "ldap"
    AZURE_AD = "azure_ad"
    GOOGLE = "google"
    GITHUB = "github"
    OKTA = "okta"


class UserRole(Enum):
    """User roles with hierarchical permissions"""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"
    ANALYST = "analyst"
    USER = "user"
    GUEST = "guest"


class Permission(Enum):
    """System permissions"""

    # System administration
    SYSTEM_ADMIN = "system_admin"
    USER_MANAGEMENT = "user_management"
    SECURITY_CONFIG = "security_config"

    # Project management
    PROJECT_CREATE = "project_create"
    PROJECT_DELETE = "project_delete"
    PROJECT_MANAGE = "project_manage"
    PROJECT_VIEW = "project_view"

    # Data access
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"

    # AI and engines
    AI_ACCESS = "ai_access"
    ENGINE_MANAGE = "engine_manage"
    ENGINE_EXECUTE = "engine_execute"

    # API and integrations
    API_ACCESS = "api_access"
    CONNECTOR_MANAGE = "connector_manage"

    # Billing and usage
    BILLING_VIEW = "billing_view"
    BILLING_MANAGE = "billing_manage"


@dataclass
class User:
    """User account information"""

    user_id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    permissions: Set[Permission] = field(default_factory=set)
    auth_provider: AuthProvider = AuthProvider.LOCAL
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    password_hash: Optional[str] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    profile_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "role": self.role.value,
            "permissions": [p.value for p in self.permissions],
            "auth_provider": self.auth_provider.value,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


@dataclass
class Session:
    """User session information"""

    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
        }


@dataclass
class AuthToken:
    """Authentication token"""

    token_id: str
    user_id: str
    token_type: str  # access, refresh, api
    token_value: str
    created_at: datetime
    expires_at: datetime
    scopes: List[str] = field(default_factory=list)
    is_revoked: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }


@dataclass
class LoginAttempt:
    """Login attempt tracking"""

    attempt_id: str
    username: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    success: bool
    failure_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "timestamp": self.timestamp.isoformat()}


class RolePermissionManager:
    """Role-based permission management"""

    def __init__(self):
        # Define role hierarchies and default permissions
        self.role_permissions = {
            UserRole.SUPER_ADMIN: {
                Permission.SYSTEM_ADMIN,
                Permission.USER_MANAGEMENT,
                Permission.SECURITY_CONFIG,
                Permission.PROJECT_CREATE,
                Permission.PROJECT_DELETE,
                Permission.PROJECT_MANAGE,
                Permission.PROJECT_VIEW,
                Permission.DATA_READ,
                Permission.DATA_WRITE,
                Permission.DATA_DELETE,
                Permission.DATA_EXPORT,
                Permission.AI_ACCESS,
                Permission.ENGINE_MANAGE,
                Permission.ENGINE_EXECUTE,
                Permission.API_ACCESS,
                Permission.CONNECTOR_MANAGE,
                Permission.BILLING_VIEW,
                Permission.BILLING_MANAGE,
            },
            UserRole.ADMIN: {
                Permission.USER_MANAGEMENT,
                Permission.PROJECT_CREATE,
                Permission.PROJECT_DELETE,
                Permission.PROJECT_MANAGE,
                Permission.PROJECT_VIEW,
                Permission.DATA_READ,
                Permission.DATA_WRITE,
                Permission.DATA_DELETE,
                Permission.DATA_EXPORT,
                Permission.AI_ACCESS,
                Permission.ENGINE_MANAGE,
                Permission.ENGINE_EXECUTE,
                Permission.API_ACCESS,
                Permission.CONNECTOR_MANAGE,
                Permission.BILLING_VIEW,
            },
            UserRole.MANAGER: {
                Permission.PROJECT_CREATE,
                Permission.PROJECT_MANAGE,
                Permission.PROJECT_VIEW,
                Permission.DATA_READ,
                Permission.DATA_WRITE,
                Permission.DATA_EXPORT,
                Permission.AI_ACCESS,
                Permission.ENGINE_EXECUTE,
                Permission.API_ACCESS,
                Permission.BILLING_VIEW,
            },
            UserRole.DEVELOPER: {
                Permission.PROJECT_CREATE,
                Permission.PROJECT_MANAGE,
                Permission.PROJECT_VIEW,
                Permission.DATA_READ,
                Permission.DATA_WRITE,
                Permission.AI_ACCESS,
                Permission.ENGINE_EXECUTE,
                Permission.API_ACCESS,
            },
            UserRole.ANALYST: {
                Permission.PROJECT_VIEW,
                Permission.DATA_READ,
                Permission.DATA_EXPORT,
                Permission.AI_ACCESS,
                Permission.ENGINE_EXECUTE,
            },
            UserRole.USER: {
                Permission.PROJECT_VIEW,
                Permission.DATA_READ,
                Permission.AI_ACCESS,
            },
            UserRole.GUEST: {Permission.PROJECT_VIEW},
        }

        self.logger = logging.getLogger(__name__)

    def get_role_permissions(self, role: UserRole) -> Set[Permission]:
        """Get permissions for a role"""
        return self.role_permissions.get(role, set())

    def has_permission(
        self,
        user_role: UserRole,
        user_permissions: Set[Permission],
        required_permission: Permission,
    ) -> bool:
        """Check if user has required permission"""
        # Check explicit permissions first
        if required_permission in user_permissions:
            return True

        # Check role-based permissions
        role_permissions = self.get_role_permissions(user_role)
        return required_permission in role_permissions

    def can_access_resource(
        self,
        user_role: UserRole,
        user_permissions: Set[Permission],
        resource_type: str,
        action: str,
    ) -> bool:
        """Check if user can access a resource with specific action"""
        permission_map = {
            ("project", "create"): Permission.PROJECT_CREATE,
            ("project", "delete"): Permission.PROJECT_DELETE,
            ("project", "manage"): Permission.PROJECT_MANAGE,
            ("project", "view"): Permission.PROJECT_VIEW,
            ("data", "read"): Permission.DATA_READ,
            ("data", "write"): Permission.DATA_WRITE,
            ("data", "delete"): Permission.DATA_DELETE,
            ("data", "export"): Permission.DATA_EXPORT,
            ("ai", "access"): Permission.AI_ACCESS,
            ("engine", "manage"): Permission.ENGINE_MANAGE,
            ("engine", "execute"): Permission.ENGINE_EXECUTE,
            ("api", "access"): Permission.API_ACCESS,
            ("connector", "manage"): Permission.CONNECTOR_MANAGE,
            ("billing", "view"): Permission.BILLING_VIEW,
            ("billing", "manage"): Permission.BILLING_MANAGE,
            ("system", "admin"): Permission.SYSTEM_ADMIN,
            ("user", "manage"): Permission.USER_MANAGEMENT,
            ("security", "config"): Permission.SECURITY_CONFIG,
        }

        required_permission = permission_map.get((resource_type, action))
        if not required_permission:
            return False

        return self.has_permission(user_role, user_permissions, required_permission)


class AuthManager:
    """Authentication and Authorization Manager"""

    def __init__(self, secret_key: str, token_expiry_hours: int = 24):
        self.secret_key = secret_key
        self.token_expiry_hours = token_expiry_hours

        # User and session management
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.tokens: Dict[str, AuthToken] = {}
        self.login_attempts: List[LoginAttempt] = []

        # Permission management
        self.permission_manager = RolePermissionManager()

        # Security settings
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 30
        self.session_timeout_hours = 8
        self.password_min_length = 8

        # Failed login tracking
        self.failed_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.locked_accounts: Dict[str, datetime] = {}

        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """Initialize authentication manager"""
        try:
            self.logger.info("Initializing Authentication Manager...")

            # Create default admin user if none exists
            if not self.users:
                await self._create_default_admin()

            # Clean up expired sessions and tokens
            await self._cleanup_expired_items()

            self.logger.info("Authentication Manager initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Authentication Manager: {e}")
            raise

    async def _create_default_admin(self):
        """Create default admin user"""
        try:
            admin_user = User(
                user_id=str(uuid.uuid4()),
                username="admin",
                email="admin@os-dashboard.com",
                full_name="System Administrator",
                role=UserRole.SUPER_ADMIN,
                is_active=True,
                is_verified=True,
                password_hash=self._hash_password("admin123!"),  # Default password
            )

            # Set role-based permissions
            admin_user.permissions = self.permission_manager.get_role_permissions(
                UserRole.SUPER_ADMIN
            )

            self.users[admin_user.user_id] = admin_user

            self.logger.info("Default admin user created")

        except Exception as e:
            self.logger.error(f"Failed to create default admin: {e}")

    # User management
    async def create_user(
        self,
        username: str,
        email: str,
        full_name: str,
        password: str,
        role: UserRole = UserRole.USER,
        auth_provider: AuthProvider = AuthProvider.LOCAL,
    ) -> Optional[User]:
        """Create new user"""
        try:
            # Check if username or email already exists
            if await self._user_exists(username, email):
                self.logger.error(f"User already exists: {username}")
                return None

            # Validate password
            if not self._validate_password(password):
                self.logger.error("Password does not meet requirements")
                return None

            user = User(
                user_id=str(uuid.uuid4()),
                username=username,
                email=email,
                full_name=full_name,
                role=role,
                auth_provider=auth_provider,
                password_hash=self._hash_password(password)
                if auth_provider == AuthProvider.LOCAL
                else None,
            )

            # Set role-based permissions
            user.permissions = self.permission_manager.get_role_permissions(role)

            self.users[user.user_id] = user

            self.logger.info(f"User created: {username}")
            return user

        except Exception as e:
            self.logger.error(f"User creation failed: {e}")
            return None

    async def _user_exists(self, username: str, email: str) -> bool:
        """Check if user exists by username or email"""
        for user in self.users.values():
            if user.username == username or user.email == email:
                return True
        return False

    def _validate_password(self, password: str) -> bool:
        """Validate password requirements"""
        if len(password) < self.password_min_length:
            return False

        # Check for at least one uppercase, lowercase, digit, and special character
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        return has_upper and has_lower and has_digit and has_special

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    # Authentication
    async def authenticate_user(
        self, username: str, password: str, ip_address: str, user_agent: str
    ) -> Optional[Dict[str, Any]]:
        """Authenticate user with username/password"""
        try:
            # Record login attempt
            attempt = LoginAttempt(
                attempt_id=str(uuid.uuid4()),
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow(),
                success=False,
            )

            # Check if account is locked
            if await self._is_account_locked(username):
                attempt.failure_reason = "Account locked"
                self.login_attempts.append(attempt)
                return None

            # Find user
            user = None
            for u in self.users.values():
                if u.username == username and u.is_active:
                    user = u
                    break

            if not user:
                attempt.failure_reason = "User not found"
                self.login_attempts.append(attempt)
                await self._record_failed_attempt(username)
                return None

            # Verify password
            if not user.password_hash or not self._verify_password(
                password, user.password_hash
            ):
                attempt.failure_reason = "Invalid password"
                self.login_attempts.append(attempt)
                await self._record_failed_attempt(username)
                return None

            # Authentication successful
            attempt.success = True
            self.login_attempts.append(attempt)

            # Clear failed attempts
            if username in self.failed_attempts:
                del self.failed_attempts[username]
            if username in self.locked_accounts:
                del self.locked_accounts[username]

            # Update last login
            user.last_login = datetime.utcnow()

            # Create session and tokens
            session = await self._create_session(user, ip_address, user_agent)
            access_token = await self._create_access_token(user)
            refresh_token = await self._create_refresh_token(user)

            self.logger.info(f"User authenticated: {username}")

            return {
                "user": user.to_dict(),
                "session": session.to_dict(),
                "access_token": access_token.token_value,
                "refresh_token": refresh_token.token_value,
                "expires_at": access_token.expires_at.isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return None

    async def _is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to failed attempts"""
        if username not in self.locked_accounts:
            return False

        locked_until = self.locked_accounts[username]
        if datetime.utcnow() > locked_until:
            del self.locked_accounts[username]
            return False

        return True

    async def _record_failed_attempt(self, username: str):
        """Record failed login attempt"""
        now = datetime.utcnow()

        # Clean old attempts (older than 1 hour)
        cutoff = now - timedelta(hours=1)
        self.failed_attempts[username] = [
            attempt for attempt in self.failed_attempts[username] if attempt > cutoff
        ]

        # Add current attempt
        self.failed_attempts[username].append(now)

        # Check if account should be locked
        if len(self.failed_attempts[username]) >= self.max_login_attempts:
            self.locked_accounts[username] = now + timedelta(
                minutes=self.lockout_duration_minutes
            )
            self.logger.warning(f"Account locked due to failed attempts: {username}")

    async def _create_session(
        self, user: User, ip_address: str, user_agent: str
    ) -> Session:
        """Create user session"""
        session = Session(
            session_id=str(uuid.uuid4()),
            user_id=user.user_id,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=self.session_timeout_hours),
            last_activity=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.sessions[session.session_id] = session
        return session

    async def _create_access_token(self, user: User) -> AuthToken:
        """Create access token"""
        token_data = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "exp": datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            "iat": datetime.utcnow(),
            "type": "access",
        }

        token_value = jwt.encode(token_data, self.secret_key, algorithm="HS256")

        token = AuthToken(
            token_id=str(uuid.uuid4()),
            user_id=user.user_id,
            token_type="access",
            token_value=token_value,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            scopes=["read", "write"],
        )

        self.tokens[token.token_id] = token
        return token

    async def _create_refresh_token(self, user: User) -> AuthToken:
        """Create refresh token"""
        token_data = {
            "user_id": user.user_id,
            "username": user.username,
            "exp": datetime.utcnow()
            + timedelta(days=30),  # Longer expiry for refresh tokens
            "iat": datetime.utcnow(),
            "type": "refresh",
        }

        token_value = jwt.encode(token_data, self.secret_key, algorithm="HS256")

        token = AuthToken(
            token_id=str(uuid.uuid4()),
            user_id=user.user_id,
            token_type="refresh",
            token_value=token_value,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30),
            scopes=["refresh"],
        )

        self.tokens[token.token_id] = token
        return token

    # Token validation
    async def validate_token(self, token_value: str) -> Optional[Dict[str, Any]]:
        """Validate and decode token"""
        try:
            # Decode token
            payload = jwt.decode(token_value, self.secret_key, algorithms=["HS256"])

            # Check if token is revoked
            token = None
            for t in self.tokens.values():
                if t.token_value == token_value and not t.is_revoked:
                    token = t
                    break

            if not token:
                return None

            # Get user
            user = self.users.get(payload["user_id"])
            if not user or not user.is_active:
                return None

            return {
                "user_id": user.user_id,
                "username": user.username,
                "role": user.role.value,
                "permissions": [p.value for p in user.permissions],
                "token_type": payload.get("type", "access"),
            }

        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid token")
            return None
        except Exception as e:
            self.logger.error(f"Token validation failed: {e}")
            return None

    # Authorization
    async def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        try:
            user = self.users.get(user_id)
            if not user or not user.is_active:
                return False

            return self.permission_manager.has_permission(
                user.role, user.permissions, permission
            )

        except Exception as e:
            self.logger.error(f"Permission check failed: {e}")
            return False

    async def check_resource_access(
        self, user_id: str, resource_type: str, action: str
    ) -> bool:
        """Check if user can access resource with specific action"""
        try:
            user = self.users.get(user_id)
            if not user or not user.is_active:
                return False

            return self.permission_manager.can_access_resource(
                user.role, user.permissions, resource_type, action
            )

        except Exception as e:
            self.logger.error(f"Resource access check failed: {e}")
            return False

    # Session management
    async def get_active_sessions(self, user_id: Optional[str] = None) -> List[Session]:
        """Get active sessions"""
        try:
            sessions = []
            now = datetime.utcnow()

            for session in self.sessions.values():
                if session.expires_at > now and session.is_active:
                    if not user_id or session.user_id == user_id:
                        sessions.append(session)

            return sessions

        except Exception as e:
            self.logger.error(f"Failed to get active sessions: {e}")
            return []

    async def revoke_session(self, session_id: str) -> bool:
        """Revoke user session"""
        try:
            session = self.sessions.get(session_id)
            if session:
                session.is_active = False
                self.logger.info(f"Session revoked: {session_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Session revocation failed: {e}")
            return False

    async def revoke_token(self, token_value: str) -> bool:
        """Revoke authentication token"""
        try:
            for token in self.tokens.values():
                if token.token_value == token_value:
                    token.is_revoked = True
                    self.logger.info(f"Token revoked: {token.token_id}")
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Token revocation failed: {e}")
            return False

    # Cleanup and maintenance
    async def _cleanup_expired_items(self):
        """Clean up expired sessions and tokens"""
        try:
            now = datetime.utcnow()

            # Remove expired sessions
            expired_sessions = [
                sid
                for sid, session in self.sessions.items()
                if session.expires_at <= now
            ]

            for sid in expired_sessions:
                del self.sessions[sid]

            # Remove expired tokens
            expired_tokens = [
                tid for tid, token in self.tokens.items() if token.expires_at <= now
            ]

            for tid in expired_tokens:
                del self.tokens[tid]

            if expired_sessions or expired_tokens:
                self.logger.info(
                    f"Cleaned up {len(expired_sessions)} sessions and {len(expired_tokens)} tokens"
                )

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

    # User management operations
    async def update_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """Update user role"""
        try:
            user = self.users.get(user_id)
            if not user:
                return False

            old_role = user.role
            user.role = new_role
            user.permissions = self.permission_manager.get_role_permissions(new_role)

            self.logger.info(
                f"User role updated: {user.username} from {old_role.value} to {new_role.value}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Role update failed: {e}")
            return False

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        try:
            user = self.users.get(user_id)
            if not user:
                return False

            user.is_active = False

            # Revoke all user sessions
            user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]
            for session in user_sessions:
                session.is_active = False

            # Revoke all user tokens
            user_tokens = [t for t in self.tokens.values() if t.user_id == user_id]
            for token in user_tokens:
                token.is_revoked = True

            self.logger.info(f"User deactivated: {user.username}")
            return True

        except Exception as e:
            self.logger.error(f"User deactivation failed: {e}")
            return False

    # Security metrics
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get authentication and security metrics"""
        try:
            now = datetime.utcnow()

            # Active users
            active_users = len([u for u in self.users.values() if u.is_active])

            # Active sessions
            active_sessions = len(
                [
                    s
                    for s in self.sessions.values()
                    if s.is_active and s.expires_at > now
                ]
            )

            # Recent login attempts
            recent_attempts = len(
                [
                    a
                    for a in self.login_attempts
                    if a.timestamp > now - timedelta(hours=24)
                ]
            )

            failed_attempts = len(
                [
                    a
                    for a in self.login_attempts
                    if not a.success and a.timestamp > now - timedelta(hours=24)
                ]
            )

            # Locked accounts
            locked_accounts = len(self.locked_accounts)

            return {
                "users": {
                    "total": len(self.users),
                    "active": active_users,
                    "locked": locked_accounts,
                },
                "sessions": {"active": active_sessions, "total": len(self.sessions)},
                "tokens": {
                    "active": len(
                        [
                            t
                            for t in self.tokens.values()
                            if not t.is_revoked and t.expires_at > now
                        ]
                    ),
                    "total": len(self.tokens),
                },
                "login_attempts": {
                    "recent_24h": recent_attempts,
                    "failed_24h": failed_attempts,
                    "success_rate": (recent_attempts - failed_attempts)
                    / recent_attempts
                    if recent_attempts > 0
                    else 0,
                },
                "role_distribution": {
                    role.value: len([u for u in self.users.values() if u.role == role])
                    for role in UserRole
                },
                "metrics_timestamp": now.isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Failed to get security metrics: {e}")
            return {}
