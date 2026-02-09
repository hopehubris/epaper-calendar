"""
Performance benchmarking and optimization tests.
"""
import pytest
import time
from datetime import datetime
import asyncio

from src.providers.base import WeatherData
from src.weather_cache import WeatherCache
from src.privacy_modes import XKCDPrivacyMode, LiteratureClockMode
from src.i18n import I18nManager
from src.fonts import FontManager
from src.display.templates import DefaultTemplate, WeatherTemplate


class TestCachePerformance:
    """Performance tests for weather cache."""

    def test_cache_write_performance(self):
        """Test cache write speed."""
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
        
        start = time.time()
        for _ in range(100):
            cache.cache_weather(weather)
        elapsed = time.time() - start
        
        # Should complete 100 writes in <100ms
        assert elapsed < 0.1, f"Cache writes too slow: {elapsed}s for 100 ops"

    def test_cache_read_performance(self):
        """Test cache read speed."""
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
        
        start = time.time()
        for _ in range(100):
            cache.get_cached_weather("London")
        elapsed = time.time() - start
        
        # Should complete 100 reads in <100ms
        assert elapsed < 0.1, f"Cache reads too slow: {elapsed}s for 100 ops"

    def test_forecast_cache_performance(self):
        """Test forecast caching performance."""
        cache = WeatherCache(db_path=":memory:")
        
        forecast = [
            WeatherData(
                temperature=20.0 + i,
                condition="Sunny",
                humidity=70,
                wind_speed=10.0,
                icon="☀️",
                timestamp=datetime.now(),
                location="London",
            )
            for i in range(40)  # 5 days of forecasts
        ]
        
        start = time.time()
        cache.cache_forecast("London", forecast)
        elapsed = time.time() - start
        
        assert elapsed < 0.05, f"Forecast caching too slow: {elapsed}s"


class TestPrivacyModePerformance:
    """Performance tests for privacy modes."""

    def test_xkcd_encryption_speed(self):
        """Test XKCD encryption performance."""
        text = "This is a confidential message " * 10
        
        start = time.time()
        for _ in range(100):
            XKCDPrivacyMode.encrypt(text)
        elapsed = time.time() - start
        
        # Should handle 100 encryptions in <50ms
        assert elapsed < 0.05, f"Encryption too slow: {elapsed}s for 100 ops"

    def test_privacy_mode_event_processing(self):
        """Test privacy mode event processing."""
        events = [
            {"summary": f"Event {i}", "start": f"{9+i}:00"}
            for i in range(50)
        ]
        
        start = time.time()
        XKCDPrivacyMode.obscure_events(events)
        elapsed = time.time() - start
        
        assert elapsed < 0.1, f"Event obscuring too slow: {elapsed}s for 50 events"

    def test_literature_clock_generation(self):
        """Test literature clock text generation."""
        events = [
            {"summary": f"Event {i}", "start": f"{9+i}:00"}
            for i in range(10)
        ]
        
        start = time.time()
        for _ in range(100):
            LiteratureClockMode.create_display_text(events)
        elapsed = time.time() - start
        
        assert elapsed < 0.1, f"Literature clock too slow: {elapsed}s for 100 ops"


class TestI18nPerformance:
    """Performance tests for internationalization."""

    def test_translation_lookup_speed(self):
        """Test translation lookup speed."""
        i18n = I18nManager("en")
        
        start = time.time()
        for _ in range(1000):
            i18n.t("today")
            i18n.t("monday")
            i18n.t("calendar")
        elapsed = time.time() - start
        
        # Should complete 3000 lookups in <10ms
        assert elapsed < 0.01, f"Translations too slow: {elapsed}s for 3000 lookups"

    def test_language_switching_speed(self):
        """Test language switching."""
        i18n = I18nManager("en")
        languages = ["en", "de", "es", "fr"]
        
        start = time.time()
        for _ in range(100):
            for lang in languages:
                i18n.set_language(lang)
        elapsed = time.time() - start
        
        assert elapsed < 0.05, f"Language switching too slow: {elapsed}s for 400 ops"

    def test_date_formatting_speed(self):
        """Test date formatting performance."""
        i18n = I18nManager("en")
        date = datetime.now()
        
        start = time.time()
        for _ in range(1000):
            i18n.format_date(date)
        elapsed = time.time() - start
        
        assert elapsed < 0.1, f"Date formatting too slow: {elapsed}s for 1000 ops"


class TestFontPerformance:
    """Performance tests for font loading."""

    def test_font_caching(self):
        """Test font caching works."""
        manager = FontManager()
        
        # First load
        start = time.time()
        font1 = manager.get_font(12)
        first_load = time.time() - start
        
        # Second load (should be cached)
        start = time.time()
        font2 = manager.get_font(12)
        cached_load = time.time() - start
        
        # Cached should be much faster
        assert font1 is font2  # Same object
        assert cached_load < first_load

    def test_font_dict_generation(self):
        """Test font dict generation performance."""
        manager = FontManager()
        
        start = time.time()
        for _ in range(100):
            manager.get_fonts_dict()
        elapsed = time.time() - start
        
        assert elapsed < 0.5, f"Font dict generation too slow: {elapsed}s for 100 ops"


class TestRenderingPerformance:
    """Performance tests for rendering."""

    def test_default_template_rendering_speed(self):
        """Test default template rendering speed."""
        template = DefaultTemplate(width=800, height=480)
        
        events = [
            {"summary": f"Event {i}", "start": f"{9 + i//4}:00"}
            for i in range(20)
        ]
        
        start = time.time()
        for _ in range(10):
            template.render(events)
        elapsed = time.time() - start
        
        # Should render 10 images in <1 second
        assert elapsed < 1.0, f"Rendering too slow: {elapsed}s for 10 renders"

    def test_weather_template_rendering_speed(self):
        """Test weather template rendering speed."""
        template = WeatherTemplate(width=800, height=480)
        
        weather = WeatherData(
            temperature=20.0,
            condition="Sunny",
            humidity=65,
            wind_speed=10.0,
            icon="☀️",
            timestamp=datetime.now(),
            location="London",
        )
        
        events = [
            {"summary": f"Event {i}", "start": f"{9+i}:00"}
            for i in range(5)
        ]
        
        start = time.time()
        for _ in range(10):
            template.render(events, weather)
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Weather template too slow: {elapsed}s for 10 renders"

    def test_large_event_set_rendering(self):
        """Test rendering with many events."""
        template = DefaultTemplate()
        
        events = [
            {"summary": f"Event {i}", "start": f"{(i // 30):02d}:{(i % 30) * 2:02d}"}
            for i in range(100)
        ]
        
        start = time.time()
        template.render(events)
        elapsed = time.time() - start
        
        # Should handle 100 events reasonably
        assert elapsed < 2.0, f"Large event rendering too slow: {elapsed}s"


class TestMemoryUsage:
    """Memory usage tests."""

    def test_cache_memory_efficiency(self):
        """Test cache doesn't grow unbounded."""
        cache = WeatherCache(db_path=":memory:")
        
        # Add many weather entries
        for i in range(100):
            weather = WeatherData(
                temperature=20.0,
                condition="Sunny",
                humidity=70,
                wind_speed=10.0,
                icon="☀️",
                timestamp=datetime.now(),
                location=f"Location_{i}",
            )
            cache.cache_weather(weather)
        
        # Cache should be manageable (SQLite handles memory well)
        # This is a basic test to ensure no obvious memory leaks
        assert cache.get_cached_weather("Location_50") is not None

    def test_font_manager_memory(self):
        """Test font manager memory usage."""
        manager = FontManager()
        
        # Load many font sizes
        for size in range(8, 32):
            manager.get_font(size)
        
        # Should still work and be cached
        assert len(manager.fonts) > 0


class TestConcurrencyPerformance:
    """Concurrency and parallel operation tests."""

    @pytest.mark.asyncio
    async def test_concurrent_cache_access(self):
        """Test concurrent cache access."""
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
        
        # Simulate concurrent reads
        async def read_cache():
            return cache.get_cached_weather("London")
        
        start = time.time()
        tasks = [read_cache() for _ in range(100)]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start
        
        assert all(r is not None for r in results)
        assert elapsed < 0.5, f"Concurrent cache too slow: {elapsed}s for 100 reads"


class TestOptimizationCheckpoints:
    """Quick performance checkpoints for optimization."""

    def test_performance_baseline(self):
        """Establish baseline performance."""
        metrics = {}
        
        # Cache performance
        cache = WeatherCache(db_path=":memory:")
        weather = WeatherData(
            temperature=20.0, condition="Sunny", humidity=70,
            wind_speed=10.0, icon="☀️", timestamp=datetime.now(),
            location="London"
        )
        
        start = time.time()
        cache.cache_weather(weather)
        metrics["cache_write"] = time.time() - start
        
        # Translation performance
        i18n = I18nManager("en")
        start = time.time()
        i18n.t("today")
        metrics["translation"] = time.time() - start
        
        # Rendering performance
        template = DefaultTemplate()
        start = time.time()
        template.render([{"summary": "Test", "start": "10:00"}])
        metrics["render"] = time.time() - start
        
        # All metrics should be reasonable
        for metric, value in metrics.items():
            assert value < 0.1, f"{metric} performance issue: {value}s"
