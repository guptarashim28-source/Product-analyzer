# Blinkit Product Insights Platform

A full-stack web application that scrapes and analyzes product data from Blinkit across multiple pincodes, providing FMCG firms with competitive intelligence including pricing, brand frequency, and price-per-100g comparisons.

![Platform](https://img.shields.io/badge/Platform-Web-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal)
![Selenium](https://img.shields.io/badge/Selenium-4.0+-orange)

## 🎯 Overview

This platform enables FMCG companies to:
- **Compare products** across multiple pincodes simultaneously
- **Analyze competitor pricing** with automatic price-per-100g normalization
- **Track brand frequency** in top 10 search results per location
- **Export insights** to CSV for further analysis
- **Automate data collection** without manual intervention

Perfect for market research, competitive analysis, and pricing strategy.

## ✨ Features

### Core Functionality
- ✅ **Multi-Pincode Scraping** - Query multiple locations in one request
- ✅ **Automated Location Setting** - No manual pincode entry required
- ✅ **Smart Product Parsing** - Extracts name, brand, weight, price with fallbacks
- ✅ **Price Normalization** - Automatic price-per-100g calculation
- ✅ **Brand Analytics** - Tracks which brands appear most in top 10
- ✅ **CSV Export** - Download results for offline analysis
- ✅ **Debug Mode** - Save raw HTML for troubleshooting

### Technical Highlights
- 🚀 FastAPI backend with async support
- 🎨 Clean, responsive frontend (vanilla JS, no build tools)
- 🤖 Headless Selenium automation with anti-detection
- 📊 Real-time scraping with progress feedback
- 🔄 Robust error handling and fallback selectors

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │  HTML/CSS/JS (served by FastAPI)
│   (Browser)     │
└────────┬────────┘
         │ HTTP POST /api/scrape
         ▼
┌─────────────────┐
│  FastAPI        │  REST API + Static File Server
│  Backend        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Selenium       │  Headless Chrome automation
│  Scraper        │  - Set pincode automatically
└────────┬────────┘  - Scroll & parse products
         │
         ▼
┌─────────────────┐
│  BeautifulSoup  │  HTML parsing with fallback selectors
│  Parser         │
└─────────────────┘
```

## 📋 Prerequisites

- **Python 3.8+**
- **Google Chrome** (latest version)
- **ChromeDriver** (auto-managed by Selenium 4.6+)
- **pip** (Python package manager)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/anubhav-77-dev/blinkit.git
cd blinkit
```

### 2. Create Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Server

```bash
python -m uvicorn app.main:app --reload --port 8000 --app-dir app_backend
```

### 5. Open the App

Navigate to [http://localhost:8000](http://localhost:8000) in your browser.

## 📖 Usage

### Web Interface

1. **Enter Product Type**
   - Example: `protein bar`, `snacks`, `milk`

2. **Enter Pincodes**
   - Comma or newline separated
   - Example: `110001, 560001, 400001`

3. **Submit & Wait**
   - Takes ~30-60 seconds per pincode
   - Progress shown in browser

4. **View Results**
   - Summary statistics
   - Brand frequency in top 10
   - Full product table with price/100g

5. **Download CSV**
   - Click "Download CSV" to export results

### API Usage

#### Scrape Products

```bash
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "pincodes": ["110001", "560001"],
    "query": "protein bar",
    "save_html": false,
    "max_scrolls": 40
  }'
```

#### Export to CSV

```bash
curl -X POST http://localhost:8000/api/export-csv \
  -H "Content-Type: application/json" \
  -d '{
    "pincodes": ["110001"],
    "query": "snacks"
  }' \
  --output results.csv
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BLINKIT_HEADLESS` | `1` | Set to `0` to show browser window (debugging) |

### Example: Debug Mode

```bash
# See the browser in action
export BLINKIT_HEADLESS=0
python -m uvicorn app.main:app --reload --port 8000 --app-dir app_backend
```

## 📂 Project Structure

```
.
├── app_backend/
│   └── app/
│       ├── main.py                 # FastAPI app + API routes
│       ├── frontend/               # Static web UI
│       │   ├── index.html
│       │   ├── main.js
│       │   ├── styles.css
│       │   └── favicon.svg
│       ├── scraper/
│       │   ├── __init__.py
│       │   └── blinkit_scraper.py  # Selenium automation
│       └── utils/
│           ├── __init__.py
│           └── weights.py          # Price/weight parsing
├── amazon_scraper.py               # Legacy Amazon scraper
├── blinkit_scraper.py              # Legacy Blinkit scraper
├── download_pages.py               # Legacy download utility
├── blinkit_scraper_combined.py    # Standalone combined scraper
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🛠️ Troubleshooting

### No Products Found

**Symptoms:** API returns empty products array

**Solutions:**
1. Run in debug mode:
   ```bash
   export BLINKIT_HEADLESS=0
   ```

2. Check saved HTML files:
   ```bash
   ls html_pages/blinkit_*/
   ```

3. Verify pincode is valid for Blinkit delivery

4. Try a different product query (e.g., `milk` instead of niche products)

### ChromeDriver Issues

**Symptoms:** `WebDriverException: chromedriver not found`

**Solution:**
```bash
# Update Selenium to 4.6+ for auto-management
pip install --upgrade selenium
```

### Location Not Setting

**Symptoms:** Same products for all pincodes

**Solution:**
- Run with `BLINKIT_HEADLESS=0` to watch automation
- Check terminal output for location warnings
- Verify saved HTML files differ per pincode

## 📊 Data Schema

### Product Object

```python
{
  "pincode": str,           # Location pincode
  "rank": int,              # Position in search results (1-based)
  "brand": str,             # Extracted brand name
  "name": str,              # Full product name
  "weight": str,            # Original weight text (e.g., "500 g")
  "grams": float | None,    # Parsed weight in grams
  "price": float | None,    # Price in rupees
  "price_text": str,        # Original price text
  "price_per_100g": float | None  # Normalized price
}
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Users must:
- Respect Blinkit's Terms of Service
- Implement rate limiting to avoid server load
- Not use for commercial scraping without permission
- Comply with data protection regulations

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Automation powered by [Selenium](https://www.selenium.dev/)
- Parsing via [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

## 📧 Support

For issues or questions:
- Open an [Issue](https://github.com/anubhav-77-dev/blinkit/issues)

---

**Made with ❤️ for FMCG market research**
