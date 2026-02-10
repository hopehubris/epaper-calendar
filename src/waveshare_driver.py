"""Waveshare 7.5" e-paper display driver."""

import logging
import sys
import os
from pathlib import Path
from PIL import Image

logger = logging.getLogger(__name__)

# Try to import Waveshare library (must be in sys.path)
HAS_HARDWARE = False
EPD = None

# Add Waveshare library path if it exists
waveshare_paths = [
    '/home/ashisheth/e-Paper/RaspberryPi_JetsonNano/python/lib',
    '/root/e-Paper/RaspberryPi_JetsonNano/python/lib',
    '/usr/local/lib/waveshare_epd',
]

for path in waveshare_paths:
    if os.path.exists(path):
        sys.path.insert(0, path)
        logger.info(f"Added Waveshare path: {path}")
        break

# Try to import the actual Waveshare 7.5" V2 display
# NOTE: This may fail on RPi 5 due to GPIO initialization issues during import
try:
    from waveshare_epd import epd7in5b_V2
    EPD = epd7in5b_V2
    HAS_HARDWARE = True
    logger.info("✅ Waveshare epd7in5b_V2 library found and loaded")
except (ImportError, ModuleNotFoundError) as e:
    logger.warning(f"Waveshare library import failed (module not found): {e}")
    HAS_HARDWARE = False
except Exception as e:
    # GPIO initialization failure or other runtime error
    logger.warning(f"Waveshare library import failed (GPIO/runtime): {e}")
    logger.info("This typically happens on RPi 5 where GPIO setup fails during import")
    HAS_HARDWARE = False
    EPD = None

class WaveshareDriver:
    """Driver for Waveshare 7.5" red/greyscale e-paper display using official library."""
    
    # Display specifications
    WIDTH = 800
    HEIGHT = 480
    
    def __init__(self):
        """Initialize Waveshare driver using official library."""
        self.epd = None
        self.initialized = False
        self.is_hardware = HAS_HARDWARE
        
        if not HAS_HARDWARE:
            logger.info("Waveshare library not available, running in simulation mode")
            return
        
        try:
            self._initialize_hardware()
        except Exception as e:
            logger.warning(f"Hardware initialization failed: {e}")
            logger.info("Falling back to simulation mode")
            self.is_hardware = False
            self.initialized = False
    
    def _initialize_hardware(self):
        """Initialize Waveshare display using official library."""
        if not HAS_HARDWARE or EPD is None:
            logger.info("Waveshare library not available")
            return
        
        try:
            # Use the official Waveshare library
            self.epd = EPD.EPD()
            logger.info("Initializing Waveshare EPD...")
            self.epd.init()
            logger.info("✅ Waveshare display initialized successfully")
            self.initialized = True
            self.is_hardware = True
        except Exception as e:
            logger.error(f"Failed to initialize Waveshare display: {e}")
            self.initialized = False
            self.is_hardware = False
            raise
    
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
            
            logger.info(f"Displaying {image.size} image ({image.mode})")
            
            if not self.is_hardware or not self.initialized:
                logger.info("Hardware not available or not initialized, skipping display")
                return True
            
            try:
                # Waveshare 7.5" V2 requires two separate 1-bit images:
                # - First buffer: BLACK channel (text, outlines)
                # - Second buffer: RED channel (accents, highlights)
                logger.info(f"Processing image for dual-channel display...")
                
                # Ensure RGB
                if image.mode != "RGB":
                    image = image.convert("RGB")
                
                # Simple approach: Convert to 1-bit grayscale for black channel
                # and create empty red channel (all white = no red)
                logger.info("Creating black channel from RGB...")
                black_image = image.convert("1")  # Converts to 1-bit B&W
                
                logger.info("Creating red channel (empty)...")
                red_image = Image.new("1", (self.WIDTH, self.HEIGHT), 255)  # All white = no red pixels
                
                logger.info("Creating Waveshare buffers...")
                black_buffer = self.epd.getbuffer(black_image)
                red_buffer = self.epd.getbuffer(red_image)
                logger.info(f"Buffers ready: black={len(black_buffer)} bytes, red={len(red_buffer)} bytes")
                
                logger.info("Sending to display... (this may take 5-10 seconds)")
                import time
                
                try:
                    # Display refresh can take several seconds on e-paper
                    # The Waveshare hardware shows a progress indicator during refresh
                    start_time = time.time()
                    self.epd.display(black_buffer, red_buffer)
                    elapsed = time.time() - start_time
                    logger.info(f"Display refresh completed in {elapsed:.1f} seconds")
                    
                    time.sleep(1)  # Give display time to finish processing
                    logger.info("✅ Image sent to Waveshare display (black + red channels)")
                    return True
                except Exception as e:
                    logger.error(f"Display refresh failed: {e}")
                    return False
            except TypeError as te:
                # Try with just black buffer if red not supported
                logger.warning(f"TypeError on display: {te}")
                if "missing" in str(te) and "imagered" in str(te):
                    logger.info("Red channel not required, trying single buffer...")
                    if image.mode != "1":
                        image = image.convert("1")
                    self.epd.display(self.epd.getbuffer(image))
                    logger.info("✅ Image sent to Waveshare display (single buffer)")
                    return True
                else:
                    raise
            
        except Exception as e:
            logger.error(f"Display error: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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
            if self.epd:
                self.epd.sleep()
                logger.info("Display entered sleep mode")
        except Exception as e:
            logger.debug(f"Cleanup note: {e}")
    
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
    if use_hardware and HAS_HARDWARE:
        driver = WaveshareDriver()
        if driver.is_hardware and driver.initialized:
            logger.info("✅ Using Waveshare hardware display")
            return driver
        else:
            logger.info("Waveshare hardware failed to initialize, falling back to simulator")
            return DisplaySimulator()
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
