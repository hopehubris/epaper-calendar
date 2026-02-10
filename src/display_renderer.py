"""PIL-based display renderer for 6-week calendar grid."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import textwrap

from . import config

logger = logging.getLogger(__name__)

class DisplayRenderer:
    """Renders calendar grid and events to PIL Image."""
    
    # Color palette
    COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "grey": (200, 200, 200),
        "light_grey": (230, 230, 230),
        "red": (255, 0, 0),
        "dark_grey": (100, 100, 100),
    }
    
    def __init__(self, width: int = 800, height: int = 480, color_mode: str = "red"):
        """Initialize renderer.
        
        Args:
            width: Display width in pixels
            height: Display height in pixels
            color_mode: 'red' for red/greyscale, 'bw' for black/white
        """
        self.width = width
        self.height = height
        self.color_mode = color_mode
        
        # For B&W mode, we need to use 0/1 for colors instead of RGB tuples
        if self.color_mode == "bw":
            self.black_color = 0
            self.white_color = 1
        else:
            self.black_color = self.COLORS["black"]
            self.white_color = self.COLORS["white"]
        
        # Layout dimensions
        self.header_height = 40
        self.event_list_height = 80
        self.grid_height = height - self.header_height - self.event_list_height
        
        # Fonts (fallback to default)
        try:
            self.font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
            self.font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
            self.font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 9)
            self.font_tiny = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 7)
        except (OSError, AttributeError):
            # Fallback for Linux/RPi
            try:
                self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
                self.font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
                self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
                self.font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 7)
            except (OSError, AttributeError):
                # Default font
                self.font_large = ImageFont.load_default()
                self.font_medium = ImageFont.load_default()
                self.font_small = ImageFont.load_default()
                self.font_tiny = ImageFont.load_default()
    
    def render(self, ashi_events: List[Dict], sindi_events: List[Dict],
               update_time: Optional[datetime] = None) -> Image.Image:
        """Render complete calendar display.
        
        Args:
            ashi_events: Ashi's events (red)
            sindi_events: Sindi's events (black)
            update_time: Last update timestamp
            
        Returns:
            PIL Image object
        """
        # Create base image
        if self.color_mode == "red":
            img = Image.new("RGB", (self.width, self.height), self.COLORS["white"])
        else:
            img = Image.new("1", (self.width, self.height), 1)  # 1-bit B&W
        
        draw = ImageDraw.Draw(img)
        
        # Draw components
        self._draw_header(draw, update_time)
        self._draw_calendar_grid(draw, ashi_events, sindi_events)
        self._draw_event_list(draw, ashi_events, sindi_events)
        
        return img
    
    def _draw_header(self, draw: ImageDraw.ImageDraw, update_time: Optional[datetime]):
        """Draw header with title and timestamp."""
        # Header background
        if self.color_mode == "red":
            bg_color = self.COLORS["light_grey"]
        else:
            bg_color = 1  # White for B&W (1 = white in 1-bit mode)
        
        draw.rectangle(
            [(0, 0), (self.width, self.header_height)],
            fill=bg_color,
            outline=self.black_color
        )
        
        # Title
        title = "6-Week Calendar"
        draw.text(
            (10, 12),
            title,
            fill=self.black_color,
            font=self.font_large
        )
        
        # Timestamp
        if update_time:
            timestamp = update_time.strftime("%Y-%m-%d %H:%M")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        draw.text(
            (self.width - 150, 12),
            f"Updated: {timestamp}",
            fill=self.black_color,
            font=self.font_small
        )
    
    def _draw_calendar_grid(self, draw: ImageDraw.ImageDraw,
                           ashi_events: List[Dict],
                           sindi_events: List[Dict]):
        """Draw 6-week (42-day) calendar grid."""
        today = datetime.now().date()
        start_date = today
        
        # Start from Sunday
        while start_date.weekday() != 6:  # 6 = Sunday
            start_date -= timedelta(days=1)
        
        # Grid parameters
        grid_top = self.header_height + 5
        grid_left = 5
        grid_width = self.width - 10
        grid_height = self.grid_height
        
        # Cell dimensions
        cols = 7  # Days of week
        rows = 6  # Weeks
        cell_width = grid_width / cols
        cell_height = grid_height / rows
        
        # Draw grid background
        if self.color_mode == "red":
            bg_color = self.COLORS["white"]
        else:
            bg_color = 1  # White in B&W
        
        draw.rectangle(
            [(grid_left, grid_top), (grid_left + grid_width, grid_top + grid_height)],
            fill=bg_color,
            outline=self.black_color
        )
        
        # Day names
        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day_name in enumerate(day_names):
            x = grid_left + i * cell_width + 5
            y = grid_top + 2
            draw.text((x, y), day_name, fill=self.black_color, font=self.font_small)
        
        # Draw cells and events
        current_date = start_date
        for row in range(rows):
            for col in range(cols):
                cell_left = grid_left + col * cell_width
                cell_top = grid_top + 15 + row * cell_height
                
                # Cell border
                draw.rectangle(
                    [(cell_left, cell_top), (cell_left + cell_width, cell_top + cell_height)],
                    outline=self.black_color,
                    width=1
                )
                
                # Highlight today
                if current_date == today:
                    if self.color_mode == "red":
                        highlight_color = self.COLORS["light_grey"]
                    else:
                        highlight_color = 0  # Dark for B&W
                    
                    draw.rectangle(
                        [(cell_left + 1, cell_top + 1),
                         (cell_left + cell_width - 1, cell_top + cell_height - 1)],
                        fill=highlight_color
                    )
                
                # Date number
                date_str = str(current_date.day)
                draw.text(
                    (cell_left + 3, cell_top + 2),
                    date_str,
                    fill=self.black_color,
                    font=self.font_medium
                )
                
                # Event indicators
                day_events = self._get_events_for_date(
                    current_date,
                    ashi_events,
                    sindi_events
                )
                
                indicator_y = cell_top + 18
                for i, (event, color) in enumerate(day_events[:2]):  # Max 2 indicators per cell
                    if self.color_mode == "red" and color == "red":
                        dot_color = self.COLORS["red"]
                    else:
                        dot_color = self.COLORS["black"]
                    
                    x = cell_left + 3 + (i * 3)
                    draw.ellipse(
                        [(x, indicator_y), (x + 2, indicator_y + 2)],
                        fill=dot_color
                    )
                
                current_date += timedelta(days=1)
    
    def _draw_event_list(self, draw: ImageDraw.ImageDraw,
                        ashi_events: List[Dict],
                        sindi_events: List[Dict]):
        """Draw today's + next 3 upcoming events at bottom."""
        list_top = self.header_height + self.grid_height + 5
        list_height = self.event_list_height
        
        # Background
        if self.color_mode == "red":
            bg_color = self.COLORS["white"]
        else:
            bg_color = 1  # White in B&W
        
        draw.rectangle(
            [(0, list_top), (self.width, list_top + list_height)],
            fill=bg_color,
            outline=self.black_color
        )
        
        # Header
        draw.text(
            (5, list_top + 2),
            "Today & Upcoming",
            fill=self.black_color,
            font=self.font_medium
        )
        
        # Get today + next 3 events
        all_events = self._get_upcoming_events(ashi_events, sindi_events, limit=4)
        
        y = list_top + 18
        for i, (event, owner) in enumerate(all_events[:4]):
            if y + 12 > list_top + list_height:
                break
            
            # Get event time and title
            start = event.get("start", {})
            start_time = start.get("dateTime", start.get("date", ""))
            
            if "T" in start_time:
                time_str = start_time[11:16]  # HH:MM
            else:
                time_str = "All day"
            
            # Truncate title
            title = event.get("summary", "Untitled")[:30]
            
            # Owner color
            if owner == "ashi":
                owner_indicator = "A"
                text_color = self.COLORS["red"] if self.color_mode == "red" else self.black_color
            else:
                owner_indicator = "S"
                text_color = self.black_color
            
            # Draw indicator and text
            draw.text((5, y), f"{owner_indicator}", fill=text_color, font=self.font_small)
            draw.text((15, y), f"{time_str} {title}", fill=self.black_color, font=self.font_small)
            
            y += 12
    
    def _get_events_for_date(self, date, ashi_events: List[Dict],
                            sindi_events: List[Dict]) -> List[Tuple[Dict, str]]:
        """Get events for a specific date.
        
        Returns:
            List of (event, owner) tuples
        """
        events = []
        date_str = date.isoformat()
        
        for event in ashi_events:
            start = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", ""))
            if start.startswith(date_str):
                events.append((event, "red"))
        
        for event in sindi_events:
            start = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", ""))
            if start.startswith(date_str):
                events.append((event, "black"))
        
        return events
    
    def _get_upcoming_events(self, ashi_events: List[Dict],
                            sindi_events: List[Dict],
                            limit: int = 4) -> List[Tuple[Dict, str]]:
        """Get upcoming events sorted by start time.
        
        Returns:
            List of (event, owner) tuples
        """
        events = []
        
        for event in ashi_events:
            events.append((event, "ashi"))
        
        for event in sindi_events:
            events.append((event, "sindi"))
        
        # Sort by start time
        def get_start_time(item):
            event, _ = item
            start = event.get("start", {})
            return start.get("dateTime", start.get("date", ""))
        
        events.sort(key=get_start_time)
        return events[:limit]
    
    def save(self, image: Image.Image, path: str):
        """Save image to file.
        
        Args:
            image: PIL Image object
            path: Output file path
        """
        image.save(path)
        logger.info(f"Saved display image to {path}")


class AtAGlanceRenderer:
    """Renders calendar in 'at a glance' format: 3 weeks + today + weather (large text)."""
    
    COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "grey": (200, 200, 200),
        "light_grey": (230, 230, 230),
        "red": (255, 0, 0),
        "dark_grey": (100, 100, 100),
    }
    
    def __init__(self, width: int = 800, height: int = 480):
        """Initialize at-a-glance renderer."""
        self.width = width
        self.height = height
        
        # Load fonts (larger sizes for easy reading)
        try:
            self.font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            self.font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        except (OSError, AttributeError):
            # Fallback
            self.font_xl = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
    
    def render(self, ashi_events: List[Dict], sindi_events: List[Dict],
               update_time: Optional[datetime] = None) -> Image.Image:
        """Render calendar in family-friendly 'smart display' format.
        
        Layout:
        - Top: Today's date (large)
        - Upper: Today's events (prominent)
        - Middle: Tomorrow and upcoming week (organized by date)
        - Bottom: Legend
        
        Args:
            ashi_events: Ashi's events (marked with red)
            sindi_events: Sindi's events (marked with black)
            update_time: Last update timestamp
            
        Returns:
            PIL Image (800x480)
        """
        # Create white background
        img = Image.new("RGB", (self.width, self.height), self.COLORS["white"])
        draw = ImageDraw.Draw(img)
        
        today = datetime.now()
        all_events = ashi_events + sindi_events
        
        # ===== HEADER: Today's date (LARGE) =====
        today_str = today.strftime("%A, %B %d").upper()
        draw.text((20, 8), today_str, font=self.font_xl, fill=self.COLORS["black"])
        
        # ===== TODAY'S EVENTS =====
        y = header_h + 5
        draw.text((20, y), "TODAY:", font=self.font_large, fill=self.COLORS["black"])
        y += 25
        
        # Parse today's events
        today_events = []
        for e in (ashi_events + sindi_events):
            try:
                # Handle both dict-based start times (from API) and ISO strings
                if isinstance(e.get('start'), dict):
                    start_str = e['start'].get('dateTime', '')
                    if not start_str:
                        continue  # Skip events without start time
                    start_dt = datetime.fromisoformat(start_str)
                else:
                    start_str = e.get('start', '')
                    if not start_str:
                        continue
                    start_dt = datetime.fromisoformat(start_str)
                
                if start_dt.date() == today.date():
                    today_events.append(e)
            except (ValueError, KeyError, TypeError):
                # Skip malformed events
                continue
        
        if today_events:
            for evt in today_events[:3]:  # Show max 3 events
                # Parse start time
                if isinstance(evt.get('start'), dict):
                    start_time = datetime.fromisoformat(evt['start']['dateTime']).strftime("%H:%M")
                else:
                    start_time = datetime.fromisoformat(evt['start']).strftime("%H:%M")
                
                title = evt.get('title', 'Untitled')[:40]  # Truncate long titles
                color = self.COLORS["red"] if evt in ashi_events else self.COLORS["black"]
                draw.text((40, y), f"{start_time} - {title}", font=self.font_small, fill=color)
                y += 20
        else:
            draw.text((40, y), "No events today", font=self.font_small, fill=self.COLORS["grey"])
        
        # ===== NEXT 3 WEEKS CALENDAR =====
        y = today_h + 70
        draw.line([(20, y), (self.width - 20, y)], fill=self.COLORS["grey"], width=1)
        y += 10
        draw.text((20, y), "NEXT 3 WEEKS:", font=self.font_large, fill=self.COLORS["black"])
        y += 28
        
        # Show week-by-week
        for week_num in range(3):
            week_start = today + timedelta(days=1 + week_num * 7)
            week_end = week_start + timedelta(days=6)
            
            week_label = week_start.strftime("%b %d") + " - " + week_end.strftime("%b %d")
            draw.text((20, y), week_label, font=self.font_medium, fill=self.COLORS["black"])
            
            # Count events this week
            week_events = []
            for e in (ashi_events + sindi_events):
                try:
                    # Parse event date
                    if isinstance(e.get('start'), dict):
                        start_str = e['start'].get('dateTime', '')
                        if not start_str:
                            continue
                        evt_date = datetime.fromisoformat(start_str).date()
                    else:
                        start_str = e.get('start', '')
                        if not start_str:
                            continue
                        evt_date = datetime.fromisoformat(start_str).date()
                    
                    if week_start.date() <= evt_date <= week_end.date():
                        week_events.append(e)
                except (ValueError, KeyError, TypeError):
                    continue
            
            if week_events:
                event_summary = f"{len(week_events)} events"
                ashi_count = len([e for e in week_events if e in ashi_events])
                if ashi_count > 0:
                    event_summary += f" ({ashi_count} yours)"
                draw.text((self.width - 200, y), event_summary, font=self.font_small, fill=self.COLORS["dark_grey"])
            
            y += 22
        
        # ===== FOOTER: Legend + update time =====
        y = self.height - footer_h + 5
        draw.text((20, y), "Legend:", font=self.font_small, fill=self.COLORS["black"])
        draw.text((100, y), "Red = Ashi  |  Black = Sindi", font=self.font_small, fill=self.COLORS["dark_grey"])
        
        if update_time:
            update_str = f"Updated: {update_time.strftime('%H:%M')}"
            draw.text((self.width - 200, y), update_str, font=self.font_small, fill=self.COLORS["grey"])
        
        return img
    
    def save(self, img: Image.Image, path: str = "display_output.png"):
        """Save image to file."""
        img.save(path)
        logger.info(f"Saved at-a-glance image to {path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test renderer
    renderer = DisplayRenderer(800, 480, "red")
    img = renderer.render([], [])
    renderer.save(img, "test_display.png")
    print("Test image saved to test_display.png")
