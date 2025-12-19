"""Authentication router with signup/login and RBAC."""

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
async def logout(current_user: User = Depends(get_current_active_user), request: Request | None = None):
    """Logout current user (server-side token invalidation is not implemented)."""
    log_user_activity(
        current_user.id,
        "logout",
        details=f"User logged out: {current_user.username}",
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
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
