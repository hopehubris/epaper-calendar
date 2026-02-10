"""Combined calendar + weather forecast renderer for e-paper display.

Layout:
- Left 60%: Calendar (Ashi in red, Sindi in black)
- Right 40%: Weather (3-day forecast, bold temps)

Colors: Black (text) and Red (accents) only - compatible with Waveshare red/black display
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class CalendarWeatherRenderer:
    """Renders calendar + weather in single view optimized for red/black e-paper."""
    
    COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "red": (255, 0, 0),
        "grey": (200, 200, 200),
        "dark_grey": (100, 100, 100),
    }
    
    # Weather icons using text symbols only (no color)
    WEATHER_ICONS = {
        "sunny": "SUN",
        "clear": "SUN",
        "partly cloudy": "P.CL",
        "cloudy": "CLDY",
        "overcast": "CLDY",
        "rain": "RAIN",
        "rainy": "RAIN",
        "thunderstorm": "STRM",
        "snowy": "SNOW",
        "snow": "SNOW",
        "foggy": "FOG",
        "fog": "FOG",
    }
    
    def __init__(self, width: int = 800, height: int = 480):
        """Initialize renderer."""
        self.width = width
        self.height = height
        self.mid_x = int(width * 0.6)  # 60/40 split
        
        # Load fonts
        try:
            self.font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            self.font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            self.font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
            self.font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            self.font_xs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        except (OSError, AttributeError):
            self.font_xl = ImageFont.load_default()
            self.font_lg = ImageFont.load_default()
            self.font_med = ImageFont.load_default()
            self.font_sm = ImageFont.load_default()
            self.font_xs = ImageFont.load_default()
    
    def render(self, ashi_events: List[Dict], sindi_events: List[Dict],
               weather_forecast: Optional[List[Dict]] = None,
               current_weather: Optional[Dict] = None,
               update_time: Optional[datetime] = None) -> Image.Image:
        """Render calendar + weather combined.
        
        Args:
            ashi_events: Ashi's calendar events
            sindi_events: Sindi's calendar events
            weather_forecast: 3-day forecast
            current_weather: Current weather
            update_time: Last update time
            
        Returns:
            PIL Image (800x480)
        """
        img = Image.new("RGB", (self.width, self.height), self.COLORS["white"])
        draw = ImageDraw.Draw(img)
        
        # Vertical divider
        draw.line([(self.mid_x, 0), (self.mid_x, self.height)],
                 fill=self.COLORS["grey"], width=2)
        
        # Left: Calendar
        self._render_calendar(draw, ashi_events, sindi_events)
        
        # Right: Weather
        self._render_weather(draw, weather_forecast, current_weather)
        
        # Footer: Update time
        if update_time:
            update_str = f"Updated: {update_time.strftime('%H:%M')}"
            draw.text((self.mid_x + 10, self.height - 15), update_str,
                     font=self.font_xs, fill=self.COLORS["grey"])
        
        return img
    
    def _render_calendar(self, draw: ImageDraw.ImageDraw,
                         ashi_events: List[Dict], sindi_events: List[Dict]):
        """Render calendar on left side."""
        today = datetime.now()
        all_events = ashi_events + sindi_events
        
        x_start = 20
        y_start = 15
        
        # Title with compact date
        date_str = today.strftime("%a, %b %d").upper()
        draw.text((x_start, y_start), date_str, font=self.font_xl,
                 fill=self.COLORS["black"])
        
        # Divider
        draw.line([(x_start, y_start + 32), (self.mid_x - 10, y_start + 32)],
                 fill=self.COLORS["grey"], width=1)
        
        y = y_start + 42
        
        # Show today's events first
        draw.text((x_start, y), "TODAY", font=self.font_med,
                 fill=self.COLORS["black"])
        y += 22
        
        today_events = self._get_events_by_date(all_events, ashi_events, today)
        if today_events:
            for evt in today_events[:3]:
                time_str = self._format_time(evt)
                title = evt.get('summary') or evt.get('title') or 'Untitled'
                title = title[:25]
                color = self.COLORS["red"] if evt in ashi_events else self.COLORS["black"]
                
                draw.text((x_start + 5, y), f"{time_str}", font=self.font_sm,
                         fill=self.COLORS["dark_grey"])
                draw.text((x_start + 50, y), title, font=self.font_sm, fill=color)
                y += 18
        else:
            draw.text((x_start + 5, y), "No events", font=self.font_sm,
                     fill=self.COLORS["grey"])
            y += 18
        
        # Next 2 days
        y += 8
        for day_offset in range(1, 3):
            check_date = today + timedelta(days=day_offset)
            day_events = self._get_events_by_date(all_events, ashi_events, check_date)
            
            if day_events:
                day_label = check_date.strftime("%a %m/%d").upper()
                draw.text((x_start, y), day_label, font=self.font_sm,
                         fill=self.COLORS["black"])
                y += 18
                
                for evt in day_events[:1]:  # Max 1 per day to save space
                    title = evt.get('summary') or evt.get('title') or 'Untitled'
                    title = title[:22]
                    color = self.COLORS["red"] if evt in ashi_events else self.COLORS["black"]
                    
                    draw.text((x_start + 5, y), title, font=self.font_sm, fill=color)
                    y += 16
                
                y += 4
    
    def _render_weather(self, draw: ImageDraw.ImageDraw,
                        weather_forecast: Optional[List[Dict]] = None,
                        current_weather: Optional[Dict] = None):
        """Render weather on right side."""
        x_start = self.mid_x + 15
        y_start = 15
        
        # Title
        draw.text((x_start, y_start), "WEATHER", font=self.font_lg,
                 fill=self.COLORS["black"])
        
        y = y_start + 35
        
        # Current conditions
        if current_weather:
            temp = current_weather.get('temp', '--')
            condition = current_weather.get('condition', 'Unknown')[:15]
            
            draw.text((x_start, y), f"{temp}°", font=self.font_xl,
                     fill=self.COLORS["black"])
            draw.text((x_start, y + 32), condition, font=self.font_sm,
                     fill=self.COLORS["dark_grey"])
            
            y += 70
        
        # 3-day forecast
        draw.line([(x_start, y), (self.width - 20, y)],
                 fill=self.COLORS["grey"], width=1)
        y += 8
        
        draw.text((x_start, y), "3-DAY", font=self.font_med,
                 fill=self.COLORS["black"])
        y += 22
        
        if weather_forecast:
            for i, day_forecast in enumerate(weather_forecast[:3]):
                # Day label
                day_offset = i
                day_date = datetime.now() + timedelta(days=day_offset)
                day_label = day_date.strftime("%a").upper()
                
                # Temp high (bold, large)
                temp_high = day_forecast.get('temp_high', '--')
                temp_low = day_forecast.get('temp_low', '--')
                condition = day_forecast.get('condition', '?')[:8]
                
                draw.text((x_start, y), f"{day_label} {temp_high}°/{temp_low}°",
                         font=self.font_sm, fill=self.COLORS["black"])
                draw.text((x_start, y + 16), condition, font=self.font_xs,
                         fill=self.COLORS["dark_grey"])
                
                y += 32
    
    def _get_events_by_date(self, all_events: List[Dict], ashi_events: List[Dict],
                            target_date: datetime) -> List[Dict]:
        """Get events for a date, sorted by time."""
        day_events = []
        for e in all_events:
            try:
                if isinstance(e.get('start'), dict):
                    start_str = e['start'].get('dateTime', '')
                else:
                    start_str = e.get('start', '')
                
                if not start_str:
                    continue
                
                evt_dt = datetime.fromisoformat(start_str)
                if evt_dt.date() == target_date.date():
                    day_events.append(e)
            except (ValueError, KeyError, TypeError):
                continue
        
        try:
            day_events.sort(key=lambda e: self._parse_datetime(e))
        except:
            pass
        
        return day_events
    
    def _parse_datetime(self, event: Dict) -> datetime:
        """Parse event datetime."""
        if isinstance(event.get('start'), dict):
            start_str = event['start'].get('dateTime', '')
        else:
            start_str = event.get('start', '')
        
        if start_str:
            try:
                return datetime.fromisoformat(start_str)
            except:
                pass
        
        return datetime.min
    
    def _format_time(self, event: Dict) -> str:
        """Format time as HH:MM."""
        try:
            dt = self._parse_datetime(event)
            if dt != datetime.min:
                return dt.strftime("%H:%M")
        except:
            pass
        return "--:--"
    
    def save(self, img: Image.Image, path: str = "calendar_weather.png"):
        """Save image."""
        img.save(path)
        logger.info(f"Saved to {path}")
