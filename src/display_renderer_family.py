"""Family-friendly smart display calendar renderer."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class FamilyCalendarRenderer:
    """Renders calendar in family-friendly 'smart display' format.
    
    Layout matches common e-ink family calendars:
    - Top: Today's date (large, prominent)
    - Upper: Today's events (easy to scan)
    - Middle: Upcoming week, organized by date
    - Bottom: Legend (color coding)
    """
    
    COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "grey": (200, 200, 200),
        "light_grey": (230, 230, 230),
        "red": (255, 0, 0),
        "dark_grey": (100, 100, 100),
    }
    
    def __init__(self, width: int = 800, height: int = 480):
        """Initialize renderer."""
        self.width = width
        self.height = height
        
        # Load fonts
        try:
            self.font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            self.font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
            self.font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
        except (OSError, AttributeError):
            # Fallback
            self.font_xl = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
            self.font_tiny = ImageFont.load_default()
    
    def render(self, ashi_events: List[Dict], sindi_events: List[Dict],
               update_time: Optional[datetime] = None) -> Image.Image:
        """Render family calendar display.
        
        Args:
            ashi_events: Ashi's events (red)
            sindi_events: Sindi's events (black)
            update_time: Last update timestamp
            
        Returns:
            PIL Image (800x480)
        """
        img = Image.new("RGB", (self.width, self.height), self.COLORS["white"])
        draw = ImageDraw.Draw(img)
        
        today = datetime.now()
        all_events = ashi_events + sindi_events
        
        # ===== HEADER: TODAY'S DATE (LARGE & PROMINENT) =====
        today_str = today.strftime("%A, %B %d").upper()
        draw.text((20, 8), today_str, font=self.font_xl, fill=self.COLORS["black"])
        
        # Divider
        draw.line([(20, 50), (self.width - 20, 50)], fill=self.COLORS["grey"], width=2)
        
        # ===== SECTION 1: TODAY'S EVENTS =====
        y = 60
        draw.text((20, y), "TODAY", font=self.font_large, fill=self.COLORS["black"])
        y += 28
        
        today_events = self._get_events_by_date(all_events, ashi_events, today)
        
        if today_events:
            for evt in today_events[:4]:
                time_str = self._format_time(evt)
                title = evt.get('title', 'Untitled')[:45]
                color = self.COLORS["red"] if evt in ashi_events else self.COLORS["black"]
                
                draw.text((30, y), time_str, font=self.font_small, fill=self.COLORS["dark_grey"])
                draw.text((85, y), title, font=self.font_small, fill=color)
                y += 19
        else:
            draw.text((30, y), "No events", font=self.font_small, fill=self.COLORS["grey"])
            y += 19
        
        # ===== SECTION 2: UPCOMING DAYS =====
        y += 8
        draw.line([(20, y), (self.width - 20, y)], fill=self.COLORS["light_grey"], width=1)
        y += 8
        draw.text((20, y), "UPCOMING", font=self.font_large, fill=self.COLORS["black"])
        y += 28
        
        # Show next 6 days
        for day_offset in range(1, 7):
            check_date = today + timedelta(days=day_offset)
            day_events = self._get_events_by_date(all_events, ashi_events, check_date)
            
            if day_events:
                # Day label
                day_str = check_date.strftime("%a, %b %d").upper()
                draw.text((20, y), day_str, font=self.font_medium, fill=self.COLORS["black"])
                y += 20
                
                # Events (max 2 per day)
                for evt in day_events[:2]:
                    time_str = self._format_time(evt)
                    title = evt.get('title', 'Untitled')[:40]
                    color = self.COLORS["red"] if evt in ashi_events else self.COLORS["black"]
                    
                    draw.text((35, y), f"{time_str} - {title}", font=self.font_small, fill=color)
                    y += 17
                
                if y > 420:
                    break
        
        # ===== FOOTER: Legend & Update Time =====
        y = self.height - 28
        draw.line([(20, y), (self.width - 20, y)], fill=self.COLORS["light_grey"], width=1)
        y += 4
        
        draw.text((20, y), "Red = Ashi  •  Black = Sindi", font=self.font_tiny, fill=self.COLORS["dark_grey"])
        
        if update_time:
            update_str = f"Updated: {update_time.strftime('%H:%M')}"
            draw.text((self.width - 170, y), update_str, font=self.font_tiny, fill=self.COLORS["grey"])
        
        return img
    
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
        
        # Sort by start time
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
    
    def save(self, img: Image.Image, path: str = "display.png"):
        """Save image."""
        img.save(path)
        logger.info(f"Saved to {path}")
