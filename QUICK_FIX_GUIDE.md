# Quick Fix Guide - E-Paper Calendar

## The Problem in 30 Seconds
The app is looking for calendars named:
- `your-ashi-calendar-id@gmail.com` ❌ (doesn't exist)
- `your-sindi-calendar-id@gmail.com` ❌ (doesn't exist)

Google Calendar API returns "404 Not Found", app gracefully falls back to empty cache, display shows nothing.

## The Fix in 5 Minutes

### Step 1: Find Calendar IDs
1. Go to https://calendar.google.com
2. Click Settings ⚙️
3. Click "Settings" in dropdown
4. Find "Calendar" on the left
5. Look for the email address (like: `ashi@gmail.com` or `ashi.backup@gmail.com`)

### Step 2: Update .env File
```bash
# Edit the config file
nano .env
```

Change:
```env
# BEFORE (❌ Placeholder)
ASHI_CALENDAR_ID=your-ashi-calendar-id@gmail.com
SINDI_CALENDAR_ID=your-sindi-calendar-id@gmail.com

# AFTER (✅ Actual emails)
ASHI_CALENDAR_ID=ashi@gmail.com
SINDI_CALENDAR_ID=sindi@gmail.com
```

Save with: `Ctrl+O`, Enter, `Ctrl+X`

### Step 3: Test It
```bash
python3 src/main.py
```

Look for in the output:
```
✓ Ashi calendar: online
✓ Sindi calendar: online
✓ Fetched 5 Ashi events, 3 Sindi events
```

**Done!** 🎉

---

## Verification Checklist
- [ ] `.env` file updated with real calendar emails (not "your-...")
- [ ] `credentials.json` exists in project root
- [ ] `token.json` exists in project root
- [ ] App runs without errors: `python3 src/main.py`
- [ ] Tests pass: `python3 -m pytest tests/ -v`
- [ ] Display renders: `python3 scripts/test_display.py`

---

## If It Still Doesn't Work

### Check 1: Calendar IDs
```bash
grep CALENDAR_ID .env
# Should NOT contain "your-"
```

### Check 2: OAuth Files
```bash
ls -la credentials.json token.json
# Both should exist
```

### Check 3: App Output
```bash
python3 src/main.py 2>&1 | grep -E "online|offline|error"
```

### Check 4: Run Tests
```bash
python3 -m pytest tests/ -v
# All 15 should PASS
```

---

## If OAuth Credentials Expired

```bash
# Refresh the token
python3 scripts/setup_oauth.py --refresh

# Or regenerate
python3 scripts/setup_oauth.py --generate
```

---

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| "404 Not Found" in logs | Calendar IDs are wrong or placeholder | Update `.env` with real emails |
| "offline (using cache)" with empty display | App can't reach Google API | Check internet, check calendar IDs |
| "No module named google_auth_oauthlib" | Dependencies not installed | `python3 -m pip install -r requirements.txt` |
| "FutureWarning: You are using Python 3.9..." | Using end-of-life Python | Upgrade to Python 3.10+: `brew install python@3.11` |

---

## Success Indicators

✅ After fix, you should see:
```
2026-02-09 13:03:44 - INFO - Fetching calendar events...
2026-02-09 13:03:45 - INFO - Fetched 5 Ashi events, 3 Sindi events
2026-02-09 13:03:45 - INFO - Ashi calendar: online
2026-02-09 13:03:45 - INFO - Sindi calendar: online
2026-02-09 13:03:45 - INFO - Rendering display...
2026-02-09 13:03:45 - INFO - Update completed in 0.4 seconds
```

---

## Next Steps

1. ✅ **Fix calendar IDs** (you are here)
2. **Deploy to Raspberry Pi** (see `docs/DEPLOYMENT.md`)
3. **Enable systemd timer** (15-minute auto-updates)
4. **Monitor logs** (check `journalctl -u epaper-calendar`)

---

For detailed analysis, see: `CODE_REVIEW_ANALYSIS.md`  
For full documentation, see: `README.md`
