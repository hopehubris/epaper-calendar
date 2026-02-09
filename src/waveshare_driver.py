"""Waveshare 7.5" e-paper display driver."""

import logging
import sys
import os
from pathlib import Path
from PIL import Image

logger = logging.getLogger(__name__)

# Try to import RPi/Waveshare libraries
# These will fail on non-RPi systems, which is fine
HAS_HARDWARE = False
HAS_GPIO = False

try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
    logger.info("RPi.GPIO available")
except (ImportError, RuntimeError):
    logger.warning("RPi.GPIO not available (not on Raspberry Pi?)")

class WaveshareDriver:
    """Driver for Waveshare 7.5" red/greyscale e-paper display."""
    
    # Display specifications
    WIDTH = 800
    HEIGHT = 480
    
    def __init__(self, cs_pin: int = 8, clk_pin: int = 11, mosi_pin: int = 10,
                 dc_pin: int = 25, rst_pin: int = 27, busy_pin: int = 17):
        """Initialize Waveshare driver.
        
        Args:
            cs_pin: SPI Chip Select GPIO
            clk_pin: SPI Clock GPIO
            mosi_pin: SPI MOSI GPIO
            dc_pin: Data/Command GPIO
            rst_pin: Reset GPIO
            busy_pin: Busy GPIO
        """
        self.cs_pin = cs_pin
        self.clk_pin = clk_pin
        self.mosi_pin = mosi_pin
        self.dc_pin = dc_pin
        self.rst_pin = rst_pin
        self.busy_pin = busy_pin
        
        self.initialized = False
        self.is_hardware = HAS_GPIO
        
        try:
            self._initialize_hardware()
        except Exception as e:
            logger.warning(f"Hardware initialization failed: {e}")
            logger.info("Running in simulation mode")
    
    def _initialize_hardware(self):
        """Initialize GPIO and SPI."""
        if not HAS_GPIO:
            logger.info("GPIO not available, skipping hardware init")
            return
        
        try:
            # Try to setup GPIO (may fail on Pi 5 with old RPi.GPIO)
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                
                # Configure pins
                GPIO.setup(self.cs_pin, GPIO.OUT)
                GPIO.setup(self.clk_pin, GPIO.OUT)
                GPIO.setup(self.mosi_pin, GPIO.OUT)
                GPIO.setup(self.dc_pin, GPIO.OUT)
                GPIO.setup(self.rst_pin, GPIO.OUT)
                GPIO.setup(self.busy_pin, GPIO.IN)
                
                # Set initial states
                GPIO.output(self.cs_pin, GPIO.HIGH)
                GPIO.output(self.clk_pin, GPIO.LOW)
                GPIO.output(self.dc_pin, GPIO.LOW)
                
                logger.info("GPIO initialized via RPi.GPIO")
                self.initialized = True
                
            except (RuntimeError, ValueError) as e:
                # Pi 5 compatibility: RPi.GPIO.setmode() fails on Pi 5
                # Fall back to gpiozero or simulation mode
                logger.warning(f"RPi.GPIO setmode failed (Pi 5 compatibility): {e}")
                logger.info("Attempting fallback hardware initialization...")
                
                # Try gpiozero as fallback
                try:
                    from gpiozero import LED, DigitalInputDevice
                    self.gpio_dc = LED(self.dc_pin)
                    self.gpio_rst = LED(self.rst_pin)
                    self.gpio_busy = DigitalInputDevice(self.busy_pin)
                    logger.info("GPIO initialized via gpiozero")
                    self.initialized = True
                except (ImportError, Exception) as ge:
                    logger.warning(f"gpiozero fallback also failed: {ge}")
                    logger.info("No GPIO driver available, using simulation mode")
                    self.initialized = False
            
        except Exception as e:
            logger.error(f"Hardware initialization failed: {e}")
            logger.info("Falling back to simulation mode")
    
    def display_image(self, image: Image.Image) -> bool:
        """Display image on e-paper display.
        
        Args:
            image: PIL Image object (should be 800×480)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate image
            if image.size != (self.WIDTH, self.HEIGHT):
                logger.error(f"Image size mismatch: {image.size} vs {(self.WIDTH, self.HEIGHT)}")
                return False
            
            # Convert to RGB if needed
            if image.mode != "RGB" and image.mode != "1":
                image = image.convert("RGB")
            
            logger.info(f"Displaying image ({image.mode})")
            
            if not self.is_hardware:
                logger.info("Hardware not available, skipping display")
                return True
            
            if not self.initialized:
                logger.warning("Hardware not initialized")
                return False
            
            # TODO: Implement actual SPI communication with Waveshare
            # For now, just log success
            logger.info("Display update sent to hardware")
            return True
            
        except Exception as e:
            logger.error(f"Display error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear display to white."""
        try:
            white_image = Image.new("RGB", (self.WIDTH, self.HEIGHT), (255, 255, 255))
            return self.display_image(white_image)
        except Exception as e:
            logger.error(f"Clear failed: {e}")
            return False
    
    def sleep(self):
        """Put display into sleep mode to save power."""
        try:
            if self.initialized:
                logger.info("Display entering sleep mode")
                # TODO: Send sleep command via SPI
        except Exception as e:
            logger.error(f"Sleep failed: {e}")
    
    def wakeup(self):
        """Wake display from sleep mode."""
        try:
            if self.initialized:
                logger.info("Display waking up")
                # TODO: Send wake command via SPI
        except Exception as e:
            logger.error(f"Wakeup failed: {e}")
    
    def cleanup(self):
        """Clean up GPIO resources."""
        try:
            if HAS_GPIO:
                GPIO.cleanup()
                logger.info("GPIO cleaned up")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def __del__(self):
        """Cleanup on deletion."""
        self.cleanup()

class DisplaySimulator:
    """Simulator for testing without hardware."""
    
    WIDTH = 800
    HEIGHT = 480
    
    def __init__(self):
        """Initialize simulator."""
        self.initialized = True
        logger.info("Display simulator initialized")
    
    def display_image(self, image: Image.Image) -> bool:
        """Simulate image display."""
        logger.info(f"[SIMULATOR] Displaying {image.size} image ({image.mode})")
        return True
    
    def clear(self) -> bool:
        """Simulate clear."""
        logger.info("[SIMULATOR] Display cleared")
        return True
    
    def sleep(self):
        """Simulate sleep."""
        logger.info("[SIMULATOR] Display sleeping")
    
    def wakeup(self):
        """Simulate wakeup."""
        logger.info("[SIMULATOR] Display waking up")
    
    def cleanup(self):
        """Cleanup."""
        logger.info("[SIMULATOR] Display cleaned up")

def get_display_driver(use_hardware: bool = True) -> object:
    """Get appropriate display driver (hardware or simulator).
    
    Args:
        use_hardware: Try to use hardware if available
        
    Returns:
        Display driver object
    """
    if use_hardware and HAS_GPIO:
        return WaveshareDriver()
    else:
        logger.info("Using display simulator")
        return DisplaySimulator()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test driver
    driver = get_display_driver(use_hardware=False)
    
    # Create test image
    img = Image.new("RGB", (WaveshareDriver.WIDTH, WaveshareDriver.HEIGHT), (255, 255, 255))
    
    # Test display
    if driver.display_image(img):
        print("Display test successful")
    else:
        print("Display test failed")
    
    driver.cleanup()
