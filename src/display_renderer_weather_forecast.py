"""Weather forecast renderer with creative visual display for 3-day forecast."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class WeatherForecastRenderer:
    """Renders a bold, readable 3-day weather forecast with visual symbols.
    
    Features:
    - Large temperature numbers (easy to read from distance)
    - Weather condition icons (☀️, ☁️, 🌧️, etc.)
    - High/low temperatures
    - Visual wind indicators
    - Color-coded conditions (green=sunny, blue=rain, grey=cloudy)
    """
    
    COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "grey": (150, 150, 150),
        "light_grey": (220, 220, 220),
        "dark_grey": (80, 80, 80),
        "sunny": (255, 180, 0),        # Orange-gold for sunny
        "cloudy": (180, 180, 180),     # Grey for cloudy
        "rainy": (100, 150, 200),      # Blue for rainy
        "stormy": (120, 100, 180),     # Purple for stormy
    }
    
    # Weather condition icons (Unicode symbols)
    WEATHER_ICONS = {
        "sunny": "☀",
        "clear": "☀",
        "partly cloudy": "⛅",
        "cloudy": "☁",
        "overcast": "☁",
        "rain": "🌧",
        "rainy": "🌧",
        "thunderstorm": "⛈",
        "snowy": "❄",
        "snow": "❄",
        "foggy": "🌫",
        "fog": "🌫",
    }
    
    def __init__(self, width: int = 800, height: int = 480):
        """Initialize weather renderer."""
        self.width = width
        self.height = height
        
        # Load fonts
        try:
            self.font_huge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            self.font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            self.font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            self.font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            self.font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
            self.font_xs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        except (OSError, AttributeError):
            self.font_huge = ImageFont.load_default()
            self.font_xl = ImageFont.load_default()
            self.font_lg = ImageFont.load_default()
            self.font_med = ImageFont.load_default()
            self.font_sm = ImageFont.load_default()
            self.font_xs = ImageFont.load_default()
    
    def render(self, weather_forecast: Optional[List[Dict]] = None,
               current_weather: Optional[Dict] = None,
               update_time: Optional[datetime] = None) -> Image.Image:
        """Render 3-day weather forecast with bold visuals.
        
        Args:
            weather_forecast: List of dicts with {date, temp_high, temp_low, condition, wind_speed}
            current_weather: Dict with {temp, condition, location}
            update_time: Last update timestamp
            
        Returns:
            PIL Image (800x480)
        """
        img = Image.new("RGB", (self.width, self.height), self.COLORS["white"])
        draw = ImageDraw.Draw(img)
        
        # Header
        draw.text((20, 15), "3-DAY FORECAST", font=self.font_lg, fill=self.COLORS["black"])
        draw.line([(20, 40), (self.width - 20, 40)], fill=self.COLORS["light_grey"], width=2)
        
        # Generate mock forecast if not provided
        if not weather_forecast:
            weather_forecast = self._generate_mock_forecast()
        
        # Render 3-day cards
        card_width = (self.width - 60) // 3  # 3 cards with margins
        card_height = 380
        
        for i, day_forecast in enumerate(weather_forecast[:3]):
            x = 20 + (i * (card_width + 10))
            y = 50
            self._render_forecast_card(draw, x, y, card_width, card_height, day_forecast, i)
        
        # Current conditions in footer
        if current_weather:
            self._render_current_conditions(draw, current_weather)
        
        # Update time
        if update_time:
            update_str = f"Updated: {update_time.strftime('%H:%M')}"
            draw.text((self.width - 150, self.height - 15), update_str,
                     font=self.font_xs, fill=self.COLORS["grey"])
        
        return img
    
    def _render_forecast_card(self, draw: ImageDraw.ImageDraw, x: int, y: int,
                              width: int, height: int, forecast: Dict, day_offset: int):
        """Render a single forecast card (bold, readable)."""
        
        # Card background
        draw.rectangle([(x, y), (x + width, y + height)], 
                      outline=self.COLORS["light_grey"], width=1)
        
        # Day label (Mon, Tue, etc.)
        today = datetime.now()
        day_date = today + timedelta(days=day_offset)
        day_label = day_date.strftime("%a").upper()
        draw.text((x + 10, y + 8), day_label, font=self.font_med,
                 fill=self.COLORS["black"])
        
        # Date (02/10)
        date_str = day_date.strftime("%m/%d")
        draw.text((x + 10, y + 28), date_str, font=self.font_sm,
                 fill=self.COLORS["dark_grey"])
        
        # Divider
        draw.line([(x + 5, y + 45), (x + width - 5, y + 45)],
                 fill=self.COLORS["light_grey"], width=1)
        
        # Condition icon (large emoji/symbol)
        condition = forecast.get('condition', 'Unknown').lower()
        icon = self._get_icon(condition)
        color = self._get_condition_color(condition)
        
        draw.text((x + (width // 2) - 15, y + 50), icon, font=self.font_huge,
                 fill=color)
        
        # High temperature (BOLD & LARGE)
        temp_high = forecast.get('temp_high', '--')
        draw.text((x + 10, y + 110), f"{temp_high}°", font=self.font_xl,
                 fill=self.COLORS["black"])
        
        # Low temperature
        temp_low = forecast.get('temp_low', '--')
        draw.text((x + 10, y + 150), f"Low: {temp_low}°", font=self.font_sm,
                 fill=self.COLORS["dark_grey"])
        
        # Condition description (bold)
        condition_text = forecast.get('condition', 'Unknown')[:12]  # Truncate long names
        draw.text((x + 10, y + 175), condition_text, font=self.font_med,
                 fill=color)
        
        # Wind indicator (if available)
        wind_speed = forecast.get('wind_speed', None)
        if wind_speed:
            wind_symbol = self._get_wind_symbol(wind_speed)
            wind_text = f"Wind: {wind_speed} mph {wind_symbol}"
            draw.text((x + 10, y + 200), wind_text, font=self.font_sm,
                     fill=self.COLORS["dark_grey"])
        
        # Precipitation chance (if available)
        precip_chance = forecast.get('precipitation_chance', None)
        if precip_chance:
            precip_text = f"💧 {precip_chance}%"
            draw.text((x + 10, y + 220), precip_text, font=self.font_sm,
                     fill=self.COLORS["rainy"])
    
    def _render_current_conditions(self, draw: ImageDraw.ImageDraw,
                                   current: Dict):
        """Render current weather conditions in footer."""
        x = 20
        y = self.height - 50
        
        draw.line([(20, y - 5), (self.width - 20, y - 5)],
                 fill=self.COLORS["light_grey"], width=1)
        
        y += 5
        
        # "Now:" label
        draw.text((x, y), "NOW:", font=self.font_med, fill=self.COLORS["black"])
        
        # Current temp (large)
        temp = current.get('temp', '--')
        draw.text((x + 60, y), f"{temp}°", font=self.font_lg,
                 fill=self.COLORS["black"])
        
        # Condition
        condition = current.get('condition', 'Unknown')
        icon = self._get_icon(condition.lower())
        draw.text((x + 140, y), icon, font=self.font_lg,
                 fill=self._get_condition_color(condition.lower()))
        
        # Location
        location = current.get('location', 'Unknown')[:20]
        draw.text((x + 190, y), location, font=self.font_sm,
                 fill=self.COLORS["dark_grey"])
    
    def _get_icon(self, condition: str) -> str:
        """Get weather icon for condition."""
        condition_lower = condition.lower()
        
        # Check for exact matches first
        if condition_lower in self.WEATHER_ICONS:
            return self.WEATHER_ICONS[condition_lower]
        
        # Check for partial matches
        for key, icon in self.WEATHER_ICONS.items():
            if key in condition_lower:
                return icon
        
        # Default fallback
        return "☀"
    
    def _get_condition_color(self, condition: str) -> Tuple:
        """Get color based on weather condition."""
        condition_lower = condition.lower()
        
        if any(word in condition_lower for word in ["sunny", "clear", "mostly sunny"]):
            return self.COLORS["sunny"]
        elif any(word in condition_lower for word in ["rainy", "rain", "drizzle", "precipitation"]):
            return self.COLORS["rainy"]
        elif any(word in condition_lower for word in ["thunder", "storm"]):
            return self.COLORS["stormy"]
        elif any(word in condition_lower for word in ["snow", "snowy"]):
            return self.COLORS["stormy"]
        elif any(word in condition_lower for word in ["cloudy", "overcast", "partly"]):
            return self.COLORS["cloudy"]
        else:
            return self.COLORS["dark_grey"]
    
    def _get_wind_symbol(self, speed: float) -> str:
        """Get wind symbol based on speed."""
        if speed < 5:
            return "↗"  # Light breeze
        elif speed < 15:
            return "⇗"  # Moderate wind
        else:
            return "⇒"  # Strong wind
    
    def _generate_mock_forecast(self) -> List[Dict]:
        """Generate mock 3-day forecast for testing."""
        today = datetime.now()
        conditions = ["Sunny", "Partly Cloudy", "Rainy"]
        temps_high = [72, 68, 65]
        temps_low = [58, 55, 52]
        winds = [5, 8, 12]
        precips = [0, 20, 60]
        
        forecast = []
        for i in range(3):
            forecast.append({
                'date': (today + timedelta(days=i)).isoformat(),
                'temp_high': temps_high[i],
                'temp_low': temps_low[i],
                'condition': conditions[i],
                'wind_speed': winds[i],
                'precipitation_chance': precips[i],
            })
        
        return forecast
    
    def save(self, img: Image.Image, path: str = "weather_forecast.png"):
        """Save image."""
        img.save(path)
        logger.info(f"Saved to {path}")
