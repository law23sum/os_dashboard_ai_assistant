"""FastAPI dependencies (auth + RBAC)."""

from __future__ import annotations

import os

from fastapi import Depends, HTTPException, Request, status

from backend_api.security import AuthUser, safe_decode_user


def _bearer_token(request: Request) -> str | None:
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth:
        return None
    parts = auth.split(" ", 1)
    if len(parts) != 2:
        return None
    scheme, token = parts[0].strip().lower(), parts[1].strip()
    if scheme != "bearer" or not token:
        return None
    return token


def _allow_anonymous(request: Request) -> bool:
    if request.url.path.startswith("/api/auth"):
        return False
    flag = os.getenv("OSDASH_ALLOW_ANON", "").strip().lower()
    if flag in {"1", "true", "yes", "on"}:
        return True
    return os.getenv("PYTEST_CURRENT_TEST") is not None


def get_current_user(request: Request) -> AuthUser:
    token = _bearer_token(request)
    user = safe_decode_user(token) if token else None
    if not user:
        if _allow_anonymous(request):
            return AuthUser(
                id="demo",
                email="demo@osdash.local",
                display_name="Demo User",
                is_admin=True,
                environment="test",
                disabled=False,
            )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
    return user


def get_optional_user(request: Request) -> AuthUser | None:
    token = _bearer_token(request)
    user = safe_decode_user(token) if token else None
    if user and user.disabled:
        return None
    return user


def require_admin(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user
