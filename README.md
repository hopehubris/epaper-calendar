# E-Paper Calendar Dashboard

A Raspberry Pi application that displays Ashi's and Sindi's Google Calendar events on a Waveshare 7.5" e-paper display (800×480px, red/greyscale).

## Features

- **6-Week Calendar Grid**: 42-day view with color-coded events (red for Ashi, black for Sindi)
- **Today + Next 3 Events**: Quick view of today's schedule and upcoming events
- **Last Update Timestamp**: Shows when the display was last refreshed
- **Automatic Updates**: Every 15 minutes via systemd timer
- **Offline Support**: SQLite cache for offline operation
- **Graceful Error Handling**: Network failures and API errors handled gracefully
- **Auto-start & Recovery**: Runs as systemd service with auto-recovery

## Architecture

```
Systemd Timer (15 min)
    ↓
calendar_fetcher.py (Google API + Cache)
    ↓
events_cache.db (SQLite)
    ↓
display_renderer.py (PIL Grid Layout)
    ↓
waveshare_driver.py (Hardware Interface)
    ↓
E-Paper Display (800×480px)
```

## Project Structure

```
epaper-calendar/
├── src/
│   ├── calendar_fetcher.py      # Google Calendar API client
│   ├── display_renderer.py      # PIL-based rendering
│   ├── cache_manager.py         # SQLite cache layer
│   ├── waveshare_driver.py      # Hardware driver (RPi only)
│   ├── utils.py                 # Shared utilities
│   └── config.py                # Configuration management
├── systemd/
│   ├── epaper-calendar.service  # Systemd service
│   └── epaper-calendar.timer    # 15-min timer
├── scripts/
│   ├── setup_oauth.py           # Google OAuth token generation
│   ├── test_display.py          # Display testing utility
│   └── deploy.sh                # RPi deployment script
├── tests/
│   ├── test_fetcher.py
│   ├── test_renderer.py
│   └── test_cache.py
├── docs/
│   ├── SETUP.md                 # Setup guide
│   ├── OAUTH_SETUP.md           # Google OAuth configuration
│   └── DEPLOYMENT.md            # RPi deployment guide
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.8+
- Raspberry Pi 4B+ (for hardware testing)
- Waveshare 7.5" e-paper display (red/greyscale variant)
- Google Calendar accounts for Ashi and Sindi

### Setup

1. **Clone and create virtual environment**:
   ```bash
   cd epaper-calendar
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Set up Google Calendar OAuth**:
   ```bash
   python scripts/setup_oauth.py
   ```

5. **Test the display**:
   ```bash
   python scripts/test_display.py
   ```

6. **Deploy to systemd**:
   ```bash
   sudo bash scripts/deploy.sh
   ```

## Configuration

See `.env.example` for all configuration options:

- `ASHI_CALENDAR_ID`: Ashi's Google Calendar email
- `SINDI_CALENDAR_ID`: Sindi's Google Calendar email
- `TIMEZONE`: Event timezone (default: America/Los_Angeles)
- `UPDATE_INTERVAL`: Update frequency in seconds (default: 900 = 15 min)

## Google Calendar OAuth

Run the setup script to generate tokens:

```bash
python scripts/setup_oauth.py
```

This will:
1. Open your browser to Google's OAuth consent page
2. Generate `credentials.json` and `token.json`
3. Securely store tokens with appropriate permissions

## Systemd Service

The application runs as a systemd service that auto-starts on boot:

```bash
# Check status
systemctl status epaper-calendar

# Manual trigger
systemctl start epaper-calendar

# View logs
journalctl -u epaper-calendar -f
```

## Testing

```bash
# Run all tests
pytest

# Test with coverage
pytest --cov=src

# Test specific component
pytest tests/test_fetcher.py -v
```

## Troubleshooting

### Display not updating?
```bash
journalctl -u epaper-calendar -f
systemctl restart epaper-calendar
```

### OAuth token expired?
```bash
python scripts/setup_oauth.py
```

### Cache issues?
```bash
rm events_cache.db
systemctl restart epaper-calendar
```

## Performance

- **Fetch time**: ~2-3 seconds (2 calendars)
- **Render time**: ~1-2 seconds (PIL)
- **Display update**: ~5-8 seconds (SPI)
- **Total cycle**: ~15 seconds
- **Power draw**: ~0.5W (idle), ~2W (update)

## Hardware

- **Display**: Waveshare 7.5" 800×480 Red/Greyscale E-Paper
- **Interface**: SPI (GPIO pins 8, 10, 11)
- **Refresh time**: ~5-8 seconds
- **Color support**: Red, Black, White, Grey

## Version

**v0.1.0** (Initial release)

## License

MIT

## Contributors

- Ashi (calendar owner)
- Sindi (calendar owner)
