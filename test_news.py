import sys
sys.path.insert(0, 'amazon_blinkit_scrapping')

from app_backend.app.utils.news_helper import get_trending_news

print("Testing news API...")
result = get_trending_news('snacks', days_back=7, max_results=10)

print(f"Success: {result.get('success')}")
print(f"Total Results: {result.get('total_results')}")
print(f"Articles Found: {len(result.get('articles', []))}")
print(f"Error: {result.get('error', 'None')}")

if result.get('articles'):
    print("\nFirst 3 articles:")
    for i, article in enumerate(result.get('articles', [])[:3], 1):
        print(f"{i}. {article['title']}")
        print(f"   Source: {article['source']}")
