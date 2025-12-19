"""Authentication and User Management API Router.

Provides endpoints for user authentication, registration, and session management.
Implements secure password hashing, JWT-like session tokens, and user data protection.
"""

from __future__ import annotations

import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Header, Response, Request
from pydantic import BaseModel, Field, EmailStr

from backend_api.db import db_session

router = APIRouter()

# Constants
SESSION_EXPIRY_HOURS = 24 * 7  # 7 days
PASSWORD_MIN_LENGTH = 8


class UserCreate(BaseModel):
    """User registration request."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH)
    display_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login request."""
    username: str
    password: str


class UserResponse(BaseModel):
    """User response (public data only)."""
    id: str
    username: str
    email: str
    display_name: Optional[str]
    is_admin: bool
    is_active: bool
    created_at: str
    last_login: Optional[str]


class SessionResponse(BaseModel):
    """Session response with token."""
    token: str
    user: UserResponse
    expires_at: str


class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str = Field(..., min_length=PASSWORD_MIN_LENGTH)


def _hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash a password with a salt."""
    if salt is None:
        salt = secrets.token_hex(32)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return hashed.hex(), salt


def _verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify a password against its hash."""
    test_hash, _ = _hash_password(password, salt)
    return secrets.compare_digest(test_hash, hashed)


def _generate_session_token() -> str:
    """Generate a secure session token."""
    return secrets.token_urlsafe(64)


def _now_iso() -> str:
    """Get current UTC time as ISO string."""
    return datetime.utcnow().isoformat(timespec="seconds")


def _ensure_auth_tables(conn: sqlite3.Connection) -> None:
    """Ensure authentication tables exist."""
    c = conn.cursor()
    
    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            display_name TEXT,
            is_admin INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            is_demo_user INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            last_login TEXT,
            login_count INTEGER DEFAULT 0,
            settings_json TEXT DEFAULT '{}'
        )
    """)
    
    # Sessions table
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Activity log table
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            action_details TEXT,
            ip_address TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Create indexes
    c.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(token)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id, is_active)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_activity_user ON user_activity_log(user_id, timestamp)")
    
    conn.commit()


def _log_activity(conn: sqlite3.Connection, user_id: str, action_type: str, 
                  details: Optional[str] = None, ip_address: Optional[str] = None) -> None:
    """Log user activity."""
    c = conn.cursor()
    c.execute("""
        INSERT INTO user_activity_log (user_id, action_type, action_details, ip_address, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, action_type, details, ip_address, _now_iso()))
    conn.commit()


def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Get current user from authorization header."""
    if not authorization:
        return None
    
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization
    
    with db_session() as conn:
        _ensure_auth_tables(conn)
        c = conn.cursor()
        
        c.execute("""
            SELECT u.*, s.expires_at, s.id as session_id
            FROM users u
            JOIN user_sessions s ON u.id = s.user_id
            WHERE s.token = ? AND s.is_active = 1
        """, (token,))
        
        row = c.fetchone()
        if not row:
            return None
        
        # Check expiration
        expires_at = datetime.fromisoformat(row["expires_at"])
        if datetime.utcnow() > expires_at:
            c.execute("UPDATE user_sessions SET is_active = 0 WHERE id = ?", (row["session_id"],))
            conn.commit()
            return None
        
        return dict(row)


def require_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Require authenticated user."""
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_admin(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Require admin user."""
    user = require_user(authorization)
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.post("/register", response_model=SessionResponse, status_code=201)
async def register_user(user_data: UserCreate, request: Request) -> SessionResponse:
    """Register a new user account."""
    with db_session() as conn:
        _ensure_auth_tables(conn)
        c = conn.cursor()
        
        # Check if username or email exists
        c.execute("SELECT id FROM users WHERE username = ? OR email = ?", 
                  (user_data.username, user_data.email))
        if c.fetchone():
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        # Create user
        user_id = uuid4().hex
        password_hash, password_salt = _hash_password(user_data.password)
        now = _now_iso()
        
        c.execute("""
            INSERT INTO users (id, username, email, password_hash, password_salt, 
                              display_name, created_at, last_login, login_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (user_id, user_data.username, user_data.email, password_hash, 
              password_salt, user_data.display_name, now, now))
        
        # Create session
        session_id = uuid4().hex
        token = _generate_session_token()
        expires_at = (datetime.utcnow() + timedelta(hours=SESSION_EXPIRY_HOURS)).isoformat()
        
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        c.execute("""
            INSERT INTO user_sessions (id, user_id, token, ip_address, user_agent, 
                                       created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, user_id, token, client_ip, user_agent, now, expires_at))
        
        conn.commit()
        
        _log_activity(conn, user_id, "REGISTER", "New user registration", client_ip)
        
        return SessionResponse(
            token=token,
            user=UserResponse(
                id=user_id,
                username=user_data.username,
                email=user_data.email,
                display_name=user_data.display_name,
                is_admin=False,
                is_active=True,
                created_at=now,
                last_login=now
            ),
            expires_at=expires_at
        )


@router.post("/login", response_model=SessionResponse)
async def login_user(credentials: UserLogin, request: Request) -> SessionResponse:
    """Login with username and password."""
    with db_session() as conn:
        _ensure_auth_tables(conn)
        c = conn.cursor()
        
        c.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", 
                  (credentials.username,))
        user = c.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not _verify_password(credentials.password, user["password_hash"], user["password_salt"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Update login stats
        now = _now_iso()
        c.execute("""
            UPDATE users SET last_login = ?, login_count = login_count + 1 
            WHERE id = ?
        """, (now, user["id"]))
        
        # Create new session
        session_id = uuid4().hex
        token = _generate_session_token()
        expires_at = (datetime.utcnow() + timedelta(hours=SESSION_EXPIRY_HOURS)).isoformat()
        
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        c.execute("""
            INSERT INTO user_sessions (id, user_id, token, ip_address, user_agent, 
                                       created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, user["id"], token, client_ip, user_agent, now, expires_at))
        
        conn.commit()
        
        _log_activity(conn, user["id"], "LOGIN", "User login", client_ip)
        
        return SessionResponse(
            token=token,
            user=UserResponse(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                display_name=user["display_name"],
                is_admin=bool(user["is_admin"]),
                is_active=bool(user["is_active"]),
                created_at=user["created_at"],
                last_login=now
            ),
            expires_at=expires_at
        )


@router.post("/logout")
async def logout_user(authorization: Optional[str] = Header(None)) -> Dict[str, str]:
    """Logout current session."""
    if not authorization:
        return {"message": "Already logged out"}
    
    token = authorization[7:] if authorization.startswith("Bearer ") else authorization
    
    with db_session() as conn:
        _ensure_auth_tables(conn)
        c = conn.cursor()
        
        c.execute("""
            UPDATE user_sessions SET is_active = 0 
            WHERE token = ?
        """, (token,))
        conn.commit()
        
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user: Dict = Depends(require_user)) -> UserResponse:
    """Get current user profile."""
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        display_name=user.get("display_name"),
        is_admin=bool(user.get("is_admin")),
        is_active=bool(user.get("is_active")),
        created_at=user["created_at"],
        last_login=user.get("last_login")
    )


@router.put("/me/password")
async def change_password(
    passwords: PasswordChange, 
    user: Dict = Depends(require_user)
) -> Dict[str, str]:
    """Change current user's password."""
    with db_session() as conn:
        _ensure_auth_tables(conn)
        c = conn.cursor()
        
        # Verify current password
        if not _verify_password(passwords.current_password, 
                                user["password_hash"], user["password_salt"]):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update password
        new_hash, new_salt = _hash_password(passwords.new_password)
        c.execute("""
            UPDATE users SET password_hash = ?, password_salt = ?, updated_at = ?
            WHERE id = ?
        """, (new_hash, new_salt, _now_iso(), user["id"]))
        
        # Invalidate other sessions
        c.execute("""
            UPDATE user_sessions SET is_active = 0 
            WHERE user_id = ? AND id != ?
        """, (user["id"], user.get("session_id")))
        
        conn.commit()
        
        _log_activity(conn, user["id"], "PASSWORD_CHANGE", "Password changed")
        
    return {"message": "Password changed successfully"}


@router.get("/sessions")
async def list_user_sessions(user: Dict = Depends(require_user)) -> List[Dict[str, Any]]:
    """List current user's active sessions."""
    with db_session() as conn:
        _ensure_auth_tables(conn)
        c = conn.cursor()
        
        c.execute("""
            SELECT id, ip_address, user_agent, created_at, expires_at
            FROM user_sessions
            WHERE user_id = ? AND is_active = 1
            ORDER BY created_at DESC
        """, (user["id"],))
        
        return [dict(row) for row in c.fetchall()]


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str, 
    user: Dict = Depends(require_user)
) -> Dict[str, str]:
    """Revoke a specific session."""
    with db_session() as conn:
        _ensure_auth_tables(conn)
        c = conn.cursor()
        
        c.execute("""
            UPDATE user_sessions SET is_active = 0 
            WHERE id = ? AND user_id = ?
        """, (session_id, user["id"]))
        
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        conn.commit()
        
    return {"message": "Session revoked"}


@router.get("/activity")
async def get_user_activity(
    limit: int = 50,
    user: Dict = Depends(require_user)
) -> List[Dict[str, Any]]:
    """Get current user's activity log."""
    with db_session() as conn:
        _ensure_auth_tables(conn)
        c = conn.cursor()
        
        c.execute("""
            SELECT * FROM user_activity_log
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user["id"], limit))
        
        return [dict(row) for row in c.fetchall()]
