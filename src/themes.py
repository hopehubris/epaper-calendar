"""
Theme system for color palettes and layout configurations.
"""
import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class ColorPalette:
    """Color palette definition."""
    black: Tuple[int, int, int] = (0, 0, 0)
    white: Tuple[int, int, int] = (255, 255, 255)
    red: Tuple[int, int, int] = (255, 0, 0)
    grey: Tuple[int, int, int] = (200, 200, 200)
    light_grey: Tuple[int, int, int] = (230, 230, 230)
    dark_grey: Tuple[int, int, int] = (100, 100, 100)
    
    def to_bw(self, color: Tuple[int, int, int]) -> int:
        """Convert RGB to B&W (0 or 1)."""
        avg = (color[0] + color[1] + color[2]) // 3
        return 0 if avg < 128 else 1


class Theme:
    """Display theme with colors and typography."""

    def __init__(self, name: str, palette: ColorPalette, layout: Dict = None):
        """
        Initialize theme.
        
        Args:
            name: Theme name
            palette: Color palette
            layout: Layout configuration
        """
        self.name = name
        self.palette = palette
        self.layout = layout or {}

    def get_color(self, key: str, color_mode: str = "rgb"):
        """
        Get color for display mode.
        
        Args:
            key: Color key (e.g., 'black', 'red')
            color_mode: Display mode ('rgb', 'bw')
            
        Returns:
            Color value
        """
        color = getattr(self.palette, key, self.palette.black)
        
        if color_mode == "bw":
            return self.palette.to_bw(color)
        
        return color


# Light theme
LIGHT_PALETTE = ColorPalette(
    black=(0, 0, 0),
    white=(255, 255, 255),
    red=(200, 0, 0),
    grey=(220, 220, 220),
    light_grey=(240, 240, 240),
    dark_grey=(80, 80, 80),
)

LIGHT_THEME = Theme(
    "light",
    LIGHT_PALETTE,
    {
        "background": "white",
        "text": "black",
        "accent": "red",
        "border_width": 1,
        "padding": 10,
    }
)

# Dark theme
DARK_PALETTE = ColorPalette(
    black=(255, 255, 255),  # Inverted for dark display
    white=(0, 0, 0),
    red=(255, 100, 100),
    grey=(80, 80, 80),
    light_grey=(120, 120, 120),
    dark_grey=(200, 200, 200),
)

DARK_THEME = Theme(
    "dark",
    DARK_PALETTE,
    {
        "background": "black",
        "text": "white",
        "accent": "red",
        "border_width": 2,
        "padding": 12,
    }
)

# High contrast theme (for accessibility)
HIGH_CONTRAST_PALETTE = ColorPalette(
    black=(0, 0, 0),
    white=(255, 255, 255),
    red=(255, 0, 0),
    grey=(128, 128, 128),
    light_grey=(192, 192, 192),
    dark_grey=(64, 64, 64),
)

HIGH_CONTRAST_THEME = Theme(
    "high_contrast",
    HIGH_CONTRAST_PALETTE,
    {
        "background": "white",
        "text": "black",
        "accent": "red",
        "border_width": 3,
        "padding": 15,
        "font_sizes": {
            "small": 11,
            "medium": 13,
            "large": 15,
        }
    }
)

# E-paper theme (optimized for e-paper displays)
EPAPER_PALETTE = ColorPalette(
    black=(0, 0, 0),
    white=(255, 255, 255),
    red=(255, 0, 0),
    grey=(200, 200, 200),
    light_grey=(230, 230, 230),
    dark_grey=(100, 100, 100),
)

EPAPER_THEME = Theme(
    "epaper",
    EPAPER_PALETTE,
    {
        "background": "white",
        "text": "black",
        "accent": "red",
        "border_width": 2,
        "padding": 8,
        "dithering": True,
        "refresh_rate": "slow",
    }
)


class ThemeManager:
    """Manages themes and color schemes."""

    THEMES = {
        "light": LIGHT_THEME,
        "dark": DARK_THEME,
        "high_contrast": HIGH_CONTRAST_THEME,
        "epaper": EPAPER_THEME,
    }

    def __init__(self, theme_name: str = "light"):
        """
        Initialize theme manager.
        
        Args:
            theme_name: Theme name
        """
        self.current_theme = self.THEMES.get(theme_name, LIGHT_THEME)
        logger.info(f"Theme set to: {self.current_theme.name}")

    def set_theme(self, name: str) -> bool:
        """
        Set active theme.
        
        Args:
            name: Theme name
            
        Returns:
            True if successful, False if theme not found
        """
        if name in self.THEMES:
            self.current_theme = self.THEMES[name]
            logger.info(f"Theme changed to: {name}")
            return True
        
        logger.warning(f"Theme not found: {name}")
        return False

    def get_color(self, key: str, color_mode: str = "rgb"):
        """
        Get color from current theme.
        
        Args:
            key: Color key
            color_mode: Display mode
            
        Returns:
            Color value
        """
        return self.current_theme.get_color(key, color_mode)

    def get_layout(self, key: str, default = None):
        """
        Get layout configuration value.
        
        Args:
            key: Layout key
            default: Default value
            
        Returns:
            Layout value or default
        """
        return self.current_theme.layout.get(key, default)

    def list_themes(self) -> list[str]:
        """
        List available themes.
        
        Returns:
            List of theme names
        """
        return list(self.THEMES.keys())

    def register_theme(self, name: str, theme: Theme) -> None:
        """
        Register custom theme.
        
        Args:
            name: Theme name
            theme: Theme instance
        """
        self.THEMES[name] = theme
        logger.info(f"Registered custom theme: {name}")


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager(theme_name: str = "light") -> ThemeManager:
    """
    Get global theme manager instance.
    
    Args:
        theme_name: Initial theme name
        
    Returns:
        ThemeManager instance
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager(theme_name)
    return _theme_manager


def set_theme(name: str) -> bool:
    """
    Set global theme.
    
    Args:
        name: Theme name
        
    Returns:
        True if successful
    """
    return get_theme_manager().set_theme(name)


def get_color(key: str, color_mode: str = "rgb"):
    """
    Get color from global theme.
    
    Args:
        key: Color key
        color_mode: Display mode
        
    Returns:
        Color value
    """
    return get_theme_manager().get_color(key, color_mode)
