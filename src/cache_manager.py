"""SQLite cache manager for calendar events."""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages SQLite cache for calendar events."""
    
    def __init__(self, db_path: str):
        """Initialize cache manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    calendar_id TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    description TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    all_day INTEGER DEFAULT 0,
                    color TEXT,
                    event_json TEXT NOT NULL,
                    cached_at TEXT NOT NULL,
                    UNIQUE(id, calendar_id)
                )
            """)
            
            # Cache metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_calendar_id ON events(calendar_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_start_time ON events(start_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cached_at ON events(cached_at)")
            
            conn.commit()
            logger.info(f"Cache database initialized: {self.db_path}")
    
    def store_events(self, calendar_id: str, events: List[Dict]) -> int:
        """Store events in cache.
        
        Args:
            calendar_id: Calendar identifier
            events: List of event dictionaries
            
        Returns:
            Number of events stored
        """
        now = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            count = 0
            for event in events:
                event_id = event.get("id", "")
                if not event_id:
                    logger.warning(f"Skipping event without ID: {event.get('summary')}")
                    continue
                
                try:
                    start_time = event.get("start", {}).get("dateTime") or \
                                 event.get("start", {}).get("date")
                    end_time = event.get("end", {}).get("dateTime") or \
                               event.get("end", {}).get("date")
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO events
                        (id, calendar_id, summary, description, start_time, end_time,
                         all_day, color, event_json, cached_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        event_id,
                        calendar_id,
                        event.get("summary", ""),
                        event.get("description", ""),
                        start_time,
                        end_time,
                        1 if "date" in event.get("start", {}) else 0,
                        event.get("colorId", ""),
                        json.dumps(event),
                        now
                    ))
                    count += 1
                except Exception as e:
                    logger.error(f"Error storing event {event_id}: {e}")
            
            conn.commit()
            logger.info(f"Stored {count} events for calendar {calendar_id}")
            
            # Update cache timestamp
            self._set_metadata("last_update", now)
        
        return count
    
    def get_events(self, calendar_id: Optional[str] = None,
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> List[Dict]:
        """Retrieve events from cache.
        
        Args:
            calendar_id: Filter by calendar (None = all)
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            
        Returns:
            List of event dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT event_json FROM events WHERE 1=1"
            params = []
            
            if calendar_id:
                query += " AND calendar_id = ?"
                params.append(calendar_id)
            
            if start_date:
                query += " AND start_time >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND start_time <= ?"
                params.append(end_date)
            
            query += " ORDER BY start_time ASC"
            
            cursor.execute(query, params)
            events = []
            
            for row in cursor.fetchall():
                try:
                    events.append(json.loads(row["event_json"]))
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing cached event JSON: {e}")
            
            return events
    
    def clear_old_events(self, days: int = 7) -> int:
        """Clear events older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of events deleted
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM events
                WHERE datetime(start_time) < datetime('now', '-' || ? || ' days')
            """, (days,))
            
            deleted = cursor.rowcount
            conn.commit()
            logger.info(f"Cleared {deleted} old events")
            
            return deleted
    
    def get_cache_age(self) -> Optional[int]:
        """Get age of cache in seconds.
        
        Returns:
            Age in seconds, or None if cache empty
        """
        last_update = self._get_metadata("last_update")
        if not last_update:
            return None
        
        try:
            cache_time = datetime.fromisoformat(last_update)
            age = (datetime.utcnow() - cache_time).total_seconds()
            return int(age)
        except Exception as e:
            logger.error(f"Error calculating cache age: {e}")
            return None
    
    def get_event_count(self, calendar_id: Optional[str] = None) -> int:
        """Get count of cached events.
        
        Args:
            calendar_id: Filter by calendar (None = all)
            
        Returns:
            Number of events
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if calendar_id:
                cursor.execute(
                    "SELECT COUNT(*) FROM events WHERE calendar_id = ?",
                    (calendar_id,)
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM events")
            
            return cursor.fetchone()[0]
    
    def _set_metadata(self, key: str, value: str):
        """Store metadata."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO cache_metadata (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, value, datetime.utcnow().isoformat()))
            conn.commit()
    
    def _get_metadata(self, key: str) -> Optional[str]:
        """Retrieve metadata."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT value FROM cache_metadata WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
    
    def clear_all(self):
        """Clear all cached events."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events")
            cursor.execute("DELETE FROM cache_metadata")
            conn.commit()
            logger.info("Cache cleared")

if __name__ == "__main__":
    # Test cache manager
    logging.basicConfig(level=logging.INFO)
    
    cache = CacheManager("test_cache.db")
    print(f"Cache initialized: {cache.db_path}")
    print(f"Event count: {cache.get_event_count()}")
    print(f"Cache age: {cache.get_cache_age()}")
