"""
Unit tests for weather providers and caching.
"""
import asyncio
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from src.providers.base import WeatherProvider, WeatherData
from src.providers.weather.openweather import OpenWeatherMapProvider
from src.weather_cache import WeatherCache


class MockWeatherProvider(WeatherProvider):
    """Mock weather provider for testing."""

    async def get_weather(self) -> WeatherData:
        """Return mock weather data."""
        return WeatherData(
            temperature=20.5,
            condition="Sunny",
            humidity=65,
            wind_speed=12.3,
            icon="☀️",
            timestamp=datetime.now(),
            location=self.location,
        )

    async def get_forecast(self, days: int = 3) -> list[WeatherData]:
        """Return mock forecast."""
        return [
            WeatherData(
                temperature=20.0 + i,
                condition="Sunny" if i % 2 == 0 else "Cloudy",
                humidity=60 + i * 2,
                wind_speed=10.0 + i,
                icon="☀️" if i % 2 == 0 else "☁️",
                timestamp=datetime.now(),
                location=self.location,
            )
            for i in range(days)
        ]


@pytest.mark.asyncio
async def test_mock_weather_provider():
    """Test mock weather provider."""
    provider = MockWeatherProvider("fake_key", "London")
    weather = await provider.get_weather()

    assert weather is not None
    assert weather.temperature == 20.5
    assert weather.condition == "Sunny"
    assert weather.location == "London"


@pytest.mark.asyncio
async def test_mock_weather_forecast():
    """Test mock weather forecast."""
    provider = MockWeatherProvider("fake_key", "London")
    forecast = await provider.get_forecast(days=3)

    assert len(forecast) == 3
    assert all(isinstance(f, WeatherData) for f in forecast)


def test_weather_cache_init():
    """Test weather cache initialization."""
    cache = WeatherCache(db_path=":memory:")
    assert cache is not None
    assert cache.ttl_hours == 1


def test_weather_cache_store_and_retrieve():
    """Test storing and retrieving weather from cache."""
    cache = WeatherCache(db_path=":memory:")

    weather = WeatherData(
        temperature=15.5,
        condition="Rainy",
        humidity=80,
        wind_speed=25.0,
        icon="🌧️",
        timestamp=datetime.now(),
        location="London",
    )

    # Store
    assert cache.cache_weather(weather) is True

    # Retrieve
    cached = cache.get_cached_weather("London")
    assert cached is not None
    assert cached.temperature == 15.5
    assert cached.condition == "Rainy"
    assert cached.location == "London"


def test_weather_cache_expiration():
    """Test cache expiration."""
    cache = WeatherCache(db_path=":memory:", ttl_hours=0)  # Immediate expiry

    weather = WeatherData(
        temperature=20.0,
        condition="Sunny",
        humidity=70,
        wind_speed=10.0,
        icon="☀️",
        timestamp=datetime.now(),
        location="London",
    )

    cache.cache_weather(weather)

    # Should be expired immediately
    cached = cache.get_cached_weather("London")
    assert cached is None


def test_weather_cache_forecast():
    """Test caching and retrieving forecast."""
    cache = WeatherCache(db_path=":memory:")

    forecast = [
        WeatherData(
            temperature=20.0,
            condition="Sunny",
            humidity=70,
            wind_speed=10.0,
            icon="☀️",
            timestamp=datetime.now(),
            location="London",
        )
        for _ in range(3)
    ]

    # Store forecast
    assert cache.cache_forecast("London", forecast) is True

    # Retrieve forecast
    cached_forecast = cache.get_cached_forecast("London", days=3)
    assert len(cached_forecast) == 3
    assert all(isinstance(f, WeatherData) for f in cached_forecast)


def test_weather_cache_clear():
    """Test clearing cache."""
    cache = WeatherCache(db_path=":memory:")

    weather = WeatherData(
        temperature=20.0,
        condition="Sunny",
        humidity=70,
        wind_speed=10.0,
        icon="☀️",
        timestamp=datetime.now(),
        location="London",
    )

    cache.cache_weather(weather)
    assert cache.get_cached_weather("London") is not None

    cache.clear_all()
    assert cache.get_cached_weather("London") is None


@pytest.mark.asyncio
async def test_openweather_provider_mock():
    """Test OpenWeatherMap provider with mocked HTTP."""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "coord": {"lon": -0.13, "lat": 51.51},
            "weather": [{"id": 803, "main": "Clouds", "description": "broken clouds", "icon": "04d"}],
            "main": {
                "temp": 15.5,
                "feels_like": 14.9,
                "temp_min": 13.1,
                "temp_max": 17.0,
                "pressure": 1013,
                "humidity": 75
            },
            "wind": {"speed": 4.1},
            "clouds": {"all": 100},
            "dt": 1613000000,
            "name": "London"
        })
        mock_get.return_value.__aenter__.return_value = mock_response

        provider = OpenWeatherMapProvider("fake_key", location="London")
        weather = await provider.get_weather()

        assert weather is not None
        assert weather.temperature == 15.5
        assert weather.humidity == 75
        assert weather.location == "London"

        await provider.close()


@pytest.mark.asyncio
async def test_openweather_provider_error_handling():
    """Test OpenWeatherMap error handling."""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 401  # Unauthorized
        mock_get.return_value.__aenter__.return_value = mock_response

        provider = OpenWeatherMapProvider("invalid_key", location="London")
        weather = await provider.get_weather()

        assert weather is None

        await provider.close()


def test_weather_data_structure():
    """Test WeatherData dataclass."""
    weather = WeatherData(
        temperature=20.0,
        condition="Sunny",
        humidity=70,
        wind_speed=10.0,
        icon="☀️",
        timestamp=datetime.now(),
        location="London",
    )

    assert weather.temperature == 20.0
    assert weather.condition == "Sunny"
    assert weather.humidity == 70
    assert weather.wind_speed == 10.0
    assert weather.icon == "☀️"
    assert weather.location == "London"
