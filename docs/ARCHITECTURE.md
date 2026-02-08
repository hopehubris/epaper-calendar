# E-Paper Calendar Dashboard - Architecture

Complete architecture documentation for the E-Paper Calendar Dashboard.

## System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    Systemd Timer (15 min)                    │
└─────────────────┬──────────────────────────────────────────┘
                  │
                  ↓
         ┌────────────────┐
         │  main.py       │  ← Entry point (runs every 15 min)
         └────────┬───────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
        ↓         ↓         ↓
    ┌──────┐  ┌──────┐  ┌──────┐
    │Cache │  │Fetch │  │Render│
    │Mgr   │  │Events│  │      │
    └──────┘  └──────┘  └──────┘
        │         │         │
        └─────────┼─────────┘
                  │
                  ↓
          ┌───────────────┐
          │   Display     │
          │   Driver      │
          └───────────────┘
                  │
                  ↓
        ┌─────────────────┐
        │  E-Paper        │
        │  Display        │
        │  (800×480)      │
        └─────────────────┘
```

## Component Architecture

### 1. Configuration Layer (`src/config.py`)
- Loads `.env` configuration
- Validates required settings
- Sets up logging
- Centralizes all configurable parameters

```python
# Key configs
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480
UPDATE_INTERVAL = 900  # 15 minutes
TIMEZONE = "America/Los_Angeles"
```

### 2. Cache Layer (`src/cache_manager.py`)
- **SQLite database** for offline support
- Stores events in relational schema
- Provides efficient date range queries
- Tracks cache age and metadata

```
Database Schema:
├── events
│   ├── id (PK)
│   ├── calendar_id
│   ├── summary
│   ├── start_time
│   ├── end_time
│   ├── all_day
│   └── event_json
├── cache_metadata
│   ├── key (PK)
│   └── value
└── indices on calendar_id, start_time, cached_at
```

**Key Methods**:
- `store_events(calendar_id, events)` - Cache events from API
- `get_events(calendar_id, start_date, end_date)` - Query cache
- `get_cache_age()` - Return seconds since last update
- `clear_old_events(days)` - Cleanup old entries

### 3. Calendar Fetcher (`src/calendar_fetcher.py`)
- **Google Calendar API v3** integration
- OAuth 2.0 authentication
- 6-week event retrieval
- Automatic fallback to cache on network failure

```python
# Fetcher flow:
1. Load OAuth token from token.json
2. Refresh if expired
3. Query Google Calendar API (timeMin → timeMax)
4. Store in SQLite cache
5. Return cached events on error
```

**Key Methods**:
- `fetch_events(calendar_id, days=42)` - Fetch 6 weeks
- `fetch_all_calendars()` - Get events from both calendars
- `get_today_events()` - Today's events
- `get_upcoming_events(limit=3)` - Next N events
- `is_online()` - Check API connectivity

### 4. Display Renderer (`src/display_renderer.py`)
- **PIL (Python Imaging Library)** for rendering
- 6-week calendar grid layout
- Event indicators (dots for events)
- Today & upcoming events list
- Support for red/greyscale and B&W modes

```
Display Layout (800×480):
┌─────────────────────────────────────┐
│ Header (40px)                       │
│ 6-Week Calendar    Updated: 10:32   │
├─────────────────────────────────────┤
│ Grid (360px)                        │
│ Sun  Mon  Tue  Wed  Thu  Fri  Sat   │
│ ┌─────────────────────────────────┐ │
│ │ 8 │ 9 │10 │11 │12 │13 │14 │    │ │
│ ├─────────────────────────────────┤ │
│ │... 42 days total (6 rows×7 cols)│ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ Event List (80px)                   │
│ Today & Upcoming                    │
│ A 10:32 Team Meeting                │
│ S 14:00 Doctor Appointment          │
└─────────────────────────────────────┘
```

**Colors**:
- Red mode: Red (Ashi), Black (Sindi), White/Grey background
- B&W mode: Black, White only
- Event dots: Small 2×2px indicators per event

**Key Methods**:
- `render(ashi_events, sindi_events, update_time)` - Full render
- `save(image, path)` - Save to PNG

### 5. Display Driver (`src/waveshare_driver.py`)
- **Waveshare 7.5" e-paper interface**
- SPI communication with GPIO
- Hardware detection & fallback
- Simulator mode for testing

```python
# Driver features:
- GPIO pin configuration
- SPI communication (BCM pins)
- Display update commands
- Sleep/wakeup modes
- Simulator fallback
```

**Hardware Pins** (configurable):
- CS: GPIO 8
- CLK: GPIO 11
- MOSI: GPIO 10
- DC: GPIO 25
- RST: GPIO 27
- BUSY: GPIO 17

### 6. Main Orchestration (`src/main.py`)
- Coordinates all components
- Executes update cycle
- Error handling & recovery
- Logging & monitoring

```python
# Update cycle:
1. Initialize components
2. Fetch events from both calendars
3. Store in cache
4. Render display image
5. Send to hardware
6. Log results
7. Cleanup
```

## Data Flow

### Event from Google Calendar to Display

```
Google Calendar API
    ↓ (JSON event)
CalendarFetcher.fetch_events()
    ↓
├─ Validate & parse
├─ Store to cache (SQLite)
└─ Return to main
    ↓
DisplayRenderer.render()
    ├─ Read from cache
    ├─ Format for display
    ├─ Draw grid & events
    └─ Generate PIL Image
    ↓
WaveshareDriver.display_image()
    ├─ Convert to correct mode
    ├─ Send via SPI
    └─ Hardware updates display
```

### Update Cycle Timeline

```
Time    Component           Action
────────────────────────────────────────
00:00s  Systemd Timer      Trigger service
00:01s  CalendarFetcher    API call #1 (Ashi)
00:02s  CalendarFetcher    API call #2 (Sindi)
00:02s  CacheManager       Store in SQLite
00:03s  DisplayRenderer    Render image
00:04s  WaveshareDriver    SPI send
00:08s  WaveshareDriver    Display update
00:09s  main.py            Logging & cleanup
────────────────────────────────────────
Total: ~9-15 seconds
```

## Error Handling Strategy

### Network Offline
```
API Error → Log → Fall back to cache → Display cached events
```

### OAuth Token Expired
```
Token Expired → Refresh → Continue → Log for admin
If refresh fails → Use cache
```

### Cache Corrupted
```
Cache Error → Log → Fallback empty display → Retry on next cycle
```

### Display Hardware Error
```
Hardware Error → Log → Continue (cache updated) → Retry later
```

### Configuration Error
```
Missing Config → Log error → Exit cleanly → Admin fixes .env
```

## Security Design

### OAuth Token Management
- **Scopes**: `calendar.readonly` only (read-only access)
- **Storage**: `token.json` in project root (gitignored)
- **Rotation**: Auto-refresh before expiration
- **Fallback**: Uses cached data if token fails

### System Security
- **User**: Runs as unprivileged `pi` user (not root)
- **Filesystem**: Restricted write paths (`/home/pi/epaper-calendar`)
- **Systemd**: Hardened service unit (no network access to others)

### Data Security
- **Events**: Cached locally, not transmitted externally
- **Cache**: SQLite file (plaintext, local access only)
- **Logs**: Systemd journal (local only)

## Performance Specifications

### Timing
- **Fetch**: 2-3 seconds (Google API + 2 calendars)
- **Render**: 1-2 seconds (PIL image generation)
- **Display**: 5-8 seconds (SPI + e-paper refresh)
- **Total**: ~15 seconds per update cycle
- **Frequency**: Every 15 minutes (900 seconds)

### Storage
- **Cache DB**: ~1-2 MB (6 weeks × 2 calendars)
- **Application**: ~50 MB (with venv)
- **Log files**: ~10 MB per month

### Power
- **Idle**: 0.5W
- **Update**: 2W
- **Average**: ~0.6W

### Concurrency
- **Single threaded** (sequential updates)
- **No race conditions** (file-based locking not needed)

## Testing Strategy

### Unit Tests
- Cache: 5 tests (init, store, retrieve, age, clear)
- Config: 5 tests (loading, validation, paths)
- Renderer: 5 tests (modes, rendering, colors)

### Integration Tests
- Full cycle test (fetch → cache → render → display)
- Offline mode test (cache-only operation)
- Error recovery tests

### Manual Tests
- `test_display.py`: Verify rendering
- `pytest`: Run test suite
- `systemctl start epaper-calendar`: Service test

## Deployment Architecture

### Development Machine
```
├── src/              (source code)
├── scripts/          (utility scripts)
├── tests/            (test suite)
└── venv/             (virtual environment)
```

### Raspberry Pi
```
/home/pi/epaper-calendar/
├── src/
├── scripts/
├── venv/
├── .env              (configuration)
├── token.json        (OAuth token)
├── events_cache.db   (SQLite cache)
└── credentials.json  (if local OAuth setup)

/etc/systemd/system/
├── epaper-calendar.service
└── epaper-calendar.timer
```

## Future Enhancements

### Phase 2: Enhanced Rendering
- [ ] Weather integration
- [ ] Customizable fonts/colors
- [ ] Multiple language support
- [ ] Event descriptions on display

### Phase 3: Advanced Features
- [ ] Manual refresh button (GPIO)
- [ ] Status LED indicators
- [ ] Network connectivity check
- [ ] Low power sleep modes

### Phase 4: Integration
- [ ] Home automation (Home Assistant)
- [ ] Mobile app sync
- [ ] Push notifications
- [ ] Weather API integration

## Documentation Map

- **README.md** - Project overview
- **QUICKSTART.md** - 5-minute setup
- **docs/SETUP.md** - Development setup
- **docs/OAUTH_SETUP.md** - Google OAuth guide
- **docs/DEPLOYMENT.md** - RPi deployment
- **docs/ARCHITECTURE.md** - This file

---

**Version**: 0.1.0
**Status**: Core infrastructure complete, ready for Phase 2
