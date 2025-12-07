"""Utilities for previewing external data sources in the GUI."""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

MS_GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


class IntegrationPreviewError(Exception):
    """Raised when a preview request cannot be fulfilled."""


def _ensure_module(module_name: str):
    """Load a module only when it is installed.

    We avoid try/except around imports by checking availability before
    importing. This keeps optional dependencies from raising at import
    time while still giving clear feedback to the caller.
    """

    if importlib.util.find_spec(module_name) is None:
        raise IntegrationPreviewError(
            f"The '{module_name}' package is required for this preview."
        )
    return importlib.import_module(module_name)


def preview_excel_data(file_path: str, sheet_name: str = "Sheet1") -> str:
    """Read up to five rows from an Excel sheet."""

    if not file_path:
        raise IntegrationPreviewError("Please choose an Excel workbook to preview.")
    if not Path(file_path).exists():
        raise IntegrationPreviewError(f"Excel file not found at {file_path}")

    openpyxl = _ensure_module("openpyxl")
    workbook = openpyxl.load_workbook(file_path, data_only=True)
    if sheet_name not in workbook.sheetnames:
        raise IntegrationPreviewError(f"Sheet '{sheet_name}' not found in workbook.")

    sheet = workbook[sheet_name]
    rows = []
    for i, row in enumerate(sheet.iter_rows(values_only=True)):
        if i >= 5:
            break
        rows.append([cell for cell in row])

    return json.dumps({
        "file": file_path,
        "sheet": sheet_name,
        "rows": rows,
    }, indent=2)


def preview_word_document(file_path: str) -> str:
    """Summarize a Word document with paragraph counts and a snippet."""

    if not file_path:
        raise IntegrationPreviewError("Please choose a Word document to preview.")
    if not Path(file_path).exists():
        raise IntegrationPreviewError(f"Word file not found at {file_path}")

    docx = _ensure_module("docx")
    document = docx.Document(file_path)
    if not document.paragraphs:
        return json.dumps({"file": file_path, "paragraphs": 0, "snippet": ""}, indent=2)

    snippet = document.paragraphs[0].text[:200]
    return json.dumps({
        "file": file_path,
        "paragraphs": len(document.paragraphs),
        "snippet": snippet,
    }, indent=2)


def preview_onenote_notebooks(access_token: Optional[str] = None) -> str:
    """List OneNote notebooks using Microsoft Graph if a token is provided."""

    token = access_token or os.getenv("ONENOTE_ACCESS_TOKEN")
    if not token:
        raise IntegrationPreviewError(
            "Set ONENOTE_ACCESS_TOKEN or provide an access token to preview OneNote notebooks."
        )

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    endpoint = f"{MS_GRAPH_BASE_URL}/me/onenote/notebooks"
    response = requests.get(endpoint, headers=headers, timeout=10)
    response.raise_for_status()

    notebooks = [
        {"name": notebook.get("displayName"), "id": notebook.get("id")}
        for notebook in response.json().get("value", [])
    ]
    return json.dumps({"notebooks": notebooks}, indent=2)


def preview_unread_gmail(access_token: Optional[str] = None) -> str:
    """Describe how to fetch unread Gmail messages.

    The full OAuth flow is handled elsewhere in the project. This preview
    simply acknowledges whether a token is present so the GUI can surface
    a useful message without performing heavy API calls in-process.
    """

    token = access_token or os.getenv("GMAIL_TOKEN")
    if not token:
        raise IntegrationPreviewError(
            "GMAIL_TOKEN is not configured. Configure OAuth credentials to preview unread mail."
        )

    return (
        "Gmail token detected. Use the Gmail integration sync to pull the latest "
        "unread messages; the first five will be displayed in the integrations API output."
    )


def preview_ical_events(file_path: str) -> str:
    """Read upcoming events from an iCalendar (.ics) export."""

    if not file_path:
        raise IntegrationPreviewError("Please choose an iCalendar (.ics) file to preview.")
    if not Path(file_path).exists():
        raise IntegrationPreviewError(f"iCalendar file not found at {file_path}")

    icalendar = _ensure_module("icalendar")

    with open(file_path, "rb") as f:
        cal = icalendar.Calendar.from_ical(f.read())

    now = datetime.now()
    events = []
    for component in cal.walk("vevent"):
        dtstart_raw = component.get("dtstart")
        if not dtstart_raw:
            continue
        dtstart = dtstart_raw.dt
        if isinstance(dtstart, datetime) and dtstart >= now:
            events.append({
                "summary": str(component.get("summary")),
                "start": dtstart.isoformat(),
            })
            if len(events) >= 5:
                break

    return json.dumps({"file": file_path, "upcoming_events": events}, indent=2)


def preview_adobe_assets(access_token: Optional[str] = None, api_key: Optional[str] = None) -> str:
    """Provide a lightweight description for Adobe Creative Cloud previews."""

    token = access_token or os.getenv("ADOBE_ACCESS_TOKEN")
    client_id = api_key or os.getenv("ADOBE_CLIENT_ID")
    if not token or not client_id:
        raise IntegrationPreviewError(
            "Adobe API credentials are missing. Set ADOBE_ACCESS_TOKEN and ADOBE_CLIENT_ID to preview assets."
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "x-api-key": client_id,
    }
    response = requests.get(
        "https://cc-api-storage.adobe.io/api/v2/assets",
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    assets = response.json().get("_embedded", {}).get("entries", [])
    preview = [
        {"name": asset.get("name"), "type": asset.get("type"), "id": asset.get("_id")}
        for asset in assets[:5]
    ]
    return json.dumps({"assets": preview}, indent=2)


def preview_for_integration(slug: str, file_path: Optional[str] = None) -> str:
    """Route preview requests based on integration slug."""

    slug = slug.lower()
    if slug == "excel":
        return preview_excel_data(file_path or "", "Sheet1")
    if slug == "word":
        return preview_word_document(file_path or "")
    if slug == "calendar":
        return preview_ical_events(file_path or "")
    if slug == "onenote":
        return preview_onenote_notebooks()
    if slug == "mail":
        return preview_unread_gmail()
    if slug == "adobe":
        return preview_adobe_assets()

    raise IntegrationPreviewError(f"No preview available for integration '{slug}'.")
