# Waveshare E-Paper Dashboard Deployment Guide (v0.2.0)

Complete guide for deploying the dashboard on Raspberry Pi with weather, multi-calendar support, and privacy modes.

## Quick Start (5 minutes)

### Prerequisites
- Raspberry Pi 3B+ or newer with Raspbian/Debian OS
- Waveshare e-paper display (7.5", 5.8", or similar)
- Internet connection
- Google account for OAuth

### Automated Setup
```bash
cd /tmp
git clone https://github.com/yourusername/epaper-calendar.git
cd epaper-calendar
bash scripts/setup_rpi.sh
```

The script will:
1. Install system dependencies
2. Clone repository
3. Setup Python virtual environment
4. Configure Google OAuth
5. Install systemd service + timer
6. Start 15-minute auto-update schedule

## Detailed Setup

### 1. System Preparation

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y \
    python3 python3-venv python3-pip \
    python3-spidev RPi.GPIO \
    git libopenjp2-7 libtiff5 libjasper1
```

### 2. Clone Repository

```bash
cd ~
git clone https://github.com/yourusername/epaper-calendar.git
cd epaper-calendar
```

### 3. Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install RPi.GPIO spidev
```

### 4. Google OAuth Setup

**Get credentials:**
1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Create new project
3. Enable Google Calendar API
4. Create OAuth 2.0 Desktop Application credentials
5. Download `credentials.json`
6. Place in project root: `epaper-calendar/credentials.json`

**Generate token:**
```bash
python3 scripts/setup_oauth.py
# Follow the prompts to authenticate
# Creates: token.json (keep secret!)
```

### 5. Configuration

Create `config/dashboard.yaml`:
```yaml
# Google Calendar
calendars:
  - email: ashi@gmail.com
    name: "Ashi Calendar"
    color: red
  - email: sindi@gmail.com
    name: "Sindi Calendar"
    color: black

# Weather (OpenWeatherMap)
weather:
  enabled: true
  api_key: "YOUR_API_KEY"  # Get from openweathermap.org
  location: "London"
  latitude: 51.5074
  longitude: -0.1278
  units: "metric"

# Display
display:
  width: 800
  height: 480
  color_mode: "red"  # "red" or "bw"
  template: "default"  # "default" or "weather"
  dpi: 150

# Privacy
privacy:
  mode: "none"  # "none", "xkcd", or "literature_clock"
  xkcd_seed: 42

# Internationalization
i18n:
  language: "en"  # "en", "de", "es", "fr"
  timezone: "Europe/London"

# Logging
logging:
  level: "INFO"
  file: "/var/log/epaper-dashboard.log"

# Cache
cache:
  ttl_hours: 1
  max_size: 1000

# API
openweather_api_key: "YOUR_API_KEY"
location: "London"
```

### 6. Test Display

```bash
# Activate environment
source venv/bin/activate

# Test rendering
python3 src/main.py --test

# Check output
ls -l test_display.png
```

### 7. Install Systemd Service

```bash
# Copy service files
sudo cp systemd/waveshare-dashboard.service /etc/systemd/system/
sudo cp systemd/waveshare-dashboard.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable waveshare-dashboard.service
sudo systemctl enable waveshare-dashboard.timer

# Start timer
sudo systemctl start waveshare-dashboard.timer
```

### 8. Verify Installation

```bash
# Check timer status
systemctl list-timers waveshare-dashboard.timer

# View service logs
sudo journalctl -u waveshare-dashboard.service -f

# Manual test
sudo systemctl start waveshare-dashboard.service
```

## Configuration Details

### Display Options

```yaml
display:
  width: 800
  height: 480
  color_mode: "red"  # Waveshare Red/Greyscale or "bw" for Black/White
  template: "default"  # "default", "weather", or "minimal"
  dpi: 150
  refresh_mode: "auto"  # "fast", "full", "auto"
```

### Weather API

**OpenWeatherMap:**
```yaml
weather:
  enabled: true
  api_key: "YOUR_API_KEY"  # Get free tier at openweathermap.org
  location: "London,UK"
  units: "metric"  # or "imperial"
  update_interval: 3600  # seconds
```

### Privacy Modes

**XKCD Cipher** - Substitution cipher for event titles:
```yaml
privacy:
  mode: "xkcd"
  xkcd_seed: 42
```

**Literature Clock** - Shows time with literary quotes:
```yaml
privacy:
  mode: "literature_clock"
```

**No Privacy**:
```yaml
privacy:
  mode: "none"
```

### Languages (i18n)

Supported: English (en), German (de), Spanish (es), French (fr)

```yaml
i18n:
  language: "de"  # Renders calendar in German
  timezone: "Europe/Berlin"
```

## Usage

### Manual Rendering

```bash
source venv/bin/activate
python3 src/main.py
```

### Command-line Options

```bash
# Test mode (renders to PNG without hardware)
python3 src/main.py --test --output test.png

# Specify config file
python3 src/main.py --config config/dashboard.yaml

# Force refresh (bypass cache)
python3 src/main.py --refresh

# Set privacy mode
python3 src/main.py --privacy xkcd

# Set language
python3 src/main.py --lang de
```

### Systemd Control

```bash
# Start service
sudo systemctl start waveshare-dashboard.service

# View logs (real-time)
sudo journalctl -u waveshare-dashboard.service -f

# View recent logs
sudo journalctl -u waveshare-dashboard.service -n 50

# Check timer schedule
systemctl status waveshare-dashboard.timer

# Manually trigger timer
sudo systemctl start waveshare-dashboard.timer

# Stop updates
sudo systemctl stop waveshare-dashboard.timer
```

## Troubleshooting

### Display Not Updating

```bash
# Check if timer is running
systemctl status waveshare-dashboard.timer

# View error logs
sudo journalctl -u waveshare-dashboard.service -f

# Manual test
cd ~/epaper-calendar
source venv/bin/activate
python3 src/main.py
```

### Google Calendar Issues

```bash
# Re-authenticate
rm token.json
python3 scripts/setup_oauth.py

# Check permissions
python3 -c "from src.calendar_fetcher import CalendarFetcher; CalendarFetcher({}).test_connection()"
```

### Weather Not Showing

```bash
# Verify API key
grep openweather_api_key config/dashboard.yaml

# Test weather API
python3 -c "from src.providers.weather.openweather import OpenWeatherMapProvider; import asyncio; asyncio.run(OpenWeatherMapProvider('YOUR_KEY', 'London').get_weather())"
```

### Memory/CPU Issues

```bash
# Check resource usage
ps aux | grep python3

# Limit CPU (update systemd service)
sudo systemctl edit waveshare-dashboard.service
# Add: CPUQuota=50%
```

### Performance Optimization

```bash
# Enable caching
cache:
  ttl_hours: 4  # Increase cache TTL

# Reduce update frequency
# Edit waveshare-dashboard.timer:
OnUnitActiveSec=30min  # Update every 30 minutes instead of 15

# Disable weather if not needed
weather:
  enabled: false
```

## Monitoring

### Check Service Health

```bash
# Is timer scheduled?
systemctl list-timers waveshare-dashboard.timer

# How many errors?
sudo journalctl -u waveshare-dashboard.service | grep ERROR | wc -l

# Last execution time?
sudo journalctl -u waveshare-dashboard.service | head -n 5
```

### Setup Email Alerts (Optional)

Create `/etc/systemd/system/waveshare-dashboard.service.d/notify.conf`:
```ini
[Service]
OnFailure=send-email@%i.service
```

## Upgrading

```bash
# Pull latest version
cd ~/epaper-calendar
git pull origin main

# Reinstall dependencies (if changed)
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart waveshare-dashboard.service
```

## Hardware Integration

### Display Setup

```bash
# Enable SPI
sudo raspi-config
# Interface Options > SPI > Enable

# Test SPI
python3 -c "import spidev; spi = spidev.SpiDev(); spi.open(0, 0); print('SPI OK')"

# Test GPIO
python3 -c "import RPi.GPIO; RPi.GPIO.setmode(RPi.GPIO.BCM); print('GPIO OK')"
```

### Cooling (Optional)

If dashboard runs continuously:
```bash
# Monitor temperature
vcgencmd measure_temp

# Install heatsinks/fan if CPU > 70°C
```

## Performance Benchmarks

On Raspberry Pi 3B+:
- Calendar fetch: ~2 seconds
- Weather fetch: ~1 second
- Rendering: ~0.5 seconds
- Display update: ~3-5 seconds
- Total cycle: ~10 seconds

## Version Information

- **Version**: 0.2.0
- **Release Date**: February 2026
- **Python**: 3.7+
- **Raspberry Pi**: 3B+ or newer
- **Display**: Waveshare e-paper (7.5" recommended)

## Support

- **Issues**: https://github.com/yourusername/epaper-calendar/issues
- **Documentation**: https://github.com/yourusername/epaper-calendar/docs
- **Community**: Raspberry Pi forums

## License

MIT License - see LICENSE file for details

## Changelog

### v0.2.0 (Latest)
- ✅ Multi-calendar support
- ✅ Weather integration (OpenWeatherMap)
- ✅ Async/await for parallel fetching
- ✅ Privacy modes (XKCD, Literature Clock)
- ✅ Internationalization (4 languages)
- ✅ Advanced theme system
- ✅ Systemd timer automation
- ✅ 20+ comprehensive tests

### v0.1.0
- Core calendar fetching
- Google OAuth integration
- Basic e-paper rendering
- Systemd service file
