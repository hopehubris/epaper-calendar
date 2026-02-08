"""Tests for display renderer."""

import pytest
from datetime import datetime, timedelta
from PIL import Image

from src.display_renderer import DisplayRenderer

@pytest.fixture
def renderer():
    """Create renderer for testing."""
    return DisplayRenderer(800, 480, "red")

def test_renderer_init(renderer):
    """Test renderer initialization."""
    assert renderer.width == 800
    assert renderer.height == 480
    assert renderer.color_mode == "red"

def test_render_empty(renderer):
    """Test rendering with no events."""
    img = renderer.render([], [])
    
    assert isinstance(img, Image.Image)
    assert img.size == (800, 480)
    assert img.mode == "RGB"

def test_render_with_events(renderer):
    """Test rendering with events."""
    today = datetime.now()
    
    ashi_events = [
        {
            "id": "1",
            "summary": "Meeting",
            "start": {"dateTime": today.isoformat() + "T10:00:00"},
            "end": {"dateTime": today.isoformat() + "T11:00:00"},
        }
    ]
    
    sindi_events = [
        {
            "id": "2",
            "summary": "Appointment",
            "start": {"dateTime": (today + timedelta(days=1)).isoformat() + "T14:00:00"},
            "end": {"dateTime": (today + timedelta(days=1)).isoformat() + "T15:00:00"},
        }
    ]
    
    img = renderer.render(ashi_events, sindi_events)
    
    assert isinstance(img, Image.Image)
    assert img.size == (800, 480)

def test_render_with_timestamp(renderer):
    """Test rendering with update timestamp."""
    update_time = datetime.now()
    img = renderer.render([], [], update_time)
    
    assert isinstance(img, Image.Image)

def test_bw_mode():
    """Test black & white mode."""
    renderer = DisplayRenderer(800, 480, "bw")
    img = renderer.render([], [])
    
    assert img.mode == "1"  # 1-bit black & white
