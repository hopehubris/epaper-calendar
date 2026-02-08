"""Google Calendar API client with cache integration."""

import logging
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from . import config
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)

# Google Calendar API scopes
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

class CalendarFetcher:
    """Fetches events from Google Calendar with caching."""
    
    def __init__(self, credentials_path: str, token_path: str, cache_manager: CacheManager):
        """Initialize calendar fetcher.
        
        Args:
            credentials_path: Path to OAuth credentials.json
            token_path: Path to token.json (created after OAuth)
            cache_manager: CacheManager instance for offline support
        """
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.cache = cache_manager
        self.service = None
        self.last_error = None
        
        try:
            self.service = self._get_service()
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            self.last_error = str(e)
    
    def _get_service(self):
        """Get or create Google Calendar API service.
        
        Returns:
            Google Calendar service object
            
        Raises:
            Exception if authentication fails
        """
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            try:
                with open(self.token_path, "rb") as token_file:
                    creds = pickle.load(token_file)
                logger.info("Loaded existing token")
            except Exception as e:
                logger.warning(f"Failed to load token: {e}")
        
        # Refresh or create new token
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Refreshed OAuth token")
            except RefreshError as e:
                logger.error(f"Token refresh failed: {e}")
                raise
        elif not creds or not creds.valid:
            raise RuntimeError(
                "No valid credentials. Run setup_oauth.py to generate token.json"
            )
        
        # Save token
        with open(self.token_path, "wb") as token_file:
            pickle.dump(creds, token_file)
        
        return build("calendar", "v3", credentials=creds)
    
    def fetch_events(self, calendar_id: str, days: int = 42) -> Tuple[List[Dict], bool]:
        """Fetch events from calendar.
        
        Args:
            calendar_id: Google Calendar ID
            days: Number of days to fetch (default: 42 for 6 weeks)
            
        Returns:
            Tuple of (events list, success flag)
        """
        now = datetime.utcnow().isoformat() + "Z"
        end_date = (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"
        
        try:
            if not self.service:
                logger.warning("Service not initialized, using cache")
                return self.cache.get_events(calendar_id), False
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                timeMax=end_date,
                singleEvents=True,
                orderBy="startTime",
                maxResults=250
            ).execute()
            
            events = events_result.get("items", [])
            logger.info(f"Fetched {len(events)} events from {calendar_id}")
            
            # Store in cache
            self.cache.store_events(calendar_id, events)
            
            return events, True
            
        except HttpError as e:
            logger.error(f"Calendar API error: {e}")
            self.last_error = str(e)
            # Return cached events
            return self.cache.get_events(calendar_id), False
        except Exception as e:
            logger.error(f"Unexpected error fetching events: {e}")
            self.last_error = str(e)
            return self.cache.get_events(calendar_id), False
    
    def fetch_all_calendars(self) -> Tuple[Dict[str, List[Dict]], Dict[str, bool]]:
        """Fetch events from all configured calendars.
        
        Returns:
            Tuple of (events dict, success dict)
            - events: {calendar_id: [events]}
            - success: {calendar_id: bool}
        """
        events = {}
        success = {}
        
        calendars = [
            ("ashi", config.ASHI_CALENDAR_ID),
            ("sindi", config.SINDI_CALENDAR_ID)
        ]
        
        for name, calendar_id in calendars:
            if not calendar_id:
                logger.warning(f"No calendar ID configured for {name}")
                events[name] = []
                success[name] = False
                continue
            
            calendar_events, is_success = self.fetch_events(calendar_id)
            events[name] = calendar_events
            success[name] = is_success
        
        return events, success
    
    def get_events_for_range(self, start_date: str, end_date: str,
                            calendar_id: Optional[str] = None) -> List[Dict]:
        """Get events for date range from cache.
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            calendar_id: Filter by calendar (None = all)
            
        Returns:
            List of events
        """
        return self.cache.get_events(
            calendar_id=calendar_id,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_today_events(self, calendar_id: Optional[str] = None) -> List[Dict]:
        """Get today's events.
        
        Args:
            calendar_id: Filter by calendar (None = all)
            
        Returns:
            List of today's events sorted by start time
        """
        today = datetime.now().date()
        start = datetime.combine(today, datetime.min.time()).isoformat()
        end = datetime.combine(today + timedelta(days=1), datetime.min.time()).isoformat()
        
        events = self.cache.get_events(
            calendar_id=calendar_id,
            start_date=start,
            end_date=end
        )
        
        return sorted(events, key=lambda e: e.get("start", {}).get("dateTime", ""))
    
    def get_upcoming_events(self, limit: int = 3,
                           calendar_id: Optional[str] = None) -> List[Dict]:
        """Get upcoming events.
        
        Args:
            limit: Maximum number of events to return
            calendar_id: Filter by calendar (None = all)
            
        Returns:
            List of upcoming events (next N days)
        """
        now = datetime.utcnow().isoformat()
        end = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        events = self.cache.get_events(
            calendar_id=calendar_id,
            start_date=now,
            end_date=end
        )
        
        return sorted(
            events,
            key=lambda e: e.get("start", {}).get("dateTime", "")
        )[:limit]
    
    def is_online(self) -> bool:
        """Check if calendar API is accessible.
        
        Returns:
            True if online, False if offline (using cache)
        """
        return self.service is not None and not self.last_error

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test fetcher
    cache = CacheManager(str(config.DB_PATH))
    fetcher = CalendarFetcher(
        str(config.CREDENTIALS_PATH),
        str(config.TOKEN_PATH),
        cache
    )
    
    if fetcher.is_online():
        events, success = fetcher.fetch_all_calendars()
        print(f"Fetched events: {len(events)}")
    else:
        print("Not online, using cache")
        events, success = fetcher.fetch_all_calendars()
