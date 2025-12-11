"""
Configuration management for OS Dashboard AI Assistant
"""
import os
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class APIConfig(BaseSettings):
    """Configuration class for all API credentials and settings"""
    
    # OpenAI/ChatGPT Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_organization: Optional[str] = Field(default=None, env="OPENAI_ORGANIZATION")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    
    # Microsoft Graph API Configuration
    microsoft_client_id: Optional[str] = Field(default=None, env="MICROSOFT_CLIENT_ID")
    microsoft_client_secret: Optional[str] = Field(default=None, env="MICROSOFT_CLIENT_SECRET")
    microsoft_tenant_id: Optional[str] = Field(default=None, env="MICROSOFT_TENANT_ID")
    microsoft_redirect_uri: str = Field(default="http://localhost:8000/auth/callback", env="MICROSOFT_REDIRECT_URI")
    
    # Google APIs Configuration
    google_credentials_file: Optional[str] = Field(default="credentials.json", env="GOOGLE_CREDENTIALS_FILE")
    google_token_file: str = Field(default="token.json", env="GOOGLE_TOKEN_FILE")
    google_scopes: list = Field(default=[
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/calendar'
    ])
    
    # GitHub Configuration
    github_token: Optional[str] = Field(default=None, env="GITHUB_TOKEN")
    github_username: Optional[str] = Field(default=None, env="GITHUB_USERNAME")
    
    # Adobe Configuration
    adobe_client_id: Optional[str] = Field(default=None, env="ADOBE_CLIENT_ID")
    adobe_client_secret: Optional[str] = Field(default=None, env="ADOBE_CLIENT_SECRET")
    adobe_organization_id: Optional[str] = Field(default=None, env="ADOBE_ORGANIZATION_ID")
    adobe_account_id: Optional[str] = Field(default=None, env="ADOBE_ACCOUNT_ID")
    adobe_private_key_file: Optional[str] = Field(default="private.key", env="ADOBE_PRIVATE_KEY_FILE")
    
    # Apple Calendar (CalDAV) Configuration
    caldav_url: Optional[str] = Field(default=None, env="CALDAV_URL")
    caldav_username: Optional[str] = Field(default=None, env="CALDAV_USERNAME")
    caldav_password: Optional[str] = Field(default=None, env="CALDAV_PASSWORD")
    
    # Application Settings
    app_name: str = Field(default="OS Dashboard AI Assistant")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global configuration instance
config = APIConfig()

def get_config() -> APIConfig:
    """Get the global configuration instance"""
    return config

def validate_config() -> Dict[str, bool]:
    """Validate that required API credentials are present"""
    validation_results = {
        "openai": bool(config.openai_api_key),
        "microsoft": bool(config.microsoft_client_id and config.microsoft_client_secret and config.microsoft_tenant_id),
        "google": bool(os.path.exists(config.google_credentials_file)),
        "github": bool(config.github_token),
        "adobe": bool(config.adobe_client_id and config.adobe_client_secret),
        "caldav": bool(config.caldav_url and config.caldav_username and config.caldav_password)
    }
    return validation_results