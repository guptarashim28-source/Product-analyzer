# 🛒 Blinkit Product Analyzer

AI-powered product analysis platform that scrapes Blinkit, analyzes products with Gemini AI, and provides market insights with NewsAPI.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-orange)

## ✨ For Users - Just Visit the Link!

**Live App:** [Your Render URL will be here after deployment]

No installation needed - just click and use!

## 🚀 Features

- 🔍 **Smart Scraping** - Automated Blinkit product scraping
- 🤖 **AI Analysis** - Gemini AI analyzes products, ingredients, market fit
- 📰 **Market Intelligence** - Real-time news and trend analysis
- 📊 **Gap Analysis** - Identifies market opportunities
- 💡 **Recommendations** - Product launch suggestions

## 📦 For Developers - Local Setup

```bash
# Clone repository
git clone https://github.com/guptarashim28-source/Product-analyzer.git
cd Product-analyzer/bl

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create .env file in amazon_blinkit_scrapping/ folder
GEMINI_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here
BLINKIT_HEADLESS=1

# Run the app
streamlit run streamlit_standalone.py
```

Visit http://localhost:8501

## 🔑 Get API Keys (Free)

1. **Gemini API** - [Get from Google AI Studio](https://makersuite.google.com/app/apikey)
2. **NewsAPI** - [Get from NewsAPI.org](https://newsapi.org/register)

## 🌐 Deploy Your Own (One-Click)

### Deploy to Render

1. **Fork this repository** on GitHub
2. Go to [Render.com](https://render.com) and sign up
3. Click **"New +" → "Blueprint"**
4. Connect your GitHub repo
5. Add environment variables:
   - `GEMINI_API_KEY`
   - `NEWSAPI_KEY`
6. Click **"Apply"**
7. Wait 10 minutes - your app is live! 🎉

### Alternative: Railway or Heroku

Same process - connect repo, add API keys, deploy!

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
