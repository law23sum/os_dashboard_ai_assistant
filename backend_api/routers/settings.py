"""Settings API router."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from assistant_hub.db import load_settings, save_settings
from backend_api.db import db_session

router = APIRouter()

class SettingsResponse(BaseModel):
    theme: str
    default_view: str
    show_system_status: bool
    font_scale: str
    data_preferences: Dict[str, bool]
    change_permission_mode: Optional[str] = None
    continuity_mode: Optional[str] = None
    risk_appetite: Optional[str] = None
    default_persona: Optional[str] = None
    governance_banner: Optional[str] = None

class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    default_view: Optional[str] = None
    show_system_status: Optional[bool] = None
    font_scale: Optional[str] = None
    data_preferences: Optional[Dict[str, bool]] = None
    change_permission_mode: Optional[str] = None
    continuity_mode: Optional[str] = None
    risk_appetite: Optional[str] = None
    default_persona: Optional[str] = None
    governance_banner: Optional[str] = None

@router.get("/", response_model=SettingsResponse)
async def get_settings():
    """Get current settings."""
    with db_session() as db:
        settings = load_settings(db)
    return SettingsResponse(
        theme=settings.theme,
        default_view=settings.default_view,
        show_system_status=settings.show_system_status,
        font_scale=settings.font_scale,
        data_preferences=settings.data_preferences or {},
        change_permission_mode=getattr(settings, "change_permission_mode", None),
        continuity_mode=getattr(settings, "continuity_mode", None),
        risk_appetite=getattr(settings, "risk_appetite", None),
        default_persona=getattr(settings, "default_persona", None),
        governance_banner=getattr(settings, "governance_banner", None),
    )

@router.put("/", response_model=SettingsResponse)
async def update_settings(settings_update: SettingsUpdate):
    """Update settings."""
    with db_session() as db:
        current_settings = load_settings(db)

        update_dict = settings_update.model_dump(exclude_unset=True)

        # Merge with existing settings
        for key, value in update_dict.items():
            setattr(current_settings, key, value)

        save_settings(db, current_settings)

    return SettingsResponse(
        theme=current_settings.theme,
        default_view=current_settings.default_view,
        show_system_status=current_settings.show_system_status,
        font_scale=current_settings.font_scale,
        data_preferences=current_settings.data_preferences or {},
        change_permission_mode=getattr(current_settings, "change_permission_mode", None),
        continuity_mode=getattr(current_settings, "continuity_mode", None),
        risk_appetite=getattr(current_settings, "risk_appetite", None),
        default_persona=getattr(current_settings, "default_persona", None),
        governance_banner=getattr(current_settings, "governance_banner", None),
    )


@router.get("", response_model=SettingsResponse, include_in_schema=False)
async def get_settings_no_slash():
    return await get_settings()


@router.put("", response_model=SettingsResponse, include_in_schema=False)
async def update_settings_no_slash(settings_update: SettingsUpdate):
    return await update_settings(settings_update)
