# google_trends_helper.py
from pytrends.request import TrendReq
import pandas as pd
from typing import Dict, List, Any
import time

def get_google_trends(keyword: str, region: str = "IN", timeframe: str = "today 3-m") -> Dict[str, Any]:
    """
    Fetch Google Trends data for a keyword
    
    Args:
        keyword: Search keyword (e.g., "snacks", "protein bars")
        region: Country code (default: "IN" for India)
        timeframe: Time range - options: "now 1-H", "now 4-H", "now 1-d", "today 1-m", "today 3-m", "today 12-m", "today 5-y", "all"
    
    Returns:
        Dictionary with trends data
    """
    try:
        # Initialize pytrends
        pytrends = TrendReq(hl='en-US', tz=330)  # IST timezone
        
        # Build payload
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=region, gprop='')
        
        # Get interest over time
        interest_over_time_df = pytrends.interest_over_time()
        
        result = {
            "keyword": keyword,
            "region": region,
            "timeframe": timeframe,
            "interest_over_time": [],
            "average_interest": 0,
            "trend_direction": "stable",
            "peak_interest": 0,
            "related_queries": {
                "rising": [],
                "top": []
            },
            "related_topics": {
                "rising": [],
                "top": []
            }
        }
        
        if not interest_over_time_df.empty and keyword in interest_over_time_df.columns:
            # Interest over time
            interest_data = interest_over_time_df[keyword].tolist()
            result["interest_over_time"] = interest_data
            result["average_interest"] = int(sum(interest_data) / len(interest_data))
            result["peak_interest"] = int(max(interest_data))
            
            # Determine trend direction
            if len(interest_data) >= 2:
                recent_avg = sum(interest_data[-4:]) / min(4, len(interest_data[-4:]))
                older_avg = sum(interest_data[:4]) / min(4, len(interest_data[:4]))
                
                if recent_avg > older_avg * 1.2:
                    result["trend_direction"] = "rising"
                elif recent_avg < older_avg * 0.8:
                    result["trend_direction"] = "falling"
        
        # Get related queries
        try:
            time.sleep(1)  # Rate limiting
            related_queries = pytrends.related_queries()
            
            if keyword in related_queries and related_queries[keyword]:
                if 'rising' in related_queries[keyword] and isinstance(related_queries[keyword]['rising'], pd.DataFrame):
                    rising_df = related_queries[keyword]['rising']
                    if not rising_df.empty and 'query' in rising_df.columns:
                        result["related_queries"]["rising"] = rising_df['query'].head(5).tolist()
                
                if 'top' in related_queries[keyword] and isinstance(related_queries[keyword]['top'], pd.DataFrame):
                    top_df = related_queries[keyword]['top']
                    if not top_df.empty and 'query' in top_df.columns:
                        result["related_queries"]["top"] = top_df['query'].head(5).tolist()
        except Exception as e:
            print(f"Error fetching related queries: {e}")
        
        # Get related topics
        try:
            time.sleep(1)  # Rate limiting
            related_topics = pytrends.related_topics()
            
            if keyword in related_topics and related_topics[keyword]:
                if 'rising' in related_topics[keyword] and isinstance(related_topics[keyword]['rising'], pd.DataFrame):
                    rising_df = related_topics[keyword]['rising']
                    if not rising_df.empty and 'topic_title' in rising_df.columns:
                        result["related_topics"]["rising"] = rising_df['topic_title'].head(5).tolist()
                
                if 'top' in related_topics[keyword] and isinstance(related_topics[keyword]['top'], pd.DataFrame):
                    top_df = related_topics[keyword]['top']
                    if not top_df.empty and 'topic_title' in top_df.columns:
                        result["related_topics"]["top"] = top_df['topic_title'].head(5).tolist()
        except Exception as e:
            print(f"Error fetching related topics: {e}")
        
        return result
        
    except Exception as e:
        print(f"Error fetching Google Trends: {e}")
        return {
            "keyword": keyword,
            "region": region,
            "timeframe": timeframe,
            "error": str(e),
            "interest_over_time": [],
            "average_interest": 0,
            "trend_direction": "unknown",
            "peak_interest": 0,
            "related_queries": {"rising": [], "top": []},
            "related_topics": {"rising": [], "top": []}
        }


def get_trending_searches(region: str = "india") -> List[Dict[str, Any]]:
    """
    Get trending searches in a region
    
    Args:
        region: Country name (e.g., "india", "united_states")
    
    Returns:
        List of trending searches
    """
    try:
        pytrends = TrendReq(hl='en-US', tz=330)
        trending_df = pytrends.trending_searches(pn=region)
        
        if not trending_df.empty:
            return [{"query": query, "rank": idx + 1} for idx, query in enumerate(trending_df[0].head(20).tolist())]
        
        return []
        
    except Exception as e:
        print(f"Error fetching trending searches: {e}")
        return []
