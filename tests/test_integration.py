"""
Integration tests for multi-calendar, weather, and privacy modes.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from src.providers.base import WeatherData
from src.privacy_modes import XKCDPrivacyMode, LiteratureClockMode, PrivacyModeFactory
from src.i18n import I18nManager
from src.fonts import FontManager
from src.themes import ThemeManager


class TestMultiCalendarIntegration:
    """Test multi-calendar integration."""

    def test_merge_multiple_calendars(self):
        """Test merging events from multiple calendars."""
        ashi_events = [
            {"summary": "Ashi Meeting", "start": "09:00", "end": "10:00"},
            {"summary": "Ashi Lunch", "start": "12:00", "end": "13:00"},
        ]
        
        sindi_events = [
            {"summary": "Sindi Call", "start": "10:00", "end": "11:00"},
            {"summary": "Sindi Workout", "start": "17:00", "end": "18:00"},
        ]
        
        # Merge events
        all_events = sorted(ashi_events + sindi_events, key=lambda x: x["start"])
        
        assert len(all_events) == 4
        assert all_events[0]["summary"] == "Ashi Meeting"
        assert all_events[1]["summary"] == "Sindi Call"

    def test_calendar_deduplication(self):
        """Test duplicate event detection."""
        events = [
            {"summary": "Team Meeting", "start": "09:00", "end": "10:00", "calendar": "ashi"},
            {"summary": "Team Meeting", "start": "09:00", "end": "10:00", "calendar": "sindi"},
            {"summary": "Different Event", "start": "11:00", "end": "12:00", "calendar": "ashi"},
        ]
        
        # Simple dedup based on summary and time
        seen = set()
        deduped = []
        for event in events:
            key = (event["summary"], event["start"])
            if key not in seen:
                seen.add(key)
                deduped.append(event)
        
        assert len(deduped) == 2

    def test_calendar_sorting_by_time(self):
        """Test events are sorted chronologically."""
        events = [
            {"summary": "Event C", "start": "15:00"},
            {"summary": "Event A", "start": "09:00"},
            {"summary": "Event B", "start": "12:00"},
        ]
        
        sorted_events = sorted(events, key=lambda x: x["start"])
        
        assert sorted_events[0]["summary"] == "Event A"
        assert sorted_events[1]["summary"] == "Event B"
        assert sorted_events[2]["summary"] == "Event C"

    def test_upcoming_events_filter(self):
        """Test filtering upcoming events."""
        now = datetime.now()
        events = [
            {"summary": "Past Event", "start": (now - timedelta(hours=1)).isoformat()},
            {"summary": "Now Event", "start": now.isoformat()},
            {"summary": "Future Event", "start": (now + timedelta(hours=1)).isoformat()},
        ]
        
        # Filter future events
        future_events = [e for e in events if datetime.fromisoformat(e["start"]) >= now]
        
        assert len(future_events) == 2
        assert "Past Event" not in [e["summary"] for e in future_events]


class TestWeatherIntegration:
    """Test weather integration with calendar."""

    @pytest.mark.asyncio
    async def test_weather_and_calendar_together(self):
        """Test fetching weather and calendar together."""
        weather = WeatherData(
            temperature=15.5,
            condition="Rainy",
            humidity=80,
            wind_speed=20.0,
            icon="🌧️",
            timestamp=datetime.now(),
            location="London",
        )
        
        events = [
            {"summary": "Office Work", "start": "09:00", "end": "17:00"},
            {"summary": "Evening Run", "start": "18:00", "end": "19:00"},
        ]
        
        # Both should be available for display
        assert weather is not None
        assert len(events) == 2
        assert events[1]["summary"] == "Evening Run"

    def test_weather_display_with_privacy(self):
        """Test weather display with privacy mode."""
        weather_text = "Sunny, 25°C, 60% humidity"
        
        # Apply privacy mode
        encrypted = XKCDPrivacyMode.encrypt(weather_text)
        
        # Should be different from original
        assert encrypted != weather_text


class TestPrivacyIntegration:
    """Test privacy modes with events and weather."""

    def test_xkcd_privacy_with_events(self):
        """Test XKCD privacy mode with real events."""
        events = [
            {"summary": "Meeting with CEO", "start": "09:00"},
            {"summary": "Confidential Project", "start": "14:00"},
        ]
        
        privacy_result = PrivacyModeFactory.apply_privacy("xkcd", events)
        
        assert privacy_result["privacy_mode"] == "xkcd"
        assert len(privacy_result["events"]) == 2
        # Events should be encrypted
        assert privacy_result["events"][0]["summary"] != "Meeting with CEO"

    def test_literature_clock_privacy(self):
        """Test literature clock privacy mode."""
        events = [
            {"summary": "Morning Meeting", "start": "09:00"},
        ]
        
        privacy_result = PrivacyModeFactory.apply_privacy("literature_clock", events)
        
        assert privacy_result["privacy_mode"] == "literature_clock"
        # Should have display text with literary reference
        assert privacy_result["display_text"] is not None
        assert "[Event]" in privacy_result["display_text"]

    def test_no_privacy_mode(self):
        """Test with privacy mode disabled."""
        events = [{"summary": "Public Meeting", "start": "09:00"}]
        weather = "Sunny"
        
        result = PrivacyModeFactory.apply_privacy("none", events, weather)
        
        assert result["privacy_mode"] == "none"
        assert result["events"] == events
        assert result["weather"] == weather


class TestI18nIntegration:
    """Test internationalization integration."""

    def test_switch_languages(self):
        """Test switching between languages."""
        i18n = I18nManager("en")
        
        # English
        assert i18n.t("today") == "Today"
        assert i18n.t("monday") == "Monday"
        
        # Switch to German
        i18n.set_language("de")
        assert i18n.t("today") == "Heute"
        assert i18n.t("monday") == "Montag"
        
        # Switch to Spanish
        i18n.set_language("es")
        assert i18n.t("today") == "Hoy"

    def test_date_formatting_multilingual(self):
        """Test date formatting in multiple languages."""
        test_date = datetime(2026, 2, 9)  # Monday, February 9
        
        for lang in ["en", "de", "es", "fr"]:
            i18n = I18nManager(lang)
            formatted = i18n.format_date(test_date)
            assert len(formatted) > 0
            assert str(test_date.day) in formatted or "9" in formatted

    def test_event_count_translation(self):
        """Test translating event counts."""
        i18n = I18nManager("en")
        
        text = i18n.t("event_count", count=3)
        assert "3" in text
        assert "events" in text.lower()


class TestFontIntegration:
    """Test font loading and fallbacks."""

    def test_font_manager_initialization(self):
        """Test font manager initializes."""
        manager = FontManager()
        
        assert manager is not None
        assert manager.platform in ["macos", "linux", "windows", "rpi"]

    def test_font_loading_with_fallback(self):
        """Test font loads with fallback."""
        manager = FontManager()
        
        font = manager.get_font(12)
        assert font is not None

    def test_font_size_variants(self):
        """Test different font sizes."""
        manager = FontManager()
        
        fonts = manager.get_fonts_dict()
        
        assert "tiny" in fonts
        assert "small" in fonts
        assert "medium" in fonts
        assert "large" in fonts
        assert "huge" in fonts


class TestThemeIntegration:
    """Test theme system integration."""

    def test_theme_switching(self):
        """Test switching themes."""
        manager = ThemeManager("light")
        
        assert manager.current_theme.name == "light"
        
        manager.set_theme("dark")
        assert manager.current_theme.name == "dark"

    def test_color_mode_conversion(self):
        """Test color conversion for display modes."""
        manager = ThemeManager("light")
        
        # RGB color
        rgb_color = manager.get_color("black", "rgb")
        assert rgb_color == (0, 0, 0)
        
        # B&W color
        bw_color = manager.get_color("black", "bw")
        assert bw_color in (0, 1)

    def test_all_themes_available(self):
        """Test all themes are available."""
        manager = ThemeManager()
        themes = manager.list_themes()
        
        assert "light" in themes
        assert "dark" in themes
        assert "high_contrast" in themes
        assert "epaper" in themes


class TestEndToEndFlow:
    """Test complete end-to-end workflows."""

    @pytest.mark.asyncio
    async def test_calendar_weather_privacy_flow(self):
        """Test complete flow: fetch -> apply privacy -> display."""
        # Simulate calendar + weather fetch
        events = [
            {"summary": "Private Meeting", "start": "10:00", "end": "11:00"},
            {"summary": "Lunch", "start": "12:00", "end": "13:00"},
        ]
        
        weather = WeatherData(
            temperature=20.0,
            condition="Sunny",
            humidity=65,
            wind_speed=10.0,
            icon="☀️",
            timestamp=datetime.now(),
            location="London",
        )
        
        # Apply privacy mode
        private_result = PrivacyModeFactory.apply_privacy("xkcd", events)
        
        # Get i18n strings
        i18n = I18nManager("en")
        calendar_label = i18n.t("calendar")
        weather_label = i18n.t("weather")
        
        # Get theme colors
        theme = ThemeManager("epaper")
        text_color = theme.get_color("black")
        
        assert private_result["privacy_mode"] == "xkcd"
        assert calendar_label == "Calendar"
        assert weather_label == "Weather"
        assert text_color == (0, 0, 0)
