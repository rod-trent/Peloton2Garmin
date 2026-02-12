# Peloton 2 Garmin Sync

Automatically sync your Peloton workouts to Garmin Connect with full metrics including heart rate, power, cadence, and speed.

## Features

✅ **Automatic Authentication**
- Secure Peloton bearer token authentication
- Garmin OAuth with MFA support
- Auto-login on startup (no password storage)

✅ **Complete Workout Data**
- Heart rate with zones
- Power/output (watts)
- Cadence (RPM)
- Speed and distance
- Calories burned
- Workout duration

✅ **Easy to Use**
- Modern Fluent Design interface
- One-click sync to Garmin
- Batch sync multiple workouts
- Export workouts as TCX files

## Installation

### Windows Installer (Recommended)

1. Download `Peloton2GarminSync-Setup-v1.0.0.exe`
2. Run the installer
3. Launch from Start Menu or Desktop

### From Source

**Requirements:**
- Python 3.11 or later
- pip package manager

**Install:**

```bash
# Clone or download the repository
cd peloton-garmin-sync

# Install dependencies
pip install -r requirements_fluent.txt

# Run the app
python peloton_garmin_fluent_app.py
```

## Quick Start

### 1. Configure Peloton

**Get Your Bearer Token:**
1. Click **Settings** in the app
2. Click **Get Token (Opens Browser)**
3. Log into Peloton in the browser
4. Press **F12** to open Developer Tools
5. Go to **Network** tab
6. Refresh the page
7. Click any request
8. Find **Authorization** header
9. Copy the token (starts with "Bearer eyJ...")
10. Paste into the app and click **Save Token**

### 2. Configure Garmin

1. Click **Login to Garmin**
2. Enter your Garmin email and password
3. Complete MFA if prompted
4. OAuth tokens are saved automatically

### 3. Sync Workouts

1. Click **📥 Fetch Workouts** to load your recent Peloton workouts
2. Select workouts you want to sync (click checkboxes)
3. Click **🔄 Sync to Garmin**
4. Check Garmin Connect - your workouts are there!

## Troubleshooting

### Peloton Token Issues

**Problem:** "Invalid bearer token" error

**Solution:**
1. Token expires after ~1 year
2. Get a new token using Settings → Get Token
3. Make sure you copy the ENTIRE token including "Bearer"

### Garmin Login Issues

**Problem:** Can't login to Garmin

**Solutions:**
- **Cloudflare blocks automated login**: First login must be manual with MFA
- **OAuth tokens expired**: Click "Login to Garmin" again
- **Check email/password**: Verify credentials are correct
- **MFA not working**: Check your phone/email for code

## Privacy & Security

### What's Stored Locally

**Config file** (`~/.peloton_garmin_sync/config.json`):
```json
{
  "peloton_bearer_token": "eyJ...",
  "garmin_email": "user@example.com"
}
```

**OAuth tokens** (`~/.peloton_garmin_sync/garmin_tokens/`):
- `oauth1_token`
- `oauth2_token`

### What's NOT Stored
- ❌ Garmin password (never saved)
- ❌ Peloton password (not needed)
- ❌ MFA codes (one-time use)

### Data Transmission
- Direct connection to Peloton API (HTTPS)
- Direct connection to Garmin Connect API (HTTPS)
- No third-party servers
- No analytics or tracking

## Building from Source

### Create Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller peloton_garmin_sync.spec

# Executable will be in dist/ folder
```

### Create Installer

**Requirements:**
- Inno Setup 6.0 or later

**Build:**
1. Build executable first (see above)
2. Open `setup.iss` in Inno Setup
3. Click **Build → Compile**
4. Installer will be in `installer/` folder

## License

MIT License - see LICENSE.txt for details

## Changelog

### Version 1.0.0 (2026-02-12)
- Initial release
- Peloton bearer token authentication
- Garmin OAuth with MFA
- Full workout metrics sync
- TCX export
- Auto-login
- Batch sync
