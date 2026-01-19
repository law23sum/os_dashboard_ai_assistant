"""
Weather Integration Plugin for AI OS

Provides weather data integration using OpenWeatherMap API.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from assistant_core.plugin_marketplace import IntegrationPlugin

class WeatherIntegrationPlugin(IntegrationPlugin):
    """Weather integration plugin using OpenWeatherMap API."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.api_key = config.get('api_key') if config else None
        self.default_location = config.get('location', 'New York,US') if config else 'New York,US'
        self.units = config.get('units', 'metric') if config else 'metric'
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache = {}
        self.cache_expiry = {}

    async def initialize(self) -> bool:
        """Initialize the weather plugin."""
        try:
            if not self.api_key:
                self.logger.error("OpenWeatherMap API key not configured")
                return False

            self.session = aiohttp.ClientSession()
            self.logger.info("Weather integration plugin initialized")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize weather plugin: {e}")
            return False

    async def execute(self, location: str = None, data_type: str = "current") -> Dict[str, Any]:
        """Execute weather data retrieval."""
        try:
            location = location or self.default_location

            if data_type == "current":
                return await self.get_current_weather(location)
            elif data_type == "forecast":
                return await self.get_weather_forecast(location)
            else:
                return {"error": f"Unknown data type: {data_type}"}

        except Exception as e:
            self.logger.error(f"Error executing weather plugin: {e}")
            return {"error": str(e)}

    async def cleanup(self) -> bool:
        """Cleanup plugin resources."""
        try:
            if self.session:
                await self.session.close()
            self.logger.info("Weather integration plugin cleaned up")
            return True

        except Exception as e:
            self.logger.error(f"Error cleaning up weather plugin: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            "name": "Weather Integration",
            "version": "1.0.0",
            "description": "Provides weather data from OpenWeatherMap API",
            "capabilities": ["current_weather", "weather_forecast"],
            "config_required": ["api_key"],
            "author": "AI OS Team"
        }

    async def connect(self) -> bool:
        """Test connection to OpenWeatherMap API."""
        try:
            # Test with a simple API call
            test_url = f"{self.base_url}/weather?q=London&appid={self.api_key}&units={self.units}"
            async with self.session.get(test_url) as response:
                return response.status == 200

        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """Disconnect from API (no persistent connection needed)."""
        return True

    async def sync_data(self, data_type: str) -> Dict[str, Any]:
        """Sync weather data."""
        return await self.execute(self.default_location, data_type)

    async def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather for a location."""
        cache_key = f"current_{location}_{self.units}"

        # Check cache first
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]

        try:
            url = f"{self.base_url}/weather?q={location}&appid={self.api_key}&units={self.units}"

            async with self.session.get(url) as response:
                if response.status != 200:
                    return {"error": f"API error: {response.status}"}

                data = await response.json()

                # Format the response
                weather_info = {
                    "location": f"{data['name']}, {data['sys']['country']}",
                    "temperature": data['main']['temp'],
                    "feels_like": data['main']['feels_like'],
                    "humidity": data['main']['humidity'],
                    "pressure": data['main']['pressure'],
                    "weather": data['weather'][0]['description'],
                    "wind_speed": data['wind']['speed'],
                    "wind_direction": data['wind'].get('deg', 0),
                    "clouds": data['clouds']['all'],
                    "sunrise": datetime.fromtimestamp(data['sys']['sunrise']).isoformat(),
                    "sunset": datetime.fromtimestamp(data['sys']['sunset']).isoformat(),
                    "timestamp": datetime.now().isoformat(),
                    "units": self.units
                }

                # Cache the result for 10 minutes
                self._cache_result(cache_key, weather_info, 600)

                return weather_info

        except Exception as e:
            self.logger.error(f"Error getting current weather: {e}")
            return {"error": str(e)}

    async def get_weather_forecast(self, location: str) -> Dict[str, Any]:
        """Get weather forecast for a location."""
        cache_key = f"forecast_{location}_{self.units}"

        # Check cache first
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]

        try:
            url = f"{self.base_url}/forecast?q={location}&appid={self.api_key}&units={self.units}"

            async with self.session.get(url) as response:
                if response.status != 200:
                    return {"error": f"API error: {response.status}"}

                data = await response.json()

                # Process forecast data (3-hourly for 5 days)
                forecast_list = []
                for item in data['list'][:16]:  # Next 2 days (8 * 3-hour intervals)
                    forecast_list.append({
                        "timestamp": datetime.fromtimestamp(item['dt']).isoformat(),
                        "temperature": item['main']['temp'],
                        "feels_like": item['main']['feels_like'],
                        "humidity": item['main']['humidity'],
                        "weather": item['weather'][0]['description'],
                        "wind_speed": item['wind']['speed'],
                        "precipitation_probability": item.get('pop', 0) * 100
                    })

                forecast_info = {
                    "location": f"{data['city']['name']}, {data['city']['country']}",
                    "forecast": forecast_list,
                    "timestamp": datetime.now().isoformat(),
                    "units": self.units
                }

                # Cache the result for 1 hour
                self._cache_result(cache_key, forecast_info, 3600)

                return forecast_info

        except Exception as e:
            self.logger.error(f"Error getting weather forecast: {e}")
            return {"error": str(e)}

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key in self.cache_expiry:
            return datetime.now() < self.cache_expiry[cache_key]
        return False

    def _cache_result(self, cache_key: str, data: Dict[str, Any], ttl_seconds: int):
        """Cache a result with TTL."""
        self.cache[cache_key] = data
        self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=ttl_seconds)

    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        if not config.get('api_key'):
            self.logger.error("API key is required")
            return False

        # Test the API key
        return await self.connect()
