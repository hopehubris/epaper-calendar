"""
Weather cache layer with TTL support.
"""
import logging
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional

from src.providers.base import WeatherData


logger = logging.getLogger(__name__)


class WeatherCache:
    """SQLite-based weather cache with TTL."""

    DEFAULT_TTL_HOURS = 1  # Weather data expires after 1 hour

    def __init__(self, db_path: str = "weather_cache.db", ttl_hours: int = DEFAULT_TTL_HOURS):
        """
        Initialize weather cache.
        
        Args:
            db_path: Path to SQLite database
            ttl_hours: Time-to-live in hours
        """
        self.db_path = db_path
        self.ttl_hours = ttl_hours
        self._connection = None
        self._init_db()

    def _get_conn(self):
        """Get or create database connection."""
        if self._connection is None or (self.db_path != ":memory:" and not self._connection):
            self._connection = sqlite3.connect(self.db_path)
            if self.db_path == ":memory:":
                # Keep connection alive for in-memory DBs
                self._connection.isolation_level = None
        return self._connection

    def _init_db(self) -> None:
        """Initialize database schema."""
        try:
            conn = self._get_conn()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weather_cache (
                    id INTEGER PRIMARY KEY,
                    location TEXT UNIQUE NOT NULL,
                    temperature REAL,
                    condition TEXT,
                    humidity INTEGER,
                    wind_speed REAL,
                    icon TEXT,
                    timestamp DATETIME,
                    cached_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weather_forecast (
                    id INTEGER PRIMARY KEY,
                    location TEXT NOT NULL,
                    forecast_date DATETIME NOT NULL,
                    temperature REAL,
                    condition TEXT,
                    humidity INTEGER,
                    wind_speed REAL,
                    icon TEXT,
                    cached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(location, forecast_date)
                )
            """)
            conn.commit()
            logger.debug(f"Weather cache database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize weather cache: {e}")
            raise

    def cache_weather(self, weather: WeatherData) -> bool:
        """
        Cache weather data.
        
        Args:
            weather: WeatherData to cache
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_conn()
            conn.execute("""
                INSERT OR REPLACE INTO weather_cache 
                (location, temperature, condition, humidity, wind_speed, icon, timestamp, cached_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                weather.location,
                weather.temperature,
                weather.condition,
                weather.humidity,
                weather.wind_speed,
                weather.icon,
                weather.timestamp,
                datetime.now(),
            ))
            conn.commit()
            logger.debug(f"Cached weather for {weather.location}")
            return True
        except Exception as e:
            logger.error(f"Failed to cache weather: {e}")
            return False

    def get_cached_weather(self, location: str) -> Optional[WeatherData]:
        """
        Get cached weather if still valid.
        
        Args:
            location: Location to retrieve weather for
            
        Returns:
            WeatherData if found and not expired, None otherwise
        """
        try:
            conn = self._get_conn()
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM weather_cache WHERE location = ?
            """, (location,))
            row = cursor.fetchone()

            if not row:
                return None

            # Check if cached data is still fresh
            cached_at = datetime.fromisoformat(row["cached_at"])
            if datetime.now() - cached_at > timedelta(hours=self.ttl_hours):
                logger.debug(f"Weather cache expired for {location}")
                return None

            logger.debug(f"Retrieved cached weather for {location}")
            return WeatherData(
                temperature=row["temperature"],
                condition=row["condition"],
                humidity=row["humidity"],
                wind_speed=row["wind_speed"],
                icon=row["icon"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                location=row["location"],
            )
        except Exception as e:
            logger.error(f"Failed to retrieve cached weather: {e}")
            return None

    def cache_forecast(self, location: str, forecast: list[WeatherData]) -> bool:
        """
        Cache weather forecast.
        
        Args:
            location: Location for forecast
            forecast: List of WeatherData for forecast
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_conn()
            # Clear old forecast data for this location
            conn.execute("DELETE FROM weather_forecast WHERE location = ?", (location,))
            
            # Insert new forecast data
            for item in forecast:
                conn.execute("""
                    INSERT OR REPLACE INTO weather_forecast 
                    (location, forecast_date, temperature, condition, humidity, wind_speed, icon, cached_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    location,
                    item.timestamp,
                    item.temperature,
                    item.condition,
                    item.humidity,
                    item.wind_speed,
                    item.icon,
                    datetime.now(),
                ))
            
            conn.commit()
            logger.debug(f"Cached {len(forecast)} forecast items for {location}")
            return True
        except Exception as e:
            logger.error(f"Failed to cache forecast: {e}")
            return False

    def get_cached_forecast(self, location: str, days: int = 3) -> list[WeatherData]:
        """
        Get cached forecast if still valid.
        
        Args:
            location: Location to retrieve forecast for
            days: Number of days to retrieve
            
        Returns:
            List of WeatherData or empty list if not found/expired
        """
        try:
            conn = self._get_conn()
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM weather_forecast 
                WHERE location = ?
                ORDER BY forecast_date ASC
                LIMIT ?
            """, (location, days * 8))
            
            rows = cursor.fetchall()
            if not rows:
                logger.debug(f"No cached forecast for {location}")
                return []

            # Check if cached data is still fresh
            if rows and rows[0]:
                cached_at = datetime.fromisoformat(rows[0]["cached_at"])
                if datetime.now() - cached_at > timedelta(hours=self.ttl_hours):
                    logger.debug(f"Weather forecast cache expired for {location}")
                    return []

            forecast = [
                WeatherData(
                    temperature=row["temperature"],
                    condition=row["condition"],
                    humidity=row["humidity"],
                    wind_speed=row["wind_speed"],
                    icon=row["icon"],
                    timestamp=datetime.fromisoformat(row["forecast_date"]),
                    location=row["location"],
                )
                for row in rows
            ]
            
            logger.debug(f"Retrieved {len(forecast)} cached forecast items for {location}")
            return forecast
        except Exception as e:
            logger.error(f"Failed to retrieve cached forecast: {e}")
            return []

    def clear_expired(self) -> None:
        """Remove expired weather data."""
        try:
            conn = self._get_conn()
            conn.execute("""
                DELETE FROM weather_cache 
                WHERE cached_at < datetime('now', '-{} hours')
            """.format(self.ttl_hours))
            conn.execute("""
                DELETE FROM weather_forecast 
                WHERE cached_at < datetime('now', '-{} hours')
            """.format(self.ttl_hours))
            conn.commit()
            logger.debug("Cleared expired weather cache")
        except Exception as e:
            logger.error(f"Failed to clear expired cache: {e}")

    def clear_all(self) -> None:
        """Clear all weather cache."""
        try:
            conn = self._get_conn()
            conn.execute("DELETE FROM weather_cache")
            conn.execute("DELETE FROM weather_forecast")
            conn.commit()
            logger.info("Cleared all weather cache")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
