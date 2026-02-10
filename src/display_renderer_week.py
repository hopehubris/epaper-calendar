"""Week overview renderer - Today, Later This Week, Next Week layout."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class WeekOverviewRenderer:
    """Renders calendar as week overview: Today, Later This Week, Next Week.
    
    Similar to family calendar reference image - organized by time period.
    """
    
    COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "grey": (200, 200, 200),
        "light_grey": (230, 230, 230),
        "ashi": (255, 0, 0),      # Red for Ashi
        "sindi": (0, 0, 0),        # Black for Sindi
        "dark_grey": (100, 100, 100),
    }
    
    def __init__(self, width: int = 800, height: int = 480):
        """Initialize week overview renderer."""
        self.width = width
        self.height = height
        
        # Load fonts
        try:
            self.font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            self.font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
            self.font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            self.font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            self.font_xs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        except (OSError, AttributeError):
            self.font_xl = ImageFont.load_default()
            self.font_lg = ImageFont.load_default()
            self.font_med = ImageFont.load_default()
            self.font_sm = ImageFont.load_default()
            self.font_xs = ImageFont.load_default()
    
    def render(self, ashi_events: List[Dict], sindi_events: List[Dict],
               update_time: Optional[datetime] = None) -> Image.Image:
        """Render week overview with three sections.
        
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
        
        # ===== HEADER: Today's date =====
        today_str = today.strftime("%A, %B %d").upper()
        draw.text((20, 10), today_str, font=self.font_xl, fill=self.COLORS["black"])
        
        # Divider
        draw.line([(20, 55), (self.width - 20, 55)], fill=self.COLORS["grey"], width=2)
        
        y = 65
        
        # ===== SECTION 1: TODAY =====
        draw.text((20, y), "TODAY", font=self.font_lg, fill=self.COLORS["black"])
        y += 28
        
        today_events = self._get_events_by_date(all_events, ashi_events, today)
        if today_events:
            for evt in today_events[:5]:
                y = self._draw_event(draw, evt, ashi_events, y, indent=30)
        else:
            draw.text((30, y), "No events", font=self.font_sm, fill=self.COLORS["grey"])
            y += 18
        
        # ===== SECTION 2: LATER THIS WEEK =====
        y += 8
        draw.line([(20, y), (self.width - 20, y)], fill=self.COLORS["light_grey"], width=1)
        y += 12
        draw.text((20, y), "LATER THIS WEEK", font=self.font_lg, fill=self.COLORS["black"])
        y += 28
        
        # Tomorrow through end of week
        for day_offset in range(1, 6):  # Tomorrow through Friday
            check_date = today + timedelta(days=day_offset)
            if check_date.weekday() < today.weekday() and day_offset > 1:  # Skip if we wrapped to next week
                break
            
            day_events = self._get_events_by_date(all_events, ashi_events, check_date)
            if day_events:
                # Day header
                day_str = check_date.strftime("%a").upper()
                draw.text((30, y), day_str, font=self.font_med, fill=self.COLORS["black"])
                y += 20
                
                # Events for this day
                for evt in day_events[:2]:
                    y = self._draw_event(draw, evt, ashi_events, y, indent=45)
                
                y += 4
            
            if y > 410:
                break
        
        # ===== FOOTER: Legend + Update Time =====
        y = self.height - 28
        draw.line([(20, y), (self.width - 20, y)], fill=self.COLORS["light_grey"], width=1)
        y += 4
        
        draw.text((20, y), "Red = Ashi  •  Black = Sindi", font=self.font_xs, 
                 fill=self.COLORS["dark_grey"])
        
        if update_time:
            update_str = f"Updated: {update_time.strftime('%H:%M')}"
            draw.text((self.width - 170, y), update_str, font=self.font_xs, 
                     fill=self.COLORS["grey"])
        
        return img
    
    def _draw_event(self, draw: ImageDraw.ImageDraw, event: Dict, 
                    ashi_events: List[Dict], y: int, indent: int = 30) -> int:
        """Draw a single event and return new y position.
        
        Returns:
            New y coordinate after drawing event
        """
        time_str = self._format_time(event)
        title = event.get('summary') or event.get('title') or 'Untitled'
        title = title[:50]
        
        color = self.COLORS["ashi"] if event in ashi_events else self.COLORS["sindi"]
        name = "Ashi" if event in ashi_events else "Sindi"
        
        # Format: TIME - TITLE (NAME)
        full_text = f"{time_str} - {title}"
        draw.text((indent, y), full_text, font=self.font_sm, fill=color)
        
        # Show name on the right
        draw.text((self.width - 120, y), f"({name})", font=self.font_xs, fill=color)
        
        return y + 18
    
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
    
    def save(self, img: Image.Image, path: str = "week_overview.png"):
        """Save image."""
        img.save(path)
        logger.info(f"Saved to {path}")
