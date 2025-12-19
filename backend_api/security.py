"""Auth helpers for the FastAPI backend (JWT + bcrypt).

This layer is intentionally lightweight (SQLite-backed users table).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt


def _jwt_secret() -> str:
    return os.getenv("OSDASH_JWT_SECRET", "dev-secret-change-me")


def _jwt_algorithm() -> str:
    return os.getenv("OSDASH_JWT_ALG", "HS256")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


@dataclass(frozen=True)
class AuthUser:
    id: str
    email: str
    display_name: str
    is_admin: bool
    environment: str
    disabled: bool


def create_access_token(*, user: AuthUser, expires_in: Optional[timedelta] = None) -> str:
    now = datetime.now(timezone.utc)
    exp = now + (expires_in or timedelta(hours=12))
    payload = {
        "sub": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "is_admin": bool(user.is_admin),
        "environment": user.environment,
        "disabled": bool(user.disabled),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=_jwt_algorithm())


def decode_token(token: str) -> dict:
    return jwt.decode(token, _jwt_secret(), algorithms=[_jwt_algorithm()])


def user_from_claims(claims: dict) -> AuthUser:
    return AuthUser(
        id=str(claims.get("sub") or ""),
        email=str(claims.get("email") or ""),
        display_name=str(claims.get("display_name") or ""),
        is_admin=bool(claims.get("is_admin") or False),
        environment=str(claims.get("environment") or "demo"),
        disabled=bool(claims.get("disabled") or False),
    )


def safe_decode_user(token: str) -> Optional[AuthUser]:
    try:
        claims = decode_token(token)
        user = user_from_claims(claims)
        if not user.id or not user.email:
            return None
        return user
    except JWTError:
        return None

