# E-Paper Calendar Dashboard - Deployment Checklist

Complete checklist for deploying the E-Paper Calendar Dashboard from GitHub to your Raspberry Pi.

## Pre-Deployment (Development Machine)

### ✓ Environment Verification
- [ ] Python 3.8+ installed: `python3 --version`
- [ ] Git installed: `git --version`
- [ ] Virtual environment support: `python3 -m venv --help`
- [ ] Network connectivity: `ping 8.8.8.8`

### ✓ Repository Setup
- [ ] Clone repository:
  ```bash
  git clone https://github.com/hopehubris/epaper-calendar.git
  cd epaper-calendar
  ```
- [ ] Verify structure:
  ```bash
  ls -la src/ scripts/ docs/ systemd/ tests/
  ```
- [ ] Check git history: `git log --oneline | head -5`

### ✓ Local Environment Setup
- [ ] Create virtual environment:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- [ ] Upgrade pip:
  ```bash
  python -m pip install --upgrade pip
  ```
- [ ] Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- [ ] Verify installations:
  ```bash
  python -c "import google.auth; from PIL import Image; print('OK')"
  ```

### ✓ Google Cloud Setup (CRITICAL)

**⚠️ MUST DO THIS FIRST - Generate credentials before deploying to RPi**

- [ ] Go to https://console.cloud.google.com/
- [ ] Create new project named "epaper-calendar"
- [ ] Enable Google Calendar API:
  - Search for "Google Calendar API"
  - Click "Enable"
- [ ] Create OAuth 2.0 credentials:
  - Go to "Credentials" (left sidebar)
  - Click "Create Credentials" → "OAuth client ID"
  - Application type: **Desktop application**
  - Name: "epaper-calendar"
  - Click "Create"
- [ ] Download credentials:
  - Find your credentials in the table
  - Click the download button (⬇️)
  - Rename file to `credentials.json`
  - Move to project root:
    ```bash
    mv ~/Downloads/client_secret_*.json /path/to/epaper-calendar/credentials.json
    ```
- [ ] Verify credentials file:
  ```bash
  python -c "import json; json.load(open('credentials.json')); print('Valid!')"
  ```

### ✓ OAuth Token Generation
- [ ] Generate token:
  ```bash
  python scripts/setup_oauth.py --generate
  ```
- [ ] Follow browser authorization (or use headless mode)
- [ ] Verify token created:
  ```bash
  ls -la token.json  # should exist and be > 100 bytes
  ```
- [ ] Verify token validity:
  ```bash
  python scripts/setup_oauth.py --verify
  ```

### ✓ Configuration
- [ ] Copy .env.example to .env:
  ```bash
  cp .env.example .env
  ```
- [ ] Find your calendar IDs:
  ```bash
  python -c "
  from src.calendar_fetcher import CalendarFetcher
  fetcher = CalendarFetcher()
  for cal_id, name in fetcher.list_available_calendars().items():
      print(f'{name}: {cal_id}')
  "
  ```
- [ ] Edit .env with your calendar IDs:
  ```bash
  nano .env
  # Update:
  # ASHI_CALENDAR_ID=correct-ashi-id@gmail.com
  # SINDI_CALENDAR_ID=correct-sindi-id@gmail.com
  ```
- [ ] Verify configuration:
  ```bash
  python src/config.py
  ```

### ✓ Local Testing
- [ ] Test display rendering:
  ```bash
  python scripts/test_display.py
  open test_display.png
  ```
- [ ] Verify image generated: `ls -la test_display.png`
- [ ] Run unit tests:
  ```bash
  pytest tests/ -v
  ```
- [ ] Verify all tests pass (15/15)
- [ ] Manual update test:
  ```bash
  python src/main.py
  ```
- [ ] Check logs produced:
  ```bash
  tail -20 /var/log/epaper-calendar/calendar.log 2>/dev/null || echo "No log yet"
  ```
- [ ] Verify cache created:
  ```bash
  ls -la events_cache.db
  ```

### ✓ Pre-Deployment Verification
- [ ] README readable: `cat README.md | head -20`
- [ ] QUICKSTART instructions clear: `cat QUICKSTART.md`
- [ ] DEPLOYMENT guide complete: `cat docs/DEPLOYMENT.md`
- [ ] All documentation links work: Check README links
- [ ] No sensitive files tracked:
  ```bash
  git status
  # Should show "nothing to commit"
  ```
- [ ] No .env or token.json in git:
  ```bash
  git check-ignore .env token.json credentials.json
  # All should be ignored
  ```

---

## Raspberry Pi Deployment

### ✓ RPi Hardware Preparation

**Physical Setup:**
- [ ] Raspberry Pi 4B+ with adequate power supply
- [ ] MicroSD card (16GB+ recommended)
- [ ] Raspberry Pi OS installed (Bullseye or newer)
- [ ] SSH enabled and accessible
- [ ] Network connected (WiFi or Ethernet)
- [ ] Waveshare 7.5" e-paper display connected via SPI
- [ ] Display power cable connected to 5V

**Network Verification:**
- [ ] Find RPi IP address:
  ```bash
  # On RPi terminal:
  hostname -I
  # Or on dev machine:
  ping raspberrypi.local
  ```
- [ ] Test SSH access from dev machine:
  ```bash
  ssh pi@192.168.1.xxx
  # Or use hostname:
  ssh pi@raspberrypi.local
  ```
- [ ] Default password is "raspberry" (consider changing)

### ✓ RPi System Setup

SSH into RPi:
```bash
ssh pi@raspberrypi.local
# or
ssh pi@192.168.1.xxx
```

Then execute on RPi:

- [ ] Update system:
  ```bash
  sudo apt-get update
  sudo apt-get upgrade -y
  ```
- [ ] Install Python 3.9+:
  ```bash
  python3 --version  # Check version
  sudo apt-get install -y python3.9 python3.9-venv python3.9-dev
  ```
- [ ] Install build dependencies:
  ```bash
  sudo apt-get install -y build-essential
  sudo apt-get install -y libjpeg-dev zlib1g-dev
  sudo apt-get install -y libatlas-base-dev libjasper-dev
  ```
- [ ] Install git:
  ```bash
  sudo apt-get install -y git
  ```
- [ ] Install rsync (for deployment):
  ```bash
  sudo apt-get install -y rsync
  ```

### ✓ Enable SPI Interface

On RPi terminal:
- [ ] Enable SPI via raspi-config:
  ```bash
  sudo raspi-config
  # → Interfacing Options → SPI → Yes → Finish
  sudo reboot
  ```
- [ ] Verify SPI enabled after reboot:
  ```bash
  ls /dev/spidev*  # should show spidev devices
  ```

### ✓ GPIO User Permissions

On RPi terminal:
- [ ] Add pi user to required groups:
  ```bash
  sudo usermod -a -G gpio pi
  sudo usermod -a -G spi pi
  ```
- [ ] Log out and back in for changes:
  ```bash
  exit
  ssh pi@raspberrypi.local
  ```
- [ ] Verify permissions:
  ```bash
  groups pi  # should include gpio and spi
  ```

### ✓ Clone and Deploy Application

From development machine, run:

```bash
cd /path/to/epaper-calendar
bash scripts/deploy.sh pi raspberrypi.local
# OR use IP address:
bash scripts/deploy.sh pi 192.168.1.xxx
```

The deploy script will:
- [ ] Copy project files to `/home/pi/epaper-calendar`
- [ ] Create virtual environment
- [ ] Install Python dependencies
- [ ] Create systemd service
- [ ] Create systemd timer
- [ ] Create log directory
- [ ] Set proper permissions

**Expected output:**
```
Deploying to pi@raspberrypi.local...
Checking prerequisites...
Syncing files...
Creating venv...
Installing dependencies...
Installing systemd files...
Creating log directory...
✓ Deployment complete!
```

### ✓ Post-Deployment Configuration

SSH into RPi:
```bash
ssh pi@raspberrypi.local
```

Then:

- [ ] Edit .env file:
  ```bash
  nano /home/pi/epaper-calendar/.env
  # Update calendar IDs (should match what you configured locally)
  ```
- [ ] Verify OAuth credentials:
  ```bash
  ls -la /home/pi/epaper-calendar/token.json
  ls -la /home/pi/epaper-calendar/credentials.json
  # token.json should exist
  # credentials.json may not be needed on RPi (only if generating OAuth)
  ```
- [ ] Test Python environment:
  ```bash
  cd /home/pi/epaper-calendar
  source venv/bin/activate
  python -c "import src; print('OK')"
  ```

### ✓ Initial Manual Test

On RPi terminal:

- [ ] Stop timer (if running):
  ```bash
  sudo systemctl stop epaper-calendar.timer
  ```
- [ ] Manually trigger update:
  ```bash
  sudo systemctl start epaper-calendar
  ```
- [ ] Monitor logs in real-time:
  ```bash
  journalctl -u epaper-calendar -f
  # Press Ctrl+C to stop monitoring
  ```
- [ ] Expected log output:
  ```
  Starting update cycle
  Fetching calendar events...
  Fetched X Ashi events, Y Sindi events
  Rendering display...
  Updating hardware display...
  Update completed in X.X seconds
  ```
- [ ] Check display updated:
  ```bash
  # Visually inspect the e-paper display
  # Should show calendar grid and events
  ```
- [ ] Verify cache created:
  ```bash
  ls -la events_cache.db
  sqlite3 events_cache.db "SELECT COUNT(*) FROM events;"
  # Should return a number > 0
  ```

### ✓ Systemd Service Configuration

On RPi terminal:

- [ ] Enable service:
  ```bash
  sudo systemctl enable epaper-calendar
  sudo systemctl enable epaper-calendar.timer
  ```
- [ ] Start timer:
  ```bash
  sudo systemctl start epaper-calendar.timer
  ```
- [ ] Verify timer active:
  ```bash
  sudo systemctl status epaper-calendar.timer
  sudo systemctl list-timers epaper-calendar*
  ```
- [ ] Check service status:
  ```bash
  sudo systemctl status epaper-calendar
  ```

### ✓ Monitoring & Verification

On RPi terminal, verify automatic operation:

- [ ] Wait 15 minutes (or adjust UPDATE_INTERVAL in .env)
- [ ] Check if display updated:
  ```bash
  journalctl -u epaper-calendar -n 20 --no-pager
  ```
- [ ] Monitor next update cycle:
  ```bash
  journalctl -u epaper-calendar -f
  # Wait for next timer trigger
  ```
- [ ] Check CPU temperature (optional):
  ```bash
  vcgencmd measure_temp
  # Should be < 70°C
  ```
- [ ] Check disk space:
  ```bash
  df -h
  # Should have > 500MB free
  ```

### ✓ Long-Term Monitoring (First 24 Hours)

- [ ] Check logs at intervals:
  ```bash
  journalctl -u epaper-calendar | tail -50
  ```
- [ ] Verify at least 3-4 successful updates in logs
- [ ] Confirm display updates each cycle
- [ ] Check for any error messages
- [ ] Monitor system performance:
  ```bash
  uptime
  free -h
  ```
- [ ] Test network resilience (if possible)

---

## Post-Deployment Customization

### ✓ Fine-Tuning Performance

- [ ] Adjust update interval in .env:
  ```bash
  nano /home/pi/epaper-calendar/.env
  # UPDATE_INTERVAL=900  # default 15 minutes
  # UPDATE_INTERVAL=1800 # 30 minutes (lower power)
  # UPDATE_INTERVAL=600  # 10 minutes (more frequent)
  ```
- [ ] Reload systemd timer:
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl restart epaper-calendar.timer
  ```

### ✓ Customize Display Colors

- [ ] Edit display_renderer.py:
  ```bash
  nano /home/pi/epaper-calendar/src/display_renderer.py
  # Modify COLORS dictionary
  ```
- [ ] Restart service:
  ```bash
  sudo systemctl restart epaper-calendar
  ```

### ✓ Add Additional Features (Phase 2)

Future enhancements to consider:
- [ ] Weather integration
- [ ] Event descriptions display
- [ ] Status LEDs
- [ ] Manual refresh button
- [ ] Multiple language support

---

## Troubleshooting Checklist

If something goes wrong:

### Display Not Updating
- [ ] Check logs: `journalctl -u epaper-calendar -f`
- [ ] Verify timer active: `systemctl status epaper-calendar.timer`
- [ ] Manually trigger: `sudo systemctl start epaper-calendar`
- [ ] Check hardware connections
- [ ] See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

### OAuth/API Issues
- [ ] Check token: `ls -la token.json`
- [ ] Refresh token: `python scripts/setup_oauth.py --refresh`
- [ ] Verify calendar IDs: `cat .env | grep CALENDAR_ID`
- [ ] Test connectivity: `ping 8.8.8.8`
- [ ] See [docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md)

### Cache Issues
- [ ] Check database: `sqlite3 events_cache.db ".tables"`
- [ ] Clear cache: `rm events_cache.db`
- [ ] Restart service: `systemctl restart epaper-calendar`

### GPIO/Hardware Issues
- [ ] Check SPI: `ls /dev/spidev*`
- [ ] Check permissions: `groups pi`
- [ ] Verify connections: Physical inspection
- [ ] Test display: `python src/waveshare_driver.py`
- [ ] See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## Success Criteria ✓

Your deployment is successful when:

- ✓ Repository cloned from GitHub
- ✓ Local testing completed (display renders, tests pass)
- ✓ OAuth credentials generated successfully
- ✓ RPi has Python 3.8+, network, and SPI enabled
- ✓ Application deployed via deploy.sh
- ✓ .env configured with calendar IDs
- ✓ Manual update completes without errors
- ✓ Display shows 6-week calendar with events
- ✓ Systemd timer active and triggering updates
- ✓ Logs show successful update cycles
- ✓ Display updates every 15 minutes automatically
- ✓ Service survives RPi reboot
- ✓ No errors in 24-hour monitoring period

---

## Support Resources

When you need help:

1. **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Solutions to 50+ common issues
2. **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Detailed deployment walkthrough
3. **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design details
4. **[QUICKSTART.md](QUICKSTART.md)** - Quick reference guide
5. **GitHub Issues** - Report bugs or request features

---

**Ready to deploy?** Start at "Pre-Deployment" section above.

**Already deployed?** Monitor logs and enjoy your e-paper calendar! 📅

---

**Version**: v0.1.0  
**Last Updated**: February 8, 2026  
**Status**: Production Ready
