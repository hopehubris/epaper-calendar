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
        
        # Layout dimensions
        self.header_height = 40
        self.grid_height = height - header_height - 120  # Top grid + bottom event list
        self.event_list_height = 80
        
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
        draw.rectangle(
            [(0, 0), (self.width, self.header_height)],
            fill=self.COLORS["light_grey"],
            outline=self.COLORS["black"]
        )
        
        # Title
        title = "6-Week Calendar"
        draw.text(
            (10, 12),
            title,
            fill=self.COLORS["black"],
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
            fill=self.COLORS["dark_grey"],
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
        draw.rectangle(
            [(grid_left, grid_top), (grid_left + grid_width, grid_top + grid_height)],
            fill=self.COLORS["white"],
            outline=self.COLORS["black"]
        )
        
        # Day names
        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day_name in enumerate(day_names):
            x = grid_left + i * cell_width + 5
            y = grid_top + 2
            draw.text((x, y), day_name, fill=self.COLORS["black"], font=self.font_small)
        
        # Draw cells and events
        current_date = start_date
        for row in range(rows):
            for col in range(cols):
                cell_left = grid_left + col * cell_width
                cell_top = grid_top + 15 + row * cell_height
                
                # Cell border
                draw.rectangle(
                    [(cell_left, cell_top), (cell_left + cell_width, cell_top + cell_height)],
                    outline=self.COLORS["black"],
                    width=1
                )
                
                # Highlight today
                if current_date == today:
                    draw.rectangle(
                        [(cell_left + 1, cell_top + 1),
                         (cell_left + cell_width - 1, cell_top + cell_height - 1)],
                        fill=self.COLORS["light_grey"]
                    )
                
                # Date number
                date_str = str(current_date.day)
                draw.text(
                    (cell_left + 3, cell_top + 2),
                    date_str,
                    fill=self.COLORS["black"],
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
        draw.rectangle(
            [(0, list_top), (self.width, list_top + list_height)],
            fill=self.COLORS["white"],
            outline=self.COLORS["black"]
        )
        
        # Header
        draw.text(
            (5, list_top + 2),
            "Today & Upcoming",
            fill=self.COLORS["black"],
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
                text_color = self.COLORS["red"] if self.color_mode == "red" else self.COLORS["black"]
            else:
                owner_indicator = "S"
                text_color = self.COLORS["black"]
            
            # Draw indicator and text
            draw.text((5, y), f"{owner_indicator}", fill=text_color, font=self.font_small)
            draw.text((15, y), f"{time_str} {title}", fill=self.COLORS["black"], font=self.font_small)
            
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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test renderer
    renderer = DisplayRenderer(800, 480, "red")
    img = renderer.render([], [])
    renderer.save(img, "test_display.png")
    print("Test image saved to test_display.png")
