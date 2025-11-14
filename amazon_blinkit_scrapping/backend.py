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
        print(f"Starting analysis for: {req.category}")
        print(f"Pincode: {req.pincode}, Max products: {req.max_products}")
        print(f"{'='*60}\n")
        
        products = scrape_blinkit(req.category, req.max_products, req.pincode)
        print(f"✅ Scraped {len(products)} products")
        
        report = analyze_products_with_gemini_and_news(products, req.category)
        print(f"✅ Analysis complete")
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"Summary: {report.get('summary', 'N/A')}")
        print(f"Products analyzed: {len(report.get('products', []))}")
        print(f"News articles: {len(report.get('news_insights', []))}")
        print(f"Market trends: {len(report.get('market_trends', []))}")
        print(f"{'='*60}\n")
        
        return {
            "category": req.category,
            "total_products": len(products),
            "report": report,
        }
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}


# Run with: uvicorn backend:app --reload --host 0.0.0.0 --port 8001
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
