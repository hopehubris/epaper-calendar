"""
OpenWeatherMap weather provider implementation.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional, List

import aiohttp

from src.providers.base import WeatherProvider, WeatherData


logger = logging.getLogger(__name__)


class OpenWeatherMapProvider(WeatherProvider):
    """OpenWeatherMap API implementation."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    WEATHER_ICONS = {
        "01d": "☀️",  # clear sky day
        "01n": "🌙",  # clear sky night
        "02d": "⛅",  # few clouds day
        "02n": "☁️",  # few clouds night
        "03d": "☁️",  # scattered clouds
        "03n": "☁️",  # scattered clouds
        "04d": "☁️",  # broken clouds
        "04n": "☁️",  # broken clouds
        "09d": "🌧️",  # shower rain
        "09n": "🌧️",  # shower rain
        "10d": "🌧️",  # rain
        "10n": "🌧️",  # rain
        "11d": "⛈️",  # thunderstorm
        "11n": "⛈️",  # thunderstorm
        "13d": "❄️",  # snow
        "13n": "❄️",  # snow
        "50d": "🌫️",  # mist
        "50n": "🌫️",  # mist
    }

    def __init__(self, api_key: str, location: str = None, lat: float = None, lon: float = None):
        """
        Initialize OpenWeatherMap provider.
        
        Args:
            api_key: OpenWeatherMap API key
            location: City name (alternative to lat/lon)
            lat: Latitude coordinate
            lon: Longitude coordinate
        """
        super().__init__(api_key, location)
        self.lat = lat
        self.lon = lon
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def get_weather(self) -> Optional[WeatherData]:
        """
        Fetch current weather.
        
        Returns:
            WeatherData if successful, None on error
        """
        try:
            session = await self._get_session()
            params = {
                "appid": self.api_key,
                "units": "metric",
            }

            # Use coordinates if available, otherwise city name
            if self.lat is not None and self.lon is not None:
                params["lat"] = self.lat
                params["lon"] = self.lon
                endpoint = f"{self.BASE_URL}/weather"
            else:
                params["q"] = self.location
                endpoint = f"{self.BASE_URL}/weather"

            async with session.get(endpoint, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    logger.error(f"OpenWeatherMap API error: {resp.status}")
                    return None

                data = await resp.json()
                return self._parse_weather(data)

        except asyncio.TimeoutError:
            logger.error("OpenWeatherMap API timeout")
            return None
        except Exception as e:
            logger.error(f"OpenWeatherMap error: {e}")
            return None

    async def get_forecast(self, days: int = 3) -> List[WeatherData]:
        """
        Fetch weather forecast.
        
        Args:
            days: Number of days to forecast (max 5 for free tier)
            
        Returns:
            List of WeatherData for forecast
        """
        try:
            session = await self._get_session()
            params = {
                "appid": self.api_key,
                "units": "metric",
                "cnt": min(days * 8, 40),  # 8 forecasts per day (3-hour intervals)
            }

            if self.lat is not None and self.lon is not None:
                params["lat"] = self.lat
                params["lon"] = self.lon
            else:
                params["q"] = self.location

            endpoint = f"{self.BASE_URL}/forecast"
            
            async with session.get(endpoint, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    logger.error(f"OpenWeatherMap forecast error: {resp.status}")
                    return []

                data = await resp.json()
                forecasts = []
                
                for item in data.get("list", []):
                    forecast = self._parse_weather(item, location=data.get("city", {}).get("name", self.location))
                    if forecast:
                        forecasts.append(forecast)
                
                return forecasts

        except Exception as e:
            logger.error(f"OpenWeatherMap forecast error: {e}")
            return []

    def _parse_weather(self, data: dict, location: str = None) -> Optional[WeatherData]:
        """
        Parse OpenWeatherMap API response.
        
        Args:
            data: API response data
            location: Optional location override
            
        Returns:
            WeatherData object or None
        """
        try:
            weather_main = data.get("weather", [{}])[0]
            main = data.get("main", {})

            icon = weather_main.get("icon", "01d")
            condition = weather_main.get("main", "Unknown")

            return WeatherData(
                temperature=round(main.get("temp", 0), 1),
                condition=condition,
                humidity=main.get("humidity", 0),
                wind_speed=round(data.get("wind", {}).get("speed", 0) * 3.6, 1),  # m/s to km/h
                icon=self.WEATHER_ICONS.get(icon, "🌤️"),
                timestamp=datetime.fromtimestamp(data.get("dt", 0)),
                location=location or self.location,
            )
        except Exception as e:
            logger.error(f"Failed to parse weather data: {e}")
            return None

    async def close(self):
        """Close aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
