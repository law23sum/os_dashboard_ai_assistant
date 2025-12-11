"""
Lightweight integration manager that routes operations to connectors with
optional fallback connectors. Uses the OperationResult contract from
`universal_connector`.
"""

from __future__ import annotations

from typing import Dict, Optional

from api_connectors.universal_connector import BaseConnector, OperationResult


class IntegrationManager:
    """
    Routes operations to primary connectors and falls back when a primary
    connector fails with a recoverable error.
    """

    def __init__(self, adapters: Dict[str, BaseConnector], fallback_adapters: Optional[Dict[str, BaseConnector]] = None):
        self.adapters = adapters
        self.fallback_adapters = fallback_adapters or {}

    def primary(self, software: str) -> Optional[BaseConnector]:
        return self.adapters.get(software)

    def fallback(self, software: str) -> Optional[BaseConnector]:
        return self.fallback_adapters.get(software)

    async def execute_operation(self, software: str, operation: str, **kwargs) -> OperationResult:
        adapter = self.primary(software)
        if not adapter:
            return OperationResult(success=False, error=f"No adapter registered for {software}")

        try:
            method = getattr(adapter, operation, None)
            if not method:
                return OperationResult(success=False, error=f"Operation not supported: {operation}")
            return await method(**kwargs)
        except Exception as exc:
            fb = self.fallback(software)
            if fb:
                fb_method = getattr(fb, operation, None)
                if fb_method:
                    return await fb_method(**kwargs)
            return OperationResult(success=False, error=str(exc))



