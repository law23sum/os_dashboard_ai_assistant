from __future__ import annotations

"""Authentication router with signup/login and RBAC."""
"""Authentication endpoints (signup/login/me)."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from backend_api.db import db_session
from backend_api.deps import get_current_user
from backend_api.security import AuthUser, create_access_token, hash_password, verify_password
"""
Authentication router with login, signup, and user management endpoints.
"""

from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status

from backend_api.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    User,
    UserCreate,
    UserLogin,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    create_user,
    get_current_active_user,
    get_current_admin_user,
    get_user_db,
    log_user_activity,
    update_last_login,
)

router = APIRouter()


@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
class AuthUserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    is_admin: bool
    environment: str


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
@router.post("/auth/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, request: Request):
    """Register a new user account."""
    # Check if username/email exist
    with get_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (user_data.username, user_data.email),
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered",
            )

    user = create_user(user_data)
    log_user_activity(
        user.id,
        "signup",
        details=f"New user registration: {user.username}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, request: Request):
    """Authenticate user and return access and refresh tokens."""
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    update_last_login(user.id)
    log_user_activity(
        user.id,
        "login",
        details=f"User logged in: {user.username}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role}
    )

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user), request: Request = None):
    """Logout current user (server-side token invalidation is not implemented)."""
    ip_address = request.client.host if request and request.client else None
    user_agent = request.headers.get("user-agent") if request else None
    log_user_activity(
        current_user.id,
        "logout",
        details=f"User logged out: {current_user.username}",
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=User)
async def me(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user's profile."""
    return current_user


@router.get("/users", response_model=List[User])
async def list_users(admin_user: User = Depends(get_current_admin_user), skip: int = 0, limit: int = 100):
    """List users (admin only)."""
    with get_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, email, full_name, role, is_active, created_at, last_login
            FROM users
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, skip),
        )
        users: List[User] = []
        for row in cursor.fetchall():
            users.append(
                User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    full_name=row[3],
                    role=row[4],
                    is_active=bool(row[5]),
                    created_at=row[6],
                    last_login=row[7],
                )
            )
        return users


@router.patch("/auth/users/{user_id}")
async def update_user(
    user_id: int,
    updates: dict,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Update user information (admin only).
    
    Allowed fields: full_name, email, role, is_active
    """
    allowed_fields = {"full_name", "email", "role", "is_active"}
    update_fields = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )
    
    with get_user_db() as conn:
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Build UPDATE query
        set_clause = ", ".join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [user_id]
        
        cursor.execute(f"""
            UPDATE users SET {set_clause} WHERE id = ?
        """, values)
        
        conn.commit()
        
        # Log activity
        log_user_activity(
            admin_user.id,
            "update_user",
            resource=f"user:{user_id}",
            details=f"Updated fields: {', '.join(update_fields.keys())}"
        )
    
    return {"message": "User updated successfully"}


@router.delete("/auth/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Delete user (admin only).
    Cannot delete own account.
    """
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    with get_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        conn.commit()
        
        # Log activity
        log_user_activity(
            admin_user.id,
            "delete_user",
            resource=f"user:{user_id}",
            details=f"Deleted user ID: {user_id}"
        )
    
    return {"message": "User deleted successfully"}
"""Authentication and authorization router with user management."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import jwt
from passlib.context import CryptContext

from backend_api.db import db_session

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # In production, use env var
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_admin: bool
    is_active: bool
    created_at: str
    last_login: Optional[str]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse


def _row_to_user(row) -> AuthUser:
    return AuthUser(
        id=row["id"],
        email=row["email"],
        display_name=row["display_name"] or "",
        is_admin=bool(row["is_admin"] or 0),
        environment=row["environment"] or "demo",
        disabled=bool(row["disabled"] or 0),
    )


async def _ensure_demo_users() -> None:
    """Ensure demo users exist in the database for testing."""
    from backend_api.db import db_session
    from backend_api.security import hash_password
    
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
async def signup(payload: SignupRequest) -> TokenResponse:
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
        # Use the create_access_token from security module
        from backend_api.security import create_access_token as create_token
        token = create_token(user=user, expires_in=timedelta(hours=12))
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
async def login(payload: LoginRequest) -> TokenResponse:
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
            from backend_api.security import verify_password as verify_pwd
            try:
                password_valid = verify_pwd(payload.password, password_hash)
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
        # Use the create_access_token from security module
        from backend_api.security import create_access_token as create_token
        token = create_token(user=user, expires_in=timedelta(hours=12))
        
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
    # Trust JWT claims (also avoids extra DB round-trip)
    return AuthUserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        is_admin=user.is_admin,
        environment=user.environment,
    )

    user: UserResponse


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def init_auth_tables():
    """Initialize authentication tables in the database."""
    with db_session() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                is_admin INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                last_login TEXT,
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                details TEXT DEFAULT '{}',
                ip_address TEXT,
                user_agent TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_logs(user_id)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_logs(created_at)
        """)
        
        conn.commit()


def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username."""
    with db_session() as conn:
        cursor = conn.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID."""
    with db_session() as conn:
        cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None


def create_user(user_data: UserCreate, is_admin: bool = False) -> dict:
    """Create a new user."""
    with db_session() as conn:
        # Check if username or email already exists
        cursor = conn.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (user_data.username, user_data.email)
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        
        password_hash = get_password_hash(user_data.password)
        created_at = datetime.utcnow().isoformat()
        
        cursor = conn.execute("""
            INSERT INTO users (username, email, password_hash, full_name, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_data.username,
            user_data.email,
            password_hash,
            user_data.full_name,
            1 if is_admin else 0,
            created_at
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        return {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "is_admin": is_admin,
            "is_active": True,
            "created_at": created_at,
            "last_login": None
        }


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current authenticated user from JWT token."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_current_admin_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Get current user and verify admin status."""
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def log_audit_event(
    user_id: Optional[int],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Log an audit event."""
    with db_session() as conn:
        conn.execute("""
            INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, ip_address, user_agent, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            action,
            resource_type,
            resource_id,
            str(details or {}),
            ip_address,
            user_agent,
            datetime.utcnow().isoformat()
        ))
        conn.commit()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """Register a new user."""
    init_auth_tables()
    
    user = create_user(user_data)
    
    log_audit_event(
        user_id=user["id"],
        action="user_signup",
        resource_type="user",
        resource_id=str(user["id"]),
        details={"username": user["username"], "email": user["email"]}
    )
    
    return UserResponse(**user)


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Authenticate user and return JWT token."""
    init_auth_tables()
    
    user = get_user_by_username(credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Update last login
    with db_session() as conn:
        conn.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), user["id"])
        )
        conn.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]},
        expires_delta=access_token_expires
    )
    
    log_audit_event(
        user_id=user["id"],
        action="user_login",
        resource_type="user",
        resource_id=str(user["id"])
    )
    
    user_response = UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name"),
        is_admin=bool(user.get("is_admin")),
        is_active=bool(user.get("is_active")),
        created_at=user["created_at"],
        last_login=datetime.utcnow().isoformat()
    )
    
    return TokenResponse(access_token=access_token, user=user_response)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information."""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        is_admin=bool(current_user.get("is_admin")),
        is_active=bool(current_user.get("is_active")),
        created_at=current_user["created_at"],
        last_login=current_user.get("last_login")
    )


@router.post("/admin/create-admin")
async def create_admin_account(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    """Create an admin account (admin only)."""
    user = create_user(user_data, is_admin=True)
    
    log_audit_event(
        user_id=current_user["id"],
        action="admin_created",
        resource_type="user",
        resource_id=str(user["id"]),
        details={"created_by": current_user["username"], "new_admin": user["username"]}
    )
    
    return UserResponse(**user)