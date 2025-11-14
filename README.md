# 🛒 Blinkit Product Analyzer

AI-powered product analysis platform that scrapes Blinkit, analyzes products with Gemini AI, and provides market insights with NewsAPI.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-orange)

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
