# Peloton 2 Garmin Sync - Releases

Welcome to the Releases page for **Peloton 2 Garmin Sync**! Download the latest version to start syncing your Peloton workouts to Garmin Connect.

---

## 📦 Latest Release

### Version 1.0.0 (February 12, 2026)

**Initial Release** - Full-featured Peloton to Garmin sync application

#### 🎉 What's New

- ✅ Complete workout sync with all metrics
- ✅ Heart rate zones, power, cadence, speed
- ✅ Peloton bearer token authentication
- ✅ Garmin OAuth with MFA support
- ✅ Auto-login capability
- ✅ Batch sync multiple workouts
- ✅ Export workouts as TCX files
- ✅ Modern Fluent Design interface

---

## 💾 Download Options

### Option 1: Windows Installer (Recommended)

**File:** `Peloton2GarminSync-Setup-v1.0.0.exe`  
**Size:** ~45-65 MB  
**SHA256:** `[checksum here]`

**Includes:**
- Automatic installation
- Start Menu shortcut
- Desktop shortcut (optional)
- Uninstaller
- All dependencies bundled

**Installation:**
1. Download the installer
2. Run `Peloton2GarminSync-Setup-v1.0.0.exe`
3. Follow the installation wizard
4. Launch from Start Menu

**Best for:** Most users who want easy installation and updates

---

### Option 2: Portable Executable

**File:** `Peloton2GarminSync.exe`  
**Size:** ~50-70 MB  
**SHA256:** `[checksum here]`

**Includes:**
- Single executable file
- No installation required
- Run from any location
- All dependencies bundled

**Usage:**
1. Download the executable
2. Place in any folder (e.g., `C:\Tools\`)
3. Double-click to run
4. Settings saved to `%USERPROFILE%\.peloton_garmin_sync\`

**Best for:** Users who want portability or don't have admin rights

---

### Option 3: Source Code

**File:** `peloton2garmin-source.zip`  
**Size:** ~128 KB  
**SHA256:** `[checksum here]`

**Includes:**
- Complete Python source code
- Build scripts and spec files
- Documentation

**Requirements:**
- Python 3.11 or later
- pip package manager

**Installation:**
```bash
# Extract the zip file
unzip peloton2garmin-source.zip
cd peloton2garmin-source

# Install dependencies
pip install -r requirements_fluent.txt

# Run the application
python peloton_garmin_fluent_app.py
```

**Best for:** Developers, advanced users, or those who want to audit/modify the code

---

## 📋 What's Included

### All Downloads Include:

✅ **Full Metric Sync**
- Heart rate with zones
- Power output (watts)
- Cadence (RPM)
- Speed and distance
- Calories burned

✅ **Secure Authentication**
- Peloton bearer token
- Garmin OAuth 2.0
- MFA support
- Auto-login

✅ **User-Friendly Features**
- Modern Fluent Design UI
- Batch workout sync
- TCX file export
- Real-time status indicators
- Activity logging

---

## ⚙️ System Requirements

**Operating System:**
- Windows 10 (64-bit) or later
- Windows 11 recommended

**Hardware:**
- 4 GB RAM minimum
- 100 MB free disk space
- Internet connection required

**Software:**
- No additional software needed (installer/portable)
- Python 3.11+ required (source code only)

---

## 🚀 Quick Start

### First-Time Setup

1. **Download** your preferred version above
2. **Install** or run the application
3. **Configure Peloton** (get bearer token via Settings)
4. **Configure Garmin** (login with email/password + MFA)
5. **Sync** your workouts!

### Detailed Instructions

See the [main README](../README.md) for complete setup instructions, including:
- How to get your Peloton bearer token
- Garmin authentication process
- Troubleshooting guide
- FAQ

---

## 🔄 Upgrading from Previous Versions

**This is the first release!** Future updates will include:
- Download the new installer/executable
- Run to automatically update
- Your settings and tokens are preserved
- No need to reconfigure

---

## ✅ Verifying Your Download

To verify the integrity of your download, check the SHA256 hash:

**Windows PowerShell:**
```powershell
Get-FileHash Peloton2GarminSync-Setup-v1.0.0.exe -Algorithm SHA256
```

**Command Prompt:**
```cmd
certutil -hashfile Peloton2GarminSync-Setup-v1.0.0.exe SHA256
```

Compare the output with the SHA256 checksum listed above.

---

## 🔒 Security & Privacy

- ✅ **No cloud services** - runs entirely on your computer
- ✅ **Direct API connections** - to Peloton and Garmin only
- ✅ **Local storage** - credentials saved on your PC only
- ✅ **No telemetry** - no tracking or analytics
- ✅ **Open source** - audit the code yourself

---

## 🐛 Known Issues

### Version 1.0.0

**Minor Issues:**
- ⚠️ "Avg Moving Speed" may display incorrectly in Garmin Connect (cosmetic only, doesn't affect actual data)
- ⚠️ First-time Garmin login may be blocked by Cloudflare (handled automatically with OAuth)

**Workarounds:**
- Speed issue: Main "Avg Speed" is correct; "Avg Moving Speed" can be ignored
- Cloudflare: App handles this automatically; if issues persist, login manually to Garmin Connect first

---

## 📝 Changelog

### Version 1.0.0 (2026-02-12)

**Initial Release**

**Features:**
- Complete Peloton to Garmin workout sync
- Heart rate zones, power, cadence, speed metrics
- Peloton bearer token authentication
- Garmin OAuth with MFA support
- Auto-login functionality
- Batch sync multiple workouts
- TCX file export
- Modern Fluent Design interface
- Real-time sync status
- Activity logging

**Technical:**
- Built with Python 3.11
- PyInstaller single-file executable
- Inno Setup installer
- TCX format for workout data
- Direct API integration

---

## 💬 Support & Feedback

### Need Help?

- 📖 [Read the FAQ](../README.md#faq)
- 🐛 [Report a Bug](https://github.com/rod-trent/Peloton2Garmin/issues/new?labels=bug)
- 💡 [Request a Feature](https://github.com/rod-trent/Peloton2Garmin/issues/new?labels=enhancement)
- 📧 [Contact Support](https://github.com/rod-trent/Peloton2Garmin/issues)

### Found a Bug?

Please report issues with:
- Application version
- Windows version
- Error messages (screenshots)
- Steps to reproduce

### Feature Requests

We'd love to hear your ideas! Please include:
- Detailed description
- Use case
- How it benefits users

---

## 🙏 Thank You!

Thank you for using Peloton 2 Garmin Sync! Your feedback and support help make this app better for everyone.

**Happy syncing!** 🚴‍♂️💪

---

<p align="center">
  <a href="https://github.com/rod-trent/Peloton2Garmin">← Back to Main Repository</a>
</p>

<p align="center">
  <sub>Not affiliated with Peloton Interactive, Inc. or Garmin Ltd.</sub>
</p>
