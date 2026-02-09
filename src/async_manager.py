"""
Async manager for parallel API fetching with error handling and fallback.
"""
import asyncio
import logging
from typing import Optional, Tuple, List
from datetime import datetime

from src.calendar_fetcher import CalendarFetcher
from src.providers.base import WeatherData
from src.providers.weather.openweather import OpenWeatherMapProvider
from src.cache_manager import CacheManager


logger = logging.getLogger(__name__)


class AsyncManager:
    """Manages parallel API fetching for calendar and weather."""

    def __init__(self, config: dict, cache_manager: CacheManager):
        """
        Initialize async manager.
        
        Args:
            config: Configuration dictionary
            cache_manager: Cache manager instance
        """
        self.config = config
        self.cache = cache_manager
        self.calendar_fetcher = None
        self.weather_provider = None

    async def initialize(self) -> None:
        """Initialize calendar and weather providers."""
        try:
            # Initialize calendar fetcher
            self.calendar_fetcher = CalendarFetcher(self.config)
            logger.info("Calendar fetcher initialized")

            # Initialize weather provider if API key is configured
            if self.config.get("openweather_api_key"):
                self.weather_provider = OpenWeatherMapProvider(
                    api_key=self.config["openweather_api_key"],
                    location=self.config.get("location", "London"),
                    lat=self.config.get("latitude"),
                    lon=self.config.get("longitude"),
                )
                logger.info("Weather provider initialized")
        except Exception as e:
            logger.error(f"Failed to initialize providers: {e}")
            raise

    async def fetch_all(self) -> Tuple[Optional[List[dict]], Optional[WeatherData]]:
        """
        Fetch calendar events and weather in parallel.
        
        Returns:
            Tuple of (events list, weather data)
        """
        if not self.calendar_fetcher:
            logger.warning("Providers not initialized, cannot fetch")
            return None, None

        try:
            # Create tasks for parallel execution
            tasks = [
                self._fetch_calendar(),
                self._fetch_weather() if self.weather_provider else asyncio.sleep(0),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            events = results[0] if not isinstance(results[0], Exception) else None
            weather = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else None

            return events, weather

        except Exception as e:
            logger.error(f"Error in parallel fetch: {e}")
            return None, None

    async def _fetch_calendar(self) -> Optional[List[dict]]:
        """
        Fetch calendar events.
        
        Returns:
            List of events or None on error
        """
        try:
            logger.debug("Fetching calendar events")
            
            # Try to fetch from API
            events = await asyncio.to_thread(self.calendar_fetcher.get_events)
            
            if events:
                # Cache the events
                self.cache.cache_events(events)
                logger.info(f"Fetched {len(events)} events from API")
                return events
            else:
                logger.warning("No events returned from API, using cache")
                return self.cache.get_cached_events()

        except Exception as e:
            logger.error(f"Calendar fetch failed: {e}, using cache")
            return self.cache.get_cached_events()

    async def _fetch_weather(self) -> Optional[WeatherData]:
        """
        Fetch current weather.
        
        Returns:
            WeatherData or None on error
        """
        try:
            logger.debug("Fetching weather data")
            weather = await self.weather_provider.get_weather()
            
            if weather:
                logger.info(f"Fetched weather: {weather.condition}, {weather.temperature}°C")
                return weather
            else:
                logger.warning("Failed to fetch weather")
                return None

        except Exception as e:
            logger.error(f"Weather fetch failed: {e}")
            return None

    async def fetch_weather_forecast(self, days: int = 3) -> List[WeatherData]:
        """
        Fetch weather forecast.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            List of WeatherData
        """
        if not self.weather_provider:
            logger.warning("Weather provider not initialized")
            return []

        try:
            forecast = await self.weather_provider.get_forecast(days)
            logger.info(f"Fetched {len(forecast)} forecast items")
            return forecast
        except Exception as e:
            logger.error(f"Weather forecast fetch failed: {e}")
            return []

    async def shutdown(self) -> None:
        """Cleanup resources."""
        if self.weather_provider:
            await self.weather_provider.close()
        logger.info("Async manager shutdown complete")
