"""
Authentication router with login, signup, and user management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from datetime import timedelta
from typing import List, Optional
import json

from backend_api.auth import (
    User,
    UserCreate,
    UserLogin,
    Token,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    get_current_admin_user,
    create_user,
    update_last_login,
    log_user_activity,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_user_db,
)

router = APIRouter()


@router.post("/auth/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, request: Request):
    """
    Register a new user account.
    
    - **username**: Unique username
    - **email**: Valid email address
    - **password**: Strong password
    - **full_name**: Optional full name
    """
    try:
        # Check if username or email already exists
        with get_user_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", 
                          (user_data.username, user_data.email))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or email already registered"
                )
        
        # Create user
        user = create_user(user_data)
        
        # Log activity
        log_user_activity(
            user.id,
            "signup",
            details=f"New user registration: {user.username}",
            ip_address=request.client.host if request.client else None
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin, request: Request):
    """
    Authenticate user and return access and refresh tokens.
    
    - **username**: User's username
    - **password**: User's password
    """
    user = authenticate_user(credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    update_last_login(user.id)
    
    # Log activity
    log_user_activity(
        user.id,
        "login",
        details=f"User logged in: {user.username}",
        ip_address=request.client.host if request.client else None
    )
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_active_user), request: Request = None):
    """
    Logout current user (invalidate tokens).
    """
    # Log activity
    log_user_activity(
        current_user.id,
        "logout",
        details=f"User logged out: {current_user.username}",
        ip_address=request.client.host if request and request.client else None
    )
    
    return {"message": "Successfully logged out"}


@router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user's information.
    """
    return current_user


@router.get("/auth/users", response_model=List[User])
async def list_users(
    admin_user: User = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100
):
    """
    List all users (admin only).
    """
    with get_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, full_name, role, is_active, created_at, last_login
            FROM users
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, skip))
        
        users = []
        for row in cursor.fetchall():
            users.append(User(
                id=row[0],
                username=row[1],
                email=row[2],
                full_name=row[3],
                role=row[4],
                is_active=bool(row[5]),
                created_at=row[6],
                last_login=row[7]
            ))
        
        return users


@router.get("/auth/users/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Get specific user by ID (admin only).
    """
    with get_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, full_name, role, is_active, created_at, last_login
            FROM users WHERE id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
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


@router.get("/auth/activity")
async def get_user_activity(
    current_user: User = Depends(get_current_active_user),
    limit: int = 50
):
    """
    Get current user's activity log.
    """
    with get_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, action, resource, details, ip_address, timestamp
            FROM user_activity
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (current_user.id, limit))
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                "id": row[0],
                "action": row[1],
                "resource": row[2],
                "details": row[3],
                "ip_address": row[4],
                "timestamp": row[5]
            })
        
        return {"activities": activities}


@router.get("/auth/activity/all")
async def get_all_activity(
    admin_user: User = Depends(get_current_admin_user),
    limit: int = 100
):
    """
    Get all users' activity log (admin only).
    """
    with get_user_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                ua.id, ua.user_id, u.username, ua.action, 
                ua.resource, ua.details, ua.ip_address, ua.timestamp
            FROM user_activity ua
            JOIN users u ON ua.user_id = u.id
            ORDER BY ua.timestamp DESC
            LIMIT ?
        """, (limit,))
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                "id": row[0],
                "user_id": row[1],
                "username": row[2],
                "action": row[3],
                "resource": row[4],
                "details": row[5],
                "ip_address": row[6],
                "timestamp": row[7]
            })
        
        return {"activities": activities}


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
