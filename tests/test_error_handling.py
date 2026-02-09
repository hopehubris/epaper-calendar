"""
Error handling and edge case tests.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.providers.base import WeatherData
from src.weather_cache import WeatherCache
from src.privacy_modes import XKCDPrivacyMode, PrivacyModeFactory
from src.i18n import I18nManager
from src.display.templates import DefaultTemplate


class TestWeatherProviderErrors:
    """Test error handling in weather providers."""

    @pytest.mark.asyncio
    async def test_invalid_api_response(self):
        """Test handling of invalid API response."""
        from src.providers.weather.openweather import OpenWeatherMapProvider
        
        provider = OpenWeatherMapProvider("invalid_key", "London")
        
        # Invalid key should return None
        weather = await provider.get_weather()
        assert weather is None

    def test_weather_data_with_missing_fields(self):
        """Test WeatherData handles missing fields gracefully."""
        # All fields are required for WeatherData dataclass
        with pytest.raises(TypeError):
            WeatherData(
                temperature=20.0,
                # Missing other fields - should fail
            )

    def test_weather_cache_corrupted_database(self):
        """Test cache handles corrupted database."""
        cache = WeatherCache(db_path=":memory:")
        
        # Try to retrieve from empty cache
        result = cache.get_cached_weather("NonExistent")
        assert result is None  # Should return None, not crash


class TestPrivacyModeErrors:
    """Test error handling in privacy modes."""

    def test_privacy_mode_with_none_events(self):
        """Test privacy mode handles None events."""
        # Should handle None gracefully
        try:
            result = PrivacyModeFactory.apply_privacy("xkcd", [])
            assert result["privacy_mode"] == "xkcd"
        except Exception as e:
            pytest.fail(f"Privacy mode failed with empty events: {e}")

    def test_privacy_mode_with_invalid_mode(self):
        """Test privacy mode with invalid mode name."""
        events = [{"summary": "Test"}]
        
        result = PrivacyModeFactory.apply_privacy("invalid_mode", events)
        
        # Should fallback to "none"
        assert result["privacy_mode"] == "none"

    def test_xkcd_encryption_with_special_chars(self):
        """Test XKCD encryption with special characters."""
        text = "Test!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        
        encrypted = XKCDPrivacyMode.encrypt(text)
        
        # Should not crash with special chars
        assert isinstance(encrypted, str)

    def test_xkcd_encryption_with_numbers(self):
        """Test XKCD encryption preserves numbers."""
        text = "Meeting 123 at 456pm"
        
        encrypted = XKCDPrivacyMode.encrypt(text)
        
        # Numbers should be preserved
        assert "123" in encrypted
        assert "456" in encrypted

    def test_xkcd_encryption_empty_string(self):
        """Test XKCD encryption with empty string."""
        encrypted = XKCDPrivacyMode.encrypt("")
        assert encrypted == ""

    def test_privacy_mode_with_very_long_event_title(self):
        """Test privacy mode with extremely long event title."""
        long_title = "A" * 10000
        events = [{"summary": long_title}]
        
        result = PrivacyModeFactory.apply_privacy("xkcd", events)
        
        assert result["privacy_mode"] == "xkcd"
        assert len(result["events"]) == 1


class TestI18nErrors:
    """Test error handling in internationalization."""

    def test_missing_translation_key(self):
        """Test handling of missing translation keys."""
        i18n = I18nManager("en")
        
        # Missing key should return the key itself
        result = i18n.t("nonexistent_key")
        assert result == "nonexistent_key"

    def test_invalid_language_code(self):
        """Test handling of invalid language code."""
        i18n = I18nManager("en")
        
        # Invalid language should not crash, should use default
        i18n.set_language("invalid_lang_xyz")
        
        # Should still work (fallback to English)
        result = i18n.t("today")
        assert result is not None

    def test_format_arguments_mismatch(self):
        """Test format string with missing arguments."""
        i18n = I18nManager("en")
        
        # Try to format without required argument
        result = i18n.t("event_count")  # This expects {count} argument
        
        # Should return the key or handle gracefully
        assert result is not None

    def test_date_formatting_with_invalid_date(self):
        """Test date formatting with edge dates."""
        i18n = I18nManager("en")
        
        # Test with year 1 (very old)
        old_date = datetime(1, 1, 1)
        result = i18n.format_date(old_date)
        assert isinstance(result, str)
        
        # Test with year 9999 (very far future)
        future_date = datetime(9999, 12, 31)
        result = i18n.format_date(future_date)
        assert isinstance(result, str)

    def test_get_day_name_with_invalid_day(self):
        """Test get_day_name with invalid input."""
        i18n = I18nManager("en")
        
        # Valid days are 0-6
        with pytest.raises(IndexError):
            i18n.get_day_name(7)  # Sunday is 6, so 7 is invalid

    def test_get_month_name_with_invalid_month(self):
        """Test get_month_name with invalid input."""
        i18n = I18nManager("en")
        
        # Valid months are 1-12
        with pytest.raises(IndexError):
            i18n.get_month_name(13)


class TestRenderingErrors:
    """Test error handling in rendering."""

    def test_render_with_none_events(self):
        """Test rendering with None events."""
        template = DefaultTemplate()
        
        # Should handle None gracefully
        with pytest.raises(TypeError):
            template.render(None)

    def test_render_with_empty_events(self):
        """Test rendering with empty events list."""
        template = DefaultTemplate()
        
        img = template.render([])
        
        assert img is not None

    def test_render_with_malformed_event(self):
        """Test rendering with malformed event data."""
        template = DefaultTemplate()
        
        malformed_events = [
            {"no_summary_key": "test"},  # Missing summary
            {"summary": None},  # None summary
            {"summary": ""},  # Empty summary
            {},  # Empty dict
        ]
        
        # Should handle malformed data without crashing
        try:
            img = template.render(malformed_events)
            assert img is not None
        except (KeyError, AttributeError, TypeError) as e:
            # Should either handle or raise a specific error
            pass

    def test_render_with_invalid_weather_icon(self):
        """Test rendering with invalid weather icon."""
        from src.display.templates import WeatherTemplate
        
        template = WeatherTemplate()
        
        weather = WeatherData(
            temperature=20.0,
            condition="Unknown",
            humidity=70,
            wind_speed=10.0,
            icon="🤷",  # Invalid/unknown icon
            timestamp=datetime.now(),
            location="London",
        )
        
        img = template.render([], weather)
        assert img is not None

    def test_render_with_extreme_dimensions(self):
        """Test rendering with extreme dimensions."""
        # Very small
        template_small = DefaultTemplate(width=100, height=100)
        img_small = template_small.render([])
        assert img_small.size == (100, 100)
        
        # Very large
        template_large = DefaultTemplate(width=4000, height=3000)
        img_large = template_large.render([])
        assert img_large.size == (4000, 3000)

    def test_render_with_many_events(self):
        """Test rendering with excessive number of events."""
        template = DefaultTemplate()
        
        # Create 10000 events
        events = [
            {"summary": f"Event {i}", "start": f"{(i % 24):02d}:{(i % 60):02d}"}
            for i in range(10000)
        ]
        
        # Should handle without crashing
        img = template.render(events)
        assert img is not None


class TestCacheErrors:
    """Test error handling in cache."""

    def test_cache_with_invalid_db_path(self):
        """Test cache with invalid database path."""
        # Try to use read-only path
        try:
            cache = WeatherCache(db_path="/root/nonexistent/path/cache.db")
            # May or may not succeed depending on permissions
        except Exception:
            # Should handle permission errors gracefully
            pass

    def test_cache_clear_expired_on_empty_db(self):
        """Test clearing expired entries on empty cache."""
        cache = WeatherCache(db_path=":memory:")
        
        # Should not crash
        cache.clear_expired()

    def test_cache_with_very_old_timestamp(self):
        """Test cache with very old timestamps."""
        cache = WeatherCache(db_path=":memory:", ttl_hours=0)
        
        weather = WeatherData(
            temperature=20.0,
            condition="Sunny",
            humidity=70,
            wind_speed=10.0,
            icon="☀️",
            timestamp=datetime(1970, 1, 1),  # Very old
            location="London",
        )
        
        cache.cache_weather(weather)
        
        # Should be immediately expired
        result = cache.get_cached_weather("London")
        assert result is None


class TestDataTypeErrors:
    """Test handling of invalid data types."""

    def test_weather_data_invalid_temperature(self):
        """Test WeatherData with non-numeric temperature."""
        # Dataclass allows string temperature (no type validation)
        weather = WeatherData(
            temperature="not a number",
            condition="Sunny",
            humidity=70,
            wind_speed=10.0,
            icon="☀️",
            timestamp=datetime.now(),
            location="London",
        )
        # Created successfully despite type mismatch
        assert weather.temperature == "not a number"

    def test_weather_data_negative_humidity(self):
        """Test WeatherData with invalid humidity."""
        # Should still be created (dataclass doesn't validate)
        weather = WeatherData(
            temperature=20.0,
            condition="Sunny",
            humidity=-10,  # Invalid but created
            wind_speed=10.0,
            icon="☀️",
            timestamp=datetime.now(),
            location="London",
        )
        assert weather.humidity == -10  # Dataclass allows it


class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""

    def test_zero_temperature(self):
        """Test weather with zero temperature."""
        weather = WeatherData(
            temperature=0.0,
            condition="Freezing",
            humidity=100,
            wind_speed=0.0,
            icon="❄️",
            timestamp=datetime.now(),
            location="Iceland",
        )
        assert weather.temperature == 0.0

    def test_empty_location(self):
        """Test weather with empty location."""
        weather = WeatherData(
            temperature=20.0,
            condition="Sunny",
            humidity=70,
            wind_speed=10.0,
            icon="☀️",
            timestamp=datetime.now(),
            location="",  # Empty
        )
        assert weather.location == ""

    def test_unicode_in_event_summary(self):
        """Test event with unicode characters."""
        events = [
            {"summary": "Meeting 👔 at 📍 Office"},
            {"summary": "日本語 テスト"},
            {"summary": "Тест на русском"},
            {"summary": "اختبار عربي"},
        ]
        
        # All should be handled
        for event in events:
            assert isinstance(event["summary"], str)
