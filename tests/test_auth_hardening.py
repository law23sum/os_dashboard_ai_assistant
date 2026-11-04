"""Regression tests for auth hardening.

Covers: required JWT secret (no default), no hardcoded/seeded accounts,
insert-only env-driven seeding, and a generic /api/health error.
"""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
GOOD_SECRET = "unit-test-secret-" + "k" * 32


def _run_python(code: str, **env_overrides):
    env = {k: v for k, v in os.environ.items() if not k.startswith("OSDASH_")}
    env.update(env_overrides)
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


# --------------------------------------------------------------------------
# JWT secret handling
# --------------------------------------------------------------------------
class TestJwtSecret:
    def test_missing_secret_is_rejected(self, monkeypatch):
        from backend_api import security

        monkeypatch.delenv("OSDASH_JWT_SECRET", raising=False)
        with pytest.raises(RuntimeError, match="OSDASH_JWT_SECRET"):
            security.require_jwt_secret()
        with pytest.raises(RuntimeError):
            security._jwt_secret()

    @pytest.mark.parametrize("value", ["", "   ", "dev-secret-change-me", "short", "x" * 31])
    def test_placeholder_or_short_secret_is_rejected(self, monkeypatch, value):
        from backend_api import security

        monkeypatch.setenv("OSDASH_JWT_SECRET", value)
        with pytest.raises(RuntimeError):
            security.require_jwt_secret()

    def test_valid_secret_is_returned(self, monkeypatch):
        from backend_api import security

        monkeypatch.setenv("OSDASH_JWT_SECRET", GOOD_SECRET)
        assert security.require_jwt_secret() == GOOD_SECRET

    def test_no_placeholder_default_in_source(self):
        src = (ROOT / "backend_api" / "security.py").read_text()
        assert 'getenv("OSDASH_JWT_SECRET", "dev-secret' not in src
        assert "token_urlsafe" not in (ROOT / "backend_api" / "auth.py").read_text()

    def test_tokens_survive_a_restart(self, monkeypatch):
        """A token minted by one process verifies in another with the same env secret."""
        code_make = (
            "from datetime import timedelta\n"
            "from backend_api.security import AuthUser, create_access_token\n"
            "u = AuthUser(id='1', email='a@b.c', display_name='A', is_admin=False,"
            " environment='demo', disabled=False)\n"
            "print(create_access_token(user=u, expires_in=timedelta(hours=1)))\n"
        )
        first = _run_python(code_make, OSDASH_JWT_SECRET=GOOD_SECRET)
        assert first.returncode == 0, first.stderr[-500:]
        token = first.stdout.strip().splitlines()[-1]

        from backend_api import security
        from jose import jwt

        monkeypatch.setenv("OSDASH_JWT_SECRET", GOOD_SECRET)
        claims = jwt.decode(token, security.require_jwt_secret(), algorithms=["HS256"])
        assert claims["sub"] == "1"

    def test_auth_module_refuses_to_import_without_secret(self):
        result = _run_python("import backend_api.auth")
        assert result.returncode != 0
        assert "OSDASH_JWT_SECRET" in result.stderr

    def test_auth_module_uses_env_secret(self):
        result = _run_python(
            "import backend_api.auth as a; print(a.SECRET_KEY == %r)" % GOOD_SECRET,
            OSDASH_JWT_SECRET=GOOD_SECRET,
        )
        assert result.returncode == 0, result.stderr[-500:]
        assert result.stdout.strip().endswith("True")


# --------------------------------------------------------------------------
# No seeded accounts in backend_api/auth.py
# --------------------------------------------------------------------------
class TestInitUserDb:
    @pytest.fixture
    def auth_mod(self, monkeypatch, tmp_path):
        monkeypatch.setenv("OSDASH_JWT_SECRET", GOOD_SECRET)
        from backend_api import auth

        monkeypatch.setattr(auth, "DB_PATH", tmp_path / "users.db")
        for name in ("OSDASH_BOOTSTRAP_ADMIN_PASSWORD", "OSDASH_BOOTSTRAP_ADMIN_EMAIL"):
            monkeypatch.delenv(name, raising=False)
        return auth

    @staticmethod
    def _usernames(path):
        conn = sqlite3.connect(path)
        try:
            return [r[0] for r in conn.execute("SELECT username FROM users")]
        finally:
            conn.close()

    def test_no_accounts_are_seeded_by_default(self, auth_mod):
        auth_mod.init_user_db()
        assert self._usernames(auth_mod.DB_PATH) == []

    def test_no_hardcoded_passwords_in_source(self):
        src = (ROOT / "backend_api" / "auth.py").read_text()
        for needle in ("admin123", "password123"):
            assert needle not in src

    def test_admin_only_created_from_env_and_password_not_logged(self, auth_mod, monkeypatch, caplog):
        pw = "bootstrap-pass-" + "z" * 12
        monkeypatch.setenv("OSDASH_BOOTSTRAP_ADMIN_PASSWORD", pw)
        with caplog.at_level("DEBUG"):
            auth_mod.init_user_db()
        assert self._usernames(auth_mod.DB_PATH) == ["admin"]
        assert pw not in caplog.text
        conn = sqlite3.connect(auth_mod.DB_PATH)
        (hashed,) = conn.execute("SELECT hashed_password FROM users WHERE username='admin'").fetchone()
        conn.close()
        assert hashed != pw and auth_mod.pwd_context.verify(pw, hashed)

    def test_short_bootstrap_password_is_ignored(self, auth_mod, monkeypatch):
        monkeypatch.setenv("OSDASH_BOOTSTRAP_ADMIN_PASSWORD", "short")
        auth_mod.init_user_db()
        assert self._usernames(auth_mod.DB_PATH) == []


# --------------------------------------------------------------------------
# Router-level demo seeding (backend_api/routers/auth.py)
# --------------------------------------------------------------------------
class TestEnsureDemoUsers:
    @pytest.fixture
    def hub(self, monkeypatch, tmp_path):
        monkeypatch.setenv("OSDASH_JWT_SECRET", GOOD_SECRET)
        for name in (
            "OSDASH_BOOTSTRAP_ADMIN_PASSWORD",
            "OSDASH_BOOTSTRAP_ADMIN_EMAIL",
            "OSDASH_DEMO_USER_PASSWORD",
        ):
            monkeypatch.delenv(name, raising=False)
        from assistant_hub import db as hub_shim
        from assistant_hub_gui.assistant_hub import db as hub_db
        from backend_api import db as api_db

        # ``assistant_hub.db`` is a star-import shim of the canonical module,
        # so DB_FILE has to be redirected on both.
        db_file = str(tmp_path / "hub.db")
        monkeypatch.setattr(hub_db, "DB_FILE", db_file)
        monkeypatch.setattr(hub_shim, "DB_FILE", db_file)
        monkeypatch.setattr(api_db, "_DB_INITIALIZED", False)
        return api_db

    @staticmethod
    def _emails(api_db):
        with api_db.db_session() as db:
            return sorted(r["email"] for r in db.execute("SELECT email FROM users"))

    @staticmethod
    async def _seed():
        from backend_api.routers.auth import _ensure_demo_users

        await _ensure_demo_users()

    @pytest.mark.asyncio
    async def test_nothing_seeded_without_env(self, hub):
        await self._seed()
        emails = self._emails(hub)
        assert not [e for e in emails if e.endswith("@demo.local")]

    def test_no_hardcoded_passwords_in_source(self):
        src = (ROOT / "backend_api" / "routers" / "auth.py").read_text()
        for needle in ("admin123", "user123", "password123"):
            assert needle not in src

    @pytest.mark.asyncio
    async def test_seeds_from_env_and_is_insert_only(self, hub, monkeypatch):
        from backend_api.security import hash_password, verify_password

        admin_pw = "admin-seed-pass-" + "a" * 8
        user_pw = "user-seed-pass-" + "b" * 8
        monkeypatch.setenv("OSDASH_BOOTSTRAP_ADMIN_PASSWORD", admin_pw)
        monkeypatch.setenv("OSDASH_DEMO_USER_PASSWORD", user_pw)
        await self._seed()
        emails = self._emails(hub)
        assert "admin@demo.local" in emails and "alice@demo.local" in emails

        with hub.db_session() as db:
            row = db.execute(
                "SELECT password_hash, is_admin FROM users WHERE email='admin@demo.local'"
            ).fetchone()
        assert verify_password(admin_pw, row["password_hash"]) and row["is_admin"] == 1

        # Operator changes the password, revokes admin and disables the account.
        changed = hash_password("operator-changed-" + "c" * 8)
        with hub.db_session() as db:
            db.execute(
                "UPDATE users SET password_hash=?, is_admin=0, disabled=1 WHERE email='admin@demo.local'",
                (changed,),
            )
        await self._seed()  # simulates a restart / another login
        with hub.db_session() as db:
            row = db.execute(
                "SELECT password_hash, is_admin, disabled FROM users WHERE email='admin@demo.local'"
            ).fetchone()
        assert row["password_hash"] == changed
        assert row["is_admin"] == 0 and row["disabled"] == 1

    @pytest.mark.asyncio
    async def test_short_password_not_seeded(self, hub, monkeypatch):
        monkeypatch.setenv("OSDASH_BOOTSTRAP_ADMIN_PASSWORD", "short")
        monkeypatch.setenv("OSDASH_DEMO_USER_PASSWORD", "short")
        await self._seed()
        assert not [e for e in self._emails(hub) if e.endswith("@demo.local")]


# --------------------------------------------------------------------------
# /api/health must not leak exception detail
# --------------------------------------------------------------------------
class TestHealthEndpoint:
    def test_error_detail_is_not_returned_but_is_logged(self, monkeypatch, caplog):
        monkeypatch.setenv("OSDASH_JWT_SECRET", GOOD_SECRET)
        from fastapi.testclient import TestClient
        from backend_api import db as api_db
        from backend_api.main import app

        leak = "unable to open /srv/private/assistant_hub.db: secret-detail-123"

        def boom():
            raise RuntimeError(leak)

        monkeypatch.setattr(api_db, "db_session", boom)
        client = TestClient(app)  # no context manager: skip startup events
        with caplog.at_level("ERROR"):
            resp = client.get("/api/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "degraded" and body["database"] == "disconnected"
        assert "secret-detail-123" not in resp.text
        assert "/srv/private" not in resp.text
        assert body["error"] == "database check failed"
        assert "secret-detail-123" in caplog.text  # detail still goes to the log

    def test_healthy_response_unchanged(self, monkeypatch):
        monkeypatch.setenv("OSDASH_JWT_SECRET", GOOD_SECRET)
        from fastapi.testclient import TestClient
        from backend_api.main import app

        resp = TestClient(app).get("/api/health")
        assert resp.status_code == 200 and resp.json()["status"] in {"ok", "degraded"}
