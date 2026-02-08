# Getting Started with E-Paper Calendar Dashboard

Welcome! This guide will help you understand the project structure and choose the right documentation for your needs.

## What Is This Project?

A Raspberry Pi application that displays Google Calendar events on a 7.5" e-paper display. Updates automatically every 15 minutes with a 6-week calendar grid and today's upcoming events.

**Status**: ✅ **Production Ready** (v0.1.0)

## Choose Your Path

### 🚀 I Want to Deploy NOW (30 minutes)

**Follow this exact sequence:**

1. **Read:** [QUICKSTART.md](QUICKSTART.md) (5 min)
   - Get overview of what you need
   - Local setup and testing on your dev machine

2. **Read:** [docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md) (10 min)
   - Generate Google Calendar credentials
   - Create OAuth token

3. **Read:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) (10 min)
   - Deploy to Raspberry Pi
   - Configure and test

4. **Reference:** [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
   - Follow checklist to verify everything works

**Total**: ~35 minutes to working calendar on your RPi

---

### 🔍 I Want to Understand the System First

**Read in this order:**

1. **[README.md](README.md)** (5 min)
   - Project overview
   - Features and architecture

2. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** (15 min)
   - How components work together
   - Data flow and error handling
   - System performance specs

3. **[docs/SETUP.md](docs/SETUP.md)** (10 min)
   - Development environment
   - Understanding the codebase
   - Running tests

4. **Then follow the deployment path above**

**Total**: ~40 minutes to understand + deploy

---

### ❓ Something Went Wrong

**Check in this order:**

1. **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** ⭐ Your best friend
   - 50+ common issues and solutions
   - Organized by component (Python, OAuth, Display, RPi, etc.)
   - Debugging tools and commands

2. **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)**
   - Verify you completed all steps
   - Find what you might have missed

3. **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**
   - Review the detailed steps
   - Check if you're following correctly

---

### 📚 I'm a Developer / Want Full Details

**Read everything in order:**

1. [README.md](README.md) - Overview
2. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
3. [docs/SETUP.md](docs/SETUP.md) - Development setup
4. [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - RPi deployment
5. [docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md) - OAuth details
6. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Verification
7. [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Problem solving
8. Source code: `src/` folder
9. Tests: `tests/` folder

---

## File Guide

### Quick Reference

| File | Purpose | Read Time |
|------|---------|-----------|
| [README.md](README.md) | Project overview, features, quick commands | 5 min |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute local setup guide | 5 min |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | v0.1.0 release details and features | 5 min |
| [GETTING_STARTED.md](GETTING_STARTED.md) | This file - navigation guide | 5 min |

### Documentation Files (docs/ folder)

| File | Purpose | Read Time |
|------|---------|-----------|
| [docs/SETUP.md](docs/SETUP.md) | Full dev environment setup | 10 min |
| [docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md) | Google OAuth credential generation | 10 min |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Step-by-step RPi deployment | 15 min |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and components | 15 min |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | 50+ solutions to common issues | Reference |

### Checklists

| File | Purpose | Use When |
|------|---------|----------|
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Step-by-step verification | Following each phase |
| [PHASE_1_COMPLETION.md](PHASE_1_COMPLETION.md) | What's included in v0.1.0 | Understanding scope |

### Configuration

| File | Purpose |
|------|---------|
| [.env.example](.env.example) | Configuration template (copy to .env) |
| [requirements.txt](requirements.txt) | Python dependencies |
| [.gitignore](.gitignore) | Protects secrets (credentials, tokens) |

### Application Files

| Folder | Contents |
|--------|----------|
| [src/](src/) | Core application (7 Python modules) |
| [scripts/](scripts/) | Utility scripts (setup, deploy, test) |
| [tests/](tests/) | Unit tests (15 tests, all passing) |
| [systemd/](systemd/) | Service and timer definitions |
| [docs/](docs/) | Documentation |

---

## Common Questions

### Q: Do I need Raspberry Pi to get started?
**A:** No. You can test locally on any machine with Python 3.8+. This is actually recommended - test locally first, then deploy to RPi.

### Q: How long does deployment take?
**A:** ~30 minutes total:
- 10 min: Google OAuth setup (one-time)
- 10 min: Local testing
- 10 min: RPi deployment and configuration

### Q: What if I don't have a Waveshare display?
**A:** The display renderer runs in simulator mode. You'll see `test_display.png` generated. Good for testing!

### Q: Can I customize the display colors/layout?
**A:** Yes! Edit `src/display_renderer.py` to modify colors, fonts, or layout.

### Q: What if I have more than 2 calendars?
**A:** Edit `src/calendar_fetcher.py` to add more calendar IDs. The renderer will need updates too.

### Q: Can I change the 15-minute update interval?
**A:** Yes! Edit `UPDATE_INTERVAL` in `.env` or the systemd timer.

### Q: What if something breaks?
**A:** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) has 50+ solutions. Start there!

---

## Quick Command Reference

### Local Development
```bash
# Clone
git clone https://github.com/hopehubris/epaper-calendar.git
cd epaper-calendar

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
python scripts/setup_oauth.py --generate

# Test
python scripts/test_display.py
pytest tests/ -v

# Run
python src/main.py
```

### RPi Deployment
```bash
# From dev machine
bash scripts/deploy.sh pi 192.168.1.xxx

# On RPi - Monitor
ssh pi@192.168.1.xxx
journalctl -u epaper-calendar -f

# On RPi - Check status
systemctl status epaper-calendar.timer
systemctl list-timers epaper-calendar*
```

---

## Learning Path

### Beginner (Just want it working)
1. QUICKSTART.md → docs/OAUTH_SETUP.md → docs/DEPLOYMENT.md
2. Follow DEPLOYMENT_CHECKLIST.md
3. If issues: docs/TROUBLESHOOTING.md

### Intermediate (Understand the system)
1. README.md → docs/ARCHITECTURE.md
2. docs/SETUP.md → Review source code
3. Deploy following DEPLOYMENT_CHECKLIST.md
4. Customize colors/layout as needed

### Advanced (Full understanding)
1. Read all documentation
2. Study source code in src/
3. Review tests/ and understand test strategy
4. Extend with Phase 2 features
5. Contribute to GitHub repository

---

## Project Structure at a Glance

```
epaper-calendar/
│
├── 📄 README.md                   ← Start here
├── 📄 QUICKSTART.md               ← 5-minute setup
├── 📄 GETTING_STARTED.md          ← You are here
├── 📄 RELEASE_NOTES.md            ← What's included
├── 📄 DEPLOYMENT_CHECKLIST.md     ← Verification
│
├── src/                           ← Application code (7 modules)
│   ├── main.py                    ← Entry point
│   ├── calendar_fetcher.py        ← Google Calendar API
│   ├── display_renderer.py        ← PIL rendering
│   ├── cache_manager.py           ← SQLite cache
│   ├── waveshare_driver.py        ← Display hardware
│   ├── config.py                  ← Configuration
│   └── utils.py                   ← Utilities
│
├── scripts/                       ← Tools
│   ├── setup_oauth.py             ← Generate credentials
│   ├── test_display.py            ← Display test
│   └── deploy.sh                  ← RPi deployment
│
├── tests/                         ← Unit tests (15 total)
│   ├── test_cache.py
│   ├── test_config.py
│   └── test_renderer.py
│
├── docs/                          ← Complete documentation
│   ├── SETUP.md                   ← Development setup
│   ├── OAUTH_SETUP.md             ← Google OAuth guide
│   ├── DEPLOYMENT.md              ← RPi deployment
│   ├── ARCHITECTURE.md            ← System design
│   └── TROUBLESHOOTING.md         ← Problem solutions
│
├── systemd/                       ← Service files
│   ├── epaper-calendar.service
│   └── epaper-calendar.timer
│
├── requirements.txt               ← Python dependencies
├── .env.example                   ← Config template
└── .gitignore                     ← Protects secrets
```

---

## Success Indicators

Your deployment is working when you see:

- ✓ `test_display.py` generates a PNG image
- ✓ `pytest` shows 15/15 tests passing
- ✓ `python src/main.py` runs without errors
- ✓ Display shows calendar grid with events
- ✓ `journalctl -u epaper-calendar` shows successful updates
- ✓ Display updates automatically every 15 minutes
- ✓ Service survives RPi reboot

---

## Need Help?

1. **Deployment issue?** → [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
2. **OAuth problem?** → [docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md)
3. **Something broken?** → [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
4. **Want details?** → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
5. **Lost?** → Read this file again! 😄

---

## Next Steps

**Choose one:**

- 🚀 **Fast track**: Read [QUICKSTART.md](QUICKSTART.md) and deploy
- 📚 **Learn first**: Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) then deploy
- 🔧 **Customize**: Explore [src/](src/) folder and modify as needed
- ✅ **Verify**: Use [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) to ensure everything works

---

## Version & Status

- **Version**: v0.1.0
- **Status**: Production Ready ✅
- **Released**: February 8, 2026
- **Tests**: 15/15 passing
- **Documentation**: Complete
- **Support**: Comprehensive troubleshooting guide included

---

## Enjoy! 📅

You're about to deploy a beautiful, automatic calendar display. Questions? Check the docs. Stuck? Try troubleshooting. Still stuck? It's probably something simple - look at the logs with `journalctl -u epaper-calendar -f`.

**Happy deploying!** 🎉
