"""
Abstract base classes for weather and calendar providers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class WeatherData:
    """Standardized weather data structure."""
    temperature: float  # Celsius
    condition: str  # e.g., "Sunny", "Rainy", "Cloudy"
    humidity: int  # percentage
    wind_speed: float  # km/h
    icon: str  # weather icon code
    timestamp: datetime
    location: str


class WeatherProvider(ABC):
    """Abstract base class for weather providers."""

    def __init__(self, api_key: str, location: str):
        """
        Initialize weather provider.
        
        Args:
            api_key: API key for the weather service
            location: Location for weather data (lat,lon or city name)
        """
        self.api_key = api_key
        self.location = location

    @abstractmethod
    async def get_weather(self) -> Optional[WeatherData]:
        """
        Fetch current weather data.
        
        Returns:
            WeatherData if successful, None on error
        """
        pass

    @abstractmethod
    async def get_forecast(self, days: int = 3) -> List[WeatherData]:
        """
        Fetch weather forecast.
        
        Args:
            days: Number of days to forecast
            
        Returns:
            List of WeatherData for forecast period
        """
        pass
