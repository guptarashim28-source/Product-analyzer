"""
News API Integration Module
Fetches trending news and market insights related to products
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from dotenv import load_dotenv

load_dotenv()

def initialize_news_api() -> Optional[NewsApiClient]:
    """Initialize NewsAPI client"""
    api_key = os.getenv('NEWSAPI_KEY')
    if not api_key or api_key == 'your_newsapi_key_here':
        return None
    return NewsApiClient(api_key=api_key)

def get_trending_news(query: str, days_back: int = 7, max_results: int = 10) -> Dict:
    """
    Fetch trending news articles related to a query
    
    Args:
        query: Search term (e.g., product category like 'snacks', 'protein powder')
        days_back: How many days back to search
        max_results: Maximum number of articles to return
    
    Returns:
        Dictionary with news articles and metadata
    """
    newsapi = initialize_news_api()
    
    if not newsapi:
        return {
            "success": False,
            "error": "NewsAPI key not configured. Get your free key from https://newsapi.org/",
            "articles": []
        }
    
    try:
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)
        
        # Search for news articles
        response = newsapi.get_everything(
            q=query,
            language='en',
            from_param=from_date.strftime('%Y-%m-%d'),
            to=to_date.strftime('%Y-%m-%d'),
            sort_by='relevancy',
            page_size=max_results
        )
        
        if response['status'] == 'ok':
            articles = []
            for article in response['articles']:
                articles.append({
                    'title': article['title'],
                    'description': article.get('description', ''),
                    'url': article['url'],
                    'source': article['source']['name'],
                    'published_at': article['publishedAt'],
                    'image_url': article.get('urlToImage', '')
                })
            
            return {
                "success": True,
                "total_results": response['totalResults'],
                "articles": articles,
                "query": query,
                "date_range": f"{from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}"
            }
        else:
            return {
                "success": False,
                "error": "Failed to fetch news",
                "articles": []
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching news: {str(e)}",
            "articles": []
        }

def get_market_trends(category: str) -> Dict:
    """
    Get market trends and industry news for a category
    
    Args:
        category: Product category (e.g., 'food industry', 'beverage market')
    
    Returns:
        Dictionary with trend analysis
    """
    newsapi = initialize_news_api()
    
    if not newsapi:
        return {
            "success": False,
            "error": "NewsAPI key not configured",
            "trends": []
        }
    
    try:
        # Search for market trends
        keywords = f"{category} market trends OR {category} industry news OR {category} consumer insights"
        
        response = newsapi.get_everything(
            q=keywords,
            language='en',
            from_param=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            sort_by='relevancy',
            page_size=15
        )
        
        if response['status'] == 'ok':
            trends = []
            for article in response['articles']:
                trends.append({
                    'title': article['title'],
                    'description': article.get('description', ''),
                    'url': article['url'],
                    'source': article['source']['name'],
                    'published_at': article['publishedAt']
                })
            
            return {
                "success": True,
                "category": category,
                "trends": trends,
                "insights": extract_key_insights(trends)
            }
        else:
            return {
                "success": False,
                "error": "Failed to fetch trends",
                "trends": []
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching trends: {str(e)}",
            "trends": []
        }

def extract_key_insights(articles: List[Dict]) -> List[str]:
    """Extract key insights from article titles and descriptions"""
    insights = []
    
    # Common trend keywords
    trend_keywords = [
        'growth', 'increase', 'rising', 'popular', 'demand',
        'trend', 'consumer', 'market', 'innovation', 'sustainable',
        'organic', 'healthy', 'plant-based', 'premium'
    ]
    
    for article in articles[:10]:  # Analyze top 10 articles
        text = f"{article['title']} {article['description']}".lower()
        
        for keyword in trend_keywords:
            if keyword in text and len(insights) < 5:
                # Extract sentence containing keyword
                sentences = text.split('.')
                for sentence in sentences:
                    if keyword in sentence and len(sentence) > 20:
                        insights.append(sentence.strip().capitalize())
                        break
    
    return list(set(insights))  # Remove duplicates
