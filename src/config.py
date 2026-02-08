"""Configuration management for E-Paper Calendar Dashboard."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Paths
BASE_DIR = Path(__file__).parent.parent
CREDENTIALS_PATH = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH", BASE_DIR / "credentials.json")
TOKEN_PATH = os.getenv("GOOGLE_CALENDAR_TOKEN_PATH", BASE_DIR / "token.json")
DB_PATH = os.getenv("DB_PATH", BASE_DIR / "events_cache.db")
LOG_FILE = os.getenv("LOG_FILE", BASE_DIR / "calendar.log")

# Calendar Configuration
ASHI_CALENDAR_ID = os.getenv("ASHI_CALENDAR_ID", "")
SINDI_CALENDAR_ID = os.getenv("SINDI_CALENDAR_ID", "")
TIMEZONE = os.getenv("TIMEZONE", "America/Los_Angeles")

# Display Configuration
DISPLAY_WIDTH = int(os.getenv("DISPLAY_WIDTH", "800"))
DISPLAY_HEIGHT = int(os.getenv("DISPLAY_HEIGHT", "480"))
DISPLAY_COLOR_MODE = os.getenv("DISPLAY_COLOR_MODE", "red")  # 'red' or 'bw'

# Update interval
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "900"))  # 15 minutes

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Waveshare GPIO pins
WAVESHARE_CS_PIN = int(os.getenv("WAVESHARE_CS_PIN", "8"))
WAVESHARE_CLK_PIN = int(os.getenv("WAVESHARE_CLK_PIN", "11"))
WAVESHARE_MOSI_PIN = int(os.getenv("WAVESHARE_MOSI_PIN", "10"))
WAVESHARE_DC_PIN = int(os.getenv("WAVESHARE_DC_PIN", "25"))
WAVESHARE_RST_PIN = int(os.getenv("WAVESHARE_RST_PIN", "27"))
WAVESHARE_BUSY_PIN = int(os.getenv("WAVESHARE_BUSY_PIN", "17"))

# Validate critical config
def validate_config():
    """Validate critical configuration."""
    if not ASHI_CALENDAR_ID:
        raise ValueError("ASHI_CALENDAR_ID not configured in .env")
    if not SINDI_CALENDAR_ID:
        raise ValueError("SINDI_CALENDAR_ID not configured in .env")
    return True

# Setup logging
def setup_logging():
    """Configure logging."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

if __name__ == "__main__":
    print(f"Config Base Dir: {BASE_DIR}")
    print(f"Credentials: {CREDENTIALS_PATH}")
    print(f"Token: {TOKEN_PATH}")
    print(f"Database: {DB_PATH}")
    print(f"Ashi Calendar: {ASHI_CALENDAR_ID}")
    print(f"Sindi Calendar: {SINDI_CALENDAR_ID}")
    print(f"Timezone: {TIMEZONE}")
    print(f"Display: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT} ({DISPLAY_COLOR_MODE})")
    print(f"Update Interval: {UPDATE_INTERVAL}s")
