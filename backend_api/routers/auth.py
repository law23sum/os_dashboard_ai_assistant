"""Authentication router with signup/login and RBAC."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from backend_api.db import db_session
from backend_api.deps import get_current_user
from backend_api.security import AuthUser, create_access_token, hash_password, verify_password

router = APIRouter()


class AuthUserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    is_admin: bool
    environment: str


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
    )


async def _ensure_demo_users() -> None:
    """Ensure demo users exist in the database for testing."""
    try:
        with db_session() as db:
            # Check if demo users already exist
            admin_user = db.execute("SELECT id FROM users WHERE email = ?", ("admin@demo.local",)).fetchone()
            regular_user = db.execute("SELECT id FROM users WHERE email = ?", ("user@demo.local",)).fetchone()
            
            now = datetime.now().isoformat(timespec="seconds")
            
            # Create admin user if it doesn't exist
            if not admin_user:
                admin_id = str(uuid4())
                db.execute(
                    """
                    INSERT INTO users (id, email, display_name, password_hash, is_admin, environment, disabled, created_at, last_login)
                    VALUES (?, ?, ?, ?, 1, 'demo', 0, ?, NULL)
                    """,
                    (admin_id, "admin@demo.local", "Admin User", hash_password("admin123"), now),
                )
            
            # Create regular user if it doesn't exist
            if not regular_user:
                user_id = str(uuid4())
                db.execute(
                    """
                    INSERT INTO users (id, email, display_name, password_hash, is_admin, environment, disabled, created_at, last_login)
                    VALUES (?, ?, ?, ?, 0, 'demo', 0, ?, NULL)
                    """,
                    (user_id, "user@demo.local", "Regular User", hash_password("user123"), now),
                )
    except Exception as e:
        import logging
        logging.error(f"Error ensuring demo users: {e}", exc_info=True)
        # Don't raise - let the login endpoint handle missing users


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, request: Request) -> TokenResponse:
    """Register a new user account."""
    try:
        email = payload.email.strip().lower()
        now = datetime.now().isoformat(timespec="seconds")
        
        with db_session() as db:
            existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            user_id = str(uuid4())
            db.execute(
                """
                INSERT INTO users (id, email, display_name, password_hash, is_admin, environment, disabled, created_at, last_login)
                VALUES (?, ?, ?, ?, 0, ?, 0, ?, NULL)
                """,
                (user_id, email, payload.display_name or "", hash_password(payload.password), payload.environment, now),
            )
            db.commit()
            row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        
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
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Signup error: {e}", exc_info=True)
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
    )
