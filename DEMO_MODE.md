# 🛒 Blinkit Product Analyzer - Demo Mode Guide

## 📺 What is Demo Mode?

Demo mode allows you to **deploy and showcase** the full Blinkit Product Analyzer without requiring:
- ✅ Selenium/Chrome installation
- ✅ API keys (Gemini AI, NewsAPI)
- ✅ Complex environment setup

Perfect for:
- **Streamlit Cloud deployment** (doesn't support Selenium)
- **Client demos** and presentations
- **Quick showcases** without infrastructure

## 🚀 Quick Start

### Option 1: View Demo Locally

```bash
# 1. Clone the repository
git clone https://github.com/guptarashim28-source/Product-analyzer.git
cd bl

# 2. Install dependencies
pip install streamlit

# 3. Run demo mode
streamlit run streamlit_demo.py
```

The app will automatically detect missing dependencies and switch to **DEMO MODE**, showing pre-analyzed results for **Snacks (Pincode: 380015)**.

### Option 2: Deploy to Streamlit Cloud

1. **Fork/Clone** this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"**
4. Select:
   - **Repository**: `your-username/Product-analyzer`
   - **Branch**: `main`
   - **Main file path**: `bl/streamlit_demo.py`
5. Click **"Deploy"**

✅ Demo mode will activate automatically (no API keys needed)!

## 🎯 Features in Demo Mode

### What You Can See:
- ✅ **Full UI/UX** - All tabs and components visible
- ✅ **Pre-analyzed Data** - Real results from snacks analysis
- ✅ **AI Insights** - Gap analysis, news insights, recommendations
- ✅ **Interactive Exploration** - Navigate all features

### What's Limited:
- ⚠️ **Category**: Locked to "snacks"
- ⚠️ **Pincode**: Locked to "380015"
- ⚠️ **Data**: Pre-saved (not live scraping)

## 🔓 Enable Live Mode

To analyze **any category/pincode** with live scraping:

### 1. Get API Keys

**Gemini AI** (Required):
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key (starts with `AIza...`)

**NewsAPI** (Optional but recommended):
1. Visit [NewsAPI](https://newsapi.org/register)
2. Sign up for free tier
3. Copy the API key

### 2. Configure Environment

Create `.env` file in the `bl/` directory:

```env
GEMINI_API_KEY=your_gemini_key_here
NEWSAPI_KEY=your_newsapi_key_here
BLINKIT_HEADLESS=1
MANUAL_LOCATION_MODE=false
```

### 3. Install Full Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Backend (For Live Mode)

```bash
cd amazon_blinkit_scrapping
python backend.py
```

### 5. Run Full App

```bash
streamlit run streamlit_app.py
```

Now you can analyze **any category/pincode** with live data!

## 📂 Demo Data Files

Demo mode uses pre-saved JSON files in `data/`:

```
data/
├── snacks_380015_products.json  # 24 scraped products
└── snacks_380015_report.json    # Full AI analysis
```

### Regenerate Demo Data

To update demo data with fresh analysis:

```bash
python save_demo_data.py
```

This will:
1. Scrape latest snacks from pincode 380015
2. Analyze with Gemini AI
3. Save updated JSON files

## 🌐 Deployment Options

### Streamlit Cloud (Demo Mode)
- **Pros**: Free, instant deployment, no setup
- **Cons**: Demo data only, no live scraping
- **Best for**: Demos, presentations, showcases

### Render.com (Full Mode)
- **Pros**: Supports Selenium, full features
- **Cons**: Requires API keys, more complex
- **Best for**: Production use, live analysis

To deploy to Render.com:
1. Use `render.yaml` configuration
2. Add environment variables in Render dashboard
3. Deploy with Chrome/Selenium support

## 🎨 UI Features

Both modes have the same UI:

### Tab 1: Products Overview
- 📊 List of all scraped products
- 🔬 Detailed AI analysis for top 3
- 🥗 Nutrition breakdown
- ✅ Pros & ❌ Cons

### Tab 2: Gap Analysis
- 🌍 Market overview
- 💪 Common strengths/weaknesses
- 🎯 Identified opportunities
- 🚀 Recommended product concepts

### Tab 3: News Insights
- 📰 Trending news articles
- 🤖 AI-extracted insights
- 📈 Market trends
- 💡 Launch recommendations

## 🔧 Technical Details

### Demo Mode Detection

The app automatically detects demo mode if:
- `GEMINI_API_KEY` not found in environment
- `NEWSAPI_KEY` not found in environment
- `DEMO_MODE=true` explicitly set

```python
DEMO_MODE = (
    not os.getenv('GEMINI_API_KEY') or 
    not os.getenv('NEWSAPI_KEY') or
    os.getenv('DEMO_MODE', '').lower() == 'true'
)
```

### Architecture

**Demo Mode Flow:**
```
User → streamlit_demo.py → Load JSON files → Display results
```

**Live Mode Flow:**
```
User → streamlit_app.py → backend.py → Selenium scraper → Gemini AI → Display results
```

## 📊 Demo Data Specs

- **Category**: Snacks
- **Pincode**: 380015 (Ahmedabad, Gujarat)
- **Products Scraped**: 24
- **Products Analyzed**: 3 (with full AI insights)
- **News Articles**: 10+ with AI analysis
- **Market Gaps**: 3-5 identified opportunities

## 💡 Use Cases

### For Companies
- Show full product capabilities without infrastructure
- Present to clients/stakeholders
- Quick POC demonstrations

### For Developers
- Test UI/UX changes without scraping
- Develop frontend without backend running
- Faster iteration during development

### For Users
- Explore features without API keys
- Understand value proposition
- Try before committing to setup

## 🆘 Troubleshooting

### Demo Data Not Loading?

```bash
# Regenerate demo files
python save_demo_data.py
```

### Want to See Different Category?

```bash
# Edit save_demo_data.py, change:
category = "protein bars"  # or any category
pincode = "110001"         # or any pincode

# Run again
python save_demo_data.py
```

### Switch from Demo to Live Mode?

1. Add API keys to `.env`
2. Restart the app
3. App will auto-detect and enable live mode

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/guptarashim28-source/Product-analyzer/issues)
- **Docs**: See `README.md` for full documentation
- **API Docs**: See `amazon_blinkit_scrapping/API_GUIDE.md`

## 🎉 Summary

**Demo Mode** = Full experience, zero setup
**Live Mode** = Custom analysis, requires setup

Choose based on your needs:
- **Just showing?** → Demo Mode
- **Actually using?** → Live Mode

---

Made with ❤️ using Streamlit, FastAPI, Gemini AI & NewsAPI
