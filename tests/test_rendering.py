"""
End-to-end rendering tests for display templates.
"""
import pytest
from datetime import datetime, timedelta
from PIL import Image

from src.display.templates import DefaultTemplate, WeatherTemplate
from src.providers.base import WeatherData


class TestDefaultTemplateRendering:
    """Test default template rendering."""

    def test_template_initialization(self):
        """Test template initializes with correct dimensions."""
        template = DefaultTemplate(width=800, height=480, color_mode="red")
        
        assert template.width == 800
        assert template.height == 480
        assert template.color_mode == "red"

    def test_render_with_events(self):
        """Test rendering with events."""
        template = DefaultTemplate(width=800, height=480)
        
        events = [
            {"summary": "Meeting 1", "start": "09:00"},
            {"summary": "Meeting 2", "start": "14:00"},
        ]
        
        img = template.render(events)
        
        assert isinstance(img, Image.Image)
        assert img.size == (800, 480)

    def test_render_with_weather(self):
        """Test rendering with weather data."""
        template = DefaultTemplate(width=800, height=480)
        
        weather = WeatherData(
            temperature=20.5,
            condition="Sunny",
            humidity=65,
            wind_speed=12.0,
            icon="☀️",
            timestamp=datetime.now(),
            location="London",
        )
        
        events = [{"summary": "Outdoor Run", "start": "17:00"}]
        
        img = template.render(events, weather)
        
        assert isinstance(img, Image.Image)
        assert img.mode in ("RGB", "1")

    def test_render_without_events(self):
        """Test rendering with no events."""
        template = DefaultTemplate()
        
        img = template.render([])
        
        assert isinstance(img, Image.Image)

    def test_bw_color_mode(self):
        """Test rendering in B&W color mode."""
        template = DefaultTemplate(color_mode="bw")
        
        events = [{"summary": "Event", "start": "10:00"}]
        img = template.render(events)
        
        # B&W images should be mode '1'
        assert img.mode == "1"

    def test_rgb_color_mode(self):
        """Test rendering in RGB color mode."""
        template = DefaultTemplate(color_mode="red")
        
        events = [{"summary": "Event", "start": "10:00"}]
        img = template.render(events)
        
        # RGB images should be mode 'RGB'
        assert img.mode == "RGB"


class TestWeatherTemplateRendering:
    """Test weather-focused template rendering."""

    def test_weather_template_initialization(self):
        """Test weather template initializes."""
        template = WeatherTemplate(width=800, height=480)
        
        assert template.width == 800
        assert template.height == 480

    def test_render_weather_display(self):
        """Test rendering weather information prominently."""
        template = WeatherTemplate(width=800, height=480)
        
        weather = WeatherData(
            temperature=22.5,
            condition="Cloudy",
            humidity=75,
            wind_speed=15.0,
            icon="☁️",
            timestamp=datetime.now(),
            location="London",
        )
        
        events = [
            {"summary": "Indoor Meeting", "start": "10:00"},
        ]
        
        img = template.render(events, weather)
        
        assert isinstance(img, Image.Image)
        assert img.size == (800, 480)

    def test_weather_template_without_weather(self):
        """Test weather template without weather data."""
        template = WeatherTemplate()
        
        img = template.render([])
        
        assert isinstance(img, Image.Image)

    def test_multiple_events_rendering(self):
        """Test rendering multiple events."""
        template = WeatherTemplate()
        
        events = [
            {"summary": f"Event {i}", "start": f"{9+i}:00"}
            for i in range(5)
        ]
        
        weather = WeatherData(
            temperature=18.0,
            condition="Rainy",
            humidity=85,
            wind_speed=20.0,
            icon="🌧️",
            timestamp=datetime.now(),
            location="London",
        )
        
        img = template.render(events, weather)
        
        assert isinstance(img, Image.Image)


class TestRenderingWithDifferentDimensions:
    """Test rendering with various display dimensions."""

    @pytest.mark.parametrize("width,height", [
        (800, 480),  # Standard
        (1024, 768),  # Larger
        (600, 400),  # Smaller
    ])
    def test_render_with_dimensions(self, width, height):
        """Test rendering with different dimensions."""
        template = DefaultTemplate(width=width, height=height)
        
        events = [{"summary": "Event", "start": "10:00"}]
        img = template.render(events)
        
        assert img.size == (width, height)


class TestEventFormatting:
    """Test event formatting in templates."""

    def test_event_with_time(self):
        """Test rendering event with time."""
        template = DefaultTemplate()
        
        events = [
            {
                "summary": "Team Meeting",
                "start": "09:30",
                "end": "10:30",
            }
        ]
        
        img = template.render(events)
        assert isinstance(img, Image.Image)

    def test_event_with_long_title(self):
        """Test rendering event with long title."""
        template = DefaultTemplate()
        
        long_title = "A" * 100  # Very long title
        events = [{"summary": long_title, "start": "10:00"}]
        
        img = template.render(events)
        assert isinstance(img, Image.Image)

    def test_many_events(self):
        """Test rendering many events."""
        template = DefaultTemplate()
        
        events = [
            {"summary": f"Event {i}", "start": f"{9 + i//4}:{(i%4)*15:02d}"}
            for i in range(20)
        ]
        
        img = template.render(events)
        assert isinstance(img, Image.Image)


class TestWeatherDataHandling:
    """Test handling of various weather conditions."""

    @pytest.mark.parametrize("condition,icon", [
        ("Sunny", "☀️"),
        ("Cloudy", "☁️"),
        ("Rainy", "🌧️"),
        ("Snowy", "❄️"),
        ("Stormy", "⛈️"),
    ])
    def test_weather_conditions(self, condition, icon):
        """Test rendering different weather conditions."""
        template = WeatherTemplate()
        
        weather = WeatherData(
            temperature=15.0,
            condition=condition,
            humidity=70,
            wind_speed=10.0,
            icon=icon,
            timestamp=datetime.now(),
            location="London",
        )
        
        img = template.render([], weather)
        assert isinstance(img, Image.Image)

    @pytest.mark.parametrize("temp", [-10, 0, 10, 20, 25, 30, 40])
    def test_temperature_values(self, temp):
        """Test rendering various temperature values."""
        template = WeatherTemplate()
        
        weather = WeatherData(
            temperature=temp,
            condition="Test",
            humidity=50,
            wind_speed=5.0,
            icon="🌡️",
            timestamp=datetime.now(),
            location="Test",
        )
        
        img = template.render([], weather)
        assert isinstance(img, Image.Image)


class TestImageQuality:
    """Test rendered image properties."""

    def test_image_size_precision(self):
        """Test images are exact size."""
        for width in [640, 800, 1024]:
            for height in [320, 480, 768]:
                template = DefaultTemplate(width=width, height=height)
                img = template.render([])
                
                assert img.size[0] == width
                assert img.size[1] == height

    def test_image_mode_consistency(self):
        """Test image mode is consistent."""
        # RGB mode
        template_rgb = DefaultTemplate(color_mode="red")
        img_rgb = template_rgb.render([])
        assert img_rgb.mode == "RGB"
        
        # B&W mode
        template_bw = DefaultTemplate(color_mode="bw")
        img_bw = template_bw.render([])
        assert img_bw.mode == "1"

    def test_image_is_valid(self):
        """Test rendered images are valid."""
        template = DefaultTemplate()
        img = template.render([{"summary": "Test", "start": "10:00"}])
        
        # Should be loadable and have valid dimensions
        assert img.width > 0
        assert img.height > 0
        assert img.format is None or img.format in ("PNG", "JPEG")
