# E-Paper Calendar Dashboard - Setup Guide

Complete setup instructions for both development and Raspberry Pi deployment.

## Prerequisites

### Development Machine (Mac/Linux)
- Python 3.8 or higher
- pip and venv
- Git

### Raspberry Pi (Target Hardware)
- Raspberry Pi 4B or higher
- Raspbian/Raspberry Pi OS (Bullseye or newer)
- Waveshare 7.5" 800×480 red/greyscale e-paper display
- SPI enabled on RPi
- Network connectivity

## Step 1: Clone Repository

```bash
git clone https://github.com/ashi-xyz/epaper-calendar.git
cd epaper-calendar
```

## Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set:
- `ASHI_CALENDAR_ID`: Ashi's Google Calendar email
- `SINDI_CALENDAR_ID`: Sindi's Google Calendar email
- `TIMEZONE`: Event timezone (default OK for PST)
- Other settings as needed

**Don't commit `.env` to Git!**

## Step 5: Set Up Google Calendar OAuth

```bash
python scripts/setup_oauth.py --generate
```

This will:
1. Open your browser to Google OAuth consent page
2. Ask permission to access Google Calendar (read-only)
3. Generate `token.json` for authentication
4. Save credentials securely

**Note:** You must have Google Calendar credentials (see [OAUTH_SETUP.md](OAUTH_SETUP.md))

## Step 6: Test Display Rendering

```bash
python scripts/test_display.py
open test_display.png  # View the generated test image
```

This verifies the display renderer works correctly.

## Step 7: Test Calendar Fetching

```bash
python -m pytest tests/ -v
```

## Step 8: Run Update Manually

```bash
python src/main.py
```

Check the output and review `events_cache.db` to verify events are cached.

## Step 9: Deploy to Raspberry Pi

### 9a. Prepare RPi

```bash
# SSH into RPi
ssh pi@192.168.1.xxx

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3-dev python3-pip python3-venv git
sudo apt-get install -y libopenjp2-7 libjpeg-dev zlib1g-dev  # For Pillow
sudo apt-get install -y libatlas-base-dev libjasper-dev
```

### 9b. Deploy Application

```bash
# On your machine
bash scripts/deploy.sh pi@192.168.1.xxx
```

This will:
1. Copy project to RPi
2. Create virtual environment
3. Install dependencies
4. Copy systemd service files
5. Enable and start the service

### 9c. Enable SPI on RPi

```bash
# SSH into RPi
ssh pi@192.168.1.xxx

# Enable SPI
sudo raspi-config
# → Interface Options → SPI → Yes
# → Reboot
```

## Step 10: Verify Installation

### On Development Machine

```bash
# Test all components
pytest -v
```

### On Raspberry Pi

```bash
# Check service status
systemctl status epaper-calendar

# View logs
journalctl -u epaper-calendar -f

# Manually trigger update
systemctl start epaper-calendar

# Check cache
sqlite3 /home/pi/epaper-calendar/events_cache.db ".tables"
```

## Troubleshooting

### OAuth Token Expired

```bash
python scripts/setup_oauth.py --refresh
```

### Cache Corrupted

```bash
rm events_cache.db
systemctl restart epaper-calendar
```

### Service Won't Start

```bash
# Check service status
systemctl status epaper-calendar

# View detailed logs
journalctl -u epaper-calendar -n 100

# Check Python syntax
python -m py_compile src/main.py
```

### GPIO/Hardware Issues

```bash
# Check GPIO pins
gpio readall

# Test SPI
# Verify /dev/spidev0.0 exists
ls -la /dev/spidev*
```

## Next Steps

1. **Customize Display**: Edit `display_renderer.py` to change colors/layout
2. **Adjust Timing**: Change `UPDATE_INTERVAL` in `.env` (seconds)
3. **Add Calendar**: Configure additional calendars in `calendar_fetcher.py`
4. **Monitor Logs**: Set up log rotation for systemd journal

## Support

For issues:
1. Check logs: `journalctl -u epaper-calendar -f`
2. Test manually: `python src/main.py`
3. Verify config: `python src/config.py`
4. Test OAuth: `python scripts/setup_oauth.py --verify`

## Security Notes

- Never commit `.env` or `token.json` to Git
- `.gitignore` is configured to prevent this
- Use environment variables for sensitive config on production
- OAuth scopes are read-only (calendar.readonly)
- Systemd service runs as unprivileged user (pi)
