# Google Calendar OAuth Setup

Complete guide to set up Google OAuth credentials for calendar access.

## What You Need

1. Google account with Google Calendar access
2. Google Cloud Project (free tier OK)
3. OAuth 2.0 Desktop Client credentials

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project:
   - Click "Select a Project" → "New Project"
   - Enter name: `epaper-calendar`
   - Click "Create"

3. Wait for project to be created, then select it

## Step 2: Enable Google Calendar API

1. In the Cloud Console, click "Enabled APIs and services"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "Credentials" (left sidebar)
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: "External"
   - Fill in required fields:
     - App name: `E-Paper Calendar Dashboard`
     - User support email: (your email)
     - Developer contact: (your email)
   - Scopes: Search for and add `calendar.readonly`
   - Save and continue
4. Back in "Create OAuth client ID":
   - Application type: "Desktop application"
   - Name: `epaper-calendar`
   - Click "Create"

## Step 4: Download Credentials

1. On the "OAuth 2.0 Client IDs" page, find your desktop app
2. Click the download button (⬇️ icon)
3. This downloads `client_secret_XXXXX.json`

## Step 5: Add Credentials to Project

```bash
# Rename the downloaded file
mv ~/Downloads/client_secret_*.json /path/to/epaper-calendar/credentials.json

# Verify
ls -la credentials.json
```

## Step 6: Generate OAuth Token

```bash
python scripts/setup_oauth.py --generate
```

This will:
1. Open your browser to Google's authorization page
2. Ask to authorize the app
3. Generate `token.json` locally
4. Save credentials securely

## Step 7: Verify Setup

```bash
python scripts/setup_oauth.py --verify
```

Expected output:
```
✓ Credentials file: ./credentials.json
✓ Token file: ./token.json
✓ Token is valid (scopes: 1 scope(s))
✓ Token is not expired
```

## Important Notes

### Security
- **Never commit** `credentials.json` or `token.json` to Git
- They are already in `.gitignore` for protection
- Treat them like passwords
- The OAuth token is specific to your Google account

### Scopes
- This app requests `calendar.readonly` only
- The app cannot modify or delete calendar events
- The app cannot access other Google services

### Token Refresh
- Token expires after some time
- The app automatically refreshes it
- If manual refresh is needed:
  ```bash
  python scripts/setup_oauth.py --refresh
  ```

### Multiple Calendars
- Each calendar is a separate `calendar_id` (email address)
- You need to authorize your account once
- Then configure both calendar IDs in `.env`

Example `.env`:
```
ASHI_CALENDAR_ID=ashi@gmail.com
SINDI_CALENDAR_ID=sindi@gmail.com
```

### Troubleshooting

**"Credentials file not found"**
- Run Step 5 to place `credentials.json` in project root

**"Redirect URI mismatch" error**
- Make sure credentials are for "Desktop application" type
- Not for "Web application"

**"Invalid client" error**
- Delete `token.json` and `credentials.json`
- Download fresh credentials from Google Cloud Console
- Run `setup_oauth.py --generate` again

**Token keeps expiring**
- Check that `token.json` exists and is readable
- Verify `GOOGLE_CALENDAR_TOKEN_PATH` in `.env`
- Manual refresh: `python scripts/setup_oauth.py --refresh`

## Revoking Access

To revoke the app's access to your Google Calendar:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Find "E-Paper Calendar Dashboard" under "Third-party apps with account access"
3. Click it and select "Remove access"
4. Delete local `token.json` and `credentials.json`

## Testing OAuth

```bash
# List available calendars
python -c "
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pickle

with open('token.json', 'rb') as f:
    creds = pickle.load(f)

service = build('calendar', 'v3', credentials=creds)
calendars = service.calendarList().list().execute()
for cal in calendars['items']:
    print(f\"{cal['summary']}: {cal['id']}\")
"
```

This shows all available calendars and their IDs.
