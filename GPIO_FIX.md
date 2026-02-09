# GPIO Hardware Fix Guide

## Current Status
✅ **App is RUNNING** in simulation mode on RPi  
⚠️ **GPIO/SPI not detected** (still fetching calendars successfully)

## Why This Happened

The app tried to import `RPi.GPIO` but it failed. This is normal on fresh RPi installs. The app gracefully falls back to **simulation mode** (rendering to images instead of hardware).

## Fix: Install Waveshare Hardware Support

### Option A: Install Official Waveshare Library (RECOMMENDED)

Run on RPi:

```bash
cd /home/ashisheth/gh_repos/epaper-calendar
source venv/bin/activate

# Install official Waveshare library
pip install RPi.GPIO spidev --break-system-packages

# Verify installation
python3 -c "import RPi.GPIO; print('✅ RPi.GPIO installed')"
python3 -c "import spidev; print('✅ spidev installed')"

# Test hardware detection
python3 << 'PYEOF'
import sys
sys.path.insert(0, 'src')
from waveshare_driver import WaveshareDriver
driver = WaveshareDriver()
print(f"Hardware available: {driver.is_hardware}")
print(f"Initialized: {driver.initialized}")
PYEOF
```

### Option B: Use Waveshare Official SDK

If GPIO still fails, use the official Waveshare SDK:

```bash
cd /tmp
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python/
pip install -r requirements.txt --break-system-packages
cd /home/ashisheth/gh_repos/epaper-calendar
# Update src/waveshare_driver.py to import from downloaded SDK
```

### Option C: Check Hardware Connections

If GPIO installs but still fails, verify hardware:

```bash
# Check if SPI is enabled
sudo raspi-config

# Navigate to: 5 Interfacing Options > P4 SPI > Yes

# Verify SPI device exists
ls -la /dev/spidev*

# Check GPIO pins (should be accessible)
python3 -c "import RPi.GPIO; RPi.GPIO.setmode(RPi.GPIO.BCM); print('✅ GPIO working')"
```

## Testing After Fix

Once hardware is detected, restart the app:

```bash
cd /home/ashisheth/gh_repos/epaper-calendar
source venv/bin/activate
python3 src/main.py --debug
```

You should see:
```
✅ RPi.GPIO available
✅ GPIO initialized
✅ Hardware display ready
```

Instead of:
```
⚠️ RPi.GPIO not available (not on Raspberry Pi?)
ℹ️ GPIO not available, skipping hardware init
ℹ️ Running in simulation mode
```

## App Status During Fix

**Good news**: The app works perfectly in simulation mode:
- ✅ Calendars fetching normally
- ✅ Display rendering to images
- ✅ All features working
- ✅ Systemd timer will still work

**Once hardware fixed**:
- 🖥️ Images will render to actual e-paper display
- ⏰ Systemd will auto-update display every 15 minutes
- 🎨 Colors will show correctly on hardware

## Recommended Next Step

**Keep the app running as-is** while we:

1. SSH into RPi
2. Run `pip install RPi.GPIO spidev --break-system-packages`
3. Restart app with `python3 src/main.py --debug`
4. Verify hardware detection

This usually takes 5 minutes and the display will activate automatically.

---

**Questions?**
- App still running? ✅
- Calendars updating? ✅  
- Just need GPIO library? ✅

We'll fix the hardware in the next step.
