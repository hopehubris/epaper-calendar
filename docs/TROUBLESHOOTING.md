# E-Paper Calendar Dashboard - Troubleshooting Guide

Solutions for common issues during setup and deployment.

## Quick Diagnostics

### Status Check Command
```bash
# Run this to check system health:
python src/main.py --status
```

## Development Machine Setup

### Python Installation Issues

**Problem**: "Python 3.8+ not found"
```bash
# Solution: Install Python 3.9 or newer
python3 --version  # Check version
# If older, install via Homebrew:
brew install python@3.9
```

**Problem**: `venv` creation fails
```bash
# Solution: Install venv package
python3 -m pip install --upgrade venv
# Then try again:
python3 -m venv venv
```

**Problem**: Virtual environment won't activate
```bash
# Solution: Check shell and source file
source venv/bin/activate  # for bash/zsh
# or
. venv/bin/activate  # alternative syntax
# Verify activation:
which python  # should show venv path
```

### Dependency Issues

**Problem**: `pip install` fails with permission error
```bash
# Solution: Use user installation
pip install --user -r requirements.txt
# Or ensure venv is activated:
source venv/bin/activate
pip install -r requirements.txt
```

**Problem**: Pillow/PIL installation fails (macOS)
```bash
# Solution: Install required development tools
xcode-select --install
pip install Pillow  # retry

# If still fails, try:
brew install libjpeg
pip install --force-reinstall Pillow
```

**Problem**: Google API library won't install
```bash
# Solution: Ensure you have pip upgraded
python -m pip install --upgrade pip
pip install google-api-python-client google-auth-oauthlib
```

## OAuth Setup Issues

### Credentials File Problems

**Problem**: "credentials.json not found"
```bash
# Solution: Download from Google Cloud Console
# 1. Go to https://console.cloud.google.com/
# 2. Select your project
# 3. Go to Credentials
# 4. Click your OAuth 2.0 Client ID (Desktop app)
# 5. Click Download button (⬇️)
# 6. Rename and place file:
mv ~/Downloads/client_secret_*.json ./credentials.json
```

**Problem**: "Invalid credentials format"
```bash
# Solution: Verify credentials are valid JSON
python -c "import json; json.load(open('credentials.json'))"
# If error, re-download from Google Cloud Console

# Check file is not empty:
wc -c credentials.json  # should be > 500 bytes
```

### OAuth Token Generation

**Problem**: "Browser won't open for OAuth authorization"
```bash
# Solution: Use headless mode
python scripts/setup_oauth.py --generate --no-webbrowser
# Copy the URL shown, paste in browser
# Enter authorization code when prompted
```

**Problem**: "Permission denied" or "redirect_uri_mismatch"
```bash
# Solution: Verify Desktop client type in Google Cloud Console
# 1. Go to Credentials
# 2. Check your OAuth client type is "Desktop application"
# 3. If wrong type, delete and recreate:
   rm token.json
   python scripts/setup_oauth.py --generate
```

**Problem**: OAuth token keeps being requested
```bash
# Solution: Check token.json exists and is valid
ls -la token.json  # should exist and be > 100 bytes
# If corrupted, regenerate:
rm token.json
python scripts/setup_oauth.py --generate
```

### Calendar ID Issues

**Problem**: "No events showing despite OAuth working"
```bash
# Solution: Verify calendar IDs in .env
# First, list available calendars:
python -c "
from src.calendar_fetcher import CalendarFetcher
fetcher = CalendarFetcher()
calendars = fetcher.list_available_calendars()
for cal_id, name in calendars.items():
    print(f'{name}: {cal_id}')
"

# Then update .env with correct IDs:
nano .env
# ASHI_CALENDAR_ID=correct-ashi-id@gmail.com
# SINDI_CALENDAR_ID=correct-sindi-id@gmail.com

# Restart app
python src/main.py
```

**Problem**: "Calendar not accessible" error
```bash
# Solution: Verify calendar sharing
# 1. On person's calendar: Settings → Share
# 2. Ensure calendar is not private
# 3. Or share explicitly with your account

# Then refresh OAuth:
python scripts/setup_oauth.py --refresh
python src/main.py
```

## Local Testing Issues

### Display Rendering

**Problem**: `test_display.py` fails with PIL error
```bash
# Solution: Verify Pillow installation
python -c "from PIL import Image; print(PIL.__version__)"
# If fails:
pip install --upgrade Pillow

# For macOS specific issues:
brew install libjpeg libpng
pip install --force-reinstall Pillow
```

**Problem**: Generated image is blank or wrong colors
```bash
# Solution: Check color mode configuration
nano .env
# Ensure: DISPLAY_COLOR_MODE=red  (or bw)

# Then regenerate:
python scripts/test_display.py
open test_display.png  # or view in image viewer
```

**Problem**: "Output file not created"
```bash
# Solution: Check write permissions
touch test_display.png  # verify writeable
# If error, check:
pwd  # current directory
ls -la . | head -5  # permissions

# Run with explicit output path:
python scripts/test_display.py --output /tmp/test.png
```

### Cache Issues

**Problem**: "Cache database corrupted"
```bash
# Solution: Delete and recreate
rm events_cache.db
python src/main.py  # recreates on next run

# Verify:
sqlite3 events_cache.db ".tables"
```

**Problem**: "Events not being cached"
```bash
# Solution: Check cache is being written
# During run:
python src/main.py --debug
# Then:
sqlite3 events_cache.db "SELECT COUNT(*) FROM events;"
```

**Problem**: "Can't access database file"
```bash
# Solution: Check permissions
ls -la events_cache.db
# If permission error:
chmod 664 events_cache.db
# Or delete and recreate:
rm events_cache.db
python src/main.py
```

## Raspberry Pi Deployment

### SSH Connection

**Problem**: "Connection refused"
```bash
# Solution: Verify RPi is on network
# On RPi:
ifconfig wlan0  # check IP address
sudo systemctl restart ssh

# From dev machine:
ping 192.168.1.xxx  # replace with actual IP
ssh pi@192.168.1.xxx  # try connection
```

**Problem**: "Permission denied (publickey)"
```bash
# Solution: Use password instead of key
ssh -o PubkeyAuthentication=no pi@192.168.1.xxx
# Default password: raspberry

# Or set up SSH key:
ssh-copy-id pi@192.168.1.xxx
```

**Problem**: rsync fails during deployment
```bash
# Solution: Verify rsync is installed on RPi
ssh pi@192.168.1.xxx "which rsync"
# If not found:
ssh pi@192.168.1.xxx "sudo apt-get install -y rsync"

# Then retry deployment:
bash scripts/deploy.sh pi 192.168.1.xxx
```

### Python Environment on RPi

**Problem**: "Python 3.8+ not found on RPi"
```bash
# Solution: Install Python
ssh pi@192.168.1.xxx
sudo apt-get update
sudo apt-get install -y python3.9 python3.9-venv python3.9-dev

# Verify:
python3.9 --version
```

**Problem**: pip install fails on RPi
```bash
# Solution: Install build dependencies
ssh pi@192.168.1.xxx
sudo apt-get install -y build-essential python3-dev

# For Pillow specifically:
sudo apt-get install -y libjpeg-dev zlib1g-dev

# Retry pip install:
cd /home/pi/epaper-calendar
source venv/bin/activate
pip install -r requirements.txt
```

**Problem**: Virtual environment stuck/corrupted
```bash
# Solution: Recreate venv
ssh pi@192.168.1.xxx
cd /home/pi/epaper-calendar
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### GPIO & Display Hardware

**Problem**: "SPI not enabled"
```bash
# Solution: Enable via raspi-config
ssh pi@192.168.1.xxx
sudo raspi-config
# → Interfacing Options → SPI → Yes → Finish

# Verify:
ls /dev/spidev*  # should show spidev devices
```

**Problem**: "GPIO access denied"
```bash
# Solution: Add pi user to gpio group
ssh pi@192.168.1.xxx
sudo usermod -a -G gpio pi
sudo usermod -a -G spi pi

# Then logout and back in for changes to take effect
exit
ssh pi@192.168.1.xxx
```

**Problem**: "Display not responding"
```bash
# Solution: Check hardware connections
# 1. Verify SPI cable connected
# 2. Check GPIO pins match configuration
# 3. Test power supply (5V for display)

# From RPi:
python -c "from src.waveshare_driver import WaveshareDriver; d = WaveshareDriver(); print('OK')"
```

**Problem**: "Display shows garbage/corrupted image"
```bash
# Solution: Reset display and re-run
ssh pi@192.168.1.xxx
# Disconnect power to display for 5 seconds, reconnect

# Then:
systemctl restart epaper-calendar
journalctl -u epaper-calendar -f
```

### Systemd Service Issues

**Problem**: "Service won't start"
```bash
# Solution: Check service logs
ssh pi@192.168.1.xxx
journalctl -u epaper-calendar -n 50 --no-pager

# Manual test:
cd /home/pi/epaper-calendar
source venv/bin/activate
python src/main.py

# Check for errors
```

**Problem**: "Service disabled after reboot"
```bash
# Solution: Enable service
ssh pi@192.168.1.xxx
sudo systemctl enable epaper-calendar
sudo systemctl enable epaper-calendar.timer

# Verify:
sudo systemctl is-enabled epaper-calendar
```

**Problem**: "Timer not triggering updates"
```bash
# Solution: Check timer status
ssh pi@192.168.1.xxx
sudo systemctl status epaper-calendar.timer
sudo systemctl list-timers epaper-calendar*

# Manual trigger for testing:
sudo systemctl start epaper-calendar

# Check logs:
journalctl -u epaper-calendar -f
```

**Problem**: "Permission denied writing to log file"
```bash
# Solution: Fix log directory
ssh pi@192.168.1.xxx
sudo mkdir -p /var/log/epaper-calendar
sudo chown pi:pi /var/log/epaper-calendar
sudo chmod 755 /var/log/epaper-calendar

# Restart service:
sudo systemctl restart epaper-calendar
```

## Network & Connectivity

**Problem**: "Network timeout during API calls"
```bash
# Solution: Check network connectivity
ssh pi@192.168.1.xxx
ping 8.8.8.8  # test internet
curl https://www.google.com  # test HTTPS

# Check DNS:
nslookup www.google.com
cat /etc/resolv.conf
```

**Problem**: "API calls work locally but not on RPi"
```bash
# Solution: Check certificate chain on RPi
ssh pi@192.168.1.xxx
python -c "import ssl; print(ssl.create_default_context().check_hostname)"

# Install certificates if missing:
sudo apt-get install -y ca-certificates
sudo update-ca-certificates
```

**Problem**: "Firewall blocking API access"
```bash
# Solution: Check firewall rules
ssh pi@192.168.1.xxx
sudo iptables -L -n | grep 443

# If port 443 blocked, allow:
sudo iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A OUTPUT -p tcp --dport 80 -j ACCEPT
```

## Performance Issues

**Problem**: "Updates take too long (>30 seconds)"
```bash
# Solution: Profile the update
ssh pi@192.168.1.xxx
cd /home/pi/epaper-calendar
source venv/bin/activate
python -m cProfile src/main.py

# Look for slow components
# Common causes:
# - Network latency (slow WiFi)
# - Slow cache queries (run maintenance)
# - GPIO issues (display communication)
```

**Problem**: "High CPU usage"
```bash
# Solution: Check what's consuming CPU
ssh pi@192.168.1.xxx
top -b -n 1 | head -20
# Look for python processes

# Check if multiple instances running:
pgrep -af epaper-calendar

# Kill duplicates if found:
pkill -f "python src/main.py"
sudo systemctl restart epaper-calendar
```

**Problem**: "RPi overheating"
```bash
# Solution: Monitor temperature
ssh pi@192.168.1.xxx
vcgencmd measure_temp

# If consistently >70°C:
# 1. Check heatsink installed
# 2. Verify adequate airflow
# 3. Reduce update frequency:
nano .env
# UPDATE_INTERVAL=1800  (30 minutes instead of 15)
```

## Data Issues

**Problem**: "Same events shown repeatedly"
```bash
# Solution: Clear and rebuild cache
ssh pi@192.168.1.xxx
cd /home/pi/epaper-calendar
source venv/bin/activate
rm events_cache.db
python src/main.py
```

**Problem**: "Events missing from display"
```bash
# Solution: Check calendar sync
# 1. Verify events exist in Google Calendar
# 2. Check calendar IDs:
python -c "
from src.config import Config
cfg = Config()
print(f'Ashi: {cfg.ASHI_CALENDAR_ID}')
print(f'Sindi: {cfg.SINDI_CALENDAR_ID}')
"

# 3. Manually fetch:
python -c "
from src.calendar_fetcher import CalendarFetcher
fetcher = CalendarFetcher()
events = fetcher.fetch_events('ashi@gmail.com', days=42)
print(f'Found {len(events)} events')
for e in events[:3]:
    print(f'- {e[\"summary\"]}: {e[\"start\"]}')
"
```

**Problem**: "Old events still showing"
```bash
# Solution: Run cache cleanup
ssh pi@192.168.1.xxx
cd /home/pi/epaper-calendar
source venv/bin/activate
sqlite3 events_cache.db "DELETE FROM events WHERE start_time < datetime('now', '-60 days');"
```

## Debugging Tools

### Enable Debug Logging

```bash
# On development machine:
LOG_LEVEL=DEBUG python src/main.py

# On RPi:
ssh pi@192.168.1.xxx
sudo systemctl stop epaper-calendar
cd /home/pi/epaper-calendar
source venv/bin/activate
LOG_LEVEL=DEBUG python src/main.py 2>&1 | tee /tmp/debug.log
```

### Check Configuration

```bash
python src/config.py
# Shows all loaded configuration
```

### Inspect Cache Database

```bash
sqlite3 events_cache.db

# List tables:
.tables

# Count events:
SELECT COUNT(*) FROM events;

# Show latest events:
SELECT summary, start_time FROM events ORDER BY start_time DESC LIMIT 10;

# Check cache metadata:
SELECT * FROM cache_metadata;
```

### Test Components in Isolation

```bash
# Test calendar fetch:
python -c "from src.calendar_fetcher import CalendarFetcher; CalendarFetcher().test_fetch()"

# Test rendering:
python scripts/test_display.py

# Test cache:
python -m pytest tests/test_cache.py -v

# Test config:
python -m pytest tests/test_config.py -v
```

## Getting Help

### Collect Debug Information

When reporting issues, provide:
```bash
# System info
python --version
pip list | grep -E "google|PIL|python-dateutil"

# Configuration (redact sensitive data)
cat .env | grep -v TOKEN | grep -v CREDENTIALS

# Recent logs
journalctl -u epaper-calendar -n 100 --no-pager
# OR
tail -100 /var/log/epaper-calendar/calendar.log

# Display test output
python scripts/test_display.py
ls -la test_display.png
```

### Useful Commands Reference

```bash
# Check Python and dependencies
python3 --version
python3 -m pip list

# Test import of key modules
python3 -c "import google.auth; print('Google Auth OK')"
python3 -c "from PIL import Image; print('PIL OK')"

# List available calendars
python3 src/calendar_fetcher.py --list-calendars

# Manual calendar fetch
python3 src/calendar_fetcher.py --fetch ashi@gmail.com

# Generate test display
python3 scripts/test_display.py

# Run full update cycle
python3 src/main.py

# Check systemd service
systemctl status epaper-calendar
journalctl -u epaper-calendar -f
```

## Still Stuck?

1. **Check the logs first**: `journalctl -u epaper-calendar -f`
2. **Test in isolation**: Run `python src/main.py` manually
3. **Verify configuration**: `cat .env | grep -v "^#"`
4. **Check credentials**: `python scripts/setup_oauth.py --verify`
5. **Review documentation**: Start with QUICKSTART.md or DEPLOYMENT.md

---

**Version**: 0.1.0
**Last Updated**: February 2026
