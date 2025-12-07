"""
Base classes and utilities for API connectors
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from config.logging_config import setup_logger

logger = setup_logger("APIConnectors")


@dataclass
class APIResponse:
    """Standardized API response"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    request_time: float = 0.0
    cached: bool = False


@dataclass
class RateLimit:
    """Rate limit information"""
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int = 10
    last_request: Optional[datetime] = None
    request_count_minute: int = 0
    request_count_hour: int = 0
    request_count_day: int = 0


class RateLimiter:
    """Rate limiting for API requests"""

    def __init__(self, rate_limit: RateLimit):
        self.rate_limit = rate_limit
        self.logger = logger

    async def wait_if_needed(self) -> bool:
        """Wait if rate limit exceeded, return True if should proceed"""
        now = datetime.now()

        # Reset counters if needed
        if self.rate_limit.last_request:
            time_diff = now - self.rate_limit.last_request

            if time_diff.total_seconds() >= 60:
                self.rate_limit.request_count_minute = 0
            if time_diff.total_seconds() >= 3600:
                self.rate_limit.request_count_hour = 0
            if time_diff.total_seconds() >= 86400:
                self.rate_limit.request_count_day = 0

        # Check limits
        if (self.rate_limit.request_count_minute >= self.rate_limit.requests_per_minute or
            self.rate_limit.request_count_hour >= self.rate_limit.requests_per_hour or
            self.rate_limit.request_count_day >= self.rate_limit.requests_per_day):
            return False

        # Update counters
        self.rate_limit.last_request = now
        self.rate_limit.request_count_minute += 1
        self.rate_limit.request_count_hour += 1
        self.rate_limit.request_count_day += 1

        return True


class BaseAPIConnector(ABC):
    """Base class for all API connectors"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logger(f"{self.__class__.__name__}")
        self.rate_limiter = self._setup_rate_limiter()
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.cache_ttl = config.get("cache_ttl_seconds", 300)

    @abstractmethod
    def _setup_rate_limiter(self) -> RateLimiter:
        """Setup rate limiter for this connector"""
        pass

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the API"""
        pass

    @abstractmethod
    async def test_connection(self) -> APIResponse:
        """Test API connection"""
        pass

    async def make_request(self, method: str, endpoint: str,
                          data: Optional[Dict[str, Any]] = None,
                          headers: Optional[Dict[str, str]] = None,
                          params: Optional[Dict[str, Any]] = None,
                          use_cache: bool = True) -> APIResponse:
        """Make authenticated API request with caching and rate limiting"""

        # Check cache first
        cache_key = f"{method}:{endpoint}:{json.dumps(data, sort_keys=True) if data else ''}"
        if use_cache and cache_key in self.cache:
            cached_data, cache_time = self.cache[cache_key]
            if datetime.now() - cache_time < timedelta(seconds=self.cache_ttl):
                return APIResponse(success=True, data=cached_data, cached=True)

        # Check rate limit
        if not await self.rate_limiter.wait_if_needed():
            return APIResponse(
                success=False,
                error="Rate limit exceeded",
                status_code=429
            )

        try:
            start_time = time.time()
            response = await self._make_http_request(method, endpoint, data, headers, params)
            request_time = time.time() - start_time

            response.request_time = request_time

            # Cache successful responses
            if response.success and use_cache:
                self.cache[cache_key] = (response.data, datetime.now())

            return response

        except Exception as e:
            self.logger.error(f"API request failed: {e}")
            return APIResponse(success=False, error=str(e))

    @abstractmethod
    async def _make_http_request(self, method: str, endpoint: str,
                               data: Optional[Dict[str, Any]],
                               headers: Optional[Dict[str, str]],
                               params: Optional[Dict[str, Any]]) -> APIResponse:
        """Make the actual HTTP request"""
        pass

    def clear_cache(self):
        """Clear the request cache"""
        self.cache.clear()
        self.logger.info("API cache cleared")


class IntegrationAPIGateway:
    """Central gateway for managing multiple API integrations"""

    def __init__(self, db_connection=None, scheduler=None):
        self.connectors: Dict[str, BaseAPIConnector] = {}
        self.logger = setup_logger("IntegrationAPIGateway")
        self.db_connection = db_connection
        self.scheduler = scheduler

    def register_connector(self, name: str, connector: BaseAPIConnector):
        """Register an API connector"""
        self.connectors[name] = connector
        self.logger.info(f"Registered connector: {name}")

    async def call_action(self, target: str, action: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call an action on a specific connector"""
        if target not in self.connectors:
            return {"error": f"Unknown connector: {target}"}

        connector = self.connectors[target]

        try:
            # Map actions to methods
            action_map = {
                "status": connector.test_connection,
                "authenticate": connector.authenticate,
                "clear_cache": lambda: connector.clear_cache()
            }

            if action in action_map:
                if asyncio.iscoroutinefunction(action_map[action]):
                    result = await action_map[action]()
                else:
                    result = action_map[action]()

                return {
                    "connector": target,
                    "action": action,
                    "result": result.__dict__ if hasattr(result, '__dict__') else result
                }
            else:
                return {"error": f"Unknown action: {action}"}

        except Exception as e:
            self.logger.error(f"Action failed: {target}.{action} - {e}")
            return {"error": str(e)}

    def list_connectors(self) -> List[str]:
        """List all registered connectors"""
        return list(self.connectors.keys())

    def get_connector_status(self, name: str) -> Dict[str, Any]:
        """Get status of a specific connector"""
        if name not in self.connectors:
            return {"error": f"Connector not found: {name}"}

        connector = self.connectors[name]
        return {
            "name": name,
            "type": connector.__class__.__name__,
            "authenticated": getattr(connector, '_authenticated', False),
            "cache_size": len(connector.cache)
        }
