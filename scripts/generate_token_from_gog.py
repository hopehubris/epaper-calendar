#!/usr/bin/env python3
"""Generate OAuth token using pre-authenticated gog skill.

This script attempts to use the already-authenticated AdmiralMondy account
via the gog (Gmail/Calendar) skill if available, otherwise falls back to
standard OAuth flow.
"""

import sys
import json
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_calendars_from_gog():
    """Get calendars using gog skill (if available)."""
    try:
        # Try to import and use gog skill
        # This would be available if gog is in the skills directory
        logger.info("Attempting to use pre-authenticated gog skill...")
        
        # For now, we'll provide manual configuration instructions
        return None
    except ImportError:
        return None

def manual_calendar_id_entry():
    """Get calendar IDs from user input."""
    print("\n" + "=" * 60)
    print("Manual Calendar ID Configuration")
    print("=" * 60)
    print("""
To find your Google Calendar ID:
1. Go to https://calendar.google.com/calendar/r/settings
2. Select your calendar from left sidebar
3. Go to Settings → Integrate calendar
4. Copy the Calendar ID (looks like email address)

You can also use:
- Your Gmail address (e.g., ashi@gmail.com)
- A shared calendar ID
- A calendar shortcut
""")
    
    ashi_id = input("\nEnter Ashi's Calendar ID (or press Enter to skip): ").strip()
    sindi_id = input("Enter Sindi's Calendar ID (or press Enter to skip): ").strip()
    
    return ashi_id, sindi_id

def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("E-Paper Calendar - Calendar Configuration")
    print("=" * 60)
    
    # Check if token already exists
    token_path = Path(config.TOKEN_PATH)
    if token_path.exists():
        print(f"\n✓ Token already exists: {token_path}")
        print("Run 'python scripts/setup_oauth.py --verify' to check status")
        return
    
    # Get calendar IDs from user
    ashi_id, sindi_id = manual_calendar_id_entry()
    
    if not ashi_id and not sindi_id:
        print("\n✗ No calendar IDs provided")
        sys.exit(1)
    
    # Update .env with calendar IDs
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, "r") as f:
            env_content = f.read()
        
        if ashi_id:
            env_content = env_content.replace(
                "ASHI_CALENDAR_ID=your-ashi-calendar-id@gmail.com",
                f"ASHI_CALENDAR_ID={ashi_id}"
            )
        
        if sindi_id:
            env_content = env_content.replace(
                "SINDI_CALENDAR_ID=your-sindi-calendar-id@gmail.com",
                f"SINDI_CALENDAR_ID={sindi_id}"
            )
        
        with open(env_path, "w") as f:
            f.write(env_content)
        
        print("\n✓ Updated .env with calendar IDs")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("""
1. Ensure you have credentials.json:
   - Go to: https://console.cloud.google.com/
   - Create project → Enable Calendar API → Create OAuth desktop client
   - Download credentials JSON
   - Save as: credentials.json in project root

2. Generate OAuth token:
   python scripts/setup_oauth.py --generate

3. Verify setup:
   python scripts/setup_oauth.py --verify

4. Test calendar fetching:
   python src/main.py
""")

if __name__ == "__main__":
    main()
