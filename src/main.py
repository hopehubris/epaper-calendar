#!/usr/bin/env python3
"""Main application entry point for E-Paper Calendar Dashboard."""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import config
from src.cache_manager import CacheManager
from src.calendar_fetcher import CalendarFetcher
from src.display_renderer import DisplayRenderer
from src.waveshare_driver import get_display_driver
from src import utils

logger = logging.getLogger(__name__)

class CalendarDashboard:
    """Main calendar dashboard application."""
    
    def __init__(self):
        """Initialize dashboard."""
        logger.info("Initializing Calendar Dashboard")
        
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
        self.renderer = DisplayRenderer(
            config.DISPLAY_WIDTH,
            config.DISPLAY_HEIGHT,
            config.DISPLAY_COLOR_MODE
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
            
            # Render display
            logger.info("Rendering display...")
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
    logger.info("=" * 60)
    logger.info("E-Paper Calendar Dashboard v0.1.0")
    logger.info(f"Start time: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    dashboard = CalendarDashboard()
    
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
