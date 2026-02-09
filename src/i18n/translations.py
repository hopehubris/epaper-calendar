"""
Internationalization (i18n) framework for multi-language support.
"""
import logging
from typing import Dict, Optional


logger = logging.getLogger(__name__)


# Translation dictionaries by language code
TRANSLATIONS = {
    "en": {
        # Display labels
        "today": "Today",
        "tomorrow": "Tomorrow",
        "this_week": "This Week",
        "next_week": "Next Week",
        "calendar": "Calendar",
        "weather": "Weather",
        "updated": "Updated",
        "no_events": "No events scheduled",
        "event_count": "{count} events",
        "weather_condition": "Condition",
        "temperature": "Temperature",
        "humidity": "Humidity",
        "wind_speed": "Wind Speed",
        "sunrise": "Sunrise",
        "sunset": "Sunset",
        
        # Days of week
        "monday": "Monday",
        "tuesday": "Tuesday",
        "wednesday": "Wednesday",
        "thursday": "Thursday",
        "friday": "Friday",
        "saturday": "Saturday",
        "sunday": "Sunday",
        "mon": "Mon",
        "tue": "Tue",
        "wed": "Wed",
        "thu": "Thu",
        "fri": "Fri",
        "sat": "Sat",
        "sun": "Sun",
        
        # Months
        "january": "January",
        "february": "February",
        "march": "March",
        "april": "April",
        "may": "May",
        "june": "June",
        "july": "July",
        "august": "August",
        "september": "September",
        "october": "October",
        "november": "November",
        "december": "December",
        
        # Privacy modes
        "privacy_mode": "Privacy Mode",
        "privacy_xkcd": "XKCD Cipher",
        "privacy_literature": "Literature Clock",
    },
    "de": {
        # German translations
        "today": "Heute",
        "tomorrow": "Morgen",
        "this_week": "Diese Woche",
        "next_week": "Nächste Woche",
        "calendar": "Kalender",
        "weather": "Wetter",
        "updated": "Aktualisiert",
        "no_events": "Keine Ereignisse geplant",
        "event_count": "{count} Ereignisse",
        "weather_condition": "Zustand",
        "temperature": "Temperatur",
        "humidity": "Luftfeuchtigkeit",
        "wind_speed": "Windgeschwindigkeit",
        "sunrise": "Sonnenaufgang",
        "sunset": "Sonnenuntergang",
        
        "monday": "Montag",
        "tuesday": "Dienstag",
        "wednesday": "Mittwoch",
        "thursday": "Donnerstag",
        "friday": "Freitag",
        "saturday": "Samstag",
        "sunday": "Sonntag",
        "mon": "Mo",
        "tue": "Di",
        "wed": "Mi",
        "thu": "Do",
        "fri": "Fr",
        "sat": "Sa",
        "sun": "So",
        
        "january": "Januar",
        "february": "Februar",
        "march": "März",
        "april": "April",
        "may": "Mai",
        "june": "Juni",
        "july": "Juli",
        "august": "August",
        "september": "September",
        "october": "Oktober",
        "november": "November",
        "december": "Dezember",
        
        "privacy_mode": "Datenschutzmodus",
        "privacy_xkcd": "XKCD-Chiffre",
        "privacy_literature": "Literaturuhr",
    },
    "es": {
        # Spanish translations
        "today": "Hoy",
        "tomorrow": "Mañana",
        "this_week": "Esta Semana",
        "next_week": "La Próxima Semana",
        "calendar": "Calendario",
        "weather": "Clima",
        "updated": "Actualizado",
        "no_events": "Sin eventos programados",
        "event_count": "{count} eventos",
        "weather_condition": "Condición",
        "temperature": "Temperatura",
        "humidity": "Humedad",
        "wind_speed": "Velocidad del Viento",
        "sunrise": "Amanecer",
        "sunset": "Atardecer",
        
        "monday": "Lunes",
        "tuesday": "Martes",
        "wednesday": "Miércoles",
        "thursday": "Jueves",
        "friday": "Viernes",
        "saturday": "Sábado",
        "sunday": "Domingo",
        "mon": "Lun",
        "tue": "Mar",
        "wed": "Mié",
        "thu": "Jue",
        "fri": "Vie",
        "sat": "Sáb",
        "sun": "Dom",
        
        "january": "Enero",
        "february": "Febrero",
        "march": "Marzo",
        "april": "Abril",
        "may": "Mayo",
        "june": "Junio",
        "july": "Julio",
        "august": "Agosto",
        "september": "Septiembre",
        "october": "Octubre",
        "november": "Noviembre",
        "december": "Diciembre",
        
        "privacy_mode": "Modo Privacidad",
        "privacy_xkcd": "Cifra XKCD",
        "privacy_literature": "Reloj Literario",
    },
    "fr": {
        # French translations
        "today": "Aujourd'hui",
        "tomorrow": "Demain",
        "this_week": "Cette Semaine",
        "next_week": "La Semaine Prochaine",
        "calendar": "Calendrier",
        "weather": "Météo",
        "updated": "Mis à jour",
        "no_events": "Aucun événement prévu",
        "event_count": "{count} événements",
        "weather_condition": "Condition",
        "temperature": "Température",
        "humidity": "Humidité",
        "wind_speed": "Vitesse du Vent",
        "sunrise": "Lever du Soleil",
        "sunset": "Coucher du Soleil",
        
        "monday": "Lundi",
        "tuesday": "Mardi",
        "wednesday": "Mercredi",
        "thursday": "Jeudi",
        "friday": "Vendredi",
        "saturday": "Samedi",
        "sunday": "Dimanche",
        "mon": "Lun",
        "tue": "Mar",
        "wed": "Mer",
        "thu": "Jeu",
        "fri": "Ven",
        "sat": "Sam",
        "sun": "Dim",
        
        "january": "Janvier",
        "february": "Février",
        "march": "Mars",
        "april": "Avril",
        "may": "Mai",
        "june": "Juin",
        "july": "Juillet",
        "august": "Août",
        "september": "Septembre",
        "october": "Octobre",
        "november": "Novembre",
        "december": "Décembre",
        
        "privacy_mode": "Mode Confidentialité",
        "privacy_xkcd": "Chiffre XKCD",
        "privacy_literature": "Horloge Littéraire",
    },
}


class I18nManager:
    """International i18n manager for translations."""

    def __init__(self, language: str = "en"):
        """
        Initialize i18n manager.
        
        Args:
            language: Language code (en, de, es, fr)
        """
        self.language = language if language in TRANSLATIONS else "en"
        self.translations = TRANSLATIONS[self.language]

    def set_language(self, language: str) -> None:
        """
        Set active language.
        
        Args:
            language: Language code
        """
        if language in TRANSLATIONS:
            self.language = language
            self.translations = TRANSLATIONS[language]
            logger.info(f"Language set to: {language}")
        else:
            logger.warning(f"Language {language} not supported, using English")

    def t(self, key: str, **kwargs) -> str:
        """
        Get translated text.
        
        Args:
            key: Translation key
            **kwargs: Format arguments for string interpolation
            
        Returns:
            Translated text
        """
        text = self.translations.get(key, key)
        
        # Handle format arguments (e.g., {count})
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing format argument: {e}")
        
        return text

    def get_available_languages(self) -> list[str]:
        """
        Get list of available languages.
        
        Returns:
            List of language codes
        """
        return list(TRANSLATIONS.keys())

    def get_day_name(self, day: int, short: bool = False) -> str:
        """
        Get translated day name.
        
        Args:
            day: Day of week (0=Monday, 6=Sunday)
            short: Use short name (e.g., 'Mon' vs 'Monday')
            
        Returns:
            Translated day name
        """
        days_long = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        days_short = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        
        key = days_short[day] if short else days_long[day]
        return self.t(key)

    def get_month_name(self, month: int) -> str:
        """
        Get translated month name.
        
        Args:
            month: Month number (1-12)
            
        Returns:
            Translated month name
        """
        months = [
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december"
        ]
        return self.t(months[month - 1])

    def format_date(self, date_obj) -> str:
        """
        Format date using translated names.
        
        Args:
            date_obj: datetime object
            
        Returns:
            Formatted date string
        """
        day_name = self.get_day_name(date_obj.weekday())
        month_name = self.get_month_name(date_obj.month)
        return f"{day_name}, {date_obj.day} {month_name} {date_obj.year}"

    def format_time(self, time_obj) -> str:
        """
        Format time (consistent across locales).
        
        Args:
            time_obj: datetime object
            
        Returns:
            Formatted time string (HH:MM)
        """
        return time_obj.strftime("%H:%M")


# Global i18n manager instance
_i18n_instance: Optional[I18nManager] = None


def get_i18n(language: str = "en") -> I18nManager:
    """
    Get global i18n instance.
    
    Args:
        language: Language code
        
    Returns:
        I18nManager instance
    """
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18nManager(language)
    return _i18n_instance


def set_language(language: str) -> None:
    """
    Set global language.
    
    Args:
        language: Language code
    """
    get_i18n().set_language(language)
