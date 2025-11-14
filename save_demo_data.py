"""
Script to save demo data from a real analysis
Run this once to create demo JSON files for the app
"""
import json
import sys
from pathlib import Path

# Add amazon_blinkit_scrapping to path
sys.path.insert(0, str(Path(__file__).parent / "amazon_blinkit_scrapping"))

from scraper_logic import scrape_blinkit, analyze_products_with_gemini_and_news

def save_demo_data():
    """Scrape and analyze snacks for 380015, then save to JSON files"""
    
    category = "snacks"
    pincode = "380015"
    max_products = 30
    
    print(f"🔍 Scraping {category} for pincode {pincode}...")
    products = scrape_blinkit(category, pincode, max_products)
    
    if not products:
        print("❌ No products found!")
        return
    
    print(f"✅ Scraped {len(products)} products")
    
    # Save products
    products_file = Path(__file__).parent / "data" / f"snacks_{pincode}_products.json"
    with open(products_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved products to {products_file}")
    
    # Analyze with AI
    print(f"🤖 Analyzing with AI...")
    report = analyze_products_with_gemini_and_news(products, category)
    
    # Save full report
    report_file = Path(__file__).parent / "data" / f"snacks_{pincode}_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved report to {report_file}")
    
    print("\n✅ Demo data saved successfully!")
    print(f"   Products: {len(products)}")
    print(f"   Analyzed: {len(report.get('products', []))}")
    print(f"   Gap Analysis: {'Yes' if report.get('gap_analysis') else 'No'}")
    print(f"   News Articles: {len(report.get('news', []))}")

if __name__ == "__main__":
    save_demo_data()
