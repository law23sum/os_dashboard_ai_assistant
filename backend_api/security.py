"""Auth helpers for the FastAPI backend (JWT + bcrypt).

This layer is intentionally lightweight (SQLite-backed users table).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt


_MIN_JWT_SECRET_LEN = 32
_REJECTED_JWT_SECRETS = {"dev-secret-change-me", "changeme", "change-me", "secret"}
_MIN_SEED_PASSWORD_LEN = 12


def require_jwt_secret() -> str:
    """Return the JWT signing secret from ``OSDASH_JWT_SECRET``.

    There is deliberately no default: a missing, placeholder or short secret
    makes tokens forgeable (or, if generated per-process, invalid after every
    restart), so we refuse to start instead.
    """
    secret = os.getenv("OSDASH_JWT_SECRET", "").strip()
    if not secret:
        raise RuntimeError(
            "OSDASH_JWT_SECRET is not set. Set it to a random value of at least "
            f"{_MIN_JWT_SECRET_LEN} characters, e.g. "
            "`python -c 'import secrets; print(secrets.token_urlsafe(48))'`."
        )
    if secret.lower() in _REJECTED_JWT_SECRETS or len(secret) < _MIN_JWT_SECRET_LEN:
        raise RuntimeError(
            "OSDASH_JWT_SECRET is a placeholder or shorter than "
            f"{_MIN_JWT_SECRET_LEN} characters; set a random value."
        )
    return secret


def _jwt_secret() -> str:
    return require_jwt_secret()


def seed_password_from_env(name: str) -> Optional[str]:
    """Read an optional seed password from the environment.

    Returns ``None`` when unset/empty. A set-but-too-short value is ignored
    (and logged by name only) so a weak seed password is never created.
    """
    value = os.getenv(name, "")
    if not value:
        return None
    if len(value) < _MIN_SEED_PASSWORD_LEN:
        logging.getLogger(__name__).error(
            "%s is shorter than %d characters; not seeding that account.",
            name,
            _MIN_SEED_PASSWORD_LEN,
        )
        return None
    return value


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
    tenant_id: Optional[str] = None
    workspace_id: Optional[str] = None


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

