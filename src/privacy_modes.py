"""
Privacy modes for display rendering (XKCD, literature clock, etc).
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
import random


logger = logging.getLogger(__name__)


class XKCDPrivacyMode:
    """XKCD-style privacy mode that obscures text with random substitution."""

    # XKCD-inspired character substitution
    ALPHABET = "abcdefghijklmnopqrstuvwxyz"
    XKCD_SUB = "dpbtgfmvwkcjs znhreyuqoxila"  # Random substitution cipher

    @classmethod
    def encrypt(cls, text: str) -> str:
        """
        Encrypt text using XKCD substitution cipher.
        
        Args:
            text: Text to encrypt
            
        Returns:
            Encrypted text
        """
        result = []
        for char in text.lower():
            if char in cls.ALPHABET:
                index = cls.ALPHABET.index(char)
                result.append(cls.XKCD_SUB[index])
            else:
                result.append(char)
        return "".join(result)

    @classmethod
    def obscure_events(cls, events: List[Dict]) -> List[Dict]:
        """
        Obscure event titles and details.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List of events with obscured titles
        """
        obscured = []
        for event in events:
            obscured_event = event.copy()
            
            # Obscure event title
            if "summary" in event:
                obscured_event["summary"] = cls.encrypt(event["summary"])
            
            # Obscure event description
            if "description" in event:
                obscured_event["description"] = cls.encrypt(event["description"])
            
            # Obscure attendees
            if "attendees" in event:
                obscured_event["attendees"] = [
                    cls.encrypt(a) for a in event["attendees"]
                ]
            
            obscured.append(obscured_event)
        
        return obscured

    @classmethod
    def create_display_text(cls, events: List[Dict]) -> str:
        """
        Create display text with XKCD-style obscuration.
        
        Args:
            events: List of events
            
        Returns:
            Formatted display text with obscured events
        """
        lines = ["[PRIVACY MODE - XKCD]"]
        
        obscured = cls.obscure_events(events)
        
        for i, event in enumerate(obscured[:5], 1):
            start = event.get("start", "??:??")
            title = event.get("summary", "[Event]")[:30]
            lines.append(f"{i}. {start} - {title}")
        
        if len(events) > 5:
            lines.append(f"... and {len(events) - 5} more")
        
        return "\n".join(lines)


class LiteratureClockMode:
    """Literature clock mode - displays time using literary references."""

    # Literature database (time -> literary quote)
    LITERATURE_DB = {
        "00:00": '"It was midnight." - Poe',
        "01:00": '"One o\'clock and all is well." - Traditional',
        "02:00": '"Two in the morning, and sleep eludes me." - Kafka',
        "03:00": '"The witching hour." - Shakespeare',
        "04:00": '"Four o\'clock and the world sleeps." - Unknown',
        "05:00": '"Five past the hour, before dawn breaks." - Dickinson',
        "06:00": '"Six o\'clock, the day begins to stir." - Thoreau',
        "07:00": '"Seven in the morning, coffee time." - Joyce',
        "08:00": '"Eight o\'clock, the working day." - Melville',
        "09:00": '"Nine o\'clock and the city awakens." - Fitzgerald',
        "10:00": '"Ten o\'clock and the work continues." - Asimov',
        "11:00": '"Eleven o\'clock, nearly noon." - Austen',
        "12:00": '"Noon has arrived." - Hemingway',
        "13:00": '"One in the afternoon." - Christie',
        "14:00": '"Two o\'clock, mid-afternoon." - Woolf',
        "15:00": '"Three o\'clock, the shadows lengthen." - Brontë',
        "16:00": '"Four o\'clock, tea time." - Wilde',
        "17:00": '"Five o\'clock, the day\'s end nears." - Larkin',
        "18:00": '"Six o\'clock, evening descends." - Hardy',
        "19:00": '"Seven o\'clock, nightfall." - Lovecraft',
        "20:00": '"Eight o\'clock, the night deepens." - Stoker',
        "21:00": '"Nine o\'clock, late evening." - Shelley',
        "22:00": '"Ten o\'clock, before bed." - Alcott',
        "23:00": '"Eleven o\'clock, the night\'s end." - Poe',
    }

    @classmethod
    def get_time_quote(cls, dt: Optional[datetime] = None) -> str:
        """
        Get literature quote for current time.
        
        Args:
            dt: Optional datetime (defaults to now)
            
        Returns:
            Literary quote with time reference
        """
        if dt is None:
            dt = datetime.now()

        time_str = dt.strftime("%H:00")
        return cls.LITERATURE_DB.get(time_str, f'"{dt.strftime("%H:%M")}" - Unknown')

    @classmethod
    def create_display_text(cls, events: List[Dict]) -> str:
        """
        Create display with literature clock theme.
        
        Args:
            events: List of events
            
        Returns:
            Display text with literary time reference
        """
        quote = cls.get_time_quote()
        lines = [quote, "", "Today's schedule:", ""]
        
        # Show only time and generic event indicator
        for i, event in enumerate(events[:7], 1):
            start = event.get("start", "??:??")
            lines.append(f"  {i}. {start} - [Event]")
        
        if len(events) > 7:
            lines.append(f"  ... and {len(events) - 7} more events")
        
        return "\n".join(lines)


class PrivacyModeFactory:
    """Factory for creating privacy mode instances."""

    MODES = {
        "xkcd": XKCDPrivacyMode,
        "literature_clock": LiteratureClockMode,
        "none": None,
    }

    @classmethod
    def create(cls, mode: str):
        """
        Create privacy mode instance.
        
        Args:
            mode: Privacy mode name ('xkcd', 'literature_clock', 'none')
            
        Returns:
            Privacy mode instance or None
        """
        if mode not in cls.MODES:
            logger.warning(f"Unknown privacy mode: {mode}, using none")
            return None

        return cls.MODES.get(mode)

    @classmethod
    def apply_privacy(cls, mode: str, events: List[Dict], weather_desc: str = "") -> Dict:
        """
        Apply privacy mode to events and weather.
        
        Args:
            mode: Privacy mode name
            events: List of events
            weather_desc: Weather description
            
        Returns:
            Dictionary with privacy_mode, events, and weather
        """
        privacy_class = cls.create(mode)

        if privacy_class is None:
            return {
                "privacy_mode": "none",
                "events": events,
                "weather": weather_desc,
                "display_text": None,
            }

        if mode == "xkcd":
            return {
                "privacy_mode": mode,
                "events": privacy_class.obscure_events(events),
                "weather": privacy_class.encrypt(weather_desc),
                "display_text": privacy_class.create_display_text(events),
            }
        elif mode == "literature_clock":
            return {
                "privacy_mode": mode,
                "events": [{"start": e.get("start", "??:??"), "summary": "[Event]"} for e in events],
                "weather": "[Weather data hidden]",
                "display_text": privacy_class.create_display_text(events),
            }

        return {
            "privacy_mode": "none",
            "events": events,
            "weather": weather_desc,
            "display_text": None,
        }
