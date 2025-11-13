from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Tuple
from pathlib import Path

from .scraper.blinkit_scraper import scrape_for_pincode_query

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


# Serve the simple frontend (single-page) from ./frontend
frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
