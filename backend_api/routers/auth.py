"""Authentication router with signup/login and RBAC."""

from __future__ import annotations

from datetime import datetime, timedelta
import re
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
try:  # Pydantic v2
    from pydantic import field_validator
    _HAS_FIELD_VALIDATOR = True
except ImportError:  # pragma: no cover - pydantic v1 fallback
    from pydantic import validator
    _HAS_FIELD_VALIDATOR = False

from backend_api.db import db_session
from backend_api.deps import get_current_user
from backend_api.security import AuthUser, create_access_token, hash_password, verify_password
from assistant_hub.demo_seed import ensure_demo_data

router = APIRouter()


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _normalize_email(value: str) -> str:
    email = (value or "").strip().lower()
    if not _EMAIL_RE.match(email):
        raise ValueError("Invalid email address")
    return email


class AuthUserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    is_admin: bool
    environment: str
    tenant_id: Optional[str] = None
    workspace_id: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse
    id: Optional[str] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str = Field(min_length=6, max_length=256)

    if _HAS_FIELD_VALIDATOR:
        @field_validator("email")
        @classmethod
        def _validate_email(cls, value: Optional[str]) -> Optional[str]:
            if value is None:
                return value
            return _normalize_email(value)
    else:  # pragma: no cover - pydantic v1 fallback
        @validator("email")
        def _validate_email(cls, value: Optional[str]) -> Optional[str]:
            if value is None:
                return value
            return _normalize_email(value)
    
    def get_identifier(self) -> str:
        """Get the identifier (username or email) for login."""
        if self.username:
            return self.username.strip().lower()
        if self.email:
            return self.email.strip().lower()
        raise ValueError("Either username or email must be provided")


class SignupRequest(BaseModel):
    email: str
    password: str = Field(min_length=6, max_length=256)
    display_name: str = Field(default="", max_length=80)
    username: Optional[str] = None
    full_name: Optional[str] = None
    environment: str = Field(default="demo", pattern="^(demo|prod)$")

    if _HAS_FIELD_VALIDATOR:
        @field_validator("email")
        @classmethod
        def _validate_email(cls, value: str) -> str:
            return _normalize_email(value)
    else:  # pragma: no cover - pydantic v1 fallback
        @validator("email")
        def _validate_email(cls, value: str) -> str:
            return _normalize_email(value)


def _row_to_user(row) -> AuthUser:
    """Convert database row to AuthUser."""
    return AuthUser(
        id=str(row["id"]),
        email=str(row["email"]),
        display_name=str(row["display_name"] or ""),
        is_admin=bool(row["is_admin"] or 0),
        environment=str(row["environment"] or "demo"),
        disabled=bool(row["disabled"] or 0),
        tenant_id=str(row["tenant_id"]) if "tenant_id" in row.keys() else None,
        workspace_id=str(row["workspace_id"]) if "workspace_id" in row.keys() else None,
    )


async def _ensure_demo_users() -> None:
    """Ensure demo users exist in the database for testing."""
    try:
        with db_session() as db:
            now = datetime.now().isoformat(timespec="seconds")
            
            # Demo users to create
            demo_users = [
                ("admin@demo.local", "Admin User", "admin123", True),
                ("user@demo.local", "Regular User", "user123", False),
                ("alice@demo.local", "Alice", "password123", False),
                ("bob@demo.local", "Bob", "password123", False),
                ("charlie@demo.local", "Charlie", "password123", False),
            ]
            
            for email, display_name, password, is_admin in demo_users:
                username = email.split("@", 1)[0]
                existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
                hashed_pw = hash_password(password)
                if not existing:
                    user_id = str(uuid4())
                    db.execute(
                        """
                        INSERT INTO users (
                            id,
                            email,
                            username,
                            display_name,
                            password_hash,
                            is_admin,
                            environment,
                            disabled,
                            created_at,
                            last_login,
                            tenant_id,
                            workspace_id
                        )
                        VALUES (?, ?, ?, ?, ?, ?, 'demo', 0, ?, NULL, 'default-tenant', 'default-workspace')
                        """,
                        (user_id, email, username, display_name, hashed_pw, 1 if is_admin else 0, now),
                    )
                else:
                    # Update password/details for existing demo users to ensure they are always valid
                    db.execute(
                        """
                        UPDATE users 
                        SET password_hash = ?, display_name = ?, username = ?, is_admin = ?, disabled = 0
                        WHERE email = ?
                        """,
                        (hashed_pw, display_name, username, 1 if is_admin else 0, email),
                    )
            admin_row = db.execute(
                "SELECT id FROM users WHERE email = ?",
                ("admin@demo.local",),
            ).fetchone()
            if admin_row:
                ensure_demo_data(db, admin_user_id=str(admin_row["id"]))
    except Exception as e:
        import logging
        logging.error(f"Error ensuring demo users: {e}", exc_info=True)
        # Don't raise - let the login endpoint handle missing users


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, request: Request) -> TokenResponse:
    """Register a new user account."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        email = _normalize_email(payload.email)
        now = datetime.now().isoformat(timespec="seconds")
        display_name = (payload.display_name or payload.full_name or payload.username or "").strip()
        username = (payload.username or "").strip()
        if not username:
            username = email.split("@", 1)[0]
        normalized_username = username.lower() if username else email
        
        with db_session() as db:
            existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                logger.warning(f"Signup attempt with existing email: {email}")
                raise HTTPException(status_code=400, detail="Email already registered")
            username_row = db.execute(
                "SELECT id FROM users WHERE LOWER(username) = LOWER(?)",
                (normalized_username,),
            ).fetchone()
            if username_row:
                logger.warning(f"Signup attempt with existing username: {username}")
                raise HTTPException(status_code=400, detail="Username already registered")
            
            user_id = str(uuid4())
            db.execute(
                """
                INSERT INTO users (
                    id,
                    email,
                    username,
                    display_name,
                    password_hash,
                    is_admin,
                    environment,
                    disabled,
                    created_at,
                    last_login,
                    tenant_id,
                    workspace_id
                )
                VALUES (?, ?, ?, ?, ?, 0, ?, 0, ?, NULL, 'default-tenant', 'default-workspace')
                """,
                (
                    user_id,
                    email,
                    normalized_username,
                    display_name,
                    hash_password(payload.password),
                    payload.environment,
                    now,
                ),
            )
            db.commit()
            row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        
        user = _row_to_user(row)
        token = create_access_token(user=user, expires_in=timedelta(hours=12))
        
        logger.info(f"User signed up successfully: {email}")
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=AuthUserResponse(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                is_admin=user.is_admin,
                environment=user.environment,
                tenant_id=user.tenant_id,
                workspace_id=user.workspace_id,
            ),
            id=user.id,
            email=user.email,
        )
    except HTTPException:
        raise
    except ValueError as e:
        # Pydantic validation errors
        logger.error(f"Signup validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Signup error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during signup")


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, request: Request) -> TokenResponse:
    """Authenticate user and return access token.
    
    Accepts either username or email for login.
    Creates demo users if they don't exist.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        identifier = payload.get_identifier()
        
        # Ensure demo users exist (non-blocking - if it fails, continue)
        try:
            await _ensure_demo_users()
        except Exception as e:
            logger.warning(f"Could not ensure demo users (non-fatal): {e}")
        
        with db_session() as db:
            # Try to find user by:
            # 1. Exact email match
            # 2. Email prefix match (e.g., "admin" matches "admin@demo.local") - only if identifier has no @
            # 3. Display name match (case-insensitive)
            if "@" in identifier:
                # Full email provided - exact match only
                candidate_rows = db.execute(
                    """
                    SELECT * FROM users
                    WHERE email = ? OR LOWER(email) = LOWER(?)
                    """,
                    (identifier, identifier),
                ).fetchall()
            else:
                # Username/prefix provided - try username, email prefix, and display name
                candidate_rows = db.execute(
                    """
                    SELECT * FROM users
                    WHERE LOWER(username) = LOWER(?)
                       OR email LIKE ?
                       OR LOWER(display_name) = LOWER(?)
                    """,
                    (identifier, f"{identifier}@%", identifier),
                ).fetchall()

            if not candidate_rows:
                logger.warning(f"Login attempt with unknown identifier: {identifier}")
                raise HTTPException(status_code=401, detail="Invalid credentials")

            selected_row = None
            for row in candidate_rows:
                try:
                    password_hash = row["password_hash"] or ""
                    if not password_hash:
                        continue
                    if not verify_password(payload.password, password_hash):
                        continue
                    if bool(row["disabled"] or 0):
                        logger.warning(f"Login attempt for disabled account: {row['email']}")
                        raise HTTPException(status_code=403, detail="Account disabled")
                    selected_row = row
                    break
                except KeyError as exc:
                    logger.error(f"Missing column in user row: {exc}")
                    raise HTTPException(status_code=500, detail="Database schema error")

            if selected_row is None:
                logger.warning(f"Invalid password for identifier: {identifier}")
                raise HTTPException(status_code=401, detail="Invalid credentials")

            found_email = selected_row["email"]
            found_display = selected_row["display_name"] if "display_name" in selected_row.keys() else "N/A"
            logger.info(f"Found user for login: email={found_email}, display_name={found_display}")

            # Update last login
            db.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now().isoformat(timespec="seconds"), selected_row["id"]),
            )
            # db_session context manager will commit automatically
        
        user = _row_to_user(selected_row)
        token = create_access_token(user=user, expires_in=timedelta(hours=12))
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=AuthUserResponse(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                is_admin=user.is_admin,
                environment=user.environment,
                tenant_id=user.tenant_id,
                workspace_id=user.workspace_id,
            ),
            id=user.id,
            email=user.email,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error during login: {str(e)}")


@router.get("/me", response_model=AuthUserResponse)
async def me(user: AuthUser = Depends(get_current_user)) -> AuthUserResponse:
    """Get current authenticated user's profile."""
    return AuthUserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        is_admin=user.is_admin,
        environment=user.environment,
        tenant_id=user.tenant_id,
        workspace_id=user.workspace_id,
    )
