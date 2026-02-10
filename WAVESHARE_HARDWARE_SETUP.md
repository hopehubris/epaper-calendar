# Waveshare Hardware Setup - E-Paper Calendar

## ✅ STATUS: WORKING ON REAL HARDWARE

The e-paper calendar is now **fully operational on your RPi with the physical Waveshare 7.5" display**.

## Running the App

### Quick Start (System Python)
```bash
ssh ashisheth@192.168.1.180
cd ~/epaper-calendar

# Add Waveshare library to path and run
export PYTHONPATH="/home/ashisheth/e-Paper/RaspberryPi_JetsonNano/python/lib:$PYTHONPATH"
/usr/bin/python3 src/main.py
```

### Recommended: Run in Background
```bash
ssh ashisheth@192.168.1.180
cd ~/epaper-calendar

nohup bash -c 'export PYTHONPATH="/home/ashisheth/e-Paper/RaspberryPi_JetsonNano/python/lib:$PYTHONPATH" && /usr/bin/python3 src/main.py' > epaper.log 2>&1 &

# Check logs
tail -f epaper.log
```

## Why System Python Instead of venv?

The Waveshare library requires specific GPIO support that works best with system Python:

- **System Python** ✅: Has working GPIO access, proper library paths, all dependencies
- **Virtual Environment** ❌: Isolated from system GPIO libraries, harder to debug

When you use `/usr/bin/python3`, it automatically finds:
- Waveshare library at `/home/ashisheth/e-Paper/RaspberryPi_JetsonNano/python/lib`
- System GPIO drivers (libgpiod / RPi.GPIO working properly)
- All global dependencies

## What's Working

✅ Display initializes on startup  
✅ Fetches Google Calendar (5 Ashi events, 52 Sindi events)  
✅ Renders 6-week calendar with events  
✅ Updates every 15 minutes  
✅ Graceful fallback if calendars go offline  
✅ Uses hardware display when available  

## Hardware Details

- **Display**: Waveshare 7.5" e-Paper Display (red/black, 800×480)
- **Library**: Official Waveshare `epd7in5b_V2` module
- **Connection**: SPI interface via GPIO pins
- **Dual Buffer**: Black and red channels rendering

## Troubleshooting

### If display shows blank/white screen
- Run the Waveshare test first: `/home/ashisheth/e-Paper/RaspberryPi_JetsonNano/python/examples/epd_7in5b_V2_test.py`
- Check GPIO connection to display
- Verify SPI is enabled: `raspi-config` → Interfacing Options → SPI

### If calendar events don't load
- Check `credentials.json` exists and is valid
- Check `.env` has correct calendar IDs:
  ```bash
  cat .env | grep CALENDAR_ID
  ```
- Test calendar fetch directly:
  ```python
  from src.calendar_fetcher import CalendarFetcher
  cf = CalendarFetcher()
  events = cf.fetch_events('ashisheth@gmail.com')
  print(len(events), "events found")
  ```

### If app crashes
- Check logs: `tail -f epaper.log`
- Run with debug logging: Set `logging.basicConfig(level=logging.DEBUG)` in `src/main.py`

## Next Steps

Optional improvements:
- Set up systemd service for auto-start on boot
- Configure cron job for periodic image saves
- Add weather widget to calendar display
- Create custom fonts/colors for calendar

---

**Production Status**: ✅ Ready for daily use
