"""
Display templates for different layouts and display modes.
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from src.providers.base import WeatherData


logger = logging.getLogger(__name__)


class DisplayTemplate:
    """Base class for display templates."""

    def __init__(self, width: int = 800, height: int = 480, color_mode: str = "red"):
        """Initialize template."""
        self.width = width
        self.height = height
        self.color_mode = color_mode
        self.black = 0 if color_mode == "bw" else (0, 0, 0)
        self.white = 1 if color_mode == "bw" else (255, 255, 255)

    def render(self, events: List[Dict], weather: Optional[WeatherData] = None) -> Image.Image:
        """Render display. Must be implemented by subclass."""
        raise NotImplementedError


class DefaultTemplate(DisplayTemplate):
    """Default template with weather integration."""

    def __init__(self, width: int = 800, height: int = 480, color_mode: str = "red"):
        """Initialize default template."""
        super().__init__(width, height, color_mode)
        self._load_fonts()

    def _load_fonts(self):
        """Load fonts with fallbacks."""
        try:
            self.font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
            self.font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
            self.font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 10)
        except (OSError, AttributeError):
            try:
                self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                self.font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
                self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
            except (OSError, AttributeError):
                self.font_large = ImageFont.load_default()
                self.font_medium = ImageFont.load_default()
                self.font_small = ImageFont.load_default()

    def render(self, events: List[Dict], weather: Optional[WeatherData] = None) -> Image.Image:
        """Render default layout with optional weather."""
        if self.color_mode == "red":
            img = Image.new("RGB", (self.width, self.height), self.white)
        else:
            img = Image.new("1", (self.width, self.height), 1)

        draw = ImageDraw.Draw(img)

        # Draw header with weather
        self._draw_header(draw, weather)

        # Draw upcoming events
        self._draw_events(draw, events)

        # Draw footer with update time
        self._draw_footer(draw)

        return img

    def _draw_header(self, draw: ImageDraw.ImageDraw, weather: Optional[WeatherData]):
        """Draw header with current time and weather."""
        y = 10

        # Title
        draw.text((10, y), "Calendar & Weather", font=self.font_large, fill=self.black)

        # Weather information
        if weather:
            weather_text = f"{weather.icon} {weather.temperature}°C | {weather.condition}"
            draw.text((self.width - 300, y), weather_text, font=self.font_small, fill=self.black)

        # Horizontal line
        line_y = y + 30
        draw.line([(10, line_y), (self.width - 10, line_y)], fill=self.black, width=1)

    def _draw_events(self, draw: ImageDraw.ImageDraw, events: List[Dict]):
        """Draw upcoming events."""
        y = 50
        max_events = 5

        for i, event in enumerate(events[:max_events]):
            if y > self.height - 50:
                break

            # Format event line
            start_time = event.get("start", "")
            title = event.get("summary", "Untitled")[:40]
            color = self.black

            event_line = f"• {start_time} - {title}"
            draw.text((20, y), event_line, font=self.font_small, fill=color)

            y += 25

        # Show "more events" indicator
        if len(events) > max_events:
            draw.text((20, y), f"... and {len(events) - max_events} more events", 
                     font=self.font_small, fill=self.black)

    def _draw_footer(self, draw: ImageDraw.ImageDraw):
        """Draw footer with update timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer_y = self.height - 20

        draw.text((10, footer_y), f"Updated: {timestamp}", 
                 font=self.font_small, fill=self.black)


class WeatherTemplate(DisplayTemplate):
    """Weather-focused template."""

    def __init__(self, width: int = 800, height: int = 480, color_mode: str = "red"):
        """Initialize weather template."""
        super().__init__(width, height, color_mode)
        self._load_fonts()

    def _load_fonts(self):
        """Load fonts with fallbacks."""
        try:
            self.font_huge = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
            self.font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
            self.font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except (OSError, AttributeError):
            try:
                self.font_huge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
                self.font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            except (OSError, AttributeError):
                self.font_huge = ImageFont.load_default()
                self.font_large = ImageFont.load_default()
                self.font_medium = ImageFont.load_default()

    def render(self, events: List[Dict], weather: Optional[WeatherData] = None) -> Image.Image:
        """Render weather-focused layout."""
        if self.color_mode == "red":
            img = Image.new("RGB", (self.width, self.height), self.white)
        else:
            img = Image.new("1", (self.width, self.height), 1)

        draw = ImageDraw.Draw(img)

        if weather:
            self._draw_large_weather(draw, weather)
            self._draw_events_compact(draw, events)
        else:
            draw.text((self.width // 2 - 80, self.height // 2), 
                     "No weather data", font=self.font_large, fill=self.black)

        return img

    def _draw_large_weather(self, draw: ImageDraw.ImageDraw, weather: WeatherData):
        """Draw large weather display."""
        # Weather icon
        draw.text((50, 40), weather.icon, font=self.font_huge, fill=self.black)

        # Temperature
        temp_text = f"{weather.temperature}°C"
        draw.text((250, 50), temp_text, font=self.font_huge, fill=self.black)

        # Condition and humidity
        cond_text = f"{weather.condition} | {weather.humidity}% humidity"
        draw.text((50, 150), cond_text, font=self.font_large, fill=self.black)

        # Wind speed
        wind_text = f"Wind: {weather.wind_speed} km/h"
        draw.text((50, 190), wind_text, font=self.font_large, fill=self.black)

        # Horizontal line
        draw.line([(20, 230), (self.width - 20, 230)], fill=self.black, width=2)

    def _draw_events_compact(self, draw: ImageDraw.ImageDraw, events: List[Dict]):
        """Draw events in compact form below weather."""
        y = 250
        for event in events[:4]:
            title = event.get("summary", "Event")[:50]
            draw.text((30, y), f"• {title}", font=self.font_medium, fill=self.black)
            y += 30
