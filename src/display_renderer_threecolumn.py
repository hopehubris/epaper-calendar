"""Three-column calendar display: Today/Weather (left), Rest of Week (middle), Next Week (right)."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class ThreeColumnRenderer:
    """Three-column display layout optimized for family planning.
    
    Left Column:   Date, 3-day weather, today's events (large fonts)
    Middle Column: Rest of this week (detailed)
    Right Column:  Next week and beyond
    """
    
    COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "grey": (200, 200, 200),
        "light_grey": (230, 230, 230),
        "ashi": (255, 0, 0),      # Red for Ashi
        "sindi": (0, 0, 0),        # Black for Sindi
        "dark_grey": (100, 100, 100),
        "blue": (0, 100, 200),     # For weather/next week
    }
    
    # Weather emoji/symbols (text-based for e-paper)
    WEATHER_SYMBOLS = {
        "sunny": "☀",
        "cloudy": "☁",
        "rainy": "🌧",
        "snowy": "❄",
        "foggy": "🌫",
        "partly": "⛅",
    }
    
    def __init__(self, width: int = 800, height: int = 480):
        """Initialize three-column renderer."""
        self.width = width
        self.height = height
        
        # Column widths
        self.col_width = width // 3
        self.col1_x = 10
        self.col2_x = self.col_width + 10
        self.col3_x = (self.col_width * 2) + 10
        
        # Load fonts (increased sizes for better readability)
        try:
            self.font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
            self.font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            self.font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            self.font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            self.font_xs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
            self.font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except (OSError, AttributeError):
            self.font_xl = ImageFont.load_default()
            self.font_lg = ImageFont.load_default()
            self.font_med = ImageFont.load_default()
            self.font_sm = ImageFont.load_default()
            self.font_xs = ImageFont.load_default()
            self.font_tiny = ImageFont.load_default()
    
    def render(self, ashi_events: List[Dict], sindi_events: List[Dict],
               weather: Optional[Dict] = None,
               update_time: Optional[datetime] = None) -> Image.Image:
        """Render three-column calendar.
        
        Args:
            ashi_events: Ashi's events (red)
            sindi_events: Sindi's events (black)
            weather: Weather dict (optional, placeholder)
            update_time: Last update timestamp
            
        Returns:
            PIL Image (800x480)
        """
        img = Image.new("RGB", (self.width, self.height), self.COLORS["white"])
        draw = ImageDraw.Draw(img)
        
        today = datetime.now()
        all_events = ashi_events + sindi_events
        
        # Draw column dividers
        draw.line([(self.col_width, 0), (self.col_width, self.height)], 
                 fill=self.COLORS["grey"], width=1)
        draw.line([(self.col_width * 2, 0), (self.col_width * 2, self.height)], 
                 fill=self.COLORS["grey"], width=1)
        
        # Render three columns
        self._render_left_column(draw, today, all_events, ashi_events, weather)
        self._render_middle_column(draw, today, all_events, ashi_events)
        self._render_right_column(draw, today, all_events, ashi_events)
        
        # Footer with update time
        if update_time:
            update_str = f"Updated: {update_time.strftime('%H:%M')}"
            draw.text((self.col1_x, self.height - 12), update_str, 
                     font=self.font_tiny, fill=self.COLORS["grey"])
        
        return img
    
    def _render_left_column(self, draw: ImageDraw.ImageDraw, today: datetime,
                            all_events: List[Dict], ashi_events: List[Dict],
                            weather: Optional[Dict]):
        """Render left column: Date, Weather, Today's Events."""
        x = self.col1_x
        y = 8
        
        # ===== DATE (Large) =====
        date_str = today.strftime("%m/%d/%y")
        draw.text((x, y), date_str, font=self.font_xl, fill=self.COLORS["black"])
        y += 60
        
        # ===== 3-DAY WEATHER FORECAST (Placeholder) =====
        draw.text((x, y), "WEATHER", font=self.font_med, fill=self.COLORS["black"])
        y += 26
        
        # Weather placeholder (ready for real API)
        weather_data = [
            {"day": "Today", "temp": "72°", "condition": "Clear"},
            {"day": "Tmr", "temp": "68°", "condition": "Cloudy"},
            {"day": "Thu", "temp": "65°", "condition": "Rainy"},
        ]
        
        for w in weather_data:
            weather_str = f"{w['day']} {w['temp']}"
            draw.text((x, y), weather_str, font=self.font_xs, fill=self.COLORS["dark_grey"])
            draw.text((x + 85, y), w['condition'][:8], font=self.font_xs, 
                     fill=self.COLORS["dark_grey"])
            y += 18
        
        # ===== TODAY'S EVENTS (Large fonts for easy reading) =====
        y += 8
        draw.line([(x, y), (x + self.col_width - 20, y)], 
                 fill=self.COLORS["light_grey"], width=1)
        y += 10
        
        draw.text((x, y), "TODAY", font=self.font_lg, fill=self.COLORS["black"])
        y += 32
        
        today_events = self._get_events_by_date(all_events, ashi_events, today)
        if today_events:
            for evt in today_events[:3]:  # Show max 3 today's events (reduced from 4 due to larger fonts)
                time_str = self._format_time(evt)
                title = evt.get('summary') or evt.get('title') or 'Untitled'
                title = title[:18]
                color = self.COLORS["ashi"] if evt in ashi_events else self.COLORS["sindi"]
                
                draw.text((x, y), f"{time_str}", font=self.font_sm, 
                         fill=self.COLORS["dark_grey"])
                draw.text((x + 50, y), title, font=self.font_sm, fill=color)
                y += 24
        else:
            draw.text((x, y), "No events", font=self.font_sm, fill=self.COLORS["grey"])
    
    def _render_middle_column(self, draw: ImageDraw.ImageDraw, today: datetime,
                              all_events: List[Dict], ashi_events: List[Dict]):
        """Render middle column: Rest of This Week."""
        x = self.col2_x
        y = 8
        
        draw.text((x, y), "THIS WEEK", font=self.font_med, fill=self.COLORS["black"])
        y += 26
        draw.line([(x, y), (x + self.col_width - 20, y)], 
                 fill=self.COLORS["light_grey"], width=1)
        y += 10
        
        # Show tomorrow through end of week
        for day_offset in range(1, 7):
            check_date = today + timedelta(days=day_offset)
            if check_date.weekday() == 6:  # Sunday - stop at end of week
                break
            
            day_events = self._get_events_by_date(all_events, ashi_events, check_date)
            
            if day_events:
                # Day header
                day_label = check_date.strftime("%a").upper()
                draw.text((x, y), day_label, font=self.font_sm, 
                         fill=self.COLORS["blue"])
                y += 20
                
                # Events (max 2 per day)
                for evt in day_events[:2]:
                    time_str = self._format_time(evt)
                    title = evt.get('summary') or evt.get('title') or 'Untitled'
                    title = title[:16]
                    color = self.COLORS["ashi"] if evt in ashi_events else self.COLORS["sindi"]
                    
                    draw.text((x + 5, y), f"{time_str} {title}", font=self.font_sm, 
                             fill=color)
                    y += 18
                
                y += 2
            
            if y > 420:
                break
    
    def _render_right_column(self, draw: ImageDraw.ImageDraw, today: datetime,
                             all_events: List[Dict], ashi_events: List[Dict]):
        """Render right column: Next Week and Beyond."""
        x = self.col3_x
        y = 8
        
        draw.text((x, y), "NEXT WEEK", font=self.font_med, fill=self.COLORS["black"])
        y += 26
        draw.line([(x, y), (x + self.col_width - 20, y)], 
                 fill=self.COLORS["light_grey"], width=1)
        y += 10
        
        # Show next week and beyond (7+ days out)
        for day_offset in range(7, 21):
            check_date = today + timedelta(days=day_offset)
            day_events = self._get_events_by_date(all_events, ashi_events, check_date)
            
            if day_events:
                # Day header (abbreviated)
                day_label = check_date.strftime("%a %m/%d")
                draw.text((x, y), day_label, font=self.font_sm, 
                         fill=self.COLORS["blue"])
                y += 20
                
                # Events (max 1 per day for compactness)
                for evt in day_events[:1]:
                    title = evt.get('summary') or evt.get('title') or 'Untitled'
                    title = title[:14]
                    color = self.COLORS["ashi"] if evt in ashi_events else self.COLORS["sindi"]
                    
                    draw.text((x + 5, y), title, font=self.font_sm, fill=color)
                    y += 16
                
                y += 2
            
            if y > 430:
                break
    
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
    
    def save(self, img: Image.Image, path: str = "three_column.png"):
        """Save image."""
        img.save(path)
        logger.info(f"Saved to {path}")
