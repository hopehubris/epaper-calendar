# E-Paper Calendar Dashboard - Deployment Guide

Step-by-step guide for deploying to Raspberry Pi.

## Prerequisites

### On Raspberry Pi
- Raspberry Pi 4B or higher
- Raspbian/Raspberry Pi OS (Bullseye or newer)
- Network connectivity
- SSH enabled
- Waveshare 7.5" e-paper display (red/greyscale)
- SPI interface enabled

### On Development Machine
- SSH client installed
- rsync installed
- Credentials and token generated locally first

## Phase 1: Local Preparation

### 1.1 Generate Google OAuth Credentials

On your development machine:

```bash
# Create credentials.json (download from Google Cloud Console)
# See docs/OAUTH_SETUP.md for full instructions

# Generate token
python scripts/setup_oauth.py --generate

# Verify
python scripts/setup_oauth.py --verify
```

### 1.2 Test Locally

```bash
# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Edit .env with calendar IDs

# Test display
python scripts/test_display.py
open test_display.png

# Test cache
pytest tests/ -v

# Manual run
python src/main.py
```

## Phase 2: Raspberry Pi Setup

### 2.1 Prepare RPi Hardware

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

### 2.2 Enable SPI Interface

```bash
# SSH into RPi
ssh pi@192.168.1.xxx

# Enable SPI
sudo raspi-config
# → Interfacing Options → SPI → Yes → Finish → Reboot
```

### 2.3 Deploy Application

From your development machine:

```bash
bash scripts/deploy.sh pi 192.168.1.xxx
```

This automatically:
- Creates remote directory
- Copies project files (excluding venv, .git, cache, etc.)
- Sets up Python virtual environment
- Installs dependencies
- Installs systemd service and timer
- Creates log directory

### 2.4 Configure Calendar IDs

SSH into RPi and edit `.env`:

```bash
ssh pi@192.168.1.xxx
nano /home/pi/epaper-calendar/.env

# Edit these fields:
# ASHI_CALENDAR_ID=ashi@gmail.com
# SINDI_CALENDAR_ID=sindi@gmail.com
```

### 2.5 Set Up OAuth Token

SSH into RPi:

```bash
ssh pi@192.168.1.xxx
cd /home/pi/epaper-calendar
source venv/bin/activate

# Generate token (interactive)
python scripts/setup_oauth.py --generate
# This opens browser (on your dev machine, copy the auth URL)
# Or use: python scripts/setup_oauth.py --generate --no-webbrowser

# Verify
python scripts/setup_oauth.py --verify
```

## Phase 3: Testing

### 3.1 Manual Update Test

```bash
ssh pi@192.168.1.xxx
sudo systemctl start epaper-calendar
sudo journalctl -u epaper-calendar -f
```

Expected output:
```
Starting update cycle
Fetching calendar events...
Fetched X Ashi events, Y Sindi events
Rendering display...
Updating hardware display...
Update completed in X.X seconds
```

### 3.2 Check Cache

```bash
ssh pi@192.168.1.xxx
sqlite3 /home/pi/epaper-calendar/events_cache.db "SELECT COUNT(*) FROM events;"
```

### 3.3 Enable Timer (15-minute updates)

```bash
ssh pi@192.168.1.xxx
sudo systemctl start epaper-calendar.timer
sudo systemctl enable epaper-calendar.timer

# Check status
sudo systemctl status epaper-calendar.timer
sudo systemctl list-timers epaper-calendar*
```

## Phase 4: Monitoring

### Check Service Status

```bash
ssh pi@192.168.1.xxx

# Check if timer is active
systemctl status epaper-calendar.timer

# View recent logs
journalctl -u epaper-calendar -n 50

# Follow logs in real-time
journalctl -u epaper-calendar -f

# View detailed error logs
journalctl -u epaper-calendar -p err -n 20
```

### Check Performance

```bash
ssh pi@192.168.1.xxx

# View execution times
journalctl -u epaper-calendar | grep "Update completed"

# Check power usage
vcgencmd measure_temp  # CPU temp
vcgencmd measure_volts # Voltage
```

## Phase 5: Troubleshooting

### Service Won't Start

```bash
# Check service logs
journalctl -u epaper-calendar -n 100

# Manually run update script
cd /home/pi/epaper-calendar
source venv/bin/activate
python src/main.py

# Check Python syntax
python -m py_compile src/main.py
```

### OAuth Token Issues

```bash
# Refresh token
python scripts/setup_oauth.py --refresh

# Regenerate token
rm token.json
python scripts/setup_oauth.py --generate
```

### Display Not Updating

```bash
# Check GPIO access
gpio readall

# Verify SPI is enabled
ls -la /dev/spidev*

# Test display directly
python src/waveshare_driver.py
```

### Cache Issues

```bash
# Check cache status
sqlite3 events_cache.db ".tables"

# Clear cache
rm events_cache.db
systemctl start epaper-calendar
```

### Logs Not Writing

```bash
# Check log directory
ls -la /var/log/epaper-calendar/

# Fix permissions
sudo chown pi:pi /var/log/epaper-calendar/

# Restart service
systemctl restart epaper-calendar
```

## Phase 6: Customization

### Change Update Interval

Edit `.env` on RPi:
```bash
UPDATE_INTERVAL=600  # 10 minutes instead of 15
```

Edit `/etc/systemd/system/epaper-calendar.timer`:
```ini
[Timer]
OnUnitActiveSec=10min
```

Then reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart epaper-calendar.timer
```

### Adjust Display Colors

Edit `src/display_renderer.py` in `COLORS` dict and rebuild.

### Add Additional Calendars

Edit `src/calendar_fetcher.py` to add more calendars.

## Maintenance

### Regular Backups

```bash
# Backup cache and config
ssh pi@192.168.1.xxx
tar czf ~/epaper-calendar-backup.tar.gz \
    /home/pi/epaper-calendar/.env \
    /home/pi/epaper-calendar/events_cache.db
```

### Update Application

```bash
# Pull latest changes
cd /path/to/epaper-calendar
git pull

# Redeploy
bash scripts/deploy.sh pi 192.168.1.xxx

# Verify
ssh pi@192.168.1.xxx "systemctl restart epaper-calendar"
```

### Clean Old Logs

```bash
# View journal size
journalctl --disk-usage

# Rotate logs
sudo journalctl --vacuum=30d  # Keep 30 days
```

## Security Notes

1. **OAuth Tokens**: Keep `token.json` and `credentials.json` secure
2. **SSH Keys**: Use SSH keys instead of passwords
3. **Service User**: Service runs as unprivileged `pi` user
4. **Systemd Hardening**: Service uses restricted filesystem access
5. **Network**: Update interval balances load (randomized by 30s)

## Performance Targets

- **Fetch time**: 2-3 seconds (2 calendars)
- **Render time**: 1-2 seconds
- **Display update**: 5-8 seconds
- **Total cycle**: ~15 seconds
- **Power draw**: 0.5W (idle), 2W (updating)

## Support

For deployment issues:
1. Check logs: `journalctl -u epaper-calendar -f`
2. Test manually: `python src/main.py`
3. Verify OAuth: `python scripts/setup_oauth.py --verify`
4. Check hardware: `gpio readall`
