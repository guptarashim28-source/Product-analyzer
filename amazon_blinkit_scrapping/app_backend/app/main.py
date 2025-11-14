from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from the project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from .scraper.blinkit_scraper import scrape_for_pincode_query
from .utils.gemini_helper import analyze_top_products, generate_gap_analysis
from .utils.news_helper import get_trending_news, get_market_trends

# Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI(title="Blinkit Scraper UI API", version="0.1.0")

# Allow local dev UIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class ScrapeRequest(BaseModel):
    pincodes: List[str] = Field(..., description="List of pincodes to scrape")
    query: str = Field(..., description="Product type or search query, e.g., 'protein bar' or 'snacks'")
    save_html: bool = Field(False, description="Whether to persist raw HTML pages to disk")
    max_scrolls: int = Field(40, description="Safety limit for scroll attempts")


class AnalysisRequest(BaseModel):
    pincodes: List[str] = Field(..., description="List of pincodes to scrape")
    query: str = Field(..., description="Product type or search query, e.g., 'protein bar' or 'snacks'")
    save_html: bool = Field(False, description="Whether to persist raw HTML pages to disk")
    max_scrolls: int = Field(40, description="Safety limit for scroll attempts")
    top_n: int = Field(5, description="Number of top products to analyze")
    include_gap_analysis: bool = Field(True, description="Whether to include gap analysis and product recommendations")


@app.get("/api/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok"}


def _run_scrape(req: ScrapeRequest) -> Tuple[List[Dict[str, Any]], List[str], str, List[Dict[str, Any]]]:
    all_products: List[Dict[str, Any]] = []
    brand_top10_counter: Dict[str, int] = {}

    # Normalize pincodes
    pincodes = [p.strip() for p in req.pincodes if p and p.strip()]

    for pincode in pincodes:
        products, _html = scrape_for_pincode_query(
            pincode=pincode,
            query=req.query,
            save_html=req.save_html,
            max_scrolls=req.max_scrolls,
        )
        # Mark ranks and pincode
        for idx, item in enumerate(products):
            item["rank"] = idx + 1
            item["pincode"] = pincode
        all_products.extend(products)

        # Count brand appearances in top 10 for this pincode
        for item in products[:10]:
            brand = item.get("brand") or "Unknown"
            brand_top10_counter[brand] = brand_top10_counter.get(brand, 0) + 1

    # Prepare brand counts as list sorted desc
    brand_top10_counts = [
        {"brand": b, "count": c} for b, c in sorted(brand_top10_counter.items(), key=lambda x: x[1], reverse=True)
    ]

    return all_products, pincodes, req.query, brand_top10_counts


@app.post("/api/scrape")
async def scrape(req: ScrapeRequest) -> Dict[str, Any]:
    all_products, pincodes, query, brand_top10_counts = _run_scrape(req)

    return {
        "summary": {
            "pincodes": pincodes,
            "query": query,
            "total_products": len(all_products)
        },
        "brand_top10_counts": brand_top10_counts,
        "products": all_products,
    }


@app.post("/api/export-csv")
async def export_csv(req: ScrapeRequest) -> Response:
    all_products, pincodes, query, _brand_counts = _run_scrape(req)

    # Build CSV content
    import csv
    import io

    buf = io.StringIO()
    writer = csv.writer(buf)
    header = [
        "pincode", "rank", "brand", "name", "weight", "price", "price_text", "grams", "price_per_100g"
    ]
    writer.writerow(header)
    for p in all_products:
        writer.writerow([
            p.get("pincode", ""),
            p.get("rank", ""),
            p.get("brand", ""),
            p.get("name", ""),
            p.get("weight", ""),
            p.get("price", ""),
            p.get("price_text", ""),
            p.get("grams", ""),
            p.get("price_per_100g", ""),
        ])

    csv_bytes = buf.getvalue()
    filename = f"blinkit_products_{'_'.join(pincodes)}_{query.replace(' ', '_')}.csv"
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@app.post("/api/analyze")
async def analyze_products(req: AnalysisRequest) -> Dict[str, Any]:
    """
    Scrape products and provide AI-powered analysis including:
    - Product descriptions
    - Nutrition analysis
    - Pros and cons
    - Gap analysis and product launch recommendations
    """
    # First, scrape the products
    scrape_req = ScrapeRequest(
        pincodes=req.pincodes,
        query=req.query,
        save_html=req.save_html,
        max_scrolls=req.max_scrolls
    )
    all_products, pincodes, query, brand_top10_counts = _run_scrape(scrape_req)
    
    # Analyze top N products with Gemini
    analyzed_products = analyze_top_products(all_products, top_n=req.top_n)
    
    # Generate gap analysis if requested
    gap_analysis = None
    if req.include_gap_analysis:
        gap_analysis = generate_gap_analysis(analyzed_products, query)
    
    return {
        "summary": {
            "pincodes": pincodes,
            "query": query,
            "total_products": len(all_products),
            "analyzed_count": len(analyzed_products)
        },
        "brand_top10_counts": brand_top10_counts,
        "analyzed_products": analyzed_products,
        "gap_analysis": gap_analysis
    }


@app.post("/api/quick-analysis")
async def quick_analysis(products: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
    """
    Analyze already scraped products without re-scraping
    Useful for analyzing existing data
    """
    top_n = min(10, len(products))
    analyzed_products = analyze_top_products(products, top_n=top_n)
    gap_analysis = generate_gap_analysis(analyzed_products, query)
    
    return {
        "analyzed_products": analyzed_products,
        "gap_analysis": gap_analysis
    }


@app.get("/api/news/{query}")
async def get_news(query: str, days: int = 7, max_results: int = 10) -> Dict[str, Any]:
    """
    Get trending news articles related to a product query
    
    Args:
        query: Product category or search term (e.g., 'snacks', 'protein powder')
        days: Number of days to look back (default: 7)
        max_results: Maximum articles to return (default: 10)
    """
    news_data = get_trending_news(query, days_back=days, max_results=max_results)
    return news_data


@app.get("/api/market-trends/{category}")
async def get_trends(category: str) -> Dict[str, Any]:
    """
    Get market trends and industry insights for a product category
    
    Args:
        category: Product category (e.g., 'snacks', 'beverages', 'dairy')
    """
    # Enhance category for better search results
    search_category = f"{category} food" if category not in ["food", "beverage"] else category
    trends_data = get_market_trends(search_category)
    return trends_data


# Serve the simple frontend (single-page) from ./frontend
frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
