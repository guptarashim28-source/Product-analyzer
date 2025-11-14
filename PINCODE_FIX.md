# How to Fix Pincode Issue - Get Correct Products for Your Location

## Problem
Products shown are from wrong location (default is Ahmedabad 380015). Yesterday it worked, today it doesn't.

## Why This Happens
Blinkit stores your location in browser cookies. Yesterday's location was cleared/expired, so now it's using the default location.

## ✅ SOLUTION: Manual Location Mode

### Step 1: Enable Manual Mode
1. Open file: `bl/amazon_blinkit_scrapping/.env`
2. Find line: `MANUAL_LOCATION_MODE=false`
3. Change to: `MANUAL_LOCATION_MODE=true`
4. Save the file

### Step 2: Restart Backend
1. Stop the backend (Ctrl+C in the terminal running uvicorn)
2. Start it again:
```powershell
cd C:\Users\Rashi\OneDrive\Desktop\GAIM\bl\amazon_blinkit_scrapping
C:/Users/Rashi/OneDrive/Desktop/GAIM/.venv/Scripts/python.exe -m uvicorn backend:app --reload --port 8000
```

### Step 3: Use the App
1. Go to Streamlit (http://localhost:8501)
2. Enter your desired pincode (e.g., 400050)
3. Click "Start Analysis"
4. **A BROWSER WINDOW WILL OPEN** - Don't close it!
5. On the Blinkit page, **manually click the location and change it to your pincode**
6. Wait - the scraper will continue automatically after 15 seconds
7. The browser will close automatically when done

### Step 4: (Optional) Turn Off Manual Mode
Once you've set the location once, Blinkit will remember it in cookies. You can:
1. Change `MANUAL_LOCATION_MODE=true` back to `false`
2. Restart backend
3. Future scrapes will use the saved location

## Quick Test
To test if your location is set correctly:
```powershell
$body = @{ category = "snacks"; pincode = "400050"; max_products = 5 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/test-scraper" -Method Post -Body $body -ContentType "application/json"
```

Compare products with what you see on Blinkit website for that pincode.

## Why This Works
- Manual mode opens a VISIBLE browser window
- You manually set the location (which Blinkit accepts)
- Blinkit saves it in cookies
- The scraper uses those cookies for subsequent requests
