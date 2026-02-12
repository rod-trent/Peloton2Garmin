# Peloton 2 Garmin Sync Desktop App

<p align="center">
  <img src="https://github.com/rod-trent/Peloton2Garmin/blob/main/Images/P2GIcon.ico" alt="Peloton 2 Garmin Sync" width="128" height="128">
</p>

<p align="center">
  <strong>Seamlessly sync your Peloton workouts to Garmin Connect with complete metrics</strong>
</p>

---

## 🎯 Overview

**Peloton 2 Garmin Sync** is a Windows desktop application that automatically syncs your Peloton workouts to Garmin Connect, preserving all your important metrics including heart rate, power output, cadence, and speed data.

Unlike other sync solutions, this app:
- ✅ **Runs locally** - no cloud services or third-party servers
- ✅ **Preserves all metrics** - heart rate zones, power, cadence, speed
- ✅ **Simple authentication** - OAuth tokens, no password storage
- ✅ **Works reliably** - handles Garmin MFA and Cloudflare protection
- ✅ **Modern UI** - Fluent Design interface

## ✨ Features

### Complete Workout Data Sync

Your Peloton workouts sync to Garmin with **full fidelity**:

| Metric | Description |
|--------|-------------|
| 💓 **Heart Rate** | Average, max, and second-by-second HR with zones |
| ⚡ **Power Output** | Average, max, and continuous power data (watts) |
| 🔄 **Cadence** | RPM tracking throughout the workout |
| 🚴 **Speed** | Average and max speed with continuous tracking |
| 📏 **Distance** | Total distance covered |
| 🔥 **Calories** | Total calories burned |
| ⏱️ **Duration** | Complete workout time |

### Secure Authentication

- **Peloton**: Bearer token authentication (no password needed)
- **Garmin**: OAuth 2.0 with MFA support
- **Auto-login**: Credentials saved securely, automatic reconnection
- **No cloud storage**: All tokens stored locally on your computer

### User-Friendly Interface

- **Modern Fluent Design**: Clean, professional Windows interface
- **Batch Operations**: Sync multiple workouts at once
- **TCX Export**: Save workouts as standard TCX files
- **Status Indicators**: Clear connection status for both services
- **Activity Log**: Real-time sync progress and errors

### Privacy & Security

- 🔒 Direct API connections to Peloton and Garmin
- 🔒 No third-party servers or cloud services
- 🔒 Credentials stored locally only
- 🔒 Open source - audit the code yourself
- 🔒 No analytics or tracking

## 📥 Installation

### Option 1: Windows Installer (Recommended)

1. Download the latest installer from [Releases](../../releases)
   - `Peloton2GarminSync-Setup-v1.0.0.exe`
2. Run the installer
3. Launch from Start Menu or Desktop shortcut

### Option 2: Run from Source

**Requirements:**
- Python 3.11 or later
- pip package manager

**Steps:**
```bash
# Clone the repository
git clone https://github.com/yourusername/peloton-garmin-sync.git
cd peloton-garmin-sync

# Install dependencies
pip install -r requirements_fluent.txt

# Run the application
python peloton_garmin_fluent_app.py
```

## 🚀 Quick Start

### 1️⃣ Configure Peloton

**Get Your Bearer Token:**

1. Click **⚙️ Settings** in the app
2. Click **Get Token (Opens Browser)**
3. Log into Peloton in your browser
4. Press **F12** to open Developer Tools
5. Click the **Network** tab
6. Refresh the page (F5)
7. Click any request in the list
8. Find the **Authorization** header
9. Copy the entire token (starts with `Bearer eyJ...`)
10. Paste into the app and click **Save Token**

> 💡 **Tip**: The token is valid for ~1 year. You'll need to refresh it when it expires.

### 2️⃣ Configure Garmin

1. Click **🔑 Login to Garmin**
2. Enter your Garmin email and password
3. Complete MFA verification if prompted
4. Tokens are saved automatically

> 💡 **Note**: First login may be blocked by Cloudflare. The app handles this automatically with OAuth.

### 3️⃣ Sync Your Workouts

1. Click **📥 Fetch Workouts** to load your recent Peloton workouts
2. Select the workouts you want to sync (checkboxes)
3. Click **🔄 Sync to Garmin**
4. Check Garmin Connect - your workouts are synced with full metrics!

## 📸 Screenshots

### Main Interface
*Modern Fluent Design with workout list and sync controls*

![Main App Window](https://github.com/rod-trent/Peloton2Garmin/blob/main/Images/MainAppWindow.png)

### Settings Panel
*Easy token configuration with browser-based authentication*

![Settings Window](https://github.com/rod-trent/Peloton2Garmin/blob/main/Images/SettingsPage.png)

### Garmin Connect Results
*Complete workout data including HR zones, power, cadence, and speed graphs*

![Garmin Results](https://github.com/rod-trent/Peloton2Garmin/blob/main/Images/ConnectResults.png)

## 🔧 How It Works

### Architecture

```
┌─────────────────┐
│  Peloton API    │
│  (Bearer Token) │
└────────┬────────┘
         │
         │ HTTPS
         ▼
┌─────────────────────────┐
│  Peloton 2 Garmin Sync  │
│  ┌─────────────────┐    │
│  │ Fetch Workouts  │    │
│  │ Convert to TCX  │    │
│  │ Upload to Garmin│    │
│  └─────────────────┘    │
└────────┬────────────────┘
         │
         │ HTTPS (OAuth)
         ▼
┌─────────────────┐
│  Garmin Connect │
│  (OAuth Tokens) │
└─────────────────┘
```

### Data Flow

1. **Fetch**: Retrieve workout data from Peloton API
2. **Convert**: Transform to TCX format (Training Center XML)
3. **Upload**: Send to Garmin Connect via OAuth API
4. **Verify**: Garmin processes and displays workout

### File Format

Workouts are converted to **TCX (Training Center XML)** format:
- Industry standard for fitness data
- Supported by Garmin, Strava, TrainingPeaks, etc.
- Contains all metrics with timestamps
- Can be exported and imported anywhere

## ❓ FAQ

<details>
<summary><strong>Is this safe to use?</strong></summary>

Yes! The app:
- Uses official Peloton and Garmin APIs
- Runs completely locally on your computer
- Makes direct HTTPS connections (no middleman)
- Doesn't collect or transmit any data elsewhere
- Is open source - you can review all the code

</details>

<details>
<summary><strong>Will I get banned from Peloton or Garmin?</strong></summary>

No. The app uses the same APIs that:
- Official mobile apps use
- Thousands of users already use for syncing
- Are documented and publicly available

Both Peloton and Garmin allow third-party integrations.

</details>

<details>
<summary><strong>Why do I need a bearer token instead of username/password?</strong></summary>

Bearer tokens are more secure:
- Don't require storing your password
- Can be easily revoked if compromised
- Have limited scope and expiration
- Are the recommended authentication method

</details>

<details>
<summary><strong>How often do I need to update my Peloton token?</strong></summary>

Peloton bearer tokens typically last **~1 year**. When it expires, just get a new one using the same process.

</details>

<details>
<summary><strong>Can I sync old workouts?</strong></summary>

Yes! The app fetches your 50 most recent workouts. You can select and sync any of them, even workouts from months ago.

</details>

<details>
<summary><strong>Does this work with Peloton Bike, Bike+, Tread, Row?</strong></summary>

Currently tested and optimized for **Peloton Bike** workouts. Other equipment types should work but may need adjustments for specific metrics.

</details>

<details>
<summary><strong>Can I sync to Strava instead?</strong></summary>

You can:
1. Export workouts as TCX files
2. Manually upload to Strava

Or connect Garmin to Strava for automatic forwarding of synced workouts.

</details>

<details>
<summary><strong>Why is the executable so large (50-70 MB)?</strong></summary>

PyInstaller bundles the entire Python runtime and all dependencies into a single file for easy distribution. This is normal for Python desktop apps.

</details>

<details>
<summary><strong>My antivirus flags the executable - is it safe?</strong></summary>

This is common for unsigned executables. The app is safe - you can:
- Review the source code yourself
- Build from source
- Submit false positive reports to antivirus vendors
- Consider a code-signed version for production use

</details>

## 🛠️ Troubleshooting

### Peloton Token Issues

**Problem**: "Invalid bearer token" error

**Solutions**:
- Token may have expired (get a new one)
- Make sure you copied the ENTIRE token including "Bearer "
- Check for extra spaces or line breaks
- Try refreshing the token

### Garmin Login Issues

**Problem**: Can't login to Garmin

**Solutions**:
- First login must include MFA verification
- Check that email and password are correct
- Try logging in manually to Garmin Connect first
- OAuth tokens may have expired - login again

### Sync Failures

**Problem**: Workouts won't sync

**Solutions**:
- Check both service status indicators are green (●)
- Verify internet connection
- Garmin may reject duplicate workouts (delete from Garmin first)
- Check the activity log for specific error messages

### Performance Issues

**Problem**: App is slow or freezing

**Solutions**:
- Close and restart the app
- Check system resources (Task Manager)
- Delete old workout cache: `~/.peloton_garmin_sync/`
- Update to latest version

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Report Bugs
- Open an [issue](../../issues)
- Include error messages and screenshots
- Describe steps to reproduce

### Suggest Features
- Open an [issue](../../issues) with the `enhancement` label
- Describe the feature and use case
- Explain how it benefits users

### Submit Code
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/peloton-garmin-sync.git
cd peloton-garmin-sync

# Install dependencies
pip install -r requirements_fluent.txt

# Run in development mode
python peloton_garmin_fluent_app.py

# Build executable
pyinstaller peloton_garmin_sync.spec
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## 🙏 Acknowledgments

**Built with:**
- [Python](https://www.python.org/) - Programming language
- [tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework
- [garminconnect](https://github.com/cyberjunky/python-garminconnect) - Garmin API wrapper
- [garth](https://github.com/matin/garth) - Garmin OAuth library
- [PyInstaller](https://www.pyinstaller.org/) - Executable builder
- [Inno Setup](https://jrsoftware.org/isinfo.php) - Installer creator

**Special Thanks:**
- Peloton API community for documentation
- garminconnect contributors for the excellent library
- All beta testers and early users
- Everyone who reported issues and suggested features

## 🔗 Links

- [Report Bug](../../issues/new?labels=bug)
- [Request Feature](../../issues/new?labels=enhancement)
- [Releases](https://github.com/rod-trent/Peloton2Garmin/tree/main/Releases)

## 💬 Support

Need help? Have questions?

- 📖 Check the [FAQ](#faq) section
- 🐛 Search [existing issues](../../issues)
- 💬 Open a [new issue](../../issues/new)
- 📧 Contact: [On X](https://x.com/rodtrent], [on LinkedIn](https://www.linkedin.com/in/rodtrent/), [on Substack](https://rodtrent.com)

---

<p align="center">
  Made with ❤️ for the Peloton and Garmin communities
</p>

<p align="center">
  <sub>Not affiliated with Peloton Interactive, Inc. or Garmin Ltd.</sub>
</p>
