"""Dashboard renderer with calendar, weather, and stocks."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class DashboardRenderer:
    """Renders multi-panel dashboard: calendar + weather + stocks.
    
    Layout:
    - Left (60%): Calendar with Sindi/Ashi color coding
    - Top Right (40%): Weather
    - Bottom Right (40%): Stock prices
    """
    
    COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "grey": (200, 200, 200),
        "light_grey": (230, 230, 230),
        "ashi": (255, 0, 0),      # Red for Ashi
        "sindi": (0, 0, 0),        # Black for Sindi
        "dark_grey": (100, 100, 100),
        "green": (0, 128, 0),      # Green for positive stocks
        "red": (200, 0, 0),        # Red for negative stocks
    }
    
    def __init__(self, width: int = 800, height: int = 480):
        """Initialize dashboard renderer."""
        self.width = width
        self.height = height
        self.mid_x = int(width * 0.6)  # Split point (60/40)
        
        # Load fonts
        try:
            self.font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            self.font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            self.font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            self.font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
            self.font_xs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        except (OSError, AttributeError):
            self.font_xl = ImageFont.load_default()
            self.font_lg = ImageFont.load_default()
            self.font_med = ImageFont.load_default()
            self.font_sm = ImageFont.load_default()
            self.font_xs = ImageFont.load_default()
    
    def render(self, ashi_events: List[Dict], sindi_events: List[Dict],
               stocks: Optional[Dict] = None, weather: Optional[Dict] = None,
               update_time: Optional[datetime] = None) -> Image.Image:
        """Render dashboard.
        
        Args:
            ashi_events: Ashi's calendar events
            sindi_events: Sindi's calendar events
            stocks: Dict with ticker → {price, change, change_pct}
            weather: Dict with {temp, condition, uv_index, location}
            update_time: Last update timestamp
            
        Returns:
            PIL Image (800x480)
        """
        img = Image.new("RGB", (self.width, self.height), self.COLORS["white"])
        draw = ImageDraw.Draw(img)
        
        # Draw vertical divider
        draw.line([(self.mid_x, 0), (self.mid_x, self.height)], 
                 fill=self.COLORS["grey"], width=1)
        
        # Draw horizontal divider on right side
        draw.line([(self.mid_x, 240), (self.width, 240)], 
                 fill=self.COLORS["grey"], width=1)
        
        # Left panel: Calendar
        self._render_calendar(draw, ashi_events, sindi_events)
        
        # Top right: Weather
        self._render_weather(draw, weather)
        
        # Bottom right: Stocks
        self._render_stocks(draw, stocks)
        
        # Footer with update time
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
        
        # Title
        draw.text((x_start, y_start), "CALENDAR", font=self.font_lg, 
                 fill=self.COLORS["black"])
        
        y = y_start + 30
        
        # Show today + next 3 days
        for day_offset in range(0, 4):
            check_date = today + timedelta(days=day_offset)
            day_events = self._get_events_by_date(all_events, ashi_events, check_date)
            
            if day_offset == 0:
                day_label = "TODAY"
            else:
                day_label = check_date.strftime("%a").upper()
            
            day_label += " " + check_date.strftime("%m/%d")
            
            draw.text((x_start, y), day_label, font=self.font_sm, 
                     fill=self.COLORS["black"])
            y += 20
            
            # Show events (max 2 per day)
            if day_events:
                for evt in day_events[:2]:
                    time_str = self._format_time(evt)
                    # Use 'summary' from Google Calendar API, not 'title'
                    title = evt.get('summary') or evt.get('title') or 'Untitled'
                    title = title[:25]
                    color = self.COLORS["ashi"] if evt in ashi_events else self.COLORS["sindi"]
                    
                    name = "Ashi" if evt in ashi_events else "Sindi"
                    draw.text((x_start + 10, y), f"{time_str}", font=self.font_xs,
                             fill=self.COLORS["dark_grey"])
                    draw.text((x_start + 50, y), f"{title}", font=self.font_xs, 
                             fill=color)
                    draw.text((self.mid_x - 40, y), f"({name})", font=self.font_xs,
                             fill=color)
                    y += 16
            else:
                draw.text((x_start + 10, y), "No events", font=self.font_xs,
                         fill=self.COLORS["grey"])
                y += 16
            
            y += 4  # Space between days
    
    def _render_weather(self, draw: ImageDraw.ImageDraw, 
                        weather: Optional[Dict]):
        """Render weather on top right."""
        x_start = self.mid_x + 15
        y_start = 15
        
        draw.text((x_start, y_start), "WEATHER", font=self.font_lg,
                 fill=self.COLORS["black"])
        
        if not weather:
            draw.text((x_start, y_start + 35), "No data", font=self.font_sm,
                     fill=self.COLORS["grey"])
            return
        
        y = y_start + 35
        
        # Temperature (large)
        temp = weather.get('temp', '--')
        temp_str = f"{temp}°"
        draw.text((x_start, y), temp_str, font=self.font_xl,
                 fill=self.COLORS["black"])
        y += 40
        
        # Condition
        condition = weather.get('condition', 'Unknown')[:20]
        draw.text((x_start, y), condition, font=self.font_sm,
                 fill=self.COLORS["dark_grey"])
        y += 20
        
        # UV Index
        uv = weather.get('uv_index', '--')
        draw.text((x_start, y), f"UV: {uv}", font=self.font_xs,
                 fill=self.COLORS["dark_grey"])
        
        # Location
        location = weather.get('location', '')[:15]
        if location:
            draw.text((x_start + 80, y), location, font=self.font_xs,
                     fill=self.COLORS["grey"])
    
    def _render_stocks(self, draw: ImageDraw.ImageDraw,
                       stocks: Optional[Dict]):
        """Render stocks on bottom right."""
        x_start = self.mid_x + 15
        y_start = 250
        
        draw.text((x_start, y_start), "STOCKS", font=self.font_lg,
                 fill=self.COLORS["black"])
        
        if not stocks:
            draw.text((x_start, y_start + 35), "No data", font=self.font_sm,
                     fill=self.COLORS["grey"])
            return
        
        y = y_start + 35
        
        # Show up to 3 stocks
        for ticker, data in list(stocks.items())[:3]:
            price = data.get('price', '--')
            change = data.get('change', 0)
            change_pct = data.get('change_pct', 0)
            
            # Color based on change
            color = self.COLORS["green"] if change >= 0 else self.COLORS["red"]
            
            # Ticker + price
            draw.text((x_start, y), ticker, font=self.font_sm,
                     fill=self.COLORS["black"])
            draw.text((x_start + 80, y), f"${price}", font=self.font_sm,
                     fill=self.COLORS["black"])
            
            # Change %
            sign = "+" if change >= 0 else ""
            change_str = f"{sign}{change_pct:.2f}%"
            draw.text((x_start + 140, y), change_str, font=self.font_xs,
                     fill=color)
            
            y += 22
    
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
    
    def save(self, img: Image.Image, path: str = "dashboard.png"):
        """Save image."""
        img.save(path)
        logger.info(f"Saved to {path}")
