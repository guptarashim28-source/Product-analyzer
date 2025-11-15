# 🚀 Production Deployment Guide

## ✅ Deploy to Render.com (Recommended - 10 minutes)

Your app is **ready to deploy** with the optimized `render.yaml` configuration!

### Step-by-Step Deployment

#### 1. Sign Up on Render
- Go to [render.com](https://render.com)
- Sign up with GitHub (easiest) or email
- Verify your email

#### 2. Create New Blueprint
- Click **"New +"** button (top right)
- Select **"Blueprint"**
- Connect your GitHub account if not already connected

#### 3. Select Repository
- Search for: `Product-analyzer`
- Or use: `guptarashim28-source/Product-analyzer`
- Click **"Connect"**

#### 4. Configure Blueprint
Render will automatically detect your `render.yaml` file:

- **Service Name**: product-analyzer
- **Branch**: main
- **Region**: Oregon (or closest to you)
- **Plan**: Free (for testing) or Starter ($7/mo for production)

#### 5. Add Environment Variables
In the Render dashboard, add these **Secret Files**:

```bash
GEMINI_API_KEY=AIzaSyAbpHAWJUxRB0UzwCCwmR6FGh_u2gd0GdY
NEWSAPI_KEY=3e9c28d1c56948dd81c3ed7149205af8
```

These are already set in `render.yaml`:
- `BLINKIT_HEADLESS=1` ✅
- `MANUAL_LOCATION_MODE=false` ✅
- `PYTHON_VERSION=3.11.0` ✅

#### 6. Deploy!
- Click **"Apply"** or **"Create Web Service"**
- Wait 10-15 minutes for:
  - Chrome installation
  - Python dependencies
  - Service startup

#### 7. Access Your App
Your app will be live at:
```
https://product-analyzer.onrender.com
```
(Replace with your actual Render URL)

### 🎉 What You Get

✅ **Backend API** running on the assigned port  
✅ **Automatic HTTPS** with SSL certificate  
✅ **Chrome + Selenium** fully installed  
✅ **Auto-deploy** on every git push to main  
✅ **Health checks** and auto-restart  

---

## 🔧 Troubleshooting

### Build Fails: Chrome Installation
If Chrome installation fails, Render might need root access:

```yaml
# Add to buildCommand in render.yaml
sudo apt-get update
sudo apt-get install -y google-chrome-stable
```

### Service Doesn't Start
Check logs in Render dashboard:
- Click on your service
- Go to "Logs" tab
- Look for Python errors

Common issues:
- Missing `.env` variables → Add in Render dashboard
- Port binding error → Render automatically sets `$PORT`
- Import errors → Check `requirements.txt`

### Selenium/Chrome Errors
If you see "Chrome binary not found":

```bash
# The render.yaml already includes this, but verify:
google-chrome --version
chromedriver --version
```

### Free Tier Limitations
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ Slow startup (30-60 seconds when waking up)
- ⚠️ 750 hours/month limit

**Solution**: Upgrade to Starter plan ($7/mo) for:
- Always-on service
- Faster performance
- No monthly hour limits

---

## 🌐 Alternative Deployment Options

### Option 2: Railway.app

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

Add environment variables in Railway dashboard.

### Option 3: Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

Requires `fly.toml` configuration file (can create if needed).

### Option 4: DigitalOcean App Platform

1. Go to [cloud.digitalocean.com](https://cloud.digitalocean.com)
2. Create new App
3. Connect GitHub repo
4. Select `bl` as root directory
5. Add environment variables
6. Deploy

---

## 📊 Cost Comparison

| Platform | Free Tier | Paid Plan | Best For |
|----------|-----------|-----------|----------|
| **Render** | 750 hrs/mo | $7/mo | Production (Recommended) |
| **Railway** | $5 credit/mo | Pay-as-go | Testing |
| **Fly.io** | 3 VMs free | $1.94/mo+ | Global deployment |
| **DigitalOcean** | ❌ None | $5/mo | Enterprise |

---

## 🎯 Post-Deployment Checklist

After successful deployment:

### 1. Test the API
```bash
curl https://your-app.onrender.com/
```

Should return: `{"message": "Blinkit Product Analyzer API"}`

### 2. Test Scraping
```bash
curl -X POST https://your-app.onrender.com/test-scraper \
  -H "Content-Type: application/json" \
  -d '{"category":"snacks","pincode":"380015","max_products":5}'
```

### 3. Test Full Analysis
```bash
curl -X POST https://your-app.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"category":"snacks","pincode":"380015","max_products":3}'
```

### 4. Update Frontend
If you deploy the backend separately, update `streamlit_app.py`:

```python
# Change API URL from localhost to your Render URL
api_url = "https://your-app.onrender.com"
```

### 5. Monitor Logs
- Render Dashboard → Your Service → Logs
- Watch for errors or rate limit issues
- Monitor Chrome/Selenium startup

---

## 🔐 Security Best Practices

### 1. API Keys
✅ **Never commit API keys to GitHub**  
✅ Add them as environment variables in Render dashboard  
✅ Use "Secret File" type in Render  

### 2. Rate Limiting
Consider adding rate limiting to prevent abuse:

```python
# In backend.py
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze")
@limiter.limit("5/minute")  # 5 requests per minute
async def analyze_products(req: AnalysisRequest):
    ...
```

### 3. CORS (if needed for frontend)
Already configured in backend.py with proper origins.

---

## 📱 Share Your App

Once deployed, share with companies/clients:

### For Testing (Demo Mode)
Deploy to Streamlit Cloud:
- URL: `https://your-demo.streamlit.app`
- No backend needed
- Shows pre-analyzed data

### For Production (Full Features)
Deploy to Render:
- URL: `https://product-analyzer.onrender.com`
- Full Selenium scraping
- Real-time AI analysis
- Custom categories/pincodes

---

## 🆘 Need Help?

### Render Support
- [Render Docs](https://render.com/docs)
- [Chrome on Render Guide](https://render.com/docs/chrome)
- [Community Forum](https://community.render.com)

### Common Issues
- **Build timeout**: Increase timeout in Render settings
- **Memory issues**: Upgrade from free tier
- **Chrome crashes**: Check headless mode is enabled

### Contact
- GitHub Issues: [Product-analyzer/issues](https://github.com/guptarashim28-source/Product-analyzer/issues)
- Check logs first before asking for help

---

## ✅ Success!

Your app is now live and accessible worldwide! 🎉

**Next Steps:**
1. Share the URL with clients
2. Monitor usage and logs
3. Consider upgrading to paid tier for better performance
4. Set up custom domain (optional)

**Live URLs:**
- Demo: https://your-demo.streamlit.app
- Production: https://product-analyzer.onrender.com

---

Made with ❤️ using FastAPI, Streamlit, Selenium, Gemini AI & NewsAPI
