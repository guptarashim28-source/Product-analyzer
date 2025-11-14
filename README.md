# 🛒 Blinkit Product Analyzer

AI-powered product analysis platform that scrapes Blinkit, analyzes products with Gemini AI, and provides market insights with NewsAPI.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-orange)

## ✨ Quick Start

### 🎯 Try Demo (No Setup Required)
View pre-analyzed results instantly: **[Demo App](https://your-streamlit-cloud-url.streamlit.app)**
- No installation needed
- No API keys required
- Full UI experience with sample data

### 🔥 Deploy Full Version (Live Analysis)
Get custom analysis for any category/pincode: **[Full App](https://your-render-url.onrender.com)**
- Live Blinkit scraping
- Real-time AI analysis
- Custom categories & pincodes

📖 **[Demo Mode Guide](DEMO_MODE.md)** - Learn about demo vs live mode

## 🚀 Features

- 🔍 **Smart Scraping** - Automated Blinkit product scraping
- 🤖 **AI Analysis** - Gemini AI analyzes products, ingredients, market fit
- 📰 **Market Intelligence** - Real-time news and trend analysis
- 📊 **Gap Analysis** - Identifies market opportunities
- 💡 **Recommendations** - Product launch suggestions

## 📦 For Developers - Local Setup

### Demo Mode (Minimal Setup)

```bash
# Clone repository
git clone https://github.com/guptarashim28-source/Product-analyzer.git
cd Product-analyzer/bl

# Install minimal dependencies
pip install -r requirements-demo.txt

# Run demo mode
streamlit run streamlit_demo.py
```

Shows pre-analyzed results for snacks in pincode 380015. Perfect for:
- Quick demos and presentations
- Testing UI/UX changes
- Showcasing to clients

### Live Mode (Full Features)

```bash
# Install all dependencies
pip install -r requirements.txt

# Configure environment variables
# Create .env file in amazon_blinkit_scrapping/ folder
GEMINI_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here
BLINKIT_HEADLESS=1

# Start backend
cd amazon_blinkit_scrapping
python backend.py

# In another terminal, start frontend
cd ..
streamlit run streamlit_app.py
```

Visit http://localhost:8501

## 🔑 Get API Keys (Free)

1. **Gemini API** - [Get from Google AI Studio](https://makersuite.google.com/app/apikey)
2. **NewsAPI** - [Get from NewsAPI.org](https://newsapi.org/register)

## 🌐 Deploy Your Own

### Option 1: Demo Mode on Streamlit Cloud (Free)

Perfect for demos and showcases. No API keys needed!

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select:
   - Repository: `your-username/Product-analyzer`
   - Branch: `main`
   - Main file: `bl/streamlit_demo.py`
5. Deploy!

✅ Shows pre-analyzed results for snacks (pincode 380015)
✅ Full UI experience
✅ Zero configuration
✅ Perfect for presentations

### Option 2: Full Mode on Render.com

For live analysis with any category/pincode:

1. Fork this repository
2. Go to [Render.com](https://render.com) and sign up
3. Click **"New +" → "Blueprint"**
4. Connect your GitHub repo
5. Select `render.yaml`
6. Add environment variables:
   - `GEMINI_API_KEY` - [Get from Google AI Studio](https://aistudio.google.com/app/apikey)
   - `NEWSAPI_KEY` - [Get from NewsAPI](https://newsapi.org/register)
   - `BLINKIT_HEADLESS=1`
   - `MANUAL_LOCATION_MODE=false`
7. Click **"Apply"**
8. Wait 10 minutes - your app is live! 🎉

✅ Live scraping from Blinkit
✅ Real-time AI analysis
✅ Custom categories & pincodes
✅ Full features enabled

### Comparison

| Feature | Demo Mode (Streamlit Cloud) | Live Mode (Render) |
|---------|---------------------------|-------------------|
| **Cost** | Free | Free tier available |
| **Setup** | No API keys needed | Requires API keys |
| **Category** | Snacks only | Any category |
| **Pincode** | 380015 only | Any pincode |
| **Data** | Pre-saved | Live scraping |
| **Best for** | Demos, showcases | Production use |

📖 See **[DEMO_MODE.md](DEMO_MODE.md)** for detailed deployment guide

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI**: Google Gemini (gemini-2.5-flash)
- **Scraping**: Selenium + Chrome
- **News**: NewsAPI

## 📝 How to Use

1. Enter product category (e.g., "snacks", "beverages")
2. Enter delivery pincode
3. Choose number of products to analyze
4. Click "Start Analysis"
5. Wait 2-3 minutes for AI-powered insights

## ⚠️ Important Notes

- Analysis takes 2-3 minutes
- Works best with common product categories
- Free API keys have rate limits (sufficient for normal use)
- For companies: Deploy your own instance for unlimited usage

## 🚢 Deployment for Companies

To give this app to a company:

1. **Deploy once on Render** (see deployment guide above)
2. **Share the URL** - That's it! They just visit the link
3. **No installation needed** on their end

### Pricing for Companies

- **Free tier**: Perfect for testing and demos
- **Paid plans** ($7/month): For production use with faster performance

## 📧 Support

For issues, open an issue on GitHub.

## 📄 License

MIT License - Free to use and modify!

## 🚀 Features

- 🔍 **Smart Scraping** - Automated Blinkit product scraping with Selenium
- 🤖 **AI Analysis** - Gemini AI analyzes nutrition, ingredients, pros/cons
- 📰 **Market Intelligence** - NewsAPI integration for trends and insights
- 📊 **Gap Analysis** - Identifies market opportunities and product recommendations
- 💰 **Price Comparison** - Automatic price-per-100g normalization
- 🌐 **REST API** - Clean FastAPI backend for easy integration

## 📦 Quick Start

```bash
# Clone repository
git clone https://github.com/guptarashim28-source/Product-analyzer.git
cd Product-analyzer

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp amazon_blinkit_scrapping/.env.example amazon_blinkit_scrapping/.env
# Edit .env with your API keys

# Run the API
cd amazon_blinkit_scrapping
uvicorn backend:app --reload --port 8000
```

Visit http://localhost:8000/docs for API documentation.

## 🔑 API Keys Required

1. **Gemini API** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **NewsAPI** - Get from [NewsAPI.org](https://newsapi.org/register)

Add to `.env`:
```env
GEMINI_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here
```

## 📡 API Endpoints

**POST** `/analyze` - Scrape and analyze products
```json
{
  "category": "snacks",
  "max_products": 30
}
```

**GET** `/health` - Health check

## 🛠️ Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Scraping**: Selenium, BeautifulSoup4
- **AI**: Google Generative AI (Gemini 2.5 Flash)
- **News**: NewsAPI
- **Data**: Pandas, Python-dotenv

## 📊 What You Get

- Product descriptions and analysis
- Nutrition and ingredient breakdown
- Pros and cons for each product
- Market gap analysis
- Product launch recommendations
- Trending news and market insights
- Price comparisons

## 🚢 Deploy on Render

**⚠️ Important: Selenium/Browser Limitation**
Render's free tier doesn't support Selenium with Chrome. The scraper won't work on Render.

**Alternatives:**
1. **Run locally** - Full functionality with scraping
2. **Use Railway.app or Heroku** - Better support for browser automation
3. **Deploy API-only mode** - Analyze pre-scraped data without live scraping

For Render deployment:
1. Push to GitHub
2. Create new Web Service on Render
3. Connect your repository
4. Add environment variables (API keys)
5. Note: Scraping will fail, but Gemini analysis and NewsAPI will work with provided data

The `render.yaml` and `Procfile` are already configured.

## ⚠️ Disclaimer

For educational and research purposes only. Respect website terms of service.

## 📝 License

MIT License - Use responsibly!

---

**Made with ❤️ for FMCG market research**
