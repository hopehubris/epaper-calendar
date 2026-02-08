"""Tests for cache manager."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from src.cache_manager import CacheManager

@pytest.fixture
def cache():
    """Create temporary cache for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        cache = CacheManager(str(db_path))
        yield cache

def test_cache_init(cache):
    """Test cache initialization."""
    assert cache.db_path.exists()
    assert cache.get_event_count() == 0

def test_store_events(cache):
    """Test storing events."""
    events = [
        {
            "id": "event1",
            "summary": "Test Event",
            "start": {"dateTime": datetime.now().isoformat()},
            "end": {"dateTime": (datetime.now() + timedelta(hours=1)).isoformat()},
        }
    ]
    
    count = cache.store_events("calendar1", events)
    assert count == 1
    assert cache.get_event_count() == 1

def test_get_events(cache):
    """Test retrieving events."""
    events = [
        {
            "id": "event1",
            "summary": "Test Event",
            "start": {"dateTime": datetime.now().isoformat()},
            "end": {"dateTime": (datetime.now() + timedelta(hours=1)).isoformat()},
        }
    ]
    
    cache.store_events("calendar1", events)
    retrieved = cache.get_events("calendar1")
    
    assert len(retrieved) == 1
    assert retrieved[0]["summary"] == "Test Event"

def test_cache_age(cache):
    """Test cache age calculation."""
    assert cache.get_cache_age() is None  # Empty cache
    
    events = [
        {
            "id": "event1",
            "summary": "Test",
            "start": {"dateTime": datetime.now().isoformat()},
            "end": {"dateTime": (datetime.now() + timedelta(hours=1)).isoformat()},
        }
    ]
    
    cache.store_events("calendar1", events)
    age = cache.get_cache_age()
    
    assert age is not None
    assert 0 <= age < 5  # Should be very recent

def test_clear_all(cache):
    """Test clearing cache."""
    events = [
        {
            "id": "event1",
            "summary": "Test",
            "start": {"dateTime": datetime.now().isoformat()},
            "end": {"dateTime": (datetime.now() + timedelta(hours=1)).isoformat()},
        }
    ]
    
    cache.store_events("calendar1", events)
    assert cache.get_event_count() == 1
    
    cache.clear_all()
    assert cache.get_event_count() == 0
