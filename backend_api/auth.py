"""
Authentication and authorization system with user management.
Supports login, signup, JWT tokens, and role-based access control.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import sqlite3
from contextlib import contextmanager
from pathlib import Path
import shutil
import logging

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = secrets.token_urlsafe(32)  # Generate secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Database path
DB_PATH = Path(__file__).parent.parent / "assistant_hub_gui" / "users.db"


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = "user"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None


class UserInDB(User):
    hashed_password: str


@contextmanager
def get_user_db():
    """Context manager for user database connection."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _check_database_integrity(conn: sqlite3.Connection) -> bool:
    """Check if database is valid by running integrity check."""
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        return result[0] == "ok"
    except Exception as e:
        logger.error(f"Database integrity check failed: {e}")
        return False


def _recover_database() -> bool:
    """Attempt to recover corrupted database by backing it up and removing it."""
    try:
        # Backup the corrupted database
        if DB_PATH.exists():
            # Add timestamp to backup filename to avoid overwriting
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = DB_PATH.parent / f"{DB_PATH.stem}_{timestamp}.db.backup"
            shutil.copy2(DB_PATH, backup_path)
            logger.warning(f"Backed up corrupted database to {backup_path}")
            
            # Remove corrupted file so it can be recreated
            DB_PATH.unlink()
            logger.info("Removed corrupted database file, will be recreated on next init")
        return True
    except Exception as e:
        logger.error(f"Database recovery failed: {e}")
        return False


def init_user_db():
    """Initialize user database with tables."""
    try:
        # First, try to connect and check integrity
        if DB_PATH.exists():
            try:
                test_conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
                if not _check_database_integrity(test_conn):
                    test_conn.close()
                    logger.warning("Database integrity check failed, attempting recovery...")
                    if not _recover_database():
                        logger.error("Database recovery failed, creating new database")
                        if DB_PATH.exists():
                            backup_path = DB_PATH.with_suffix('.db.backup')
                            shutil.move(DB_PATH, backup_path)
                            logger.info(f"Moved corrupted database to {backup_path}")
                else:
                    test_conn.close()
            except sqlite3.DatabaseError as e:
                logger.warning(f"Database error detected: {e}, attempting recovery...")
                if not _recover_database():
                    logger.error("Database recovery failed, creating new database")
                    if DB_PATH.exists():
                        backup_path = DB_PATH.with_suffix('.db.backup')
                        shutil.move(DB_PATH, backup_path)
                        logger.info(f"Moved corrupted database to {backup_path}")
        
        # Ensure parent directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Now initialize the database
        with get_user_db() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    full_name TEXT,
                    role TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # Sessions/tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    refresh_token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # User activity log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    resource TEXT,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Create admin user if not exists
            cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
            if not cursor.fetchone():
                admin_password = "admin123"  # Default password - should be changed
                hashed = pwd_context.hash(admin_password)
                cursor.execute("""
                    INSERT INTO users (username, email, hashed_password, full_name, role)
                    VALUES (?, ?, ?, ?, ?)
                """, ("admin", "admin@osdashboard.ai", hashed, "System Administrator", "admin"))
                logger.info("✅ Admin user created: username='admin', password='admin123' (CHANGE THIS!)")
            
            # Create dummy test users for demonstration
            test_users = [
                ("alice", "alice@example.com", "Alice Johnson", "user"),
                ("bob", "bob@example.com", "Bob Smith", "user"),
                ("charlie", "charlie@example.com", "Charlie Brown", "user"),
            ]
            
            for username, email, full_name, role in test_users:
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if not cursor.fetchone():
                    hashed = pwd_context.hash("password123")
                    cursor.execute("""
                        INSERT INTO users (username, email, hashed_password, full_name, role)
                        VALUES (?, ?, ?, ?, ?)
                    """, (username, email, hashed, full_name, role))
            
            conn.commit()
            logger.info("User database initialized successfully")
            
    except sqlite3.DatabaseError as e:
        logger.error(f"Database error during initialization: {e}")
        # Try to recover one more time
        if DB_PATH.exists():
            backup_path = DB_PATH.with_suffix('.db.backup')
            try:
                shutil.move(DB_PATH, backup_path)
                logger.info(f"Moved corrupted database to {backup_path}, retrying initialization...")
                # Recursively call to retry with fresh database
                init_user_db()
            except Exception as recovery_error:
                logger.error(f"Failed to recover database: {recovery_error}")
                raise
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}", exc_info=True)
        raise


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


# JWT token utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Database operations
def get_user_by_username(username: str) -> Optional[UserInDB]:
    """Get user from database by username."""
    with get_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, hashed_password, full_name, role, is_active, created_at, last_login
            FROM users WHERE username = ?
        """, (username,))
        row = cursor.fetchone()
        if row:
            return UserInDB(
                id=row[0],
                username=row[1],
                email=row[2],
                hashed_password=row[3],
                full_name=row[4],
                role=row[5],
                is_active=bool(row[6]),
                created_at=row[7],
                last_login=row[8]
            )
    return None


def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user from database by ID."""
    with get_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, full_name, role, is_active, created_at, last_login
            FROM users WHERE id = ?
        """, (user_id,))
        row = cursor.fetchone()
        if row:
            return User(
                id=row[0],
                username=row[1],
                email=row[2],
                full_name=row[3],
                role=row[4],
                is_active=bool(row[5]),
                created_at=row[6],
                last_login=row[7]
            )
    return None


def create_user(user_data: UserCreate) -> User:
    """Create a new user in the database."""
    with get_user_db() as conn:
        cursor = conn.cursor()
        hashed_password = get_password_hash(user_data.password)
        
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, full_name)
            VALUES (?, ?, ?, ?)
        """, (user_data.username, user_data.email, hashed_password, user_data.full_name))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        return get_user_by_id(user_id)


def update_last_login(user_id: int):
    """Update user's last login timestamp."""
    with get_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
        """, (user_id,))
        conn.commit()


def log_user_activity(user_id: int, action: str, resource: Optional[str] = None, 
                      details: Optional[str] = None, ip_address: Optional[str] = None,
                      user_agent: Optional[str] = None):
    """Log user activity."""
    with get_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_activity (user_id, action, resource, details, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, action, resource, details, ip_address, user_agent))
        conn.commit()


# Authentication functions
def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with username and password."""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None or user_id is None:
            raise credentials_exception
            
        token_data = TokenData(username=username, user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_id(token_data.user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current admin user (requires admin role)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user


# Initialize database on module import
# Wrap in try-except to prevent import failures from crashing the app
try:
    init_user_db()
except Exception as e:
    logger.error(f"Failed to initialize user database: {e}", exc_info=True)
    # Don't raise - allow the app to start, but authentication will fail
    # This gives the admin a chance to fix the database manually
