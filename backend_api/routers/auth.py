"""Authentication endpoints (signup/login/me)."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
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


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=256)


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=256)
    display_name: str = Field(default="", max_length=80)
    environment: str = Field(default="demo", pattern="^(demo|prod)$")


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


@router.post("/auth/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest) -> TokenResponse:
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
        row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    user = _row_to_user(row)
    token = create_access_token(user=user, expires_in=timedelta(hours=12))
    return TokenResponse(
        access_token=token,
        user=AuthUserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            is_admin=user.is_admin,
            environment=user.environment,
        ),
    )


@router.post("/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    email = payload.email.strip().lower()
    with db_session() as db:
        row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if bool(row["disabled"] or 0):
            raise HTTPException(status_code=403, detail="Account disabled")
        if not verify_password(payload.password, row["password_hash"] or ""):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        db.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now().isoformat(timespec="seconds"), row["id"]),
        )
    user = _row_to_user(row)
    token = create_access_token(user=user, expires_in=timedelta(hours=12))
    return TokenResponse(
        access_token=token,
        user=AuthUserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            is_admin=user.is_admin,
            environment=user.environment,
        ),
    )


@router.get("/auth/me", response_model=AuthUserResponse)
async def me(user: AuthUser = Depends(get_current_user)) -> AuthUserResponse:
    # Trust JWT claims (also avoids extra DB round-trip)
    return AuthUserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        is_admin=user.is_admin,
        environment=user.environment,
    )

