from typing import List, Dict
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Check if we're in a cloud environment without browser support
CLOUD_MODE = os.getenv("CLOUD_MODE", "false").lower() == "true"

if not CLOUD_MODE:
    # Import existing modules only if not in cloud mode
    try:
        from app_backend.app.scraper.blinkit_scraper import scrape_for_pincode_query
        from app_backend.app.utils.gemini_helper import analyze_top_products, generate_gap_analysis, analyze_news_insights
        from app_backend.app.utils.news_helper import get_trending_news, get_market_trends
    except Exception as e:
        print(f"Warning: Could not import scraping modules: {e}")
        CLOUD_MODE = True
else:
    # Mock imports for cloud mode
    print("Running in CLOUD_MODE - using mock data for scraping")


def scrape_blinkit(category: str, max_products: int = 30, pincode: str = "380015") -> List[Dict]:
    """
    Scrape Blinkit for products in a given category.
    Returns a list of product dicts with complete information.
    
    Args:
        category: Product category to search (e.g., 'snacks', 'protein bar')
        max_products: Maximum number of products to return
        pincode: Pincode for location-based search (default: 380015)
    
    Returns:
        List of product dictionaries with:
        - id: Unique identifier (generated from name + brand)
        - title: Product name
        - brand: Brand name
        - price: Price in rupees
        - rating: Placeholder rating (Blinkit doesn't show ratings in search)
        - description: Product weight/size
        - name: Full product name
        - weight: Weight/size string
        - price_text: Original price text with ₹
        - grams: Parsed weight in grams
        - price_per_100g: Price per 100g for comparison
    """
    # Use provided pincode or fall back to environment variable
    if not pincode:
        pincode = os.getenv("DEFAULT_PINCODE", "380015")
    
    # Scrape products
    products, _ = scrape_for_pincode_query(
        pincode=pincode,
        query=category,
        save_html=False,
        max_scrolls=40
    )
    
    # Limit to max_products
    products = products[:max_products]
    
    # Enrich products with additional fields for API compatibility
    enriched_products = []
    for idx, product in enumerate(products):
        # Generate unique ID from name and brand
        product_id = f"{product.get('brand', 'unknown')}_{product.get('name', 'product')}_{idx}".replace(" ", "_")[:50]
        
        enriched_products.append({
            "id": product_id,
            "title": product.get("name", "N/A"),
            "brand": product.get("brand", "Unknown"),
            "price": product.get("price", 0),
            "rating": 4.0,  # Placeholder - Blinkit doesn't show ratings in search results
            "description": product.get("weight", "N/A"),
            # Keep original fields for analysis
            "name": product.get("name", "N/A"),
            "weight": product.get("weight", "N/A"),
            "price_text": product.get("price_text", ""),
            "grams": product.get("grams"),
            "price_per_100g": product.get("price_per_100g"),
        })
    
    return enriched_products


def analyze_products_with_gemini_and_news(products: List[Dict], category: str) -> Dict:
    """
    Analyze products using Gemini AI and fetch related news using NewsAPI.
    
    This function:
    1. Uses Gemini to analyze product ingredients, nutrition, pros/cons
    2. Generates gap analysis and product launch recommendations
    3. Fetches trending news related to the category
    4. Fetches market trends and industry insights
    5. Returns a comprehensive report
    
    Args:
        products: List of product dictionaries from scrape_blinkit()
        category: Product category for context
    
    Returns:
        Dictionary containing:
        - summary: Overall analysis summary
        - products: Analyzed products with AI insights
        - gap_analysis: Market gaps and product recommendations
        - news_insights: Trending news articles
        - market_trends: Industry trends and insights
    """
    # Check if required API keys are configured
    gemini_key = os.getenv("GEMINI_API_KEY")
    news_key = os.getenv("NEWSAPI_KEY")
    
    result = {
        "summary": "",
        "products": [],
        "gap_analysis": None,
        "news_insights": [],
        "market_trends": [],
        "ai_news_analysis": None
    }
    
    # Gemini Analysis
    if gemini_key:
        try:
            # Analyze top products (default: top 5)
            top_n = min(5, len(products))
            analyzed_products = analyze_top_products(products, top_n=top_n)
            result["products"] = analyzed_products
            
            # Generate gap analysis and recommendations
            gap_analysis = generate_gap_analysis(analyzed_products, category)
            result["gap_analysis"] = gap_analysis
            
            # Create summary
            result["summary"] = f"Analyzed {len(analyzed_products)} top products in '{category}' category. "
            if gap_analysis:
                result["summary"] += f"Identified {len(gap_analysis.get('market_gaps', []))} market opportunities."
        except Exception as e:
            result["summary"] += f" Gemini analysis error: {str(e)}"
            print(f"Gemini analysis failed: {e}")
    else:
        result["summary"] = "Gemini API key not configured. AI analysis skipped. "
    
    # News API Analysis
    if news_key:
        try:
            # Get trending news (7 days, 10 articles)
            news_data = get_trending_news(category, days_back=7, max_results=10)
            if news_data.get("articles"):
                result["news_insights"] = news_data["articles"]
                result["summary"] += f" Found {len(news_data['articles'])} recent news articles."
                
                # AI Analysis of news articles
                if gemini_key and len(news_data["articles"]) > 0:
                    try:
                        ai_insights = analyze_news_insights(news_data["articles"], category)
                        result["ai_news_analysis"] = ai_insights
                        result["summary"] += " AI analyzed news for product launch insights."
                    except Exception as e:
                        print(f"AI news analysis failed: {e}")
            
            # Get market trends (30 days, 15 articles)
            search_category = f"{category} food" if category not in ["food", "beverage"] else category
            trends_data = get_market_trends(search_category)
            if trends_data.get("articles"):
                result["market_trends"] = trends_data["articles"]
                result["summary"] += f" Identified {len(trends_data['articles'])} market trend insights."
        except Exception as e:
            result["summary"] += f" NewsAPI error: {str(e)}"
            print(f"NewsAPI analysis failed: {e}")
    else:
        result["summary"] += " NewsAPI key not configured. News insights skipped."
    
    # Final summary
    if not result["summary"]:
        result["summary"] = f"Scraped {len(products)} products for '{category}' category. Configure API keys for full analysis."
    
    return result
