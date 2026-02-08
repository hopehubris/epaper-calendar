#!/usr/bin/env python3
"""Test display rendering without hardware."""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.display_renderer import DisplayRenderer
from src import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_events():
    """Create test events for display testing."""
    today = datetime.now()
    
    ashi_events = [
        {
            "id": "ashi1",
            "summary": "Team Meeting",
            "start": {"dateTime": today.isoformat() + "T10:00:00"},
            "end": {"dateTime": today.isoformat() + "T11:00:00"},
        },
        {
            "id": "ashi2",
            "summary": "Project Deadline",
            "start": {"date": (today + timedelta(days=3)).isoformat()},
            "end": {"date": (today + timedelta(days=3)).isoformat()},
        },
        {
            "id": "ashi3",
            "summary": "Lunch Break",
            "start": {"dateTime": today.isoformat() + "T12:00:00"},
            "end": {"dateTime": today.isoformat() + "T13:00:00"},
        },
    ]
    
    sindi_events = [
        {
            "id": "sindi1",
            "summary": "Doctor Appointment",
            "start": {"dateTime": today.isoformat() + "T14:00:00"},
            "end": {"dateTime": today.isoformat() + "T15:00:00"},
        },
        {
            "id": "sindi2",
            "summary": "Birthday Party",
            "start": {"date": (today + timedelta(days=7)).isoformat()},
            "end": {"date": (today + timedelta(days=7)).isoformat()},
        },
    ]
    
    return ashi_events, sindi_events

def main():
    """Test display rendering."""
    print("=" * 60)
    print("E-Paper Calendar Display Test")
    print("=" * 60)
    
    # Create renderer
    renderer = DisplayRenderer(
        config.DISPLAY_WIDTH,
        config.DISPLAY_HEIGHT,
        config.DISPLAY_COLOR_MODE
    )
    logger.info(f"Display: {config.DISPLAY_WIDTH}x{config.DISPLAY_HEIGHT} ({config.DISPLAY_COLOR_MODE})")
    
    # Create test events
    ashi_events, sindi_events = create_test_events()
    logger.info(f"Created {len(ashi_events)} Ashi events, {len(sindi_events)} Sindi events")
    
    # Render display
    logger.info("Rendering display...")
    img = renderer.render(ashi_events, sindi_events)
    
    # Save test image
    output_path = Path(__file__).parent.parent / "test_display.png"
    renderer.save(img, str(output_path))
    
    print(f"\n✓ Test image saved to: {output_path}")
    print(f"  Size: {img.size}")
    print(f"  Mode: {img.mode}")
    
    print("\nYou can view this image to verify display rendering:")
    print(f"  open {output_path}")

if __name__ == "__main__":
    main()
