# backend.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from scraper_logic import scrape_blinkit, analyze_products_with_gemini_and_news

app = FastAPI(title="Blinkit Marketing Analyzer")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class AnalyzeRequest(BaseModel):
    category: str
    max_products: int = 30
    pincode: str = "380015"

@app.post("/analyze")
def analyze(req: AnalyzeRequest) -> Dict:
    """
    1. Scrape Blinkit for the given category
    2. Run Gemini + NewsAPI analysis
    3. Return JSON report
    """
    try:
        print(f"\n{'='*60}")
        print(f"🎯 Starting analysis for: {req.category}")
        print(f"📍 Pincode: {req.pincode}")
        print(f"🔢 Max products: {req.max_products}")
        print(f"{'='*60}\n")
        
        print(f"⏳ Step 1/2: Scraping Blinkit for '{req.category}' in pincode {req.pincode}...")
        products = scrape_blinkit(req.category, req.max_products, req.pincode)
        print(f"✅ Scraped {len(products)} products from pincode {req.pincode}")
        
        print(f"\n⏳ Step 2/2: Running AI analysis (Gemini + News + Trends + STP)...")
        report = analyze_products_with_gemini_and_news(products, req.category)
        print(f"✅ Analysis complete")
        print(f"\n📊SUMMARY:")
        print(f"Summary: {report.get('summary', 'N/A')}")
        print(f"Products analyzed: {len(report.get('products', []))}")
        print(f"News articles: {len(report.get('news_insights', []))}")
        
        # Check for rate limit issues
        if len(report.get('products', [])) == 0:
            print(f"\n⚠️ WARNING: No products were analyzed!")
            print(f"This usually means Gemini API rate limit was hit.")
        
        if not report.get('stp_analysis'):
            print(f"\n⚠️ WARNING: STP analysis failed (likely rate limit)")
        
        print(f"{'='*60}\n")
        
        return {
            "category": req.category,
            "pincode": req.pincode,
            "total_products": len(products),
            "report": report,
        }
    except Exception as e:
        error_msg = str(e)
        print(f"❌ ERROR: {error_msg}")
        
        # Check if it's a rate limit error
        if "429" in error_msg or "quota" in error_msg.lower():
            print(f"\n🚫 GEMINI API RATE LIMIT EXCEEDED!")
            print(f"\nYou've hit the daily quota for Gemini API (250 requests/day for free tier)")
            print(f"\n💡 SOLUTIONS:")
            print(f"1. Wait 24 hours for quota reset")
            print(f"2. Get a new Gemini API key from https://aistudio.google.com/app/apikey")
            print(f"3. Upgrade to paid tier for higher limits")
            print(f"4. Use fewer analysis features temporarily\n")
            
            raise HTTPException(
                status_code=429,
                detail="Gemini API rate limit exceeded. Please wait or use a new API key. See terminal for details."
            )
        
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/test-scraper")
def test_scraper(req: AnalyzeRequest) -> Dict:
    """
    Test endpoint: Only scrape products, no AI analysis.
    Use this to verify pincode and products are correct.
    """
    try:
        print(f"\n{'='*60}")
        print(f"🧪 TEST MODE - Scraping only (no AI analysis)")
        print(f"📦 Category: {req.category}")
        print(f"📍 Pincode: {req.pincode}")
        print(f"🔢 Max products: {req.max_products}")
        print(f"{'='*60}\n")
        
        products = scrape_blinkit(req.category, req.max_products, req.pincode)
        
        return {
            "test_mode": True,
            "category": req.category,
            "pincode": req.pincode,
            "total_products": len(products),
            "products": products[:10],  # Return first 10 for inspection
            "message": "Scraping complete. Check terminal for detailed logs."
        }
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn backend:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
