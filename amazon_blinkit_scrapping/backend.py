# backend.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from scraper_logic import scrape_blinkit, analyze_products_with_gemini_and_news

app = FastAPI(title="Blinkit Marketing Analyzer")

class AnalyzeRequest(BaseModel):
    category: str
    max_products: int = 30

@app.post("/analyze")
def analyze(req: AnalyzeRequest) -> Dict:
    """
    1. Scrape Blinkit for the given category
    2. Run Gemini + NewsAPI analysis
    3. Return JSON report
    """
    try:
        products = scrape_blinkit(req.category, req.max_products)
        report = analyze_products_with_gemini_and_news(products, req.category)
        return {
            "category": req.category,
            "total_products": len(products),
            "report": report,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}


# Run with: uvicorn backend:app --reload --host 0.0.0.0 --port 8001
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
