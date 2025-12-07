"""Authentication Helpers - Functions for handling generic token storage, retrieval, and refresh."""

import os
import json
import pickle
from typing import Dict, Any, Optional
from pathlib import Path


class TokenManager:
    """Manages OAuth tokens and credentials."""

    def __init__(self, credentials_dir: str = "config/credentials"):
        self.credentials_dir = Path(credentials_dir)
        self.credentials_dir.mkdir(exist_ok=True, parents=True)

    def save_token(self, service_name: str, token_data: Dict[str, Any], use_pickle: bool = False):
        """Save token data to file."""
        file_path = self.credentials_dir / f"{service_name}_token.json"
        if use_pickle:
            file_path = file_path.with_suffix('.pickle')
            with open(file_path, 'wb') as f:
                pickle.dump(token_data, f)
        else:
            with open(file_path, 'w') as f:
                json.dump(token_data, f, indent=2)

    def load_token(self, service_name: str, use_pickle: bool = False) -> Optional[Dict[str, Any]]:
        """Load token data from file."""
        file_path = self.credentials_dir / f"{service_name}_token.json"
        if use_pickle:
            file_path = file_path.with_suffix('.pickle')

        if not file_path.exists():
            return None

        try:
            if use_pickle:
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
            else:
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception:
            return None

    def token_exists(self, service_name: str) -> bool:
        """Check if token file exists."""
        json_path = self.credentials_dir / f"{service_name}_token.json"
        pickle_path = self.credentials_dir / f"{service_name}_token.pickle"
        return json_path.exists() or pickle_path.exists()

    def delete_token(self, service_name: str):
        """Delete token file."""
        json_path = self.credentials_dir / f"{service_name}_token.json"
        pickle_path = self.credentials_dir / f"{service_name}_token.pickle"

        if json_path.exists():
            json_path.unlink()
        if pickle_path.exists():
            pickle_path.unlink()

    def is_token_expired(self, token_data: Dict[str, Any]) -> bool:
        """Check if token is expired."""
        # This is a simplified check - implement based on specific service requirements
        expires_at = token_data.get('expires_at')
        if not expires_at:
            return False

        import time
        return time.time() > expires_at


class CredentialManager:
    """Manages API credentials and secrets."""

    def __init__(self, credentials_dir: str = "config/credentials"):
        self.credentials_dir = Path(credentials_dir)
        self.credentials_dir.mkdir(exist_ok=True, parents=True)

    def save_credentials(self, service_name: str, credentials: Dict[str, Any]):
        """Save credentials to file."""
        file_path = self.credentials_dir / f"{service_name}_credentials.json"
        with open(file_path, 'w') as f:
            json.dump(credentials, f, indent=2)

    def load_credentials(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Load credentials from file."""
        file_path = self.credentials_dir / f"{service_name}_credentials.json"
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def get_from_env(self, service_name: str, keys: list) -> Dict[str, str]:
        """Get credentials from environment variables."""
        credentials = {}
        for key in keys:
            env_key = f"{service_name.upper()}_{key.upper()}"
            value = os.getenv(env_key)
            if value:
                credentials[key] = value
        return credentials
