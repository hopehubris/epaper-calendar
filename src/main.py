#!/usr/bin/env python3
"""Main application entry point for E-Paper Calendar Dashboard."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import config
from src.cache_manager import CacheManager
from src.calendar_fetcher import CalendarFetcher
from src.display_renderer import DisplayRenderer, AtAGlanceRenderer
from src.display_renderer_family import FamilyCalendarRenderer
from src.display_renderer_week import WeekOverviewRenderer
from src.display_renderer_threecolumn import ThreeColumnRenderer
from src.display_renderer_three_column_v2 import ThreeColumnV2Renderer
from src.display_renderer_dashboard import DashboardRenderer
from src.display_renderer_weather_forecast import WeatherForecastRenderer
from src.display_renderer_calendar_weather import CalendarWeatherRenderer
from src.stock_fetcher import StockFetcher
from src.weather_fetcher import WeatherFetcher
from src.waveshare_driver import get_display_driver
from src import utils

logger = logging.getLogger(__name__)

class CalendarDashboard:
    """Main calendar dashboard application."""
    
    # Display modes
    MODE_6WEEK = "6week"
    MODE_GLANCE = "glance"
    MODE_FAMILY = "family"
    MODE_WEEK = "week"
    MODE_3COL = "3col"
    MODE_3COL_V2 = "3col-v2"
    MODE_DASHBOARD = "dashboard"
    MODE_WEATHER = "weather"
    MODE_CAL_WEATHER = "calendar-weather"
    DEFAULT_MODE = MODE_3COL_V2  # Default to 3-column v2 (calendar + weather)
    
    def __init__(self, display_mode: str = DEFAULT_MODE, 
                 stock_tickers: Optional[List[str]] = None):
        """Initialize dashboard.
        
        Args:
            display_mode: Display mode ("6week", "glance", "family", "dashboard")
            stock_tickers: Stock tickers to show in dashboard mode
        """
        logger.info(f"Initializing Calendar Dashboard (mode: {display_mode})")
        
        # Validate configuration
        try:
            config.validate_config()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
        
        # Initialize components
        self.cache = CacheManager(str(config.DB_PATH))
        self.fetcher = CalendarFetcher(
            str(config.CREDENTIALS_PATH),
            str(config.TOKEN_PATH),
            self.cache
        )
        
        # Initialize stock and weather fetchers for dashboard mode
        self.stock_fetcher = StockFetcher()
        self.weather_fetcher = WeatherFetcher()
        self.stock_tickers = stock_tickers or ["NFLX", "MSFT"]
        
        # Initialize appropriate renderer
        self.display_mode = display_mode
        if display_mode == self.MODE_6WEEK:
            self.renderer = DisplayRenderer(
                config.DISPLAY_WIDTH,
                config.DISPLAY_HEIGHT,
                config.DISPLAY_COLOR_MODE
            )
        elif display_mode == self.MODE_GLANCE:
            self.renderer = AtAGlanceRenderer(
                config.DISPLAY_WIDTH,
                config.DISPLAY_HEIGHT
            )
        elif display_mode == self.MODE_WEEK:
            self.renderer = WeekOverviewRenderer(
                config.DISPLAY_WIDTH,
                config.DISPLAY_HEIGHT
            )
        elif display_mode == self.MODE_3COL:
            self.renderer = ThreeColumnRenderer(
                config.DISPLAY_WIDTH,
                config.DISPLAY_HEIGHT
            )
        elif display_mode == self.MODE_3COL_V2:
            self.renderer = ThreeColumnV2Renderer(
                config.DISPLAY_WIDTH,
                config.DISPLAY_HEIGHT
            )
        elif display_mode == self.MODE_DASHBOARD:
            self.renderer = DashboardRenderer(
                config.DISPLAY_WIDTH,
                config.DISPLAY_HEIGHT
            )
        elif display_mode == self.MODE_WEATHER:
            self.renderer = WeatherForecastRenderer(
                config.DISPLAY_WIDTH,
                config.DISPLAY_HEIGHT
            )
        elif display_mode == self.MODE_CAL_WEATHER:
            self.renderer = CalendarWeatherRenderer(
                config.DISPLAY_WIDTH,
                config.DISPLAY_HEIGHT
            )
        else:  # MODE_FAMILY
            self.renderer = FamilyCalendarRenderer(
                config.DISPLAY_WIDTH,
                config.DISPLAY_HEIGHT
            )
        
        self.display = get_display_driver(use_hardware=True)
        
        logger.info("Dashboard initialized successfully")
    
    def update(self) -> bool:
        """Fetch events and update display.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Starting update cycle")
            start_time = datetime.now()
            
            # Fetch events from calendars
            logger.info("Fetching calendar events...")
            events, success = self.fetcher.fetch_all_calendars()
            
            ashi_events = events.get("ashi", [])
            sindi_events = events.get("sindi", [])
            
            logger.info(f"Fetched {len(ashi_events)} Ashi events, "
                       f"{len(sindi_events)} Sindi events")
            
            # Log success status
            if success.get("ashi"):
                logger.info("Ashi calendar: online")
            else:
                logger.warning("Ashi calendar: offline (using cache)")
            
            if success.get("sindi"):
                logger.info("Sindi calendar: online")
            else:
                logger.warning("Sindi calendar: offline (using cache)")
            
            # Fetch stocks and weather if needed
            stocks = None
            weather = None
            weather_forecast = None
            
            if self.display_mode == self.MODE_DASHBOARD:
                logger.info("Fetching stock prices...")
                stocks = self.stock_fetcher.get_multiple_prices(self.stock_tickers)
                logger.info(f"Fetched {len(stocks)} stocks")
                
                logger.info("Fetching weather...")
                weather = self.weather_fetcher.get_current_weather()
                if weather:
                    logger.info(f"Weather: {weather.get('temp')}° {weather.get('condition')}")
            
            elif self.display_mode == self.MODE_WEATHER:
                logger.info("Fetching 3-day weather forecast...")
                weather = self.weather_fetcher.get_current_weather()
                weather_forecast = self.weather_fetcher.get_forecast_3day()
                if weather:
                    logger.info(f"Current: {weather.get('temp')}° {weather.get('condition')}")
                if weather_forecast:
                    logger.info(f"Forecast: {len(weather_forecast)} days")
            
            elif self.display_mode == self.MODE_CAL_WEATHER:
                logger.info("Fetching weather for calendar view...")
                weather = self.weather_fetcher.get_current_weather()
                weather_forecast = self.weather_fetcher.get_forecast_3day()
                if weather:
                    logger.info(f"Current: {weather.get('temp')}° {weather.get('condition')}")
                if weather_forecast:
                    logger.info(f"Forecast: {len(weather_forecast)} days")
            
            elif self.display_mode == self.MODE_3COL_V2:
                logger.info("Fetching weather for 3-column view...")
                weather = self.weather_fetcher.get_current_weather()
                forecast = self.weather_fetcher.get_forecast_3day()
                if weather:
                    logger.info(f"Current: {weather.get('temp')}° {weather.get('condition')}")
                if forecast:
                    logger.info(f"Forecast: {len(forecast)} days available")
            
            # Render display
            logger.info("Rendering display...")
            if self.display_mode == self.MODE_DASHBOARD:
                img = self.renderer.render(ashi_events, sindi_events, 
                                         stocks=stocks, weather=weather, 
                                         update_time=start_time)
            elif self.display_mode == self.MODE_WEATHER:
                img = self.renderer.render(weather_forecast=weather_forecast,
                                         current_weather=weather,
                                         update_time=start_time)
            elif self.display_mode == self.MODE_CAL_WEATHER:
                img = self.renderer.render(ashi_events, sindi_events,
                                         weather_forecast=weather_forecast,
                                         current_weather=weather,
                                         update_time=start_time)
            elif self.display_mode == self.MODE_3COL_V2:
                img = self.renderer.render(ashi_events, sindi_events,
                                         current_weather=weather,
                                         forecast=forecast,
                                         update_time=start_time)
            elif self.display_mode == self.MODE_3COL:
                img = self.renderer.render(ashi_events, sindi_events, 
                                         weather=weather, 
                                         update_time=start_time)
            else:
                img = self.renderer.render(ashi_events, sindi_events, start_time)
            
            # Display image
            logger.info("Updating hardware display...")
            success = self.display.display_image(img)
            elapsed = (datetime.now() - start_time).total_seconds()
            
            if success:
                logger.info(f"Update completed in {elapsed:.1f} seconds")
                return True
            else:
                # Not an error - hardware may just not be initialized
                logger.info(f"Display update handled (simulation mode or hardware not ready) - {elapsed:.1f}s")
                return True  # Still consider this a successful update
            
        except Exception as e:
            utils.log_error("Update cycle failed", e)
            return False
    
    def run_once(self):
        """Run single update cycle (for testing or systemd timer)."""
        success = self.update()
        sys.exit(0 if success else 1)
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            self.display.cleanup()
            logger.info("Cleanup complete")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="E-Paper Calendar Dashboard")
    parser.add_argument("--mode", choices=["6week", "glance", "family", "week", "3col", "3col-v2", "dashboard", "weather", "calendar-weather"], 
                       default="3col-v2",
                       help="Display mode: '3col-v2' (40/30/30 three-column), 'calendar-weather', 'dashboard', 'weather', 'family', '3col', 'week', 'glance', '6week'")
    parser.add_argument("--stocks", nargs="+", default=["NFLX", "MSFT"],
                       help="Stock tickers to show in dashboard mode (e.g., --stocks AAPL MSFT)")
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("E-Paper Calendar Dashboard v0.1.0")
    logger.info(f"Start time: {datetime.now().isoformat()}")
    logger.info(f"Display mode: {args.mode}")
    if args.mode == "dashboard":
        logger.info(f"Stocks: {', '.join(args.stocks)}")
    logger.info("=" * 60)
    
    dashboard = CalendarDashboard(display_mode=args.mode, 
                                 stock_tickers=args.stocks if args.mode == "dashboard" else None)
    
    try:
        dashboard.run_once()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        dashboard.cleanup()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        dashboard.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
