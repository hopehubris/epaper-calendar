"""
Font management with fallback support for different platforms.
"""
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Tuple
from PIL import ImageFont


logger = logging.getLogger(__name__)


class FontManager:
    """Manages font loading with platform-specific fallbacks."""

    # Font search paths by platform
    FONT_PATHS = {
        "macos": [
            "/System/Library/Fonts",
            "/Library/Fonts",
            "~/Library/Fonts",
        ],
        "linux": [
            "/usr/share/fonts/truetype",
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            "~/.local/share/fonts",
        ],
        "windows": [
            "C:\\Windows\\Fonts",
            "C:\\Program Files\\fonts",
        ],
        "rpi": [
            "/usr/share/fonts/truetype",
            "/usr/share/fonts",
        ],
    }

    # Font priority list
    FONT_PREFERENCES = [
        ("dejavu", "DejaVuSans"),
        ("liberation", "LiberationSans"),
        ("freesans", "FreeSans"),
        ("noto", "NotoSans"),
        ("ubuntu", "Ubuntu"),
        ("sans", ""),  # Generic sans-serif
    ]

    def __init__(self):
        """Initialize font manager."""
        self.fonts: Dict[str, ImageFont.FreeTypeFont] = {}
        self.loaded_fonts: Dict[str, Path] = {}
        self._detect_platform()

    def _detect_platform(self) -> None:
        """Detect platform and set search paths."""
        import sys
        
        if sys.platform == "darwin":
            self.platform = "macos"
        elif sys.platform == "win32":
            self.platform = "windows"
        elif sys.platform == "linux":
            # Check if running on RPi
            try:
                with open("/proc/cpuinfo") as f:
                    if "BCM" in f.read():  # BCM = Broadcom (RPi chipset)
                        self.platform = "rpi"
                    else:
                        self.platform = "linux"
            except:
                self.platform = "linux"
        else:
            self.platform = "linux"  # Default
        
        logger.info(f"Detected platform: {self.platform}")

    def _find_font_file(self, font_name: str, style: str = "") -> Optional[Path]:
        """
        Find font file on system.
        
        Args:
            font_name: Font name (e.g., 'DejaVuSans')
            style: Font style ('Bold', 'Italic', etc.)
            
        Returns:
            Path to font file or None
        """
        search_paths = self.FONT_PATHS.get(self.platform, self.FONT_PATHS["linux"])
        
        # Expand home directory
        search_paths = [Path(p).expanduser() for p in search_paths]
        
        # Try various font file patterns
        patterns = [
            f"{font_name}{style}.ttf",
            f"{font_name}-{style}.ttf",
            f"{font_name.lower()}{style.lower()}.ttf",
            f"{font_name.lower()}-{style.lower()}.ttf",
        ]
        
        for path in search_paths:
            if not path.exists():
                continue
            
            for pattern in patterns:
                font_file = path / pattern
                if font_file.exists():
                    logger.debug(f"Found font: {font_file}")
                    return font_file
        
        return None

    def _find_fallback_font(self) -> Optional[Path]:
        """
        Find best available fallback font.
        
        Returns:
            Path to fallback font or None
        """
        for font_name, _ in self.FONT_PREFERENCES:
            font_file = self._find_font_file(font_name)
            if font_file:
                logger.info(f"Using fallback font: {font_file}")
                return font_file
        
        return None

    def load_font(self, font_name: str, size: int = 12, style: str = "") -> ImageFont.FreeTypeFont:
        """
        Load font with fallback support.
        
        Args:
            font_name: Font name (e.g., 'DejaVuSans')
            size: Font size in pixels
            style: Font style ('Bold', 'Italic')
            
        Returns:
            PIL ImageFont object
        """
        cache_key = f"{font_name}_{size}_{style}"
        
        # Return cached font if available
        if cache_key in self.fonts:
            return self.fonts[cache_key]

        # Try to find and load the requested font
        font_file = self._find_font_file(font_name, style)
        
        # If not found, try fallbacks
        if not font_file:
            logger.warning(f"Font not found: {font_name}, trying fallback")
            font_file = self._find_fallback_font()
        
        # Load font or use default
        try:
            if font_file:
                font = ImageFont.truetype(str(font_file), size)
                self.loaded_fonts[cache_key] = font_file
                logger.info(f"Loaded font: {font_file} (size={size})")
            else:
                logger.warning("No TrueType fonts found, using default")
                font = ImageFont.load_default()
        except Exception as e:
            logger.error(f"Failed to load font {font_file}: {e}")
            font = ImageFont.load_default()

        self.fonts[cache_key] = font
        return font

    def get_font(self, size: int = 12, weight: str = "normal") -> ImageFont.FreeTypeFont:
        """
        Get font with size and weight.
        
        Args:
            size: Font size
            weight: Font weight ('normal', 'bold')
            
        Returns:
            PIL ImageFont object
        """
        # Map weight to font style
        style = "Bold" if weight == "bold" else ""
        return self.load_font("DejaVuSans", size, style)

    def get_fonts_dict(self) -> Dict[str, ImageFont.FreeTypeFont]:
        """
        Get dictionary of common font sizes.
        
        Returns:
            Dictionary with keys like 'tiny', 'small', 'medium', 'large', 'huge'
        """
        return {
            "tiny": self.get_font(8),
            "small": self.get_font(10),
            "medium": self.get_font(12),
            "large": self.get_font(14),
            "xlarge": self.get_font(16),
            "huge": self.get_font(20),
            "bold": self.get_font(12, "bold"),
            "large_bold": self.get_font(14, "bold"),
        }

    def list_available_fonts(self) -> list[str]:
        """
        List available fonts on system.
        
        Returns:
            List of available font names
        """
        fonts = set()
        search_paths = self.FONT_PATHS.get(self.platform, self.FONT_PATHS["linux"])
        
        for path_str in search_paths:
            path = Path(path_str).expanduser()
            if not path.exists():
                continue
            
            # Find all .ttf files
            for ttf_file in path.rglob("*.ttf"):
                fonts.add(ttf_file.stem)
        
        return sorted(list(fonts))


# Global font manager instance
_font_manager: Optional[FontManager] = None


def get_font_manager() -> FontManager:
    """
    Get global font manager instance.
    
    Returns:
        FontManager instance
    """
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager


def get_font(size: int = 12, weight: str = "normal") -> ImageFont.FreeTypeFont:
    """
    Get font from global manager.
    
    Args:
        size: Font size
        weight: Font weight ('normal' or 'bold')
        
    Returns:
        PIL ImageFont object
    """
    return get_font_manager().get_font(size, weight)


def load_font(font_name: str, size: int = 12, style: str = "") -> ImageFont.FreeTypeFont:
    """
    Load specific font from global manager.
    
    Args:
        font_name: Font name
        size: Font size
        style: Font style
        
    Returns:
        PIL ImageFont object
    """
    return get_font_manager().load_font(font_name, size, style)
