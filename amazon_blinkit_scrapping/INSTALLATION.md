# Installation Guide

Complete step-by-step installation instructions for the Blinkit Product Insights Platform.

## Table of Contents
- [System Requirements](#system-requirements)
- [Installation Steps](#installation-steps)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **Operating System:** macOS 10.14+, Windows 10+, or Linux (Ubuntu 18.04+)
- **Python:** 3.8 or higher
- **RAM:** 4 GB (8 GB recommended)
- **Disk Space:** 500 MB free space
- **Internet:** Stable broadband connection

### Required Software
1. **Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify installation: `python --version` or `python3 --version`

2. **Google Chrome**
   - Download from [google.com/chrome](https://www.google.com/chrome/)
   - Version 90+ recommended

3. **Git** (optional, for cloning)
   - Download from [git-scm.com](https://git-scm.com/downloads/)

## Installation Steps

### Step 1: Clone or Download Repository

**Option A: Using Git**
```bash
git clone https://github.com/anubhav-77-dev/blinkit.git
cd blinkit
```

**Option B: Download ZIP**
1. Visit [https://github.com/anubhav-77-dev/blinkit](https://github.com/anubhav-77-dev/blinkit)
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Open terminal/command prompt in the extracted folder

### Step 2: Create Virtual Environment

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

> **Note:** If you see a "script execution disabled" error on Windows PowerShell:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `selenium` - Browser automation
- `beautifulsoup4` - HTML parsing
- `pandas` - Data manipulation
- `requests` - HTTP library
- `plotly` - Visualization (legacy notebooks)
- `scikit-learn` - ML utilities (legacy notebooks)
- `scipy` - Scientific computing (legacy notebooks)

### Step 4: Verify Chrome Installation

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version

# Windows (PowerShell)
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --version

# Linux
google-chrome --version
```

Expected output: `Google Chrome 118.x.xxxx.xx` (or newer)

### Step 5: Start the Server

```bash
python -m uvicorn app.main:app --reload --port 8000 --app-dir app_backend
```

Expected output:
```
INFO:     Will watch for changes in these directories: ['/path/to/blinkit']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 6: Access the Application

Open your web browser and navigate to:
```
http://localhost:8000
```

You should see the **Blinkit Product Insights** interface.

## Verification

### Test the Web Interface

1. **Enter a Product Query:**
   - Type: `milk`

2. **Enter a Pincode:**
   - Type: `110001`

3. **Click "Fetch Insights"**
   - Wait ~30-60 seconds
   - You should see products listed

### Test the API

```bash
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"pincodes": ["110001"], "query": "milk", "save_html": false}'
```

Expected: JSON response with products array

### Test Health Endpoint

```bash
curl http://localhost:8000/api/health
```

Expected: `{"status":"ok"}`

## Troubleshooting

### Python Not Found

**Error:** `python: command not found`

**Solution:**
- Try `python3` instead of `python`
- Reinstall Python from [python.org](https://www.python.org/)
- On Windows, check "Add Python to PATH" during installation

### pip Install Fails

**Error:** `pip: command not found` or permission errors

**Solutions:**
```bash
# Use python -m pip
python -m pip install -r requirements.txt

# On macOS/Linux, use sudo (not recommended in venv)
sudo pip install -r requirements.txt

# Or upgrade pip first
python -m pip install --upgrade pip
```

### Virtual Environment Issues

**Error:** `venv\Scripts\activate` not working on Windows

**Solution:**
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or use the batch file instead
venv\Scripts\activate.bat
```

### ChromeDriver Not Found

**Error:** `WebDriverException: 'chromedriver' executable needs to be in PATH`

**Solution:**
```bash
# Ensure you have Selenium 4.6+
pip install --upgrade selenium

# Or manually install webdriver-manager
pip install webdriver-manager
```

### Port Already in Use

**Error:** `[Errno 48] Address already in use`

**Solution:**
```bash
# Use a different port
python -m uvicorn app.main:app --reload --port 8001 --app-dir app_backend

# Or kill the process using port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Module Import Errors

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Ensure virtual environment is activated
# You should see (venv) in your terminal prompt

# If not, activate it:
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Then reinstall dependencies
pip install -r requirements.txt
```

### No Products Found

**Error:** API returns empty products array

**Solutions:**

1. **Enable Debug Mode:**
   ```bash
   export BLINKIT_HEADLESS=0  # macOS/Linux
   set BLINKIT_HEADLESS=0     # Windows CMD
   $env:BLINKIT_HEADLESS="0"  # Windows PowerShell
   ```

2. **Check Saved HTML:**
   ```bash
   # Look for saved files
   ls html_pages/blinkit_*/
   
   # Open them in a browser to verify content
   ```

3. **Try Different Queries:**
   - Use common products: `milk`, `bread`, `eggs`
   - Use popular pincodes: `110001` (Delhi), `560001` (Bangalore)

4. **Check Internet Connection:**
   ```bash
   ping blinkit.com
   ```

### Chrome Version Mismatch

**Error:** `SessionNotCreatedException: session not created: This version of ChromeDriver only supports Chrome version XX`

**Solution:**
```bash
# Update Selenium (auto-manages driver)
pip install --upgrade selenium

# Or update Chrome to latest version
```

## Uninstallation

To completely remove the application:

```bash
# Deactivate virtual environment
deactivate

# Remove the project folder
cd ..
rm -rf blinkit  # macOS/Linux
rmdir /s blinkit  # Windows
```

## Next Steps

- Read [README.md](./README.md) for usage examples
- Check [API_GUIDE.md](./API_GUIDE.md) for API documentation
- Run in debug mode: `export BLINKIT_HEADLESS=0`
- Try different product queries and pincodes

## Support

If you encounter issues not covered here:
1. Check existing [GitHub Issues](https://github.com/anubhav-77-dev/blinkit/issues)
2. Open a new issue with:
   - Error message
   - Python version (`python --version`)
   - Operating system
   - Steps to reproduce

---

**Installation complete! 🎉**
