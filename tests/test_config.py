"""Tests for configuration."""

import pytest
import os
from pathlib import Path

from src import config

def test_config_loaded():
    """Test that configuration is loaded."""
    assert config.DISPLAY_WIDTH == 800
    assert config.DISPLAY_HEIGHT == 480
    assert config.DISPLAY_COLOR_MODE == "red"

def test_timezone():
    """Test timezone configuration."""
    assert config.TIMEZONE == "America/Los_Angeles"

def test_update_interval():
    """Test update interval."""
    assert config.UPDATE_INTERVAL == 900
    assert config.UPDATE_INTERVAL % 60 == 0  # Must be whole minutes

def test_paths_exist():
    """Test that base directory exists."""
    assert config.BASE_DIR.exists()
    assert (config.BASE_DIR / "src").exists()
    assert (config.BASE_DIR / "scripts").exists()

def test_calendar_ids_configured():
    """Test that calendar IDs are in config (might be placeholders)."""
    assert config.ASHI_CALENDAR_ID  # Should not be empty in .env
    assert config.SINDI_CALENDAR_ID  # Should not be empty in .env
