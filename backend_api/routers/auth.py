"""Authentication router with signup/login and RBAC."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from backend_api.db import db_session
from backend_api.deps import get_current_user
from backend_api.auth import get_current_admin_user
from backend_api.security import AuthUser, create_access_token, hash_password, verify_password
from assistant_hub.demo_seed import ensure_demo_data

router = APIRouter()


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


class LoginRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str = Field(min_length=6, max_length=256)
    
    def get_identifier(self) -> str:
        """Get the identifier (username or email) for login."""
        if self.username:
            return self.username.strip().lower()
        if self.email:
            return self.email.strip().lower()
        raise ValueError("Either username or email must be provided")


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=256)
    display_name: str = Field(default="", max_length=80)
    environment: str = Field(default="demo", pattern="^(demo|prod)$")


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
                existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
                hashed_pw = hash_password(password)
                if not existing:
                    user_id = str(uuid4())
                    db.execute(
                        """
                        INSERT INTO users (
                            id,
                            email,
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
                        VALUES (?, ?, ?, ?, ?, 'demo', 0, ?, NULL, 'default-tenant', 'default-workspace')
                        """,
                        (user_id, email, display_name, hashed_pw, 1 if is_admin else 0, now),
                    )
                else:
                    # Update password/details for existing demo users to ensure they are always valid
                    db.execute(
                        """
                        UPDATE users 
                        SET password_hash = ?, display_name = ?, is_admin = ?, disabled = 0
                        WHERE email = ?
                        """,
                        (hashed_pw, display_name, 1 if is_admin else 0, email),
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
        email = payload.email.strip().lower()
        now = datetime.now().isoformat(timespec="seconds")
        
        with db_session() as db:
            existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                logger.warning(f"Signup attempt with existing email: {email}")
                raise HTTPException(status_code=400, detail="Email already registered")
            
            user_id = str(uuid4())
            db.execute(
                """
                INSERT INTO users (
                    id,
                    email,
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
                VALUES (?, ?, ?, ?, 0, ?, 0, ?, NULL, 'default-tenant', 'default-workspace')
                """,
                (user_id, email, payload.display_name or "", hash_password(payload.password), payload.environment, now),
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
                row = db.execute(
                    """
                    SELECT * FROM users 
                    WHERE email = ? OR LOWER(email) = LOWER(?)
                    """,
                    (identifier, identifier)
                ).fetchone()
            else:
                # Username/prefix provided - try email prefix and display name
                row = db.execute(
                    """
                    SELECT * FROM users 
                    WHERE email LIKE ? 
                       OR LOWER(display_name) = LOWER(?)
                    """,
                    (f"{identifier}@%", identifier)
                ).fetchone()
            
            if not row:
                logger.warning(f"Login attempt with unknown identifier: {identifier}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            found_email = row["email"]
            found_display = row["display_name"] if "display_name" in row.keys() else "N/A"
            logger.info(f"Found user for login: email={found_email}, display_name={found_display}")
            
            # SQLite Row objects use dictionary-style access with row["key"], not row.get()
            try:
                disabled = bool(row["disabled"] or 0)
                if disabled:
                    logger.warning(f"Login attempt for disabled account: {found_email}")
                    raise HTTPException(status_code=403, detail="Account disabled")
                
                password_hash = row["password_hash"] or ""
                if not password_hash:
                    logger.error(f"User {found_email} has no password hash")
                    raise HTTPException(status_code=401, detail="Invalid credentials")
            except KeyError as e:
                logger.error(f"Missing column in user row: {e}")
                raise HTTPException(status_code=500, detail="Database schema error")
            
            # Use verify_password from backend_api.security
            try:
                password_valid = verify_password(payload.password, password_hash)
                if not password_valid:
                    logger.warning(f"Invalid password for user: {found_email} (identifier: {identifier})")
                    raise HTTPException(status_code=401, detail="Invalid credentials")
                logger.info(f"Password verified successfully for user: {found_email}")
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Password verification error for {found_email}: {e}", exc_info=True)
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Update last login
            db.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now().isoformat(timespec="seconds"), row["id"]),
            )
            # db_session context manager will commit automatically
        
        user = _row_to_user(row)
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
