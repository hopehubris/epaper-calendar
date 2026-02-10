"""Three-column calendar display with current weather and week views.

Layout:
- Left Column (40%): Top half = date + current weather, Bottom half = today's events
- Middle Column (30%): Events for rest of this week (tomorrow-Sunday)
- Right Column (30%): Events for next week

Colors: Black text with red highlights for Ashi events, black for Sindi events
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class ThreeColumnV2Renderer:
    """Three-column calendar + weather renderer optimized for e-paper."""
    
    COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "red": (255, 0, 0),
        "grey": (200, 200, 200),
        "light_grey": (230, 230, 230),
        "dark_grey": (100, 100, 100),
    }
    
    def __init__(self, width: int = 800, height: int = 480):
        """Initialize renderer."""
        self.width = width
        self.height = height
        
        # Column widths
        self.col1_width = int(width * 0.40)  # 40% (320px)
        self.col2_width = int(width * 0.30)  # 30% (240px)
        self.col3_width = width - self.col1_width - self.col2_width  # 30% (240px)
        
        self.col1_x = 0
        self.col2_x = self.col1_width
        self.col3_x = self.col1_width + self.col2_width
        
        # Load fonts
        try:
            self.font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            self.font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            self.font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
            # Event fonts: large (titles regular weight, times/labels bold)
            self.font_event_time = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            self.font_event = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)  # Regular weight, 14pt (reduced for more detail)
            self.font_day_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            self.font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
            self.font_xs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        except (OSError, AttributeError):
            self.font_xl = ImageFont.load_default()
            self.font_lg = ImageFont.load_default()
            self.font_med = ImageFont.load_default()
            self.font_event_time = ImageFont.load_default()
            self.font_event = ImageFont.load_default()
            self.font_day_label = ImageFont.load_default()
            self.font_sm = ImageFont.load_default()
            self.font_xs = ImageFont.load_default()
    
    def render(self, ashi_events: List[Dict], sindi_events: List[Dict],
               current_weather: Optional[Dict] = None,
               update_time: Optional[datetime] = None) -> Image.Image:
        """Render three-column layout.
        
        Args:
            ashi_events: Ashi's calendar events
            sindi_events: Sindi's calendar events
            current_weather: Current weather dict {temp, condition}
            update_time: Last update time
            
        Returns:
            PIL Image (800x480)
        """
        img = Image.new("RGB", (self.width, self.height), self.COLORS["white"])
        draw = ImageDraw.Draw(img)
        
        today = datetime.now()
        all_events = ashi_events + sindi_events
        
        # Draw column dividers
        draw.line([(self.col2_x, 0), (self.col2_x, self.height)],
                 fill=self.COLORS["grey"], width=1)
        draw.line([(self.col3_x, 0), (self.col3_x, self.height)],
                 fill=self.COLORS["grey"], width=1)
        
        # Horizontal divider in left column (mid-height)
        draw.line([(self.col1_x, self.height // 2), (self.col2_x, self.height // 2)],
                 fill=self.COLORS["light_grey"], width=1)
        
        # LEFT COLUMN (40%)
        # Top half: Date + Weather
        self._render_left_top(draw, today, current_weather)
        
        # Bottom half: Today's events
        self._render_left_bottom(draw, all_events, ashi_events, today)
        
        # MIDDLE COLUMN (30%)
        # Rest of this week (tomorrow - end of week)
        self._render_middle_column(draw, all_events, ashi_events, today)
        
        # RIGHT COLUMN (30%)
        # Next week events
        self._render_right_column(draw, all_events, ashi_events, today)
        
        # Footer: Update time (larger and more visible)
        if update_time:
            update_str = f"Updated: {update_time.strftime('%b %d at %H:%M')}"
            draw.text((10, self.height - 18), update_str,
                     font=self.font_sm, fill=self.COLORS["dark_grey"])
        
        return img
    
    def _render_left_top(self, draw: ImageDraw.ImageDraw, today: datetime,
                        current_weather: Optional[Dict]):
        """Render date and current weather in top half of left column."""
        x_start = self.col1_x + 10
        y = 10
        
        # Date (large)
        date_str = today.strftime("%a").upper()
        draw.text((x_start, y), date_str, font=self.font_xl,
                 fill=self.COLORS["black"])
        
        # Full date below
        date_full = today.strftime("%b %d, %Y")
        y += 36
        draw.text((x_start, y), date_full, font=self.font_med,
                 fill=self.COLORS["dark_grey"])
        
        # Current weather (expanded to fill space)
        y += 28
        if current_weather:
            temp = current_weather.get('temp', '--')
            condition = current_weather.get('condition', 'Unknown')[:20]  # Longer condition text
            wind = current_weather.get('wind', '')
            precip = current_weather.get('precip', '')
            
            # Temperature (extra large)
            draw.text((x_start, y), f"{temp}°", font=self.font_xl,
                     fill=self.COLORS["black"])
            
            # Condition (larger font)
            y += 32
            draw.text((x_start, y), condition, font=self.font_lg,
                     fill=self.COLORS["dark_grey"])
            
            # Wind (if available)
            if wind:
                y += 22
                draw.text((x_start, y), f"Wind: {wind}", font=self.font_sm,
                         fill=self.COLORS["dark_grey"])
            
            # Precipitation (if available)
            if precip:
                y += 18
                draw.text((x_start, y), f"Rain: {precip}", font=self.font_sm,
                         fill=self.COLORS["dark_grey"])
        else:
            draw.text((x_start, y), "No weather", font=self.font_sm,
                     fill=self.COLORS["grey"])
    
    def _render_left_bottom(self, draw: ImageDraw.ImageDraw,
                           all_events: List[Dict], ashi_events: List[Dict],
                           today: datetime):
        """Render today's events in bottom half of left column."""
        x_start = self.col1_x + 8
        y = (self.height // 2) + 8
        y_max = self.height - 20
        
        # Header (matching day labels in middle/right columns - 20pt bold)
        draw.text((x_start, y), "TODAY", font=self.font_day_label,
                 fill=self.COLORS["black"])
        y += 26
        
        # Get today's events
        today_events = self._get_events_by_date(all_events, today)
        
        if today_events:
            for evt in today_events:  # Show ALL events for today
                if y > y_max:
                    break
                
                title = evt.get('summary') or evt.get('title') or 'Untitled'
                title = title[:16]  # Match middle/right column title length
                
                # Who: Ashi or Sindi (full name)
                who = "Ashi" if evt in ashi_events else "Sindi"
                color = self.COLORS["red"] if evt in ashi_events else self.COLORS["black"]
                
                # Time if available
                time_str = self._format_time(evt)
                
                # Line 1: Time - Title (matching middle/right style)
                draw.text((x_start + 5, y), f"{time_str} - {title}", font=self.font_event,
                         fill=color)
                y += 16
                
                # Line 2: Who (person name - same font)
                draw.text((x_start + 5, y), who, font=self.font_event,
                         fill=color)
                
                y += 24
        else:
            draw.text((x_start + 5, y), "No events", font=self.font_event,
                     fill=self.COLORS["grey"])
    
    def _render_middle_column(self, draw: ImageDraw.ImageDraw,
                             all_events: List[Dict], ashi_events: List[Dict],
                             today: datetime):
        """Render rest of this week in middle column."""
        x_start = self.col2_x + 8
        y = 10
        y_max = self.height - 20
        
        # Header
        draw.text((x_start, y), "THIS WEEK", font=self.font_med,
                 fill=self.COLORS["black"])
        y += 20
        
        # Days: tomorrow through Sunday (or end of week)
        week_end = today + timedelta(days=(6 - today.weekday()))  # End of week
        
        current_date = today + timedelta(days=1)
        while current_date <= week_end and y < y_max:
            day_events = self._get_events_by_date(all_events, current_date)
            
            if day_events:
                # Day label (20pt bold)
                day_label = current_date.strftime("%a %m/%d").upper()
                draw.text((x_start, y), day_label, font=self.font_day_label,
                         fill=self.COLORS["black"])
                y += 24
                
                # Events for this day (show ALL events)
                for evt in day_events:
                    if y > y_max:
                        break
                    
                    title = evt.get('summary') or evt.get('title') or 'Untitled'
                    title = title[:16]  # Allow longer titles
                    
                    # Who (full name)
                    who = "Ashi" if evt in ashi_events else "Sindi"
                    color = self.COLORS["red"] if evt in ashi_events else self.COLORS["black"]
                    
                    # Time if available
                    time_str = self._format_time(evt)
                    
                    # Line 1: Time - Title
                    draw.text((x_start + 5, y), f"{time_str} - {title}", font=self.font_event,
                             fill=color)
                    y += 16
                    
                    # Line 2: Who (person name)
                    draw.text((x_start + 5, y), who, font=self.font_event,
                             fill=color)
                    
                    y += 24
                
                y += 6  # Space between days
            
            current_date += timedelta(days=1)
    
    def _render_right_column(self, draw: ImageDraw.ImageDraw,
                            all_events: List[Dict], ashi_events: List[Dict],
                            today: datetime):
        """Render next week events in right column."""
        x_start = self.col3_x + 8
        y = 10
        y_max = self.height - 20
        
        # Header
        draw.text((x_start, y), "NEXT WEEK", font=self.font_med,
                 fill=self.COLORS["black"])
        y += 20
        
        # Days: next Monday through Friday
        next_week_start = today + timedelta(days=(7 - today.weekday()))  # Next Monday
        next_week_end = next_week_start + timedelta(days=4)  # Through Friday
        
        current_date = next_week_start
        while current_date <= next_week_end and y < y_max:
            day_events = self._get_events_by_date(all_events, current_date)
            
            if day_events:
                # Day label (20pt bold)
                day_label = current_date.strftime("%a %m/%d").upper()
                draw.text((x_start, y), day_label, font=self.font_day_label,
                         fill=self.COLORS["black"])
                y += 24
                
                # Events for this day (show ALL events)
                for evt in day_events:
                    if y > y_max:
                        break
                    
                    title = evt.get('summary') or evt.get('title') or 'Untitled'
                    title = title[:16]  # Allow longer titles
                    
                    # Who (full name)
                    who = "Ashi" if evt in ashi_events else "Sindi"
                    color = self.COLORS["red"] if evt in ashi_events else self.COLORS["black"]
                    
                    # Time if available
                    time_str = self._format_time(evt)
                    
                    # Line 1: Time - Title
                    draw.text((x_start + 5, y), f"{time_str} - {title}", font=self.font_event,
                             fill=color)
                    y += 16
                    
                    # Line 2: Who (person name)
                    draw.text((x_start + 5, y), who, font=self.font_event,
                             fill=color)
                    
                    y += 24
                
                y += 6  # Space between days
            
            current_date += timedelta(days=1)
    
    def _get_events_by_date(self, all_events: List[Dict],
                           target_date: datetime) -> List[Dict]:
        """Get events for a specific date, sorted by time."""
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
    
    def _wrap_text(self, text: str, max_width: int = 18) -> List[str]:
        """Wrap text into lines for multi-line display.
        
        Args:
            text: Text to wrap
            max_width: Max characters per line
            
        Returns:
            List of text lines (max 2)
        """
        if len(text) <= max_width:
            return [text]
        
        # Try to break at a space
        for i in range(max_width, 0, -1):
            if i < len(text) and text[i] == ' ':
                return [text[:i], text[i+1:max_width]]
        
        # No space found, break at max_width
        return [text[:max_width], text[max_width:]]
    
    def save(self, img: Image.Image, path: str = "three_column_v2.png"):
        """Save image."""
        img.save(path)
        logger.info(f"Saved to {path}")
