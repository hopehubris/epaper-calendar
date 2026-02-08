# E-Paper Calendar Dashboard - Quick Start

Get up and running in 10 minutes (local testing) or 30 minutes (RPi deployment).

## TL;DR - 5 Step Setup

### 1. Clone & Setup (2 min)
```bash
cd epaper-calendar
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Calendar IDs (1 min)
```bash
cp .env.example .env
# Edit .env - add your calendar email addresses
```

### 3. Get Google OAuth Credentials (3 min)
```bash
# Download credentials.json from Google Cloud Console
# (See docs/OAUTH_SETUP.md for full instructions)
python scripts/setup_oauth.py --generate
```

### 4. Test Display (1 min)
```bash
python scripts/test_display.py
open test_display.png
```

### 5. Deploy to RPi (3 min)
```bash
bash scripts/deploy.sh pi 192.168.1.xxx
```

## Key Files

| File | Purpose |
|------|---------|
| `.env.example` | Configuration template |
| `src/main.py` | Main update script |
| `src/calendar_fetcher.py` | Google Calendar API client |
| `src/display_renderer.py` | PIL display renderer |
| `src/cache_manager.py` | SQLite cache |
| `scripts/setup_oauth.py` | OAuth token generator |
| `scripts/test_display.py` | Display test utility |
| `scripts/deploy.sh` | RPi deployment |
| `systemd/epaper-calendar.service` | Systemd service |
| `systemd/epaper-calendar.timer` | 15-min timer |

## Configuration

Edit `.env`:

```bash
# Your calendar email addresses
ASHI_CALENDAR_ID=ashi@gmail.com
SINDI_CALENDAR_ID=sindi@gmail.com

# Display settings
DISPLAY_WIDTH=800
DISPLAY_HEIGHT=480
DISPLAY_COLOR_MODE=red

# Update frequency (seconds)
UPDATE_INTERVAL=900
```

## Testing

```bash
# Test cache
pytest tests/ -v

# Test display rendering
python scripts/test_display.py

# Manual update
python src/main.py

# Check logs
tail -f /var/log/epaper-calendar/calendar.log
```

## Systemd Service (RPi Only)

```bash
# Check status
systemctl status epaper-calendar.timer

# Manual trigger
systemctl start epaper-calendar

# View logs
journalctl -u epaper-calendar -f

# Enable on boot
systemctl enable epaper-calendar.timer
```

## Common Tasks

### Update Calendar IDs
```bash
nano .env
systemctl restart epaper-calendar
```

### Refresh OAuth Token
```bash
python scripts/setup_oauth.py --refresh
systemctl restart epaper-calendar
```

### Clear Cache
```bash
rm events_cache.db
systemctl start epaper-calendar
```

### Check What's Cached
```bash
sqlite3 events_cache.db "SELECT calendar_id, COUNT(*) FROM events GROUP BY calendar_id;"
```

### View Real-time Logs
```bash
journalctl -u epaper-calendar -f
```

## Troubleshooting

### "Credentials not found"
→ Download from Google Cloud Console, save as `credentials.json`

### "Token expired"
→ Run: `python scripts/setup_oauth.py --refresh`

### "Display not updating"
→ Check: `journalctl -u epaper-calendar -f`

### "Events not showing"
→ Verify calendar IDs: `python src/config.py`

## Project Structure

```
epaper-calendar/
├── src/                      # Core application
│   ├── main.py              # Main entry point
│   ├── calendar_fetcher.py  # Google Calendar API
│   ├── display_renderer.py  # PIL rendering
│   ├── cache_manager.py     # SQLite cache
│   ├── config.py            # Configuration
│   └── utils.py             # Utilities
├── scripts/                  # Utility scripts
│   ├── setup_oauth.py       # OAuth token gen
│   ├── test_display.py      # Display test
│   └── deploy.sh            # RPi deployment
├── systemd/                  # Systemd files
│   ├── epaper-calendar.service
│   └── epaper-calendar.timer
├── tests/                    # Test suite
├── docs/                     # Documentation
│   ├── SETUP.md
│   ├── OAUTH_SETUP.md
│   └── DEPLOYMENT.md
├── requirements.txt
├── .env.example
└── README.md
```

## Next Steps

1. **Full Setup**: See [docs/SETUP.md](docs/SETUP.md)
2. **OAuth Details**: See [docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md)
3. **RPi Deployment**: See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
4. **Customization**: Edit `src/display_renderer.py` for colors/layout

## Architecture

```
Every 15 minutes (systemd timer)
  ↓
src/main.py
  ├─ calendar_fetcher.py → Google Calendar API
  ├─ cache_manager.py → events_cache.db (SQLite)
  ├─ display_renderer.py → PIL image (800×480)
  └─ waveshare_driver.py → E-paper display (SPI)
```

## Display Layout

```
┌────────────────────────────────────────┐
│ 6-Week Calendar    Updated: 10:32 AM  │ ← Header (40px)
├────────────────────────────────────────┤
│  Sun  Mon  Tue  Wed  Thu  Fri  Sat    │
│  ┌─────────────────────────────────┐  │
│  │ 8  │ 9  │10  │11  │12  │13  │14│  │
│  ├─────────────────────────────────┤  │
│  │15  │16  │17  │18  │19  │20  │21│  │
│  ├─────────────────────────────────┤  │ ← Grid (360px)
│  │22  │23  │24  │25  │26  │27  │28│  │
│  ├─────────────────────────────────┤  │
│  │ 1  │ 2  │ 3  │ 4  │ 5  │ 6  │ 7│  │
│  └─────────────────────────────────┘  │
├────────────────────────────────────────┤
│ Today & Upcoming Events                │ ← Events (80px)
│ A 10:32 Team Meeting                   │
│ S 14:00 Doctor Appointment             │
└────────────────────────────────────────┘

A = Ashi's event (red on color display)
S = Sindi's event (black)
```

## Performance

- **Update cycle**: ~15 seconds
- **Display refresh**: ~5-8 seconds (e-paper)
- **Power draw**: 0.5W idle, 2W updating
- **Offline support**: Full (SQLite cache)

## Success Indicators

✓ Display renders locally (`test_display.py` works)
✓ Cache stores events (`events_cache.db` exists)
✓ OAuth token generated (`token.json` exists)
✓ Manual update works (`python src/main.py` succeeds)
✓ Systemd timer active (`systemctl status epaper-calendar.timer`)

---

**Need help?** Check the [documentation](docs/) or [GitHub](https://github.com/ashi-xyz/epaper-calendar).
